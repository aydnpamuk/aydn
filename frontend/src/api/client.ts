import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Types
export interface ScrapeJobCreate {
  product_urls: string[]
  marketplace: string
  rating_filter: 'negative' | 'positive' | 'all'
  max_reviews_per_product?: number
}

export interface ScrapeJob {
  id: number
  job_id: string
  asins: string[]
  marketplace: string
  rating_filter: string
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled'
  progress: number
  total_products: number
  processed_products: number
  total_reviews: number
  error_message?: string
  created_at: string
  started_at?: string
  completed_at?: string
  updated_at: string
}

export interface Review {
  id: number
  review_id: string
  asin: string
  marketplace: string
  rating: number
  title?: string
  text?: string
  verified_purchase: boolean
  author_name?: string
  review_date?: string
  helpful_votes: number
  sentiment_score?: number
  sentiment_label?: string
  is_negative: boolean
  is_positive: boolean
  created_at: string
}

export interface ReviewListResponse {
  items: Review[]
  total: number
  page: number
  page_size: number
  total_pages: number
  has_next: boolean
  has_prev: boolean
}

export interface ReviewStats {
  total_reviews: number
  average_rating: number
  rating_distribution: { [key: string]: number }
  sentiment_distribution: { [key: string]: number }
  verified_percentage: number
}

// API functions
export const api = {
  // Scrape jobs
  createScrapeJob: (data: ScrapeJobCreate) =>
    apiClient.post<ScrapeJob>('/ingest/', data),

  getJobStatus: (jobId: string) =>
    apiClient.get<ScrapeJob>(`/ingest/status/${jobId}`),

  listJobs: (params?: { status?: string; limit?: number; offset?: number }) =>
    apiClient.get<ScrapeJob[]>('/ingest/jobs', { params }),

  cancelJob: (jobId: string) =>
    apiClient.delete(`/ingest/jobs/${jobId}`),

  // Reviews
  getReviews: (params: {
    asin?: string
    marketplace?: string
    rating_min?: number
    rating_max?: number
    sentiment?: string
    verified_only?: boolean
    sort_by?: string
    sort_order?: string
    page?: number
    page_size?: number
  }) => apiClient.get<ReviewListResponse>('/reviews/', { params }),

  getReviewStats: (params: { asin?: string; marketplace?: string }) =>
    apiClient.get<ReviewStats>('/reviews/stats', { params }),

  compareProducts: (asins: string[], marketplace: string) =>
    apiClient.get('/reviews/compare', {
      params: { asins: asins.join(','), marketplace },
    }),

  // Upload
  uploadHtml: (formData: FormData) =>
    apiClient.post('/upload/html', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),

  uploadCsv: (formData: FormData) =>
    apiClient.post('/upload/csv', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
}
