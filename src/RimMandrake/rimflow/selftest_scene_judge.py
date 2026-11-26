#!/usr/bin/env python3
"""The offline judge, against the slice's recorded trace and hand-made records."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
UTILS = HERE.parent / "Utils"
sys.path.insert(0, str(UTILS))
RECORDED = json.loads((UTILS / "scene_recorded.json").read_text(encoding="utf-8"))
try:
    import scene_judge as J
except ModuleNotFoundError as exc:
    if exc.name != "scene_judge":
        raise
    J = None


def module():
    assert J is not None, "no offline scene judge on this tree"
    return J


def cmp(name, op, value):
    return {"cmp": [{"p": "track", "name": name}, op, value]}


def tap_count(name):
    return {"cmp": [{"p": "count", "taps": [name]}, ">", 0]}


def fixture():
    rows = copy.deepcopy(RECORDED["trace_hit"])
    plan = {"success": cmp("job", "==", "GotoWander"), "exposure": cmp("job", "!=", ""),
            "opportunity": cmp("dead", "==", False), "forbidden": cmp("downed", "==", True), "version": "original"}
    receipt = {"entry": {"name": "s.run", "request": "run_fixture"},
               "game": {"name": "ArchSmall", "session": "scene_fixture", "tick_before": rows[0]["tick"],
                        "tick_after": rows[-1]["tick"]},
               "build": {"list": "fixture-list", "version": "1.6", "dlls": {}, "companion": {"mvid": "fixture-companion"}},
               "commit": "a" * 40, "did": [], "hands": {"jawa/scene_slice": 1},
               "stamps": [], "could_not_look": []}
    return plan, rows, [receipt]


def normalize(rows):
    for i, row in enumerate(rows, 24):
        row.update(n=i + 100, seq=i)
    rows[-1]["rows"] = len(rows) - 1
    return rows


def insert(rows, rec, tick=None, **fields):
    end = next(i for i, r in enumerate(rows) if r["rec"] == "end")
    tick = rows[end]["tick"] if tick is None else tick
    at = next((i for i, r in enumerate(rows[:end]) if r["tick"] > tick), end)
    rows.insert(at, {**rows[0], "rec": rec, "tick": tick, "phase": "end_of_tick", **fields})
    normalize(rows)


def classify(data):
    return module().classify(*data)


def expect(verdict, word, row, detail=None):
    assert (verdict.outcome, verdict.row) == (word, row), "got %s row %s, want %s row %s (%s)" % (
        verdict.outcome, verdict.row, word, row, verdict.first_failed)
    if detail:
        assert detail in str(verdict.first_failed), verdict.first_failed
    if word != "SUCCESS":
        assert not verdict.counts_for_bar, word + " counted for the bar"


def hazard(data, approach=False):
    plan, rows, _ = data
    plan.update(external=["fire"], cast_activity=cmp("field", "!=", 136))
    rows[0]["taps"] = ["fire"]
    if approach:
        insert(rows, "track", tick=3, name="field", st="ok", v=137)
    insert(rows, "tap", tick=4, name="fire", enterSeq=2, exitSeq=3, parentSeq=None, data={"entered_station": True})
    insert(rows, "track", tick=4, name="dead", st="ok", v=True)
    next(r for r in rows if r.get("name") == "dead" and r["phase"] == "last")["v"] = True
    return data


def classifier_case(n):
    module()
    plan, rows, receipts = data = fixture()
    if n == 1:
        from scene_cond import after, before, count, seq, to_tree
        rows[0]["taps"] = ["damage", "death", "unseen"]
        # Nested death exits first. Ordering comes from entries. An armed empty tap measures zero.
        insert(rows, "tap", tick=4, name="death", enterSeq=2, exitSeq=3, parentSeq=1, data={})
        insert(rows, "tap", tick=4, name="damage", enterSeq=1, exitSeq=4, parentSeq=None, data={})
        plan["forbidden"] = to_tree((count("unseen") == 0) & (count("damage") == 1) &
                                    seq("damage", "death") & before("damage", "death") & after("death", "damage"))
        insert(rows, "fault", what="threw", detail="apparatus also failed")
    elif n == 2:
        insert(rows, "fault", what="threw", detail="runner threw")
    elif n == 3:
        end = next(r for r in rows if r["rec"] == "end")
        end.update(state="unknown", unknown={"value": "job"})
    elif n in (4, 5):
        hazard(data, approach=n == 5)
    elif n >= 7:
        plan["success"] = cmp("job", "==", "Rescue")
        if n != 8:
            plan["kind"] = "B"
        if n == 7:
            plan["allowed_miss"] = True
    word = ("MOD FAILURE", "APPARATUS FAULT", "COULD NOT LOOK", "ENVIRONMENT FAULT", "UNRESOLVED",
            "SUCCESS", "RANDOM MISS", "MOD FAILURE", "UNRESOLVED")[n - 1]
    v = classify(data)
    expect(v, word, n)
    if n in (7, 8, 9):
        assert v.first_failed["condition"] == "success" and v.first_failed["tick"] == rows[-1]["tick"]
        assert v.first_failed["observed"][0]["pv"] == "GotoWander", v.first_failed
    if n == 6:
        assert v.first_failed is None
        receipts[0]["stamps"] = ["TUNED a"]
        assert not classify(data).counts_for_bar
        receipts[0]["stamps"] = []
        assert classify(data).counts_for_bar
        assert not module().classify(*data, accepted=False).counts_for_bar, "unaccepted SUCCESS counted for the bar"
        for commit in (None, "short"):
            data = fixture()
            data[2][0]["commit"] = commit
            result = classify(data)
            expect(result, "SUCCESS", 6)
            assert not result.counts_for_bar, "unidentified commit counted for the bar: %r" % commit
        other = copy.deepcopy(receipts[0])
        other["build"]["list"] = "different"
        expect(module().classify(plan, rows, receipts + [other]), "COULD NOT LOOK", 3, "build")
        check_receipt_identity()


def check_receipt_identity():
    for field, value, detail in (
        ("game", {"name": "ArchSmall", "session": "scene_fixture", "tick_before": 1, "tick_after": 22},
         "does not identify the trace"),
        ("stamps", None, "stamps or commit"),
    ):
        data = fixture()
        data[2][0][field] = value
        expect(classify(data), "COULD NOT LOOK", 3, detail)


def t_classifier_rows():
    classifier_case(1)


def t_no_closing_record():
    plan, rows, receipts = fixture()
    for trace in (rows[:-1], []):
        expect(classify((plan, trace, receipts)), "COULD NOT LOOK", 3, "close")
    for index, key, bad, detail in (
        (0, "schema", "other", "no scene_trace_v1 opening record"),
        (1, "n", "2", "no integer n"),
        (1, "run", "another", "different runs"),
        (1, "seq", "9", "no integer seq or tick"),
        (1, "seq", rows[0]["seq"], "sequence or tick went back"),
        (-1, "paused", False, "paused closing phase"),
        (-1, "tickAfter", rows[-1]["tick"] + 1, "last sample does not stand"),
        (0, "taps", "smoke", "opening list of tracks or taps"),
        (0, "tracks", rows[0]["tracks"] + ["thing:job"], "track names in open are ambiguous"),
        (1, "phase", "middle", "invalid phase"),
    ):
        trace = copy.deepcopy(rows)
        trace[index][key] = bad
        expect(classify((plan, trace, receipts)), "COULD NOT LOOK", 3, detail)
    trace = copy.deepcopy(rows)
    next(r for r in trace if r["rec"] == "end")["executed"] += 1
    expect(classify((plan, trace, receipts)), "COULD NOT LOOK", 3, "executed tick span")


def t_dropped_span():
    plan, rows, receipts = fixture()
    rows[0]["taps"] = ["smoke"]
    plan["forbidden"] = tap_count("smoke")
    rows[-1]["dropped"] = 1
    expect(classify((plan, rows, receipts)), "COULD NOT LOOK", 3, "dropped")
    rows[-1]["dropped"] = 0
    del rows[1]
    expect(classify((plan, rows, receipts)), "COULD NOT LOOK", 3, "gap")


def missing_sample(phase):
    plan, rows, receipts = fixture()
    rows = normalize([r for r in rows if (r.get("name"), r["phase"]) != ("job", phase)])
    expect(classify((plan, rows, receipts)), "COULD NOT LOOK", 3, phase + " sample: job")


def t_missing_first_sample():
    missing_sample("first")
    for key, value, detail in (
        ("st", "invalid", "has no valid sample"),
        ("st", "gone", "opportunity"),
        ("phase", "end_of_tick", "outside a tick"),
        ("name", "downed", "duplicate or undeclared sample"),
    ):
        data = fixture()
        next(r for r in data[1] if r.get("name") == "dead" and r["phase"] == "first")[key] = value
        verdict = classify(data)
        expect(verdict, "COULD NOT LOOK", 3, detail)
        if value == "gone":
            assert verdict.receipt["could_not_look"] == ["unreadable condition opportunity"], verdict.receipt


def t_forbidden_wins_over_an_unreadable_success():
    """A forbidden effect is a MOD FAILURE in any run, also when another condition went unreadable (a destroyed thing that the
    success reads). Found by RIMMANDRAKE_CONVERT_THREE_SCENES_SHOW_IF_TEN_NAMES_HELP: the storeroom pit's goods stack destroyed."""
    data = fixture()
    first = {r.get("name"): r for r in data[1] if r.get("rec") == "track" and r["phase"] == "first"}
    first["downed"]["v"] = True
    first["job"].update(st="gone", v=None)
    expect(classify(data), "MOD FAILURE", 1, "forbidden")


