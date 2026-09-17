import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

/**
 * SEC-014 FIX: JWT is stored in sessionStorage only.
 * localStorage is NOT used for token storage to reduce XSS attack surface.
 * sessionStorage tokens are cleared when the browser tab is closed.
 */
export const getStoredToken = (): string => {
  if (typeof window === 'undefined') return ''
  try {
    return sessionStorage.getItem('crimenet_jwt') || ''
  } catch {
    return ''
  }
}

export const setStoredToken = (token: string): void => {
  if (typeof window === 'undefined') return
  try {
    sessionStorage.setItem('crimenet_jwt', token)
    // SEC-014: Never store tokens in localStorage
  } catch {
    // Storage unavailable — graceful degradation
  }
}

export const clearStoredToken = (): void => {
  if (typeof window === 'undefined') return
  try {
    sessionStorage.removeItem('crimenet_jwt')
    sessionStorage.removeItem('crimenet_authenticated')
    // Clean up any legacy localStorage tokens that may have been set previously
    localStorage.removeItem('crimenet_jwt_token')
    localStorage.removeItem('crimenet_user')
  } catch {
    // Storage unavailable
  }
}

// Attach JWT Bearer token to all outbound requests
api.interceptors.request.use((config) => {
  const token = getStoredToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
}, (error) => {
  return Promise.reject(error)
})

// Handle 401 responses — clear session and redirect to login
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      clearStoredToken()
      // Avoid redirect loop on the login page itself
      if (!window.location.pathname.includes('/login')) {
        window.dispatchEvent(new CustomEvent('crimenet:session-expired'))
      }
    }
    return Promise.reject(error)
  }
)

// Also intercept global axios requests
axios.interceptors.request.use((config) => {
  const token = getStoredToken()
  if (token && !config.headers.Authorization) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default api

export const graphApi = { getNetwork: () => api.get('/graph/network') }
export const analyticsApi = {
  getTopInfluencers: () => api.get('/analytics/top-influencers'),
  getAnomalies: () => api.get('/analytics/anomalies'),
  getCommunities: () => api.get('/analytics/communities'),
  getNetworkStats: () => api.get('/analytics/network-stats'),
  runAnalysis: () => api.post('/analytics/run'),
}
export const chatApi = { send: (message: string) => api.post('/chat/message', { message }) }
export const alertsApi = {
  list: () => api.get('/alerts'),
  acknowledge: (id: string) => api.post('/alerts/' + id + '/acknowledge'),
}
export const casesApi = {
  list: () => api.get('/cases'),
  get: (id: string) => api.get('/cases/' + id),
  create: (d: any) => api.post('/cases', d),
  addComment: (id: string, content: string) => api.post('/cases/' + id + '/comments', { content }),
}
export const reportsApi = {
  generate: (entity_type: string, entity_id: string, report_type: string = 'full') =>
    api.post('/reports/generate', { entity_type, entity_id, report_type }, { responseType: 'blob' }),
  getTemplates: () => api.get('/reports/templates'),
}
export const entitiesApi = { search: (q: string) => api.get('/entities/search?q=' + encodeURIComponent(q)) }
export const authApi = {
  listUsers: () => api.get('/auth/users'),
  getToken: (payload: any) => api.post('/auth/token', payload),
  verifyToken: () => api.get('/auth/verify-token')
}
