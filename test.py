from constraint_engine.validator import ConstraintValidator
from constraint_engine.models import ParsedConstraint


employees=[
    "E1",
    "E2"
]


tasks=[
    "T1",
    "T2"
]


constraint = ParsedConstraint(

    dsl="x[E1,T1]==0",

    expression_type="variable",

    variable="x",

    indices=[
        "E1",
        "T1"
    ],

    operator="==",

    rhs=0,

    constraint_type="hard",

    family="employee_unavailable"
)



validator = ConstraintValidator(
    employees,
    tasks
)


result = validator.validate(
    [constraint]
)


print(result)