<template>
  <div class="weekly-wrap">
    <div class="weekly-header">
      <div class="weekly-title-group">
        <h2 class="weekly-title">WEEKLY PERFORMANCE</h2>
        <span class="weekly-week">WK {{ currentWeek }}</span>
      </div>
      <div class="weekly-period">
        <span class="period-icon">◈</span>
        {{ weekRange }}
      </div>
    </div>

    <div v-if="loading" class="stats-strip">
      <div v-for="n in 4" :key="n" class="stat-item">
        <AppSkeleton height="60px" width="100%" />
      </div>
    </div>
    <div v-else class="stats-strip">
      <div class="stat-item" @click="navigateTo('/stats/sleep')">
        <div class="stat-icon-wrap stat-icon--sleep">
          <svg viewBox="0 0 20 20" fill="none">
            <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" fill="currentColor"/>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ sleepSummary.h }}<span class="stat-unit">h</span> {{ sleepSummary.m }}<span class="stat-unit">m</span></div>
          <div class="stat-label">AVG SLEEP</div>
          <div class="stat-delta" :class="sleepSummary.deltaMin >= 0 ? 'stat-delta--pos' : 'stat-delta--neg'">
            {{ sleepSummary.deltaMin >= 0 ? '+' : '' }}{{ sleepSummary.deltaMin }}m vs last week
          </div>
        </div>
      </div>

      <div class="stat-divider"></div>

      <div class="stat-item" @click="navigateTo('/stats/intensity')">
        <div class="stat-icon-wrap stat-icon--intensity">
          <svg viewBox="0 0 20 20" fill="currentColor">
            <path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zM8 7a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zM14 4a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z"/>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ intensitySummary.total }}<span class="stat-unit">min</span></div>
          <div class="stat-label">INTENSITY</div>
          <div class="stat-delta" :class="intensitySummary.delta >= 0 ? 'stat-delta--pos' : 'stat-delta--neg'">
            {{ intensitySummary.delta >= 0 ? '+' : '' }}{{ intensitySummary.delta }} min vs last week
          </div>
        </div>
      </div>

      <div class="stat-divider"></div>

      <div class="stat-item" @click="navigateTo('/stats/sessions')">
        <div class="stat-icon-wrap stat-icon--sessions">
          <svg viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clip-rule="evenodd"/>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ sessionSummary.count }}<span class="stat-unit">runs</span></div>
          <div class="stat-label">TRAININGS</div>
          <div class="stat-delta" :class="sessionSummary.count >= 3 ? 'stat-delta--goal' : ''">
            {{ sessionSummary.count >= 3 ? 'Goal reached' : (3 - sessionSummary.count) + ' more to goal' }}
          </div>
        </div>
      </div>

      <div class="stat-divider"></div>

      <div class="stat-item" @click="navigateTo('/stats/distance')">
        <div class="stat-icon-wrap stat-icon--distance">
          <svg viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd"/>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ distSummary.total.toFixed(1) }}<span class="stat-unit">km</span></div>
          <div class="stat-label">TOTAL DIST</div>
          <div class="stat-delta" :class="distSummary.delta >= 0 ? 'stat-delta--pos' : 'stat-delta--neg'">
            {{ distSummary.delta >= 0 ? '+' : '' }}{{ distSummary.delta.toFixed(1) }} km vs last week
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const { activitiesByDay, prevActivitiesByDay, currentIntensity, prevIntensity, loading, fetchActivities } = useWeeklyActivities()

onMounted(() => {
  fetchActivities()
})

const sleepSummary = computed(() => {
  const curr = activitiesByDay.value.map(d => d.sleep_hours).filter(v => v > 0)
  const prev = prevActivitiesByDay.value.map(d => d.sleep_hours).filter(v => v > 0)
  
  const avg = curr.length ? curr.reduce((a, b) => a + b, 0) / curr.length : 0
  const h = Math.floor(avg)
  const m = Math.round((avg - h) * 60)
  
  const prevAvg = prev.length ? prev.reduce((a, b) => a + b, 0) / prev.length : 0
  const deltaMin = Math.round((avg - prevAvg) * 60)
  
  return { h, m, deltaMin }
})

