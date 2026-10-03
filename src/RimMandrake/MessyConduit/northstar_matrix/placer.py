"""Deterministic scene PLACER spec: the bridge calls the live runner makes to build one scene. Emitted, never run.

    plan(scene, case, origin=(X0, Z0)) -> {"site", "to_game", "steps": [...], "expect_game": {...}}

Step kinds:
  {"kind": "probe", "cmd": "set:style=StarWarsJawa"}  -> MessyConduitProbe via jawa/mod_settings_field (validation.py
                                                         Bridge.probe: set `request`, wait for `serial` to change)
  {"kind": "tool",  "tool": "jawa/build_batch", "args": {...}}
  {"kind": "resolve_thing", "def": "Battery", "cell": [gx, gz], "as": "$src"}   -> jawa/list_things, keep the id
  {"kind": "unbuilt", "what": ..., "why": ...}          -> nothing exists to call yet: the runner records UNBUILT
                                                           (only for things with no tool/mod hook: switch flick, aerial masts)
  {"kind": "hose_probe", "cmd": "lay:rx,rz,fx,fz"}     -> HoseProbe via jawa/mod_settings_field (validation_hose.py H.hp:
                                                         set `request`, wait for `serial`); cmds lay: check: flow:x,z=on defaults
  {"kind": "hose_census", "reel": [x, z], "expect": {...}}  -> HoseProbe census, pick the hose whose `reel` is [x, z]
  {"kind": "census" | "screenshot" | "cleanup", ...}

The recipe is validation.py's proven one (live passes 1-2, 2026-10-02): destroy_batch All -> Soil -> unfog -> unroof
-> walls/doors (Steel) -> conduit -> batteries -> battery_set setPct -> connectors -> map_commit -> frame -> 2 ticks
-> census. Order matters in game: connectors pick their transmitter when THEY spawn (PowerConnectionMaker:
nearest wire-able transmitter by squared distance), so every conduit and transmitter is built before any connector.
The break axis is realised by NOT building the break cell (same end state as building it and destroying it).
Coordinates: scene (x, y-south) -> game (X0 + x, Z0 + (h - 1 - y)), north up, so a screenshot reads like the scene.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
SCHEMAS = os.path.join(REPO, "src", "RimMandrake", "Utils", "northstar_driver", "tool_schemas.json")
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import scenes as S  # noqa: E402

STYLE_ENUM = {"jawa": "StarWarsJawa", "extcord": "ExtensionCord", "cybertek": "Cybertek", "starwars": "StarWars"}
STYLE_ART_INSTALLED = {"jawa": True, "extcord": False, "cybertek": False, "starwars": False}   # validation.py U_other_styles
PROVEN = {
    "jawa/destroy_batch": "validation.py live 1-2", "jawa/set_terrain_batch": "validation.py (Soil); FlowWorks (WaterDeep)",
    "jawa/set_fog": "validation.py", "jawa/set_roof_batch": "validation.py", "jawa/build_batch": "validation.py",
    "jawa/battery_set": "validation.py", "jawa/map_commit": "validation.py", "rimworld/frame_cell_rect": "validation.py",
    "rimworld/step_game_ticks": "validation.py", "jawa/list_things": "validation.py",
    "rimworld/screenshot_cell_rect": "PlantGrowth / live-review", "jawa/set_plants": "RimUtinni/PlantGrowth/validation.py",
    "jawa/weather_set": "schema only (args from tool_schemas.json)",
}
UNVERIFIED = [
    "WaterproofConduit on WaterDeep: its def needs WaterproofConduitable affordance (shallow water/mud); build_batch "
    "spawns may or may not bypass it -- check the conduit build's `survived` count; if refused, the canal cases "
    "need the water painted AFTER the conduit, or shallow water (walkable: then no water stubs, re-run the oracle)",
    "Granite spawned by build_batch on cleared soil: proven to spawn (live pass 2) but reads as a grey slab",
    "WoodFiredGenerator spawns unfuelled (active=False in every scene): its node must census as 'source' while "
    "its net's liveness comes from the battery",
]


REEL_DEF = "RM_HoseReel"
TRANSITION_TICKS = 30            # HoseSettings.transitionTicks default; the census reports the live value


def hose_steps(reel, far, state):
    """Steps run AFTER map_commit + 2 ticks, the call shapes of validation_hose.py (12/12 PASS live): install-validity
    check, lay, 2 ticks, then drive the flow signal to the wanted state and read the census. Flat: no flow, a 300-tick
    settle. Plump: flow on, transition + 5 ticks. Filling (the Filling50 row): flow on, HALF a transition (blend ~0.5)."""
    rf = "%d,%d,%d,%d" % (reel[0], reel[1], far[0], far[1])
    st = [{"kind": "hose_probe", "cmd": "check:" + rf, "expect_reason": None},
          {"kind": "hose_probe", "cmd": "lay:" + rf},
          {"kind": "tool", "tool": "rimworld/step_game_ticks", "args": {"ticks": 2, "pauseFirst": True, "timeoutMs": 120000}}]
    if state == "Flat":
        st.append({"kind": "tool", "tool": "rimworld/step_game_ticks", "args": {"ticks": 300, "pauseFirst": True, "timeoutMs": 120000},
                   "why": "no flow: stays Flat (validation_hose H5 settles 300 ticks)"})
    else:
        st.append({"kind": "hose_probe", "cmd": "flow:%d,%d=on" % (reel[0], reel[1])})
        n = TRANSITION_TICKS // 2 if state == "Filling" else TRANSITION_TICKS + 5
        st.append({"kind": "tool", "tool": "rimworld/step_game_ticks", "args": {"ticks": n, "pauseFirst": True, "timeoutMs": 120000},
                   "why": "%s: H6 steps transitionTicks//2 for the mid read, transitionTicks for Plump" % state})
    st.append({"kind": "hose_census", "reel": list(reel), "state": state})
    return st


def hose_plan(sc, origin):
    """Plan for one DESIGN hose scene (design_spec.hose_spec): its ops are plot-local game cells (north up already), so
    game = origin + cell. Returns {"site", "steps", "reel", "far", "expect"}; `expect` is the scene's own intrinsic row."""
    X0, Z0 = origin
    w, h = sc["plot"][2], sc["plot"][3]
    site = [X0 - 1, Z0 - 1, w + 2, h + 2]
    rect = "%d,%d,%d,%d" % tuple(site)
    steps = []

    def tool(t, **args):
        steps.append({"kind": "tool", "tool": t, "args": args})
    g = lambda c: [X0 + c[0], Z0 + c[1]]  # noqa: E731
    tool("jawa/destroy_batch", rects=rect, categories="All")
    tool("jawa/set_terrain_batch", ops="Soil:" + rect)
    tool("jawa/set_fog", action="unfog", rect=rect)
    tool("jawa/set_roof_batch", ops="None:" + rect)
    reel = far = state = None
    for op in sc["build"]:
        if op["op"] == "terrain" and op["def"] != "Soil":
            tool("jawa/set_terrain_batch", ops=";".join("%s:%d,%d,1,1" % ((op["def"],) + tuple(g(c))) for c in op["cells"]))
        elif op["op"] == "build":
            tool("jawa/build_batch", ops=_ops(op["def"], [g(c) for c in op["cells"]]), stuff=op["stuff"], faction="player",
                 wipeExisting=False)
        elif op["op"] == "debug_hose":
            reel, far, state = g(op["a"]), g(op["b"]), op["force_state"]
    tool("jawa/build_batch", ops=_ops(REEL_DEF, [reel]), faction="player", wipeExisting=False)
    tool("jawa/map_commit")
    tool("rimworld/step_game_ticks", ticks=2, pauseFirst=True, timeoutMs=120000)
    steps += hose_steps(reel, far, state)
    for k, s in enumerate(steps):
        s["n"] = k
    return {"origin": [X0, Z0], "site": site, "steps": steps, "reel": reel, "far": far, "state": state,
            "expect": sc["expect"]["intrinsic"]}


