# HUB_LAMP_TIME_FIX_1 — hub freshness lamps compute age against mislabeled time

Found by a BENCH full-file review 2026-09-12; the two load-bearing claims
confirmed by BENCH reading the code. Neither file has ever been mark-clean.

## Findings
`infrastructure/dashboards/hub/make_tab_data.py`:
- :29-32 `iso()` appends `Z` to LOCAL wall-clock stamps (its own comment
  admits it) — every downstream age is off by the UTC offset. CONFIRMED in
  the wild: RECORD_HUB_HEALTH_PROOF_1's recorded "health GREEN 7.0 h" was
  minutes-old data + the 7-hour PDT offset. Fix: stamp real UTC (or parse as
  local and convert); regenerate tab data after.
- :78 `worldmap()` hardcodes `post_freeze_2026-09-11.json` — the next audit
  silently stops feeding the tab.
- :83 worldmap `artifactUrl` hardcoded in source — second source of truth.
- :32 a loose stamp with no `:` yields invalid ISO (`...Z` with no time).

`infrastructure/dashboards/hub/hub_check.py`:
- :38-44 the `except (KeyError, ValueError)` GREY path never sets `bad` —
  gate exits 0 on unusable data.
- :47-52 missing/moved source file leaves `fresh=""` — reads as fine, not
  MISSING.
- :39 a naive timestamp (no Z/offset) makes aware-minus-naive raise
  TypeError, outside the caught tuple — crashes the whole check.

## verify
After fix: a tab generated "now" reads ~0.0 h; GREY sets nonzero exit; a
deleted source path prints MISSING and fails the gate; re-review both files
full-file before any mark-clean.

## Note on recorded numbers
DASHBOARD_HUB_ARTIFACT_1's proof sections cite "7.0 h" — annotated there; the
fingerprint no-clobber conclusions are unaffected (sha match is ageless).
