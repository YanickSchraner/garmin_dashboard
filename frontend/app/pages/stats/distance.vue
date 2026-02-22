<template>
  <div class="stats-page">
    <div class="page-header">
      <AppButton @click="navigateTo('/')" icon-left="←">
        DASHBOARD
      </AppButton>
      <div class="page-title-group">
        <span class="page-eyebrow">WEEKLY DRILLDOWN</span>
        <h1 class="page-title">Running Distance</h1>
      </div>
    </div>

    <div class="top-summary">
      <AppCard>
        <div class="summary-grid">
          <StatBlock label="TOTAL DISTANCE" value="28.4" unit="km" />
          <div class="stat-divider"></div>
          <StatBlock label="TARGET" value="30.0" unit="km" />
          <div class="stat-divider"></div>
          <StatBlock label="PROGRESS" value="94.7" unit="%" class="stat-pos" />
        </div>
      </AppCard>
    </div>

    <div class="main-grid">
      <!-- Distance Chart -->
      <AppCard label="Weekly Accumulation" sub-label="Daily Mileage vs Previous Week">
        <div class="chart-container">
          <div class="chart-y-axis">
            <span>12k</span>
            <span>10k</span>
            <span>8k</span>
            <span>6k</span>
            <span>4k</span>
            <span>2k</span>
            <span>0</span>
          </div>
          <div class="chart-area">
            <div v-for="(day, i) in weeklyData" :key="i" class="chart-column">
              <div class="bar-group">
                <div 
                  class="bar bar--prev" 
                  :style="{ height: (day.prevDist / 12 * 100) + '%' }"
                ></div>
                <div 
                  class="bar bar--curr" 
                  :style="{ height: (day.dist / 12 * 100) + '%' }"
                >
                  <span v-if="day.dist > 0" class="bar-val">{{ day.dist }}k</span>
                </div>
              </div>
              <div class="day-label">{{ day.label }}</div>
            </div>
          </div>
        </div>
        <div class="chart-legend">
          <div class="legend-item"><span class="legend-box bar--curr"></span> Current Week</div>
          <div class="legend-item"><span class="legend-box bar--prev"></span> Previous Week</div>
        </div>
      </AppCard>

      <!-- Activity List -->
      <AppCard label="Activities" sub-label="This Week">
        <div class="list-container">
          <div v-for="(day, i) in weeklyData.filter(d => d.dist > 0)" :key="i" class="list-row">
            <div class="day-info">
              <span class="day-name">{{ day.fullDay }}</span>
              <span class="day-type">Running Session</span>
            </div>
            <div class="dist-val">
              <span class="val-num">{{ day.dist }}</span>
              <span class="val-unit">KM</span>
            </div>
          </div>
          <div v-if="weeklyData.filter(d => d.dist > 0).length === 0" class="empty-list">
            No activities recorded this week.
          </div>
        </div>
      </AppCard>
    </div>
  </div>
</template>

<script setup>
const weeklyData = [
  { label: 'MON', fullDay: 'Monday',    dist: 5.2, prevDist: 0.0 },
  { label: 'TUE', fullDay: 'Tuesday',   dist: 8.4, prevDist: 6.2 },
  { label: 'WED', fullDay: 'Wednesday', dist: 0.0, prevDist: 10.5 },
  { label: 'THU', fullDay: 'Thursday',  dist: 4.8, prevDist: 0.0 },
  { label: 'FRI', fullDay: 'Friday',    dist: 10.0, prevDist: 5.5 },
  { label: 'SAT', fullDay: 'Saturday',  dist: 0.0, prevDist: 0.0 },
  { label: 'SUN', fullDay: 'Sunday',    dist: 0.0, prevDist: 3.0 },
]
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
  height: 300px;
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
  width: 30px;
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
  gap: 4px;
  padding-bottom: 2px;
}

.bar {
  width: 20px;
  border-radius: 2px 2px 0 0;
  transition: height 1s ease-out;
  position: relative;
}

.bar--curr { background: var(--amber); }
.bar--prev { background: var(--border); opacity: 0.5; }

.bar-val {
  position: absolute;
  top: -18px;
  left: 50%;
  transform: translateX(-50%);
  font-family: var(--font-mono);
  font-size: 9px;
  color: var(--text);
  white-space: nowrap;
}

.day-label {
  position: absolute;
  bottom: -25px;
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--muted);
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
.day-type { font-family: var(--font-mono); font-size: 10px; color: var(--muted); }

.dist-val { display: flex; align-items: baseline; gap: 4px; }
.val-num { font-family: var(--font-display); font-size: 24px; color: var(--text); }
.val-unit { font-family: var(--font-mono); font-size: 10px; color: var(--muted); }

.empty-list { padding: 40px; text-align: center; color: var(--muted); font-family: var(--font-mono); font-size: 12px; }
</style>
