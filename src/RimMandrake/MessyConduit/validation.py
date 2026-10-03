"""validation.py -- Messy Conduit functional script (debug_process.md section 2), phase 1a.

Walk: design/validation_walks/RimMandrake/MessyConduit.md (## must be true lines M1..M9).
Design: design/RimMandrake/messy_conduit_design_2026-10-02.md (section 5 "First functional script").

    python3    src/RimMandrake/MessyConduit/validation.py                 # offline tier, 0 ticks
    python.exe src/RimMandrake/MessyConduit/validation.py --live --fresh-map   # messyconduit tier, bridge held
    python.exe src/RimMandrake/MessyConduit/validation.py --save-load NAME     # M4 on the current map's scene (after --live)
    python.exe src/RimMandrake/MessyConduit/validation.py --removal-check NAME # M9: a tier WITHOUT the mod (e.g. flowworks)

M4 (--save-load): census, save as a NEW name with the Saves folder stat'd before/after (only NAME.rws may
appear, nothing else may change), assert the save holds nothing of ours, load it, census, compare the cord set
(geometry hash, per-edge hashes, node types, decals, ends). M9 (--removal-check): load_game NAME with
ignoreModCompatibility on a list without the mod, step 60 ticks, no warning+ log entry or Player.log line may
name the mod. Batch: --live, then --save-load, then ONE cold load onto the other tier for --removal-check.

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
  * Live pass 2 (2026-10-02), two MOD defects found by the new modes and fixed in RM_MapComponent_CordGraph.cs:
    (1) M4 FAILED: after a load the graph had 8 edges but 0 laid pieces -- no cords on ANY loaded save. Log:
    "Could not regenerate layer SectionLayer_RM_MessyCords: NRE at MapDrawer.MapMeshDirty". MapDrawer.
    RegenerateEverythingNow creates its Sections one by one inside the regen loop, so dirtying a later section
    hit a null slot, and pieces were published after the dirty loop so the throw lost them. A fresh quicktest
    map never shows it (no conduit exists at its first regenerate) -- only a load does.
    (2) M9 FAILED: the save held <li Class="RimMandrake.MessyConduit.RM_MapComponent_CordGraph" /> (every
    MapComponent is written, ExposeData or not); a mod-less load logged "Could not find class ..." + "Can't load
    abstract class Verse.MapComponent". Fixed by keeping the component out of Map.ExposeComponents while saving.
    Both re-proven: M4 PASS (hash d957f9fa758583d6 before == after), M9 PASS (0 errors naming the mod).
  * The same scene on two different fresh quicktest maps gave the same geometry hash (d957f9fa758583d6).
  * HARNESS: modset_builder --apply writes its "before" backup per tier name, so swapping A->B->A overwrites
    the earlier backup of the same name; the pre-pass list is whatever tier you swap back to by name.
  * HARNESS: sparks are flecks thrown on ticks, so a paused screenshot never shows them (look, do not hunt).
  * Phase 1b lane A (2026-10-02): frame_cell_rect moves the camera but KEEPS the zoom, so after the far-zoom LOD
    read the camera stayed Furthest and every later read/screenshot was far (B8 FAILED in harness, fixed by
    set_camera_zoom back). screenshot_cell_rect does NOT capture per-frame Graphics.DrawMesh draws (selection
    highlight, whip, sway): the highlight was on screen (OS capture) yet absent from the cell-rect capture.
    The first highlight material tinted the near-black strand texture and stayed near-black; it is now a warm
    band on a white texture.
  * Lane C art styles (2026-10-02): ST1-ST5 run inside --live (after the 1b block); --style-shots repeats them on the
    current map with a screenshot per style. A style switch is set:style=X (Apply rebuilds the materials and regenerates
    every map mesh); ST2 proves the PRINTED section meshes carry only that style's strands, not just the material table.
    The settings round trip (ST4) writes the real Config/Mod_MessyConduit_MessyConduitMod.xml; when that file did not
    exist before a session, delete it afterwards. At ~26 px/cell Star Wars reads as Jawa and Cybertek as dull grey-green
    (look, README), which no state row can catch.
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
           "sparkIntensity": "1f", "hideHookupWires": "true", "debugDraw": "false",
           # phase 1b lane A
           "tangleMin": "9", "whip": "true", "downedWire": "true", "sparksOnlyOverlay": "false",
           "maxSparkingEnds": "24", "highlight": "true", "sway": "true", "swayAmplitude": "1f", "lod": "true",
           # lane C art styles
           "extCordColorMode": "ExtCordColorMode.Mixed", "extCordColor": "0"}

# Bars this phase does not build or this short tier does not reach. Honest, named, never PASS.
UNBUILT = [
    ("U_sway_shader_path", "UNBUILT", "CutoutPlant vertex-shader sway (phase-2 doc 1.5 option 1); the CPU path is what ships"),
    ("U_floor_ripple", "UNBUILT", "optional outdoor floor-cord ripple (phase-2 doc 1.3, default off)"),
    ("U_motion_look", "UNCOVERED", "whip / drip rhythm / sway LOOK: motion is not a Northstar bar (owner); state proxies above"),
    ("U_style_missing_art", "UNBUILT", "per-family EndFrayed_Live / PowerStrip / StrandShadow art does not exist; those slots "
                                       "fall back to the Jawa pieces (ST1 asserts the fallback list is exactly that)"),
    ("M4_save_load_hash", "UNCOVERED", "walk M4: same polylines after save/load -- its own mode, --save-load NAME"),
    ("M9_remove_mod_clean", "UNCOVERED", "walk M9: a save made with the mod loads clean without it -- its own mode, "
                                         "--removal-check NAME on a tier without the mod"),
]

SAVES = os.path.join(os.environ.get("USERPROFILE", ""), "AppData", "LocalLow", "Ludeon Studios",
                     "RimWorld by Ludeon Studios", "Saves")
PLAYER_LOG = os.path.join(os.path.dirname(SAVES), "Player.log")
MOD_MARKERS = ("MessyConduit", "RM_MessyCords", "CordGraph", "ConduitTransparent")


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


# ---------------------------------------------------------------- lane C: art styles (offline)
# Every style's required PNGs (paths relative to Textures/RimMandrake/MessyConduit), canvas, and kind. Wired by
# src/RimMandrake/Utils/mockups/messy_conduit/wire_style_art.py; slots not listed fall back to the Jawa root set.
STYLE_FILES = {
    "StarWarsJawa": ["Strand_Jawa", "Junction_Tape", "Junction_Tin", "Plug", "StubWall", "StubRock", "EndFrayed_Dead"],
    "Cybertek": ["Styles/Cybertek/" + n for n in ("Strand", "Junction_T", "Junction_X", "Plug", "StubWall", "StubRock", "EndFrayed_Dead")],
    "ExtensionCord": ["Styles/ExtCord/Strand_" + c for c in ("Orange", "Green", "Brown", "Yellow", "Blue")] +
                     ["Styles/ExtCord/" + n for n in ("Junction_T", "Junction_X", "Plug", "StubWall", "StubRock", "EndFrayed_Dead")],
    "StarWars": ["Styles/StarWars/Strand_" + v for v in ("BlackRubber", "CorrugatedSteel", "CoiledBlack")] +
                ["Styles/StarWars/" + n for n in ("Junction_T", "Junction_X", "Plug", "StubWall", "StubRock", "EndFrayed_Dead")],
}
SHARED_FILES = ["StrandShadow", "SparkGlow", "EndFrayed_Live", "PowerStrip", "Aerial/AerialMast", "Aerial/AerialMastTop",
                "Aerial/AerialLampMast", "Aerial/AerialLampMastTop", "Aerial/WallBracket", "Aerial/TapClamp", "Aerial/SpanShadow"]
STAGED_HOSE = ["Hose/" + n for n in ("Strand_Flat", "Strand_Plump", "Strand_Shadow", "Coupling_Brass", "Nozzle", "Reel_PumpHookup", "EndCap")]
ALLOWED_FALLBACKS = {"EndFrayed_Live", "PowerStrip", "PowerStripDark"}


def _canvas_for(rel):
    n = rel.split("/")[-1]
    if rel.startswith("Hose/Strand"):
        return (256, 64)
    if n.startswith("Strand") or n in ("SpanShadow", "SpanWire"):
        return (128, 32)
    if n in ("EndFrayed_Dead", "EndFrayed_Live", "SparkGlow", "TapClamp"):
        return (64, 64)
    if n == "PowerStrip":
        return (64, 32)
    if n in ("AerialMast", "AerialLampMast"):
        return (128, 256)
    return (128, 128)


def png_sanity(rel):
    """None if the PNG is sane, else why: RGBA, exact canvas, real transparency, not empty, not magenta; a strip
    (Strand*, SpanShadow, Hose strands) must tile: edge-column diff <= max(1.5 x mean adjacent diff, +4)."""
    from PIL import Image
    import numpy as np
    p = os.path.join(HERE, "Textures", "RimMandrake", "MessyConduit", rel + ".png")
    if not os.path.exists(p):
        return "missing"
    im = Image.open(p)
    if im.mode != "RGBA":
        return "mode %s" % im.mode
    want = _canvas_for(rel)
    if im.size != want:
        return "size %s != %s" % (im.size, want)
    a = np.asarray(im).astype(np.float32)
    al = a[:, :, 3]
    if (al > 8).mean() < 0.01:
        return "empty"
    if (al < 8).mean() < 0.02 and not rel.split("/")[-1].startswith("Strand"):
        return "no transparency"
    vis = a[al > 128][:, :3]
    if len(vis) and ((vis[:, 0] > 200) & (vis[:, 1] < 60) & (vis[:, 2] > 200)).mean() > 0.2:
        return "magenta"
    n = rel.split("/")[-1]
    if n.startswith("Strand") or n == "SpanShadow":
        pm = np.concatenate([a[:, :, :3] * (a[:, :, 3:4] / 255.0), a[:, :, 3:4]], axis=2)
        edge = float(np.abs(pm[:, 0] - pm[:, -1]).mean())
        adj = float(np.abs(np.diff(pm, axis=1)).mean())
        if edge > max(1.5 * adj, adj + 4.0):
            return "seam %.1f vs adjacent %.1f" % (edge, adj)
    return None


def o5_style_art(rows):
    probs = {}
    n = 0
    for style, files in STYLE_FILES.items():
        for rel in files:
            n += 1
            why = png_sanity(rel)
            if why:
                probs.setdefault(style, []).append("%s: %s" % (rel, why))
    for rel in SHARED_FILES + STAGED_HOSE:
        n += 1
        why = png_sanity(rel)
        if why:
            probs.setdefault("shared", []).append("%s: %s" % (rel, why))
    # the sanity check must be able to fail: a planted magenta strip and a seam-broken strip are refused
    import tempfile
    from PIL import Image
    import numpy as np
    plant = np.zeros((32, 128, 4), np.uint8)
    plant[8:24, :, :] = (255, 0, 255, 255)
    seam = np.zeros((32, 128, 4), np.uint8)
    seam[8:24, :64] = (20, 20, 20, 255)
    seam[8:24, 64:] = (220, 220, 220, 255)
    tdir = os.path.join(HERE, "Textures", "RimMandrake", "MessyConduit", "_o5probe")
    can_fail = False
    try:
        os.makedirs(tdir, exist_ok=True)
        Image.fromarray(plant).save(os.path.join(tdir, "Strand_magenta.png"))
        Image.fromarray(seam).save(os.path.join(tdir, "Strand_seam.png"))
        can_fail = png_sanity("_o5probe/Strand_magenta") == "magenta" and (png_sanity("_o5probe/Strand_seam") or "").startswith("seam")
    finally:
        import shutil
        shutil.rmtree(tdir, ignore_errors=True)
    row(rows, "O5_style_art_sane", "PASS" if not probs and can_fail else "FAIL", "MOD",
        probs or "%d PNGs sane (4 styles + shared/aerial + staged hose); planted magenta+seam refused=%s" % (n, can_fail))


def run_offline():
    rows = []
    o1_files(rows)
    o2_defaults(rows)
    o5_style_art(rows)
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
    try:
        lane_a_live(B, rows, log)
    except Exception as ex:  # noqa: BLE001
        row(rows, "P1B_block", "FAIL", "HARNESS", "lane A block raised: %r" % ex)
    try:
        style_live(B, rows, log)
    except Exception as ex:  # noqa: BLE001
        row(rows, "ST_block", "FAIL", "HARNESS", "lane C style block raised: %r" % ex)
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


# ============================================================================ phase 1b lane A (live)
# A second plot north-east of the room: battery 2, a 4x3 conduit field (a TANGLE at the default threshold 9),
# a run east into a wall that carries one buried conduit cell (a live WALL terminal = downed wire, outdoors so
# it sways). Run after M8b, so the west end of the gap is a LIVE floor terminal (whip) on screen.
BAT2 = (X0 + 19, Z0 + 8)
FIELD = [(x, z) for x in range(X0 + 20, X0 + 24) for z in range(Z0 + 8, Z0 + 11)]
RUN2 = [(X0 + 24, Z0 + 9), (X0 + 25, Z0 + 9), (X0 + 26, Z0 + 9)]
WALL2 = [(X0 + 26, Z0 + 8), (X0 + 26, Z0 + 9), (X0 + 26, Z0 + 10)]
SHOTS = os.path.join(REPO, "Transient", "messy_conduit_live_20261002")


def shot(B, name, rect, log, pad=1, root=None):
    import shutil
    kw = {} if root is None else {"rootSize": root}
    r = B.call("rimworld/screenshot_cell_rect", x=rect[0], z=rect[1], width=rect[2], height=rect[3], paddingCells=pad,
               fileName=name, suppressMessage=True, **kw)
    src = r.get("path") or r.get("filePath")
    dst = None
    try:
        if src and os.path.exists(src):
            os.makedirs(SHOTS, exist_ok=True)
            dst = os.path.join(SHOTS, name + os.path.splitext(src)[1])
            shutil.copyfile(src, dst)
    except Exception as ex:  # noqa: BLE001
        log.append("screenshot copy failed %s: %r" % (name, ex))
    log.append({"shot": name, "src": src, "dst": dst, "ok": r.get("success")})
    return dst


def motion(B, frames=2):
    """The motion counters describe the LAST drawn frame: read twice so a setting change has been drawn."""
    m = {}
    for _ in range(frames):
        m = B.probe("motion")
        time.sleep(0.25)
    return m


def lane_a_live(B, rows, log):
    b1 = B.call("jawa/build_batch", ops=ops("Wall", WALL2), stuff="Steel", faction="player")
    b2 = B.call("jawa/build_batch", ops="Battery:%d,%d,0" % BAT2, faction="player")
    b3 = B.call("jawa/build_batch", ops=ops("PowerConduit", FIELD + RUN2), faction="player", wipeExisting=False)
    bat2 = None
    for t in B.call("jawa/list_things", defName="Battery", limit=10).get("things") or []:
        pos = t.get("position") or t.get("pos") or t.get("cell")
        if pos and tuple(pos[:1] + pos[-1:]) == BAT2 or (isinstance(pos, dict) and (pos.get("x"), pos.get("z")) == BAT2):
            bat2 = t.get("id") or t.get("thingId")
    if not bat2:
        lst = B.call("jawa/list_things", defName="Battery", limit=10).get("things") or []
        bat2 = (lst[-1].get("id") or lst[-1].get("thingId")) if lst else None
    bs = B.call("jawa/battery_set", thing=bat2, mode="setPct", value=1.0) if bat2 else {}
    B.call("rimworld/frame_cell_rect", x=SITE[0], z=SITE[1], width=SITE[2], height=SITE[3], paddingCells=1)
    B.ticks(2)
    time.sleep(1.0)
    B.probe("poll")
    m0 = motion(B)
    log.append({"lane_a_m0": m0, "plot": {"walls": b1.get("survived"), "battery": bat2, "conduit": b3.get("survived"),
                                          "stored": bs.get("storedEnergyAfter")}})
    row(rows, "P1B_plot_built", "PASS" if b3.get("survived") == len(FIELD + RUN2) and bs.get("storedEnergyAfter", 0) > 0 else "FAIL",
        "SITE", {"conduit": b3.get("survived"), "battery2": bat2, "stored": bs.get("storedEnergyAfter")})
    # B1 settle
    row(rows, "B1_rope_settle", "PASS" if m0.get("settledStrands", 0) > 0 and m0.get("settleMaxStretch", 1) < 0.03 and
        m0.get("settleMaxLenDev", 1) <= 0.05 else "FAIL", "MOD",
        {k: m0.get(k) for k in ("settledStrands", "settleMaxStretch", "settleMaxLenDev", "endHeaps", "laidPoints", "lastRebuildMs")})
    # L2 tangle entity + lit strips
    row(rows, "B6_tangle_lit_strips", "PASS" if m0.get("tangles", 0) >= 1 and m0.get("litStrips", 0) > 0 and m0.get("darkStrips", 1) == 0 else "FAIL",
        "MOD", {k: m0.get(k) for k in ("tangles", "tangleMinUsed", "litStrips", "darkStrips", "stubs", "mergedStubs")})
    shot(B, "p1b_01_wide", SITE, log)
    shot(B, "p1b_02_tangle_lit_and_downed_wire", (X0 + 18, Z0 + 6, 10, 6), log, root=7)
    # B3 whip
    w_on = m0.get("whipDraws", 0)
    B.probe("set:whip=False")
    m1 = motion(B)
    B.probe("set:whip=True")
    m1b = motion(B)
    row(rows, "B3_whip_live_ends", "PASS" if w_on > 0 and m0.get("whipTails", 0) > 0 and m1.get("whipDraws") == 0 and m1b.get("whipDraws", 0) > 0 else "FAIL",
        "MOD", {"whipDraws_on": w_on, "whipTails": m0.get("whipTails"), "liveFloorEnds": m0.get("liveFloorEnds"),
                "deadFloorEnds": m0.get("deadFloorEnds"), "whipDraws_off": m1.get("whipDraws"), "whipDraws_on_again": m1b.get("whipDraws")})
    # B4 downed-wire schedule: real time, histogram of events (counts while paused; flecks only while time runs)
    B.probe("motionreset")
    hist, t0 = {}, time.time()
    while time.time() - t0 < 45:
        time.sleep(5)
        hist = (B.probe("motion").get("downedHist") or {})
        if all(hist.get(k, 0) > 0 for k in ("Drip", "Flash", "Quiet", "Crackle")):
            break
    m2 = B.probe("motion")
    row(rows, "B4_downed_wire_bursts", "PASS" if m2.get("liveWallEnds", 0) >= 1 and all(hist.get(k, 0) > 0 for k in ("Drip", "Flash", "Quiet", "Crackle")) else "FAIL",
        "MOD", {"liveWallEnds": m2.get("liveWallEnds"), "hist": hist, "events": m2.get("dripEvents"), "seconds": int(time.time() - t0)})
    s0 = m2.get("sparksThrown", 0)
    B.ticks(160)
    m3 = B.probe("motion")
    row(rows, "B4b_sparks_thrown_ticking", "PASS" if m3.get("sparksThrown", 0) > s0 else "FAIL", "MOD",
        {"sparksBefore": s0, "sparksAfter160Ticks": m3.get("sparksThrown")})
    # B7 sway (CPU path): two frames 30 ticks apart differ with sway ON, nothing drawn with it OFF
    a = motion(B)
    B.ticks(30)
    b = motion(B)
    B.probe("set:sway=False")
    c = motion(B)
    B.probe("set:sway=True")
    sway_ok = a.get("swayDraws", 0) > 0 and a.get("swayHash") != b.get("swayHash") and c.get("swayDraws") == 0 and c.get("liftedSwaying") == 0
    row(rows, "B7_sway_cpu_two_frame", ("PASS" if sway_ok else "FAIL") if a.get("plantWindSway") else "UNMEASURED", "MOD",
        {"mode": a.get("swayMode"), "plantWindSway": a.get("plantWindSway"), "wind": a.get("windSpeed"), "amp": a.get("swayAmplitude"),
         "lifted": a.get("liftedStrands"), "swaying": a.get("liftedSwaying"), "swayDraws": a.get("swayDraws"), "swayVerts": a.get("swayVerts"),
         "hashA": a.get("swayHash"), "hashB_30ticks": b.get("swayHash"), "off_swayDraws": c.get("swayDraws"), "off_swaying": c.get("liftedSwaying")})
    # B5 selection highlight
    sa = B.probe("select:%d,%d" % (X0 + 5, Z0 + 3))
    h1 = motion(B, 3)
    # (no screenshot here: screenshot_cell_rect renders its own camera pass and does NOT include the per-frame
    #  Graphics.DrawMesh calls -- highlight, whip, sway -- LEARNED live 1b; an OS capture does show them)
    sb = B.probe("select:%d,%d" % (X0 + 24, Z0 + 9))
    h2 = motion(B, 3)
    B.probe("deselect")
    h3 = motion(B)
    per1, per2 = h1.get("cordsPerNet") or {}, h2.get("cordsPerNet") or {}
    hl_ok = (sa.get("success") and sb.get("success") and h1.get("highlightCords", 0) > 0 and
             h1.get("highlightCords") == per1.get(str(h1.get("selectedNet"))) and
             h2.get("highlightCords") == per2.get(str(h2.get("selectedNet"))) and h1.get("selectedNet") != h2.get("selectedNet") and
             h3.get("highlightCords") == 0)
    row(rows, "B5_selection_highlight", "PASS" if hl_ok else "FAIL", "MOD",
        {"net1": [h1.get("selectedNet"), h1.get("highlightCords"), per1.get(str(h1.get("selectedNet")))],
         "net2": [h2.get("selectedNet"), h2.get("highlightCords"), per2.get(str(h2.get("selectedNet")))],
         "stubRings": [h1.get("highlightStubs"), h2.get("highlightStubs")], "deselected": h3.get("highlightCords")})
    # B8 LOD by zoom
    cam = B.call("rimworld/get_camera_state")
    B.call("rimworld/set_camera_zoom", rootSize=58)
    f1 = motion(B, 3)
    shot_far = shot(B, "p1b_04_far_zoom_lod", (SITE[0] - 10, SITE[1] - 10, SITE[2] + 20, SITE[3] + 20), log, pad=0)
    # LEARNED run 1b-1: frame_cell_rect moves the camera but keeps a Furthest zoom; set the root back explicitly
    B.call("rimworld/set_camera_zoom", rootSize=cam.get("rootSize") or 24)
    B.call("rimworld/frame_cell_rect", x=SITE[0], z=SITE[1], width=SITE[2], height=SITE[3], paddingCells=1)
    f2 = motion(B, 3)
    lod_ok = f1.get("lodFarNow") and f1.get("lodEnabled", 0) > 0 and f1.get("fullEnabled") == 0 and \
        (not f2.get("lodFarNow")) and f2.get("lodEnabled") == 0 and f2.get("fullEnabled", 0) > 0
    row(rows, "B8_lod_far_zoom", "PASS" if lod_ok else "FAIL", "MOD",
        {"far": {k: f1.get(k) for k in ("zoom", "lodFarNow", "lodSubMeshes", "lodEnabled", "fullSubMeshes", "fullEnabled")},
         "close": {k: f2.get(k) for k in ("zoom", "lodFarNow", "lodEnabled", "fullEnabled")}, "camera0": cam.get("rootSize"), "shot": bool(shot_far)})
    # B9 cutscene guard (state read; a gravship launch is not staged here)
    row(rows, "B9_cutscene_guard_idle", "PASS" if f2.get("cutsceneInProgress") is False and f2.get("cutsceneHides") is False else "FAIL",
        "MOD", {k: f2.get(k) for k in ("cutsceneInProgress", "cutsceneHides", "cutsceneSkips")})
    shot(B, "p1b_05_downed_wire_close", (X0 + 23, Z0 + 7, 5, 4), log, root=4)
    # B6 strips go dark when the field's net is dead (one 250-tick poll, no manual poll)
    if bat2:
        B.call("jawa/battery_set", thing=bat2, mode="setPct", value=0.0)
    B.ticks(260)
    d1 = motion(B)
    shot(B, "p1b_06_tangle_dark", (X0 + 18, Z0 + 6, 10, 6), log, root=7)
    row(rows, "B6b_strips_dark_when_dead", "PASS" if d1.get("darkStrips", 0) > 0 and d1.get("litStrips") == 0 else "FAIL", "MOD",
        {k: d1.get(k) for k in ("litStrips", "darkStrips", "liveWallEnds")})
    if bat2:
        B.call("jawa/battery_set", thing=bat2, mode="setPct", value=1.0)
    B.ticks(2)
    # M10 the messiness (tangle threshold) setting changes the census on the same field
    B.probe("set:tangleMin=20")
    t20 = motion(B)
    B.probe("set:tangleMin=6")
    t6 = motion(B)
    B.probe("set:tangleMin=9")
    row(rows, "M10_tangle_threshold_setting", "PASS" if t20.get("tangles") == 0 and t6.get("tangles", 0) >= 1 else "FAIL", "MOD",
        {"tangleMin20": t20.get("tangles"), "tangleMin6": t6.get("tangles")})
    row(rows, "P1B_perf_rebuild", "PASS" if (m0.get("lastRebuildMs") or 0) > 0 else "UNMEASURED", "MOD",
        {"lastRebuildMs": m0.get("lastRebuildMs"), "laidPoints": m0.get("laidPoints"), "note": "first C# rebuild timing; no bar set"})


# ============================================================================ lane C: art styles (live)
STYLES = ["StarWarsJawa", "StarWars", "ExtensionCord", "Cybertek"]


def style_live(B, rows, log, shots_prefix=None):
    """ST rows: every style loads every texture it needs (no null / bad / missing material, fallbacks only to
    the Jawa slots no family has art for), switching re-prints the section meshes with that style's strand,
    the extension-cord colour modes, the settings file round trip, and a clean return to the default."""
    per = {}
    for st in STYLES:
        B.probe("set:style=%s" % st)
        B.ticks(1)
        time.sleep(0.5)
        c = B.probe("census")
        sp = B.probe("styles")
        per[st] = sp
        log.append({"style": st, "styles": sp})
        fb = set(sp.get("fallbacks") or [])
        allowed = set() if st == "StarWarsJawa" else ALLOWED_FALLBACKS
        ok = (sp.get("success") and not sp.get("nulls") and not sp.get("bad") and not sp.get("missing") and fb <= allowed and
              sp.get("builtKey") == sp.get("currentKey") and (sp.get("installed") or {}).get(st) and (c.get("layerVerts") or 0) > 0)
        row(rows, "ST1_%s_textures_load" % st, "PASS" if ok else "FAIL", "MOD",
            {"strandTex": sp.get("strandTex"), "fallbacks": sorted(fb), "nulls": sp.get("nulls"), "bad": sp.get("bad"),
             "missing": sp.get("missing"), "layerVerts": c.get("layerVerts")})
        if shots_prefix:
            shots_prefix(st)
    strand_sets = {st: tuple(per[st].get("strandTex") or []) for st in STYLES}
    distinct = len(set(strand_sets.values())) == len(STYLES)
    printed_ok = {st: any(t in (per[st].get("printedTex") or {}) for t in strand_sets[st]) and
                  not any(t in (per[st].get("printedTex") or {}) for o in STYLES if o != st for t in strand_sets[o] if t not in strand_sets[st])
                  for st in STYLES}
    plug_ids = {st: ((per[st].get("slots") or {}).get("Plug") or {}).get("id") for st in STYLES}
    span_ok = {st: per[st].get("aerialSpanTex") == (strand_sets[st][0] if strand_sets[st] else None) for st in STYLES}
    row(rows, "ST2_switch_changes_textures", "PASS" if distinct and all(printed_ok.values()) and len(set(plug_ids.values())) == len(STYLES)
        and all(span_ok.values()) else "FAIL", "MOD",
        {"strandTex": strand_sets, "printedOnlyOwnStrand": printed_ok, "plugTexIds": plug_ids, "aerialSpanFollows": span_ok,
         "rebuilds": [per[st].get("rebuilds") for st in STYLES]})
    # extension cords: mixed = 5 colours, one per net (every piece of one net the same colour); single = one colour
    B.probe("set:style=ExtensionCord")
    B.probe("set:extCordColorMode=Mixed")
    B.ticks(1)
    mx = B.probe("styles")
    B.probe("set:extCordColor=2")
    B.probe("set:extCordColorMode=Single")
    B.ticks(1)
    time.sleep(0.5)
    sg = B.probe("styles")
    pt = sg.get("printedTex") or {}
    other = [k for k in pt if k.startswith("Strand_") and k != "Strand_Brown" and "(lod)" not in k]
    nets_ok = sum((mx.get("netsPerVariant") or {}).values()) == mx.get("cordNets")   # each net in exactly one variant
    row(rows, "ST3_extcord_colour_modes", "PASS" if mx.get("variantCount") == 5 and nets_ok and sg.get("variantCount") == 1 and
        sg.get("strandTex") == ["Strand_Brown"] and "Strand_Brown" in pt and not other else "FAIL", "MOD",
        {"mixed": {k: mx.get(k) for k in ("variantCount", "piecesPerVariant", "netsPerVariant", "cordNets")},
         "single": {"strandTex": sg.get("strandTex"), "printed": pt}})
    B.probe("set:extCordColorMode=Mixed")
    B.probe("set:extCordColor=0")
    # the settings file round trip (written, reset in memory, read back), then the pre-test values restored
    rt = B.probe("settingsroundtrip")
    row(rows, "ST4_settings_roundtrip", "PASS" if rt.get("readBack") == "Cybertek/Single/3" and rt.get("afterReset") != rt.get("readBack")
        and rt.get("fileHadStyle") and rt.get("fileHadMode") and not rt.get("restoredFileHasCybertek") else "FAIL", "MOD", rt)
    # restore cleanly: the default style is back, same textures as the first read, master switch still works
    B.probe("set:style=StarWarsJawa")
    B.probe("set:enabled=False")
    off = B.probe("census")
    B.probe("set:enabled=True")
    B.ticks(1)
    time.sleep(0.5)
    on = B.probe("census")
    back = B.probe("styles")
    row(rows, "ST5_restore_default_and_master", "PASS" if back.get("strandTex") == list(strand_sets["StarWarsJawa"]) and
        not off.get("layerVisible") and on.get("layerVisible") and (on.get("layerVerts") or 0) > 0 and not back.get("nulls") else "FAIL",
        "MOD", {"strandTex": back.get("strandTex"), "offVisible": off.get("layerVisible"), "onVerts": on.get("layerVerts"),
                "printed": back.get("printedTex")})
    return per


AERIAL_RECT = (88, 178, 46, 20)        # validation_aerial.SITE (kept literal: that module imports this one)
SHOT_NAMES = {"StarWarsJawa": "jawa", "StarWars": "starwars", "ExtensionCord": "extcord", "Cybertek": "cybertek"}


def run_style_shots():
    """Screenshot each style on the same scenes from the same rects: the cord site and the aerial site."""
    B = Bridge()
    log, rows = [], []

    def snap(st):
        n = SHOT_NAMES[st]
        shot(B, "style_" + n, SITE, log)
        shot(B, "style_" + n + "_aerial", AERIAL_RECT, log)
    style_live(B, rows, log, shots_prefix=snap)
    B.probe("set:style=ExtensionCord")
    B.probe("set:extCordColor=2")
    B.probe("set:extCordColorMode=Single")
    B.ticks(1)
    shot(B, "style_extcord_single_brown", SITE, log)
    B.probe("defaults")
    B.ticks(1)
    out = os.path.join(HERE, "northstar", "validation_styles_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"mode": "style-shots", "rows": rows, "log": log}, f, indent=1, default=str)
    bad = [r for r in rows if r["status"] != "PASS"]
    print("style-shots: %d rows, %d not PASS -> %s" % (len(rows), len(bad), out))
    return 1 if bad else 0


# ============================================================================ M4 / M9 (own modes)
def _saves_stat():
    return {n: (os.path.getsize(os.path.join(SAVES, n)), int(os.path.getmtime(os.path.join(SAVES, n))))
            for n in os.listdir(SAVES) if os.path.isfile(os.path.join(SAVES, n))}


def _wait_playing(B, budget_s=240):
    st = None
    t0 = time.time()
    while time.time() - t0 < budget_s:
        st = B.call("rimworld/get_ui_state").get("programState")
        if st == "Playing" and B.call("jawa/map_info").get("success"):
            return True, int(time.time() - t0)
        time.sleep(2)
    return False, st


def _frame_poll_census(B):
    B.call("rimworld/frame_cell_rect", x=SITE[0], z=SITE[1] - 6, width=SITE[2], height=SITE[3] + 6, paddingCells=1)
    B.ticks(2)                       # nets + hookups form on the next tick (LEARNED, seed)
    time.sleep(1.0)
    B.probe("poll")
    return B.probe("census")


def _cord_set(c):
    """The comparable cord set: everything about the laid cords that must survive a save/load."""
    return {"geometryHash": c.get("geometryHash"), "edgeHashes": c.get("edgeHashes"), "nodeTypes": c.get("nodeTypes"),
            "decals": c.get("decals"), "conduitCells": c.get("conduitCells"), "cordEdges": c.get("cordEdges"),
            "strands": c.get("strands"),
            "ends": sorted((tuple(e["cell"]), e.get("wall"), e.get("netLive"), e.get("registryLive")) for e in c.get("ends") or [])}


def run_save_load(args):
    """M4 on whatever scene the current map holds (run after --live): census, save under a NEW name with the Saves
    folder stat'd before/after (save_game has written the current slot instead of the name), load, census, compare."""
    B = Bridge()
    rows = []
    res = {"mod": MOD, "mode": "save-load", "tier": TIER, "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows}
    name = args.save_load
    ca = _frame_poll_census(B)
    if not ca.get("edgeHashes"):
        row(rows, "M4_save_load_hash", "FAIL", "SITE", "no cords on the current map to compare: %s" % str(ca)[:200])
        return res
    before = _saves_stat()
    if name + ".rws" in before:
        row(rows, "M4_save_load_hash", "FAIL", "HARNESS", "%s.rws already exists; pick a new name" % name)
        return res
    sv = B.call("rimworld/save_game", saveName=name)
    time.sleep(3.0)
    after = _saves_stat()
    new = sorted(set(after) - set(before))
    changed = sorted(n for n in before if n in after and after[n] != before[n])
    gone = sorted(set(before) - set(after))
    ok_save = new == [name + ".rws"] and not changed and not gone
    row(rows, "M4a_save_landed_new_file_only", "PASS" if ok_save else "FAIL", "HARNESS",
        {"new": new, "changed": changed, "gone": gone, "size": after.get(name + ".rws"), "tool": sv.get("success")})
    if not ok_save:
        res["aborted"] = "save did not land as a new file only -- not loading"
        return res
    with open(os.path.join(SAVES, name + ".rws"), "rb") as f:
        blob = f.read()
    hits = [blob[max(0, i - 120):i + 80].decode("utf-8", "replace") for i in _find_all(blob, b"MessyConduit")]
    res["save_mentions"] = hits
    # Run 2026-10-02: the save held <li Class="RimMandrake.MessyConduit.RM_MapComponent_CordGraph" />, which made a
    # mod-less load log two red errors (M9). Nothing of ours may be in a save; the packageId in the mod list is
    # lowercase and does not match this needle.
    row(rows, "M9a_save_holds_nothing_of_ours", "PASS" if not hits else "FAIL", "MOD",
        {"count": len(hits), "first": [h.strip()[-160:] for h in hits[:4]]})
    ld = B.call("rimworld/load_game", saveName=name)
    ok, waited = _wait_playing(B)
    if not ok:
        row(rows, "M4_save_load_hash", "FAIL", "SITE", {"load": ld.get("success"), "state": waited})
        return res
    cb = _frame_poll_census(B)
    sa, sb = _cord_set(ca), _cord_set(cb)
    diff = sorted(k for k in sa if sa[k] != sb[k])
    row(rows, "M4_save_load_hash", "PASS" if not diff and sa["edgeHashes"] else "FAIL", "MOD",
        {"geometryHash": [sa["geometryHash"], sb["geometryHash"]], "edges": len(sa["edgeHashes"] or {}), "differs": diff,
         "loadSeconds": waited, "spawned": cb.get("spawnedConduitTexture")})
    res["before"], res["after"] = sa, sb
    return res


def _find_all(blob, needle):
    i = blob.find(needle)
    while i >= 0:
        yield i
        i = blob.find(needle, i + 1)


def run_removal_check(args):
    """M9: load a save made WITH the mod on a tier WITHOUT it; no red error may name the mod."""
    B = Bridge()
    rows = []
    res = {"mod": MOD, "mode": "removal-check", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows}
    rm = B.call("jawa/running_mods", details=False)
    running = [p.lower() for p in rm.get("packageIds") or []]
    if not running or PKG in running:
        row(rows, "M9_remove_mod_clean", "UNMEASURED", "SITE", "mod list unreadable or %s still running" % PKG)
        return res
    lg0 = B.call("rimbridge/list_logs", limit=500, minimumLevel="warning")
    base = max([x.get("Sequence", 0) for x in lg0.get("logs") or []] or [0])
    log_off = os.path.getsize(PLAYER_LOG)
    ld = B.call("rimworld/load_game", saveName=args.removal_check, ignoreModCompatibility=True)
    ok, waited = _wait_playing(B)
    if not ok:
        row(rows, "M9_remove_mod_clean", "FAIL", "MOD", {"load": ld, "state": waited})
        return res
    B.call("rimworld/jump_camera_to_cell", x=X0 + 14, z=Z0 + 4)
    B.ticks(60)                                   # a second of play: ticks, nets, a section regenerate in view
    time.sleep(1.0)
    lg = B.call("rimbridge/list_logs", limit=500, minimumLevel="warning")
    new = [e for e in lg.get("logs") or [] if (e.get("Sequence") or 0) > base]
    errs = [e for e in new if str(e.get("Level", "")).lower() in ("error", "exception")]
    ours = [e for e in errs if any(m in (str(e.get("Message", "")) + str(e.get("StackTrace", ""))) for m in MOD_MARKERS)]
    with open(PLAYER_LOG, "rb") as f:
        f.seek(log_off)
        tail = f.read().decode("utf-8", "replace").splitlines()
    plog = [ln.strip()[:240] for ln in tail if any(m in ln for m in MOD_MARKERS)]
    lt = B.call("jawa/list_things", defName="PowerConduit", limit=3)
    row(rows, "M9_remove_mod_clean", "PASS" if not ours and lt.get("things") else "FAIL", "MOD",
        {"running": len(running), "loadSeconds": waited, "errorsNamingMod": [str(e.get("Message", ""))[:240] for e in ours[:6]],
         "playerLogLinesNamingMod": plog[:8], "otherErrors": [str(e.get("Message", ""))[:160] for e in errs if e not in ours][:6],
         "newWarnings": len(new) - len(errs), "conduitStillThere": len(lt.get("things") or [])})
    return res


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--fresh-map", action="store_true")
    ap.add_argument("--out", default=None)
    ap.add_argument("--save-load", default=None, metavar="NAME", help="M4: census, save as NAME (new), load, census, compare")
    ap.add_argument("--removal-check", default=None, metavar="NAME", help="M9: load NAME on a tier WITHOUT the mod, read the log")
    ap.add_argument("--style-shots", action="store_true",
                    help="lane C: on the current map (after --live and validation_aerial --live) screenshot every style, same rects")
    a = ap.parse_args(argv)
    if a.style_shots:
        return run_style_shots()
    if a.save_load or a.removal_check:
        res = run_save_load(a) if a.save_load else run_removal_check(a)
        os.makedirs(os.path.join(HERE, "northstar"), exist_ok=True)
        out = a.out or os.path.join(HERE, "northstar", "validation_%s_%s.json" % (res["mode"], time.strftime("%Y%m%dT%H%M%S")))
        with open(out, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        bad = [r for r in res["rows"] if r["status"] not in ("PASS", "INFO")]
        print("%s: %d rows, %d not PASS -> %s" % (res["mode"], len(res["rows"]), len(bad), out))
        return 1 if bad or res.get("aborted") else 0
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
