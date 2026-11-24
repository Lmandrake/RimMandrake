#!/usr/bin/env python3
"""scene - the scene library: ten names on which a live test of a mod is written. Read `scene.py help` first.

    python3   scene.py help [<name>]             the contract page of a name (no game)
    python3   scene.py judge <run_dir> [--rejudge] judge a kept call (no game)
    python.exe scene.py accept <script.py>       run a committed script: clean tree, commit hash on each receipt, no keyboard
    python.exe scene.py explore <game> [--map M] an interactive prompt on an open session; each run is EXPLORED
    python.exe scene.py end-session <game>       end the session of a driver that died (until scene.attach is built)
    python3   scene.py tools <words>             find a bridge tool (no game)
    python3   scene.py raw-census                every s.raw call in the committed scenes, a proposal for a reviewer

A script: `import scene; from scene import cond as c`. Pages: scene_contracts/. Promises, limits and what is not promised:
design/specs/2026-11-23-scene-library/boundary.md. Exit of a command: 0 done, 1 the script stopped, 2 could not look, 3 refused."""
import ast
import difflib
import inspect
import json
import os
import re
import sys
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import scene_cond as cond  # noqa: E402
import scene_hands as hands  # noqa: E402
from scene_core import (CallFailed, Fault, NotBuilt, Receipt, Refused, Reply, ReplyLost, RunResult, Value, text)  # noqa: E402,F401

VERSION = "0.2.0"
PAGES = os.path.join(HERE, "scene_contracts")
NAMES = ("contract", "open", "stage", "run", "act", "read", "judge", "shot", "attach", "raw")
BUILT = ("open", "run", "judge", "raw")
CONVERT = "RIMMANDRAKE_CONVERT_THREE_SCENES_SHOW_IF_TEN_NAMES_HELP"
OWED = {"attach": "RIMMANDRAKE_HARDEN_RUN_LIFE_CYCLE_KILL_CANCEL_THROWN_TICK"}
GAME_STATE = "RM_SCENE_STATE"           # the text in the game process: {"pid", "stamps", "session"}
EXPLORED = "EXPLORED"
SPEEDS = ("Normal", "Fast", "Superfast", "Ultrafast")
CALM_PROFILES = ("standard",)
CALM_MINUTES = 240                      # the calm tool's own longest lease (design/specs/2026-11-23-calm-map/boundary.md)
# budget: danger=a run whose clock stands still never ends (a window that pauses the game); ends no work: the silence bound of a
# budget: progress guard: a clock that moves starts it again
STALL_S = 60.0                          # boundary.md LIMITS
# budget: danger=a load that never settles holds the scene and its game; never reached in the 14 days to 2026-11-24; no record
# budget: of its run
SETTLE_S = 600.0
CLOSE_RECORD_S = 20.0
CLOSE_SESSION_S = 60.0                  # the companion's writer drain limit (bridge-v2-hands/boundary.md)
POLL_S = 0.3
LIFE_CYCLE = re.compile(r"(?:^rimworld/(?:load_game|load_game_ready|start_debug_game|start_debug_game_ready|go_to_main_menu)$)|^jawa/session$|"
                        r"quit|shutdown|restart|set_mods|mod_list_set|enable_mod|disable_mod|modsconfig")
OLD_LAYERS = {"validation_core", "helpers", "quiet_site", "scenelib", "scenes", "rimbridge_client", "modcheck", "clockgate", "rimdrive",
              "load_session", "scene_runner", "scene_world"}
PHASES = ("lock", "identify", "load", "settle", "calm", "arm")

WORLD = None                            # scene_world.RealWorld(), made on first use; a test puts its fake here
LAUNCH = {"mode": "script", "commit": None, "script": None}     # scene.py accept / explore set this


def _world():
    global WORLD
    if WORLD is None:
        import scene_world
        WORLD = scene_world.RealWorld()
    return WORLD


def __getattr__(name):
    if name in ("contract", "attach"):
        raise _not_built(name)
    raise AttributeError("module 'scene' has no attribute %r; the ten names: %s" % (name, ", ".join(NAMES)))


def _not_built(name):
    return NotBuilt("NOT_BUILT", "%s is not built yet: %s builds it. Built today: %s. Until then `s.raw` reaches each tool, and the "
                    "run is EXPLORED" % (name, OWED.get(name, CONVERT), ", ".join(BUILT)))


# ------------------------------------------------------------------------------------------------- open
class PhaseReport(list):
    """Six phases, each {phase, state: done | refused | not reached, did: [], put_back: []}."""

    def __repr__(self):
        return "\n".join("%-9s %-11s %s%s" % (p["phase"], p["state"], "; ".join(p["did"]) or "nothing changed",
                                              " | put back: " + "; ".join(p["put_back"]) if p["put_back"] else "") for p in self)


def _game_key(game):
    sys.path.append(os.path.join(HERE, "..", "rimflow"))
    import game_names
    try:
        key = game_names.name_key(game) or game_names.key(game)
    except game_names.GameNameError:
        key = None
    if key is None or game_names.show_key(key) not in [n for n, _k, _m, _l in game_names.GAMES]:
        raise Refused("UNKNOWN_GAME", "no game %r; the four names: %s" % (game, game_names.known()))
    name = game_names.show_key(key)
    try:
        return name, key, game_names.letter(key)
    except game_names.GameNameError:
        raise Refused("GAME_HELD", "%s is driven from its own machine, through its test lane (infrastructure/stevedesktop/RUNBOOK.md); "
                      "from here use ArchSmall" % name)


def open(game, contract=None, needs=None):  # noqa: A001 - the name of the contract page
    """Take one game, check its build, load the map, arm the recorders (scene_contracts/open.md)."""
    W = _world()
    name, key, letter = _game_key(game)
    needs = dict(needs or {})
    odd = sorted(set(needs) - {"mods", "map", "calm"})
    if odd:
        raise Refused("BAD_ARGS", "needs takes mods, map and calm, not %s" % ", ".join(odd))
    if needs.get("calm") not in (None,) + CALM_PROFILES:
        raise Refused("BAD_ARGS", "no calm profile %r; the profiles: %s" % (needs["calm"], ", ".join(CALM_PROFILES)))
    where = needs.get("map")
    if where is not None and not isinstance(where, str):
        raise Refused("BAD_ARGS", "needs['map'] is a fixture save by name or 'fresh:<kind>', not %r" % (where,))
    if where and not where.startswith("fresh:"):
        names, starts = W.canonical()
        low = where.lower()
        if low in [n.lower() for n in names] or any(low.startswith(x.lower()) for x in starts):
            raise Refused("CANONICAL_SAVE", "%s is a canonical world save (infrastructure/state/CANONICAL_SAVE.md); name a fixture, or "
                          "fresh:quicktest" % where)
    try:
        wanted = W.wanted(needs["mods"]) if needs.get("mods") else []
    except KeyError as e:
        raise Refused("BAD_ARGS", "needs['mods']: %s" % (e.args[0],))
    s = Session(W, name, key, letter, contract)
    report = PhaseReport({"phase": p, "state": "not reached", "did": [], "put_back": []} for p in PHASES)
    s.opened = report
    rec = s._receipt("scene.open")
    at = 0
    try:
        for at, step in enumerate((s._lock, lambda p: s._identify(p, wanted, where, rec), lambda p: s._load(p, where, rec),
                                   lambda p: s._settle(p, where), lambda p: s._calm(p, needs.get("calm"), rec), lambda p: s._arm(p, contract, rec))):
            step(report[at])
            report[at]["state"] = "done"
    except BaseException as e:
        report[at]["state"] = "refused"
        for phase, line in s._put_back():
            next(p for p in report if p["phase"] == phase)["put_back"].append(line)
        s.closed = True
        if isinstance(e, (Refused, Fault)):
            e.report = report
            e.args = ("%s\n%r" % (e, report),)
        raise
    s.receipt = s._finish(rec, did=["%s: %s" % (p["phase"], d) for p in report for d in p["did"]])
    return s


