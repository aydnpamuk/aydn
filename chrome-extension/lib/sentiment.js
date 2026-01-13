/**
 * Simple client-side sentiment analysis
 * Lightweight alternative to VADER
 */

const SentimentAnalyzer = {
  // Negative keywords (common in reviews)
  negativeWords: [
    'bad', 'terrible', 'horrible', 'awful', 'poor', 'worst', 'useless',
    'waste', 'disappointed', 'disappointing', 'broken', 'defective',
    'failed', 'failure', 'problem', 'issue', 'wrong', 'never', 'not',
    'dont', 'doesn\'t', 'didn\'t', 'won\'t', 'wouldn\'t', 'can\'t',
    'hate', 'hated', 'dislike', 'terrible', 'pathetic', 'junk',
    'cheap', 'low quality', 'fell apart', 'stopped working', 'died',
    // Turkish negative words (bonus)
    'kötü', 'berbat', 'çöp', 'işe yaramaz', 'rezalet', 'hayal kırıklığı'
  ],

  // Positive keywords
  positiveWords: [
    'good', 'great', 'excellent', 'amazing', 'awesome', 'wonderful',
    'fantastic', 'perfect', 'love', 'loved', 'best', 'happy',
    'satisfied', 'impressed', 'quality', 'recommend', 'recommended',
    'worth', 'valuable', 'reliable', 'solid', 'sturdy', 'durable',
    'efficient', 'effective', 'beautiful', 'nice', 'works great',
    // Turkish positive words (bonus)
    'güzel', 'harika', 'mükemmel', 'süper', 'kaliteli', 'tavsiye'
  ],

  // Negation words (reverse sentiment)
  negationWords: ['not', 'no', 'never', 'neither', 'nobody', 'nothing', 'nowhere', 'hardly', 'barely', 'scarcely'],

  // Intensifiers
  intensifiers: ['very', 'really', 'extremely', 'absolutely', 'completely', 'totally', 'utterly'],

  /**
   * Analyze sentiment of text
   */
  analyze(text) {
    if (!text || typeof text !== 'string') {
      return {
        sentiment_score: 0,
        sentiment_label: 'neutral',
        confidence: 0
      };
    }

    const normalized = text.toLowerCase();
    const words = normalized.split(/\s+/);

    let score = 0;
    let wordCount = 0;

    for (let i = 0; i < words.length; i++) {
      const word = words[i];
      let wordScore = 0;

      // Check for positive words
      if (this.positiveWords.some(pw => word.includes(pw))) {
        wordScore = 1;
      }

      // Check for negative words
      if (this.negativeWords.some(nw => word.includes(nw))) {
        wordScore = -1;
      }

      // Skip if no sentiment
      if (wordScore === 0) continue;

      // Check for negation before this word
      if (i > 0 && this.negationWords.includes(words[i - 1])) {
        wordScore *= -1;
      }

      // Check for intensifiers
      if (i > 0 && this.intensifiers.includes(words[i - 1])) {
        wordScore *= 1.5;
      }

      score += wordScore;
      wordCount++;
    }

    // Normalize score to -1 to 1 range
    let normalizedScore = 0;
    if (wordCount > 0) {
      normalizedScore = Math.max(-1, Math.min(1, score / Math.sqrt(wordCount)));
    }

    // Determine label
    let label = 'neutral';
    if (normalizedScore > 0.1) {
      label = 'positive';
    } else if (normalizedScore < -0.1) {
      label = 'negative';
    }

    // Calculate confidence based on word count
    const confidence = Math.min(1, wordCount / 10);

    return {
      sentiment_score: Math.round(normalizedScore * 100) / 100,
      sentiment_label: label,
      confidence: Math.round(confidence * 100) / 100
    };
  },

  /**
   * Batch analyze
   */
  batchAnalyze(texts) {
    return texts.map(text => this.analyze(text));
  },

  /**
   * Get sentiment emoji
   */
  getEmoji(label) {
    const emojis = {
      positive: '😊',
      neutral: '😐',
      negative: '😞'
    };
    return emojis[label] || '🤔';
  },

  /**
   * Get sentiment color
   */
  getColor(label) {
    const colors = {
      positive: '#51cf66',
      neutral: '#ffd43b',
      negative: '#ff6b6b'
    };
    return colors[label] || '#868e96';
  }
};

// Export for use in other scripts
if (typeof window !== 'undefined') {
  window.SentimentAnalyzer = SentimentAnalyzer;
}
