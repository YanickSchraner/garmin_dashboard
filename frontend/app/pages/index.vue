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
            <AppButton @click="navigateTo('/activities')" icon-right="→">
              VIEW ALL
            </AppButton>
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
        <AppCard label="Health" sub-label="2026 TRENDS">
          <div class="health-metrics">
            <div class="health-metric">
              <div class="hm-label">RHR IMPROVEMENT</div>
              <div class="hm-value">
                <span class="hm-num">-4</span>
                <span class="hm-unit">BPM</span>
              </div>
              <div class="hm-desc">since January 2026</div>
              <div class="hm-bar"><div class="hm-bar-fill" style="width: 72%"></div></div>
            </div>

            <div class="hm-separator"></div>

            <div class="health-metric">
              <div class="hm-label">AVG SLEEP DURATION</div>
              <div class="hm-value">
                <span class="hm-num">7h 12m</span>
              </div>
              <div class="hm-desc">+18m vs 2025</div>
              <div class="hm-bar"><div class="hm-bar-fill hm-bar--blue" style="width: 60%"></div></div>
            </div>
          </div>
        </AppCard>
      </section>
    </div>
  </div>
</template>

<script setup>
const apiBase = 'http://localhost:8000'

const { formatDate } = useFormatters()

const {
  data: goalStatus,
  pending: statusLoading,
  error: statusError,
  refresh: refreshGoal
} = await useFetch(`${apiBase}/goal-status`, {
  query: { year: 2026 },
  immediate: true
})

const {
  data: activities,
  pending: activitiesLoading,
  refresh: refreshActivities
} = await useFetch(`${apiBase}/activities`, {
  query: {
    start_date: '2026-02-01',
    end_date: '2026-02-22'
  },
  immediate: true
})

const activityColumns = [
  { accessorKey: 'activityName', header: 'Activity' },
  { accessorKey: 'startTimeLocal', header: 'Date' },
  { accessorKey: 'distance', header: 'Distance' }
]

const refreshData = async () => {
  await Promise.all([refreshGoal(), refreshActivities()])
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
