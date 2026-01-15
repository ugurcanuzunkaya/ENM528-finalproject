import numpy as np


class ProblemInstance:
    def __init__(self, main_depot, mobile_depots, customers):
        self.main_depot = main_depot
        self.mobile_depots = mobile_depots
        self.customers = customers
        self.num_mobile = len(mobile_depots)
        self.num_customers = len(customers)


def generate_clustered_data(seed=42, n_customers=20, n_depots=4):
    """
    Generates clustered data to simulate more realistic scenarios.
    Uses a few centers and scatters customers around them.
    """
    np.random.seed(seed)

    # Main Depot at (0,0)
    main_depot = np.array([0, 0])

    # Generate Cluster Centers for Customers
    # Say we have 3 main clusters for 20 customers
    n_clusters = 3
    cluster_centers = np.random.uniform(20, 70, size=(n_clusters, 2))

    customers = []
    points_per_cluster = n_customers // n_clusters

    for i in range(n_clusters):
        # Scatter points around center
        # Standard deviation 5.0
        n_points = (
            points_per_cluster if i < n_clusters - 1 else n_customers - len(customers)
        )
        points = cluster_centers[i] + np.random.normal(0, 5, size=(n_points, 2))
        customers.extend(points)

    customers = np.array(customers)

    # Generate Mobile Depots
    # Maybe place them somewhat between main depot and clusters, or random
    # Let's keep them somewhat random but in distinct areas
    mobile_depots = np.random.uniform(10, 50, size=(n_depots, 2))

    return ProblemInstance(main_depot, mobile_depots, customers)


def load_solomon_data(file_path, n_customers=None, n_depots=4, seed=42):
    """
    Parses a Solomon format file (e.g., c101.txt).
    Extracts Main Depot and Customers.
    Generates synthetic Mobile Depots bounds of customers.
    """
    customers = []
    main_depot = None

    with open(file_path, "r") as f:
        lines = f.readlines()

    # Find CUSTOMER section
    start_parsing = False
    for line in lines:
        if "CUSTOMER" in line:
            start_parsing = False  # Next line is headers
            continue
        if "CUST NO." in line:
            start_parsing = True
            continue

        if start_parsing:
            parts = line.strip().split()
            if not parts:
                continue

            # CUST NO.  XCOORD.   YCOORD. ...
            cust_id = int(parts[0])
            x = float(parts[1])
            y = float(parts[2])
            # demand = float(parts[3]) # Unused for now

            if cust_id == 0:
                main_depot = np.array([x, y])
            else:
                customers.append([x, y])

    if n_customers:
        customers = customers[:n_customers]

    customers = np.array(customers)

    if main_depot is None:
        raise ValueError("Could not find depot (Cust No 0) in file")

    # Generate synthetic mobile depots within customer bounds
    np.random.seed(seed)
    min_x, min_y = customers.min(axis=0)
    max_x, max_y = customers.max(axis=0)

    mobile_depots = np.random.uniform(
        low=[min_x, min_y], high=[max_x, max_y], size=(n_depots, 2)
    )

    return ProblemInstance(main_depot, mobile_depots, customers)


def generate_data(seed=42, mode="uniform", file_path=None):
    """
    Generates dataset based on mode.
    Modes:
    - 'uniform': Original random uniform
    - 'clustered': Clustered customer distribution
    - 'solomon': Load from Solomon file
    """
    if mode == "solomon":
        if not file_path:
            raise ValueError("file_path is required for 'solomon' mode")
        # Defaulting to 25 customers for quick plotting if not specified?
        # The user said "first 20 customers" in previous turn.
        # Let's default to 20 for speed/viz unless full
        return load_solomon_data(file_path, n_customers=20, seed=seed)

    if mode == "clustered":
        return generate_clustered_data(seed=seed)

    # Default / Uniform
    np.random.seed(seed)

    # Main Depot
    main_depot = np.array([0, 0])

    # 4 Mobile Depots (Potential Locations)
    # Spread them out a bit to make the choice interesting
    mobile_depots = np.random.uniform(10, 30, size=(4, 2))

    # 20 Customers
    customers = np.random.uniform(30, 80, size=(20, 2))

    return ProblemInstance(main_depot, mobile_depots, customers)
