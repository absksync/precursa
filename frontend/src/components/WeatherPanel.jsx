import { motion } from 'framer-motion'
import { FiAlertTriangle, FiCloudRain, FiNavigation, FiDroplet, FiWind } from 'react-icons/fi'
import Card from './Card'

export default function WeatherPanel({ currentWeather, alerts = [], routeImpact = null, loading = false, lastUpdated = '--' }) {
  const weather = currentWeather || {}
  const severity = Number(weather.weather_severity || weather.risk || 0)
  const displayTemp = Number.isFinite(Number(weather.temperature ?? weather.temp_c))
    ? Math.round(Number(weather.temperature ?? weather.temp_c))
    : null

  return (
    <Card
      as={motion.div}
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.24 }}
      className="space-y-4 p-4"
    >
      {!currentWeather && (
        <div className="rounded-xl border border-sky-400/20 bg-sky-500/10 px-3 py-2 text-xs text-sky-100">
          Loading weather...
        </div>
      )}

      <div className="flex items-center justify-between gap-4 border-b border-white/10 pb-3">
        <div>
          <p className="text-sm font-medium text-white">Live Weather Intelligence</p>
          <p className="text-xs text-gray-400">{weather.zone_name || 'Primary maritime zone'}</p>
        </div>
        <div className={`rounded-full border px-2.5 py-1 text-[10px] uppercase tracking-[0.2em] ${loading ? 'border-slate-400/20 bg-slate-400/10 text-slate-300' : 'border-slate-400/20 bg-slate-500/10 text-slate-200'}`}>
          {loading ? 'Updating' : 'Live'}
        </div>
      </div>

      <div className="flex items-center gap-3">
        <FiCloudRain size={30} className="text-gray-300" />
        <div>
          <p className="text-3xl font-semibold text-white">{displayTemp === null ? '--' : `${displayTemp}°C`}</p>
          <p className="text-sm text-gray-400">{weather.condition || 'Live weather feed'}</p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-2 text-xs sm:grid-cols-4">
        <div className="rounded-xl border border-white/10 bg-white/5 p-3 transition duration-300">
          <div className="flex items-center gap-1 text-gray-400"><FiWind size={12} /> Wind</div>
          <p className="mt-2 text-sm text-white">{Number(weather.wind_speed ?? weather.wind_kph ?? 0).toFixed(1)} km/h</p>
        </div>
        <div className="rounded-xl border border-white/10 bg-white/5 p-3 transition duration-300">
          <div className="flex items-center gap-1 text-gray-400"><FiDroplet size={12} /> Rain</div>
          <p className="mt-2 text-sm text-white">{Number(weather.rain || 0).toFixed(1)} mm</p>
        </div>
        <div className="rounded-xl border border-white/10 bg-white/5 p-3 transition duration-300">
          <div className="flex items-center gap-1 text-gray-400"><FiNavigation size={12} /> Visibility</div>
          <p className="mt-2 text-sm text-white">{Number(weather.visibility || 0).toFixed(1)} km</p>
        </div>
        <div className="rounded-xl border border-white/10 bg-white/5 p-3 transition duration-300">
          <div className="text-gray-400">Severity</div>
          <p className="mt-2 text-sm text-white">{severity}</p>
        </div>
      </div>

      <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
        <div className="flex items-center justify-between gap-3">
          <p className="text-sm font-medium text-white">Weather Alerts</p>
          <span className="text-xs text-gray-400">Updated {lastUpdated}</span>
        </div>
        <div className="mt-3 space-y-2">
          {alerts.length > 0 ? alerts.map((alert) => (
            <div
              key={alert.id}
              className={`flex items-center gap-2 rounded-xl border px-3 py-2 text-xs ${alert.tone === 'red' ? 'border-red-400/20 bg-red-500/10 text-red-100' : alert.tone === 'amber' ? 'border-orange-400/20 bg-orange-500/10 text-orange-100' : 'border-white/10 bg-black/20 text-slate-200'}`}
            >
              <FiAlertTriangle size={13} className="shrink-0 animate-pulse" />
              <span>{alert.message}</span>
            </div>
          )) : (
            <div className="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs text-slate-300">
              No active weather alerts in the current maritime zone.
            </div>
          )}
        </div>
      </div>

      {routeImpact ? (
        <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
          <p className="text-sm font-medium text-white">Route Impact</p>
          <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
            <div className="rounded-xl border border-white/10 bg-black/20 p-3">
              <div className="text-gray-400">Affected route</div>
              <p className="mt-2 text-sm text-white">{routeImpact.affectedPercent}%</p>
            </div>
            <div className="rounded-xl border border-white/10 bg-black/20 p-3">
              <div className="text-gray-400">Delay probability</div>
              <p className="mt-2 text-sm text-white">{routeImpact.delayProbability}%</p>
            </div>
          </div>
        </div>
      ) : null}
    </Card>
  )
}
