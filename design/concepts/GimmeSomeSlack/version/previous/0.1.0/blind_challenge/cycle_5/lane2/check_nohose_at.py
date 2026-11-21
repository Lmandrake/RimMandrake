#!/usr/bin/env python3
"""Run T_NO_HOSE as it stands at one sha against the mod tree as it stood at another (the red-first record of
RIMMANDRAKE_WIDEN_GSS_NOHOSE_SCAN_LOAD_FOLDERS_SAID_PIPES).
    python3 check_nohose_at.py --sha <mod tree sha> --test-from <test sha>      exit = the test's rc
The mod folder is taken with `git archive` into a temp dir; the test file from --test-from is put in its northstar/."""
import argparse, os, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
MOD = "src/RimMandrake/GimmeSomeSlack"; TEST = MOD + "/northstar/selftest_gss_no_hose.py"
ap = argparse.ArgumentParser(); ap.add_argument("--sha", required=True); ap.add_argument("--test-from", required=True)
a = ap.parse_args()
with tempfile.TemporaryDirectory(prefix="gss_nohose_at_") as tmp:
    arc = subprocess.run(["git", "-C", REPO, "archive", a.sha, MOD], capture_output=True, check=True).stdout
    subprocess.run(["tar", "-x", "-C", tmp], input=arc, check=True)
    test = subprocess.run(["git", "-C", REPO, "show", "%s:%s" % (a.test_from, TEST)], capture_output=True, check=True).stdout
    open(os.path.join(tmp, TEST), "wb").write(test)
    r = subprocess.run([sys.executable, TEST], cwd=tmp, capture_output=True, text=True, timeout=300)
    lines = [l for l in r.stdout.splitlines() if l.strip()]
    first_bad = next((l for l in lines if not l.startswith("PASS")), lines[-1] if lines else "")
    print("tree %s, test %s: rc %d; %s" % (a.sha[:10], a.test_from[:10], r.returncode, first_bad[:200]))
    sys.exit(r.returncode)