# ------------------------------------------------------------------------------------------------- the session
class State(object):
    def __init__(self, **kw):
        self.__dict__.update(kw)

    def __repr__(self):
        return ", ".join("%s=%r" % i for i in sorted(self.__dict__.items()))


class Session(object):
    def __init__(self, W, name, key, letter, contract=None):
        self.W, self.game, self.key, self.letter, self.contract = W, name, key, letter, contract
        self.id = "scn_" + uuid.uuid4().hex[:12]
        self.bridge, self.closed, self.opened, self.receipt = None, False, None, None
        self.build, self.pid, self.stamps, self.hand = None, None, [], None
        self._locked = self._calmed = self._recorded = self._insession = False
        self._tools, self._hands, self._run, self._dir, self._loaded = {}, {}, None, None, None
        self._tick = None

    # ---- the bridge
    def _call(self, tool, **args):
        self._hands[tool] = self._hands.get(tool, 0) + 1
        return self.bridge.call(tool, args)

    def _look(self, tool, **args):
        """A call whose failure means that we could not look."""
        try:
            r = self._call(tool, **args)
        except (CallFailed, ReplyLost) as e:
            raise Fault("COULD_NOT_LOOK", detail="%s: %s" % (tool, e))
        return r

    def _get_state(self):
        """The text in the game process. -> dict. Another process's text (a child inherited it) reads as none."""
        r = self._look("jawa/static_call", type="System.Environment", method="GetEnvironmentVariable", args=GAME_STATE)
        if r.get("success") is not True:
            raise Fault("COULD_NOT_LOOK", detail="the process mark could not be read (a campaign game refuses jawa/static_call): %s" % str(r.get("message") or r))
        if r.get("result") in (None, "null", ""):
            return {"pid": self.pid, "stamps": [], "session": None}
        try:
            d = json.loads(r["result"])
            d["stamps"], d["session"], d["pid"]
        except (ValueError, KeyError, TypeError):
            raise Fault("COULD_NOT_LOOK", detail="the process mark is not readable text: %r" % (r["result"],))
        return d if d["pid"] == self.pid else {"pid": self.pid, "stamps": [], "session": None}

    def _set_state(self, d):
        want = json.dumps(d, sort_keys=True).replace("|", "/")      # '|' parts the arguments of jawa/static_call
        self._look("jawa/static_call", type="System.Environment", method="SetEnvironmentVariable", args="%s|%s" % (GAME_STATE, want))
        got = self._get_state()
        if got != json.loads(want):
            raise Fault("MARK_NOT_HELD", detail="the game did not keep the process mark: wrote %s, read %s" % (want, got))

    def _status(self):
        st = self._look("rimbridge/get_bridge_status").get("state")
        if not isinstance(st, dict) or "paused" not in st:
            raise Fault("COULD_NOT_LOOK", detail="the bridge status has no state: %r" % (st,))
        if st.get("tick") is not None:
            self._tick = st["tick"]
        return st

    # ---- receipts
    def _receipt(self, name, request=None):
        self._hands = {}
        rec = Receipt(name, request or name.split(".")[-1] + "_" + uuid.uuid4().hex[:10], commit=LAUNCH["commit"] or "none: not started by scene.py accept")
        rec.game = {"name": self.game, "session": self.id, "tick_before": self._tick, "tick_after": None}
        return rec

    def _begin(self, name, request=None):
        """The first reading of each name on an open session: is this still our process and our session, and how is it marked."""
        if self.closed:
            raise Refused("SESSION_CLOSED", "this session has ended; open a session")
        rec = self._receipt(name, request)
        d = self._get_state()
        if (d["session"] or {}).get("id") != self.id:
            raise Fault("SESSION_LOST", detail="the game process holds session %r, not %s: the game was restarted, or another driver ended this session" % (
                (d["session"] or {}).get("id"), self.id))
        self.stamps = d["stamps"]
        rec.game["tick_before"] = self._status().get("tick")
        return rec

    def _finish(self, rec, did=()):
        rec.did += list(did)
        rec.build = self.build
        rec.hands = dict(self._hands)
        rec.game["tick_after"] = self._tick
        rec.stamps = sorted(set(self.stamps) | ({EXPLORED} if LAUNCH["mode"] == "explore" else set()))
        self.W.save(os.path.join(self.run_dir, "receipts.jsonl"), json.dumps(rec.as_dict(), sort_keys=True, default=str) + "\n", append=True)
        return rec

    @property
    def run_dir(self):
        if self._dir is None:
            self._dir = self.W.run_dir("%s_%s" % (os.path.splitext(os.path.basename(LAUNCH["script"] or LAUNCH["mode"]))[0], self.game))
            self.W.save(os.path.join(self._dir, "run.json"), json.dumps({
                "session": self.id, "game": self.game, "mode": LAUNCH["mode"], "commit": LAUNCH["commit"], "script": LAUNCH["script"],
                "contract": getattr(self.contract, "hash", None), "library": VERSION}, indent=1, sort_keys=True))
        return self._dir

    # ---- the six phases of open
    def _require_game_health(self):
        from game_watcher import BROKEN
        r = self.W.game_health(self.letter)
        if r.state in BROKEN:
            raise Refused("GAME_BROKEN", "%s: %s (%s). The Conductor must clear the broken game before a run." %
                          (self.game, r.state, r.detail))
        if r.state == "process_gone":
            raise Refused("NO_GAME", "%s: %s. Start the game before opening a scene." % (self.game, r.detail))
        if r.state == "could_not_look":
            return ["%s game watcher: %s" % (self.game, r.detail)]
        return []

    def _lock(self, p):
        r = self.W.lock_take(self.letter, "scene.open %s (%s)" % (self.id, LAUNCH["script"] or LAUNCH["mode"]))
        if r["code"] == 75:
            raise Refused("GAME_HELD", "%s; use a free game (game_lock.py query all)" % r["line"])
        if r["code"] == 3:
            raise Refused("OWNER_HOLD", "%s; use ArchSmall, or SteveDesktop through its lane" % r["line"])
        if r["code"] != 0:
            raise Fault("COULD_NOT_LOOK", detail="the driver lock of %s could not be read: %s" % (self.game, r["line"]))
        self._locked = not r.get("inherited")
        p["did"].append("took the driver lock of %s" % self.game if self._locked else "drives under a take that was there: %s" % r["line"])

    def _identify(self, p, wanted, where, rec):
        rec.could_not_look += self._require_game_health()
        self.bridge = self.W.connect(self.letter)
        try:
            descriptors = self.bridge.tools()
        except (CallFailed, ReplyLost) as e:
            raise Fault("COULD_NOT_LOOK", detail="the bridge's tool list: %s" % e)
        self._tools = {t["name"]: t for t in descriptors if isinstance(t, dict) and t.get("name")}
        if not self._tools:
            raise Fault("COULD_NOT_LOOK", detail="the bridge listed no tool: its companion did not load")
        r = self._look("jawa/running_mods", details=False, assembly="", loadedOf="ours")
        ld, ids = r.get("loaded"), r.get("packageIds")
        if r.get("success") is not True or not isinstance(ld, dict) or not isinstance(ids, list) or not ids:
            raise Fault("COULD_NOT_LOOK", detail="the game did not say what it has loaded (a companion older than the receipt): %s" % str(r))
        if ld.get("gameKey") != self.key:
            raise Fault("WRONG_GAME", detail="the bridge of %s answers for %s" % (self.game, ld.get("gameKey")))
        self.pid = ld.get("pid")
        comp = ld.get("companion") or {}
        self.build = {
            "list": ld.get("listFingerprint"), "mods": len(ids), "version": ld.get("gameVersion"), "pid": self.pid,
            "dlls": {a.get("name"): {"mvid": a.get("mvid"), "sha256": a.get("fileSha256"), "file_holds_loaded": a.get("fileHoldsLoadedCode")}
                     for m in ld.get("mods") or [] for a in m.get("assemblies") or []},
            "companion": {"mvid": comp.get("mvid"), "source_hash": comp.get("srcHash"), "version": comp.get("version")}}
        src = self.W.companion_hash()
        if src is None or not comp.get("srcHash"):
            rec.could_not_look.append("whether the companion is the source at this commit: a hash could not be read")
        else:
            self.build["companion"]["is_source_at_this_commit"] = src == comp["srcHash"]
        low = [str(i).lower().replace("_steam", "") for i in ids]
        absent = [(n, pid) for n, pid, _part, _d in wanted if pid not in low]
        if absent:
            raise Refused("MOD_NOT_LOADED", "not in the loaded list of %s: %s. Set the list with the game down (python3 "
                          "src/RimMandrake/Utils/modlist_swap.py --enable %s --apply, in that game's environment: game_instance.py env %s), then "
                          "./game --why \"load %s\" down, then up" % (self.game, ", ".join(n for n, _p in absent), " ".join(n for n, _p in absent),
                                                                    self.game, absent[0][0]))
        for n, pid, part, dlls in wanted:
            if dlls is None:
                rec.could_not_look.append("%s: its source folder has no readable DLL list, so its loaded code was not compared" % n)
                continue
            if not dlls:
                rec.could_not_look.append("%s ships no DLL: its loaded code cannot be identified" % n)
                continue
            j = self.W.judge_loaded(r, pid, dlls, self.key, part)
            if j["verdict"] in ("WRONG_BUILD", "NOT_LOADED", "FOREIGN_COPY"):
                raise Refused("WRONG_BUILD", "%s: %s. Deploy it and restart the game: python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod %s "
                              "--instance %s --apply" % (n, "; ".join(str(w) for w in j["why"]), n, self.game))
            if j["verdict"] == "NO_ASSEMBLY":
                rec.could_not_look.append("%s ships no DLL: its loaded code cannot be identified" % n)
            elif j["verdict"] != "MATCH":
                raise Fault("COULD_NOT_LOOK", detail="the loaded build of %s: %s %s" % (n, j["verdict"], j["why"]))
        d = self._get_state()
        self.stamps = d["stamps"]
        open_s = d["session"]
        if open_s is None and hands.SESSION in self._tools:
            st = self._look(hands.SESSION, action="state")
            if st.get("stage") in ("open", "closing"):
                open_s = {"id": st.get("session"), "driver": None, "text": st.get("driver")}
        if open_s is not None:
            alive = self.W.alive(open_s.get("driver")) if open_s.get("driver") else None
            raise Refused("SESSION_OPEN", "session %s is open on %s; its driver %s. scene.attach(%r) takes it over (not built yet); until then, when its "
                          "driver is dead: python.exe src/RimMandrake/Utils/scene.py end-session %s" % (
                              open_s.get("id"), self.game, {True: "is alive: wait for it, or stop that process", False: "is dead",
                                                            None: "could not be inspected"}[alive], self.game, self.game))
        if where and not where.startswith("fresh:") and not self._has_save(where):
            raise Refused("FIXTURE_MISSING", "%s is not on %s (looked in %s). Copy it there from the game that holds it: cp '<Saves folder of "
                          "that game>/%s.rws' '%s'" % (where, self.game, self._saves, where, self._saves))
        if where and where.startswith("fresh:") and where != "fresh:quicktest":
            raise Refused("FIXTURE_MISSING", "the library makes fresh:quicktest only, not %s; name a fixture save for another map" % where)

    def _has_save(self, name):
        at, self._saves = 0, None
        while True:
            r = self._look("rimworld/list_saves", offset=at)
            if r.get("success") is not True or not isinstance(r.get("saves"), list):
                raise Fault("COULD_NOT_LOOK", detail="the saves of the game could not be listed: %s" % str(r))
            self._saves = r.get("saveFolder")
            if any(str(x.get("name")).lower() == name.lower() for x in r["saves"]):
                return True
            at2 = (r.get("page") or {}).get("nextOffset")
            if not at2 or at2 <= at:
                return False
            at = at2

    def _load(self, p, where, rec):
        if where is None:
            p["did"].append("nothing: no map was asked for")
            rec.could_not_look.append("the map was not loaded by this session: its state is whatever was there")
            return
        fresh = where.startswith("fresh:")
        if fresh and self._status().get("programState") != "Entry":
            self._menu(p)
        tool, args = ("rimworld/start_debug_game_ready", {}) if fresh else ("rimworld/load_game_ready", {"saveName": where})
        # budget: danger=a load that never answers holds the scene and its game; never reached in the 14 days to 2026-11-24; no
        # budget: record of its run
        args.update(timeoutMs=280000, readiness="mapData", pauseIfNeeded=True)
        try:
            r = self._call(tool, **args)
        except (CallFailed, ReplyLost) as e:
            raise Fault("LOAD_FAILED", done=["asked for %s; whether the game loaded it is not known" % where], detail=str(e))
        if r.get("success") is not True:
            raise Fault("LOAD_FAILED", done=["asked for %s" % where], detail=str(r.get("message") or r.get("error") or r))
        self._loaded = where
        p["did"].append("loaded %s (the game's earlier map is gone)" % where)
        if not fresh:
            rec.could_not_look.append("whether %s was saved in a marked process: a save does not carry the mark yet" % where)

    def _menu(self, p):
        """A fresh map is started from the main menu only (measured 2026-11-23: from a map the start timed out after 280 s)."""
        r = self._look("rimworld/go_to_main_menu")
        if r.get("success") is not True:
            raise Fault("LOAD_FAILED", detail="the game did not go to the main menu: %s" % str(r.get("message") or r))
        self._loaded = "the main menu"
        p["did"].append("left the loaded map for the main menu")
        end = self.W.clock() + SETTLE_S
        while True:
            try:
                st = self._status()
            except Fault as e:                      # the bridge may not answer while the scene changes
                st = {"unread": e.detail}
            if st.get("programState") == "Entry" and not st.get("longEventPending"):
                return
            if self.W.clock() > end:
                raise Fault("LOAD_NOT_SETTLED", done=list(p["did"]), detail="%.0f s and the main menu is not there: %s" % (SETTLE_S, st))
            self.W.sleep(POLL_S)

    def _settle(self, p, where):
        """Playing, a current map, no long event, paused, and the same tick on three reads."""
        end, same, last, st = self.W.clock() + SETTLE_S, 0, None, {}
        while same < 3:
            try:
                st = self._status()
            except Fault as e:
                st = {"unread": e.detail}
            ready = st.get("automationReady") is True and not st.get("longEventPending") and st.get("programState") == "Playing"
            if ready and st.get("paused") is not True:
                self._look("rimworld/pause_game", pause=True)
                if "paused the game" not in p["did"]:
                    p["did"].append("paused the game")
                ready = False
            same = same + 1 if ready and st.get("tick") == last else (1 if ready else 0)
            last = st.get("tick") if ready else None
            if self.W.clock() > end:
                raise Fault("LOAD_NOT_SETTLED", done=list(p["did"]), detail="%.0f s and the game is not ready, paused and still: %s%s" % (
                    SETTLE_S, {k: st.get(k) for k in ("programState", "automationReady", "longEventPending", "paused", "tick", "unread")},
                    "" if where else "; no map was asked for: name one (needs={'map': 'fresh:quicktest'})"))
            if same < 3:
                if not where and st.get("programState") == "Entry":
                    raise Fault("NO_MAP", detail="the game stands at the menu and no map was asked for: needs={'map': 'fresh:quicktest'}")
                self.W.sleep(POLL_S)

    def _calm(self, p, profile, rec):
        if profile is None:
            p["did"].append("nothing: no calm profile was asked for")
            return
        self._calmed = True                     # owed from before the call: a lost reply may have set it
        r = self._look("jawa/quiet_site", action="calm", clear=True, minutes=CALM_MINUTES)
        if r.get("success") is not True:
            raise Fault("NOT_CALM", detail="the calm tool refused: %s" % str(r.get("message") or r))
        p["did"] += ["calm: %s" % x for x in r.get("repaired") or []]
        for c in r.get("controls") or []:
            if c.get("status") == "COULD_NOT_READ":
                rec.could_not_look.append("calm control %s: %s" % (c.get("name"), c.get("detail")))
        rec.could_not_look += ["calm does not cover: %s" % x for x in r.get("notCovered") or []]
        if r.get("verdict") != "CALM":
            raise Fault("NOT_CALM", done=list(p["did"]), detail="%s: %s" % (r.get("verdict"), [
                (c.get("name"), c.get("detail"), c.get("things")) for c in r.get("controls") or [] if c.get("status") in ("NOT_CALM", "COULD_NOT_READ")]))

    def _arm(self, p, contract, rec):
        d = self._get_state()
        self.stamps = d["stamps"]
        d["session"] = {"id": self.id, "driver": self.W.me(), "script": LAUNCH["script"] or LAUNCH["mode"], "calm": self._calmed}
        self._recorded = True
        self._set_state(d)
        p["did"].append("wrote the session record in the game process")
        if hands.RUN_UNTIL in self._tools and hands.SESSION in self._tools:
            r = self._look(hands.SESSION, action="open", driver=self.id)
            if r.get("success") is not True:
                raise Fault(r.get("refused") or "SESSION_NOT_OPENED", done=list(p["did"]), detail=str(r.get("message") or r))
            self._insession = True
            p["did"].append("opened the game's session %s" % r.get("session"))
            self.hand = hands.RunUntil(self._call, self.id)
        elif hands.SLICE in self._tools:
            self.hand = hands.Slice(self._call)
        self._mark_record("scene session %s opened" % self.id, rec)
        if contract is None:
            rec.could_not_look.append("no contract was given, so no recorder was armed for one")
        rec.could_not_look.append("the standard cast taps (spawn, death, damage) are not built (RIMMANDRAKE_BUILD_WORLD_EVENT_TAPS_SECOND_FAMILY), so none was armed")

    def _mark_record(self, why, rec=None):
        """A line in the game's own record. Best effort: what could not be written is said."""
        try:
            r = self._call("jawa/telemetry_mark", why=why)
            bad = None if r.get("success") is True else str(r.get("error") or r.get("message") or r)
        except (CallFailed, ReplyLost) as e:
            bad = str(e)
        if bad and rec is not None:
            rec.could_not_look.append("the game's record has no line for %r: %s" % (why[:60], bad))
        return bad is None

    # ---- the end
    def _put_back(self):
        """-> [(phase, line)], each thing that open changed, in reverse order. Never raises."""
        out = []

        def step(phase, fn):
            try:
                out.append((phase, fn()))
            except (Fault, Refused, CallFailed, ReplyLost, OSError) as e:
                out.append((phase, "NOT PUT BACK: %s: %s" % (type(e).__name__, str(e).split("\n")[0])))

        def end_session():
            self._insession = False
            r = self._look(hands.SESSION, action="close", driver=self.id)
            if r.get("success") is not True:
                raise Fault(r.get("refused") or "SESSION_NOT_CLOSED", detail=str(r.get("message") or r))
            session = r.get("session")
            end = self.W.clock() + CLOSE_SESSION_S
            while r.get("stage") == "closing" and self.W.clock() < end:
                self.W.sleep(POLL_S)
                r = self._look(hands.SESSION, action="state")
                if r.get("success") is not True or r.get("session") != session:
                    raise Fault("SESSION_NOT_CLOSED", detail="could not confirm the close of session %s: %s" % (session, str(r)))
            if r.get("stage") not in ("closed", "aborted"):
                raise Fault("SESSION_NOT_CLOSED", detail="session %s still reports stage %s" % (session, r.get("stage")))
            return "closed the game's session"

        def forget():
            d = self._get_state()
            self._recorded = False
            if (d["session"] or {}).get("id") != self.id:
                return "the session record was already gone"
            d["session"] = None
            self._set_state(d)
            return "cleared the session record"

        def uncalm():
            self._calmed = False
            r = self._look("jawa/quiet_site", action="release")
            if r.get("success") is not True:
                raise Fault("CALM_NOT_RELEASED", detail=str(r.get("message") or r))
            return "released the calm: %s" % "; ".join(str(x) for x in r.get("restored") or [])

        def unlock():
            self._locked = False
            line = self.W.lock_release(self.letter)
            if not line.startswith(("released", "already free")):
                raise Fault("LOCK_NOT_RELEASED", detail=line)
            return "driver lock: %s" % line
        if self._insession:
            step("arm", end_session)
        if self._recorded:
            step("arm", forget)
        if self._calmed:
            step("calm", uncalm)
        if self._loaded:
            out.append(("load", "NOT PUT BACK: the map that was there before %s was replaced" % self._loaded))
        if self.bridge is not None:
            try:
                self.bridge.close()
            except OSError as e:
                out.append(("identify", "the socket did not close: %s" % e))
        if self._locked:
            step("lock", unlock)
        return out

    def close(self):
        """End the session: the run, the record, the calm and the lock. The game stays paused."""
        if self.closed:
            return
        self.closed = True
        rec = self._receipt("close")
        try:
            live = self.hand.live() if self.hand else None
            if live:
                self.hand.cancel(live)
                rec.did.append("cancelled the live run %s" % live)
            if self._status().get("paused") is not True:
                self._look("rimworld/pause_game", pause=True)
                rec.did.append("paused the game")
        except (Fault, Refused, CallFailed, ReplyLost) as e:
            rec.could_not_look.append("the last run and the pause: %s" % str(e).split("\n")[0])
        self._mark_record("scene session %s closed" % self.id, rec)
        lines = [ln for _ph, ln in self._put_back() if "the map that was there before" not in ln]
        self._finish(rec, did=lines)
        self.closed_report = rec
        bad = [x for x in lines if x.startswith("NOT PUT BACK")]
        if bad:
            raise Fault("CLOSE_INCOMPLETE", done=[x for x in lines if x not in bad], detail="; ".join(bad))

    def __enter__(self):
        return self

    def __exit__(self, et, ev, tb):
        try:
            self.close()
        except Fault as e:
            if et is None:
                raise
            sys.stderr.write("scene: the session did not close cleanly: %s\n" % e)   # the first error is the one that is raised
        return False

    # ---- what is not built
    def __getattr__(self, name):
        if name in ("stage", "act", "read", "read_many", "shot"):
            raise _not_built("s." + name)
        raise AttributeError("a session has no %r; built: s.run, s.raw, s.state, s.cancel_run, s.close, s.run_dir" % name)

    # ---- state
    @property
    def state(self):
        rec = self._begin("s.state")
        st = self._status()
        out = State(paused=st.get("paused"), tick=st.get("tick"), last_run=self._run, open_act=None, stamps=list(self.stamps),
                    trace=self._run and self._run.get("trace"), live_run=self.hand.live() if self.hand else None)
        out.receipt = self._finish(rec)
        return out

    def cancel_run(self):
        rec = self._begin("s.cancel_run")
        live = self.hand.live() if self.hand else None
        if live:
            self.hand.cancel(live)
        self._finish(rec, did=["cancelled run %s" % live] if live else [])
        return bool(live)

    # ---- run
    def run(self, until, limit=None, speed="Normal", record=None):
        """Let the game play to an exact tick, and record values on every tick (scene_contracts/run.md)."""
        if self.closed:
            raise Refused("SESSION_CLOSED", "this session has ended; open a session")
        if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
            raise Refused("NO_LIMIT", "limit=%r: give the most ticks the run may play" % (limit,))
        if speed not in SPEEDS:
            raise Refused("BAD_ARGS", "speed=%r; the speeds: %s" % (speed, ", ".join(SPEEDS)))
        tracks = []
        for t in record or []:
            if not isinstance(t, cond.Track):
                raise Refused("BAD_ARGS", "record takes c.track(of, path), not %r" % (t,))
            why = cond.bad_path(t.of, t.path)
            if why:
                raise Refused("BAD_PATH", "%s (`help read`)" % why)
            tracks.append(t)
        tree, ticks = cond.compile_until(until)
        health_notes = self._require_game_health()
        rec = self._begin("s.run")
        rec.could_not_look += health_notes
        if self.hand is None:
            raise Fault("NO_HAND", detail="the game has neither %s nor %s" % (hands.RUN_UNTIL, hands.SLICE))
        try:
            return self._play(rec, tree, ticks, tracks, limit, speed)
        except Fault as e:
            e.receipt = self._finish(rec, did=e.done)
            raise

    def _play(self, rec, tree, ticks, tracks, limit, speed):
        live = self.hand.live()
        if live:
            raise Refused("RUN_ACTIVE", "run %s has not ended; read s.state.live_run, then s.cancel_run()" % live)
        st = self._status()
        if st.get("paused") is not True:
            raise Refused("GAME_RUNNING", "the game is not paused; s.run ends paused, so something else unpaused it: read s.state")
        start = st.get("tick")
        if ticks is not None:
            if start is None:
                raise Fault("COULD_NOT_LOOK", detail="the game's tick could not be read")
            tree = cond.to_tree(cond.game.tick >= start + ticks)
        plan = self.hand.plan(tree, tracks)
        names = [self.hand.name(cond.probe_name(p)) for p, _o in cond.walk(tree) if p["p"] not in (cond.TICK, "value.state")]
        request = rec.entry["request"]
        row, lost = self._start(request, plan, limit, speed)
        row, stalled = self._wait(request, row)
        self._run = dict(row)
        rows = self._trace(row)
        for r in rows:
            if r.get("rec") == "track":
                r["name"] = self.hand.name(r["name"])
        path = os.path.join(self.run_dir, "trace_%s.jsonl" % request)
        self.W.save(path, "".join(json.dumps(r, sort_keys=True) + "\n" for r in rows))
        self._run["trace"] = path
        bad = hands.trace_fault(rows)
        did = ["the run was played to tick %s" % row.get("tick")]
        if bad:
            raise Fault("TRACE_INCOMPLETE", done=did, detail=bad, request=request, trace=path)
        over = hands.ran_on(rows)
        after = self._status()
        t2 = next(r for r in rows if r["rec"] == "end")["tick"]
        if over is None and after.get("paused") is not True:
            over = ("PAUSE_REFUSED", "read a second time, the game is not paused")
        if over is None and after.get("tick") != t2:
            over = ("RAN_PAST_END", "read a second time, the game stands on tick %s; the run ended on %s" % (after.get("tick"), t2))
        if over:
            raise Fault(over[0], done=did, detail=over[1], request=request, trace=path)
        blind = hands.unreadable(rows)
        for n, (state, first, n_ticks, d) in sorted(blind.items()):
            rec.could_not_look.append("%s was %s on %d tick(s), first on %s (%s)" % (n, state, n_ticks, first, d or "no detail"))
        why, detail = row["why"] or "fault", row.get("detail")
        if stalled:
            why, detail = "fault", "the clock stood still for %.0f s, so the run was cancelled (a window that pauses the game?)" % STALL_S
        elif why in ("hit", "limit", "unknown"):
            free = {self.hand.name(n) for n in cond.excused(tree)}
            unread = [n for n in names if n in blind and n not in free]
            if unread:
                n = unread[0]
                detail = "%s was %s from tick %s%s" % (n, blind[n][0], blind[n][1], "" if why == "unknown" else
                                                       "; the hand went on and said %r on tick %s" % (why, t2))
                why = "unknown"
            elif row.get("unknown") and why == "unknown":
                detail = text(row["unknown"])
        faults = hands.other_faults(rows)
        if faults:
            rec.could_not_look.append("the trace holds fault records: %s" % "; ".join(faults))
        rec.could_not_look += self.hand.note()
        if lost:
            rec.could_not_look.append("the reply to the start was lost; the run was found by its request")
        t1 = row.get("tickFrom") if row.get("tickFrom") is not None else start
        values = {n: Value(n, v[0], v[1], v[3], v[2]) for n, v in hands.last_values(rows).items()}
        values[cond.TICK] = Value(cond.TICK, "ok", t2, t2)
        res = RunResult(request, why, int(t1) if t1 is not None else None, t2, values, path, detail)
        self._run.update(why=why)
        res.receipt = self._finish(rec, did=["played ticks %s to %s at speed %s; paused on %s" % (res.tick_from, t2, speed, t2)])
        return res

    def _start(self, request, plan, limit, speed):
        """-> (the run, was the reply lost). A lost reply is looked up by the request; the run is never started twice."""
        try:
            return self.hand.start(request, plan, limit, speed), False
        except CallFailed as e:
            raise Fault("RUN_NOT_STARTED", detail=str(e), request=request)
        except ReplyLost as e:
            why, reconcile = str(e), e.reconcile
        row = self._ask(request)
        if row is None:
            raise Fault("REPLY_LOST", done=["the start of the run was sent"], detail="%s; the game knows no run of this request" % why, request=request)
        if reconcile is not None:
            try:
                reconcile("found run %s for scene request %s" % (row["run"], request))
            except OSError as e:
                raise Fault("COULD_NOT_LOOK", done=["found run %s" % row["run"]],
                            detail="the start marker could not be reconciled: %s" % e, request=request) from e
        return row, True

    def _ask(self, request):
        """The run of this request, over lost replies. -> row, or None (the game says it has no such run)."""
        end = self.W.clock() + STALL_S
        while True:
            try:
                return self.hand.find(request)
            except (ReplyLost, CallFailed) as e:
                last = str(e)
            if self.W.clock() > end:
                raise Fault("REPLY_LOST", done=["the run may be playing"], detail="the status of the run could not be read for %.0f s: %s" % (STALL_S, last), request=request)
            self.W.sleep(1.0)

    def _wait(self, request, row):
        """-> (the closed run, did its clock stand still)."""
        seen, at, stalled = (row.get("tick"), row.get("rows")), self.W.clock(), False
        while row.get("stage") != "closed":
            self.W.sleep(POLL_S)
            row = self._ask(request) or row
            now = (row.get("tick"), row.get("rows"))
            if now != seen:
                seen, at = now, self.W.clock()
            elif self.W.clock() - at > STALL_S:
                if stalled:
                    raise Fault("RUN_NOT_ENDED", done=["the run was cancelled and did not close"], detail="stage %s" % row.get("stage"), request=request)
                stalled, at = True, self.W.clock()
                self.hand.cancel(request)
        return row, stalled

    def _trace(self, row):
        end = self.W.clock() + CLOSE_RECORD_S
        folder, writer = row.get("recordDir"), row.get("writer")
        if not folder and self._insession:
            st = self._look(hands.SESSION, action="state", driver=self.id)
            folder, writer = st.get("recordDir"), st.get("writerSession")
        while True:
            rows = self.W.read_trace(folder, writer, row.get("run"))
            if any(r.get("rec") == "close" for r in rows) or self.W.clock() > end:
                return rows or [{"rec": "none", "n": 0}]
            self.W.sleep(POLL_S)

    # ---- raw
    def raw(self, tool, /, **args):
        """Call any bridge tool by name while you explore (scene_contracts/raw.md)."""
        if self.closed:
            raise Refused("SESSION_CLOSED", "this session has ended; open a session")
        if LIFE_CYCLE.search(tool):
            raise Refused("LIFE_CYCLE_TOOL", "%s would end or replace the session; close the session first (s.act.reload is not built)" % tool)
        d = self._tools.get(tool)
        if d is None:
            raise Refused("UNKNOWN_TOOL", "no tool %r; the nearest: %s; or scene.tools(words)" % (
                tool, ", ".join(difflib.get_close_matches(tool, self._tools, 5, 0.4)) or "none"))
        why = _bad_args(d, args)
        if why:
            raise Refused("BAD_ARGS", "%s: %s. Its schema: %s" % (tool, why, json.dumps(d.get("parameters") or d.get("inputSchema"), default=str)))
        rec = self._begin("s.raw")
        changing = not _read_only(d)
        if changing and EXPLORED not in self.stamps:
            st = self._get_state()
            st["stamps"] = sorted(set(st["stamps"]) | {EXPLORED})
            self._set_state(st)                 # before the call: a call that dies half way has marked the process
            self.stamps = st["stamps"]
        self._mark_record("scene raw %s %s" % (tool, json.dumps(args, sort_keys=True, default=str)), rec)
        rec.did = ["raw call of %s; the library does not know what it changed" % tool] if changing else []
        rec.could_not_look.append("the effect of a raw call is not read back")
        try:
            r = self._call(tool, **args)
        except CallFailed as e:
            self._finish(rec)
            raise Fault("RAW_FAILED", done=["the mark %s was set" % EXPLORED] if changing else [], detail=str(e))
        except ReplyLost as e:
            rec.could_not_look.append("the reply was lost: whether the call was done is not known")
            self._finish(rec)
            raise Fault("REPLY_LOST", done=list(rec.did), detail=str(e))
        out = Reply(r)
        self._status()
        out.receipt = self._finish(rec)
        return out


