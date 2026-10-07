import pandas as pd
import random
# -----------------------------
# Parameters
# -----------------------------
NUM_EMPLOYEES = 5
NUM_TASKS = 4

SKILLS = ["S1", "S2", "S3", "S4", "S5"]

EMPLOYEE_NAMES = [
    "Alice",
    "Bob",
    "Charlie",
    "Diana",
    "Ethan"
]

TASK_NAMES = [
    "Data_Cleaning",
    "Backend_Development",
    "Reporting",
    "System_Testing"
]

# -----------------------------
# Generate Employees
# -----------------------------
employees = []

for i in range(NUM_EMPLOYEES):

    # Each employee has 3-5 skills
    num_skills = random.randint(3, 5)
    emp_skills = random.sample(SKILLS, num_skills)

    employees.append({
        "Employee_ID": f"E{i+1}",
        "Employee_Name": EMPLOYEE_NAMES[i],
        "Skills": ",".join(sorted(emp_skills))
    })

employees_df = pd.DataFrame(employees)

# -----------------------------
# Generate Tasks
# -----------------------------
tasks = []

for i in range(NUM_TASKS):

    # Each task requires 1-3 skills
    num_required = random.randint(1, 3)
    req_skills = random.sample(SKILLS, num_required)

    tasks.append({
        "Task_ID": f"T{i+1}",
        "Task_Name": TASK_NAMES[i],
        "Required_Skills": ",".join(sorted(req_skills))
    })

tasks_df = pd.DataFrame(tasks)

# -----------------------------
# Generate Cost Matrix
# -----------------------------
cost_data = []

for i in range(NUM_EMPLOYEES):

    row = {"Employee_ID": f"E{i+1}"}

    for j in range(NUM_TASKS):
        row[f"T{j+1}"] = random.randint(5, 20)

    cost_data.append(row)

cost_df = pd.DataFrame(cost_data)

# -----------------------------
# Save CSV Files
# -----------------------------
employees_df.to_csv("employees.csv", index=False)
tasks_df.to_csv("tasks.csv", index=False)
cost_df.to_csv("cost_matrix.csv", index=False)

print("CSV files generated successfully!")

print("\nEmployees")
print(employees_df)

print("\nTasks")
print(tasks_df)

print("\nCost Matrix")
print(cost_df)