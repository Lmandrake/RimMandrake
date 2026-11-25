#!/usr/bin/env python3
"""selftest_run_peek.py: the promises of design/specs/2026-11-25-run-peek/boundary.md, one check of each name.
Planted transcripts and run records in a temp folder; no real run, log or state is read or written."""
import datetime as dt
import json
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import detached_helper as DH  # noqa: E402
import run_peek as RP  # noqa: E402

FAILS = []
T0 = 1795600000.0
MOD = "Knock"
IDS = ["sc_barrage", "sc_spared", "sc_gas", "T_KERNEL"]


def check(name, ok, said=""):
    print("%s  %s%s" % ("PASS" if ok else "FAIL", name, ("  (%s)" % said) if said and not ok else ""))
    if not ok:
        FAILS.append(name)


def iso(t):
    return dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def call(t, cmd):
    return {"type": "assistant", "timestamp": iso(t), "message": {"content": [
        {"type": "tool_use", "name": "Bash", "input": {"command": cmd}}]}}


def say(t, text):
    return {"type": "assistant", "timestamp": iso(t), "message": {"content": [{"type": "text", "text": text}]}}


def world(tmp, unit, lines, table=True):
    """-> a run record whose clone holds the test table and whose project folder holds the transcript."""
    clone = os.path.join(tmp, "clones", unit)
    if table:
        p = os.path.join(clone, "design", "concepts", MOD, "version")
        os.makedirs(p, exist_ok=True)
        with open(os.path.join(p, "test_table.json"), "w") as fh:
            json.dump({"tests": {i: {"id": i} for i in IDS}}, fh)
    else:
        os.makedirs(clone, exist_ok=True)
    proj = os.path.join(tmp, "projects")
    d = DH.project_dir(clone, proj)
    os.makedirs(d, exist_ok=True)
    if lines is not None:
        with open(os.path.join(d, "s1.jsonl"), "w") as fh:
            for ln in lines:
                fh.write(json.dumps(ln) + "\n")
    return {"unit": unit, "item": "ITEM_" + unit, "clone": clone, "at": T0 - 10, "status": "running",
            "env": {"RM_CONTROL_MOD": MOD}}, proj


def long_run():
    """70 min on sc_barrage: a scene run named once, then its long command, then the run's PROGRESS note."""
    return [call(T0, "ls"), call(T0 + 60, "python3 scene.py run sc_barrage --game ArchSmall"),
            call(T0 + 60 + 4000, 'python3 src/RimMandrake/rimflow/cli.py note X --text "PROGRESS: theory: perf | '
                                  'experiment: sc_barrage again | reading: 3 fps | next: retry" --publish'),
            say(T0 + 4100, "Retrying sc_barrage on ArchSmall.")]


TMP = tempfile.mkdtemp(prefix="run_peek_")
NOW = T0 + 4200


def fixture():
    """-> (the long run's record, projects folder, run-record root, the tick's facts); built once in TMP."""
    if not hasattr(fixture, "got"):
        rec, proj = world(TMP, "u-long", long_run())
        short, _ = world(TMP, "u-short", [call(T0, "python3 scene.py run sc_spared"), call(T0 + 600, "ls")])
        root = os.path.join(TMP, "state")
        os.makedirs(DH.runs_dir(root), exist_ok=True)
        with open(os.path.join(DH.runs_dir(root), "u-long.json"), "w") as fh:
            json.dump(rec, fh)
        with open(os.path.join(DH.runs_dir(root), "u-other.json"), "w") as fh:
            json.dump(dict(short, unit="u-other"), fh)
        facts = {MOD: {"live_units": ["u-long", "u-gone"]}, "Other": {"live_units": "UNMEASURED"}}
        fixture.got = (rec, proj, root, facts, short)
    return fixture.got


def t_a_long_check_is_named():
    rec, proj, _, _, short = fixture()
    now, tmp = NOW, TMP
    row = RP.peek_run(rec, now, proj, repo=tmp)
    check("a-long-check-is-named", row.get("long") == ["sc_barrage"] and row.get("progress") ==
          "PROGRESS: theory: perf | experiment: sc_barrage again | reading: 3 fps | next: retry"
          and row.get("message") == "Retrying sc_barrage on ArchSmall."
          and row.get("mod") == MOD and row.get("item") == "ITEM_u-long", json.dumps(row)[:400])
    r2 = RP.peek_run(short, T0 + 900, proj, repo=tmp)
    check("a-long-check-is-named: 15 min is not long", r2.get("long") == [] and r2["checks"][0][0] == "sc_spared",
          json.dumps(r2)[:300])


