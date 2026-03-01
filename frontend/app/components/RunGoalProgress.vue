<template>
  <div class="goal-card">
    <!-- Top accent line -->
    <div class="accent-line"></div>

    <div class="goal-body">
      <!-- Left: Main stats -->
      <div class="goal-left">
        <div class="goal-meta">
          <span class="goal-meta-tag">ANNUAL GOAL · {{ year }}</span>
          <div class="goal-status-chip" :class="statusClass">
            <span class="chip-dot"></span>
            {{ statusText }}
          </div>
        </div>

        <div class="goal-count" :class="{ 'is-loading': loading }">
          <span class="count-actual">{{ loading ? '—' : actual }}</span>
          <div class="count-right">
            <span class="count-slash">/</span>
            <span class="count-total">{{ goal }}</span>
            <span class="count-unit">RUNS</span>
          </div>
        </div>

        <div class="goal-subrow">
          <div class="subrow-item">
            <span class="subrow-label">COMPLETED</span>
            <span class="subrow-val">{{ percent.toFixed(1) }}%</span>
          </div>
          <div class="subrow-divider"></div>
          <div class="subrow-item">
            <span class="subrow-label">TARGET TO DATE</span>
            <span class="subrow-val">{{ targetToDate }}</span>
          </div>
          <div class="subrow-divider"></div>
          <div class="subrow-item">
            <span class="subrow-label">REMAINING</span>
            <span class="subrow-val">{{ goal - actual }}</span>
          </div>
        </div>

        <!-- Progress track -->
        <div class="progress-track">
          <div class="track-bar">
            <div class="track-actual" :style="{ width: Math.min(actualPct, 100) + '%' }"></div>
            <div
              v-if="targetPct > 0 && targetPct <= 100"
              class="track-target-marker"
              :style="{ left: targetPct + '%' }"
            >
              <span class="marker-label">TARGET</span>
            </div>
          </div>
          <div class="track-ticks">
            <span v-for="n in 5" :key="n" class="track-tick">{{ Math.round(goal / 4 * (n - 1)) }}</span>
          </div>
        </div>
      </div>

      <!-- Right: Progress ring -->
      <div class="goal-right">
        <div class="ring-wrap">
          <svg class="ring-svg" viewBox="0 0 200 200">
            <!-- Background track -->
            <circle
              cx="100" cy="100" r="82"
              fill="none"
              class="ring-track"
              stroke-width="10"
            />
            <!-- Decorative dashes on track -->
            <circle
              cx="100" cy="100" r="82"
              fill="none"
              class="ring-track-dashes"
              stroke-width="10"
              stroke-dasharray="4 8"
              transform="rotate(-90 100 100)"
            />
            <!-- Progress arc -->
            <circle
              cx="100" cy="100" r="82"
              fill="none"
              :stroke="ringColor"
              stroke-width="10"
              stroke-linecap="round"
              :stroke-dasharray="circumference"
              :stroke-dashoffset="loading ? circumference : dashOffset"
              transform="rotate(-90 100 100)"
              class="progress-arc"
            />
            <!-- Target indicator tick -->
            <line
              v-if="targetPct > 0 && targetPct <= 100"
              :x1="targetTickX1" :y1="targetTickY1"
              :x2="targetTickX2" :y2="targetTickY2"
              class="ring-tick"
              stroke-width="2"
              stroke-linecap="round"
            />
          </svg>
          <div class="ring-center">
            <div class="ring-pct">
              <span class="ring-num">{{ loading ? '—' : Math.round(percent) }}</span>
              <span class="ring-sym">%</span>
            </div>
            <div class="ring-label">of goal</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div class="goal-footer">
      <div class="footer-date">
        <span class="footer-icon">◷</span>
        {{ formattedDate }}
      </div>
      <button
        class="sync-btn"
        :class="{ 'is-loading': loading }"
        :disabled="loading"
        @click="$emit('refresh')"
      >
        <span class="sync-spinner" :class="{ 'spin': loading }">↻</span>
        SYNC GARMIN
      </button>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  goal:         { type: Number, default: 104 },
  actual:       { type: Number, default: 0 },
  targetToDate: { type: Number, default: 0 },
  percent:      { type: Number, default: 0 },
  status:       { type: String, default: 'behind' },
  year:         { type: Number, default: () => new Date().getFullYear() },
  loading:      { type: Boolean, default: false }
})

