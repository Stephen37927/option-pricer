# from options.option import Option
from option import Option
import numpy as np
from scipy.stats import norm

class BasketOption(Option):
    def __init__(self, spot_prices: list, risk_free_rate: float, maturity: float, strike_price: float, volatilities: list, correlation: float):
        """
        Base class for Basket Option.

        :param spot_prices: List of current prices of the underlying assets
        :param risk_free_rate: Risk-free interest rate
        :param maturity: Time to maturity in years
        :param strike_price: Strike price of the option
        :param volatilities: List of volatilities for each underlying asset
        :param correlation: Correlation coefficient between the underlying assets (assumed equal pairwise)
        """
        super().__init__(spot_prices[0], risk_free_rate, maturity, strike_price)
        self.spot_prices = spot_prices
        self.volatilities = volatilities
        self.correlation = correlation


class GeometricBasketOption(BasketOption):
    def __init__(self, spot_prices: list, risk_free_rate: float, maturity: float, strike_price: float, volatilities: list, correlation: float, option_type: str = 'call'):
        """
        Geometric Basket Option with closed-form pricing formula.

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
        Calculate the price of the Geometric Basket option using closed-form solution.

        :return: Price of the Geometric Basket Option
        """
        S = np.array(self.spot_prices)
        sigma = np.array(self.volatilities)
        K = self.strike_price
        r = self.risk_free_rate
        T = self.maturity
        rho = self.correlation
        n = len(S)

        # Geometric average of initial prices
        G0 = np.prod(S) ** (1 / n)

        # Effective basket volatility under constant correlation assumption
        sigma_G_squared = (1 / n**2) * (
            np.sum(sigma**2) + rho * (np.sum(sigma)**2 - np.sum(sigma**2))
        )
        sigma_G = np.sqrt(sigma_G_squared)

        # Drift of geometric basket
        avg_var = np.mean(sigma**2)           # 各资产方差的平均
        mu_G = r - 0.5 * avg_var + 0.5 * sigma_G_squared

        # mu_G = r - 0.5 * sigma_G_squared

        # d1 and d2 for BS-like formula
        d1 = (np.log(G0 / K) + (mu_G + 0.5 * sigma_G_squared) * T) / (sigma_G * np.sqrt(T))
        d2 = d1 - sigma_G * np.sqrt(T)

        # Closed-form pricing based on option type
        if self.option_type == 'call':
            price = np.exp(-r * T) * (G0 * np.exp(mu_G * T) * norm.cdf(d1) - K * norm.cdf(d2))
        elif self.option_type == 'put':
            price = np.exp(-r * T) * (K * norm.cdf(-d2) - G0 * np.exp(mu_G * T) * norm.cdf(-d1))
        else:
            raise ValueError("option_type must be 'call' or 'put'")

        return price

