# Critical review: the DeTime proposal (JMLR MLOSS submission draft)

**Scope of this review.** The "method proposed" is the contribution put forward in
`submission/jmlr_mloss_software_paper_draft.md` and its supporting materials: DeTime as a
unified software contract (one config, one result object, one CLI, packaged schemas, an MCP
server, native acceleration) over time-series decomposition, with four core maintained methods
(SSA, STD, STDR, MSSA), one DeTime-original method (GABOR_CLUSTER), and sixteen
architecture-named "neural block" extractors.

**How this review was produced.** Eight parallel referee analyses (contribution/novelty,
core-method fidelity, DeTime-specific methods, evidence validity, claims consistency, software
design, paper quality, empirical execution) followed by adversarial verification. Every
critical/major finding below was verified against the repository — file/line citations were
re-opened and commands re-run. Findings that rest on a fresh-environment run by a review agent
(not re-run a second time) are marked *[agent-empirical]*.

---

## Verdict

**Not submittable in its current state; major revision required.** The underlying software is
better than a skeptical referee would expect — the core algorithms are correct and, in the case
of STD/STDR, faithful to the cited paper; the C++ kernels are real and agreement-tested; the
release engineering is unusually disciplined for an academic package. But the submission is
undermined by three classes of problems, in increasing order of severity:

1. The **paper does not describe the software** (no example, no figure, no URL; a third of it is
   version bureaucracy; the majority of the registered method catalog is never mentioned).
2. The **central claim — a "validated configuration/result contract" — is not implemented**:
   parameters are not validated, the result contract is not enforced, more than half the catalog
   violates the metadata contract, and the advertised MCP interoperability cannot work against
   spec-compliant clients.
3. Several **evidence and consistency claims are factually wrong or misleading** as shipped:
   the primary install path points at a PyPI package that does not exist, the headline speedup
   is ~2× inflated by a cold-start artifact visible in the repo's own raw samples, the "generated"
   cross-package comparison is hand-written and wrong about sktime in DeTime's favor, the
   "consistency checker" enforces optimistic wording rather than facts, and the release/freeze
   story is contradicted by the git history and the repo's own tags.

None of these is unfixable, and the transparency of the repo (raw timing samples, per-file
coverage JSONs, both coverage configs committed) is precisely what made this audit possible —
that same transparency will expose these issues to any referee who looks.

---

## What is genuinely strong

- **STD/STDR is a faithful implementation of Dudek (2022), arXiv:2204.10398.** Verified against
  the paper: per-cycle mean trend (Eq. 4/6), L2-norm "diversity" dispersion (Eq. 5/7), unit-norm
  seasonal shape (Eq. 8), reconstruction y = T + D·S (Eq. 9), and STDR's averaged pattern with
  remainder (Eqs. 11/13) — see `src/detime/methods/std.py:79–117`. The dispersion component is
  not lost: it is exposed in `components["dispersion"]`. The partial-final-cycle extension is
  handled and honestly flagged (`meta["incomplete_cycle"]`).
- **SSA is a correct basic SSA** (Hankel embedding → SVD → rank-1 grouping → diagonal
  averaging), and **MSSA is a genuine joint multichannel SSA** (stacked per-channel Hankel
  blocks, joint SVD), not a per-channel loop (`src/detime/methods/mssa.py:39–57`).
- **The native kernels are real** (~2,160 lines of C++ across 7 kernels) with native/Python
  agreement tests at atol 1e-6/1e-9 (`tests/core/test_native_agreement.py`), and the
  "deterministic exact native SSA" headline claim holds (same LAPACK SVD both paths, seeded
  fast mode, bitwise reproducibility tested).
- **Fail-fast backend semantics work as claimed**: `backend="native"` without the extension
  raises a clear RuntimeError naming the missing exports (`src/detime/backends.py:98–107`).
- **The tsdecomp deprecation is executed cleanly** (re-export + DeprecationWarning + stated
  removal window), the public import surface is small and deliberate, and dispatch errors are
  helpful (1D/2D mismatches name alternative methods).
