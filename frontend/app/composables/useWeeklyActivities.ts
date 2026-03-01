export const useWeeklyActivities = () => {
  const activities = ref([])
  const weeklyStats = ref({ current: [], previous: [] })
  const loading = ref(true)

  const getWeekRange = () => {
    const now = new Date()
    const referenceDateStr = now.toISOString().split('T')[0]
    return { referenceDateStr }
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
      // For backward compatibility
      activities.value = data.current?.days || []
    } catch (e) {
      console.error('Failed to fetch weekly stats', e)
    } finally {
      loading.value = false
    }
  }

  const activitiesByDay = computed(() => {
    if (!weeklyStats.value.current?.days?.length) return []
    
    return weeklyStats.value.current.days.map(day => ({
      label: day.day_label,
      fullDay: day.full_day,
      date: day.date,
      training: day.training_intensity,
      dist: day.distance,
      count: day.count,
      rhr: day.rhr,
      sleep_hours: day.sleep_hours,
      sleep_score: day.sleep_score,
      sleep_hrv_status: day.sleep_hrv_status,
      aerobic_te: day.aerobic_te ?? 0,
      anaerobic_te: day.anaerobic_te ?? 0,
    }))
  })

  const prevActivitiesByDay = computed(() => {
    if (!weeklyStats.value.previous?.days?.length) return []
    
    return weeklyStats.value.previous.days.map(day => ({
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

  const currentIntensity = computed(() => weeklyStats.value.current?.zones || [0,0,0,0,0,0])
  const prevIntensity = computed(() => weeklyStats.value.previous?.zones || [0,0,0,0,0,0])

  return {
    loading,
    activities,
    weeklyStats,
    activitiesByDay,
    prevActivitiesByDay,
    currentIntensity,
    prevIntensity,
    fetchActivities,
    getWeekRange
  }
}
