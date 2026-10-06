"""Approach C: a bounded "AI plays FlowWorks" mission driver. NOT a game-playing platform.

Three fixed missions (player_missions_spec.json): canal, pit, chain. A player agent (a Claude subagent following
player_missions_BRIEF.md) plays one by calling this script, one command per move:

    python.exe src/RimMandrake/FlowWorks/northstar/player_missions.py start canal        # fixture, checkpoint save, clock starts
    python.exe src/RimMandrake/FlowWorks/northstar/player_missions.py observe [--shot]
    python.exe src/RimMandrake/FlowWorks/northstar/player_missions.py act <tool> '<json args>' [--intent "..."]
    python.exe src/RimMandrake/FlowWorks/northstar/player_missions.py note <kind> "<what happened>"
    python.exe src/RimMandrake/FlowWorks/northstar/player_missions.py report [--json]
    python3    src/RimMandrake/FlowWorks/northstar/player_missions.py verify        # offline: whitelist vs dump + C# source
    python3    src/RimMandrake/FlowWorks/northstar/player_missions.py start canal --dry-run   # same loop, fake game

Live = Windows python.exe from the repo root (WSL cannot reach the bridge). --dry-run runs against an extended
fakegame.FakeFlowWorksGame pickled in the run dir, so the whole loop is exercisable with the game down.

Every action row in <run>/actions.jsonl carries: wall start/end, bridge_ms (the tool call itself), overhead_ms
(the tick reads around it + connect), think_s (gap since the previous row ended = agent deliberation), ticks
advanced by the call and ticks that passed during the think gap (game left running), and friction flags.
"""
import argparse
import glob
import json
import os
import pickle
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
UTILS = os.path.join(REPO, "src", "RimMandrake", "Utils")
SPEC_PATH = os.path.join(HERE, "player_missions_spec.json")
RUNS = os.path.join(REPO, "Transient", "player_missions")
DUMP = os.path.join(REPO, "Transient", "bench_tools_dump.json")
TOOLSRC = os.path.join(REPO, "src", "RimMandrake", "bridgetools", "JawaBench.BridgeTools")
for p in (HERE, UTILS):
    if p not in sys.path:
        sys.path.insert(0, p)


def load_spec(path=SPEC_PATH):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


class Clock(object):
    """Injectable so the selftest can drive timing deterministically."""
    wall = staticmethod(time.time)
    perf = staticmethod(time.perf_counter)


CLOCK = Clock()


# ============================================================================ whitelist
class Refused(Exception):
    pass


def check_action(spec, tool, args, gizmo_label=None, option_label=None):
    """Return the args actually sent (forced/capped), or raise Refused(reason). Pure; no I/O."""
    args = dict(args or {})
    wl = spec["whitelist"]
    if tool in spec["refused"]:
        raise Refused("refused dev shortcut: %s (%s)" % (tool, spec["refused"][tool]))
    for pat in spec["refused_patterns"]:
        if pat in tool.lower():
            raise Refused("refused by pattern '%s': %s" % (pat, tool))
    if tool not in wl:
        raise Refused("not on the player whitelist: %s" % tool)
    ent = wl[tool]
    allowed = set(ent["params"]) | set(ent.get("force", {}))
    unknown = sorted(k for k in args if k not in allowed)
    if unknown:
        # the bridge drops unknown keys silently and runs on defaults - refuse loudly instead
        raise Refused("unknown parameter(s) %s for %s; allowed: %s" % (unknown, tool, sorted(ent["params"])))
    for k, v in ent.get("force", {}).items():
        args[k] = v
    for k, cap in ent.get("cap", {}).items():
        if k in args:
            try:
                if float(args[k]) > cap:
                    raise Refused("%s=%s exceeds the per-call cap %s for %s" % (k, args[k], cap, tool))
            except (TypeError, ValueError):
                raise Refused("%s must be a number" % k)
    rx = re.compile(spec["refused_labels"])
    for lab in (gizmo_label, option_label, args.get("label")):
        if lab and rx.search(str(lab)):
            raise Refused("refused dev/debug UI label: %r" % lab)
    return args


# ============================================================================ geometry
def rect_of(anchor, r):
    return (anchor[0] + r["dx"], anchor[1] + r["dz"], r["w"], r["h"])


def rect_str(t):
    return "%d,%d,%d,%d" % t


def landmark_rects(mission, anchor):
    out = {"site": rect_of(anchor, mission["site"])}
    for k, r in mission.get("landmarks", {}).items():
        out[k] = rect_of(anchor, r)
    return out


def resolve_args(args, anchor, rects):
    """'{site}' -> 'x,z,w,h'; '=ax-2' -> int. Fixture/event args only."""
    out = {}
    env = {"ax": anchor[0], "az": anchor[1]}
    fmt = dict((k, rect_str(v)) for k, v in rects.items())
    for k, v in args.items():
        if isinstance(v, str) and v.startswith("="):
            out[k] = int(eval(v[1:], {"__builtins__": {}}, env))     # noqa: S307 - spec-authored arithmetic
        elif isinstance(v, str) and "{" in v:
            out[k] = v.format(**fmt)
        else:
            out[k] = v
    return out


def in_rect(x, z, r):
    return r[0] <= x < r[0] + r[2] and r[1] <= z < r[1] + r[3]


# ============================================================================ transports
def unwrap(r):
    if isinstance(r, dict) and r.get("content") and isinstance(r["content"], list):
        try:
            return json.loads(r["content"][0]["text"])
        except Exception:                      # noqa: BLE001
            pass
    return r if isinstance(r, dict) else {"success": False, "raw": r}


