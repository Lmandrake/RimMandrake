"""The lines functional script runs every path offline (lines_proof.py --mock, FakeBridge): all nine rows are written, every
mock verdict is PASS, and no mock row claims a live verdict. Can-fail, at least one per row: a FakeBridge fault that breaks
the ruled behaviour turns that row's mock verdict FAIL. The MOD/SITE/HARNESS split (PROOF_VERDICTS_REPAIR_SAME_BUG_EVERY_
ROUND): the owed C# proof class missing, a clock that never moved, a site that is not the scene (a timber deck for the rope
row, no cover, the shock switched off, a wreck on the fallen square, an unpowered pump) each read UNMEASURED with the right
class, never a mod FAIL. Also: validation.py's lines chain names exactly these rows and every C# case of the line suites,
and RM_LineProofs carries every method the rows call. Proves the SCRIPT, never the game.

    python3 src/RimMandrake/FlowWorks/northstar/selftest_lines_proof.py
"""
import io
import json
import os
import re
import sys
import tempfile
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lines_proof as LP  # noqa: E402

# fault -> (row it must break, the mock verdict it must give, the class it must carry)
CAN_FAIL = {
    "pipe_on_rope": ("ROPE_DECK_RIGID_REFUSED_FLEX_OK", "FAIL", "MOD"),
    "hose_avoids_deck": ("ROPE_DECK_RIGID_REFUSED_FLEX_OK", "FAIL", "MOD"),
    "rope_is_timber": ("ROPE_DECK_RIGID_REFUSED_FLEX_OK", "UNMEASURED", "SITE"),
    "cover_open": ("COVER_CARRIES_NO_HOSE", "FAIL", "MOD"),
    "no_cover": ("COVER_CARRIES_NO_HOSE", "UNMEASURED", "SITE"),
    "span_no_join": ("POLE_SPAN_CARRIES_LIQUID", "FAIL", "MOD"),
    "dig_no_break": ("DIG_UNDER_PIPE_SPLITS_NET", "FAIL", "MOD"),
    "dig_breaks_twice": ("DIG_UNDER_PIPE_SPLITS_NET", "FAIL", "MOD"),
    "deck_cord_dead": ("CORD_DECK_LAMP_LIT", "FAIL", "MOD"),
    "leaf_no_cut": ("LEAF_RAISED_LAMP_DARK", "FAIL", "MOD"),
    "leaf_stays_dark": ("LEAF_RAISED_LAMP_DARK", "FAIL", "MOD"),
    "double_split": ("COLLAPSE_CORD_SHOCKS_ONCE", "FAIL", "MOD"),
    "no_shock": ("COLLAPSE_CORD_SHOCKS_ONCE", "FAIL", "MOD"),
    "shock_off": ("COLLAPSE_CORD_SHOCKS_ONCE", "UNMEASURED", "SITE"),
    "wreck_blocks": ("COLLAPSE_CORD_SHOCKS_ONCE", "UNMEASURED", "SITE"),
    "no_drain": ("LADDER_HOSE_DRAINS_RAISED_STAYS", "FAIL", "MOD"),
    "raise_cuts": ("LADDER_HOSE_DRAINS_RAISED_STAYS", "FAIL", "MOD"),
    "no_power": ("LADDER_HOSE_DRAINS_RAISED_STAYS", "UNMEASURED", "SITE"),
    "no_reroute": ("DIG_REROUTES_LAID_HOSE", "FAIL", "MOD"),
    "reroute_retracts": ("DIG_REROUTES_LAID_HOSE", "FAIL", "MOD"),
    "wreck_shields": ("COLLAPSE_CORD_SHOCKS_ONCE", "FAIL", "MOD"),
    "cover_no_fall": ("COVER_BREAK_DROPS_RIDER", "FAIL", "MOD"),
    "history_lost": ("PITFALL_SAVED_ARRIVAL_FALLS", "FAIL", "MOD"),
}


def run(d, name, *argv):
    out = os.path.join(d, name + ".json")
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = LP.main(["--mock", out] + list(argv))
    rows = json.load(open(out, encoding="utf-8"))["rows"]
    return rc, {r["id"]: r for r in rows}, buf.getvalue()