def _read_only(descriptor):
    """Only the C# declaration says so: a description that begins with READ ONLY. jawa/static_call never."""
    if descriptor.get("name") == "jawa/static_call":
        return False
    return bool(re.match(r"READ[ -]ONLY\b", str(descriptor.get("description") or ""), re.I))


def _bad_args(descriptor, args):
    """Why these arguments do not fit the live schema, or None."""
    sch = descriptor.get("inputSchema")
    params = descriptor.get("parameters")
    if isinstance(params, list):
        known = {p.get("name"): p for p in params}
        required = [p.get("name") for p in params if p.get("required")]
    elif isinstance(sch, dict) and isinstance(sch.get("properties"), dict):
        known, required = sch["properties"], list(sch.get("required") or [])
    else:
        return "the bridge gives no schema for it, so the arguments could not be checked" if args else None
    odd = sorted(set(args) - set(known))
    missing = sorted(set(required) - set(args))
    return "; ".join((["it does not take %s" % ", ".join(odd)] if odd else []) + (["it needs %s" % ", ".join(missing)] if missing else [])) or None


# ------------------------------------------------------------------------------------------------- tools (no session)
class Tool(object):
    def __init__(self, name, what, read_only):
        self.name, self.what, self.read_only = name, what, read_only

    def __repr__(self):
        return "%-36s %-11s %s" % (self.name, "read-only" if self.read_only else "changing", self.what)


