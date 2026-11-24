#!/usr/bin/env python3
"""selftest_wrapup_void_relaunch.py — RELAPSE_WRAPUP_FIX_DIED_TWICE: a debt owed to a game process that has exited
stops standing, and sweep pays it; an unmeasured relaunch never clears one.

The incident (wrapup-20261105161822) relapsed because SettingsTransaction / door debts owed by dead python.exe pids
aged past DEBT_AGE_S and stood until a hand `resolve`, though the game process holding the change had been relaunched.

  V1  the instance: aged debts (an unkeyed SettingsTransaction row and a keyed door row) owed BEFORE the relaunch do
      not stand; sweep moves them to resolved/ with a void why and empties the register
  V2  a debt owed AFTER the relaunch (the running process) still stands once aged
  V3  relaunch unmeasured (no Player-prev.log, or the reader raises): the aged debt stands, sweep pays nothing
  V4  a filed open record whose debt rows (unkeyed and keyed, in debts/filed/) predate the relaunch stops standing,
      sweep resolves the file and clears debts/filed/
  V6  clock-skew margin: a debt owed within VOID_MARGIN_S before the relaunch stands; a non-object debt file never
      crashes sweep
  V5  World.game_relaunched reads the file RM_WRAPUP_PREV_LOG names: its mtime; '' or missing = None
  V7  new scene and setting debts carry the game's letter, including when filed in an open record
  V8  only that game's previous log can void a registered or filed debt; an absent log leaves it standing
"""
import glob
import json
import os
import sys
import tempfile
import time
from unittest.mock import Mock, patch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
TMP = tempfile.mkdtemp(prefix="selftest_wrapup_void_")
os.environ["RM_WRAPUP_DIR"] = os.path.join(TMP, "state")
os.environ["RM_WRAPUP_PREV_LOG"] = ""
os.environ["RM_HOST"] = "archmagi"
os.environ["RM_GAME_INSTANCE"] = "a"
os.environ["RM_INSTANCES_ROOT"] = os.path.join(TMP, "instances")

import wrapup  # noqa: E402

FAILS = []


def check(ok, what):
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


class Fake(wrapup.World):
    def __init__(self, relaunched=None, raises=False):
        self.relaunched, self.raises = relaunched, raises

    def game_a_hold(self):
        return None

    def game_relaunched(self, game="a"):
        if self.raises:
            raise OSError("drive gone")
        return self.relaunched


def put_debt(at, owner, key=None, sub=()):
    tok = "T%d-%s" % (int(at), owner.replace(":", ""))
    body = {"token": tok, "kind": "setting", "what": "forced %s" % owner, "undo": "x", "owner": owner,
            "at": wrapup._iso(at), "cwd": TMP}
    if key:
        body.update(key=key, orig="True")
    wrapup._write_json(wrapup._p("debts", *(list(sub) + [tok + ".json"])), body)
    return tok


def standing_tokens(world, now):
    return sorted(r.get("token") for _, _, rs in wrapup.standing(world, now=now) for r in rs if r.get("token"))


def reset():
    for f in glob.glob(wrapup._p("*", "*.json")) + glob.glob(wrapup._p("debts", "filed", "*.json")):
        os.remove(f)


now = time.time()
launch = now - 2 * 3600                       # the game relaunched two hours ago
old = now - wrapup.DEBT_AGE_S - 3600          # owed seven hours ago, to the process before

# V1 -----------------------------------------------------------------------------------------------------------------
t_tx = put_debt(old, "pid:21516")
t_door = put_debt(old + 1, "pid:21516", key="debug_settings:enableStoryteller")
check(standing_tokens(Fake(None), now) == sorted([t_tx, t_door]),
      "V1 guard: unmeasured relaunch, the instance's two aged debts stand (as they did in the incident)")
check(standing_tokens(Fake(launch), now) == [], "V1 owed before the relaunch: neither stands")
c, left = wrapup.sweep(Fake(launch))
res = [json.load(open(f)) for f in glob.glob(wrapup._p("resolved", "debt-*.json"))]
check(c == 2 and left == 0 and not glob.glob(wrapup._p("debts", "*.json")),
      "V1 sweep pays both off the register (cleared=%d left=%d)" % (c, left))
check(len(res) == 2 and all("void" in r["resolved"]["why"] and "Player-prev.log" in r["resolved"]["why"] for r in res),
      "V1 each lands in resolved/ with a void why")
reset()

