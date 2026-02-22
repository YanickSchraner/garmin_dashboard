export const useFormatters = () => {
  const formatDate = (s: string | Date | undefined, options: Intl.DateTimeFormatOptions = { weekday: 'short', month: 'short', day: 'numeric' }) => {
    if (!s) return '—'
    return new Date(s).toLocaleDateString('en-US', options).toUpperCase()
  }

  const formatDistance = (m: number | undefined) => {
    if (m === undefined || m === null) return '—'
    return (m / 1000).toFixed(2) + ' km'
  }

  const formatDuration = (s: number | undefined) => {
    if (s === undefined || s === null) return '—'
    const h = Math.floor(s / 3600)
    const m = Math.floor((s % 3600) / 60)
    const sec = Math.round(s % 60)
    if (h > 0) return `${h}:${String(m).padStart(2, '0')}:${String(sec).padStart(2, '0')}`
    return `${m}:${String(sec).padStart(2, '0')}`
  }

  const formatPace = (mps: number | undefined) => {
    if (!mps) return '—'
    const spk = 1000 / mps
    const m = Math.floor(spk / 60)
    const s = Math.round(spk % 60)
    return `${m}:${String(s).padStart(2, '0')}/km`
  }

  return {
    formatDate,
    formatDistance,
    formatDuration,
    formatPace
  }
}
