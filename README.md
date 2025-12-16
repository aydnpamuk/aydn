# Amazon Private Label Product Analyzer (AYDN)

🚀 **Data-driven analysis tool for Amazon Private Label product opportunities**

This application implements a comprehensive research-based framework for evaluating private label products on Amazon. It combines data from multiple sources (Helium 10, SellerSprite, Keepa) and applies industry best practices to provide RED/YELLOW/GREEN decisions.

---

## 📋 Features

### Core Analysis Rules

✅ **Price Barrier Check** ($39/€39 rule)
- Ensures products meet minimum price threshold for sustainable margins
- Based on Amazon fee structure and profit margin requirements

✅ **Brand Dominance Analysis** (50% monopoly rule)
- Detects market monopolies and Amazon's private label presence
- Uses Click Concentration metrics from SellerSprite

✅ **Keyword Volume Validation** (3,000+ monthly searches)
- Verifies sufficient market demand
- Supports long-tail keyword strategies

✅ **Data Triangulation**
- Cross-validates data from multiple sources
- Industry best practice: never rely on single data source

✅ **Comprehensive Reporting**
- JSON and CSV output formats
- Detailed risk assessment and recommendations
- Actionable next steps

---

## 🏗️ Architecture

```
src/
├── app.py                  # Main CLI application
├── core/
│   ├── config.py          # Configuration management
│   └── models.py          # Pydantic data models
├── api/
│   ├── base.py            # Base API client with retry logic
│   ├── helium10.py        # Helium 10 API integration
│   ├── sellersprite.py    # SellerSprite API integration
│   └── keepa.py           # Keepa API integration
├── analyzers/
│   ├── price_barrier.py   # $39 rule implementation
│   ├── brand_dominance.py # Monopoly detection
│   ├── keyword_volume.py  # Search volume analysis
│   └── triangulation.py   # Cross-validation engine
├── decision/
│   └── scoring.py         # RED/YELLOW/GREEN decision engine
├── reports/
│   ├── json_reporter.py   # JSON report generator
│   └── csv_reporter.py    # CSV report generator
└── utils/
    └── logger.py          # Logging configuration
```

---

## 🚀 Installation

### Requirements

- Python 3.9+
- API Keys for:
  - Helium 10 (optional)
  - SellerSprite (optional)
  - Keepa (optional)

### Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd aydn
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt -r requirements-dev.txt
   ```

4. **Configure API keys**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

5. **Verify installation**
   ```bash
   python -m src.app validate
   ```

---

## 📖 Usage

### Basic Product Analysis

Analyze a product by ASIN and target keyword:

```bash
python -m src.app analyze B08N5WRWNW "hydraulic crimper" -m US -f json
```

**Options:**
- `-m, --marketplace`: Amazon marketplace (US, UK, DE, FR, IT, ES, CA, JP)
- `-f, --output-format`: Report format (json, csv, both, none)
- `-o, --output-dir`: Output directory for reports

### Validate API Configuration

Check if API keys are properly configured:

```bash
python -m src.app validate
```

### Example Output

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃           Analysis Result                    ┃
┃ ✅ GREEN                                     ┃
┃                                              ┃
┃ Overall Score: 78.5/100                     ┃
┃                                              ┃
┃ ✓ APPROVE - This product meets all         ┃
┃ criteria and shows strong potential.        ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

Detailed Analysis
┌─────────────────────┬────────┬───────┬─────────────────┐
│ Rule                │ Status │ Score │ Details         │
├─────────────────────┼────────┼───────┼─────────────────┤
│ Price Barrier       │   ✓    │ 85.0  │ T:39.0 | A:49.0 │
│ Brand Dominance     │   ✓    │ 75.0  │ T:0.5 | A:0.35  │
│ Keyword Volume      │   ✓    │ 80.0  │ T:3000 | A:5200  │
│ Triangulation       │   ✓    │ 90.0  │ T:0.3 | A:0.85  │
└─────────────────────┴────────┴───────┴─────────────────┘

Next Steps:
  1. Source suppliers on Alibaba/1688
  2. Request product samples
  3. Calculate landed costs and margins
  4. Design packaging and branding
  5. Plan product launch strategy
```

---

## ⚙️ Configuration

All settings can be configured in `.env` file:

### API Keys
```env
HELIUM10_API_KEY=your_key_here
SELLERSPRITE_API_KEY=your_key_here
KEEPA_API_KEY=your_key_here
```

### Analysis Thresholds
```env
PRICE_BARRIER_USD=39.0
BRAND_DOMINANCE_THRESHOLD=0.50
MIN_KEYWORD_VOLUME=3000
CLICK_CONCENTRATION_THRESHOLD=0.60
TITLE_DENSITY_THRESHOLD=5.0
```

