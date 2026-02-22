<template>
  <UApp>
    <div class="shell">
      <header class="site-header">
        <div class="header-inner">
          <div class="logo">
            <svg class="logo-mark" viewBox="0 0 24 24" fill="none">
              <polygon points="12,2 22,8 22,16 12,22 2,16 2,8" fill="none" stroke="currentColor" stroke-width="1.5"/>
              <polygon points="12,6 18,10 18,14 12,18 6,14 6,10" fill="currentColor" opacity="0.3"/>
            </svg>
            <span class="logo-text">GARMIN<em>DASH</em></span>
          </div>
          <div class="header-right">
            <span class="header-tag">PERSONAL ATHLETICS</span>
            <UColorModeButton />
          </div>
        </div>
      </header>

      <main class="site-main">
        <NuxtPage />
      </main>

      <footer class="site-footer">
        <span>GARMIN DASHBOARD · 2026 · PERSONAL RUNNING COMMAND CENTER</span>
      </footer>
    </div>
  </UApp>
</template>

<script setup>
// Global layout
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Mono:wght@400;500&family=Outfit:wght@400;500;600;700;800&display=swap');

:root {
  --bg:           #07090E;
  --surface:      #0D1018;
  --raised:       #131722;
  --border:       #1C2130;
  --border-light: #242C3D;
  --accent:       #FF4521;
  --accent-soft:  rgba(255, 69, 33, 0.12);
  --accent-glow:  rgba(255, 69, 33, 0.3);
  --text:         #EBE6E0;
  --muted:        #4D5770;
  --muted-light:  #6B7A99;
  --green:        #27D47E;
  --green-soft:   rgba(39, 212, 126, 0.12);
  --amber:        #F59E0B;
  --amber-soft:   rgba(245, 158, 11, 0.12);
  --blue:         #4E9EFF;
  --blue-soft:    rgba(78, 158, 255, 0.12);
  --font-display: 'Bebas Neue', sans-serif;
  --font-mono:    'DM Mono', monospace;
  --font-body:    'Outfit', sans-serif;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body {
  background: var(--bg);
  color: var(--text);
  font-family: var(--font-body);
  font-size: 15px;
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
}

/* Nuxt UI overrides for dark theme */
.u-card {
  background: var(--surface) !important;
  border-color: var(--border) !important;
}
</style>

<style scoped>
.shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg);
}

.site-header {
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 50;
}

.header-inner {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 28px;
  height: 58px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-mark {
  width: 22px;
  height: 22px;
  color: var(--accent);
}

.logo-text {
  font-family: var(--font-display);
  font-size: 22px;
  letter-spacing: 0.12em;
  color: var(--text);
}

.logo-text em {
  font-style: normal;
  color: var(--accent);
  margin-left: 1px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-tag {
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.18em;
  color: var(--muted);
  text-transform: uppercase;
  border: 1px solid var(--border-light);
  padding: 3px 8px;
  border-radius: 2px;
}

.site-main {
  flex: 1;
  max-width: 1280px;
  width: 100%;
  margin: 0 auto;
  padding: 36px 28px;
}

.site-footer {
  border-top: 1px solid var(--border);
  text-align: center;
  padding: 14px;
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.18em;
  color: var(--muted);
}
</style>
