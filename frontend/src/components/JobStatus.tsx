import { useEffect, useState } from 'react'
import { api, ScrapeJob } from '../api/client'

interface JobStatusProps {
  jobId: string
}

export default function JobStatus({ jobId }: JobStatusProps) {
  const [job, setJob] = useState<ScrapeJob | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchJobStatus = async () => {
      try {
        const response = await api.getJobStatus(jobId)
        setJob(response.data)
        setLoading(false)

        // Continue polling if job is still processing
        if (
          response.data.status === 'pending' ||
          response.data.status === 'processing'
        ) {
          setTimeout(fetchJobStatus, 3000) // Poll every 3 seconds
        }
      } catch (error) {
        console.error('Error fetching job status:', error)
        setLoading(false)
      }
    }

    fetchJobStatus()
  }, [jobId])

  if (loading) {
    return (
      <div className="bg-white shadow rounded-lg p-6">
        <p className="text-gray-600">Loading job status...</p>
      </div>
    )
  }

  if (!job) {
    return null
  }

  const statusColors = {
    pending: 'bg-yellow-100 text-yellow-800',
    processing: 'bg-blue-100 text-blue-800',
    completed: 'bg-green-100 text-green-800',
    failed: 'bg-red-100 text-red-800',
    cancelled: 'bg-gray-100 text-gray-800',
  }

  const statusEmojis = {
    pending: '⏳',
    processing: '⚙️',
    completed: '✅',
    failed: '❌',
    cancelled: '🚫',
  }

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <h2 className="text-xl font-semibold mb-4">Job Status</h2>

      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-gray-700">Status:</span>
          <span
            className={`px-3 py-1 rounded-full text-sm font-medium ${
              statusColors[job.status]
            }`}
          >
            {statusEmojis[job.status]} {job.status.toUpperCase()}
          </span>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-gray-700">Job ID:</span>
          <code className="text-sm bg-gray-100 px-2 py-1 rounded">{job.job_id}</code>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-gray-700">Products:</span>
          <span className="font-medium">
            {job.processed_products} / {job.total_products}
          </span>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-gray-700">Total Reviews:</span>
          <span className="font-medium">{job.total_reviews}</span>
        </div>

        {/* Progress bar */}
        {(job.status === 'processing' || job.status === 'pending') && (
          <div>
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm text-gray-700">Progress:</span>
              <span className="text-sm font-medium">{job.progress}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${job.progress}%` }}
              />
            </div>
          </div>
        )}

        {/* Error message */}
        {job.error_message && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3">
            <p className="text-sm text-red-800">{job.error_message}</p>
          </div>
        )}

        {/* ASINs */}
        <div>
          <span className="text-gray-700 block mb-2">ASINs:</span>
          <div className="flex flex-wrap gap-2">
            {job.asins.map((asin) => (
              <code
                key={asin}
                className="text-xs bg-gray-100 px-2 py-1 rounded"
              >
                {asin}
              </code>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
