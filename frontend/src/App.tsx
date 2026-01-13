import { useState } from 'react'
import { QueryClient, QueryClientProvider } from 'react-query'
import ProductInput from './components/ProductInput'
import Dashboard from './components/Dashboard'
import ReviewList from './components/ReviewList'
import JobStatus from './components/JobStatus'

const queryClient = new QueryClient()

function App() {
  const [activeJobId, setActiveJobId] = useState<string | null>(null)
  const [selectedAsin, setSelectedAsin] = useState<string | null>(null)

  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <h1 className="text-3xl font-bold text-gray-900">
              AYDN - Amazon Review Analyzer
            </h1>
            <p className="mt-1 text-sm text-gray-600">
              Analyze Amazon product reviews ethically and compliantly
            </p>
          </div>
        </header>

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Product Input Section */}
          <section className="mb-8">
            <ProductInput
              onJobCreated={setActiveJobId}
              onAsinSelected={setSelectedAsin}
            />
          </section>

          {/* Job Status Section */}
          {activeJobId && (
            <section className="mb-8">
              <JobStatus jobId={activeJobId} />
            </section>
          )}

          {/* Dashboard Section */}
          {selectedAsin && (
            <>
              <section className="mb-8">
                <Dashboard asin={selectedAsin} />
              </section>

              {/* Review List Section */}
              <section>
                <ReviewList asin={selectedAsin} />
              </section>
            </>
          )}
        </main>

        {/* Footer */}
        <footer className="bg-white border-t mt-12">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <p className="text-center text-sm text-gray-500">
              AYDN - Ethical Amazon Review Analysis Tool
            </p>
            <p className="text-center text-xs text-gray-400 mt-2">
              For research and analysis purposes. Always respect Amazon's Terms of Service.
            </p>
          </div>
        </footer>
      </div>
    </QueryClientProvider>
  )
}

export default App
