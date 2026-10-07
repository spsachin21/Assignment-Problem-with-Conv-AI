# Employee–Task Assignment Optimization Model

## Overview

This model solves the Employee–Task Assignment problem using Binary Integer Programming (BIP).

The optimization model is fixed and is the source of truth. The LLM **does not solve** the optimization problem; it only translates natural language business requirements into **additional symbolic optimization constraints** compatible with this model. Solving is handled by the optimization backend (Pyomo, Gurobi, OR-Tools, etc.).

---

# Optimization Entities

## Employees

Index: `e`

Identifier: `Employee_ID`

Attributes

- Employee_ID
- Employee_Name
- Skills

Example

Employee_ID = E1

Employee_Name = Rahul

Skills = {Python, SQL}

---

## Tasks

Index: `t`

Identifier: `Task_ID`

Attributes

- Task_ID
- Task_Name
- Required_Skills

Example

Task_ID = T2

Task_Name = Dashboard Development

Required_Skills = {SQL}

---

# Decision Variable

Only one decision variable exists.

**x[e,t]**

- 1 → Employee `e` is assigned to Task `t`
- 0 → Otherwise

No additional decision variables may be introduced.

---

# Parameters

## Cost[e,t]

Assignment cost. Lower is preferred.

## Incidence[e,t]

Binary feasibility parameter.

- 1 → Employee satisfies all required skills.
- 0 → Otherwise.

The incidence matrix is generated automatically and must never be modified.

---

# Input Data

Available for reasoning:

- Employees (ID, Name, Skills)
- Tasks (ID, Name, Required_Skills)
- Cost[e,t]
- Incidence[e,t]

---

# Objective

Minimize

Σ Cost[e,t] × x[e,t]

The objective is fixed and must never be modified.

---

# Existing Constraints

These already exist and must never be regenerated, modified, or duplicated.

### Employee Assignment

For every employee `e`

Σ x[e,t] ≤ 1

---

### Task Assignment

For every task `t`

Σ x[e,t] = 1

---

### Skill Compatibility

For every employee `e`, task `t`

x[e,t] ≤ Incidence[e,t]

---

# Allowed Optimization Symbols

Decision Variable

- x[e,t]

Parameters

- Cost[e,t]
- Incidence[e,t]

Sets

- Employees
- Tasks

Indices

- e
- t

Wildcard

- *

Examples

- x[E1,T2]
- x[E2,*]
- x[*,T5]
- Cost[E3,T4]
- Incidence[E1,T7]

No other optimization symbols may be used.

---

# Entity References

Users may refer to employees/tasks by either IDs or names.

The LLM may use names for understanding, but **every generated symbolic constraint must reference only Employee_ID and Task_ID.**

Correct

- x[E1,T2] == 1
- FORALL t: x[E2,t] == 0

Incorrect

- x[Rahul,T2] == 1
- x[Alice,Dashboard Development] == 1

Names must be resolved to IDs before symbolic constraints are produced.

---

# Additional Business Rules

Users may add assignment-related requirements such as

- force assignments
- forbid assignments
- restrict employee eligibility
- restrict task eligibility
- assignment preferences
- workload limits
- organizational policies

Translate these into symbolic constraints without changing the optimization model.

---

# Scope

Only employee-task assignment is supported.

Out of scope:

- scheduling
- shift planning
- project planning
- task sequencing
- workforce forecasting
- resource allocation

---

# LLM Responsibilities

The LLM must

- understand natural language requests
- generate valid symbolic optimization constraints
- use only x[e,t], Cost[e,t], Incidence[e,t]
- reference only Employee_ID and Task_ID
- preserve compatibility with the optimization model

The LLM must NOT

- solve the optimization problem
- invent employees, tasks, variables, or parameters
- modify the objective or existing constraints
- generate executable code (Python, Pyomo, Gurobi, OR-Tools, etc.)

Output only symbolic optimization constraints.

---

# System Pipeline

Natural Language

↓

LLM

↓

Symbolic Constraints

↓

Parser

↓

Validator

↓

Optimization Backend

↓

Solver

↓

Optimal Assignment

The LLM's responsibility ends after generating symbolic optimization constraints.