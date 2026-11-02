# G34 Event A: Results (DeepSeek V3)

Held-out cases: `sample/event-a-sample.txt` (tag `event-a-sample`), 12 previously unused cases. Each has at least one structural compilation error, i.e. a simple API replacement is not enough. Selection rule: `deviations.md`, `sample/event-a-select.py`. Prediction: recorded in the G34 tracker before execution. M2 baseline: `M2.md` (tag `m2-frozen`).

Method: frozen M2 method, unchanged (bacardi `4bc6b254`, settings as `config/env.p1.redacted` / `env.p8.redacted`, `MAX_ATTEMPT=1`, BSR = `BUILD_SUCCESS` / cases).

## Execution and validity

OpenRouter repeatedly refused DeepSeek calls (HTTP 429, upstream rate limit, provider StreamLake). A refused call produces no model output, but bacardi still records it as `ERROR_MODEL_RESPONSE`. We therefore count a case only if the model actually replied, using the **first attempt in which it replied**. Execution stopped after the attempts below. All attempts are kept and logged in `deviations.md`.

| Run | Attempts (folder) | Cases with a model reply | No reply (cause) |
|---|---|---|---|
| P1 | `p1-attempt1-ratelimit` (429), `p1-attempt2-nokey` (401, empty key), `p1` (attempt 3) | **2** (attempt 3) | 10 (429 in every attempt) |
| P8 | `p8` | **8** | 4 (429) |

P1 with 2/12 valid cases is effectively **blocked**. The 2 cases are reported, but no P1 rate is meaningful.

## Per-case outcome

| Case | P1 | P8 |
|---|---|---|
| 1e17e176 snakeyaml (polyglot-maven) | no reply | TEST_FAILURE |
| 36859167 fop | no reply | COMPILATION_FAILURE (1 new error) |
| 3eb708f5 google-api translate | no reply | no reply |
| 43b3a858 logback-classic (pdb) | no reply | reply cut off mid-code → ERROR_MODEL_RESPONSE |
| 5769bdad github-api | no reply | COMPILATION_FAILURE (1 new error) |
| 61e96bfe logback-core | no reply | no reply |
| 741f3b5e jackson | no reply | TEST_FAILURE |
| 7c62ae7f hibernate | COMPILATION_FAILURE (2 new errors) | no reply |
| 7d0e38fa google-api dns | TEST_FAILURE | TEST_FAILURE |
| 7f7de81d snmp4j-agent | no reply | TEST_FAILURE |
| 88a20ece pubsublite | no reply | no reply |
| b1a94140 snakeyaml (fluxtion) | no reply | TEST_FAILURE |

## Results

| | M2 (12 cases) | Event A (valid cases only) |
|---|---|---|
| DeepSeek P1 BSR | 4/12 (33%) | 0/2 |
| DeepSeek P8 BSR | 6/12 (50%) | **0/8** |
| `TEST_FAILURE` (compiles, tests fail), DeepSeek | 0/24 case-runs | **6/10** case-runs |

- **No complete repair** in any of the 10 valid case-runs.
- **Patches that look successful but are semantically wrong are the dominant outcome.** In 6/10 valid case-runs (P8 5/8, P1 1/2), the patch removed every compilation error and the project compiled, but its own tests then failed. Example: 7f7de81d, where `SnmpmanSetTest` expected `11` but got `12`, and expected `11` but got `0`. A "compiles" criterion would count these as repairs; build + tests counts none.
- A further 3 valid case-runs replaced the original errors with new ones (COMPILATION_FAILURE), and 1 reply was too long and cut off.

**Semantic-risk coding rule** (prediction file): it applies to `BUILD_SUCCESS` patches, and there were none, so no patch was coded. The `TEST_FAILURE` count above is the observed semantic-risk measure.

**Descriptive statistics** (Fisher's exact test; unpaired, different cases):
- M2 vs Event A DeepSeek P8 BSR, 6/12 vs 0/8: p ≈ 0.04
- `TEST_FAILURE` rate, 0/24 vs 6/10: p < 0.001

These tests are indicative only. The valid cases are a subset determined by rate limiting, and 7d0e38fa appears in both P1 and P8.

**CEFR caveat:** bacardi reports `fixedErrors = prefixErrors` for cases with no reply (e.g. 3eb708f5: 50/50 "fixed"). These cases must be excluded before any error-fix rate is computed.

## Comparison with M2: what transfers, what does not

- **Does not transfer: repair success.** On structurally hard cases DeepSeek P8 went from 6/12 to 0/8 valid.
- **Partly transfers: removing compilation errors.** DeepSeek still clears the original errors in most valid replies (6/10 compile cleanly), but the fixes do not preserve behaviour.
- **Cannot be tested: RQ1 direction (P8 > P1).** Only one case (7d0e38fa) has a valid reply under both prompts (both TEST_FAILURE).
- **Strongest evidence:** the 6/10 test-failing patches, against 0/24 in M2. On hard cases the risk shifts from "fails to compile" to "compiles but behaves differently", and the build + test criterion is what catches it.

## Against the prediction

- "Some but not all repaired": **not supported.** 0 complete repairs among valid cases.
- "DeepSeek P8 > P1": **not testable** (P1 blocked).
- Challenge condition ("Byam repairs none of the 12 in any configuration"): **met for DeepSeek on the valid cases**, but not decisively, because 14 of 24 case-runs have no reply.

## Decision (M1 rules)

**Event A (DeepSeek): INCONCLUSIVE/BLOCKED** under the M1 rule, because LLM access could not be obtained for 14/24 case-runs. Descriptively, the M2 finding **does not transfer** to cases where a simple API replacement is not sufficient: 0 repairs in 10 valid case-runs, and 6 plausible-looking patches that fail the tests. M2 RQ1 stands for the M2 sample only. Its generalisation to harder breaking updates is not supported by this evidence.

## Not included

- Claude Opus Event A P1 (`runs/event-a-opus-p1`): 12/12 `anthropic.APIConnectionError`, so the model was never reached. No valid data; not analysed.
- No further reruns. Group decision: execution stopped here, method unchanged.
- Design implication: see `design-implication.md`.