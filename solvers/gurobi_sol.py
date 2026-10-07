import gurobipy as gp
from gurobipy import GRB
import pandas as pd
# import io
import os
import tempfile
from constraint_engine.validator import ConstraintValidator
from constraint_engine.translator import apply_constraints
from solvers.optimization_result import OptimizationResult


# ==========================================================
# Build Model
# ==========================================================

def build_assignment_model(incidence_matrix, cost_matrix):

    employees = incidence_matrix.index.tolist()
    tasks = incidence_matrix.columns.tolist()

    model = gp.Model("Employee_Assignment")

    # ------------------------------------------------------
    # Decision Variables
    # ------------------------------------------------------

    x = model.addVars(
        employees,
        tasks,
        vtype=GRB.BINARY,
        name="x"
    )

    # ------------------------------------------------------
    # Objective
    # ------------------------------------------------------

    model.setObjective(

        gp.quicksum(
            cost_matrix.loc[e, t] * x[e, t]
            for e in employees
            for t in tasks
        ),

        GRB.MINIMIZE
    )

    # ------------------------------------------------------
    # Employee Constraints
    # ------------------------------------------------------

    for e in employees:

        model.addConstr(

            gp.quicksum(
                x[e, t]
                for t in tasks
            ) <= 1,

            name=f"Emp_{e}"
        )

    # ------------------------------------------------------
    # Task Constraints
    # ------------------------------------------------------

    for t in tasks:

        model.addConstr(

            gp.quicksum(
                x[e, t]
                for e in employees
            ) == 1,

            name=f"Task_{t}"
        )

    # ------------------------------------------------------
    # Feasibility Constraints
    # ------------------------------------------------------

    for e in employees:
        for t in tasks:

            model.addConstr(

                x[e, t] <= incidence_matrix.loc[e, t],

                name=f"Feasible_{e}_{t}"

            )

    return model, x, employees, tasks

# Solve Model
def solve_model(model, time_limit=None):
    if time_limit is not None:
        model.Params.TimeLimit = time_limit

    with tempfile.NamedTemporaryFile(suffix=".log", delete=False) as f:
        log_path = f.name

    model.Params.LogFile = log_path
    model.optimize()

    # Important: close Gurobi's handle
    model.Params.LogFile = ""

    with open(log_path, "r", encoding="utf-8") as f:
        solver_log = f.read()

    os.remove(log_path)

    return solver_log


# ==========================================================
# Extract Results
# ==========================================================

def extract_results(
    model,
    x,
    employees,
    tasks,
    cost_matrix,
    employees_df,
    solver_log
):

    employee_names = (
        employees_df
        .set_index("Employee_ID")["Employee_Name"]
        .to_dict()
    )

    status_map = {

        GRB.OPTIMAL: "Optimal",

        GRB.TIME_LIMIT: "Time Limit",

        GRB.INFEASIBLE: "Infeasible",

        GRB.UNBOUNDED: "Unbounded",

        GRB.INF_OR_UNBD: "Infeasible or Unbounded"

    }

    status = status_map.get(model.Status, "Unknown")

    assignments = []

    if model.SolCount > 0:

        for e in employees:
            for t in tasks:

                if x[e, t].X > 0.5:

                    assignments.append({

                        "Employee_ID": e,

                        "Employee_Name": employee_names[e],

                        "Task": t,

                        "Cost": cost_matrix.loc[e, t]

                    })

        assignments_df = pd.DataFrame(assignments)

        objective = model.ObjVal

        gap = model.MIPGap

    else:

        assignments_df = pd.DataFrame(

            columns=[
                "Employee_ID",
                "Employee_Name",
                "Task",
                "Cost"
            ]

        )

        objective = None

        gap = None

    return OptimizationResult(

        solver="Gurobi",

        status=status,

        objective=objective,

        runtime=model.Runtime,

        gap=gap,

        assignments=assignments_df,

        solver_statistics={

            "Node Count": model.NodeCount,

            "Simplex Iterations": model.IterCount,

            "Number of Variables": model.NumVars,

            "Number of Constraints": model.NumConstrs

        },

        solver_log = solver_log

    )


# ==========================================================
# Main Solver
# ==========================================================

def solve_assignment_gurobipy(
    incidence_matrix,
    cost_matrix,
    employees_df,
    time_limit=None,
    parsed_constraints=None,
):

    # ------------------------------------------------------
    # Build Base Model
    # ------------------------------------------------------

    model, x, employees, tasks = build_assignment_model(
        incidence_matrix,
        cost_matrix
    )

    # ------------------------------------------------------
    # Register Optimization Variables
    # ------------------------------------------------------

    variables = {

        "x": x

    }

    # ------------------------------------------------------
    # Insert LLM Constraints
    # ------------------------------------------------------

    if parsed_constraints:

        for c in parsed_constraints:
            print("Constraint:", c)
            print("lhs:", c.lhs)
            print("lhs type:", type(c.lhs))
            print("rhs =", c.rhs, type(c.rhs))

        validator = ConstraintValidator(employees, tasks)

        validation = validator.validate(parsed_constraints)

        if not validation.valid:
            raise ValueError(validation.errors)
        
        apply_constraints(
            model=model,
            x=x,
            constraints=parsed_constraints,
            employees=employees,
            tasks=tasks,
            solver="gurobi"
        )

    # ------------------------------------------------------
    # Solve
    # ------------------------------------------------------

    solver_log = solve_model(
        model,
        time_limit
    )

    # ------------------------------------------------------
    # Extract Results
    # ------------------------------------------------------

    return extract_results(

        model,

        x,

        employees,

        tasks,

        cost_matrix,

        employees_df,

        solver_log

    )