def t_missing_last_sample():
    missing_sample("last")


def t_missing_tap():
    plan, rows, receipts = fixture()
    plan["forbidden"] = tap_count("smoke")
    expect(classify((plan, rows, receipts)), "COULD NOT LOOK", 3, "tap smoke")
    rows[0]["taps"] = ["smoke"]
    insert(rows, "tap", name="smoke", enterSeq=2, exitSeq=4, parentSeq=1, data={})
    insert(rows, "tap", name="smoke", enterSeq=1, exitSeq=3, parentSeq=None, data={})
    expect(classify((plan, rows, receipts)), "COULD NOT LOOK", 3, "exits outside its parent call")
    next(r for r in rows if r["rec"] == "tap")["data"] = None
    expect(classify((plan, rows, receipts)), "COULD NOT LOOK", 3, "no valid entry/exit record")


def t_success_at_first_sample():
    plan, rows, receipts = fixture()
    plan["success"] = cmp("hediffs", ">=", 5)
    expect(classify((plan, rows, receipts)), "APPARATUS FAULT", 2, "success")


def t_success_without_exposure():
    plan, rows, receipts = fixture()
    plan["exposure"] = cmp("hediffs", ">", 6)
    expect(classify((plan, rows, receipts)), "UNRESOLVED", 9, "exposure")
    del plan["exposure"]
    expect(classify((plan, rows, receipts)), "UNRESOLVED", 9, "exposure")


