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


CHAINS = ["chain_a", "chain_b"]


def ext(verdicts, h="H" * 64, running=TIER, ran=CHAINS, **kw):
    """A step-4 (extension_proof.py) result: one component per verdict, spread over CHAINS."""
    chains = [dict(name=CHAINS[i % 2], components=[]) for i in range(2)]
    for i, v in enumerate(verdicts):
        chains[i % 2]["components"].append(dict(name="c%d" % i, verdict=v))
    r = dict(script="extension_proof", mod="FlowWorks", mode="live", aborted=None, refused="", chains=chains,
             all_green=all(v == "PASS" for v in verdicts), chains_run=list(ran), chains_declared=list(CHAINS),
             mod_hash=h, env=dict(running=list(running), running_sha256="x", assembly_sha256="y"))
    r.update(kw)
    return r


def t_judge_step4():
    ref, s4 = record.judge_step4(ext(["PASS", "PASS", "PASS"]), "FlowWorks", "H" * 64, TIER)
    ok(not ref and s4["status"] == "PASS" and s4["pass"] == 3, "step 4: an all-PASS full run judges PASS")
    ref, s4 = record.judge_step4(ext(["PASS", "FAIL", "PASS"]), "FlowWorks", "H" * 64, TIER)
    ok(not ref and s4["status"] == "FAIL" and s4["fail"] == ["chain_b/c1"],
       "step 4: a planted FAIL component judges FAIL, naming it: %s" % s4["fail"])
    ref, s4 = record.judge_step4(ext(["PASS", "UNMEASURED"]), "FlowWorks", "H" * 64, TIER)
    ok(s4["status"] == "UNMEASURED" and s4["unmeasured"] == ["chain_b/c1"], "step 4: an UNMEASURED component is not a pass")
    ref, s4 = record.judge_step4(None, "FlowWorks", "H" * 64, TIER)
    ok(not ref and s4["status"] == "UNMEASURED", "step 4: no result -> UNMEASURED, never PASS")
    ref, s4 = record.judge_step4(ext(["PASS"], all_green=False), "FlowWorks", "H" * 64, TIER)
    ok(s4["status"] == "UNMEASURED", "step 4: all_green false with every component PASS is not a pass")
    ref, _ = record.judge_step4(ext(["PASS", "PASS"]), "FlowWorks", "G" * 64, TIER)
    ok(any("STALE" in r for r in ref), "step 4: a result at another mod hash is refused STALE")
    ref, _ = record.judge_step4(ext(["PASS", "PASS"], ran=CHAINS[:1]), "FlowWorks", "H" * 64, TIER)
    ok(any("PARTIAL" in r and "chain_b" in r for r in ref), "step 4: a --chains subset run is refused PARTIAL")
    ref, _ = record.judge_step4(ext(["PASS"], chains_declared=None), "FlowWorks", "H" * 64, TIER)
    ok(any("chains_declared" in r for r in ref), "step 4: a legacy result with no chains_declared is refused")
    ref, _ = record.judge_step4(ext(["PASS"], mode=None, mod_hash=None, env={}), "FlowWorks", "H" * 64, TIER)
    ok(len(ref) >= 3, "step 4: a pre-contract result (no mode/mod_hash/env) is refused: %d refusals" % len(ref))
    ref, _ = record.judge_step4(ext(["PASS"], running=TIER + ["x.y"]), "FlowWorks", "H" * 64, TIER)
    ok(any("not the declared tier" in r for r in ref), "step 4: an off-tier run is refused")
    ref, _ = record.judge_step4(ext([], chains=[]), "FlowWorks", "H" * 64, TIER)
    ok(any("no components" in r for r in ref), "step 4: a result with no components is refused")
    ref, _ = record.judge_step4(ext(["PASS"], refused="floor"), "FlowWorks", "H" * 64, TIER)
    ok(any("REFUSED" in r for r in ref), "step 4: a run the floor refused is refused")


