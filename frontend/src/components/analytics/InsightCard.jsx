import { motion } from 'framer-motion'
import Card from '../Card'

export default function InsightCard({ title, label, tone = 'slate', children }) {
  const toneClasses = {
    slate: 'border-white/10 bg-white/5 text-slate-300',
    orange: 'border-orange-400/20 bg-orange-500/10 text-orange-100',
    sky: 'border-slate-400/20 bg-slate-500/10 text-slate-100',
    red: 'border-red-400/20 bg-red-500/10 text-red-100',
    emerald: 'border-slate-400/20 bg-slate-500/10 text-slate-100'
  }

  return (
    <Card
      as={motion.article}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.24 }}
      className={`p-4 ${toneClasses[tone] || toneClasses.slate}`}
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-[0.18em] text-white/60">{label}</p>
          <h4 className="mt-1 text-sm font-semibold text-white">{title}</h4>
        </div>
      </div>
      <div className="mt-3 text-sm leading-6 text-slate-200">{children}</div>
    </Card>
  )
}