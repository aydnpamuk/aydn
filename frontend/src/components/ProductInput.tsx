import { useState } from 'react'
import { api, ScrapeJobCreate } from '../api/client'

interface ProductInputProps {
  onJobCreated: (jobId: string) => void
  onAsinSelected: (asin: string) => void
}

export default function ProductInput({ onJobCreated, onAsinSelected }: ProductInputProps) {
  const [productUrls, setProductUrls] = useState<string>('')
  const [marketplace, setMarketplace] = useState<string>('us')
  const [ratingFilter, setRatingFilter] = useState<'negative' | 'positive' | 'all'>('negative')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [uploadMode, setUploadMode] = useState<'scrape' | 'upload'>('upload')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    try {
      const urls = productUrls.split('\n').filter(url => url.trim())

      if (urls.length === 0) {
        throw new Error('Please enter at least one product URL or ASIN')
      }

      if (urls.length > 10) {
        throw new Error('Maximum 10 products allowed')
      }

      const jobData: ScrapeJobCreate = {
        product_urls: urls,
        marketplace,
        rating_filter: ratingFilter,
      }

      const response = await api.createScrapeJob(jobData)
      onJobCreated(response.data.job_id)

      // Select first ASIN for display
      if (response.data.asins.length > 0) {
        onAsinSelected(response.data.asins[0])
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to create job')
    } finally {
      setLoading(false)
    }
  }

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    setError(null)
    setLoading(true)

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('marketplace', marketplace)

      // Assuming ASIN is part of filename or user will provide
      const asin = prompt('Enter the ASIN for this HTML file:')
      if (!asin) {
        throw new Error('ASIN is required')
      }

      formData.append('asin', asin)

      if (file.name.endsWith('.html') || file.name.endsWith('.htm')) {
        await api.uploadHtml(formData)
      } else if (file.name.endsWith('.csv')) {
        await api.uploadCsv(formData)
      } else {
        throw new Error('Invalid file type. Please upload HTML or CSV')
      }

      alert('File uploaded successfully!')
      onAsinSelected(asin)
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to upload file')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <h2 className="text-2xl font-semibold mb-4">Add Products</h2>

      {/* Mode selector */}
      <div className="mb-6">
        <div className="flex space-x-4">
          <button
            onClick={() => setUploadMode('upload')}
            className={`px-4 py-2 rounded-lg font-medium ${
              uploadMode === 'upload'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700'
            }`}
          >
            📁 Manual Upload (Recommended)
          </button>
          <button
            onClick={() => setUploadMode('scrape')}
            className={`px-4 py-2 rounded-lg font-medium ${
              uploadMode === 'scrape'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700'
            }`}
          >
            🤖 Controlled Scraping
          </button>
        </div>
      </div>

      {uploadMode === 'upload' ? (
        /* Manual Upload Mode */
        <div className="space-y-4">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="font-semibold text-blue-900 mb-2">✅ Recommended: Manual Upload</h3>
            <p className="text-sm text-blue-800">
              This method is 100% compliant with Amazon's Terms of Service:
            </p>
            <ol className="list-decimal list-inside text-sm text-blue-800 mt-2 space-y-1">
              <li>Open Amazon product reviews in your browser</li>
              <li>Save the page as HTML (Ctrl+S / Cmd+S)</li>
              <li>Upload the HTML file below</li>
            </ol>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Marketplace
            </label>
            <select
              value={marketplace}
              onChange={(e) => setMarketplace(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            >
              <option value="us">🇺🇸 Amazon.com (US)</option>
              <option value="de">🇩🇪 Amazon.de (Germany)</option>
              <option value="uk">🇬🇧 Amazon.co.uk (UK)</option>
              <option value="fr">🇫🇷 Amazon.fr (France)</option>
              <option value="it">🇮🇹 Amazon.it (Italy)</option>
              <option value="es">🇪🇸 Amazon.es (Spain)</option>
              <option value="ca">🇨🇦 Amazon.ca (Canada)</option>
              <option value="jp">🇯🇵 Amazon.co.jp (Japan)</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Upload HTML or CSV File
            </label>
            <input
              type="file"
              accept=".html,.htm,.csv"
              onChange={handleFileUpload}
              disabled={loading}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>
        </div>
      ) : (
        /* Scraping Mode */
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <h3 className="font-semibold text-yellow-900 mb-2">⚠️ Controlled Scraping</h3>
            <p className="text-sm text-yellow-800">
              This mode scrapes reviews with careful rate limiting. Use responsibly:
            </p>
            <ul className="list-disc list-inside text-sm text-yellow-800 mt-2 space-y-1">
              <li>Limited to 10 pages per product</li>
              <li>2-5 second delays between requests</li>
              <li>Non-headless browser (visible operation)</li>
              <li>May encounter CAPTCHA or rate limits</li>
            </ul>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Product URLs or ASINs (one per line, max 10)
            </label>
            <textarea
              value={productUrls}
              onChange={(e) => setProductUrls(e.target.value)}
              placeholder="https://amazon.com/dp/B08N5WRWNW&#10;B07XQK7H3P&#10;..."
              rows={5}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Marketplace
            </label>
            <select
              value={marketplace}
              onChange={(e) => setMarketplace(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            >
              <option value="us">🇺🇸 Amazon.com (US)</option>
              <option value="de">🇩🇪 Amazon.de (Germany)</option>
              <option value="uk">🇬🇧 Amazon.co.uk (UK)</option>
              <option value="fr">🇫🇷 Amazon.fr (France)</option>
              <option value="it">🇮🇹 Amazon.it (Italy)</option>
              <option value="es">🇪🇸 Amazon.es (Spain)</option>
              <option value="ca">🇨🇦 Amazon.ca (Canada)</option>
              <option value="jp">🇯🇵 Amazon.co.jp (Japan)</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Review Filter
            </label>
            <select
              value={ratingFilter}
              onChange={(e) => setRatingFilter(e.target.value as any)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            >
              <option value="negative">⭐ Negative Reviews (≤4 stars)</option>
              <option value="positive">⭐⭐⭐⭐⭐ Positive Reviews (≥4 stars)</option>
              <option value="all">All Reviews</option>
            </select>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400"
          >
            {loading ? 'Creating Job...' : 'Start Scraping'}
          </button>
        </form>
      )}

      {error && (
        <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}
    </div>
  )
}
