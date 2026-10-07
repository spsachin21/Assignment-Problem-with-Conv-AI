from dataclasses import dataclass
from typing import List, Union


# ==========================================================
# Expression Types
# ==========================================================

@dataclass
class VariableExpression:
    type: str          # "variable"
    variable: str
    indices: List[str]


@dataclass
class SumExpression:
    type: str          # "sum"
    variable: str
    employees: Union[str, List[str]]
    tasks: Union[str, List[str]]


# All supported expressions
Expression = Union[
    VariableExpression,
    SumExpression
]


# ==========================================================
# Parsed Constraint
# ==========================================================

@dataclass
class ParsedConstraint:
    dsl: str
    lhs: Expression
    operator: str
    rhs: Union[int, float]
    constraint_type: str
    family: str


# ==========================================================
# Validation
# ==========================================================

@dataclass
class ValidationResult:
    valid: bool
    errors: List[str]