# 📈 Quantitative Portfolio Optimizer & Efficient Frontier Dashboard

A Python-based financial engineering tool implementing **Markowitz Mean-Variance Analysis (MVA)** and **Tobin's Two-Fund Separation Theorem** to construct optimal investment portfolios. The project fetches live market data, computes CAPM-based expected returns across multiple benchmark indices, and renders an interactive GUI dashboard with the Efficient Frontier, Capital Market Line (CML), and weight distribution charts.

---

## 📊 Visualizations
<img width="1102" height="444" alt="Screenshot 2026-08-28 134103" src="https://github.com/user-attachments/assets/2cd8250f-4997-42c3-a209-da8f754dc373" />
<img width="1920" height="1030" alt="Screenshot 2026-08-28 134659" src="https://github.com/user-attachments/assets/c1cbc7d2-4b99-4107-8063-eb2bbe125681" />
<img width="1536" height="759" alt="Efficient_Frontiers_(Indexes_1_to_4)" src="https://github.com/user-attachments/assets/1bd2226b-0667-401f-8c68-08d6beea3157" />
<img width="1536" height="759" alt="Tangency_Weights_(Indexes_1_to_2)" src="https://github.com/user-attachments/assets/563c7f93-b39c-44f2-8046-c7f57a8bffb8" />

---

## 🚀 Features

- **Live Market Data:** Fetches historical OHLCV data via `yfinance` for any global ticker.
- **Multi-Index Benchmarking:** Runs Tobin Separation for each benchmark index sequentially (Nifty 50, Sensex, Bank Nifty, Midcap 50, Nifty Auto).
- **Interactive GUI Dashboard:** Built with `tkinter` — add/remove tickers dynamically, set RFR and C-points, view live results.
- **Efficient Frontier & CML:** Parametric EF construction using two-fund separation; Capital Market Line drawn from RFR through Tangency Portfolio.
- **Grouped Plots:** Efficient Frontiers displayed in 2×2 grids; weight distributions in 2×1 stacked panels for readability with large asset sets.
- **20-Stock Indian Portfolio:** Pre-configured with 40% Large Cap, 30% Mid Cap, 30% Small Cap across sectors.

---

## ⚙️ How to Run

1. Clone or download this repository.
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Navigate to the `PF MVA` folder:
   ```
   cd "PF MVA"
   ```
4. Launch the dashboard:
   ```
   python PF_stats_and_EF.py
   ```

---

## 🏗️ Architecture

The project uses a clean OOP architecture separating mathematical engine from the UI:

```
Portfolio-Asset-Weight-Optimizer/
├── PF MVA/
│   ├── calculations.py       # Data processing + statistical calculations (EF_calc class)
│   ├── Tobin_separ.py        # Tobin two-fund separation theorem (Tobin_sep class)
│   └── PF_stats_and_EF.py   # GUI Dashboard (Tkinter + Matplotlib)
├── Efficient Frontier in excel/
│   └── PF_stks_indexes.xlsx  # Excel reference implementation for cross-verification
├── requirements.txt
└── README.md
```

| File | Class | Responsibility |
|---|---|---|
| `calculations.py` | `EF_calc` | Transform price data → returns, compute μ, σ², Σ, β (hedge ratio), CAPM E(R) |
| `Tobin_separ.py` | `Tobin_sep(EF_calc)` | Compute GMVP weights (g), speculative weights (h), EF mixing scalar (c), final weights w* |
| `PF_stats_and_EF.py` | `PFDashboard` | Tkinter GUI, Matplotlib visualization, multi-index iteration |

---

## 🧮 Mathematical Framework