def t_the_focus_lapses():
    evs = [(T0, "run sc_gas")] + [(T0 + 10 * (i + 1), "ls") for i in range(11)] + [(T0 + 7200, "ls")]
    tot, focus = RP.dwell(evs, set(IDS), T0 + 7300)
    check("the-focus-lapses", tot.get("sc_gas", 0) <= 110 and focus == [], "%s %s" % (tot, focus))
    evs = [(T0, "run sc_gas")] + [(T0 + 10 * (i + 1), "ls") for i in range(9)] + [(T0 + 4000, "ls")]
    tot, _ = RP.dwell(evs, set(IDS), T0 + 4000)
    check("the-focus-lapses: within the lapse the time counts", tot.get("sc_gas", 0) >= 3990, str(tot))


def t_bookkeeping_is_not_focus():
    evs = [(T0, "run sc_gas"), (T0 + 10, "edit table sc_gas sc_spared sc_barrage"), (T0 + 5000, "ls")]
    tot, _ = RP.dwell(evs, set(IDS), T0 + 5000)
    check("bookkeeping-is-not-focus: three checks named", tot.get("sc_gas", 0) == 10 and not tot.get("sc_spared"),
          str(tot))
    evs = [(T0, "run sc_gas"), (T0 + 10, "python3 src/RimMandrake/rimflow/cli.py claim NEXT_ITEM --seat BENCH"),
           (T0 + 5000, "ls")]
    tot, _ = RP.dwell(evs, set(IDS), T0 + 5000)
    check("bookkeeping-is-not-focus: a claim clears it", tot.get("sc_gas", 0) == 10, str(tot))
    evs = [(T0, "run sc_gas and sc_spared"), (T0 + 3700, "ls")]
    tot, _ = RP.dwell(evs, set(IDS), T0 + 3700)
    check("bookkeeping-is-not-focus: two checks are both in focus", tot.get("sc_gas") == 3700 and
          tot.get("sc_spared") == 3700, str(tot))
    tot, _ = RP.dwell([(T0, "run sc_gas_extra"), (T0 + 4000, "ls")], set(IDS), T0 + 4000)
    check("bookkeeping-is-not-focus: a longer word is not the check", not tot, str(tot))


def t_a_blind_run_says_so():
    _, proj, _, _, _ = fixture()
    nt, _ = world(TMP, "u-notable", long_run(), table=False)
    r3 = RP.peek_run(nt, NOW, proj, repo=os.path.join(TMP, "norepo"))
    check("a-blind-run-says-so: no test table", str(r3.get("blind", "")).startswith("could not look") and
          "long" not in r3, json.dumps(r3)[:300])
    nx, _ = world(TMP, "u-notranscript", None)
    r4 = RP.peek_run(nx, NOW, proj, repo=TMP)
    check("a-blind-run-says-so: no transcript", str(r4.get("blind", "")).startswith("could not look") and
          "long" not in r4, json.dumps(r4)[:300])


def _tick_rows():
    _, proj, root, facts, _ = fixture()
    units = RP.tick_units(facts)
    rows = RP.peek(NOW, root=root, projects=proj, repo=TMP, units=units)
    return units, rows, {r["unit"]: r for r in rows}


def t_the_tick_reads_its_own_runs():
    units, rows, by = _tick_rows()
    check("the-tick-reads-its-own-runs", units == {"u-long": MOD, "u-gone": MOD} and set(by) == {"u-long", "u-gone"}
          and by["u-long"].get("long") == ["sc_barrage"], json.dumps(rows)[:400])


def t_one_run_never_stops_the_others():
    _, rows, by = _tick_rows()
    check("one-run-never-stops-the-others", str(by["u-gone"].get("blind", "")).startswith("could not look")
          and by["u-long"].get("long") == ["sc_barrage"], json.dumps(rows)[:400])


