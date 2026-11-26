#!/usr/bin/env python3
"""Selftest: a pilot holder run whose open items all need the live game gets a live-allowed brief: it takes the bridge
(`bridge take --idle-ok`), brings the game up, runs the live acceptance commands, releases the bridge and never leaves a
broken game running (RIMMANDRAKE_LET_HOLDER_TAKE_BRIDGE_ALL_ITEMS_NEED_GAME). Any other holder or fixer keeps the
offline brief. Offline, on a temp root; no claude, unit, bridge or landing is touched.

    python3 src/RimMandrake/rimflow/selftest_holder_live_brief.py
"""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
SDIR = tempfile.mkdtemp(prefix="holder_live_sd_")
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
    print(("PASS  " if ok else "FAIL  ") + name + ("" if ok else "  " + str(detail)[:300]))


# The offline fixer brief closes on its offline test and runs the touched in-game check on a free game (owner, 2026-11-24; RIMMANDRAKE_RUN_LIVE_CHECKS_IN_BUILDER_RUN_WHEN_GAME_FREE): its old ban on the bridge is gone, so the offline brief is told from the live holder brief by these two marks.
FORBID = "The item closes on its OFFLINE acceptance test"
TAKE = "Every item here needs a game, so this run drives one"

root = tempfile.mkdtemp(prefix="holder_live_st_")
PILOT = (L.config().get("pilot_mods") or ["ExplosiveKnockback"])[0]
os.makedirs(os.path.join(root, "design", "concepts", PILOT))
L.append(root, PILOT, "DISPATCH", "version.open", "version", body={"version": "0.1.0"}, version="0.1.0")
L.append(root, PILOT, "DISPATCH", "stage.enter", "stage", body={"stage": "in_game"})
ev = os.path.join(root, "infrastructure", "state", "ledger", "events")
os.makedirs(ev)
with open(os.path.join(ev, "BENCH.jsonl"), "w", encoding="utf-8") as fh:
    for e in ({"event": "file", "id": "RIMMANDRAKE_FIX_LIVE_ONE_A", "caused_by": "ROUTE_X", "needs": "game-up"},
              {"event": "file", "id": "RIMMANDRAKE_FIX_LIVE_TWO_B", "caused_by": "ROUTE_X", "needs": "bridge"},
              {"event": "file", "id": "RIMMANDRAKE_FIX_OFF_THREE_C", "caused_by": "ROUTE_Y", "needs": "game-up"},
              {"event": "needs", "id": "RIMMANDRAKE_FIX_OFF_THREE_C", "to": "offline"},
              {"event": "file", "id": "RIMMANDRAKE_FIX_PLAIN_FOUR_D", "caused_by": "ROUTE_Y"}):
        fh.write(json.dumps(e) + "\n")

got = M.ledger_items_caused_by(root, ["ROUTE_X", "ROUTE_Y"])
need = {x["id"]: x.get("needs") for x in got}
check("open road-back items carry their needs, the latest `needs` event winning",
      need == {"RIMMANDRAKE_FIX_LIVE_ONE_A": "game-up", "RIMMANDRAKE_FIX_LIVE_TWO_B": "bridge",
               "RIMMANDRAKE_FIX_OFF_THREE_C": "offline", "RIMMANDRAKE_FIX_PLAIN_FOUR_D": None}, need)
check("ledger_needs reads one item's needs", M.ledger_needs(root, ["RIMMANDRAKE_FIX_LIVE_ONE_A"]) ==
      {"RIMMANDRAKE_FIX_LIVE_ONE_A": "game-up"}, M.ledger_needs(root, ["RIMMANDRAKE_FIX_LIVE_ONE_A"]))
check("live_only: every item needs the game", A.live_only([{"needs": "game-up"}, {"needs": "bridge"}]))
check("live_only: one offline item is not live-only", not A.live_only([{"needs": "game-up"}, {"needs": "offline"}]))
check("live_only: an unknown needs is not live-only", not A.live_only([{"needs": "game-up"}, {}]))
check("live_only: no items is not live-only", not A.live_only([]))

off = A.fixer_brief("I", PILOT, 15)
live = A.fixer_brief("I", PILOT, 15, live=True)
check("the offline fixer brief closes on its offline test and is not the live holder brief", FORBID in off and TAKE not in off, off[-300:])
check("the live brief takes the bridge, brings the game up and releases it",
      FORBID not in live and TAKE in live and "./game --idle-ok --why" in live and "bridge release" in live, live)
check("the live brief keeps the live rules: no flyer flight, no fullscreen or focus, no broken game left running",
      "flyer" in live and "fullscreen" in live and "broken game" in live, live)