class Mapper(object):
    def __init__(self, sc, origin):
        self.X0, self.Z0 = origin
        self.h = sc["h"]

    def g(self, p):
        return [self.X0 + p[0], self.Z0 + (self.h - 1 - p[1])]


def _ops(defn, cells, rot=None):
    return ";".join("%s:%d,%d%s" % (defn, c[0], c[1], "" if rot is None else ",%d" % rot) for c in cells)


def plan(sc, case, origin=(150, 150)):
    M = Mapper(sc, origin)
    W, H = sc["w"], sc["h"]
    site = [origin[0] - 2, origin[1] - 2, W + 4, H + 4]
    rect = "%d,%d,%d,%d" % tuple(site)
    steps = []

    def tool(t, why=None, **args):
        s = {"kind": "tool", "tool": t, "args": args}
        if why:
            s["why"] = why
        steps.append(s)
    lv = __import__("oracle").LEVELS[case["tangle"]]
    steps.append({"kind": "probe", "cmd": "defaults"})
    steps.append({"kind": "probe", "cmd": "set:style=%s" % STYLE_ENUM[case["style"]]})
    for k in ("slack", "sprawlCap", "cordsPerConnection"):
        steps.append({"kind": "probe", "cmd": "set:%s=%s" % (k, lv[k])})
    steps.append({"kind": "probe", "cmd": "set:tangles=True"})
    tool("jawa/destroy_batch", rects=rect, categories="All")
    tool("jawa/set_terrain_batch", ops="Soil:" + rect)
    tool("jawa/set_fog", action="unfog", rect=rect)
    tool("jawa/set_roof_batch", ops="None:" + rect)
    water = [M.g(p) for p in sc["water"]]
    if water:
        tool("jawa/set_terrain_batch", ops=";".join("WaterDeep:%d,%d,1,1" % tuple(c) for c in water))
    if sc["rock"]:
        tool("jawa/build_batch", ops=_ops("Granite", [M.g(p) for p in sc["rock"]]))
    if sc["walls"]:
        tool("jawa/build_batch", ops=_ops("Wall", [M.g(p) for p in sc["walls"]]), stuff="Steel", faction="player")
    if sc["doors"]:
        tool("jawa/build_batch", ops=_ops("Door", [M.g(p) for p in sc["doors"]]), stuff="Steel", faction="player")
    wset = {tuple(p) for p in sc["water"]}
    dry = [M.g(p) for p in sc["conduit"] if tuple(p) not in wset]
    wet = [M.g(p) for p in sc["conduit"] if tuple(p) in wset]
    tool("jawa/build_batch", ops=_ops("PowerConduit", dry), faction="player", wipeExisting=False,
         why="expect survived == %d" % len(dry))
    if wet:
        tool("jawa/build_batch", ops=_ops("WaterproofConduit", wet), faction="player", wipeExisting=False,
             why="expect survived == %d (UNVERIFIED on WaterDeep)" % len(wet))
    devs = sorted(sc["devices"], key=lambda d: (not S.DEVICE_DEFS[d["role"]]["transmitter"], d["id"]))
    dev_game = {}
    for d in devs:
        r = S.DEVICE_DEFS[d["role"]]
        gp = M.g(S.game_position(d))
        dev_game[d["id"]] = gp
        rot = 0 if d["role"] in ("battery", "bench") else None
        if not r["transmitter"] and not any(s.get("_tx_done") for s in steps):
            steps.append({"kind": "note", "_tx_done": True,
                          "text": "all conduit + transmitters are down: connectors from here wire to their nearest"})
        tool("jawa/build_batch", ops=_ops(r["def"], [gp], rot), faction="player",
             why="%s %s at game Position %s" % (d["role"], d["id"], gp))
        if d["role"] == "battery":
            var = "$" + d["id"]
            steps.append({"kind": "resolve_thing", "def": "Battery", "cell": gp, "as": var})
            tool("jawa/battery_set", thing=var, mode="setPct", value=1.0 if d.get("charged") else 0.0)
        if d["role"] == "switch" and not d.get("on", True):
            steps.append({"kind": "unbuilt", "what": "flick %s off" % d["id"],
                          "why": "no bridge tool flicks a CompFlickable (NEEDED_TOOL)"})
    if sc["trees"]:
        tool("jawa/set_plants", ops=";".join("Plant_TreeOak:%d,%d,1,1" % tuple(M.g(p)) for p in sc["trees"]),
             growth=1.0, density=1.0)
    if sc.get("aerial"):
        a = sc["aerial"]
        steps.append({"kind": "unbuilt", "what": "aerial: %d RM_AerialMast at %s, spans %s, cut %s" % (
            len(a["poles"]), [M.g(p) for p in a["poles"]], a["spans"], a["cut"]),
            "why": "RM_AerialMast / CompAerialAnchor not built (phase-2 design section 2.3); floor part IS built"})
    hose_after = []
    if sc.get("hose"):
        hs = sc["hose"]
        reel, far = M.g(hs["cells"][0]), M.g(hs["cells"][-1])
        tool("jawa/build_batch", ops=_ops(REEL_DEF, [reel]), faction="player", wipeExisting=False,
             why="hose strip: reel at %s, far end %s (%d cells, %s)" % (reel, far, len(hs["cells"]), hs["inflation"]))
        hose_after = hose_steps(reel, far, "Plump" if hs["inflation"] == "plump" else "Flat")
    tool("jawa/map_commit")
    tool("rimworld/frame_cell_rect", x=site[0], z=site[1], width=site[2], height=site[3], paddingCells=1)
    tool("rimworld/step_game_ticks", ticks=2, pauseFirst=True, timeoutMs=120000,
         why="power nets and connector hookups form on the next tick (validation.py LEARNED)")
    steps += hose_after
    steps.append({"kind": "census", "cmd": "census", "compare": "oracle.graph via expect_game"})
    tool("rimworld/screenshot_cell_rect", x=site[0], z=site[1], width=site[2], height=site[3], paddingCells=1,
         fileName="%s.png" % sc["name"])
    # the OFF frame of the same view: the only pixel evidence that cords are present (contact_sheet.py
    # wire_evidence); master off restores vanilla art with no restart (validation.py M7, proven live)
    steps.append({"kind": "probe", "cmd": "set:enabled=False"})
    tool("rimworld/screenshot_cell_rect", x=site[0], z=site[1], width=site[2], height=site[3], paddingCells=1,
         fileName="%s_off.png" % sc["name"], why="same camera, same tick: contact_sheet pairs it with the ON frame")
    steps.append({"kind": "probe", "cmd": "set:enabled=True"})
    steps.append({"kind": "cleanup", "tool": "jawa/destroy_batch", "args": {"rects": rect, "categories": "All"}})
    for s in steps:
        s.pop("_tx_done", None)
    for k, s in enumerate(steps):
        s["n"] = k
    return {"origin": list(origin), "site": site, "to_game": "gx = X0 + x; gz = Z0 + (%d - 1 - y)" % H,
            "style_art_installed": STYLE_ART_INSTALLED[case["style"]], "steps": steps,
            "expect_game": expect_game(sc, M, dev_game)}


