# ARENA_RUNNER_FIX_OPTIONAL_IMPORT_DENIED

## spec
After the frozen fix (ARENA_RUNNER_FIX_FROZEN_PATHLIB_DENIED), a real vet (runner @1dcb8ea95a096495,
D:\ClaudeWork\rimmandrake\arena\foundry_vet\vet4_tally.txt) still had 31 of 265 hidden fix_tests 'denied' with
'ARENA_RUNNER_DENIED import': '_interpreters' (py3.14 concurrent/futures/__init__.py does `try: import _interpreters
except ImportError`) and 'ctypes' (optional imports). The hook killed the process on the import event.

Fix (b7a773744e): a plain-import event of a BADMOD name (args (name, None, sys.path, ...)) raises ModuleNotFoundError
from the hook, aborting the import, so optional imports carry on; any other shape is still a kill. Rejected first
design: seeding sys.modules[n] = None and letting the hook pass None entries opened two holes, found by probe: the
extension loader route (`PathFinder.find_spec('_interpreters')` + `exec_module`, which raises an import event with
(name, path, None, None, None)) passed, and `_interpreters.create()` raises NO audit event on 3.14, so a hook-less
subinterpreter was created; and a thread could delete the None between the event and _find_and_load (TOCTOU).

## criteria
- A1 L0: selftest_arena_judge t_nonce_hunt: controls 'from concurrent.futures import ThreadPoolExecutor' and an optional `try: import ctypes` -> pass; hunt "subinterpreter via the extension loader" -> denied; hunt ctypes -> never pass
- A2 L1: the arena_tasks owner re-vets on the final runner hash; no 'ARENA_RUNNER_DENIED import' remains for _interpreters/ctypes optional imports
