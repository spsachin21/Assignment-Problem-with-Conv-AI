from pyomo.environ import Constraint


# ==========================================================
# Public API
# ==========================================================

def apply_constraints(
    model,
    constraints,
    employees,
    tasks
):
    """
    Apply LLM generated constraints into a Pyomo model.
    """

    counter = 1

    for constraint in constraints:

        _apply_single_constraint(
            model,
            constraint,
            employees,
            tasks,
            counter,
        )

        counter += 1


# ==========================================================
# Single Constraint
# ==========================================================

def _apply_single_constraint(
    model,
    constraint,
    employees,
    tasks,
    counter,
):

    lhs = constraint.lhs

    expression_type = lhs.type

    # ------------------------------------------------------
    # Variable Expression
    # ------------------------------------------------------

    if expression_type == "variable":

        expr = _build_variable_expression(
            model,
            lhs,
        )

    # ------------------------------------------------------
    # Sum Expression
    # ------------------------------------------------------

    elif expression_type == "sum":

        expr = _build_sum_expression(
            model,
            lhs,
            employees,
            tasks,
        )

    else:

        raise ValueError(
            f"Unsupported expression type: {expression_type}"
        )

    _add_constraint(
        model,
        expr,
        constraint.operator,
        constraint.rhs,
        counter,
    )


# ==========================================================
# Variable Expression
# ==========================================================

def _build_variable_expression(
    model,
    lhs,
):
    """
    Supports

    x[E1,T2]
    """

    if len(lhs.indices) != 2:

        raise ValueError(
            "Variable expression requires exactly two indices."
        )

    employee = lhs.indices[0]
    task = lhs.indices[1]

    return model.x[employee, task]


# ==========================================================
# Sum Expression
# ==========================================================

def _build_sum_expression(
    model,
    lhs,
    employees,
    tasks,
):
    """
    Supports

    sum(x[E1,*])

    sum(x[*,T1])

    sum(x[E1,{T1,T2}])

    sum(x[{E1,E2},*])
    """

    # -----------------------------
    # Employees
    # -----------------------------

    if lhs.employees == "*":

        employee_set = employees

    else:

        employee_set = lhs.employees

    # -----------------------------
    # Tasks
    # -----------------------------

    if lhs.tasks == "*":

        task_set = tasks

    else:

        task_set = lhs.tasks

    # -----------------------------
    # Expression
    # -----------------------------

    return sum(

        model.x[e, t]

        for e in employee_set

        for t in task_set

    )


# ==========================================================
# Add Constraint
# ==========================================================

def _add_constraint(
    model,
    expr,
    operator,
    rhs,
    counter,
):
    """
    Dynamically adds a Pyomo constraint to the model.
    """

    name = f"llm_constraint_{counter}"

    if operator == "==":

        c = Constraint(expr=expr == rhs)

    elif operator == "<=":

        c = Constraint(expr=expr <= rhs)

    elif operator == ">=":

        c = Constraint(expr=expr >= rhs)

    elif operator == "<":

        c = Constraint(expr=expr < rhs)

    elif operator == ">":

        c = Constraint(expr=expr > rhs)

    else:

        raise ValueError(
            f"Unsupported operator '{operator}'"
        )

    setattr(model, name, c)