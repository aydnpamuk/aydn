# Amazon PPC & SEO Management System 🚀

Professional-grade Amazon advertising and SEO optimization platform based on the comprehensive PPC & SEO Bible v3.0.

## 🎯 Features

### Core Capabilities
- **Campaign Management**: Auto, Manual (Exact/Phrase/Broad), Product Targeting
- **Keyword Optimization**: Discovery, harvesting, strike zone analysis
- **Performance Metrics**: ACoS, TACOS, CTR, CVR, RPC calculations
- **Decision Trees**: Automated decision-making based on performance data
- **Crisis Protocols**: Stock-out, BSR drops, listing issues, review crises
- **Multi-Marketplace**: Support for US, UK, DE, CA, FR, IT, ES

### Intelligent Systems
- **User Profiling**: Beginner/Intermediate/Advanced adaptive responses
- **Budget Optimization**: Smart allocation based on performance
- **Placement Modifiers**: TOS, ROS, PP strategic bidding
- **A/B Testing**: Image, title, price optimization tracking
- **Seasonal Strategy**: Q1-Q4 planning and event management

### Analytics & Reporting
- **SQP Analysis**: Search Query Performance tracking
- **Competitor Intelligence**: ASIN targeting and market analysis
- **Strike Zone Detection**: Organic rank 20-50 opportunities
- **Wasted Spend Tracking**: Automatic negative keyword suggestions

## 🏗️ Architecture

```
src/
├── core/                   # Core business logic
│   ├── metrics/           # ACoS, TACOS, CTR, CVR calculations
│   ├── formulas/          # RPC, bid optimization formulas
│   ├── benchmarks/        # Industry benchmarks
│   └── constants/         # Golden rules, thresholds
├── campaign/              # Campaign management
│   ├── models/            # Campaign, AdGroup, Keyword models
│   ├── strategies/        # Auto, Manual, Product targeting
│   └── optimization/      # Bid adjustment, budget management
├── keyword/               # Keyword management
│   ├── discovery/         # Search term harvesting
│   ├── research/          # Cerebro, Magnet integration
│   └── negative/          # Negative keyword management
├── decision/              # Decision trees
│   ├── acos/              # ACoS management decisions
│   ├── ctr/               # CTR optimization decisions
│   ├── bsr/               # BSR drop protocols
│   └── wasted_spend/      # Waste detection
├── crisis/                # Crisis management
│   ├── stockout/          # Stock crisis protocols
│   ├── listing/           # Listing suppression
│   ├── review/            # Review crisis management
│   └── competitor/        # Competitor attack response
├── analytics/             # Analytics and reporting
│   ├── sqp/               # Search Query Performance
│   ├── strike_zone/       # Strike zone analysis
│   └── reporting/         # Report generation
├── user/                  # User profiling
│   ├── profiling/         # User type detection
│   └── adaptation/        # Response adaptation
├── automation/            # Automation rules
│   ├── rules/             # Rule engine
│   └── scheduling/        # Dayparting, scheduling
└── cli/                   # CLI application
    └── commands/          # CLI commands
```

## 🛠️ Technology Stack

- **Backend**: Python 3.11+
- **CLI**: Typer
- **Data Analysis**: Pandas, NumPy
- **Validation**: Pydantic
- **Testing**: Pytest
- **Formatting**: Ruff

## 📦 Installation

```bash
# Clone repository
git clone <repository-url>
cd aydn

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt -r requirements-dev.txt

# Run tests
make test
```

## 🚀 Quick Start

### CLI Usage

```bash
# Analyze campaign performance
python -m src.cli analyze campaign --id "SP_AUTO_001"

# Check for wasted spend
python -m src.cli check wasted-spend --threshold 20

# Run crisis protocol
python -m src.cli crisis stockout --product "ASIN123"

# Optimize bids using RPC formula
python -m src.cli optimize bids --campaign "SP_EXACT_HERO"

# Generate weekly report
python -m src.cli report weekly
```

### Python SDK Usage

```python
from src.core.metrics import Metrics
from src.campaign.models import Campaign
from src.decision.acos import AcosDecisionTree

# Calculate metrics
metrics = Metrics.calculate(
    ad_spend=500,
    ad_sales=2000,
    total_sales=5000
)
print(f"ACoS: {metrics.acos}%")
print(f"TACOS: {metrics.tacos}%")

# Create campaign
campaign = Campaign(
    name="SP - Leather Wallet - Exact",
    type="MANUAL_EXACT",
    budget=50.0,
    target_acos=0.25
)

# Run decision tree
decision = AcosDecisionTree.evaluate(
    acos=0.67,
    clicks=25,
    cvr=0.08
)
print(decision.action)  # "Decrease bid by 40%"
```

## 📊 Example Workflows

### 1. New Product Launch

```python
from src.workflows.launch import ProductLaunch

launch = ProductLaunch(
    asin="B0123456",
    budget=100,
    target_tacos=0.30
)

# Generate 60-day launch plan
plan = launch.generate_plan()
```

### 2. Campaign Optimization

```python
from src.workflows.optimization import CampaignOptimization

optimizer = CampaignOptimization(campaign_id="SP_AUTO_001")

# Run weekly optimization
results = optimizer.run_weekly_check()
```

## 🧪 Testing

```bash
# Run all tests
make test

# Run specific test
pytest tests/core/test_metrics.py

# Run with coverage
pytest --cov=src
```

## 📖 Project Structure

- `src/` — Main application code
- `tests/` — Pytest test suite
- `Makefile` — Format, lint, and test commands
- `requirements.txt` — Production dependencies
- `requirements-dev.txt` — Development dependencies
- `.ruff.toml` — Ruff linter configuration
- `pyproject.toml` — Package configuration

## 📝 License

MIT License

## 🙏 Acknowledgments

Based on the comprehensive Amazon PPC & SEO Bible v3.0

---

**Version**: 1.0.0
**Last Updated**: 2024-12-23
**Rating**: 9.5/10