def t_advisory_record():
    plan, rows, receipts = fixture()
    plan["success"] = cmp("job", "==", "Rescue")
    insert(rows, "mod_says", success=True)
    expect(classify((plan, rows, receipts)), "MOD FAILURE", 8, "success")


def t_cast_went_to_hazard():
    expect(classify(hazard(fixture(), approach=True)), "UNRESOLVED", 5, "opportunity")


def t_giver_refusal():
    plan, rows, receipts = fixture()
    plan["success"] = cmp("job", "==", "Rescue")
    rows[0]["acts"] = [{"name": "order", "at": 2}]
    insert(rows, "act", tick=3, name="order", ok=False, delivery="giver_refused", detail="giver said no")
    expect(classify((plan, rows, receipts)), "MOD FAILURE", 8, "success")
    next(r for r in rows if r["rec"] == "act").pop("delivery")
    expect(classify((plan, rows, receipts)), "APPARATUS FAULT", 2, "order")
    for change, detail in (
        (lambda o, a, c: c.pop("actsNotDone"), "did not record which acts ran"),
        (lambda o, a, c: a.update(tick=c["tick"]), "has no following sample"),
        (lambda o, a, c: a.update(ok=None), "invalid act record"),
        (lambda o, a, c: o["acts"][0].update(at="2"), "invalid act in the opening call"),
    ):
        data = fixture()
        _, trace, _ = data
        trace[0]["acts"] = [{"name": "order", "at": 2}]
        insert(trace, "act", tick=4, name="order", ok=True)
        change(trace[0], next(r for r in trace if r["rec"] == "act"), trace[-1])
        expect(classify(data), "COULD NOT LOOK", 3, detail)


