import { useState } from 'react'
import AdvisorForm from './components/AdvisorForm.jsx'
import ResultCard from './components/ResultCard.jsx'

export default function App() {
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  return (
    /*
      Background: a layered sunset-over-ocean gradient.
      Deep navy at top (night sky) → ocean blue → golden horizon → warm coral.
      Evokes a peaceful retirement evening by the sea.
    */
    <div
      className="min-h-screen"
      style={{
        background:
          'linear-gradient(to bottom, #0f2027 0%, #1d4e89 28%, #3a86ff 52%, #ffb347 78%, #ff6b6b 100%)',
      }}
    >
      {/* ── Sticky banner ── */}
      <header className="sticky top-0 z-20 bg-black/40 backdrop-blur-md border-b border-white/10">
        <div className="max-w-7xl mx-auto px-6 py-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
          <div>
            <h1 className="text-2xl font-extrabold text-white tracking-tight leading-tight">
              Retirement Readiness Advisor
            </h1>
            <p className="text-blue-200 text-sm">
              AI-powered UK pension planning · private &amp; runs entirely on your device
            </p>
          </div>

          {/* Status pill */}
          <div className="flex items-center gap-2 bg-green-400/20 border border-green-400/30 rounded-full px-4 py-1.5 self-start sm:self-auto">
            <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse inline-block" />
            <span className="text-green-300 text-sm font-medium">Local AI Active</span>
          </div>
        </div>
      </header>

      {/* ── Hero sub-header ── */}
      <div className="max-w-7xl mx-auto px-6 pt-8 pb-4 text-center">
        <p className="text-white/80 text-lg max-w-2xl mx-auto leading-relaxed">
          Enter your pension details on the left. Your personalised readiness score,
          projections, and action plan will appear instantly on the right.
        </p>
      </div>

      {/* ── Two-column main area ── */}
      <main className="max-w-7xl mx-auto px-6 pb-10">
        {error && (
          <div className="mb-5 bg-red-900/60 border border-red-400/40 text-red-200 px-4 py-3 rounded-lg text-sm backdrop-blur-sm">
            <strong>Error: </strong>{error}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">

          {/* ── Left column: input form ── */}
          <AdvisorForm onResult={setResult} onError={setError} />

          {/* ── Right column: results or placeholder ── */}
          {result ? (
            <ResultCard result={result} />
          ) : (
            <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-2xl p-10 flex flex-col items-center justify-center text-center min-h-[520px]">
              {/* Simple SVG illustration – beach chairs on a shore */}
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 200 120"
                className="w-40 h-24 mb-6 opacity-80"
              >
                {/* Sun */}
                <circle cx="160" cy="30" r="18" fill="#FFD166" opacity="0.9" />
                {/* Rays */}
                {[0,45,90,135,180,225,270,315].map((deg, i) => (
                  <line
                    key={i}
                    x1={160 + 22 * Math.cos((deg * Math.PI) / 180)}
                    y1={30 + 22 * Math.sin((deg * Math.PI) / 180)}
                    x2={160 + 30 * Math.cos((deg * Math.PI) / 180)}
                    y2={30 + 30 * Math.sin((deg * Math.PI) / 180)}
                    stroke="#FFD166"
                    strokeWidth="2"
                    strokeLinecap="round"
                    opacity="0.7"
                  />
                ))}
                {/* Sea */}
                <rect x="0" y="80" width="200" height="40" fill="#3a86ff" opacity="0.5" rx="2" />
                <path d="M0 80 Q25 74 50 80 Q75 86 100 80 Q125 74 150 80 Q175 86 200 80" fill="none" stroke="#ffffff" strokeWidth="1.5" opacity="0.4" />
                {/* Beach */}
                <ellipse cx="100" cy="82" rx="100" ry="10" fill="#f4a261" opacity="0.6" />
                {/* Chair 1 */}
                <rect x="55" y="62" width="22" height="4" rx="2" fill="#fff" opacity="0.8" />
                <rect x="57" y="58" width="18" height="10" rx="2" fill="#e9c46a" opacity="0.9" />
                <line x1="57" y1="72" x2="55" y2="82" stroke="#fff" strokeWidth="1.5" opacity="0.7" />
                <line x1="75" y1="72" x2="77" y2="82" stroke="#fff" strokeWidth="1.5" opacity="0.7" />
                {/* Chair 2 */}
                <rect x="123" y="62" width="22" height="4" rx="2" fill="#fff" opacity="0.8" />
                <rect x="125" y="58" width="18" height="10" rx="2" fill="#e9c46a" opacity="0.9" />
                <line x1="125" y1="72" x2="123" y2="82" stroke="#fff" strokeWidth="1.5" opacity="0.7" />
                <line x1="143" y1="72" x2="145" y2="82" stroke="#fff" strokeWidth="1.5" opacity="0.7" />
                {/* Umbrella */}
                <line x1="100" y1="45" x2="100" y2="82" stroke="#fff" strokeWidth="1.5" opacity="0.7" />
                <path d="M78 55 Q100 38 122 55" fill="#e76f51" opacity="0.85" />
              </svg>

              <h3 className="text-white text-xl font-semibold">
                Your assessment will appear here
              </h3>
              <p className="text-white/60 text-sm mt-2 max-w-xs leading-relaxed">
                Complete the form on the left and click&nbsp;
                <span className="text-white/80 font-medium">"Get My Retirement Assessment"</span>
                &nbsp;to see your personalised score, projections, and recommended actions.
              </p>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
