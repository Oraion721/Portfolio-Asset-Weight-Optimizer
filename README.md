# Quantitative Portfolio Optimizer & Efficient Frontier Dashboard

A Python-based financial engineering tool that applies **Markowitz Mean-Variance Optimization** and **Tobin's Separation Theorem** to construct optimal portfolios. This project dynamically fetches live market data, calculates risk/return metrics across multiple benchmark indices, and visualizes the Efficient Frontier.

## 🚀 Features
* **Live Data Integration:** Automatically fetches historical daily closing prices using `yfinance`.
* **Tobin's Separation Theorem:** Computes the Tangency Portfolio (Maximum Sharpe Ratio) and Global Minimum Variance Portfolio (GMVP) by mixing a risk-free asset with a risky portfolio.
* **Multi-Index Benchmarking:** Dynamically evaluates the portfolio against multiple market indices (e.g., Nifty 50, Sensex) simultaneously.
* **Interactive GUI Dashboard:** Built with `tkinter` and `matplotlib` to provide a user-friendly interface for inputting tickers, setting risk-free rates, and viewing comprehensive data tables.
* **Advanced Visualizations:** Generates the Efficient Frontier curve, Capital Market Line (CML), and weight distribution bar charts.

## 📊 Visualizations

<img width="1102" height="444" alt="Screenshot 2026-08-28 134103" src="https://github.com/user-attachments/assets/8e6bd743-1691-4995-a682-f42ea9ba17bd" />
<img width="1920" height="1030" alt="Screenshot 2026-08-28 134659" src="https://github.com/user-attachments/assets/5167e98a-c0f3-4cf8-92c5-a1716aba05ed" />
<img width="1536" height="759" alt="Efficient_Frontiers_(Indexes_1_to_4)" src="https://github.com/user-attachments/assets/1626808c-2051-4bf6-a254-694925d56f17" />
<img width="1536" height="759" alt="Tangency_Weights_(Indexes_1_to_2)" src="https://github.com/user-attachments/assets/e42c72cc-671c-4813-a826-c24c81cdc882" />


## 🧠 Architecture & Methodology

This project is structured using Object-Oriented Programming (OOP) principles to separate the mathematical engine from the user interface:

1. `calculations.py`: The core data processor. Handles data fetching, cleaning, and calculating covariance matrices and daily expected returns using the Capital Asset Pricing Model (CAPM).
2. `Tobin_separ.py`: The quantitative engine. Executes matrix algebra (`w.T @ Cov @ w`) to calculate the baseline weights, scalar mixing values (c), and final asset allocations.
3. `PF_stats_and_EF.py`: The front-end view. Uses a `tkinter` TreeView to display tabular statistics and `matplotlib` to render multi-grid subplots of the Efficient Frontier and Tangency Weights.

## 🛠️ Tech Stack
* **Python 3.x**
* **Pandas & NumPy:** For linear algebra, matrix inversion, and financial time-series manipulation.
* **Matplotlib:** For rendering financial plots (Efficient Frontier, CML).
* **yfinance:** For live API data extraction.
* **Tkinter:** For the desktop graphical user interface.

## 💼 Investment Strategy Evaluated
The default configuration tests a 20-stock Indian equity portfolio split across **40% Large Cap, 30% Mid Cap, and 30% Small Cap**. The algorithm calculates the exact capital allocation (weights) required to achieve the Maximum Sharpe Ratio against benchmark indices.
