import { useEffect, useState } from 'react'
import { api, Review } from '../api/client'
import { format } from 'date-fns'

interface ReviewListProps {
  asin: string
}

export default function ReviewList({ asin }: ReviewListProps) {
  const [reviews, setReviews] = useState<Review[]>([])
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [ratingFilter, setRatingFilter] = useState<'all' | 'negative' | 'positive'>('all')
  const [sortBy, setSortBy] = useState<'review_date' | 'rating' | 'helpful_votes'>('review_date')

  useEffect(() => {
    fetchReviews()
  }, [asin, page, ratingFilter, sortBy])

  const fetchReviews = async () => {
    setLoading(true)
    try {
      const params: any = {
        asin,
        page,
        page_size: 20,
        sort_by: sortBy,
        sort_order: 'desc',
      }

      if (ratingFilter === 'negative') {
        params.rating_max = 4
      } else if (ratingFilter === 'positive') {
        params.rating_min = 4
      }

      const response = await api.getReviews(params)
      setReviews(response.data.items)
      setTotalPages(response.data.total_pages)
    } catch (error) {
      console.error('Error fetching reviews:', error)
    } finally {
      setLoading(false)
    }
  }

  const renderStars = (rating: number) => {
    return '⭐'.repeat(rating) + '☆'.repeat(5 - rating)
  }

  const getSentimentBadge = (sentiment?: string, score?: number) => {
    if (!sentiment) return null

    const colors = {
      negative: 'bg-red-100 text-red-800',
      neutral: 'bg-yellow-100 text-yellow-800',
      positive: 'bg-green-100 text-green-800',
    }

    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${colors[sentiment as keyof typeof colors]}`}>
        {sentiment} ({score?.toFixed(2)})
      </span>
    )
  }

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-semibold">Reviews</h2>

        <div className="flex space-x-4">
          {/* Filter */}
          <select
            value={ratingFilter}
            onChange={(e) => {
              setRatingFilter(e.target.value as any)
              setPage(1)
            }}
            className="px-3 py-2 border border-gray-300 rounded-md"
          >
            <option value="all">All Reviews</option>
            <option value="negative">Negative (≤4★)</option>
            <option value="positive">Positive (≥4★)</option>
          </select>

          {/* Sort */}
          <select
            value={sortBy}
            onChange={(e) => {
              setSortBy(e.target.value as any)
              setPage(1)
            }}
            className="px-3 py-2 border border-gray-300 rounded-md"
          >
            <option value="review_date">Latest</option>
            <option value="rating">Rating</option>
            <option value="helpful_votes">Most Helpful</option>
          </select>
        </div>
      </div>

      {loading ? (
        <p className="text-gray-600">Loading reviews...</p>
      ) : reviews.length === 0 ? (
        <p className="text-gray-600">No reviews found.</p>
      ) : (
        <div className="space-y-4">
          {reviews.map((review) => (
            <div key={review.id} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-1">
                    <span className="text-lg">{renderStars(review.rating)}</span>
                    {review.verified_purchase && (
                      <span className="bg-orange-100 text-orange-800 text-xs px-2 py-1 rounded">
                        ✓ Verified Purchase
                      </span>
                    )}
                    {getSentimentBadge(review.sentiment_label, review.sentiment_score)}
                  </div>

                  {review.title && (
                    <h3 className="font-semibold text-gray-900 mb-1">{review.title}</h3>
                  )}

                  <div className="flex items-center space-x-2 text-sm text-gray-600 mb-2">
                    {review.author_name && <span>{review.author_name}</span>}
                    {review.review_date && (
                      <>
                        <span>•</span>
                        <span>{format(new Date(review.review_date), 'MMM d, yyyy')}</span>
                      </>
                    )}
                  </div>
                </div>

                {review.helpful_votes > 0 && (
                  <div className="text-sm text-gray-600">
                    👍 {review.helpful_votes} helpful
                  </div>
                )}
              </div>

              {review.text && (
                <p className="text-gray-700 whitespace-pre-wrap">{review.text}</p>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center space-x-2 mt-6">
          <button
            onClick={() => setPage(page - 1)}
            disabled={page === 1}
            className="px-4 py-2 border border-gray-300 rounded-md disabled:opacity-50"
          >
            Previous
          </button>

          <span className="text-gray-700">
            Page {page} of {totalPages}
          </span>

          <button
            onClick={() => setPage(page + 1)}
            disabled={page === totalPages}
            className="px-4 py-2 border border-gray-300 rounded-md disabled:opacity-50"
          >
            Next
          </button>
        </div>
      )}
    </div>
  )
}
