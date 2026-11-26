#!/usr/bin/env python3
"""Offline selftest of maturation.py's stage record (spend, version rollover, the offline build's facts): one test per
promise on design/specs/2026-11-19-maturation-record/boundary.md, each named after it (boundary_check.py reads that).
Item RIMMANDRAKE_FIX_MATURATION_REVIEW_FINDINGS_SIX_PREDATE_SCOPE; each test watched failing on the base 7df09c59a2.
The two unit tests (RIMMANDRAKE_STAMP_STAGE_SPEND_ROWS_ONE_UNIT, RIMMANDRAKE_RELABEL_SPEND_PRINTERS_STILL_V1) were
watched failing on 9c3ad408cd.

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
    V2 = {"token_unit": "weighted_v2"}     # these rows are this version's own unit (t_stage_spend_sums_one_unit)
    rows = [dict(V2, stage="blind_challenge", tokens=U, usd=U, wall_s=U),
            dict(V2, stage="blind_challenge", tokens=U, usd=U, wall_s=U),
            dict(V2, stage="in_game", tokens=300, usd=U, wall_s=20),
            dict(V2, stage="in_game", tokens=U, usd=0.5, wall_s=U),
            dict(V2, stage="designer", tokens=0, usd=0.0, wall_s=0)]
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


OLD_EVIDENCE = {"version/blind_challenge/cycle_1/SUMMARY.md": "old cycle 1\n",
                "version/blind_challenge/cycle_2/SUMMARY.md": "old cycle 2\n",
                "version/in_game/visit_1/rows.jsonl": '{"test": "old", "result": "PASS"}\n',
                "version/walk_brief/arrival_1.md": "old arrival 1\n"}


def rollover_root(name):
    """-> a root holding MOD's passed 0.1.0 (two blind cycles, one visit, one arrival) and VERSION.json at 0.2.0."""
    root = fresh(name, stage="passed", cycles={"visit": 2, "total": 2}, pre_human_arrivals=1)
    for p, text in dict(OLD_EVIDENCE, **{"version/blind_challenge/notes.md": "not numbered\n"}).items():
        M.write_text(root, MOD, p, text)
    M.write_text(root, MOD, "version/VERSION.json", json.dumps({"mod": MOD, "version": "0.2.0",
                                                                "state": "locked 2026-11-19"}))
    M.write_text(root, MOD, "journal.md", "# journal\n\n- **Stage now:** passed.\n\n## History\n")
    return root


def t_next_version_sets_aside_numbered_evidence():
    """next_version moves the previous version's numbered cycles, visits and arrival briefs to version/previous/<old>/,
    names them, and the new version's cycle 1, visit 1 and arrival 1 start empty: no old exit is read as the new one's."""
    root = rollover_root("roll")
    d = M.mod_dir(root, MOD)
    r = M.next_version(root, MOD, "BENCH", "selftest: 0.2.0 opened")
    check(r.get("ok") and M.load(root, MOD).get("version") == "0.2.0", "the version moves", r)
    check(M.cycle_numbers(root, MOD) == [] and M.visit_numbers(root, MOD) == []
          and not os.path.exists(os.path.join(d, "version/walk_brief/arrival_1.md")),
          "the new version has no cycle, visit or arrival evidence", (M.cycle_numbers(root, MOD),
                                                                       M.visit_numbers(root, MOD)))
    kept = {p: M.read_text(root, MOD, p.replace("version/", "version/previous/0.1.0/", 1)) for p in OLD_EVIDENCE}
    check(kept == OLD_EVIDENCE, "the old version's evidence is kept whole under version/previous/0.1.0/", kept)
    want = sorted(M.rel(MOD, p.rsplit("/", 1)[0] if "/cycle_" in p or "/visit_" in p else p) for p in OLD_EVIDENCE)
    check(sorted(r.get("archived") or []) == want, "the result names every path it set aside", r.get("archived"))
    check("set aside in `version/previous/0.1.0`" in (M.read_text(root, MOD, "journal.md") or ""),
          "the journal entry says where the evidence went")
    check(M.read_text(root, MOD, "version/blind_challenge/notes.md") == "not numbered\n",
          "a file that is not numbered evidence stays where it is")
    # the new version's first blind cycle: no folder reads as past it, and its exit is absent until a judge writes it
    rec = M.load(root, MOD)
    M.write_text(root, MOD, M.RECORD, M.dump(dict(rec, stage="blind_challenge", cycles={"visit": 1, "total": 1})))
    bf = M.blind_facts(root, MOD)
    check(not any("past" in b for b in bf.get("blocked") or []) and (bf.get("exit") or {}).get("state") == "absent",
          "the new version's cycle 1 is neither blocked as past nor read from the old exit",
          (bf.get("blocked"), (bf.get("exit") or {}).get("state")))
    # the CLI line names the moved paths, so the caller lands them
    root = rollover_root("roll_cli")
    import contextlib
    import io
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = M.main(["--root", root, "next-version", MOD, "--by", "BENCH", "--why", "selftest"])
    check(rc == 0 and all(w in buf.getvalue() for w in want), "the CLI line names every path set aside",
          buf.getvalue()[-300:])
    # an archive folder that already exists is refused before anything moves
    root = rollover_root("roll_taken")
    M.write_text(root, MOD, "version/previous/0.1.0/blind_challenge/cycle_1/SUMMARY.md", "already here\n")
    r = M.next_version(root, MOD, "BENCH", "selftest")
    check(not r.get("ok") and M.load(root, MOD).get("version") == "0.1.0" and M.cycle_numbers(root, MOD) == [1, 2],
          "an archive path already taken refuses the move, and nothing moves", r)