class LiveBridge(object):
    def __init__(self):
        import rimbridge_client as rb          # noqa: E402
        t0 = CLOCK.perf()
        host, port, token = rb.resolve_endpoint()
        self.S = rb.RimBridge(host=host, port=port, token=token, timeout=60.0)
        self.S.connect()
        self.connect_ms = (CLOCK.perf() - t0) * 1000.0

    def call(self, tool, args):
        return unwrap(self.S.call(tool, args))

    def close(self):
        try:
            self.S.close()
        except Exception:                      # noqa: BLE001
            pass


def _mission_fake_class():
    from fakegame import FakeFlowWorksGame

    class MissionFake(FakeFlowWorksGame):
        """Toy model of the player loop for --dry-run: designate dig -> colonist digs a cell per 300 ticks ->
        dug cells 4-connected to the pond draw 1 unit each from its limited stock. Shapes follow the live
        tools' ResultDescriptions; the PHYSICS is a toy and proves nothing about FlowWorks."""
        DIG = "Designator_DigCanal_fake"

        def __init__(self):
            super().__init__(size=(120, 120))
            self.ticks = 1000
            self.paused = True
            self.designated = []
            self.dig_progress = 0
            self.pond = set()
            self.pond_stock = 40
            self.selection = None
            self.shots = 0
            self.pawns = [{"id": "Thing_Human1", "name": "Ada", "x": 60, "z": 66, "faction": "PlayerColony"}]

        def handle(self, tool, p):
            p = p or {}
            W, Z = self.size
            if tool == "rimworld/get_game_info":
                return {"success": True, "ticksGame": self.ticks}
            if tool == "jawa/set_terrain_batch":
                for op in p["ops"].split(";"):
                    terr, r = op.split(":")
                    x, z, w, h = [int(v) for v in r.split(",")]
                    for i in range(x, x + w):
                        for j in range(z, z + h):
                            self.terrain[(i, j)] = terr
                            if terr.startswith("Water"):
                                self.pond.add((i, j))
                            else:
                                self.pond.discard((i, j))
                return {"success": True, "cellsFailedVerify": 0}
            if tool == "jawa/destroy_batch":
                return {"success": True, "destroyed": {}}
            if tool == "rimworld/list_colonists":
                return {"success": True, "colonists": [{"pawnId": q["id"], "name": q["name"],
                                                         "position": {"x": q["x"], "z": q["z"]}} for q in self.pawns]}
            if tool == "rimworld/list_architect_categories":
                return {"success": True, "categories": [{"id": "Orders", "label": "Orders"}]}
            if tool == "rimworld/list_architect_designators":
                return {"success": True, "designators": [{"id": self.DIG, "label": "Dig canal"}]}
            if tool == "rimworld/apply_architect_designator":
                if p["designatorId"] != self.DIG:
                    return {"success": False, "message": "fake: unknown designator"}
                x, z, w, h = int(p["x"]), int(p["z"]), int(p.get("width", 1)), int(p.get("height", 1))
                cells = [(i, j) for i in range(x, x + w) for j in range(z, z + h)]
                ok = [c for c in cells if c not in self.pond and 0 <= c[0] < W and 0 <= c[1] < Z]
                if not ok:
                    return {"success": False, "message": "Must designate on diggable ground."}
                if not p.get("dryRun"):
                    self.designated += [c for c in ok if c not in self.designated]
                return {"success": True, "appliedCellCount": len(ok), "rejectedCellCount": len(cells) - len(ok)}
            if tool == "rimworld/step_game_ticks":
                n = int(p.get("ticks", 1))
                self.ticks += n
                self.dig_progress += n
                while self.dig_progress >= 300 and self.designated:
                    self.dig_progress -= 300
                    c = self.designated.pop(0)
                    self.D[c] = max(1, self.D.get(c, 0))
                self._flow()
                return {"success": True, "ticksAdvanced": n}
            if tool == "jawa/flowworks_excavation_rect":
                x, z, w, h = int(p["x"]), int(p["z"]), int(p["w"]), int(p["h"])
                rows = []
                for i in range(x, x + w):
                    for j in range(z, z + h):
                        d, f = self.D.get((i, j), 0), self.F.get((i, j), 0)
                        src = (i, j) in self.pond
                        if p.get("onlyNonZero") and not (d or f or src):
                            continue
                        rows.append({"x": i, "z": j, "d": d, "f": f, "dEff": 4 if src else d, "fEff": 4 if src else f,
                                     "isExcavated": d > 0, "isSource": src, "isSink": False})
                return {"success": True, "rows": rows, "cellCount": len(rows), "ticksGame": self.ticks}
            if tool == "rimworld/get_designator_state":
                return {"success": True, "selectedDesignator": None, "godMode": False}
            if tool in ("rimworld/list_letters", "rimworld/list_messages", "rimworld/list_alerts"):
                return {"success": True, "letters": [], "messages": [], "alerts": []}
            if tool in ("rimworld/screenshot_cell_rect", "rimworld/take_screenshot"):
                self.shots += 1
                return {"success": True, "path": "FAKE://shot_%d.png" % self.shots}
            if tool in ("jawa/weather_set", "jawa/incident_queue_clear", "rimworld/pause_game", "jawa/clear_ui"):
                return {"success": True}
            if tool == "jawa/map_info":
                return {"success": True, "sizeX": W, "sizeZ": Z, "mapId": 7}
            if tool == "rimworld/save_game":
                return {"success": True, "path": "FAKE://%s.rws" % p["saveName"]}
            raise RuntimeError("dry-run fake does not model %s" % tool)

        def _flow(self):
            wet = set(self.pond) | set(c for c, f in self.F.items() if f > 0)
            changed = True
            while changed and self.pond_stock > 0:
                changed = False
                for c in sorted(self.D):
                    if self.D[c] > 0 and self.F.get(c, 0) == 0 and self.pond_stock > 0:
                        x, z = c
                        if any(n in wet for n in ((x + 1, z), (x - 1, z), (x, z + 1), (x, z - 1))):
                            self.F[c] = 1
                            self.pond_stock -= 1
                            wet.add(c)
                            changed = True

    return MissionFake


