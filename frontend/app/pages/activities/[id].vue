<template>
  <div class="detail-page">
    <!-- Header -->
    <div class="detail-header">
      <div class="header-nav">
        <AppButton @click="navigateTo('/')" icon-left="←" variant="ghost">
          DASHBOARD
        </AppButton>
        <AppButton @click="navigateTo('/activities')" variant="outline">
          ALL ACTIVITIES
        </AppButton>
      </div>

      <div v-if="pending" class="header-loading">
        <AppSkeleton height="14px" width="120px" />
        <AppSkeleton height="38px" width="280px" style="margin-top:6px;" />
      </div>

      <div v-else-if="data" class="header-info">
        <div class="header-meta">
          <span class="header-date">{{ formatDate(act?.startTimeLocal, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }) }}</span>
          <ActivityBadge :type="act?.activityType" />
        </div>
        <h1 class="activity-title">{{ act?.activityName }}</h1>
      </div>
    </div>

    <!-- Loading skeleton -->
    <div v-if="pending" class="skeleton-grid">
      <AppSkeleton v-for="n in 6" :key="n" height="80px" />
    </div>

    <template v-else-if="data">
      <!-- Overview stats strip -->
      <div class="stats-strip">
        <StatBlock label="DISTANCE" :value="formatDistance(act?.distance)" />
        <div class="stat-divider"></div>
        <StatBlock label="DURATION" :value="formatDuration(act?.duration)" />
        <div class="stat-divider"></div>
        <StatBlock label="AVG PACE" :value="formatPace(act?.averageSpeed)" />
        <div class="stat-divider"></div>
        <StatBlock label="AVG HR" :value="act?.averageHR ?? '—'" :unit="act?.averageHR ? 'bpm' : ''" />
        <div class="stat-divider"></div>
        <StatBlock label="MAX HR" :value="act?.maxHR ?? '—'" :unit="act?.maxHR ? 'bpm' : ''" />
        <div class="stat-divider"></div>
        <StatBlock label="CALORIES" :value="act?.calories ?? '—'" :unit="act?.calories ? 'kcal' : ''" />
      </div>

      <!-- Middle grid: Training + HR Zones -->
      <div class="mid-grid">
        <!-- Training metrics -->
        <AppCard label="TRAINING METRICS">
          <MetricRow label="Aerobic Effect">
            {{ act?.aerobicTrainingEffect?.toFixed(1) ?? '—' }}
            <template #after-val>
              <TrainingEffectBar v-if="act?.aerobicTrainingEffect" :value="act.aerobicTrainingEffect" color="var(--green)" />
            </template>
          </MetricRow>

          <MetricRow label="Anaerobic Effect">
            {{ act?.anaerobicTrainingEffect?.toFixed(1) ?? '—' }}
            <template #after-val>
              <TrainingEffectBar v-if="act?.anaerobicTrainingEffect" :value="act.anaerobicTrainingEffect" color="var(--amber)" />
            </template>
          </MetricRow>

          <MetricRow label="Avg Cadence" :value="act?.averageRunCadence?.toFixed(0) ?? '—'" :unit="act?.averageRunCadence ? 'spm' : ''" />
          <MetricRow label="Avg Stride Length" :value="act?.strideLength ?? '—'" :unit="act?.strideLength ? 'm' : ''" />
          <MetricRow label="Elevation Gain" :value="act?.elevationGain?.toFixed(0) ?? '—'" :unit="act?.elevationGain ? 'm' : ''" />
        </AppCard>

        <!-- HR Zones -->
        <AppCard label="HEART RATE ZONES" :sub-label="!hrZones ? 'Not available' : ''">
          <div v-if="hrZones?.length" class="zones-list">
            <div
              v-for="zone in sortedZones"
              :key="zone.zoneNumber"
              class="zone-row"
            >
              <div class="zone-label">
                <span class="zone-num" :style="{ color: zoneColor(zone.zoneNumber) }">Z{{ zone.zoneNumber }}</span>
                <span class="zone-name">{{ zoneName(zone.zoneNumber) }}</span>
              </div>
              <div class="zone-bar-wrap">
                <div class="zone-bar">
                  <div
                    class="zone-fill"
                    :style="{
                      width: zonePct(zone.secsInZone) + '%',
                      background: zoneColor(zone.zoneNumber)
                    }"
                  ></div>
                </div>
                <span class="zone-time">{{ secsToTime(zone.secsInZone) }}</span>
                <span class="zone-pct">{{ zonePct(zone.secsInZone).toFixed(0) }}%</span>
              </div>
            </div>
          </div>
          <div v-else class="zone-empty">
            <span class="metric-val--muted">No zone data available for this activity</span>
          </div>
        </AppCard>
      </div>

      <!-- Splits table -->
      <div v-if="lapDTOs?.length">
        <AppCard label="SPLITS" :sub-label="`${lapDTOs.length} laps`" allow-overflow>
          <div class="splits-table-wrap">
            <UTable :data="lapDTOs" :columns="splitColumns">
              <template #lapIndex-cell="{ row }">
                <span class="split-lap">{{ row.original.lapIndex }}</span>
              </template>
              <template #distance-cell="{ row }">
                <span class="cell-mono">{{ (row.original.distance / 1000).toFixed(2) }} km</span>
              </template>
              <template #duration-cell="{ row }">
                <span class="cell-mono">{{ formatDuration(row.original.duration) }}</span>
              </template>
              <template #averageSpeed-cell="{ row }">
                <span class="cell-stat">{{ formatPace(row.original.averageSpeed) }}</span>
              </template>
              <template #averageHR-cell="{ row }">
                <span v-if="row.original.averageHR" class="cell-stat">
                  {{ row.original.averageHR }}
                </span>
                <span v-else class="cell-muted">—</span>
              </template>
              <template #maxHR-cell="{ row }">
                <span v-if="row.original.maxHR" class="cell-muted-val">{{ row.original.maxHR }}</span>
                <span v-else class="cell-muted">—</span>
              </template>
              <template #elevationGain-cell="{ row }">
                <span v-if="row.original.elevationGain" class="cell-mono">
                  +{{ row.original.elevationGain?.toFixed(0) }}m
                </span>
                <span v-else class="cell-muted">—</span>
              </template>
            </UTable>
          </div>
        </AppCard>
      </div>
    </template>

    <div v-else-if="error" class="error-state">
      <span class="error-icon">⚠</span>
      <span>Could not load activity — {{ error?.data?.detail || 'Backend unavailable' }}</span>
    </div>
  </div>
