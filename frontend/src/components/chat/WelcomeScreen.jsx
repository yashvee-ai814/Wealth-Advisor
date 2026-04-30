const SCENARIOS = [
  {
    title: 'Retirement readiness',
    description: '35-year-old, £60k salary, £20k saved',
    message: "I'm 35, earn £60k/year, have £20k in my pension and contribute £400/month. I want to retire at 65 with £35k/year income. Am I on track?",
    color: 'amber',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" className="w-5 h-5">
        <polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/>
        <polyline points="16 7 22 7 22 13"/>
      </svg>
    ),
  },
  {
    title: 'Early retirement goal',
    description: '40-year-old aiming to retire at 55',
    message: "I'm 40 with £120k saved, earning £95k. I want to retire at 55 with £45k/year income. Is this feasible and what steps do I need?",
    color: 'indigo',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" className="w-5 h-5">
        <circle cx="12" cy="12" r="10"/>
        <circle cx="12" cy="12" r="3"/>
        <line x1="12" y1="2" x2="12" y2="5"/>
        <line x1="12" y1="19" x2="12" y2="22"/>
        <line x1="2" y1="12" x2="5" y2="12"/>
        <line x1="19" y1="12" x2="22" y2="12"/>
      </svg>
    ),
  },
  {
    title: 'Late starter catch-up',
    description: '52-year-old, £10k saved, £75k salary',
    message: "I'm 52, just starting to save seriously with £10k in my pension. I earn £75k and want to retire at 67. How much do I need to save monthly to reach a decent pot?",
    color: 'rose',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" className="w-5 h-5">
        <circle cx="12" cy="12" r="10"/>
        <polyline points="12 6 12 12 16 14"/>
      </svg>
    ),
  },
  {
    title: 'State pension planning',
    description: 'UK state pension eligibility & amount',
    message: "I'm 45. How much state pension will I get, when can I access it, and how does the £11,502/year figure fit into my retirement plan alongside my £80k private pension?",
    color: 'emerald',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" className="w-5 h-5">
        <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
        <line x1="8" y1="21" x2="16" y2="21"/>
        <line x1="12" y1="17" x2="12" y2="21"/>
      </svg>
    ),
  },
  {
    title: 'Inflation impact analysis',
    description: 'Real value of £30k/yr in 25 years',
    message: "I want £30k/year in today's money when I retire in 25 years. With 2.5% annual inflation, what income target should I actually be planning for?",
    color: 'violet',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" className="w-5 h-5">
        <line x1="12" y1="1" x2="12" y2="23"/>
        <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
      </svg>
    ),
  },
  {
    title: 'Drawdown income model',
    description: '£400k pot at 60 — income planning',
    message: "I'm 60 with a £400k pension pot. Model my drawdown income at 3.5% withdrawal rate alongside my state pension starting at 67 — what will my annual income look like each year?",
    color: 'cyan',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" className="w-5 h-5">
        <rect x="2" y="2" width="20" height="8" rx="2" ry="2"/>
        <rect x="2" y="14" width="20" height="8" rx="2" ry="2"/>
        <line x1="6" y1="6" x2="6.01" y2="6"/>
        <line x1="6" y1="18" x2="6.01" y2="18"/>
      </svg>
    ),
  },
]

const COLOUR_MAP = {
  amber:  { bg: 'bg-amber-50  dark:bg-amber-950/30',  border: 'border-amber-200  dark:border-amber-800/40',  icon: 'text-amber-600  dark:text-amber-400',  title: 'text-amber-800  dark:text-amber-300'  },
  indigo: { bg: 'bg-indigo-50 dark:bg-indigo-950/30', border: 'border-indigo-200 dark:border-indigo-800/40', icon: 'text-indigo-600 dark:text-indigo-400', title: 'text-indigo-800 dark:text-indigo-300' },
  rose:   { bg: 'bg-rose-50   dark:bg-rose-950/30',   border: 'border-rose-200   dark:border-rose-800/40',   icon: 'text-rose-600   dark:text-rose-400',   title: 'text-rose-800   dark:text-rose-300'   },
  emerald:{ bg: 'bg-emerald-50 dark:bg-emerald-950/30',border: 'border-emerald-200 dark:border-emerald-800/40',icon: 'text-emerald-600 dark:text-emerald-400',title: 'text-emerald-800 dark:text-emerald-300'},
  violet: { bg: 'bg-violet-50 dark:bg-violet-950/30', border: 'border-violet-200 dark:border-violet-800/40', icon: 'text-violet-600 dark:text-violet-400', title: 'text-violet-800 dark:text-violet-300' },
  cyan:   { bg: 'bg-cyan-50   dark:bg-cyan-950/30',   border: 'border-cyan-200   dark:border-cyan-800/40',   icon: 'text-cyan-600   dark:text-cyan-400',   title: 'text-cyan-800   dark:text-cyan-300'   },
}

