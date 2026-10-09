# art_status readers repoint 2026-10-09

Started. Readers: regen_hub.py, hub_check.py, build_standalone.py, make_tab_data.py, artpipe_state.py.

## Finding
art_status.json = artreg.build_status(): per-target iteration state machine (registered..deployed), spend (codex %/gemini $), throughput fingerprints, burn-up projection — all derived from registry.jsonl + throughput.jsonl. The art ledger (infrastructure/state/art) records variants/rulings/installs; it holds NONE of those fields. No ledger projection can supply them.

## Per reader
- regen_hub.py, hub_check.py, build_standalone.py: LIVE (hub index.html reads stateCounts/spend/projection/perTarget; rm-codebase-health timer path). GAP: state machine + spend + projection not in ledger. Left on art_status.json.
- make_tab_data.py: never reads art_status.json (docstring only); path in docstring corrected.
- artpipe_state.py: `find` searched art_status.json, a derived duplicate of registry.jsonl (old: registry 16 + art_status 2 lines for "korrum"-style probe; new: registry only, same). Dropped from SEARCH_FILES. `where` still reports file size (existence only).

## Retiring art_status.json needs
Daemon-side change (out of scope tonight): hub art tab to read artreg.build_status() directly, or ledger gaining iteration/spend events.
