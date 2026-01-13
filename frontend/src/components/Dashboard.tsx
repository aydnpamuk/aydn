import { useEffect, useState } from 'react'
import { api, ReviewStats } from '../api/client'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, PieChart, Pie, Cell } from 'recharts'

interface DashboardProps {
  asin: string
}

const COLORS = ['#ef4444', '#f97316', '#eab308', '#84cc16', '#22c55e']
const SENTIMENT_COLORS = {
  negative: '#ef4444',
  neutral: '#eab308',
  positive: '#22c55e',
}

export default function Dashboard({ asin }: DashboardProps) {
  const [stats, setStats] = useState<ReviewStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await api.getReviewStats({ asin })
        setStats(response.data)
      } catch (error) {
        console.error('Error fetching stats:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
  }, [asin])

  if (loading) {
    return (
      <div className="bg-white shadow rounded-lg p-6">
        <p className="text-gray-600">Loading statistics...</p>
      </div>
    )
  }

  if (!stats || stats.total_reviews === 0) {
    return (
      <div className="bg-white shadow rounded-lg p-6">
        <p className="text-gray-600">No review data available for this product.</p>
      </div>
    )
  }

  // Prepare chart data
  const ratingData = Object.entries(stats.rating_distribution).map(([rating, count]) => ({
    rating: `${rating} ⭐`,
    count,
  }))

  const sentimentData = Object.entries(stats.sentiment_distribution).map(([label, count]) => ({
    name: label,
    value: count,
  }))

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-sm font-medium text-gray-500 mb-2">Total Reviews</h3>
          <p className="text-3xl font-bold text-gray-900">{stats.total_reviews}</p>
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-sm font-medium text-gray-500 mb-2">Average Rating</h3>
          <p className="text-3xl font-bold text-gray-900">
            {stats.average_rating} ⭐
          </p>
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-sm font-medium text-gray-500 mb-2">Verified Purchases</h3>
          <p className="text-3xl font-bold text-gray-900">
            {stats.verified_percentage}%
          </p>
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-sm font-medium text-gray-500 mb-2">Negative Reviews</h3>
          <p className="text-3xl font-bold text-red-600">
            {Object.entries(stats.rating_distribution)
              .filter(([rating]) => parseInt(rating) <= 4)
              .reduce((sum, [, count]) => sum + count, 0)}
          </p>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Rating Distribution */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">Rating Distribution</h3>
          <BarChart width={400} height={300} data={ratingData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="rating" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="count" fill="#3b82f6">
              {ratingData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        </div>

        {/* Sentiment Distribution */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">Sentiment Distribution</h3>
          <PieChart width={400} height={300}>
            <Pie
              data={sentimentData}
              cx={200}
              cy={150}
              labelLine={false}
              label={({ name, percent }) =>
                `${name}: ${(percent * 100).toFixed(0)}%`
              }
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {sentimentData.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={SENTIMENT_COLORS[entry.name as keyof typeof SENTIMENT_COLORS]}
                />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </div>
      </div>
    </div>
  )
}
