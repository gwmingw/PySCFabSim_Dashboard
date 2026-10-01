# SMT2020 LV/HM CR Baseline: 30-day run

## Run configuration

- Simulator: PySCFabSim-release, public repository `prosysscience/PySCFabSim-release`
- Dataset: simulator-bundled `SMT2020_LVHM` input files
- Dispatcher: `cr` (Critical Ratio)
- Algorithm mode: `l4m`
- Duration: 30 simulated days from 2018-01-01 00:00
- Random seed: 0
- Runtime: 1 min 24 sec (Python 3.13.7)
- Command, run from the `PySCFabSim` directory: `python main.py --days 30 --dataset SMT2020_LVHM --dispatcher cr --seed 0 --alg l4m`

## Results

| Metric | Result |
|---|---:|
| Completed lots | 1,679 |
| Throughput | 55.97 lots/day |
| On-time completions | 1,584 / 1,679 (94.34%) |
| Mean cycle time (completed lots, throughput-weighted) | 38.27 days |
| Tool groups in output | 106 |
| Tool groups with PM time reported | 96 |
| Tool groups with breakdown time reported | 105 |

Highest reported utilization by tool group:

| Tool group | Utilization |
|---|---:|
| Litho_BE_110 | 100.94% |
| Litho_FE_111 | 100.35% |
| DE_FE_71 | 96.11% |
| Litho_FE_92 | 95.44% |
| DE_FE_51 | 94.68% |

## Interpretation and limits

This is an initial baseline run to confirm that lots progress, orders enter the model, and equipment, PM, and breakdown records are processed. It is a single 30-day seed and includes startup effects; it is not a steady-state comparison or a replication of the full experiment. The simulator's own reproduction script runs a much longer 730-day horizon across 10 seeds.

Two utilization values exceed 100% slightly in this run. Treat per-tool utilization as a preliminary signal and inspect the simulator's calculation before using it to make bottleneck claims. The on-time rate and cycle time are simulation outputs for this 30-day run and should not be directly compared with the EDA's planned lead-time distribution as if they measured the same thing.

## Files

- `baseline_30days.json`: raw lot and machine metrics
- `baseline_30days.log`: full console output