const emit = defineEmits(['refresh'])

const circumference = 2 * Math.PI * 82 // ≈ 515.2

const dashOffset = computed(() =>
  circumference * (1 - Math.min(props.percent, 100) / 100)
)

const actualPct  = computed(() => (props.actual / props.goal) * 100)
const targetPct  = computed(() => (props.targetToDate / props.goal) * 100)

// Target tick on SVG ring
const targetAngle = computed(() => {
  const pct = Math.min(props.targetToDate / props.goal, 1)
  return -Math.PI / 2 + pct * 2 * Math.PI
})
const targetTickX1 = computed(() => 100 + 76 * Math.cos(targetAngle.value))
const targetTickY1 = computed(() => 100 + 76 * Math.sin(targetAngle.value))
const targetTickX2 = computed(() => 100 + 90 * Math.cos(targetAngle.value))
const targetTickY2 = computed(() => 100 + 90 * Math.sin(targetAngle.value))

const statusText = computed(() => {
  if (props.status === 'ahead') return 'AHEAD'
  if (props.actual >= props.targetToDate) return 'ON TRACK'
  return 'BEHIND'
})

const statusClass = computed(() => {
  if (props.status === 'ahead') return 'chip--green'
  if (props.actual >= props.targetToDate) return 'chip--blue'
  return 'chip--amber'
})

const ringColor = computed(() => {
  if (props.status === 'ahead') return 'var(--green)'
  if (props.actual >= props.targetToDate) return 'var(--accent)'
  return 'var(--amber)'
})

const formattedDate = computed(() => {
  return new Date().toLocaleDateString('en-US', {
    weekday: 'long', month: 'long', day: 'numeric', year: 'numeric'
  }).toUpperCase()
})
</script>

<style scoped>
.goal-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 4px;
  overflow: hidden;
  position: relative;
}

.accent-line {
  height: 3px;
  background: linear-gradient(90deg, var(--accent) 0%, transparent 70%);
}

.goal-body {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 32px;
  padding: 28px 32px;
  align-items: center;
}

@media (max-width: 640px) {
  .goal-body { grid-template-columns: 1fr; }
  .goal-right { display: none; }
}

/* Left */
.goal-left { flex: 1; }

.goal-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.goal-meta-tag {
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.2em;
  color: var(--muted);
  text-transform: uppercase;
}

.goal-status-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.15em;
  padding: 3px 8px;
  border-radius: 2px;
  font-weight: 500;
}

.chip-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: currentColor;
}

.chip--green  { background: var(--green-soft);  color: var(--green); }
.chip--amber  { background: var(--amber-soft);  color: var(--amber); }
.chip--blue   { background: var(--accent-soft); color: var(--accent); }

.goal-count {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-bottom: 20px;
  transition: opacity 0.3s;
}

.goal-count.is-loading { opacity: 0.4; }

.count-actual {
  font-family: var(--font-display);
  font-size: clamp(72px, 10vw, 112px);
  line-height: 0.9;
  color: var(--text);
  letter-spacing: 0.02em;
}

.count-right {
  display: flex;
  flex-direction: column;
  padding-bottom: 6px;
}

.count-slash {
  font-family: var(--font-display);
  font-size: 28px;
  color: var(--border-light);
  line-height: 1;
}

.count-total {
  font-family: var(--font-display);
  font-size: 36px;
  color: var(--muted-light);
  line-height: 1;
}

.count-unit {
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.2em;
  color: var(--muted);
  margin-top: 4px;
}