export default function WelcomeScreen({ onSend }) {
  return (
    <div className="flex flex-col items-center justify-start px-4 py-8 max-w-4xl mx-auto w-full">
      {/* Hero */}
      <div className="mb-8 text-center">
        <div className="flex justify-center mb-4">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-amber-400 to-yellow-600 flex items-center justify-center shadow-xl shadow-amber-500/25">
            <svg viewBox="0 0 24 24" fill="none" className="w-8 h-8" stroke="white" strokeWidth="1.8">
              <path d="M12 2L2 7l10 5 10-5-10-5z"/>
              <path d="M2 17l10 5 10-5"/>
              <path d="M2 12l10 5 10-5"/>
            </svg>
          </div>
        </div>
        <h2 className="font-display text-2xl font-bold text-slate-900 dark:text-white mb-2">
          Your UK Wealth Advisor
        </h2>
        <p className="text-slate-500 dark:text-slate-400 text-sm max-w-md mx-auto leading-relaxed">
          Powered by local AI with deterministic financial calculations. Ask anything about retirement, pensions, savings, and wealth planning.
        </p>
        {/* Mini chart */}
        <div className="flex justify-center mt-5">
          <svg viewBox="0 0 280 60" className="w-56 h-12 opacity-60">
            <defs>
              <linearGradient id="wf" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#f59e0b" stopOpacity="0.3"/>
                <stop offset="100%" stopColor="#f59e0b" stopOpacity="0"/>
              </linearGradient>
            </defs>
            {[0,15,30,45].map(y => <line key={y} x1="0" y1={y} x2="280" y2={y} stroke="currentColor" strokeWidth="0.3" className="text-slate-200 dark:text-slate-700"/>)}
            <polygon points="10,50 50,42 90,44 130,30 170,32 210,18 250,10 250,55 10,55" fill="url(#wf)"/>
            <polyline points="10,50 50,42 90,44 130,30 170,32 210,18 250,10" fill="none" stroke="#f59e0b" strokeWidth="2" strokeLinejoin="round" strokeLinecap="round"/>
            {[[10,50],[50,42],[90,44],[130,30],[170,32],[210,18],[250,10]].map(([x,y],i) => (
              <circle key={i} cx={x} cy={y} r="3" fill="#f59e0b" stroke="white" strokeWidth="1.5"/>
            ))}
          </svg>
        </div>
      </div>

      {/* Scenario cards */}
      <div className="w-full">
        <p className="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-widest mb-3 text-center">Example scenarios</p>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
          {SCENARIOS.map((s) => {
            const c = COLOUR_MAP[s.color]
            return (
              <button
                key={s.title}
                onClick={() => onSend(s.message)}
                className={`text-left px-4 py-3.5 rounded-xl border transition-all duration-150 hover:scale-[1.01] hover:shadow-md group ${c.bg} ${c.border}`}
              >
                <div className={`mb-2 ${c.icon}`}>{s.icon}</div>
                <p className={`text-sm font-semibold mb-0.5 ${c.title}`}>{s.title}</p>
                <p className="text-xs text-slate-500 dark:text-slate-400 leading-snug">{s.description}</p>
              </button>
            )
          })}
        </div>
        <p className="text-xs text-slate-400 dark:text-slate-600 text-center mt-4">
          Or type your own question in the box below
        </p>
      </div>
    </div>
  )
}
