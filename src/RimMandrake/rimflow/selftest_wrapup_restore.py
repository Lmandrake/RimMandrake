#!/usr/bin/env python3
"""selftest_wrapup_restore.py — WRAPUP_SETTINGS_DEBT_RESTORE_TIDY_ELF: settings debts that outlived their owners are
paid by `wrapup.py restore` (wrapup.restore), and SettingsTransaction no longer leaks an unpayable debt.

  R1  plans: the door's key + orig -> the exact write (debug_settings, difficulty_tune, mod_settings_field with a
      dotted type name); a door debt written before plans derives one; a legacy SettingsTransaction debt (prose undo)
      gets its exact pre-run difficulty back and a CHECK that the debug value it forced is gone
  R2  SettingsTransaction killed mid-run: its debt carries a plan for every value it forced (pre-run values), the
      wild-spawner cleanup as a step; a cleanup with no step is named `unplanned`
  R3  restore() on a fake game: every owed setting written back and read back, its debt paid; a FILED one (the
      wrap-up ran first) too, and sweep then resolves the open record (the row stops standing)
  R4  a write the game does not keep: failed, the debt stays owed; one debt's failure never stops the rest
  R5  legacy debt: its difficulty is written back, its check passes once the door's exact debt (replayed first, even
      when its token sorts earlier) has put the debug field back; a field still forced fails and stays owed
  R6  a debt with an unplanned cleanup is replayed but left owed, named; a debt with no plan is left, named
  R7  a void debt (owed to an exited game) is never replayed
  R8  probe(): the live proof's logic on a fake game -> 0 restored and paid; no such field -> 2 UNMEASURED
  R10 the CLI: `wrapup.py restore` prints its tally and exits 1 on a failed restore, 0 on a clean one, 2 with no bridge
  R11 restore's writes through the bridge door pay what they put back and never owe the reverse change
  R12 a debt whose owner process is still running is in flight, never replayed (left, named); its owner restores it
      at teardown. RIMMANDRAKE_HOLD_WRAPUP_RESTORE_OFF_A_LIVE_OWNERS_DEBT: on 2026-11-23 a `wrapup.py restore` replayed
      sc_garden's converterRateMultiplier 4.1 -> 1 mid-window on ArchBig and its filter row read half rate (14 batches
      of 32). The real World reads the owner's pid: this process is alive, a pid that never ran is not.
"""
import glob
import io
import os
import shutil
import sys
import tempfile
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils", "modcheck"))

TMP = tempfile.mkdtemp(prefix="selftest_wrapup_restore_")
os.environ["RM_WRAPUP_DIR"] = os.path.join(TMP, "state")
os.environ["RM_WRAPUP_PREV_LOG"] = ""               # the real game's relaunch never voids a test debt

import wrapup  # noqa: E402
import wrapup_debt as D  # noqa: E402
import helpers as HL  # noqa: E402

FAILS = []


def check(ok, what):
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


class World(wrapup.World):
    def __init__(self, relaunched=None):
        self.relaunched = relaunched

    def game_a_hold(self):
        return None

    def release_bridge(self, clone, holder):
        return True, "fake"

    def doing_claims(self, seat, since, session=None):
        return []

    def game_relaunched(self, game="a"):
        return self.relaunched

    def owner_alive(self, debt):
        return debt.get("owner") in getattr(self, "live", ())