def t_step4_end_to_end_temp_registry():
    import floor
    mod_dir = runner.find_mod_dir("FlowWorks")
    ok(status.step4_required(mod_dir), "FlowWorks ships northstar/extension_proof.py, so it owes a step 4")
    keep = (status.LOG_PATH, status.LOCK_PATH)
    real_before = open(keep[0], "rb").read() if os.path.isfile(keep[0]) else None
    h = status.mod_hash(mod_dir)
    rows_pass = [dict(id="A1", status="PASS"), dict(id="A2", status="PASS")]
    with tempfile.TemporaryDirectory() as tmp:
        status.LOG_PATH = os.path.join(tmp, "modcheck_status.json")
        status.LOCK_PATH = status.LOG_PATH + ".lock"
        try:
            core, e4 = os.path.join(tmp, "core.json"), os.path.join(tmp, "ext.json")
            with open(core, "w") as f:
                json.dump(res(rows_pass, h=h), f)
            R = lambda t: (TIER, [])                            # noqa: E731

            with open(e4, "w") as f:
                json.dump(ext(["PASS", "FAIL", "PASS"], h=h), f)
            code, msg, e = record.record("FlowWorks", core, "flowworks", ext_path=e4, _resolve=R)
            ok(code == 0 and e["status"] == "RED" and e["step4"]["status"] == "FAIL",
               "PLANTED: a green core + a failing step 4 records RED (%s)" % msg)
            chk = status.check("FlowWorks", mod_dir)
            ok(chk.startswith("RED") and "step 4 FAIL" in chk and "chain_b/c1" in chk,
               "status.check names the failing step-4 component: %s" % chk)
            fr = [r for r in floor.triage(runner.ROOT, only={"FlowWorks"})[0] if r["mod"] == "FlowWorks"]
            ok(fr and fr[0]["step4"] == "FAIL", "floor triage reads step 4 FAIL: %s" % (fr and fr[0]["step4"]))

            code, msg, e = record.record("FlowWorks", core, "flowworks", ext_path=None, _resolve=R)
            ok(code == 0 and e["status"] == "REFUSED" and e["step4"]["status"] == "UNMEASURED"
               and "step 4 UNMEASURED" in (e["refused"] or ""),
               "MISSING step 4: a green core records REFUSED naming step 4 (%s)" % msg)
            chk = status.check("FlowWorks", mod_dir)
            ok(chk.startswith("REFUSED") and "step 4 UNMEASURED" in chk, "status.check: %s" % chk[:90])
            fr = [r for r in floor.triage(runner.ROOT, only={"FlowWorks"})[0] if r["mod"] == "FlowWorks"]
            ok(fr and fr[0]["step4"] == "UNMEASURED", "floor triage reads a missing step 4 as UNMEASURED")

            with open(e4, "w") as f:
                json.dump(ext(["PASS", "PASS", "PASS"], h=h), f)
            code, msg, e = record.record("FlowWorks", core, "flowworks", ext_path=e4, _resolve=R)
            ok(code == 0 and e["status"] not in ("RED", "REFUSED") and e["step4"]["status"] == "PASS"
               and e["step4"]["result"].endswith("ext.json"),
               "a green core + passing step 4 is not held back by step 4 (%s)" % msg)
            ok(status.step4_live(e, mod_dir) == "PASS", "step4_live: a stored PASS at the current hash reads PASS")
            ok(status.step4_live(dict(e, step4=dict(e["step4"], mod_hash="0" * 64)), mod_dir) == "STALE",
               "step4_live: a stored PASS at another hash reads STALE")

            with open(e4, "w") as f:
                json.dump(ext(["PASS", "PASS"], h="0" * 64), f)
            code, msg, e = record.record("FlowWorks", core, "flowworks", ext_path=e4, _resolve=R)
            ok(code == 2 and e is None and "step 4: STALE" in msg, "a stale step-4 result is refused, exit 2")

            # a GREEN entry with no step 4 (a `modcheck run`, or an entry from before step 4 was wired) is not GREEN
            data = status.load()
            data["FlowWorks"] = {"hash": h, "run_id": "x", "status": "GREEN", "ts": 0, "minor": None,
                                 "owner_review": None, "refused": None}
            status.save(data)
            chk = status.check("FlowWorks", mod_dir)
            ok(chk.startswith("UNMEASURED (step 4"), "a GREEN entry with no step-4 record reads UNMEASURED: %s" % chk)
            data["FlowWorks"]["step4"] = {"status": "PASS", "mod_hash": h}
            status.save(data)
            ok(status.check("FlowWorks", mod_dir) == "GREEN", "the same entry with a step-4 PASS at the hash is GREEN")
            data["FlowWorks"]["step4"] = {"status": "PASS", "mod_hash": "0" * 64}
            status.save(data)
            ok(status.check("FlowWorks", mod_dir).startswith("STALE (step 4"), "a step-4 PASS at an old hash is STALE")
        finally:
            status.LOG_PATH, status.LOCK_PATH = keep
    real_after = open(keep[0], "rb").read() if os.path.isfile(keep[0]) else None
    ok(real_before == real_after, "step 4: the real modcheck_status.json was not touched")


if __name__ == "__main__":
    t_judge()
    t_hash_ignores_northstar_harness()
    t_end_to_end_temp_registry()
    t_judge_step4()
    t_step4_end_to_end_temp_registry()
    print("%d FAIL" % len(FAILS))
    sys.exit(1 if FAILS else 0)
