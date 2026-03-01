<template>
  <div class="dashboard">
    <!-- Error banner -->
    <div v-if="statusError" class="error-banner">
      <span class="error-icon">⚠</span>
      <span>Backend offline — {{ statusError.data?.detail || 'Could not connect to Garmin Dashboard API' }}</span>
    </div>

    <!-- Goal Hero -->
    <section>
      <RunGoalProgress
        :goal="goalStatus?.goal || 104"
        :actual="goalStatus?.actual || 0"
        :target-to-date="goalStatus?.expected_to_date || 0"
        :percent="goalStatus?.progress_percent || 0"
        :status="goalStatus?.status || 'behind'"
        :year="goalStatus?.year || 2026"
        :loading="statusLoading"
        @refresh="refreshData"
      />
    </section>

    <!-- Weekly Stats -->
    <section>
      <WeeklySummary />
    </section>

    <!-- Bottom grid -->
    <div class="bottom-grid">
      <!-- Recent Activities -->
      <section class="activities-panel">
        <AppCard allow-overflow>
          <template #header>
            <div class="panel-title-group">
              <span class="panel-eyebrow">RECENT</span>
              <h2 class="panel-title">Activities</h2>
            </div>
            <div class="header-actions">
              <button
                class="log-btn"
                :class="`log-btn--${logState}`"
                :disabled="logState === 'loading'"
                @click="logBouldering"
              >
                <span class="log-btn-icon">⬡</span>
                {{ logLabel }}
              </button>
              <AppButton @click="navigateTo('/activities')" icon-right="→">
                VIEW ALL
              </AppButton>
            </div>
          </template>

          <div class="table-wrap">
            <div v-if="activitiesLoading" class="table-loading">
              <div class="loading-rows">
                <div v-for="n in 5" :key="n" class="loading-row">
                  <AppSkeleton class="w-half" />
                  <AppSkeleton class="w-quarter" />
                  <AppSkeleton class="w-fifth" />
                </div>
              </div>
            </div>

            <div v-else-if="!activities || activities.length === 0" class="table-empty">
              <div class="empty-icon">⬡</div>
              <p class="empty-text">No recent activities — time to hit the road.</p>
            </div>

            <UTable
              v-else
              :data="activities"
              :columns="activityColumns"
              class="clickable-table"
              @select="(_, row) => navigateTo(`/activities/${row.original.activityId}`)"
            >
              <template #activityName-cell="{ row }">
                <div class="cell-activity">
                  <ActivityTypeDot :type="row.original.activityType?.typeKey" />
                  <span class="activity-name">{{ row.original.activityName }}</span>
                </div>
              </template>
              <template #startTimeLocal-cell="{ row }">
                <span class="cell-date">{{ formatDate(row.original.startTimeLocal) }}</span>
              </template>
              <template #distance-cell="{ row }">
                <span class="cell-distance">{{ (row.original.distance / 1000).toFixed(2) }}<span class="cell-unit"> km</span></span>
              </template>
            </UTable>
          </div>
        </AppCard>
      </section>

      <!-- Health Snapshot -->
      <section class="health-panel">
        <AppCard label="Health" :sub-label="`${currentYear} TRENDS`">
          <div class="health-metrics">
            <div v-if="snapshotPending" class="health-metric">
              <AppSkeleton height="80px" />
            </div>
            <template v-else>
              <div class="health-metric">
                <div class="hm-label">RESTING HEART RATE</div>
                <div class="hm-value">
                  <span class="hm-num" :class="rhrDelta <= 0 ? 'hm-pos' : 'hm-neg'">
                    {{ rhrDelta !== null ? (rhrDelta > 0 ? '+' : '') + rhrDelta : '--' }}
                  </span>
                  <span class="hm-unit" :class="rhrDelta <= 0 ? 'hm-pos' : 'hm-neg'">BPM</span>
                </div>
                <div class="hm-desc">vs January {{ currentYear }} ({{ snapshot?.rhr?.current ?? '--' }} bpm now)</div>
                <div class="hm-bar">
                  <div class="hm-bar-fill" :class="rhrDelta <= 0 ? '' : 'hm-bar--neg'" :style="{ width: rhrBarPct + '%' }"></div>
                </div>
              </div>

              <div class="hm-separator"></div>

              <div class="health-metric">
                <div class="hm-label">AVG SLEEP DURATION</div>
                <div class="hm-value">
                  <span class="hm-num hm-blue">{{ snapshot?.sleep?.avg_formatted || '--' }}</span>
                </div>
                <div class="hm-desc">{{ sleepDeltaDesc }}</div>
                <div class="hm-bar">
                  <div class="hm-bar-fill hm-bar--blue" :style="{ width: sleepBarPct + '%' }"></div>
                </div>
              </div>

              <div class="hm-separator"></div>

              <div class="health-metric">
                <div class="hm-label">AVG STRESS LEVEL</div>
                <div class="hm-value">
                  <span class="hm-num" :class="stressDelta <= 0 ? 'hm-pos' : 'hm-neg'">
                    {{ snapshot?.stress?.current ?? '--' }}
                  </span>
                  <span class="hm-unit" :class="stressDelta <= 0 ? 'hm-pos' : 'hm-neg'">/100</span>
                </div>
                <div class="hm-desc">{{ stressDeltaDesc }}</div>
                <div class="hm-bar">
                  <div class="hm-bar-fill" :class="stressDelta <= 0 ? '' : 'hm-bar--neg'" :style="{ width: stressBarPct + '%' }"></div>
                </div>
              </div>
            </template>
          </div>
        </AppCard>
      </section>
    </div>
  </div>
