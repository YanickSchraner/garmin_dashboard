<template>
  <div class="stats-page">
    <div class="page-header">
      <AppButton @click="navigateTo('/')" icon-left="←">
        DASHBOARD
      </AppButton>
      <div class="page-title-group">
        <span class="page-eyebrow">WEEKLY DRILLDOWN</span>
        <h1 class="page-title">Intensity Distribution</h1>
      </div>
    </div>

    <div class="top-summary">
      <AppCard>
        <div v-if="loading" class="summary-grid">
          <AppSkeleton v-for="n in 3" :key="n" height="40px" width="100px" />
        </div>
        <div v-else class="summary-grid">
          <StatBlock label="TOTAL TRAINING" :value="Math.round(totalMinutes)" unit="min" />
          <div class="stat-divider"></div>
          <StatBlock label="HIGH INTENSITY" :value="Math.round(currentIntensity[4] + currentIntensity[5])" unit="min" />
          <div class="stat-divider"></div>
          <StatBlock label="VS LAST WEEK" :value="(totalMinutes - prevTotalMinutes).toFixed(0)" unit="min" :class="totalMinutes >= prevTotalMinutes ? 'stat-pos' : 'stat-neg'" />
        </div>
      </AppCard>
    </div>

    <div class="main-grid">
      <!-- Intensity Distribution Chart -->
      <AppCard label="Time in HR Zones" sub-label="Current Week Breakdown">
        <div v-if="loading" class="chart-loading">
          <AppSkeleton height="200px" />
        </div>
        <div v-else class="chart-container">
          <div class="intensity-bars">
            <div v-for="(mins, i) in currentIntensity.slice(1)" :key="i" class="intensity-row">
              <div class="zone-label">ZONE {{ i + 1 }}</div>
              <div class="bar-track">
                <div
                  class="bar-fill"
                  :class="'zone--' + (i + 1)"
                  :style="{ width: (maxZoneMinutes > 0 ? (mins / maxZoneMinutes * 100) : 0) + '%' }"
                >
                  <span v-if="mins > 0" class="bar-val" :class="{ 'bar-val--inside': isBarLong(mins) }">{{ Math.round(mins) }}m</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="chart-legend">
          <div v-for="i in 5" :key="i" class="legend-item">
            <span class="legend-box" :class="'zone--' + i"></span>
            Z{{ i }}
          </div>
        </div>
      </AppCard>

      <!-- Training Breakdown -->
      <AppCard label="Daily Training" sub-label="Intensity Mix">
        <div v-if="loading" class="list-loading">
          <AppSkeleton v-for="n in 5" :key="n" height="40px" style="margin-bottom:8px" />
        </div>
        <div v-else class="list-container">
          <div v-for="(day, i) in activitiesByDay" :key="i" class="list-row">
            <div class="day-info">
              <span class="day-name">{{ day.fullDay }}</span>
              <div class="training-badge" v-if="day.training" :class="'training--' + day.training">
                {{ day.training.toUpperCase() }}
              </div>
              <span v-else class="no-training">REST DAY</span>
            </div>
            <div class="te-val" v-if="day.training">
              <span class="val-label">TE</span>
              <span class="val-num">{{ day.aerobic_te.toFixed(1) }}</span>
            </div>
          </div>
        </div>
      </AppCard>
    </div>
  </div>
</template>

<script setup>
const { activitiesByDay, currentIntensity, prevIntensity, loading, fetchActivities } = useWeeklyActivities()

onMounted(() => {
  fetchActivities()
})

const totalMinutes = computed(() => {
  return currentIntensity.value.reduce((a, b) => a + b, 0)
})

const prevTotalMinutes = computed(() => {
  return prevIntensity.value.reduce((a, b) => a + b, 0)
})

const maxZoneMinutes = computed(() => {
  return Math.max(...currentIntensity.value.slice(1), 1)
})

const isBarLong = (mins) => maxZoneMinutes.value > 0 && (mins / maxZoneMinutes.value) > 0.75
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
.stat-neg { color: var(--accent); }

.main-grid {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 24px;
}

@media (max-width: 1024px) {
  .main-grid { grid-template-columns: 1fr; }
}

/* Chart Styles */
.chart-loading { padding: 40px; }

.chart-container {
  padding: 30px 20px;
}

.intensity-bars {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.intensity-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.zone-label {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--muted);
  width: 50px;
}

.bar-track {
  flex: 1;
  height: 24px;
  background: var(--raised);
  border-radius: 2px;
  overflow: hidden;
  position: relative;
}

.bar-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 1s ease-out;
  position: relative;
}

.bar-val {
  position: absolute;
  right: -35px;
  top: 50%;
  transform: translateY(-50%);
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--text);
  white-space: nowrap;
}

.bar-val--inside {
  right: 8px;
  color: #fff;
}

.zone--1 { background: #94a3b8; }
.zone--2 { background: var(--green); }
.zone--3 { background: var(--amber); }
.zone--4 { background: #f97316; }
.zone--5 { background: var(--accent); }

.chart-legend {
  display: flex;
  justify-content: space-between;
  padding: 20px;
  border-top: 1px solid var(--border);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-family: var(--font-mono);
  font-size: 9px;
  color: var(--muted-light);
}

.legend-box { width: 10px; height: 10px; border-radius: 2px; }

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
.no-training { font-family: var(--font-mono); font-size: 9px; color: var(--muted); letter-spacing: 0.1em; }

.te-val { display: flex; flex-direction: column; align-items: flex-end; }
.val-label { font-family: var(--font-mono); font-size: 8px; color: var(--muted); }
.val-num { font-family: var(--font-display); font-size: 20px; color: var(--text); }
</style>