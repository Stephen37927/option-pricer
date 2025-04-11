from .option import Option

class AmericanOption(Option):

    def __init__(self, spot_price: float, risk_free_rate: float, maturity: float, strike_price: float, num_steps: int, option_type: str = 'call'):
        """
        Constructor for AmericanOption class.

        :param spot_price: Current price of the underlying asset
        :param risk_free_rate: Risk-free interest rate
        :param maturity: Time to maturity in years
        :param strike_price: Strike price of the option
        :param num_steps: Number of steps in the binomial tree
        :param option_type: Type of the option ('call' or 'put')
        """
        super().__init__(spot_price, risk_free_rate, maturity, strike_price)
        self.num_steps = num_steps
        self.option_type = option_type

    def price(self):
        """
        Calculate the price of the American option using the binomial tree method.

        :return: Price of the American option
        """
        # Implementation of the binomial tree method for American option pricing
        pass