def write(path, data):
    path.write_text(json.dumps(data) + "\n", encoding="utf-8")


def keep(folder, data):
    plan, rows, receipts = data
    write(folder / "contract.json", plan)
    write(folder / "run.json", {"mode": "accept", "commit": receipts[0]["commit"], "session": receipts[0]["game"]["session"],
                                "game": receipts[0]["game"]["name"], "contract": None})
    for name, records in (("trace_run_fixture.jsonl", rows), ("receipts.jsonl", receipts)):
        (folder / name).write_text("".join(json.dumps(r) + "\n" for r in records), encoding="utf-8")


def cli(folder, rejudge=False, library=False):
    tool = UTILS / "scene.py" if library else HERE / "scene_judge.py"
    args = (["judge", str(folder)] + (["--rejudge"] if rejudge else [])) if library else (
        ["--rejudge", str(folder)] if rejudge else [str(folder)])
    return subprocess.run([sys.executable, str(tool), *args], capture_output=True, text=True, check=False)


def t_same_checker_adds_history():
    with tempfile.TemporaryDirectory() as d:
        folder = Path(d)
        keep(folder, fixture())
        first = module().judge(folder)
        p = cli(folder, rejudge=True, library=True)
        assert p.returncode == 0, p.stdout + p.stderr
        last = [json.loads(s) for s in (folder / "verdict_history.jsonl").read_text().splitlines()]
        assert len(last) == 1 and last[0]["outcome"] == first.outcome and last[0]["row"] == first.row
        assert last[0]["checker"] == "original" and last[0]["changed"] is False, last


def t_unrecorded_value_named():
    with tempfile.TemporaryDirectory() as d:
        folder = Path(d)
        plan, rows, receipts = fixture()
        keep(folder, (plan, rows, receipts))
        module().judge(folder)
        for probe, name in ((cmp("pawn.unrecorded", "==", 0), "pawn.unrecorded"), (tap_count("smoke"), "smoke")):
            plan["success"] = probe
            write(folder / "contract.json", plan)
            p = cli(folder, rejudge=True)
            assert p.returncode == 6 and "COULD NOT LOOK" in p.stdout and name in p.stdout, p.stdout + p.stderr
            assert not (folder / "verdict_history.jsonl").exists()
    from scene_cond import pawn, to_tree, value
    plan, rows, receipts = fixture()
    rows[0]["cond"] = {"mapId": 0, "sample": {"probes": {
        "job": {"p": "pawn.job", "f": "def", "pawn": "Human612"},
        "field": {"p": "thing.field", "thing": "Human612", "path": "positionInt.x"},
    }}}
    plan["success"] = to_tree(pawn("Human612").job_def == "GotoWander")
    expect(classify((plan, rows, receipts)), "SUCCESS", 6)
    plan["exposure"] = to_tree(value("thing:Human612", "positionInt.x") >= 136)
    expect(classify((plan, rows, receipts)), "SUCCESS", 6)
    plan["success"] = to_tree(pawn("Human613").job_def == "GotoWander")
    expect(classify((plan, rows, receipts)), "COULD NOT LOOK", 3, "Human613")


