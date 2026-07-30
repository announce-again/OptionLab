# NCX Derivatives Roadmap

NCX Derivatives is a from-scratch quantitative derivatives research and market-making platform.

The project is designed to progress from mathematically transparent pricing models to a modular research, risk, and electronic market-making system. Each stage should produce a usable, tested component rather than a collection of disconnected notebooks.

---

## Engineering Principles

Development follows several core principles:

- Mathematical correctness before optimisation
- Explicit assumptions and unit conventions
- Stable, documented public APIs
- Analytical results validated against numerical methods
- Numerical methods validated through convergence and invariants
- Input validation and well-defined boundary behaviour
- Reproducible research workflows
- Automated testing for every production-facing component
- Separation between reusable library code and exploratory research
- Incremental commits organised around complete milestones

The standard development cycle is:

```text
Design
→ Implement
→ Test
→ Validate
→ Document
→ Commit
```

---

# Stage 0 — Engineering Foundation

## Objective

Establish a maintainable Python project suitable for long-term quantitative research and software development.

## Deliverables

- `src/`-based Python package structure
- Editable package installation
- `pyproject.toml` configuration
- Automated testing with `pytest`
- Consistent module boundaries
- Git and GitHub integration
- Project documentation
- Ignore rules for generated files and local environments

## Completion Criteria

- Package imports correctly after `pip install -e .`
- Tests run from the repository root
- Generated files are excluded from version control
- Repository naming and package naming are consistent
- Initial documentation accurately describes the project

## Status

**Complete**

---

# Stage 1 — Pricing and Volatility Foundation

## Objective

Build a reliable analytical and numerical foundation for derivatives pricing.

---

## Stage 1.1 — Black–Scholes Pricing

### Scope

Implement European call and put pricing under the no-dividend
Black–Scholes model.

### Capabilities

- European call pricing
- European put pricing
- Negative interest-rate support
- Expiry payoff handling
- Zero-volatility deterministic limits
- Input validation
- Static no-arbitrage bounds

### Validation

- Published benchmark prices
- No-dividend put-call parity
- Price monotonicity
- Volatility monotonicity
- Static-arbitrage bounds
- Boundary and invalid-input tests

### Status

**Complete**

---

## Stage 1.2 — Analytical Greeks

### Scope

Implement first- and second-order sensitivities for European options.

### Capabilities

- Call and put Delta
- Gamma
- Vega
- Call and put Theta
- Call and put Rho
- Black–Scholes analytical formulas
- Explicit unit conventions

### Validation

- Published benchmark values
- Central finite-difference Delta
- Second central-difference Gamma
- Central finite-difference Vega
- Maturity-difference Theta
- Central finite-difference Rho
- Structural Greek relationships

### Status

**Complete**

---

## Stage 1.3 — Implied Volatility Solver

### Scope

Invert Black–Scholes prices to recover implied volatility.

### Capabilities

- Call implied volatility
- Put implied volatility
- Hybrid Newton and bisection solver
- Bracket-preserving Newton steps
- Bisection fallback
- Low-Vega protection
- No-arbitrage price validation
- Lower-bound mapping to zero volatility
- Upper-bound mapping to infinite volatility
- Configurable convergence tolerance and iteration limits

### Validation

- Price-to-volatility round trips
- Deep in-the-money options
- Deep out-of-the-money options
- Near-expiry options
- Negative interest rates
- Boundary prices
- Invalid market prices

### Status

**Complete**

---

## Stage 1.4 — Continuous Dividend Yield

### Scope

Extend the analytical pricing, Greeks, and implied-volatility stack from Black–Scholes to Black–Scholes–Merton with continuous dividend yield \(q\).

### Capabilities

- Discounted spot term \(S e^{-qT}\)
- Cost-of-carry term \(r-q\)
- Dividend-aware pricing
- Dividend-aware Greeks
- Dividend-aware implied-volatility inversion
- Backwards-compatible `dividend_yield=0.0` API

### Validation

- Black–Scholes–Merton put-call parity
- Dividend-aware finite-difference Greeks
- Dividend-aware implied-volatility round trips
- Zero-volatility forward payoff
- Dividend-aware no-arbitrage bounds

### Status

**Complete**

---

## Stage 1.5 — Binomial Tree Pricing

### Scope

Introduce the first general-purpose numerical pricing method using the Cox–Ross–Rubinstein tree.

### Capabilities

- European call and put pricing
- American call and put pricing
- Continuous dividend yield
- Early-exercise detection
- Configurable tree depth
- Memory-efficient backward induction
- Optional exercise-boundary extraction

### Validation

- European tree convergence to Black–Scholes–Merton
- American option value greater than or equal to European value
- Non-dividend-paying American call equivalence
- Intrinsic-value lower bounds
- Early-exercise behaviour for American puts
- Stability across moneyness and maturity
- Convergence behaviour across tree depths

