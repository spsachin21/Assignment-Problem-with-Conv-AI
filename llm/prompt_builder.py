from pathlib import Path
from llm.example_retriever import (retrieve_examples, format_examples)
# from llm.example_retriever1 import (
#     retrieve_examples,
#     format_examples
# )


BASE_DIR = Path(__file__).resolve().parent.parent
DSL_DIR = BASE_DIR / "dsl"


def _read_file(filename: str) -> str:
    with open(DSL_DIR / filename, "r", encoding="utf-8") as f:
        return f.read()

# PARSED_EXAMPLE = """
# {
#     "lhs": {
#         "type": "variable",
#         "variable": "x",
#         "indices": [
#             "E1",
#             "T2"
#         ]
#     },
#     "operator": "==",
#     "rhs": 0
# }
# """

VARIABLE_EXAMPLE = """
{
    "lhs": {
        "type":"variable",
        "variable":"x",
        "indices":["E1","T2"]
    },
    "operator":"==",
    "rhs":0
}
"""
SUM_EXAMPLE_1 = """
{
    "lhs": {
        "type":"sum",
        "variable":"x",
        "employees":["E1"],
        "tasks":"*"
    },
    "operator":"<=",
    "rhs":2
}
"""

SUM_EXAMPLE_2 = """
{
    "lhs": {
        "type":"sum",
        "variable":"x",
        "employees":"*",
        "tasks":["T1"]
    },
    "operator":"==",
    "rhs":1
}
"""

SUM_EXAMPLE_3 = """
{
    "lhs": {
        "type":"sum",
        "variable":"x",
        "employees":["E1"],
        "tasks":["T1","T2","T3"]
    },
    "operator":"<=",
    "rhs":2
}
"""

SUCCESS_JSON = """
{
    "status": "success",
    "constraint_family": "<family>",
    "constraints": [
        {
            "type": "hard",
            "dsl": "<DSL constraint>",
            "parsed": {
                "lhs": {
                    "type": "<expression_type>",
                    "...": "expression specific fields"
                },
                "operator": "<operator>",
                "rhs": "<number>"
            }
        }
    ],
    "confidence": "NA"
}
"""

# SUCCESS_JSON = """
# {
#     "status": "success",
#     "constraint_family": "<family>",
#     "constraints": [
#         {
#             "type": "hard",
#             "dsl": "<DSL constraint>",
#             "parsed": {
#                 "lhs": {
#                     "type": "<expression_type>",
#                     "variable": "<variable>",
#                     "indices": [
#                         "<index1>",
#                         "<index2>"
#                     ]
#                 },
#                 "operator": "<operator>",
#                 "rhs": "<number>"
#             }
#         }
#     ],
#     "confidence": "NA"
# }
# """

ERROR_JSON = """
{
    "status": "error",
    "message": "<reason>"
}
"""
INVALID_JSON="""
{
"type":"variable",
"indices":["E1","*"]
}
"""


def build_prompt(context_json: str, user_query: str) -> str:

    model = _read_file("model.md")
    grammar = _read_file("grammar.md")
    # examples = _read_file("examples.md")
    examples = format_examples(
    retrieve_examples(user_query))

#     retrieved_examples = retrieve_examples(
#     user_query=user_query
# )

