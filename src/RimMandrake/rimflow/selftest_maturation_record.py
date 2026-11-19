#!/usr/bin/env python3
"""Offline selftest of maturation.py's stage record (spend, version rollover, the offline build's facts): one test per
promise on design/specs/2026-11-19-maturation-record/boundary.md, each named after it (boundary_check.py reads that).
Item RIMMANDRAKE_FIX_MATURATION_REVIEW_FINDINGS_SIX_PREDATE_SCOPE; each test watched failing on the base 7df09c59a2.

    python3 src/RimMandrake/rimflow/selftest_maturation_record.py                 every test; exit 0 PASS, 1 FAILED
    python3 src/RimMandrake/rimflow/selftest_maturation_record.py --only t_x ...  those alone
"""
import json
import os
import shutil
import sys
import tempfile
import threading

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import maturation as M  # noqa: E402

TMP = tempfile.mkdtemp(prefix="selftest_maturation_record_")
FAILS = []
MOD = "RecordTestMod"


def check(ok, what, got=None):
    print("%s %s%s" % ("ok  " if ok else "FAIL", what, "" if ok or got is None else "  got: %r" % (got,)))
    if not ok:
        FAILS.append(what)


def fresh(name, **rec):
    """-> a new root holding MOD with a stage record (0.1.0 at offline build unless rec says otherwise)."""
    root = os.path.join(TMP, name)
    base = {"schema": 1, "mod": MOD, "version": "0.1.0", "stage": "offline_build", "since": "2026-11-19T09:00:00-08:00",
            "cycles": {"visit": 0, "total": 0}, "pre_human_arrivals": 0, "moves": [], "spend": []}
    base.update(rec)
    M.write_text(root, MOD, M.RECORD, M.dump(base))
    return root


def t_spend_write_holds_the_mod_lock():
    """An add_spend started while another process holds the mod's lock (a move between its read and its write) waits
    for it, then writes: the move is not erased."""
    root = fresh("lock")
    lk = M._mod_lock(root, MOD)
    th = threading.Thread(target=M.add_spend, args=(root, MOD, "blind_challenge", 7), kwargs={"source": "run-locked"},
                          daemon=True)
    try:
        th.start()
        th.join(1.5)
        waited = th.is_alive() and (M.load(root, MOD).get("spend") or []) == []
        if waited:      # the move that lands while add_spend waits
            rec = M.load(root, MOD)
            rec["moves"].append({"from": "offline_build", "to": "blind_challenge", "by": "selftest"})
            rec["stage"] = "blind_challenge"
            M.write_text(root, MOD, M.RECORD, M.dump(rec))
    finally:
        lk.close()
    th.join(30)
    rec = M.load(root, MOD)
    check(waited, "add_spend waits while the mod's lock is held", waited)
    check(not th.is_alive() and [x.get("source") for x in rec.get("spend") or []] == ["run-locked"],
          "then it writes its row", rec.get("spend"))
    check(rec.get("stage") == "blind_challenge" and len(rec.get("moves") or []) == 1,
          "the move made while it waited is kept", (rec.get("stage"), rec.get("moves")))


def t_stage_spend_unmeasured_when_no_row_measured():
    """A stage whose rows all carry tokens/usd/wall_s UNMEASURED reads each UNMEASURED, never 0; a stage where some rows
    measured a field sums those; show prints the unmeasured field as UNMEASURED, and does not crash on it."""
    U = M.UNM
    rows = [{"stage": "blind_challenge", "tokens": U, "usd": U, "wall_s": U},
            {"stage": "blind_challenge", "tokens": U, "usd": U, "wall_s": U},
            {"stage": "in_game", "tokens": 300, "usd": U, "wall_s": 20},
            {"stage": "in_game", "tokens": U, "usd": 0.5, "wall_s": U},
            {"stage": "designer", "tokens": 0, "usd": 0.0, "wall_s": 0}]
    by = M.spend_by_stage({"spend": rows})
    b = by.get("blind_challenge") or {}
    check([b.get(k) for k in ("tokens", "usd", "wall_s")] == [U, U, U],
          "a stage no row measured reads UNMEASURED in every field", b)
    check(b.get("entries") == 2 and b.get("unmeasured") == 6, "its entries and unmeasured fields are still counted", b)
    g = by.get("in_game") or {}
    check([g.get(k) for k in ("tokens", "usd", "wall_s")] == [300, 0.5, 20],
          "a stage some rows measured sums those rows", g)
    d = by.get("designer") or {}
    check([d.get(k) for k in ("tokens", "usd", "wall_s")] == [0, 0.0, 0], "a measured 0 stays 0", d)
    cost = M.pass_cost(TMP, MOD, {"spend": rows[:2]})
    check(cost["weighted_tokens"] == U and cost["by_stage"]["blind_challenge"]["tokens"] == U,
          "pass_cost's by_stage reads UNMEASURED where no row measured tokens", cost)
    root = fresh("show", spend=rows[:2])
    import contextlib
    import io
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            rc = M.main(["--root", root, "show", MOD])
    except Exception as e:      # noqa: BLE001
        rc = "%s: %s" % (type(e).__name__, e)
    line = [x for x in buf.getvalue().splitlines() if x.strip().startswith("spend ")]
    check(rc == 0 and line and "UNMEASURED weighted tokens" in line[0] and "UNMEASURED s wall" in line[0]
          and " 0 weighted tokens" not in line[0], "show prints the stage's tokens and wall time as UNMEASURED",
          (rc, line))


