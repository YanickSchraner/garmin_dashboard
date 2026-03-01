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
          <AppSkeleton v-for="n in 4" :key="n" height="40px" width="100px" />
        </div>
        <div v-else class="summary-grid">
          <StatBlock label="TOTAL SESSIONS" :value="totalSessions" unit="runs" />
          <div class="stat-divider"></div>
          <StatBlock label="WEEKLY GOAL" :value="config?.weekly_run_goal ?? 2" unit="runs" />
          <div class="stat-divider"></div>
          <StatBlock label="TOTAL DISTANCE" :value="totalDist.toFixed(1)" unit="km" />
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
                  :class="{ 'bar--active': day.session, ['bar--intensity-' + day.intensity]: day.session }"
                  :style="{ height: day.session ? '100%' : '5%' }"
                ></div>
              </div>
              <div class="day-label">{{ day.label }}</div>
              <div v-if="day.session" class="session-dist">{{ day.dist.toFixed(1) }}k</div>
            </div>
          </div>
        </div>
        <div class="chart-legend">
          <div class="legend-item"><span class="legend-box bar--intensity-high bar--active"></span> High</div>
          <div class="legend-item"><span class="legend-box bar--intensity-medium bar--active"></span> Medium</div>
          <div class="legend-item"><span class="legend-box bar--intensity-low bar--active"></span> Low</div>
          <div class="legend-item"><span class="legend-box bar--prev bar--active"></span> Previous Week</div>
        </div>
      </AppCard>

      <!-- Session Detail List -->
      <AppCard label="Session Breakdown" sub-label="Type · Load · Distance">
        <div v-if="loading" class="list-loading">
          <AppSkeleton v-for="n in 3" :key="n" height="54px" style="margin-bottom:8px" />
        </div>
        <div v-else class="list-container">
          <div v-for="(day, i) in weeklyData.filter(d => d.session)" :key="i" class="list-row">
            <div class="day-info">
              <div class="day-top">
                <span class="day-name">{{ day.fullDay }}</span>
                <div class="session-type-badge" :class="'type--' + day.sessionType.toLowerCase()">
                  {{ day.sessionType }}
                </div>
              </div>
              <div class="day-dist">{{ day.dist.toFixed(1) }} km</div>
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

    <!-- Week vs Week Comparison -->
    <AppCard label="Week vs Week" sub-label="Current · Previous · Delta">
      <div v-if="loading" class="comp-loading">
        <AppSkeleton height="60px" />
      </div>
      <div v-else class="comp-grid">
        <div class="comp-row comp-row--header">
          <span class="comp-label"></span>
          <span class="comp-col-head">THIS WEEK</span>
          <span class="comp-col-head">LAST WEEK</span>
          <span class="comp-col-head">CHANGE</span>
        </div>
        <div class="comp-row">
          <span class="comp-label">Sessions</span>
          <span class="comp-val">{{ weekComp.sessions.curr }}</span>
          <span class="comp-val comp-val--muted">{{ weekComp.sessions.prev }}</span>
          <span class="comp-val" :class="weekComp.sessions.delta >= 0 ? 'comp-pos' : 'comp-neg'">
            {{ weekComp.sessions.delta >= 0 ? '+' : '' }}{{ weekComp.sessions.delta }}
          </span>
        </div>
        <div class="comp-row">
          <span class="comp-label">Distance</span>
          <span class="comp-val">{{ weekComp.dist.curr.toFixed(1) }} km</span>
          <span class="comp-val comp-val--muted">{{ weekComp.dist.prev.toFixed(1) }} km</span>
          <span class="comp-val" :class="weekComp.dist.delta >= 0 ? 'comp-pos' : 'comp-neg'">
            {{ weekComp.dist.delta >= 0 ? '+' : '' }}{{ weekComp.dist.delta.toFixed(1) }} km
          </span>
        </div>
        <div class="comp-row">
          <span class="comp-label">Avg Aerobic TE</span>
          <span class="comp-val">{{ weekComp.te.curr.toFixed(1) }}</span>
          <span class="comp-val comp-val--muted">{{ weekComp.te.prev.toFixed(1) }}</span>
          <span class="comp-val" :class="weekComp.te.delta >= 0 ? 'comp-pos' : 'comp-neg'">
            {{ weekComp.te.delta >= 0 ? '+' : '' }}{{ weekComp.te.delta.toFixed(1) }}
          </span>
        </div>
        <div class="comp-row comp-row--last">
          <span class="comp-label">Intensity Mix</span>
          <span class="comp-val">{{ weekComp.mix.curr }}</span>
          <span class="comp-val comp-val--muted">{{ weekComp.mix.prev }}</span>
          <span class="comp-val comp-val--muted">—</span>
        </div>
      </div>
    </AppCard>
  </div>
</template>

<script setup>
const { activitiesByDay, prevActivitiesByDay, loading, fetchActivities } = useWeeklyActivities()
const config = useConfig()

onMounted(() => {
  fetchActivities()
})

const sessionType = (te) => {
  if (te >= 4.5) return 'RACE'
  if (te >= 4.0) return 'TEMPO'
  if (te >= 3.0) return 'BASE'
  if (te >= 2.0) return 'EASY'
  if (te > 0)    return 'RECOVERY'
  return 'REST'
}

const intensityMix = (days) => {
  const h = days.filter(d => d.training === 'high' || d.intensity === 'high').length
  const m = days.filter(d => d.training === 'medium' || d.intensity === 'medium').length
  const l = days.filter(d => (d.training === 'low' || d.intensity === 'low') && (d.count > 0 || d.session)).length
  return `${h}H ${m}M ${l}L`
}