class FakeBridge(object):
    def __init__(self, run_dir, fresh=False):
        self.path = os.path.join(run_dir, "fake.pickle")
        if fresh or not os.path.exists(self.path):
            self.g = _mission_fake_class()()
        else:
            cls = _mission_fake_class()        # a local class does not pickle; its state does
            self.g = cls.__new__(cls)
            with open(self.path, "rb") as f:
                self.g.__dict__.update(pickle.load(f))
        self.connect_ms = 0.0

    def call(self, tool, args):
        return self.g.handle(tool, dict(args or {}))

    def close(self):
        with open(self.path, "wb") as f:
            pickle.dump(self.g.__dict__, f)


# ============================================================================ run state
def current_run(explicit=None):
    if explicit:
        return explicit
    ptr = os.path.join(RUNS, "CURRENT")
    if not os.path.exists(ptr):
        raise SystemExit("no current run - `start <mission>` first")
    with open(ptr, encoding="utf-8") as f:
        return os.path.join(RUNS, f.read().strip())


def read_run(run_dir):
    with open(os.path.join(run_dir, "run.json"), encoding="utf-8") as f:
        return json.load(f)


def write_run(run_dir, run):
    with open(os.path.join(run_dir, "run.json"), "w", encoding="utf-8") as f:
        json.dump(run, f, indent=1)


