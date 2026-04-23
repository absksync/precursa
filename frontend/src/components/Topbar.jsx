import { motion } from 'framer-motion'
import { FiBell, FiMenu, FiMoon, FiSearch, FiSun } from 'react-icons/fi'

export default function Topbar({ title, subtitle, theme, onToggleTheme, onSearch, searchValue, onSearchValueChange, onMenuClick }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      className="topbar-shell sticky top-0 z-10 mb-6 flex flex-wrap items-center justify-between gap-4 px-4 py-4"
    >
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={onMenuClick}
          className="inline-flex h-10 w-10 items-center justify-center rounded-xl border border-white/10 bg-white/5 text-gray-300 transition hover:bg-white/10 hover:text-white md:hidden"
          aria-label="Open sidebar"
        >
          <FiMenu size={16} />
        </button>

        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-gray-500">{subtitle || 'Live Operations'}</p>
          <h1 className="mt-1 text-2xl font-semibold tracking-tight text-white">{title || 'Maritime Logistics Command Center'}</h1>
        </div>
      </div>

      <div className="flex flex-wrap items-center justify-end gap-3 text-sm text-gray-300">
        <button
          type="button"
          onClick={onToggleTheme}
          className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-2 text-xs uppercase tracking-[0.18em] text-gray-300 transition hover:bg-white/10 hover:text-white"
          aria-label="Toggle color theme"
        >
          {theme === 'dark' ? <FiSun size={14} /> : <FiMoon size={14} />}
          {theme === 'dark' ? 'Light mode' : 'Dark mode'}
        </button>

        <div className="flex items-center gap-2 rounded-lg border border-white/10 bg-white/5 px-3 py-2">
          <FiSearch size={14} className="text-gray-500" />
          <input
            value={searchValue}
            onChange={(e) => onSearchValueChange(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') onSearch(e.currentTarget.value)
            }}
            placeholder="Search shipments"
            className="w-36 bg-transparent text-xs text-white placeholder:text-gray-500 outline-none md:w-48"
          />
        </div>

        <button
          type="button"
          className="relative flex h-10 w-10 items-center justify-center rounded-lg border border-white/10 bg-white/5 text-gray-300 transition hover:bg-white/10 hover:text-white"
          aria-label="Notifications"
        >
          <FiBell size={15} />
          <span className="absolute right-2 top-2 h-2 w-2 rounded-full bg-orange-400" />
        </button>

        <button type="button" className="flex items-center gap-3 rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-left transition hover:bg-white/10">
          <span className="flex h-8 w-8 items-center justify-center rounded-full border border-white/10 bg-white/10 text-xs font-semibold text-white">
            AS
          </span>
          <span className="hidden md:block">
            <span className="block text-xs text-white">Abhishek Singh</span>
            <span className="block text-[11px] text-gray-500">Admin</span>
          </span>
        </button>
      </div>
    </motion.div>
  )
}