# V2 -----------------------------------------------------------------------------------------------------------------
t_now = put_debt(launch + 60, "pid:33028")
later = launch + 60 + wrapup.DEBT_AGE_S + 60
check(standing_tokens(Fake(launch), later) == [t_now], "V2 owed after the relaunch: stands once aged")
check(wrapup.sweep(Fake(launch))[0] == 0 and glob.glob(wrapup._p("debts", "*.json")), "V2 sweep does not pay it")
reset()

# V3 -----------------------------------------------------------------------------------------------------------------
t3 = put_debt(old, "pid:1")
check(standing_tokens(Fake(None), now) == [t3], "V3 no Player-prev.log: the aged debt stands")
check(standing_tokens(Fake(raises=True), now) == [t3], "V3 reader raises: the aged debt stands")
check(wrapup.sweep(Fake(raises=True))[0] == 0 and glob.glob(wrapup._p("debts", "*.json")), "V3 sweep pays nothing")
reset()

# V4 -----------------------------------------------------------------------------------------------------------------
os.environ["RM_ROLE_UNIT"] = "v4"
tk = wrapup.owe("setting", "debug_settings:x=False (was True)", "set x", extra={"key": "debug_settings:x", "orig": "True"})
tu = wrapup.owe("setting", "SettingsTransaction forced debug x=False", "set it back")
ctx = {"kind": "unit", "key": "v4", "seat": "BENCH", "owner": "unit:v4", "holder": "RELENTLESS", "clones": [],
       "since": None, "carried": False}
rec = wrapup.run(Fake(None), ctx)
debt_rows = [r for r in rec["rows"] if r["kind"] == "debt"]
check(len(debt_rows) == 2 and all(r.get("at") for r in debt_rows), "V4 filed debt rows carry the debt's own time")
check(os.path.exists(wrapup._p("debts", "filed", tk + ".json")), "V4 the keyed one waits in debts/filed/")
t_rec = time.time()
check(len([r for _, _, rs in wrapup.standing(Fake(t_rec - 3600), now=t_rec) for r in rs]) == 2,
      "V4 relaunch before the debts: both rows stand")
check([r for _, _, rs in wrapup.standing(Fake(t_rec + 600), now=t_rec) for r in rs] == [],
      "V4 relaunch after the debts: no row stands")
c, left = wrapup.sweep(Fake(t_rec + 600))
check(not glob.glob(wrapup._p("open", "*.json")) and not glob.glob(wrapup._p("debts", "filed", "*.json")) and left == 0,
      "V4 sweep resolves the open file and clears debts/filed/ (cleared=%d)" % c)
# a pre-change record (rows without `at`) falls back to the record's own time
legacy = dict(rec, rows=[dict(r, at=None) for r in debt_rows])
wrapup._write_json(wrapup._p("open", "unit-legacy.json"), legacy)
check([r for _, _, rs in wrapup.standing(Fake(t_rec + 600), now=t_rec) for r in rs] == [],
      "V4 a legacy row without `at` is judged by its record's time")
del os.environ["RM_ROLE_UNIT"]
reset()

# V6 -----------------------------------------------------------------------------------------------------------------
t6 = put_debt(launch - 60, "pid:6")
check(standing_tokens(Fake(launch), launch - 60 + wrapup.DEBT_AGE_S + 60) == [t6],
      "V6 owed 60 s before the relaunch (inside the skew margin): stands")
wrapup._write_json(wrapup._p("debts", "list.json"), ["not", "a", "debt"])
try:
    wrapup.sweep(Fake(launch))
    check(True, "V6 a non-object debt file does not crash sweep")
except Exception as e:  # noqa: BLE001
    check(False, "V6 a non-object debt file does not crash sweep: %r" % e)
reset()

# V5 -----------------------------------------------------------------------------------------------------------------
pl = os.path.join(TMP, "Player-prev.log")
open(pl, "w").close()
os.utime(pl, (launch, launch))
os.environ["RM_WRAPUP_PREV_LOG"] = pl
check(abs(wrapup.World().game_relaunched() - launch) < 1, "V5 reads the named file's mtime")
os.environ["RM_WRAPUP_PREV_LOG"] = os.path.join(TMP, "missing.log")
check(wrapup.World().game_relaunched() is None, "V5 missing file: None")
os.environ["RM_WRAPUP_PREV_LOG"] = ""
check(wrapup.World().game_relaunched() is None, "V5 empty name: None")

