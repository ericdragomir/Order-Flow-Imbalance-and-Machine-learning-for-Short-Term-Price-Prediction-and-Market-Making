# Order Flow Imbalance and Machine learning for Short-Term Price Prediction and Market Making

> **A quantitative research project investigating whether limit order book dynamics contain predictive information about short-term price movements and how those signals can be incorporated into an inventory-aware market making strategy.**

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-orange.svg)
![scikit-learn](https://img.shields.io/badge/scikit--learn-ML-orange.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## Overview

*Note: The data was not included due to GitHub space limitations*

This repository presents an end-to-end quantitative research pipeline built around high-frequency cryptocurrency market data obtained from the Binance public API.

The project investigates whether **Order Flow Imbalance (OFI)** and other limit order book features possess predictive power over short-term price movements and whether those signals can be exploited within an inventory-aware market making framework based on the Avellaneda–Stoikov model.

Rather than optimizing for maximum backtest performance, the primary objective is to demonstrate a rigorous quantitative research workflow including:

- reproducible data collection
- statistically motivated feature engineering
- robust out-of-sample validation
- transparent discussion of assumptions and limitations

The repository is intended as a portfolio project for quantitative research, algorithmic trading, and systematic trading roles.

---

## Research Objectives

The project is organized around three research questions:

1. Can information contained in the limit order book predict future mid-price movements?

2. Does Order Flow Imbalance provide statistically significant predictive information beyond simple price-based features?

3. Can these predictions improve the reservation price of an inventory-constrained market maker?

---

## Methodology

The complete workflow consists of four stages.

```text
               Binance API
          (REST + WebSockets)
                    │
                    ▼
       Limit Order Book Reconstruction
                    │
                    ▼
      Feature Engineering (OFI, Depth,
       Queue Imbalance, Volatility...)
                    │
                    ▼
      Machine Learning Classification
                    │
                    ▼
      Walk-Forward Validation
                    │
                    ▼
     Avellaneda–Stoikov Market Maker
                    │
                    ▼
         Backtesting & Evaluation
```

---

# Repository Structure

```text
│
├── models/
│
├── data/raw
│
├── src/
│   ├── data_ingestion/
│   └── notebooks/
│
├── research_note.pdf
│
├── requirements.txt
│
└── README.md
```

---

# Data

Market data are obtained directly from the **Binance Public API**, requiring no authentication or proprietary datasets.

### Data Sources

- REST Order Book Snapshot
- WebSocket Depth Stream
- WebSocket Trade Stream

The local limit order book is reconstructed by synchronizing REST snapshots with incremental WebSocket updates.

Only publicly available market data are used throughout the project.

---

# Exploratory Analysis

Before any predictive modelling, several stylized facts of market microstructure are investigated:

- Bid-ask spread distribution
- Market depth
- Return autocorrelation
- Intraday activity patterns
- Trade size distribution
- Realized volatility

Different sampling schemes are also compared:

- Physical time
- Event time
- Volume time

This step provides the statistical foundation for subsequent modelling decisions.

---

# Feature Engineering

The primary explanatory variable is **Order Flow Imbalance (OFI)** following:

> Cont, Kukanov & Stoikov (2014)

Additional engineered features include:

- Multi-level OFI
- Queue imbalance
- Bid/Ask depth
- Rolling returns
- Realized volatility
- Trade imbalance
- Signed trade counts
- Recent execution intensity

The prediction target is defined as the future direction of the mid-price over a fixed event horizon.

---

# Machine Learning

The project formulates the problem as a supervised binary classification task.

Current models include:

- Logistic Regression (baseline)
- LightGBM

Potential extensions include:

- Gradient Boosting
- XGBoost
- Deep learning

---

# Validation

Traditional random train-test splits are inappropriate for financial time series because they introduce look-ahead bias.

Instead, the project employs:

- Walk-forward validation
- Expanding training windows
- Strict chronological evaluation

This validation procedure preserves temporal causality and more accurately reflects real trading conditions.

---

# Market Making Strategy

The predictive signal is integrated into the classical **Avellaneda–Stoikov** inventory management framework.

The reservation price is dynamically adjusted according to:

- inventory level
- estimated volatility
- market risk
- predictive probability from the classifier

This allows the market maker to skew quotes according to expected short-term price pressure while controlling inventory risk.

---

# Performance Evaluation

Model evaluation focuses on statistical significance rather than raw profitability.

Performance metrics include:

| Model | Metrics |
|--------|----------|
| Signal | Directional Accuracy |
| Signal | Log Loss |
| Signal | Precision / Recall |
| Strategy | Sharpe Ratio |
| Strategy | Inventory P&L |
| Strategy | Spread Capture |
| Strategy | Maximum Drawdown |

All reported metrics are computed strictly out-of-sample.

---

# Results

The objective of this repository is **research**, not performance marketing.

A successful outcome is defined by demonstrating a complete research pipeline rather than achieving unusually high backtest returns.

The project emphasizes:

- reproducibility
- methodological rigor
- transparent reporting
- honest discussion of limitations

---

# Limitations

Several simplifying assumptions should be acknowledged.

- Queue position is approximated.
- Exchange latency is ignored.
- Transaction costs are simplified.
- Market impact is not modelled.
- Order execution assumes immediate fills once prices cross.
- Binance data do not expose the full exchange matching engine.

Consequently, results should not be interpreted as deployable trading performance.

---

# Reproducibility

Clone the repository

```bash
git clone https://github.com/<username>/order-flow-imbalance.git
cd order-flow-imbalance
```

Install dependencies

```bash
pip install -r requirements.txt
```

Launch Jupyter

```bash
jupyter notebook
```

Execute the notebooks in the following order:

1. `analysis_signal.ipynb`
2. `strategy.ipynb`

---

# Future Work

Several extensions naturally arise from this work.

- Queue-reactive market making
- Hawkes process order arrivals
- Lead-lag relationships between correlated assets
- Cross-exchange arbitrage
- Reinforcement Learning for optimal quoting
- More realistic execution simulator
- Transaction cost calibration
- Inventory-aware reinforcement learning
- Testing on more assets

---

# References

Avellaneda, M., & Stoikov, S. (2008). *High-Frequency Trading in a Limit Order Book*. Quantitative Finance.

Cont, R., Kukanov, A., & Stoikov, S. (2014). *The Price Impact of Order Book Events*. Journal of Financial Econometrics.

Cartea, Á., Jaimungal, S., & Penalva, J. (2015). *Algorithmic and High-Frequency Trading*. Cambridge University Press.

Gould, M., Porter, M., Williams, S., McDonald, M., Fenn, D., & Howison, S. (2013). *Limit Order Books*. Quantitative Finance.

Lopez de Prado, M. (2018). *Advances in Financial Machine Learning*. Wiley.

---

# Disclaimer

This repository is intended exclusively for educational and research purposes.

Nothing contained herein constitutes financial advice, investment advice, or a recommendation to trade any financial instrument.

---

## Author

**Quantitative Research Project**

**Topics:** Market Microstructure • Statistical Learning • Algorithmic Trading • High-Frequency Trading

---

### Acknowledgements

This project was developed as an independent study of modern market microstructure and systematic trading methodologies using exclusively open-source tools and publicly available market data.