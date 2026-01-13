/**
 * Popup script for standalone extension
 */

// Open dashboard
document.getElementById('dashboard-btn').addEventListener('click', () => {
  chrome.tabs.create({
    url: chrome.runtime.getURL('dashboard/dashboard.html')
  });
});

// Export data
document.getElementById('export-btn').addEventListener('click', async () => {
  try {
    // We'll trigger export from dashboard
    chrome.tabs.create({
      url: chrome.runtime.getURL('dashboard/dashboard.html') + '?action=export'
    });
  } catch (error) {
    alert('Error opening dashboard');
  }
});

// Load quick stats
async function loadStats() {
  try {
    const statsContent = document.getElementById('stats-content');
    statsContent.textContent = 'Opening IndexedDB...';

    // Open IndexedDB
    const dbRequest = indexedDB.open('AydnReviewsDB', 1);

    dbRequest.onsuccess = (event) => {
      const db = event.target.result;

      // Count products
      const productTx = db.transaction(['products'], 'readonly');
      const productStore = productTx.objectStore('products');
      const productCountRequest = productStore.count();

      productCountRequest.onsuccess = () => {
        const productCount = productCountRequest.result;

        // Count reviews
        const reviewTx = db.transaction(['reviews'], 'readonly');
        const reviewStore = reviewTx.objectStore('reviews');
        const reviewCountRequest = reviewStore.count();

        reviewCountRequest.onsuccess = () => {
          const reviewCount = reviewCountRequest.result;

          statsContent.innerHTML = `
            📦 ${productCount} Products<br>
            📝 ${reviewCount} Reviews
          `;
        };
      };
    };

    dbRequest.onerror = () => {
      statsContent.textContent = 'No data yet';
    };

  } catch (error) {
    console.error('Error loading stats:', error);
    document.getElementById('stats-content').textContent = 'Error loading stats';
  }
}

// Load stats on popup open
loadStats();
