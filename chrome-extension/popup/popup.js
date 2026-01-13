/**
 * Popup Script for AYDN Chrome Extension
 */

// Load settings and status on popup open
document.addEventListener('DOMContentLoaded', async () => {
  await loadSettings();
  await checkStatus();
  await loadLastCollection();
  setupEventListeners();
});

/**
 * Load settings from storage
 */
async function loadSettings() {
  const { backendUrl } = await chrome.storage.sync.get({
    backendUrl: 'http://localhost:8000'
  });

  document.getElementById('backend-url').value = backendUrl;
}

/**
 * Check current tab status
 */
async function checkStatus() {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    if (!tab || !tab.url) {
      updateStatus('⚠️ No active tab', 'warning');
      return;
    }

    const url = tab.url;

    // Check if on Amazon review page
    if (url.includes('amazon.') && url.includes('/product-reviews/')) {
      const asinMatch = url.match(/\/product-reviews\/([A-Z0-9]{10})/);
      const asin = asinMatch ? asinMatch[1] : 'Unknown';

      updateStatus(`✅ On review page (${asin})`, 'success');
    } else if (url.includes('amazon.')) {
      updateStatus('Navigate to product reviews', 'info');
    } else {
      updateStatus('Not on Amazon page', 'warning');
    }
  } catch (error) {
    console.error('Error checking status:', error);
    updateStatus('Error checking page', 'error');
  }
}

/**
 * Update status display
 */
function updateStatus(message, type = 'info') {
  const statusCard = document.getElementById('status-card');
  const statusMessage = document.getElementById('status-message');

  statusMessage.textContent = message;

  // Remove all status classes
  statusCard.classList.remove('status-success', 'status-warning', 'status-error', 'status-info');

  // Add appropriate class
  statusCard.classList.add(`status-${type}`);

  // Update icon
  const statusIcon = statusCard.querySelector('.status-icon');
  const icons = {
    success: '✅',
    warning: '⚠️',
    error: '❌',
    info: '🔍'
  };
  statusIcon.textContent = icons[type] || '🔍';
}

/**
 * Load last collection info
 */
async function loadLastCollection() {
  const { lastCollection } = await chrome.storage.local.get('lastCollection');

  if (lastCollection) {
    document.getElementById('last-collection').style.display = 'block';
    document.getElementById('last-asin').textContent = lastCollection.asin;
    document.getElementById('last-count').textContent = lastCollection.count;

    const date = new Date(lastCollection.timestamp);
    const timeAgo = getTimeAgo(date);
    document.getElementById('last-time').textContent = timeAgo;
  }
}

/**
 * Get time ago string
 */
function getTimeAgo(date) {
  const seconds = Math.floor((new Date() - date) / 1000);

  const intervals = {
    year: 31536000,
    month: 2592000,
    week: 604800,
    day: 86400,
    hour: 3600,
    minute: 60,
    second: 1
  };

  for (const [unit, secondsInUnit] of Object.entries(intervals)) {
    const interval = Math.floor(seconds / secondsInUnit);
    if (interval >= 1) {
      return `${interval} ${unit}${interval > 1 ? 's' : ''} ago`;
    }
  }

  return 'Just now';
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
  // Save settings
  document.getElementById('save-settings').addEventListener('click', async () => {
    const backendUrl = document.getElementById('backend-url').value.trim();

    if (!backendUrl) {
      showMessage('Please enter a backend URL', 'error');
      return;
    }

    // Validate URL
    try {
      new URL(backendUrl);
    } catch (e) {
      showMessage('Invalid URL format', 'error');
      return;
    }

    // Save to storage
    await chrome.storage.sync.set({ backendUrl });

    showMessage('Settings saved!', 'success');

    // Test connection
    testConnection(backendUrl);
  });

  // Open dashboard
  document.getElementById('open-dashboard').addEventListener('click', async () => {
    const { backendUrl } = await chrome.storage.sync.get({
      backendUrl: 'http://localhost:8000'
    });

    const dashboardUrl = backendUrl.replace(':8000', ':3000');
    chrome.tabs.create({ url: dashboardUrl });
  });

  // Open docs
  document.getElementById('open-docs').addEventListener('click', () => {
    chrome.tabs.create({ url: 'https://github.com/aydnpamuk/aydn' });
  });

  // View on GitHub
  document.getElementById('view-on-github').addEventListener('click', (e) => {
    e.preventDefault();
    chrome.tabs.create({ url: 'https://github.com/aydnpamuk/aydn' });
  });
}

/**
 * Show message
 */
function showMessage(text, type = 'info') {
  const messageEl = document.getElementById('save-message');
  messageEl.textContent = text;
  messageEl.className = `message message-${type}`;
  messageEl.style.display = 'block';

  setTimeout(() => {
    messageEl.style.display = 'none';
  }, 3000);
}

/**
 * Test backend connection
 */
async function testConnection(backendUrl) {
  try {
    const response = await fetch(`${backendUrl}/health`, {
      method: 'GET',
      mode: 'cors'
    });

    if (response.ok) {
      showMessage('✅ Backend connection successful!', 'success');
    } else {
      showMessage('⚠️ Backend responded but not healthy', 'warning');
    }
  } catch (error) {
    showMessage('❌ Cannot connect to backend', 'error');
    console.error('Connection test failed:', error);
  }
}