### Scoring Weights (must sum to 1.0)
```env
WEIGHT_PRICE_BARRIER=0.25
WEIGHT_BRAND_DOMINANCE=0.25
WEIGHT_KEYWORD_VOLUME=0.20
WEIGHT_REVIEW_VELOCITY=0.10
WEIGHT_TITLE_DENSITY=0.10
WEIGHT_TRIANGULATION=0.10
```

### Decision Thresholds
```env
GREEN_THRESHOLD=70.0    # >= 70 = GREEN
YELLOW_THRESHOLD=40.0   # 40-70 = YELLOW, < 40 = RED
```

---

## 🧪 Testing

Run tests with pytest:

```bash
# Run all tests
make test

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_price_barrier.py -v
```

---

## 📊 Analysis Methodology

### 1. Price Barrier ($39 Rule)

**Research Basis:**
- Amazon fee structure: 8-15% referral + FBA fulfillment + storage + PPC (15-25% TACoS)
- Rule of Three: 1/3 COGS, 1/3 Amazon fees, 1/3 profit
- $30 product ≈ $10 net profit (unsustainable)

**Decision Logic:**
- < $27 (70% of threshold): RED
- $27-$39: YELLOW
- $39-$58: GREEN
- > $58: GREEN (high score)

### 2. Brand Dominance (50% Rule)

**Research Basis:**
- Click Concentration > 60% = high monopoly
- Amazon has 400+ private label brands
- FTC investigation: Amazon uses seller data

**Decision Logic:**
- Amazon detected in top 3: RED (auto-reject)
- Click concentration > 70%: RED
- 50-70%: YELLOW
- < 50%: GREEN

### 3. Keyword Volume (3,000 Minimum)

**Research Basis:**
- Low volume = low demand = limited sales potential
- 3,000+ monthly searches recommended for sustainable business
- Long-tail strategy: 1,000-3,000 acceptable with low competition

**Decision Logic:**
- < 900 (30% of threshold): RED
- 900-3,000: YELLOW
- 3,000-6,000: GREEN
- > 6,000: GREEN (verify competition)

### 4. Triangulation (Cross-Validation)

**Research Basis:**
- Each tool has different data sources and algorithms
- Amazon doesn't share official data (except ABA)
- Industry best practice: never rely on single source

**Validation Matrix:**
- Sales: Helium 10 Xray vs SellerSprite vs Keepa BSR Drops
- Keywords: Helium 10 Magnet/Cerebro vs SellerSprite ABA
- Competition: Title Density vs Click Concentration vs Seller Count

---

## 📚 API Documentation

### Helium 10 Integration

**Features Used:**
- **Black Box**: Product discovery with filters
- **Xray**: Real-time market analysis
- **Cerebro**: Keyword research and Title Density
- **CPR**: 8-day giveaway estimate

### SellerSprite Integration

**Features Used:**
- **Click Concentration**: Top 3 products' click share
- **Traffic Analysis**: Organic vs sponsored traffic
- **ABA Data**: Amazon Brand Analytics
- **Market Analysis**: 16-dimensional evaluation

### Keepa Integration

**Features Used:**
- **Price History**: Historical price charts
- **BSR Tracking**: Sales rank changes
- **Buy Box Analysis**: Buy Box ownership
- **Race to Bottom**: Price war detection

---

## 🛣️ Roadmap

- [ ] Black Box integration for product discovery
- [ ] Batch analysis mode for multiple products
- [ ] Web dashboard for results visualization
- [ ] Patent/IP risk checking
- [ ] Supplier research integration
- [ ] PPC cost estimation
- [ ] Seasonality trend analysis
- [ ] Email alerts for opportunities

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is proprietary software. All rights reserved.

---

## 📧 Contact

For questions or support, please contact: [your-email@example.com]

---

## 🙏 Acknowledgments

This application is based on comprehensive research of Amazon FBA best practices and implements methodologies from:

- Jungle Scout State of the Amazon Seller Reports
- Helium 10 Official Documentation
- SellerSprite Market Analysis Framework
- Industry expert blogs and case studies

---

## ⚠️ Disclaimer

This tool provides analysis based on available data and industry research. It does not guarantee success in Amazon private label business. Always conduct your own due diligence, verify data from multiple sources, and consult with business advisors before making significant investments.

Amazon, Amazon FBA, and related trademarks are property of Amazon.com, Inc. or its affiliates. This project is not affiliated with, endorsed by, or sponsored by Amazon.
