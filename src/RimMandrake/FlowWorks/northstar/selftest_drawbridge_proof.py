"""The drawbridge functional script runs every path offline (drawbridge_proof.py --mock, FakeBridge): all twelve rows (the eleven R13 rows
plus WINCH_DESPAWN_CRASHES) are written, every mock verdict is PASS, and no mock row claims a live verdict. Can-fail, one per row: a FakeBridge fault that
breaks the ruled behaviour turns that row's mock verdict FAIL. The MOD/SITE/HARNESS split (PROOF_VERDICTS_REPAIR_SAME_BUG_
EVERY_ROUND): the owed C# proof class missing, a clock that never moved, a site that is not the scene and raiders that
never came near each read UNMEASURED with the right class, never a mod FAIL. Proves the SCRIPT, never the game.

    python3 src/RimMandrake/FlowWorks/northstar/selftest_drawbridge_proof.py
"""
import io
import json
import os
import sys
import tempfile
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import drawbridge_proof as DP  # noqa: E402

# fault -> (row it must break, the mock verdict it must give, the class it must carry)
CAN_FAIL = {
    "tip_all_fall": ("RAISE_TIPS_RIDERS", "FAIL", "MOD"),
    "no_repath": ("RAISE_PATH", "FAIL", "MOD"),
    "underpass_tipped": ("RAISE_SPARES_UNDERPASS", "FAIL", "MOD"),
    "lower_from_far": ("LOWER_ONLY_FROM_WINCH", "FAIL", "MOD"),
    "tip_colony_bank": ("TWO_LEAF_TIPS_OWN_HINGE", "FAIL", "MOD"),
    "trapped_locks": ("HOSTILE_LOCKS", "FAIL", "MOD"),
    "freeze_ignored": ("STEEL_UNPOWERED_FREEZES", "FAIL", "MOD"),
    "no_crash": ("WINCH_LOST_CRASHES", "FAIL", "MOD"),
    "despawn_stale": ("WINCH_DESPAWN_CRASHES", "FAIL", "MOD"),
    "raid_loop": ("RAID_UP", "FAIL", "MOD"),
    "dup_plank": ("RAID_PLANK", "FAIL", "MOD"),
    "replay_tip": ("SAVE_MIDRAISE", "FAIL", "MOD"),
    "no_free": ("RAISE_TIPS_RIDERS", "UNMEASURED", "SITE"),
    "far_reaches_winch": ("LOWER_ONLY_FROM_WINCH", "UNMEASURED", "SITE"),
    "far_raiders": ("RAID_UP", "UNMEASURED", "SITE"),
}
TICKLESS = {"TWO_LEAF_TIPS_OWN_HINGE"}   # LOWER_ONLY_FROM_WINCH ticks since 2026-10-22 (1.6 pathfinder settle)


def run(d, name, *argv):
    out = os.path.join(d, name + ".json")
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = DP.main(["--mock", out] + list(argv))
    rows = json.load(open(out, encoding="utf-8"))["rows"]
    return rc, {r["id"]: r for r in rows}, buf.getvalue()


