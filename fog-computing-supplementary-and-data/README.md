# Fog Computing — Supplementary Data and Reproducibility Package

This directory contains the data, source code, validation summaries, and supplementary instrumentation supporting the manuscript on congestion-aware Stackelberg competition among fog service providers with iFogSim2 validation.

## Canonical validation dataset

- [`data/ifogsim_218_with_observed_and_projected_validation.csv`](./data/ifogsim_218_with_observed_and_projected_validation.csv) — canonical 218-row dataset containing the analytical variables, iFogSim2 measurements, validation metrics, observed strict-validation flag, and the explicitly identified counterfactual projected trace-gate flag.
- [`data/ifogsim_218_matlab_view.csv`](./data/ifogsim_218_matlab_view.csv) — reduced 218-row view used for analysis and plotting.
- [`data/ifogsim_218_validation_failures.csv`](./data/ifogsim_218_validation_failures.csv) — subset of rows that do not satisfy the observed strict criterion.

The observed iFogSim2 validation and the revised-trace counterfactual analysis are intentionally kept separate. `observedValidationPass` corresponds to observed simulation output; `projectedValidationPassAfterRevisedTraceGate` is a diagnostic projection and is not presented as a new iFogSim2 run.

## Validation summaries and diagnostics

- [`data/updated_results_summary.csv`](./data/updated_results_summary.csv) — global validation summary.
- [`data/updated_summary_by_family.csv`](./data/updated_summary_by_family.csv) — validation results grouped by scenario family.
- [`data/agreement_metrics.csv`](./data/agreement_metrics.csv) — agreement metrics between analytical and simulated latency.
- [`data/bland_altman_summary.csv`](./data/bland_altman_summary.csv) — Bland–Altman summary statistics.
- [`data/failure_gate_counts_by_family.csv`](./data/failure_gate_counts_by_family.csv) — strict-gate failure counts by family.
- [`data/replace_with_interarrival_trace_s_validation_summary.csv`](./data/replace_with_interarrival_trace_s_validation_summary.csv) — revised synthetic-trace validation summary.
- [`data/trace_validation_old_vs_new.csv`](./data/trace_validation_old_vs_new.csv) — comparison of the previous and revised trace diagnostics.

## Reproducibility code

- [`code/FogEconomicsIFogSim2StrictMM1V5.java`](./code/FogEconomicsIFogSim2StrictMM1V5.java) — validated iFogSim2 V5 implementation used for the controlled experiments.
- [`code/analyze_ifogsim_218_trace_updated.m`](./code/analyze_ifogsim_218_trace_updated.m) — MATLAB post-processing and validation script. By default, it reads the canonical consolidated dataset in `data/`.

## Supplementary tail-latency instrumentation

- [`instrumentation/TailLatencyRecorder.java`](./instrumentation/TailLatencyRecorder.java) — tuple-level latency recorder for mean, p95, p99, SLA violations, and raw latency samples.

## Minimal reproduction workflow

1. Place `FogEconomicsIFogSim2StrictMM1V5.java` in the iFogSim2 package `org.fog.test.perfeval` and execute the scenario set used in the study.
2. Use the canonical 218-row CSV in `data/` to reproduce the reported validation summaries and figure inputs.
3. Run `code/analyze_ifogsim_218_trace_updated.m` from the repository directory (or pass explicit file paths).
4. Use `TailLatencyRecorder.java` for future runs requiring tuple-level p95/p99 recording rather than inference from aggregate means.

## Data-availability wording for the manuscript

> The data and computational artifacts supporting this study are openly available in the public GitHub repository associated with the manuscript. The repository contains the consolidated 218-row iFogSim2 validation dataset, the reduced analysis dataset, the strict-validation failure subset, agreement and family-level summaries, the validated Java implementation, the MATLAB post-processing script, and supplementary tuple-level tail-latency instrumentation. The revised-trace effect is reported separately as a counterfactual diagnostic and is supported by the corresponding validation-summary files.

## Citation and reuse

These materials are provided to support transparency and computational reproducibility of the associated study. When reusing them, please cite the final published article once bibliographic information is available.

---

**Researcher:** Jairo Sacoto, PhD — Universidad Politécnica Salesiana, Ecuador  
**Research Group:** GIHP4C — Cloud Computing, High Performance Computing and Smart Cities