</template>

<script setup>
const route  = useRoute()
const id     = route.params.id

const { formatDate, formatDistance, formatDuration, formatPace } = useFormatters()
const apiBase = useApiBase()

const { data, pending, error } = await useFetch(`${apiBase}/activities/${id}`)

const act      = computed(() => data.value?.summary)
const hrZones  = computed(() => data.value?.hr_zones)
const lapDTOs  = computed(() => data.value?.splits?.lapDTOs)

// HR Zone helpers
const totalZoneSecs = computed(() =>
  hrZones.value?.reduce((s, z) => s + (z.secsInZone ?? 0), 0) ?? 0
)
const sortedZones = computed(() =>
  hrZones.value ? [...hrZones.value].sort((a, b) => b.zoneNumber - a.zoneNumber) : []
)

const zonePct = (secs) =>
  totalZoneSecs.value > 0 ? (secs / totalZoneSecs.value) * 100 : 0

const zoneColor = (n) => {
  const map = { 1: 'var(--blue)', 2: 'var(--green)', 3: 'var(--amber)', 4: '#FF8C00', 5: 'var(--accent)' }
  return map[n] ?? 'var(--muted-light)'
}

const zoneName = (n) => {
  const map = { 1: 'Recovery', 2: 'Aerobic Base', 3: 'Tempo', 4: 'Threshold', 5: 'Max Effort' }
  return map[n] ?? `Zone ${n}`
}

