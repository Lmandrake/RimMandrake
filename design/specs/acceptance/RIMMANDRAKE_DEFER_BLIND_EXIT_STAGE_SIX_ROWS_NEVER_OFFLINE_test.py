"""Acceptance: the blind exit reader (maturation.read_exit) must clear lane 1 when its only non-PASS rows are
not_kernel UNSETTLED rows whose bars all prove at stage 6 or 8 (GimmeSomeSlack cycle 1's 14 L1_NK_* rows, per
version/test_table.md), and must still refuse a not_kernel UNSETTLED row naming an offline bar (no_hose proves at 4-5).
Read on a temp copy of design/concepts/GimmeSomeSlack whose lane-1 files hold only the rows under test.
rc 1 on the base de4383a05d (case stage6: lane1_fail_cleared_after_fix False); rc 0 on a fix."""
import json, os, shutil, sys, tempfile
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "rimflow"))
import maturation as M

SRC = os.path.join(ROOT, "design", "concepts", "GimmeSomeSlack")
C1 = os.path.join("version", "blind_challenge", "cycle_1")
rows = [json.loads(l) for l in open(os.path.join(SRC, C1, "lane2", "lane1_rows_after_fix.jsonl")) if l.strip()]
nk = [r for r in rows if r.get("kind") == "not_kernel" and r.get("verdict") == "UNSETTLED"]
assert len(nk) == 14, "expected the 14 cycle-1 not_kernel rows, read %d" % len(nk)
planted = {"id": "L1_NK_PLANTED_OFFLINE", "bars": ["no_hose"], "kind": "not_kernel", "verdict": "UNSETTLED",
           "cases": 0, "detail": "planted: an offline bar dodged as not_kernel"}


def cleared(lane1):
    tmp = tempfile.mkdtemp()
    try:
        dst = os.path.join(tmp, "design", "concepts", "GimmeSomeSlack")
        shutil.copytree(SRC, dst)
        for rel in (os.path.join("lane1", "lane1_rows.jsonl"), os.path.join("lane2", "lane1_rows_after_fix.jsonl")):
            with open(os.path.join(dst, C1, rel), "w") as fh:
                fh.write("".join(json.dumps(r) + "\n" for r in lane1))
        return M.read_exit(tmp, "GimmeSomeSlack", 1).get("checks", {}).get("lane1_fail_cleared_after_fix")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


fails = []
got = cleared(nk)
if got is not True:
    fails.append("stage6: 14 Stage-6/8 not_kernel rows still block lane 1 (lane1_fail_cleared_after_fix %r)" % got)
got = cleared(nk + [planted])
if got is not False:
    fails.append("offline: a not_kernel row on offline bar no_hose cleared lane 1 (lane1_fail_cleared_after_fix %r)" % got)
for f in fails:
    print("FAIL", f)
print("PASS" if not fails else "%d FAIL" % len(fails))
sys.exit(1 if fails else 0)
