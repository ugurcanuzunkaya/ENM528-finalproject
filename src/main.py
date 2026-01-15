import argparse
import sys
import os

# Ensure src is in path to find modules if running from deeper dir
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from common.runner import ExperimentRunner


def main():
    parser = argparse.ArgumentParser(description="VRP Model V2 - Modular Scenarios")
    parser.add_argument(
        "--scenario",
        type=int,
        default=0,
        choices=[0, 1, 2, 3],
        help="Scenario ID (0-3)",
    )
    parser.add_argument(
        "--locator",
        type=str,
        default="p-median",
        choices=["fixed", "p-median", "centroid"],
        help="Locator Strategy",
    )
    parser.add_argument(
        "--fleet",
        type=str,
        default="homog",
        choices=["homog", "mix_1", "mix_2"],
        help="Fleet Mix",
    )
    parser.add_argument(
        "--loop-type",
        type=str,
        default="closed",
        choices=["closed", "open"],
        help="Loop Type",
    )
    parser.add_argument(
        "--candidates",
        type=int,
        default=4,
        help="Number of depot candidates for Scenario 3",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random Seed",
    )

    # New arg for batch run description if needed, or just let runner handle

    args = parser.parse_args()

    # Construct Config
    config = {
        "scenario": args.scenario,
        "locator": args.locator,
        "candidates": args.candidates,
        "fleet_mode": args.fleet,
        "loop_type": args.loop_type,
        "seed": args.seed,
        "run_name": f"scen_{args.scenario}_{args.locator}_{args.fleet}",
    }

    # Add timestamp to run_name to avoid overwrites
    import time

    config["run_name"] += f"_{int(time.time())}"

    print(f"Starting Experiment: {config['run_name']}")

    runner = ExperimentRunner(output_base="solutions")
    metrics = runner.run_experiment(config)

    print("\nFinal Metrics:")
    print(metrics)


if __name__ == "__main__":
    main()
