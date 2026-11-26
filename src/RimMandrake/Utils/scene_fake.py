"""scene_fake.py - the fake game of selftest_scene_library.py: it replays replies that were recorded on ArchSmall
(scene_recorded.json) and keeps what the library can see of a game: the process text, the pause, the calm, one run.

The replies of jawa/session and jawa/run_until are made from their wire page (design/specs/2026-11-23-bridge-v2-hands/
boundary.md); they are not recorded. A fake proves what the Python does, never what the game does."""
import copy
import json
import os
from types import SimpleNamespace

from scene_core import CallFailed, Fault, ReplyLost

HERE = os.path.dirname(os.path.abspath(__file__))
# the fake games are Archmagi's (ArchBig, ArchSmall): a test names that machine, or on SteveDesktop game_names reads the
# host and refuses each fake game as another machine's (GAME_HELD, 2026-11-25)
os.environ["RM_HOST"] = "archmagi"
with open(os.path.join(HERE, "scene_recorded.json"), encoding="utf-8") as _f:
    REC = json.load(_f)
DEAD = {"pid": 1, "platform": "dead"}


def rec(name):
    return copy.deepcopy(REC[name])


# JawaBench.BridgeTools/JawaBenchHands.cs OneHopTools.WaitArg: the tools that wait inside their body unless this argument is 0
WAIT_ARG = {"jawa/ordered_job": "waitTicks", "jawa/order_pawn": "waitTicks", "jawa/prioritized_work": "waitTicks",
            "jawa/do_bill_now": "waitTicks", "jawa/pawn_flight": "maintainTicks"}

