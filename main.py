
from input_data import load_cost, load_data
from incidence_matrix import create_incidence_matrix
# from solvers.gurobi_solver import solve_assignment_gurobipy
from solvers.gurobi_sol import solve_assignment_gurobipy
from solvers.pyomo_sol import solve_assignment_pyomo
# from solvers.pyomo_glpk import solve_assignment_pyomo
from solvers.ortools import solve_assignment_ortools
from solvers.ortool_cpsat import solve_assignment_cpsat
from solvers.optimization_result import OptimizationResult
from llm.context_builder import (build_context, context_to_json)
from llm.prompt_builder import build_prompt
from constraint_engine.parser import parse_constraints
from llm.llm_client import ask_llm
from llm.example_retriever import (retrieve_examples, format_examples)
from llm.solution_context_builder import (build_solution_context, solution_context_to_json)
from llm.solution_prompt_builder import build_solution_prompt
from utils.model_viewer import show_model
import time
import io


import streamlit as st
import pandas as pd
from config import *
# import gurobipy as gp
# from gurobipy import GRB

# Session State Initialization
# =====================================================
# RESET APPLICATION
# =====================================================

def reset_application():
    keys_to_clear = [
        # Uploaded files
        "employee_file",
        "task_file",
        "cost_file",

        # Sample dataset
        "use_sample",

        # Constraint state
        "approved_constraints",
        "pending_constraint",
        "current_constraints",

        # Query / LLM state
        "last_query",
        "response",
        "prompt",
        "elapsed",
        "retrieved_examples",

        # Optimization
        "result",

        # Solution chat
        "solution_chat_history",

        # Dataset display checkboxes
        "show_sample_emp",
        "show_sample_task",
        "show_sample_cost",
        "show_sample_incidence",
        "show_emp",
        "show_task",
        "show_cost",
        "show_incidence",
    ]

    for key in keys_to_clear:
        st.session_state.pop(key, None)

    st.rerun()

if "approved_constraints" not in st.session_state:
    st.session_state.approved_constraints = []

if "pending_constraint" not in st.session_state:
    st.session_state.pending_constraint = None

if "response" not in st.session_state:
    st.session_state.response = None

if "elapsed" not in st.session_state:
    st.session_state.elapsed = 0.0

if "retrieved_examples" not in st.session_state:
    st.session_state.retrieved_examples = []

if "current_constraints" not in st.session_state:
    st.session_state.current_constraints=[]    

if "last_query" not in st.session_state:
    st.session_state.last_query = None

if "prompt" not in st.session_state:
    st.session_state.prompt = None


st.title("🎯Employee Task Assignment")

st.markdown(
    "<div style='margin-left: 60px;'>Hey! Let me save your manual efforts.</div>",
    unsafe_allow_html=True
)

st.write("") # for gap

# Upload tabs
tab_col, reset_col = st.columns([5, 1])
employee_tab, task_tab, cost_tab=st.tabs(["Employees data", "Tasks data", "Costs data"])
with employee_tab:
    employee_file = st.file_uploader("Upload your employees data", type ="csv", key= "employee_file")

with task_tab:
    task_file = st.file_uploader("Upload your tasks data", type = "csv", key= "task_file")

with cost_tab:
    cost_file = st.file_uploader("Upload your costs data", type="csv", key= "cost_file")

employees_df=None
task_df=None
cost_df=None

use_sample = st.checkbox(
    "Use sample dataset",
    value=False,
    key= "use_sample",
    help="Load the sample dataset included with the application."
)
if use_sample:

    employees_df, tasks_df = load_data("employees.csv", "tasks.csv")
    cost_df = load_cost("cost_matrix.csv")
    incidence_matrix = create_incidence_matrix(employees_df, tasks_df)
    st.success("Loaded sample dataset.")

    tab_col, reset_col = st.columns([5, 1])

    with tab_col:
        emp_data_tab, task_data_tab, cost_data_tab, incidence_tab = st.tabs(
                ["Employees", "Tasks", "Costs", "Incidence_matrix"]
            )
        
        with emp_data_tab:
            if st.checkbox("Show employees data", key="show_sample_emp"):
                st.dataframe(
                    employees_df,
                    width=1200,
                    # width="stretch",
                    hide_index=True
                )

        with task_data_tab:
            if st.checkbox("Show tasks data", key="show_sample_task"):
                st.dataframe(
                    tasks_df,
                    width="stretch",
                    hide_index=True
                )

        with cost_data_tab:
            if st.checkbox("Show costs matrix", key="show_sample_cost"):
                st.dataframe(
                    cost_df,
                    width="stretch",
                    hide_index=False
                )

        with incidence_tab:
            if st.checkbox("Show incidence matrix", key="show_sample_incidence"):
                st.dataframe(
                    incidence_matrix,
                    width="stretch"
                )
    with reset_col:
            if st.button("↻ Reset", key="sample_reset_button"):
                reset_application()            

