from ortools.sat.python import cp_model
import pandas as pd
import io
import contextlib
from solvers.optimization_result import OptimizationResult

def solve_assignment_cpsat(incidence_matrix, cost_matrix, employees_df, time_limit=None, parsed_constraints=None):

    employees = incidence_matrix.index.tolist()
    tasks = incidence_matrix.columns.tolist()
    employee_names = (employees_df.set_index("Employee_ID")["Employee_Name"].to_dict())

    model = cp_model.CpModel()

    x = {}
    for emp in employees:
        for tas in tasks:
            x[emp, tas] = model.NewBoolVar(f"x_{emp}_{tas}")

    # Employee Constraint
    for emp in employees:
        model.Add(
            sum(x[emp, tas] for tas in tasks) <= 1
        )

    # Task Constraint
    for tas in tasks:
        model.Add(
            sum(x[emp, tas] for emp in employees) == 1
        )

    # Incidence Constraint
    for emp in employees:
        for tas in tasks:
            model.Add(
                x[emp, tas] <= int(incidence_matrix.loc[emp, tas])
            )

    # Objective
    model.Minimize(
        sum(int(cost_matrix.loc[emp, tas]) * x[emp, tas]
            for emp in employees
            for tas in tasks
        )
    )

    solver = cp_model.CpSolver()

    if time_limit is not None:
        solver.parameters.max_time_in_seconds = time_limit

    # Enable CP-SAT search log
    solver.parameters.log_search_progress = True

    # Capture solver log
    log_stream = io.StringIO()

    with contextlib.redirect_stdout(log_stream):
        status_code = solver.Solve(model)

    solver_log = log_stream.getvalue()

    # Status Mapping
    status_map = {
        cp_model.OPTIMAL: "Optimal",
        cp_model.FEASIBLE: "Feasible",
        cp_model.INFEASIBLE: "Infeasible",
        cp_model.MODEL_INVALID: "Model Invalid",
        cp_model.UNKNOWN: "Unknown"
    }

    status = status_map.get(status_code, "Unknown")

    # Extract Assignments
    assignments = []

    if status_code in (cp_model.OPTIMAL, cp_model.FEASIBLE):

        for emp in employees:
            for tas in tasks:

                if solver.Value(x[emp, tas]) == 1:

                    assignments.append({
                        "Employee_ID": emp,
                        "Employee_Name": employee_names[emp],
                        "Task": tas,
                        "Cost": cost_matrix.loc[emp, tas]
                    })

        assignments_df = pd.DataFrame(assignments)

        objective = solver.ObjectiveValue()

    else:

        assignments_df = pd.DataFrame(
            columns=["Employee", "Task", "Cost"]
        )

        objective = None

    gap = None

    if status_code in (cp_model.OPTIMAL, cp_model.FEASIBLE):

        bound = solver.BestObjectiveBound()

        if objective != 0:
            gap = abs(objective - bound) / abs(objective)

    # Return Result
    return OptimizationResult(

        solver="OR-Tools (CP-SAT)",

        status=status,

        objective=objective,

        runtime=solver.WallTime(),

        gap=gap,

        assignments=assignments_df,

        solver_statistics={

            "Number of Variables": len(x),

            "Number of Constraints":
                len(employees)
                + len(tasks)
                + len(employees) * len(tasks),
        },
        solver_log=solver_log

    )