def t_debts_keep_the_games_letter():
    os.environ["RM_GAME_INSTANCE"] = "ArchSmall"
    try:
        scene = wrapup.owe("scene", "staged scene", owner="unit:v7")
        setting = wrapup.owe("setting", "forced setting", owner="unit:v7", extra={"key": "debug_settings:x"})
    finally:
        os.environ["RM_GAME_INSTANCE"] = "a"
    debts = [wrapup._read_json(wrapup._p("debts", tok + ".json")) for tok in (scene, setting)]
    check(all(d.get("game") == "b" for d in debts), "V7 owe stamps the process game's letter on settings and scenes")
    ctx = wrapup.unit_ctx("v7", "BENCH", None)
    rec = wrapup.run(Fake(), ctx)
    rows = [r for r in rec["rows"] if r["kind"] == "debt"]
    check(len(rows) == 2 and all(r.get("game") == "b" for r in rows), "V7 filed rows keep the debt's game")
    reset()


def t_only_the_debts_game_can_void_it():
    a_log = os.path.join(TMP, "Player-prev.log")
    b_log = os.path.join(os.environ["RM_INSTANCES_ROOT"], "b", "Player.log.prev")
    os.makedirs(os.path.dirname(b_log))
    open(a_log, "w").close()
    os.utime(a_log, (launch, launch))
    os.environ["RM_WRAPUP_PREV_LOG"] = a_log
    try:
        named = put_debt(old, "pid:1")
        path = wrapup._p("debts", named + ".json")
        wrapup.amend(named, {"game": "b"})
        filed = {"kind": "debt", "act": "filed", "token": "filed-b", "game": "b", "at": wrapup._iso(old)}
        wrapup._write_json(wrapup._p("open", "unit-v8.json"), {"rows": [filed]})
        check(standing_tokens(wrapup.World(), now) == sorted([named, "filed-b"]),
              "V8 an unreadable ArchSmall log leaves its aged debt and filed row standing after ArchBig relaunched")
        wrapup.sweep()
        check(os.path.isfile(path) and os.path.isfile(wrapup._p("open", "unit-v8.json")),
              "V8 sweep leaves ArchSmall's debts when only ArchBig relaunched")
        os.mkdir(b_log)
        os.utime(b_log, (launch, launch))
        check(standing_tokens(wrapup.World(), now) == sorted([named, "filed-b"]),
              "V8 a directory at ArchSmall's log path cannot void a debt")
        os.rmdir(b_log)
        reset()
        put_debt(old, "pid:1")
        wrapup.amend(named, {"game": "b"})
        wrapup._write_json(wrapup._p("open", "unit-v8.json"), {"rows": [filed]})
        os.utime(a_log, (old - 60, old - 60))
        open(b_log, "w").close()
        os.utime(b_log, (launch, launch))
        legacy = put_debt(old, "pid:2")
        wrapup.sweep()
        check(standing_tokens(wrapup.World(), now) == [legacy] and not os.path.isfile(path),
              "V8 ArchSmall's own relaunch voids its debts and leaves legacy ArchBig debts standing")
    finally:
        os.environ["RM_WRAPUP_PREV_LOG"] = ""
        reset()

    steve_log = os.path.join(TMP, "sjlewis", "Player-prev.log")
    os.makedirs(os.path.dirname(steve_log))
    open(steve_log, "w").close()
    os.utime(steve_log, (launch, launch))
    fallback = os.path.join(TMP, "missing-default", "Player-prev.log")
    with patch.dict(os.environ, RM_HOST="stevedesktop", RM_GAME_INSTANCE="Steve1",
                    RM_GAME_LOGDIR=os.path.dirname(steve_log)), \
         patch.multiple(wrapup, PREV_LOG_WSL=fallback, PREV_LOG_WIN=fallback):
        os.environ.pop("RM_WRAPUP_PREV_LOG")
        os.environ.pop("RM_GAME_A_LOGDIR", None)
        tok = put_debt(old, "pid:0")
        wrapup.amend(tok, {"game": "a", "plan": [
            wrapup._door().step("jawa/difficulty_tune", threatScale=1.0)]})
        runner = Mock(side_effect=OSError("fixture runner"))
        code, line = wrapup.restore_at_release(runner=runner, game="a")
        check(code is None and "no planned setting debt" in line and not runner.called,
              "V8 Steve1 release skips restore after its own relaunch: %s" % line)
        write = Mock(return_value={"success": True})
        out = wrapup.restore(write)
        check(not write.called and out["void"] == 1,
              "V8 restore sends no Steve1 write for a debt from its exited process")
        check(out["swept"] == [1, 0] and not os.path.isfile(wrapup._p("debts", tok + ".json")),
              "V8 sweep clears Steve1's prelaunch debt")
    reset()


def main():
    t_debts_keep_the_games_letter()
    t_only_the_debts_game_can_void_it()
    print("selftest_wrapup_void_relaunch: %s (%d fail)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
