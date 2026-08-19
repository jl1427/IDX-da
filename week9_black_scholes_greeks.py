"""
Week 9 - Black-Scholes and the Greeks
Computational Finance

Main ideas:
1. Black-Scholes European call and put prices
2. d1 and d2
3. Delta
4. Gamma
5. Vega
6. Theta
7. Rho

This file is self-contained and can be run directly.
"""

import numpy as np
import pandas as pd
from scipy.stats import norm


def d1_d2(S, K, T, r, sigma, q=0.0):
    """
    Calculate d1 and d2.

    S     = stock price
    K     = strike price
    T     = time to maturity in years
    r     = continuously compounded risk-free rate
    sigma = annualized volatility
    q     = continuous dividend yield
    """
    if S <= 0 or K <= 0 or T <= 0 or sigma <= 0:
        raise ValueError("S, K, T, and sigma must be positive.")

    d1 = (
        np.log(S / K)
        + (r - q + 0.5 * sigma**2) * T
    ) / (sigma * np.sqrt(T))

    d2 = d1 - sigma * np.sqrt(T)

    return d1, d2


def black_scholes_call(S, K, T, r, sigma, q=0.0):
    """European call option price."""
    d1, d2 = d1_d2(S, K, T, r, sigma, q)

    return (
        S * np.exp(-q * T) * norm.cdf(d1)
        - K * np.exp(-r * T) * norm.cdf(d2)
    )


def black_scholes_put(S, K, T, r, sigma, q=0.0):
    """European put option price."""
    d1, d2 = d1_d2(S, K, T, r, sigma, q)

    return (
        K * np.exp(-r * T) * norm.cdf(-d2)
        - S * np.exp(-q * T) * norm.cdf(-d1)
    )


def greeks(S, K, T, r, sigma, q=0.0):
    """
    Return Black-Scholes Greeks for a European call and put.

    Theta is reported per YEAR.
    Vega and Rho are reported for a 1.00 absolute change,
    so divide by 100 to interpret a 1 percentage-point change.
    """
    d1, d2 = d1_d2(S, K, T, r, sigma, q)

    pdf_d1 = norm.pdf(d1)

    call_delta = np.exp(-q * T) * norm.cdf(d1)
    put_delta = np.exp(-q * T) * (norm.cdf(d1) - 1)

    gamma = (
        np.exp(-q * T) * pdf_d1
        / (S * sigma * np.sqrt(T))
    )

    vega = S * np.exp(-q * T) * pdf_d1 * np.sqrt(T)

    call_theta = (
        -S * np.exp(-q * T) * pdf_d1 * sigma / (2 * np.sqrt(T))
        - r * K * np.exp(-r * T) * norm.cdf(d2)
        + q * S * np.exp(-q * T) * norm.cdf(d1)
    )

    put_theta = (
        -S * np.exp(-q * T) * pdf_d1 * sigma / (2 * np.sqrt(T))
        + r * K * np.exp(-r * T) * norm.cdf(-d2)
        - q * S * np.exp(-q * T) * norm.cdf(-d1)
    )

    call_rho = K * T * np.exp(-r * T) * norm.cdf(d2)
    put_rho = -K * T * np.exp(-r * T) * norm.cdf(-d2)

    return {
        "Call Delta": call_delta,
        "Put Delta": put_delta,
        "Gamma": gamma,
        "Vega": vega,
        "Call Theta": call_theta,
        "Put Theta": put_theta,
        "Call Rho": call_rho,
        "Put Rho": put_rho,
    }


def put_call_parity_check(S, K, T, r, sigma, q=0.0):
    """Check European put-call parity."""
    call = black_scholes_call(S, K, T, r, sigma, q)
    put = black_scholes_put(S, K, T, r, sigma, q)

    left = call - put
    right = S * np.exp(-q * T) - K * np.exp(-r * T)

    return left, right, left - right


def demo():
    # Example option inputs
    S = 100.0
    K = 100.0
    T = 0.50
    r = 0.04
    sigma = 0.25
    q = 0.00

    print("=" * 70)
    print("WEEK 9: BLACK-SCHOLES AND THE GREEKS")
    print("=" * 70)

    call_price = black_scholes_call(S, K, T, r, sigma, q)
    put_price = black_scholes_put(S, K, T, r, sigma, q)

    print("\nInputs")
    print(f"Stock price S:     {S}")
    print(f"Strike K:          {K}")
    print(f"Time T:            {T} years")
    print(f"Risk-free rate r:  {r:.2%}")
    print(f"Volatility sigma:  {sigma:.2%}")

    print("\n1. Black-Scholes prices")
    print(f"Call price: {call_price:.4f}")
    print(f"Put price:  {put_price:.4f}")

    g = greeks(S, K, T, r, sigma, q)

    table = pd.DataFrame({
        "Greek": [
            "Call Delta",
            "Put Delta",
            "Gamma",
            "Vega (per 1 vol unit)",
            "Call Theta (per year)",
            "Put Theta (per year)",
            "Call Rho (per 1 rate unit)",
            "Put Rho (per 1 rate unit)",
        ],
        "Value": [
            g["Call Delta"],
            g["Put Delta"],
            g["Gamma"],
            g["Vega"],
            g["Call Theta"],
            g["Put Theta"],
            g["Call Rho"],
            g["Put Rho"],
        ],
    })

    print("\n2. Greeks")
    print(table.to_string(index=False))

    left, right, error = put_call_parity_check(S, K, T, r, sigma, q)

    print("\n3. Put-call parity check")
    print(f"C - P:                         {left:.8f}")
    print(f"S*exp(-qT) - K*exp(-rT):      {right:.8f}")
    print(f"Difference:                    {error:.12f}")

    print("\nMEETING SUMMARY")
    print("- Black-Scholes gives a theoretical price for European options.")
    print("- Delta measures option sensitivity to the stock price.")
    print("- Gamma measures how quickly Delta changes.")
    print("- Vega measures sensitivity to volatility.")
    print("- Theta measures time decay.")
    print("- Rho measures sensitivity to the risk-free interest rate.")
    print("- The model assumes a stylized market, so actual option prices can differ.")


if __name__ == "__main__":
    demo()
