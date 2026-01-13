/**
 * Background Service Worker for AYDN Chrome Extension
 */

// Installation
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === 'install') {
    console.log('AYDN Extension installed');

    // Set default settings
    chrome.storage.sync.set({
      backendUrl: 'http://localhost:8000'
    });

    // Open welcome page
    chrome.tabs.create({
      url: 'https://github.com/aydnpamuk/aydn'
    });
  } else if (details.reason === 'update') {
    console.log('AYDN Extension updated');
  }
});

// Listen for messages from content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'sendReviews') {
    handleSendReviews(request.data)
      .then(result => sendResponse({ success: true, result }))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true; // Keep channel open for async response
  }

  if (request.action === 'testConnection') {
    testBackendConnection()
      .then(result => sendResponse({ success: true, result }))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true;
  }
});

/**
 * Handle sending reviews to backend
 */
async function handleSendReviews(data) {
  const { backendUrl } = await chrome.storage.sync.get({
    backendUrl: 'http://localhost:8000'
  });

  const { product, reviews } = data;

  try {
    const response = await fetch(`${backendUrl}/api/v1/reviews/bulk`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        product,
        reviews
      })
    });

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }

    const result = await response.json();

    // Store last collection info
    await chrome.storage.local.set({
      lastCollection: {
        asin: product.asin,
        count: reviews.length,
        timestamp: new Date().toISOString()
      }
    });

    return result;
  } catch (error) {
    console.error('Error sending reviews:', error);
    throw error;
  }
}

/**
 * Test backend connection
 */
async function testBackendConnection() {
  const { backendUrl } = await chrome.storage.sync.get({
    backendUrl: 'http://localhost:8000'
  });

  try {
    const response = await fetch(`${backendUrl}/health`);

    if (!response.ok) {
      throw new Error(`Backend unhealthy: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Connection test failed:', error);
    throw error;
  }
}

// Context menu integration
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: 'aydn-collect-reviews',
    title: 'AYDN: Collect Reviews',
    contexts: ['page'],
    documentUrlPatterns: [
      '*://*.amazon.com/product-reviews/*',
      '*://*.amazon.de/product-reviews/*',
      '*://*.amazon.co.uk/product-reviews/*',
      '*://*.amazon.fr/product-reviews/*',
      '*://*.amazon.it/product-reviews/*',
      '*://*.amazon.es/product-reviews/*',
      '*://*.amazon.ca/product-reviews/*',
      '*://*.amazon.co.jp/product-reviews/*'
    ]
  });
});

// Handle context menu clicks
chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === 'aydn-collect-reviews') {
    // Send message to content script to start collection
    chrome.tabs.sendMessage(tab.id, {
      action: 'startCollection'
    });
  }
});
