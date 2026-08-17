"""
CASE-001 — THE OBSERVER EFFECT
Clean reproducible source.

Generated from the audited canonical Colab cells.

This file is intended to run independently of notebook state.
"""

from pathlib import Path
import json
import hashlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt



# ============================================================
# CANONICAL PARAMETERS
# ============================================================

A = 0.95
B = 0.1
K = 11.0
N = 120
X0 = 1.0

ROOT = Path("/content/AEVUMARD_CASE_001")
RUN = ROOT / "source" / "clean_reproduction" / "generated"

BENCHMARK = ROOT / "benchmark"
FIGURES = RUN / "figures"
DATA = RUN / "data"

RUN.mkdir(parents=True, exist_ok=True)
FIGURES.mkdir(parents=True, exist_ok=True)
DATA.mkdir(parents=True, exist_ok=True)



# ============================================================
# CORE DYNAMICS
# ============================================================

def simulate_stable(
    A=A,
    B=B,
    K=K,
    N=N,
    x0=X0,
):
    x = np.zeros(N + 1)
    u = np.zeros(N)

    x[0] = x0

    for k in range(N):
        u[k] = -K * x[k]
        x[k + 1] = A * x[k] + B * u[k]

    return x, u


def simulate_failure(
    A=A,
    B=B,
    K=K,
    N=N,
    x0=X0,
):
    x = np.zeros(N + 1)
    u = np.zeros(N)

    x[0] = x0

    previous_y = x0

    for k in range(N):
        y = x[k]

        u[k] = -K * previous_y

        x[k + 1] = A * x[k] + B * u[k]

        previous_y = y

    return x, u


def simulate_decoupled(
    A=A,
    B=B,
    K=K,
    N=N,
    x0=X0,
):
    x = np.zeros(N + 1)
    u = np.zeros(N)

    x[0] = x0

    for k in range(N):
        u[k] = -K * x[k]
        x[k + 1] = A * x[k] + B * u[k]

    return x, u


def simulate_predictor(
    A_true=A,
    B_true=B,
    A_model=A,
    B_model=B,
    K=K,
    N=N,
    x0=X0,
    model_error=0.0,
):
    x = np.zeros(N + 1)
    u = np.zeros(N)

    x[0] = x0

    previous_y = x0
    previous_control = 0.0

    factor = 1.0 + model_error

    Am = A_model * factor
    Bm = B_model * factor

    for k in range(N):

        # Prediction from delayed observation
        x_hat = Am * previous_y + Bm * previous_control

        u[k] = -K * x_hat

        x[k + 1] = (
            A_true * x[k]
            + B_true * u[k]
        )

        previous_y = x[k]
        previous_control = u[k]

    return x, u
