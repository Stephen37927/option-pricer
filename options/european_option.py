from option import Option
import numpy as np
from scipy.stats import norm

class EuropeanOption(Option):

    def __init__(self, spot_price: float, risk_free_rate: float, maturity: float, strike_price: float, repo_rate: float, volatility: float, option_type: str = 'call'):
        """
        Constructor for EuropeanOption class.

        :param spot_price: Current price of the underlying asset
        :param risk_free_rate: Risk-free interest rate
        :param maturity: Time to maturity in years
        :param strike_price: Strike price of the option
        :param option_type: Type of the option ('call' or 'put')
        """
        super().__init__(spot_price, risk_free_rate, maturity, strike_price, volatility)
        self.option_type = option_type
        self.repo_rate = repo_rate
        

    def price(self):
        """
        Calculate the price of the European option using the Black-Scholes formula.

        :return: Price of the European option
        """

        # Implementation of the Black-Scholes formula for European option pricing
        # from math import exp, log, sqrt
        # from scipy.stats import norm

        # d1 = (log(self.spot_price / self.strike_price) + (self.risk_free_rate + 0.5 * (self.volatility ** 2)) * self.maturity) / (self.volatility * sqrt(self.maturity))
        # d2 = d1 - self.volatility * sqrt(self.maturity)

        # if self.option_type == 'call':
        #     return (self.spot_price * norm.cdf(d1) - self.strike_price * exp(-self.risk_free_rate * self.maturity) * norm.cdf(d2))
        # else:
        #     return (self.strike_price * exp(-self.risk_free_rate * self.maturity) * norm.cdf(-d2) - self.spot_price * norm.cdf(-d1))


        """
        Calculate the Black-Scholes option price considering the repo rate q
        """
        S0 = self.spot_price
        K = self.strike_price
        T = self.maturity
        r = self.risk_free_rate
        q = self.repo_rate
        sigma = self.volatility
        option_type = self.option_type
        d1 = (np.log(S0 / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        if option_type == 'call':
            price = S0 * np.exp(-q * T) * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        else:
            price = K * np.exp(-r * T) * norm.cdf(-d2) - S0 * np.exp(-q * T) * norm.cdf(-d1)
        return price
    
if __name__ == "__main__":
    # Example usage
    S0 = 2     # Underlying asset price
    K = 2      # Strike price
    T = 3      # Time to maturity (years)
    r = 0.03     # Risk-free rate
    q = 0     # Repo rate
    sigma = 0.3  # Volatility
    option_type = 'call'  # Option type ('call' or 'put')
    option = EuropeanOption(S0, r, T, K, q, sigma, option_type)
    print("European Option Price:", option.price())
    option = EuropeanOption(S0, r, T, K, q, sigma, 'put')
    print("European Option Price:", option.price())