/* Sub row */
.goal-subrow {
  display: flex;
  align-items: center;
  gap: 0;
  margin-bottom: 20px;
}

.subrow-item {
  display: flex;
  flex-direction: column;
  gap: 3px;
  padding: 0 20px 0 0;
}

.subrow-item:first-child { padding-left: 0; }

.subrow-label {
  font-family: var(--font-mono);
  font-size: 9px;
  letter-spacing: 0.18em;
  color: var(--muted);
  text-transform: uppercase;
}

.subrow-val {
  font-family: var(--font-display);
  font-size: 22px;
  color: var(--text);
  letter-spacing: 0.03em;
}

.subrow-divider {
  width: 1px;
  height: 28px;
  background: var(--border-light);
  margin: 0 20px 0 0;
  flex-shrink: 0;
}

/* Progress track */
.progress-track { margin-top: 4px; }

.track-bar {
  position: relative;
  height: 6px;
  background: var(--border);
  border-radius: 3px;
  overflow: visible;
  margin-bottom: 8px;
}

.track-actual {
  height: 100%;
  background: var(--accent);
  border-radius: 3px;
  transition: width 1.2s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: 0 0 12px var(--accent-glow);
}

.track-target-marker {
  position: absolute;
  top: -14px;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.track-target-marker::after {
  content: '';
  display: block;
  width: 2px;
  height: 20px;
  background: rgba(255, 255, 255, 0.25);
  border-radius: 1px;
  margin-top: 2px;
}

.marker-label {
  font-family: var(--font-mono);
  font-size: 8px;
  letter-spacing: 0.12em;
  color: rgba(255, 255, 255, 0.3);
}

.track-ticks {
  display: flex;
  justify-content: space-between;
  padding: 0 1px;
}

.track-tick {
  font-family: var(--font-mono);
  font-size: 9px;
  color: var(--muted);
  letter-spacing: 0.05em;
}

/* Right: Ring */
.goal-right { flex-shrink: 0; }

.ring-wrap {
  position: relative;
  width: 180px;
  height: 180px;
}

.ring-svg {
  width: 100%;
  height: 100%;
}

.ring-track {
  stroke: var(--border);
}

.ring-track-dashes {
  stroke: var(--raised);
}

.ring-tick {
  stroke: var(--muted-light);
  opacity: 0.6;
}

.progress-arc {
  transition: stroke-dashoffset 1.4s cubic-bezier(0.16, 1, 0.3, 1),
              stroke 0.4s ease;
}

.ring-center {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.ring-pct {
  display: flex;
  align-items: flex-start;
  line-height: 1;
}

.ring-num {
  font-family: var(--font-display);
  font-size: 52px;
  color: var(--text);
  letter-spacing: 0.02em;
}

.ring-sym {
  font-family: var(--font-display);
  font-size: 22px;
  color: var(--muted-light);
  margin-top: 6px;
}

.ring-label {
  font-family: var(--font-mono);
  font-size: 9px;
  letter-spacing: 0.18em;
  color: var(--muted);
  text-transform: uppercase;
  margin-top: 4px;
}

/* Footer */
.goal-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 32px;
  border-top: 1px solid var(--border);
  background: var(--raised);
}

.footer-date {
  display: flex;
  align-items: center;
  gap: 7px;
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.14em;
  color: var(--muted);
  text-transform: uppercase;
}

.footer-icon { font-size: 13px; }

.sync-btn {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.18em;
  color: var(--muted-light);
  background: transparent;
  border: 1px solid var(--border-light);
  padding: 5px 12px;
  border-radius: 2px;
  cursor: pointer;
  transition: all 0.2s;
  text-transform: uppercase;
}

.sync-btn:hover:not(:disabled) {
  border-color: var(--accent);
  color: var(--accent);
}

.sync-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.sync-spinner { display: inline-block; font-size: 14px; }
.sync-spinner.spin { animation: spin 1s linear infinite; }

@keyframes spin { to { transform: rotate(360deg); } }
</style>
