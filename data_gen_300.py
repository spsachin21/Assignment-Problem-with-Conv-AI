import random
from itertools import combinations
from collections import Counter

import pandas as pd

# ==========================================================
# Reproducibility
# ==========================================================

random.seed(42)

# ==========================================================
# Parameters
# ==========================================================

NUM_EMPLOYEES = 600
NUM_TASKS = 550

MIN_EMPLOYEE_SKILLS = 5
MAX_EMPLOYEE_SKILLS = 10

MIN_TASK_SKILLS = 1
MAX_TASK_SKILLS = 6

# Desired task distribution
NUM_EASY = 150
NUM_MEDIUM = 300
NUM_HARD = 100

# Qualification thresholds
EASY_MIN = 40
MEDIUM_MIN = 15
HARD_MIN = 5

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
# Employee Names
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

# ==========================================================
# Task Names
# ==========================================================

TASK_PREFIX = [
    "Backend","Frontend","Database","Analytics",
    "Security","Cloud","Reporting","Automation",
    "Testing","Migration","Integration","Support",
    "Monitoring"
]

TASK_SUFFIX = [
    "Module","API","Dashboard","Pipeline",
    "Portal","Framework","Engine",
    "Platform","Service","System"
]

# ==========================================================
# Generate Employees
# ==========================================================

employees = []
employee_skill_sets = []

for i in range(NUM_EMPLOYEES):

    k = random.randint(
        MIN_EMPLOYEE_SKILLS,
        MAX_EMPLOYEE_SKILLS
    )

    skills = set(random.sample(SKILLS, k))

    employee_skill_sets.append(skills)

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

for s in employee_skill_sets:
    counter.update(s)

print(counter)

# ==========================================================
# Generate ALL Skill Combinations
# ==========================================================

all_combinations = []

for r in range(
    MIN_TASK_SKILLS,
    MAX_TASK_SKILLS + 1
):

    all_combinations.extend(combinations(SKILLS, r))

print(f"Total combinations = {len(all_combinations)}")

# ==========================================================
# Classify Combinations
# ==========================================================
# ==========================================================
# Evaluate Every Skill Combination
# ==========================================================

combination_stats = []

for combo in all_combinations:

    required = set(combo)

    qualified = sum(
        required.issubset(emp)
        for emp in employee_skill_sets
    )

    combination_stats.append({
        "combo": combo,
        "qualified": qualified
    })

# ----------------------------------------------------------
# Sort by number of qualified employees
# ----------------------------------------------------------

combination_stats.sort(
    key=lambda x: x["qualified"]
)

print(f"\nTotal combinations: {len(combination_stats)}")

# ----------------------------------------------------------
# Dynamic Difficulty Split
# ----------------------------------------------------------

n = len(combination_stats)

hard_end = int(0.20 * n)      # Bottom 20%
medium_end = int(0.70 * n)    # Next 50%
# Remaining Top 30% -> Easy

hard_pool = combination_stats[:hard_end]
medium_pool = combination_stats[hard_end:medium_end]
easy_pool = combination_stats[medium_end:]

print(f"Hard combinations   : {len(hard_pool)}")
print(f"Medium combinations : {len(medium_pool)}")
print(f"Easy combinations   : {len(easy_pool)}")

print()

print("Qualification Range")

print(
    "Hard   :",
    hard_pool[0]["qualified"],
    "-",
    hard_pool[-1]["qualified"]
)

print(
    "Medium :",
    medium_pool[0]["qualified"],
    "-",
    medium_pool[-1]["qualified"]
)

print(
    "Easy   :",
    easy_pool[0]["qualified"],
    "-",
    easy_pool[-1]["qualified"]
)

# ==========================================================
# Build Tasks
# ==========================================================
# ==========================================================
# Build Tasks
# ==========================================================

tasks = []

task_number = 1


def build_task(combo):

    global task_number

    return {

        "Task_ID": f"T{task_number}",

        "Task_Name":
            random.choice(TASK_PREFIX)
            + "_"
            + random.choice(TASK_SUFFIX)
            + "_"
            + str(task_number),

        "Required_Skills":
            ",".join(sorted(combo))
    }


def add_tasks(pool, number):

    global task_number

    # Shuffle for randomness
    pool = pool.copy()

    random.shuffle(pool)

    # Use every combination once first
    used = min(number, len(pool))

    for i in range(used):

        combo = pool[i]["combo"]

        tasks.append(
            build_task(combo)
        )

        task_number += 1

    # If more tasks are required, allow repeats
    remaining = number - used

    if remaining > 0:

        for _ in range(remaining):

            combo = random.choice(pool)["combo"]

            tasks.append(
                build_task(combo)
            )

            task_number += 1


add_tasks(easy_pool, 150)
add_tasks(medium_pool, 300)
add_tasks(hard_pool, 100)

random.shuffle(tasks)

# Renumber IDs

for i, task in enumerate(tasks, start=1):

    task["Task_ID"] = f"T{i}"

tasks_df = pd.DataFrame(tasks)
print("Tasks generated.")

# ==========================================================
# Cost Matrix
# ==========================================================

cost = []

for i in range(NUM_EMPLOYEES):

    row = {

        "Employee_ID": f"E{i+1}"

    }

    for j in range(NUM_TASKS):

        row[f"T{j+1}"] = random.randint(10, 100)

    cost.append(row)

cost_df = pd.DataFrame(cost)

print("Cost matrix generated.")

# ==========================================================
# Save Files
# ==========================================================

employees_df.to_csv(
    "employees_600_550.csv",
    index=False
)

tasks_df.to_csv(
    "tasks_600_550.csv",
    index=False
)

cost_df.to_csv(
    "cost_matrix_600_550.csv",
    index=False
)

# ==========================================================
# Summary
# ==========================================================

print()
print("======================================")
print("Dataset Generated Successfully")
print("======================================")

print("Employees :", len(employees_df))
print("Tasks     :", len(tasks_df))

print("Easy Tasks   :", NUM_EASY)
print("Medium Tasks :", NUM_MEDIUM)
print("Hard Tasks   :", NUM_HARD)

print()

print("Files Created")
print("employees_300.csv")
print("tasks_300.csv")
print("cost_matrix_300.csv")