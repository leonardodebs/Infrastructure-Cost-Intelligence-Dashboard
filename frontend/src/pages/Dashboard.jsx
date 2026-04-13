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
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts'

const COLORS = ['#0ea5e9', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444']

function StatCard({ title, value, subtitle, icon }) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-slate-500">{title}</p>
          <p className="text-2xl font-bold text-slate-800 mt-1">{value}</p>
          {subtitle && (
            <p className="text-sm text-slate-400 mt-1">{subtitle}</p>
          )}
        </div>
        <div className="text-3xl">{icon}</div>
      </div>
    </div>
  )
}

function AnomalyAlert({ anomalies }) {
  if (!anomalies || anomalies.length === 0) return null

  return (
    <div className="bg-red-50 border-l-4 border-red-500 rounded-lg p-4 mb-6">
      <div className="flex items-start">
        <span className="text-2xl mr-3">⚠️</span>
        <div>
          <h3 className="font-semibold text-red-800">Anomalia de Custo Detectada</h3>
          {anomalies.slice(0, 3).map((anomaly, idx) => (
            <p key={idx} className="text-sm text-red-700 mt-1">
              {anomaly.date}: ${anomaly.cost.toFixed(2)} (
              {anomaly.deviation_percentage}% acima da média de 7 dias) -{' '}
              <span className="font-medium">{anomaly.affected_service}</span>
            </p>
          ))}
        </div>
      </div>
    </div>
  )
}

function CostPieChart({ data }) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          innerRadius={60}
          outerRadius={100}
          paddingAngle={2}
          dataKey="cost"
          nameKey="service"
          label={({ name, percent }) =>
            `${name} ${(percent * 100).toFixed(0)}%`
          }
        >
          {data.map((entry, index) => (
            <Cell key={index} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip formatter={(value) => `$${value.toFixed(2)}`} />
      </PieChart>
    </ResponsiveContainer>
  )
}

function DailyTrendChart({ data }) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <AreaChart data={data}>
        <defs>
          <linearGradient id="colorCost" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.3} />
            <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis
          dataKey="date"
          tick={{ fontSize: 12 }}
          tickFormatter={(value) => value.slice(5)}
        />
        <YAxis tick={{ fontSize: 12 }} tickFormatter={(v) => `$${v}`} />
        <Tooltip formatter={(value) => `$${value.toFixed(2)}`} />
        <Area
          type="monotone"
          dataKey="total"
          stroke="#0ea5e9"
          strokeWidth={2}
          fill="url(#colorCost)"
        />
      </AreaChart>
    </ResponsiveContainer>
  )
}

function TopResourcesChart({ data }) {
  return (
    <ResponsiveContainer width="100%" height={250}>
      <BarChart data={data} layout="vertical">
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis type="number" tickFormatter={(v) => `$${v}`} />
        <YAxis
          type="category"
          dataKey="service"
          width={80}
          tick={{ fontSize: 12 }}
        />
        <Tooltip formatter={(value) => `$${value.toFixed(2)}`} />
        <Bar dataKey="cost" fill="#8b5cf6" radius={[0, 4, 4, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}

function TagComplianceTable({ resources }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead className="bg-slate-50">
          <tr>
            <th className="text-left p-3 font-medium text-slate-600">
              Recurso
            </th>
            <th className="text-left p-3 font-medium text-slate-600">
              Tipo
            </th>
            <th className="text-left p-3 font-medium text-slate-600">
              Serviço
            </th>
            <th className="text-left p-3 font-medium text-slate-600">
              Tags Ausentes
            </th>
          </tr>
        </thead>
        <tbody>
          {resources.slice(0, 10).map((r, idx) => (
            <tr key={idx} className="border-t border-slate-100">
              <td className="p-3 text-slate-800 max-w-xs truncate">
                {r.resource_name || r.resource_id}
              </td>
              <td className="p-3 text-slate-600">{r.resource_type}</td>
              <td className="p-3 text-slate-600">{r.service}</td>
              <td className="p-3">
                {r.missing_tags.length > 0 ? (
                  <span className="inline-flex gap-1">
                    {r.missing_tags.map((tag, i) => (
                      <span
                        key={i}
                        className="px-2 py-1 bg-red-100 text-red-700 rounded text-xs"
                      >
                        {tag}
                      </span>
                    ))}
                  </span>
                ) : (
                  <span className="text-green-600">✓ Conforme</span>
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
  const [activeTab, setActiveTab] = useState('overview')

  const { data: dashboardData, isLoading: dashLoading } = useQuery({
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
    const res = await exportCsv()
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'costs.csv')
    document.body.appendChild(link)
    link.click()
    link.remove()
  }

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(value)
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <nav className="bg-white border-b border-slate-200 px-6 py-4">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <div className="flex items-center gap-3">
            <span className="text-2xl">☁️</span>
            <h1 className="text-xl font-bold text-slate-800">CloudCost IQ</h1>
          </div>
          <div className="flex items-center gap-4">
            <button
              onClick={handleExport}
              className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition text-sm font-medium"
            >
              Exportar CSV
            </button>
            <button
              onClick={logout}
              className="text-slate-600 hover:text-slate-800 text-sm font-medium"
            >
              Sair
            </button>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto p-6">
        <AnomalyAlert anomalies={anomalyData} />

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <StatCard
            title="Gasto do Mês"
            value={formatCurrency(dashboardData?.month_to_date || 0)}
            subtitle="Período de cobrança atual"
            icon="💰"
          />
          <StatCard
            title="Projeção Fim do Mês"
            value={formatCurrency(forecastData?.forecast || 0)}
            subtitle={`Baseado em ${forecastData?.daily_average || 0}/dia média`}
            icon="📈"
          />
          <StatCard
            title="Média Diária"
            value={formatCurrency(forecastData?.daily_average || 0)}
            subtitle={`${forecastData?.days_passed || 0} dias passados`}
            icon="📊"
          />
          <StatCard
            title="Conformidade de Tags"
            value={`${tagData?.summary?.compliance_percentage || 0}%`}
            subtitle={`${tagData?.summary?.non_compliant_resources || 0} não conforme`}
            icon="🏷️"
          />
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-slate-200 mb-6">
          <div className="p-4 border-b border-slate-200">
            <h2 className="text-lg font-semibold text-slate-800">
              Tendência de Custo Diário (30 Dias)
            </h2>
          </div>
          <div className="p-4">
            <DailyTrendChart data={dashboardData?.daily_trend || []} />
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <div className="bg-white rounded-xl shadow-sm border border-slate-200">
            <div className="p-4 border-b border-slate-200">
              <h2 className="text-lg font-semibold text-slate-800">
                Gasto por Serviço
              </h2>
            </div>
            <div className="p-4">
              <CostPieChart data={dashboardData?.spend_by_service || []} />
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-slate-200">
            <div className="p-4 border-b border-slate-200">
              <h2 className="text-lg font-semibold text-slate-800">
                Top 5 Recursos Mais Caros
              </h2>
            </div>
            <div className="p-4">
              <TopResourcesChart data={dashboardData?.top_resources || []} />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-slate-200">
          <div className="p-4 border-b border-slate-200">
            <h2 className="text-lg font-semibold text-slate-800">
              Relatório de Conformidade de Tags
            </h2>
            <p className="text-sm text-slate-500 mt-1">
              Recursos com tags obrigatórias ausentes: projeto, ambiente, gerenciado-por
            </p>
          </div>
          <TagComplianceTable resources={tagData?.resources || []} />
        </div>
      </main>
    </div>
  )
}
