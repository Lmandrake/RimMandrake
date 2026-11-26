#!/usr/bin/env python3
"""Selftest: offline stages never wait for a game (spec 2026-11-13-maturation-pipeline.md §4 Stage 3 exit and the Stage 6
road back; item RIMMANDRAKE_CLOSE_OFFLINE_STAGE_ITEMS_OFFLINE_GAME_WAS_DEMANDED, the owner 2026-11-16: "You are saying
Step 3 for these builders requires the game? That's not how it's supposed to have to be").

1. A road-back item worked at an offline stage closes on an OFFLINE acceptance command; its in-game check is recorded
   UNRUN with its exact command (`maturation.py unrun`) and the Stage 6 brief lists it.
2. No holder or fixer brief at an offline stage allows the bridge; the live brief is for Stage 6 records only.
3. A fault only the game can show is Stage 6 work: the tick gives it no offline run, and the record goes back to Stage 6
   (`advance --to in_game --game-only`, or in_game -> in_game, the next visit), never parked at Stage 3.

Offline, on temp roots; no claude, unit, bridge or landing is touched.

    python3 src/RimMandrake/rimflow/selftest_offline_stage_road_back.py
"""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
SDIR = tempfile.mkdtemp(prefix="offline_rb_sd_")
os.environ["RM_MATURATION_DISPATCH_DIR"] = SDIR       # never the live dispatcher's state
os.environ["RM_STAGE_LAND"] = "0"
for _k in ("RM_MODLEDGER_WRITER", "RM_MODLEDGER_TOKEN"):
    os.environ.pop(_k, None)
import maturation_autonomy as A     # noqa: E402
import maturation as M              # noqa: E402
import maturation_dispatch as D     # noqa: E402
import modledger as L               # noqa: E402

res = []


def check(name, ok, detail=""):
    res.append(bool(ok))
    print(("PASS  " if ok else "FAIL  ") + name + ("" if ok else "  " + str(detail)[:400]))


def attempt(name, fn):
    try:
        return fn()
    except Exception as e:      # noqa: BLE001  a missing function is this test's FAIL, never its crash
        check(name, False, "%s: %s" % (type(e).__name__, e))
        return None


# The offline fixer brief closes on its offline test and runs the touched in-game check on a free game (owner, 2026-11-24; RIMMANDRAKE_RUN_LIVE_CHECKS_IN_BUILDER_RUN_WHEN_GAME_FREE): its old ban on the bridge is gone, so the offline brief is told from the live holder brief by these two marks.
FORBID = "The item closes on its OFFLINE acceptance test"
TAKE = "Every item here needs a game, so this run drives one"
LIVE_A, LIVE_B, OFF_C = "RIMMANDRAKE_FIX_LIVE_ONE_A", "RIMMANDRAKE_FIX_LIVE_TWO_B", "RIMMANDRAKE_FIX_OFF_THREE_C"

root = tempfile.mkdtemp(prefix="offline_rb_st_")
PILOT = (L.config().get("pilot_mods") or ["ExplosiveKnockback"])[0]
os.makedirs(os.path.join(root, "design", "concepts", PILOT, "version"))
L.append(root, PILOT, "DISPATCH", "version.open", "version", body={"version": "0.1.0"}, version="0.1.0")
L.append(root, PILOT, "DISPATCH", "stage.enter", "stage", body={"stage": "offline_build"})
ev = os.path.join(root, "infrastructure", "state", "ledger", "events")
os.makedirs(ev)
with open(os.path.join(ev, "BENCH.jsonl"), "w", encoding="utf-8") as fh:
    for e in ({"event": "file", "id": LIVE_A, "caused_by": "ROUTE_X", "needs": "game-up"},
              {"event": "file", "id": LIVE_B, "caused_by": "ROUTE_X", "needs": "bridge"},
              {"event": "file", "id": OFF_C, "caused_by": "ROUTE_X", "needs": "offline"}):
        fh.write(json.dumps(e) + "\n")

cdir = os.path.join(root, "design", "concepts", PILOT)


