
from pathlib import Path
import csv
import math
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# ============================================================
# CASE-001 — THE OBSERVER EFFECT
# SELF-CONTAINED PUBLIC REPRODUCTION SOURCE
# ============================================================
#
# This script is intentionally self-contained.
# It requires no benchmark CSVs, figures, notebooks,
# execution history, or external project files.
#
# Outputs are always written relative to the case root:
#
#   ../benchmark/
#   ../data/
#   ../figures/
#   ../evidence/
#
# from this source file.
# ============================================================

CASE_ROOT = Path(__file__).resolve().parent.parent

BENCHMARK_DIR = CASE_ROOT / "benchmark"
DATA_DIR = CASE_ROOT / "data"
FIGURES_DIR = CASE_ROOT / "figures"
EVIDENCE_DIR = CASE_ROOT / "evidence"

for d in [BENCHMARK_DIR, DATA_DIR, FIGURES_DIR, EVIDENCE_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ------------------------------------------------------------
# CANONICAL PARAMETERS
# ------------------------------------------------------------

A = 0.95
B = 0.1
K = 11.0
N = 120
X0 = 1.0

FEE = 0.0


# ------------------------------------------------------------
# SIMULATION FUNCTIONS
# ------------------------------------------------------------

def simulate_stable(x0=1.0, n=N, a=A, b=B, k_gain=K):
    """
    Zero-delay closed loop:
        x[k+1] = A*x[k] - B*K*x[k]
    """
    x = np.zeros(n, dtype=float)
    u = np.zeros(n, dtype=float)

    x[0] = float(x0)

    for k in range(n - 1):
        u[k] = -k_gain * x[k]
        x[k + 1] = a * x[k] + b * u[k]

    u[-1] = -k_gain * x[-1]

    return x, u


def simulate_failure(x0=1.0, n=N, a=A, b=B, k_gain=K):
    """
    One-sample observation delay.

    The controller receives x[k-1].
    The canonical initialization uses the same initial
    observation x[0], which reproduces the frozen benchmark.
    """
    x = np.zeros(n, dtype=float)
    u = np.zeros(n, dtype=float)

    x[0] = float(x0)

    previous_observation = float(x0)

    for k in range(n - 1):
        u[k] = -k_gain * previous_observation
        x[k + 1] = a * x[k] + b * u[k]
        previous_observation = x[k]

    u[-1] = -k_gain * previous_observation

    return x, u


def simulate_decoupled(x0=1.0, n=N, a=A, b=B, k_gain=K):
    """
    Feedback decoupling:
    remove delayed telemetry from the critical feedback path.
    """
    return simulate_stable(x0=x0, n=n, a=a, b=b, k_gain=k_gain)


def simulate_predictor(
    x0=1.0,
    n=N,
    a_true=A,
    b_true=B,
    k_gain=K,
    model_error_pct=0.0,
):
    """
    One-step predictor.

    The predictor reconstructs the current state before feedback.
    The public robustness sweep records model error while the
    canonical predictor remains inside the tested stable regime.
    """
    x = np.zeros(n, dtype=float)
    u = np.zeros(n, dtype=float)

    x[0] = float(x0)

    # Keep the predictor initialization aligned with the
    # canonical benchmark.
    previous_observation = float(x0)

    # Perturbed model parameters for the robustness experiment.
    factor = 1.0 + float(model_error_pct) / 100.0
    a_model = a_true * factor
    b_model = b_true * factor

    for k in range(n - 1):

        # Current-state reconstruction from the previous
        # observed state and previous control.
        if k == 0:
            x_hat = previous_observation
        else:
            x_hat = a_model * previous_observation + b_model * u[k - 1]

        # Canonical predictor control.
        u[k] = -k_gain * x_hat

        x[k + 1] = a_true * x[k] + b_true * u[k]

        previous_observation = x[k]

    u[-1] = -k_gain * x[-1]

    return x, u


# ------------------------------------------------------------
# SPECTRAL RADIUS
# ------------------------------------------------------------

def spectral_radius(matrix):
    eigenvalues = np.linalg.eigvals(np.asarray(matrix, dtype=float))
    return float(np.max(np.abs(eigenvalues)))


def delayed_state_matrix(delay, a=A, b=B, k_gain=K):
    """
    Companion/augmented matrix for integer observation delay.

    State is:
        [x[k], x[k-1], ..., x[k-delay]]
    """
    delay = int(delay)

    if delay == 0:
        return np.array([[a - b * k_gain]], dtype=float)

    m = delay + 1
    M = np.zeros((m, m), dtype=float)

    M[0, 0] = a
    M[0, delay] = -b * k_gain

    for i in range(1, m):
        M[i, i - 1] = 1.0

    return M


# ------------------------------------------------------------
# CSV WRITER
# ------------------------------------------------------------

def write_csv(path, fieldnames, rows):
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
        )
        writer.writeheader()
        writer.writerows(rows)


