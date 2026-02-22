<template>
  <div class="stats-page">
    <div class="page-header">
      <AppButton @click="navigateTo('/')" icon-left="←">
        DASHBOARD
      </AppButton>
      <div class="page-title-group">
        <span class="page-eyebrow">WEEKLY DRILLDOWN</span>
        <h1 class="page-title">Resting Heart Rate</h1>
      </div>
    </div>

    <div class="top-summary">
      <AppCard>
        <div class="summary-grid">
          <StatBlock label="WEEKLY AVG" value="52" unit="bpm" />
          <div class="stat-divider"></div>
          <StatBlock label="MIN RHR" value="48" unit="bpm" />
          <div class="stat-divider"></div>
          <StatBlock label="VS LAST WEEK" value="-2 bpm" class="stat-pos" />
        </div>
      </AppCard>
    </div>

    <div class="main-grid">
      <!-- RHR Trend Chart -->
      <AppCard label="Daily RHR Trend" sub-label="Current Week vs Previous">
        <div class="chart-container">
          <div class="chart-y-axis">
            <span>65</span>
            <span>60</span>
            <span>55</span>
            <span>50</span>
            <span>45</span>
          </div>
          <div class="chart-area">
            <svg class="trend-svg" viewBox="0 0 700 300" preserveAspectRatio="none">
              <!-- Grid lines -->
              <line v-for="n in 5" :key="n" x1="0" :y1="(n-1)*75" x2="700" :y2="(n-1)*75" stroke="var(--border)" stroke-width="0.5" stroke-dasharray="4" />
              
              <!-- Previous week line -->
              <path 
                class="line-prev" 
                :d="prevLinePath" 
                fill="none" 
                stroke="var(--border)" 
                stroke-width="2" 
                stroke-dasharray="5,5" 
                opacity="0.6"
              />
              
              <!-- Current week line -->
              <path 
                class="line-curr" 
                :d="currLinePath" 
                fill="none" 
                stroke="var(--accent)" 
                stroke-width="3" 
              />
              
              <!-- Data points -->
              <circle 
                v-for="(day, i) in weeklyData" 
                :key="'p'+i" 
                :cx="getX(i)" 
                :cy="getY(day.rhr)" 
                r="4" 
                fill="var(--surface)" 
                stroke="var(--accent)" 
                stroke-width="2" 
              />
            </svg>
            <div class="chart-labels">
              <div v-for="(day, i) in weeklyData" :key="'l'+i" class="day-label" :style="{ left: (i * 100 / 6) + '%' }">
                {{ day.label }}
              </div>
            </div>
          </div>
        </div>
        <div class="chart-legend">
          <div class="legend-item"><span class="legend-line line--curr"></span> Current Week</div>
          <div class="legend-item"><span class="legend-line line--prev"></span> Previous Week</div>
        </div>
      </AppCard>

      <!-- Training & Stress -->
      <AppCard label="Training & Stress" sub-label="RHR Correlation">
        <div class="list-container">
          <div v-for="(day, i) in weeklyData" :key="i" class="list-row">
            <div class="day-info">
              <span class="day-name">{{ day.fullDay }}</span>
              <div class="training-badge" v-if="day.training" :class="'training--' + day.training">
                {{ day.training.toUpperCase() }} INTENSITY
              </div>
              <span v-else class="no-training">REST DAY</span>
            </div>
            <div class="rhr-val">
              <span class="val-num">{{ day.rhr }}</span>
              <span class="val-unit">BPM</span>
            </div>
          </div>
        </div>
      </AppCard>
    </div>
  </div>
</template>

<script setup>
const weeklyData = [
  { label: 'MON', fullDay: 'Monday',    rhr: 54, prevRhr: 55, training: 'medium' },
  { label: 'TUE', fullDay: 'Tuesday',   rhr: 52, prevRhr: 56, training: 'high' },
  { label: 'WED', fullDay: 'Wednesday', rhr: 51, prevRhr: 54, training: null },
  { label: 'THU', fullDay: 'Thursday',  rhr: 53, prevRhr: 53, training: 'low' },
  { label: 'FRI', fullDay: 'Friday',    rhr: 50, prevRhr: 52, training: 'medium' },
  { label: 'SAT', fullDay: 'Saturday',  rhr: 48, prevRhr: 50, training: 'high' },
  { label: 'SUN', fullDay: 'Sunday',    rhr: 52, prevRhr: 51, training: null },
]

const getX = (index) => (index * 700 / 6)
const getY = (val) => {
  const min = 45
  const max = 65
  return 300 - ((val - min) / (max - min) * 300)
}

const currLinePath = computed(() => {
  return weeklyData.reduce((path, day, i) => {
    return path + (i === 0 ? 'M' : ' L') + getX(i) + ' ' + getY(day.rhr)
  }, '')
})

const prevLinePath = computed(() => {
  return weeklyData.reduce((path, day, i) => {
    return path + (i === 0 ? 'M' : ' L') + getX(i) + ' ' + getY(day.prevRhr)
  }, '')
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
  position: relative;
  border-bottom: 1px solid var(--border);
  border-left: 1px solid var(--border);
}

.trend-svg {
  width: 100%;
  height: 100%;
  overflow: visible;
}

.chart-labels {
  position: absolute;
  bottom: -25px;
  left: 0;
  right: 0;
  display: flex;
}

.day-label {
  position: absolute;
  transform: translateX(-50%);
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

.legend-line { width: 24px; height: 3px; border-radius: 2px; }
.line--curr { background: var(--accent); }
.line--prev { border-top: 2px dashed var(--border); height: 0; }

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

.rhr-val { display: flex; align-items: baseline; gap: 4px; }
.val-num { font-family: var(--font-display); font-size: 24px; color: var(--text); }
.val-unit { font-family: var(--font-mono); font-size: 10px; color: var(--muted); }
</style>
