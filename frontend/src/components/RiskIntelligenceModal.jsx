import { AnimatePresence } from 'framer-motion'
import { FiBarChart2, FiClock, FiMapPin, FiX } from 'react-icons/fi'

import Card from './Card'

function toneClass(level) {
  if (level === 'Critical') return 'border-red-400/30 bg-red-500/10 text-red-100'
  if (level === 'High') return 'border-orange-400/30 bg-orange-500/10 text-orange-100'
  if (level === 'Medium') return 'border-amber-400/30 bg-amber-500/10 text-amber-100'
  return 'border-slate-400/30 bg-slate-500/10 text-slate-100'
}

function SectionTitle({ title, subtitle }) {
  return (
    <div>
      <p className="text-sm font-medium text-white">{title}</p>
      {subtitle ? <p className="mt-1 text-xs text-slate-400">{subtitle}</p> : null}
    </div>
  )
}

export default function RiskIntelligenceModal({ open, loading, analysis, error, onClose }) {
  const breakdown = analysis?.breakdown || {}
  const zones = analysis?.zones || []
  const confidence = Math.round((Number(analysis?.confidence || 0) || 0) * 100)
  const trend = String(analysis?.trend || 'stable')
  const trendLabel = trend === 'increasing' ? 'Increasing risk' : trend === 'decreasing' ? 'Decreasing risk' : 'Stable risk'

  return (
    <AnimatePresence>
      {open && (
        <div
          className="fixed inset-0 z-[60] flex items-center justify-center bg-black/70 px-4 py-6 backdrop-blur-md"
          onClick={onClose}
        >
          <div
            className="w-full max-w-5xl"
            onClick={(event) => event.stopPropagation()}
          >
            <Card className="max-h-[90vh] overflow-y-auto p-0">
              <div className="flex items-center justify-between border-b border-white/10 px-5 py-4">
                <div>
                  <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Operational Risk Analysis</p>
                  <h3 className="mt-1 text-xl font-semibold text-white">Risk Intelligence</h3>
                </div>
                <button
                  type="button"
                  onClick={onClose}
                  className="rounded-full border border-white/10 bg-white/5 p-2 text-gray-300 transition hover:border-white/20 hover:bg-white/10 hover:text-white"
                >
                  <FiX size={18} />
                </button>
              </div>

              {loading ? (
                <div className="p-5 text-sm text-slate-400">Computing live shipment risk...</div>
              ) : error ? (
                <div className="p-5 text-sm text-red-200">{error}</div>
              ) : analysis ? (
                <div className="space-y-5 p-5">
                  <div className="grid gap-4 xl:grid-cols-[1.2fr_0.8fr]">
                    <Card className="p-4">
                      <div className="flex flex-wrap items-center justify-between gap-4">
                        <div>
                          <SectionTitle title={analysis.shipment_id} subtitle={`${analysis.origin} → ${analysis.destination}`} />
                          <p className="mt-2 text-xs text-slate-400">Route: {analysis.route}</p>
                        </div>
                        <div className={`rounded-full border px-3 py-1 text-xs uppercase tracking-[0.2em] ${toneClass(analysis.level)}`}>
                          {analysis.level}
                        </div>
                      </div>

                      <div className="mt-4 grid gap-3 sm:grid-cols-3">
                        <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                          <p className="text-xs uppercase tracking-[0.2em] text-slate-400">DRI Score</p>
                          <p className="mt-2 text-4xl font-semibold text-white">{analysis.dri}</p>
                        </div>
                        <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                          <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Delay Estimate</p>
                          <p className="mt-2 text-2xl font-semibold text-white">+{analysis.delay_estimate}</p>
                        </div>
                        <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                          <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Vessels Nearby</p>
                          <p className="mt-2 text-4xl font-semibold text-white">{analysis.vessels_nearby}</p>
                        </div>
                      </div>

                      <div className="mt-3 grid gap-3 sm:grid-cols-2">
                        <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                          <p className="text-xs uppercase tracking-[0.2em] text-slate-400">AI Model Confidence</p>
                          <p className="mt-2 text-3xl font-semibold text-white">{confidence}%</p>
                        </div>
                        <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                          <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Prediction Engine</p>
                          <p className="mt-2 text-lg font-semibold text-white">{analysis.prediction_engine || 'Rule-based fallback'}</p>
                        </div>
                      </div>

                      <div className="mt-3 grid gap-3 sm:grid-cols-2">
                        <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                          <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Trend</p>
                          <p className="mt-2 text-xl font-semibold text-white">{trendLabel}</p>
                        </div>
                        <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                          <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Time-aware prediction</p>
                          <p className="mt-2 text-lg font-semibold text-white">
                            {analysis.time_aware_prediction ? 'Enabled' : 'Unavailable'}
                          </p>
                        </div>
                      </div>
                    </Card>

                    <Card className="p-4">
                      <SectionTitle title="Weather Details" subtitle="Live conditions at the active zone" />
                      <div className="mt-4 grid grid-cols-3 gap-2 text-xs">
                        {Object.entries(analysis.weather_details || {}).map(([label, value]) => (
                          <div key={label} className="rounded-xl border border-white/10 bg-white/5 p-3">
                            <p className="text-slate-400 capitalize">{label}</p>
                            <p className="mt-2 text-sm text-white">{value}</p>
                          </div>
                        ))}
                      </div>
                      <div className="mt-4 rounded-2xl border border-white/10 bg-white/5 p-4">
                        <div className="flex items-center gap-2 text-xs text-slate-400">
                          <FiClock size={12} />
                          <span>Estimated delay</span>
                        </div>
                        <p className="mt-2 text-2xl font-semibold text-white">Estimated Delay: +{analysis.delay_estimate}</p>
                      </div>
                    </Card>
                  </div>

                  <div className="grid gap-4 xl:grid-cols-[1fr_0.95fr]">
                    <Card className="p-4">
                      <SectionTitle title="Risk Breakdown" subtitle="Computed from weather, AIS congestion, route density and carrier pressure" />
                      <div className="mt-4 space-y-3">
                        {Object.entries(breakdown).map(([label, value]) => (
                          <div key={label}>
                            <div className="mb-1 flex items-center justify-between text-xs text-slate-400">
                              <span className="capitalize">{label}</span>
                              <span>{value}%</span>
                            </div>
                            <div className="h-2 rounded-full bg-white/8">
                              <div
                                className={`h-2 rounded-full ${label === 'weather' ? 'bg-red-400' : label === 'congestion' ? 'bg-orange-400' : label === 'density' ? 'bg-amber-300' : 'bg-slate-400'}`}
                                style={{ width: `${value}%` }}
                              />
                            </div>
                          </div>
                        ))}
                      </div>
                    </Card>

                    <Card className="p-4">
                      <SectionTitle title="Route Impact" subtitle="Affected weather and congestion zones" />
                      <div className="mt-4 space-y-2">
                        {zones.length > 0 ? zones.map((zone) => (
                          <div key={zone} className="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-slate-200">
                            <span>{zone}</span>
                            <FiMapPin size={14} className="text-slate-400" />
                          </div>
                        )) : (
                          <div className="rounded-xl border border-dashed border-white/10 bg-white/5 p-4 text-sm text-slate-400">No impacted zones detected.</div>
                        )}
                      </div>
                    </Card>
                  </div>

                  <Card className="p-5">
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <SectionTitle title="Insight" subtitle="System-generated operational analysis" />
                        <p className="mt-3 text-sm leading-7 text-slate-200">{analysis.insight}</p>
                      </div>
                      <FiBarChart2 className="shrink-0 text-orange-300" size={20} />
                    </div>
                  </Card>
                </div>
              ) : null}
            </Card>
          </div>
        </div>
      )}
    </AnimatePresence>
  )
}