# FOG COMPUTING — SUPPLEMENTARY AND DATA

This section provides supplementary material, validation summaries, and reproducibility data associated with ongoing research on Fog Computing, queueing-aware performance analysis, network economics, and iFogSim2-based simulation.

## Available data

- [`agreement_metrics.csv`](./data/agreement_metrics.csv) — agreement metrics between analytical and simulated latency results.
- [`bland_altman_summary.csv`](./data/bland_altman_summary.csv) — Bland–Altman summary statistics for providers A and B.
- [`failure_gate_counts_by_family.csv`](./data/failure_gate_counts_by_family.csv) — validation-gate failure counts grouped by scenario family.
- [`replace_with_interarrival_trace_s_validation_summary.csv`](./data/replace_with_interarrival_trace_s_validation_summary.csv) — revised interarrival-trace validation statistics.
- [`trace_validation_old_vs_new.csv`](./data/trace_validation_old_vs_new.csv) — comparison between the previous and revised trace validation results.
- [`updated_results_summary.csv`](./data/updated_results_summary.csv) — global validation summary for the 218 simulation rows.
- [`updated_summary_by_family.csv`](./data/updated_summary_by_family.csv) — observed and projected validation results grouped by scenario family.

## Supplementary Instrumentation for p95/p99

- [`TailLatencyRecorder.java`](./instrumentation/TailLatencyRecorder.java) — dependency-free tuple-level end-to-end latency recorder for providers A and B.

This supplementary instrumentation stores latency samples per provider, computes the mean, p95 and p99 using R-7 / NumPy-like linear interpolation, tracks SLA violations, and exports both a summary CSV and a raw tuple-level latency CSV. It is intended to support tail-latency analysis and reproducibility of p95/p99 measurements in the iFogSim2 validation workflow.

## Research context

The validation workflow compares analytical queueing models with discrete-event simulation results from iFogSim2. The simulation implementation uses FCFS provider-level scheduling, explicit queue/service/system-time instrumentation, and separate measurements for ingress, egress, network usage, energy, SLA violations, and analytical-versus-simulated error metrics.

The revised trace diagnostics are reported separately from the original iFogSim2 validation output so that observed simulation results and projected trace-gate effects remain distinguishable.

## Citation and reuse

These files are intended to support transparency and reproducibility of the associated Fog Computing research. When reusing the data, please cite the corresponding publication once its bibliographic information is available.

---

**Researcher:** Jairo Sacoto, PhD — Universidad Politécnica Salesiana, Ecuador  
**Research Group:** GIHP4C — Cloud Computing, High Performance Computing and Smart Cities
