import random
from collections import Counter

import pandas as pd

# ==========================================================
# Reproducibility
# ==========================================================

random.seed(42)

# ==========================================================
# Parameters
# ==========================================================

NUM_EMPLOYEES = 300
NUM_TASKS = 300

MIN_EMPLOYEE_SKILLS = 5
MAX_EMPLOYEE_SKILLS = 10

MIN_TASK_SKILLS = 1
MAX_TASK_SKILLS = 6

# Desired difficulty distribution
EASY_TASKS = 90
MEDIUM_TASKS = 150
HARD_TASKS = 60

# Qualification thresholds
# Easy   : 40+ employees
# Medium : 15-39 employees
# Hard   : 5-14 employees

HARD_MIN = 5
MEDIUM_MIN = 15
EASY_MIN = 40

# ==========================================================
# Skill Pool
# ==========================================================

SKILLS = [
    "Python",
    "Java",
    "SQL",
    "Machine Learning",
    "Data Analysis",
    "Cloud",
    "DevOps",
    "Testing",
    "Project Management",
    "Communication"
]

# ==========================================================
# Random Names
# ==========================================================

FIRST_NAMES = [
    "Alice","Bob","Charlie","David","Emma","Frank","Grace",
    "Henry","Ivy","Jack","Karen","Leo","Mia","Nathan",
    "Olivia","Paul","Quinn","Ryan","Sophia","Thomas",
    "Uma","Victor","William","Xavier","Yara","Zane"
]

LAST_NAMES = [
    "Smith","Johnson","Williams","Brown","Jones",
    "Garcia","Miller","Davis","Wilson","Taylor",
    "Anderson","Thomas","Moore","Martin","Lee",
    "Walker","Hall","Allen","Young","King"
]

TASK_PREFIX = [
    "Backend",
    "Frontend",
    "Database",
    "Analytics",
    "Security",
    "Cloud",
    "Reporting",
    "Automation",
    "Testing",
    "Migration",
    "Integration",
    "Support",
    "Monitoring"
]

TASK_SUFFIX = [
    "Module",
    "API",
    "Dashboard",
    "Pipeline",
    "Portal",
    "Framework",
    "Engine",
    "Platform",
    "Service",
    "System"
]

# ==========================================================
# Generate Employees
# ==========================================================

employees = []

employee_skill_sets = []

for i in range(NUM_EMPLOYEES):

    num_skills = random.randint(
        MIN_EMPLOYEE_SKILLS,
        MAX_EMPLOYEE_SKILLS
    )

    skills = random.sample(SKILLS, num_skills)

    employee_skill_sets.append(set(skills))

    employees.append({
        "Employee_ID": f"E{i+1}",
        "Employee_Name": f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
        "Skills": ",".join(sorted(skills))
    })

employees_df = pd.DataFrame(employees)

print("Employees generated.")

# ==========================================================
# Skill Frequency
# ==========================================================

counter = Counter()

for skills in employee_skill_sets:
    counter.update(skills)

weights = [counter[s] for s in SKILLS]

# ==========================================================
# Helper Functions
# ==========================================================

def weighted_skill_sample(k):

    selected = []

    available = SKILLS.copy()
    available_weights = weights.copy()

    for _ in range(k):

        skill = random.choices(
            available,
            weights=available_weights,
            k=1
        )[0]

        idx = available.index(skill)

        selected.append(skill)

        available.pop(idx)
        available_weights.pop(idx)

    return selected


def qualified_employee_count(required):

    required = set(required)

    count = 0

    for emp in employee_skill_sets:

        if required.issubset(emp):
            count += 1

    return count

# ==========================================================
# Generate Tasks
# ==========================================================

tasks = []

easy = 0
medium = 0
hard = 0

task_id = 1

while len(tasks) < NUM_TASKS:

    num_required = random.randint(
        MIN_TASK_SKILLS,
        MAX_TASK_SKILLS
    )

    required = weighted_skill_sample(num_required)

    qualified = qualified_employee_count(required)

    difficulty = None

    if qualified >= EASY_MIN:
        difficulty = "Easy"

    elif qualified >= MEDIUM_MIN:
        difficulty = "Medium"

    elif qualified >= HARD_MIN:
        difficulty = "Hard"

    else:
        continue

    if difficulty == "Easy" and easy >= EASY_TASKS:
        continue

    if difficulty == "Medium" and medium >= MEDIUM_TASKS:
        continue

    if difficulty == "Hard" and hard >= HARD_TASKS:
        continue

    if difficulty == "Easy":
        easy += 1

    elif difficulty == "Medium":
        medium += 1

    else:
        hard += 1

    task_name = (
        random.choice(TASK_PREFIX)
        + "_"
        + random.choice(TASK_SUFFIX)
        + "_"
        + str(task_id)
    )

    tasks.append({
        "Task_ID": f"T{task_id}",
        "Task_Name": task_name,
        "Required_Skills": ",".join(sorted(required))
    })

    task_id += 1

tasks_df = pd.DataFrame(tasks)

print("Tasks generated.")

# ==========================================================
# Cost Matrix
# ==========================================================

cost_rows = []

for i in range(NUM_EMPLOYEES):

    row = {
        "Employee_ID": f"E{i+1}"
    }

    for j in range(NUM_TASKS):

        row[f"T{j+1}"] = random.randint(10, 100)

    cost_rows.append(row)

cost_df = pd.DataFrame(cost_rows)

print("Cost matrix generated.")

# ==========================================================
# Save Files
# ==========================================================

employees_df.to_csv(
    "employees_300@.csv",
    index=False
)

tasks_df.to_csv(
    "tasks_300@.csv",
    index=False
)

cost_df.to_csv(
    "cost_matrix_300@.csv",
    index=False
)

# ==========================================================
# Summary
# ==========================================================

print("\nDataset Generated Successfully!")

print(f"Employees : {len(employees_df)}")
print(f"Tasks     : {len(tasks_df)}")
print(f"Easy      : {easy}")
print(f"Medium    : {medium}")
print(f"Hard      : {hard}")

print("\nCSV Files Created")
print("employees.csv")
print("tasks.csv")
print("cost_matrix.csv")