class Game(object):
    """The bridge's settings tools in their reply shapes (JawaBench*.cs): set -> valueBefore/valueAfter,
    difficulty_tune -> before/after, wild_spawner_block -> blocked. `stuck` fields ignore writes."""

    def __init__(self):
        self.dbg = {"enableStoryteller": True, "logRaidInfo": False, "enableRandomDiseases": True}
        self.diff = {"threatScale": 1.0, "allowBigThreats": True}
        self.mod = {("RimMandrake.Pits.PitSettings", "shovelRequired"): True}
        self.blocked = False
        self.stuck = set()
        self.calls = []

    def call(self, tool, params=None):
        q = dict(params or {})
        self.calls.append((tool, q))
        if tool == "jawa/debug_settings":
            if q.get("action") == "set":
                before = self.dbg[q["field"]]
                if q["field"] not in self.stuck:
                    self.dbg[q["field"]] = q["value"]
                return {"success": True, "valueBefore": before, "valueAfter": self.dbg[q["field"]]}
            return {"success": True, "fields": [{"name": k, "value": v} for k, v in self.dbg.items()]}
        if tool == "jawa/difficulty_tune":
            before = dict(self.diff)
            for k, v in q.items():
                if k not in self.stuck:
                    self.diff[k] = v
            return {"success": True, "before": before, "after": dict(self.diff)}
        if tool == "jawa/mod_settings_field":
            k = (q["typeName"], q["field"])
            before = self.mod[k]
            if q.get("action") == "set" and q["field"] not in self.stuck:
                self.mod[k] = q["value"]
            return {"success": True, "valueBefore": before, "valueAfter": self.mod[k]}
        if tool == "jawa/wild_spawner_block":
            if q.get("action") == "block":
                self.blocked = True
            elif q.get("action") == "release" and "blocked" not in self.stuck:
                self.blocked = False
            return {"success": True, "blocked": self.blocked}
        return {"success": True}


class Session(object):
    """modcheck's session shape: call(tool, **kw)."""

    def __init__(self, game):
        self.game = game

    def call(self, tool, **kw):
        return self.game.call(tool, kw)


def reset():
    shutil.rmtree(os.environ["RM_WRAPUP_DIR"], ignore_errors=True)


def owed():
    return sorted(os.path.basename(f)[:-5] for f in glob.glob(wrapup._p("debts", "*.json"))
                  + glob.glob(wrapup._p("debts", "filed", "*.json")))


def legacy(field="enableStoryteller", forced="False", diff="{'threatScale': 1.0, 'allowBigThreats': True}"):
    return {"what": "SettingsTransaction forced debug %s=%s" % (field, forced),
            "undo": "set it back to its pre-run value (debug_settings / difficulty_tune; difficulty was %s)" % diff}


