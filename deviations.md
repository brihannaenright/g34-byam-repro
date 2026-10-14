# Deviations log

Every change made after M1 was frozen (tag `m1-frozen`) is recorded here **before** the affected run is executed.

- **Ordinary**: execution fault fixed without changing an M1 decision (e.g. Docker permissions, missing Python package, configuration typo).
- **Material**: changes an M1 decision (sample, method/parameters, metric, or interpretation rule). The original M1 entry is left unchanged.

| date | M1 item affected | what changed | why | run(s) affected |
|------|------------------|--------------|-----|-----------------|
| 2026-10-14 | none | ordinary: pilot attempt 1 failed at startup with "Invalid pipeline" because `.env` had blank values (`PIPELINE=` empty); `.env` rewritten with all values set and the pilot rerun. Failed log kept as `runs/pilot/run-attempt1-config-error.log` | configuration error; no LLM call or build took place | pilot |