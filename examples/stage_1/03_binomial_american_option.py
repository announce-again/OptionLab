from ncx_derivatives.pricing import (
    BinomialTreeResult,
    binomial_put_price,
    put_price,
)


def main() -> None:
    spot = 80.0
    strike = 100.0
    maturity = 1.0
    rate = 0.05
    volatility = 0.25
    dividend_yield = 0.0

    european_put = put_price(
        spot,
        strike,
        maturity,
        rate,
        volatility,
        dividend_yield,
    )
    american_put = binomial_put_price(
        spot,
        strike,
        maturity,
        rate,
        volatility,
        dividend_yield,
        steps=500,
        american=True,
        return_exercise_boundary=True,
    )

    assert isinstance(american_put, BinomialTreeResult)

    early_exercise_steps = sum(
        boundary is not None
        for boundary in american_put.exercise_boundary
    )

    print(f"European put:         {european_put:.4f}")
    print(f"American put:         {american_put.price:.4f}")
    print(f"Early exercise steps: {early_exercise_steps}")


if __name__ == "__main__":
    main()
