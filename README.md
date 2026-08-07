# Quantum-Enhanced Multi-Asset Portfolio Optimization ⚛️📊

An end-to-end Quantum Financial Technology prototype built for the **Vanguard Quantum Internship Challenge**. 

This system optimizes a ₹10,00,000 capital allocation across an 8-asset universe (*Apple, Microsoft, Google, Amazon, Tesla, Gold ETF, Govt Bonds, Healthcare ETF*) balancing **Return, Risk, Diversification, Liquidity, and Transaction Costs**.

It formulates and solves the problem using two methods:
1. **Classical Optimization**: Continuous Mean-Variance Quadratic Programming via **CVXPY** (ECOS/SCS solvers).
2. **Quantum / Hybrid Optimization**: Discrete Quadratic Unconstrained Binary Optimization (**QUBO**) mapped to an Ising Hamiltonian and solved via **Qiskit Aer (QAOA / Minimum Eigen Optimizer)**.

The system features empirical side-by-side benchmarking and an interactive **Portfolio Co-Pilot** that provides natural language explanations for portfolio decisions.

---

## 🏛️ Technical Architecture

```
                    USER / HOD
                        │
                        ↓
         Interactive Web Dashboard (HTML/CSS/JS)
                        │
                        ↓
            FastAPI Backend Engine (REST)
                        │
          ┌─────────────┴─────────────┐
          ↓                           ↓
 Classical Optimizer         Quantum Optimizer
      (CVXPY)                  (Qiskit QAOA)
          │                           │
          └─────────────┬─────────────┘
                        ↓
                 Result Analyzer
                        │
          ┌─────────────┴─────────────┐
          ↓                           ↓
 Benchmark Metrics          Portfolio Co-Pilot
 (Return, Risk, Runtime)    (Explainability AI)
```

---

## 📐 Mathematical Formulation

### 1. Classical Formulation (CVXPY)
$$\max_w \quad w^T \mu - \gamma \, w^T \Sigma w$$
$$\text{subject to} \quad \sum_{i=1}^n w_i = 1, \quad 0 \le w_i \le w_{\max}, \quad \sum_{i \in \text{Tech}} w_i \le C_{\text{tech}}, \quad w^T L \ge L_{\min}$$

### 2. Quantum QUBO Formulation (Qiskit)
Discretizing weight decisions $w_i = \sum_b 2^b \, \delta \, x_{i,b}$ into binary decision vector $x \in \{0,1\}^N$:
$$\min_x \quad - \lambda_R (w(x)^T \mu) + \lambda_V (w(x)^T \Sigma w(x)) + P_{\text{sum}} \left( \sum_i w_i(x) - 1 \right)^2 + P_{\text{tech}} \left( \max(0, \text{Tech}(x) - C_{\text{tech}}) \right)^2$$
Formulated as:
$$f(x) = x^T Q x + c^T x \quad \longrightarrow \quad \text{Mapped to Ising Hamiltonian } H = \sum J_{ij} Z_i Z_j + \sum h_i Z_i$$

---

## 📂 Project Folder Structure

```
QuantumPortfolio/
│
├── data/
│   ├── generate_data.py          # Asset universe & correlation covariance generator
│   ├── synthetic_portfolio_data.csv
│   └── covariance_matrix.csv
│
├── optimizer/
│   ├── classical_optimizer.py    # CVXPY Mean-Variance continuous solver
│   ├── quantum_optimizer.py      # Qiskit QUBO / QAOA discrete solver
│   └── portfolio_optimizer.py    # Unified benchmark runner
│
├── copilot/
│   └── explanation_engine.py     # Portfolio Co-Pilot natural language engine
│
├── backend/
│   └── main.py                   # FastAPI REST server & static files host
│
├── frontend/
│   ├── index.html                # Modern glassmorphic dashboard
│   ├── styles.css                # Dark mode styling & animations
│   └── app.js                    # Chart.js dynamic dashboard logic
│
├── notebooks/
│   └── quantum_portfolio_demo.ipynb  # HOD presentation notebook
│
├── results/
│   ├── benchmark_results.json
│   └── portfolio_allocation_chart.png
│
├── README.md
└── requirements.txt
```

---

## 🚀 How to Run the Project

### 1. Activate Environment & Install Dependencies
```bash
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run Data Generation & Benchmark Test
```bash
python data/generate_data.py
python optimizer/portfolio_optimizer.py
```

### 3. Launch the FastAPI Backend & Web App
```bash
python backend/main.py
```
Open your browser and navigate to:
**`http://localhost:8000`**

### 4. HOD Demo / Presentation Notebook
Launch Jupyter Notebook to present step-by-step:
```bash
jupyter notebook notebooks/quantum_portfolio_demo.ipynb
```

---

## 📊 Classical vs Quantum Benchmark Results

| Metric | Classical (CVXPY) | Quantum/Hybrid (Qiskit QUBO) |
|---|---|---|
| **Expected Return** | 10.8% | 10.5% |
| **Portfolio Risk (Std Dev)** | 7.2% | 7.5% |
| **Sharpe Ratio** | 0.94 | 0.87 |
| **Turnover** | 12.0% | 10.0% |
| **Constraint Breaches** | 0 | 0 |
| **Runtime** | 0.018 s | 0.420 s |

---

## 🤖 Portfolio Co-Pilot Feature
The Co-Pilot addresses explainability by providing targeted rationale for allocations:
* **Why Gold ETF?**: *"Gold ETF (20.0%) was included because it has negative correlation (-0.15) with tech stocks, stabilizing total portfolio risk."*
* **Why Capped Tesla?**: *"Tesla was restricted due to higher annualized volatility (35.0%) under risk penalization."*
