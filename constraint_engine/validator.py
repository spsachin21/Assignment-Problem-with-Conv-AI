from typing import List

from .models import (
    ParsedConstraint,
    ValidationResult,
    VariableExpression,
    SumExpression,
)


class ConstraintValidator:
    """
    Validates parsed constraints before they are inserted
    into the optimization model.
    """

    def __init__(
        self,
        employees,
        tasks,
        variables=None,
    ):

        self.employees = set(employees)
        self.tasks = set(tasks)

        if variables is None:
            self.variables = {"x"}
        else:
            self.variables = set(variables)

    # ==========================================================
    # Public API
    # ==========================================================

    def validate(
        self,
        constraints: List[ParsedConstraint],
    ) -> ValidationResult:

        errors = []

        for constraint in constraints:
            errors.extend(
                self.validate_constraint(constraint)
            )

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
        )

    # ==========================================================
    # Single Constraint
    # ==========================================================

    def validate_constraint(
        self,
        constraint: ParsedConstraint,
    ):

        errors = []

        lhs = constraint.lhs

        # ------------------------------------------------------
        # Variable name
        # ------------------------------------------------------

        if lhs.variable not in self.variables:

            errors.append(
                f"Unknown variable '{lhs.variable}'"
            )

        # ------------------------------------------------------
        # Operator
        # ------------------------------------------------------

        allowed = {
            "==",
            "<=",
            ">=",
            "<",
            ">",
        }

        if constraint.operator not in allowed:

            errors.append(
                f"Unsupported operator '{constraint.operator}'"
            )

        # ------------------------------------------------------
        # RHS
        # ------------------------------------------------------

        if not isinstance(constraint.rhs, (int, float)):

            errors.append(
                "RHS must be numeric."
            )

        # ------------------------------------------------------
        # Expression Type
        # ------------------------------------------------------
        print("--------------------------------")
        print("lhs =", lhs)
        print("lhs type =", type(lhs))
        print("lhs module =", type(lhs).__module__)
        print("Imported VariableExpression =", VariableExpression)
        print("Imported module =", VariableExpression.__module__)
        print("isinstance =", isinstance(lhs, VariableExpression))
        print("issubclass =", issubclass(type(lhs), VariableExpression))

        expr_type = type(lhs).__name__

        if expr_type == "VariableExpression":

            errors.extend(
                self.validate_variable_expression(lhs, constraint.rhs)
            )

        elif expr_type == "SumExpression":

            errors.extend(
                self.validate_sum_expression(lhs)
            )

        else:

            errors.append(
                f"Unsupported expression type: {expr_type}"
            )

        return errors

    # ==========================================================
    # Variable Expression
    # ==========================================================

    def validate_variable_expression(
        self,
        lhs: VariableExpression,
        rhs,
    ):

        errors = []

        if len(lhs.indices) != 2:

            errors.append(
                "Variable x must contain exactly two indices."
            )

            return errors

        employee = lhs.indices[0]
        task = lhs.indices[1]

        if employee not in self.employees:

            errors.append(
                f"Unknown employee '{employee}'."
            )

        if task not in self.tasks:

            errors.append(
                f"Unknown task '{task}'."
            )

        # x is binary

        if rhs not in [0, 1]:

            errors.append(
                "Binary variable x can only be constrained to 0 or 1."
            )

        return errors

    # ==========================================================
    # Sum Expression
    # ==========================================================

    def validate_sum_expression(
        self,
        lhs: SumExpression,
    ):

        errors = []

        # ---------------- Employees ----------------

        if lhs.employees != "*":

            for emp in lhs.employees:

                if emp not in self.employees:

                    errors.append(
                        f"Unknown employee '{emp}' in summation."
                    )

        # ---------------- Tasks ----------------

        if lhs.tasks != "*":

            for task in lhs.tasks:

                if task not in self.tasks:

                    errors.append(
                        f"Unknown task '{task}' in summation."
                    )

        return errors

    