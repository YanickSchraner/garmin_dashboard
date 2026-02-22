<template>
  <div class="detail-page">
    <!-- Header -->
    <div class="detail-header">
      <button class="back-btn" @click="navigateTo('/activities')">
        <span>←</span> ALL ACTIVITIES
      </button>

      <div v-if="pending" class="header-loading">
        <div class="shimmer" style="height:14px;width:120px;border-radius:2px;"></div>
        <div class="shimmer" style="height:38px;width:280px;border-radius:2px;margin-top:6px;"></div>
      </div>

      <div v-else-if="data" class="header-info">
        <div class="header-meta">
          <span class="header-date">{{ formatDate(summary?.startTimeLocal) }}</span>
          <div class="activity-type-badge" :style="{ color: activityColor(summary?.activityType?.typeKey), borderColor: activityColor(summary?.activityType?.typeKey) + '40' }">
            {{ formatType(summary?.activityType?.typeKey) }}
          </div>
        </div>
        <h1 class="activity-title">{{ summary?.activityName }}</h1>
      </div>
    </div>

    <!-- Loading skeleton -->
    <div v-if="pending" class="skeleton-grid">
      <div v-for="n in 6" :key="n" class="skeleton-stat shimmer"></div>
    </div>

    <template v-else-if="data">
      <!-- Overview stats strip -->
      <div class="stats-strip">
        <div class="stat-block">
          <span class="stat-label">DISTANCE</span>
          <span class="stat-value">{{ formatDistance(summary?.distance) }}</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-block">
          <span class="stat-label">DURATION</span>
          <span class="stat-value">{{ formatDuration(summary?.duration) }}</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-block">
          <span class="stat-label">AVG PACE</span>
          <span class="stat-value">{{ formatPace(summary?.averageSpeed) }}</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-block">
          <span class="stat-label">AVG HR</span>
          <span class="stat-value">{{ summary?.averageHR ?? '—' }}<span v-if="summary?.averageHR" class="stat-unit">bpm</span></span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-block">
          <span class="stat-label">MAX HR</span>
          <span class="stat-value">{{ summary?.maxHR ?? '—' }}<span v-if="summary?.maxHR" class="stat-unit">bpm</span></span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-block">
          <span class="stat-label">CALORIES</span>
          <span class="stat-value">{{ summary?.calories ?? '—' }}<span v-if="summary?.calories" class="stat-unit">kcal</span></span>
        </div>
      </div>

      <!-- Middle grid: Training + HR Zones -->
      <div class="mid-grid">
        <!-- Training metrics -->
        <div class="panel">
          <div class="panel-head">
            <span class="panel-label">TRAINING METRICS</span>
          </div>
          <div class="panel-body">
            <div class="metric-row">
              <span class="metric-name">Aerobic Effect</span>
              <div class="metric-right">
                <span class="metric-val">{{ summary?.aerobicTrainingEffect?.toFixed(1) ?? '—' }}</span>
                <div v-if="summary?.aerobicTrainingEffect" class="metric-bar">
                  <div class="metric-fill metric-fill--green" :style="{ width: (summary.aerobicTrainingEffect / 5 * 100) + '%' }"></div>
                </div>
              </div>
            </div>

            <div class="metric-row">
              <span class="metric-name">Anaerobic Effect</span>
              <div class="metric-right">
                <span class="metric-val">{{ summary?.anaerobicTrainingEffect?.toFixed(1) ?? '—' }}</span>
                <div v-if="summary?.anaerobicTrainingEffect" class="metric-bar">
                  <div class="metric-fill metric-fill--amber" :style="{ width: (summary.anaerobicTrainingEffect / 5 * 100) + '%' }"></div>
                </div>
              </div>
            </div>

            <div class="metric-row">
              <span class="metric-name">Training Stress Score</span>
              <div class="metric-right">
                <span class="metric-val">{{ summary?.trainingStressScore?.toFixed(0) ?? '—' }}</span>
              </div>
            </div>

            <div class="metric-divider"></div>

            <div class="metric-row">
              <span class="metric-name">Recovery Time</span>
              <div class="metric-right">
                <span class="metric-val metric-val--accent">
                  {{ summary?.recoveryTime ? summary.recoveryTime + 'h' : '—' }}
                </span>
              </div>
            </div>

            <div class="metric-row">
              <span class="metric-name">Avg Cadence</span>
              <div class="metric-right">
                <span class="metric-val">{{ summary?.averageRunningCadenceInStepsPerMinute?.toFixed(0) ?? '—' }}<span v-if="summary?.averageRunningCadenceInStepsPerMinute" class="metric-unit"> spm</span></span>
              </div>
            </div>

            <div class="metric-row">
              <span class="metric-name">Avg Stride Length</span>
              <div class="metric-right">
                <span class="metric-val">{{ summary?.avgStrideLength?.toFixed(2) ?? '—' }}<span v-if="summary?.avgStrideLength" class="metric-unit"> m</span></span>
              </div>
            </div>

            <div class="metric-row">
              <span class="metric-name">Elevation Gain</span>
              <div class="metric-right">
                <span class="metric-val">{{ summary?.elevationGain?.toFixed(0) ?? '—' }}<span v-if="summary?.elevationGain" class="metric-unit"> m</span></span>
              </div>
            </div>

            <div class="metric-row">
              <span class="metric-name">VO2 Max</span>
              <div class="metric-right">
                <span class="metric-val">{{ summary?.vO2MaxValue?.toFixed(1) ?? '—' }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- HR Zones -->
        <div class="panel">
          <div class="panel-head">
            <span class="panel-label">HEART RATE ZONES</span>
            <span v-if="!hrZones" class="panel-na">Not available</span>
          </div>
          <div class="panel-body">
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
              <span class="metric-val metric-val--muted">No zone data available for this activity</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Splits table -->
      <div v-if="lapDTOs?.length" class="panel">
        <div class="panel-head">
          <span class="panel-label">SPLITS</span>
          <span class="panel-sub">{{ lapDTOs.length }} laps</span>
        </div>
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

const { data, pending, error } = await useFetch(`http://localhost:8000/activities/${id}`)

const summary  = computed(() => data.value?.summary)
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

// Formatters
const formatDate = (s) => {
  if (!s) return '—'
  return new Date(s).toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }).toUpperCase()
}