def t_first_outcome_kept():
    with tempfile.TemporaryDirectory() as d:
        folder = Path(d)
        plan, rows, receipts = fixture()
        keep(folder, (plan, rows, receipts))
        expect(module().judge(folder), "SUCCESS", 6)
        original = (folder / "verdict.json").read_bytes()
        plan.update(success=cmp("job", "==", "Rescue"), version="changed")
        write(folder / "contract.json", plan)
        expect_refused(module().judge, "CONTRACT_MISMATCH", "--rejudge", folder)
        expect(module().judge(folder, rejudge=True), "MOD FAILURE", 8)
        with (folder / "receipts.jsonl").open("a", encoding="utf-8") as f:
            f.write("\n")
        expect_refused(module().judge, "EVIDENCE_CHANGED", "kept call or receipt changed", folder, True)
        assert (folder / "verdict.json").read_bytes() == original, "rejudgement overwrote the first outcome"


def t_check_rows_decide():
    """A scene whose checks are rows it computes after its session: a FAIL row is no SUCCESS, also when its contract's success
    holds (the ExplosiveKnockback scenes' success is only 'the run played'); an INVALID row is an apparatus fault."""
    rows = lambda *v: [{"id": "V_%d" % i, "verdict": w, "text": "read %d" % i} for i, w in enumerate(v)]
    data = fixture()
    expect(classify(data), "SUCCESS", 6)
    expect(module().classify(*data, checks=rows("PASS", "PASS")), "SUCCESS", 6)
    expect(module().classify(*data, checks=rows("PASS", "FAIL", "INVALID")), "MOD FAILURE", 8, "check V_1")
    expect(module().classify(*data, checks=rows("PASS", "INVALID")), "APPARATUS FAULT", 2, "check V_1")
    expect(module().classify(*data, checks=rows("UNMEASURED", "PASS")), "COULD NOT LOOK", 3, "check V_0")
    expect(module().classify(*data, checks=rows("UNMEASURED", "FAIL")), "MOD FAILURE", 8, "check V_1")
    plan, trace, receipts = fixture()
    plan.update(kind="B", allowed_miss=True)
    expect(module().classify(plan, trace, receipts, checks=rows("FAIL")), "RANDOM MISS", 7, "check V_0")
    for bad in ([], [{"id": "V", "verdict": "ok"}], [{"id": "", "verdict": "PASS"}], [{"id": "V", "verdict": "PASS", "x": 1}]):
        try:
            module().classify(*fixture(), checks=bad)
        except module().Refused as e:
            assert e.name == "BAD_CHECKS", str(e)
        else:
            raise AssertionError("bad check rows were taken: %r" % bad)
    with tempfile.TemporaryDirectory() as d:     # kept beside the trace; a later judgement reads the kept rows
        folder = Path(d)
        keep(folder, fixture())
        expect(module().judge(folder, checks=rows("PASS", "FAIL")), "MOD FAILURE", 8, "check V_1")
        assert (folder / "checks.json").is_file(), "the rows were not kept"
        p = cli(folder, library=True)
        assert p.returncode == 1 and "MOD FAILURE" in p.stdout, p.stdout + p.stderr
        expect_refused(module().judge, "EVIDENCE_CHANGED", "check rows differ", folder, False, None, rows("PASS", "PASS"))
    with tempfile.TemporaryDirectory() as d:     # a run judged without rows keeps its first verdict; nothing is written
        folder = Path(d)
        keep(folder, fixture())
        expect(module().judge(folder), "SUCCESS", 6)
        expect_refused(module().judge, "EVIDENCE_CHANGED", "without check rows", folder, False, None, rows("FAIL"))
        assert not (folder / "checks.json").exists(), "a refused judgement wrote checks.json"
    with tempfile.TemporaryDirectory() as d:     # a refused rejudge of an unjudged run writes nothing
        folder = Path(d)
        keep(folder, fixture())
        expect_refused(module().judge, "NO_VERDICT", "before rejudging", folder, True, None, rows("FAIL"))
        assert not (folder / "checks.json").exists(), "a refused rejudge wrote checks.json"


