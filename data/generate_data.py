import os
import numpy as np
import pandas as pd

def get_asset_universe():
    """
    Returns asset metadata for the multi-asset portfolio.
    """
    assets = [
        {"ticker": "AAPL", "name": "Apple Inc.", "return": 0.145, "risk": 0.210, "sector": "Technology", "liquidity": 0.95},
        {"ticker": "MSFT", "name": "Microsoft Corp.", "return": 0.152, "risk": 0.227, "sector": "Technology", "liquidity": 0.95},
        {"ticker": "GOOGL", "name": "Alphabet Inc.", "return": 0.138, "risk": 0.195, "sector": "Technology", "liquidity": 0.90},
        {"ticker": "AMZN", "name": "Amazon.com Inc.", "return": 0.148, "risk": 0.240, "sector": "Technology", "liquidity": 0.90},
        {"ticker": "TSLA", "name": "Tesla Inc.", "return": 0.185, "risk": 0.350, "sector": "Technology", "liquidity": 0.85},
        {"ticker": "GLD", "name": "Gold ETF", "return": 0.078, "risk": 0.112, "sector": "Commodity", "liquidity": 0.95},
        {"ticker": "BND", "name": "Govt Bonds ETF", "return": 0.056, "risk": 0.065, "sector": "Finance", "liquidity": 0.99},
        {"ticker": "XLV", "name": "Healthcare ETF", "return": 0.105, "risk": 0.145, "sector": "Healthcare", "liquidity": 0.88}
    ]
    return assets

def generate_covariance_matrix(assets):
    """
    Generates a realistic positive semi-definite Covariance Matrix based on sector correlations.
    """
    n = len(assets)
    vols = np.array([a["risk"] for a in assets])
    sectors = [a["sector"] for a in assets]
    
    # Base correlation matrix
    corr = np.eye(n)
    for i in range(n):
        for j in range(i + 1, n):
            if sectors[i] == sectors[j]:
                # Intra-sector high correlation
                c = 0.65 if sectors[i] == "Technology" else 0.50
            elif (sectors[i] == "Commodity" or sectors[j] == "Commodity") and (sectors[i] == "Technology" or sectors[j] == "Technology"):
                # Negative/low correlation between Gold and Tech
                c = -0.15
            elif (sectors[i] == "Finance" or sectors[j] == "Finance"):
                # Bonds have low correlation with equities
                c = 0.05
            else:
                c = 0.25
            
            corr[i, j] = c
            corr[j, i] = c

    # Ensure positive semi-definiteness
    # Covariance = D * Corr * D
    D = np.diag(vols)
    cov = D @ corr @ D
    
    # Eigenvalue regularization if needed
    min_eig = np.min(np.linalg.eigvals(cov))
    if min_eig < 0:
        cov += (-min_eig + 1e-6) * np.eye(n)
        
    return cov, corr

def save_synthetic_data(output_dir=None):
    if output_dir is None:
        output_dir = os.path.dirname(__file__)
    
    assets = get_asset_universe()
    cov, corr = generate_covariance_matrix(assets)
    
    df = pd.DataFrame(assets)
    df_path = os.path.join(output_dir, "synthetic_portfolio_data.csv")
    df.to_csv(df_path, index=False)
    
    cov_df = pd.DataFrame(cov, index=[a["ticker"] for a in assets], columns=[a["ticker"] for a in assets])
    cov_path = os.path.join(output_dir, "covariance_matrix.csv")
    cov_df.to_csv(cov_path)
    
    print(f"Data successfully generated and saved to {output_dir}")
    return df, cov_df

if __name__ == "__main__":
    save_synthetic_data()
