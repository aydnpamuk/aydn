# Usage Guide

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt -r requirements-dev.txt
```

### 2. Run Demo

```bash
PYTHONPATH=. python examples/demo.py
```

### 3. Use CLI

```bash
python -m src.cli.app --help
```

## CLI Commands

### Metrics Calculation

Calculate all PPC metrics:

```bash
python -m src.cli.app metrics calculate \
    --ad-spend 500 \
    --ad-sales 2000 \
    --total-sales 5000 \
    --impressions 10000 \
    --clicks 100 \
    --orders 10
```

Quick ACoS calculation:

```bash
python -m src.cli.app metrics acos 500 2000
# Output: ACoS: 25.00%
```

Quick TACOS calculation:

```bash
python -m src.cli.app metrics tacos 500 5000
# Output: TACOS: 10.00%
```

### Crisis Management

Check stock situation:

```bash
python -m src.cli.app crisis check-stock 100 5.0
```

Full stock analysis:

```bash
python -m src.cli.app crisis stockout \
    --current-stock 100 \
    --daily-velocity 5.0 \
    --lead-time 30
```

## Python API

### Calculate Metrics

```python
from src.core.metrics.calculator import MetricsCalculator

result = MetricsCalculator.calculate(
    ad_spend=500,
    ad_sales=2000,
    total_sales=5000,
    impressions=10000,
    clicks=100,
    orders=10
)

print(f"ACoS: {result.acos}%")
print(f"TACOS: {result.tacos}%")
print(f"CTR: {result.ctr}%")
print(f"CVR: {result.cvr}%")
```

### Bid Optimization

```python
from src.core.formulas.bid_optimization import RPCBidOptimizer

# Calculate optimal bid using RPC formula
optimal_bid = RPCBidOptimizer.calculate_optimal_bid(
    total_sales=1000,
    total_clicks=200,
    target_acos=0.25
)
print(f"Optimal Bid: ${optimal_bid}")

# Get bid recommendation
recommendation = RPCBidOptimizer.recommend_bid_adjustment(
    current_bid=2.0,
    total_sales=1000,
    total_clicks=200,
    target_acos=0.25,
    current_acos=0.40
)
print(f"Recommended Bid: ${recommendation.recommended_bid}")
print(f"Reason: {recommendation.reason}")
```

### ACoS Decision Tree

```python
from src.decision.acos.manager import ACoSDecisionTree

decision = ACoSDecisionTree.evaluate(
    acos=67.0,
    clicks=25,
    cvr=8.0,
    target_acos=25.0
)

print(f"Action: {decision.action}")
print(f"Reason: {decision.reason}")
print(f"Confidence: {decision.confidence}")
```

### Stock Crisis Protocol

```python
from src.crisis.stockout.protocol import StockoutProtocol

analysis = StockoutProtocol.analyze_stock_situation(
    current_stock=100,
    daily_velocity=5.0,
    lead_time_days=30
)

print(f"Days Remaining: {analysis.days_remaining:.1f}")
print(f"Stock Level: {analysis.stock_level}")

for action in analysis.recommended_actions:
    print(f"[{action.priority}] {action.action}")
```

### Golden Rules Checker

```python
from src.core.constants.golden_rules import GoldenRulesChecker

violations = GoldenRulesChecker.check_all(
    current_stock=50,
    daily_sales_velocity=5.0,
    lead_time_days=30,
    budget_spent_percentage=85.0,
    current_hour=12,
    campaigns_paused=0,
    organic_sales=3000,
    ppc_sales=2000
)

for violation in violations:
    print(f"Rule #{violation.rule_number}: {violation.rule_name}")
    print(f"Severity: {violation.severity}")
    print(f"Action: {violation.recommended_action}")
```

### Benchmark Evaluation

```python
from src.core.benchmarks.standards import BenchmarkEvaluator

evaluation = BenchmarkEvaluator.evaluate_all(
    ctr_ppc=0.65,
    cvr=12.0,
    acos=28.0,
    tacos=10.0,
    organic_sales=3000,
    ppc_sales=2000
)

print(evaluation)
```

## Testing

Run all tests:

```bash
pytest
```

Run specific test file:

```bash
pytest tests/core/test_metrics.py
```

Run with coverage:

```bash
pytest --cov=src --cov-report=html
```

## Development

### Format Code

```bash
make fmt
```

### Lint Code

```bash
make lint
```

### Run All Checks

```bash
make test
```

## Key Formulas

### ACoS (Advertising Cost of Sale)
```
ACoS = (Ad Spend / Ad Sales) × 100
```

### TACOS (Total Advertising Cost of Sale)
```
TACOS = (Total Ad Spend / Total Sales) × 100
```

### RPC (Revenue Per Click)
```
RPC = Total Sales / Total Clicks
```

### Optimal Bid
```
Optimal Bid = RPC × Target ACoS
```

### Reorder Point
```
Reorder Point = (Daily Velocity × Lead Time) + Safety Stock
```

## Benchmarks

### CTR (Click-Through Rate)
- **Poor**: < 0.3% (PPC)
- **Average**: 0.3-0.5%
- **Good**: 0.5-0.75%
- **Excellent**: > 1.0%

### CVR (Conversion Rate)
- **Poor**: < 5%
- **Average**: 5-10%
- **Good**: 10-15%
- **Excellent**: > 20%

### ACoS
- **Excellent**: < 15%
- **Good**: 15-20%
- **Average**: 20-35%
- **Poor**: > 50%

### TACOS
- **Conservative**: 5-8%
- **Standard**: 8-12% (Healthy)
- **Aggressive**: 12-20%

### Organic:PPC Ratio
- **Excellent**: 3:1 or better
- **Healthy**: 2:1
- **Normal**: 1:1
- **Aggressive**: 1:2

## Golden Rules

1. **NEVER RUN OUT OF STOCK** - Maintain 4+ weeks buffer
2. **NEVER EXHAUST BUDGET EARLY** - Pace throughout day
3. **ALWAYS RUN ADS** - Never pause temporarily
4. **RESPECT THE DATA** - Need 20+ clicks for decisions
5. **SEO AND PPC WORK TOGETHER** - Integrated system

## Support

For issues and questions:
- Check the [README.md](README.md)
- Review the [Amazon PPC & SEO Bible v3.0](docs/bible.md)
- Open an issue on GitHub

---

**Based on Amazon PPC & SEO Bible v3.0 - Rating: 9.5/10**
