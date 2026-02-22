export const useWeeklyActivities = () => {
  const activities = ref([])
  const weeklyStats = ref({ current: [], previous: [] })
  const loading = ref(true)

  const getWeekRange = () => {
    // In a real app, this would be new Date()
    // For consistency with the session and project context, we use Feb 22, 2026
    const now = new Date('2026-02-22')
    const day = now.getDay()
    const monday = new Date(now)
    monday.setDate(now.getDate() - (day === 0 ? 6 : day - 1))
    monday.setHours(0, 0, 0, 0)
    
    return { 
      referenceDateStr: '2026-02-22'
    }
  }

  const fetchActivities = async () => {
    loading.value = true
    const { referenceDateStr } = getWeekRange()
    
    try {
      const data = await $fetch(`http://localhost:8000/stats/weekly`, {
        query: {
          date: referenceDateStr
        }
      })
      weeklyStats.value = data
      // For backward compatibility with existing components using activities.value
      activities.value = data.current || []
    } catch (e) {
      console.error('Failed to fetch weekly stats', e)
    } finally {
      loading.value = false
    }
  }

  const activitiesByDay = computed(() => {
    if (!weeklyStats.value.current.length) return []
    
    return weeklyStats.value.current.map(day => ({
      label: day.day_label,
      fullDay: day.full_day,
      date: day.date,
      training: day.training_intensity,
      dist: day.distance,
      count: day.count,
      rhr: day.rhr,
      sleep_hours: day.sleep_hours,
      sleep_score: day.sleep_score
    }))
  })

  const prevActivitiesByDay = computed(() => {
    if (!weeklyStats.value.previous.length) return []
    
    return weeklyStats.value.previous.map(day => ({
      label: day.day_label,
      fullDay: day.full_day,
      date: day.date,
      training: day.training_intensity,
      dist: day.distance,
      count: day.count,
      rhr: day.rhr,
      sleep_hours: day.sleep_hours,
      sleep_score: day.sleep_score
    }))
  })

  return {
    loading,
    activities,
    weeklyStats,
    activitiesByDay,
    prevActivitiesByDay,
    fetchActivities,
    getWeekRange
  }
}
