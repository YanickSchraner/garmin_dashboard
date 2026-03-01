<template>
  <div class="stats-page">
    <div class="page-header">
      <AppButton @click="navigateTo('/')" icon-left="←">
        DASHBOARD
      </AppButton>
      <div class="page-title-group">
        <span class="page-eyebrow">WEEKLY DRILLDOWN</span>
        <h1 class="page-title">Training Sessions</h1>
      </div>
    </div>

    <div class="top-summary">
      <AppCard>
        <div v-if="loading" class="summary-grid">
          <AppSkeleton v-for="n in 3" :key="n" height="40px" width="100px" />
        </div>
        <div v-else class="summary-grid">
          <StatBlock label="TOTAL SESSIONS" :value="totalSessions" unit="runs" />
          <div class="stat-divider"></div>
          <StatBlock label="WEEKLY GOAL" :value="config?.weekly_run_goal ?? 2" unit="runs" />
          <div class="stat-divider"></div>
          <StatBlock label="GOAL STATUS" :value="goalStatus" unit="%" :class="goalStatus >= 100 ? 'stat-pos' : ''" />
        </div>
      </AppCard>
    </div>

    <div class="main-grid">
      <!-- Session Bar Chart -->
      <AppCard label="Frequency" sub-label="Training Days Comparison">
        <div v-if="loading" class="chart-loading">
          <AppSkeleton height="200px" />
        </div>
        <div v-else class="chart-container">
          <div class="chart-y-axis">
            <span>1</span>
            <span>0</span>
          </div>
          <div class="chart-area">
            <div v-for="(day, i) in weeklyData" :key="i" class="chart-column">
              <div class="bar-group">
                <div 
                  class="bar bar--prev" 
                  :class="{ 'bar--active': day.prevSession }"
                  :style="{ height: day.prevSession ? '100%' : '5%' }"
                ></div>
                <div 
                  class="bar bar--curr" 
                  :class="{ 'bar--active': day.session }"
                  :style="{ height: day.session ? '100%' : '5%' }"
                ></div>
              </div>
              <div class="day-label">{{ day.label }}</div>
              <div v-if="day.session" class="session-icon">◈</div>
            </div>
          </div>
        </div>
        <div class="chart-legend">
          <div class="legend-item"><span class="legend-box bar--curr bar--active"></span> Training (Current)</div>
          <div class="legend-item"><span class="legend-box bar--prev bar--active"></span> Training (Previous)</div>
        </div>
      </AppCard>

      <!-- Training Load -->
      <AppCard label="Training Distribution" sub-label="Intensity Mix">
        <div v-if="loading" class="list-loading">
          <AppSkeleton v-for="n in 3" :key="n" height="40px" style="margin-bottom:8px" />
        </div>
        <div v-else class="list-container">
          <div v-for="(day, i) in weeklyData.filter(d => d.session)" :key="i" class="list-row">
            <div class="day-info">
              <span class="day-name">{{ day.fullDay }}</span>
              <div class="training-badge" :class="'training--' + day.intensity">
                {{ day.intensity ? day.intensity.toUpperCase() : 'LOW' }}
              </div>
            </div>
            <div class="load-info">
              <div class="te-row">
                <span class="load-label">AEROBIC</span>
                <span class="load-val">{{ day.aerobic_te.toFixed(1) }}</span>
              </div>
              <div class="te-row">
                <span class="load-label">ANAEROBIC</span>
                <span class="load-val load-val--anaerobic">{{ day.anaerobic_te.toFixed(1) }}</span>
              </div>
            </div>
          </div>
          <div v-if="weeklyData.filter(d => d.session).length === 0" class="empty-list">
            No activities recorded this week.
          </div>
        </div>
      </AppCard>
    </div>
  </div>
</template>

<script setup>
const { activitiesByDay, prevActivitiesByDay, loading, fetchActivities } = useWeeklyActivities()
const config = useConfig()

onMounted(() => {
  fetchActivities()
})

