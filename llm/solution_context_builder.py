import json


# ==========================================================
# Build Solution Context
# ==========================================================

def build_solution_context(
    result,
    approved_constraints,
    employees_df,
    tasks_df,
):
    """
    Builds the context supplied to the Solution Chat LLM.

    The context contains everything required to answer
    questions about the optimization result.
    """

    context = {}

    # ------------------------------------------------------
    # Optimization Summary
    # ------------------------------------------------------

    context["summary"] = {

        "solver": result.solver,

        "status": result.status,

        "objective": result.objective,

        "runtime_seconds": result.runtime,

        "optimality_gap": result.gap

    }

    # ------------------------------------------------------
    # Final Assignments
    # ------------------------------------------------------

    context["assignments"] = result.assignments.to_dict(
        orient="records"
    )

    # ------------------------------------------------------
    # Solver Statistics
    # ------------------------------------------------------

    context["solver_statistics"] = result.solver_statistics

    # ------------------------------------------------------
    # Solver Log
    # ------------------------------------------------------

    context["solver_log"] = result.solver_log

    # ------------------------------------------------------
    # Employee Data
    # ------------------------------------------------------

    employees = []

    for _, row in employees_df.iterrows():

        skills = row["Skill_Set"]

        if isinstance(skills, set):
            skills = sorted(skills)

        employees.append({

            "id": row["Employee_ID"],

            "name": row["Employee_Name"],

            "skills": skills

        })

    context["employees"] = employees

    # ------------------------------------------------------
    # Task Data
    # ------------------------------------------------------

    tasks = []

    for _, row in tasks_df.iterrows():

        required = row["Required_Skills_Set"]

        if isinstance(required, set):
            required = sorted(required)

        tasks.append({

            "id": row["Task_ID"],

            "name": row["Task_Name"],

            "required_skills": required

        })

    context["tasks"] = tasks

    # ------------------------------------------------------
    # Approved Constraint History
    # ------------------------------------------------------

    history = []

    for constraint in approved_constraints:

        history.append({

            "user_query": constraint["query"],

            "constraint_family": constraint["family"],

            "dsl_constraints": constraint["dsl"]

        })

    context["approved_constraints"] = history

    return context


# ==========================================================
# Convert Context to JSON
# ==========================================================

def solution_context_to_json(context):
    """
    Converts solution context to JSON.
    """

    return json.dumps(
        context,
        indent=4,
        default=str
    )