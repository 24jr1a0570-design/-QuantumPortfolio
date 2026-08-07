import os
import sys
import numpy as np
import pandas as pd
import cvxpy as cp
import time

# Ensure root directory is in sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

class ClassicalPortfolioOptimizer:
    def __init__(self, asset_df, cov_matrix):
        """
        asset_df: DataFrame containing ticker, return, risk, sector, liquidity
        cov_matrix: 2D numpy array or DataFrame of covariance matrix
        """
        self.asset_df = asset_df.copy()
        self.cov_matrix = np.array(cov_matrix)
        self.n_assets = len(asset_df)
        self.tickers = asset_df['ticker'].tolist()
        self.returns = asset_df['return'].values
        self.sectors = asset_df['sector'].values
        self.liquidity = asset_df['liquidity'].values

    def optimize(self, risk_aversion=0.5, max_weight=0.40, tech_sector_cap=0.55, min_liquidity=0.85):
        """
        Solves continuous mean-variance portfolio optimization using CVXPY.
        risk_aversion: gamma penalty factor (0.0 to 1.0 mapped to CVXPY risk penalty)
        """
        start_time = time.time()
        
        # Decision variable: Portfolio weights vector
        w = cp.Variable(self.n_assets)
        
        # Scale gamma: 0.1 (low risk penalty) to 10.0 (high risk penalty)
        # risk_aversion parameter in UI (0 to 1) -> gamma = 0.5 + 8.0 * risk_aversion
        gamma = 0.5 + 8.0 * float(risk_aversion)
        
        # Objective: Maximize Return - Gamma * Portfolio Variance
        expected_return = w @ self.returns
        portfolio_variance = cp.quad_form(w, self.cov_matrix)
        objective = cp.Maximize(expected_return - gamma * portfolio_variance)
        
        # Constraints
        constraints = [
            cp.sum(w) == 1.0,           # Weights sum to 100%
            w >= 0.0,                   # No short selling
            w <= max_weight             # Max allocation limit per asset
        ]
        
        # Sector limits (e.g. Technology sector cap)
        tech_indices = [i for i, sec in enumerate(self.sectors) if sec == "Technology"]
        if tech_indices:
            constraints.append(cp.sum(w[tech_indices]) <= tech_sector_cap)
            
        # Liquidity constraint
        constraints.append(w @ self.liquidity >= min_liquidity)
        
        # Solve Problem
        problem = cp.Problem(objective, constraints)
        try:
            problem.solve(solver=cp.ECOS)
        except Exception:
            problem.solve(solver=cp.SCS)
            
        runtime = time.time() - start_time
        
        if w.value is None:
            # Fallback to equal weight if solver fails
            weights = np.ones(self.n_assets) / self.n_assets
        else:
            weights = np.clip(w.value, 0.0, 1.0)
            weights /= np.sum(weights)  # Normalize
            
        # Calculate summary metrics
        ret = float(weights @ self.returns)
        var = float(weights @ self.cov_matrix @ weights)
        std_dev = float(np.sqrt(max(var, 1e-8)))
        sharpe = float((ret - 0.04) / std_dev) if std_dev > 0 else 0.0
        avg_liquidity = float(weights @ self.liquidity)
        
        # Turnover baseline comparison (vs equal weight)
        equal_w = np.ones(self.n_assets) / self.n_assets
        turnover = float(np.sum(np.abs(weights - equal_w)) / 2.0)
        
        # Check constraint breaches
        breaches = 0
        if np.abs(np.sum(weights) - 1.0) > 1e-4:
            breaches += 1
        if np.any(weights > max_weight + 1e-4):
            breaches += 1
        if tech_indices and np.sum(weights[tech_indices]) > tech_sector_cap + 1e-4:
            breaches += 1
            
        allocation = {self.tickers[i]: round(float(weights[i]), 4) for i in range(self.n_assets)}
        
        return {
            "method": "Classical (CVXPY)",
            "allocation": allocation,
            "weights": weights.tolist(),
            "expected_return": round(ret, 4),
            "portfolio_risk": round(std_dev, 4),
            "sharpe_ratio": round(sharpe, 4),
            "liquidity_score": round(avg_liquidity, 4),
            "turnover": round(turnover, 4),
            "constraint_breaches": breaches,
            "runtime_sec": round(runtime, 5)
        }

if __name__ == "__main__":
    from data.generate_data import get_asset_universe, generate_covariance_matrix
    assets = get_asset_universe()
    cov, _ = generate_covariance_matrix(assets)
    df = pd.DataFrame(assets)
    
    opt = ClassicalPortfolioOptimizer(df, cov)
    res = opt.optimize()
    print("Classical Optimization Result:")
    print(res)
