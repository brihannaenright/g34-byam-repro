# G34 Event A: Design / maintainability implication

## Problem

bacardi's LLM layer has no explicit contract for what a model reply is, or for how a model call can fail. Every failure between "send prompt" and "patched file" is collapsed into one outcome, `ERROR_MODEL_RESPONSE`. The real cause survives only as text in `run.log`. As a result, the tool cannot tell a **tool or infrastructure fault** apart from a **model fault**, and our results inherit that ambiguity.

## Evidence

| Run | What actually happened | What bacardi recorded |
|---|---|---|
| M2 Opus P1, attempt 1 | Opus replied, but the reply began with a thinking block; `anthropic.py` read only `content[0].text` and crashed | `ERROR_MODEL_RESPONSE` (6/12) |
| M2 Opus P8 | Model-response failures on 6/12; cause had to be rechecked by hand (`runs/opus-error-recheck.txt`) | `ERROR_MODEL_RESPONSE`; this confounded RQ3 |
| Event A DeepSeek P1, attempt 1 | HTTP 429, OpenRouter upstream rate limit; no reply at all | `ERROR_MODEL_RESPONSE` (12/12) |
| Event A DeepSeek P1, attempt 2 | HTTP 401, API key missing from `.env`; no call reached the model | `ERROR_MODEL_RESPONSE` (12/12) |
| Event A DeepSeek P8 | 4 cases rate-limited (429); 1 case (43b3a858) had a real 66 KB reply cut off mid-code block | `ERROR_MODEL_RESPONSE` for all 5 |
| Event A Opus P1 | `anthropic.APIConnectionError`; network failure, model never reached | `ERROR_MODEL_RESPONSE` (12/12) |

In every one of these error cases the result JSON also reports `fixedErrors = prefixErrors` (e.g. 3eb708f5: 50/50 "fixed"), although no patch was applied. Any CEFR computed from the raw fields is therefore inflated unless these cases are excluded by hand.

## Where it comes from (bacardi `4bc6b254`)

1. **Broad catch-all.** `core/.../BacardiCore.java:250–276` wraps the LLM call, reply extraction, file writes and the diff in one `catch (Exception e)`. Every failure becomes `ERROR_MODEL_RESPONSE`, with the misleading log message "Error saving prompt to file".
2. **Failed subprocess treated as a normal reply.** `core/.../prompt/GeneratePrompt.java:88–118` (`callPythonScript`) returns whatever was on stdout even when the Python script exits non-zero. The error goes only to stderr, so a failed API call turns into an empty "reply" that fails later, at extraction.
3. **Provider details spread around, with no common contract.** Text extraction happens in a different place for each provider: inside the model class (`llm/models/anthropic.py:29`), in the dispatcher (`llm/call_llm.py:58`, OpenRouter), or through a helper (`extract_text`, Gemini). Cost tracking exists for OpenRouter and Gemini only. Supporting a new model (Opus) meant editing provider internals: `config/opus-refactor.patch`.
## Module concepts

- **Cohesion and separation of concerns:** reply normalisation is split between the model classes and the dispatcher, and error handling is mixed into the repair loop.
- **Error handling that throws information away:** one generic category replaces distinct, meaningful failures. This also creates a measurement-validity problem, because a tool fault is indistinguishable from a model's failure to repair.
## Proportionate refactoring

1. Give every provider class the same return contract: either `text`, or a failure with a reason (`RATE_LIMITED`, `AUTH`, `NETWORK`, `TRUNCATED`, `UNPARSEABLE`). Move each provider's extraction into its own class.
2. Make `callPythonScript` treat a non-zero exit as a failure and pass stderr upward.
3. Replace the catch-all with separate handling for the LLM call, extraction and file I/O. Record the reason in the result JSON (e.g. an `errorDetail` field), and do not report `fixedErrors` when no patch was applied.
## Why no design pattern

The forces do not justify one. There are four providers, they change rarely, and `LLMResolver.get_model` already dispatches through a lookup table. An Adapter or Strategy hierarchy would add structure without addressing the evidence. The defect the evidence shows is an implicit return contract and swallowed errors, so Extract Method plus narrower exception handling is the proportionate change.

## Consequence for our study

Every `ERROR_MODEL_RESPONSE` must be checked against `run.log` before it can be counted as a model outcome. We did this for Event A: the rate-limit, missing-key and connection failures were logged in `deviations.md` and rerun. Only 43b3a858 (P8, cut-off reply) is counted as a genuine non-repair.