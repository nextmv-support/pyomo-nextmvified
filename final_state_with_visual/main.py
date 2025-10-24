#!/usr/bin/env python3

import json
import os

import nextmv
import plotly.graph_objects as go
from diet import add_dairy_constraint, model
from nextmv import cloud
from pyomo.environ import value
from pyomo.opt import SolverFactory

# MODIFIED - load manifest and extract options to use in the execution
manifest = cloud.Manifest.from_yaml(".")
options = manifest.extract_options()


def main():
    """
    Main function to solve the diet optimization problem using Pyomo functions.
    """
    instance = model.create_instance("inputs/diet.dat")

    # MODIFIED - add dairy constraint if specified in options
    if options.limit_dairy:
        add_dairy_constraint(instance)

    # MODIFIED - use solver that was specified in the options
    solver = SolverFactory(options.solver)
    if not solver.available():
        print(f"Error: {options.solver} solver is not available!")
        print("Please install the solver or try a different solver.")
        return
    results = solver.solve(instance, tee=True)
    os.makedirs("outputs", exist_ok=True)
    output_file = os.path.join("outputs", "diet_solution.txt")

    # Collect solution data for visualization
    selected_foods = []
    food_servings = []
    food_costs = []
    food_total_costs = []

    with open(output_file, "w") as f:
        if results.solver.termination_condition == "optimal":
            f.write("=" * 50 + "\n")
            f.write("DIET OPTIMIZATION SOLUTION\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Minimum cost: ${value(instance.cost):.2f}\n\n")
            f.write("Optimal food selections:\n")
            f.write("-" * 40 + "\n")
            total_cost = 0
            for food in instance.F:
                servings = value(instance.x[food])
                if servings > 0:
                    cost_per_serving = value(instance.c[food])
                    food_cost = cost_per_serving * servings
                    total_cost += food_cost
                    f.write(
                        f"{food:18s}: {servings:2.0f} servings @ ${cost_per_serving:.2f} = ${food_cost:.2f}\n"
                    )
                    # Collect data for visualization
                    selected_foods.append(food)
                    food_servings.append(servings)
                    food_costs.append(cost_per_serving)
                    food_total_costs.append(food_cost)
        else:
            f.write(
                f"Solver terminated with condition: {results.solver.termination_condition}\n"
            )
            f.write("No optimal solution found.\n")

    # MODIFIED - write statistics for experiments
    statistics_file = "statistics.json"
    with open(statistics_file, "w") as stats_f:
        # Create food servings dictionary for statistics
        food_servings_dict = {}
        for food in instance.F:
            servings = value(instance.x[food])
            food_servings_dict[food] = servings

        statistics = nextmv.Statistics(
            result=nextmv.ResultStatistics(
                value=value(instance.cost),
                custom={
                    "nvars": len(instance.x),
                    "nconstraints": len(instance.nutrient_limit)
                    + 1
                    + (1 if options.limit_dairy else 0),
                    "food_servings": food_servings_dict,
                    "selected_foods": len(selected_foods),
                    "total_servings": sum(food_servings) if selected_foods else 0,
                },
            ),
        )
        stats_f.write(json.dumps({"statistics": statistics.to_dict()}))

    # Create Plotly visualization for selected foods
    if results.solver.termination_condition == "optimal" and selected_foods:
        # Create a subplot with secondary y-axis to properly show both metrics
        from plotly.subplots import make_subplots

        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Add bars for servings on primary y-axis
        fig.add_trace(
            go.Bar(
                x=selected_foods,
                y=food_servings,
                name="Servings",
                marker_color="lightblue",
                text=[f"{s:.0f}" for s in food_servings],
                textposition="auto",
                offsetgroup=1,
            ),
            secondary_y=False,
        )

        # Add bars for total cost on secondary y-axis
        fig.add_trace(
            go.Bar(
                x=selected_foods,
                y=food_total_costs,
                name="Total Cost ($)",
                marker_color="lightcoral",
                text=[f"${c:.2f}" for c in food_total_costs],
                textposition="auto",
                offsetgroup=2,
            ),
            secondary_y=True,
        )

        # Set y-axes titles
        fig.update_yaxes(title_text="Number of Servings", secondary_y=False)
        fig.update_yaxes(title_text="Total Cost ($)", secondary_y=True)

        # Update layout
        fig.update_layout(
            title="Optimal Diet Solution: Selected Food Items",
            xaxis_title="Food Items",
            barmode="group",
            legend=dict(x=0.7, y=1),
            height=500,
            margin=dict(l=50, r=50, t=80, b=100),
        )

        # Convert to JSON
        fig_json = fig.to_json()

        #  MODIFIED - Create Nextmv assets
        assets = []
        assets.append(
            nextmv.Asset(
                name="Diet Optimization Results",
                content_type="json",
                visual=nextmv.Visual(
                    visual_schema=nextmv.VisualSchema.PLOTLY,
                    visual_type="custom-tab",
                    label="Food Selection",
                ),
                content=[json.loads(fig_json)],
            )
        )

        # Write assets to file
        assets_file = "assets.json"
        with open(assets_file, "w") as assets_f:
            assets_dict = {"assets": [asset.to_dict() for asset in assets]}
            assets_f.write(json.dumps(assets_dict, indent=2))
        print(f"Assets written to {assets_file}")

    print(f"Results written to {output_file}")
    print(f"Statistics written to {statistics_file}")
    print(f"Assets written to {assets_file}")


if __name__ == "__main__":
    main()
