#!/usr/bin/env python3
"""Selftest for modcheck.record (`modcheck record`): every refusal fires, the verdict never
reads UNBUILT/UNCOVERED bars as green, and the real registry is never touched (LOG_PATH is
pointed at a temp file for the end-to-end case)."""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

import record  # noqa: E402
import runner  # noqa: E402
import status  # noqa: E402

FAILS = []


def ok(cond, what):
    print(("PASS  " if cond else "FAIL  ") + what)
    if not cond:
        FAILS.append(what)


TIER = ["ludeon.rimworld", "brrainz.harmony", "mandrake.rm.flowworks"]


def res(rows, h="H" * 64, running=TIER, **kw):
    r = dict(script="validation_v2", mod="FlowWorks", mode="live", aborted=None, rows=rows,
             mod_hash=h, env=dict(running=list(running), running_sha256="x", assembly_sha256="y"))
    r.update(kw)
    return r


ROWS_OK = [dict(id="A1", status="PASS"), dict(id="U_bar1", status="UNBUILT"),
           dict(id="U_bar2", status="UNBUILT"), dict(id="S6", status="UNCOVERED")]


def t_judge():
    ref, g, why, comp = record.judge(res(ROWS_OK), "FlowWorks", "H" * 64, TIER)
    ok(not ref and g, "clean live result on the tier at the current hash is recordable")
    ok("U_bar1" in why and "U_bar2" in why and "S6" in why and "2 bars UNBUILT, 1 UNCOVERED" in why,
       "UNBUILT/UNCOVERED bars are named in the refusal reason, never silently green: %s" % why)
    ok(comp["counts"] == {"PASS": 1, "UNBUILT": 2, "UNCOVERED": 1}, "components tally the rows")
    ref, g, why, _ = record.judge(res([dict(id="A1", status="PASS")]), "FlowWorks", "H" * 64, TIER)
    ok(not ref and g and not why, "all PASS -> no refusal reason (verdict_for decides)")
    ref, g, why, _ = record.judge(res(ROWS_OK + [dict(id="E7", status="FAIL")]), "FlowWorks", "H" * 64, TIER)
    ok(not g and not why, "a FAIL row -> not green, and RED rather than REFUSED")
    ref, g, why, _ = record.judge(res(ROWS_OK + [dict(id="E6n", status="UNMEASURED")]), "FlowWorks", "H" * 64, TIER)
    ok(not g, "an UNMEASURED row -> not green")
    ref, *_ = record.judge(res(ROWS_OK), "FlowWorks", "G" * 64, TIER)
    ok(any("STALE" in r for r in ref), "a result at another mod hash is refused STALE")
    ref, *_ = record.judge(res(ROWS_OK, h=None), "FlowWorks", "H" * 64, TIER)
    ok(any("no mod_hash" in r for r in ref), "a legacy result with no mod_hash is refused")
    ref, *_ = record.judge(res(ROWS_OK, running=TIER + ["sarg.alphabiomes"]), "FlowWorks", "H" * 64, TIER)
    ok(any("not the declared tier" in r and "sarg.alphabiomes" in r for r in ref),
       "an extra mod in the live list is refused, naming it")
    ref, *_ = record.judge(res(ROWS_OK, running=TIER[:2]), "FlowWorks", "H" * 64, TIER)
    ok(any("missing" in r and "flowworks" in r for r in ref), "a missing tier mod is refused")
    ref, *_ = record.judge(res(ROWS_OK, running=[]), "FlowWorks", "H" * 64, TIER)
    ok(any("env.running" in r for r in ref), "no live mod list -> refused, never skipped")
    ref, *_ = record.judge(res(ROWS_OK), "FlowWorks", "H" * 64, None)
    ok(any("could not be resolved" in r for r in ref), "an unresolvable tier is a refusal")
    ref, *_ = record.judge(res(ROWS_OK, mode="mock"), "FlowWorks", "H" * 64, TIER)
    ok(any("not a live run" in r for r in ref), "a mock run is refused")
    ref, g, *_ = record.judge(res(ROWS_OK, aborted="settings drift"), "FlowWorks", "H" * 64, TIER)
    ok(any("ABORTED" in r for r in ref) and not g, "an aborted run is refused")
    ref, *_ = record.judge(res(ROWS_OK, mod="Pits"), "FlowWorks", "H" * 64, TIER)
    ok(any("not 'FlowWorks'" in r for r in ref), "another mod's result is refused")


def t_hash_ignores_northstar_harness():
    with tempfile.TemporaryDirectory() as d:
        with open(os.path.join(d, "a.xml"), "w") as f:
            f.write("<x/>")
        h1 = status.mod_hash(d)
        os.makedirs(os.path.join(d, "northstar"))
        with open(os.path.join(d, "northstar", "validation_v2_result_1.json"), "w") as f:
            f.write("{}")
        ok(status.mod_hash(d) == h1, "mod_hash: a result JSON written into northstar/ does not move the hash")


def t_end_to_end_temp_registry():
    mod_dir = runner.find_mod_dir("FlowWorks")
    keep = (status.LOG_PATH, status.LOCK_PATH)
    real_before = open(keep[0], "rb").read() if os.path.isfile(keep[0]) else None
    with tempfile.TemporaryDirectory() as tmp:
        status.LOG_PATH = os.path.join(tmp, "modcheck_status.json")
        status.LOCK_PATH = status.LOG_PATH + ".lock"
        try:
            p = os.path.join(tmp, "r.json")
            with open(p, "w") as f:
                json.dump(res(ROWS_OK, h=status.mod_hash(mod_dir)), f)
            code, msg, e = record.record("FlowWorks", p, "flowworks", _resolve=lambda t: (TIER, []))
            ok(code == 0 and e and e["status"] == "REFUSED", "end-to-end: recorded as REFUSED (%s)" % msg)
            ok(e and e["components"]["unbuilt"] == ["U_bar1", "U_bar2"] and e["source"]["verb"] == "modcheck record",
               "end-to-end: components + source ride in the entry")
            chk = status.check("FlowWorks", mod_dir)
            ok(chk.startswith("REFUSED (") and "U_bar1" in chk, "status.check shows the stored reason: %s" % chk[:80])
            with open(p, "w") as f:
                json.dump(res(ROWS_OK, h="0" * 64), f)
            code, msg, e = record.record("FlowWorks", p, "flowworks", _resolve=lambda t: (TIER, []))
            ok(code == 2 and e is None and "STALE" in msg, "end-to-end: stale result refused, exit 2")
            code, msg, e = record.record("FlowWorks", p, "flowworks",
                                         _resolve=lambda t: (TIER, ["forbidden mod in closure: x"]))
            ok(code == 2 and "forbidden" in msg, "end-to-end: a tier guard refusal blocks the record")
        finally:
            status.LOG_PATH, status.LOCK_PATH = keep
    real_after = open(keep[0], "rb").read() if os.path.isfile(keep[0]) else None
    ok(real_before == real_after, "the real modcheck_status.json was not touched")


if __name__ == "__main__":
    t_judge()
    t_hash_ignores_northstar_harness()
    t_end_to_end_temp_registry()
    print("%d FAIL" % len(FAILS))
    sys.exit(1 if FAILS else 0)
