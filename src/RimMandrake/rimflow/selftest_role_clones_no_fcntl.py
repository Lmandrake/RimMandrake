#!/usr/bin/env python3
"""selftest_role_clones_no_fcntl: role_clones imports where fcntl does not exist (Windows python.exe).

wrapup.py restore runs under python.exe at every bridge release (rimflow cli _restore_owed_settings); on a filed clone row
it reaches wrapup.check_clone -> `import role_clones`, whose top-level `import fcntl` raised ModuleNotFoundError there, so
the restore died with a traceback and owed settings were never put back (Pyrelands visit 4, 2026-11-22, game a release).
This hides fcntl as Windows does and imports the module, then checks is_role_clone still answers. Red on the parent."""
import importlib, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.modules["fcntl"] = None          # `import fcntl` now raises ImportError, as under Windows python.exe
sys.modules.pop("role_clones", None)
bad = 0
try:
    rc = importlib.import_module("role_clones")
    print("PASS role_clones imports with no fcntl")
    try:
        v = rc.is_role_clone("/nonexistent/clone/path")
        print("PASS is_role_clone answers without fcntl (%r)" % (v,))
    except Exception as e:  # noqa: BLE001
        bad += 1
        print("FAIL is_role_clone raised without fcntl: %s: %s" % (type(e).__name__, e))
except Exception as e:  # noqa: BLE001
    bad += 1
    print("FAIL role_clones import raised without fcntl: %s: %s" % (type(e).__name__, e))
print("selftest_role_clones_no_fcntl: %d failed" % bad)
sys.exit(1 if bad else 0)
