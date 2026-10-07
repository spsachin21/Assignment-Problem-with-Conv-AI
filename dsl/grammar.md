# Employee–Task Optimization DSL Grammar

## Purpose

This DSL defines the symbolic language for expressing additional optimization constraints. It is the intermediate representation between natural language and the optimization solver.

The LLM must generate **only** expressions defined by this grammar. Every expression is validated by the parser before conversion into optimization constraints.

---

# General Rules

- Output only symbolic optimization constraints.
- Never output natural language, explanations, comments, or markdown.
- Never generate Python, Pyomo, Gurobi, or OR-Tools code.
- Never invent symbols outside this grammar.

---

# Available Optimization Symbols

Decision Variable

x[e,t]

Parameters

Cost[e,t]

Incidence[e,t]

Sets

Employees

Tasks

Indices

e

t

Wildcard

*

---

# Entity References

Employees are referenced only by **Employee_ID** (E1, E2, ...).

Tasks are referenced only by **Task_ID** (T1, T5, ...).

Employee names and task names must never appear in symbolic constraints.

---

# Constants

Allowed constants

- 0
- 1
- Positive integers
- Positive decimal numbers

Examples

0

1

5

25

100

0.75

---

# Comparison Operators

==

!=

<

<=

>

>=

---

# Arithmetic Operators

+

-

*

Parentheses may be used for grouping.

Examples

x[E1,T1] + x[E2,T2]

SUM x[E1,*] + SUM x[E2,*]

2 * x[E1,T3]

SUM x[E1,*] + SUM x[E2,*] - SUM x[E3,*]

---

# Logical Operators

AND

OR

NOT

---

# Quantifiers

FORALL

EXISTS

---

# Aggregation Operators

SUM

COUNT

---

# Conditional Filters

General form

FORALL variable

WHERE condition

expression

Supported conditions

==

!=

IN

NOT IN

Examples

FORALL e

WHERE e != E1

x[e,T5] == 0

---

FORALL e

WHERE e IN {E1,E2,E3}

SUM x[e,*] <= 1

---

FORALL t

WHERE t NOT IN {T3,T4}

x[E2,t] == 0

---

# Wildcards

`*` represents every element of a dimension.

Examples

x[E2,*]

x[*,T4]

---

# Mandatory Aggregation Rule

A wildcard represents a set, not a scalar.

Whenever `*` appears in a comparison, it **must** be wrapped with SUM or COUNT.

Valid

SUM x[E1,*] == 1

SUM x[E1,*] <= 1

SUM x[*,T5] == 1

COUNT x[E1,*] <= 1

Invalid

x[E1,*] == 1

x[E1,*] <= 1

x[*,T5] == 1

This rule has no exceptions.

---

# Decision Variable Syntax

x[E1,T3]

x[E2,*]

x[*,T3]

---

# Linear Expressions

Linear expressions may contain decision variables, SUM/COUNT expressions, constants, and arithmetic operators.

Examples

x[E1,T1] + x[E2,T3]

SUM x[E1,*] + SUM x[E2,*]

SUM x[*,T1] + SUM x[*,T2]

2 * x[E1,T4] + x[E2,T5]

SUM x[E1,*] + SUM x[E2,*] - SUM x[E3,*]

Linear expressions may appear on either side of a comparison.

---

# Assignment Expressions

Examples

x[E1,T2] == 1

x[E3,T5] == 0

x[E4,T1] != 1

---

# Quantified Expressions

General form

FORALL variable

expression

Nested quantifiers are allowed.

Examples

FORALL t

x[E2,t] == 0

---

FORALL e

x[e,T5] == 0

---

FORALL e

FORALL t

x[e,t] <= Incidence[e,t]

---

# Conditional Quantifiers

General form

FORALL variable

WHERE condition

expression

Examples

FORALL e

WHERE e != E1

x[e,T7] == 0

---

FORALL t

WHERE t != T2

x[E5,t] == 0

---

# Summation Expressions

General form

SUM expression

comparison

constant

Examples

SUM x[E2,*] <= 1

SUM x[E1,*] == 0

SUM x[*,T4] == 1

SUM x[E5,*] >= 1

---

# Multi-Term Constraints

Examples

SUM x[E1,*] + SUM x[E2,*] <= 1

SUM x[E1,*] + SUM x[E2,*] == 1

x[E1,T1] + x[E1,T2] == 1

x[E2,T3] + x[E2,T4] <= 1

x[E3,T5] + x[E4,T5] <= 1

SUM x[E1,*] + SUM x[E2,*] + SUM x[E3,*] <= 2

---

# Group Constraints

Examples

SUM x[E1,*] + SUM x[E2,*] <= 1

SUM x[E3,*] + SUM x[E4,*] == 1

SUM x[E1,*] + SUM x[E2,*] + SUM x[E5,*] <= 2

SUM x[*,T1] + SUM x[*,T2] == 1

---

# Count Expressions

General form

COUNT expression

comparison

constant

Examples

COUNT x[E2,*] <= 1

COUNT x[*,T3] == 1

---

# Logical Expressions

Examples

x[E1,T1] == 1

AND

x[E2,T2] == 0

---

x[E1,T3] == 1

OR

x[E2,T3] == 1

---

NOT

x[E3,T7] == 1

---

# Soft Constraints

General form

SOFT

WEIGHT = integer

expression

Examples

SOFT

WEIGHT = 20

x[E2,T5] == 1

---

SOFT

WEIGHT = 10

SUM x[E3,*] >= 1

---

# Canonical Constraint Patterns

Employee unavailable

FORALL t

x[E1,t] == 0

---

Assign employee to task

x[E2,T4] == 1

---

Forbid employee from task

x[E3,T5] == 0

---

Allow only one employee for a task

FORALL e

WHERE e != E2

x[e,T7] == 0

---

Employees cannot work together

SUM x[E1,*] + SUM x[E2,*] <= 1

---

Exactly one employee should work

SUM x[E1,*] + SUM x[E2,*] == 1

---

At least one employee should work

SUM x[E1,*] + SUM x[E2,*] >= 1

---

Employee must perform one of two tasks

x[E1,T1] + x[E1,T2] == 1

---

Employee may only perform specific tasks

FORALL t

WHERE t NOT IN {T3,T4}

x[E2,t] == 0

---

Only one employee among a group may work

SUM x[E1,*] + SUM x[E2,*] + SUM x[E3,*] <= 1

---

# Invalid Expressions

Employee names

x[Rahul,T1] == 1

Task names

x[E1,Dashboard] == 1

Unknown variable

y[E1,T2] == 1

Unknown parameter

Priority[E1,T2]

Python

if employee == ...

Pyomo

model.x[E1,T2]

Natural language

Assign Rahul to Task 2

---

# Output Rules

Output only valid DSL.

No explanations.

No markdown.

No comments.

No code fences.

If multiple constraints are generated, separate them with one blank line.

Every constraint must conform to this grammar and be parsable by the optimization parser.