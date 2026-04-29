const LABEL_STYLES = {
  'On track': {
    border: 'border-green-500',
    text: 'text-green-600',
    bg: 'bg-green-50',
    badge: 'bg-green-100 text-green-800',
  },
  'Needs attention': {
    border: 'border-amber-500',
    text: 'text-amber-600',
    bg: 'bg-amber-50',
    badge: 'bg-amber-100 text-amber-800',
  },
  'At risk': {
    border: 'border-red-500',
    text: 'text-red-600',
    bg: 'bg-red-50',
    badge: 'bg-red-100 text-red-800',
  },
}

const PRIORITY_DOT = {
  high: 'bg-red-500',
  medium: 'bg-amber-400',
  low: 'bg-green-500',
}

const METRIC_COLOURS = {
  indigo: 'bg-indigo-50 text-indigo-700',
  green: 'bg-green-50 text-green-700',
  red: 'bg-red-50 text-red-700',
}

function fmt(n) {
  return new Intl.NumberFormat('en-GB', {
    style: 'currency',
    currency: 'GBP',
    maximumFractionDigits: 0,
  }).format(n)
}

function MetricBox({ label, value, colour }) {
  return (
    <div className={`rounded-xl p-4 ${METRIC_COLOURS[colour] ?? METRIC_COLOURS.indigo}`}>
      <p className="text-xs font-semibold uppercase tracking-wide opacity-60">{label}</p>
      <p className="text-2xl font-bold mt-1">{value}</p>
    </div>
  )
}

export default function ResultCard({ result }) {
  const styles = LABEL_STYLES[result.readiness_label] ?? LABEL_STYLES['At risk']

  return (
    <div className="bg-white rounded-2xl shadow-2xl ring-1 ring-black/5 p-8 space-y-6">
      {/* Score + summary */}
      <div className="flex flex-col sm:flex-row items-center gap-6">
        {/* Score circle */}
        <div
          className={`relative flex-shrink-0 flex flex-col items-center justify-center w-32 h-32 rounded-full border-8 ${styles.border} ${styles.bg}`}
        >
          <span className={`text-4xl font-extrabold leading-none ${styles.text}`}>
            {result.readiness_score}
          </span>
          <span className="text-xs text-gray-400 font-medium">/ 100</span>
        </div>

        <div className="text-center sm:text-left">
          <span className={`inline-block text-sm font-semibold px-3 py-1 rounded-full mb-2 ${styles.badge}`}>
            {result.readiness_label}
          </span>
          <p className="text-gray-700 leading-relaxed">{result.summary}</p>
          <p className="text-gray-400 text-sm mt-1">{result.years_to_retirement} years until retirement</p>
        </div>
      </div>

      {/* Key metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <MetricBox label="Projected Pension Pot" value={fmt(result.projected_pot)} colour="indigo" />
        <MetricBox
          label="Projected Annual Income"
          value={fmt(result.projected_annual_income)}
          colour="green"
        />
        <MetricBox
          label="Annual Shortfall"
          value={result.shortfall > 0 ? fmt(result.shortfall) : 'None'}
          colour={result.shortfall > 0 ? 'red' : 'green'}
        />
      </div>

      {/* Action steps */}
      {result.action_steps.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gray-800 mb-3">Recommended Actions</h3>
          <ul className="space-y-3">
            {result.action_steps.map((step, i) => (
              <li key={i} className="flex gap-3 items-start">
                <span
                  className={`mt-1.5 flex-shrink-0 w-2.5 h-2.5 rounded-full ${PRIORITY_DOT[step.priority]}`}
                />
                <div>
                  <p className="text-gray-800 font-medium">{step.action}</p>
                  <p className="text-gray-500 text-sm">{step.reason}</p>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Disclaimer */}
      <p className="text-xs text-gray-400 border-t border-gray-100 pt-4 leading-relaxed">
        {result.disclaimer}
      </p>
    </div>
  )
}
