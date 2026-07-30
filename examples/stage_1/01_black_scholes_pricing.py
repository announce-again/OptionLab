from ncx_derivatives.greeks import call_delta, gamma, vega
from ncx_derivatives.pricing import call_price, put_price


def main() -> None:
    spot = 100.0
    strike = 100.0
    maturity = 1.0
    rate = 0.05
    volatility = 0.20
    dividend_yield = 0.02

    call = call_price(
        spot,
        strike,
        maturity,
        rate,
        volatility,
        dividend_yield,
    )
    put = put_price(
        spot,
        strike,
        maturity,
        rate,
        volatility,
        dividend_yield,
    )

    print(f"Call price: {call:.4f}")
    print(f"Put price:  {put:.4f}")
    print(
        "Call Delta: "
        f"{call_delta(spot, strike, maturity, rate, volatility, dividend_yield):.4f}"
    )
    print(
        "Gamma:      "
        f"{gamma(spot, strike, maturity, rate, volatility, dividend_yield):.6f}"
    )
    print(
        "Vega:       "
        f"{vega(spot, strike, maturity, rate, volatility, dividend_yield):.4f}"
    )


if __name__ == "__main__":
    main()