def put_record(stage, moves):
    with open(os.path.join(cdir, "version", "VERSION.json"), "w") as f:
        json.dump({"version": "0.1.0"}, f)
    with open(os.path.join(cdir, M.RECORD), "w") as f:
        json.dump({"mod": PILOT, "version": "0.1.0", "stage": stage, "moves": moves, "cycles": {"visit": 1, "total": 2}},
                  f)


BACK = [{"from": "blind_challenge", "to": "in_game", "at": "2026-11-15T15:13:51-08:00"},
        {"from": "in_game", "to": "offline_build", "at": "2026-11-15T17:50:11-08:00"}]

# ---- 2. the briefs: the live one only at Stage 6 ----------------------------------------------------------------------
check("the offline-stage fixer brief closes on the offline test and records the live check UNRUN (maturation.py unrun)",
      "maturation.py unrun" in A.fixer_brief("I", PILOT, 15) and FORBID in A.fixer_brief("I", PILOT, 15),
      A.fixer_brief("I", PILOT, 15)[-500:])
check("game_takeable: only a Stage 6 record may have the game",
      attempt("game_takeable", lambda: [M.game_takeable(s) for s in M.WORDS]) ==
      [w == "in_game" for w in M.WORDS])

ok_ready = {"ready": lambda r, m: (True, "PASS 7/7"), "land_ledger": lambda paths: "landed",
            "bridge": lambda purpose: (True, "TAKEABLE")}
D.ledger_ready = lambda r, m: (True, "PASS 7/7")
STAGE = {"now": "offline_build"}
M.brief_text = lambda r, m, cap, **k: ("", {"stage": STAGE["now"], "owed": "nothing"})
sent = []


def launch_brief(item, text, model, cap, seat, env=None, **kw):
    sent.append((item, text))
    return 0, "DETACHED u%d" % len(sent), "u%d" % len(sent)


def pilot(open_items, stage):
    STAGE["now"] = stage
    D._write(os.path.join(SDIR, "state.json"), {"mods": {PILOT: {"road_back": {"caused_by": "ROUTE_X"}}}})
    return D.pilot_launch(root, {"cap_tokens": 3_750_000, "seat": "BENCH"}, PILOT, "t", now=7000 + len(sent), fx=dict(
        ok_ready, open_items=lambda ids: open_items, launch_brief=launch_brief))


ALL_LIVE = [{"id": LIVE_A, "needs": "game-up"}, {"id": LIVE_B, "needs": "bridge"}]
n = len(sent)
rc, text = pilot(ALL_LIVE, "offline_build")
check("pilot-launch at Stage 3, every open item game-only: refused, nothing launched, no bridge", rc == 2 and
      len(sent) == n, (rc, text, sent[n:]))
check("the refusal names the move back to Stage 6 (advance --to in_game --game-only)",
      "--to in_game" in text and "--game-only" in text and LIVE_A in text, text)
rc, text = pilot(ALL_LIVE + [{"id": OFF_C, "needs": "offline"}], "offline_build")
b = sent[-1][1] if len(sent) > n else ""
check("pilot-launch at Stage 3 with an offline item among game-only ones: an offline brief, not the live holder brief",
      rc == 0 and FORBID in b and TAKE not in b, (rc, text, b[-400:]))
check("that holder works the offline item and leaves the game-only ones to Stage 6",
      ("work every open road-back item together, from the packet above: %s." % OFF_C) in b and "Stage 6" in b, b[-600:])
rc, text = pilot(ALL_LIVE, "in_game")
check("pilot-launch at Stage 6, every open item live: the live brief stands (Stage 6 needs it)",
      rc == 0 and TAKE in sent[-1][1] and FORBID not in sent[-1][1], (rc, text))
rc, text = pilot(ALL_LIVE, "blind_challenge")
check("pilot-launch at Stages 4 and 5 is offline too: refused, not given the game", rc == 2 and "--game-only" in text,
      (rc, text))

