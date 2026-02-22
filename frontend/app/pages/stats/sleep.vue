<template>
  <div class="stats-page">
    <div class="page-header">
      <AppButton @click="navigateTo('/')" icon-left="←">
        DASHBOARD
      </AppButton>
      <div class="page-title-group">
        <span class="page-eyebrow">WEEKLY DRILLDOWN</span>
        <h1 class="page-title">Sleep Performance</h1>
      </div>
    </div>

    <div class="top-summary">
      <AppCard>
        <div class="summary-grid">
          <StatBlock label="WEEKLY AVG" value="7h 45m" />
          <div class="stat-divider"></div>
          <StatBlock label="AVG SCORE" value="82" unit="/100" />
          <div class="stat-divider"></div>
          <StatBlock label="VS LAST WEEK" value="+15m" :class="'stat-pos'" />
        </div>
      </AppCard>
    </div>

    <div class="main-grid">
      <!-- Daily Breakdown Chart -->
      <AppCard label="Daily Breakdown" sub-label="Current Week vs Previous">
        <div class="chart-container">
          <div class="chart-y-axis">
            <span>10h</span>
            <span>8h</span>
            <span>6h</span>
            <span>4h</span>
            <span>2h</span>
            <span>0h</span>
          </div>
          <div class="chart-area">
            <div v-for="(day, i) in weeklyData" :key="i" class="chart-column">
              <div class="bar-group">
                <!-- Previous week shadow bar -->
                <div 
                  class="bar bar--prev" 
                  :style="{ height: (day.prevHours / 10 * 100) + '%' }"
                ></div>
                <!-- Current week bar -->
                <div 
                  class="bar bar--curr" 
                  :style="{ height: (day.hours / 10 * 100) + '%' }"
                >
                  <span class="bar-val">{{ day.hours }}h</span>
                </div>
              </div>
              <div class="day-label">{{ day.label }}</div>
              <!-- Training intensity indicator -->
              <div 
                v-if="day.training" 
                class="training-dot" 
                :class="'training--' + day.training"
                :title="'Training: ' + day.training + ' intensity'"
              ></div>
            </div>
          </div>
        </div>
        <div class="chart-legend">
          <div class="legend-item"><span class="legend-box bar--curr"></span> Current Week</div>
          <div class="legend-item"><span class="legend-box bar--prev"></span> Previous Week</div>
          <div class="legend-item"><span class="legend-dot training--high"></span> High Intensity</div>
          <div class="legend-item"><span class="legend-dot training--medium"></span> Medium</div>
          <div class="legend-item"><span class="legend-dot training--low"></span> Low</div>
        </div>
      </AppCard>

      <!-- Sleep Score Table -->
      <AppCard label="Sleep Quality" sub-label="Score & Recovery">
        <div class="score-list">
          <div v-for="(day, i) in weeklyData" :key="i" class="score-row">
            <div class="score-day">
              <span class="day-name">{{ day.fullDay }}</span>
              <span class="day-date">{{ day.date }}</span>
            </div>
            <div class="score-viz">
              <div class="score-bar-bg">
                <div class="score-bar-fill" :style="{ width: day.score + '%', background: getScoreColor(day.score) }"></div>
              </div>
              <span class="score-num" :style="{ color: getScoreColor(day.score) }">{{ day.score }}</span>
            </div>
            <div class="score-meta">
              <span class="meta-label">RECOVERY</span>
              <span class="meta-val">{{ day.recovery }}</span>
            </div>
          </div>
        </div>
      </AppCard>
    </div>
  </div>
</template>

<script setup>
const weeklyData = [
  { label: 'MON', fullDay: 'Monday',    date: 'Feb 16', hours: 7.2, prevHours: 7.5, score: 78, training: 'medium', recovery: 'Fair' },
  { label: 'TUE', fullDay: 'Tuesday',   date: 'Feb 17', hours: 8.1, prevHours: 6.8, score: 88, training: 'high',   recovery: 'Good' },
  { label: 'WED', fullDay: 'Wednesday', date: 'Feb 18', hours: 7.5, prevHours: 7.2, score: 82, training: null,     recovery: 'Good' },
  { label: 'THU', fullDay: 'Thursday',  date: 'Feb 19', hours: 6.9, prevHours: 7.8, score: 72, training: 'low',    recovery: 'Needs Rest' },
  { label: 'FRI', fullDay: 'Friday',    date: 'Feb 20', hours: 8.4, prevHours: 7.0, score: 92, training: 'medium', recovery: 'Excellent' },
  { label: 'SAT', fullDay: 'Saturday',  date: 'Feb 21', hours: 8.8, prevHours: 8.2, score: 94, training: 'high',   recovery: 'Excellent' },
  { label: 'SUN', fullDay: 'Sunday',    date: 'Feb 22', hours: 7.8, prevHours: 8.5, score: 85, training: null,     recovery: 'Good' },
]

const getScoreColor = (s) => {
  if (s >= 90) return 'var(--green)'
  if (s >= 80) return 'var(--blue)'
  if (s >= 70) return 'var(--amber)'
  return 'var(--accent)'
}
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
  padding-bottom: 25px;
  text-align: right;
  width: 30px;
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
  width: 24px;
  border-radius: 2px 2px 0 0;
  transition: height 1s ease-out;
  position: relative;
}

.bar--curr { background: var(--blue); }
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

.training-dot {
  position: absolute;
  bottom: -45px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.training--high   { background: var(--accent); }
.training--medium { background: var(--amber); }
.training--low    { background: var(--green); }

.chart-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  padding: 0 20px 20px;
  border-top: 1px solid var(--border);
  padding-top: 20px;
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
.legend-dot { width: 8px; height: 8px; border-radius: 50%; }

/* Score list */
.score-list {
  padding: 10px 0;
}

.score-row {
  display: grid;
  grid-template-columns: 100px 1fr 100px;
  align-items: center;
  padding: 12px 20px;
  border-bottom: 1px solid var(--border);
}

.score-row:last-child { border-bottom: none; }

.score-day { display: flex; flex-direction: column; }
.day-name { font-family: var(--font-body); font-weight: 600; font-size: 13px; color: var(--text); }
.day-date { font-family: var(--font-mono); font-size: 10px; color: var(--muted); }

.score-viz { display: flex; align-items: center; gap: 12px; }
.score-bar-bg { flex: 1; height: 4px; background: var(--border); border-radius: 2px; overflow: hidden; }
.score-bar-fill { height: 100%; border-radius: 2px; transition: width 1s ease; }
.score-num { font-family: var(--font-display); font-size: 20px; width: 30px; text-align: right; }

.score-meta { display: flex; flex-direction: column; align-items: flex-end; }
.meta-label { font-family: var(--font-mono); font-size: 8px; color: var(--muted); letter-spacing: 0.1em; }
.meta-val { font-family: var(--font-mono); font-size: 11px; color: var(--muted-light); }
</style>