#Only continue once all files are uploaded    
if  employee_file and task_file and cost_file:

    employees_df, tasks_df = load_data(employee_file, task_file)
    cost_df = load_cost(cost_file)
    incidence_matrix = create_incidence_matrix(employees_df, tasks_df)

    st.success("All files uploaded successfully!")

    tab_col, reset_col = st.columns([5, 1])

    with tab_col:
        emp_data_tab, task_data_tab, cost_data_tab, incidence_tab = st.tabs(
                ["Employees", "Tasks", "Costs", "Incidence_matrix"]
            )

        with emp_data_tab:
            if st.checkbox("Show employees data", key="show_emp"):
                st.dataframe(
                    employees_df,
                    width="stretch",
                    hide_index=True
                )

        with task_data_tab:
            if st.checkbox("Show tasks data", key="show_task"):
                st.dataframe(
                    tasks_df,
                    width="stretch",
                    hide_index=True
                )

        with cost_data_tab:
            if st.checkbox("Show costs matrix", key="show_cost"):
                st.dataframe(
                    cost_df,
                    width="stretch",
                    hide_index=True
                )

        with incidence_tab:
            if st.checkbox("Show incidence matrix", key="show_incidence"):
                st.dataframe(
                    incidence_matrix,
                    width="stretch"
                )    
    with reset_col:
        if st.button("↻ Reset", key= "main_reset_button"):
            reset_application()            

# st.sidebar.divider()



# with st.sidebar.expander(
#     "📘 Optimization Model",
#     expanded=False
# ):

#     st.markdown("""
# View the complete mathematical formulation
# used by the optimization engine.
# """)

#     if st.button(
#         "Open Model",
#         use_container_width=True
#     ):
#         st.session_state.show_model = True

#Solver settings
# st.sidebar.divider()

SOLVERS = {
    "Gurobi": solve_assignment_gurobipy,
    "Pyomo (GLPK)": solve_assignment_pyomo,
    "OR-Tools (SCIP)": solve_assignment_ortools,
    "OR-Tools (CP-SAT)": solve_assignment_cpsat,
}

st.sidebar.header("Solver Settings")
solver=st.sidebar.selectbox(
    "Select Solver",
    ["Gurobi", "Pyomo (GLPK)", "OR-Tools (SCIP)", "OR-Tools (CP-SAT)"]
)

solve_function=SOLVERS[solver]

mode=st.sidebar.radio("Stopping Criterion",
                      ["Optimality", "Time Limit"]
                      )

time_limit = None

if mode == "Time Limit":
    time_limit = st.sidebar.number_input(
        "Time Limit (seconds)",
        min_value =1,
        value=60
    )

# run = st.sidebar.button("Start assignment")
st.markdown("""
<style>
section[data-testid="stSidebar"] button {
    background-color: #d32f2f;
    color: white;
    border: none;
}

section[data-testid="stSidebar"] button:hover {
    background-color: #b71c1c;
    color: white;
}
</style>
""", unsafe_allow_html=True)

run = st.sidebar.button("Start assignment")

if run:
    if employees_df is not None and tasks_df is not None and cost_df is not None:

        with st.status("Running optimization...", expanded=True) as status:

            st.write("Loading data...")
            st.write("Building optimization model...")

            if mode == "Optimality":
                st.write("Solving until optimality...")
            else:
                st.write(f" Solving with a time limit of {time_limit} seconds...")

            parsed_constraints = []
            if "approved_constraints" in st.session_state:
                    for item in st.session_state.approved_constraints:
                        parsed_constraints.extend(item["parsed"])

            result = solve_function(
                    incidence_matrix=incidence_matrix,
                    cost_matrix=cost_df,
                    employees_df=employees_df,
                    time_limit=time_limit,
                    parsed_constraints=parsed_constraints
                )

            st.session_state["result"] = result

            st.write("Processing solution...")

            status.update(
                label="Assignment completed!",
                state="complete"
            )
        
    else:
        st.error("Please provide all the required data first.")       