def t_next_version_refuses_a_move_made_meanwhile():
    """A stage move that lands between next_version's read of the record and its write is not overwritten: the
    version move refuses, the landed move stays, and the old evidence is moved back."""
    root = rollover_root("roll_meanwhile")
    real = M.numbered_evidence

    def landed(r, m):       # another process's move lands after next_version read the record
        rec = M.load(r, m)
        rec["moves"].append({"from": "passed", "to": "passed", "by": "selftest meanwhile"})
        M.write_text(r, m, M.RECORD, M.dump(rec))
        return real(r, m)
    M.numbered_evidence = landed
    try:
        r = M.next_version(root, MOD, "BENCH", "selftest")
    finally:
        M.numbered_evidence = real
    rec = M.load(root, MOD)
    check(not r.get("ok") and "meanwhile" in str(r.get("why")), "next_version refuses when the record moved", r)
    check(rec.get("version") == "0.1.0" and [x.get("by") for x in rec.get("moves") or []] == ["selftest meanwhile"],
          "the move that landed meanwhile is kept", rec)
    check(M.cycle_numbers(root, MOD) == [1, 2], "the old evidence is moved back", M.cycle_numbers(root, MOD))


def t_seed_writes_under_the_mod_lock():
    """A record written by another process while seed_mod gathers its facts is returned untouched, never written over."""
    root = os.path.join(TMP, "seed_meanwhile")
    os.makedirs(M.mod_dir(root, MOD), exist_ok=True)
    other = {"schema": 1, "mod": MOD, "version": "0.1.0", "stage": "offline_build", "moves": [{"by": "other seed"}],
             "spend": []}
    real = M.read_text

    def meanwhile(r, m, p):
        if p == "journal.md" and M.load(r, m) is None:
            M.write_text(r, m, M.RECORD, M.dump(other))
        return real(r, m, p)
    M.read_text = meanwhile
    MN, rm = M.MN, M.MN.read_mod
    MN.read_mod = lambda *a, **k: {"name": MOD, "column": next(iter(M.WORD_OF_COL)), "version": "0.1.0"}
    try:
        rec, made = M.seed_mod(root, MOD, live=False)
    except Exception as e:      # noqa: BLE001
        rec, made = {"raised": str(e)}, None
    finally:
        M.read_text, MN.read_mod = real, rm
    check(made is False and rec.get("moves") == [{"by": "other seed"}], "seed_mod returns the record made meanwhile",
          (made, rec))
    check((M.load(root, MOD) or {}).get("moves") == [{"by": "other seed"}], "and does not write over it",
          M.load(root, MOD))


SWITCH_LAST_V1, SWITCH_FIRST_V2 = "2026-11-16T23:00:13-08:00", "2026-11-16T23:10:17-08:00"   # measured, the records


def _epoch(s):
    return M._instant(s)