- **Evidence transparency is exemplary in form**: raw per-sample timings, per-file coverage
  JSONs, and both coverage configs are committed; performance claims are hedged in the text
  ("one environment", "not against external packages"); limitations sections are unusually candid.
- CI runs a 3-OS matrix plus both coverage configs; wheels are built with cibuildwheel.

These strengths matter: the revision path is "make the claims match this genuinely decent
software," not "rescue bad software."

---

## Critical issues (submission blockers)

### C1. The primary install path is broken: `de-time` does not exist on PyPI
`README.md:31–33` ("The current reviewed release version is 0.1.2. Install the latest published
package from PyPI with `python -m pip install de-time`") and `docs/install.md` point every user
and referee at a package that returns **404** on PyPI (verified: `https://pypi.org/pypi/de-time/json`
→ 404; the unrelated `detime` package exists, which the README itself warns about). For a
software-track submission where installability is a first-order criterion, the documented
one-liner failing is disqualifying on its own. **Fix:** publish before submission, or make the
GitHub install the documented path and label PyPI as planned.

### C2. The release story is internally incoherent and contradicted by the repo itself
The paper (line ~100), cover letter, and `RELEASE_MANIFEST.md` all say the `de-time-v0.1.2` tag
"should be cut" / is "planned" — but the tag **exists**, locally and on the remote (verified:
`git tag -l`, `git ls-remote`), pointing at HEAD, with a GitHub Release published 2026-06-24
*[agent-empirical]*. Meanwhile `CHANGELOG.md` dates 0.1.2 as released 2026-06-19 and the README
badge says "release target: 0.1.2" two lines above "current reviewed release". Additionally, the
claimed "candidate freeze date: June 19, 2026" (`submission/software_evidence.md:10`) is
violated by three subsequent commits (verified) — one of which (`2fbb502`, June 22) adds ~300
lines of new tests **together with** the coverage-evidence JSONs the submission quotes, so the
quoted 92.58%/88.41% describes a post-freeze state produced by the same commit that generated
the evidence. A referee cannot identify the frozen reviewed object. **Fix:** pick the true state,
propagate it everywhere, and regenerate evidence from the tagged commit.

### C3. The "validated configuration contract" — the paper's central claim — is not implemented
`DecompositionConfig` is `method: str` plus a free-form `params: Dict[str, Any]`
(`src/detime/core.py:28–29`); nothing validates method-specific parameters. A typo'd key
(`params={"windw": 24}`) is silently ignored and defaults substituted *[agent-empirical, and
statically certain: `decompose()` passes `params` straight through; `ssa.py:66` does
`cfg.get("window", max(4, T // 4))`]*. The registry documents `window` as `required=True`
(`registry.py:952`) — the code silently defaults it. Pydantic extra fields are not forbidden.
The rich `METHOD_PARAMETER_GUIDE` exists but has **no runtime consumer** (docs generation only).
Behavior is inconsistent across methods (STL forwards `**cfg`, so unknown keys raise an upstream
TypeError; SSA/STD/all blocks ignore them). Silent misconfiguration is the exact failure mode a
configuration contract exists to prevent. **Fix:** drive validation from the existing parameter
guide (reject/warn on unknown keys, enforce required params, `extra="forbid"`), with contract
tests for the typo case.

### C4. The MCP server cannot interoperate with any spec-compliant MCP client
`src/detime/mcp/server.py:228–240` implements LSP-style `Content-Length` framing while
declaring `protocolVersion: "2024-11-05"` (line 273) — but MCP's stdio transport is
newline-delimited JSON-RPC; a compliant client's first message would deadlock `_read_message`.
The tests only exercise the same nonstandard framing (`tests/mcp/test_server.py:25`), so the
suite cannot catch it. The MCP surface is cited as a differentiator in the abstract and the
comparison matrices ("mcp_tool_surface: yes" vs "no" for all comparators) — as shipped it is a
private JSON-RPC loop, not ecosystem interoperability. **Fix:** newline-delimited framing or the
official `mcp` SDK, plus an interop test with a real client library.

### C5. "Generated" comparison evidence is hand-written, and wrong about sktime in DeTime's favor
`benchmarks/software_comparison/generate_comparison_evidence.py` contains only literal dicts
(verified); its sole package import is `detime.__version__`; no comparator is ever imported,
introspected, or timed; SSALib is admitted "not installed". Yet README/docs present the output
as "generated" evidence with an audit date. The matrix asserts sktime has no machine-readable
catalog (`machine_readable_catalog: "no"`, verified at lines ~109/312) — sktime ships
`sktime.registry.all_estimators`/`all_tags` — and `mcp_surface: "no"` despite the official
sktime-mcp project *[agent-verified via web]*. Two competitor cells wrong on exactly the axes
DeTime claims as differentiators would seriously damage referee trust. **Fix:** relabel as a
hand-authored position statement or actually introspect comparators; correct the sktime rows.

### C6. The headline 18.2× speedup is a measurement artifact, visible in the repo's own data
`scripts/generate_performance_snapshot.py` uses `repeat=4` with **no warmup** (verified). The
committed GABOR_CLUSTER Python samples are `[8.7843, 1.5195, 1.5065, 1.4044]` ms (verified in
`performance_snapshot.json`) — the cold first call is ~6× steady state and single-handedly
produces the 18.2× headline; steady-state speedup is ≈8.6×. This number anchors the advertised
"2.66×–18.2×" range in the paper, README, cover letter, and evidence note. Relatedly, the
speedups are only against DeTime's own Python fallbacks, and the SSA fallback's diagonal
averaging is a pure-Python double loop that a one-line `np.bincount` vectorization makes ~80×
faster — which would collapse the 7.3× SSA "speedup" to roughly parity *[agent-empirical;
the loop is verified at `ssa.py:14–24`]*. The speedup table currently establishes "C++ beats
unvectorized Python", not "native acceleration materially improves throughput". **Fix:** warmup +
≥50 repeats, median±IQR, vectorize the fallbacks (or say plainly they are unoptimized reference
implementations), 2 significant figures, regenerate all downstream tables.

### C7. The benchmark bridge contradicts the paper's boundary story and is a supply-chain risk
The paper's central narrative is a "clean software submission" with benchmark artifacts removed;
its CLI list (`run, batch, profile, version, schema, recommend`) omits `detime benchmark`. Yet
the package exports `run_tsdecompose_benchmark` at the root and ships a `benchmark` CLI that
downloads code from a Hugging Face dataset at **mutable revision `"main"`** with **no checksum
or pinning** and executes it via `subprocess.run([sys.executable, ...])` (verified:
`benchmark.py:16, 264`; HF token forwarded at 85). Any push to that dataset changes what every
user executes; runs are unreproducible by construction. A referee reading only the paper would
not know this surface exists. **Fix:** disclose it in the paper; pin to a commit SHA with digest
verification; document in SECURITY.md.

### C8. Authorship is unresolved
`AUTHORS.md` states the manuscript lists **eight** authors (Wu, Wei, Chen, Zhou, Shang, Zhu,
Spill, Andrews — verified); the actual paper draft carries **no author list**, the cover letter
is signed by Zipeng Wu alone, and CREDIT.md flags itself as an unapproved draft. For a journal
submission this must be settled before anything else is polished.

---

## Major issues

### Method fidelity and naming
- **M1. Eight-plus "neural blocks" are classical smoothers wearing famous names.** Verified:
  `TIMEKAN_BLOCK`'s `kan_width` enters the computation only as `kan_width // 32` (so 8 and 63
  give identical output); `FREQMOE_BLOCK`'s `expert_width` maps to `round(expert_width/64)`
  harmonics — no KAN layers, no experts, no gating anywhere; a hardcoded
  `blend = clip(0.35 + 0.1·min(bands,4), …)`. AUTOFORMER/DLINEAR/MOVING_AVERAGE blocks are
  **three registrations of the same function** (verified, `forecasting_blocks.py:72–84`) whose
  residual is **identically zero by construction** (`season = arr − trend; residual = arr −
  trend − season`). README's claim that blocks were "extracted" from these architectures is
  accurate for Autoformer/DLinear/N-BEATS and factually wrong for the TimeKAN/FreqMoE/ST-MTM/
  LEDDAM tier. This borrows the credibility of published architectures to pad the catalog and
  goes to scientific integrity, not polish. **Fix:** rename to what they compute ("inspired by"
  in references), collapse duplicates into aliases, drop decorative pseudo-hyperparameters.
