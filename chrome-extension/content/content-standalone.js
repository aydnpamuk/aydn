/**
 * Standalone Content Script for AYDN Chrome Extension
 * NO BACKEND REQUIRED - All data stored locally
 */

// State
let isCollecting = false;
let collectedReviews = [];
let currentPage = 1;
let maxPages = 10;
let storage = null;

// Initialize storage when script loads
(async () => {
  storage = window.StorageManager;
  await storage.init();
})();

/**
 * Inject floating action button
 */
function injectFloatingButton() {
  if (document.getElementById('aydn-floating-btn')) {
    return;
  }

  const button = document.createElement('div');
  button.id = 'aydn-floating-btn';
  button.className = 'aydn-fab';
  button.innerHTML = `
    <div class="aydn-fab-icon">📊</div>
    <div class="aydn-fab-tooltip">AYDN: Collect & Save Reviews</div>
  `;

  button.addEventListener('click', () => {
    if (isCollecting) {
      stopCollection();
    } else {
      showCollectionModal();
    }
  });

  document.body.appendChild(button);
}

/**
 * Show collection modal
 */
function showCollectionModal() {
  const existing = document.getElementById('aydn-modal');
  if (existing) existing.remove();

  const productInfo = AmazonReviewParser.extractProductInfo();
  const paginationInfo = AmazonReviewParser.getPaginationInfo();

  const modal = document.createElement('div');
  modal.id = 'aydn-modal';
  modal.className = 'aydn-modal';
  modal.innerHTML = `
    <div class="aydn-modal-content">
      <div class="aydn-modal-header">
        <h2>📊 AYDN Review Collector</h2>
        <button class="aydn-modal-close" id="aydn-close-modal">×</button>
      </div>

      <div class="aydn-modal-body">
        <div class="aydn-info-box">
          <strong>✅ 100% Local Storage</strong>
          <p>All data saved in your browser - no backend needed!</p>
        </div>

        <div class="aydn-product-info">
          <h3>${productInfo.title || 'Product'}</h3>
          <p><strong>ASIN:</strong> ${productInfo.asin}</p>
          <p><strong>Marketplace:</strong> ${productInfo.marketplace.toUpperCase()}</p>
          <p><strong>Current Page:</strong> ${paginationInfo.currentPage}</p>
        </div>

        <div class="aydn-options">
          <label>
            <span>Collection Mode:</span>
            <select id="aydn-mode">
              <option value="current">Current Page Only</option>
            </select>
          </label>

          <label>
            <span>Rating Filter:</span>
            <select id="aydn-rating-filter">
              <option value="all">All Reviews</option>
              <option value="negative" selected>Negative (≤4★)</option>
              <option value="positive">Positive (≥4★)</option>
            </select>
          </label>
        </div>

        <div class="aydn-actions">
          <button id="aydn-start-collection" class="aydn-btn aydn-btn-primary">
            💾 Collect & Save Locally
          </button>
          <button id="aydn-cancel" class="aydn-btn aydn-btn-secondary">
            Cancel
          </button>
        </div>

        <div id="aydn-progress" style="display: none;">
          <div class="aydn-progress-bar">
            <div id="aydn-progress-fill" class="aydn-progress-fill"></div>
          </div>
          <p id="aydn-progress-text">Collecting reviews...</p>
        </div>
      </div>
    </div>
  `;

  document.body.appendChild(modal);

  // Event listeners
  document.getElementById('aydn-close-modal').addEventListener('click', () => modal.remove());
  document.getElementById('aydn-cancel').addEventListener('click', () => modal.remove());
  document.getElementById('aydn-start-collection').addEventListener('click', startCollection);
}

/**
 * Start collection process
 */
async function startCollection() {
  isCollecting = true;
  collectedReviews = [];

  const ratingFilter = document.getElementById('aydn-rating-filter').value;

  // Update UI
  document.getElementById('aydn-start-collection').disabled = true;
  document.getElementById('aydn-progress').style.display = 'block';

  try {
    // Collect current page
    updateProgress('Parsing reviews from page...');
    const pageData = AmazonReviewParser.getPageData();
    let reviews = pageData.reviews;

    // Apply rating filter
    if (ratingFilter === 'negative') {
      reviews = reviews.filter(r => r.rating <= 4);
    } else if (ratingFilter === 'positive') {
      reviews = reviews.filter(r => r.rating >= 4);
    }

    updateProgress(`Found ${reviews.length} reviews, analyzing sentiment...`);

    // Analyze sentiment for each review
    reviews = reviews.map(review => {
      const sentiment = SentimentAnalyzer.analyze(review.text);
      return {
        ...review,
        sentiment_score: sentiment.sentiment_score,
        sentiment_label: sentiment.sentiment_label,
        sentiment_confidence: sentiment.confidence,
        is_negative: review.rating <= 4,
        is_positive: review.rating >= 4
      };
    });

    collectedReviews = reviews;

    updateProgress('Saving to local storage...');

    // Save to IndexedDB
    await saveToStorage(pageData.product, reviews);

    // Show success
    showSuccess(reviews.length);

  } catch (error) {
    console.error('Collection error:', error);
    showError(error.message);
  } finally {
    isCollecting = false;
    document.getElementById('aydn-start-collection').disabled = false;
  }
}

