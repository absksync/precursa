export function riskLevelFromDRI(dri) {
  if (dri >= 80) return 'Critical'
  if (dri >= 65) return 'High'
  if (dri >= 45) return 'Medium'
  return 'Low'
}

export function riskColor(level) {
  if (level === 'Critical') return 'text-red-400 bg-red-500/15 border-red-400/40'
  if (level === 'High') return 'text-orange-300 bg-orange-500/15 border-orange-300/40'
  if (level === 'Medium') return 'text-amber-300 bg-amber-500/15 border-amber-300/40'
  return 'text-slate-300 bg-slate-500/15 border-slate-300/40'
}

export function driColor(dri) {
  if (dri >= 80) return '#ef4444'
  if (dri >= 65) return '#f97316'
  if (dri >= 45) return '#facc15'
  return '#64748b'
}
