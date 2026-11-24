#!/usr/bin/env python3
"""selftest_prove_stall_dump_site.py - the stall proof reads the companion of the game it drives, on any machine."""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
d = tempfile.mkdtemp()
env = {k: v for k, v in os.environ.items() if k not in ("RM_COMPANION_DLL", "RM_GAME_INSTANCE")}
env["RM_STEAMAPPS"] = d
code = "import sys; sys.path.insert(0, %r); import prove_bridge_stall_dump as P; print(P.DLL)" % HERE
r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env=env, timeout=120)
got = r.stdout.strip()
want = os.path.join(d, "common", "RimWorld", "BridgeTools", "JawaBench", "JawaBench.BridgeTools.dll")
ok = got.replace("\\", "/") == want
print(("ok    " if ok else "FAIL  ") + "the DLL is the driven game's: %s %s" % (got, r.stderr.strip()[-200:]))
print("PASS" if ok else "FAIL 1")
sys.exit(0 if ok else 1)
