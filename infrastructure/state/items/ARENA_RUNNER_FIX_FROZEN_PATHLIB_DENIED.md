# ARENA_RUNNER_FIX_FROZEN_PATHLIB_DENIED

## spec
Probe (FOUNDRY 2026-10-30): a check body 'import pathlib' (or ntpath, or 'from pathlib import Path') under python3 -P -c arena_judge.RUNNER exits 86 'ARENA_RUNNER_DENIED marshal.loads'; 'import json/subprocess/tempfile' pass. Trace: pathlib/__init__.py:617 PureWindowsPath imports ntpath, a FROZEN module whose FrozenImporter.exec_module calls marshal.loads; pycache_prefix does not cover frozen modules. Real-pool vet through the judge's own materialise+run_hidden: 184 of 265 hidden fix_tests come back 'denied' at the FIX (179 denied at both sides), so the judge would call ~70% of genuine fixes invalid. Fix: allow marshal.loads from the frozen importer (or pre-import frozen stdlib modules before installing the hook) without reopening crafted-bytecode routes; then rerun 'arena_tasks.py vet' (its cache key hashes the judge runner, so every record re-vets) and census. Evidence: D:\ClaudeWork\rimmandrake\arena\foundry_vet\vet2_tally.txt, denied_samples.txt

## criteria
- A1 L0: selftest_arena_judge t_nonce_hunt: control 'import pathlib' / 'from pathlib import Path' / 'import ntpath, runpy, importlib.util' -> pass; hunts marshal.loads crafted bytecode, `_imp.get_frozen_object(name, arm bytes)`, del+re-import of a pre-loaded frozen module -> never pass (denied)
- A2 L0: real `arena_tasks.py vet` with the fixed runner: 'ARENA_RUNNER_DENIED marshal.loads' 181 -> 0 of 265 hidden checks (D:\ClaudeWork\rimmandrake\arena\foundry_vet\vet4_tally.txt, runner @1dcb8ea95a096495)
- A3 L1: the arena_tasks owner re-vets on the final runner hash and re-runs census; the pool's denied count is near zero and any remaining denials are filed per cause
