# Open Models and Developer Attention

Open-model launches often follow a launch-to-retention pattern. The launch week
creates a public burst; the useful question is whether downloads, likes, stars,
or repository activity keep accumulating after the burst fades.

This page uses two public proxies:

1. Hugging Face model metadata snapshots;
2. GitHub repository metadata plus stargazer timestamps.

The proxies are useful because they are public and repeatable. They still need
benchmarks, deployment evidence, and user evidence before a story can claim
model quality or production adoption.

## Hugging Face model pulse

The Hugging Face notebook ranks a dated public snapshot and appends it to a
local snapshot log. A single snapshot can support a current public-adoption
proxy, but it cannot support momentum language. Momentum needs repeated dated
snapshots collected with the same query, sort, and limit.

Download and like fields are Hub metadata fields exposed by the public API.
Gated, private, renamed, or deleted models can change what appears in a query
response, so the source card records the endpoint parameters and access date.

| Output | How to read it | Boundary |
|---|---|---|
| Snapshot audit | access date, row count, source field, query context | tells whether the table is publishable |
| Snapshot rank | current downloads and likes for the selected API response | cross-sectional attention, not retention |
| Repeated-snapshot series | change in downloads or likes across collection dates | available only after several snapshots |
| Residual events | launch-like deviations after decomposition | event pointer, not model-quality evidence |

Use [03 Hugging Face open-model pulse](notebooks/03_huggingface_open_model_pulse.md)
for the rendered notebook.

## GitHub developer pulse

GitHub stars are visible and easy to compare, but they are a developer-attention
signal. Star velocity is sensitive to the repository list, token limits,
pagination depth, and the chosen coverage window. The notebook therefore shows
coverage before interpretation.

| Output | How to read it | Boundary |
|---|---|---|
| Repo metadata | selected repositories and current public metadata | basket selection shapes the result |
| Stargazer coverage | number of fetched stargazer rows by repository | low coverage weakens velocity claims |
| Daily velocity | stars per day in the fetched window | attention in the window, not usage |
| Residual events | unusually large daily deviations | launch or media-event candidates |

Use [04 GitHub AI-agent star velocity](notebooks/04_github_ai_agent_star_velocity.md)
for the rendered notebook.

## Launch-to-retention article shape

1. Name the launch or repo basket.
2. Show the dated Hugging Face snapshot or GitHub coverage window.
3. Separate the launch spike from later retention.
4. Add benchmark or deployment evidence before quality or adoption language.

A good sentence says, "the public snapshot places this model near the top of the
selected download table." It does not turn downloads or stars into a direct
measure of technical superiority.
