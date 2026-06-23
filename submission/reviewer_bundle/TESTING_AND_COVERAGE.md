# Testing and Coverage

- Core-surface coverage: gated via `.coveragerc` and `fail_under = 90`.
- Package-wide coverage: emitted as a second CI artifact with the broader denominator.
- Core-contract result: `92.58%`.
- Package-wide result: `88.41%`.
- Runtime snapshot file: `docs/assets/generated/evidence/performance_snapshot.json`.
- Runtime snapshot methods: SSA, STD, STDR, MA_BASELINE, MSSA, VMD, GABOR_CLUSTER.
