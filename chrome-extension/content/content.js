/**
 * Content Script for AYDN Chrome Extension
 * Runs on Amazon review pages and provides scraping functionality
 */

// State
let isCollecting = false;
let collectedReviews = [];
let currentPage = 1;
let maxPages = 10; // Default max pages

/**
 * Inject floating action button
 */
function injectFloatingButton() {
  // Check if button already exists
  if (document.getElementById('aydn-floating-btn')) {
    return;
  }

  const button = document.createElement('div');
  button.id = 'aydn-floating-btn';
  button.className = 'aydn-fab';
  button.innerHTML = `
    <div class="aydn-fab-icon">📊</div>
    <div class="aydn-fab-tooltip">AYDN: Collect Reviews</div>
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
  // Remove existing modal if any
  const existing = document.getElementById('aydn-modal');
  if (existing) {
    existing.remove();
  }

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
        <div class="aydn-product-info">
          <h3>${productInfo.title || 'Product'}</h3>
          <p><strong>ASIN:</strong> ${productInfo.asin}</p>
          <p><strong>Marketplace:</strong> ${productInfo.marketplace.toUpperCase()}</p>
          <p><strong>Current Page:</strong> ${paginationInfo.currentPage} / ${paginationInfo.totalPages}</p>
        </div>

        <div class="aydn-options">
          <label>
            <span>Collection Mode:</span>
            <select id="aydn-mode">
              <option value="current">Current Page Only</option>
              <option value="multi">Multiple Pages</option>
            </select>
          </label>

          <div id="aydn-multi-options" style="display: none;">
            <label>
              <span>Max Pages:</span>
              <input type="number" id="aydn-max-pages" min="1" max="50" value="10">
            </label>
            <p class="aydn-note">⚠️ Respectful scraping: 2-3 second delay between pages</p>
          </div>

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
            🚀 Start Collection
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

  document.getElementById('aydn-mode').addEventListener('change', (e) => {
    const multiOptions = document.getElementById('aydn-multi-options');
    multiOptions.style.display = e.target.value === 'multi' ? 'block' : 'none';
  });
}

/**
 * Start collection process
 */
async function startCollection() {
  isCollecting = true;
  collectedReviews = [];
  currentPage = 1;

  const mode = document.getElementById('aydn-mode').value;
  maxPages = mode === 'multi' ? parseInt(document.getElementById('aydn-max-pages').value) : 1;
  const ratingFilter = document.getElementById('aydn-rating-filter').value;

  // Update UI
  document.getElementById('aydn-start-collection').disabled = true;
  document.getElementById('aydn-progress').style.display = 'block';

  try {
    // Collect current page
    await collectCurrentPage(ratingFilter);

    // Collect additional pages if multi-page mode
    if (mode === 'multi') {
      await collectMultiplePages(ratingFilter);
    }

    // Send to backend
    await sendToBackend();

    // Show success
    showSuccess();
  } catch (error) {
    showError(error.message);
  } finally {
    isCollecting = false;
    document.getElementById('aydn-start-collection').disabled = false;
  }
}

/**
 * Collect reviews from current page
 */
function collectCurrentPage(ratingFilter) {
  return new Promise((resolve) => {
    const pageData = AmazonReviewParser.getPageData();
    let reviews = pageData.reviews;

    // Apply rating filter
    if (ratingFilter === 'negative') {
      reviews = reviews.filter(r => r.rating <= 4);
    } else if (ratingFilter === 'positive') {
      reviews = reviews.filter(r => r.rating >= 4);
    }

    collectedReviews.push(...reviews);

    updateProgress(`Collected ${reviews.length} reviews from page ${currentPage}`);
    resolve();
  });
}

/**
 * Collect reviews from multiple pages
 */
async function collectMultiplePages(ratingFilter) {
  const paginationInfo = AmazonReviewParser.getPaginationInfo();

  while (currentPage < maxPages && paginationInfo.hasNext) {
    // Respectful delay
    await delay(2000 + Math.random() * 1000); // 2-3 seconds

    // Navigate to next page
    const nextPageUrl = paginationInfo.nextPageUrl;
    if (!nextPageUrl) break;

    updateProgress(`Navigating to page ${currentPage + 1}...`);

    // Note: In Chrome extension, we can't directly navigate
    // Instead, we'll open pages in background and collect via messages
    // For now, we'll collect only current page + manual navigation

    currentPage++;
    updateProgress(`Please manually go to page ${currentPage} and click the collect button again`);
    break; // Stop auto-navigation for safety
  }
}

/**
 * Send collected reviews to backend
 */
async function sendToBackend() {
  updateProgress('Sending reviews to backend...');

  const productInfo = AmazonReviewParser.extractProductInfo();

  try {
    // Get backend URL from storage
    const { backendUrl } = await chrome.storage.sync.get({ backendUrl: 'http://localhost:8000' });

    const response = await fetch(`${backendUrl}/api/v1/reviews/bulk`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        product: productInfo,
        reviews: collectedReviews
      })
    });

    if (!response.ok) {
      throw new Error(`Backend error: ${response.status}`);
    }

    const result = await response.json();
    updateProgress(`✅ Successfully sent ${result.saved || collectedReviews.length} reviews!`);

    // Store stats
    chrome.storage.local.set({
      lastCollection: {
        asin: productInfo.asin,
        count: collectedReviews.length,
        timestamp: new Date().toISOString()
      }
    });

  } catch (error) {
    console.error('Backend error:', error);
    throw new Error('Failed to send to backend. Make sure backend is running.');
  }
}

/**
 * Helper functions
 */
function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function updateProgress(text) {
  const progressText = document.getElementById('aydn-progress-text');
  if (progressText) {
    progressText.textContent = text;
  }

  const progressFill = document.getElementById('aydn-progress-fill');
  if (progressFill) {
    const percentage = (collectedReviews.length / (maxPages * 10)) * 100;
    progressFill.style.width = `${Math.min(percentage, 100)}%`;
  }
}

function showSuccess() {
  const modal = document.getElementById('aydn-modal');
  if (modal) {
    modal.querySelector('.aydn-modal-body').innerHTML = `
      <div class="aydn-success">
        <h3>✅ Collection Complete!</h3>
        <p><strong>${collectedReviews.length}</strong> reviews collected and sent to backend.</p>
        <button id="aydn-view-dashboard" class="aydn-btn aydn-btn-primary">
          View Dashboard
        </button>
        <button id="aydn-close-success" class="aydn-btn aydn-btn-secondary">
          Close
        </button>
      </div>
    `;

    document.getElementById('aydn-view-dashboard').addEventListener('click', async () => {
      const { backendUrl } = await chrome.storage.sync.get({ backendUrl: 'http://localhost:8000' });
      window.open(`${backendUrl.replace(':8000', ':3000')}`, '_blank');
    });

    document.getElementById('aydn-close-success').addEventListener('click', () => {
      modal.remove();
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
  // Check if we're on a review page
  if (window.location.pathname.includes('/product-reviews/')) {
    injectFloatingButton();
    console.log('AYDN Extension: Ready on Amazon review page');
  }
}

// Run on page load
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}

// Listen for URL changes (SPA navigation)
let lastUrl = location.href;
new MutationObserver(() => {
  const currentUrl = location.href;
  if (currentUrl !== lastUrl) {
    lastUrl = currentUrl;
    init();
  }
}).observe(document, { subtree: true, childList: true });