class FakeGame(object):
    """One game process."""

    def __init__(self, run_until=False):
        self.running_mods, self.pid = rec("running_mods"), REC["running_mods"]["loaded"]["pid"]
        self.env, self.saves = {}, [x["name"] for x in rec("list_saves")["saves"]]
        self.status = rec("status_playing")
        self.status["tick"] = 1
        self.calm_on, self.loads, self.log, self.marks = False, [], [], []
        self.calm = rec("calm")
        self.tools = rec("tools")
        self.run_until = run_until
        if run_until:
            for n in ("jawa/session", "jawa/run_until", "jawa/read_paths", "jawa/act_batch"):
                self.tools.append({"name": n, "description": "from the wire page", "inputSchema": {"properties": {}}, "parameters": []})
        self.open_act = None
        self.session = None             # the game's own session (run_until only)
        self.run, self.rows, self.serial, self.starts = None, [], 0, 0
        self.script = {"state": "hit", "ticks": 20, "tracks": {}}   # how the next run goes
        self.after_run = {}             # what the status reads after the run, over what the trace says
        self.lose, self.fail, self.deny_static = set(), {}, False   # tool:action whose reply is lost; tool -> error
        self.menu_polls = 0
        self.load_ready = [rec("status_initializing")]              # what a load shows before it is ready
        # the names of the conversion ticket (scene_names.py), from the wire pages; not recorded
        self.values = {}                # (of, path) -> (state, v): what jawa/read_paths reads
        self.pawns_on, self.vanished = {}, []   # rect "x,z,w,h" (None: the whole map) -> pawns that jawa/list_pawns lists; vanished ids
        self.cleaned, self.dirty = [], {}   # the rects that jawa/destroy_batch cleaned; rects "x,z,w,h" -> things its clean leaves
        self.rect_values = []           # what a rect read gives: [{of, path, state, v}]
        self.kind_made = {}             # kindDef -> the kind the game makes instead (a replaced pawn kind)
        self.echo = False               # planted: a staging tool whose block echoes the request (no readBack)
        self.serial_id, self.acts_done, self.bound, self.pictures = 20000, {}, {}, {}
        self.map_size = (250, 250)
        self.load_windows, self.windows = [], []    # the windows that a save load opens; the windows open now

    # ---- the tools
    def call(self, tool, a):
        self.log.append((tool, dict(a)))
        if tool in self.fail:
            raise CallFailed(self.fail[tool])
        r = self._do(tool, a)
        key = "%s:%s" % (tool, a.get("action", ""))
        if key in self.lose:
            self.lose.discard(key)
            raise ReplyLost("%s: timed out" % tool)
        return r

    def _do(self, tool, a):
        if tool == "jawa/running_mods":
            return copy.deepcopy(self.running_mods)
        if tool == "rimbridge/get_bridge_status":
            if getattr(self, "windows_soon", None):
                self.windows, self.windows_soon = self.windows + self.windows_soon, []
            if self.menu_polls:
                self.menu_polls -= 1
                if not self.menu_polls:
                    self.status = rec("status_menu")
            st = self.load_ready.pop(0) if self.loads and self.load_ready else dict(self.status, **self.after_run)
            return {"success": True, "state": st}
        if tool == "jawa/static_call":
            if self.deny_static:
                return {"success": False, "message": "REFUSED in the CAMPAIGN profile: jawa/static_call is debug-invoke"}
            args = a["args"].split("|")
            if a["method"] == "GetEnvironmentVariable":
                return dict(rec("env_null"), result=self.env.get(args[0], "null"))
            if a["method"] == "SetEnvironmentVariable":
                self.env[args[0]] = args[1]
                return rec("env_set")
            return dict(rec("env_set"), result="called")
        if tool == "rimworld/list_saves":
            r = rec("list_saves")
            r["saves"] = [{"name": n} for n in self.saves[a.get("offset", 0):][:22]]
            at = a.get("offset", 0) + 22
            r["page"] = {"offset": a.get("offset", 0), "nextOffset": at if at < len(self.saves) else None}
            return r
        if tool in ("rimworld/load_game_ready", "rimworld/start_debug_game_ready"):
            if not a.get("saveName") and self.status["programState"] != "Entry":     # measured on ArchSmall 2026-11-23, after 280 s
                return {"success": False, "message": "Timed out waiting for RimWorld entry scene readiness."}
            self.loads.append(a.get("saveName") or "fresh")
            self.status = rec("status_playing")
            if a.get("saveName"):           # VEF opens them a few frames after the load returns (live on ArchBig 2026-11-25)
                self.windows_soon = [dict(w) for w in self.load_windows]
            return {"success": True}
        if tool == "jawa/window_list_close" and a.get("action") == "list":
            return {"success": True, "windows": [dict(w) for w in self.windows]}
        if tool == "rimworld/get_ui_layout":
            return {"success": True, "surfaces": [{"type": w["type"], "children": [{"label": b, "targetId": "%s/%s" % (w["ID"], b)}
                                                                                    for b in w.get("buttons", ())]} for w in self.windows]}
        if tool == "rimworld/click_ui_target":
            wid, label = a["targetId"].split("/", 1)
            self.windows = [w for w in self.windows if str(w["ID"]) != wid]
            self.clicked = getattr(self, "clicked", []) + [label]
            return {"success": True}
        if tool == "rimworld/go_to_main_menu":
            self.menu_polls = 2
            return {"success": True}
        if tool == "rimworld/pause_game":
            self.status["paused"] = bool(a.get("pause", True))
            return {"success": True}
        if tool == "jawa/quiet_site":
            if a["action"] == "calm":
                self.calm_on = True
                return copy.deepcopy(self.calm)
            r = rec("release")
            r["released"], self.calm_on = self.calm_on, False
            return r
        if tool == "jawa/telemetry_mark":
            self.marks.append(a["why"])
            return rec("telemetry_mark")
        if tool == "jawa/pawn_get":
            return rec("pawns")
        if tool == "jawa/scene_slice":
            return self._slice(a)
        if tool == "jawa/session":
            return self._session(a)
        if tool == "jawa/run_until":
            return self._run_until(a)
        if tool == "jawa/read_paths":
            return self._read_paths(a)
        if tool == "jawa/act_batch":
            return self._act_batch(a)
        if tool in ("jawa/spawn_pawn", "jawa/build_batch", "jawa/set_terrain_batch", "jawa/destroy_batch"):
            return self._stage(tool, a)
        if tool == "jawa/artboard_capture":
            self.pictures[a["path"]] = self.pictures.get(a["path"], 0) + 1
            return {"success": True, "path": a["path"], "fileSizeBytes": 4096, "frame": [a["w"] * a["ppc"], a["h"] * a["ppc"]],
                    "foggedCells": 0, "cameraRestored": True}
        if tool == "jawa/new_allowed_area":
            return {"success": True, "label": a.get("label")}
        if tool == "jawa/paint_area":
            return {"success": True, "failedVerify": 0, "outOfBounds": 0}
        if tool == "jawa/set_player_settings":
            self.areas = getattr(self, "areas", {})
            if "area" in a:
                self.areas[a["pawnId"]] = None if a["area"] in ("none", "clear") else a["area"]
            return {"success": True, "area": self.areas.get(a["pawnId"])}
        if tool == "jawa/set_forbidden":
            return {"success": True, "changed": 1}
        if tool == "jawa/list_pawns":
            return {"success": True, "pawns": [dict(p) for p in self.pawns_on.get(a.get("rect"), [])]}
        if tool == "jawa/pawn_force_incapacitate":
            self.vanished.append(a.get("pawn"))
            for k in self.pawns_on:
                self.pawns_on[k] = [p for p in self.pawns_on[k] if p.get("id") != a.get("pawn")]
            return {"success": True}
        if tool == "jawa/ordered_job" and ("targetBX" in a or "targetBId" in a) and not ("targetAId" in a or "targetAX" in a):
            # the game's own refusal (live ArchBig 2026-11-25): JobMaker has no B-without-A overload
            return {"success": False, "message": "targetB was given without targetA. Give targetAId, or targetAX and targetAZ."}
        if tool in ("jawa/damage", "jawa/ordered_job"):
            return {"success": True, "accepted": True}
        return {"success": True, "tool": tool}

    # ---- the hands of the conversion ticket
    def _value(self, of, path):
        if of == "map" and path == "info.sizeInt":      # Verse.MapInfo.sizeInt (read live 2026-11-24: there is no field `size`)
            return "ok", "%d,0,%d" % self.map_size
        return self.values.get((of, path), ("error", None))

    def _read_paths(self, a):
        out = []
        if a.get("rect"):
            out += [dict(v) for v in self.rect_values if v["path"] == a.get("path")]
        for r in json.loads(a.get("reads") or "[]"):
            st, v = self._value(r["of"], r["path"])
            out.append({"of": r["of"], "path": r["path"], "state": st, "v": v, "detail": None if st == "ok" else "the fake holds it as %s" % st})
        return {"success": True, "tick": self.status["tick"], "paused": self.status.get("paused", True), "values": out}

    def _act_batch(self, a):
        if not self.session:
            return {"success": False, "refused": "NO_SESSION", "message": "no session"}
        if not self.status.get("paused", True):
            return {"success": False, "refused": "GAME_RUNNING", "message": "the game is running"}
        rows = []
        acts = json.loads(a["acts"])
        for act in acts:     # the game's rule (JawaBenchHands.cs OneHopTools.WaitArg): a tool that waits inside its body is refused
            arg = WAIT_ARG.get(act["tool"])                     # in a batch unless its wait argument is 0; the whole batch is refused
            if arg and act["args"].get(arg) != 0:
                return {"success": False, "refused": "NOT_ONE_HOP",
                        "message": "NOT_ONE_HOP: %s waits inside its body unless %s is 0" % (act["tool"], arg)}
        for act in acts:
            key = json.dumps([act["tool"], act["args"]], sort_keys=True)
            if act["id"] in self.acts_done:
                old = self.acts_done[act["id"]]
                if old["key"] != key:
                    return {"success": False, "refused": "REQUEST_CONFLICT", "message": "id %s came again with other arguments" % act["id"]}
                rows.append(dict(old["row"], replayed=True))
                continue
            reply = self._do(act["tool"], act["args"])
            row = {"id": act["id"], "tool": act["tool"], "state": "done" if reply.get("success") is not False else "refused",
                   "reply": reply, "tick": self.status["tick"], "frame": 7, "replayed": False}
            self.acts_done[act["id"]] = {"key": key, "row": row}
            rows.append(row)
        return {"success": True, "acts": rows}

    def _stage(self, tool, a):
        made, wrong = [], []
        if tool == "jawa/spawn_pawn":
            self.serial_id += 1
            kind = self.kind_made.get(a["kindDef"], a["kindDef"])
            row = {"op": "pawn", "id": "Human%d" % self.serial_id, "x": a["x"], "z": a["z"],
                   "got": {"kind": kind, "spawned": "True", "cell": "%d,%d" % (a["x"], a["z"]), "faction": "PlayerColony"}}
            made.append(row)
            if kind != a["kindDef"]:
                wrong.append(dict(row, wrong=[{"key": "kind", "want": a["kindDef"], "got": kind}]))
        elif tool == "jawa/build_batch":
            for op in a["ops"].split(";"):
                d, rest = op.split(":")
                xz = rest.split(",")
                self.serial_id += 1
                made.append({"op": "thing", "id": "%s%d" % (d, self.serial_id), "x": int(xz[0]), "z": int(xz[1]),
                             "got": {"def": d, "cell": "%s,%s" % (xz[0], xz[1]), "rot": xz[2] if len(xz) > 2 else "0"}})
        elif tool == "jawa/set_terrain_batch":
            for op in a["ops"].split(";"):
                d, rest = op.split(":")
                x, z = (int(n) for n in rest.split(",")[:2])
                made.append({"op": "terrain", "id": None, "x": x, "z": z, "got": {"terrain": d}})
        left = []
        if tool == "jawa/destroy_batch":
            self.cleaned.append(a.get("rects"))
            left = list(self.dirty.get(a.get("rects")) or [])
        if self.echo:
            return {"success": True, "pawns": [{"id": "Human1", "kind": a.get("kindDef")}], "ops": a.get("ops")}
        block = {"ok": not wrong and not left, "tool": tool, "faults": ["read_back_wrong"] if wrong else [], "frameOpen": 7, "frameReply": 7,
                 "sameFrame": True, "rows": len(made), "rowsWrong": len(wrong), "wrong": wrong, "made": made, "leftBlocking": len(left),
                 "leftKept": 0, "left": left, "digest": "d"}
        return {"success": not wrong, "readBack": block}

    # ---- a run: its records in the recorded schema
    def _play(self, run_id, names, limit):
        s = self.script
        t0 = self.status["tick"]
        n = min(s["ticks"], limit) if s["state"] in ("hit", "unknown") else (limit if s["state"] == "done" else s["ticks"])
        end = t0 + n
        base = {k: REC["trace_hit"][0][k] for k in ("v", "utc", "mono", "session", "kind")}
        rows = []

        def add(tick, phase, kind, **kw):
            rows.append(dict(base, seq=len(self.rows) + len(rows) + 8, run=run_id, n=len(rows) + 1, tick=tick, phase=phase, rec=kind, **kw))
        add(t0, "first", "open", acts=[], tracks=list(names), taps=[],
            **{k: v for k, v in REC["trace_hit"][0].items() if k in ("schema", "mode", "epoch")})
        last, samples = {}, []
        for name in names:
            for off, st, v in s["tracks"].get(name, [(0, "ok", 5)]):
                if off <= n:
                    samples.append((off, name, st, v))
        for off, name, st, v in sorted(samples, key=lambda x: (x[0], x[1])):
            add(t0 + off, "first" if off == 0 else "end_of_tick", "track", name=name, st=st, v=v)
            last[name] = (st, v)
        add(end, "end_of_tick", "end", complete=s["state"] in ("hit", "done"), state=s["state"], hitTick=end if s["state"] == "hit" else None, executed=n, why=None)
        for name in names:
            add(end, "last", "track", name=name, st=last[name][0], v=last[name][1])
        if s.get("fault"):
            add(end, "last", "fault", what=s["fault"], detail="planted")
        add(end, "last", "close", actsNotDone=[], rows=len(rows), dropped=s.get("dropped", 0), drained=s.get("drained", True), paused=s.get("paused", True),
            tickAfter=end + s.get("ran_on", 0))
        if s.get("no_close"):
            rows.pop()
        if s.get("gap"):
            rows.pop(len(rows) // 2)
        self.rows += rows
        self.status["tick"] = end + s.get("ran_on", 0)
        return end

    def _slice(self, a):
        if a["action"] == "start":
            if self.script.get("bind"):
                return dict(rec("slice_refused_bind"), at=self.script["bind"])
            self.serial += 1
            self.starts += 1
            rid = "s20261124T050344_%d" % self.serial
            names = list(json.loads(a["tracks"])) + ["dead", "job"]
            t0 = self.status["tick"]
            end = self._play(rid, names, a["maxTicks"])
            self.run = dict(rec("slice_hit"), run=rid, state=self.script["state"], endTick=end, hitTick=end, polls=self.script.get("polls", 1),
                            result={"tickFrom": float(t0), "values": self.script.get("unknown", [])})
            return dict(rec("slice_started"), run=rid, endTick=t0)
        if self.run is None:
            return rec("slice_none")
        if a["action"] == "cancel":
            self.run.update(polls=0, state="cancelled")
        if self.run["polls"] > 0:
            self.run["polls"] -= 1
            return dict(self.run, stage="running", state="running")
        return dict(self.run)

    def _session(self, a):
        if a["action"] == "open":
            self.session = {"session": "g1", "driver": a["driver"], "stage": "open"}
            return {"success": True, "session": "g1", "state": "open"}
        if a["action"] == "take":
            if not self.session or self.session["stage"] != "open":
                return {"success": False, "refused": "NO_SESSION", "message": "no session is open"}
            if a.get("from") != self.session["driver"]:
                return {"success": False, "refused": "DRIVER_ALIVE", "message": "another driver"}
            self.session.update(driver=a["driver"], taken=True)
            if self.run and self.run["polls"] > 0:
                self.run.update(polls=0, state="cancelled", why="cancelled")
            self.status["paused"] = True
            return dict({"success": True, "openAct": self.open_act}, **self.session)
        if a["action"] in ("close", "abort"):
            old, self.session = self.session or {}, None
            return {"success": True, "session": old.get("session"), "stage": "closed" if a["action"] == "close" else "aborted"}
        out = {"success": True, "stage": "none", "lastRun": None, "recordDir": "D:\\rec", "writerSession": "w"}
        out.update(self.session or {})
        out["lastRun"] = self.run and {"request": self.run["request"], "run": self.run["run"], "stage": "running" if self.run["polls"] > 0 else "closed",
                                        "why": self.run.get("why"), "state": self.run.get("state"), "tick": self.run.get("tick")}
        return out

    def _run_until(self, a):
        if a["action"] == "start":
            if self.run and self.run["request"] == a["request"]:
                return dict(self.run, replayed=True)
            self.starts += 1
            t0 = self.status["tick"]
            names = ["%s.%s" % (t["of"], t["path"]) for t in json.loads(a["record"])] + [n for n in self.script["tracks"]]
            rid = "S1_r%d" % self.starts
            end = self._play(rid, sorted(set(names)), a["limit"])
            why = {"done": "limit"}.get(self.script["state"], self.script["state"])
            self.run = {"success": True, "request": a["request"], "run": rid, "stage": "closed", "why": why, "state": self.script["state"],
                        "tickFrom": t0, "tick": end, "rows": 5, "polls": 0}
            return dict(self.run, stage="running", why=None)
        if not self.run or self.run["request"] != a.get("request"):
            return {"success": False, "refused": "UNKNOWN_REQUEST", "message": "no such request"}
        return dict(self.run)


class FakeBridge(object):
    def __init__(self, game):
        self.game, self.closed = game, False

    def tools(self):
        if "tools/list" in self.game.fail:
            raise CallFailed(self.game.fail["tools/list"])
        return self.game.tools

    def call(self, tool, args):
        return self.game.call(tool, args)

    def close(self):
        self.closed = True


class FakeWorld(object):
    """Everything outside the library, in memory."""

    def __init__(self, game=None, repo=None):
        self.games = {"b": game or FakeGame()}
        self.lock, self.lock_code, self.released = None, 0, 0
        self.files, self.t, self.dead = {}, 0.0, False
        self.wanted_rows, self.verdict = {}, {"verdict": "MATCH", "why": []}
        self.canon = (["ASHKARR_WORLDMAP_FULL"], ["CANON_"])
        self.repo, self.gits = repo, {}
        self.stages = {}                # ("made", save) | ("live", game key) -> the stage file's text

    game = property(lambda self: self.games["b"])

    def sleep(self, s):
        self.t += s

    def clock(self):
        self.t += 0.001
        return self.t

    def lock_take(self, letter, purpose):
        if self.lock_code:
            return {"code": self.lock_code, "line": "ArchSmall: held (planted %d)" % self.lock_code, "inherited": False}
        if self.lock:
            return {"code": 75, "line": "ArchSmall: HELD by another scene", "inherited": False}
        self.lock = letter
        return {"code": 0, "line": "CLAIMED", "inherited": False}

    def lock_release(self, letter):
        self.lock, self.released = None, self.released + 1
        return "released"

    def connect(self, letter):
        if letter not in self.games:
            raise Fault("NO_GAME", detail="the bridge did not answer")
        return FakeBridge(self.games[letter])

    def game_health(self, letter):
        return SimpleNamespace(state="paused")

    def me(self):
        return {"pid": 4242, "platform": "fake"}

    def alive(self, ident):
        return False if ident == DEAD or self.dead else True

    def wanted(self, mods):
        out = []
        for m in ([mods] if isinstance(mods, str) else mods):
            if m not in self.wanted_rows:
                raise KeyError("%r is no mod" % m)
            out.append(self.wanted_rows[m])
        return out

    def judge_loaded(self, reply, pid, dlls, key, part):
        return dict(self.verdict)

    def canonical(self):
        return self.canon

    def companion_hash(self):
        return "the-hash-that-the-repo-holds"

    def git(self, *args):
        for k, v in self.gits.items():
            if args[:len(k)] == k:
                return v
        return 0, ""

    def run_dir(self, label):
        return "/fake/%s" % label

    def picture_path(self, run_dir, name):
        return "%s/%s.png" % (run_dir, name)

    def file_stamp(self, path):
        n = self.game.pictures.get(path)
        return None if n is None else (4096, n)

    def stage_state(self, key):
        return self.stages.get(("live", key))

    def stage_save(self, key, text):
        self.stages[("live", key)] = text

    def stage_loaded(self, key, where):
        made = self.stages.get(("made", where))
        if made:
            self.stages[("live", key)] = made
            return "the stage of %s: its stations are all clean (a fresh load)" % where
        self.stages.pop(("live", key), None)
        return "%s is not a made stage: no station allocator" % where

    def stage_made(self, save, text):
        self.stages[("made", save)] = text
        return "made/%s" % save

    def save(self, path, text, append=False):
        self.files[path] = (self.files.get(path, "") if append else "") + text

    def read_trace(self, folder, writer, run):
        return [r for r in self.game.rows if r["run"] == run]
