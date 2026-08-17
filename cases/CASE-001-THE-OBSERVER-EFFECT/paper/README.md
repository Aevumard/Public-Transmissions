# CASE-001 — THE OBSERVER EFFECT

**Status:** Resolved  
**Class:** Deterministic feedback instability  
**Type:** Controlled mathematical benchmark

## Result

A system that is stable without observation delay becomes unstable when a
one-sample observation delay is introduced into the feedback path.

### Baseline

- spectral radius: `0.150000`
- stable: `True`

### Failure

- spectral radius: `1.048808848`
- stable: `False`
- maximum `|x|`: `326.303262296441`

### Resolution

Removing the delayed telemetry signal from the feedback-critical path restores
stability:

- maximum `|x|`: `1.000000000000`
- final `|x|`: `0.000000000000`

## Evidence

The repository contains the numerical sweeps, trajectory data and figures used
to construct the case.

The full investigation is documented in:

`paper/CASE-001.md`
