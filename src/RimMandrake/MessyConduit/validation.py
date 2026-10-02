"""validation.py -- Messy Conduit functional script (debug_process.md section 2), phase 1a.

Walk: design/validation_walks/RimMandrake/MessyConduit.md (## must be true lines M1..M9).
Design: design/RimMandrake/messy_conduit_design_2026-10-02.md (section 5 "First functional script").

    python3    src/RimMandrake/MessyConduit/validation.py                 # offline tier, 0 ticks
    python.exe src/RimMandrake/MessyConduit/validation.py --live --fresh-map   # messyconduit tier, bridge held

Offline tier: O1 mod files (About, csproj Compile list == every Source/*.cs outside SelfTest, DLL +
.srchash, textures, the transparent conduit PNG all-zero), O2 settings defaults == shipped table,
O3 C# core SelfTest against the Python oracle (selftest_messyconduit.py) + its --probe (a planted
mismatch must turn every scene red), O4 the Python oracle's own selftest.

Live tier (one fresh quicktest map, ~270 ticks total): a battery, a 9x7 walled room with a door,
a conduit run through the doorway and into the room, a branch, a lamp, a run INTO the east wall,
and a far-away isolated conduit run for the local-invalidation check. State is read through
MessyConduitProbe (written and read with the existing jawa/mod_settings_field tool; the mod's map
component answers on its next frame), never from screenshots.

LEARNED (seed; each line is a check below, not prose only):
  * Power nets and connector hookups are made on the next TICK (PowerNetManager in MapPreTick), so
    every build is followed by step_game_ticks 2 before a census; a census on a paused fresh build
    sees no nets and every cord edge reads "without net".
  * A spawned battery is EMPTY and an empty battery is not an active power source: battery_set
    setPct 1 makes the net live, setPct 0 makes it dead (the source-off negative, M8).
  * Run 1 (2026-10-02) FAILED M1_node_census with the MOD right and the SCENE wrong: the lamp hooked
    onto the main run, so the 2-cell branch was a needless spur (design 8.7.5, pruned into a loop) and
    the into-wall run touched the main run only diagonally (a separate dead net). Scene fixed; the
    census row now also requires a wall terminal on the LIVE net.
  * Run 2: layerVerts 0 and overlayConnectorVerts 0 with every graph row green -- the camera was
    elsewhere and off-screen sections never regenerate. The script now frames the scene first.
  * First screenshots (run 3): every decal (plug, junction, grommet, frayed end) printed but at a third
    of a cell they read as specks; the art fills ~60% of its canvas. Scales doubled; M1c counts them.
  * HARNESS: status.mod_hash takes the mod DIRECTORY (a bare "MessyConduit" hashed nothing:
    e3b0c442...), and results must land in northstar/ (excluded from the hash) or each run's own
    output makes the next record STALE.
RULED OUT: (none yet)
"""
import glob
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
UTILS = os.path.join(REPO, "src", "RimMandrake", "Utils")
MOD = "MessyConduit"
PKG = "mandrake.rm.messyconduit"
TIER = "messyconduit"
PROBE = "RimMandrake.MessyConduit.MessyConduitProbe"
SETTINGS = "RimMandrake.MessyConduit.MessyConduitSettings"
TRANSPARENT = "RimMandrake/MessyConduit/ConduitTransparent"

SHIPPED = {"enabled": "true", "style": "CordStyle.StarWarsJawa", "slack": "1f", "sprawlCap": "16f",
           "cordsPerConnection": "3", "tangles": "true", "needlessLoops": "true", "breakReadout": "true",
           "sparkIntensity": "1f", "hideHookupWires": "true", "debugDraw": "false"}