- **M2. The paper never mentions the 16 blocks** — more than half of the 31 registered methods,
  all surfaced by the CLI catalog, MCP, and recommender. The software's most contestable content
  escapes review while inflating apparent breadth.
- **M3. GABOR_CLUSTER (the only DeTime-original method) is unusable as shipped**: it requires a
  pre-trained k-means model that no shipped code can produce (no training routine anywhere;
  config fields `n_iter`/`random_state`/`max_atoms` are dead), needs `faiss`, which appears in
  **no dependency group** (verified: zero hits in pyproject.toml), and the project's own gallery
  marks it "skipped". Yet it supplies the largest number in the paper (18.2×) and is ranked 6th
  by the recommender. Its trend/season split also reads centroid coordinates in standardized
  space as if they were raw normalized frequencies — correct only when μ=0, σ=1, which is what
  every shipped usage hardcodes, so no test can catch it; and `np.load(..., allow_pickle=True)`
  on user paths is a deserialization risk. **Fix:** ship a training entry point + extras group +
  end-to-end example, fix the coordinate-space bug with a non-trivial μ/σ test — or remove it
  from the evidence table and recommender.
- **M4. SSA grouping is an undocumented ad-hoc heuristic.** Without `primary_period` the split is
  hard-coded `trend=[0,1], season=[2,3]` regardless of the signal; with it, membership is a
  single ±25% frequency band, so seasonal harmonics (e.g. period-6 alongside period-12) land in
  the residual *[agent-empirical]*. This is not the cited Golyandina & Zhigljavsky eigentriple
  identification and is disclosed nowhere. **Fix:** document precisely; add harmonic bands;
  cite as a DeTime heuristic.
