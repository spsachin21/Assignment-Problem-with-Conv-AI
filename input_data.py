import pandas as pd

def load_data(employee_file, task_file):
    employees=pd.read_csv(employee_file)
    tasks=pd.read_csv(task_file)

    employees["Skill_Set"]= employees['Skills'].apply(lambda x: set(skill.strip().lower() for skill in x.split(",")))

    tasks["Required_Skills_Set"]=tasks["Required_Skills"].apply(lambda x: set(skill.strip().lower() for skill in x.split(",")))

    employees.drop(columns=["Skills"], inplace=True)
    tasks.drop(columns=["Required_Skills"], inplace=True)
    
    return employees, tasks

def load_cost(cost_file):
    costs_data=pd.read_csv(cost_file)

    costs_matrix = costs_data.set_index("Employee_ID")

    return costs_matrix