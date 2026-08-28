import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import yfinance as yf
import tkinter as tk
from tkinter import ttk, messagebox
import warnings
from datetime import datetime, timedelta
from Tobin_separ import Tobin_sep
warnings.filterwarnings('ignore')

# ── Default Portfolio: 40% Large / 30% Mid / 30% Small Cap (20 stocks) ─────────────────
LARGE_CAP = ['ADANIPORTS.NS','ASIANPAINT.NS','AXISBANK.NS','BAJFINANCE.NS','BAJAJFINSV.NS','BEL.NS','BHARTIARTL.NS','HCLTECH.NS','HDFCBANK.NS','HINDUNILVR.NS','ICICIBANK.NS','INDIGO.NS','KOTAKBANK.NS','LT.NS','M&M.NS','MARUTI.NS','SBIN.NS','SUNPHARMA.NS','TITAN.NS','TRENT.NS','ULTRACEMCO.NS']
MID_CAP   = ['HAL.NS','FEDERALBNK.NS','CHOLAFIN.NS','PERSISTENT.NS','TATAELXSI.NS','BAJAJ-AUTO.NS','DMART.NS','MAFANG.NS','MON100.NS','MCX.NS','HINDZINC.NS','HEROMOTOCO.NS']
SMALL_CAP = ['BDL.NS','BSE.NS','CDSL.NS','MAZDOCK.NS','BHEL.NS','KAYNES.NS','FORTIS.NS','ASTRAMICRO.NS','LTF.NS','HINDCOPPER.NS','NATIONALUM.NS','TVSMOTOR.NS','EICHERMOT.NS']
DEF_ASSETS = LARGE_CAP + MID_CAP + SMALL_CAP

# ── Indexes ─────────────────────────────────────────────────────────────────────────────
DEF_INDEXES = ['^NSEI', '^BSESN', '^NSEBANK', '^NSEMDCP50', '^NSEAUTO']

def calc_stats(w, cov, E, rfr, days=252):
    w = np.asarray(w); v = w @ np.asarray(cov) @ w
    s = np.sqrt(v); r = w @ np.asarray(E)
    sharpe = (r - rfr) / s if s > 0 else 0
    return {'Var': v, 'Std': s, 'Ann_Std': s*np.sqrt(days), 'Ret': r,
            'Ann_Ret': (1+r)**days - 1, 'Ann_Sharpe': sharpe * np.sqrt(days)}

