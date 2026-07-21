# Third-Party License Summary

This summary supports the DeTime JMLR-MLOSS release candidate. It is a
component-level audit aid, not legal advice.

| Component | Role in DeTime | Dependency status | License |
|---|---|---|---|
| NumPy | array operations | required | BSD-style |
| SciPy | numerical routines | required | BSD-style |
| pandas | optional tabular I/O paths and examples | required | BSD-style |
| statsmodels | STL/MSTL/ROBUST_STL wrappers | required runtime dependency | BSD-style |
| scikit-learn | selected helper routines | required | BSD-style |
| matplotlib | plotting helpers | required | PSF-compatible |
| PyWavelets | WAVELET and wavelet-inspired experimental operators | required | MIT-style |
| pydantic | config/result/schema models | required | MIT-style |
| [EMD-signal / PyEMD](https://pypi.org/project/EMD-signal/) | optional EMD/CEEMDAN wrapper backend | optional extra `emd` | Apache-2.0 |
| [vmdpy](https://pypi.org/project/vmdpy/) | Python fallback for VMD | optional extra `vmd` | MIT |
| [PySDKit](https://pypi.org/project/PySDKit/) | optional MVMD/MEMD backend | optional extra `multivar` | MIT |
| [faiss-cpu](https://pypi.org/project/faiss-cpu/) | optional Gabor-cluster assignment backend | optional extra `gabor` | MIT |
| torch | optional `NBEATS_INTERPRETABLE` learned-prior operator | optional extra `neural` | BSD-style |
| pybind11 | native extension build | build dependency | BSD-style |
| scikit-build-core | native extension build | build dependency | Apache/BSD-compatible |

The optional-backend identifiers above were checked against their official
PyPI metadata on 2026-07-14. Dependencies are installed separately and are not
vendored into DeTime release artifacts.
