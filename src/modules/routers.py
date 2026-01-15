import gurobipy as gp
from gurobipy import GRB
import numpy as np


class VRPRouter:
    def __init__(self, instance, potential_depots, fleet):
        """
        :param instance: ProblemInstance (customers, main_depot)
        :param potential_depots: List/Array of [x,y] coordinates for candidate depots.
        :param fleet: List of VehicleType objects
        """
        self.instance = instance
        self.potential_depots = potential_depots
        self.fleet = fleet
        self.num_veh = len(fleet)

    def solve(self, open_loop=False):
        m = gp.Model("VRP_Router")
        # m.setParam("TimeLimit", 18000)

        # ---------------------------
        # 1. Graph Construction
        # ---------------------------
        D = self.potential_depots
        C = self.instance.customers
        Main = self.instance.main_depot

        num_depots = len(D)
        num_customers = len(C)

        D_nodes = list(range(num_depots))
        C_nodes = list(range(num_depots, num_depots + num_customers))
        All_nodes = D_nodes + C_nodes

        coords = {}
        for i in range(num_depots):
            coords[i] = D[i]
        for i in range(num_customers):
            coords[num_depots + i] = C[i]

        # Distance Matrix
        # If Open Loop: Cost(Customer -> Depot) = 0
        dist = np.zeros((len(All_nodes), len(All_nodes)))
        for i in All_nodes:
            for j in All_nodes:
                cost = np.linalg.norm(coords[i] - coords[j])

                # OPEN LOOP LOGIC:
                # If i is customer and j is depot, cost = 0
                if open_loop and i in C_nodes and j in D_nodes:
                    cost = 0.0

                dist[i, j] = cost

        dist_main_to_D = np.linalg.norm(D - Main, axis=1)

        # ---------------------------
        # 2. Variables
        # ---------------------------
        z = m.addVars(D_nodes, vtype=GRB.BINARY, name="z")
        vehicles = list(range(self.num_veh))

        arcs = []
        for i in All_nodes:
            for j in All_nodes:
                if i == j:
                    continue
                if i in D_nodes and j in D_nodes:
                    continue
                arcs.append((i, j))

        x = m.addVars(arcs, vehicles, vtype=GRB.BINARY, name="x")
        u = m.addVars(
            C_nodes,
            vehicles,
            vtype=GRB.CONTINUOUS,
            lb=0,
            ub=num_customers + 100,
            name="u",
        )  # Load variable
        W = m.addVar(vtype=GRB.CONTINUOUS, name="MaxDist")

        # ---------------------------
        # 3. Constraints
        # ---------------------------
        m.addConstr(z.sum() == 1, "OneDepot")

        for k in vehicles:
            cap = self.fleet[k].capacity

            # Flow
            for h in C_nodes:
                flow_in = gp.quicksum(x[i, h, k] for i in All_nodes if (i, h) in arcs)
                flow_out = gp.quicksum(x[h, j, k] for j in All_nodes if (h, j) in arcs)
                m.addConstr(flow_in == flow_out, f"Flow_{h}_{k}")

            # Depot Boundaries
            for d in D_nodes:
                outflow = gp.quicksum(x[d, j, k] for j in C_nodes if (d, j) in arcs)
                inflow = gp.quicksum(x[i, d, k] for i in C_nodes if (i, d) in arcs)
                m.addConstr(outflow <= z[d])
                m.addConstr(inflow <= z[d])
                m.addConstr(
                    outflow == inflow
                )  # Always conserve flow even in Open Loop (virtual return)

            # Global limit
            m.addConstr(
                gp.quicksum(
                    x[d, j, k] for d in D_nodes for j in C_nodes if (d, j) in arcs
                )
                <= 1
            )

        # Assignments
        for j in C_nodes:
            m.addConstr(
                gp.quicksum(
                    x[i, j, k] for k in vehicles for i in All_nodes if (i, j) in arcs
                )
                == 1
            )

        # Capacity & MTZ (Combined logic)
        # u[j,k] = Load on vehicle k AFTER visiting node j
        # Assuming demand = 1 per customer for now (User didn't specify load, but implied 'capacity' matters)
        # Let's use demand=1 per customer for generic capacity or generate random
        # Wait, previous plan mentioned 30kg. Let's assume random loads or fixed 10kg in data gen?
        # Demand Assumption
        # Total Vehicles: Mix 1 (40+30+10+10 = 90)
        # 20 Customers. If demand=5 => Total=100 > 90 (Infeasible).
        # Let's set demand = 1 for now (Total=20) to ensure feasibility.
        DEMAND = 1

        M_cap = max(v.capacity for v in self.fleet) + 100

        for k in vehicles:
            cap = self.fleet[k].capacity
            for i in C_nodes:
                # Capacity Constraint
                m.addConstr(u[i, k] <= cap, f"Cap_{i}_{k}")
                m.addConstr(
                    u[i, k]
                    >= DEMAND
                    * gp.quicksum(
                        x[pre, i, k] for pre in All_nodes if (pre, i) in arcs
                    ),
                    f"MinLoad_{i}_{k}",
                )

                for j in C_nodes:
                    if i != j:
                        # If x[i,j,k]=1 => u[j] >= u[i] + dem
                        m.addConstr(
                            u[j, k] >= u[i, k] + DEMAND - M_cap * (1 - x[i, j, k]),
                            f"LoadProp_{k}_{i}_{j}",
                        )

        # ---------------------------
        # 4. Objective
        # ---------------------------
        veh_dist_vars = []
        for k in vehicles:
            # Cost Factor included? "cost_factor"
            # Objective says Minimize Total Distance.
            # But maybe Minimize Cost?
            # "optimize their route and cargo"
            # Let's keep Minimizing Distance for consistency, but multiply by cost_factor for the "Efficiency" term

            d_k = gp.quicksum(dist[i, j] * x[i, j, k] for i, j in arcs)
            m.addConstr(W >= d_k, f"MaxDist_{k}")
            veh_dist_vars.append(d_k * self.fleet[k].cost_factor)

        truck_dist = gp.quicksum(z[d] * dist_main_to_D[d] for d in D_nodes)
        sum_sec_cost = gp.quicksum(veh_dist_vars)

        obj = 1.0 * W + 0.001 * (truck_dist + sum_sec_cost)
        m.setObjective(obj, GRB.MINIMIZE)

        m.optimize()

        # ---------------------------
        # 5. Result
        # ---------------------------
        if (
            m.Status in [GRB.OPTIMAL, GRB.TIME_LIMIT, GRB.INTERRUPTED]
            and m.SolCount > 0
        ):
            selected_idx = -1
            for d in D_nodes:
                if z[d].X > 0.5:
                    selected_idx = d
                    break

            sol_assignments = {}
            sol_veh_dists = {}

            for k in vehicles:
                active_arcs = []
                for i, j in arcs:
                    if x[i, j, k].X > 0.5:
                        active_arcs.append((i, j))

                if not active_arcs:
                    sol_assignments[k] = []
                    sol_veh_dists[k] = 0.0
                    continue

                path = []
                curr = selected_idx
                # Trace path
                for _ in range(len(active_arcs) + 5):
                    next_n = None
                    for u, v in active_arcs:
                        if u == curr:
                            next_n = v
                            break
                    if next_n is None:
                        break
                    if next_n in D_nodes:
                        break  # End of loop

                    path.append(next_n - num_depots)
                    curr = next_n

                sol_assignments[k] = path

                d_val = 0
                for u, v in active_arcs:
                    d_val += dist[u, v]
                sol_veh_dists[k] = d_val

            return {
                "selected_depot_idx": selected_idx,
                "selected_depot_loc": D[selected_idx],
                "all_potential_depots": D,
                "truck_dist": dist_main_to_D[selected_idx],
                "assignments": sol_assignments,
                "veh_dists": sol_veh_dists,
                "max_dist": W.X,
                "total_sec_cost": sum(sol_veh_dists.values()),
                "open_loop": open_loop,
                "solver_stats": {
                    "status": m.Status,
                    "mip_gap": m.MIPGap if m.IsMIP else 0.0,
                    "runtime": m.Runtime,
                },
            }
        else:
            return None


