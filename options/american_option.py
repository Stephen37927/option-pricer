from option import Option
import numpy as np
import math

class AmericanOption(Option):

    def __init__(self, spot_price: float, risk_free_rate: float, maturity: float, strike_price: float, volatility: float, num_steps: int, option_type: str = 'call'):
        """
        Constructor for AmericanOption class.

        :param spot_price: Current price of the underlying asset
        :param risk_free_rate: Risk-free interest rate
        :param maturity: Time to maturity in years
        :param strike_price: Strike price of the option
        :param num_steps: Number of steps in the binomial tree
        :param option_type: Type of the option ('call' or 'put')
        """
        super().__init__(spot_price, risk_free_rate, maturity, strike_price, volatility)
        self.num_steps = num_steps
        self.option_type = option_type

    def price(self):
        """
        Calculate the price of the American option using the binomial tree method.

        :return: Price of the American option
        """
        # Implementation of the binomial tree method for American option pricing
        
        S0 = self.spot_price
        K = self.strike_price
        r = self.risk_free_rate
        T = self.maturity
        N = self.num_steps
        option_type = self.option_type
        sigma = self.volatility
        # Calculate parameters for the binomial tree
        dt = T / N  # time step
        u = math.exp(sigma * math.sqrt(dt))  # up factor
        d = 1 / u  # down factor
        p = (math.exp(r * dt) - d) / (u - d)  # risk-neutral probability

        # Initialize asset prices at maturity
        ST = np.zeros(N + 1)
        for j in range(N + 1):
            ST[j] = S0 * (u ** (N - j)) * (d ** j)

        # Initialize option values at maturity
        if option_type == 'call':
            option_values = np.maximum(0, ST - K)
        elif option_type == 'put':
            option_values = np.maximum(0, K - ST)
        else:
            raise ValueError("option_type must be either 'call' or 'put'")

        # Backward induction to calculate option price at t=0
        for i in range(N - 1, -1, -1):
            option_values[:-1] = (p * option_values[:-1] + (1 - p) * option_values[1:]) * math.exp(-r * dt)

        return option_values[0]
    

# Example usage
if __name__ == "__main__":
    S0 = 50  # initial stock price
    K = 70   # strike price
    T = 2     # time to expiration in years
    r = 0.1  # risk-free interest rate
    sigma = 0.4  # volatility of the underlying asset
    N = 200   # number of time steps in the binomial tree
    option_type = 'put'  # 'call' or 'put'

    option_price = AmericanOption(S0, r, T, K, sigma, N, option_type).price()
    print(f"The {option_type} option price is: {option_price:.2f}")