_DECL = re.compile(r'\[Tool\(\s*"([a-z_]+/[a-z0-9_]+)"\s*,\s*Description\s*=\s*((?:"(?:[^"\\]|\\.)*"\s*\+?\s*)+)', re.S)


def _catalogue():
    """-> {tool: description} from the committed schema record and the C# declarations. An unreadable record is a Fault."""
    try:
        with _file(os.path.join(HERE, "northstar_driver", "tool_schemas.json"), encoding="utf-8") as f:
            out = {n: "" for n in json.load(f)["tools"]}
    except (OSError, ValueError, KeyError) as e:
        raise Fault("COULD_NOT_LOOK", detail="the schema record: %s" % e)
    top = os.path.join(HERE, "..", "bridgetools", "JawaBench.BridgeTools")
    for n in sorted(os.listdir(top)) if os.path.isdir(top) else []:
        if n.endswith(".cs"):
            with _file(os.path.join(top, n), encoding="utf-8", errors="replace") as f:
                for m in _DECL.finditer(f.read()):
                    out[m.group(1)] = "".join(re.findall(r'"((?:[^"\\]|\\.)*)"', m.group(2)))
    return out


def tools(words):
    """At most ten bridge tools that match the words, one line each (scene_contracts/raw.md). [] means looked and found none."""
    want = [w for w in re.findall(r"[a-z0-9]+", str(words).lower())]
    scored = []
    for n, d in _catalogue().items():
        hay_n, hay_d = n.lower(), d.lower()
        score = sum(5 * (w in hay_n) + (w in hay_d) for w in want)
        if want and all(w in hay_n or w in hay_d for w in want):
            scored.append((-score, n, d))
    return [Tool(n, (d.split(". ")[0] or "(no description in the repo)")[:150], _read_only({"name": n, "description": d})) for _s, n, d in sorted(scored)[:10]]  # cut-ok: short tool listing from the full description


