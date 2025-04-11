from .option import Option
import numpy as np
from scipy.stats import norm

class BasketOption(Option):

    def __init__(self, spot_prices: list, risk_free_rate: float, maturity: float, strike_price: float, volatilities: list, correlation: float):
        """
        Constructor for BasketOption class.

        :param spot_prices: List of current prices of the underlying assets
        :param risk_free_rate: Risk-free interest rate
        :param maturity: Time to maturity in years
        :param strike_price: Strike price of the option
        :param volatilities: List of volatilities for each underlying asset
        :param correlation: Correlation coefficient between the underlying assets
        """
        super().__init__(spot_prices[0], risk_free_rate, maturity, strike_price)
        self.spot_prices = spot_prices
        self.volatilities = volatilities
        self.correlation = correlation


class GeometricBasketOption(BasketOption):

    def __init__(self, spot_prices: list, risk_free_rate: float, maturity: float, strike_price: float, volatilities: list, correlation: float, option_type: str = 'call'):
        """
        Constructor for GeometricBasketOption class.

        :param spot_prices: List of current prices of the underlying assets
        :param risk_free_rate: Risk-free interest rate
        :param maturity: Time to maturity in years
        :param strike_price: Strike price of the option
        :param volatilities: List of volatilities for each underlying asset
        :param correlation: Correlation coefficient between the underlying assets
        :param option_type: Type of the option ('call' or 'put')
        """
        super().__init__(spot_prices, risk_free_rate, maturity, strike_price, volatilities, correlation)
        self.option_type = option_type

    def price(self):
        """
        Calculate the price of the Geometric Basket option with closed-form formula. 
        :return: Price of the Geometric Basket option
        """
        # Implementation of the closed-form formula for Geometric Basket option pricing
        S = self.spot_prices
        sigma = self.volatilities
        K = self.strike_price
        r = self.risk_free_rate
        T = self.maturity
        rho = self.correlation
        option_type = self.option_type

        n = len(S)
        S = np.array(S)
        sigma = np.array(sigma)

        # 几何平均初始价格 G_0
        G0 = np.prod(S) ** (1 / n)

        # Effective volatility σ_G
        sigma_G_squared = (1 / n**2) * (
            np.sum(sigma**2) + rho * (np.sum(sigma)**2 - np.sum(sigma**2))
        )
        sigma_G = np.sqrt(sigma_G_squared)

        # μ_G
        mu_G = r - 0.5 * sigma_G_squared

        # d1 和 d2
        d1 = (np.log(G0 / K) + (mu_G + 0.5 * sigma_G_squared) * T) / (sigma_G * np.sqrt(T))
        d2 = d1 - sigma_G * np.sqrt(T)

        # 封闭公式
        if option_type == 'call':
            price = np.exp(-r * T) * (G0 * np.exp(mu_G * T) * norm.cdf(d1) - K * norm.cdf(d2))
        elif option_type == 'put':
            price = np.exp(-r * T) * (K * norm.cdf(-d2) - G0 * np.exp(mu_G * T) * norm.cdf(-d1))
        else:
            raise ValueError("option_type must be 'call' or 'put'")

        return price

class ArithmeticBasketOption(BasketOption):

    # addtional parameters include num_paths, use_control_variate, option_type
    def __init__(self, spot_prices: list, risk_free_rate: float, maturity: float, strike_price: float, volatilities: list, correlation: float, num_paths: int, use_control_variate: bool = True, option_type: str = 'call'):
        """
        Constructor for ArithmeticBasketOption class.

        :param spot_prices: List of current prices of the underlying assets
        :param risk_free_rate: Risk-free interest rate
        :param maturity: Time to maturity in years
        :param strike_price: Strike price of the option
        :param volatilities: List of volatilities for each underlying asset
        :param correlation: Correlation coefficient between the underlying assets
        :param num_paths: Number of Monte Carlo simulation paths
        :param use_control_variate: Whether to use control variate technique
        :param option_type: Type of the option ('call' or 'put')
        """
        super().__init__(spot_prices, risk_free_rate, maturity, strike_price, volatilities, correlation)
        self.num_paths = num_paths
        self.use_control_variate = use_control_variate
        self.option_type = option_type

    def price(self):
        """
        Calculate the price of the Arithmetic Basket option using Monte Carlo simulation.
        :return: Price of the Arithmetic Basket option
        """
        # Implementation of the Monte Carlo simulation for Arithmetic Basket option pricing
        pass
