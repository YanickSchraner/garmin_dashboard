export const useConfig = () => {
  const { data } = useFetch('http://localhost:8000/config', {
    key: 'dashboard-config',
    default: () => ({ annual_run_goal: 104, weekly_run_goal: 2 }),
  })
  return data
}