seen = []
st = {"mods": {PILOT: {}}}
for stage, want in (("offline_build", False), ("blind_challenge", False), ("in_game", True)):
    row = {"mod": PILOT, "aut": "fixer", "fix_item": LIVE_A, "cap": 15, "stage": stage}
    A._execute_one(root, {"seat": "BENCH"}, st, row, 8000 + len(seen), None,
                   lambda it, text, model, cap, seat, env=None: seen.append(text) or (0, "DETACHED v", "v"), set())
    check("dispatcher fixer on a game-up item at %s: %s brief" % (stage, "live" if want else "offline"),
          seen and ((TAKE in seen[-1] and FORBID not in seen[-1]) if want else (FORBID in seen[-1] and
                                                                                 TAKE not in seen[-1])), seen[-1:])

# ---- 3. a game-only fault is Stage 6 work ------------------------------------------------------------------------------
def road_back(items, stage):
    s = {"road_back": {"caused_by": "ROUTE_X"}}
    row = {"mod": PILOT, "stage": stage}
    row["_rv"] = A._road_back(s, row, lambda ids: items, 100, ver="0.1.0", version_bugs=lambda m, v: [])
    return row


row = road_back(ALL_LIVE, "offline_build")
# RIMMANDRAKE_UNPARK_FLOWWORKS_STUCK_AT_OFFLINE_STAGE_EIGHT_HOURS: this check pinned the hand line (decision game_only,
# the move printed in the Needs Conductor line), which left the record parked at Stage 3 against promise 3 above; the
# tick now takes the move itself (selftest_tick_game_only_exit.py holds the act's promises)
check("the tick at Stage 3 gives no fixer to game-only items; it takes the game-only exit back to Stage 6 itself",
      row.get("decision") == "autogameonly" and row.get("aut") == "autogameonly" and not row.get("fix_item")
      and row.get("game_only_items") == [LIVE_A, LIVE_B] and not row.get("need"), row)
# RIMMANDRAKE_REPAIR_PYRELANDS_FORM_REFUSAL_AT_THE_RUN_FIVE: at Stage 4/5 the move to in_game is the FORWARD exit (the
# blind cycle's exit reading, the steward's confirm, the certificate), so a DISPATCH game-only exit there is refused
# every time; Pyrelands, sent to blind_challenge by the Conductor, had its cycle 5 replaced by that refused act
row = road_back(ALL_LIVE, "blind_challenge")
check("the tick at Stage 4/5, every open item game-only: no game-only exit; the blind cycle or its steward runs",
      row.get("_rv") is False and row.get("decision") != "autogameonly" and row.get("aut") is None
      and not row.get("fix_item"), row)
row = road_back([{"id": LIVE_A, "needs": "game-up"}, {"id": OFF_C, "needs": "offline"}], "offline_build")
check("the tick at Stage 3 with a mix: the fixer goes to the offline item only", row.get("fix_item") == OFF_C, row)
row = road_back(ALL_LIVE, "in_game")
check("the tick at Stage 6: a game-up item still gets its fixer (it may have the game there)",
      row.get("fix_item") == LIVE_A, row)

put_record("offline_build", BACK)
ev_part = attempt("evaluate game_only part", lambda: M.evaluate(root, PILOT, "in_game", game_only=[LIVE_A, LIVE_B]))
check("--game-only leaving an open item of the same road back unnamed (an offline one) is refused",
      ev_part is not None and "game_only" in [r["clause"] for r in ev_part["verdict"]["refusals"]],
      ev_part and ev_part["verdict"]["refusals"])
with open(os.path.join(ev, "BENCH.jsonl"), "a", encoding="utf-8") as fh:
    fh.write(json.dumps({"event": "close", "id": OFF_C, "sha": "abc1234"}) + "\n")
ev_ok = attempt("evaluate game_only", lambda: M.evaluate(root, PILOT, "in_game", game_only=[LIVE_A, LIVE_B]))
refused = [r["clause"] for r in (ev_ok or {}).get("verdict", {}).get("refusals", [])]
check("advance --to in_game --game-only from Stage 3, every named item open and game-only: order and game_only pass",
      ev_ok is not None and "order" not in refused and "game_only" not in refused, refused)