def t_build_facts_refuses_what_evaluate_refuses():
    """A bar the table flags runnable whose deciding scene owes script parts to an open item: evaluate refuses the exit
    on it, so build_facts hands it to the builder in refused_bars (it was [] there: the builder had nothing to do)."""
    import selftest_maturation as ST
    root = os.path.join(TMP, "owed")
    os.environ["MATURATION_CLOCK"] = str(ST.CLOCK)
    was = ST.isolate(root)
    try:
        ST.copy_mods(root)
        mod = "FlowWorks"
        M.seed_mod(root, mod, live=False)
        tt = json.loads(ST.read(root, mod, "version/test_table.json"))
        bar = next(b for b in tt["bars"] if b.get("decides") and b.get("every_decider_runnable_today") is True)
        before = M.build_facts(root, mod)
        check(before.get("stage") == "offline_build" and isinstance(before.get("refused_bars"), list)
              and bar["id"] not in before["refused_bars"], "the fixture: %s at offline build, %s not refused"
              % (mod, bar["id"]), before.get("refused_bars"))
        owed = "RIMMANDRAKE_BUILD_SELFTEST_RECORD_SCENE_PARTS_OWED"
        with open(os.path.join(M.mod_dir(root, mod), "scenes.json"), "w") as f:
            json.dump({"scenes": [{"id": bar["decides"][0], "owed_parts_item": [owed]}]}, f)
        ev = os.path.join(root, "infrastructure", "state", "ledger", "events")
        os.makedirs(ev, exist_ok=True)
        with open(os.path.join(ev, "BENCH.jsonl"), "w") as f:
            f.write(json.dumps({"seat": "BENCH", "event": "file", "id": owed, "title": "selftest"}) + "\n")
        res = M.evaluate(root, mod, "blind_challenge", by="selftest", why="owed scene parts")
        cl = [r for r in res["verdict"]["refusals"] if r["clause"] == "every_bar_has_a_check_that_runs"]
        check(cl and owed in json.dumps(cl) and bar["id"] in json.dumps(cl), "evaluate refuses the exit on the bar",
              json.dumps(cl)[:200])
        f = M.build_facts(root, mod)
        check(isinstance(f.get("refused_bars"), list) and bar["id"] in f["refused_bars"],
              "build_facts lists the bar in refused_bars", f.get("refused_bars"))
        check(sorted(set(before["refused_bars"]) | {bar["id"]}) == sorted(f["refused_bars"]),
              "and nothing else changes", (before["refused_bars"], f.get("refused_bars")))
        text, _ = M.brief_text(root, mod)
        check("`%s` (%s)" % (bar["id"], owed) in text, "the builder's brief names the bar's open owed item",
              [x for x in text.splitlines() if bar["id"] in x][:3])
        with open(os.path.join(ev, "BENCH.jsonl"), "a") as fh:
            fh.write(json.dumps({"seat": "BENCH", "event": "close", "id": owed}) + "\n")
        f = M.build_facts(root, mod)
        check(sorted(f.get("refused_bars") or []) == sorted(before["refused_bars"]),
              "once the owed item closes, the bar leaves refused_bars", f.get("refused_bars"))
    finally:
        ST.restore(was)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    only = set(argv[argv.index("--only") + 1:]) if "--only" in argv else None
    for t in (t_spend_write_holds_the_mod_lock, t_stage_spend_unmeasured_when_no_row_measured,
              t_build_facts_refuses_what_evaluate_refuses):
        if only is not None and t.__name__ not in only:
            continue
        print("== %s" % t.__name__)
        try:
            t()
        except Exception as e:      # noqa: BLE001
            check(False, "%s raised %s: %s" % (t.__name__, type(e).__name__, e))
    shutil.rmtree(TMP, ignore_errors=True)
    if FAILS:
        print("FAILED %d: %s" % (len(FAILS), "; ".join(FAILS[:8])))
        return 1
    print("PASS selftest_maturation_record")
    return 0


if __name__ == "__main__":
    sys.exit(main())
