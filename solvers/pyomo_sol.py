from pyomo.environ import *
from pyomo.opt import SolverStatus, TerminationCondition
import pandas as pd
import time
from solvers.optimization_result import OptimizationResult
from constraint_engine.translator_pyomo import apply_constraints
from constraint_engine.validator import ConstraintValidator
from pyomo.environ import SolverFactory
import tempfile
import os
from pyomo.environ import SolverFactory

# ==========================================================
# Build Model
# ==========================================================

def build_assignment_model(incidence_matrix, cost_matrix):

    employees = incidence_matrix.index.tolist()
    tasks = incidence_matrix.columns.tolist()

    model = ConcreteModel()

    # ------------------------------------------------------
    # Sets
    # ------------------------------------------------------

    model.Employees = Set(
        initialize=employees
    )

    model.Tasks = Set(
        initialize=tasks
    )

    # ------------------------------------------------------
    # Decision Variables
    # ------------------------------------------------------

    model.x = Var(
        model.Employees,
        model.Tasks,
        domain=Binary
    )

    # ------------------------------------------------------
    # Objective
    # ------------------------------------------------------

    def objective_rule(model):

        return sum(
            cost_matrix.loc[e, t] * model.x[e, t]
            for e in employees
            for t in tasks
        )

    model.objective = Objective(
        rule=objective_rule,
        sense=minimize
    )

    # ------------------------------------------------------
    # Employee Constraints
    # ------------------------------------------------------

    def employee_constraint(model, e):

        return sum(
            model.x[e, t]
            for t in tasks
        ) <= 1

    model.employee_constraint = Constraint(
        model.Employees,
        rule=employee_constraint
    )

    # ------------------------------------------------------
    # Task Constraints
    # ------------------------------------------------------

    def task_constraint(model, t):

        return sum(
            model.x[e, t]
            for e in employees
        ) == 1

    model.task_constraint = Constraint(
        model.Tasks,
        rule=task_constraint
    )

    # ------------------------------------------------------
    # Feasibility Constraints
    # ------------------------------------------------------

    def feasibility_constraint(model, e, t):

        return (
            model.x[e, t]
            <=
            incidence_matrix.loc[e, t]
        )

    model.feasibility_constraint = Constraint(
        model.Employees,
        model.Tasks,
        rule=feasibility_constraint
    )

    return model, employees, tasks

# ==========================================================
# Solve Model
# ==========================================================


def solve_model(
    model,
    solver_name,
    time_limit=None,
):

    solver = SolverFactory(solver_name)

    if solver is None or not solver.available():
        raise RuntimeError(f"Solver '{solver_name}' is not available.")

    if time_limit is not None:

        if solver_name.lower() == "glpk":
            solver.options["tmlim"] = time_limit

        elif solver_name.lower() == "cbc":
            solver.options["seconds"] = time_limit

        elif solver_name.lower() == "gurobi":
            solver.options["TimeLimit"] = time_limit

    # log_file = tempfile.mktemp(suffix=".log")
    with tempfile.NamedTemporaryFile(suffix=".log", delete=False) as tmp:
        log_file = tmp.name

    tmp.close()

    start = time.perf_counter()

    results = solver.solve(
        model,
        tee=False,
        logfile=log_file,
    )

    runtime = time.perf_counter() - start

    solver_log = ""

    try:
        if os.path.exists(log_file):
            with open(log_file, "r", encoding="utf-8") as f:
                solver_log = f.read()
    finally:
        if os.path.exists(log_file):
            os.remove(log_file)

    # if os.path.exists(log_file): 
    #     with open(log_file, "r", encoding="utf-8") as f: 
    #         solver_log = f.read() 
    #     os.remove(log_file)

    return results, runtime, solver_log

# def solve_model(
#     model,
#     solver_name,
#     time_limit=None):
#     """
#     Solves the Pyomo model and captures the solver log.
#     """

#     # solver = SolverFactory("glpk")
#     solver = SolverFactory(solver_name)

#     # ------------------------------------------------------
#     # Time Limit
#     # ------------------------------------------------------


#     if time_limit is not None:

#         solver.options["tmlim"] = time_limit

#     # ------------------------------------------------------
#     # Create Temporary Log File
#     # ------------------------------------------------------

#     log_file = tempfile.NamedTemporaryFile(
#         suffix=".log",
#         delete=False,
#     )
#     log_file.close()

#     # ------------------------------------------------------
#     # Solve
#     # ------------------------------------------------------

#     start = time.perf_counter()

#     results = solver.solve(
#         model,
#         tee=False,
#         logfile=log_file.name,
#     )

