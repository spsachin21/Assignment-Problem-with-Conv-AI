from pyomo.environ import *
from pyomo.opt import SolverStatus, TerminationCondition
import pandas as pd
import time
from solvers.optimization_result import OptimizationResult

def solve_assignment_pyomo(incidence_matrix, cost_matrix, employees_df, time_limit=None):
        
    model = ConcreteModel()
    employees=incidence_matrix.index.tolist()
    tasks=incidence_matrix.columns.tolist()
    employee_names = (employees_df.set_index("Employee_ID")["Employee_Name"].to_dict())

    #Sets
    model.Employees= Set(initialize=employees)
    model.Tasks= Set(initialize=tasks)

    #Decision Variables
    model.x=Var(model.Employees, model.Tasks, domain=Binary)

    #Objective
    def objective_rule(model):
        return sum(cost_matrix.loc[emp, tas]*model.x[emp,tas]
                for emp in model.Employees 
                for tas in model.Tasks
                )
    
    model.objective=Objective(rule=objective_rule, sense=minimize)

    #Employee Constraint
    def employee_constraint(model,emp):
        return sum(model.x[emp,tas] for tas in model.Tasks)<=1

    model.employee_constraint= Constraint(model.Employees, rule=employee_constraint)

    #Task Constraint
    def task_constraint(model,tas):
        return sum(model.x[emp,tas] for emp in model.Employees)==1

    model.task_constraint=Constraint(model.Tasks, rule=task_constraint)

    #Incidence Matrix
    def feasibility_constraint(model, emp, tas):
        return model.x[emp, tas]<=incidence_matrix.loc[emp, tas]

    model.feasibility_constraint = Constraint(model.Employees, model.Tasks,
                                               rule=feasibility_constraint)

    solver=SolverFactory("glpk")

    if time_limit is not None:
        solver.options['tmlim']=time_limit

    start = time.perf_counter()
    results = solver.solve(model, tee=False)
    runtime = time.perf_counter() - start

    if (results.solver.status == SolverStatus.ok and
    results.solver.termination_condition == TerminationCondition.optimal):
        status = "Optimal"

    elif results.solver.termination_condition==TerminationCondition.maxTimeLimit:
        status = "Time Limit"

    elif results.solver.termination_condition==TerminationCondition.infeasible:
        status="Infeasible"

    elif results.solver.termination_condition == TerminationCondition.unbounded:
        status = "Unbounded"

    elif results.solver.termination_condition == TerminationCondition.feasible:
        status = "Feasible"            
    else:
        status = f"{results.solver.status} ({results.solver.termination_condition})"


    assignments = []
    if results.solver.termination_condition in (TerminationCondition.optimal, TerminationCondition.feasible):
        objective = value(model.objective)
        for emp in model.Employees:
            for tas in model.Tasks:
                if value(model.x[emp, tas]) > 0.5:
                    assignments.append({
                        "Employee_ID": emp,
                        "Employee_Name": employee_names[emp],
                        "Task": tas,
                        "Cost": cost_matrix.loc[emp, tas]
                    })
    else:
        objective = None
    assignments_df = pd.DataFrame(assignments, columns=["Employee_ID", "Employee_Name", "Task", "Cost"])

    return OptimizationResult(
        solver="Glpk",
        status=status,
        objective=objective,
        runtime=runtime,
        gap=None,
        assignments=assignments_df,
        solver_statistics={
            "Number of Variables": len(model.x),
            "Number of Constraints": (len(model.employee_constraint) + len(model.task_constraint) + len(model.feasibility_constraint)),
            }
        )              
        