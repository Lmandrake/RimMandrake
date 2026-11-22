"""mutations.py - plant each fault in account_live.py, run selftest_account_live.py, expect new FAILs; restores the file.

    python3 design/specs/2026-11-22-live-account/mutations.py     exit 0 when every planted fault is caught
"""
import os
import subprocess
import sys
UT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "src", "RimMandrake", "Utils")
os.chdir(UT)
F = "account_live.py"
MUT = [
 ("rc ignored", "    if rc != 0:\n", "    if False:\n"),
 ("no tolerance of text before", '(out or "").find("{")', '(0 if (out or "").startswith("{") else -1)'),
 ("ok=false accepted", 'st.get("ok") is False', 'False'),
 ("non-string live accepted", 'not isinstance(live, str) or not live.strip()', 'live is None'),
 ("timeout read as failed", 'PR.could_not_look("claude-account status timed out', 'PR.failed("claude-account status timed out'),
 ("ssh without BatchMode", '"BatchMode=yes"', '"BatchMode=no"'),
 ("why None on empty", 'if answer.kind == "value":\n        return None', 'if answer.kind in ("value", "empty"):\n        return None'),
 ("first object taken even without live", 'if isinstance(obj, dict) and "live" in obj:', 'if isinstance(obj, dict):'),
]
orig = open(F).read()
def fails():
    r = subprocess.run([sys.executable, "selftest_account_live.py"], capture_output=True, text=True)
    return {l for l in r.stdout.splitlines() if l.startswith("FAIL")}
base = fails()
missed = 0
try:
    for name, a, b in MUT:
        assert orig.count(a) == 1, name
        open(F, "w").write(orig.replace(a, b))
        extra = fails() - base
        print("%-40s %s" % (name, "CAUGHT (%d new FAIL)" % len(extra) if extra else "NOT CAUGHT"))
        missed += not extra
finally:
    open(F, "w").write(orig)
print("MUTATIONS %d planted, %d not caught" % (len(MUT), missed))
sys.exit(1 if missed else 0)
