#!/usr/bin/env python3
"""selftest_ops_watch_review_finish.py — four ops_watch.py defects from its full-file review
(RELENTLESS_REVIEW_FINISH_TOO_BIG_TO_SKIM). Each check fails on the code before the fix.

1. run_alarms: a PENDING alarm whose saved name is on the ledger but CLOSED is not acknowledged as filed (that tells
   nobody): it stays PENDING as a reopen.
2. andon silent rule: a MEASURED state string ("RUNNING") is a reading, not silence.
3. run_alarms fresh news: a note cut at 600 chars marks noted only the names it said; the rest are said next pass.
4. metric_problem: an idle_if gate from another family is refused (per-family stamping can never read it).
5. dead_targets: a wildcard target with no instance this pass (testing.red_* on a clean night) is not a dead rule.
6. run_alarms: a new filing marks noted only the names its title shows: the next pass notes the rest (6b: a cut title).
7. found_filed recovery delivers the Conductor line the pass that died after filing may have owed.
8. c_relentless: a reading.json stamped ahead of the clock counts as blind.

Fixtures only: rules are built here, alarm state lives in a temp RM_OPS_WATCH_DIR, the filer and minter are fakes.

    python3 src/RimMandrake/Utils/selftest_ops_watch_review_finish.py
"""
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
TMP = Path(tempfile.mkdtemp(prefix="selftest_ops_watch_review_finish_"))
os.environ["RM_OPS_WATCH_DIR"] = str(TMP / "ops")
(TMP / "ops").mkdir()
FAILS = []
NOW = 1_800_000_000.0


def ok(cond, what, got=None):
    print(("PASS " if cond else "FAIL ") + what + ("" if cond else "  got: %r" % (got,)))
    if not cond:
        FAILS.append(what)


def M(v, **x):
    return {"m": "MEASURED", "v": v, "x": x}