- **M5. Provenance metadata is wrong in two places.** The native exact SSA labels its solver
  `"jacobi-eigen"` while actually calling numpy's LAPACK SVD from C++ — the Jacobi code is dead
  (verified: defined, never called; `mssa.cpp` labels the same design correctly as `"numpy-svd"`).
  And `speed_mode="fast"` is silently ignored on the Python SSA path yet stamped into `meta`
  (verified: the only `speed_mode` use in `ssa.py` is forwarding to native). A reproducibility
  contract that records algorithms that never ran is self-defeating. Also: fast means three
  different algorithms depending on method/backend, with no cross-backend fast-mode test, and
  the approximation error is characterized by a single 5e-2 tolerance on one synthetic signal.
- **M6. `std_multi.py` ships placeholder generated code**, including the comment "Fallback to
  SSA for now as per prompt hint 'Placeholder for user-provided STD implementation'" (verified,
  lines ~54–58) — a function named `std_multi_decompose` that silently returns **SSA** results,
  plus a dead `import fasttimes`. Visible prompt-residue in a journal-submitted package invites
  the worst kind of referee inference. Remove or raise NotImplementedError.

### Evidence and quality gates
- **M7. The gated 92.58% coverage scope omits exactly what the paper headlines.** `.coveragerc`
  (verified) excludes `cli.py`, `io.py`, `viz.py`, `metrics.py` and 11 method files — including
  **three of the seven methods in the performance table** (VMD, MA_BASELINE, GABOR_CLUSTER) —
  while experimental neural blocks are inside the gate. Package-wide coverage (88.41%) fails the
  advertised `fail_under=90`. The dual reporting is disclosed (mitigating), but the
  "core-plus-maintained" label is incoherent and reads as engineered to keep the badge green.