const formatDistance = (m) => {
  if (!m) return '—'
  return (m / 1000).toFixed(2) + ' km'
}

const formatDuration = (s) => {
  if (!s) return '—'
  const h = Math.floor(s / 3600)
  const m = Math.floor((s % 3600) / 60)
  const sec = Math.round(s % 60)
  if (h > 0) return `${h}:${String(m).padStart(2,'0')}:${String(sec).padStart(2,'0')}`
  return `${m}:${String(sec).padStart(2,'0')}`
}

const formatPace = (mps) => {
  if (!mps) return '—'
  const spk = 1000 / mps
  const m = Math.floor(spk / 60)
  const s = Math.round(spk % 60)
  return `${m}:${String(s).padStart(2,'0')}/km`
}

const activityColor = (type) => {
  if (type === 'running')  return 'var(--accent)'
  if (type === 'cycling')  return 'var(--blue)'
  return 'var(--muted-light)'
}

const formatType = (type) => {
  if (!type) return 'ACTIVITY'
  return type.replace(/_/g, ' ').toUpperCase()
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
  align-items: flex-start;
  gap: 20px;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.18em;
  color: var(--muted-light);
  background: transparent;
  border: 1px solid var(--border-light);
  padding: 6px 12px;
  border-radius: 2px;
  cursor: pointer;
  transition: all 0.2s;
  text-transform: uppercase;
  flex-shrink: 0;
  margin-top: 6px;
}

.back-btn:hover { border-color: var(--accent); color: var(--accent); }

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

.activity-type-badge {
  font-family: var(--font-mono);
  font-size: 9px;
  letter-spacing: 0.18em;
  border: 1px solid;
  padding: 2px 7px;
  border-radius: 2px;
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

.skeleton-stat {
  height: 80px;
  background: var(--surface);
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

.stat-block {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 20px 20px;
  transition: background 0.15s;
}

.stat-block:hover { background: var(--raised); }

.stat-divider {
  width: 1px;
  background: var(--border);
  margin: 16px 0;
}

.stat-label {
  font-family: var(--font-mono);
  font-size: 9px;
  letter-spacing: 0.2em;
  color: var(--muted);
  text-transform: uppercase;
}

.stat-value {
  font-family: var(--font-display);
  font-size: 28px;
  color: var(--text);
  letter-spacing: 0.03em;
  line-height: 1;
}

.stat-unit {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--muted-light);
  letter-spacing: 0.05em;
  margin-left: 2px;
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

/* Panels */
.panel {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 4px;
  overflow: hidden;
}

.panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px;
  border-bottom: 1px solid var(--border);
  background: var(--raised);
}

.panel-label {
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.2em;
  color: var(--muted-light);
  text-transform: uppercase;
}

.panel-na {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--muted);
  letter-spacing: 0.1em;
}

.panel-sub {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--muted);
  letter-spacing: 0.12em;
}

.panel-body { padding: 6px 0; }

/* Training metrics */
.metric-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 20px;
  border-bottom: 1px solid var(--border);
  gap: 12px;
}

.metric-row:last-child { border-bottom: none; }

.metric-divider {
  height: 1px;
  background: var(--border-light);
  margin: 4px 20px;
}

.metric-name {
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 0.08em;
  color: var(--muted-light);
  flex-shrink: 0;
}

.metric-right {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.metric-val {
  font-family: var(--font-display);
  font-size: 20px;
  color: var(--text);
  letter-spacing: 0.03em;
  white-space: nowrap;
}

.metric-val--accent { color: var(--accent); }
.metric-val--muted { font-size: 11px; font-family: var(--font-mono); color: var(--muted); }

.metric-unit {
  font-family: var(--font-mono);
  font-size: 9px;
  color: var(--muted-light);
  letter-spacing: 0.1em;
}

.metric-bar {
  width: 80px;
  height: 4px;
  background: var(--border);
  border-radius: 2px;
  overflow: hidden;
}

.metric-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.8s ease;
}

.metric-fill--green { background: var(--green); }
.metric-fill--amber { background: var(--amber); }

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

/* Shimmer */
.shimmer {
  background: linear-gradient(90deg, var(--raised) 25%, var(--border) 50%, var(--raised) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0%   { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>
