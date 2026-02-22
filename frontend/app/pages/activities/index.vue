<template>
  <div class="page">
    <div class="page-header">
      <button class="back-btn" @click="navigateTo('/')">
        <span>←</span> DASHBOARD
      </button>
      <div class="page-title-group">
        <span class="page-eyebrow">ALL ACTIVITIES</span>
        <h1 class="page-title">Activity Log</h1>
      </div>
      <div class="page-controls">
        <div class="limit-control">
          <span class="control-label">SHOW</span>
          <select v-model="limit" class="limit-select" @change="refresh()">
            <option :value="25">25</option>
            <option :value="50">50</option>
            <option :value="100">100</option>
          </select>
        </div>
      </div>
    </div>

    <div class="table-panel">
      <div v-if="pending" class="table-loading">
        <div v-for="n in 8" :key="n" class="loading-row">
          <div class="loading-cell w-lg shimmer"></div>
          <div class="loading-cell w-sm shimmer"></div>
          <div class="loading-cell w-sm shimmer"></div>
          <div class="loading-cell w-sm shimmer"></div>
          <div class="loading-cell w-sm shimmer"></div>
          <div class="loading-cell w-xs shimmer"></div>
        </div>
      </div>

      <div v-else-if="!activities?.length" class="table-empty">
        <div class="empty-icon">⬡</div>
        <p class="empty-text">No activities found.</p>
      </div>

      <UTable
        v-else
        :data="activities"
        :columns="columns"
        @select="(_, row) => navigateTo(`/activities/${row.original.activityId}`)"
      >
        <template #activityName-cell="{ row }">
          <div class="cell-name">
            <div class="type-dot" :style="{ background: activityColor(row.original.activityType?.typeKey) }"></div>
            <span class="name-text">{{ row.original.activityName }}</span>
          </div>
        </template>
        <template #startTimeLocal-cell="{ row }">
          <span class="cell-mono">{{ formatDate(row.original.startTimeLocal) }}</span>
        </template>
        <template #distance-cell="{ row }">
          <span class="cell-stat">{{ formatDistance(row.original.distance) }}</span>
        </template>
        <template #duration-cell="{ row }">
          <span class="cell-mono">{{ formatDuration(row.original.duration) }}</span>
        </template>
        <template #averageSpeed-cell="{ row }">
          <span class="cell-stat">{{ formatPace(row.original.averageSpeed) }}</span>
        </template>
        <template #averageHR-cell="{ row }">
          <span v-if="row.original.averageHR" class="cell-hr">
            {{ row.original.averageHR }} <span class="cell-unit">bpm</span>
          </span>
          <span v-else class="cell-muted">—</span>
        </template>
        <template #aerobicTrainingEffect-cell="{ row }">
          <div v-if="row.original.aerobicTrainingEffect" class="te-wrap">
            <span class="te-val">{{ row.original.aerobicTrainingEffect?.toFixed(1) }}</span>
            <div class="te-bar">
              <div class="te-fill" :style="{ width: (row.original.aerobicTrainingEffect / 5 * 100) + '%', background: teColor(row.original.aerobicTrainingEffect) }"></div>
            </div>
          </div>
          <span v-else class="cell-muted">—</span>
        </template>
      </UTable>
    </div>

    <div class="page-footer">
      <span class="footer-count">{{ activities?.length || 0 }} activities shown</span>
    </div>
  </div>
</template>

<script setup>
const limit = ref(25)

const { data: activities, pending, refresh } = await useFetch(
  () => `http://localhost:8000/activities/recent?limit=${limit.value}`,
  { watch: false }
)

const columns = [
  { accessorKey: 'activityName',           header: 'Activity' },
  { accessorKey: 'startTimeLocal',          header: 'Date' },
  { accessorKey: 'distance',               header: 'Distance' },
  { accessorKey: 'duration',               header: 'Duration' },
  { accessorKey: 'averageSpeed',            header: 'Pace' },
  { accessorKey: 'averageHR',              header: 'Avg HR' },
  { accessorKey: 'aerobicTrainingEffect',  header: 'Training Effect' },
]

const activityColor = (type) => {
  if (type === 'running')  return 'var(--accent)'
  if (type === 'cycling')  return 'var(--blue)'
  if (type === 'swimming') return 'var(--blue)'
  return 'var(--muted-light)'
}

const teColor = (te) => {
  if (te >= 4)  return 'var(--accent)'
  if (te >= 3)  return 'var(--amber)'
  return 'var(--green)'
}

const formatDate = (s) => {
  if (!s) return '—'
  return new Date(s).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' }).toUpperCase()
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
</script>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
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
  align-self: center;
}

.back-btn:hover { border-color: var(--accent); color: var(--accent); }

.page-title-group {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
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

.page-controls { display: flex; align-items: center; gap: 12px; }

.limit-control {
  display: flex;
  align-items: center;
  gap: 8px;
}

.control-label {
  font-family: var(--font-mono);
  font-size: 9px;
  letter-spacing: 0.2em;
  color: var(--muted);
}

.limit-select {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--text);
  background: var(--raised);
  border: 1px solid var(--border-light);
  border-radius: 2px;
  padding: 4px 8px;
  cursor: pointer;
}

/* Table panel */
.table-panel {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 4px;
  overflow: hidden;
}

.table-loading { padding: 20px 24px; display: flex; flex-direction: column; gap: 12px; }

.loading-row {
  display: flex;
  gap: 12px;
  align-items: center;
}

.loading-cell {
  height: 12px;
  border-radius: 2px;
}

.w-lg  { flex: 3; }
.w-sm  { flex: 1; }
.w-xs  { flex: 0.7; }

.shimmer {
  background: linear-gradient(90deg, var(--raised) 25%, var(--border) 50%, var(--raised) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0%   { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.table-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 64px 24px;
  gap: 10px;
}

.empty-icon { font-size: 32px; color: var(--border-light); }
.empty-text {
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 0.1em;
  color: var(--muted);
}

/* Cell styles */
.cell-name { display: flex; align-items: center; gap: 10px; }

.type-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}

.name-text { font-weight: 600; font-size: 13px; color: var(--text); }

.cell-mono {
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.08em;
  color: var(--muted-light);
}

.cell-stat {
  font-family: var(--font-display);
  font-size: 16px;
  color: var(--text);
}

.cell-hr {
  font-family: var(--font-display);
  font-size: 16px;
  color: var(--text);
}

.cell-unit {
  font-family: var(--font-mono);
  font-size: 9px;
  color: var(--muted-light);
}

.cell-muted {
  font-family: var(--font-mono);
  color: var(--muted);
  font-size: 13px;
}

.te-wrap { display: flex; align-items: center; gap: 8px; }
.te-val { font-family: var(--font-display); font-size: 16px; color: var(--text); width: 28px; }
.te-bar { flex: 1; height: 4px; background: var(--border); border-radius: 2px; overflow: hidden; }
.te-fill { height: 100%; border-radius: 2px; transition: width 0.6s ease; }

/* Page footer */
.page-footer {
  display: flex;
  justify-content: flex-end;
  padding: 4px 0;
}

.footer-count {
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.12em;
  color: var(--muted);
}
</style>

<style>
/* UTable overrides for clickable rows on activities page */
.clickable-rows tbody tr { cursor: pointer; }
</style>