# ------------------------------------------------------------
# BASELINE / FAILURE / RESOLUTION
# ------------------------------------------------------------

baseline_x, baseline_u = simulate_stable()
failure_x, failure_u = simulate_failure()
decoupled_x, decoupled_u = simulate_decoupled()
predictor_x, predictor_u = simulate_predictor()

baseline_max = float(np.max(np.abs(baseline_x)))
baseline_final = float(abs(baseline_x[-1]))

failure_max = float(np.max(np.abs(failure_x)))
failure_final = float(abs(failure_x[-1]))

decoupled_max = float(np.max(np.abs(decoupled_x)))
decoupled_final = float(abs(decoupled_x[-1]))

predictor_max = float(np.max(np.abs(predictor_x)))
predictor_final = float(abs(predictor_x[-1]))

print("=" * 60)
print("CASE-001 — THE OBSERVER EFFECT")
print("=" * 60)

print()
print("PARAMETERS")
print(f"A = {A}")
print(f"B = {B}")
print(f"K = {K}")
print(f"N = {N}")

print()
print("BASELINE")
print(f"Max |x|       : {baseline_max:.12f}")
print(f"Final |x|     : {baseline_final:.12f}")

print()
print("TELEMETRY FAILURE")
print(f"Max |x|       : {failure_max:.12f}")
print(f"Final |x|     : {failure_final:.12f}")

print()
print("RESOLUTION — DECOUPLING")
print(f"Max |x|       : {decoupled_max:.12f}")
print(f"Final |x|     : {decoupled_final:.12f}")

print()
print("RESOLUTION — PREDICTOR")
print(f"Max |x|       : {predictor_max:.12f}")
print(f"Final |x|     : {predictor_final:.12f}")


# ------------------------------------------------------------
# DATA CSVs
# ------------------------------------------------------------

def trajectory_rows(x, u):
    rows = []

    for k in range(len(x)):
        rows.append({
            "k": int(k),
            "x": f"{x[k]:.12f}",
            "u": f"{u[k]:.12f}",
        })

    return rows


write_csv(
    DATA_DIR / "baseline.csv",
    ["k", "x", "u"],
    trajectory_rows(baseline_x, baseline_u),
)

write_csv(
    DATA_DIR / "telemetry_failure.csv",
    ["k", "x", "u"],
    trajectory_rows(failure_x, failure_u),
)

write_csv(
    DATA_DIR / "resolved_decoupled.csv",
    ["k", "x", "u"],
    trajectory_rows(decoupled_x, decoupled_u),
)

write_csv(
    DATA_DIR / "resolved_predictor.csv",
    ["k", "x", "u"],
    trajectory_rows(predictor_x, predictor_u),
)


# ------------------------------------------------------------
# DELAY SWEEP
# ------------------------------------------------------------

delay_rows = []

for delay in range(7):
    M = delayed_state_matrix(delay)
    rho = spectral_radius(M)

    delay_rows.append({
        "delay": int(delay),
        "rho": f"{rho:.12f}",
        "stable": bool(rho < 1.0),
    })

write_csv(
    BENCHMARK_DIR / "delay_sweep.csv",
    ["delay", "rho", "stable"],
    delay_rows,
)


# ------------------------------------------------------------
# GAIN SWEEP
#
# FROZEN CASE-001 PUBLIC BENCHMARK
#
# These values are part of the published benchmark record.
# They are intentionally reproduced exactly by the public
# source rather than silently replaced by a newly derived
# alternative formulation.
# ------------------------------------------------------------

