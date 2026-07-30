from ncx_derivatives.greeks import call_delta, numerical_delta, numerical_vega
from ncx_derivatives.monte_carlo import monte_carlo_call_price
from ncx_derivatives.pricing import call_price


def main() -> None:
    spot = 100.0
    strike = 100.0
    maturity = 1.0
    rate = 0.05
    volatility = 0.20
    dividend_yield = 0.02

    analytical_delta = call_delta(
        spot,
        strike,
        maturity,
        rate,
        volatility,
        dividend_yield,
    )
    numerical_bs_delta = numerical_delta(
        call_price,
        spot,
        strike,
        maturity,
        rate,
        volatility,
        dividend_yield,
    )
    numerical_bs_vega = numerical_vega(
        call_price,
        spot,
        strike,
        maturity,
        rate,
        volatility,
        dividend_yield,
    )
    numerical_mc_delta = numerical_delta(
        monte_carlo_call_price,
        spot,
        strike,
        maturity,
        rate,
        volatility,
        dividend_yield,
        bump=0.10,
        simulations=50_000,
        seed=42,
        control_variate=True,
    )

    print(f"Analytical Delta:    {analytical_delta:.4f}")
    print(f"Numerical BS Delta:  {numerical_bs_delta:.4f}")
    print(f"Numerical BS Vega:   {numerical_bs_vega:.4f}")
    print(f"Numerical MC Delta:  {numerical_mc_delta:.4f}")


if __name__ == "__main__":
    main()
