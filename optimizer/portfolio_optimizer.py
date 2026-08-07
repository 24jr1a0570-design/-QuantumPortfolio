import os
import sys
import json
import pandas as pd
import numpy as np

import matplotlib
matplotlib.use('Agg')  # Non-interactive headless backend for web server safety
import matplotlib.pyplot as plt

# Ensure root directory is in sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from data.generate_data import save_synthetic_data
from optimizer.classical_optimizer import ClassicalPortfolioOptimizer
from optimizer.quantum_optimizer import QuantumPortfolioOptimizer

class UnifiedPortfolioEngine:
    def __init__(self, data_dir=None):
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
            
        csv_path = os.path.join(data_dir, "synthetic_portfolio_data.csv")
        cov_path = os.path.join(data_dir, "covariance_matrix.csv")
        
        if not os.path.exists(csv_path) or not os.path.exists(cov_path):
            self.asset_df, self.cov_df = save_synthetic_data(data_dir)
        else:
            self.asset_df = pd.read_csv(csv_path)
            self.cov_df = pd.read_csv(cov_path, index_col=0)
            
        self.classical_solver = ClassicalPortfolioOptimizer(self.asset_df, self.cov_df)
        self.quantum_solver = QuantumPortfolioOptimizer(self.asset_df, self.cov_df)

    def run_optimization(self, investment_amount=1000000, risk_aversion=0.5, max_weight=0.40, tech_cap=0.55):
        """
        Runs both Classical CVXPY and Quantum Qiskit QUBO optimizers.
        Returns combined results dictionary.
        """
        classical_res = self.classical_solver.optimize(
            risk_aversion=risk_aversion, 
            max_weight=max_weight, 
            tech_sector_cap=tech_cap
        )
        
        quantum_res = self.quantum_solver.optimize(
            risk_aversion=risk_aversion, 
            max_weight=max_weight, 
            tech_sector_cap=tech_cap
        )
        
        # Dollar amounts
        classical_dollars = {t: round(classical_res["allocation"][t] * investment_amount, 2) for t in classical_res["allocation"]}
        quantum_dollars = {t: round(quantum_res["allocation"][t] * investment_amount, 2) for t in quantum_res["allocation"]}
        
        comparison = {
            "investment_amount": investment_amount,
            "params": {
                "risk_aversion": risk_aversion,
                "max_asset_weight": max_weight,
                "tech_sector_cap": tech_cap
            },
            "classical": classical_res,
            "quantum": quantum_res,
            "dollar_allocations": {
                "classical": classical_dollars,
                "quantum": quantum_dollars
            },
            "benchmarks": [
                {
                    "metric": "Expected Return",
                    "classical": f"{classical_res['expected_return']*100:.1f}%",
                    "quantum": f"{quantum_res['expected_return']*100:.1f}%"
                },
                {
                    "metric": "Portfolio Risk",
                    "classical": f"{classical_res['portfolio_risk']*100:.1f}%",
                    "quantum": f"{quantum_res['portfolio_risk']*100:.1f}%"
                },
                {
                    "metric": "Sharpe Ratio",
                    "classical": f"{classical_res['sharpe_ratio']:.2f}",
                    "quantum": f"{quantum_res['sharpe_ratio']:.2f}"
                },
                {
                    "metric": "Turnover",
                    "classical": f"{classical_res['turnover']*100:.1f}%",
                    "quantum": f"{quantum_res['turnover']*100:.1f}%"
                },
                {
                    "metric": "Constraint Breaches",
                    "classical": str(classical_res['constraint_breaches']),
                    "quantum": str(quantum_res['constraint_breaches'])
                },
                {
                    "metric": "Runtime (sec)",
                    "classical": f"{classical_res['runtime_sec']:.3f} s",
                    "quantum": f"{quantum_res['runtime_sec']:.3f} s"
                }
            ]
        }
        
        return comparison

    def save_benchmark_charts(self, results, output_dir=None):
        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results")
        os.makedirs(output_dir, exist_ok=True)
        
        # Save JSON
        json_path = os.path.join(output_dir, "benchmark_results.json")
        with open(json_path, "w") as f:
            json.dump(results, f, indent=2)
            
        # Plot Allocation Comparison Bar Chart
        tickers = list(results["classical"]["allocation"].keys())
        class_alloc = [results["classical"]["allocation"][t]*100 for t in tickers]
        quant_alloc = [results["quantum"]["allocation"][t]*100 for t in tickers]
        
        x = np.arange(len(tickers))
        width = 0.35
        
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(10, 5))
        
        rects1 = ax.bar(x - width/2, class_alloc, width, label='Classical (CVXPY)', color='#00F0FF')
        rects2 = ax.bar(x + width/2, quant_alloc, width, label='Quantum (QAOA/QUBO)', color='#7000FF')
        
        ax.set_ylabel('Allocation (%)', fontsize=12)
        ax.set_title('Portfolio Allocation: Classical vs Quantum/Hybrid', fontsize=14, fontweight='bold', pad=15)
        ax.set_xticks(x)
        ax.set_xticklabels(tickers, rotation=30)
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        chart_path = os.path.join(output_dir, "portfolio_allocation_chart.png")
        plt.savefig(chart_path, dpi=200)
        plt.close()
        
        print(f"Benchmark chart saved to {chart_path}")

if __name__ == "__main__":
    engine = UnifiedPortfolioEngine()
    res = engine.run_optimization()
    engine.save_benchmark_charts(res)
    print("Optimization and Benchmarking completed!")