### Completion Criteria

- European prices converge within documented tolerances
- American exercise logic is independently tested
- Complexity and numerical limitations are documented
- Public API remains consistent with the analytical pricing layer

### Status

**Complete**

---

## Stage 1.6 — Monte Carlo Pricing

### Scope

Develop a reusable simulation framework for pricing and sensitivity estimation.

Monte Carlo prices are statistical estimates rather than exact values. The
first public API should return a result object instead of a bare float:

```python
MonteCarloResult(
    price=...,
    standard_error=...,
    confidence_interval=...,
    simulations=...,
)
```

### Status

**Complete**

---

## Stage 1.6a — GBM Terminal Simulation

### Scope

Implement reproducible terminal-price simulation under risk-neutral geometric
Brownian motion.

### Capabilities

- Terminal stock-price simulation
- Continuous dividend yield through drift \(r-q\)
- Reproducible random seeds
- Batch terminal simulation
- Input validation

### Validation

- Simulated terminal mean close to risk-neutral forward
- Simulated log-return variance close to \(\sigma^2 T\)
- Reproducibility tests with fixed seeds
- Stability across moneyness, maturities, rates, and dividend yields

### Status

**Complete**

---

## Stage 1.6b — European Monte Carlo Pricing

### Scope

Price European call and put options from simulated terminal payoffs.

### Capabilities

- European call pricing
- European put pricing
- Discounted payoff estimation
- `MonteCarloResult` return object
- Configurable simulation count
- Batch-ready pricing structure

### Validation

- Convergence to Black–Scholes–Merton prices
- Comparison against binomial tree prices
- Intrinsic-value and non-negativity checks
- Reproducibility tests

### Status

**Complete**

---

## Stage 1.6c — Standard Error and Confidence Intervals

### Scope

Expose uncertainty estimates for Monte Carlo prices.

### Capabilities

- Standard-error estimation
- Configurable confidence level
- Confidence intervals
- Simulation count reporting
- Payoff variance diagnostics

### Validation

- Confidence-interval coverage checks
- Standard error decreases at approximately \(1/\sqrt{N}\)
- Deterministic zero-volatility behaviour
- Invalid confidence-level handling

### Status

**Complete**

---

## Stage 1.6d — Variance Reduction

### Scope

Add variance-reduction methods for European option Monte Carlo pricing.

### Capabilities

- Antithetic variates
- Control variates
- Black–Scholes–Merton control for European options
- Error-reduction diagnostics
- Variance-reduction configuration

### Validation

- Antithetic estimator reduces or maintains variance
- Control variate improves convergence to analytical prices
- Reproducibility with variance-reduction enabled
- Comparison against plain Monte Carlo at equal random draw budgets

### Status

**Complete**

---

## Stage 1.7 — Numerical Greeks

### Scope

Provide model-independent Greek estimation for numerical pricers.

### Planned Capabilities

- Bump-and-revalue Delta
- Gamma
- Vega
- Theta
- Rho
- Adaptive bump sizing
- Forward, backward, and central differences
- Common-random-number Monte Carlo Greeks
- Error diagnostics

### Validation

- Comparison against analytical Black–Scholes–Merton Greeks
- Sensitivity to bump size
- Numerical stability across moneyness and maturity
- Monte Carlo estimator variance analysis

### Status

**Planned**

---

# Stage 2 — Market Data Infrastructure

## Objective

Create a clean and reproducible pipeline for transforming raw option-chain data into research-ready inputs.

---

## Stage 2.1 — Market Data Models

### Planned Capabilities

- Underlying quote representation
- Option contract representation
- Option quote representation
- Expiry and strike organisation
- Bid, ask, midpoint, and spread calculations
- Timestamp and exchange metadata
- Contract validation
- Call-put pairing

### Status

**Planned**

---

## Stage 2.2 — Data Ingestion

### Planned Capabilities

- CSV and Parquet ingestion
- Extensible provider adapters
- Schema normalisation
- Type validation
- Missing-value handling
- Duplicate detection
- Raw-data preservation
- Reproducible processed datasets

### Status

**Planned**

---

## Stage 2.3 — Quote Cleaning

### Planned Capabilities

- Invalid bid-ask detection
- Crossed-market filtering
- Zero-liquidity filtering
- Stale-quote detection
- Minimum-price and minimum-size filters
- Moneyness and maturity filters
- Static-arbitrage diagnostics
- Configurable cleaning rules

### Status

**Planned**

---

## Stage 2.4 — Rates, Dividends, and Forwards

### Planned Capabilities