def main():
    # R1 plans
    check(D.key_plan("debug_settings:enableStoryteller", True)
          == [{"tool": "jawa/debug_settings", "params": {"action": "set", "field": "enableStoryteller", "value": True}}],
          "R1 a debug key's plan is the exact write back")
    check(D.key_plan("difficulty_tune:threatScale", 1.0)
          == [{"tool": "jawa/difficulty_tune", "params": {"threatScale": 1.0}}], "R1 a difficulty key's plan")
    p = D.key_plan("mod_settings_field:RimMandrake.Pits.PitSettings.shovelRequired", "True")
    check(p == [{"tool": "jawa/mod_settings_field", "params": {"typeName": "RimMandrake.Pits.PitSettings",
                                                                "action": "set", "field": "shovelRequired",
                                                                "value": "True"}}],
          "R1 a mod field's plan splits the dotted type name from the field: %r" % p)
    check(D.key_plan("debug_settings:x", None) == [] and D.key_plan("nonsense", 1) == [],
          "R1 no orig or no kind: no plan")
    check(D.plan_of({"key": "debug_settings:logRaidInfo", "orig": False})[0]["params"]["value"] is False,
          "R1 a door debt written before plans derives its plan from key + orig")
    lp = D.plan_of(legacy())
    check(lp == [{"tool": "jawa/difficulty_tune", "params": {"threatScale": 1.0, "allowBigThreats": True}},
                 {"tool": "jawa/debug_settings", "params": {"action": "list"},
                  "not": {"field": "enableStoryteller", "value": False}}],
          "R1 a legacy SettingsTransaction debt: exact difficulty + a check on the forced debug field: %r" % lp)
    check(D.plan_of(legacy(diff="{}")) == [D.check_not("enableStoryteller", False)],
          "R1 a legacy debt with no readable difficulty is a check only")
    check(D.plan_of({"what": "scene staged", "undo": "remove it"}) == [], "R1 an unrecognised debt has no plan")

    # R2 SettingsTransaction killed mid-run
    reset()
    g = Game()
    tx = HL.SettingsTransaction(Session(g)).__enter__()
    HL.storyteller_off(Session(g), tx)
    tx.set_debug("logRaidInfo", True)
    r, _ = HL._try_call(Session(g), "jawa/wild_spawner_block", action="block")
    tx.on_restore("wild_spawner_block", lambda: True,
                  step=D.step("jawa/wild_spawner_block", expect={"blocked": False}, action="release"))
    d = wrapup._read_json(wrapup._p("debts", tx.debt + ".json"))         # killed here: restore() never runs
    plan = d.get("plan") or []
    check([st["tool"] for st in plan] == ["jawa/wild_spawner_block", "jawa/debug_settings", "jawa/debug_settings",
                                          "jawa/difficulty_tune"],
          "R2 the killed transaction's debt carries a plan, cleanup first: %r" % [st["tool"] for st in plan])
    check(plan[1]["params"] == {"action": "set", "field": "enableStoryteller", "value": True}
          and plan[2]["params"]["value"] is False
          and plan[3]["params"] == {"threatScale": 1.0, "allowBigThreats": True},
          "R2 every value in the plan is the PRE-run one")
    check(d.get("unplanned") == [], "R2 every cleanup has a step: nothing unplanned")
    import inspect
    src = inspect.getsource(HL.quiet_world)
    check("step=wrapup_debt.step(\"jawa/wild_spawner_block\"" in src,
          "R2 quiet_world registers its wild-spawner cleanup WITH a replay step")

    # R3 restore on the game it left forced: everything back, debt paid; then filed by a wrap-up first
    out = wrapup.restore(g.call, World())
    check(out["restored"] == [tx.debt] and not out["failed"] and not out["left"],
          "R3 restore replays the killed transaction's plan: %r" % (out,))
    check(g.dbg == {"enableStoryteller": True, "logRaidInfo": False, "enableRandomDiseases": True}
          and g.diff == {"threatScale": 1.0, "allowBigThreats": True} and g.blocked is False,
          "R3 the game reads every pre-run value back: %r %r %r" % (g.dbg, g.diff, g.blocked))
    check(owed() == [], "R3 the debt is paid")

    reset()
    g = Game()
    tx = HL.SettingsTransaction(Session(g)).__enter__()
    HL.storyteller_off(Session(g), tx)
    tok = tx.debt
    rec = wrapup.run(World(), {"kind": "unit", "key": "killedproof", "seat": "BENCH", "owner": wrapup.owner_key(),
                               "holder": "RELENTLESS", "clones": [], "since": 0, "carried": False})
    rows = [x for x in rec["rows"] if x["kind"] == "debt"]
    check(len(rows) == 1 and rows[0].get("plan") is True and owed() == [tok]
          and os.path.exists(wrapup._p("debts", "filed", tok + ".json")),
          "R3 the wrap-up files a planned debt and keeps it findable (debts/filed/): %r" % rows)
    check(len(glob.glob(wrapup._p("open", "*.json"))) == 1, "R3 one open record stands")
    out = wrapup.restore(g.call, World())
    check(out["restored"] == [tok] and owed() == [] and g.dbg["enableStoryteller"] is True
          and g.diff["threatScale"] == 1.0, "R3 the filed debt is restored and paid: %r" % (out,))
    check(out["swept"][0] == 1 and glob.glob(wrapup._p("open", "*.json")) == []
          and len(glob.glob(wrapup._p("resolved", "*.json"))) == 1,
          "R3 sweep then resolves the open record: %r" % (out["swept"],))

    # R4 a write the game does not keep
    reset()
    g = Game()
    g.dbg["enableStoryteller"] = False
    g.diff["threatScale"] = 0.0
    a = wrapup.owe("setting", "debug_settings:enableStoryteller=False (was True)", "x",
                   extra={"key": "debug_settings:enableStoryteller", "orig": True})
    b = wrapup.owe("setting", "difficulty_tune:threatScale=0 (was 1)", "x",
                   extra={"key": "difficulty_tune:threatScale", "orig": 1.0})
    g.stuck.add("enableStoryteller")
    out = wrapup.restore(g.call, World())
    check([t for t, _ in out["failed"]] == [a] and out["restored"] == [b],
          "R4 the stuck write fails, the other is still restored: %r" % (out,))
    check(owed() == [a] and "read back" in out["failed"][0][1], "R4 the failed debt stays owed, with why")
    g2 = Game()
    g2.call = lambda tool, params=None: (_ for _ in ()).throw(ConnectionError("bridge dropped"))
    out = wrapup.restore(g2.call, World())
    check([t for t, _ in out["failed"]] == [a] and "ConnectionError" in out["failed"][0][1],
          "R4 a raising call is a failure, not a crash")

    # R5 legacy debts: the door's exact debt runs first, then the legacy check
    reset()
    g = Game()
    g.dbg["enableStoryteller"] = False
    g.diff.update(threatScale=0.0, allowBigThreats=False)
    door = wrapup.owe("setting", "debug_settings:enableStoryteller=False (was True)", "x",
                      extra={"key": "debug_settings:enableStoryteller", "orig": True})
    old = wrapup.owe("setting", legacy()["what"], legacy()["undo"])
    # force the legacy token to sort AFTER the door's, so newest-first alone would ask its check first
    os.rename(wrapup._p("debts", old + ".json"), wrapup._p("debts", "29991231T000000-legacy00.json"))
    body = wrapup._read_json(wrapup._p("debts", "29991231T000000-legacy00.json"))
    body["token"] = old = "29991231T000000-legacy00"
    wrapup._write_json(wrapup._p("debts", old + ".json"), body)
    out = wrapup.restore(g.call, World())
    check(sorted(out["restored"]) == sorted([door, old]) and owed() == [],
          "R5 the door debt and the legacy debt are both restored and paid: %r" % (out,))
    check(g.dbg["enableStoryteller"] is True and g.diff == {"threatScale": 1.0, "allowBigThreats": True},
          "R5 the legacy debt's exact difficulty is written back")
    reset()
    g = Game()
    g.dbg["enableStoryteller"] = False
    old = wrapup.owe("setting", legacy()["what"], legacy()["undo"])
    out = wrapup.restore(g.call, World())
    check([t for t, _ in out["failed"]] == [old] and "still reads the forced" in out["failed"][0][1]
          and owed() == [old], "R5 a legacy debt whose field is still forced fails and stays owed: %r" % (out,))

    # R6 unplanned cleanup; no plan at all
    reset()
    g = Game()
    tx = HL.SettingsTransaction(Session(g)).__enter__()
    tx.set_debug("logRaidInfo", True)
    tx.on_restore("mystery", lambda: True)
    tok = tx.debt
    plain = wrapup.owe("setting", "something forced by hand", "ask the owner")
    out = wrapup.restore(g.call, World())
    left = dict(out["left"])
    check(g.dbg["logRaidInfo"] is False and tok in left and "mystery" in left[tok] and tok in [
        os.path.basename(f)[:-5] for f in glob.glob(wrapup._p("debts", "*.json"))],
          "R6 an unplanned cleanup: values replayed, debt left owed and named: %r" % (out["left"],))
    check(plain in left and "no restore plan" in left[plain], "R6 a debt with no plan is left, named")

    # R7 void debt
    reset()
    g = Game()
    g.dbg["enableStoryteller"] = False
    wrapup.owe("setting", "debug_settings:enableStoryteller=False (was True)", "x",
               extra={"key": "debug_settings:enableStoryteller", "orig": True})
    import time
    out = wrapup.restore(g.call, World(relaunched=time.time() + 3 * 3600))
    check(out["void"] == 1 and not out["restored"] and not [c for c in g.calls if c[1].get("action") == "set"],
          "R7 a debt owed to an exited game is never replayed: %r" % (out,))

    # R12 a live owner's debt is in flight: restore leaves it, names it, writes nothing; a dead owner's is replayed
    reset()
    g = Game()
    g.dbg["enableStoryteller"] = False
    live = wrapup.owe("setting", "debug_settings:enableStoryteller=False (was True)", "x", owner="pid:4242",
                      extra={"key": "debug_settings:enableStoryteller", "orig": True})
    w = World()
    w.live = ("pid:4242",)
    out = wrapup.restore(g.call, w)
    left = dict(out["left"])
    check(not out["restored"] and live in left and "in flight" in left[live] and owed() == [live]
          and not [c for c in g.calls if c[1].get("action") == "set"] and g.dbg["enableStoryteller"] is False,
          "R12 a debt whose owner still runs is never replayed, left in flight: %r" % (out,))
    w.live = ()
    out = wrapup.restore(g.call, w)
    check(out["restored"] == [live] and g.dbg["enableStoryteller"] is True and owed() == [],
          "R12 once its owner has ended the same debt is replayed and paid: %r" % (out,))
    real = wrapup.World()
    check(real.owner_alive({"owner": "pid:%d" % os.getpid(), "at": "2000-01-01T00:00:00Z"}) is False
          and real.owner_alive({"owner": "pid:%d" % os.getpid(), "at": wrapup._iso(wrapup._now())}) is True,
          "R12 the real World reads this live process as alive, and not as the owner of a debt older than it (pid reuse)")
    check(real.owner_alive({"owner": "pid:999999999", "at": wrapup._iso(wrapup._now())}) is False
          and real.owner_alive({"owner": "unit:rm-x", "at": wrapup._iso(wrapup._now())}) is None,
          "R12 a pid that never ran is not alive; a unit owner is unread (None: replayed as before)")

    # R8 probe
    reset()
    g = Game()
    code, line = wrapup.probe(g.call, World())
    check(code == 0 and g.dbg["logRaidInfo"] is False and owed() == [], "R8 probe -> 0 on a game that restores: %s"
          % line)
    g = Game()
    del g.dbg["logRaidInfo"]
    code, line = wrapup.probe(g.call, World())
    check(code == 2 and line.startswith("UNMEASURED"), "R8 probe -> 2 UNMEASURED with no field: %s" % line)

    # R11 restore's own writes go through the door (RimBridge.call -> settings_write): they pay, never owe the reverse
    reset()
    g = Game()
    g.diff.update(threatScale=0.0, allowBigThreats=False)      # forced, and the door's exact debts already gone
    g.dbg["enableStoryteller"] = True

    def door(tool, params=None):
        out = g.call(tool, params)
        D.settings_write(tool, params, out)
        return out
    old = wrapup.owe("setting", legacy()["what"], legacy()["undo"])
    out = wrapup.restore(door, World())
    check(out["restored"] == [old] and owed() == [] and g.diff["threatScale"] == 1.0 and D.RESTORING[0] == 0,
          "R11 a legacy write through the door owes no reverse debt: %r, owed %r" % (out, owed()))
    door("jawa/difficulty_tune", {"threatScale": 0.5})
    check(len(owed()) == 1, "R11 after restore the door owes again (the guard is released)")

    # R10 CLI
    reset()
    g = Game()
    g.dbg["enableStoryteller"] = False
    wrapup.owe("setting", "x", "x", extra={"key": "debug_settings:enableStoryteller", "orig": True})

    class RB(object):
        call = staticmethod(g.call)

        def close(self):
            pass

    real = wrapup._bridge_call
    try:
        wrapup._bridge_call = lambda: RB()
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = wrapup.main(["restore"])
        check(code == 0 and "1 restored, 0 failed" in buf.getvalue(), "R10 CLI clean restore -> 0: %r"
              % buf.getvalue())
        g.dbg["enableStoryteller"] = False
        g.stuck.add("enableStoryteller")
        wrapup.owe("setting", "x", "x", extra={"key": "debug_settings:enableStoryteller", "orig": True})
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = wrapup.main(["restore"])
        check(code == 1 and "1 failed" in buf.getvalue(), "R10 CLI failed restore -> 1")

        def nobridge():
            raise RuntimeError("no bridge token found")
        wrapup._bridge_call = nobridge
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = wrapup.main(["restore"])
        check(code == 2 and buf.getvalue().startswith("UNMEASURED"), "R10 CLI with no bridge -> 2 UNMEASURED")
    finally:
        wrapup._bridge_call = real

    shutil.rmtree(TMP, ignore_errors=True)
    print("selftest_wrapup_restore: %s (%d failed)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
