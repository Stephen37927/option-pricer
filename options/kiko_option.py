from option import Option
import numpy as np
import math
from scipy.stats import norm, qmc

class KIKOOption(Option):

    # additional parameters: lower_barrier, upper_barrier, num_observations, rebate
    def __init__(self, spot_price: float, risk_free_rate: float, maturity: float, strike_price: float, volatility: float, lower_barrier: float, upper_barrier: float, num_observations: int, rebate: float = 0.0):
        """
        Constructor for KIKOOption class.

        :param spot_price: Current price of the underlying asset
        :param risk_free_rate: Risk-free interest rate
        :param maturity: Time to maturity in years
        :param strike_price: Strike price of the option
        :param volatility: Volatility of the underlying asset
        :param lower_barrier: Lower barrier level
        :param upper_barrier: Upper barrier level
        :param num_observations: Number of observations for averaging
        :param rebate: Rebate amount if the option is knocked out
        """
        super().__init__(spot_price, risk_free_rate, maturity, strike_price, volatility)
        self.lower_barrier = lower_barrier
        self.upper_barrier = upper_barrier
        self.num_observations = num_observations
        self.rebate = rebate

    def price(self, num_paths=1000, seed=1000):
        """
        Calculate the price of the KIKO option using Monte Carlo simulation.

        :return: Price of the KIKO option
        """
        dt = self.maturity / self.num_observations
        np.random.seed(seed)
        values = []

        # 1. Create QMC sequence
        sequencer = qmc.Sobol(d=self.num_observations, seed=seed)
        U = sequencer.random(n=num_paths)
        Z = norm.ppf(U)  # Standard normalize samples

        # 2. Construct stock log-returns
        drift = (self.risk_free_rate - 0.5 * self.volatility ** 2) * dt
        diffusion = self.volatility * math.sqrt(dt) * Z
        log_returns = drift + diffusion
        cum_log_returns = np.cumsum(log_returns, axis=1)

        # 3. Generate paths
        stock_paths = self.spot_price * np.exp(cum_log_returns)

        for path in stock_paths:
            price_max = np.max(path)
            price_min = np.min(path)

            if price_max >= self.upper_barrier:
                # When knockout happens, calculate the rebate
                knockout_index = np.argmax(path >= self.upper_barrier)
                discount_factor = math.exp(-self.risk_free_rate * dt * knockout_index)
                values.append(self.rebate * discount_factor)
            elif price_min <= self.lower_barrier:
                # When knockin happens, calculate the payoff
                final_price = path[-1]
                payoff = max(self.strike_price - final_price, 0)
                values.append(math.exp(-self.risk_free_rate * self.maturity) * payoff)
            else:
                # No knockin or knockout, the payoff is zero
                values.append(0)

        # Calculate the mean and confidence interval
        values = np.array(values)
        price = np.mean(values)
        std_dev = np.std(values)
        conf_low = price - 1.96 * std_dev / math.sqrt(num_paths)
        conf_high = price + 1.96 * std_dev / math.sqrt(num_paths)

        return price, conf_low, conf_high

    def calculate_delta(self, epsilon=1e-2, num_paths=1000, seed=1000):
        # Use two slightly different spot prices to estimate the price
        original_spot = self.spot_price

        # S + ε
        self.spot_price = original_spot + epsilon
        price_plus, _, _ = self.price(num_paths=num_paths, seed=seed)

        # S - ε
        self.spot_price = original_spot - epsilon
        price_minus, _, _ = self.price(num_paths=num_paths, seed=seed)

        # Restore the original spot price
        self.spot_price = original_spot

        # Use the central difference formula to estimate Delta
        delta = (price_plus - price_minus) / (2 * epsilon)
        return delta

# Example usage
if __name__ == "__main__":
    option = KIKOOption(
    spot_price=100,
    risk_free_rate=0.05,
    maturity=2.0,
    strike_price=100,
    volatility=0.2,
    lower_barrier=80,
    upper_barrier=125,
    num_observations=24,
    rebate=1.5
)

price, low, high = option.price()
delta = option.calculate_delta()

print(f"KIKO Option Price: {price:.4f}, 95% CI: [{low:.4f}, {high:.4f}]")
print(f"Delta: {delta:.4f}")