if "result" in st.session_state:
    with st.expander("View Optimization Results", expanded=True):
        result = st.session_state["result"]

        # st.divider()
        st.header("Assignment Results")

        if "active_result_tab" not in st.session_state:
            st.session_state.active_result_tab = "📈 Summary"

        active_tab = st.segmented_control(
            "Result section",
            ["📈 Summary", "📋 Assignments", "⚙️ Solver Statistics", "💬 Solution Chat"],
            key="active_result_tab",
            label_visibility="collapsed"
        )    

        if active_tab == "📈 Summary":
            if result.status=="Infeasible":
                st.error(f"Status: {result.status}")
            else:    
                st.success(f"Status: {result.status}")

            c1, c2, c3 = st.columns(3)

            c1.metric("Objective", result.objective)
            c2.metric("Runtime", f"{result.runtime:.3f} s")
            c3.metric(
                "Gap",
                "N/A" if result.gap is None else f"{100*result.gap:.2%}"
            )

        if active_tab == "📋 Assignments":
            st.dataframe(
                result.assignments,
                width="stretch"
            )

            # Create Excel file in memory
            output = io.BytesIO()

            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                result.assignments.to_excel(
                    writer,
                    index=False,
                    sheet_name="Assignments"
                )

            output.seek(0)

            st.download_button(
                label="📥 Download Assignments (Excel)",
                data=output,
                file_name="employee_assignments.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        if active_tab == "⚙️ Solver Statistics":
            for key, value in result.solver_statistics.items():
                st.metric(key, value) 

        if active_tab == "💬 Solution Chat":
            st.subheader("Ask questions about the optimization result")

            if "solution_chat_history" not in st.session_state:
                st.session_state.solution_chat_history = []

            # Display previous conversation

            for msg in st.session_state.solution_chat_history:

                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

            question = st.chat_input(
                "Ask about this solution..."
            )

            if question:

                st.session_state.solution_chat_history.append(
                    {
                        "role": "user",
                        "content": question
                    }
                )

                with st.chat_message("user"):
                    st.markdown(question)

                # ---------------------------------------
                # Build Context
                # ---------------------------------------

                context = build_solution_context(

                    result=result,

                    approved_constraints=st.session_state.approved_constraints,

                    employees_df=employees_df,

                    tasks_df=tasks_df

                )

                context_json = solution_context_to_json(
                    context
                )

                prompt = build_solution_prompt(

                    context_json,

                    question

                )

                with st.spinner("Analyzing solution..."):

                    # answer = ask_llm(prompt)
                    answer = ask_llm(
                        prompt,
                        expect_json=False
                    )
                # ---------------------------------------
                # Handle LLM Response
                # ---------------------------------------

                # if isinstance(answer, dict):

                #     if "answer" in answer:

                #         response = answer["answer"]

                #     elif "response" in answer:

                #         response = answer["response"]

                #     else:

                #         response = str(answer)

                # else:

                #     response = str(answer)

                st.session_state.solution_chat_history.append(

                    {
                        "role": "assistant",
                        "content": answer
                    }

                )

                with st.chat_message("assistant"):

                    st.markdown(answer)             

            
        
            

        # summary_tab, assignment_tab, stats_tab, chat_tab = st.tabs(
        #     ["📈 Summary", "📋 Assignments", "⚙️ Solver Statistics", "💬 Solution Chat"]
        # )

        # with summary_tab:
        #     if result.status=="Infeasible":
        #         st.error(f"Status: {result.status}")
        #     else:    
        #         st.success(f"Status: {result.status}")

        #     c1, c2, c3 = st.columns(3)

        #     c1.metric("Objective", result.objective)
        #     c2.metric("Runtime", f"{result.runtime:.3f} s")
        #     c3.metric(
        #         "Gap",
        #         "N/A" if result.gap is None else f"{100*result.gap:.2%}"
        #     )

        # with assignment_tab:

        #     st.dataframe(
        #         result.assignments,
        #         width="stretch"
        #     )

        #     # Create Excel file in memory
        #     output = io.BytesIO()

        #     with pd.ExcelWriter(output, engine="openpyxl") as writer:
        #         result.assignments.to_excel(
        #             writer,
        #             index=False,
        #             sheet_name="Assignments"
        #         )

        #     output.seek(0)

        #     st.download_button(
        #         label="📥 Download Assignments (Excel)",
        #         data=output,
        #         file_name="employee_assignments.xlsx",
        #         mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        #     )

        # with stats_tab:

        #     for key, value in result.solver_statistics.items():
        #         st.metric(key, value) 

        # with chat_tab:  
        #     st.subheader("Ask questions about the optimization result")

        #     if "solution_chat_history" not in st.session_state:
        #         st.session_state.solution_chat_history = []

        #     # Display previous conversation

        #     for msg in st.session_state.solution_chat_history:

        #         with st.chat_message(msg["role"]):
        #             st.markdown(msg["content"])

        #     question = st.chat_input(
        #         "Ask about this solution..."
        #     )

        #     if question:

        #         st.session_state.solution_chat_history.append(
        #             {
        #                 "role": "user",
        #                 "content": question
        #             }
        #         )

        #         with st.chat_message("user"):
        #             st.markdown(question)

        #         # ---------------------------------------
        #         # Build Context
        #         # ---------------------------------------

        #         context = build_solution_context(

        #             result=result,

        #             approved_constraints=st.session_state.approved_constraints,

        #             employees_df=employees_df,

        #             tasks_df=tasks_df

        #         )

        #         context_json = solution_context_to_json(
        #             context
        #         )

        #         prompt = build_solution_prompt(

        #             context_json,

        #             question

        #         )

        #         with st.spinner("Analyzing solution..."):

        #             # answer = ask_llm(prompt)
        #             answer = ask_llm(
        #                 prompt,
        #                 expect_json=False
        #             )
        #         # ---------------------------------------
        #         # Handle LLM Response
        #         # ---------------------------------------

        #         # if isinstance(answer, dict):

        #         #     if "answer" in answer:

        #         #         response = answer["answer"]

        #         #     elif "response" in answer:

        #         #         response = answer["response"]

        #         #     else:

        #         #         response = str(answer)

        #         # else:

        #         #     response = str(answer)

        #         st.session_state.solution_chat_history.append(

        #             {
        #                 "role": "assistant",
        #                 "content": answer
        #             }

        #         )

        #         with st.chat_message("assistant"):

        #             st.markdown(answer)             


# Chat Interface
# =====================================================
# CHAT PROCESSING
# =====================================================

user_query = st.chat_input(
    "Enter a business rule..."
)


if user_query:

    if employees_df is None:

        st.error(
            "Please upload datasets first."
        )

    else:

        start_time = time.perf_counter()


        with st.status(
            "Generating constraint...",
            expanded=True
        ) as status:


            if "approved_constraints" not in st.session_state:

                st.session_state.approved_constraints = []

            context_constraints = []    
            for item in st.session_state.approved_constraints:

                context_constraints.append(
                    {
                        "query": item["query"],
                        "family": item["family"],
                        "dsl": item["dsl"],
                    }
                )    

            status.write("Retrieving similar examples...")

            retrieved_examples = retrieve_examples(user_query)
            st.session_state.retrieved_examples = retrieved_examples

            status.write(
                "Building context..."
            )
        
            context = build_context(
                employees_df,
                tasks_df,
                incidence_matrix,
                context_constraints
            )


            context_json = context_to_json(context)


            status.write(
                "Building prompt..."
            )


            prompt = build_prompt(
                context_json,
                user_query
            )


            status.write(
                "Calling LLM..."
            )


            response = ask_llm(prompt)




            status.update(
                label="Constraint generated",
                state="complete"
            )



        elapsed = time.perf_counter()-start_time


        # store raw response

        st.session_state.response=response
        st.session_state.elapsed=elapsed

        st.session_state.last_query = user_query
        
        if "last_query" not in st.session_state:
            st.session_state.last_query = None


        try:

            parsed_constraints = parse_constraints(
                response
            )


            if len(parsed_constraints)>0:

                st.session_state.pending_constraint = (
                    parsed_constraints
                )

                st.success(
                    "Constraint generated. Awaiting approval."
                )


        except Exception as e:

            st.error(
                f"Constraint parsing failed: {e}"
            )

# Display Previous Results (survives Streamlit reruns)
if (
    st.session_state.last_query is not None
    and st.session_state.response is not None
):

    st.success(
        f"Response generated in **{st.session_state.elapsed:.2f} seconds**"
    )

    st.json(st.session_state.response)

    with st.expander("🔍 Retrieved Similar Examples", expanded=False):

        examples = st.session_state.retrieved_examples

        if not examples:
            st.info("No similar examples found.")

        else:

            for i, ex in enumerate(examples, start=1):

                st.markdown(f"### Example {i}")

                col1, col2 = st.columns(2)

                with col1:
                    st.metric("Hybrid Score", f"{ex['score']:.3f}")

                with col2:
                    st.write(f"**Family:** {ex['family']}")

                st.write("**Tags**")
                st.write(", ".join(ex["tags"]))

                st.write("**User Query Example**")
                st.code(ex["user"])

                st.write("**DSL Constraint**")
                st.code(ex["dsl"])

                st.divider()


    # # Prompt


    # with st.expander("📄 View Prompt", expanded=False):

    #     st.code(st.session_state.prompt)
    # =====================================================
# CONSTRAINT APPROVAL
# =====================================================

if st.session_state.pending_constraint:


    st.subheader(
        "🔎 Constraint Review"
    )


    for c in st.session_state.pending_constraint:


        st.write(
            "Constraint Type:",
            c.constraint_type
        )


        st.code(
            c.dsl
        )

        data = {
        "dsl": c.dsl,
        "expression_type": c.lhs.type,
        "variable": c.lhs.variable,
        "operator": c.operator,
        "rhs": c.rhs,
        "family": c.family,
        }

        if c.lhs.type == "variable":
            data["indices"] = c.lhs.indices
        elif c.lhs.type == "sum":
            data["employees"] = c.lhs.employees
            data["tasks"] = c.lhs.tasks  

        st.json(data)
        # st.json(
        #     {
        #         "lhs":{
        #             "type":c.lhs.type,
        #             "variable":c.lhs.variable
        #         },
        #         "operator":c.operator,
        #         "rhs":c.rhs
        #     }
        # )



    col1,col2 = st.columns(2)


    with col1:

        approve = st.button(
            "✅ Approve Constraint"
        )


    with col2:

        reject = st.button(
            "❌ Discard Constraint"
        )



    if approve:

        # -------------------------
        # Store for History (UI)
        # -------------------------

        st.session_state.approved_constraints.append(
            {
                "query": st.session_state.last_query,
                "family": st.session_state.response["constraint_family"],
                "dsl": [
                    c.dsl
                    for c in st.session_state.pending_constraint
                ],
                "parsed": st.session_state.pending_constraint
            }
        )

        # -------------------------
        # Store for Optimization
        # -------------------------

        st.session_state.current_constraints.extend(
            st.session_state.pending_constraint
        )

        st.session_state.pending_constraint = None

        st.success(
            "Constraint added to optimization model."
        )

        st.rerun()



    if reject:


        st.session_state.pending_constraint=None


        st.warning(
            "Constraint discarded."
        )


        st.rerun()

# =====================================================
# CONSTRAINT HISTORY
# =====================================================


with st.expander(
    "📜 Approved Constraint History",
    expanded=True
):

    if len(st.session_state.approved_constraints) == 0:

        st.info("No approved constraints.")

    else:

        remove_index = None

        for i, item in enumerate(st.session_state.approved_constraints):

            with st.expander(
                f"Constraint {i+1}: {item['query']}"
            ):

                st.markdown(
                    f"**Constraint Family:** `{item['family']}`"
                )

                st.markdown("### Generated DSL")

                st.json(item["dsl"])

                st.markdown("### Parsed Representation")

                for pc in item["parsed"]:

                    parsed_data = {
                        "expression_type": pc.lhs.type,
                        "variable": pc.lhs.variable,
                        "operator": pc.operator,
                        "rhs": pc.rhs,
                    }

                    if pc.lhs.type == "variable":

                        parsed_data["indices"] = pc.lhs.indices

                    else:

                        parsed_data["employees"] = pc.lhs.employees
                        parsed_data["tasks"] = pc.lhs.tasks

                    st.json(parsed_data)

                if st.button(
                    "🗑 Remove Constraint",
                    key=f"remove_{i}"
                ):

                    remove_index = i

        if remove_index is not None:

            removed = st.session_state.approved_constraints.pop(remove_index)

            for pc in removed["parsed"]:
                if pc in st.session_state.current_constraints:
                    st.session_state.current_constraints.remove(pc)

            st.success("Constraint removed.")

            st.rerun()   

# if st.session_state.get("show_model", False):

#     st.header("📘 Mathematical Formulation")

#     show_model()
# for _ in range(11):
#     st.sidebar.write("")

# if st.sidebar.button(
#     "🔄 Reset",
#     use_container_width=True
# ):
#     reset_application()
    
@st.dialog("Employee Task Assignment Model")
def optimization_model_dialog():
    show_model()

for _ in range(28):
    st.sidebar.write("")
    
st.sidebar.divider()

if st.sidebar.button(
    "View Optimization Model",
    use_container_width=True
):
    optimization_model_dialog()