from common.runner import ExperimentRunner


def main():
    runner = ExperimentRunner(output_base="batch_results")

    # Define the suite of experiments for the paper
    experiments = [
        # Baseline
        {"scenario": 0, "run_name": "01_Baseline_Fixed", "seed": 42},
        # Scenario 1: Dynamic Single Depot
        {
            "scenario": 1,
            "locator": "centroid",
            "run_name": "02_Scen1_Centroid",
            "seed": 42,
        },
        {
            "scenario": 1,
            "locator": "p-median",
            "run_name": "03_Scen1_PMedian",
            "seed": 42,
        },
        # Scenario 3: LRP with Mixed Fleet
        {
            "scenario": 3,
            "locator": "p-median",
            "candidates": 4,
            "fleet_mode": "mix_1",
            "run_name": "04_Scen3_LRP_Mix1",
            "seed": 42,
        },
    ]

    print(f"Running batch of {len(experiments)} experiments...")

    results = []
    for config in experiments:
        print(f"\n--- Starting {config['run_name']} ---")
        metrics = runner.run_experiment(config)
        results.append(metrics)

    # Validation / Comparison Report
    print("\n" + "=" * 30)
    print("BATCH SUMMARY")
    print("=" * 30)
    for res in results:
        cfg = res["config"]
        status = "SOLVED" if res["solved"] else "FAILED"
        print(f"{cfg['run_name']}: {status}")
        if res["solved"]:
            print(f"  Obj Used: {res.get('obj_val', 0):.2f}")
            print(f"  Truck Dist: {res.get('truck_dist', 0):.2f}")
            print(f"  Sec Cost: {res.get('sec_cost', 0):.2f}")


if __name__ == "__main__":
    main()
