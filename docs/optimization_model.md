

Formulates employee-task assignment problem as a **Binary Integer Programming (BIP)** optimization model.

---

# Sets

| Symbol | Description |
|---------|-------------|
| **E** | Set of employees |
| **T** | Set of tasks |

---

# Parameters

| Symbol | Description | Entries
|---------|-------------|-----------|
| **cₑₜ** | Cost of assigning employee *e* to task *t* | Cost matrix
| **aₑₜ** | Skill compatibility parameter | Incidence matrix

where

\[
a_{et}=
\begin{cases}
1,&\text{if employee }e\text{ possesses all skills required for task }t\\
0,&\text{otherwise}
\end{cases}
\]

---

# Decision Variable

\[
x_{et}=
\begin{cases}
1,&\text{if employee }e\text{ is assigned to task }t\\
0,&\text{otherwise}
\end{cases}
\]

---

# Objective Function

Minimize the total assignment cost.

\[
\min
\sum_{e\in E}
\sum_{t\in T}
c_{et}x_{et}
\]

---

# Constraints

## 1. Employee Assignment

Each employee can perform **at most one task**.

\[
\sum_{t\in T}
x_{et}
\le
1
\qquad
\forall e\in E
\]

---

## 2. Task Assignment

Each task must be assigned to **exactly one employee**.

\[
\sum_{e\in E}
x_{et}
=
1
\qquad
\forall t\in T
\]

---

## 3. Skill Compatibility

Assignments are allowed only when the employee satisfies the required skills.

\[
x_{et}
\le
a_{et}
\qquad
\forall e\in E,\;
t\in T
\]

---

## 4. Binary Variables

\[
x_{et}
\in
\{0,1\}
\qquad
\forall e\in E,\;
t\in T
\]

---

# Model Summary

The optimization model minimizes the total assignment cost while ensuring that:

- Every task is assigned exactly once.
- An employee performs at most one task.
- Employees are assigned only to tasks for which they possess the required skills.
- Decision variables remain binary.
- Additionally, users can add custom business rules without violating the predefined optimization constraints.