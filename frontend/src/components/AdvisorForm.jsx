import { useState } from 'react'
import { assessRetirement } from '../api/advisor.ts'
import LoadingSpinner from './LoadingSpinner.jsx'

const INITIAL_FORM = {
  age: '',
  retirement_age: '',
  current_salary: '',
  current_pot: '',
  monthly_contribution: '',
  employer_contribution: '',
  retirement_income_goal: '',
}

const FIELDS = [
  {
    name: 'age',
    label: 'Your Current Age',
    monetary: false,
    min: 18,
    max: 79,
    placeholder: 'e.g. 35',
    hint: 'Between 18 and 79',
  },
  {
    name: 'retirement_age',
    label: 'Target Retirement Age',
    monetary: false,
    min: 51,
    max: 80,
    placeholder: 'e.g. 65',
    hint: 'Between 51 and 80',
  },
  {
    name: 'current_salary',
    label: 'Annual Salary',
    monetary: true,
    min: 1,
    placeholder: 'e.g. 45000',
    hint: 'Your gross annual salary (GBP)',
  },
  {
    name: 'current_pot',
    label: 'Current Pension Pot',
    monetary: true,
    min: 0,
    placeholder: 'e.g. 80000',
    hint: 'Total value of all pension pots today',
  },
  {
    name: 'monthly_contribution',
    label: 'Your Monthly Contribution',
    monetary: true,
    min: 0,
    placeholder: 'e.g. 400',
    hint: 'Amount you personally contribute each month',
  },
  {
    name: 'employer_contribution',
    label: 'Employer Monthly Contribution',
    monetary: true,
    min: 0,
    placeholder: 'e.g. 200',
    hint: "Amount your employer adds each month",
  },
  {
    name: 'retirement_income_goal',
    label: 'Target Annual Retirement Income',
    monetary: true,
    min: 1,
    placeholder: 'e.g. 30000',
    hint: "The annual income you want in retirement (today's money)",
  },
]

export default function AdvisorForm({ onResult, onError }) {
  const [form, setForm] = useState(INITIAL_FORM)
  const [loading, setLoading] = useState(false)

  const handleChange = (e) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    onError(null)

    try {
      const req = {
        age: parseInt(form.age, 10),
        retirement_age: parseInt(form.retirement_age, 10),
        current_salary: parseFloat(form.current_salary),
        current_pot: parseFloat(form.current_pot),
        monthly_contribution: parseFloat(form.monthly_contribution),
        employer_contribution: parseFloat(form.employer_contribution),
        retirement_income_goal: parseFloat(form.retirement_income_goal),
      }
      const result = await assessRetirement(req)
      onResult(result)
    } catch (err) {
      onError(err instanceof Error ? err.message : 'An unexpected error occurred')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white rounded-2xl shadow-2xl ring-1 ring-black/5 p-8">
      <h2 className="text-2xl font-bold text-gray-800 mb-1">Your Retirement Details</h2>
      <p className="text-gray-500 text-sm mb-6">
        Fill in your pension information to receive a personalised assessment powered by AI.
      </p>

      <form onSubmit={handleSubmit}>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {FIELDS.map(({ name, label, monetary, min, max, placeholder, hint }) => (
            <div key={name}>
              <label htmlFor={name} className="block text-sm font-medium text-gray-700 mb-1">
                {label}
              </label>
              <div className="relative">
                {monetary && (
                  <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 font-semibold select-none">
                    £
                  </span>
                )}
                <input
                  id={name}
                  name={name}
                  type="number"
                  min={min}
                  max={max}
                  step="1"
                  required
                  value={form[name]}
                  onChange={handleChange}
                  placeholder={placeholder}
                  className={`w-full border border-gray-300 rounded-lg py-2.5 pr-3 text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition ${
                    monetary ? 'pl-7' : 'pl-3'
                  }`}
                />
              </div>
              <p className="text-xs text-gray-400 mt-1">{hint}</p>
            </div>
          ))}
        </div>

        {loading && (
          <div className="mt-6 flex justify-center">
            <LoadingSpinner />
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="mt-6 w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-400 disabled:cursor-not-allowed text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200"
        >
          {loading ? 'Analysing your retirement…' : 'Get My Retirement Assessment'}
        </button>
      </form>
    </div>
  )
}