ev_mix = attempt("evaluate game_only mix", lambda: M.evaluate(root, PILOT, "in_game", game_only=[LIVE_A, OFF_C]))
check("--game-only naming an offline item is refused (an offline test can show it)",
      ev_mix is not None and "game_only" in [r["clause"] for r in ev_mix["verdict"]["refusals"]], ev_mix and
      ev_mix["verdict"]["refusals"])
ev_none = M.evaluate(root, PILOT, "in_game")
check("Stage 3 -> Stage 6 without --game-only is still refused (forward is one stage)",
      "order" in [r["clause"] for r in ev_none["verdict"]["refusals"]])
put_record("offline_build", [])
ev_new = attempt("evaluate never at 6", lambda: M.evaluate(root, PILOT, "in_game", game_only=[LIVE_A]))
check("--game-only on a record that never came back from Stage 6 is refused",
      ev_new is not None and "game_only" in [r["clause"] for r in ev_new["verdict"]["refusals"]],
      ev_new and ev_new["verdict"]["refusals"])
check("Stage 6 -> Stage 6 is a drawn road (a game-only failure opens the next visit)",
      "in_game" in M.ROADS_BACK.get("in_game", ()), M.ROADS_BACK.get("in_game"))

# ---- 1. the in-game half of an offline-closed item is recorded UNRUN ---------------------------------------------------
put_record("in_game", BACK + [{"from": "offline_build", "to": "in_game", "at": "2026-11-16T02:00:00-08:00"}])
with open(os.path.join(cdir, "version", "test_table.json"), "w") as f:
    json.dump({"tests": {"sc_walk": {"kind": "live_full", "stage": "6", "command": "python.exe walk.py --out <json>",
                                     "bars": ["B1"]}}}, f)
CMD = "python.exe src/RimMandrake/FlowWorks/northstar/concept_scenes.py --scene scene_walk_moat_season --out <json>"
row1 = attempt("record_unrun", lambda: M.record_unrun(root, PILOT, OFF_C, "sc_walk", CMD,
                                                      "python3 selftest_walk_scene.py", "abc1234", by="BENCH"))
got = attempt("read_unrun", lambda: M.read_unrun(root, PILOT)) or []
check("maturation.py unrun records the item's in-game check UNRUN with its exact command",
      len(got) == 1 and got[0].get("result") == "UNRUN" and got[0].get("command") == CMD and
      got[0].get("item") == OFF_C and got[0].get("check") == "sc_walk", got)
def _refuses(fn):
    try:
        fn()
    except ValueError:
        return True
    return False


check("an UNRUN record with no command is refused", _refuses(lambda: M.record_unrun(
    root, PILOT, OFF_C, "sc_walk", "", "python3 t.py", "abc1234")) if hasattr(M, "record_unrun") else False)
brief = attempt("ingame brief", lambda: M.ingame_brief_text(root, PILOT, 10)[0]) or ""
check("the Stage 6 brief lists the UNRUN in-game check with its item and exact command",
      "UNRUN" in brief and OFF_C in brief and CMD in brief, brief[-800:])

# ---- 1b. the steward's road-back instructions ---------------------------------------------------------------------------
sb = A.steward_brief(root, PILOT, {"steward_kind": "exit_not_met", "stage": "in_game", "decision": "steward",
                                   "why": "visit ended not met"})
check("the Stage 6 steward files an offline acceptance command for a line it sends to Stage 3",
      "offline acceptance" in sb and "maturation.py unrun" in sb, sb[:1600])
check("the Stage 6 steward keeps a game-only line at Stage 6 (advance --to in_game), never parks it at Stage 3",
      "--to in_game" in sb and "game-only" in sb, sb[:1600])

shutil.rmtree(SDIR, ignore_errors=True)
shutil.rmtree(root, ignore_errors=True)
print("PASS %d/%d" % (sum(res), len(res)) if all(res) else "FAIL %d of %d" % (res.count(False), len(res)))
sys.exit(0 if all(res) else 1)