def main():
    fails = []
    with tempfile.TemporaryDirectory() as d:
        rc, rows, txt = run(d, "clean")
        if rc != 0:
            fails.append("clean mock exit %s: %s" % (rc, txt.strip().splitlines()[-1]))
        if list(rows) != DP.ROW_IDS:
            fails.append("rows %s, want the twelve rows in order %s" % (list(rows), DP.ROW_IDS))
        for rid, r in rows.items():
            if r["status"] != "SKIP":
                fails.append("%s: a mock row claimed a live verdict (%s)" % (rid, r["status"]))
            if r["detail"].get("mock") != "PASS":
                fails.append("%s: clean mock verdict %s" % (rid, r["detail"].get("mock")))
        for fault, (rid, want, cls) in sorted(CAN_FAIL.items()):
            _, got, _ = run(d, fault, "--only", rid, "--mock-faults", fault)
            r = got.get(rid) or {}
            if r.get("detail", {}).get("mock") != want or r.get("class") != cls:
                fails.append("can-fail %s: %s reads %s/%s, want %s/%s" % (fault, rid, r.get("detail", {}).get("mock"),
                                                                          r.get("class"), want, cls))
        # RM_DrawbridgeProofs not in the loaded FlowWorks (an old deploy): every row UNMEASURED/HARNESS, none FAIL, exit 2
        rc, got, _ = run(d, "no_proofs", "--mock-faults", "no_proofs")
        if rc != 2 or list(got) != DP.ROW_IDS or any((r["detail"].get("mock"), r["class"]) != ("UNMEASURED", "HARNESS")
                                                       for r in got.values()):
            fails.append("owed proof class: rc=%s rows=%s" % (rc, {k: (v["detail"].get("mock"), v["class"]) for k, v in got.items()}))
        # a clock that never moved: every row that waits on it is UNMEASURED/HARNESS; the tickless ones still PASS
        _, got, _ = run(d, "noclock", "--mock-faults", "noclock")
        for rid, r in got.items():
            want = ("PASS", "MOD") if rid in TICKLESS else ("UNMEASURED", "HARNESS")
            if (r["detail"].get("mock"), r["class"]) != want:
                fails.append("clock never moved: %s reads %s/%s, want %s/%s" % ((rid, r["detail"].get("mock"), r["class"]) + want))
        if any(r["detail"].get("mock") == "FAIL" for r in got.values()):
            fails.append("clock never moved: a row scored a mod FAIL")
    # validation.py's drawbridges chain names exactly these rows and every DrawbridgeChecks.cs case, and reads this driver
    import re
    fw = os.path.dirname(HERE)
    for p_ in (os.path.join(os.path.dirname(fw), "Utils"), fw):
        if p_ not in sys.path:
            sys.path.insert(0, p_)
    import validation as VAL  # noqa: E402
    if [r[0] for r in VAL.DRAWBRIDGE_LIVE] != DP.ROW_IDS:
        fails.append("validation.DRAWBRIDGE_LIVE ids %s != drawbridge_proof.ROW_IDS" % [r[0] for r in VAL.DRAWBRIDGE_LIVE])
    cs = open(os.path.join(fw, "Source", "SelfTest", "DrawbridgeChecks.cs"), encoding="utf-8").read()
    cases = re.findall(r'Case\("(Drawbridge_\w+)"', cs)
    if not cases or sorted(cases) != sorted(VAL.DRAWBRIDGE_CASES):
        fails.append("validation.DRAWBRIDGE_CASES drifted from DrawbridgeChecks.cs: missing %s, extra %s"
                     % (sorted(set(cases) - set(VAL.DRAWBRIDGE_CASES)), sorted(set(VAL.DRAWBRIDGE_CASES) - set(cases))))
    # the C# proof class has every method the rows call, each answering the word its contract names (can-fail: a method
    # missing or renamed, or a reply word drifted from OWED_PROOFS, is caught here instead of as HARNESS on a live run)
    prf = open(os.path.join(fw, "Source", "Pits", "Drawbridge", "RM_DrawbridgeProofs.cs"), encoding="utf-8").read()
    if "public static class RM_DrawbridgeProofs" not in prf or "namespace RimMandrake.FlowWorks.Pits" not in prf:
        fails.append("RM_DrawbridgeProofs is not public static in RimMandrake.FlowWorks.Pits (DPROOF %s)" % DP.DPROOF)
    for m_, contract in sorted(DP.OWED_PROOFS.items()):
        if "public static string %s(string arg)" % m_ not in prf:
            fails.append("RM_DrawbridgeProofs.%s(string) missing" % m_)
        word = re.search(r"'([A-Z]+) ", contract)
        if word and '"%s ' % word.group(1) not in prf:
            fails.append("RM_DrawbridgeProofs.%s never answers %s" % (m_, word.group(1)))
    if '"LEAF none"' not in prf:
        fails.append("ProofLeaf off a leaf must answer 'LEAF none' (the preflight probe asks an off-map square)")
    if "drawbridge_result_*.json" not in VAL.DRIVER_RESULTS:
        fails.append("validation.DRIVER_RESULTS does not read drawbridge_result_*.json")
    for f in fails:
        print("FAIL " + f)
    print("drawbridge proof mock: %d rows, %d can-fail faults, %s" % (len(DP.ROW_IDS), len(CAN_FAIL), "ok" if not fails else "FAIL"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