- Discount-factor representation
- Yield-curve interpolation
- Continuous and discrete dividend handling
- Forward-price estimation
- Put-call-parity implied forwards
- Borrow and carry diagnostics

### Status

**Planned**

---

# Stage 3 — Volatility Research

## Objective

Transform cleaned option prices into consistent implied-volatility structures and research tools.

---

## Stage 3.1 — Implied Volatility Chains

### Planned Capabilities

- Chain-wide implied-volatility calculation
- Bid, ask, and midpoint implied volatility
- Solver diagnostics
- Failed-inversion reporting
- Vega-aware filtering
- Moneyness transformations
- Forward log-moneyness

### Status

**Planned**

---

## Stage 3.2 — Smile and Skew Analysis

### Planned Capabilities

- Volatility smile visualisation
- Strike skew
- Delta-based skew
- Risk reversals
- Butterflies
- Term-structure analysis
- ATM volatility extraction
- Skew slope and curvature metrics

### Status

**Planned**

---

## Stage 3.3 — Volatility Surface Construction

### Planned Capabilities

- Strike-expiry grids
- Interpolation in total variance
- Forward-moneyness coordinates
- Missing-data handling
- Smoothness controls
- Surface diagnostics
- Extrapolation policies

### Validation

- Recovery of observed liquid quotes
- Calendar monotonicity checks
- Butterfly-arbitrage checks
- Stability under sparse data
- Cross-validation across withheld quotes

### Status

**Planned**

---

## Stage 3.4 — Parametric Volatility Models

### Planned Capabilities

- SVI smile parameterisation
- SSVI surface construction
- Calibration objectives
- Weighted calibration using spreads or Vega
- Parameter constraints
- Arbitrage diagnostics
- Calibration error reporting

### Status

**Planned**

---

## Stage 3.5 — Volatility Dynamics

### Planned Research

- Realised versus implied volatility
- Volatility risk premium
- Sticky-strike behaviour
- Sticky-delta behaviour
- Smile dynamics after spot moves
- Term-structure evolution
- Event-volatility decomposition

### Status

**Planned**

---

# Stage 4 — Strategy Research

## Objective

Build a reproducible framework for defining, valuing, and analysing option strategies.

---

## Stage 4.1 — Instruments and Positions

### Planned Capabilities

- Option contract objects
- Underlying positions
- Cash positions
- Long and short quantities
- Contract multipliers
- Position-level valuation
- Position-level Greeks

### Status

**Planned**

---

## Stage 4.2 — Multi-Leg Strategies

### Planned Capabilities

- Vertical spreads
- Straddles
- Strangles
- Butterflies
- Condors
- Calendars
- Diagonals
- Covered positions
- Custom strategy composition

### Status

**Planned**

---

## Stage 4.3 — Payoff and Scenario Analysis

### Planned Capabilities

- Expiry payoff
- Mark-to-market P&L
- Spot-volatility scenario grids
- Time-decay scenarios
- Break-even analysis
- Maximum gain and loss
- Greek decomposition
- Transaction-cost assumptions

### Status

**Planned**

---

## Stage 4.4 — Historical Strategy Research

### Planned Capabilities

- Entry and exit rules
- Option selection rules
- Rolling logic
- Position sizing
- Transaction costs
- Slippage assumptions
- Survivorship-safe data handling
- Performance attribution

### Status

**Planned**

---

# Stage 5 — Portfolio Risk Engine

## Objective

Aggregate instrument-level valuation and sensitivities into portfolio-level risk measures.

---

## Stage 5.1 — Portfolio Valuation

### Planned Capabilities

- Multi-instrument portfolios
- Net present value
- Aggregated Greeks
- Grouping by underlying
- Grouping by expiry
- Grouping by strategy
- Currency-aware valuation architecture

### Status

**Planned**

---

## Stage 5.2 — Scenario Risk

### Planned Capabilities

- Spot shocks
- Volatility shocks
- Rate shocks
- Time-decay shocks
- Parallel and non-parallel volatility moves
- Combined stress scenarios
- Full revaluation
- Greek approximation comparison

### Status

**Planned**

---

## Stage 5.3 — P&L Attribution

### Planned Capabilities

- Delta contribution
- Gamma contribution
- Vega contribution
- Theta contribution
- Rho contribution
- Higher-order residual
- Realised versus predicted P&L
- Daily attribution reports

### Status

**Planned**

---

## Stage 5.4 — Statistical Risk

### Planned Capabilities

- Historical Value at Risk
- Parametric Value at Risk
- Expected Shortfall
- Volatility and correlation estimation
- Stress-period replay
- Model-risk comparison

### Status

**Planned**

---

# Stage 6 — Electronic Market-Making Simulation

## Objective

Build an event-driven simulation of an options market maker managing quotes, fills, inventory, and risk.

