# Assignment-Problem-with-Conv-AI
AI-driven workforce assignment: turn everyday business rules into guaranteed optimal schedules with Gurobi, OR-Tools, and an interactive human-in-the-loop chat interface.
# 🎯 AI-Powered Workforce Task Assignment Engine

> **Turn plain-English business rules into mathematically optimal workforce schedules with LLMs, Gurobi, and OR-Tools.**

---

## 📌 Overview

Assigning employees to tasks while balancing costs, skills, and shifting corporate policies is an NP-hard combinatorial problem. Traditional methods require Operations Research engineers to hand-code mathematical constraints whenever rules change.

This application bridges **Generative AI** with **Rigorous Mathematical Optimization**:
1. **Natural Language Interface**: Users type everyday business policies (e.g., *"Alice can take at most 2 critical tasks"*).
2. **Deterministic Constraint Compilation**: An LLM parses the input into an intermediate Domain-Specific Language (DSL) backed by in-context few-shot examples.
3. **Human-in-the-Loop Review**: Managers inspect, verify, and approve the generated constraints before solving.
4. **Industrial-Grade Solvers**: The model is solved to proven optimality using your solver of choice (**Gurobi**, **Google OR-Tools**, or **Pyomo/GLPK**).
5. **Conversational Solution Analytics**: Chat directly with the solved assignment to understand trade-offs, bottlenecks, and costs.

---

## ⚡ Core Features

- **Multi-Solver Architecture**: Switch on the fly between:
  - **Gurobi** (MIP / Industrial Standard)
  - **Google OR-Tools (SCIP)** (MIP Solver)
  - **Google OR-Tools (CP-SAT)** (Constraint Programming)
  - **Pyomo (GLPK)** (Open-Source LP/MIP)
- **Zero-Code Rule Engine**: Parses natural-language prompts into formal algebraic constraints without writing code.
- **Dynamic Human-in-the-Loop (HITL)**: Inspect the parsed AST/JSON, verify indices and operators, and approve or discard rules safely.
- **Live Solver Statistics**: Track runtime, gap percentage, objective cost, and feasibility status in real time.
- **Post-Solve Solution Chat**: Ask questions directly about the solution (e.g., *"Why was Task 4 assigned to Bob instead of Alice?"*).
- **One-Click Excel Export**: Download final assignment schedules formatted for enterprise reporting.

---

## 🏗️ Architecture & Pipeline

```text
       User Prompt ("No junior dev on Task A")
                          │
                          ▼
            [ Few-Shot Example Retriever ]
                          │
                          ▼
             [ LLM Prompt & Context Builder ]
                          │
                          ▼
             [ Intermediate DSL Generation ]
                          │
                          ▼
              [ Constraint Parser / AST ]
                          │
                          ▼
             [ Human Approval / Rejection ]
                          │
                          ▼
  ┌─────────────────────────────────────────────────┐
  │         Mathematical Optimization Engine        │
  │     (Gurobi / OR-Tools CP-SAT / Pyomo / SCIP)   │
  └─────────────────────────────────────────────────┘
                          │
                          ▼
             [ Optimal Assignments & Cost ]
                          │
                          ▼
       [ Solution Q&A via Contextual LLM Chat ]
