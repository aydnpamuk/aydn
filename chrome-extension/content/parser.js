/**
 * Amazon Review Parser
 * Parses Amazon review pages and extracts review data
 */

const AmazonReviewParser = {
  /**
   * Detect marketplace from current URL
   */
  detectMarketplace() {
    const hostname = window.location.hostname;
    const marketplaceMap = {
      'amazon.com': 'us',
      'amazon.de': 'de',
      'amazon.co.uk': 'uk',
      'amazon.fr': 'fr',
      'amazon.it': 'it',
      'amazon.es': 'es',
      'amazon.ca': 'ca',
      'amazon.co.jp': 'jp'
    };

    for (const [domain, code] of Object.entries(marketplaceMap)) {
      if (hostname.includes(domain)) {
        return code;
      }
    }
    return 'us'; // default
  },

  /**
   * Extract ASIN from URL
   */
  extractASIN() {
    const url = window.location.pathname;
    const match = url.match(/\/product-reviews\/([A-Z0-9]{10})/);
    return match ? match[1] : null;
  },

  /**
   * Extract product information from the page
   */
  extractProductInfo() {
    const asin = this.extractASIN();

    // Try multiple selectors for product title
    const titleSelectors = [
      'a[data-hook="product-link"]',
      '.a-link-normal[data-hook="product-link"]',
      'h1.a-size-large.a-text-ellipsis'
    ];

    let title = null;
    for (const selector of titleSelectors) {
      const elem = document.querySelector(selector);
      if (elem) {
        title = elem.textContent.trim();
        break;
      }
    }

    // Extract average rating
    const avgRatingElem = document.querySelector('[data-hook="rating-out-of-text"]');
    const avgRating = avgRatingElem ? parseFloat(avgRatingElem.textContent.match(/[\d.]+/)[0]) : null;

    // Extract total review count
    const totalReviewsElem = document.querySelector('[data-hook="total-review-count"]');
    const totalReviews = totalReviewsElem ? parseInt(totalReviewsElem.textContent.replace(/\D/g, '')) : null;

    return {
      asin,
      title,
      average_rating: avgRating,
      total_reviews: totalReviews,
      marketplace: this.detectMarketplace(),
      url: window.location.href
    };
  },

  /**
   * Parse a single review element
   */
  parseReview(reviewElement) {
    try {
      // Review ID
      const reviewId = reviewElement.getAttribute('data-review-id') ||
                      reviewElement.id ||
                      `review_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

      // Rating
      const ratingElem = reviewElement.querySelector('i[data-hook="review-star-rating"], i[data-hook="cmps-review-star-rating"]');
      let rating = null;
      if (ratingElem) {
        const ratingText = ratingElem.textContent || ratingElem.getAttribute('class');
        const ratingMatch = ratingText.match(/(\d+(?:\.\d+)?)/);
        rating = ratingMatch ? parseFloat(ratingMatch[1]) : null;
      }

      // Title
      const titleElem = reviewElement.querySelector('[data-hook="review-title"]');
      const title = titleElem ? titleElem.textContent.trim().replace(/^[\d.]+\s*out of 5 stars\s*/i, '') : null;

      // Review text
      const textElem = reviewElement.querySelector('[data-hook="review-body"]');
      const text = textElem ? textElem.textContent.trim() : null;

      // Author
      const authorElem = reviewElement.querySelector('.a-profile-name');
      const authorName = authorElem ? authorElem.textContent.trim() : null;

      // Date
      const dateElem = reviewElement.querySelector('[data-hook="review-date"]');
      let reviewDate = null;
      if (dateElem) {
        const dateText = dateElem.textContent.trim();
        // Extract date from text like "Reviewed in Germany on December 15, 2023"
        const dateMatch = dateText.match(/on\s+(.+)$/i);
        if (dateMatch) {
          reviewDate = new Date(dateMatch[1]).toISOString().split('T')[0];
        }
      }

      // Verified purchase
      const verifiedElem = reviewElement.querySelector('[data-hook="avp-badge"]');
      const verifiedPurchase = verifiedElem !== null;

      // Helpful votes
      const helpfulElem = reviewElement.querySelector('[data-hook="helpful-vote-statement"]');
      let helpfulVotes = 0;
      if (helpfulElem) {
        const helpfulText = helpfulElem.textContent;
        const helpfulMatch = helpfulText.match(/(\d+)/);
        helpfulVotes = helpfulMatch ? parseInt(helpfulMatch[1]) : 0;
      }

      return {
        review_id: reviewId,
        rating,
        title,
        text,
        author_name: authorName,
        review_date: reviewDate,
        verified_purchase: verifiedPurchase,
        helpful_votes: helpfulVotes,
        marketplace: this.detectMarketplace(),
        asin: this.extractASIN()
      };
    } catch (error) {
      console.error('Error parsing review:', error);
      return null;
    }
  },

  /**
   * Parse all reviews on the current page
   */
  parseAllReviews() {
    const reviewSelectors = [
      '[data-hook="review"]',
      '.review',
      '[id^="customer_review"]'
    ];

    let reviews = [];
    for (const selector of reviewSelectors) {
      const reviewElements = document.querySelectorAll(selector);
      if (reviewElements.length > 0) {
        reviewElements.forEach(elem => {
          const review = this.parseReview(elem);
          if (review && review.rating) {
            reviews.push(review);
          }
        });
        break; // Found reviews, no need to try other selectors
      }
    }

    return reviews;
  },

  /**
   * Get pagination info
   */
  getPaginationInfo() {
    const paginationBar = document.querySelector('.a-pagination');
    if (!paginationBar) {
      return { currentPage: 1, totalPages: 1, hasNext: false };
    }

    // Current page
    const currentPageElem = paginationBar.querySelector('.a-selected');
    const currentPage = currentPageElem ? parseInt(currentPageElem.textContent) : 1;

    // Next page link
    const nextPageLink = paginationBar.querySelector('.a-last:not(.a-disabled) a');
    const hasNext = nextPageLink !== null;

    // Try to find total pages
    const pageLinks = paginationBar.querySelectorAll('.a-normal');
    const totalPages = pageLinks.length > 0 ?
      Math.max(...Array.from(pageLinks).map(link => parseInt(link.textContent))) :
      currentPage;

    return {
      currentPage,
      totalPages,
      hasNext,
      nextPageUrl: hasNext ? nextPageLink.href : null
    };
  },

  /**
   * Get complete page data
   */
  getPageData() {
    return {
      product: this.extractProductInfo(),
      reviews: this.parseAllReviews(),
      pagination: this.getPaginationInfo(),
      scrapedAt: new Date().toISOString()
    };
  }
};

// Make parser available globally for content script
window.AmazonReviewParser = AmazonReviewParser;