> 📖 **Full derivations, proofs, and notes are documented in Notion:**
> - [Mean-Variance Analysis (MVA) — Full Notes](https://app.notion.com/p/Mean-Variance-Analysis-MVA-3cb93de17f3d803988a1f20ff136cdff)
> - [Tobin's Separation Theorem — Full Notes](https://app.notion.com/p/Tobin-s-Separation-Theorem-3cc93de17f3d809caf7feb1e33615846)

### 1. Mean-Variance Analysis (Markowitz, 1952)

**Core Idea:** For a portfolio of *m* assets, any efficient portfolio minimizes variance for a given target return.

**Key Notation:**

| Symbol | Meaning |
|---|---|
| $\mathbf{W} = [w_1, \dots, w_m]^T$ | Asset weight vector |
| $\alpha = \mathbb{E}[R]$ | Expected return vector |
| $\Sigma$ | Covariance matrix of returns |
| $R_p = \mathbf{W}^T R$ | Portfolio return |
| $\sigma_p^2 = \mathbf{W}^T \Sigma \mathbf{W}$ | Portfolio variance |

**Optimization Problem (Risk Minimization):**

$$\min_{\mathbf{W}} \left( \frac{\mathbf{W}^T \Sigma \mathbf{W}}{2} \right) \quad \text{subject to} \quad \mathbf{W}^T \alpha = \alpha_0, \quad \mathbf{W}^T \mathbf{1}_m = 1$$

Solved using a Lagrangian with multipliers $\lambda_1$ (return constraint) and $\lambda_2$ (budget constraint):

$$L(\mathbf{W}, \lambda_1, \lambda_2) = \frac{1}{2} \mathbf{W}^T \Sigma \mathbf{W} + \lambda_1(\alpha_0 - \mathbf{W}^T \alpha) + \lambda_2(1 - \mathbf{W}^T \mathbf{1}_m)$$

**Why simple returns, not log returns?**
Simple returns are additive across assets: $R_p = \sum_i w_i R_i$. Log returns are additive over *time* but not across assets — making them unsuitable for multi-asset portfolio math.

---

### 2. Tobin's Two-Fund Separation Theorem

**Core Idea:** Every efficient portfolio is a linear combination of exactly two funds:
- **Fund g (GMVP):** Global Minimum Variance Portfolio — the safest fully-invested portfolio.
- **Fund h (Speculative):** The direction of increasing expected return in weight space.

$$\boxed{\mathbf{W}^* = g + c \cdot h}$$

where $c$ is a scalar mixing parameter set by the investor's target return.

**Derivation with Risk-Free Asset:**

Portfolio with risk-free asset $r_0$:

$$\mathbb{E}[R_p] = \mathbf{W}^T(\alpha - r_0 \mathbf{1}_m) + r_0$$

Minimizing variance subject to a target return $\alpha_0$:

$$\mathbf{W} = \frac{\alpha_0 - r_0}{(\alpha - r_0 \mathbf{1}_m)^T \Sigma^{-1} (\alpha - r_0 \mathbf{1}_m)} \cdot \Sigma^{-1}(\alpha - r_0 \mathbf{1}_m)$$

**Two-Fund Decomposition (implemented in `Tobin_separ.py`):**

| Vector | Formula | Meaning |
|---|---|---|
| $g$ (baseline) | $\Sigma^{-1}\mathbf{1} \;/\; \mathbf{1}^T\Sigma^{-1}\mathbf{1}$ | GMVP weights — sum to 1, minimize variance |
| $h_1$ | $\Sigma^{-1} \cdot E$ | Sensitivity to expected returns |
| $h_2$ | $\frac{\mathbf{1}^T h_1}{\mathbf{1}^T \Sigma^{-1} \mathbf{1}} \cdot \Sigma^{-1}\mathbf{1}$ | Budget correction term |
| $h = h_1 - h_2$ (speculative) | $h_1 - h_2$ | Always sums to 0 — pure reallocation |
| $c$ (mixing scalar) | $\frac{\mu^* - \mu_G}{h^T \cdot E}$ | Investor's target return encoded as a scalar |

**Final efficient portfolio:** $\mathbf{W}^* = g + c \cdot h$, where:
- $c = 0$ → GMVP (minimum risk)
- $c > 0$ → Higher return, higher risk portfolio
- $c < 0$ → Sub-optimal (below GMVP return)

---

### 3. CAPM Expected Returns (used as input to Tobin)

$$E(R_i) = r_f + \beta_i \cdot (E(R_{market}) - r_f)$$

where $\beta_i = \frac{\text{Cov}(R_i, R_{market})}{\text{Var}(R_{market})}$ (implemented in `calc_hedge_ratio()`)

---

## 💼 Default Portfolio Configuration

| Segment | Weight | Stocks |
|---|---|---|
| **Large Cap** | 40% (8 stocks) | RELIANCE, TCS, HDFCBANK, INFY, ICICIBANK, SBIN, BHARTIARTL, AXISBANK |
| **Mid Cap** | 30% (6 stocks) | HAL, BEL, FEDERALBNK, CHOLAFIN, PERSISTENT, TATAELXSI |
| **Small Cap** | 30% (6 stocks) | BDL, BSE, CDSL, MAZDOCK, BHEL, KAYNES |

**Benchmark Indices:** Nifty 50, Sensex, Bank Nifty, Nifty Midcap 50, Nifty Auto

> **Validity:** Weights are calculated from 3 years of historical data. Recommended rebalancing period: **every 3–6 months**. Large-cap weights are more stable; small-cap weights may drift faster due to higher volatility.

---

## 🛠️ Tech Stack

| Library | Usage |
|---|---|
| `numpy` | Matrix algebra — inverse covariance ($\Sigma^{-1}$), dot products ($\mathbf{W}^T \Sigma \mathbf{W}$) |
| `pandas` | Time-series data handling, covariance matrix (`.cov()`), alignment |
| `yfinance` | Live historical price data from Yahoo Finance API |
| `matplotlib` | Efficient Frontier curves, CML, weight distribution bar charts |
| `tkinter` | Desktop GUI dashboard |
