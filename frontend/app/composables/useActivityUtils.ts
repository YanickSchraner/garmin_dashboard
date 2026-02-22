export const useActivityUtils = () => {
  const getActivityColor = (type: string | undefined) => {
    if (!type) return 'var(--muted-light)'
    const t = type.toLowerCase()
    if (t === 'running')  return 'var(--accent)'
    if (t === 'cycling' || t === 'swimming') return 'var(--blue)'
    return 'var(--muted-light)'
  }

  const formatActivityType = (type: string | undefined) => {
    if (!type) return 'ACTIVITY'
    return type.replace(/_/g, ' ').toUpperCase()
  }

  const getTEColor = (te: number | undefined) => {
    if (!te) return 'var(--muted-light)'
    if (te >= 4)  return 'var(--accent)'
    if (te >= 3)  return 'var(--amber)'
    return 'var(--green)'
  }

  return {
    getActivityColor,
    formatActivityType,
    getTEColor
  }
}
