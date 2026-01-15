import numpy as np


class ProblemInstance:
    def __init__(self, main_depot, mobile_depots, customers):
        self.main_depot = main_depot
        self.mobile_depots = mobile_depots
        self.customers = customers
        self.num_mobile = len(mobile_depots)
        self.num_customers = len(customers)


def generate_data(seed=42):
    """
    Generates a fixed baseline dataset:
    - 1 Main Depot at (0,0)
    - 4 Mobile Depots in range [10, 30]
    - 20 Customers in range [30, 80]
    """
    np.random.seed(seed)

    # Main Depot
    main_depot = np.array([0, 0])

    # 4 Mobile Depots (Potential Locations)
    # Spread them out a bit to make the choice interesting
    mobile_depots = np.random.uniform(10, 30, size=(4, 2))

    # 20 Customers
    customers = np.random.uniform(30, 80, size=(20, 2))

    return ProblemInstance(main_depot, mobile_depots, customers)
