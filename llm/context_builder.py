import json


def build_context(
    employees_df,
    tasks_df,
    incidence_matrix,
    current_constraints=None,
):
    """
    Builds the dynamic context for the LLM.
    """

    current_constraints = current_constraints or []

    context = {
        "employees": [
            {
                "id": row["Employee_ID"],
                "name": row["Employee_Name"],
                "skills": sorted(row["Skill_Set"])
                if isinstance(row["Skill_Set"], set)
                else row["Skill_Set"],
            }
            for _, row in employees_df.iterrows()
        ],
        "tasks": [
            {
                "id": row["Task_ID"],
                "name": row["Task_Name"],
                "required_skills": sorted(row["Required_Skills_Set"])
                if isinstance(row["Required_Skills_Set"], set)
                else row["Required_Skills_Set"],
            }
            for _, row in tasks_df.iterrows()
        ],
        "incidence": {
            emp: [
                task
                for task in incidence_matrix.columns
                if incidence_matrix.loc[emp, task] == 1
            ]
            for emp in incidence_matrix.index
        },
        "current_constraints": current_constraints,
    }

    return context


def context_to_json(context):
    return json.dumps(context, indent=4)