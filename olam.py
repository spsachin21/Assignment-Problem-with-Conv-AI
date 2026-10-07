# from ollama import chat

# response = chat(
#     model="qwen2.5:3b",
#     messages=[
#         {
#             "role": "user",
#             "content": "What is 2+2?"
#         }
#     ]
# )

# print(response["message"]["content"])

# import gurobipy as gp
# print(gp.gurobi.version())
# print(gp.Env().getParamInfo("ComputeServer"))

import gurobipy as gp

try:
    m = gp.Model()
    print("Model created successfully")
except gp.GurobiError as e:
    print(e)