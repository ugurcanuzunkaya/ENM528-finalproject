import matplotlib.pyplot as plt
import numpy as np
import os


def plot_solution(instance, result, save_path=None):
    """
    Plots the VRP/LRP solution.
    Handles both Single Depot and Multi-Depot (LRP) results.
    """
    plt.figure(figsize=(10, 8))

    # Common: Plot All Customers
    plt.scatter(
        instance.customers[:, 0],
        instance.customers[:, 1],
        c="skyblue",
        edgecolors="blue",
        s=80,
        label="Customers",
        zorder=5,
    )
    for i, (x, y) in enumerate(instance.customers):
        plt.text(x, y + 0.5, str(i), fontsize=8, ha="center", color="darkblue")

    # Common: Plot Main Depot
    plt.scatter(
        instance.main_depot[0],
        instance.main_depot[1],
        c="black",
        marker="s",
        s=100,
        label="Main Depot",
        zorder=10,
    )

    # Check Mode
    is_lrp = "sec_assignments" in result

    if is_lrp:
        # --- LRP LOGIC ---

        # 1. Plot Depots (Open vs Closed)
        # All potential depots
        all_depots = result.get(
            "all_potential_depots", instance.mobile_depots
        )  # Fallback if not in result
        # Open indices
        open_indices = result["open_depots"]  # e.g. [1, 3]

        for i, loc in enumerate(all_depots):
            if i in open_indices:
                plt.scatter(
                    loc[0],
                    loc[1],
                    c="red",
                    marker="*",
                    s=200,
                    label="Active Depot"
                    if "Active Depot" not in plt.gca().get_legend_handles_labels()[1]
                    else "",
                    zorder=10,
                )
            else:
                plt.scatter(loc[0], loc[1], c="lightgray", marker="x", s=50, zorder=1)

        # 2. Truck Route (Edges)
        # Nodes: 0..N-1 (Depots), N (Main)
        truck_edges = result["truck_edges"]
        N = len(all_depots)

        # Helper to get loc
        def get_loc(idx):
            if idx == N:
                return instance.main_depot
            return all_depots[idx]

        for u, v in truck_edges:
            p1 = get_loc(u)
            p2 = get_loc(v)
            plt.plot(
                [p1[0], p2[0]],
                [p1[1], p2[1]],
                c="black",
                linewidth=2,
                linestyle="--",
                label="Truck"
                if "Truck" not in plt.gca().get_legend_handles_labels()[1]
                else "",
            )

        # 3. Secondary Routes
        colors = [
            "#1f77b4",
            "#ff7f0e",
            "#2ca02c",
            "#9467bd",
            "#e377c2",
            "#7f7f7f",
            "#bcbd22",
            "#17becf",
        ]

        sec_assignments = result["sec_assignments"]
        for d_idx, fleets in sec_assignments.items():
            depot_loc = all_depots[d_idx]

            for v_idx, path in fleets.items():
                if not path:
                    continue

                # Pick color (unique per vehicle globally? or per depot?)
                # Let's simple rotate colors
                color = colors[(d_idx * 4 + v_idx) % len(colors)]

                route_coords = [depot_loc]
                for c_idx in path:
                    route_coords.append(instance.customers[c_idx])
                route_coords.append(depot_loc)  # Closed loop always for LRP secondary?

                route_coords = np.array(route_coords)
                plt.plot(
                    route_coords[:, 0],
                    route_coords[:, 1],
                    c=color,
                    linewidth=1.5,
                    alpha=0.8,
                )

        title_str = f"2-Echelon LRP (Truck Dist: {result['truck_dist']:.1f}, Sec Cost: {result['total_sec_cost']:.1f})"

    else:
        # --- SINGLE DEPOT LOGIC ---

        # 1. Selected Depot
        sel_idx = result["selected_depot_idx"]
        sel_loc = instance.mobile_depots[
            sel_idx
        ]  # Note: This assumes instance.mobile_depots matches result logic.
        # In Scen 1/2, 'mobile_depots' in instance might not clear.
        # But 'result' has 'selected_depot_loc' usually
        if "selected_depot_loc" in result:
            sel_loc = result["selected_depot_loc"]

        plt.scatter(
            sel_loc[0],
            sel_loc[1],
            c="red",
            marker="*",
            s=200,
            label="Selected Depot",
            zorder=10,
        )

        # Plot others if they exist (for Scen 0)
        # If result has 'all_potential_depots', use that
        if "all_potential_depots" in result:
            for i, loc in enumerate(result["all_potential_depots"]):
                if i != sel_idx:
                    plt.scatter(loc[0], loc[1], c="lightgray", marker="x", s=30)

        # 2. Truck Route
        plt.plot(
            [instance.main_depot[0], sel_loc[0]],
            [instance.main_depot[1], sel_loc[1]],
            c="black",
            linewidth=2,
            linestyle="--",
            label="Truck",
        )

        # 3. Assignments
        colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#9467bd"]
        assignments = result["assignments"]
        for v_idx, path in assignments.items():
            if not path:
                continue
            color = colors[v_idx % len(colors)]

            route_coords = [sel_loc]
            for c_idx in path:
                route_coords.append(instance.customers[c_idx])

            if not result.get("open_loop", False):
                route_coords.append(sel_loc)

            route_coords = np.array(route_coords)
            plt.plot(
                route_coords[:, 0],
                route_coords[:, 1],
                c=color,
                linewidth=2,
                alpha=0.8,
                label=f"Veh {v_idx + 1}",
            )

        title_str = f"VRP Solution (Max Dist: {result.get('max_dist', 0):.2f})"

    plt.title(title_str)
    plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
    plt.grid(True, linestyle=":", alpha=0.6)

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        plt.close()
    else:
        plt.show()
