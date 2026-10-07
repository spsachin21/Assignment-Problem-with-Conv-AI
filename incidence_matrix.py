import pandas as pd

def create_incidence_matrix(employees, tasks):
    incidence=pd.DataFrame(
        index=employees["Employee_ID"],
        columns=tasks["Task_ID"]
    )

    for _,emp in employees.iterrows():  #return row index(_ --means notuseful) and row itself as a series
        for _,task in tasks.iterrows():
            if task["Required_Skills_Set"].issubset(emp["Skill_Set"]):
                incidence.loc[emp["Employee_ID"],task["Task_ID"]]=1
            else:
                incidence.loc[emp["Employee_ID"],task["Task_ID"]] =0

    return incidence            

