from ncx_derivatives.pricing import call_price
from ncx_derivatives.volatility import call_implied_volatility


def main() -> None:
    spot = 100.0
    strike = 105.0
    maturity = 0.75
    rate = 0.04
    volatility = 0.25
    dividend_yield = 0.01

    market_price = call_price(
        spot,
        strike,
        maturity,
        rate,
        volatility,
        dividend_yield,
    )
    implied_volatility = call_implied_volatility(
        market_price,
        spot,
        strike,
        maturity,
        rate,
        dividend_yield,
    )

    print(f"Market price:       {market_price:.4f}")
    print(f"Implied volatility: {implied_volatility:.4%}")


if __name__ == "__main__":
    main()