# ------------------------------------------------------------------------------------------------- help
def page(name):
    """-> the text of a help page, or None when there is none of that name."""
    name = re.sub(r"^(?:scene|s)\.", "", name)
    if name == "cond":
        return (cond.__doc__ or "").strip() + "\n\nThe probes: " + ", ".join(sorted(cond.conds.PROBES) + list(cond.VALUE_PROBES))
    if name == "verbs":
        return "s.act and its verbs are not built yet (%s); the page: help act" % CONVERT
    f = os.path.join(PAGES, "README.md" if name in ("", "readme") else name + ".md")
    if name and name not in NAMES and name != "readme":
        return None
    with _file(f, encoding="utf-8") as fh:
        return fh.read()


def signature(name):
    """-> the argument names that a built name takes (its own self left out)."""
    fn = {"open": open, "run": Session.run, "judge": judge, "raw": Session.raw, "tools": tools}[name]
    return [p for p in inspect.signature(fn).parameters if p != "self"]


def page_arguments(name, text_=None):
    """-> {function: [argument names]} that the page's Accepts table gives (raw.md's table has one row for each call)."""
    t = text_ if text_ is not None else page(name)
    sec = t.split("## Accepts", 1)[1].split("\n## ", 1)[0]
    out = {name: []}
    for ln in sec.splitlines():
        m = re.match(r"\|\s*`([^`]+)`\s*\|", ln)
        if not m:
            continue
        cell = m.group(1)
        call = re.match(r"(?:s|scene)\.(\w+)\((.*)\)$", cell)
        if call:
            out[call.group(1)] = [a.strip().lstrip("*") for a in call.group(2).split(",") if a.strip()]
        else:
            base = re.match(r"\w+", cell).group(0)
            if base not in out[name]:
                out[name].append(base)
    return out


