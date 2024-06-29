
def capacity_tariff(self, tariff:int=41.3087):
    """
    Calculates the capacity tariff cost for the full period which is depending on the highest consumption for each month
    """
    highest_periods = []
    for month in range(1, 13):
        grouped_data = self.pd["GridFlow"][self.pd["GridFlow"].index.month == month].resample('15min').sum() / 60
        highest_period = grouped_data.max()
        highest_periods.append(highest_period)
    print(highest_periods)
    Capacity_cost = max((sum(highest_periods) / 12), 2.5) * tariff
    return Capacity_cost
