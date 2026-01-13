/**
 * IndexedDB Storage Manager for AYDN Extension
 * Stores all data locally in browser
 */

const DB_NAME = 'AydnReviewsDB';
const DB_VERSION = 1;
const STORES = {
  PRODUCTS: 'products',
  REVIEWS: 'reviews',
  SETTINGS: 'settings'
};

class StorageManager {
  constructor() {
    this.db = null;
  }

  /**
   * Initialize database
   */
  async init() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(DB_NAME, DB_VERSION);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        this.db = request.result;
        resolve(this.db);
      };

      request.onupgradeneeded = (event) => {
        const db = event.target.result;

        // Products store
        if (!db.objectStoreNames.contains(STORES.PRODUCTS)) {
          const productStore = db.createObjectStore(STORES.PRODUCTS, {
            keyPath: 'id',
            autoIncrement: true
          });
          productStore.createIndex('asin', 'asin', { unique: false });
          productStore.createIndex('marketplace', 'marketplace', { unique: false });
          productStore.createIndex('created_at', 'created_at', { unique: false });
        }

        // Reviews store
        if (!db.objectStoreNames.contains(STORES.REVIEWS)) {
          const reviewStore = db.createObjectStore(STORES.REVIEWS, {
            keyPath: 'id',
            autoIncrement: true
          });
          reviewStore.createIndex('review_id', 'review_id', { unique: true });
          reviewStore.createIndex('product_id', 'product_id', { unique: false });
          reviewStore.createIndex('asin', 'asin', { unique: false });
          reviewStore.createIndex('rating', 'rating', { unique: false });
          reviewStore.createIndex('is_negative', 'is_negative', { unique: false });
          reviewStore.createIndex('created_at', 'created_at', { unique: false });
        }

        // Settings store
        if (!db.objectStoreNames.contains(STORES.SETTINGS)) {
          db.createObjectStore(STORES.SETTINGS, { keyPath: 'key' });
        }
      };
    });
  }

  /**
   * Save product
   */
  async saveProduct(productData) {
    const transaction = this.db.transaction([STORES.PRODUCTS], 'readwrite');
    const store = transaction.objectStore(STORES.PRODUCTS);

    // Check if product exists
    const index = store.index('asin');
    const existing = await new Promise((resolve) => {
      const request = index.get(productData.asin);
      request.onsuccess = () => resolve(request.result);
    });

    if (existing) {
      // Update existing
      const updated = { ...existing, ...productData, updated_at: new Date().toISOString() };
      return new Promise((resolve, reject) => {
        const request = store.put(updated);
        request.onsuccess = () => resolve(updated);
        request.onerror = () => reject(request.error);
      });
    } else {
      // Create new
      const newProduct = {
        ...productData,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };
      return new Promise((resolve, reject) => {
        const request = store.add(newProduct);
        request.onsuccess = () => {
          newProduct.id = request.result;
          resolve(newProduct);
        };
        request.onerror = () => reject(request.error);
      });
    }
  }

  /**
   * Save review
   */
  async saveReview(reviewData) {
    const transaction = this.db.transaction([STORES.REVIEWS], 'readwrite');
    const store = transaction.objectStore(STORES.REVIEWS);

    // Check if review exists
    const index = store.index('review_id');
    const existing = await new Promise((resolve) => {
      const request = index.get(reviewData.review_id);
      request.onsuccess = () => resolve(request.result);
    });

    if (existing) {
      return existing; // Skip duplicate
    }

    const newReview = {
      ...reviewData,
      created_at: new Date().toISOString()
    };

    return new Promise((resolve, reject) => {
      const request = store.add(newReview);
      request.onsuccess = () => {
        newReview.id = request.result;
        resolve(newReview);
      };
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Get all products
   */
  async getAllProducts() {
    const transaction = this.db.transaction([STORES.PRODUCTS], 'readonly');
    const store = transaction.objectStore(STORES.PRODUCTS);

    return new Promise((resolve, reject) => {
      const request = store.getAll();
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Get product by ASIN
   */
  async getProductByAsin(asin) {
    const transaction = this.db.transaction([STORES.PRODUCTS], 'readonly');
    const store = transaction.objectStore(STORES.PRODUCTS);
    const index = store.index('asin');

    return new Promise((resolve, reject) => {
      const request = index.get(asin);
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Get reviews by ASIN
   */
  async getReviewsByAsin(asin, filters = {}) {
    const transaction = this.db.transaction([STORES.REVIEWS], 'readonly');
    const store = transaction.objectStore(STORES.REVIEWS);
    const index = store.index('asin');

    return new Promise((resolve, reject) => {
      const request = index.getAll(asin);
      request.onsuccess = () => {
        let reviews = request.result;

        // Apply filters
        if (filters.rating_min) {
          reviews = reviews.filter(r => r.rating >= filters.rating_min);
        }
        if (filters.rating_max) {
          reviews = reviews.filter(r => r.rating <= filters.rating_max);
        }
        if (filters.verified_purchase !== undefined) {
          reviews = reviews.filter(r => r.verified_purchase === filters.verified_purchase);
        }
        if (filters.is_negative !== undefined) {
          reviews = reviews.filter(r => r.is_negative === filters.is_negative);
        }

        resolve(reviews);
      };
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Get statistics for a product
   */
  async getProductStats(asin) {
    const reviews = await this.getReviewsByAsin(asin);

    if (reviews.length === 0) {
      return null;
    }

    const stats = {
      total_reviews: reviews.length,
      average_rating: reviews.reduce((sum, r) => sum + r.rating, 0) / reviews.length,
      rating_distribution: {
        1: reviews.filter(r => r.rating === 1).length,
        2: reviews.filter(r => r.rating === 2).length,
        3: reviews.filter(r => r.rating === 3).length,
        4: reviews.filter(r => r.rating === 4).length,
        5: reviews.filter(r => r.rating === 5).length
      },
      sentiment_distribution: {
        negative: reviews.filter(r => r.sentiment_label === 'negative').length,
        neutral: reviews.filter(r => r.sentiment_label === 'neutral').length,
        positive: reviews.filter(r => r.sentiment_label === 'positive').length
      },
      verified_count: reviews.filter(r => r.verified_purchase).length,
      verified_percentage: (reviews.filter(r => r.verified_purchase).length / reviews.length) * 100
    };

    return stats;
  }

  /**
   * Export all data as JSON
   */
  async exportData() {
    const products = await this.getAllProducts();
    const allReviews = [];

    for (const product of products) {
      const reviews = await this.getReviewsByAsin(product.asin);
      allReviews.push(...reviews);
    }

    return {
      version: 1,
      exported_at: new Date().toISOString(),
      products,
      reviews: allReviews
    };
  }

  /**
   * Import data from JSON
   */
  async importData(data) {
    const results = {
      products_imported: 0,
      reviews_imported: 0,
      errors: []
    };

    // Import products
    for (const product of data.products || []) {
      try {
        await this.saveProduct(product);
        results.products_imported++;
      } catch (error) {
        results.errors.push(`Product ${product.asin}: ${error.message}`);
      }
    }

    // Import reviews
    for (const review of data.reviews || []) {
      try {
        await this.saveReview(review);
        results.reviews_imported++;
      } catch (error) {
        results.errors.push(`Review ${review.review_id}: ${error.message}`);
      }
    }

    return results;
  }

  /**
   * Clear all data
   */
  async clearAllData() {
    const transaction = this.db.transaction([STORES.PRODUCTS, STORES.REVIEWS], 'readwrite');

    await Promise.all([
      new Promise((resolve) => {
        transaction.objectStore(STORES.PRODUCTS).clear().onsuccess = resolve;
      }),
      new Promise((resolve) => {
        transaction.objectStore(STORES.REVIEWS).clear().onsuccess = resolve;
      })
    ]);
  }
}

// Create singleton instance
const storage = new StorageManager();

// Export for use in other scripts
if (typeof window !== 'undefined') {
  window.StorageManager = storage;
}