# ------------------------------------------------------------------------------------------------- accept, explore
def old_imports(path, repo):
    """-> [(file, module)] of each older layer that a script imports, itself or through a module of the repo beside it."""
    out, seen, todo = [], set(), [os.path.abspath(path)]
    while todo:
        f = todo.pop()
        if f in seen:
            continue
        seen.add(f)
        with _file(f, encoding="utf-8") as fh:
            tree = ast.parse(fh.read(), f)
        mods = set()
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                mods.update(a.name for a in n.names)
            elif isinstance(n, ast.ImportFrom):
                mods.add(n.module or "")
                mods.update((n.module + "." if n.module else "") + a.name for a in n.names)
            elif isinstance(n, ast.Call) and n.args and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str):
                fn = n.func.attr if isinstance(n.func, ast.Attribute) else getattr(n.func, "id", "")
                if fn in ("import_module", "__import__", "run_path", "spec_from_file_location"):
                    mods.add(n.args[0].value.replace("\\", "/").rsplit("/", 1)[-1].replace(".py", ""))
        for m in sorted(x for x in mods if x):
            parts = m.split(".")
            if parts[0] in ("scene", "scene_cond", "scene_core"):
                continue
            own = parts[0] == "helpers" and os.path.isfile(os.path.join(os.path.dirname(f), "helpers.py")) and \
                os.path.basename(os.path.dirname(f)) != "modcheck"
            if set(parts) & OLD_LAYERS and not own:
                out.append((f, m))
                continue
            for base in (os.path.dirname(f), HERE):
                cand = os.path.join(base, *parts) + ".py"
                if os.path.isfile(cand) and os.path.abspath(cand).startswith(os.path.abspath(repo)):
                    todo.append(os.path.abspath(cand))
                    break
    return out


