from ncx_derivatives.monte_carlo import monte_carlo_call_price
from ncx_derivatives.pricing import call_price


def main() -> None:
    spot = 100.0
    strike = 100.0
    maturity = 1.0
    rate = 0.05
    volatility = 0.20
    dividend_yield = 0.02

    result = monte_carlo_call_price(
        spot,
        strike,
        maturity,
        rate,
        volatility,
        dividend_yield,
        simulations=50_000,
        seed=42,
        control_variate=True,
    )
    analytic = call_price(
        spot,
        strike,
        maturity,
        rate,
        volatility,
        dividend_yield,
    )

    print(f"Monte Carlo price: {result.price:.4f}")
    print(f"Standard error:    {result.standard_error:.4f}")
    print(
        "95% CI:            "
        f"[{result.confidence_interval[0]:.4f}, "
        f"{result.confidence_interval[1]:.4f}]"
    )
    print(f"Analytical price:  {analytic:.4f}")


if __name__ == "__main__":
    main()