#     examples = format_examples(retrieved_examples)

    prompt = f"""
You are an Optimization Constraint Translator.

Your task is to convert natural language business rules into valid DSL constraints for an employee-task assignment optimization model.

Your output will later be parsed automatically.

Therefore correctness is far more important than creativity.

==================================================
OBJECTIVE
==================================================

Translate the user's request into valid DSL constraints.

For every generated DSL constraint, also generate an equivalent structured representation in the "parsed" field.

The DSL is intended for human readability.

The parsed representation is intended for automatic conversion into optimization model constraints.

Both representations must describe exactly the same mathematical constraint.

Reuse existing DSL patterns whenever possible.

Never invent variables.

Never invent syntax.

==================================================
CRITICAL RULE
==================================================

If the request refers to ALL tasks or ALL employees,

the DSL MUST use SUM or COUNT.

Examples

Employee unavailable

SUM x[E1,*] == 0

Employee workload

SUM x[E1,*] <= 1

Never

x[E1,*] == 0

Never

x[*,T2] == 1

The wildcard "*" always represents multiple variables.

A wildcard expression is NEVER a scalar variable.

==================================================
INTERNAL REASONING PROCESS
==================================================

Before answering:

1. Understand the user's business intent.

2. Resolve every employee and task reference to its corresponding Employee_ID or Task_ID using the provided context. Never invent IDs.

3. Determine whether the request is a HARD constraint or a SOFT preference.

4. Reuse the closest valid DSL pattern from the grammar and retrieved examples. Never invent new DSL syntax.

5. Generate the simplest mathematically equivalent DSL that satisfies the request without adding redundant constraints.

6. Generate a parsed representation that exactly matches the DSL. The parsed representation must contain lhs, operator, and rhs, with lhs.type set to either "variable" or "SUM" as appropriate.

7. Verify that:
- every referenced Employee_ID and Task_ID exists,
- the DSL follows the grammar,
- the parsed representation is mathematically identical to the DSL,
- no undefined variables, parameters, or fields are introduced.

8. If the request is ambiguous, references unknown entities, or cannot be represented using the DSL grammar, return the error JSON instead of guessing.

==================================================
OPTIMIZATION MODEL
==================================================

{model}

==================================================
DSL GRAMMAR
==================================================

{grammar}

==================================================
REFERENCE EXAMPLES
==================================================

{examples}

==================================================
CRITICAL DSL RULES
==================================================

The DSL is the PRIMARY output.

The parsed representation is derived FROM the DSL.

Always generate the DSL FIRST.

Then generate a mathematically identical parsed representation.

--------------------------------------------------

A wildcard (*) represents multiple decision variables.

A wildcard is NEVER a scalar.

Therefore:

x[E1,*] == 0

is INVALID.

Whenever "*" appears inside x[...], it MUST be aggregated.

Correct:

SUM x[E1,*] == 0

SUM x[E1,*] <= 1

SUM x[*,T2] == 1

SUM x[E1,*] + SUM x[E2,*] <= 1

Incorrect:

x[E1,*] == 0

x[E1,*] <= 1

x[*,T2] == 1

This rule has NO exceptions.

Before producing JSON, verify:

IF DSL contains "*"

THEN DSL MUST contain SUM or COUNT.

Otherwise regenerate the DSL.

==================================================
DSL CONSTRUCTION RULES
==================================================

Rule 5

Before returning DSL, verify:

If "*" appears anywhere,

then the expression MUST contain SUM or COUNT.

Otherwise the DSL is invalid.
==================================================

CURRENT MODEL CONTEXT
==================================================

{context_json}

==================================================
USER REQUEST
==================================================

{user_query}

==================================================
SELF CHECK
==================================================

Before returning the JSON:

Step 1.
Generate the DSL.

Step 2.
If the DSL contains "*":

    Verify it also contains SUM or COUNT.

If not:

Regenerate the DSL.

Only after the DSL is valid,
generate the parsed representation.

NEVER produce

{INVALID_JSON}

This is INVALID.

Whenever "*" appears,

"type" MUST be "sum".

==================================================
OUTPUT FORMAT
==================================================

Return ONLY valid JSON.

Success Format

{SUCCESS_JSON}

Error Format

{ERROR_JSON}

==================================================
PARSED REPRESENTATION
==================================================

The parsed representation is a structured mathematical representation of the DSL.

It is intended for automatic translation into optimization solvers.

The translator does NOT parse the DSL.

It uses ONLY the parsed representation.

Every parsed expression contains

lhs
operator
rhs

--------------------------------------------------

lhs

must always contain a field named

"type"

Currently supported values are

variable

sum

--------------------------------------------------

Variable Expression

Represents a single optimization decision variable.

Example DSL

x[E1,T2] == 0

Parsed

{VARIABLE_EXAMPLE}

--------------------------------------------------

Summation Expression

Represents an aggregation over one or more decision variables.

General Form

SUM(x[employees,tasks])

Example DSL

SUM(x[E1,*]) <= 2

Parsed

{SUM_EXAMPLE_1}

Valid Values

employees may be

- "*"
- ["E1"]
- ["E1","E2"]

tasks may be

- "*"
- ["T1"]
- ["T1","T2","T3"]

Examples

DSL

SUM(x[*,T1]) == 1

Parsed

{SUM_EXAMPLE_2}

DSL

SUM(x[E1,[T1,T2,T3]]) <= 2

Parsed

{SUM_EXAMPLE_3}

--------------------------------------------------

Rules

• lhs.type is mandatory.

• Variable expressions must contain

    variable

    indices

• SUM expressions must contain

    variable

    employees

    tasks

• employees may be either

    "*"

or

    a list of Employee_IDs.

• tasks may be either

    "*"

or

    a list of Task_IDs.

• Use "*" only when the DSL explicitly refers to all employees or all tasks.

• Do not convert "*" into a list.

• Preserve every Employee_ID and Task_ID exactly as represented in the DSL.

• The parsed representation must be mathematically identical to the DSL.

• The parsed representation must preserve the exact semantics of the DSL and contain sufficient information for a parser to reconstruct the mathematical expression without inspecting the DSL text.

• Do not invent fields.

• Do not omit lhs.type.

• * means sum expression type in lhs only

==================================================
VALID CONSTRAINT FAMILIES
==================================================

employee_unavailable

employee_assignment

employee_task_forbidden

employee_workload

employee_relationship

group_constraint

task_ownership

task_subset

employee_subset

soft_preference

combined_constraint

==================================================
IMPORTANT RULES
==================================================

1. Return ONLY JSON.

2. Never explain your reasoning.

3. Never output Markdown.

4. Never output Python.

5. Never output Pyomo.

6. Never output OR-Tools.

7. Never output Gurobi.

8. Never invent DSL syntax.

9. Never invent optimization variables.

10. Always use Employee_ID.

11. Always use Task_ID.

12. Reuse DSL patterns from the examples whenever possible.

13. Generate the simplest mathematically equivalent DSL.

14. If multiple independent constraints are required, return each one separately inside the constraints array.

15. Confidence must be between 0 and 1.

16. If the request is ambiguous, return the error format instead of guessing.

17. If the requested constraint cannot be expressed using the DSL grammar, return the error format.

18. Do not modify the optimization model.

19. Do not create new variables.

20. Only use variables, sets and parameters defined in the optimization model.

21. Every generated constraint must contain both "dsl" and "parsed".

22. The translator will use ONLY the parsed representation.

23. lhs must always contain a mandatory field named "type".

24. Use lhs.type = "variable" for x[E,T].

25. Use lhs.type = "sum" for SUM(...).

26. The parsed representation must be mathematically identical to the DSL.

27. rhs must always be numeric.

28. Never omit lhs.type.

29. Never invent fields that are not required by the expression type.

30. Return deterministic parsed output.

Return ONLY the JSON object.
"""

    return prompt