This stage is intended to integrate the pricing, volatility, strategy, and risk components developed earlier.

---

## Stage 6.1 — Market Simulator

### Planned Capabilities

- Event-driven simulation loop
- Underlying-price process
- Option fair-value updates
- Bid and ask quotes
- Order arrivals
- Probabilistic or queue-based fills
- Position and cash accounting
- Configurable latency assumptions

### Status

**Planned**

---

## Stage 6.2 — Quoting Engine

### Planned Capabilities

- Fair-value-based quoting
- Minimum spread
- Volatility-aware spread
- Liquidity-aware spread
- Inventory skew
- Delta-risk skew
- Quote-size control
- Quote refresh logic

### Status

**Planned**

---

## Stage 6.3 — Hedging Engine

### Planned Capabilities

- Delta hedging
- Threshold-based hedging
- Periodic hedging
- Transaction costs
- Hedge slippage
- Hedge latency
- Residual risk tracking
- Comparison of hedging policies

### Status

**Planned**

---

## Stage 6.4 — Inventory and Risk Controls

### Planned Capabilities

- Position limits
- Delta limits
- Gamma limits
- Vega limits
- Loss limits
- Quote widening
- Quote withdrawal
- Kill-switch logic
- Risk-aware size reduction

### Status

**Planned**

---

## Stage 6.5 — Market-Making Evaluation

### Planned Metrics

- Gross and net P&L
- Spread capture
- Hedge P&L
- Inventory P&L
- Adverse selection
- Transaction costs
- Risk-adjusted returns
- Maximum drawdown
- Inventory utilisation
- Fill rate
- Quote competitiveness

### Planned Experiments

- Symmetric versus inventory-skewed quoting
- Different hedge thresholds
- Different volatility regimes
- Spread-width sensitivity
- Latency sensitivity
- Informed versus uninformed order flow
- Risk-limit effectiveness

### Status

**Planned**

---

# Stage 7 — Advanced Models and Research

## Objective

Extend the platform beyond the initial Black–Scholes–Merton assumptions.

Potential areas will be prioritised based on the maturity of the earlier stages.

---

## Candidate Extensions

### Pricing Models

- Local volatility
- Heston stochastic volatility
- Merton jump diffusion
- SABR
- Finite-difference PDE methods
- Least-Squares Monte Carlo
- Fourier pricing methods

### Products

- Barrier options
- Asian options
- Digital options
- Lookback options
- Bermudan options
- Variance swaps
- Volatility swaps

### Market Microstructure

- Limit-order-book simulation
- Queue-position modelling
- Adverse-selection models
- Order-flow imbalance
- Multi-venue execution
- Latency and stale-quote risk

### Research Infrastructure

- Calibration pipelines
- Experiment tracking
- Reproducible reports
- Benchmark datasets
- Performance profiling
- Parallel computation
- Optional compiled acceleration

### Status

**Exploratory**

---

# Cross-Cutting Engineering Work

The following work applies throughout all stages rather than belonging to a single milestone.

## Documentation

- Public API documentation
- Mathematical assumptions
- Formula and unit conventions
- Usage examples
- Numerical limitations
- Research methodology
- Architecture decisions

## Quality Assurance

- Unit tests
- Property-based tests
- Regression tests
- Numerical convergence tests
- Cross-model validation
- Static analysis
- Type checking
- Continuous integration

## Performance

Optimisation should occur only after correctness is established.

Potential work includes:

- Profiling
- Vectorisation
- Memory reduction
- Parallel simulation
- Caching
- Optional NumPy or compiled backends
- Benchmark tracking

## Reproducibility

- Fixed random seeds where appropriate
- Versioned configuration
- Raw and processed data separation
- Deterministic test fixtures
- Documented environment setup
- Saved experiment outputs

---

# Near-Term Priorities

The immediate development sequence is:

1. Introduce numerical Greek estimators
2. Begin market-data models and option-chain processing
3. Build chain-wide implied-volatility workflows
4. Start volatility smile and surface research

The project should not advance to complex volatility or market-making research until the foundational numerical methods are independently validated.

---

# Definition of Project Success

NCX Derivatives will be considered successful when it can:

- Price standard European and American derivatives using multiple methods
- Recover and analyse implied volatility from market quotes
- Construct and diagnose volatility smiles and surfaces
- Represent and value multi-leg portfolios
- Explain portfolio P&L through risk sensitivities
- Simulate a market maker that quotes, trades, hedges, and controls inventory
- Produce reproducible quantitative research supported by documented assumptions and automated tests

The final objective is not to reproduce the infrastructure of a full trading firm. It is to build a transparent, technically rigorous miniature derivatives research and market-making stack that demonstrates the mathematical, engineering, and decision-making foundations behind professional options trading.