const secsToTime = (s) => {
  if (!s) return '0s'
  const m = Math.floor(s / 60)
  const sec = Math.round(s % 60)
  if (m > 0) return `${m}m ${sec}s`
  return `${sec}s`
}

// Splits table columns
const splitColumns = [
  { accessorKey: 'lapIndex',     header: 'Lap' },
  { accessorKey: 'distance',     header: 'Distance' },
  { accessorKey: 'duration',     header: 'Time' },
  { accessorKey: 'averageSpeed', header: 'Pace' },
  { accessorKey: 'averageHR',    header: 'Avg HR' },
  { accessorKey: 'maxHR',        header: 'Max HR' },
  { accessorKey: 'elevationGain',header: 'Elev +' },
]
</script>

<style scoped>
.detail-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Header */
.detail-header {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.header-nav {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-info { flex: 1; }

.header-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 6px;
}

.header-date {
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.16em;
  color: var(--muted);
}

.activity-title {
  font-family: var(--font-display);
  font-size: clamp(28px, 4vw, 48px);
  color: var(--text);
  letter-spacing: 0.04em;
  line-height: 1;
}

.header-loading { flex: 1; }

/* Skeleton */
.skeleton-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 1px;
  background: var(--border);
  border: 1px solid var(--border);
  border-radius: 4px;
  overflow: hidden;
}

/* Stats strip */
.stats-strip {
  display: grid;
  grid-template-columns: 1fr auto 1fr auto 1fr auto 1fr auto 1fr auto 1fr;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 4px;
  overflow: hidden;
}

@media (max-width: 768px) {
  .stats-strip {
    grid-template-columns: 1fr 1fr 1fr;
    grid-template-rows: 1fr 1fr;
  }
  .stat-divider { display: none; }
}

.stat-divider {
  width: 1px;
  background: var(--border);
  margin: 16px 0;
}

/* Mid grid */
.mid-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

@media (max-width: 768px) {
  .mid-grid { grid-template-columns: 1fr; }
}

.metric-val--muted { font-size: 11px; font-family: var(--font-mono); color: var(--muted); }

/* HR Zones */
.zones-list {
  display: flex;
  flex-direction: column;
  gap: 0;
  padding: 8px 0;
}

.zone-row {
  display: grid;
  grid-template-columns: 140px 1fr;
  align-items: center;
  gap: 12px;
  padding: 10px 20px;
  border-bottom: 1px solid var(--border);
}

.zone-row:last-child { border-bottom: none; }

.zone-label {
  display: flex;
  align-items: center;
  gap: 8px;
}

.zone-num {
  font-family: var(--font-display);
  font-size: 18px;
  letter-spacing: 0.05em;
}

.zone-name {
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.1em;
  color: var(--muted-light);
  text-transform: uppercase;
}

.zone-bar-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
}

.zone-bar {
  flex: 1;
  height: 6px;
  background: var(--border);
  border-radius: 3px;
  overflow: hidden;
}

.zone-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.8s ease;
  opacity: 0.85;
}

.zone-time {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--muted-light);
  letter-spacing: 0.06em;
  width: 54px;
  text-align: right;
}

.zone-pct {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--muted);
  letter-spacing: 0.05em;
  width: 32px;
  text-align: right;
}

.zone-empty { padding: 24px 20px; }

/* Splits table */
.splits-table-wrap { overflow-x: auto; }

/* Cell overrides */
.split-lap {
  font-family: var(--font-display);
  font-size: 18px;
  color: var(--muted-light);
}

.cell-mono {
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 0.06em;
  color: var(--muted-light);
}

.cell-stat {
  font-family: var(--font-display);
  font-size: 16px;
  color: var(--text);
}

.cell-muted-val {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--muted-light);
}

.cell-muted {
  font-family: var(--font-mono);
  color: var(--muted);
}

/* Error */
.error-state {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(255, 69, 33, 0.08);
  border: 1px solid rgba(255, 69, 33, 0.25);
  border-radius: 4px;
  padding: 16px 20px;
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 0.08em;
  color: var(--accent);
}

.error-icon { font-size: 16px; }
</style>
