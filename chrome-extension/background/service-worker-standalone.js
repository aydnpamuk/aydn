/**
 * Background Service Worker for AYDN (Standalone Mode)
 * NO BACKEND REQUIRED
 */

// Installation
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === 'install') {
    console.log('AYDN Extension installed (Standalone Mode)');

    // Open dashboard on first install
    chrome.tabs.create({
      url: chrome.runtime.getURL('dashboard/dashboard.html')
    });
  } else if (details.reason === 'update') {
    console.log('AYDN Extension updated');
  }
});

// Listen for messages from content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'openDashboard') {
    chrome.tabs.create({
      url: chrome.runtime.getURL('dashboard/dashboard.html')
    });
    sendResponse({ success: true });
  }

  if (request.action === 'getStats') {
    // Stats will be fetched from IndexedDB by the caller
    sendResponse({ success: true });
  }
});

// Context menu integration
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: 'aydn-collect-reviews',
    title: 'AYDN: Collect Reviews (Local Storage)',
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

  chrome.contextMenus.create({
    id: 'aydn-view-dashboard',
    title: 'AYDN: View Dashboard',
    contexts: ['all']
  });
});

// Handle context menu clicks
chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === 'aydn-collect-reviews') {
    chrome.tabs.sendMessage(tab.id, {
      action: 'startCollection'
    });
  }

  if (info.menuItemId === 'aydn-view-dashboard') {
    chrome.tabs.create({
      url: chrome.runtime.getURL('dashboard/dashboard.html')
    });
  }
});

// Keyboard shortcut (Alt+Shift+A to open dashboard)
chrome.commands.onCommand.addListener((command) => {
  if (command === 'open-dashboard') {
    chrome.tabs.create({
      url: chrome.runtime.getURL('dashboard/dashboard.html')
    });
  }
});
