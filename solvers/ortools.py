from ortools.linear_solver import pywraplp
import pandas as pd
import io
import contextlib
from solvers.optimization_result import OptimizationResult

def solve_assignment_ortools(incidence_matrix, cost_matrix, employees_df, time_limit=None, parsed_constraints=None):

    employees=incidence_matrix.index.tolist()
    tasks=incidence_matrix.columns.tolist()
    employee_names = (employees_df.set_index("Employee_ID")["Employee_Name"].to_dict())

    #Create the mip solver with the scip backend (MPSolver Wrapper)
    solver=pywraplp.Solver.CreateSolver("SCIP")
    if solver is None:
        raise RuntimeError("SCIP solver is unavailable.")

    #Decision variables
    x={}
    for emp in employees:
        for tas in tasks:
            x[emp,tas] = solver.IntVar(0,1,f"x_{emp}_{tas}") 

    #Employee Constraint
    for emp in employees:
        solver.Add(solver.Sum([x[emp,tas] for tas in tasks])<=1)    

    #Task Constraint
    for tas in tasks:
        solver.Add(solver.Sum([x[emp,tas] for emp in employees])==1)

    #Incidence Matrix based constraint
    for emp in employees:
        for tas in tasks:
            solver.Add(x[emp,tas]<=incidence_matrix.loc[emp,tas])         

    #Objective
    objective_terms=[]
    for emp in employees:
        for tas in tasks:
            objective_terms.append(cost_matrix.loc[emp,tas]*x[emp,tas])
    solver.Minimize(solver.Sum(objective_terms))      

    if time_limit is not None:
    # OR-Tools expects milliseconds
        solver.SetTimeLimit(int(time_limit * 1000))

    # status_code = solver.Solve()
    solver.EnableOutput()

    log_stream = io.StringIO()

    with contextlib.redirect_stdout(log_stream):
        status_code = solver.Solve()

    solver_log = log_stream.getvalue()
    
    status_map = {
        pywraplp.Solver.OPTIMAL: "Optimal",
        pywraplp.Solver.FEASIBLE: "Feasible",
        pywraplp.Solver.INFEASIBLE: "Infeasible",
        pywraplp.Solver.UNBOUNDED: "Unbounded",
        pywraplp.Solver.ABNORMAL: "Abnormal",
        pywraplp.Solver.NOT_SOLVED: "Not Solved"
    }    

    status = status_map.get(status_code, "Unknown")

    assignments = []

    if status_code in (pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE):
        for emp in employees:
            for tas in tasks:
                if x[emp, tas].solution_value() > 0.5:
                    assignments.append({
                        "Employee_ID": emp,
                        "Employee_Name": employee_names[emp],
                        "Task": tas,
                        "Cost": cost_matrix.loc[emp, tas]
                    })

        assignments_df = pd.DataFrame(assignments)

        objective = solver.Objective().Value()

    else:
        assignments_df = pd.DataFrame(
            columns=["Employee", "Task", "Cost"]
        )
        objective = None

    return OptimizationResult(
            solver="OR-Tools (SCIP)",
            status=status,
            objective=objective,
            runtime=solver.wall_time() / 1000.0,
            gap=None,
            assignments=assignments_df,
            solver_statistics={
            "Number of Variables": solver.NumVariables(),
            "Number of Constraints": solver.NumConstraints(),
            "Iterations": solver.iterations(),
            },
            solver_log=solver_log

)    

