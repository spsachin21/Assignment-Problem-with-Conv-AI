from dataclasses import dataclass
import pandas as pd

@dataclass
class OptimizationResult:

    solver:str

    status:str

    objective: float | None

    runtime: float | None

    gap: float |None

    assignments: pd.DataFrame

    solver_statistics: dict

    solver_log: str