# Bars this phase does not build or this short tier does not reach. Honest, named, never PASS.
UNBUILT = [
    ("U_whip_tails", "UNBUILT", "live tails whip (phase 1b); 1a tails are static, live = straight + sparks"),
    ("U_downed_wire_bursts", "UNBUILT", "wall-terminal drip/flash schedule (phase 1b); 1a uses the plain spark poll"),
    ("U_pbd_settle", "UNBUILT", "rope settle / SDF (phase 1b); 1a lays canned loops + smoothing"),
    ("U_selection_highlight", "UNBUILT", "selecting a conduit highlights its net's cords (design 8.3, phase 1b)"),
    ("U_sway", "UNBUILT", "CutoutPlant sway (phase 2)"),
    ("U_other_styles", "UNBUILT", "Extension cord / Cybertek / Star Wars art families (art not installed)"),
    ("M4_save_load_hash", "UNCOVERED", "walk M4: same polylines after save/load -- not run in the short tier"),
    ("M9_remove_mod_clean", "UNCOVERED", "walk M9: a save made with the mod loads clean without it -- not run"),
]


class Row(dict):
    pass


def row(rows, rid, status, cls, detail):
    rows.append({"id": rid, "status": status, "class": cls, "detail": detail})
    print("%-28s %-9s %s" % (rid, status, str(detail)[:150]), flush=True)


# ============================================================================ offline
def o1_files(rows):
    probs = []
    about = open(os.path.join(HERE, "About", "About.xml"), encoding="utf-8").read()
    if "<packageId>%s</packageId>" % PKG not in about:
        probs.append("About packageId")
    if "brrainz.harmony" not in about:
        probs.append("About lacks Harmony dependency")
    csproj = open(os.path.join(HERE, "Source", "RimMandrake_MessyConduit.csproj"), encoding="utf-8").read()
    srcs = sorted(os.path.relpath(p, os.path.join(HERE, "Source")).replace("/", "\\")
                  for p in glob.glob(os.path.join(HERE, "Source", "**", "*.cs"), recursive=True)
                  if "SelfTest" not in p and "/obj/" not in p and "/bin/" not in p)
    missing = [s for s in srcs if '<Compile Include="%s" />' % s not in csproj]
    if missing:
        probs.append("csproj misses Compile lines (they would compile into nothing): %s" % missing)
    dll = os.path.join(HERE, "Assemblies", "RimMandrakeMessyConduit.dll")
    if not (os.path.exists(dll) and os.path.exists(dll + ".srchash")):
        probs.append("DLL or .srchash missing")
    tex = os.path.join(HERE, "Textures", "RimMandrake", "MessyConduit")
    want = ["ConduitTransparent", "Strand_Jawa", "StrandShadow", "Plug", "Junction_Tape", "Junction_Tin",
            "StubWall", "StubRock", "PowerStrip", "EndFrayed_Dead", "EndFrayed_Live"]
    gone = [w for w in want if not os.path.exists(os.path.join(tex, w + ".png"))]
    if gone:
        probs.append("textures missing: %s" % gone)
    try:
        from PIL import Image
        im = Image.open(os.path.join(tex, "ConduitTransparent.png")).convert("RGBA")
        if any(hi != 0 for _, hi in im.getextrema()):
            probs.append("ConduitTransparent.png is not all-zero: %s" % (im.getextrema(),))
    except Exception as ex:  # noqa: BLE001
        probs.append("transparent PNG unreadable: %s" % ex)
    row(rows, "O1_mod_files", "PASS" if not probs else "FAIL", "MOD", probs or "%d sources compiled, %d textures" % (len(srcs), len(want)))


def o2_defaults(rows):
    src = open(os.path.join(HERE, "Source", "MessyConduitMod.cs"), encoding="utf-8").read()
    bad = []
    for f, v in SHIPPED.items():
        needle = " %s = %s;" % (f, v)
        if needle not in src:
            bad.append("%s != %s" % (f, v))
    row(rows, "O2_settings_defaults", "PASS" if not bad else "FAIL", "MOD", bad or "%d defaults match the shipped table" % len(SHIPPED))