def expect_game(sc, M, dev_game):
    """The oracle's cell-keyed answers in GAME coordinates (what the census `ends` and node cells carry)."""
    import oracle as O
    g = O.expect(sc)
    return {"terminals": sorted([M.g((t[0], t[1])) + [t[2]] for t in g["terminals"]]),
            "wall_terminals": sorted([M.g((t[0], t[1])) + [t[2]] for t in g["wall_terminals"]]),
            "break_cell": M.g(sc["break_cell"]) if sc.get("break_cell") else None,
            "device_positions": dev_game}


def load_schemas(path=SCHEMAS):
    with open(path, encoding="utf-8") as f:
        return json.load(f)["tools"]


def check_plan(pl, tools=None):
    """Every tool step names a tool in the live tool_schemas.json snapshot with only declared parameters and every
    required one present. [] = clean."""
    tools = tools or load_schemas()
    probs = []
    calls = [(s["tool"], s["args"]) for s in pl["steps"] if s["kind"] == "tool"]
    calls += [(s["tool"], s["args"]) for s in pl["steps"] if s["kind"] == "cleanup"]
    calls += [("jawa/mod_settings_field", {"typeName": 1, "action": 1, "field": 1, "value": 1})
              for s in pl["steps"] if s["kind"] in ("probe", "census")]
    calls += [("jawa/mod_settings_field", {"typeName": 1, "action": 1, "field": 1, "value": 1})
              for s in pl["steps"] if s["kind"] in ("hose_probe", "hose_census")]
    calls += [("jawa/list_things", {"defName": 1, "limit": 1}) for s in pl["steps"] if s["kind"] == "resolve_thing"]
    for t, args in calls:
        if t not in tools:
            probs.append("UNKNOWN_TOOL %s" % t)
            continue
        decl = set(tools[t].get("parameters") or [])
        req = set(tools[t].get("required") or [])
        for k in args:
            if k not in decl:
                probs.append("UNDECLARED_PARAM %s.%s" % (t, k))
        for k in req - set(args):
            probs.append("MISSING_REQUIRED %s.%s" % (t, k))
    return probs
