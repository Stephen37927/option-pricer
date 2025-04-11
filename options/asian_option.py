from .option import Option
import numpy as np
from scipy.stats import norm

class AsianOption(Option):

    def __init__(self, spot_price: float, risk_free_rate: float, maturity: float, strike_price: float, num_observations: int):
        """
        Constructor for AsianOption class.

        :param spot_price: Current price of the underlying asset
        :param risk_free_rate: Risk-free interest rate
        :param maturity: Time to maturity in years
        :param strike_price: Strike price of the option
        :param average_type: Type of averaging ('arithmetic' or 'geometric')
        """
        super().__init__(spot_price, risk_free_rate, maturity, strike_price)
        self.num_observations = num_observations

class GeometricAsianOption(AsianOption):

    def __init__(self, spot_price: float, risk_free_rate: float, maturity: float, strike_price: float, num_observations: int, option_type: str = 'call'):
        """
        Constructor for GeometricAsianOption class.

        :param spot_price: Current price of the underlying asset
        :param risk_free_rate: Risk-free interest rate
        :param maturity: Time to maturity in years
        :param strike_price: Strike price of the option
        :param option_type: Type of the option ('call' or 'put')
        """
        super().__init__(spot_price, risk_free_rate, maturity, strike_price, num_observations)
        self.option_type = option_type

    def price(self):
        """
        Calculate the price of the Geometric Asian option with closed-form formula. 
        :return: Price of the Geometric Asian option
        """
        # Parameters transferred from the parent class
        sigma = self.volatility
        S0 = self.spot_price
        K = self.strike_price
        r = self.risk_free_rate
        T = self.maturity
        n = self.num_observations
        option_type = self.option_type
        # Implementation of the closed-form formula for Geometric Asian option pricing
        sigma_hat = sigma * np.sqrt((n+1) * (2*n + 1)/(6*n**2))
        mu_hat = (r - 0.5 * sigma**2) * (n + 1) / (2*n) + 0.5 * sigma_hat**2
        d1 = (np.log(S0 / K) + (mu_hat + 0.5 * sigma_hat**2) * T) / (sigma_hat * np.sqrt(T))
        d2 = d1 - sigma_hat * np.sqrt(T)
        
        if option_type == "call":
            price = np.exp(-r * T) * (S0 * np.exp(mu_hat * T) * norm.cdf(d1) - K * norm.cdf(d2))
        elif option_type == "put":
            price = np.exp(-r * T) * (K * norm.cdf(-d2) - S0 * np.exp(mu_hat * T) * norm.cdf(-d1))
        else:
            raise ValueError("option_type must be 'call' or 'put'")
        
        return price

class ArithmeticAsianOption(AsianOption):

    def __init__(self, spot_price: float, risk_free_rate: float, maturity: float, strike_price: float, num_observations: int, num_paths: int, use_control_variate: bool = True, option_type: str = 'call'):
        """
        Constructor for ArithmeticAsianOption class.

        :param spot_price: Current price of the underlying asset
        :param risk_free_rate: Risk-free interest rate
        :param maturity: Time to maturity in years
        :param strike_price: Strike price of the option
        :param num_observations: Number of observations for averaging
        :param num_paths: Number of Monte Carlo simulation paths
        :param use_control_variate: Whether to use control variate technique
        :param option_type: Type of the option ('call' or 'put')
        """
        super().__init__(spot_price, risk_free_rate, maturity, strike_price, num_observations)
        self.num_paths = num_paths
        self.use_control_variate = use_control_variate
        self.option_type = option_type

    def price(self):
        """
        Calculate the price of the Arithmetic Asian option using Monte Carlo simulation.
        :return: Price of the Arithmetic Asian option
        """
        # Implementation of the Monte Carlo simulation for Arithmetic Asian option pricing
        


    