check("the live brief names the item's LEFT OPEN note as its live commands", "LEFT OPEN" in live, live)

ok_ready = {"ready": lambda r, m: (True, "PASS 7/7"), "land_ledger": lambda paths: "landed",
            "bridge": lambda purpose: (True, "TAKEABLE")}
M.brief_text = lambda r, m, cap, **k: ("", {"stage": "in_game", "owed": "exit_not_met"})
D.ledger_ready = lambda r, m: (True, "PASS 7/7")
sent, kws = [], []


def launch_brief(item, text, model, cap, seat, env=None, **kw):
    sent.append((item, text))
    kws.append(kw)
    return 0, "DETACHED u%d" % len(sent), "u%d" % len(sent)


def pilot(open_items, **extra):
    D._write(os.path.join(SDIR, "state.json"), {"mods": {PILOT: {"road_back": {"caused_by": "ROUTE_X"}}}})
    return D.pilot_launch(root, {"cap_tokens": 3_750_000, "seat": "BENCH"}, PILOT, "t", now=7000 + len(sent), fx=dict(
        ok_ready, open_items=lambda ids: open_items, launch_brief=launch_brief, **extra))


rc, text = pilot([{"id": "RIMMANDRAKE_FIX_LIVE_ONE_A", "needs": "game-up"},
                  {"id": "RIMMANDRAKE_FIX_LIVE_TWO_B", "needs": "bridge"}])
check("pilot-launch: open items all live -> a live-allowed holder brief", rc == 0 and TAKE in sent[-1][1] and
      FORBID not in sent[-1][1] and "RIMMANDRAKE_FIX_LIVE_TWO_B" in sent[-1][1], (rc, text, sent[-1:]))
check("pilot-launch says it is a live holder run", "live" in text, text)
rc, text = pilot([{"id": "RIMMANDRAKE_FIX_LIVE_ONE_A", "needs": "game-up"},
                  {"id": "RIMMANDRAKE_FIX_OFF_THREE_C", "needs": "offline"}])
check("pilot-launch: an offline item among them -> the offline brief", rc == 0 and FORBID in sent[-1][1] and
      TAKE not in sent[-1][1], sent[-1:])
n = len(sent)
rc, text = pilot([{"id": "RIMMANDRAKE_FIX_LIVE_ONE_A", "needs": "game-up"}],
                 bridge=lambda purpose: (False, "HELD  BENCH (another live driver)"))
check("pilot-launch: a live-only holder with the bridge not takeable is refused, nothing launched (one holder at a "
      "time)", rc == 2 and "bridge" in text and len(sent) == n, (rc, text))
rc, text = pilot([{"id": "RIMMANDRAKE_FIX_LIVE_ONE_A"}])
check("pilot-launch: open items without needs read from the ledger (a test's open_items may omit it)",
      rc == 0 and TAKE in sent[-1][1], (rc, text))

check("no holder session recorded: the road-back holder starts from the packet (no --resume)",
      "session" not in kws[-1], kws[-1])
L.record_session(root, PILOT, "sess-abc", 1234, views=False)
rc, text = pilot([{"id": "RIMMANDRAKE_FIX_LIVE_ONE_A", "needs": "game-up"}])
check("a recorded holder session is resumed by the next road-back holder run (modledger.resume_plan)",
      rc == 0 and kws[-1].get("session") == "sess-abc" and "resume" in text, (rc, text, kws[-1]))

# the Dispatch step's own fixer launch on a pilot (maturation_autonomy._execute_one): the fix item's needs decide
st = {"mods": {PILOT: {}}}
seen = []
for item, want in (("RIMMANDRAKE_FIX_LIVE_ONE_A", True), ("RIMMANDRAKE_FIX_OFF_THREE_C", False)):
    row = {"mod": PILOT, "aut": "fixer", "fix_item": item, "cap": 15, "stage": "in_game"}
    A._execute_one(root, {"seat": "BENCH"}, st, row, 8000 + len(seen), None,
                   lambda it, text, model, cap, seat, env=None: seen.append(text) or (0, "DETACHED v", "v"), set())
    check("dispatcher fixer on a pilot, %s (%s): %s brief" % (item, "game" if want else "offline",
                                                              "live" if want else "offline"),
          seen and ((TAKE in seen[-1] and FORBID not in seen[-1]) if want else (FORBID in seen[-1])), seen[-1:])

shutil.rmtree(SDIR, ignore_errors=True)
shutil.rmtree(root, ignore_errors=True)
print("PASS %d/%d" % (sum(res), len(res)) if all(res) else "FAIL %d of %d" % (res.count(False), len(res)))
sys.exit(0 if all(res) else 1)
