import pandas as pd
import random

# -------------------------------
# Parameters
# -------------------------------
NUM_EMPLOYEES = 20
NUM_TASKS = 16
NUM_SKILLS = 20

random.seed(42)       # Remove this line if you want different data every run

skills = [f"S{i}" for i in range(1, NUM_SKILLS + 1)]

# -------------------------------
# Generate Employees
# -------------------------------
employees = []

for i in range(1, NUM_EMPLOYEES + 1):

    num_skills = random.randint(8, 20)

    employee_skills = random.sample(skills, num_skills)

    employees.append({
        "Employee_ID": f"E{i}",
        "Employee_Name": f"Employee_{i}",
        "Skills": ", ".join(sorted(employee_skills))
    })

employees_df = pd.DataFrame(employees)

# -------------------------------
# Generate Tasks
# -------------------------------
tasks = []

for i in range(1, NUM_TASKS + 1):

    num_required = random.randint(1, 10)

    required_skills = random.sample(skills, num_required)

    tasks.append({
        "TaskID": f"T{i}",
        "Required_Skills": ", ".join(sorted(required_skills))
    })

tasks_df = pd.DataFrame(tasks)

# -------------------------------
# Generate Cost Matrix
# -------------------------------

cost_matrix = pd.DataFrame(
    index=[f"E{i}" for i in range(1, NUM_EMPLOYEES + 1)],
    columns=[f"T{i}" for i in range(1, NUM_TASKS + 1)]
)

for emp in cost_matrix.index:
    for task in cost_matrix.columns:
        cost_matrix.loc[emp, task] = random.randint(10, 100)

cost_matrix = cost_matrix.astype(int)

# -------------------------------
# Save CSV Files
# -------------------------------

employees_df.to_csv("employees1.csv", index=False)
tasks_df.to_csv("tasks1.csv", index=False)
cost_matrix.to_csv("cost_matrix1.csv")

print("CSV files generated successfully!")