const weeklyData = computed(() => {
  return activitiesByDay.value.map((day, i) => ({
    label: day.label,
    fullDay: day.fullDay,
    session: day.count > 0,
    prevSession: (prevActivitiesByDay.value[i]?.count || 0) > 0,
    intensity: day.training,
    aerobic_te: day.aerobic_te || 0,
    anaerobic_te: day.anaerobic_te || 0,
  }))
})

const totalSessions = computed(() => {
  return weeklyData.value.filter(d => d.session).length
})

const goalStatus = computed(() => {
  const goal = config.value?.weekly_run_goal ?? 2
  const progress = (totalSessions.value / goal) * 100
  return Math.min(100, Math.round(progress))
})
</script>

<style scoped>
.stats-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.page-header {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 16px;
}

.page-title-group {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.page-eyebrow {
  font-family: var(--font-mono);
  font-size: 9px;
  letter-spacing: 0.25em;
  color: var(--muted);
}

.page-title {
  font-family: var(--font-display);
  font-size: 38px;
  color: var(--text);
  letter-spacing: 0.05em;
  line-height: 1;
}

.summary-grid {
  display: flex;
  align-items: center;
  padding: 10px 0;
}

.stat-divider {
  width: 1px;
  height: 40px;
  background: var(--border);
  margin: 0 10px;
}

.stat-pos { color: var(--green); }

.main-grid {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 24px;
}

@media (max-width: 1024px) {
  .main-grid { grid-template-columns: 1fr; }
}

/* Chart Styles */
.chart-container {
  display: flex;
  height: 200px;
  padding: 20px 20px 40px 10px;
  gap: 15px;
}

.chart-y-axis {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--muted);
  text-align: right;
  width: 20px;
  padding-bottom: 25px;
}

.chart-area {
  flex: 1;
  display: flex;
  align-items: flex-end;
  justify-content: space-around;
  border-bottom: 1px solid var(--border);
  position: relative;
}

.chart-column {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
  position: relative;
}

.bar-group {
  flex: 1;
  width: 100%;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  gap: 6px;
  padding-bottom: 2px;
}

.bar {
  width: 16px;
  border-radius: 2px 2px 0 0;
  transition: height 1s ease-out;
  background: var(--border);
  opacity: 0.2;
}

.bar--curr.bar--active { background: var(--green); opacity: 1; }
.bar--prev.bar--active { background: var(--border-light); opacity: 0.8; }

.day-label {
  position: absolute;
  bottom: -25px;
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--muted);
}

.session-icon {
  position: absolute;
  bottom: -45px;
  color: var(--green);
  font-size: 12px;
}

.chart-legend {
  display: flex;
  gap: 20px;
  padding: 20px;
  border-top: 1px solid var(--border);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--muted-light);
}

.legend-box { width: 12px; height: 12px; border-radius: 2px; }

/* List Styles */
.list-container { padding: 10px 0; }
.list-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 20px;
  border-bottom: 1px solid var(--border);
}
.list-row:last-child { border-bottom: none; }

.day-info { display: flex; flex-direction: column; gap: 4px; }
.day-name { font-family: var(--font-body); font-weight: 600; font-size: 14px; color: var(--text); }

.training-badge {
  font-family: var(--font-mono);
  font-size: 9px;
  letter-spacing: 0.1em;
  padding: 2px 6px;
  border-radius: 2px;
  display: inline-block;
  width: fit-content;
}

.training--high   { background: var(--accent-soft); color: var(--accent); border: 1px solid var(--accent); }
.training--medium { background: var(--amber-soft); color: var(--amber); border: 1px solid var(--amber); }
.training--low    { background: var(--green-soft); color: var(--green); border: 1px solid var(--green); }

.load-info { display: flex; gap: 16px; }
.te-row { display: flex; flex-direction: column; align-items: flex-end; }
.load-label { font-family: var(--font-mono); font-size: 8px; color: var(--muted); }
.load-val { font-family: var(--font-display); font-size: 20px; color: var(--text); }
.load-val--anaerobic { color: var(--accent); }
</style>
