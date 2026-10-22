"""Every FlowWorks northstar proof that starts a fresh quicktest map must calm the site in its preflight (validation_core
.site_calm, or .clear_threat_structures / jawa/quiet_site for the proofs that own their storyteller handling), or map-generated
hostiles and hives stop safe_advance at arm (TESTENV_PREFLIGHT_HARDEN_TRISPIKE_AT_ARM). Offline, text-level; can-fail: a proof
that drops the call fails. Proves the SCRIPTS call it, never that the game obeys.

    python3 src/RimMandrake/FlowWorks/northstar/selftest_preflight_calm.py
"""
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CALM = re.compile(r"site_calm\(|clear_threat_structures\(|jawa/quiet_site")
# proofs owed the calm but not editable now (another helper owns the file); remove the entry when it is fixed
OWED = {"reach_map_proof.py": "being edited by the live-driving helper 2026-10-22"}


def needs_calm(src):
    return "fresh_map" in src and "start_debug_game_ready" in src


def check(files):
    bad = []
    for f in files:
        name = os.path.basename(f)
        src = open(f, encoding="utf-8").read()
        if needs_calm(src) and not CALM.search(src) and name not in OWED:
            bad.append(name)
    return bad


def main():
    files = sorted(glob.glob(os.path.join(HERE, "*_proof*.py")) + [os.path.join(HERE, "validation_v2.py")])
    files = [f for f in files if "selftest_" not in f]
    ok = True
    judged = [os.path.basename(f) for f in files if needs_calm(open(f, encoding="utf-8").read())]
    if len(judged) < 6:
        print("FAIL instrument blind: only %d fresh-map proofs seen: %s" % (len(judged), judged))
        ok = False
    bad = check(files)
    if bad:
        print("FAIL preflight skips site_calm: %s" % bad)
        ok = False
    # can-fail: strip the call from a real proof's text and the check must object
    probe = open(os.path.join(HERE, "lines_proof.py"), encoding="utf-8").read()
    if not CALM.search(probe) or CALM.search(CALM.sub("", probe)):
        print("FAIL check cannot see the call in lines_proof.py")
        ok = False
    for k in OWED:
        if not os.path.exists(os.path.join(HERE, k)):
            print("FAIL OWED names a missing file %s" % k)
            ok = False
    print("preflight calm: %d fresh-map proofs, owed %s -> %s" % (len(judged), sorted(OWED), "PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