def o3_csharp_selftest(rows):
    r = subprocess.run([sys.executable, os.path.join(UTILS, "selftest_messyconduit.py")], capture_output=True, text=True,
                       timeout=600)
    tail = [ln for ln in r.stdout.splitlines() if "checks passed" in ln or ln.startswith("FAIL")]
    row(rows, "O3_core_selftest", "PASS" if r.returncode == 0 else "FAIL", "MOD", tail[-6:] or r.stderr[-300:])
    r2 = subprocess.run([sys.executable, os.path.join(UTILS, "selftest_messyconduit.py"), "--probe", "--no-export"],
                        capture_output=True, text=True, timeout=600)
    pl = [ln for ln in r2.stdout.splitlines() if ln.startswith("PROBE")]
    row(rows, "O3n_selftest_can_fail", "PASS" if r2.returncode == 0 and pl else "FAIL", "HARNESS", pl or r2.stdout[-300:])


def o4_oracle(rows):
    r = subprocess.run([sys.executable, os.path.join(UTILS, "mockups", "messy_conduit", "selftest.py")],
                       capture_output=True, text=True, timeout=600)
    last = (r.stdout.strip().splitlines() or ["?"])[-1]
    row(rows, "O4_python_oracle", "PASS" if r.returncode == 0 else "FAIL", "HARNESS", last)


def run_offline():
    rows = []
    o1_files(rows)
    o2_defaults(rows)
    o3_csharp_selftest(rows)
    o4_oracle(rows)
    return rows


# ============================================================================ live
class Bridge(object):
    def __init__(self):
        sys.path.insert(0, UTILS)
        import rimbridge_client as rb  # noqa: E402
        host, port, token = rb.resolve_endpoint()
        self.S = rb.RimBridge(host=host, port=port, token=token, timeout=600.0)
        self.S.connect()

    def call(self, tool, **kw):
        r = self.S.call(tool, kw, check=False) or {}
        if isinstance(r, dict) and r.get("content"):
            try:
                r = json.loads(r["content"][0]["text"])
            except Exception:  # noqa: BLE001
                pass
        return r if isinstance(r, dict) else {"success": False, "raw": r}

    def probe(self, cmd, wait_s=20.0):
        before = self.call("jawa/mod_settings_field", typeName=PROBE, action="get", field="serial").get("value")
        s = self.call("jawa/mod_settings_field", typeName=PROBE, action="set", field="request", value=cmd)
        if not s.get("success"):
            return {"success": False, "error": "probe set failed", "raw": s}
        t0 = time.time()
        while time.time() - t0 < wait_s:
            now = self.call("jawa/mod_settings_field", typeName=PROBE, action="get", field="serial").get("value")
            if now != before:
                res = self.call("jawa/mod_settings_field", typeName=PROBE, action="get", field="result").get("value")
                try:
                    return json.loads(res)
                except Exception:  # noqa: BLE001
                    return {"success": False, "raw": res}
            time.sleep(0.3)
        return {"success": False, "error": "probe timed out (no frame serviced it)"}

    def ticks(self, n):
        return self.call("rimworld/step_game_ticks", ticks=n, pauseFirst=True, timeoutMs=120000)


# The scene, absolute cells on a fresh quicktest map (centre 125,125 avoided: colonists stand there).
X0, Z0 = 150, 150
SITE = (X0 - 2, Z0 - 2, 34, 14)                   # cleared + painted Soil + unfogged
ROOM = (X0 + 10, Z0, X0 + 18, Z0 + 6)              # wall perimeter x0,z0,x1,z1
DOOR = (X0 + 10, Z0 + 3)
BATTERY = (X0 + 2, Z0 + 3)                         # Battery 1x2, rot N: cells z..z+1
MAIN = [(x, Z0 + 3) for x in range(X0 + 3, X0 + 18)]        # through the door, across the room
BRANCH = [(X0 + 13, Z0 + 4), (X0 + 13, Z0 + 5)]               # north branch -> lamp (its hookup keeps it)
INTO_WALL = [(X0 + 17, Z0 + 2), (X0 + 18, Z0 + 2)]            # off the main run's end, INTO the east wall (ends inside)
LAMP = (X0 + 12, Z0 + 5)                                      # nearest conduit = the branch end
FAR = [(X0 + 28, Z0 + 9), (X0 + 29, Z0 + 9)]                  # isolated far-away run (local invalidation)
GAP = (X0 + 7, Z0 + 3)                                        # the conduit cell destroyed for the break