def read_actions(run_dir):
    p = os.path.join(run_dir, "actions.jsonl")
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def append_action(run_dir, row):
    with open(os.path.join(run_dir, "actions.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")


def bridge_for(run, run_dir):
    return FakeBridge(run_dir) if run.get("dry_run") else LiveBridge()


def ticks_of(B):
    r = B.call("rimworld/get_game_info", {})
    v = r.get("ticksGame") if isinstance(r, dict) else None
    return int(v) if isinstance(v, (int, float)) else None


def _norm(args):
    return json.dumps(args or {}, sort_keys=True)


def friction_flags(tool, args, result, ok, prior_rows):
    """Automatic friction classification for one action. Agent-reported kinds come in through `note`."""
    flags = []
    msg = ""
    if isinstance(result, dict):
        msg = str(result.get("message") or result.get("reason") or result.get("error") or "")
    cls = (run_spec_cache.get("whitelist", {}).get(tool) or {}).get("cls")
    if cls not in ("read", "time", "shot") and prior_rows and any(
            r["tool"] == tool and r.get("args_norm") == _norm(args) and r["kind"] == "act" for r in prior_rows):
        flags.append("repeated_attempt")
    if not ok:
        if tool in ("rimworld/apply_architect_designator", "rimworld/select_architect_designator"):
            flags.append("failed_placement")
        else:
            flags.append("failed_action")
        if not msg.strip():
            flags.append("unclear_refusal")
    elif tool == "rimworld/apply_architect_designator" and isinstance(result, dict):
        if result.get("rejectedCellCount"):
            flags.append("partial_placement")
    return flags, msg


def deadline_hit(run, rows, now_wall, ticks_now):
    dl = run["deadline"]
    acts = sum(1 for r in rows if r["kind"] in ("act", "observe"))
    if now_wall - run["mission_start_wall"] > dl["wall_s"]:
        return "wall deadline %ds" % dl["wall_s"]
    if ticks_now is not None and run.get("tick0") is not None and ticks_now - run["tick0"] > dl["ticks"]:
        return "game-time deadline %d ticks" % dl["ticks"]
    if acts >= dl["actions"]:
        return "action budget %d" % dl["actions"]
    return None


def fire_due_events(B, run, ticks_now, run_dir):
    """Mission events (the storyteller) fire when the game clock passes them. Logged, never the agent's."""
    fired = []
    for i, ev in enumerate(run["events"]):
        if i in run.get("events_fired", []) or ticks_now is None or run.get("tick0") is None:
            continue
        if ticks_now - run["tick0"] >= ev["at_ticks"]:
            args = resolve_args(ev["args"], run["anchor"], {k: tuple(v) for k, v in run["rects"].items()})
            t0 = CLOCK.perf()
            try:
                res = B.call(ev["tool"], args)
            except Exception as ex:            # noqa: BLE001
                res = {"success": False, "message": str(ex)}
            run.setdefault("events_fired", []).append(i)
            append_action(run_dir, {"kind": "event", "tool": ev["tool"], "args": args, "ok": bool(res.get("success")),
                                    "bridge_ms": round((CLOCK.perf() - t0) * 1000, 2), "wall_start": CLOCK.wall(),
                                    "wall_end": CLOCK.wall(), "result_excerpt": json.dumps(res)[:400]})
            fired.append(ev["tool"])
    return fired


# ============================================================================ commands
def cmd_start(a, spec):
    m = spec["missions"].get(a.mission)
    if m is None:
        raise SystemExit("unknown mission %r; one of %s" % (a.mission, sorted(spec["missions"])))
    stamp = time.strftime("%Y%m%dT%H%M%S")
    name = "%s_%s%s" % (a.mission, stamp, "_dry" if a.dry_run else "")
    run_dir = os.path.join(a.runs or RUNS, name)
    os.makedirs(os.path.join(run_dir, "shots"), exist_ok=True)
    B = FakeBridge(run_dir, fresh=True) if a.dry_run else LiveBridge()
    t_fix = CLOCK.wall()
    fixture_rows = []
    try:
        if a.anchor:
            anchor = [int(v) for v in a.anchor.split(",")]
        else:
            mi = B.call("jawa/map_info", {})
            anchor = [int(mi["sizeX"]) // 2, int(mi["sizeZ"]) // 2]
        rects = landmark_rects(m, anchor)
        B.call("rimworld/pause_game", {"pause": True})
        for op in ([] if a.skip_fixture else m["fixture"]):
            args = resolve_args(op["args"], anchor, rects)
            t0 = CLOCK.perf()
            res = B.call(op["tool"], args)
            fixture_rows.append({"tool": op["tool"], "args": args, "ok": bool(res.get("success")),
                                 "ms": round((CLOCK.perf() - t0) * 1000, 2), "excerpt": json.dumps(res)[:300]})
        tick0 = ticks_of(B)
        save = "PM_%s_start_%s" % (a.mission, stamp)
        sres = B.call("rimworld/save_game", {"saveName": save})
    finally:
        B.close()
    run = {"mission": a.mission, "title": m["title"], "goal": m["goal"], "dry_run": bool(a.dry_run),
           "anchor": anchor, "rects": {k: list(v) for k, v in rects.items()}, "events": m["events"],
           "goal_check": m["goal_check"], "deadline": m["deadline"], "fixture": fixture_rows,
           "fixture_s": round(CLOCK.wall() - t_fix, 3), "checkpoint_save": save,
           "checkpoint_reply_path": sres.get("path"), "tick0": tick0, "mission_start_wall": CLOCK.wall(),
           "events_fired": [], "connect_ms": B.connect_ms}
    write_run(run_dir, run)
    os.makedirs(a.runs or RUNS, exist_ok=True)
    with open(os.path.join(a.runs or RUNS, "CURRENT"), "w", encoding="utf-8") as f:
        f.write(name)
    bad = [r for r in fixture_rows if not r["ok"]]
    print("RUN %s" % run_dir)
    print("MISSION %s: %s" % (a.mission, m["title"]))
    print("GOAL: %s" % m["goal"])
    print("PLACES (x,z,w,h): %s" % ", ".join("%s=%s" % (k, rect_str(tuple(v))) for k, v in run["rects"].items()))
    print("DEADLINE: %(wall_s)ds wall, %(ticks)d ticks, %(actions)d actions" % m["deadline"])
    print("FIXTURE: %d ops in %.1fs, %d failed%s; checkpoint save %s (stat the Saves folder - save_game has "
          "written the wrong slot before)" % (len(fixture_rows), run["fixture_s"], len(bad),
                                              (" -> " + "; ".join(r["tool"] for r in bad)) if bad else "", save))
    return 1 if bad else 0


def _do(run_dir, run, B, kind, tool, args, intent=None, sent=None, refused=None, rows=None):
    """One logged row. `sent` = checked args (None when refused)."""
    rows = read_actions(run_dir) if rows is None else rows
    prev_end = rows[-1]["wall_end"] if rows else run["mission_start_wall"]
    prev_ticks = next((r["ticks_after"] for r in reversed(rows) if r.get("ticks_after") is not None), run.get("tick0"))
    w0 = CLOCK.wall()
    row = {"kind": kind, "tool": tool, "args": args, "args_norm": _norm(args), "intent": intent,
           "wall_start": w0, "think_s": round(w0 - prev_end, 3), "visible": None}
    if refused:
        row.update(ok=False, refused=refused, bridge_ms=0.0, overhead_ms=0.0, wall_end=CLOCK.wall(),
                   ticks_before=None, ticks_after=None, flags=["refused_by_driver"], message=refused)
        append_action(run_dir, row)
        return row, None
    o0 = CLOCK.perf()
    tb = ticks_of(B)
    overhead = (CLOCK.perf() - o0) * 1000
    t0 = CLOCK.perf()
    try:
        res = B.call(tool, sent)
        ok = bool(res.get("success", True)) if isinstance(res, dict) else False
    except Exception as ex:                    # noqa: BLE001
        res, ok = {"success": False, "message": "%s: %s" % (type(ex).__name__, ex)}, False
        if "does not model" in str(ex):
            row["transport_limitation"] = True
    bridge_ms = (CLOCK.perf() - t0) * 1000
    o1 = CLOCK.perf()
    ta = ticks_of(B)
    overhead += (CLOCK.perf() - o1) * 1000
    flags, msg = friction_flags(tool, args, res, ok, rows)
    row.update(ok=ok, bridge_ms=round(bridge_ms, 2), overhead_ms=round(overhead, 2), ticks_before=tb, ticks_after=ta,
               ticks_advanced=(ta - tb) if (ta is not None and tb is not None) else None,
               ticks_during_think=(tb - prev_ticks) if (tb is not None and prev_ticks is not None) else None,
               flags=flags, message=msg, sent=sent, result_excerpt=json.dumps(res, default=str)[:600],
               wall_end=CLOCK.wall())
    if kind == "act" and tool in run_spec_cache.get("whitelist", {}):
        row["visible"] = run_spec_cache["whitelist"][tool].get("visible")
    append_action(run_dir, row)
    return row, res


run_spec_cache = {}


def cmd_act(a, spec):
    run_dir = current_run(a.run)
    run = read_run(run_dir)
    run_spec_cache.update(spec)
    try:
        args = json.loads(a.args) if a.args else {}
    except ValueError as ex:
        raise SystemExit("args must be a JSON object: %s" % ex)
    rows = read_actions(run_dir)
    if any(r["kind"] == "deadline" for r in rows):
        print("REFUSED: the mission is over (deadline). Run `report`.")
        return 3
    B = bridge_for(run, run_dir)
    try:
        tnow = ticks_of(B)
        why = deadline_hit(run, rows, CLOCK.wall(), tnow)
        if why:
            append_action(run_dir, {"kind": "deadline", "tool": None, "message": why, "wall_start": CLOCK.wall(),
                                    "wall_end": CLOCK.wall(), "flags": []})
            print("DEADLINE: %s. The mission is over; run `report`." % why)
            return 3
        gizmo_label = None
        if a.tool == "rimworld/execute_gizmo" and "gizmoId" in args:
            gz = B.call("rimworld/list_selected_gizmos", {})
            for g in (gz.get("gizmos") or []) if isinstance(gz, dict) else []:
                if str(g.get("gizmoId") or g.get("id")) == str(args["gizmoId"]):
                    gizmo_label = g.get("label") or g.get("defaultLabel")
        try:
            sent = check_action(spec, a.tool, args, gizmo_label=gizmo_label)
        except Refused as r:
            _do(run_dir, run, B, "act", a.tool, args, a.intent, refused=str(r), rows=rows)
            print("REFUSED: %s" % r)
            return 2
        row, res = _do(run_dir, run, B, "act", a.tool, args, a.intent, sent=sent, rows=rows)
        fired = fire_due_events(B, run, row.get("ticks_after"), run_dir)
        write_run(run_dir, run)
    finally:
        B.close()
    print(json.dumps(res, default=str)[: a.max_chars])
    tail = "ok=%s bridge=%.0fms ticks+%s" % (row["ok"], row["bridge_ms"], row.get("ticks_advanced"))
    if row["flags"]:
        tail += " flags=" + ",".join(row["flags"])
    if fired:
        tail += " | EVENT fired: " + ", ".join(fired)
    print("--", tail)
    return 0


def observe_state(B, run):
    """Compact state. Reads only; internal (non-player-visible) reads are labelled."""
    rects = {k: tuple(v) for k, v in run["rects"].items()}
    site = rects["site"]
    out = {"ticksGame": ticks_of(B)}
    if out["ticksGame"] is not None and run.get("tick0") is not None:
        out["missionTicks"] = out["ticksGame"] - run["tick0"]
    col = B.call("rimworld/list_colonists", {"currentMapOnly": True})
    out["colonists"] = [{"id": c.get("pawnId") or c.get("id"), "name": c.get("name"),
                         "pos": c.get("position")} for c in (col.get("colonists") or [])][:8]
    try:
        ex = B.call("jawa/flowworks_excavation_rect", {"x": site[0], "z": site[1], "w": site[2], "h": site[3],
                                                       "onlyNonZero": True, "includeTerrain": False})
        rows = ex.get("rows") or []
        out["INTERNAL_excavation"] = {
            "dug": sum(1 for r in rows if r.get("isExcavated")),
            "dugAndFilled": sum(1 for r in rows if r.get("isExcavated") and (r.get("fEff") or 0) >= 1),
            "maxDepth": max([r.get("d") or 0 for r in rows] or [0])}
    except Exception as e:                     # noqa: BLE001
        out["INTERNAL_excavation"] = "UNMEASURED (%s)" % e
    for tool, key in (("rimworld/list_letters", "letters"), ("rimworld/list_messages", "messages"),
                      ("rimworld/list_alerts", "alerts")):
        try:
            r = B.call(tool, {"limit": 5})
            items = r.get(key) or []
            out[key] = [i.get("label") or i.get("text") or i.get("title") for i in items][:5]
        except Exception as e:                 # noqa: BLE001
            out[key] = "UNMEASURED (%s)" % e
    try:
        out["designator"] = B.call("rimworld/get_designator_state", {})
    except Exception as e:                     # noqa: BLE001
        out["designator"] = "UNMEASURED (%s)" % e
    if run["goal_check"]["kind"] == "prisoner":
        try:
            pr = B.call("jawa/pawn_roles", {"faction": "nonplayer", "limit": 50})
            out["prisoners"] = [p.get("id") for p in (pr.get("pawns") or []) if p.get("isPrisonerOfColony")]
        except Exception as e:                 # noqa: BLE001
            out["prisoners"] = "UNMEASURED (%s)" % e
    return out


def cmd_observe(a, spec):
    run_dir = current_run(a.run)
    run = read_run(run_dir)
    rows = read_actions(run_dir)
    B = bridge_for(run, run_dir)
    try:
        prev_end = rows[-1]["wall_end"] if rows else run["mission_start_wall"]
        w0 = CLOCK.wall()
        t0 = CLOCK.perf()
        st = observe_state(B, run)
        ms = (CLOCK.perf() - t0) * 1000
        shot, shot_ms = None, 0.0
        if a.shot:
            s = run["rects"]["site"]
            s0 = CLOCK.perf()
            try:
                B.call("jawa/clear_ui", {"devWindows": True, "clearSelection": False})
            except Exception:                  # noqa: BLE001
                pass
            r = B.call("rimworld/screenshot_cell_rect", {"x": s[0], "z": s[1], "width": s[2], "height": s[3],
                                                         "paddingCells": 2,
                                                         "fileName": "pm_%s_%d" % (run["mission"], len(rows))})
            shot_ms = (CLOCK.perf() - s0) * 1000
            shot = r.get("path") or r.get("screenshotPath") or r.get("filePath")
        if run["goal_check"]["kind"] == "prisoner" and isinstance(st.get("prisoners"), list) and st["prisoners"] \
                and run.get("prisoner_first_tick") is None:
            run["prisoner_first_tick"] = st["ticksGame"]
        fire_due_events(B, run, st.get("ticksGame"), run_dir)
        write_run(run_dir, run)
        append_action(run_dir, {"kind": "observe", "tool": "observe", "args": {"shot": bool(a.shot)}, "ok": True,
                                "wall_start": w0, "think_s": round(w0 - prev_end, 3), "bridge_ms": round(ms, 2),
                                "overhead_ms": 0.0, "shot": shot, "shot_ms": round(shot_ms, 2),
                                "ticks_before": st.get("ticksGame"), "ticks_after": st.get("ticksGame"),
                                "ticks_advanced": 0, "flags": [], "visible": False, "wall_end": CLOCK.wall()})
    finally:
        B.close()
    st["places"] = {k: rect_str(tuple(v)) for k, v in run["rects"].items()}
    if shot:
        st["screenshot"] = shot
    print(json.dumps(st, default=str)[: a.max_chars])
    return 0


NOTE_KINDS = ("abandoned_job", "unclear_feedback", "unexpected_consequence", "cannot_find", "agent_error",
              "transport_limitation", "other")


def cmd_note(a, spec):
    if a.kind not in NOTE_KINDS:
        raise SystemExit("kind must be one of %s" % (NOTE_KINDS,))
    run_dir = current_run(a.run)
    rows = read_actions(run_dir)
    w = CLOCK.wall()
    append_action(run_dir, {"kind": "note", "tool": None, "flags": [a.kind], "message": a.text, "wall_start": w,
                            "wall_end": w, "think_s": round(w - (rows[-1]["wall_end"] if rows else w), 3),
                            "agent_reported": True})
    print("noted %s" % a.kind)
    return 0


def goal_check(B, run):
    """PASS / FAIL / UNMEASURED with evidence. Reads game state; never the agent's word."""
    g = run["goal_check"]
    rects = {k: tuple(v) for k, v in run["rects"].items()}
    try:
        if g["kind"] == "canal":
            b = rects[g["band"]]
            ex = B.call("jawa/flowworks_excavation_rect", {"x": b[0], "z": b[1], "w": b[2], "h": b[3],
                                                           "onlyNonZero": True, "includeTerrain": False})
            if not ex.get("success", True) or "rows" not in ex:
                return "UNMEASURED", {"why": "excavation_rect answered without rows", "reply": str(ex)[:300]}
            good = [r for r in ex["rows"] if r.get("isExcavated") and (r.get("fEff") or 0) >= g["min_fill"]]
            ev = {"band": rect_str(b), "filledCanalCells": len(good), "needed": g["min_cells"]}
            return ("PASS" if len(good) >= g["min_cells"] else "FAIL"), ev
        if g["kind"] == "prisoner":
            pr = B.call("jawa/pawn_roles", {"faction": "nonplayer", "limit": 100})
            if "pawns" not in pr:
                return "UNMEASURED", {"why": "pawn_roles answered without pawns", "reply": str(pr)[:300]}
            held = [p.get("id") for p in pr["pawns"] if p.get("isPrisonerOfColony")]
            t = ticks_of(B)
            first = run.get("prisoner_first_tick")
            if held and first is None:
                first = t
            ev = {"prisoners": held, "firstSeenTick": first, "now": t, "holdTicks": g["hold_ticks"]}
            ok = bool(held) and first is not None and t is not None and t - first >= g["hold_ticks"]
            return ("PASS" if ok else "FAIL"), ev
        if g["kind"] == "chain":
            ev = {}
            far = rects[g["far_bank"]]
            col = B.call("rimworld/list_colonists", {"currentMapOnly": True})
            across = [c.get("name") for c in (col.get("colonists") or [])
                      if c.get("position") and in_rect(int(c["position"]["x"]), int(c["position"]["z"]), far)]
            ev["colonistsOnFarBank"] = across
            pw = B.call("jawa/list_pawns", {"faction": "player", "includeHealth": True})
            hurt = [p.get("name") for p in (pw.get("pawns") or [])
                    if any(h.get("isInjury") or "Drown" in str(h.get("def", "")) for h in
                           ((p.get("health") or {}).get("hediffs") or []))]
            ev["injuredColonists"] = hurt
            tanks = B.call("jawa/list_things", {"defName": g["tank_def"]})
            ev["tanks"] = len(tanks.get("things") or [])
            # tank volume: only player-visible channel is the inspect string "Holding: X (a / b units)";
            # selecting the tank to read it is UNVERIFIED live, so the units half reports UNMEASURED unless parsed.
            units = None
            for t in (tanks.get("things") or [])[:3]:
                pos = t.get("position") or {}
                B.call("rimworld/click_cell", {"x": pos.get("x"), "z": pos.get("z")})
                sem = json.dumps(B.call("rimworld/get_selection_semantics", {}))
                m = re.search(r"\((\d+(?:\.\d+)?) / (\d+(?:\.\d+)?) units\)", sem)
                if m:
                    units = max(units or 0, float(m.group(1)))
            ev["tankUnits"] = units if units is not None else "UNMEASURED (no 'Holding: ... units' inspect line read)"
            if units is None:
                return "UNMEASURED", ev
            ok = across and not hurt and units >= g["min_units"]
            return ("PASS" if ok else "FAIL"), ev
    except Exception as ex:                    # noqa: BLE001
        return "UNMEASURED", {"why": "%s: %s" % (type(ex).__name__, ex)}
    return "UNMEASURED", {"why": "unknown goal kind"}


def summarize(run, rows):
    acts = [r for r in rows if r["kind"] in ("act", "observe")]
    sum_ = lambda k, rs=acts: round(sum((r.get(k) or 0) for r in rs), 3)       # noqa: E731
    end = max([r["wall_end"] for r in rows] or [run["mission_start_wall"]])
    t = {"mission_wall_s": round(end - run["mission_start_wall"], 3),
         "fixture_s": run.get("fixture_s"),
         "bridge_s": round(sum_("bridge_ms") / 1000.0, 3),
         "overhead_s": round(sum_("overhead_ms") / 1000.0, 3),
         "think_s": sum_("think_s", [r for r in rows if r["kind"] in ("act", "observe", "note")]),
         "ticks_by_actions": sum_("ticks_advanced"),
         "ticks_during_think": sum_("ticks_during_think"),
         "screenshots": sum(1 for r in rows if r.get("shot")) +
                        sum(1 for r in acts if r.get("tool") in ("rimworld/take_screenshot", "rimworld/screenshot_cell_rect")),
         "screenshot_s": round((sum_("shot_ms") + sum((r.get("bridge_ms") or 0) for r in acts if r.get("tool") in
                               ("rimworld/take_screenshot", "rimworld/screenshot_cell_rect"))) / 1000.0, 3),
         "actions": sum(1 for r in rows if r["kind"] == "act"),
         "observes": sum(1 for r in rows if r["kind"] == "observe"),
         "refused": sum(1 for r in rows if r.get("refused")),
         "internal_reads": sum(1 for r in rows if r["kind"] == "act" and r.get("visible") is False)}
    by_cls = {}
    for r in rows:
        if r["kind"] != "act":
            continue
        ent = run_spec_cache.get("whitelist", {}).get(r["tool"]) or {}
        c = by_cls.setdefault(ent.get("cls", "refused" if r.get("refused") else "?"), {"n": 0, "bridge_s": 0.0,
                                                                                     "think_s": 0.0, "ticks": 0})
        c["n"] += 1
        c["bridge_s"] += (r.get("bridge_ms") or 0) / 1000.0
        c["think_s"] += r.get("think_s") or 0
        c["ticks"] += r.get("ticks_advanced") or 0
    t["by_class"] = {k: {kk: (round(vv, 3) if isinstance(vv, float) else vv) for kk, vv in v.items()}
                     for k, v in by_cls.items()}
    friction = [r for r in rows if set(r.get("flags") or []) - {"partial_placement"} or r.get("transport_limitation")]
    return t, friction


def cmd_report(a, spec):
    run_spec_cache.update(spec)
    run_dir = current_run(a.run)
    run = read_run(run_dir)
    rows = read_actions(run_dir)
    B = bridge_for(run, run_dir)
    try:
        verdict, ev = goal_check(B, run)
        tnow = ticks_of(B)
    finally:
        B.close()
    over = next((r["message"] for r in rows if r["kind"] == "deadline"), None)
    # A goal reached after the game-time deadline is not a PASS (a run printed PASS at 66,918 ticks vs 60,000):
    # the deadline gate only fires on the next action, so the report re-checks elapsed ticks itself.
    if over is None and tnow is not None and run.get("tick0") is not None and tnow - run["tick0"] > run["deadline"]["ticks"]:
        over = "game-time deadline %d ticks (mission ran %d)" % (run["deadline"]["ticks"], tnow - run["tick0"])
    if verdict in ("FAIL", "PASS") and over:
        verdict = "TIMEOUT"
    t, friction = summarize(run, rows)
    rep = {"run": run_dir, "mission": run["mission"], "dry_run": run["dry_run"], "verdict": verdict,
           "evidence": ev, "deadline": over, "timing": t,
           "friction": [{"i": rows.index(r), "kind": r["kind"], "tool": r.get("tool"), "flags": r.get("flags"),
                         "message": (r.get("message") or "")[:160], "intent": r.get("intent")} for r in friction]}
    with open(os.path.join(run_dir, "report.json"), "w", encoding="utf-8") as f:
        json.dump(rep, f, indent=1, default=str)
    if a.json:
        print(json.dumps(rep, indent=1, default=str))
        return 0
    print("MISSION %s  %s  verdict %s%s" % (run["mission"], "(DRY RUN, toy physics)" if run["dry_run"] else "",
                                             verdict, ("  [" + over + "]") if over else ""))
    print("evidence: %s" % json.dumps(ev, default=str))
    print("\nTIMING")
    for k in ("mission_wall_s", "fixture_s", "think_s", "bridge_s", "overhead_s", "ticks_by_actions",
              "ticks_during_think", "screenshots", "screenshot_s", "actions", "observes", "refused", "internal_reads"):
        print("  %-20s %s" % (k, t[k]))
    print("  %-10s %5s %9s %9s %8s" % ("class", "n", "bridge_s", "think_s", "ticks"))
    for k, v in sorted(t["by_class"].items()):
        print("  %-10s %5d %9.2f %9.2f %8d" % (k, v["n"], v["bridge_s"], v["think_s"], v["ticks"]))
    print("\nFRICTION (%d)" % len(friction))
    for f in rep["friction"]:
        print("  #%-3d %-7s %-38s %-34s %s" % (f["i"], f["kind"], f["tool"] or "", ",".join(f["flags"] or []),
                                             f["message"]))
    print("\nTRACE")
    for i, r in enumerate(rows):
        print("  #%-3d %-8s %-38s think %6.1fs bridge %7.0fms ticks+%-5s %s%s" % (
            i, r["kind"], (r.get("tool") or "")[:38], r.get("think_s") or 0, r.get("bridge_ms") or 0,
            r.get("ticks_advanced") if r.get("ticks_advanced") is not None else "-",
            "OK " if r.get("ok") else ("-- " if r["kind"] in ("note", "deadline", "event") else "NO "),
            (r.get("intent") or r.get("message") or "")[:70]))
    print("\nreport.json: %s" % os.path.join(run_dir, "report.json"))
    return 0


# ============================================================================ verify
def scan_source_tools(src=TOOLSRC):
    tools = {}
    for f in glob.glob(os.path.join(src, "*.cs")):
        s = open(f, encoding="utf-8", errors="replace").read()
        for m in re.finditer(r'\[Tool\(\s*"([^"]+)"', s):
            rest = s[m.end():]
            ps = rest.find("public static")
            if ps < 0:
                continue
            body = rest[ps:]
            e = re.search(r"\)\s*\{", body)
            sig = body[: e.end()] if e else body[:3000]
            tools[m.group(1)] = set(re.findall(r"\]\s*(?:int|string|bool|float|double|long)\??\s+(\w+)", sig))
    return tools


def load_dump(path=DUMP):
    if not os.path.exists(path):
        return None
    d = json.load(open(path, encoding="utf-8"))
    return {t["name"]: set((t.get("inputSchema") or {}).get("properties", {}).keys()) for t in d["tools"]}


def verify(spec, dump=None, source=None):
    """Re-derive every 'verified' claim. Returns (rows, problems). UNVERIFIED claims are reported, not failed."""
    dump = load_dump() if dump is None else dump
    source = scan_source_tools() if source is None else source
    rows, problems = [], []
    items = [(t, e["verified"], e["params"] + list(e.get("force", {}))) for t, e in spec["whitelist"].items()]
    items += [(t, v, []) for t, v in spec["fixture_tools"].items() if not t.startswith("_")]
    for tool, claim, params in items:
        in_dump = dump is not None and tool in dump
        in_src = tool in source
        miss_dump = sorted(set(params) - dump[tool]) if in_dump else None
        miss_src = sorted(set(params) - source[tool]) if in_src else None
        if in_dump and not miss_dump:
            got = "dump"
        elif in_src and not miss_src:
            got = "source"
        elif dump is None and not in_src:
            got = "UNMEASURED(no dump)"
        else:
            got = "NOT FOUND" if not (in_dump or in_src) else "PARAM MISMATCH %s" % (miss_dump or miss_src)
        rows.append((tool, claim, got))
        if claim in ("dump", "source") and got not in ("dump", "source") and not got.startswith("UNMEASURED"):
            problems.append("%s claims %s, measured %s" % (tool, claim, got))
        if claim == "UNVERIFIED" and got.startswith(("NOT FOUND", "PARAM")):
            problems.append("%s (UNVERIFIED) is not even present: %s" % (tool, got))
    return rows, problems


def cmd_verify(a, spec):
    rows, problems = verify(spec)
    for tool, claim, got in rows:
        print("  %-40s claim %-10s measured %s" % (tool, claim, got))
    print("%d tools, %d problems" % (len(rows), len(problems)))
    for p in problems:
        print("  PROBLEM %s" % p)
    return 1 if problems else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--run", help="run dir (default: Transient/player_missions/CURRENT)")
    ap.add_argument("--runs", help=argparse.SUPPRESS)
    ap.add_argument("--max-chars", type=int, default=4000)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("start")
    s.add_argument("mission")
    s.add_argument("--dry-run", action="store_true")
    s.add_argument("--anchor", help="x,z site centre (default: map centre)")
    s.add_argument("--skip-fixture", action="store_true", help="the map is already prepared")
    o = sub.add_parser("observe")
    o.add_argument("--shot", action="store_true")
    c = sub.add_parser("act")
    c.add_argument("tool")
    c.add_argument("args", nargs="?", default="{}")
    c.add_argument("--intent")
    n = sub.add_parser("note")
    n.add_argument("kind")
    n.add_argument("text")
    r = sub.add_parser("report")
    r.add_argument("--json", action="store_true")
    sub.add_parser("verify")
    a = ap.parse_args(argv)
    spec = load_spec()
    run_spec_cache.update(spec)
    if a.runs and a.run is None and a.cmd != "start":
        a.run = current_run_in(a.runs)
    return {"start": cmd_start, "observe": cmd_observe, "act": cmd_act, "note": cmd_note,
            "report": cmd_report, "verify": cmd_verify}[a.cmd](a, spec)


def current_run_in(runs):
    with open(os.path.join(runs, "CURRENT"), encoding="utf-8") as f:
        return os.path.join(runs, f.read().strip())


if __name__ == "__main__":
    sys.exit(main())
