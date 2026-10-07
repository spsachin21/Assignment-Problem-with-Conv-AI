# Natural Language to DSL Translation Examples

These examples illustrate how natural language business rules are translated into DSL constraints.

The LLM should infer the translation pattern from these examples.

Always generate valid DSL.

Never generate Python, Pyomo or explanatory text.

---

## Employee Availability

### Example 1

User

Employee E2 is unavailable.

DSL

FORALL t

x[E2,t] == 0

---

### Example 2

User

Assign Employee E1 to Task T3.

DSL

x[E1,T3] == 1

---

### Example 3

User

Never assign Employee E4 to Task T7.

DSL

x[E4,T7] == 0

---

## Task Ownership

### Example 4

User

Only Employee E2 may perform Task T5.

DSL

FORALL e

WHERE e != E2

x[e,T5] == 0

---

### Example 5

User

Assign Task T8 only to Employee E7.

DSL

FORALL e

WHERE e != E7

x[e,T8] == 0

---

## Employee Workload

### Example 6

User

Employee E3 should receive no work.

DSL

SUM x[E3,*] == 0

---

### Example 7

User

Employee E6 must receive at least one task.

DSL

SUM x[E6,*] >= 1

---

### Example 8

User

Employee E5 may perform at most one task.

DSL

SUM x[E5,*] <= 1

---

## Soft Preferences

### Example 9

User

Prefer assigning Employee E4 to Task T6.

DSL

SOFT

WEIGHT = 20

x[E4,T6] == 1

---

### Example 10

User

If possible, assign Employee E8.

DSL

SOFT

WEIGHT = 15

SUM x[E8,*] >= 1

---

## Employee Relationships

### Example 11

User

Employees E1 and E2 cannot work together.

DSL

SUM x[E1,*] + SUM x[E2,*] <= 1

---

### Example 12

User

Exactly one of Employees E3 and E4 should work.

DSL

SUM x[E3,*] + SUM x[E4,*] == 1

---

### Example 13

User

At least one of Employees E5 and E6 must be assigned.

DSL

SUM x[E5,*] + SUM x[E6,*] >= 1

---

### Example 14

User

Only one of Employees E7, E8 and E9 may work.

DSL

SUM x[E7,*] + SUM x[E8,*] + SUM x[E9,*] <= 1

---

## Task Choices

### Example 15

User

Employee E2 must work on either Task T3 or Task T4.

DSL

x[E2,T3] + x[E2,T4] == 1

---

### Example 16

User

Employee E5 may work only on Tasks T1 or T2.

DSL

FORALL t

WHERE t NOT IN {T1,T2}

x[E5,t] == 0

---

### Example 17

User

Employee E6 cannot work on Tasks T8, T9 or T10.

DSL

x[E6,T8] == 0

x[E6,T9] == 0

x[E6,T10] == 0

---

## Employee Groups

### Example 18

User

Employees E1, E2 and E3 are unavailable.

DSL

FORALL t

x[E1,t] == 0

FORALL t

x[E2,t] == 0

FORALL t

x[E3,t] == 0

---

### Example 19

User

Only Employees E4 and E5 may perform Task T6.

DSL

FORALL e

WHERE e NOT IN {E4,E5}

x[e,T6] == 0

---

### Example 20

User

Employees except E7 may not perform Task T8.

DSL

FORALL e

WHERE e != E7

x[e,T8] == 0

---

## Combined Constraints

### Example 21

User

Assign Employee E1 to Task T2 and do not assign Employee E3.

DSL

x[E1,T2] == 1

FORALL t

x[E3,t] == 0

---

### Example 22

User

Employee E2 should preferably work on Task T5 and Employee E6 must not work on Task T5.

DSL

SOFT

WEIGHT = 20

x[E2,T5] == 1

x[E6,T5] == 0

---

### Example 23

User

Only one of Employees E1 and E2 may work, and if one works it should preferably be E1.

DSL

SUM x[E1,*] + SUM x[E2,*] <= 1

SOFT

WEIGHT = 10

SUM x[E1,*] >= 1

---

## Conditional Filters

### Example 24

User

Employees E2, E4 and E6 cannot perform Task T3.

DSL

FORALL e

WHERE e IN {E2,E4,E6}

x[e,T3] == 0

---

### Example 25

User

Employee E5 cannot perform any task except T2 and T4.

DSL

FORALL t

WHERE t NOT IN {T2,T4}

x[E5,t] == 0