const weeklyData = computed(() => {
  return activitiesByDay.value.map((day, i) => ({
    label: day.label,
    fullDay: day.fullDay,
    session: day.count > 0,
    prevSession: (prevActivitiesByDay.value[i]?.count || 0) > 0,
    intensity: day.training,
    dist: day.dist || 0,
    aerobic_te: day.aerobic_te || 0,
    anaerobic_te: day.anaerobic_te || 0,
    sessionType: sessionType(day.aerobic_te || 0),
  }))
})

const totalSessions = computed(() => weeklyData.value.filter(d => d.session).length)
const totalDist = computed(() => weeklyData.value.reduce((s, d) => s + d.dist, 0))

const goalStatus = computed(() => {
  const goal = config.value?.weekly_run_goal ?? 2
  return Math.min(100, Math.round((totalSessions.value / goal) * 100))
})

const weekComp = computed(() => {
  const curr = weeklyData.value.filter(d => d.session)
  const prev = prevActivitiesByDay.value.filter(d => d.count > 0)

  const currDist = weeklyData.value.reduce((s, d) => s + d.dist, 0)
  const prevDist = prevActivitiesByDay.value.reduce((s, d) => s + (d.dist || 0), 0)

  const currTeVals = curr.map(d => d.aerobic_te).filter(v => v > 0)
  const prevTeVals = prev.map(d => d.aerobic_te || 0).filter(v => v > 0)
  const currAvgTe = currTeVals.length ? currTeVals.reduce((a, b) => a + b, 0) / currTeVals.length : 0
  const prevAvgTe = prevTeVals.length ? prevTeVals.reduce((a, b) => a + b, 0) / prevTeVals.length : 0

  return {
    sessions: { curr: curr.length, prev: prev.length, delta: curr.length - prev.length },
    dist:     { curr: currDist, prev: prevDist, delta: currDist - prevDist },
    te:       { curr: currAvgTe, prev: prevAvgTe, delta: currAvgTe - prevAvgTe },
    mix:      { curr: intensityMix(curr), prev: intensityMix(prev) },
  }
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
  padding: 20px 20px 50px 10px;
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
  padding-bottom: 35px;
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

.bar--prev.bar--active            { background: var(--border-light); opacity: 0.6; }
.bar--intensity-high.bar--active  { background: var(--accent); opacity: 1; }
.bar--intensity-medium.bar--active{ background: var(--amber); opacity: 1; }
.bar--intensity-low.bar--active   { background: var(--green); opacity: 1; }

.day-label {
  position: absolute;
  bottom: -22px;
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--muted);
}

.session-dist {
  position: absolute;
  bottom: -38px;
  font-family: var(--font-mono);
  font-size: 9px;
  color: var(--muted-light);
}

.chart-legend {
  display: flex;
  gap: 16px;
  padding: 20px;
  border-top: 1px solid var(--border);
  flex-wrap: wrap;
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

.day-info { display: flex; flex-direction: column; gap: 6px; }
.day-top  { display: flex; align-items: center; gap: 8px; }
.day-name { font-family: var(--font-body); font-weight: 600; font-size: 14px; color: var(--text); }
.day-dist { font-family: var(--font-mono); font-size: 11px; color: var(--muted-light); }

.session-type-badge {
  font-family: var(--font-mono);
  font-size: 9px;
  letter-spacing: 0.1em;
  padding: 2px 6px;
  border-radius: 2px;
  display: inline-block;
}

.type--race     { background: var(--accent-soft); color: var(--accent); border: 1px solid var(--accent); }
.type--tempo    { background: var(--accent-soft); color: var(--accent); border: 1px solid var(--accent); }
.type--base     { background: var(--amber-soft);  color: var(--amber);  border: 1px solid var(--amber); }
.type--easy     { background: var(--green-soft);  color: var(--green);  border: 1px solid var(--green); }
.type--recovery { background: var(--raised);      color: var(--muted);  border: 1px solid var(--border); }
.type--rest     { background: var(--raised);      color: var(--muted);  border: 1px solid var(--border); }

.load-info { display: flex; gap: 16px; }
.te-row { display: flex; flex-direction: column; align-items: flex-end; }
.load-label { font-family: var(--font-mono); font-size: 8px; color: var(--muted); }
.load-val { font-family: var(--font-display); font-size: 20px; color: var(--text); }
.load-val--anaerobic { color: var(--accent); }

.empty-list {
  padding: 32px 20px;
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--muted);
  text-align: center;
}

/* Week comparison */
.comp-loading { padding: 20px; }
.comp-grid {
  display: flex;
  flex-direction: column;
}

.comp-row {
  display: grid;
  grid-template-columns: 160px 1fr 1fr 1fr;
  align-items: center;
  padding: 12px 20px;
  border-bottom: 1px solid var(--border);
  gap: 8px;
}
.comp-row--header { padding: 10px 20px 8px; }
.comp-row--last   { border-bottom: none; }

.comp-col-head {
  font-family: var(--font-mono);
  font-size: 8px;
  letter-spacing: 0.15em;
  color: var(--muted);
  text-align: right;
}

.comp-label {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--muted-light);
  letter-spacing: 0.05em;
}

.comp-val {
  font-family: var(--font-display);
  font-size: 18px;
  color: var(--text);
  text-align: right;
}

.comp-val--muted { color: var(--muted-light); font-size: 16px; }
.comp-pos { color: var(--green); }
.comp-neg { color: var(--accent); }
</style>