class ArithmeticBasketOption(GeometricBasketOption):
    def __init__(self, spot_prices: list, risk_free_rate: float, maturity: float, strike_price: float,
                 volatilities: list, correlation: float, option_type: str = 'call',
                 num_paths: int = 10000, control_variate: str = 'geometric'):
        """
        Arithmetic mean basket option pricer using Monte Carlo with control variate.

        :param spot_prices: List of two spot prices
        :param risk_free_rate: Risk-free rate
        :param maturity: Time to maturity
        :param strike_price: Strike price
        :param volatilities: List of two volatilities
        :param correlation: Correlation between assets
        :param option_type: 'call' or 'put'
        :param num_paths: Number of Monte Carlo paths
        :param control_variate: 'none' or 'geometric'
        """
        super().__init__(spot_prices, risk_free_rate, maturity, strike_price, volatilities, correlation, option_type)
        self.num_paths = num_paths
        self.control_variate = control_variate

    # def price(self):
    #     """
    #     Monte Carlo simulation for arithmetic basket option with optional control variate technique.
        
    #     :return: Estimated option price with 95% confidence interval (tuple)
    #     """
    #     S1, S2 = self.spot_prices
    #     sigma1, sigma2 = self.volatilities
    #     rho = self.correlation
    #     T = self.maturity
    #     K = self.strike_price
    #     r = self.risk_free_rate
    #     n = self.num_paths
    #     option_type = self.option_type

    #     np.random.seed(0)  # random seed🧪

    #     # Generate correlated random variables
    #     Z1 = np.random.randn(n)
    #     Z2 = rho * Z1 + np.sqrt(1 - rho**2) * np.random.randn(n)

    #     # Simulate the asset prices at maturity
    #     S1_T = S1 * np.exp((r - 0.5 * sigma1**2) * T + sigma1 * np.sqrt(T) * Z1)
    #     S2_T = S2 * np.exp((r - 0.5 * sigma2**2) * T + sigma2 * np.sqrt(T) * Z2)

    #     # Arithmetic mean payoff
    #     arithmetic_mean = (S1_T + S2_T) / 2
    #     if option_type == 'call':
    #         payoff_arith = np.maximum(arithmetic_mean - K, 0)
    #     elif option_type == 'put':
    #         payoff_arith = np.maximum(K - arithmetic_mean, 0)
    #     else:
    #         raise ValueError("option_type must be 'call' or 'put'")

    #     if self.control_variate == 'geometric':
    #         # Calculate the geometric mean payoff
    #         geometric_mean = np.sqrt(S1_T * S2_T)
    #         if option_type == 'call':
    #             payoff_geom = np.maximum(geometric_mean - K, 0)
    #         else:
    #             payoff_geom = np.maximum(K - geometric_mean, 0)

    #         # Geometric basket option price as control variate
    #         geo_option = GeometricBasketOption(self.spot_prices, r, T, K, self.volatilities, rho, option_type)
    #         geo_price_analytic = geo_option.price()

    #         # Calculate the covariance between the payoffs
    #         cov_matrix = np.cov(payoff_arith, payoff_geom)
    #         b_hat = cov_matrix[0, 1] / cov_matrix[1, 1]

    #         # Control variate adjustment
    #         price_control = np.exp(-r * T) * (payoff_arith - b_hat * (payoff_geom - geo_price_analytic))

    #         price_mean = np.mean(price_control)
    #         std_dev = np.std(price_control, ddof=1)
    #     else:
    #         # No control variate adjustment
    #         discounted_payoff = np.exp(-r * T) * payoff_arith
    #         price_mean = np.mean(discounted_payoff)
    #         std_dev = np.std(discounted_payoff, ddof=1)

    #     # 95% confidence interval
    #     conf_interval = (float(price_mean - 1.96 * std_dev / np.sqrt(n)),
    #                      float(price_mean + 1.96 * std_dev / np.sqrt(n)))

    #     return price_mean, conf_interval
    def price(self):
        """
        Monte Carlo simulation for arithmetic basket option with optional control variate technique.
        
        :return: Estimated option price with 95% confidence interval (tuple)
        """
        S1, S2 = self.spot_prices
        sigma1, sigma2 = self.volatilities
        rho = self.correlation
        T = self.maturity
        K = self.strike_price
        r = self.risk_free_rate
        n = self.num_paths
        option_type = self.option_type

        np.random.seed(0)  # 固定随机种子，便于结果复现

        # 生成相关标准正态随机变量
        Z1 = np.random.randn(n)
        Z2 = rho * Z1 + np.sqrt(1 - rho**2) * np.random.randn(n)

        # 模拟到期价格
        S1_T = S1 * np.exp((r - 0.5 * sigma1**2) * T + sigma1 * np.sqrt(T) * Z1)
        S2_T = S2 * np.exp((r - 0.5 * sigma2**2) * T + sigma2 * np.sqrt(T) * Z2)

        # 计算算术平均
        arithmetic_mean = (S1_T + S2_T) / 2
        if option_type == 'call':
            payoff_arith = np.maximum(arithmetic_mean - K, 0)
        elif option_type == 'put':
            payoff_arith = np.maximum(K - arithmetic_mean, 0)
        else:
            raise ValueError("option_type must be 'call' or 'put'")

        if self.control_variate == 'geometric':
            # 计算几何平均
            geometric_mean = np.sqrt(S1_T * S2_T)
            if option_type == 'call':
                payoff_geom = np.maximum(geometric_mean - K, 0)
            else:
                payoff_geom = np.maximum(K - geometric_mean, 0)

            # 计算几何篮子期权价格的解析解作为控制变量的已知值
            geo_option = GeometricBasketOption(self.spot_prices, r, T, K, self.volatilities, rho, option_type)
            geo_price_analytic = geo_option.price()

            # 计算折现后的 payoffs
            X = np.exp(-r * T) * payoff_arith  # 算术部分
            Y = np.exp(-r * T) * payoff_geom   # 几何部分

            # 使用折现后的值计算控制变量系数
            cov_matrix = np.cov(X, Y)
            b_hat = cov_matrix[0, 1] / cov_matrix[1, 1]

            # 控制变量调整
            price_control = X - b_hat * (Y - geo_price_analytic)

            price_mean = np.mean(price_control)
            std_dev = np.std(price_control, ddof=1)
        else:
            # 若不使用控制变量
            discounted_payoff = np.exp(-r * T) * payoff_arith
            price_mean = np.mean(discounted_payoff)
            std_dev = np.std(discounted_payoff, ddof=1)

        # 95% 置信区间
        conf_interval = (float(price_mean - 1.96 * std_dev / np.sqrt(n)),
                        float(price_mean + 1.96 * std_dev / np.sqrt(n)))

        return price_mean, conf_interval


# Example usage
if __name__ == "__main__":
    spot_prices = [100, 100]
    risk_free_rate = 0.05
    maturity = 3
    strike_price = 100
    volatilities = [0.3, 0.3]
    correlation = 0.5
    option_type = 'call'

    geometric_option = GeometricBasketOption(spot_prices, risk_free_rate, maturity, strike_price, volatilities, correlation, option_type)
    print("Geometric Basket Option Price:", geometric_option.price())

    use_control_variate = True
    control_variate = 'geometric' if use_control_variate else 'none'
    arithmetic_option = ArithmeticBasketOption(spot_prices, risk_free_rate, maturity, strike_price, volatilities, correlation, option_type, num_paths=10000, control_variate=control_variate)
    price, conf_interval = arithmetic_option.price()
    print("Arithmetic Basket Option Price:", price)
    print("95% Confidence Interval:", conf_interval)