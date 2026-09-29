# Data Availability Statement

For the manuscript submission, the repository contents support the following statement:

> The data and computational artifacts supporting this study are openly available in the public GitHub repository: https://github.com/jsacoto/Principal/tree/main/fog-computing-supplementary-and-data. The repository contains the consolidated 218-row iFogSim2 validation dataset, the reduced analysis dataset, the strict-validation failure subset, agreement and family-level summaries, the validated Java implementation, the MATLAB post-processing script, and supplementary tuple-level tail-latency instrumentation. The revised-trace effect is reported separately as a counterfactual diagnostic and is supported by the corresponding validation-summary files.

## Canonical files

- `data/ifogsim_218_with_observed_and_projected_validation.csv`
- `data/ifogsim_218_matlab_view.csv`
- `data/ifogsim_218_validation_failures.csv`
- `data/updated_results_summary.csv`
- `data/updated_summary_by_family.csv`
- `data/agreement_metrics.csv`
- `data/bland_altman_summary.csv`
- `data/failure_gate_counts_by_family.csv`
- `data/replace_with_interarrival_trace_s_validation_summary.csv`
- `data/trace_validation_old_vs_new.csv`
- `code/FogEconomicsIFogSim2StrictMM1V5.java`
- `code/analyze_ifogsim_218_trace_updated.m`
- `instrumentation/TailLatencyRecorder.java`

The canonical observed simulation results and the counterfactual revised-trace diagnostic are explicitly distinguished in both the data and the manuscript.