def t_the_conductor_is_asked_once():
    _, proj, root, facts, _ = fixture()
    now = NOW
    logged = []
    sd = os.path.join(TMP, "tick")
    fx = {"peek": lambda n, u: RP.peek(n, root=root, projects=proj, repo=TMP, units=u), "log": logged.append}
    rd = RP.observe(now, {}, fx, sd, facts)
    rd2 = RP.observe(now + 60, {}, fx, sd, facts)
    line = logged[0] if logged else ""
    asks = all(w in line for w in ("sensible", "Defer", "re-examine", "cheaper test", "raise it with him"))
    check("the-conductor-is-asked-once", len(logged) == 1 and line.startswith(RP.HEAD + ": u-long") and asks
          and "sc_barrage" in line and len(rd.get("needs_conductor") or []) == 1 and not rd2.get("needs_conductor")
          and rd2["peek"]["long"] == {"u-long": ["sc_barrage"]}, "%s | %s" % (logged, rd2.get("needs_conductor")))
    failing = []

    def bad_log(text):
        failing.append(text)
        raise OSError("disk full")
    sd2 = os.path.join(TMP, "tick2")
    RP.observe(now, {}, dict(fx, log=bad_log), sd2, facts)
    RP.observe(now + 60, {}, dict(fx, log=bad_log), sd2, facts)
    check("the-conductor-is-asked-once: an unwritten line is tried again", len(failing) == 2, str(failing))


def t_the_peek_fails_quiet_in_the_tick():
    src = open(os.path.join(HERE, "maturation_dispatch.py"), encoding="utf-8").read()
    m = re.search(r"try:[^\n]*\n\s+import run_peek as RP[^\n]*\n\s+RP\.observe\(now, rd, fx\.get\(\"peek\"\), d, "
                  r"facts\)\n\s+except Exception as e:[^\n]*\n\s+rd\[\"peek_error\"\]", src)
    check("the-peek-fails-quiet-in-the-tick", bool(m) and src.index("RP.observe(") < src.index(
        '_write(os.path.join(d, "reading.json"), rd)'))


def t_live_says_the_tick_runs_it():
    now = NOW
    rp = os.path.join(TMP, "reading.json")

    def live_of(obj):
        if obj is None:
            if os.path.exists(rp):
                os.remove(rp)
        else:
            with open(rp, "w") as fh:
                json.dump(obj, fh)
        return RP.live(now, rp)[0]
    got = [live_of({"peek": {"at": now - 60, "runs": 1}}), live_of({"peek": {"at": now - RP.FRESH_S - 1}}),
           live_of({"peek": {"at": now - 60}, "peek_error": "OSError: x"}), live_of({"at": now}), live_of(None)]
    check("live-says-the-tick-runs-it", got == [0, 1, 1, 1, 2], str(got))


def t_it_changes_no_run():
    me = open(os.path.join(HERE, "run_peek.py"), encoding="utf-8").read()
    check("it-changes-no-run", not re.search(r"\bsubprocess\b|systemctl|cli\.py\"|\.launch\(|kill\(", me))


def main():
    tests = (t_a_long_check_is_named, t_the_conductor_is_asked_once, t_the_focus_lapses, t_bookkeeping_is_not_focus,
             t_a_blind_run_says_so, t_the_tick_reads_its_own_runs, t_one_run_never_stops_the_others,
             t_the_peek_fails_quiet_in_the_tick, t_live_says_the_tick_runs_it, t_it_changes_no_run)
    try:
        for fn in tests:
            try:
                fn()
            except Exception as e:  # noqa: BLE001
                import traceback
                check("%s raised %s: %s" % (fn.__name__, type(e).__name__, e), False, traceback.format_exc()[-600:])
        with open(os.path.join(HERE, "..", "..", "..", "design/specs/2026-11-25-run-peek/boundary.md"),
                  encoding="utf-8") as fh:
            text = fh.read().split("## PROMISES")[1].split("## LIMITS")[0]
        named = set(re.findall(r"^- \*\*([a-z-]+)\.\*\*", text, re.M))
        mine = {f.__name__[2:].replace("_", "-") for f in tests}
        check("each promise of the page has its test", named == mine, str(named ^ mine))
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    print("ALL PASS" if not FAILS else "FAILED: %s" % ", ".join(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
