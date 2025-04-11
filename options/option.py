class Option:
    
    # Constructor: spot_price(float), risk_free_rate(float), maturity(float), strike_price(float)
    def __init__(self, spot_price: float, risk_free_rate: float, maturity: float, strike_price: float, volatility: float = 0.0):
        self.spot_price = spot_price
        self.risk_free_rate = risk_free_rate
        self.maturity = maturity
        self.strike_price = strike_price
        self.volatility = volatility

    def price(self) -> float:
        """
        This method should be overridden by subclasses.
        """
        raise NotImplementedError("This method should be overridden by subclasses.")