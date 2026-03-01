/**
 * Returns the correct API base URL for the current environment.
 *
 * On the server (SSR/Docker): uses NUXT_API_BASE_INTERNAL so the frontend
 * container can reach the backend container via the Docker network name.
 *
 * In the browser: uses NUXT_PUBLIC_API_BASE — the publicly accessible URL.
 */
export const useApiBase = (): string => {
  const config = useRuntimeConfig()
  if (import.meta.server && config.apiBaseInternal) {
    return config.apiBaseInternal as string
  }
  return config.public.apiBase
}