def main():
    import ops_watch as ow
    ow.mint_name = lambda tag, known, prefix: prefix + "_AB12"
    rules = {"alarms": {"clear_passes": 1},
             "targets": [{"key": "t.reds", "op": ">", "value": 0, "alarm": True, "tag": "T_RED", "name": "OPS_T_RED",
                          "marks": ["MEASURED"], "note_field": "news"}]}
    aid = "T_RED:t.reds"
    sent = []

    def filer(todo, conf):
        sent.append([dict(a) for a in todo])
        return {a["name"]: None for a in todo}

    def put(obj):
        (ow.ops_dir() / "alarms.json").write_text(json.dumps(obj))

    def state():
        return ow.read_json(ow.ops_dir() / "alarms.json")

    # 1. a PENDING whose name is a closed item
    put({aid: {"state": "PENDING", "since": ow.iso(NOW), "tries": 1,
               "name": "OPS_T_RED_AB12", "title": "Ops alarm T_RED",
               "noted": ["a"], "told": {"v": 1, "class": None}}})   # nothing new: no news reopens it later
    ow.run_alarms({"t.reds": M(1, news=["a"])}, rules, NOW, {"OPS_T_RED_AB12"}, None, open_ids=set())
    cur = state().get(aid) or {}
    ok(cur.get("state") == "PENDING" and cur.get("reopen") is True,
       "1: a PENDING named for a CLOSED item stays PENDING as a reopen, not acknowledged", cur)
    put({aid: {"state": "PENDING", "since": ow.iso(NOW), "tries": 1,
               "name": "OPS_T_RED_AB12", "title": "Ops alarm T_RED"}})
    ow.run_alarms({"t.reds": M(1, news=["a"])}, rules, NOW, {"OPS_T_RED_AB12"}, None, open_ids={"OPS_T_RED_AB12"})
    cur = state().get(aid) or {}
    ok(cur.get("state") == "OPEN" and cur.get("item") == "OPS_T_RED_AB12",
       "1: a PENDING named for an OPEN item is found filed (unchanged)", cur)

    # 3. fresh news longer than 600 chars
    long_names = ["N%02d_" % i + "x" * 95 for i in range(10)]       # 10 x 99 chars: about six fit in 600
    put({aid: {"state": "OPEN", "item": "OPS_T_RED_AB12", "name": "OPS_T_RED_AB12",
               "noted": [], "told": {"v": 10, "class": None}}})
    ow.run_alarms({"t.reds": M(10, news=long_names)}, rules, NOW, {"OPS_T_RED_AB12"}, filer, open_ids={"OPS_T_RED_AB12"})
    cur = state().get(aid) or {}
    note = (sent[-1][0]["text"] if sent and sent[-1] else "")
    noted = cur.get("noted") or []
    said = [n for n in long_names if n in note]
    ok(said and len(said) < len(long_names), "3: the note says some names whole, not all", (len(said), note[-80:]))
    ok(set(noted) == set(said), "3: noted holds exactly the names the note said", (len(noted), len(said)))
    ok("more next pass" in note, "3: the note says the rest come next pass", note[-80:])
    ow.run_alarms({"t.reds": M(10, news=long_names)}, rules, NOW + 900, {"OPS_T_RED_AB12"}, filer,
                  open_ids={"OPS_T_RED_AB12"})
    cur = state().get(aid) or {}
    ok(set(cur.get("noted") or []) > set(noted), "3: the next pass says names the first left out", len(cur.get("noted") or []))

    # 2. silent rule on a MEASURED string
    arules = {"band": {"keys": [], "skip": []}, "run": {"keys": []}, "targets": [],
              "silent": {"keys": ["s.*"], "skip": [], "per_key": {}, "default_h": 1}}
    lm = {"s.state": NOW - 5 * 3600}
    flags = ow.andon({"s.state": M("RUNNING")}, {}, lm, arules, NOW)
    ok(not [f for f in flags if f["rule"] == "silent"], "2: a MEASURED state string is not silent",
       [f for f in flags if f["rule"] == "silent"])
    flags = ow.andon({"s.state": {"m": "UNMEASURED", "v": None}}, {}, lm, arules, NOW)
    ok([f for f in flags if f["rule"] == "silent"], "2: an UNMEASURED reading past its limit is still silent", flags)

    # 4. cross-family idle_if
    base = {"owner": "Ops", "why": "w", "max_age_min": 10, "classes": {"sane": {"at_least": 0}}}
    gate = {"owner": "Ops", "why": "w", "max_age_min": 10, "classes": {"idle": {"in": ["yes"]}, "sane": {"otherwise": True}}}
    ms = {"fam.m": dict(base, idle_if=["other.gate"]), "other.gate": gate, "fam.gate": gate}
    ok(ow.metric_problem("fam.m", ms["fam.m"], ms) is not None and "family" in ow.metric_problem("fam.m", ms["fam.m"], ms),
       "4: an idle_if gate from another family is refused", ow.metric_problem("fam.m", ms["fam.m"], ms))
    ok(ow.metric_problem("fam.m", dict(base, idle_if=["fam.gate"]), ms) is None, "4: a same-family gate is accepted")
    ok(not ow.ranges_problems(ow.load_rules()), "4: the shipped rules still pass", ow.ranges_problems(ow.load_rules()))

    # 6. a fresh filing carries its title only: the names reach the item in the first note after it
    sent.clear()
    put({})
    ow.run_alarms({"t.reds": M(2, news=["n1", "n2"])}, rules, NOW, set(), filer, open_ids=set())
    filed = [a["name"] for a in (sent[-1] if sent else []) if not a.get("note_only")]
    ok(len(filed) == 1, "6: a new crossing files", sent)
    ow.run_alarms({"t.reds": M(2, news=["n1", "n2"])}, rules, NOW + 900, set(filed), filer, open_ids=set(filed))
    notes = [a["text"] for a in (sent[-1] if len(sent) > 1 else []) if a.get("note_only")]
    ok(notes and "n1" in notes[0] and "n2" in notes[0], "6: the next pass notes the names the filing did not say", notes)

    # 6b. a title that shows names marks those told (RED_COP_BUILD_NO_ORPHAN_REDS): only a name its cut dropped is noted
    sent.clear()
    put({})
    rt = {"alarms": {"clear_passes": 1},
          "targets": [dict(rules["targets"][0], title_field="said")]}
    long_ = "z" * 200
    pt = M(3, said="n1 and n2 " + long_, news=["n1 (x)", "n2 (x)", "n3 (x)"], titled={"n1 (x)": "n1", "n2 (x)": "n2", "n3 (x)": "n3"})
    ow.run_alarms({"t.reds": pt}, rt, NOW, set(), filer, open_ids=set())
    filed = [a["name"] for a in (sent[-1] if sent else []) if not a.get("note_only")]
    ok(len(filed) == 1, "6b: a new crossing files", sent)
    ow.run_alarms({"t.reds": pt}, rt, NOW + 900, set(filed), filer, open_ids=set(filed))
    notes = [a["text"] for a in (sent[-1] if len(sent) > 1 else []) if a.get("note_only")]
    ok(len(notes) == 1 and "n3" in notes[0] and "n1" not in notes[0] and "n2" not in notes[0],
       "6b: the next pass notes only the name the title did not show", notes)
    ow.run_alarms({"t.reds": pt}, rt, NOW + 1800, set(filed), filer, open_ids=set(filed))
    ok(len(sent) == 2, "6b: the pass after says nothing more", sent[2:])

    # 7. found_filed recovery delivers a Conductor line the dead pass may have owed
    clog = TMP / "conductor.md"
    rules7 = {"alarms": {"clear_passes": 1}, "targets": [dict(rules["targets"][0], conductor_log=str(clog))]}
    put({aid: {"state": "PENDING", "since": ow.iso(NOW), "tries": 1, "name": "OPS_T_RED_AB12",
               "title": "Ops alarm T_RED: t.reds = 1", "conductor_log": str(clog), "noted": ["a"],
               "told": {"v": 1, "class": None}}})
    ow.run_alarms({"t.reds": M(1, news=["a"])}, rules7, NOW, {"OPS_T_RED_AB12"}, None, open_ids={"OPS_T_RED_AB12"})
    said = clog.read_text() if clog.exists() else ""
    ok("OPS_T_RED_AB12" in said and "ALARM" in said, "7: found_filed delivers the owed Conductor line", said)

    # 8. reading.json dated ahead of the clock is blind, not fresh
    root = TMP / "belt"
    (root / "store" / "items").mkdir(parents=True)
    (root / "live").mkdir()
    (root / "live" / "runs.jsonl").write_text("")
    at = ow.iso(NOW)
    row = {"at": at, "t": NOW, "live": 3, "running": 3, "places": 3, "target": 3, "ready": 4, "minutes_under": 0,
           "under": False, "why": None, "checks": {"waiting": 0, "running": 1, "oldest_wait_s": 0}}
    for n, o in (("staffing.json", row), ("reading.json", {"at": ow.iso(NOW + 86400)}), ("breaker.json", {})):
        (root / "store" / n).write_text(json.dumps(o))
    (root / "store" / "staffing.jsonl").write_text(json.dumps(row) + "\n")
    (root / "store" / "journal.jsonl").write_text(json.dumps({"at": at, "do": "lease"}) + "\n")
    saved = os.environ.get("RELENTLESS_ROOT")
    os.environ["RELENTLESS_ROOT"] = str(root)
    try:
        pts = ow.c_relentless(NOW, ow.load_rules(), {})
    finally:
        if saved is None:
            os.environ.pop("RELENTLESS_ROOT", None)
        else:
            os.environ["RELENTLESS_ROOT"] = saved
    cause = str((pts.get("relentless.blind") or {}).get("x", {}).get("cause"))
    ok("reading.json is dated" in cause, "8: a reading.json stamped a day ahead counts as blind", cause)

    # 5. a wildcard target that matches nothing this pass (a quiet night) is not a dead rule
    def tg(key):
        return {"key": key, "op": ">", "value": 0, "alarm": True, "tag": "T5", "name": "OPS_T5", "marks": ["MEASURED"]}
    pts = {"testing.nightly_news": M(0)}
    dead = lambda key: [f["key"] for f in ow.dead_targets({"targets": [tg(key)]}, pts)]
    ok(dead("testing.red_*") == [], "5: a wildcard with no instance this pass raises no bad_rule", dead("testing.red_*"))
    ok(dead("nofamily.red_*") == ["rules.target.nofamily.red_*"], "5: a wildcard on a family nobody reports is dead",
       dead("nofamily.red_*"))
    ok(dead("testing.absent") == ["rules.target.testing.absent"], "5: a literal key no reading carries is dead",
       dead("testing.absent"))


if __name__ == "__main__":
    try:
        main()
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    print("RESULT: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    sys.exit(1 if FAILS else 0)