/**
 * Save data to IndexedDB
 */
async function saveToStorage(productInfo, reviews) {
  // Save product
  const product = await storage.saveProduct({
    asin: productInfo.asin,
    title: productInfo.title,
    average_rating: productInfo.average_rating,
    total_reviews: productInfo.total_reviews,
    marketplace: productInfo.marketplace,
    url: productInfo.url
  });

  // Save reviews
  let savedCount = 0;
  let duplicateCount = 0;

  for (const review of reviews) {
    try {
      const saved = await storage.saveReview({
        product_id: product.id,
        review_id: review.review_id,
        asin: productInfo.asin,
        rating: review.rating,
        title: review.title,
        text: review.text,
        verified_purchase: review.verified_purchase,
        author_name: review.author_name,
        review_date: review.review_date,
        helpful_votes: review.helpful_votes,
        marketplace: productInfo.marketplace,
        sentiment_score: review.sentiment_score,
        sentiment_label: review.sentiment_label,
        sentiment_confidence: review.sentiment_confidence,
        is_negative: review.is_negative,
        is_positive: review.is_positive
      });

      if (saved.id) {
        savedCount++;
      } else {
        duplicateCount++;
      }
    } catch (error) {
      console.error('Error saving review:', error);
    }
  }

  return { savedCount, duplicateCount };
}

/**
 * Helper functions
 */
function updateProgress(text) {
  const progressText = document.getElementById('aydn-progress-text');
  if (progressText) {
    progressText.textContent = text;
  }

  const progressFill = document.getElementById('aydn-progress-fill');
  if (progressFill) {
    // Animate progress
    const currentWidth = parseInt(progressFill.style.width) || 0;
    progressFill.style.width = `${Math.min(currentWidth + 25, 90)}%`;
  }
}

function showSuccess(count) {
  const modal = document.getElementById('aydn-modal');
  if (modal) {
    modal.querySelector('.aydn-modal-body').innerHTML = `
      <div class="aydn-success">
        <h3>✅ Collection Complete!</h3>
        <p><strong>${count}</strong> reviews collected and saved locally!</p>
        <p class="aydn-info">Data is stored in your browser's IndexedDB.</p>
        <div class="aydn-actions">
          <button id="aydn-view-dashboard" class="aydn-btn aydn-btn-primary">
            📊 View Dashboard
          </button>
          <button id="aydn-collect-more" class="aydn-btn aydn-btn-secondary">
            Collect More
          </button>
        </div>
      </div>
    `;

    document.getElementById('aydn-view-dashboard').addEventListener('click', () => {
      chrome.runtime.sendMessage({ action: 'openDashboard' });
      modal.remove();
    });

    document.getElementById('aydn-collect-more').addEventListener('click', () => {
      modal.remove();
      showCollectionModal();
    });
  }
}

function showError(message) {
  const modal = document.getElementById('aydn-modal');
  if (modal) {
    modal.querySelector('.aydn-modal-body').innerHTML = `
      <div class="aydn-error">
        <h3>❌ Error</h3>
        <p>${message}</p>
        <p class="aydn-info">Try refreshing the page or collecting from a different page.</p>
        <button id="aydn-close-error" class="aydn-btn aydn-btn-secondary">
          Close
        </button>
      </div>
    `;

    document.getElementById('aydn-close-error').addEventListener('click', () => {
      modal.remove();
    });
  }
}

function stopCollection() {
  isCollecting = false;
  const modal = document.getElementById('aydn-modal');
  if (modal) {
    modal.remove();
  }
}

/**
 * Initialize extension on Amazon review pages
 */
function init() {
  if (window.location.pathname.includes('/product-reviews/')) {
    injectFloatingButton();
    console.log('AYDN Extension: Ready (Standalone Mode - No Backend Required)');
  }
}

// Run on page load
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}

// Listen for URL changes
let lastUrl = location.href;
new MutationObserver(() => {
  const currentUrl = location.href;
  if (currentUrl !== lastUrl) {
    lastUrl = currentUrl;
    init();
  }
}).observe(document, { subtree: true, childList: true });
