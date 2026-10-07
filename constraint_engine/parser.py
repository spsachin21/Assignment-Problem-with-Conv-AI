from typing import List

from .models import (
    ParsedConstraint,
    VariableExpression,
    SumExpression,
)


def parse_constraints(llm_response: dict) -> List[ParsedConstraint]:
    """
    Converts the LLM JSON response into ParsedConstraint objects.
    """

    if llm_response.get("status") != "success":
        raise ValueError(
            llm_response.get(
                "message",
                "LLM did not return a successful response."
            )
        )

    family = llm_response.get("constraint_family", "")

    parsed_constraints = [] 

    for constraint in llm_response.get("constraints", []):

        parsed = constraint["parsed"]
        lhs_json = parsed["lhs"]

        expression_type = lhs_json["type"]

        # --------------------------------------------------
        # Variable expression
        # --------------------------------------------------

        if expression_type == "variable":

            lhs = VariableExpression(
                type="variable",
                variable=lhs_json["variable"],
                indices=lhs_json["indices"],
            )


        # --------------------------------------------------
        # Sum expression
        # --------------------------------------------------

        elif expression_type == "sum":

            lhs = SumExpression(
                type="sum",
                variable=lhs_json["variable"],
                employees=lhs_json["employees"],
                tasks=lhs_json["tasks"],
            )

        else:

            raise ValueError(
                f"Unsupported expression type '{expression_type}'"
            )

        print(lhs)
        print(type(lhs))

        pc = ParsedConstraint(

            dsl=constraint["dsl"],

            lhs=lhs,

            operator=parsed["operator"],

            rhs=parsed["rhs"],

            constraint_type=constraint["type"],

            family=family,
        )

        parsed_constraints.append(pc)

    return parsed_constraints