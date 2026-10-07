import gurobipy as gp

#translator for gurobipy


def apply_constraints(
    model,
    x,
    constraints,
    employees,
    tasks,
    solver="gurobi",
):
    """
    Apply LLM generated constraints into optimization model.
    """

    if solver.lower() != "gurobi":

        raise NotImplementedError(
            f"Translator for '{solver}' not implemented."
        )


    for constraint in constraints:

        _apply_single_constraint(
            model,
            x,
            constraint,
            employees,
            tasks
        )



# ==========================================================
# Single Constraint
# ==========================================================

def _apply_single_constraint(
    model,
    x,
    constraint,
    employees,
    tasks,
):

    # expression_type = constraint.expression_type
    lhs = constraint.lhs
    expression_type = lhs.type


    # -----------------------------
    # Variable expression
    # -----------------------------

    if expression_type == "variable":

        expr = _build_variable_expression(
            x,
            lhs
        )


    # -----------------------------
    # Sum expression
    # -----------------------------

    elif expression_type == "sum":

        expr = _build_sum_expression(
            x,
            lhs,
            employees,
            tasks
        )


    else:

        raise ValueError(
            f"Unsupported expression type: {expression_type}"
        )


    _add_expr_to_constraint(
        model,
        expr,
        constraint.operator,
        constraint.rhs,
        constraint.dsl
    )



# ==========================================================
# Variable Expression
# ==========================================================

def _build_variable_expression(
    x,
    lhs
):
    """
    Example:

    x[E1,T2]

    """

    if len(lhs.indices) != 2:

        raise ValueError(
            "Variable expression requires two indices"
        )


    employee = lhs.indices[0]

    task = lhs.indices[1]


    return x[employee, task]



# ==========================================================
# Sum Expression
# ==========================================================

def _build_sum_expression(
    x,
    lhs,
    employees,
    tasks
):
    """
    Supports

    sum(x[E1,*])

    sum(x[*,T1])

    sum(x[E1,{T1,T2}])

    sum(x[{E1,E2},*])
    """

    # -----------------------------
    # Employee dimension
    # -----------------------------

    if lhs.employees == "*":

        employee_set = employees

    else:

        employee_set = lhs.employees

    # -----------------------------
    # Task dimension
    # -----------------------------

    if lhs.tasks == "*":

        task_set = tasks

    else:

        task_set = lhs.tasks

    # -----------------------------
    # Build summation
    # -----------------------------

    return gp.quicksum(

        x[e, t]

        for e in employee_set

        for t in task_set

    )



# ==========================================================
# Add Constraint
# ==========================================================

def _add_expr_to_constraint(
    model,
    expr,
    operator,
    rhs,
    name
):

    if operator == "==":


        model.addConstr(
            expr == rhs,
            name=name
        )


    elif operator == "<=":


        model.addConstr(
            expr <= rhs,
            name=name
        )


    elif operator == ">=":


        model.addConstr(
            expr >= rhs,
            name=name
        )


    elif operator == "<":


        model.addConstr(
            expr < rhs,
            name=name
        )


    elif operator == ">":


        model.addConstr(
            expr > rhs,
            name=name
        )


    else:

        raise ValueError(
            f"Unsupported operator {operator}"
        )