def t_alias_needs_link():
    plan, rows, receipts = fixture()
    first, last = [r for r in rows if r.get("name") == "hediffs" and r["phase"] in ("first", "last")]
    first.update(alias="pawn", object="Human1")
    last.update(alias="pawn", object="Corpse1")
    expect(classify((plan, rows, receipts)), "COULD NOT LOOK", 3, "pawn")
    insert(rows, "link", tick=4, alias="pawn", old="Human1", new="Corpse1")
    expect(classify((plan, rows, receipts)), "SUCCESS", 6)
    link = next(r for r in rows if r["rec"] == "link")
    link["old"] = "OtherPawn"
    expect(classify((plan, rows, receipts)), "COULD NOT LOOK", 3, "unproved link")
    link.pop("alias")
    expect(classify((plan, rows, receipts)), "COULD NOT LOOK", 3, "does not name its alias")



def t_cast_link_is_proved_by_the_cast_taps():
    """The companion's cast writes a link as alias, from, to, why (a dead pawn's corpse), and its tap rows (job_end, kill) carry
    the alias and its thing id (boundary.md, the cast). Live on ArchBig 2026-11-25: a colonist killed by the blast read COULD NOT
    LOOK, 'alias people[1] has an unproved link', which hid a forbidden effect. A from that matches the thing of the alias's taps
    proves the link; a from that does not, a link before any tap names the thing, or a tap on another thing with no link, does not."""
    def run(*extra):
        plan, rows, receipts = fixture()
        for row in extra:
            insert(rows, row.pop("rec"), tick=row.pop("tick"), **row)
        return classify((plan, rows, receipts))
    tap = dict(rec="kill", tick=3, phase="in_tick", alias="pawn", thing=36520, ord=1, culprit="hediff MissingBodyPart")
    link = dict(rec="link", tick=3, alias="pawn", why="dead: its corpse")
    expect(run(dict(tap), dict(link, **{"from": 36520, "to": 67951})), "SUCCESS", 6)
    expect(run(dict(tap), dict(link, **{"from": 11, "to": 67951})), "COULD NOT LOOK", 3, "unproved link")
    expect(run(dict(link, **{"from": 36520, "to": 67951})), "COULD NOT LOOK", 3, "unproved link")
    expect(run(dict(tap), dict(tap, thing=99, tick=4)), "COULD NOT LOOK", 3, "changed object without a link")


def exit_case(code):
    module()
    with tempfile.TemporaryDirectory() as d:
        plan, rows, receipts = data = fixture()
        if code in (1, 2):
            plan.update(success=cmp("job", "==", "Rescue"))
        if code == 2:
            plan.update(kind="B", allowed_miss=True)
        if code in (3, 5):
            hazard(data, approach=code == 5)
        if code == 4:
            insert(rows, "fault", what="threw", detail="runner threw")
        if code == 6:
            rows.clear()
        keep(Path(d), data)
        p = cli(Path(d))
        word = ("SUCCESS", "MOD FAILURE", "RANDOM MISS", "ENVIRONMENT FAULT", "APPARATUS FAULT", "UNRESOLVED", "COULD NOT LOOK")[code]
        assert p.returncode == code and json.loads(p.stdout)["outcome"] == word, (p.returncode, p.stdout, p.stderr)


