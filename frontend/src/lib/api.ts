import axios from 'axios'
const api = axios.create({ baseURL: '/api' })
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
export const authApi = { listUsers: () => api.get('/auth/users') }
