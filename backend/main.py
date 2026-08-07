import os
import sys

# Ensure root directory is in sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

from optimizer.portfolio_optimizer import UnifiedPortfolioEngine
from copilot.explanation_engine import PortfolioCoPilot

app = FastAPI(
    title="Quantum Multi-Asset Portfolio Optimizer",
    description="Vanguard Challenge - Classical CVXPY vs Quantum Qiskit QUBO Portfolio Engine & Co-Pilot",
    version="1.0.0"
)

# CORS middleware for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engine & co-pilot
engine = UnifiedPortfolioEngine()
copilot = PortfolioCoPilot(engine.asset_df)

class OptimizationRequest(BaseModel):
    investment_amount: float = Field(default=1000000.0, ge=1000.0, description="Total portfolio capital in INR/USD")
    risk_aversion: float = Field(default=0.5, ge=0.0, le=1.0, description="Risk penalty weight (0=Low, 1=High)")
    max_weight: float = Field(default=0.40, ge=0.10, le=1.0, description="Maximum allocation per asset")
    tech_cap: float = Field(default=0.55, ge=0.20, le=1.0, description="Maximum allocation to Tech sector")

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "engine": "active",
        "assets_count": len(engine.asset_df)
    }

@app.get("/api/assets")
def get_assets():
    return engine.asset_df.to_dict(orient="records")

@app.post("/api/optimize")
def optimize_portfolio(req: OptimizationRequest):
    try:
        results = engine.run_optimization(
            investment_amount=req.investment_amount,
            risk_aversion=req.risk_aversion,
            max_weight=req.max_weight,
            tech_cap=req.tech_cap
        )
        
        explanations = copilot.generate_portfolio_explanation(results)
        results["copilot_explanation"] = explanations
        
        # Save benchmark chart updates
        engine.save_benchmark_charts(results)
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/explain/{ticker}")
def explain_single_asset(ticker: str, weight: float = 0.15):
    explanation = copilot.explain_asset(ticker.upper(), weight)
    return {"ticker": ticker.upper(), "explanation": explanation}

# Mount static frontend directory if it exists
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
def serve_dashboard():
    index_file = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Quantum Portfolio Optimizer API is active. Access /api/assets or /api/optimize."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
