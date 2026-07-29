from ncx_derivatives.pricing import call_price, put_price

def test_black_scholes_prices():
    call = call_price(
        S=100,
        K=100,
        T=1,
        r=0.05,
        sigma=0.2,
    )

    put = put_price(
        S=100,
        K=100,
        T=1,
        r=0.05,
        sigma=0.2,
    )

    assert abs(call - 10.4506) < 1e-4
    assert abs(put - 5.5735) < 1e-4