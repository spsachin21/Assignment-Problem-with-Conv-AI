import gurobipy as gp
from gurobipy import GRB
import pandas as pd
from solvers.optimization_result import OptimizationResult

def solve_assignment_gurobipy(incidence_matrix, cost_matrix, employees_df, time_limit=None):

    employees=incidence_matrix.index.tolist()
    tasks=incidence_matrix.columns.tolist()
    employee_names = (employees_df.set_index("Employee_ID")["Employee_Name"].to_dict())

    #Create model
    model=gp.Model("Employee_Assignment")

    #Decision variables
    x=model.addVars(employees, tasks, vtype=GRB.BINARY,name="x")

    # Objective
    model.setObjective(gp.quicksum(cost_matrix.loc[emp, tas]*x[emp, tas] for emp in employees for tas in tasks), GRB.MINIMIZE)
    #Constraint-- every employee gets atmost one task
    for emp in employees:
        model.addConstr(gp.quicksum(x[emp,tas] for tas in tasks)<=1, name=f"Emp_{emp}")

    #Constraint -- every task is assigned to only one employee
    for tas in tasks:
        model.addConstr(gp.quicksum(x[emp, tas] for emp in employees)==1, name=f"Task_{tas}")

    #Constraint-- assignment based on skillset
    for emp in employees:
        for tas in tasks:
            model.addConstr(x[emp, tas]<= incidence_matrix.loc[emp, tas], name=f"feasible_assignment {emp}X{tas}")

    if time_limit is not None:
        model.Params.TimeLimit=time_limit
    model.optimize()

    status_map={
        GRB.OPTIMAL: "Optimal",
        GRB.TIME_LIMIT: "Time Limit",
        GRB.INFEASIBLE: "Infeasible",
        GRB.UNBOUNDED: "Unbounded",
        GRB.INF_OR_UNBD: "Infeasible or Unbounded"
    }

    status=status_map.get(model.Status, "Unknown")

    assignments = []

    if model.SolCount > 0:
        for emp in employees:
            for tas in tasks:
                if x[emp, tas].X > 0.5:
                    assignments.append({
                        "Employee_ID": emp,
                        "Employee_Name": employee_names[emp],
                        "Task": tas,
                        "Cost": cost_matrix.loc[emp, tas]
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
            }
        )        



