import axios from 'axios'

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8001'

const client = axios.create({
  baseURL,
  timeout: 15000
})

async function unwrap(response) {
  return response.data?.data ?? response.data
}

export async function fetchShipments() {
  const response = await client.get('/shipments')
  return unwrap(response)
}

export async function fetchVessels() {
  const response = await client.get('/vessels')
  return unwrap(response)
}

export async function fetchDashboardOverview() {
  const response = await client.get('/dashboard/overview')
  return unwrap(response)
}

export async function fetchGlobalRiskIntelligence(window = '24h') {
  const response = await client.get('/global-risk', { params: { window } })
  return unwrap(response)
}

export async function fetchSystemHealth() {
  const response = await client.get('/health/system')
  return unwrap(response)
}

export async function fetchWeather(lat, lon) {
  const response = await client.get('/weather', { params: { lat, lon } })
  return unwrap(response)
}

export async function fetchWeatherZones() {
  const response = await client.get('/weather/zones')
  return unwrap(response)
}

export async function explainShipmentRisk(shipment) {
  const response = await client.post('/explain-risk', shipment)
  return unwrap(response)
}

export default client