- **M8. The default test suite fails on a clean pure-Python checkout.**
  `tests/docs/test_tutorial_assets.py` runs `generate_tutorial_assets.py` with `check=True`,
  which invokes `detime profile --backend native` (verified, script line ~327) with no
  native-availability guard — so the most likely referee path (clone, pip install deps, pytest)
  produces a red suite (*[agent-empirical: "1 failed, 105 passed, 17 skipped" in a fresh venv]*),
  contradicting the paper's "native fallback handling" claim and the release-check list.
- **M9. The README badge "unit tests: 112 passed" contradicts the repo's own evidence file**,
  which records "123 passed" from the same 2026-06-22 audit the README cites three lines later
  (both verified). The numeric claims are hand-synced and have already rotted once.
- **M10. `check_doc_consistency.py` enforces narrative, not facts.** Verified: BANNED_PATTERNS
  forbids truthful status phrases — "not yet tagged or published" (CHANGELOG), "still pending"
  (cover letter!), "not yet available" (install docs) — and REQUIRED_PATTERNS mandates the
  broken `pip install de-time` string. The gate the submission cites as quality discipline
  structurally prevents the documentation from being honest about release state. This one is a
  serious credibility problem if a referee reads the script.
- **M11. "Reproducible performance snapshot" over-claims.** n=4, no warmup, one 240-point series,
  one Windows machine, no CPU/BLAS/dependency pinning (requirements are all `>=`), sub-ms means
  with >2× sample spread quoted to 6–7 significant figures. What is reproducible is the script,
  not the numbers.

### Software design (the software *is* the claimed contribution)
- **M12. The result/meta contract is not enforced and not uniform.** `DecompResult.__post_init__`
  is a `pass` (verified); no shape/finiteness/reconstruction validation exists anywhere in
  dispatch; a malformed native payload silently becomes empty arrays
  (`backends.py:124–133`, `payload.get("trend", [])`). All 16 neural blocks bypass
  `finalize_result`, so they return no `backend_used`/`speed_mode`/`runtime_ms` even with
  `profile=True`, and the CLI then back-fills `backend_used` with the *requested* preference
  string *[agent-empirical; code paths verified]*. The majority of the catalog violates the
  contract the paper calls uniform.
