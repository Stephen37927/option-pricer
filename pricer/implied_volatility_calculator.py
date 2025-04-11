import numpy as np
from scipy.stats import norm

class ImpliedVolatility:

    def __init__(self):
        """
        Constructor for ImpliedVolatility class.
        """
        pass

    def calculate(self, option_type, spot_price, risk_free_rate, repo_rate, maturity, strike_price, option_premium):
        """
        Calculate the implied volatility using Newton-Raphson method.

        """

        # Implementation of the Newton-Raphson method for implied volatility calculation

        def black_scholes_price(S0, K, T, r, q, sigma, option_type='call'):
            """
            Calculate the Black-Scholes option price considering the repo rate q
            """
            d1 = (np.log(S0 / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
            d2 = d1 - sigma * np.sqrt(T)
            
            if option_type == 'call':
                price = S0 * np.exp(-q * T) * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
            else:
                price = K * np.exp(-r * T) * norm.cdf(-d2) - S0 * np.exp(-q * T) * norm.cdf(-d1)
            return price

        def compute_vega(S0, K, T, r, q, sigma):
            """
            Calculate the Vega of the option (sensitivity to volatility)
            """
            d1 = (np.log(S0 / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
            vega = S0 * np.exp(-q * T) * np.sqrt(T) * norm.pdf(d1)
            return vega

        def initial_sigma_guess(S0, K, T, r, q):
            """
            Calculate the initial volatility guess based on the provided formula
            """
            numerator = np.log(S0 / K) + (r - q) * T
            denominator = T
            sigma_guess = np.sqrt(2 * np.abs(numerator / denominator))
            return sigma_guess

        def is_price_valid(S0, K, T, r, q, market_price):
            # Calculate theoretical price lower and upper bounds
            lower_bound = max(S0 * np.exp(-q * T) - K * np.exp(-r * T), 0)
            upper_bound = S0 * np.exp(-q * T)
            
            # Check if the market price is within a reasonable range
            if market_price < lower_bound - 1e-6:  # Consider floating-point error
                return False, "Market price is below the theoretical lower bound (arbitrage opportunity exists)"
            elif market_price > upper_bound + 1e-6:
                return False, "Market price is above the theoretical upper bound (risk-free arbitrage)"
            else:
                return True, ""

        def find_implied_volatility(S0, K, T, r, q, market_price, max_iter=100, tol=1e-6, option_type='call'):
            """
            Use Newton-Raphson iteration to solve for the implied volatility
            market_price: the option premium
            """
            # Calculate theoretical price lower and upper bounds
            lower_bound = max(S0 * np.exp(-q * T) - K * np.exp(-r * T), 0)
            upper_bound = S0 * np.exp(-q * T)
            
            # Check if the market price is within a reasonable range
            if market_price < lower_bound - 1e-6 or market_price > upper_bound + 1e-6:  # Consider floating-point error
                return np.nan
            
            # Initial guess
            sigma = initial_sigma_guess(S0, K, T, r, q)
            
            for _ in range(max_iter):
                # Calculate model price and Vega
                price = black_scholes_price(S0, K, T, r, q, sigma, option_type)
                vega = compute_vega(S0, K, T, r, q, sigma)
                
                # Calculate error
                error = price - market_price
                
                # Update volatility
                sigma -= error / vega
                
                # Check for convergence
                if np.abs(error) < tol:
                    return sigma
            
            # If not converged, return NaN
            return np.nan

        S0 = spot_price
        K = strike_price
        T = maturity
        r = risk_free_rate
        q = repo_rate
        market_price = option_premium
        option_type = option_type.lower()
        if option_type not in ['call', 'put']:
            raise ValueError("option_type must be either 'call' or 'put'")
        # Check if the market price is valid
        is_valid, message = is_price_valid(S0, K, T, r, q, market_price)
        if not is_valid:
            raise ValueError(message)
        # Find the implied volatility
        implied_volatility = find_implied_volatility(S0, K, T, r, q, market_price, option_type=option_type)
        if np.isnan(implied_volatility):
            raise ValueError("Implied volatility calculation did not converge.")
        return implied_volatility

if __name__ == "__main__":
    # Example usage
    iv_calculator = ImpliedVolatility()
    # Parameter settings
    S0 = 2     # Underlying asset price
    K = 2      # Strike price
    T = 3      # Time to maturity (years)
    r = 0.03     # Risk-free rate
    q = 0.01     # Repo rate
    option_premium = 0.4841  # Observed market option price

    try:
        iv = iv_calculator.calculate('call', S0, r, q, T, K, option_premium)
        print(f"Implied Volatility: {iv}")
    except ValueError as e:
        print(e)