from options.option import Option
import numpy as np
from scipy.stats import norm

class AsianOption(Option):
    def __init__(self, spot_price: float, risk_free_rate: float, maturity: float, strike_price: float, volatility: float, num_observations: int):
        """
        Base class for Asian options.

        :param spot_price: Current price of the underlying asset
        :param risk_free_rate: Risk-free interest rate
        :param maturity: Time to maturity in years
        :param strike_price: Strike price of the option
        :param volatility: Volatility of the underlying asset
        :param num_observations: Number of averaging observations
        """
        super().__init__(spot_price, risk_free_rate, maturity, strike_price, volatility)
        self.num_observations = num_observations


class GeometricAsianOption(AsianOption):
    def __init__(self, spot_price: float, risk_free_rate: float, maturity: float, strike_price: float, volatility: float, num_observations: int, option_type: str = 'call'):
        """
        Geometric Asian Option using closed-form formula.

        :param spot_price: Current price of the underlying asset
        :param risk_free_rate: Risk-free interest rate
        :param maturity: Time to maturity in years
        :param strike_price: Strike price of the option
        :param volatility: Volatility of the underlying asset
        :param num_observations: Number of averaging observations
        :param option_type: Type of the option ('call' or 'put')
        """
        super().__init__(spot_price, risk_free_rate, maturity, strike_price, volatility, num_observations)
        self.option_type = option_type

    def price(self):
        """
        Calculate the price of the Geometric Asian option using the closed-form formula.
        :return: Price of the Geometric Asian option
        """
        sigma = self.volatility
        S0 = self.spot_price
        K = self.strike_price
        r = self.risk_free_rate
        T = self.maturity
        n = self.num_observations
        option_type = self.option_type

        # Adjusted parameters for geometric averaging
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
    def __init__(self, spot_price: float, risk_free_rate: float, maturity: float, strike_price: float, volatility: float, num_observations: int, num_paths: int, use_control_variate: bool = True, option_type: str = 'call'):
        """
        Arithmetic Asian Option using Monte Carlo simulation.

        :param spot_price: Current price of the underlying asset
        :param risk_free_rate: Risk-free interest rate
        :param maturity: Time to maturity in years
        :param strike_price: Strike price of the option
        :param volatility: Volatility of the underlying asset
        :param num_observations: Number of averaging observations
        :param num_paths: Number of Monte Carlo simulation paths
        :param use_control_variate: Whether to use control variate technique
        :param option_type: Type of the option ('call' or 'put')
        """
        super().__init__(spot_price, risk_free_rate, maturity, strike_price, volatility, num_observations)
        self.num_paths = num_paths
        self.use_control_variate = use_control_variate
        self.option_type = option_type

    def price(self):
        """
        Estimate the price of the Arithmetic Asian option using Monte Carlo simulation.
        Uses geometric Asian option as control variate if enabled.

        :return: Tuple of estimated price and 95% confidence interval
        """
        dt = self.maturity / self.num_observations
        drift = (self.risk_free_rate - 0.5 * self.volatility**2) * dt
        diffusion = self.volatility * np.sqrt(dt)

        # Simulate asset paths
        np.random.seed(0)  # For reproducibility
        Z = np.random.normal(size=(self.num_paths, self.num_observations))
        S_paths = self.spot_price * np.exp(np.cumsum(drift + diffusion * Z, axis=1))

        # Arithmetic and geometric averages
        arithmetic_means = np.mean(S_paths, axis=1)
        geometric_means = np.exp(np.mean(np.log(S_paths), axis=1))

        if self.option_type == 'call':
            payoffs_arith = np.exp(-self.risk_free_rate * self.maturity) * np.maximum(arithmetic_means - self.strike_price, 0)
            payoffs_geom = np.exp(-self.risk_free_rate * self.maturity) * np.maximum(geometric_means - self.strike_price, 0)
        elif self.option_type == 'put':
            payoffs_arith = np.exp(-self.risk_free_rate * self.maturity) * np.maximum(self.strike_price - arithmetic_means, 0)
            payoffs_geom = np.exp(-self.risk_free_rate * self.maturity) * np.maximum(self.strike_price - geometric_means, 0)
        else:
            raise ValueError("option_type must be 'call' or 'put'")

        # Apply control variate
        if self.use_control_variate:
            geo_option = GeometricAsianOption(
                self.spot_price, self.risk_free_rate, self.maturity, self.strike_price,
                self.volatility, self.num_observations, self.option_type
            )
            geo_price = geo_option.price()
            cov = np.cov(payoffs_arith, payoffs_geom)[0, 1]
            theta = cov / np.var(payoffs_geom)
            adjusted_payoffs = payoffs_arith + theta * (geo_price - payoffs_geom)
        else:
            adjusted_payoffs = payoffs_arith

        price = np.mean(adjusted_payoffs)
        std_err = np.std(adjusted_payoffs, ddof=1) / np.sqrt(self.num_paths)
        conf_interval = (float(price - 1.96 * std_err), float(price + 1.96 * std_err))

        return price, conf_interval


# Example usage
if __name__ == "__main__":
    S0 = 100      # Initial stock price
    r = 0.05      # Risk-free rate
    T = 3         # Time to maturity
    K = 100       # Strike price
    sigma = 0.3   # Volatility
    N = 50        # Number of observations

    geo_option = GeometricAsianOption(
        spot_price=S0,
        risk_free_rate=r,
        maturity=T,
        strike_price=K,
        volatility=sigma,
        num_observations=N,
        option_type='call'
    )

    ari_option = ArithmeticAsianOption(
        spot_price=S0,
        risk_free_rate=r,
        maturity=T,
        strike_price=K,
        volatility=sigma,
        num_observations=N,
        num_paths=100000,
        use_control_variate=False,
        option_type='put'
    )

    price, conf_interval = ari_option.price()
    print(f"Arithmetic Asian Option Price: {price:.4f}")
    print(f"95% Confidence Interval: {conf_interval}")

    geo_price = geo_option.price()
    print(f"Geometric Asian Option Price: {geo_price:.4f}")