#     runtime = time.perf_counter() - start

#     # ------------------------------------------------------
#     # Read Solver Log
#     # ------------------------------------------------------

#     with open(
#         log_file.name,
#         "r",
#         encoding="utf-8",
#     ) as f:

#         solver_log = f.read()

#     return (
#         results,
#         runtime,
#         solver_log,
#     )

# ==========================================================
# Extract Results
# ==========================================================

def extract_results(
    model,
    results,
    employees,
    tasks,
    cost_matrix,
    employees_df,
    runtime,
    solver_log,
):

    employee_names = (
        employees_df
        .set_index("Employee_ID")["Employee_Name"]
        .to_dict()
    )

    # ------------------------------------------------------
    # Solver Status
    # ------------------------------------------------------

    if (
        results.solver.status == SolverStatus.ok
        and results.solver.termination_condition == TerminationCondition.optimal
    ):

        status = "Optimal"

    elif (
        results.solver.termination_condition
        == TerminationCondition.maxTimeLimit
    ):

        status = "Time Limit"

    elif (
        results.solver.termination_condition
        == TerminationCondition.infeasible
    ):

        status = "Infeasible"

    elif (
        results.solver.termination_condition
        == TerminationCondition.unbounded
    ):

        status = "Unbounded"

    elif (
        results.solver.termination_condition
        == TerminationCondition.feasible
    ):

        status = "Feasible"

    else:

        status = (
            f"{results.solver.status} "
            f"({results.solver.termination_condition})"
        )

    # ------------------------------------------------------
    # Extract Assignments
    # ------------------------------------------------------

    assignments = []

    if results.solver.termination_condition in (
        TerminationCondition.optimal,
        TerminationCondition.feasible,
    ):

        for e in employees:
            for t in tasks:

                if value(model.x[e, t]) > 0.5:

                    assignments.append(

                        {

                            "Employee_ID": e,

                            "Employee_Name": employee_names[e],

                            "Task": t,

                            "Cost": cost_matrix.loc[e, t],

                        }

                    )

        assignments_df = pd.DataFrame(assignments)

        objective = value(model.objective)

        gap = None

    else:

        assignments_df = pd.DataFrame(

            columns=[

                "Employee_ID",

                "Employee_Name",

                "Task",

                "Cost",

            ]

        )

        objective = None

        gap = None

    # ------------------------------------------------------
    # Optimization Result
    # ------------------------------------------------------

    return OptimizationResult(

        solver="GLPK",

        status=status,

        objective=objective,

        runtime=runtime,

        gap=gap,

        assignments=assignments_df,

        solver_statistics={

            "Number of Variables": len(model.x),

            "Number of Constraints": (

                len(model.employee_constraint)

                + len(model.task_constraint)

                + len(model.feasibility_constraint)

            ),

        },

        solver_log=solver_log,

    )

# ==========================================================
# Main Solver
# ==========================================================

def solve_assignment_pyomo(
    incidence_matrix,
    cost_matrix,
    employees_df,
    time_limit=None,
    parsed_constraints=None,
    solver_name="glpk"
):

    # ------------------------------------------------------
    # Build Base Model
    # ------------------------------------------------------

    model, employees, tasks = build_assignment_model(
        incidence_matrix,
        cost_matrix
    )

    # ------------------------------------------------------
    # Register Optimization Variables
    # ------------------------------------------------------

    x = model.x

    # variables = {
    #     "x": x
    # }

    # ------------------------------------------------------
    # Insert LLM Constraints
    # ------------------------------------------------------

    if parsed_constraints:

        for c in parsed_constraints:
            print("Constraint:", c)
            print("lhs:", c.lhs)
            print("lhs type:", type(c.lhs))

        validator = ConstraintValidator(
            employees,
            tasks
        )

        validation = validator.validate(
            parsed_constraints
        )

        if not validation.valid:
            raise ValueError(validation.errors)

        apply_constraints(
            model=model,
            constraints=parsed_constraints,
            employees=employees,
            tasks=tasks )

    # ------------------------------------------------------
    # Solve
    # ------------------------------------------------------

    # results, runtime, solver_log = solve_model(
    #     model, solver_name,
    #     time_limit
    # )
    results, runtime, solver_log = solve_model(
    model=model,
    solver_name=solver_name,
    time_limit=time_limit,
    )
    # ------------------------------------------------------
    # Extract Results
    # ------------------------------------------------------

    return extract_results(

        model,

        results,

        employees,

        tasks,

        cost_matrix,

        employees_df,

        runtime,

        solver_log

    )