</template>

<script setup>
const apiBase = useApiBase()

const { formatDate } = useFormatters()

const now = new Date()
const currentYear = now.getFullYear()
const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1).toISOString().split('T')[0]
const today = now.toISOString().split('T')[0]

const {
  data: goalStatus,
  pending: statusLoading,
  error: statusError,
  refresh: refreshGoal
} = await useFetch(`${apiBase}/goal-status`, {
  query: { year: currentYear },
  immediate: true
})

const {
  data: activities,
  pending: activitiesLoading,
  refresh: refreshActivities
} = await useFetch(`${apiBase}/activities`, {
  query: {
    start_date: startOfMonth,
    end_date: today
  },
  immediate: true
})

const activityColumns = [
  { accessorKey: 'activityName', header: 'Activity' },
  { accessorKey: 'startTimeLocal', header: 'Date' },
  { accessorKey: 'distance', header: 'Distance' }
]

const {
  data: snapshot,
  pending: snapshotPending,
} = await useFetch(`${apiBase}/health-snapshot`, { immediate: true })

const rhrDelta = computed(() => snapshot.value?.rhr?.delta ?? null)
const rhrBarPct = computed(() => {
  const d = rhrDelta.value
  return d !== null ? Math.min(Math.round(Math.abs(d) / 10 * 100), 100) : 0
})
const sleepDeltaDesc = computed(() => {
  const m = snapshot.value?.sleep?.delta_minutes
  if (m === null || m === undefined) return `vs ${currentYear - 1}`
  return `${m >= 0 ? '+' : ''}${m}m vs ${currentYear - 1}`
})
const sleepBarPct = computed(() => {
  const fmt = snapshot.value?.sleep?.avg_formatted
  if (!fmt) return 0
  const [h, m] = fmt.split('h ').map(parseFloat)
  const hours = h + (m || 0) / 60
  return Math.min(Math.round(hours / 8 * 100), 100)
})

const stressDelta = computed(() => snapshot.value?.stress?.delta ?? null)
const stressDeltaDesc = computed(() => {
  const d = stressDelta.value
  const base = snapshot.value?.stress?.baseline
  if (d === null) return `vs January ${currentYear}`
  return `${d >= 0 ? '+' : ''}${d} vs January ${currentYear} (was ${base})`
})
const stressBarPct = computed(() => {
  const curr = snapshot.value?.stress?.current
  return curr ? Math.min(Math.round(curr), 100) : 0
})

const refreshData = async () => {
  await Promise.all([refreshGoal(), refreshActivities()])
}

// Bouldering quick-log
const logState = ref('idle') // 'idle' | 'loading' | 'success' | 'error'
const logLabel = computed(() => ({
  idle: 'LOG BOULDERING',
  loading: 'LOGGING...',
  success: 'LOGGED ✓',
  error: 'FAILED',
}[logState.value]))

const logBouldering = async () => {
  logState.value = 'loading'
  try {
    await $fetch(`${apiBase}/activities/bouldering`, { method: 'POST' })
    logState.value = 'success'
    refreshActivities()
  } catch {
    logState.value = 'error'
  } finally {
    setTimeout(() => { logState.value = 'idle' }, 3000)
  }
}
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Error banner */
.error-banner {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(255, 69, 33, 0.08);
  border: 1px solid rgba(255, 69, 33, 0.25);
  border-radius: 4px;
  padding: 12px 18px;
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 0.08em;
  color: var(--accent);
}

