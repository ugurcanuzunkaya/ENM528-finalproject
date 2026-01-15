import itertools
from common.runner import ExperimentRunner


def main():
    runner = ExperimentRunner(output_base="comprehensive_results")

    experiments = []

    # ---------------------------------------------------------
    # Scenario 0: Baseline (Fixed Locations, Homog Fleet)
    # ---------------------------------------------------------
    experiments.append(
        {
            "scenario": 0,
            "locator": "fixed",
            "fleet_mode": "homog",
            "loop_type": "closed",
            "run_name": "S0_Baseline_Fixed_Homog",
        }
    )

    # ---------------------------------------------------------
    # Scenario 1: Dynamic Single Depot (Centroid/P-Median, Homog Fleet)
    # ---------------------------------------------------------
    for loc in ["centroid", "p-median"]:
        experiments.append(
            {
                "scenario": 1,
                "locator": loc,
                "fleet_mode": "homog",
                "loop_type": "closed",
                "run_name": f"S1_Dynamic_{loc}_Homog",
            }
        )

    # ---------------------------------------------------------
    # Scenario 2: Parametric Single Depot (All Combinations)
    # ---------------------------------------------------------
    # Locators x Fleets x LoopTypes
    s2_locators = ["centroid", "p-median"]
    s2_fleets = ["homog", "mix_1", "mix_2"]
    s2_loops = ["closed", "open"]

    for loc, fleet, loop in itertools.product(s2_locators, s2_fleets, s2_loops):
        experiments.append(
            {
                "scenario": 2,
                "locator": loc,
                "fleet_mode": fleet,
                "loop_type": loop,
                "run_name": f"S2_{loc}_{fleet}_{loop}",
            }
        )

    # ---------------------------------------------------------
    # Scenario 3: 2-Echelon LRP
    # ---------------------------------------------------------
    # Locator: Usually P-Median for Multi-Candidate selection.
    # Note: Centroid only returns 1 candidate, so it degrades to Single Depot if n_candidates=1.
    # We will run P-Median with C=4.

    s3_fleets = ["homog", "mix_1", "mix_2"]
    # Loop type is forced to Closed in main.py for Scen 3 currently.

    for fleet in s3_fleets:
        experiments.append(
            {
                "scenario": 3,
                "locator": "p-median",
                "candidates": 4,
                "fleet_mode": fleet,
                "loop_type": "closed",
                "run_name": f"S3_LRP_PMedian_C4_{fleet}",
            }
        )

    print(f"Total Experiments Defined: {len(experiments)}")

    # Execution Loop
    results = []
    for i, config in enumerate(experiments):
        config["seed"] = 42  # Consistent seed for comparison
        print(f"\n[{i + 1}/{len(experiments)}] Running {config['run_name']}...")

        try:
            metrics = runner.run_experiment(config)
            results.append(metrics)
        except Exception as e:
            print(f"Error running {config['run_name']}: {e}")
            results.append({"config": config, "solved": False, "error": str(e)})

    # ---------------------------------------------------------
    # Report Generation
    # ---------------------------------------------------------
    print("\n" + "=" * 50)
    print("COMPREHENSIVE RUN SUMMARY")
    print("=" * 50)
    print(
        f"{'Run Name':<35} | {'Status':<8} | {'Obj (Dist+Cost)':<15} | {'Truck':<10} | {'Sec Cost':<10}"
    )
    print("-" * 90)

    for res in results:
        cfg = res.get("config", {})
        name = cfg.get("run_name", "Unknown")
        status = "SOLVED" if res.get("solved") else "FAILED"
        if res.get("solved"):
            obj = res.get("obj_val", 0)
            truck = res.get("truck_dist", 0)
            sec = res.get("sec_cost", 0)
            print(
                f"{name:<35} | {status:<8} | {obj:<15.2f} | {truck:<10.2f} | {sec:<10.2f}"
            )
        else:
            print(f"{name:<35} | {status:<8} | {'-':<15} | {'-':<10} | {'-':<10}")

    # Save CSV Summary
    import csv

    with open("comprehensive_results/summary_table.csv", "w", newline="") as csvfile:
        fieldnames = [
            "scenario",
            "run_name",
            "locator",
            "fleet",
            "loop",
            "solved",
            "obj_total",
            "truck_dist",
            "sec_cost",
            "time_s",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for res in results:
            cfg = res.get("config", {})
            row = {
                "scenario": cfg.get("scenario"),
                "run_name": cfg.get("run_name"),
                "locator": cfg.get("locator"),
                "fleet": cfg.get("fleet_mode"),
                "loop": cfg.get("loop_type"),
                "solved": res.get("solved", False),
                "obj_total": f"{res.get('obj_val', 0):.2f}"
                if res.get("solved")
                else "",
                "truck_dist": f"{res.get('truck_dist', 0):.2f}"
                if res.get("solved")
                else "",
                "sec_cost": f"{res.get('sec_cost', 0):.2f}"
                if res.get("solved")
                else "",
                "time_s": f"{res.get('elapsed_time', 0):.2f}",
            }
            writer.writerow(row)

    print("\nSummary saved to comprehensive_results/summary_table.csv")


if __name__ == "__main__":
    main()
