from ncx_derivatives.monte_carlo import monte_carlo_asian_call_price
from ncx_derivatives.pricing import call_price


def main() -> None:
    spot = 100.0
    strike = 100.0
    maturity = 1.0
    rate = 0.05
    volatility = 0.20
    dividend_yield = 0.0

    asian_call = monte_carlo_asian_call_price(
        spot,
        strike,
        maturity,
        rate,
        volatility,
        dividend_yield,
        monitoring_dates=12,
        simulations=50_000,
        seed=7,
        antithetic=True,
        control_variate=True,
    )
    european_call = call_price(
        spot,
        strike,
        maturity,
        rate,
        volatility,
        dividend_yield,
    )

    print(f"Asian call price:    {asian_call.price:.4f}")
    print(f"Standard error:      {asian_call.standard_error:.4f}")
    print(f"European call price: {european_call:.4f}")


if __name__ == "__main__":
    main()