def perimeter(x0, z0, x1, z1):
    out = []
    for x in range(x0, x1 + 1):
        out += [(x, z0), (x, z1)]
    for z in range(z0 + 1, z1):
        out += [(x0, z), (x1, z)]
    return out


def ops(defn, cells, rot=None):
    return ";".join("%s:%d,%d%s" % (defn, c[0], c[1], "" if rot is None else ",%d" % rot) for c in cells)


def run_live(args):
    B = Bridge()
    rows, log = [], []
    res = {"mod": MOD, "mode": "live", "tier": TIER, "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows}
    if args.fresh_map:
        B.call("rimworld/go_to_main_menu")
        r = B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
        st = None
        for _ in range(90):
            st = B.call("rimworld/get_ui_state").get("programState")
            if st == "Playing" and B.call("jawa/map_info").get("success"):
                break
            time.sleep(2)
        row(rows, "L0_fresh_map", "PASS" if st == "Playing" else "FAIL", "SITE", {"start": r.get("success"), "programState": st})
        if st != "Playing":
            res["aborted"] = "no fresh map"
            return res
    # environment fingerprint for `modcheck record`
    env = {}
    rm = B.call("jawa/running_mods", assembly="RimMandrakeMessyConduit", details=False)
    if rm.get("success"):
        import hashlib
        env["running"] = [p.lower() for p in rm.get("packageIds") or []]
        env["running_sha256"] = hashlib.sha256("\n".join(env["running"]).encode("utf-8")).hexdigest()
        ms = (rm.get("assembly") or {}).get("matches") or []
        env["assembly_matches"] = len(ms)
    res["env"] = env
    try:
        sys.path.insert(0, os.path.join(UTILS, "modcheck"))
        import status as _mc  # noqa: E402
        res["mod_hash"] = _mc.mod_hash(HERE)          # the mod DIR; a bare name hashes nothing
    except Exception as ex:  # noqa: BLE001
        res["mod_hash"] = None
        log.append("mod_hash unavailable: %s" % ex)
    row(rows, "L1_tier_running", "PASS" if PKG in env.get("running", []) else "FAIL", "SITE",
        "%d mods running, messyconduit %s" % (len(env.get("running", [])), PKG in env.get("running", [])))
    lg0 = B.call("rimbridge/list_logs", limit=500, minimumLevel="warning")
    logs0 = lg0.get("logs") or []
    log_base = max([x.get("Sequence", 0) for x in logs0] or [0])
    bridge_line = any("[RimBridge]" in (x.get("Message") or "") for x in logs0)
    pre = [x.get("Message", "")[:200] for x in logs0 if "MessyConduit" in (x.get("Message", "") + x.get("StackTrace", ""))
           and (x.get("Level") or "").lower() in ("error", "exception")]
    row(rows, "L2_startup_log_clean", ("PASS" if not pre else "FAIL") if bridge_line else "UNMEASURED", "MOD",
        pre or "no MessyConduit error in %d warn+ startup entries (sanity: [RimBridge] line seen=%s)" % (len(logs0), bridge_line))
    pd = B.probe("defaults")
    if not pd.get("success"):
        res["aborted"] = "probe channel dead: %s" % pd
        row(rows, "L3_probe_channel", "FAIL", "HARNESS", pd)
        return res
    t_start = B.probe("census").get("ticksGame")

    # ---------------------------------------------------------------- site and scene
    x, z, w, h = SITE
    B.call("jawa/destroy_batch", rects="%d,%d,%d,%d" % SITE, categories="All")
    B.call("jawa/set_terrain_batch", ops="Soil:%d,%d,%d,%d" % SITE)
    B.call("jawa/set_fog", action="unfog", rect="%d,%d,%d,%d" % SITE)
    B.call("jawa/set_roof_batch", ops="None:%d,%d,%d,%d" % SITE)      # a quicktest map can land on roofed ruins
    walls = [c for c in perimeter(*ROOM) if c != DOOR]
    b1 = B.call("jawa/build_batch", ops=ops("Wall", walls), stuff="Steel", faction="player")
    b2 = B.call("jawa/build_batch", ops="Door:%d,%d" % DOOR, stuff="Steel", faction="player")
    b3 = B.call("jawa/build_batch", ops="Battery:%d,%d,0" % BATTERY, faction="player")
    cond = MAIN + BRANCH + INTO_WALL + FAR
    b4 = B.call("jawa/build_batch", ops=ops("PowerConduit", cond), faction="player", wipeExisting=False)
    b5 = B.call("jawa/build_batch", ops="StandingLamp:%d,%d" % LAMP, faction="player")
    built = {k: (v.get("survived"), len(v.get("failed") or [])) for k, v in
             dict(walls=b1, door=b2, battery=b3, conduit=b4, lamp=b5).items()}
    bat_id = None
    for t in (b3.get("things") or b3.get("readBack") or []):
        if "Battery" in str(t.get("defName", "")):
            bat_id = t.get("id") or t.get("thingId")
    if not bat_id:
        lt = B.call("jawa/list_things", defName="Battery", limit=5)
        for t in lt.get("things") or []:
            bat_id = t.get("id") or t.get("thingId")
    bs = B.call("jawa/battery_set", thing=bat_id, mode="setPct", value=1.0) if bat_id else {}
    B.call("jawa/map_commit")
    # Section meshes regenerate only when a section is in VIEW (Section.TryUpdate / DrawSection), so a
    # census of the drawer's sub-meshes needs the camera on the scene (run 2: layerVerts 0 off-screen).
    B.call("rimworld/jump_camera_to_cell", x=X0 + 14, z=Z0 + 4)
    B.call("rimworld/frame_cell_rect", x=SITE[0], z=SITE[1], width=SITE[2], height=SITE[3], paddingCells=1)
    B.ticks(2)
    time.sleep(1.0)
    ok_scene = b4.get("survived") == len(cond) and bs.get("storedEnergyAfter", 0) > 0
    row(rows, "S0_scene_built", "PASS" if ok_scene else "FAIL", "SITE", dict(built, battery=bat_id, stored=bs.get("storedEnergyAfter")))
    c0 = B.probe("census")
    log.append({"census0": c0})

    # ---------------------------------------------------------------- M3 / M1: invisible conduit
    tp = c0.get("texPaths") or {}
    inv = c0.get("invisibleApplied") and tp and all(v == TRANSPARENT for v in tp.values()) and \
        c0.get("spawnedConduitTexture") == "ConduitTransparent"
    row(rows, "M1_conduit_transparent", "PASS" if inv else "FAIL", "MOD",
        {"texPaths": tp, "spawned": c0.get("spawnedConduitTexture")})
    # ---------------------------------------------------------------- M1: cords exist for the network
    nt = c0.get("nodeTypes") or {}
    cords_ok = (c0.get("cordEdges") or 0) >= 4 and (c0.get("layerVerts") or 0) > 0 and c0.get("layerVisible")
    row(rows, "M1_cords_exist", "PASS" if cords_ok else "FAIL", "MOD",
        {k: c0.get(k) for k in ("conduitCells", "cordEdges", "hiddenEdges", "strands", "layerVerts", "layerSectionsWithCords")} | {"nodes": nt})
    want_types = {"battery", "consumer", "junction", "stub_wall"}
    wall_live = [e for e in c0.get("ends") or [] if e.get("wall") and e.get("netLive")]
    row(rows, "M1_node_census", "PASS" if want_types <= set(nt) and nt.get("terminal", 0) >= 2 and wall_live else "FAIL", "MOD",
        "need %s + >=2 terminals (FAR run ends) + a live wall terminal; got %s, live wall ends %d" % (sorted(want_types), nt, len(wall_live)))
    dc = c0.get("decals") or {}
    row(rows, "M1c_end_pieces", "PASS" if dc.get("Plug", 0) > 0 and dc.get("StubWall", 0) > 0 and
        (dc.get("JunctionTape", 0) + dc.get("JunctionTin", 0)) > 0 and (dc.get("FrayDead", 0) + dc.get("FrayLive", 0)) > 0 else "FAIL",
        "MOD", {"decals": dc})
    # ---------------------------------------------------------------- M2: connected only, floor rule
    m2 = c0.get("cordsAcrossNets") == 0 and c0.get("cordEndsWithoutNet") == 0
    row(rows, "M2_cords_only_within_net", "PASS" if m2 else "FAIL", "MOD",
        {k: c0.get(k) for k in ("cordsAcrossNets", "cordsAcrossNetsList", "cordEndsWithoutNet")})
    row(rows, "M2b_no_vertex_unwalkable", "PASS" if c0.get("verticesInUnwalkable") == 0 and c0.get("interiorVertices", 0) > 0 else "FAIL",
        "MOD", {k: c0.get(k) for k in ("verticesInUnwalkable", "interiorVertices", "fellBack", "unroutable")})
    # ---------------------------------------------------------------- M6: hookup wire hidden, overlay intact
    m6 = (c0.get("hookupWiresSuppressed") or 0) > 0 and (c0.get("overlayConnectorVerts") or 0) > 0
    row(rows, "M6_overlay_lines_intact", "PASS" if m6 else "FAIL", "MOD",
        {k: c0.get(k) for k in ("hookupWiresSuppressed", "overlayWiresPrinted", "overlayConnectorVerts")})
    # ---------------------------------------------------------------- determinism (fresh builder, same map)
    fr = B.probe("fresh")
    row(rows, "D1_determinism_fresh_build", "PASS" if fr.get("edges", 0) > 0 and fr.get("different") == 0 and fr.get("missing") == 0 else "FAIL",
        "MOD", fr)
    # ---------------------------------------------------------------- M5: local invalidation
    hashes0 = c0.get("edgeHashes") or {}
    B.call("jawa/build_batch", ops=ops("PowerConduit", [(FAR[-1][0] + 1, FAR[-1][1])]), faction="player", wipeExisting=False)
    B.ticks(2)
    c1 = B.probe("census")
    hashes1 = c1.get("edgeHashes") or {}
    changed = sorted(k for k in hashes0 if k in hashes1 and hashes0[k] != hashes1[k])
    gone = sorted(k for k in hashes0 if k not in hashes1)
    far_keys = [k for k in gone + changed if ("%d," % FAR[0][0]) in k or ("%d," % FAR[-1][0]) in k]
    m5 = not [k for k in changed + gone if k not in far_keys] and (c1.get("lastPlanned") or 0) <= 2
    row(rows, "M5_local_invalidation", "PASS" if m5 else "FAIL", "MOD",
        {"changed": changed, "gone": gone, "lastPlanned": c1.get("lastPlanned"), "lastReused": c1.get("lastReused")})
    # ---------------------------------------------------------------- M8: a break -> two dangling ends
    B.call("jawa/destroy_batch", rects="%d,%d,1,1" % GAP, categories="Building")
    B.ticks(2)
    B.probe("poll")
    c2 = B.probe("census")
    ends = {tuple(e["cell"]): e for e in c2.get("ends") or []}
    west, east = (GAP[0] - 1, GAP[1]), (GAP[0] + 1, GAP[1])
    ew, ee = ends.get(west), ends.get(east)
    m8 = bool(ew and ee and ew.get("registryLive") is True and ee.get("registryLive") is False and
              ew.get("netLive") is True and ee.get("netLive") is False)
    row(rows, "M8_break_two_ends_live_dead", "PASS" if m8 else "FAIL", "MOD",
        {"west(battery side)": ew, "east": ee, "cordsAcrossNets": c2.get("cordsAcrossNets")})
    row(rows, "M8b_no_cord_across_gap", "PASS" if c2.get("cordsAcrossNets") == 0 else "FAIL", "MOD",
        {"cordsAcrossNets": c2.get("cordsAcrossNets"), "list": c2.get("cordsAcrossNetsList")})
    # source off -> the live end reads dead within one 250-tick poll, no manual poll
    if bat_id:
        B.call("jawa/battery_set", thing=bat_id, mode="setPct", value=0.0)
    B.ticks(260)
    c3 = B.probe("census")
    e3 = {tuple(e["cell"]): e for e in c3.get("ends") or []}.get(west)
    m8c = bool(e3 and e3.get("netLive") is False and e3.get("registryLive") is False)
    row(rows, "M8c_source_off_reads_dead_250", "PASS" if m8c else "FAIL", "MOD", {"west": e3})
    if bat_id:
        B.call("jawa/battery_set", thing=bat_id, mode="setPct", value=1.0)
    B.ticks(2)
    # ---------------------------------------------------------------- M7: master off -> vanilla art
    B.probe("set:enabled=False")
    c4 = B.probe("census")
    tp4 = c4.get("texPaths") or {}
    m7 = (not c4.get("invisibleApplied")) and tp4 and all(v != TRANSPARENT for v in tp4.values()) and \
        c4.get("spawnedConduitTexture") not in (None, "ConduitTransparent") and not c4.get("layerVisible")
    row(rows, "M7_off_restores_vanilla", "PASS" if m7 else "FAIL", "MOD",
        {"texPaths": tp4, "spawned": c4.get("spawnedConduitTexture"), "layerVisible": c4.get("layerVisible")})
    B.probe("set:enabled=True")
    c5 = B.probe("census")
    row(rows, "M7b_on_again_invisible", "PASS" if c5.get("spawnedConduitTexture") == "ConduitTransparent" and c5.get("layerVerts", 0) > 0 else "FAIL",
        "MOD", {"spawned": c5.get("spawnedConduitTexture"), "layerVerts": c5.get("layerVerts")})
    B.probe("defaults")
    # ---------------------------------------------------------------- log budget
    lg = B.call("rimbridge/list_logs", limit=500, minimumLevel="warning")
    new = [e for e in lg.get("logs") or [] if (e.get("Sequence") or 0) > log_base]
    errs = [e for e in new if str(e.get("Level", "")).lower() in ("error", "exception")]
    row(rows, "Z_log_budget", "PASS" if not errs else "FAIL", "MOD",
        {"errors": [str(e.get("Message", ""))[:200] for e in errs[:6]], "newWarnings": len(new)})
    t_end = B.probe("census").get("ticksGame")
    res["ticks"] = (t_end - t_start) if isinstance(t_end, int) and isinstance(t_start, int) else None
    for rid, st, why in UNBUILT:
        row(rows, rid, st, "SCOPE", why)
    res["log"] = log
    return res


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--fresh-map", action="store_true")
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    if not a.live:
        rows = run_offline()
        bad = [r for r in rows if r["status"] != "PASS"]
        print("offline: %d/%d PASS" % (len(rows) - len(bad), len(rows)))
        return 1 if bad else 0
    res = run_live(a)
    os.makedirs(os.path.join(HERE, "northstar"), exist_ok=True)       # excluded from status.mod_hash
    out = a.out or os.path.join(HERE, "northstar", "validation_result_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
    with open(out, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1, default=str)
    t = {}
    for r in res["rows"]:
        t[r["status"]] = t.get(r["status"], 0) + 1
    print("live: %s ticks=%s -> %s" % (t, res.get("ticks"), out))
    return 0 if not res.get("aborted") and t.get("FAIL", 0) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