def main():
    fails = []
    with tempfile.TemporaryDirectory() as d:
        rc, rows, txt = run(d, "clean")
        if rc != 0:
            fails.append("clean mock exit %s: %s" % (rc, txt.strip().splitlines()[-1]))
        if list(rows) != LP.ROW_IDS:
            fails.append("rows %s, want the nine rows in order %s" % (list(rows), LP.ROW_IDS))
        for rid, r in rows.items():
            if r["status"] != "SKIP":
                fails.append("%s: a mock row claimed a live verdict (%s)" % (rid, r["status"]))
            if r["detail"].get("mock") != "PASS":
                fails.append("%s: clean mock verdict %s (%s)" % (rid, r["detail"].get("mock"),
                                                                  json.dumps(r["detail"], default=str)[:400]))
            if r.get("item") != LP.ROW_ITEM[rid]:
                fails.append("%s: row names item %s" % (rid, r.get("item")))
        missing = set(LP.ROW_IDS) - {v[0] for v in CAN_FAIL.values() if v[1] == "FAIL"}
        if missing:
            fails.append("rows with no MOD can-fail: %s" % sorted(missing))
        for fault, (rid, want, cls) in sorted(CAN_FAIL.items()):
            _, got, _ = run(d, fault, "--only", rid, "--mock-faults", fault)
            r = got.get(rid) or {}
            if r.get("detail", {}).get("mock") != want or r.get("class") != cls:
                fails.append("can-fail %s: %s reads %s/%s, want %s/%s (%s)" % (fault, rid, r.get("detail", {}).get("mock"),
                                                                               r.get("class"), want, cls,
                                                                               json.dumps(r.get("detail"), default=str)[:300]))
        # RM_LineProofs not in the loaded FlowWorks (an old deploy): every row UNMEASURED/HARNESS, none FAIL, exit 2
        rc, got, _ = run(d, "no_proofs", "--mock-faults", "no_proofs")
        if rc != 2 or list(got) != LP.ROW_IDS or any((r["detail"].get("mock"), r["class"]) != ("UNMEASURED", "HARNESS")
                                                       for r in got.values()):
            fails.append("owed proof class: rc=%s rows=%s" % (rc, {k: (v["detail"].get("mock"), v["class"]) for k, v in got.items()}))
        # a clock that never moved: every row waits on it, so every row is UNMEASURED/HARNESS and none a mod FAIL
        _, got, _ = run(d, "noclock", "--mock-faults", "noclock")
        for rid, r in got.items():
            if (r["detail"].get("mock"), r["class"]) != ("UNMEASURED", "HARNESS"):
                fails.append("clock never moved: %s reads %s/%s" % (rid, r["detail"].get("mock"), r["class"]))
    # validation.py's lines chain names exactly these rows and every C# case of the line suites, and reads this driver
    fw = os.path.dirname(HERE)
    for p_ in (os.path.join(os.path.dirname(fw), "Utils"), fw):
        if p_ not in sys.path:
            sys.path.insert(0, p_)
    import validation as VAL  # noqa: E402
    if [r[0] for r in VAL.LINES_LIVE] != LP.ROW_IDS:
        fails.append("validation.LINES_LIVE ids %s != lines_proof.ROW_IDS" % [r[0] for r in VAL.LINES_LIVE])
    cases = []
    for f in VAL.LINES_CASE_FILES:
        cases += re.findall(r'Case\("(\w+)"', open(os.path.join(fw, "Source", "SelfTest", f), encoding="utf-8").read())
    if not cases or sorted(cases) != sorted(VAL.LINES_CASES):
        fails.append("validation.LINES_CASES drifted from %s: missing %s, extra %s" % (
            ",".join(VAL.LINES_CASE_FILES), sorted(set(cases) - set(VAL.LINES_CASES)), sorted(set(VAL.LINES_CASES) - set(cases))))
    if "lines_result_*.json" not in VAL.DRIVER_RESULTS:
        fails.append("validation.DRIVER_RESULTS does not read lines_result_*.json")
    # the C# proof class has every method the rows call, each answering the word its contract names
    prf = open(os.path.join(fw, "Source", "Machinery", "RM_LineProofs.cs"), encoding="utf-8").read()
    if "public static class RM_LineProofs" not in prf or "namespace RimMandrake.FlowWorks.Machinery" not in prf:
        fails.append("RM_LineProofs is not public static in RimMandrake.FlowWorks.Machinery (LPROOF %s)" % LP.LPROOF)
    for m_, contract in sorted(LP.OWED_PROOFS.items()):
        if "public static string %s(string arg)" % m_ not in prf:
            fails.append("RM_LineProofs.%s(string) missing" % m_)
        word = re.search(r"'([A-Z]+) ", contract)
        if word and '"%s ' % word.group(1) not in prf:
            fails.append("RM_LineProofs.%s never answers %s" % (m_, word.group(1)))
    csproj = open(os.path.join(fw, "Source", "RimMandrake_FlowWorks.csproj"), encoding="utf-8").read()
    if "Machinery\\RM_LineProofs.cs" not in csproj:
        fails.append("RM_LineProofs.cs is not in the mod build")
    # the proofs the rows borrow from other classes exist under the names called
    for rel, sig in ((("Pits", "Suspension", "RM_SuspensionProofs.cs"), "public static string ProofBuild(string arg)"),
                     (("Pits", "Suspension", "RM_SuspensionProofs.cs"), "public static string ProofFell(string arg)"),
                     (("Pits", "Drawbridge", "RM_DrawbridgeProofs.cs"), "public static string ProofMakeDrawbridge(string arg)"),
                     (("Pits", "Drawbridge", "RM_DrawbridgeProofs.cs"), "public static string ProofDevSet(string arg)"),
                     (("RM_PromotionProofs.cs",), "public static string ProofLadder(string arg)")):
        if sig not in open(os.path.join(fw, "Source", *rel), encoding="utf-8").read():
            fails.append("%s: %s missing" % ("/".join(rel), sig))
    for f in fails:
        print("FAIL " + f)
    print("lines proof mock: %d rows, %d can-fail faults, %s" % (len(LP.ROW_IDS), len(CAN_FAIL), "ok" if not fails else "FAIL"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
