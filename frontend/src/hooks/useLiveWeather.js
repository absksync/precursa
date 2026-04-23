import { useEffect, useMemo, useState } from 'react'

import { fetchWeather, fetchWeatherZones } from '../services/api'

const POLL_INTERVAL_MS = 15000
const WIND_ALERT_THRESHOLD = 20
const VISIBILITY_ALERT_THRESHOLD = 5
const RAIN_ALERT_THRESHOLD = 6
const SEVERITY_ALERT_THRESHOLD = 70

function clamp(value, low = 0, high = 100) {
  return Math.max(low, Math.min(high, value))
}

function haversineKm([lat1, lon1], [lat2, lon2]) {
  const earthRadius = 6371
  const toRadians = (value) => (value * Math.PI) / 180
  const deltaLat = toRadians(lat2 - lat1)
  const deltaLon = toRadians(lon2 - lon1)
  const a = Math.sin(deltaLat / 2) ** 2
    + Math.cos(toRadians(lat1)) * Math.cos(toRadians(lat2)) * Math.sin(deltaLon / 2) ** 2

  return 2 * earthRadius * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
}

function buildAlerts(weather) {
  if (!weather) return []

  const zoneName = weather.zone_name || 'Primary maritime zone'
  const alerts = []

  if (Number(weather.wind_speed || 0) >= WIND_ALERT_THRESHOLD) {
    alerts.push({ id: 'wind', tone: 'amber', message: `⚠ High wind detected in ${zoneName}` })
  }

  if (Number(weather.visibility || 0) <= VISIBILITY_ALERT_THRESHOLD) {
    alerts.push({ id: 'visibility', tone: 'red', message: '⚠ Low visibility - navigation risk' })
  }

  if (Number(weather.rain || 0) >= RAIN_ALERT_THRESHOLD) {
    alerts.push({ id: 'rain', tone: 'orange', message: `⚠ Heavy rain activity in ${zoneName}` })
  }

  if (Number(weather.weather_severity || 0) >= SEVERITY_ALERT_THRESHOLD) {
    alerts.push({ id: 'severity', tone: 'slate', message: '⚠ Severe weather band is active along the live maritime corridor' })
  }

  return alerts
}

function calculateRouteImpact(routeCoords, zones) {
  if (!Array.isArray(routeCoords) || routeCoords.length === 0 || !Array.isArray(zones) || zones.length === 0) {
    return null
  }

  const affectedWaypoints = routeCoords.filter((point) => {
    const [lat, lon] = point
    return zones.some((zone) => Number(zone.severity || 0) >= 55 && haversineKm([lat, lon], [zone.lat, zone.lon]) <= 120)
  }).length

  if (!affectedWaypoints) {
    return { affectedPercent: 0, delayProbability: 0 }
  }

  const affectedPercent = Math.round((affectedWaypoints / routeCoords.length) * 100)
  const worstSeverity = zones.reduce((max, zone) => Math.max(max, Number(zone.severity || 0)), 0)
  const delayProbability = clamp(Math.round(affectedPercent * 0.55 + worstSeverity * 0.45), 0, 100)

  return { affectedPercent, delayProbability }
}

