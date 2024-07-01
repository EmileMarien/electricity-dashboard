total_solar_panel_cost= 0
initial_cash_flow = 400
installation_cost = total_solar_panel_cost*0.3/0.35
BOS_cost = total_solar_panel_cost/0.35*0.125
discount_rate = 0.0682
capex = 7000 + (BOS_cost + installation_cost + total_solar_panel_cost)*(1+0.21)    # multiplication for installation_cost + maintenance_cost
annual_degradation = 0
investment_cost = capex
print("Investment cost:", investment_cost)
Year_1_payback = initial_cash_flow/investment_cost
print("Year 1 payback:", Year_1_payback)
cost_savings = sum((initial_cash_flow * pow(1 - annual_degradation, t - 1)) / pow(1 + discount_rate, t) for t in range(1, 26))
print("Total cost savings:", cost_savings)
npv = -investment_cost + cost_savings
print(npv)