def t_spend_rows_carry_their_unit():
    """Every spend row a writer adds names its token unit: a run row its run's own token_unit, else weighted_v1
    (role_launch.stored_unit: a run record with no unit predates the weighting), whatever its end time; add_spend
    weighted_v2; the seed's VERSION.json row the unit VERSION.json names, else "unstated". The row names the run's
    model too."""
    old = {"unit": "u-old", "item": "I", "tokens": 100, "end": _epoch(SWITCH_LAST_V1), "model": "opus"}
    new = {"unit": "u-new", "item": "I", "tokens": 100, "end": _epoch(SWITCH_FIRST_V2), "model": "sonnet"}
    own = dict(old, unit="u-own", token_unit="weighted_v2")
    got = [M._spend_row(r, ["blind_challenge"]).get("token_unit") for r in (old, new, own)]
    check(got == ["weighted_v1", "weighted_v1", "weighted_v2"],
          "a run row is stamped from its own unit, else weighted_v1, never by its end time", got)
    check(M._spend_row(new, ["blind_challenge"]).get("model") == "sonnet", "a run row names its run's model")
    nowhen = {"unit": "u-x", "item": "I", "tokens": 5}
    check(M._spend_row(nowhen, ["designer"]).get("token_unit") == "weighted_v1",
          "a run row with no end, start or unit reads its record's unit: weighted_v1", M._spend_row(nowhen, ["designer"]))
    root = fresh("unit_add")
    rec = M.add_spend(root, MOD, "offline_build", 1234, source="hand")
    check(rec["spend"][-1].get("token_unit") == "weighted_v2", "add_spend stamps weighted_v2", rec["spend"][-1])
    root = fresh("unit_runspend")
    M.record_run_spend(root, MOD, [dict(new, token_unit="weighted_v2")], lambda r: ["blind_challenge"])
    rows = M.read_run_spend(root, MOD)
    check([x.get("token_unit") for x in rows] == ["weighted_v2"], "record_run_spend's rows carry their unit", rows)
    d = M._designer_seed_row({"tokens_spent": 900}, MOD)
    d2 = M._designer_seed_row({"tokens_spent": 900, "token_unit": "weighted_v2"}, MOD)
    check(d.get("token_unit") == "unstated" and d2.get("token_unit") == "weighted_v2",
          "the seed's VERSION.json row takes VERSION.json's unit, else unstated", (d, d2))


def t_stage_spend_sums_one_unit():
    """spend_by_stage, pass_cost and show sum weighted_v2 rows only; every other unit is summed apart, by unit, and
    printed under its own name. An unstamped row reads weighted_v1, whatever its `at` (role_launch.stored_unit)."""
    U = M.UNM
    rows = [{"stage": "blind_challenge", "tokens": 100, "token_unit": "weighted_v2"},
            {"stage": "blind_challenge", "tokens": 50, "at": SWITCH_LAST_V1},
            {"stage": "blind_challenge", "tokens": 30, "at": SWITCH_FIRST_V2},
            {"stage": "blind_challenge", "tokens": 5, "token_unit": "weighted_v1"},
            {"stage": "designer", "tokens": 7},
            {"stage": "designer", "tokens": 9, "token_unit": "unstated"},
            {"stage": "designer", "tokens": U, "token_unit": "weighted_v2"}]
    check([M.row_unit(r) for r in rows] == ["weighted_v2", "weighted_v1", "weighted_v1", "weighted_v1", "weighted_v1",
                                            "unstated", "weighted_v2"], "row_unit reads each row's unit",
          [M.row_unit(r) for r in rows])
    by = M.spend_by_stage({"spend": rows})
    b, d = by.get("blind_challenge") or {}, by.get("designer") or {}
    check(b.get("tokens") == 100 and b.get("tokens_other") == {"weighted_v1": 85},
          "a stage sums its weighted_v2 rows and holds the weighted_v1 rows apart", b)
    check(d.get("tokens") == U and d.get("tokens_other") == {"weighted_v1": 7, "unstated": 9},
          "a stage with no measured weighted_v2 row reads UNMEASURED, its other units apart", d)
    cost = M.pass_cost(TMP, MOD, {"spend": rows})
    check(cost.get("weighted_tokens") == 100 and cost.get("tokens_other") == {"weighted_v1": 92, "unstated": 9}
          and cost.get("unit") == "weighted_v2", "pass_cost sums weighted_v2 only and names its unit", cost)
    root = fresh("unit_show", spend=rows)
    import contextlib
    import io
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = M.main(["--root", root, "show", MOD])
    lines = {x.split(":")[0].strip(): x for x in buf.getvalue().splitlines() if x.strip().startswith("spend ")}
    bl = [v for k, v in lines.items() if "Blind" in k or "blind" in k]
    dl = [v for k, v in lines.items() if "esign" in k]
    check(rc == 0 and bl and "100 weighted tokens" in bl[0] and "85 weighted_v1" in bl[0] and "185" not in bl[0],
          "show prints the weighted_v2 sum and labels the weighted_v1 history apart", (rc, bl))
    check(dl and "UNMEASURED weighted tokens" in dl[0] and "7 weighted_v1" in dl[0] and "9 unstated" in dl[0],
          "show labels every other unit by name", dl)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    only = set(argv[argv.index("--only") + 1:]) if "--only" in argv else None
    for t in (t_spend_write_holds_the_mod_lock, t_stage_spend_unmeasured_when_no_row_measured,
              t_build_facts_refuses_what_evaluate_refuses, t_next_version_sets_aside_numbered_evidence,
              t_next_version_refuses_a_move_made_meanwhile, t_seed_writes_under_the_mod_lock,
              t_spend_rows_carry_their_unit, t_stage_spend_sums_one_unit):
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
