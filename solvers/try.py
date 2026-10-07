from pyomo.environ import SolverFactory

solver = SolverFactory("glpk")
print(solver.available())