import { boot } from 'quasar/wrappers'
import createClient from 'openapi-fetch'
import type { paths } from '../types/api'

var API_ENDPOINT = ''
if (process.env.NODE_ENV === 'development') {
  API_ENDPOINT = process.env.API_ENDPOINT_DEV.replace('/api', '')
} else if (process.env.NODE_ENV === 'production') {
  API_ENDPOINT =
    window.location.protocol +
    '//' +
    window.location.hostname +
    ':' +
    process.env.PRODUCTION_BACKEND_PORT
}

// Create typed API client using OpenAPI schema
// Note: baseUrl should NOT include /api since paths in OpenAPI schema already include it
const client = createClient<paths>({ baseUrl: API_ENDPOINT })

// Add auth token interceptor
client.use({
  async onRequest({ request }) {
    const token = localStorage.getItem('jwt-token')
    if (token) {
      request.headers.set('Authorization', `Bearer ${token}`)
    }
    return request
  },
  async onResponse({ response }) {
    if (response.status === 401) {
      localStorage.removeItem('jwt-token')

      // if current page is not login page, reload page, which will redirect to login page
      if (!window.location.href.endsWith('/login')) {
        window.location.reload()
      }
    }
    return response
  }
})

export default boot(({ app }) => {
  // Make typed API client available throughout the app
  app.config.globalProperties.$typedApi = client
})

export { client }