class PFDashboard:
    def __init__(self, root):
        self.r = root
        self.r.title("Indian PF Optimizer & Efficient Frontier Dashboard")
        self.r.resizable(True, True)
        self.assets  = list(DEF_ASSETS)
        self.indexes = list(DEF_INDEXES)
        self._build_ui()

    def _build_ui(self):
        f0 = tk.Frame(self.r); f0.pack(fill=tk.X, padx=10, pady=(10,0))
        tk.Label(f0, text="Ticker Symbol:", font=("Arial",10)).pack(side=tk.LEFT)
        self.t_ent = tk.Entry(f0, width=14, font=("Arial",10)); self.t_ent.pack(side=tk.LEFT, padx=6)
        self.t_ent.bind("<Return>", lambda e: None)
        tk.Button(f0, text="Add → Asset",  bg="#3498db", fg="white", command=lambda: self._add(self.a_lb, self.assets)).pack(side=tk.LEFT, padx=2)
        tk.Button(f0, text="Add → Index",  bg="#9b59b6", fg="white", command=lambda: self._add(self.i_lb, self.indexes)).pack(side=tk.LEFT, padx=2)

        mid = tk.Frame(self.r); mid.pack(fill=tk.BOTH, padx=10, pady=5)
        af = tk.LabelFrame(mid, text="  Assets (20 stocks: 40% Large | 30% Mid | 30% Small Cap)  ", fg="blue", font=("Arial",9,"bold"))
        af.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,5))
        self.a_lb = tk.Listbox(af, selectmode=tk.EXTENDED, height=8, exportselection=False)
        for a in self.assets: self.a_lb.insert(tk.END, a)
        asb = tk.Scrollbar(af, orient=tk.VERTICAL, command=self.a_lb.yview)
        self.a_lb.config(yscrollcommand=asb.set)
        asb.pack(side=tk.RIGHT, fill=tk.Y); self.a_lb.pack(fill=tk.BOTH, expand=True)
        tk.Button(af, text="Remove Selected Asset(s)", fg="red", command=lambda: self._remove(self.a_lb, self.assets)).pack(pady=2)

        if_ = tk.LabelFrame(mid, text="  Benchmark Indexes  ", fg="purple", font=("Arial",9,"bold"))
        if_.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.i_lb = tk.Listbox(if_, selectmode=tk.EXTENDED, height=8, exportselection=False)
        for i in self.indexes: self.i_lb.insert(tk.END, i)
        isb = tk.Scrollbar(if_, orient=tk.VERTICAL, command=self.i_lb.yview)
        self.i_lb.config(yscrollcommand=isb.set)
        isb.pack(side=tk.RIGHT, fill=tk.Y); self.i_lb.pack(fill=tk.BOTH, expand=True)
        tk.Button(if_, text="Remove Selected Index(es)", fg="red", command=lambda: self._remove(self.i_lb, self.indexes)).pack(pady=2)

        f2 = tk.Frame(self.r); f2.pack(fill=tk.X, padx=10, pady=5)
        for lbl, default, attr, w in [("C Points:", "100", "c_ent", 7), ("RFR (Daily):", "0.0001428", "rfr_ent", 12), ("Period (yf):", "3y", "per_ent", 5)]:
            tk.Label(f2, text=lbl, font=("Arial",10)).pack(side=tk.LEFT, padx=(8,2))
            e = tk.Entry(f2, width=w, font=("Arial",10)); e.insert(0, default); e.pack(side=tk.LEFT)
            setattr(self, attr, e)
        tk.Button(f2, text="  Run Analysis  ", bg='#27ae60', fg='white', font=("Arial",10,"bold"), command=self.run).pack(side=tk.LEFT, padx=15)
        tk.Button(f2, text="Clear All", command=self._clr_all).pack(side=tk.LEFT)

        info = ("Calculation Validity: Results based on historical returns (yfinance). Tobin weights assume stationary covariance — recommended to rebalance every 3–6 months. "
                "Large-cap weights are more stable; small-cap weights may drift faster due to volatility.\n"
                "Portfolio Mix: 40% Large Cap | 30% Mid Cap | 30% Small Cap (20 Indian stocks, multi-sector)")
        tk.Label(self.r, text=info, wraplength=860, justify=tk.LEFT, fg="#555", font=("Arial",8,"italic"), bd=1, relief=tk.SUNKEN, bg="#f9f9e0", padx=6, pady=4).pack(fill=tk.X, padx=10, pady=(2,8))

    def _add(self, lb, lst):
        t = self.t_ent.get().strip().upper()
        if t and t not in lst:
            lst.append(t); lb.insert(tk.END, t)
        self.t_ent.delete(0, 'end')

    def _remove(self, lb, lst):
        sel = list(lb.curselection())[::-1]
        if not sel: return messagebox.showinfo("Info", "Select item(s) to remove first.")
        for i in sel: lst.pop(i); lb.delete(i)

    def _clr_all(self):
        self.assets.clear(); self.indexes.clear()
        self.a_lb.delete(0, tk.END); self.i_lb.delete(0, tk.END)

    def run(self):
        if len(self.assets) < 2: return messagebox.showerror("Error", "Need >= 2 assets")
        if len(self.indexes) < 1: return messagebox.showerror("Error", "Need >= 1 index")
        try:
            c_pts = int(self.c_ent.get())
            rfr   = float(self.rfr_ent.get())
            per   = self.per_ent.get().strip()
        except: return messagebox.showerror("Error", "Invalid C points, RFR, or period.")

        dl = tk.Label(self.r, text="Downloading data & computing — please wait...", fg="darkorange", font=("Arial",11,"bold"))
        dl.pack(); self.r.update()

        a_df = yf.download(self.assets,  period=per, interval='1d', auto_adjust=True, progress=False)['Close']
        i_df = yf.download(self.indexes, period=per, interval='1d', auto_adjust=True, progress=False)['Close']
        dl.destroy()

        if a_df.empty or i_df.empty: return messagebox.showerror("Error", "No data returned. Check ticker symbols.")

        valid_assets  = [a for a in self.assets  if a in a_df.columns]
        valid_indexes = [i for i in self.indexes if i in i_df.columns]
        a_df = a_df[valid_assets]; i_df = i_df[valid_indexes]

        if len(valid_assets) < 2 or len(valid_indexes) < 1:
            return messagebox.showerror("Error", f"Not enough valid tickers.\nAssets OK: {valid_assets}\nIndexes OK: {valid_indexes}")

        tobin = Tobin_sep(a_df, 'normal', 'daily', 'returns', i_df, True, True)
        all_results = []

        for idx in valid_indexes:
            tobin.weight_calc(rfr, idx)
            tr_min, tr_max = rfr, max(tobin.E.max() * 4.0, rfr + 0.001)
            tr = (tr_min, tr_max)
            c_vals = tobin.c_calc(target_ret_range=tr)

            c_samp  = np.linspace(float(c_vals.min()), float(c_vals.max()), c_pts)
            mu_samp = np.linspace(tr_min, tr_max, c_pts)

            ef = []
            for cv, mu in zip(c_samp, mu_samp):
                w = tobin.pf_weight(cv)
                s = calc_stats(w, tobin.covariance, tobin.E, rfr, tobin._trading_days)
                row = {'Target(D)': round(mu,6), 'c': round(cv,6), 'Ann_Ret': f"{s['Ann_Ret']*100:.2f}%",
                       'Ann_Std': f"{s['Ann_Std']*100:.2f}%", 'Sharpe':  round(s['Ann_Sharpe'],4)}
                for a in valid_assets: row[a] = round(float(w[a]), 4)
                ef.append(row)

            df = pd.DataFrame(ef)
            gmvp  = df.iloc[df['c'].abs().idxmin()]
            tan   = df.iloc[df['Sharpe'].astype(float).idxmax()]
            all_results.append({'idx': idx, 'df': df, 'gmvp': gmvp, 'tan': tan, 'rfr': rfr, 'td': tobin._trading_days, 'assets': valid_assets})

        self._show_all(all_results)

    def _show_all(self, all_results):
        # 1. Data Tables (One per index)
        for res in all_results:
            idx, df, gmvp, tan = res['idx'], res['df'], res['gmvp'], res['tan']
            top = tk.Toplevel(self.r); top.title(f"EF Data — Index: {idx}"); top.geometry("1150x320")
            tv  = ttk.Treeview(top, columns=list(df.columns), show='headings')
            ys  = ttk.Scrollbar(top, orient='vertical', command=tv.yview); xs  = ttk.Scrollbar(top, orient='horizontal', command=tv.xview)
            tv.configure(yscrollcommand=ys.set, xscrollcommand=xs.set)
            ys.pack(side='right', fill='y'); xs.pack(side='bottom', fill='x'); tv.pack(fill='both', expand=True)
            for c in df.columns: tv.heading(c, text=c); tv.column(c, width=95, anchor='center')
            for i, row in df.iterrows():
                tag = ('tan',) if i == tan.name else ('gm',) if i == gmvp.name else ()
                tv.insert("", "end", values=list(row), tags=tag)
            tv.tag_configure('tan', background='#98FB98'); tv.tag_configure('gm', background='#ADD8E6')
            tk.Label(top, text="[ Light Blue = GMVP (Min Risk) ]  [ Light Green = Tangency (Max Sharpe) ]", font=("Arial",9,"italic"), fg="#555").pack()

        # 2. EF Graphs (Grouped by 4, max 2x2 grid per window)
        for i in range(0, len(all_results), 4):
            chunk = all_results[i:i+4]
            n = len(chunk)
            rows = 2 if n > 2 else (1 if n > 0 else 0)
            cols = 2 if n > 1 else 1
            if rows == 0: continue

            fig_ef, axes_ef = plt.subplots(rows, cols, figsize=(14, 5*rows), squeeze=False)
            fig_ef.canvas.manager.set_window_title(f"Efficient Frontiers (Indexes {i+1} to {i+n})")
            ax_ef_flat = axes_ef.flatten()

            for j, res in enumerate(chunk):
                idx, df, gmvp, tan = res['idx'], res['df'], res['gmvp'], res['tan']
                rfr, td = res['rfr'], res['td']

                ax1 = ax_ef_flat[j]
                stds = df['Ann_Std'].str.rstrip('%').astype(float) / 100
                rets = df['Ann_Ret'].str.rstrip('%').astype(float) / 100
                ax1.plot(stds, rets, color='#2c3e50', lw=2, label='Efficient Frontier')

                g_s = float(gmvp['Ann_Std'].rstrip('%')) / 100; g_r = float(gmvp['Ann_Ret'].rstrip('%')) / 100
                t_s = float(tan['Ann_Std'].rstrip('%'))  / 100; t_r = float(tan['Ann_Ret'].rstrip('%'))  / 100
                ax1.scatter(g_s, g_r, c='#3498db', s=160, zorder=5, edgecolors='k', label='GMVP')
                ax1.scatter(t_s, t_r, c='#2ecc71', s=160, zorder=5, edgecolors='k', label='Tangency')

                ra = (1+rfr)**td - 1
                xcml = np.linspace(0, max(stds)*1.1, 200)
                ax1.plot(xcml, ra + float(tan['Sharpe'])*xcml, 'r--', lw=1.5, label='CML')
                ax1.scatter(0, ra, c='r', s=80, zorder=5)
                
                # Cap X-axis at 100% risk if it exceeds it
                if ax1.get_xlim()[1] > 1.0:
                    ax1.set_xlim(right=1.0)
                    
                ax1.set(xlabel='Annualized Std Dev (Risk)', ylabel='Annualized Expected Return', title=f'Efficient Frontier ({idx})')
                ax1.xaxis.set_major_formatter(PercentFormatter(1.0))
                ax1.yaxis.set_major_formatter(PercentFormatter(1.0))
                ax1.legend(fontsize=8); ax1.grid(True, alpha=0.3)

            for j in range(n, len(ax_ef_flat)): ax_ef_flat[j].axis('off')
            fig_ef.tight_layout()

        # 3. Weights Graphs (Grouped by 2, max 2x1 grid per window)
        for i in range(0, len(all_results), 2):
            chunk = all_results[i:i+2]
            n = len(chunk)
            rows = n
            cols = 1
            if rows == 0: continue

            fig_w, axes_w = plt.subplots(rows, cols, figsize=(14, 5*rows), squeeze=False)
            fig_w.canvas.manager.set_window_title(f"Tangency Weights (Indexes {i+1} to {i+n})")
            ax_w_flat = axes_w.flatten()

            for j, res in enumerate(chunk):
                idx, tan, assets = res['idx'], res['tan'], res['assets']

                ax2 = ax_w_flat[j]
                w_vals = [float(tan[a]) for a in assets]
                colors = ['#2ecc71' if v >= 0 else '#e74c3c' for v in w_vals]
                bars = ax2.bar(range(len(assets)), w_vals, color=colors, edgecolor='k', width=0.6)
                
                ax2.set_xticks([]); ax2.axhline(0, color='k', lw=0.8)
                ax2.set(title=f'Tangency Portfolio Weights ({idx})', ylabel='Weight Allocation')
                ax2.yaxis.set_major_formatter(PercentFormatter(1.0))
                ax2.grid(True, axis='y', alpha=0.3)
                
                for bar, name, val in zip(bars, assets, w_vals):
                    ypos = bar.get_height() + (0.025 if val >= 0 else -0.025)
                    va = 'bottom' if val >= 0 else 'top'
                    ax2.text(bar.get_x() + bar.get_width()/2, ypos, name, ha='center', va=va, rotation=90, fontsize=8, fontweight='bold')

            for j in range(n, len(ax_w_flat)): ax_w_flat[j].axis('off')
            fig_w.tight_layout()

        plt.show(block=False)

if __name__ == "__main__":
    root = tk.Tk(); PFDashboard(root); root.mainloop()