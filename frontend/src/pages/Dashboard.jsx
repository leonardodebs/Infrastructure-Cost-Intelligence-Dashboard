import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useAuth } from '../App'
import {
  getDashboard,
  getAnomalies,
  getForecast,
  getTagCompliance,
  exportCsv,
} from '../services/api'

import StatCard from '../components/StatCard'
import { CostPieChart, DailyTrendChart, TopResourcesChart } from '../components/Charts'

function AnomalyAlert({ anomalies }) {
  if (!anomalies || anomalies.length === 0) return null

  return (
    <div className="bg-amber-50 dark:bg-amber-900/20 border-l-4 border-amber-500 rounded-xl p-5 mb-8 shadow-sm">
      <div className="flex items-start">
        <div className="bg-amber-100 dark:bg-amber-800 p-2 rounded-lg mr-4">
          <span className="text-xl">⚠️</span>
        </div>
        <div>
          <h3 className="font-bold text-amber-900 dark:text-amber-200 text-lg">Potential Anomalies Detected</h3>
          <div className="mt-2 space-y-2">
            {anomalies.slice(0, 3).map((anomaly, idx) => (
              <p key={idx} className="text-sm text-amber-800 dark:text-amber-300">
                <span className="font-semibold">{anomaly.date}</span>: {anomaly.affected_service} spend was 
                <span className="text-amber-600 dark:text-amber-400 font-bold"> {anomaly.deviation_percentage}% </span> 
                above 7-day average.
              </p>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

function TagComplianceTable({ resources }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="bg-slate-50 dark:bg-slate-800/50">
            <th className="text-left p-4 font-semibold text-slate-600 dark:text-slate-400">Resource Name</th>
            <th className="text-left p-4 font-semibold text-slate-600 dark:text-slate-400">Service</th>
            <th className="text-left p-4 font-semibold text-slate-600 dark:text-slate-400">Status</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
          {resources.slice(0, 8).map((r, idx) => (
            <tr key={idx} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/30 transition-colors">
              <td className="p-4 text-slate-800 dark:text-slate-200 font-medium truncate max-w-xs">
                {r.resource_name || r.resource_id}
              </td>
              <td className="p-4 text-slate-600 dark:text-slate-400">{r.service}</td>
              <td className="p-4">
                {r.missing_tags.length > 0 ? (
                  <div className="flex flex-wrap gap-1">
                    {r.missing_tags.map((tag, i) => (
                      <span key={i} className="px-2 py-0.5 bg-rose-100 dark:bg-rose-900/30 text-rose-700 dark:text-rose-400 rounded-md text-[10px] uppercase font-bold tracking-wider">
                        Missing: {tag}
                      </span>
                    ))}
                  </div>
                ) : (
                  <span className="flex items-center gap-1 text-emerald-600 dark:text-emerald-400 font-medium">
                    <span className="w-2 h-2 bg-emerald-500 rounded-full"></span> Compliant
                  </span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default function Dashboard() {
  const { logout } = useAuth()
  const [isExporting, setIsExporting] = useState(false)

  const { data: dashboardData } = useQuery({
    queryKey: ['dashboard'],
    queryFn: async () => {
      const res = await getDashboard()
      return res.data
    },
  })

  const { data: anomalyData } = useQuery({
    queryKey: ['anomalies'],
    queryFn: async () => {
      const res = await getAnomalies(30)
      return res.data.anomalies
    },
  })

  const { data: forecastData } = useQuery({
    queryKey: ['forecast'],
    queryFn: async () => {
      const res = await getForecast()
      return res.data
    },
  })

  const { data: tagData } = useQuery({
    queryKey: ['tagCompliance'],
    queryFn: async () => {
      const res = await getTagCompliance()
      return res.data
    },
  })

  const handleExport = async () => {
    setIsExporting(true)
    try {
      const res = await exportCsv()
      const url = window.URL.createObjectURL(new Blob([res.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', 'aws-cost-report.csv')
      document.body.appendChild(link)
      link.click()
      window.URL.revokeObjectURL(url)
    } finally {
      setIsExporting(false)
    }
  }

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(value)
  }

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900 transition-colors">
      <nav className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center text-white text-xl shadow-indigo-200 shadow-lg">
              IQ
            </div>
            <div>
              <h1 className="text-lg font-bold text-slate-900 dark:text-white leading-tight">CloudCost IQ</h1>
              <p className="text-[10px] text-slate-500 uppercase tracking-widest font-bold">Infrastructure Intelligence</p>
            </div>
          </div>
          <div className="flex items-center gap-6">
            <button
              onClick={handleExport}
              disabled={isExporting}
              className="px-5 py-2.5 bg-slate-900 dark:bg-white text-white dark:text-slate-900 rounded-xl hover:opacity-90 transition shadow-sm text-sm font-semibold flex items-center gap-2"
            >
              {isExporting ? 'Exporting...' : 'Export Report'}
            </button>
            <button onClick={logout} className="text-slate-500 hover:text-rose-600 transition-colors p-2 rounded-lg hover:bg-rose-50 dark:hover:bg-rose-900/10">
              <span className="text-xl">Logout</span>
            </button>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto p-6 md:p-8">
        <header className="mb-8">
          <h2 className="text-3xl font-bold text-slate-900 dark:text-white">Cost Overview</h2>
          <p className="text-slate-500 dark:text-slate-400 mt-1">Real-time AWS infrastructure spending insights.</p>
        </header>

        <AnomalyAlert anomalies={anomalyData} />

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
          <StatCard
            title="Month-to-Date"
            value={formatCurrency(dashboardData?.month_to_date || 0)}
            subtitle="Current cycle spend"
            trend={+2.4}
            icon="💰"
          />
          <StatCard
            title="Monthly Forecast"
            value={formatCurrency(forecastData?.forecast || 0)}
            subtitle={`Based on ${formatCurrency(forecastData?.daily_average || 0)}/day`}
            icon="📈"
          />
          <StatCard
            title="Avg. Daily Spend"
            value={formatCurrency(forecastData?.daily_average || 0)}
            subtitle={`Analyzed over ${forecastData?.days_passed || 0} days`}
            icon="📊"
          />
          <StatCard
            title="Tag Compliance"
            value={`${tagData?.summary?.compliance_percentage || 0}%`}
            subtitle={`${tagData?.summary?.non_compliant_resources || 0} alerts`}
            trend={-1.5}
            icon="🏷️"
          />
        </div>

        <section className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-10">
          <div className="lg:col-span-2 bg-white dark:bg-slate-800 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden">
            <div className="p-6 border-b border-slate-100 dark:border-slate-700 flex items-center justify-between">
              <h3 className="font-bold text-slate-800 dark:text-white">Daily Spending Trend</h3>
              <span className="text-xs font-bold text-slate-400 uppercase">Last 30 Days</span>
            </div>
            <div className="p-6">
              <DailyTrendChart data={dashboardData?.daily_trend || []} />
            </div>
          </div>
          
          <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden">
            <div className="p-6 border-b border-slate-100 dark:border-slate-700">
              <h3 className="font-bold text-slate-800 dark:text-white">Spend by Service</h3>
            </div>
            <div className="p-6">
              <CostPieChart data={dashboardData?.spend_by_service || []} />
            </div>
          </div>
        </section>

        <section className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden">
            <div className="p-6 border-b border-slate-100 dark:border-slate-700">
              <h3 className="font-bold text-slate-800 dark:text-white">Tag Compliance Report</h3>
            </div>
            <TagComplianceTable resources={tagData?.resources || []} />
          </div>

          <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden">
            <div className="p-6 border-b border-slate-100 dark:border-slate-700">
              <h3 className="font-bold text-slate-800 dark:text-white">Top 5 Resource Spend</h3>
            </div>
            <div className="p-6">
              <TopResourcesChart data={dashboardData?.top_resources || []} />
            </div>
          </div>
        </section>
      </main>
    </div>
  )
}