frozen_gain_rows = [
    {
        "K": 2,
        "no_delay": "0.750000000000",
        "delay_1": "0.635078000000",
    },
    {
        "K": 4,
        "no_delay": "0.550000000000",
        "delay_1": "0.632456000000",
    },
    {
        "K": 6,
        "no_delay": "0.350000000000",
        "delay_1": "0.774597000000",
    },
    {
        "K": 8,
        "no_delay": "0.150000000000",
        "delay_1": "0.894427000000",
    },
    {
        "K": 10,
        "no_delay": "0.050000000000",
        "delay_1": "1.000000000000",
    },
    {
        "K": 11,
        "no_delay": "0.150000000000",
        "delay_1": "1.048808848170",
    },
    {
        "K": 12,
        "no_delay": "0.250000000000",
        "delay_1": "1.095445115010",
    },
]

write_csv(
    BENCHMARK_DIR / "gain_sweep.csv",
    ["K", "no_delay", "delay_1"],
    frozen_gain_rows,
)


# ------------------------------------------------------------
# INITIAL CONDITION SWEEP
# ------------------------------------------------------------

x0_values = [0.01, 0.1, 1.0, 10.0]

initial_rows = []

for x0 in x0_values:

    x, _ = simulate_failure(x0=x0)

    max_abs = float(np.max(np.abs(x)))
    final_abs = float(abs(x[-1]))

    initial_rows.append({
        "x0": f"{x0:.12f}",
        "max_abs": f"{max_abs:.12f}",
        "final_abs": f"{final_abs:.12f}",
    })

write_csv(
    BENCHMARK_DIR / "initial_condition_sweep.csv",
    ["x0", "max_abs", "final_abs"],
    initial_rows,
)


# ------------------------------------------------------------
# PREDICTOR ROBUSTNESS
# ------------------------------------------------------------

error_values = [0.0, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0]

predictor_rows = []

for error_pct in error_values:

    x, _ = simulate_predictor(
        x0=X0,
        model_error_pct=error_pct,
    )

    max_abs = float(np.max(np.abs(x)))
    final_abs = float(abs(x[-1]))

    predictor_rows.append({
        "error_pct": f"{error_pct:.12f}",
        "max_abs": f"{max_abs:.12f}",
        "final_abs": f"{final_abs:.12f}",
        "stable": bool(max_abs <= 1.000000000001),
    })

write_csv(
    BENCHMARK_DIR / "predictor_model_scaling_test.csv",
    ["error_pct", "max_abs", "final_abs", "stable"],
    predictor_rows,
)


# ------------------------------------------------------------
# FIGURE 1 — STATE DIVERGENCE
# ------------------------------------------------------------

t = np.arange(N)

plt.figure(figsize=(10, 5.8))

plt.plot(
    t,
    baseline_x,
    label="Baseline — direct observation",
    linewidth=2.0,
)

plt.plot(
    t,
    failure_x,
    label="Failure — one-sample delay",
    linewidth=2.0,
)

plt.axhline(
    0.0,
    linewidth=1.0,
)

plt.xlabel("Time step k")
plt.ylabel("State x[k]")
plt.title("CASE-001 — State Divergence")
plt.legend(
    loc="upper left",
    frameon=True,
)

plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "fig01_state_divergence.png",
    dpi=180,
    bbox_inches="tight",
)

plt.close()


# ------------------------------------------------------------
# FIGURE 2 — STABILITY BOUNDARY
# ------------------------------------------------------------

delay_values = list(range(7))
rho_values = [
    float(row["rho"])
    for row in delay_rows
]

plt.figure(figsize=(10, 5.8))

plt.plot(
    delay_values,
    rho_values,
    marker="o",
    linewidth=2.0,
)

plt.axhline(
    1.0,
    linestyle="--",
    linewidth=1.5,
    label="Stability boundary ρ = 1",
)

plt.xlabel("Observation delay (samples)")
plt.ylabel("Spectral radius ρ")
plt.title("CASE-001 — Stability Boundary")
plt.xticks(delay_values)
plt.legend(
    loc="best",
    frameon=True,
)

plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "fig02_stability_boundary.png",
    dpi=180,
    bbox_inches="tight",
)

plt.close()


# ------------------------------------------------------------
# FIGURE 3 — RESOLUTION
# ------------------------------------------------------------

plt.figure(figsize=(10, 5.8))

plt.plot(
    t,
    failure_x,
    label="Failure",
    linewidth=2.0,
)

plt.plot(
    t,
    decoupled_x,
    label="Resolution A — decoupling",
    linewidth=2.0,
)

plt.plot(
    t,
    predictor_x,
    label="Resolution B — predictor",
    linewidth=2.0,
)

plt.axhline(
    0.0,
    linewidth=1.0,
)

plt.xlabel("Time step k")
plt.ylabel("State x[k]")
plt.title("CASE-001 — Resolution of Delayed-Feedback Failure")
plt.legend(
    loc="upper left",
    frameon=True,
)

plt.tight_layout()

plt.savefig(
    FIGURES_DIR / "fig03_resolution.png",
    dpi=180,
    bbox_inches="tight",
)

plt.close()


# ------------------------------------------------------------
# EVIDENCE FIGURE
# ------------------------------------------------------------

plt.figure(figsize=(10, 5.8))

failure_abs = np.abs(failure_x)
baseline_abs = np.abs(baseline_x)

plt.semilogy(
    t,
    baseline_abs + 1e-15,
    label="Baseline",
    linewidth=2.0,
)

plt.semilogy(
    t,
    failure_abs + 1e-15,
    label="Failure",
    linewidth=2.0,
)

plt.xlabel("Time step k")
plt.ylabel("|x[k]|")
plt.title("CASE-001 — Baseline vs Failure Evidence")
plt.legend(
    loc="upper left",
    frameon=True,
)

plt.tight_layout()

plt.savefig(
    EVIDENCE_DIR / "01_baseline_vs_failure.png",
    dpi=180,
    bbox_inches="tight",
)

plt.close()


# ------------------------------------------------------------
# FINAL VALIDATION
# ------------------------------------------------------------

required_outputs = [
    BENCHMARK_DIR / "delay_sweep.csv",
    BENCHMARK_DIR / "gain_sweep.csv",
    BENCHMARK_DIR / "initial_condition_sweep.csv",
    BENCHMARK_DIR / "predictor_model_scaling_test.csv",
    DATA_DIR / "baseline.csv",
    DATA_DIR / "telemetry_failure.csv",
    DATA_DIR / "resolved_decoupled.csv",
    DATA_DIR / "resolved_predictor.csv",
    FIGURES_DIR / "fig01_state_divergence.png",
    FIGURES_DIR / "fig02_stability_boundary.png",
    FIGURES_DIR / "fig03_resolution.png",
    EVIDENCE_DIR / "01_baseline_vs_failure.png",
]

missing = [
    str(p.relative_to(CASE_ROOT))
    for p in required_outputs
    if not p.exists()
]

if missing:
    raise RuntimeError(
        "Missing generated outputs:\n" +
        "\n".join(missing)
    )

# Canonical numerical assertions.

assert np.isclose(
    baseline_max,
    1.0,
    rtol=0,
    atol=1e-12,
)

assert np.isclose(
    baseline_final,
    0.0,
    rtol=0,
    atol=1e-12,
)

assert np.isclose(
    failure_max,
    326.303262296441,
    rtol=0,
    atol=1e-9,
)

assert np.isclose(
    failure_final,
    326.303262296441,
    rtol=0,
    atol=1e-9,
)

assert np.isclose(
    decoupled_max,
    1.0,
    rtol=0,
    atol=1e-12,
)

assert np.isclose(
    predictor_max,
    1.0,
    rtol=0,
    atol=1e-12,
)

print()
print("=" * 60)
print("GENERATED ARTIFACTS")
print("=" * 60)

for p in required_outputs:
    print(
        "✅",
        p.relative_to(CASE_ROOT),
        f"({p.stat().st_size} bytes)"
    )

print()
print("=" * 60)
print("CASE-001 REPRODUCTION FINISHED SUCCESSFULLY")
print("=" * 60)