- **M13. Dependency footprint contradicts the "thin layer" positioning.** `numba`, `sympy`, and
  `tqdm` are mandatory dependencies with **zero imports anywhere in src/** (verified);
  matplotlib/statsmodels/sklearn are already lazily imported and could be extras.
- **M14. CLI discipline.** `detime batch` exits 0 when every file fails (verified,
  `cli.py:281–282`); malformed `--param` entries are silently dropped (verified, `cli.py:79`);
  `--out_dir` vs `--output-mode` mixed flag styles are baked into the documented interface.
- **M15. Registry doc-data drift.** `power_iterations` documented default 4 vs code 12; SSA
  `rank` documented None vs code 10; `window` documented required vs silently defaulted (all
  verified); `fit_scope` defaults inconsistent across sibling blocks *[agent-verified]*. The
  1,541-line registry mixing dispatch with ~1,300 lines of hand-maintained parallel data
  guarantees continued divergence; nothing tests guide-vs-code agreement.
- **M16. Dead contract surface.** `backend="gpu"` is accepted by the schema and advertised in
  CLI help but unconditionally raises; `return_components` is consumed nowhere; the recommender
  is a static, hand-tuned score table that never inspects the data and hard-codes accuracy
  bonuses for DeTime's own flagship methods.

### Paper and positioning (all machine-verified CONFIRMED)
- **M17.** The paper contains **no code example, no figure, no install command, and no URL to its
  own repository or docs** — for a software track whose entire point is "show me the software".
- **M18.** Roughly 30% of the draft is version/tag/namespace bureaucracy; SSA/STD/STDR/MSSA are
  never expanded or algorithmically described (a reader never learns what STDR stands for); the
  abstract is a list of packaging facts.
- **M19.** The tone violates the project's own `DESIGN.md` ("docs should feel like a scientific
  toolkit, not a review dossier"): pervasive defensive disclaimers in place of positive claims.
- **M20.** The cover letter reads as internal release notes — including instructions about which
  git tag "should be cut", addressed to journal editors; the reviewer_bundle is five near-empty
  files duplicating other documents (one already drifted from its generator).
- **M21.** Related work compares against six packages fairly (a strength — the "never engages
  competitors" criticism was tested and **refuted**), but omits the closest neighbors on the
  "one interface over many methods" axis: Nixtla statsforecast, aeon, Darts (zero hits in the
  repo, verified). And there is **no quantitative comparison against any external package
  anywhere** (machine-verified) — for a layer over existing tools, wrapper overhead vs
  statsmodels STL / PyEMD / SSALib is the one number a referee will ask for.
- **M22.** MLOSS weighs user engagement; the submission concedes adoption is early. That is
  survivable (criteria are explicitly not strict requirements, and engagement evidence belongs
  in the cover letter), but it makes the fixable problems above decisive: a low-adoption
  submission gets no benefit of the doubt on evidence hygiene.

---

## Minor issues (selected)
- STD's residual is identically zero by construction (inherent to Dudek's STD; verified) —
  undisclosed, so residual-based diagnostics trivially flatter STD; one sentence fixes it.
- Native SSA rejects T<4 while the Python path accepts T=3 — backend-dependent validity envelope.
- GABOR_CLUSTER docs show a `.pkl` example for an `.npz` serializer.
- Internal working notes at repo root (`HOT_TREND_LAB_ADDED.md`, `QUANT_TRADING_*_ADDED.md`,
  `hot_trend_lab_file_manifest.csv`) — one claims the `submission/` directory was moved out of
  the repo, which is false in the current tree; the built `site/` directory is committed.
- 4-significant-digit speedups ("7.307×") from n=4 micro-benchmarks, repeated in four documents.

---

## Prioritized recommendations

**Before anything else (integrity):**
1. Resolve authorship (C8) and the release story (C1, C2): publish to PyPI or re-document the
   install path; align paper/cover letter/README/CHANGELOG/RELEASE_MANIFEST to one true state;
   regenerate evidence from the tagged commit.
2. Fix or relabel the evidence: warmup+repeats for the snapshot, drop or re-measure the 18.2×,
   re-badge the test count, make `check_doc_consistency.py` check facts instead of banning
   honest phrasing, relabel the comparison matrices as hand-authored and correct the sktime cells.
3. Remove `std_multi.py` (or NotImplementedError), fix the `jacobi-eigen` label and the
   `speed_mode` metadata lie — these are cheap fixes to "the metadata records things that never
   ran".

**To make the claimed contribution true (the substantive revision):**
4. Implement parameter validation from the existing guide (C3) and route every registered method
   through `finalize_result` (M12); add a `DecompResult.validate()` called in dispatch.
5. Fix MCP framing to spec and add a real-client interop test (C4).
6. Rename or properly implement the eight name-only neural blocks; collapse the three duplicate
   MA registrations; disclose the block tier in the paper or unregister it for the submission (M1, M2).
7. Make GABOR_CLUSTER trainable and installable, or withdraw it from evidence and recommender (M3).
8. Guard the tutorial-assets test on native availability (M8); pin the benchmark bridge to a
   commit SHA with digest checks and disclose it in the paper (C7).

**To make the paper reviewable:**
9. Rewrite the paper around the software: one worked example (config → result → saved artifact),
   one architecture figure, algorithmic one-liners for SSA/STD/STDR/MSSA, URLs, author list;
   cut the version bureaucracy to two sentences; add statsforecast/aeon/Darts to related work;
   add one small cross-package table (wrapper overhead + same-method runtime on 2 platforms).

A revision that does items 1–9 would present materially the same software as a much stronger
submission: the honest core (correct methods, real kernels, real tests, real transparency) is
already there; what fails review today is the gap between the claims and the shipped artifact.
