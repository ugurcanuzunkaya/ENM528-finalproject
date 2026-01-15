import numpy as np
import gurobipy as gp
from gurobipy import GRB


class Locator:
    def find_depots(self, instance, n_candidates=1):
        """
        Returns a list of coordinate arrays [x, y].
        :param n_candidates: Number of candidates to select/return.
        """
        raise NotImplementedError


class FixedCandidateLocator(Locator):
    """Scenario 0/3: Returns the fixed mobile depots from the instance."""

    def find_depots(self, instance, n_candidates=None):
        # Always return all fixed candidates (4)
        # The Router will decide which ones to OPEN.
        return instance.mobile_depots


class CentroidLocator(Locator):
    """Scenario 1 (Continuous): Finds Center of Mass."""

    def find_depots(self, instance, n_candidates=1):
        if n_candidates > 1:
            # Could implement K-Means here for N > 1
            # For now warning and just returning centroid
            print(
                "Warning: CentroidLocator only supports 1 candidate (Center of Mass)."
            )

        centroid = np.mean(instance.customers, axis=0)
        return np.array([centroid])


class PMedianLocator(Locator):
    """
    Scenario 1 (Discrete P=1) or Scenario 3 (Discrete P=N).
    Selects P node(s) from Customers to serve as Hubs.
    """

    def find_depots(self, instance, n_candidates=1):
        m = gp.Model("PMedian_Locator")
        m.setParam("OutputFlag", 0)

        candidates = instance.customers
        customers = instance.customers
        main = instance.main_depot

        num_cand = len(candidates)
        num_cust = len(customers)

        # Distance Matrices
        d_cand_cust = np.zeros((num_cand, num_cust))
        for i in range(num_cand):
            for j in range(num_cust):
                d_cand_cust[i, j] = np.linalg.norm(candidates[i] - customers[j])

        d_main_cand = np.linalg.norm(candidates - main, axis=1)

        # Vars
        y = m.addVars(num_cand, vtype=GRB.BINARY, name="y")  # Select candidate
        x = m.addVars(
            num_cand, num_cust, vtype=GRB.BINARY, name="x"
        )  # Assign cust to cand

        # Constraints
        # Select Exactly N
        m.addConstr(y.sum() == n_candidates, "SelectN")

        # Assign all customers
        for j in range(num_cust):
            m.addConstr(x.sum("*", j) == 1, f"Assign_{j}")

        # Link
        for i in range(num_cand):
            for j in range(num_cust):
                m.addConstr(x[i, j] <= y[i])

        # Objective
        # Minimal weighted distance
        truck_cost = gp.quicksum(d_main_cand[i] * y[i] for i in range(num_cand))
        dlv_cost = gp.quicksum(
            d_cand_cust[i, j] * x[i, j]
            for i in range(num_cand)
            for j in range(num_cust)
        )

        m.setObjective(truck_cost + dlv_cost, GRB.MINIMIZE)
        m.optimize()

        if m.Status == GRB.OPTIMAL:
            selected_indices = []
            for i in range(num_cand):
                if y[i].X > 0.5:
                    selected_indices.append(i)
            return candidates[selected_indices]
        else:
            # Fallback
            return np.array([np.mean(customers, axis=0)])