const intensitySummary = computed(() => {
  const total = Math.round(currentIntensity.value.reduce((a, b) => a + b, 0))
  const prevTotal = Math.round(prevIntensity.value.reduce((a, b) => a + b, 0))
  const delta = total - prevTotal
  
  return { total, delta }
})

const sessionSummary = computed(() => {
  const count = activitiesByDay.value.filter(d => d.count > 0).length
  return { count }
})

const distSummary = computed(() => {
  const total = activitiesByDay.value.reduce((a, b) => a + b.dist, 0)
  const prevTotal = prevActivitiesByDay.value.reduce((a, b) => a + b.dist, 0)
  const delta = total - prevTotal
  return { total, delta }
})

const currentWeek = computed(() => {
  const now = new Date()
  const start = new Date(now.getFullYear(), 0, 1)
  return Math.ceil(((now - start) / 86400000 + start.getDay() + 1) / 7)
})

const weekRange = computed(() => {
  const now = new Date()
  const day = now.getDay()
  const monday = new Date(now)
  monday.setDate(now.getDate() - (day === 0 ? 6 : day - 1))
  const sunday = new Date(monday)
  sunday.setDate(monday.getDate() + 6)

  const fmt = (d) => d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  return `${fmt(monday)} — ${fmt(sunday)}`.toUpperCase()
})
</script>

<style scoped>
.weekly-wrap {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 4px;
  overflow: hidden;
}

.weekly-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 28px;
  border-bottom: 1px solid var(--border);
  background: var(--raised);
}

.weekly-title-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.weekly-title {
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 0.2em;
  color: var(--muted-light);
  font-weight: 500;
}

.weekly-week {
  font-family: var(--font-display);
  font-size: 18px;
  color: var(--accent);
  letter-spacing: 0.08em;
}

.weekly-period {
  display: flex;
  align-items: center;
  gap: 7px;
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.14em;
  color: var(--muted);
}

.period-icon { color: var(--accent); font-size: 12px; }

.stats-strip {
  display: grid;
  grid-template-columns: 1fr auto 1fr auto 1fr auto 1fr;
  align-items: stretch;
  padding: 0;
}

@media (max-width: 640px) {
  .stats-strip {
    grid-template-columns: 1fr 1fr;
    grid-template-rows: 1fr 1fr;
  }
  .stat-divider { display: none; }
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 22px 28px;
  transition: background 0.2s;
  cursor: pointer;
}

.stat-item:hover { background: var(--raised); }

.stat-divider {
  width: 1px;
  background: var(--border);
  margin: 18px 0;
}

.stat-icon-wrap {
  width: 38px;
  height: 38px;
  border-radius: 3px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-icon-wrap svg { width: 18px; height: 18px; }

.stat-icon--sleep    { background: var(--blue-soft);   color: var(--blue); }
.stat-icon--intensity { background: rgba(255,165,0,0.12); color: var(--amber); }
.stat-icon--sessions { background: var(--green-soft);  color: var(--green); }
.stat-icon--distance { background: var(--amber-soft);  color: var(--amber); }

.stat-content { display: flex; flex-direction: column; gap: 2px; }

.stat-value {
  font-family: var(--font-display);
  font-size: 30px;
  color: var(--text);
  letter-spacing: 0.03em;
  line-height: 1;
}

.stat-unit {
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--muted-light);
  letter-spacing: 0.05em;
  margin-left: 2px;
}

.stat-label {
  font-family: var(--font-mono);
  font-size: 9px;
  letter-spacing: 0.2em;
  color: var(--muted);
  text-transform: uppercase;
  margin-top: 2px;
}

.stat-delta {
  font-family: var(--font-mono);
  font-size: 9px;
  letter-spacing: 0.05em;
  margin-top: 3px;
}

.stat-delta--pos  { color: var(--green); }
.stat-delta--neg  { color: var(--accent); }
.stat-delta--goal {
  color: var(--green);
  font-weight: 500;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}
</style>
