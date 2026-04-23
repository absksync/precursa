import { motion } from 'framer-motion'
import Card from '../Card'

export default function ChartCard({ title, description, children, className = '' }) {
  return (
    <Card
      as={motion.section}
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.28 }}
      className={`overflow-hidden ${className}`}
    >
      <div className="border-b border-white/10 px-4 py-4 sm:px-5">
        <p className="text-sm font-medium text-white">{title}</p>
        {description ? <p className="mt-1 text-xs leading-5 text-slate-400">{description}</p> : null}
      </div>
      <div className="p-4 sm:p-5">{children}</div>
    </Card>
  )
}