# G34 – Bounded reproduction of Byam (RQ1)

Evidence repository for group G34's bounded reproduction of:

> Reyes et al. (2026). *Byam: Fixing Breaking Dependency Updates with Large Language Models.*
> Empirical Software Engineering 31:113. https://doi.org/10.1007/s10664-026-10835-1
> Artefact: https://github.com/chains-project/bacardi · Dataset: https://github.com/chains-project/bump

## Research question

**RQ1:** On a fixed sample of BUMP breaking updates, does Byam with DeepSeek V3 reproduce
the paper's reported Build Success Rate (BSR) and Compilation Error Fix Rate (CEFR) for the
baseline prompt (P1) and the full-context prompt (P8)?

- **Sample:** 12 eligible breaking-dependency-update cases, selected by a fixed rule (see `M1.md`, `sample/`).
- **Model:** DeepSeek V3 (`deepseek/deepseek-chat` via OpenRouter).
- **Prompts:** P1 = `BASELINE`, P8 = `BASELINE_COT_API_DIFF_BUGGY`.
- **Decision rule:** pre-declared in `M1.md` (frozen at tag `m1-frozen`) before any execution.

## Repository layout

| Path | Purpose |
|---|---|
| `M1.md` | Frozen pre-declaration: RQ, target values, sample, method, metrics, decision rule. |
| `deviations.md` | Every change made after M1 was frozen: what, why, and which runs it affects. |
| `sample/` | The frozen 12 cases, the eligible population, selection command, case metadata, Docker image digests. |
| `env/` | Exact commits of bacardi and BUMP, tool/library versions, build log, OpenRouter activity export. |
| `config/` | The `.env` used for each run, with API keys redacted. |
| `runs/pilot/` | Pilot run on case 1 of the sample (pipeline check only). |
| `runs/p1/`, `runs/p8/` | Raw pipeline output per prompt: result JSON, generated prompts and patches, run logs, command used. |
| `derived/` | Script that computes BSR/CEFR, its outputs, per-case tables, and the comparison against the reference. |

## Git tags

- `m1-frozen`: M1 decisions committed before any run.
- `results-v1`: derived results and decision applied.

## How to rerun

1. Clone bacardi and BUMP at the commits in `env/commits.txt`.
2. Match the environment in `env/versions.txt` and `env/pip-freeze.txt`; build with `mvn clean install`.
3. Copy `config/env.<run>.redacted` to `bacardi/.env`, fix the local paths, and add your own `OPENROUTER_API_KEY`.
4. Run the command in `runs/<run>/command.txt` from the bacardi root.
5. Recompute metrics with `derived/derive.sh <result JSON> sample/g34-sample.txt`.

## Result

_To be filled after `results-v1`: BSR and CEFR for P1 and P8, the reference values, and the verdict under the M1 decision rule._