def check_accept(script, repo, git):
    """-> the commit hash. Refuses TREE_NOT_CLEAN, SCRIPT_NOT_IN_REPO, IMPORTS_OLD_LAYER; nothing is run."""
    full = os.path.abspath(script)
    if not os.path.isfile(full):
        raise Refused("SCRIPT_NOT_IN_REPO", "no file %s" % full)
    rel = os.path.relpath(full, repo).replace("\\", "/") if os.path.splitdrive(full)[0].lower() == os.path.splitdrive(repo)[0].lower() else ".."
    if rel.startswith(".."):
        raise Refused("SCRIPT_NOT_IN_REPO", "%s is outside %s: a run that counts has one commit" % (full, repo))
    rc, out = git("ls-files", "--error-unmatch", "--", rel)
    if rc != 0:
        rc2, out2 = git("rev-parse", "--is-inside-work-tree")
        if rc2 != 0:
            raise Fault("COULD_NOT_LOOK", detail="git could not read the tree: %s" % out2.strip())
        raise Refused("SCRIPT_NOT_IN_REPO", "%s is not committed: commit it, then accept" % rel)
    rc, out = git("status", "--porcelain")
    if rc != 0:
        raise Fault("COULD_NOT_LOOK", detail="git status: %s" % out.strip())
    if out.strip():
        rows = out.strip("\n").split("\n")
        raise Refused("TREE_NOT_CLEAN", "%d path(s) differ from the commit: %s%s. Commit or remove them, then accept" % (
            len(rows), "; ".join(r.strip() for r in rows[:5]), " ..." if len(rows) > 5 else ""))
    old = old_imports(full, repo)
    if old:
        raise Refused("IMPORTS_OLD_LAYER", "; ".join("%s imports %s" % (os.path.relpath(f, repo), m) for f, m in old) +
                      ". A scene imports scene only; a scene of a mod that already passed keeps its old script and is not accepted again")
    rc, out = git("rev-parse", "HEAD")
    if rc != 0 or not out.strip():
        raise Fault("COULD_NOT_LOOK", detail="git rev-parse HEAD: %s" % out.strip())
    return out.strip()


def _judge_module():
    folder = os.path.join(HERE, "..", "rimflow")
    if folder not in sys.path:
        sys.path.insert(0, folder)
    import scene_judge
    return scene_judge