.error-icon { font-size: 14px; }

/* Bottom grid */
.bottom-grid {
  display: grid;
  grid-template-columns: 1fr 360px;
  gap: 20px;
  align-items: start;
}

@media (max-width: 900px) {
  .bottom-grid { grid-template-columns: 1fr; }
}

.panel-title-group {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.panel-eyebrow {
  font-family: var(--font-mono);
  font-size: 9px;
  letter-spacing: 0.25em;
  color: var(--muted);
}

.panel-title {
  font-family: var(--font-display);
  font-size: 26px;
  color: var(--text);
  letter-spacing: 0.05em;
}

/* Activities header actions */
.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.log-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.15em;
  padding: 6px 12px;
  border-radius: 3px;
  border: 1px solid var(--border-light);
  background: transparent;
  color: var(--muted-light);
  cursor: pointer;
  transition: all 0.15s;
  white-space: nowrap;
}

.log-btn:hover:not(:disabled) {
  border-color: var(--green);
  color: var(--green);
  background: var(--green-soft);
}

.log-btn--loading {
  opacity: 0.6;
  cursor: not-allowed;
}

.log-btn--success {
  border-color: var(--green);
  color: var(--green);
  background: var(--green-soft);
}

.log-btn--error {
  border-color: var(--accent);
  color: var(--accent);
  background: var(--accent-soft);
}

.log-btn-icon {
  font-size: 12px;
}

/* Table */
.table-wrap { padding: 4px 0; }

.table-loading { padding: 16px 24px; }

.loading-rows {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.loading-row {
  display: flex;
  gap: 12px;
  align-items: center;
}

.w-half    { flex: 2; }
.w-quarter { flex: 1; }
.w-fifth   { flex: 0.6; }

.table-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  gap: 10px;
}

.empty-icon {
  font-size: 28px;
  color: var(--border-light);
}

.empty-text {
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 0.1em;
  color: var(--muted);
  text-align: center;
}

/* Table cell overrides */
.cell-activity {
  display: flex;
  align-items: center;
  gap: 10px;
}

.activity-name {
  font-weight: 600;
  font-size: 13px;
  color: var(--text);
}

.cell-date {
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.08em;
  color: var(--muted-light);
}

.cell-distance {
  font-family: var(--font-display);
  font-size: 18px;
  color: var(--text);
}

.cell-unit {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--muted-light);
}

/* Health panel */
.health-metrics {
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 0;
}

.health-metric {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 16px 0;
}

.hm-separator {
  height: 1px;
  background: var(--border);
}

.hm-label {
  font-family: var(--font-mono);
  font-size: 9px;
  letter-spacing: 0.2em;
  color: var(--muted);
  text-transform: uppercase;
}

.hm-value {
  display: flex;
  align-items: baseline;
  gap: 6px;
}

.hm-num {
  font-family: var(--font-display);
  font-size: 38px;
  color: var(--green);
  letter-spacing: 0.03em;
  line-height: 1;
}

.hm-unit {
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--green);
  opacity: 0.7;
  letter-spacing: 0.1em;
}

.hm-pos { color: var(--green); }
.hm-neg { color: var(--accent); }
.hm-blue { color: var(--blue); }

.hm-desc {
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.08em;
  color: var(--muted-light);
  margin-top: 1px;
}

.hm-bar {
  height: 3px;
  background: var(--border-light);
  border-radius: 2px;
  margin-top: 8px;
  overflow: hidden;
}

.hm-bar-fill {
  height: 100%;
  background: var(--green);
  border-radius: 2px;
  transition: width 1s ease;
}

.hm-bar--blue { background: var(--blue); }
.hm-bar--neg  { background: var(--accent); }

</style>

<style>
/* Global UTable overrides for dark theme */
table {
  width: 100%;
  border-collapse: collapse;
}

thead tr {
  background: var(--raised) !important;
  border-bottom: 1px solid var(--border) !important;
}

thead th {
  font-family: var(--font-mono) !important;
  font-size: 9px !important;
  letter-spacing: 0.2em !important;
  color: var(--muted) !important;
  text-transform: uppercase !important;
  padding: 10px 16px !important;
  font-weight: 500 !important;
  background: var(--raised) !important;
}

tbody tr {
  border-bottom: 1px solid var(--border) !important;
  transition: background 0.15s !important;
}

tbody tr:hover { background: var(--raised) !important; }
tbody tr:last-child { border-bottom: none !important; }

tbody td {
  padding: 12px 16px !important;
  background: transparent !important;
  color: var(--text) !important;
}
</style>
