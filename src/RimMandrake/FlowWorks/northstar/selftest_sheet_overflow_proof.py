"""The canal-overflow functional script runs every path offline (sheet_overflow_proof.py --mock, FakeBridge): all thirteen rows
are written in order, every built row's mock verdict is PASS, the two rows whose feature a Stage-1 build lacks (crops, cap
setting) read UNMEASURED/NOT_BUILT with a reason (never PASS), and no mock row claims a live verdict. With the features
present (crops_built, cap_setting_built) those two rows score PASS too. Can-fail, at least one MOD fault per row: each turns
that row's mock verdict FAIL. The MOD/SITE/HARNESS split: the owed C# proof class missing, a clock that never moved, a canal
that was not full, a map that never got cold read UNMEASURED with the right class, never a mod FAIL. Also: every RM_SheetProofs
method a row calls is in OWED_PROOFS, and perf rows stay out of the exit code. Proves the SCRIPT, never the game.

    python3 src/RimMandrake/FlowWorks/northstar/selftest_sheet_overflow_proof.py
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
import sheet_overflow_proof as SP  # noqa: E402

BUILT = "crops_built,cap_setting_built"
# fault -> (row it must break, the mock verdict it must give, the class it must carry, extra faults it needs)
CAN_FAIL = {
    "pump_no_spill": ("PUMP_FULL_CANAL_SPILLS_SHEET", "FAIL", "MOD", ""),
    "pump_leaks": ("PUMP_FULL_CANAL_SPILLS_SHEET", "FAIL", "MOD", ""),
    "canal_not_full": ("PUMP_FULL_CANAL_SPILLS_SHEET", "UNMEASURED", "SITE", ""),
    "rain_no_spill": ("RAIN_FULL_CANAL_SPILLS_SHEET", "FAIL", "MOD", ""),
    "fillin_destroys": ("FILLIN_HOMELESS_SPILLS", "FAIL", "MOD", ""),
    "no_return": ("SHEET_RETURNS_TO_PIT", "FAIL", "MOD", ""),
    "unbounded": ("SPILL_EXTENT_FINITE", "FAIL", "MOD", ""),
    "cap_destroys": ("BACKPRESSURE_REFUSES_DESTROYS_NOTHING", "FAIL", "MOD", ""),
    "door_seals": ("DOOR_LEAKS_SLOWLY", "FAIL", "MOD", ""),
    "door_open": ("DOOR_LEAKS_SLOWLY", "FAIL", "MOD", ""),
    "off_still_spills": ("SETTING_OFF_STOPS_NEW_KEEPS_DRAINING", "FAIL", "MOD", ""),
    "off_purges": ("SETTING_OFF_STOPS_NEW_KEEPS_DRAINING", "FAIL", "MOD", ""),
    "crop_never_dies": ("CROPS_IRRIGATE_THEN_DROWN", "FAIL", "MOD", "crops_built"),
    "no_freeze": ("SHEET_FREEZES_AND_THAWS", "FAIL", "MOD", ""),
    "ice_loses": ("SHEET_FREEZES_AND_THAWS", "FAIL", "MOD", ""),
    "never_cold": ("SHEET_FREEZES_AND_THAWS", "UNMEASURED", "SITE", ""),
    "cap_lower_cuts": ("LOWERED_CAP_KEEPS_DEEPER_WATER", "FAIL", "MOD", "cap_setting_built"),
    "ledger_open": ("LEDGER_CONSERVES_TO_THE_DL", "FAIL", "MOD", ""),
    "load_drift": ("SAVE_LOAD_CONTINUES_IDENTICAL", "FAIL", "MOD", ""),
}
# rows a fault needs staged before it (the whole-run ledger row needs a booked transfer)
NEEDS = {"LEDGER_CONSERVES_TO_THE_DL": ["SHEET_RETURNS_TO_PIT"]}


def run(d, name, *argv):
    out = os.path.join(d, name + ".json")
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = SP.main(["--mock", out] + list(argv))
    res = json.load(open(out, encoding="utf-8"))
    return rc, {r["id"]: r for r in res["rows"]}, buf.getvalue(), res


def main():
    fails = []
    with tempfile.TemporaryDirectory() as d:
        rc, rows, txt, res = run(d, "clean")
        if rc != 0:
            fails.append("clean mock exit %s: %s" % (rc, txt.strip().splitlines()[-1]))
        if list(rows) != SP.ROW_IDS:
            fails.append("rows %s, want the thirteen rows in order %s" % (list(rows), SP.ROW_IDS))
        for rid, r in rows.items():
            if r["status"] != "SKIP":
                fails.append("%s: a mock row claimed a live verdict (%s)" % (rid, r["status"]))
            want = ("UNMEASURED", "NOT_BUILT") if rid in SP.GATED else ("PASS", "MOD")
            if (r["detail"].get("mock"), r["class"]) != want:
                fails.append("%s: clean mock %s/%s, want %s/%s (%s)" % ((rid, r["detail"].get("mock"), r["class"]) + want
                                                                       + (json.dumps(r["detail"], default=str)[:300],)))
            if rid in SP.GATED and not r["detail"].get("why"):
                fails.append("%s: NOT_BUILT row names no reason" % rid)
        if [p["id"] for p in res["perf"]] != SP.PERF_IDS:
            fails.append("perf rows %s, want %s" % ([p["id"] for p in res["perf"]], SP.PERF_IDS))
        if any(p["id"] in rows for p in res["perf"]):
            fails.append("a perf row leaked into the acceptance rows")
        if not all(p["detail"].get("provisional") for p in res["perf"]):
            fails.append("a perf row is not marked provisional")
        # features present: the gated rows score
        rc, rows, txt, _ = run(d, "built", "--mock-faults", BUILT)
        if rc != 0:
            fails.append("built mock exit %s: %s" % (rc, txt.strip().splitlines()[-1]))
        for rid in SP.GATED:
            if rows.get(rid, {}).get("detail", {}).get("mock") != "PASS":
                fails.append("%s with its feature built: mock %s" % (rid, rows.get(rid, {}).get("detail", {}).get("mock")))
        missing = set(SP.ROW_IDS) - {v[0] for v in CAN_FAIL.values() if v[1] == "FAIL"}
        if missing:
            fails.append("rows with no MOD can-fail: %s" % sorted(missing))
        for fault, (rid, want, cls, extra) in sorted(CAN_FAIL.items()):
            fl = ",".join(x for x in (fault, extra) if x)
            only = ",".join(NEEDS.get(rid, []) + [rid])
            _, got, _, _ = run(d, fault, "--only", only, "--mock-faults", fl)
            r = got.get(rid)
            if r is None:
                fails.append("%s: row %s not written" % (fault, rid))
                continue
            if (r["detail"].get("mock"), r["class"]) != (want, cls):
                fails.append("%s: %s mock %s/%s, want %s/%s (%s)" % (fault, rid, r["detail"].get("mock"), r["class"], want, cls,
                                                                   json.dumps(r["detail"], default=str)[:300]))
        # the C# proof class missing: every row UNMEASURED/HARNESS, none FAIL
        rc, got, _, _ = run(d, "noproofs", "--mock-faults", "no_proofs")
        bad = [k for k, r in got.items() if (r["detail"].get("mock"), r["class"]) != ("UNMEASURED", "HARNESS")]
        if bad or rc == 1 or len(got) != len(SP.ROW_IDS):
            fails.append("no_proofs: rows not all UNMEASURED/HARNESS: %s (rc %s)" % (bad, rc))
        # a clock that never moved never reads as a mod FAIL
        _, got, _, _ = run(d, "noclock", "--mock-faults", "noclock", "--only", "SPILL_EXTENT_FINITE,SHEET_RETURNS_TO_PIT")
        for k, r in got.items():
            if r["detail"].get("mock") == "FAIL" or r["class"] == "MOD" and r["detail"].get("mock") == "PASS":
                fails.append("noclock: %s read %s/%s" % (k, r["detail"].get("mock"), r["class"]))
    # every RM_SheetProofs method the rows call is in the owed table
    src = open(os.path.join(HERE, "sheet_overflow_proof.py"), encoding="utf-8").read()
    called = set(re.findall(r'sp\("(Proof\w+)"', src)) | set(re.findall(r'method="(ProofSheet\w+)"', src))
    called |= {m for m in re.findall(r'"(ProofSheet\w+)"', src)}
    unowed = sorted(m for m in called if m.startswith("ProofSheet") and m not in SP.OWED_PROOFS)
    if unowed:
        fails.append("RM_SheetProofs methods called but not in OWED_PROOFS: %s" % unowed)
    if fails:
        for f in fails:
            print("FAIL", f)
        return 1
    print("OK sheet_overflow_proof: %d rows (%d gated NOT_BUILT), %d perf, %d can-fails, no_proofs/noclock split"
          % (len(SP.ROW_IDS), len(SP.GATED), len(SP.PERF_IDS), len(CAN_FAIL)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