def t_exit_codes():
    exit_case(0)
    with tempfile.TemporaryDirectory() as d:
        folder = Path(d)
        data = fixture()
        keep(folder, data)
        (folder / "receipts.jsonl").unlink()
        expect(module().judge(folder), "COULD NOT LOOK", 3, "could not read the kept trace, run metadata or receipts")
        data[2][0]["entry"]["request"] = "another_call"
        keep(folder, data)
        expect(module().judge(folder), "COULD NOT LOOK", 3, "no receipt matches request run_fixture")


def expect_refused(call, name, detail, *args):
    try:
        call(*args)
    except module().Refused as e:
        assert e.name == name and detail in e.repair, str(e)
    else:
        raise AssertionError("%s was not refused (%s)" % (detail, name))


def t_unknown_key_named():
    plan, rows, receipts = fixture()
    plan["sucess"] = plan["success"]
    try:
        classify((plan, rows, receipts))
    except module().Refused as e:
        assert "sucess" in str(e), str(e)
    else:
        raise AssertionError("unknown key sucess was accepted")
    for bad, detail in (
        ([], "must hold an object"),
        ({}, "declare success"),
        ({"success": plan["success"], "kind": "C"}, "kind must be A or B"),
        ({"success": plan["success"], "allowed_miss": True}, "only B may allow it"),
        ({"success": plan["success"], "external": "fire"}, "external must list tap names"),
        ({"success": plan["success"], "request": ""}, "request must be nonempty text"),
    ):
        expect_refused(module().classify, "BAD_PLAN", detail, bad, rows, receipts)
    for probe, detail in (
        ({"p": "track", "name": 7}, "track needs a name"),
        ({"p": "count", "taps": []}, "count needs named taps"),
        ({"p": "unrecognised"}, "unrecognised"),
    ):
        expect_refused(module().classify, "BAD_CONDITION", detail, {"success": {"cmp": [probe, "==", 0]}}, rows, receipts)
    check_folder_refusals()


def check_folder_refusals():
    with tempfile.TemporaryDirectory() as d:
        folder = Path(d)
        expect_refused(module().judge, "NO_CONTRACT", "contract.json", folder)
        contract = folder / "contract.json"
        contract.write_text("{", encoding="utf-8")
        expect_refused(module().judge, "BAD_PLAN", "line 1", folder)
        data = fixture()
        write(contract, data[0])
        expect_refused(module().judge, "NO_TRACE", "no kept trace", folder)
        keep(folder, data)
        expect_refused(module().judge, "NO_VERDICT", "before rejudging", folder, True)
        (folder / "trace_second.jsonl").touch()
        expect_refused(module().judge, "BAD_PLAN", "choose request from run_fixture, second", folder)


def standard_rows(names, last=True, first_phase="first"):
    """The fixture with the companion's standard tracks added: first at the start tick, one change, last at the end tick."""
    plan, rows, receipts = fixture()
    at_first = 1 + sum(1 for r in rows if r["phase"] == "first" and r["rec"] == "track")
    stop = next(r for r in rows if r["rec"] == "end")["tick"]
    for k, name in enumerate(names):
        start = rows[0]["tick"] if first_phase == "first" else rows[0]["tick"] + 1
        rows.insert(at_first + k, {**rows[0], "rec": "track", "name": name, "phase": first_phase, "tick": start, "st": "ok", "v": "a"})
        if last:
            rows.insert(len(rows) - 1, {**rows[0], "rec": "track", "name": name, "phase": "last", "tick": stop, "st": "ok", "v": "b"})
    for r in rows:
        r.pop("tracks", None) if r["rec"] != "open" else None
    return plan, normalize(rows), receipts