export default function useLiveWeather(routeCoords = []) {
  const [weatherZones, setWeatherZones] = useState([])
  const [currentWeather, setCurrentWeather] = useState(null)
  const [weatherHistory, setWeatherHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [lastUpdated, setLastUpdated] = useState('--')

  useEffect(() => {
    let cancelled = false

    const refresh = async () => {
      try {
        const zones = await fetchWeatherZones()
        if (cancelled) return

        const normalizedZones = Array.isArray(zones) ? zones : []
        setWeatherZones(normalizedZones)

        const focusZone = normalizedZones
          .slice()
          .sort((left, right) => Number(right.severity || 0) - Number(left.severity || 0))[0]

        if (focusZone) {
          const weather = await fetchWeather(focusZone.lat, focusZone.lon)
          if (!cancelled) {
            setCurrentWeather(weather || null)
            setWeatherHistory((previous) => {
              const next = [...previous, {
                timestamp: weather?.timestamp || new Date().toISOString(),
                wind_speed: Number(weather?.wind_speed ?? weather?.wind_kph ?? 0),
                rain: Number(weather?.rain ?? 0),
                visibility: Number(weather?.visibility ?? 0),
                severity: Number(weather?.weather_severity ?? weather?.risk ?? 0),
                zone_name: weather?.zone_name || focusZone.name,
              }]

              return next.slice(-48)
            })
            setLastUpdated(new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }))
            setError('')
          }
        }
      } catch (fetchError) {
        if (!cancelled) {
          setError(fetchError?.message || 'Unable to refresh weather data.')
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    refresh()
    const timer = window.setInterval(refresh, POLL_INTERVAL_MS)

    return () => {
      cancelled = true
      window.clearInterval(timer)
    }
  }, [])

  const alerts = useMemo(() => buildAlerts(currentWeather), [currentWeather])
  const routeImpact = useMemo(() => calculateRouteImpact(routeCoords, weatherZones), [routeCoords, weatherZones])

  const weatherTimeline = useMemo(() => {
    const source = weatherHistory.length > 0 ? weatherHistory : currentWeather ? [{
      timestamp: currentWeather.timestamp || new Date().toISOString(),
      wind_speed: Number(currentWeather.wind_speed ?? currentWeather.wind_kph ?? 0),
      rain: Number(currentWeather.rain ?? 0),
      visibility: Number(currentWeather.visibility ?? 0),
      severity: Number(currentWeather.weather_severity ?? currentWeather.risk ?? 0),
      zone_name: currentWeather.zone_name || 'Primary maritime zone',
    }] : []

    const historyPoints = source.slice(-24).map((entry, index) => ({
      label: index === 0 ? 'Now' : `T-${(source.length - index) * 15}m`,
      wind: entry.wind_speed,
      rain: entry.rain,
      visibility: entry.visibility,
      severity: entry.severity,
      type: 'history'
    }))

    const latest = source[source.length - 1]
    const forecastPoints = latest ? Array.from({ length: 6 }, (_, index) => {
      const drift = index + 1
      const trendWeight = Math.max(-8, Math.min(8, (latest.severity - (source[Math.max(0, source.length - 3)]?.severity || latest.severity)) * 0.45))
      return {
        label: `+${(index + 1) * 2}h`,
        wind: Math.max(0, Number((latest.wind_speed + drift * 0.4 + trendWeight * 0.12).toFixed(1))),
        rain: Math.max(0, Number((latest.rain + drift * 0.15 + trendWeight * 0.08).toFixed(1))),
        visibility: Math.max(0.1, Number((latest.visibility - drift * 0.18 - trendWeight * 0.05).toFixed(1))),
        severity: Math.max(0, Math.min(100, Math.round(latest.severity + drift * 1.6 + trendWeight * 0.9))),
        type: 'forecast'
      }
    }) : []

    return [...historyPoints, ...forecastPoints]
  }, [currentWeather, weatherHistory])

  const dominantFactor = useMemo(() => {
    if (!currentWeather) return 'Wind'
    const factors = [
      { name: 'Wind', value: Number(currentWeather.wind_speed ?? currentWeather.wind_kph ?? 0) * 0.3 },
      { name: 'Rain', value: Number(currentWeather.rain ?? 0) * 0.4 },
      { name: 'Visibility', value: (1 / Math.max(Number(currentWeather.visibility ?? 1), 0.1)) * 0.3 }
    ]
    return factors.sort((left, right) => right.value - left.value)[0]?.name || 'Wind'
  }, [currentWeather])

  const stormTrack = useMemo(() => {
    const severity = Number(currentWeather?.weather_severity ?? currentWeather?.risk ?? 0)
    const center = weatherZones.slice().sort((left, right) => Number(right.severity || 0) - Number(left.severity || 0))[0]
    if (!center) return null

    const path = Array.from({ length: 4 }, (_, index) => ({
      lat: center.lat + (index * 0.15),
      lon: center.lon + (index % 2 === 0 ? 0.12 : -0.08),
    }))

    return {
      lat: center.lat,
      lon: center.lon,
      severity,
      speed: Math.max(12, Math.round((severity * 0.7) + 8)),
      direction: severity >= 65 ? 'NE' : 'E',
      path,
    }
  }, [currentWeather, weatherZones])

  return {
    currentWeather,
    weatherZones,
    alerts,
    routeImpact,
    weatherTimeline,
    stormTrack,
    dominantFactor,
    loading,
    error,
    lastUpdated,
  }
}