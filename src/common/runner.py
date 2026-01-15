import os
import time
import json
import numpy as np
from common.data_gen import generate_data
from common.plotting import plot_solution
from common.vehicles import create_fleet
from modules.locators import FixedCandidateLocator, PMedianLocator, CentroidLocator
from modules.routers import VRPRouter, TwoEchelonRouter


class ExperimentRunner:
    def __init__(self, output_base="solutions"):
        self.output_base = output_base
        os.makedirs(self.output_base, exist_ok=True)

    def run_experiment(self, config):
        """
        Executes a single experiment based on the provided configuration.
        Returns a dictionary containing the results and metrics.

        Config Keys:
        - scenario (int): 0-3
        - locator (str): 'fixed', 'p-median', 'centroid'
        - candidates (int): Number of candidates (Scen 3/1)
        - fleet_mode (str): 'homog', 'mix_1', 'mix_2'
        - loop_type (str): 'closed', 'open'
        - seed (int): Random seed for data generation
        - run_name (str): Identifier for saving results
        """
        start_time = time.time()

        # 1. Setup Data
        # 1. Setup Data
        seed = config.get("seed", 42)
        data_mode = config.get("data_mode", "uniform")
        data_file = config.get("data_file")
        print(f"Generating data with seed {seed} (Mode: {data_mode})...")
        data = generate_data(seed=seed, mode=data_mode, file_path=data_file)

        # 2. Setup Fleet
        fleet_mode = config.get("fleet_mode", "homog")
        fleet = create_fleet(fleet_mode)

        # 3. Locator Step
        scenario = config.get("scenario", 0)
        locator_type = config.get("locator", "fixed")
        n_candidates = config.get("candidates", 1)

        print(f"Running Locator ({locator_type})...")
        if scenario == 0:
            locator = FixedCandidateLocator()
            # Scenario 0 implies using the fixed ones regardless of logic, usually all 4
            candidates = locator.find_depots(data)
        else:
            if locator_type == "p-median":
                locator = PMedianLocator()
            elif locator_type == "centroid":
                locator = CentroidLocator()
            else:
                # Default fallback or strict fixed?
                locator = FixedCandidateLocator()

            # Logic: If Scen 3, we pick 'candidates' number of best spots
            # If default Fixed, it returns all mobile_depots (4)
            candidates = locator.find_depots(data, n_candidates=n_candidates)

        # 4. Router Step
        loop_type = config.get("loop_type", "closed")
        res = None

        print(f"Running Router (Scenario {scenario})...")
        if scenario == 3:
            router = TwoEchelonRouter(data, candidates, fleet)
            res = router.solve(open_loop=(loop_type == "open"))
            # Note: Scen 3 logic might just ignore open_loop if not implemented, but passing it is safe
        else:
            router = VRPRouter(data, candidates, fleet)
            res = router.solve(open_loop=(scenario == 2 and loop_type == "open"))

        elapsed = time.time() - start_time

        # 5. Save Results
        run_name = config.get("run_name", f"scen_{scenario}_{int(time.time())}")
        output_dir = os.path.join(self.output_base, run_name)
        os.makedirs(output_dir, exist_ok=True)

        metrics = {"config": config, "elapsed_time": elapsed, "solved": False}

        if res:
            metrics["solved"] = True
            metrics["truck_dist"] = res.get("truck_dist", 0.0)
            metrics["sec_cost"] = res.get("total_sec_cost", 0.0)
            metrics["obj_val"] = float(metrics["truck_dist"]) + float(
                metrics["sec_cost"]
            )  # approx

            # Save visual
            plot_path = os.path.join(output_dir, "plot.png")
            plot_solution(data, res, save_path=plot_path)

            # Save raw dict (converting numpy things)
            def np_encoder(o):
                if isinstance(o, np.integer):
                    return int(o)
                if isinstance(o, np.floating):
                    return float(o)
                if isinstance(o, np.ndarray):
                    return o.tolist()
                return str(o)

            with open(os.path.join(output_dir, "result.json"), "w") as f:
                json.dump(res, f, default=np_encoder, indent=2)

            # Summary Text
            def calc_route_dist(route_nodes, start_loc, end_loc, coords):
                if not route_nodes:
                    return 0.0
                d = 0.0
                curr = start_loc
                for c_idx in route_nodes:
                    nxt = coords[c_idx]
                    d += np.linalg.norm(curr - nxt)
                    curr = nxt
                d += np.linalg.norm(curr - end_loc)
                return d

            with open(os.path.join(output_dir, "summary.txt"), "w") as f:
                f.write("=" * 50 + "\n")
                f.write(f"SCENARIO REPORT: {run_name}\n")
                f.write("=" * 50 + "\n\n")

                # 1. Parameters & Config
                f.write("CONFIGURATION:\n")
                f.write(f"  Scenario ID: {scenario}\n")
                f.write(f"  Locator: {config.get('locator')}\n")
                f.write(f"  Fleet Mode: {config.get('fleet_mode')}\n")
                f.write(f"  Loop Type: {config.get('loop_type')}\n")
                f.write(f"  Data Mode: {config.get('data_mode')}\n")
                f.write(f"  Candidates (S3): {config.get('candidates')}\n")
                f.write(f"  Seed: {config.get('seed')}\n\n")

                # 2. Key Metrics
                f.write("SOLUTION METRICS:\n")
                if "solver_stats" in res:
                    stats = res["solver_stats"]
                    mip_gap = stats.get("mip_gap", 0.0)
                    if isinstance(mip_gap, float):
                        f.write(
                            f"  Solver Status: {stats.get('status')} (Gap: {mip_gap * 100:.2f}%)\n"
                        )
                    else:
                        f.write(
                            f"  Solver Status: {stats.get('status')} (Gap: {mip_gap})\n"
                        )
                    f.write(f"  Runtime: {stats.get('runtime', 0):.2f} s\n")

                f.write("  Status: Solved\n")
                f.write(f"  Solve Time: {elapsed:.2f} s\n")
                f.write(f"  Total Objective: {metrics['obj_val']:.4f}\n")
                f.write(f"  Truck Distance: {metrics['truck_dist']:.4f}\n")
                f.write(f"  Total Secondary Cost: {metrics['sec_cost']:.4f}\n\n")

                # Utilization Calculation

                # Helper to sum up capacity
                # We need to access fleet to know capacity.
                # In Scen 3, fleet is per depot. In others, it's global fleet list.

                all_vehicle_loads = []

                # 3. Depot & Routing Details
                f.write("ROUTING DETAILS:\n")

                if scenario == 3:
                    # LRP Logic
                    open_locs = res["open_depot_locs"]
                    open_indices = res["open_depots"]

                    for i, d_idx in enumerate(open_indices):
                        loc = open_locs[i]
                        f.write(
                            f"\n  [Active Depot #{d_idx}] at Location: ({loc[0]:.2f}, {loc[1]:.2f})\n"
                        )

                        # Assignments for this depot
                        depot_assigns = res["sec_assignments"].get(str(d_idx))
                        # JSON integer keys might be strings after dump/load logic in some cases, but here it's direct dict
                        # Check key type (int usually)
                        if not depot_assigns:
                            depot_assigns = res["sec_assignments"].get(d_idx, {})

                        for v_idx, path in depot_assigns.items():
                            veh = fleet[int(v_idx)]
                            f.write(f"    - Vehicle {int(v_idx) + 1} [{veh.name}]:\n")
                            f.write(f"      Assigned Customers ({len(path)}): {path}\n")

                            # Calculate distance if not present
                            dist = calc_route_dist(path, loc, loc, data.customers)

                            # Load / Utilization (Assumes Demand=1)
                            load = len(path) * 1
                            cap = veh.capacity
                            util = (load / cap) * 100 if cap > 0 else 0
                            all_vehicle_loads.append(util)

                            f.write(f"      Traveled Distance: {dist:.2f}\n")
                            f.write(f"      Load: {load}/{cap} ({util:.1f}%)\n")
                else:
                    # Single Depot Logic
                    sel_loc = res["selected_depot_loc"]
                    f.write(
                        f"\n  [Selected Depot] at Location: ({sel_loc[0]:.2f}, {sel_loc[1]:.2f})\n"
                    )

                    assignments = res["assignments"]
                    veh_dists = res.get("veh_dists", {})

                    for v_idx, path in assignments.items():
                        v_idx = int(v_idx)  # ensure int
                        if not path:
                            continue

                        veh = fleet[v_idx]
                        dist = veh_dists.get(str(v_idx)) or veh_dists.get(v_idx)
                        if dist is None:
                            # Calc open/closed based on logic
                            is_open = scenario == 2 and loop_type == "open"
                            end_loc = (
                                sel_loc if not is_open else data.customers[path[-1]]
                            )
                            dist = calc_route_dist(
                                path, sel_loc, end_loc, data.customers
                            )

                        f.write(f"    - Vehicle {v_idx + 1} [{veh.name}]:\n")
                        f.write(f"      Assigned Customers ({len(path)}): {path}\n")
                        f.write(f"      Traveled Distance: {dist:.2f}\n")

                        # Load / Utilization
                        load = len(path) * 1
                        cap = veh.capacity
                        util = (load / cap) * 100 if cap > 0 else 0
                        all_vehicle_loads.append(util)
                        f.write(f"      Load: {load}/{cap} ({util:.1f}%)\n")

                if all_vehicle_loads:
                    avg_util = sum(all_vehicle_loads) / len(all_vehicle_loads)
                    f.write(
                        f"\n  Average Fleet Capacity Utilization: {avg_util:.2f}%\n"
                    )

            print(f"Experiment '{run_name}' completed. Results saved in {output_dir}")
        else:
            print(f"Experiment '{run_name}' failed to find a solution.")

        return metrics