def t_standard_cast_and_world_tracks_are_read():
    """The companion writes the twelve cast tracks of each cast member (<alias>.pos, .job, ...) and the six world tracks
    (world.weather, ...) as track rows that the open row does not list (boundary.md, the cast and the world tracks). Live on
    ArchBig 2026-11-25: scene_storeroom_pit read COULD NOT LOOK, 'duplicate or undeclared sample: people[0].pos'. They are read,
    and held to the first-and-last rule of a declared track; any other undeclared name stays a refusal."""
    std = ["people[0].pos", "people[0].job", "bomb.dead", "world.weather", "world.windows"]
    expect(classify(standard_rows(std)), "SUCCESS", 6)
    expect(classify(standard_rows(["people[0].pos"], last=False)), "COULD NOT LOOK", 3, "last sample: people[0].pos")
    expect(classify(standard_rows(["people[0].banana"])), "COULD NOT LOOK", 3, "duplicate or undeclared sample: people[0].banana")
    expect(classify(standard_rows(["world.pos"])), "COULD NOT LOOK", 3, "duplicate or undeclared sample: world.pos")
    expect(classify(standard_rows(["people[0].pos"], first_phase="end_of_tick")), "COULD NOT LOOK", 3, "undeclared sample: people[0].pos")



def t_in_tick_tap_rows_are_read_in_the_span():
    """The cast and world taps write their rows with phase in_tick (job_start, job_end, reserve, kill, link, mental_attempt, ...;
    boundary.md). Live on ArchBig 2026-11-25: once the cast tracks were read, the same run read 'invalid phase on tick 15006'.
    They are read; on a track, in_tick stays invalid (a row outside the run's ticks is refused first by the tick order)."""
    def with_row(**row):
        plan, rows, receipts = fixture()
        at = next(i for i, r in enumerate(rows) if r["rec"] == "end")
        rows.insert(at, {**rows[0], **row})
        for r in rows[1:]:
            r.pop("tracks", None)
        return plan, normalize(rows), receipts
    expect(classify(with_row(rec="job_start", phase="in_tick", tick=3, alias="pawn", job="Wait#1", ord=1)), "SUCCESS", 6)
    expect(classify(with_row(rec="rebind", phase="end_of_tick", tick=3, name="pawn.toil", to=None)), "SUCCESS", 6)
    expect(classify(with_row(rec="track", phase="in_tick", tick=3, name="job", st="ok", v="x")), "COULD NOT LOOK", 3,
           "invalid phase on tick 3")


def main():
    tests = [("classifier row 1", t_classifier_rows)] + [
        ("classifier row %s" % n, lambda n=n: classifier_case(n)) for n in range(2, 10)]
    tests += [(t.__name__[2:].replace("_", " "), t) for t in (
        t_no_closing_record, t_dropped_span, t_missing_first_sample, t_missing_last_sample, t_missing_tap,
        t_success_at_first_sample, t_success_without_exposure, t_advisory_record, t_cast_went_to_hazard, t_giver_refusal,
        t_same_checker_adds_history, t_unrecorded_value_named, t_first_outcome_kept, t_alias_needs_link,
        t_forbidden_wins_over_an_unreadable_success, t_standard_cast_and_world_tracks_are_read,
        t_in_tick_tap_rows_are_read_in_the_span, t_cast_link_is_proved_by_the_cast_taps, t_check_rows_decide)]
    tests += [("exit code 0", t_exit_codes)] + [("exit code %s" % n, lambda n=n: exit_case(n)) for n in range(1, 7)]
    tests.append(("unknown key named", t_unknown_key_named))
    good = 0
    for name, test in tests:
        try:
            test()
        except Exception as e:
            print("FAIL %s: %s" % (name, e))
        else:
            print("ok   " + name)
            good += 1
    print("scene judge: %d of %d checks passed" % (good, len(tests)))
    return 0 if good == len(tests) == 36 else 1


if __name__ == "__main__":
    sys.exit(main())
