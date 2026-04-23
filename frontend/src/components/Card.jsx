import { motion } from 'framer-motion'

export default function Card({ children, className = '', as: Component = motion.div, ...props }) {
  return (
    <Component
      {...props}
      className={`glass-card ${className}`}
    >
      {children}
    </Component>
  )
}