def judge(run_dir, rejudge=False):
    """Read a kept run from disk and return its verdict."""
    return _judge_module().judge(run_dir, rejudge)


def accept(script):
    """Run a committed script as an acceptance run. -> exit code."""
    import runpy
    import scene_world
    W = _world()
    repo = getattr(W, "repo", None) or scene_world.REPO
    commit = check_accept(script, repo, W.git)
    LAUNCH.update(mode="accept", commit=commit, script=os.path.relpath(os.path.abspath(script), repo).replace("\\", "/"))
    old_in, sys.stdin = sys.stdin, _file(os.devnull)
    print("ACCEPT %s at %s" % (LAUNCH["script"], commit[:12]), flush=True)
    try:
        runpy.run_path(script, run_name="__main__")
        word, rc = "the script ended", 0
    except SystemExit as e:
        rc = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
        word = "the script ended with exit %s" % rc
    except Fault as e:
        word, rc = "FAULT %s" % e, 2 if e.name == "COULD_NOT_LOOK" else 1
    except Refused as e:
        word, rc = "REFUSED %s" % e, 3
    finally:
        sys.stdin.close()
        sys.stdin = old_in
    _rc, after = W.git("rev-parse", "HEAD")
    _rc2, dirty = W.git("status", "--porcelain")
    if after.strip() != commit or dirty.strip():
        word, rc = word + "; THE TREE CHANGED DURING THE RUN, so the run has no identity", max(rc, 1)
    print("ACCEPT %s: %s. For a kept run, use scene.py judge." % (LAUNCH["script"], word), flush=True)
    return rc


def explore(game, where=None):
    """An interactive prompt on an open session. Each run is EXPLORED."""
    import code
    LAUNCH.update(mode="explore", commit=None, script=None)
    with open(game, needs={"map": where} if where else None) as s:
        print(s.opened)
        code.interact(banner="s is the open session on %s; c is scene.cond. Each run here is EXPLORED and counts for no bar." % game,
                      local={"s": s, "scene": sys.modules[__name__], "c": cond}, exitmsg="")
    return 0


def end_session(game):
    """End the session of a driver that is dead: its record, the game's session and its calm. Nothing else is changed."""
    W = _world()
    name, key, letter = _game_key(game)
    s = Session(W, name, key, letter)
    lock = {"did": []}
    s._lock(lock)
    try:
        s.bridge = W.connect(letter)
        s._tools = {t["name"]: t for t in s.bridge.tools()}
        s.pid = (s._look("jawa/running_mods", details=False, assembly="", loadedOf="ours").get("loaded") or {}).get("pid")
        if s.pid is None:
            raise Fault("COULD_NOT_LOOK", detail="the game's process id")
        d = s._get_state()
        rec = d["session"]
        if rec is None:
            print("%s: no session is open" % name)
            return 0
        alive = W.alive(rec.get("driver"))
        if alive is not False:
            raise Refused("DRIVER_ALIVE", "the driver of %s %s: %s" % (rec.get("id"), "is alive" if alive else "could not be inspected", rec.get("driver")))
        did = []
        if hands.SESSION in s._tools:
            r = s._look(hands.SESSION, action="abort", driver=rec.get("id"))
            did.append("the game's session: %s" % ("aborted" if r.get("success") is True else r.get("refused") or r.get("message")))
        if rec.get("calm"):
            r = s._look("jawa/quiet_site", action="release")
            did.append("calm: %s" % ("released" if r.get("success") is True else "NOT RELEASED %s" % r.get("message")))
        d["session"] = None
        s._set_state(d)
        print("%s: ended session %s (%s); %s; the map is as the dead driver left it" % (name, rec.get("id"), rec.get("script"), "; ".join(did) or "nothing else was owed"))
        return 0
    finally:
        if s.bridge is not None:
            s.bridge.close()
        if s._locked:
            print("driver lock: %s" % W.lock_release(letter))


def raw_census(files=None):
    """-> {typed operation: set of files}: every literal s.raw call in the given (default: committed) scenes."""
    if files is None:
        rc, out = _world().git("ls-files", "*.py")
        if rc != 0:
            raise Fault("COULD_NOT_LOOK", detail="git ls-files: %s" % out)
        import scene_world
        files = [os.path.join(scene_world.REPO, f) for f in out.split("\n") if f]
    ops, looked, blind = {}, 0, []
    for f in files:
        if os.path.basename(f).startswith(("selftest_scene", "scene")):
            continue
        try:
            with _file(f, encoding="utf-8", errors="replace") as fh:
                src = fh.read()
            if not re.search(r"^\s*(?:import|from)\s+scene\b", src, re.M):
                continue
            tree = ast.parse(src)
        except (OSError, SyntaxError, ValueError) as e:
            blind.append("%s: %s" % (f, e))
            continue
        looked += 1
        for n in ast.walk(tree):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "raw" and n.args:
                kw = {k.arg: k.value.value for k in n.keywords if isinstance(k.value, ast.Constant)}
                name = n.args[0].value if isinstance(n.args[0], ast.Constant) else "(a name that is not a literal)"
                if name == "jawa/static_call":
                    name += " %s.%s" % (kw.get("type", "?"), kw.get("method", "?"))
                ops.setdefault(name, set()).add(f)
    return ops, looked, blind


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    verb, rest = argv[0], argv[1:]
    try:
        if verb == "help":
            t = page(rest[0] if rest else "")
            if t is None:
                print("no page %r; the pages: %s, cond, verbs" % (rest[0], ", ".join(NAMES)))
                return 3
            print(t)
            return 0
        if verb == "tools":
            got = tools(" ".join(rest))
            print("\n".join(map(repr, got)) if got else "looked: no tool matches %r" % " ".join(rest))
            return 0
        if verb == "accept" and len(rest) == 1:
            return accept(rest[0])
        if verb == "judge":
            return _judge_module().main(rest)
        if verb == "explore" and rest:
            return explore(rest[0], rest[2] if rest[1:2] == ["--map"] and len(rest) > 2 else None)
        if verb == "end-session" and len(rest) == 1:
            return end_session(rest[0])
        if verb == "raw-census":
            ops, looked, blind = raw_census()
            print("%d committed scene(s) on the library were read; %d file(s) could not be read%s" % (looked, len(blind), ": " + "; ".join(blind) if blind else ""))
            for op, fs in sorted(ops.items(), key=lambda i: -len(i[1])):
                print("%-60s %d scene(s)%s" % (op, len(fs), "  PROPOSED: a reviewer decides" if len(fs) > 1 else ""))
            return 2 if blind else 0
    except Refused as e:
        print("REFUSED %s" % e)
        return 3
    except Fault as e:
        print("%s %s" % ("COULD NOT LOOK" if e.name == "COULD_NOT_LOOK" else "FAULT", e))
        return 2 if e.name == "COULD_NOT_LOOK" else 1
    print(__doc__)
    return 3


import builtins as _b  # noqa: E402
_file = _b.open               # `open` is the second of the ten names

if __name__ == "__main__":
    import scene                        # the one copy that a script imports too (its LAUNCH is the launcher's)
    sys.exit(scene.main(sys.argv[1:]))
