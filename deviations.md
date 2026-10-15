# Deviations log

Every change made after M1 was frozen (tag `m1-frozen`) is recorded here **before** the affected run is executed.

- **Ordinary**: execution fault fixed without changing an M1 decision (e.g. Docker permissions, missing Python package, configuration typo).
- **Material**: changes an M1 decision (sample, method/parameters, metric, or interpretation rule). The original M1 entry is left unchanged.

| date | M1 item affected | what changed | why | run(s) affected |
|------|------------------|--------------|-----|-----------------|
| 2026-10-14 | none | ordinary: pilot attempt 1 failed at startup with "Invalid pipeline" because `.env` had blank values (`PIPELINE=` empty); `.env` rewritten with all values set and the pilot rerun. Failed log kept as `runs/pilot/run-attempt1-config-error.log` | configuration error; no LLM call or build took place | pilot |
| 2026-10-15 | Method (LLM parameters) | material: Opus calls failed with "`temperature` is deprecated for this model"; `temperature` line removed from bacardi `llm/models/anthropic.py`, so Opus uses its default settings instead of `LLM_TEMP=0`. Change kept as `config/opus-refactor.patch` | model does not accept temperature; Byam cannot call Opus without the change | opus-pilot, opus-p1, opus-p8 |
| 2026-10-15 | Method (LLM parameters) | material: Opus P1 attempt 1 had 6/12 cases end as `ERROR_MODEL_RESPONSE` because Opus returned a thinking block first and bacardi read only `content[0].text` (AttributeError). bacardi `llm/models/anthropic.py` changed to read all text blocks. Attempt 1 kept as `runs/opus-p1-attempt1-thinking-error/`; `config/opus-refactor.patch` updated; P1 rerun on all 12 cases | execution fault in Opus support; model replies were produced but not read by bacardi | opus-p1, opus-p8 |
