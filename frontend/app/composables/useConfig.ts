export const useConfig = () => {
  const apiBase = useApiBase()
  const { data } = useFetch(`${apiBase}/config`, {
    key: 'dashboard-config',
    default: () => ({ annual_run_goal: 104, weekly_run_goal: 2 }),
  })
  return data
}