class TwoEchelonRouter:
    def __init__(self, instance, potential_depots, fleet):
        """
        :param instance: ProblemInstance (customers, main_depot)
        :param potential_depots: List/Array of Candidate Locations
        :param fleet: List of VehicleType objects (This fleet is available AT EACH DEPOT)
        """
        self.instance = instance
        self.potential_depots = potential_depots
        # Fleet is duplicated per potential depot!
        # If 4 depots and fleet size 4, total secondary vehicles = 16.
        self.fleet_template = fleet
        self.num_sec_per_depot = len(fleet)
        self.num_candidates = len(potential_depots)

    def solve(self, open_loop=False):
        m = gp.Model("2E_LRP_Router")
        # m.setParam("TimeLimit", 18000)

        D = self.potential_depots
        C = self.instance.customers
        Main = self.instance.main_depot

        num_depots = len(D)
        num_customers = len(C)

        # Nodes Mapping
        # 0..N-1: Depots
        # N..N+M-1: Customers

        D_nodes = list(range(num_depots))
        C_nodes = list(range(num_depots, num_depots + num_customers))
        All_nodes = D_nodes + C_nodes

        coords = {}
        for i in range(num_depots):
            coords[i] = D[i]
        for i in range(num_customers):
            coords[num_depots + i] = C[i]

        # 1. Distances (Secondary)
        dist_sec = np.zeros((len(All_nodes), len(All_nodes)))
        for i in All_nodes:
            for j in All_nodes:
                cost = np.linalg.norm(coords[i] - coords[j])
                if open_loop and i in C_nodes and j in D_nodes:
                    cost = 0.0
                dist_sec[i, j] = cost

        # 2. Distances (Truck)
        dist_truck = np.zeros((num_depots + 1, num_depots + 1))
        # Index map: 0..D-1 = Depots, D = Main
        MAIN_IDX = num_depots

        for i in range(num_depots):
            for j in range(num_depots):
                dist_truck[i, j] = np.linalg.norm(D[i] - D[j])
            # Main links
            d_m = np.linalg.norm(D[i] - Main)
            dist_truck[i, MAIN_IDX] = d_m
            dist_truck[MAIN_IDX, i] = d_m

        # ---------------------------
        # Variables
        # ---------------------------

        z = m.addVars(D_nodes, vtype=GRB.BINARY, name="z")

        # Truck Routing (TSP on Main + Open Depots)
        # y[i,j] where nodes are D_nodes + MAIN_IDX
        truck_nodes = D_nodes + [MAIN_IDX]
        truck_arcs = [(i, j) for i in truck_nodes for j in truck_nodes if i != j]
        y = m.addVars(truck_arcs, vtype=GRB.BINARY, name="y")

        u_truck = m.addVars(
            truck_nodes, vtype=GRB.CONTINUOUS, lb=0, ub=len(truck_nodes), name="u_truck"
        )

        # Secondary Routing
        sec_vehs = list(range(self.num_sec_per_depot))
        sec_arcs = []
        for i in All_nodes:
            for j in All_nodes:
                if i == j:
                    continue
                # Block Depot-Depot for secondary
                if i in D_nodes and j in D_nodes:
                    continue
                sec_arcs.append((i, j))

        # x[depot, vehicle, from, to]
        x = m.addVars(D_nodes, sec_vehs, sec_arcs, vtype=GRB.BINARY, name="x")

        # ---------------------------
        # Constraints
        # ---------------------------

        # A. At least 1 depot
        m.addConstr(z.sum() >= 1, "AtLeastOneDepot")

        # B. Truck Routing Flow
        for d in D_nodes:
            # If z[d]=1, must have 1 in, 1 out. If 0, 0.
            m.addConstr(
                gp.quicksum(y[i, d] for i in truck_nodes if (i, d) in truck_arcs)
                == z[d]
            )
            m.addConstr(
                gp.quicksum(y[d, j] for j in truck_nodes if (d, j) in truck_arcs)
                == z[d]
            )

        # Main Flow (Always 1)
        m.addConstr(
            gp.quicksum(
                y[i, MAIN_IDX] for i in truck_nodes if (i, MAIN_IDX) in truck_arcs
            )
            == 1
        )
        m.addConstr(
            gp.quicksum(
                y[MAIN_IDX, j] for j in truck_nodes if (MAIN_IDX, j) in truck_arcs
            )
            == 1
        )

        # Truck MTZ
        m.addConstr(u_truck[MAIN_IDX] == 0)
        for i in D_nodes:
            for j in D_nodes:
                if i != j:
                    m.addConstr(
                        u_truck[j] >= u_truck[i] + 1 - len(truck_nodes) * (1 - y[i, j])
                    )

        # C. Secondary Routing
        for d in D_nodes:
            for k in sec_vehs:
                outflow = gp.quicksum(
                    x[d, k, d, j] for j in C_nodes if (d, j) in sec_arcs
                )
                inflow = gp.quicksum(
                    x[d, k, i, d] for i in C_nodes if (i, d) in sec_arcs
                )

                m.addConstr(outflow <= z[d])
                m.addConstr(inflow <= z[d])
                m.addConstr(outflow == inflow)

                for h in C_nodes:
                    f_in = gp.quicksum(
                        x[d, k, i, h] for i in All_nodes if (i, h) in sec_arcs
                    )
                    f_out = gp.quicksum(
                        x[d, k, h, j] for j in All_nodes if (h, j) in sec_arcs
                    )
                    m.addConstr(f_in == f_out)

        # D. Assignment
        for h in C_nodes:
            m.addConstr(
                gp.quicksum(
                    x[d, k, i, h]
                    for d in D_nodes
                    for k in sec_vehs
                    for i in All_nodes
                    if (i, h) in sec_arcs
                )
                == 1
            )

        # E. Capacity
        DEMAND = 1
        M_cap = max(v.capacity for v in self.fleet_template) + 100
        u_sec = m.addVars(
            D_nodes,
            sec_vehs,
            C_nodes,
            vtype=GRB.CONTINUOUS,
            lb=0,
            ub=num_customers + 10,
        )

        # F. Fleet-Depot Binding (Fix Ghost Rides)
        for d in D_nodes:
            for k in sec_vehs:
                for p in D_nodes:
                    if p != d:
                        # Ban starting at p
                        for j in All_nodes:
                            if (p, j) in sec_arcs:
                                m.addConstr(x[d, k, p, j] == 0)
                        # Ban ending at p
                        for i in All_nodes:
                            if (i, p) in sec_arcs:
                                m.addConstr(x[d, k, i, p] == 0)

        for d in D_nodes:
            for k in sec_vehs:
                cap = self.fleet_template[k].capacity
                for i in C_nodes:
                    m.addConstr(u_sec[d, k, i] <= cap)
                    m.addConstr(u_sec[d, k, i] >= DEMAND)

                    for j in C_nodes:
                        if i != j:
                            m.addConstr(
                                u_sec[d, k, j]
                                >= u_sec[d, k, i] + DEMAND - M_cap * (1 - x[d, k, i, j])
                            )

        # ---------------------------
        # Objective
        # ---------------------------
        truck_cost = gp.quicksum(dist_truck[i, j] * y[i, j] for i, j in truck_arcs)

        sec_cost_vars = []
        for d in D_nodes:
            for k in sec_vehs:
                cost_k = gp.quicksum(
                    dist_sec[i, j] * x[d, k, i, j] for i, j in sec_arcs
                )
                sec_cost_vars.append(cost_k * self.fleet_template[k].cost_factor)

        total_sec_cost = gp.quicksum(sec_cost_vars)

        m.setObjective(truck_cost + total_sec_cost, GRB.MINIMIZE)
        m.optimize()

        if (
            m.Status in [GRB.OPTIMAL, GRB.TIME_LIMIT, GRB.INTERRUPTED]
            and m.SolCount > 0
        ):
            open_depots = [d for d in D_nodes if z[d].X > 0.5]

            # Truck Route
            # Truck Route Assignment

            # Simple extraction for now
            # Since it might visit multiple, just list them or try to trace
            # Careful with loops or time limit

            # Let's just collect edges
            truck_edges = []
            for i, j in truck_arcs:
                if y[i, j].X > 0.5:
                    truck_edges.append((i, j))

            sec_assignments = {}
            for d in open_depots:
                sec_assignments[d] = {}
                for k in sec_vehs:
                    path = []
                    curr_node = d
                    # Trace
                    visited = set()
                    while True:
                        next_n = None
                        for target in All_nodes:
                            if (curr_node, target) in sec_arcs and x[
                                d, k, curr_node, target
                            ].X > 0.5:
                                next_n = target
                                break
                        if next_n is None:
                            break
                        if next_n in D_nodes:
                            break
                        if next_n in visited:
                            break  # Loop guard
                        visited.add(next_n)

                        path.append(next_n - num_depots)
                        curr_node = next_n

                    if path:
                        sec_assignments[d][k] = path

            return {
                "open_depots": open_depots,
                "open_depot_locs": [D[d] for d in open_depots],
                "truck_edges": truck_edges,
                "truck_dist": truck_cost.getValue(),
                "sec_assignments": sec_assignments,
                "max_dist": 0.0,
                "total_sec_cost": total_sec_cost.getValue(),
                "solver_stats": {
                    "status": m.Status,
                    "mip_gap": m.MIPGap if m.IsMIP else 0.0,
                    "runtime": m.Runtime,
                },
            }
        return None
