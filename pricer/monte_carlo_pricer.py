class MonteCarloPricer:

    def __init__(self):
        """
        Constructor for MonteCarloPricer class.
        """
        pass

    def price(self, payoff_function, num_paths: int, discount_rate: float, control_variate_function=None):
        """
        Price an option using Monte Carlo simulation.

        :param payoff_function: Function to calculate the payoff of the option for a given set of simulated asset prices.
        :param num_paths: Number of Monte Carlo simulation paths
        :param discount_rate: Discount rate for present value calculation
        :param control_variate_function: Optional control variate function for variance reduction
        :return: Estimated price of the option
        """
        
        # Implementation of Monte Carlo simulation for option pricing

        pass

    def calculate_confidence_interval(self, prices):
        """
        Calculate the 95% confidence interval
        
        :param prices: List of simulated option prices
        :return: Tuple containing the lower and upper bounds of the confidence interval
        """

        