class RiskManagement:
    def __init__(self, initial_capital, risk_percentage):
        self.initial_capital = initial_capital
        self.risk_percentage = risk_percentage

    def calculate_position_size(self, stop_loss_pips):
        risk_amount = self.initial_capital * (self.risk_percentage / 100)
        position_size = risk_amount / stop_loss_pips
        return position_size