# Third-Party License Summary

This summary supports the DeTime JMLR-MLOSS release candidate. It is a
component-level audit aid, not legal advice.

| Component | Role in DeTime | Dependency status | License status to verify before release |
|---|---|---|---|
| NumPy | array operations | required | BSD-style |
| SciPy | numerical routines | required | BSD-style |
| pandas | optional tabular I/O paths and examples | required | BSD-style |
| statsmodels | STL/MSTL/ROBUST_STL wrappers | required runtime dependency | BSD-style |
| scikit-learn | selected helper routines | required | BSD-style |
| matplotlib | plotting helpers | required | PSF-compatible |
| numba | accelerated Python helper paths | required | BSD-style |
| PyWavelets | WAVELET and wavelet-inspired experimental operators | required | MIT-style |
| tqdm | progress display | required | MPL/BSD-style |
| pydantic | config/result/schema models | required | MIT-style |
| sympy | symbolic/helper routines | required | BSD-style |
| EMD-signal / PyEMD | optional EMD/CEEMDAN wrapper backend | optional extra `emd` | verify package metadata for reviewed version |
| PySDKit | optional MVMD/MEMD backend | optional extra `multivar` | verify package metadata for reviewed version |
| torch | optional `NBEATS_INTERPRETABLE` learned-prior operator | optional extra `neural` | BSD-style |
| pybind11 | native extension build | build dependency | BSD-style |
| scikit-build-core | native extension build | build dependency | Apache/BSD-compatible |

Before creating a JMLR-reviewed archive, run a dependency-license report for the
exact locked environment and attach the output to the release.
