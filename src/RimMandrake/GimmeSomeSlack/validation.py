"""validation.py -- Gimme Some Slack functional script (debug_process.md section 2), phase 1a.

Walk: design/validation_walks/RimMandrake/GimmeSomeSlack.md (## must be true lines M1..M9).
Design: design/RimMandrake/messy_conduit_design_2026-10-02.md (section 5 "First functional script").

    python3    src/RimMandrake/GimmeSomeSlack/validation.py                 # offline tier, 0 ticks
    python.exe src/RimMandrake/GimmeSomeSlack/validation.py --live --fresh-map   # gimmesomeslack tier, bridge held
    python.exe src/RimMandrake/GimmeSomeSlack/validation.py --save-load NAME     # M4 on the current map's scene (after --live)
    python.exe src/RimMandrake/GimmeSomeSlack/validation.py --removal-check NAME # M9: a tier WITHOUT the mod (e.g. flowworks)
    python.exe src/RimMandrake/Utils/modcheck/cli.py run GimmeSomeSlack           # the same checks as a modcheck suite

MODCHECK SUITE (module-level `suite`, 2026-10-03). The standalone modes above and the suite run the SAME
functions; the CLI is a thin wrapper. Every standalone row becomes one component of the same id (FAIL raises;
UNMEASURED/UNBUILT/UNCOVERED read UNMEASURED, never PASS).
  * chain `offline_O1_O5`: run_offline(). Under python.exe (no numpy) it runs in WSL python3 via `--rows-json -`.
  * chain `live_battery`: live_battery() on the runner's map and Session. The scene is built around the runner's
    anchor (clamped inside the map), every tick goes through t.wait_ticks (clockgate + detector sweeps when the
    run is situational), the runner's map stands in for L0 (--fresh-map), and the SITE rect is destroyed at the end.
  Separate lanes, NOT chains, and why:
  * M4 --save-load: it loads a save, which replaces the map the runner's Session, anchor, fixture ledger and
    bland-world proof belong to; every later chain would run on a map the runner did not prepare.
  * M9 --removal-check: needs a cold load onto a mod list WITHOUT this mod; a suite runs inside one list.
  * northstar_matrix/run_live.py: places 100 scenes over an absolute 226x100 REGION with map-wide clears
    (non-colonists destroyed, weather/clock pinned), which the anchor/teardown model and the bland world cannot
    contain; it reads a spec JSON precomputed by design_spec.py (numpy, absent under python.exe); ~26 min wall.

M4 (--save-load): census, save as a NEW name with the Saves folder stat'd before/after (only NAME.rws may
appear, nothing else may change), assert the save holds nothing of ours, load it, census, compare the cord set
(geometry hash, per-edge hashes, node types, decals, ends). M9 (--removal-check): load_game NAME with
ignoreModCompatibility on a list without the mod, step 60 ticks, no warning+ log entry or Player.log line may
name the mod. Batch: --live, then --save-load, then ONE cold load onto the other tier for --removal-check.

Offline tier: O1 mod files (About, csproj Compile list == every Source/*.cs outside SelfTest, DLL +
.srchash, textures, the transparent conduit PNG all-zero), O2 settings defaults == shipped table,
O3 C# core SelfTest against the Python oracle (selftest_gimmesomeslack.py) + its --probe (a planted
mismatch must turn every scene red), O4 the Python oracle's own selftest.

Live tier (one fresh quicktest map, ~270 ticks total): a battery, a 9x7 walled room with a door,
a conduit run through the doorway and into the room, a branch, a lamp, a run INTO the east wall,
and a far-away isolated conduit run for the local-invalidation check. State is read through
GimmeSomeSlackProbe (written and read with the existing jawa/mod_settings_field tool; the mod's map
component answers on its next frame), never from screenshots.

LEARNED (seed; each line is a check below, not prose only):
  * HARNESS (lane F 2026-10-02): a fresh map can put a SteamGeyser inside the scene; the clear's destroy_batch then
    logs a red "Tried to destroy non-destroyable thing" that Z_log_budget charged to the mod. Counted separately now.
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
  * HARNESS: status.mod_hash takes the mod DIRECTORY (a bare "GimmeSomeSlack" hashed nothing:
    e3b0c442...), and results must land in northstar/ (excluded from the hash) or each run's own
    output makes the next record STALE.
  * Live pass 2 (2026-10-02), two MOD defects found by the new modes and fixed in RM_MapComponent_CordGraph.cs:
    (1) M4 FAILED: after a load the graph had 8 edges but 0 laid pieces -- no cords on ANY loaded save. Log:
    "Could not regenerate layer SectionLayer_RM_MessyCords: NRE at MapDrawer.MapMeshDirty". MapDrawer.
    RegenerateEverythingNow creates its Sections one by one inside the regen loop, so dirtying a later section
    hit a null slot, and pieces were published after the dirty loop so the throw lost them. A fresh quicktest
    map never shows it (no conduit exists at its first regenerate) -- only a load does.
    (2) M9 FAILED: the save held <li Class="RimMandrake.GimmeSomeSlack.RM_MapComponent_CordGraph" /> (every
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
    The settings round trip (ST4) writes the real Config/Mod_GimmeSomeSlack_GimmeSomeSlackMod.xml; when that file did not
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
if UTILS not in sys.path:
    sys.path.insert(0, UTILS)
from modcheck import Suite, ExpectationFailed  # noqa: E402

MOD = "GimmeSomeSlack"
PKG = "mandrake.rm.gimmesomeslack"
TIER = "gimmesomeslack"
PROBE = "RimMandrake.GimmeSomeSlack.GimmeSomeSlackProbe"
SETTINGS = "RimMandrake.GimmeSomeSlack.GimmeSomeSlackSettings"
TRANSPARENT = "RimMandrake/GimmeSomeSlack/ConduitTransparent"

SHIPPED = {"enabled": "true", "style": "CordStyle.StarWarsJawa", "slack": "1f", "loopBudget": "16f",
           "cordsPerConnection": "3", "tangles": "true", "needlessLoops": "true", "breakReadout": "true",
           "sparkIntensity": "1f", "hideHookupWires": "true", "debugDraw": "false",
           # phase 1b lane A
           "tangleMin": "9", "whip": "true", "downedWire": "true", "sparksOnlyOverlay": "false",
           "maxSparkingEnds": "24", "highlight": "true", "sway": "true", "swayAmplitude": "1f", "lod": "true",
           "swayMode": "SwayMode.CPU", "floorRipple": "false",
           # lane C art styles
           "extCordColorMode": "ExtCordColorMode.Mixed", "extCordColor": "0"}

# The UNBUILT/UNCOVERED placeholder rows (U_motion_look, U_style_missing_art, M4_save_load_hash, M9_remove_mod_clean) are
# GONE (owner 2026-10-05 densification, design/RimMandrake/gimmesomeslack_verification_consolidation_2026-10-05.md
# section 2 "Core" + section 7 items 3-4): the two U looks are taste and live on the human review sheet as notes
# (human_review.py), M4 is proof_all.py's SL3 (one save/load), M9 is the walk's extended E1 (paused by the owner).

# SHARED (set by proof_all.py): one session, one map. The per-script harness/site rows collapse into proof_all's
# P1-P3 (doc section 2 "Harness/site rows"): a harness row is then written only when it is NOT PASS (a fault still
# surfaces under its own id; a green one becomes a site note), and per-script log budgets / determinism / save rows
# are proof_all's session rows (Z, D1/D2, SL1-SL4).
SHARED = False
SITE_NOTES = []


def hrow(rows, rid, status, cls, detail):
    """A harness/site row: a row of its own standalone; in SHARED mode only when it is not PASS."""
    if SHARED and status == "PASS":
        SITE_NOTES.append({"id": rid, "detail": detail})
        return
    row(rows, rid, status, cls, detail)


SAVES = os.path.join(os.environ.get("USERPROFILE", ""), "AppData", "LocalLow", "Ludeon Studios",
                     "RimWorld by Ludeon Studios", "Saves")
PLAYER_LOG = os.path.join(os.path.dirname(SAVES), "Player.log")
MOD_MARKERS = ("GimmeSomeSlack", "RM_MessyCords", "CordGraph", "ConduitTransparent")


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
    csproj = open(os.path.join(HERE, "Source", "RimMandrake_GimmeSomeSlack.csproj"), encoding="utf-8").read()
    srcs = sorted(os.path.relpath(p, os.path.join(HERE, "Source")).replace("/", "\\")
                  for p in glob.glob(os.path.join(HERE, "Source", "**", "*.cs"), recursive=True)
                  if "SelfTest" not in p and "/obj/" not in p and "/bin/" not in p)
    missing = [s for s in srcs if '<Compile Include="%s" />' % s not in csproj]
    if missing:
        probs.append("csproj misses Compile lines (they would compile into nothing): %s" % missing)
    dll = os.path.join(HERE, "Assemblies", "RimMandrakeGimmeSomeSlack.dll")
    if not (os.path.exists(dll) and os.path.exists(dll + ".srchash")):
        probs.append("DLL or .srchash missing")
    tex = os.path.join(HERE, "Textures", "RimMandrake", "GimmeSomeSlack")
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
    src = open(os.path.join(HERE, "Source", "GimmeSomeSlackMod.cs"), encoding="utf-8").read()
    bad = []
    for f, v in SHIPPED.items():
        needle = " %s = %s;" % (f, v)
        if needle not in src:
            bad.append("%s != %s" % (f, v))
    row(rows, "O2_settings_defaults", "PASS" if not bad else "FAIL", "MOD", bad or "%d defaults match the shipped table" % len(SHIPPED))


def o3_csharp_selftest(rows):
    r = subprocess.run([sys.executable, os.path.join(UTILS, "selftest_gimmesomeslack.py")], capture_output=True, text=True,
                       timeout=600)
    tail = [ln for ln in r.stdout.splitlines() if "checks passed" in ln or ln.startswith("FAIL")]
    row(rows, "O3_core_selftest", "PASS" if r.returncode == 0 else "FAIL", "MOD", tail[-6:] or r.stderr[-300:])
    r2 = subprocess.run([sys.executable, os.path.join(UTILS, "selftest_gimmesomeslack.py"), "--probe", "--no-export"],
                        capture_output=True, text=True, timeout=600)
    pl = [ln for ln in r2.stdout.splitlines() if ln.startswith("PROBE")]
    row(rows, "O3n_selftest_can_fail", "PASS" if r2.returncode == 0 and pl else "FAIL", "HARNESS", pl or r2.stdout[-300:])


def o4_oracle(rows):
    r = subprocess.run([sys.executable, os.path.join(UTILS, "mockups", "messy_conduit", "selftest.py")],
                       capture_output=True, text=True, timeout=600)
    last = (r.stdout.strip().splitlines() or ["?"])[-1]
    row(rows, "O4_python_oracle", "PASS" if r.returncode == 0 else "FAIL", "HARNESS", last)


# ---------------------------------------------------------------- lane C: art styles (offline)
# Every style's required PNGs (paths relative to Textures/RimMandrake/GimmeSomeSlack), canvas, and kind. Wired by
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
STAGED_HOSE = ["Hose/" + n for n in ("Strand_Flat", "Strand_Plump", "Strand_Shadow", "Coupling_Brass", "Nozzle", "Reel_PumpHookup", "EndCap", "Binding", "Mouth", "Coupling_Bare", "EndCap_Bare", "Nozzle_Bare")]
# owner review round 1 (2026-10-04): the margin-safe switch (B3) and the extension-cord pieces in every cord colour (B14)
SHARED_FILES += ["PowerSwitch", "PowerSwitch_Off"]
STYLE_FILES["ExtensionCord"] += ["Styles/ExtCord/%s/%s" % (c, n) for c in ("Green", "Brown", "Yellow", "Blue")
                                 for n in ("Plug", "Junction_T", "Junction_X", "StubWall", "StubRock", "EndFrayed_Dead")]
ALLOWED_FALLBACKS = {"EndFrayed_Live", "PowerStrip", "PowerStripDark"}


def _canvas_for(rel):
    n = rel.split("/")[-1]
    if rel.startswith("Hose/Strand"):
        return (256, 64)
    if rel == "Hose/Binding":
        return (82, 40)            # the cloth wrap cropped from the accepted render (make_hose_binding.py, B22)
    if rel == "Hose/Mouth":
        return (64, 64)
    if n.startswith("Strand") or n in ("SpanShadow", "SpanWire"):
        return (128, 32)
    if n == "TapClamp" or rel == "Hose/Reel_PumpHookup":
        return (256, 256)          # art r5 (9245c831b): "256 px tap clamps"; the 2x2 reel's drum art is 256 too
    if n in ("EndFrayed_Dead", "EndFrayed_Live", "SparkGlow"):
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
    p = os.path.join(HERE, "Textures", "RimMandrake", "GimmeSomeSlack", rel + ".png")
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
    tdir = os.path.join(HERE, "Textures", "RimMandrake", "GimmeSomeSlack", "_o5probe")
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


def _band_px(path, xs=(10, 20)):
    from PIL import Image
    a = Image.open(path).convert("RGBA").getchannel("A")
    return max(sum(1 for y in range(a.size[1]) if a.getpixel((x, y)) > 128) for x in xs)


OWNER_WORDS = ("fire hoses they use", "firehose is shown as going OVER")   # the owner's words, quoted verbatim


def visible_fire_hose(paths):
    """Case-insensitive 'fire hose' / 'firehose' / 'fire-hose' hits in player- or reviewer-visible text (B20): every line
    of the given files except C#/Python identifiers. Returns [(path, line_no, text)]."""
    import re
    rx = re.compile(r"fire[\s_-]?hoses?", re.I)
    hits = []
    for p in paths:
        try:
            lines = open(p, encoding="utf-8").read().splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        for i, ln in enumerate(lines, 1):
            if any(q in ln for q in OWNER_WORDS):
                continue                         # the owner's verbatim words are quoted, never reworded
            for m in rx.finditer(ln):
                pre, post = ln[m.start() - 1:m.start()], ln[m.end():m.end() + 1]
                if "_" in m.group(0) or (pre and (pre.isalnum() or pre == "_")) or (post and (post.isalnum() or post == "_")):
                    continue                     # an identifier (FireHosesMod, fire_hose_x), not text
                hits.append((os.path.relpath(p, REPO), i, ln.strip()[:120]))
    return hits


def fire_hose_sweep_paths():
    out = []
    for ext in ("*.cs", "*.xml", "*.py", "*.md", "*.html"):
        out += [p for p in glob.glob(os.path.join(HERE, "**", ext), recursive=True) if "/obj/" not in p and "/bin/" not in p and "__pycache__" not in p]
    for rel in ("design/validation_walks/RimMandrake/GimmeSomeSlack.md", "design/RimMandrake/northstar_human_review.md",
                "design/RimMandrake/debug_process.md", "Transient/mc_human_review/KEYSHEET.md", "Transient/mc_human_review/keysheet.html"):
        p = os.path.join(REPO, rel)
        if os.path.exists(p):
            out.append(p)
    return [p for p in out if not p.endswith("validation.py")]


def o6_review_round1(rows):
    """Owner review round 1 (2026-10-04), the offline half: one load-bearing measurement per art/def bar.
    B3 switch art margin, B7 bracket is a vanilla wall attachment, B8 hose fittings match the hose band, B22 binding wrap wider than hose and fitting, B14 every
    extension-cord piece takes its cord colour, B6/B16/B19 per-look pole table current, B20 no visible 'fire hose'."""
    import colorsys
    import xml.etree.ElementTree as ET
    from PIL import Image
    probs, info = [], []
    tex = os.path.join(HERE, "Textures", "RimMandrake", "GimmeSomeSlack")
    # B3: the switch art keeps a fully transparent 6 px margin (of 128): nothing can be sampled at the tile edge
    for n in ("PowerSwitch", "PowerSwitch_Off"):
        im = Image.open(os.path.join(tex, n + ".png")).convert("RGBA")
        a = im.getchannel("A")
        edge = max(a.getpixel((x, y)) for x in range(128) for y in range(128) if x < 6 or y < 6 or x >= 122 or y >= 122)
        if edge != 0:
            probs.append("B3 %s: alpha %d inside the 6 px margin" % (n, edge))
    cv = open(os.path.join(HERE, "Source", "ConduitVisuals.cs"), encoding="utf-8").read()
    if 'SwitchTexPathOurs = "RimMandrake/GimmeSomeSlack/PowerSwitch"' not in cv or "ApplySwitch(invisible)" not in cv:
        probs.append("B3: ConduitVisuals does not swap the switch art")
    # B7: the bracket is placed the vanilla way (Core TorchWallLamp): attachment, not an edifice, drawn 0.9 onto the wall
    root = ET.parse(os.path.join(HERE, "Defs", "Aerial", "RM_AerialAnchors.xml")).getroot()
    br = next(d for d in root.iter("ThingDef") if d.findtext("defName") == "RM_AerialWallBracket")
    pw = [li.text for li in br.findall("placeWorkers/li")]
    gd = br.find("graphicData")
    offs = {k: gd.findtext("drawOffset" + k) for k in ("North", "South", "East", "West")}
    want = {"North": "(0,0,0.9)", "South": "(0,0,-0.9)", "East": "(0.9,0,0)", "West": "(-0.9,0,0)"}
    if br.findtext("building/isAttachment") != "true" or br.findtext("building/isEdifice") != "false" or pw != ["Placeworker_AttachedToWall"] \
            or offs != want or br.findtext("rotatable") != "true":
        probs.append("B7 bracket def: attachment=%s edifice=%s placeWorkers=%s offsets=%s" % (
            br.findtext("building/isAttachment"), br.findtext("building/isEdifice"), pw, offs))
    if "PlaceWorker_AerialWallBracket" in open(os.path.join(HERE, "Source", "Aerial", "PlaceWorkers_Aerial.cs"), encoding="utf-8").read():
        probs.append("B7: the old in-front-of-the-wall placeworker is still in the source")
    # B8: every hose fitting's hose band matches the band constant the code sizes it by (within 2 px of 128)
    # HARNESS 2026-10-05: the constant moved to HoseMath.cs (RM_MapComponent_Hoses aliases it as (float)HoseMath.PieceBand),
    # and the old regex crashed the whole offline tier; read the numeric definition wherever it lives
    import re
    hs = "".join(open(os.path.join(HERE, "Source", "Hose", f), encoding="utf-8").read() for f in ("HoseMath.cs", "RM_MapComponent_Hoses.cs"))
    pb = float(re.search(r"PieceBand = ([0-9.]+)f?[,;]", hs).group(1))
    for n, b in (("Coupling_Brass", pb), ("EndCap", pb)):
        px = _band_px(os.path.join(tex, "Hose", n + ".png"))
        info.append("%s band %d px (code %.0f)" % (n, px, b * 128))
        if abs(px - b * 128) > 2:
            probs.append("B8 %s: hose band %d px, code sizes it as %.0f px" % (n, px, b * 128))
    # B22: the binding wrap, measured from the PNGs and sized by the code's own formula: on a flat and a plump hose,
    # every fitting's widest part <= the wrap's drawn width, and the wrap >= 1.3 x the hose; the open end draws the
    # dark Mouth, never the old pale OpenEnd stub
    hm = open(os.path.join(HERE, "Source", "Hose", "HoseMath.cs"), encoding="utf-8").read()
    wk = float(re.search(r"WrapK = ([0-9.]+)", hm).group(1))
    fv, pe = [float(x) for x in re.search(r"FlatVisible = ([0-9.]+), PlumpExtra = ([0-9.]+)", hm).groups()]
    bind_code = float(re.search(r"BindBand = ([0-9.]+)f", hs).group(1))
    bim = Image.open(os.path.join(tex, "Hose", "Binding.png")).convert("RGBA")
    ba = bim.getchannel("A")
    bind_px = max(sum(1 for y in range(bim.size[1]) if ba.getpixel((x, y)) > 128) for x in range(bim.size[0]))
    bind_frac = bind_px / float(bim.size[1])
    # each constant read by name wherever it is DEFINED with a number (CouplingMax moved to HoseMath.cs; HARNESS 2026-10-05)
    maxes = {n: float(re.search(r"\b%s = ([0-9.]+)f?[,;]" % c, hs).group(1))
             for n, c in (("Coupling_Brass", "CouplingMax"), ("Nozzle", "NozzleMax"), ("EndCap", "EndCapMax"))}
    worst = []
    for vis in (fv, fv + pe):
        wrap_drawn = wk * vis / bind_code * bind_frac
        if wrap_drawn < 1.3 * vis - 1e-6:
            probs.append("B22 wrap %.3f < 1.3 x hose %.3f" % (wrap_drawn, vis))
        for n, mx in maxes.items():
            im = Image.open(os.path.join(tex, "Hose", n + ".png")).convert("RGBA").getchannel("A")
            mpx = max(sum(1 for y in range(128) if im.getpixel((x, y)) > 128) for x in range(128)) / 128.0
            if abs(mpx - mx) > 2 / 128.0:
                probs.append("B22 %s widest band %.3f, code says %.3f" % (n, mpx, mx))
            size = min(vis / pb, 0.95 * wk * vis / mx)
            fit_w = size * mpx
            worst.append(fit_w / wrap_drawn)
            if fit_w > wrap_drawn + 1e-6:
                probs.append("B22 %s on hose %.2f: fitting %.3f wider than wrap %.3f" % (n, vis, fit_w, wrap_drawn))
    # HARNESS 2026-10-05: per-look hose materials (style stage 3) draw the open end's mouth as hm.Mouth (the look's set)
    if os.path.exists(os.path.join(tex, "Hose", "OpenEnd.png")) or not ("HoseMaterials.Mouth" in hs or "PieceXZ(hm.Mouth" in hs) or "Wrap(" not in hs:
        probs.append("B22: open end still the OpenEnd stub, or no wrap drawn")
    info.append("B22 wrap band %d/%d px, wrap %.2f x hose, fitting/wrap max %.2f" % (bind_px, bim.size[1], wk * bind_frac / bind_code, max(worst)))
    if "public HoseEnd end = HoseEnd.Open;" not in open(os.path.join(HERE, "Source", "Hose", "CompHoseReel.cs"), encoding="utf-8").read():
        probs.append("B8: the free end does not default to Open")
    # B14: the recoloured pieces are current, and their cord pixels carry the cord colour (hue within 15 deg)
    rc = subprocess.run([sys.executable, os.path.join(UTILS, "mockups", "messy_conduit", "recolor_extcord_pieces.py"), "--check"],
                        capture_output=True, text=True, timeout=600)
    if rc.returncode != 0:
        probs.append("B14: recoloured pieces stale: %s" % rc.stdout.strip()[-200:])
    ext = os.path.join(tex, "Styles", "ExtCord")

    def hue(rgb):
        return colorsys.rgb_to_hsv(*[v / 255.0 for v in rgb])[0] * 360

    for c in ("Green", "Brown", "Yellow", "Blue"):
        st = Image.open(os.path.join(ext, "Strand_%s.png" % c)).convert("RGBA")
        sp = [p for p in st.getdata() if p[3] > 128]
        th = hue(tuple(sum(p[i] for p in sp) / len(sp) for i in range(3)))
        src = Image.open(os.path.join(ext, "Junction_T.png")).convert("RGBA")
        var = Image.open(os.path.join(ext, c, "Junction_T.png")).convert("RGBA")
        ch = [q for p, q in zip(src.getdata(), var.getdata()) if p != q and q[3] > 128]
        if not ch:
            probs.append("B14 %s: nothing recoloured" % c)
            continue
        mh = hue(tuple(sum(q[i] for q in ch) / len(ch) for i in range(3)))
        d = min(abs(mh - th), 360 - abs(mh - th))
        if d > 15:
            probs.append("B14 %s: cord pixels hue %.0f vs cord %.0f" % (c, mh, th))
    cm = open(os.path.join(HERE, "Source", "CordMaterials.cs"), encoding="utf-8").read()
    # HARNESS 2026-10-05: style stage 2 draws each piece with its GLOBAL material index (look x variant), DecalG(kind, g),
    # which falls back to Decal(kind); the per-variant table itself is still Decal(kind, variant)
    sl = open(os.path.join(HERE, "Source", "SectionLayer_RM_MessyCords.cs"), encoding="utf-8").read()
    if "public static Material Decal(DecalKind k, int variant)" not in cm or not (
            "CordMaterials.Decal(d.Kind, variant)" in sl or ("CordMaterials.DecalG(d.Kind, g)" in sl and "public static Material DecalG(" in cm)):
        probs.append("B14: the section layer does not draw pieces per cord variant")
    # B6/B16/B19: the per-look pole geometry table matches the wired art
    rp = subprocess.run([sys.executable, os.path.join(UTILS, "mockups", "messy_conduit", "wire_pole_art.py"), "--check"],
                        capture_output=True, text=True, timeout=600)
    if rp.returncode != 0:
        probs.append("B6: pole geometry table stale (re-run wire_pole_art.py)")
    wired = [ln.split(":")[0] for ln in rp.stdout.splitlines() if "crossarm row" in ln]
    info.append("real pole art: %s" % (wired or "none yet (tinted stand-ins)"))
    # per-build style stage 1: the 12 pole style defs, their art on disk, no ideo category lists them, no shared-def edit
    rs = subprocess.run([sys.executable, os.path.join(HERE, "validation_style.py"), "--offline"], capture_output=True, text=True, timeout=300)
    if rs.returncode != 0:
        probs.append("style stage 1 (validation_style.py --offline): %s" % rs.stdout.strip()[-200:])
    # B7 round 2: the wall bracket's per-look, per-facing art and its measured insulator table are current
    rb = subprocess.run([sys.executable, os.path.join(UTILS, "mockups", "messy_conduit", "wire_bracket_art.py"), "--check"],
                        capture_output=True, text=True, timeout=600)
    if rb.returncode != 0:
        probs.append("B7: bracket art / geometry table stale (re-run wire_bracket_art.py): %s" % rb.stdout.strip()[-200:])
    info.append("bracket art: %s" % [ln.split(":")[0] for ln in rb.stdout.splitlines() if ": wired" in ln])
    # B20: no visible 'fire hose' text, and the sweep can see one (sanity probe)
    hits = visible_fire_hose(fire_hose_sweep_paths())
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write("a Fire Hose here\nand fire_hose_id there\n")
    probe = visible_fire_hose([f.name])
    os.unlink(f.name)
    if hits:
        probs.append("B20: visible 'fire hose' text: %s" % hits[:4])
    if len(probe) != 1:
        probs.append("B20 sweep cannot see a planted 'Fire Hose' (%d hits)" % len(probe))
    row(rows, "O6_review_round1", "PASS" if not probs else "FAIL", "MOD", probs or "; ".join(info))


# GPT source read 2026-10-06 (design/RimMandrake/gss_gpt_source_read_2026-10-06.md): the Verse-bound fixes, checked by the
# shape of the shipped source (the Verse-free halves are C# selftest rows, SelfTest/GptReadFixChecks.cs). One (finding, file,
# fragment that must be present) per fix; the can-fail is the planted probe below, which must be reported missing.
GPT_READ_FIX_SHAPES = [
    ("B4 port cache uses CacheFresh", "Hose/CompHoseReel.cs", "HoseLive.CacheFresh(now, portTick, 60)"),
    ("B1 tick lays hoses on every map", "Hose/RM_MapComponent_Hoses.cs", "% 250 == 0) EnsureLay(r);"),
    ("B5 no no-outlet fallback lay", "Hose/RM_MapComponent_Hoses.cs", "HoseMath.LeadOutBlocked"),
    ("B2 order need judged on shortest route", "Hose/CompHoseReel.cs", "new Cell(target.x, target.z), -1, false)"),
    ("B8 hose length in the shape fingerprint", "Hose/HoseSettings.cs", '"|L" + maxLength'),
    ("B10 order loop check sees pending orders", "Hose/CompHoseReel.cs", "comp.Loops(this, relay, true)"),
    ("B11 resume rule for every dropped order", "Hose/Jobs/WorkGiver_HoseOrders.cs", "HoseOrderRules.MayResume("),
    ("B12 refused right-click restores the order", "Hose/Jobs/FloatMenuOptionProvider_Hose.cs", "r.pending = prevOrder;"),
    ("B13 pre-grab path failure clears the order", "Hose/Jobs/JobDriver_CarryHoseEnd.cs", "HoseOrderRules.KeepOrderAfterJob("),
    ("B14 port candidates in thing-id order", "Hose/HosePorts.cs", "ById(things, cands);"),
    ("B7 hose corridor hash has route cost", "Hose/RM_MapComponent_Hoses.cs", "CordBuilder.CellSig(w, c)"),
    ("A1 taps share one surplus", "Aerial/CompPowerTap.cs", "TapRegistry.TakenThisTick(victim)"),
    ("A2 switched-off tap drains nothing", "Aerial/CompPowerTap.cs", "if (victim != null && ours != null && working)"),
    ("A4 auto-link selected is player-only", "Aerial/CompAerialAnchor.cs", "b.Faction == Faction.OfPlayer"),
    ("A5 link verdict refuses a despawned end", "Aerial/CompAerialAnchor.cs", "return LinkVerdict.Gone;"),
    ("A6 queued auto-link saved", "Aerial/CompAerialAnchor.cs", '"rmAerialAutoLinkPending"'),
    ("A8 fallen lays watch the ground", "Aerial/RM_MapComponent_Aerial.cs", "FallenGroundCheck();"),
    ("A10 whip tails past the cap drawn still", "RM_MapComponent_CordGraph.cs", "else WhipStillDraws++;"),
    ("A15 restyle never crosses a cut span", "Aerial/RM_MapComponent_ConduitRuns.cs", "s.state == SpanState.Up &&"),
    ("A17 wall home for transmitter buildings", "CordWorldAdapter.cs", "SetWallHome(th, m);   // GPT source read"),
    ("A18 span meshes destroyed", "Aerial/RM_MapComponent_Aerial.cs", "Notify_SpansChanged() => ClearSpanMeshes();"),
    ("A19 dark strip aspect", "SectionLayer_RM_MessyCords.cs", "DecalAspect.Of(d.Kind)"),
    ("A20 unhooked lamp message shown", "Aerial/RM_MapComponent_ConduitRuns.cs", "this used to return before any message was shown"),
]


def gpt_read_fix_missing(shapes, src_dir):
    miss = []
    for name, rel, frag in shapes:
        path = os.path.join(src_dir, rel)
        body = open(path, encoding="utf-8").read() if os.path.exists(path) else ""
        if frag not in body:
            miss.append(name)
    return miss


def o7_gpt_read_fixes(rows):
    src = os.path.join(HERE, "Source")
    miss = gpt_read_fix_missing(GPT_READ_FIX_SHAPES, src)
    probe = gpt_read_fix_missing([("planted", "Hose/HoseMath.cs", "this fragment is not in the source 7f3a")], src)
    import struct
    sizes = {}
    for rel in ("PowerStrip.png", "Styles/ExtCord/PowerStrip_Off.png"):
        with open(os.path.join(HERE, "Textures", "RimMandrake", "GimmeSomeSlack", rel), "rb") as f:
            sizes[rel] = struct.unpack(">II", f.read(24)[16:24])
    if any(w != 2 * h for w, h in sizes.values()):
        miss.append("A19 power strip art is not 2:1 (DecalAspect 0.5 assumes it): %s" % sizes)
    if probe != ["planted"]:
        miss.append("probe: the shape check cannot see a missing fragment")
    row(rows, "O7_gpt_read_fixes", "PASS" if not miss else "FAIL", "MOD",
        miss or "%d fix shapes present; planted probe reported missing" % len(GPT_READ_FIX_SHAPES))


def run_offline():
    rows = []
    o7_gpt_read_fixes(rows)
    o1_files(rows)
    o2_defaults(rows)
    o5_style_art(rows)
    o6_review_round1(rows)
    o3_csharp_selftest(rows)
    o4_oracle(rows)
    return rows


# ============================================================================ live
class _BridgeBase(object):
    """call / probe / ticks over a raw transport (`_raw`): the standalone socket or the suite's Session."""

    def _raw(self, tool, kw):
        raise NotImplementedError

    def call(self, tool, **kw):
        r = self._raw(tool, kw) or {}
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


class Bridge(_BridgeBase):
    """Standalone: its own socket to the bridge."""

    def __init__(self):
        sys.path.insert(0, UTILS)
        import rimbridge_client as rb  # noqa: E402
        host, port, token = rb.resolve_endpoint()
        self.S = rb.RimBridge(host=host, port=port, token=token, timeout=600.0)
        self.S.connect()

    def _raw(self, tool, kw):
        return self.S.call(tool, kw, check=False)


class SuiteBridge(_BridgeBase):
    """Suite: calls ride the runner's Session; game time goes through t.wait_ticks (clock-verified, and under a
    situational run budgeted + detector-swept), so no tick moves behind the watch's back."""

    def __init__(self, t):
        self.t = t

    def _raw(self, tool, kw):
        return self.t.session.call(tool, **kw)

    def ticks(self, n):
        self.t.wait_ticks(n)
        return {"success": True}


# The scene, cells relative to an origin (X0, Z0). Standalone: absolute 150,150 on a fresh quicktest map (centre
# 125,125 avoided: colonists stand there). Suite: the runner's anchor, clamped inside the map (_set_origin).
SCENE_EXTENT = (-2, -2, 32, 12)                   # min dx, min dz, max dx, max dz of everything built (== SITE)


def _set_origin(x0, z0):
    g = globals()
    X0, Z0 = x0, z0                                         # locals here; published below
    g["X0"], g["Z0"] = X0, Z0
    g["SITE"] = (X0 - 2, Z0 - 2, 34, 14)                   # cleared + painted Soil + unfogged
    g["ROOM"] = (X0 + 10, Z0, X0 + 18, Z0 + 6)              # wall perimeter x0,z0,x1,z1
    g["DOOR"] = (X0 + 10, Z0 + 3)
    g["BATTERY"] = (X0 + 2, Z0 + 3)                         # Battery 1x2, rot N: cells z..z+1
    g["MAIN"] = [(x, Z0 + 3) for x in range(X0 + 3, X0 + 18)]        # through the door, across the room
    g["BRANCH"] = [(X0 + 13, Z0 + 4), (X0 + 13, Z0 + 5)]               # north branch -> lamp (its hookup keeps it)
    g["INTO_WALL"] = [(X0 + 17, Z0 + 2), (X0 + 18, Z0 + 2)]            # off the main run's end, INTO the east wall
    g["LAMP"] = (X0 + 12, Z0 + 5)                                      # nearest conduit = the branch end
    g["FAR"] = [(X0 + 28, Z0 + 9), (X0 + 29, Z0 + 9)]                  # isolated far-away run (local invalidation)
    g["GAP"] = (X0 + 7, Z0 + 3)                                        # the conduit cell destroyed for the break
    # phase 1b lane A plot (see lane_a_live)
    g["BAT2"] = (X0 + 19, Z0 + 8)
    g["FIELD"] = [(x, z) for x in range(X0 + 20, X0 + 24) for z in range(Z0 + 8, Z0 + 11)]
    g["RUN2"] = [(X0 + 24, Z0 + 9), (X0 + 25, Z0 + 9), (X0 + 26, Z0 + 9)]
    g["WALL2"] = [(X0 + 26, Z0 + 8), (X0 + 26, Z0 + 9), (X0 + 26, Z0 + 10)]


def origin_for_anchor(anchor, size_x, size_z, margin=3):
    """The scene origin that centres the scene on `anchor`, clamped so the whole SITE (+margin) is on the map."""
    mx0, mz0, mx1, mz1 = SCENE_EXTENT
    x = anchor[0] - (mx0 + mx1) // 2
    z = anchor[1] - (mz0 + mz1) // 2
    x = max(margin - mx0, min(size_x - 1 - margin - mx1, x))
    z = max(margin - mz0, min(size_z - 1 - margin - mz1, z))
    return x, z


_set_origin(150, 150)


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
    return live_battery(Bridge(), fresh_map=args.fresh_map)


def _reraise_harness_stop(ex):
    """A detector / clock abort (watch.SurpriseAbort) or a failed clock-verified wait must end the suite
    component, never be folded into a block's own FAIL row (that would charge the environment to the mod)."""
    if getattr(ex, "is_surprise_abort", False) or isinstance(ex, ExpectationFailed):
        raise ex


def live_battery(B, fresh_map=False, rows=None):
    """The live tier on B's map. `rows` (optional) is filled in place, so a caller sees every row measured
    before an abort."""
    rows = [] if rows is None else rows
    log = []
    res = {"mod": MOD, "mode": "live", "tier": TIER, "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows}
    if fresh_map:
        B.call("rimworld/go_to_main_menu")
        r = B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
        st = None
        for _ in range(90):
            st = B.call("rimworld/get_ui_state").get("programState")
            if st == "Playing" and B.call("jawa/map_info").get("success"):
                break
            time.sleep(2)
        hrow(rows, "L0_fresh_map", "PASS" if st == "Playing" else "FAIL", "SITE", {"start": r.get("success"), "programState": st})
        if st != "Playing":
            res["aborted"] = "no fresh map"
            return res
    # environment fingerprint for `modcheck record`
    env = {}
    rm = B.call("jawa/running_mods", assembly="RimMandrakeGimmeSomeSlack", details=False)
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
    hrow(rows, "L1_tier_running", "PASS" if PKG in env.get("running", []) else "FAIL", "SITE",
        "%d mods running, gimmesomeslack %s" % (len(env.get("running", [])), PKG in env.get("running", [])))
    lg0 = B.call("rimbridge/list_logs", limit=500, minimumLevel="warning")
    logs0 = lg0.get("logs") or []
    log_base = max([x.get("Sequence", 0) for x in logs0] or [0])
    bridge_line = any("[RimBridge]" in (x.get("Message") or "") for x in logs0)
    pre = [x.get("Message", "")[:200] for x in logs0 if "GimmeSomeSlack" in (x.get("Message", "") + x.get("StackTrace", ""))
           and (x.get("Level") or "").lower() in ("error", "exception")]
    hrow(rows, "L2_startup_log_clean", ("PASS" if not pre else "FAIL") if bridge_line else "UNMEASURED", "MOD",
        pre or "no GimmeSomeSlack error in %d warn+ startup entries (sanity: [RimBridge] line seen=%s)" % (len(logs0), bridge_line))
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
    hrow(rows, "S0_scene_built", "PASS" if ok_scene else "FAIL", "SITE", dict(built, battery=bat_id, stored=bs.get("storedEnergyAfter")))
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
    # M2 is written after the break (M8) so it is evaluated on the post-break census too -- see there.
    row(rows, "M2b_no_vertex_unwalkable", "PASS" if c0.get("verticesInUnwalkable") == 0 and c0.get("interiorVertices", 0) > 0 else "FAIL",
        "MOD", {k: c0.get(k) for k in ("verticesInUnwalkable", "interiorVertices", "fellBack", "unroutable")})
    # ---------------------------------------------------------------- M6: hookup wire hidden, overlay intact
    m6 = (c0.get("hookupWiresSuppressed") or 0) > 0 and (c0.get("overlayConnectorVerts") or 0) > 0
    row(rows, "M6_overlay_lines_intact", "PASS" if m6 else "FAIL", "MOD",
        {k: c0.get(k) for k in ("hookupWiresSuppressed", "overlayWiresPrinted", "overlayConnectorVerts")})
    # ---------------------------------------------------------------- determinism (fresh builder, same map)
    # D1 (fresh builder reproduces every edge) is the same predicate as the matrix's D2 on a superset of boards; in a
    # SHARED (proof_all) session D2 carries it (consolidation doc section 2 "Determinism"); standalone it stays here.
    if not SHARED:
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
    # M2 on BOTH the built scene (c0) and the post-break census (c2). The one-cell gap splits the PowerNet, so a cord
    # across it IS a cross-net edge: M8b ("no cord across the gap") is this predicate on c2 and is cut as a row
    # (consolidation doc section 2 "Core": "cut M8b after that one-line harness change").
    m2 = all(c.get("cordsAcrossNets") == 0 and c.get("cordEndsWithoutNet") == 0 for c in (c0, c2))
    row(rows, "M2_cords_only_within_net", "PASS" if m2 else "FAIL", "MOD",
        {"built": {k: c0.get(k) for k in ("cordsAcrossNets", "cordsAcrossNetsList", "cordEndsWithoutNet")},
         "afterBreak": {k: c2.get(k) for k in ("cordsAcrossNets", "cordsAcrossNetsList", "cordEndsWithoutNet")}})
    try:
        lane_a_live(B, rows, log)
    except Exception as ex:  # noqa: BLE001
        _reraise_harness_stop(ex)
        row(rows, "P1B_block", "FAIL", "HARNESS", "lane A block raised: %r" % ex)
    try:
        style_live(B, rows, log)
    except Exception as ex:  # noqa: BLE001
        _reraise_harness_stop(ex)
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
    # the scene clear's own destroy_batch over a map geyser/monolith ("Tried to destroy non-destroyable thing
    # SteamGeyser..."): the harness, not the mod -- counted, never charged to the mod (run_live.py does the same)
    site = [e for e in errs if "non-destroyable" in str(e.get("Message", ""))]
    errs = [e for e in errs if e not in site]
    if not SHARED:                   # SHARED: one run-end log budget over the whole session (proof_all Z)
        row(rows, "Z_log_budget", "PASS" if not errs else "FAIL", "MOD",
            {"errors": [str(e.get("Message", ""))[:200] for e in errs[:6]], "newWarnings": len(new), "siteClearErrors": len(site)})
    t_end = B.probe("census").get("ticksGame")
    res["ticks"] = (t_end - t_start) if isinstance(t_end, int) and isinstance(t_start, int) else None
    res["log"] = log
    return res


# ============================================================================ phase 1b lane A (live)
# A second plot north-east of the room: battery 2, a 4x3 conduit field (a TANGLE at the default threshold 9),
# a run east into a wall that carries one buried conduit cell (a live WALL terminal = downed wire, outdoors so
# it sways). Run after M8b, so the west end of the gap is a LIVE floor terminal (whip) on screen.
# BAT2 / FIELD / RUN2 / WALL2 are set by _set_origin with the rest of the scene.
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
    hrow(rows, "P1B_plot_built", "PASS" if b3.get("survived") == len(FIELD + RUN2) and bs.get("storedEnergyAfter", 0) > 0 else "FAIL",
        "SITE", {"conduit": b3.get("survived"), "battery2": bat2, "stored": bs.get("storedEnergyAfter")})
    # owner review 2026-10-04 B1: power strips are the Modern (ExtensionCord) look only; the default Scrapper look's
    # pile is junction boxes. So the strip rows (B6, B6b) read the field in the Modern look; settle is look-agnostic.
    B.probe("set:style=ExtensionCord")
    B.ticks(2)
    time.sleep(1.0)
    m0 = motion(B)
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
    # B4c SPARK_EFFECT_BUDGET_REWORK_1 A2: sparkIntensity scales the sparks thrown by downed wall wires (credit k per event)
    spk = {}
    for k in ("0.5", "2"):
        B.probe("set:sparkIntensity=%s" % k)
        B.probe("motionreset")
        B.ticks(900)
        spk[k] = B.probe("motion").get("sparksThrown", 0)
    B.probe("set:sparkIntensity=1")
    row(rows, "B4c_spark_intensity_scales_downed", "PASS" if spk["2"] > 0 and spk["2"] >= 2 * max(spk["0.5"], 1) else "FAIL", "MOD",
        {"sparksThrown900": spk, "liveWallEnds": m2.get("liveWallEnds")})
    # B4d SPARK_EFFECT_BUDGET_REWORK_1 A1: ONE shared spark set, capped at maxSparkingEnds in total, on-screen ends first.
    # The scene has only 2 live ends ~11 cells apart (one camera view holds both), so a powered 3-cell stub is built ~70 cells
    # away and the cap set to 1 (the same rule as "8 of many"): framed on the stub, the one chosen end must be ITS end (1 of 3
    # live ends on screen); framed on the scene, one of the scene's. Measured 2026-10-09: a whole-scene frame alone could not tell.
    fx, fz = (X0 - 70, Z0) if X0 >= 80 else (X0 + 70, Z0)
    frect = "%d,%d,8,6" % (fx - 1, fz - 1)
    B.call("jawa/destroy_batch", rects=frect, categories="All")
    B.call("jawa/set_terrain_batch", ops="Soil:" + frect)
    B.call("jawa/set_fog", action="unfog", rect=frect)
    B.call("jawa/build_batch", ops="Battery:%d,%d,0" % (fx, fz), faction="player")
    B.call("jawa/build_batch", ops=ops("PowerConduit", [(fx + 1, fz), (fx + 2, fz), (fx + 3, fz)]), faction="player", wipeExisting=False)
    flt = B.call("jawa/list_things", defName="Battery", rect="%d,%d,1,2" % (fx, fz), limit=3)
    fbid = next((t.get("id") or t.get("thingId") for t in flt.get("things") or []), None)
    if fbid:
        B.call("jawa/battery_set", thing=fbid, mode="setPct", value=1.0)
    B.ticks(3)
    B.probe("poll")
    B.ticks(2)
    bud = {}
    B.probe("set:maxSparkingEnds=1")
    for name, (cx, cz) in (("stub", (fx + 2, fz)), ("scene", (X0 + 14, Z0 + 2))):
        B.call("rimworld/frame_cell_rect", x=cx, z=cz, width=1, height=1, paddingCells=0)
        time.sleep(1.5)
        mm = B.probe("motion")
        bud[name] = {k: mm.get(k) for k in ("liveEndsAll", "liveEndsOnScreen", "sparkSet", "sparkSetOnScreen", "maxSparkingEnds")}
    B.probe("set:maxSparkingEnds=24")
    mm = B.probe("motion")
    bud["cap24"] = {k: mm.get(k) for k in ("liveEndsAll", "sparkSet", "maxSparkingEnds")}
    st_, s_, c_ = bud["stub"], bud["scene"], bud["cap24"]
    b4d = (st_.get("liveEndsAll") or 0) >= 3 and st_.get("liveEndsOnScreen") == 1 and st_.get("sparkSet") == 1 \
        and st_.get("sparkSetOnScreen") == 1 and s_.get("sparkSet") == 1 and s_.get("sparkSetOnScreen") == 1 \
        and c_.get("sparkSet") == min(24, c_.get("liveEndsAll") or 0)
    row(rows, "B4d_spark_budget_shared_visible_first", "PASS" if b4d else "FAIL", "MOD", bud)
    B.call("jawa/destroy_batch", rects=frect, categories="All")
    B.ticks(2)
    B.probe("poll")
    B.call("rimworld/frame_cell_rect", x=SITE[0], z=SITE[1], width=SITE[2], height=SITE[3], paddingCells=1)
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
    optional_motion_live(B, rows, a)
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
    # HARNESS (proof_all runs 1-2, 2026-10-05): root 58 is NOT the far zoom on every camera setup -- with the tier's camera
    # mod the root range is 0.5..100 and 58 reads CurrentZoom "Middle" (measured: 58 and 60 Middle, 100 Furthest). FALSE
    # THEORY first tried: the camera was still easing (polling 5 s at 58 stayed Middle). Zoom to the camera's own maximum.
    far_root = max(58, int(((cam.get("sizeRange") or {}).get("max")) or 58))
    B.call("rimworld/set_camera_zoom", rootSize=far_root)
    t_z = time.time()
    f1 = motion(B, 3)
    while f1.get("zoom") != "Furthest" and time.time() - t_z < 5.0:
        f1 = motion(B, 2)
    shot_far = shot(B, "p1b_04_far_zoom_lod", (SITE[0] - 10, SITE[1] - 10, SITE[2] + 20, SITE[3] + 20), log, pad=0)
    # LEARNED run 1b-1: frame_cell_rect moves the camera but keeps a Furthest zoom; set the root back explicitly
    B.call("rimworld/set_camera_zoom", rootSize=cam.get("rootSize") or 24)
    B.call("rimworld/frame_cell_rect", x=SITE[0], z=SITE[1], width=SITE[2], height=SITE[3], paddingCells=1)
    f2 = motion(B, 3)
    lod_ok = f1.get("lodFarNow") and f1.get("lodEnabled", 0) > 0 and f1.get("fullEnabled") == 0 and \
        (not f2.get("lodFarNow")) and f2.get("lodEnabled") == 0 and f2.get("fullEnabled", 0) > 0
    row(rows, "B8_lod_far_zoom", "PASS" if lod_ok else "FAIL", "MOD",
        {"far": {k: f1.get(k) for k in ("zoom", "lodFarNow", "lodSubMeshes", "lodEnabled", "fullSubMeshes", "fullEnabled")},
         "close": {k: f2.get(k) for k in ("zoom", "lodFarNow", "lodEnabled", "fullEnabled")}, "camera0": cam.get("rootSize"), "farRoot": far_root, "shot": bool(shot_far)})
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
    B.probe("set:style=StarWarsJawa")              # back to the shipped default look for the rows after lane A
    B.ticks(2)
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


def optional_motion_live(B, rows, cpu):
    """The two OPTIONAL motion features (owner card 2026-10-04: build both, prove both), one roof toggle each side
    so a single pass covers on / off / roofed / fallback for both. All state reads, never pixels.
      B7b shader sway: swayMode=Shader prints the lifted tails ONCE with the CutoutPlant strand -- shader name ==
        ShaderDatabase.CutoutPlant, the material is in WindManager.plantMaterials (reflection), _SwayHead advances
        over 30 ticks, open vertex alpha max > 0, the CPU route draws nothing (no double draw); roofing the WALL2
        terminal makes its alpha 0; back to CPU, the CPU route draws again (the fallback/default path).
      B7c floor ripple: default OFF draws nothing; ON, the unroofed plain floor strands ripple (draws > 0, pose hash
        changes over 30 ticks, the static layer leaves exactly those out); the roof over RUN2 takes them out; OFF
        again draws nothing."""
    roof = (X0 + 23, Z0 + 7, 5, 5)                      # over the WALL2 terminal and the east end of RUN2
    B.probe("set:swayMode=Shader")
    s1 = motion(B, 3)
    B.ticks(30)
    s2 = motion(B)
    B.call("jawa/set_roof_batch", ops="RoofConstructed:%d,%d,%d,%d" % roof)
    B.ticks(2)
    s3 = motion(B, 3)
    B.call("jawa/set_roof_batch", ops="None:%d,%d,%d,%d" % roof)
    B.ticks(2)
    B.probe("set:swayMode=CPU")
    s4 = motion(B, 3)
    head1, head2 = s1.get("plantSwayHead"), s2.get("plantSwayHead")
    wind = s1.get("windSpeed") or 0
    sh_ok = (s1.get("swayMode") == "Shader" and s1.get("plantShader") and s1.get("plantShader") == s1.get("cutoutPlantShader") and
             s1.get("plantRegistered") is True and s1.get("shaderSubMeshes", 0) > 0 and s1.get("shaderLiftedOpen", 0) > 0 and
             s1.get("shaderAlphaMaxOpen", 0) > 0 and s1.get("shaderAlphaMaxRoofed", 0) == 0 and s1.get("swayDraws") == 0 and
             isinstance(head1, (int, float)) and isinstance(head2, (int, float)) and (head2 > head1 or wind < 0.01) and
             s3.get("shaderLiftedRoofed", 0) > 0 and s3.get("shaderAlphaMaxRoofed") == 0 and
             s4.get("swayMode") == "CPU" and s4.get("shaderSubMeshes") == 0 and s4.get("swayDraws", 0) > 0)
    keys = ("swayMode", "swayModeReason", "plantShader", "cutoutPlantShader", "plantRegistered", "plantSwayHead", "shaderSubMeshes",
            "shaderVerts", "shaderLiftedOpen", "shaderLiftedRoofed", "shaderAlphaMaxOpen", "shaderAlphaMaxRoofed", "swayDraws", "windSpeed")
    row(rows, "B7b_sway_shader_path", ("PASS" if sh_ok else "FAIL") if cpu.get("plantWindSway") else "UNMEASURED", "MOD",
        {"shader": {k: s1.get(k) for k in keys}, "after30": {k: s2.get(k) for k in ("plantSwayHead", "ticksGame")},
         "roofed": {k: s3.get(k) for k in keys}, "backToCpu": {k: s4.get(k) for k in keys}})
    # ---- B7c floor ripple
    r0 = motion(B)
    B.probe("set:floorRipple=True")
    r1 = motion(B, 3)
    B.ticks(30)
    r2 = motion(B)
    B.call("jawa/set_roof_batch", ops="RoofConstructed:%d,%d,%d,%d" % roof)
    B.ticks(2)
    r3 = motion(B, 3)
    B.call("jawa/set_roof_batch", ops="None:%d,%d,%d,%d" % roof)
    B.ticks(2)
    B.probe("set:floorRipple=False")
    r4 = motion(B, 3)
    rp_ok = (r0.get("floorRipple") is False and r0.get("rippleDraws") == 0 and r0.get("rippling") == 0 and r0.get("floorStrandsOpen", 0) > 0 and
             r1.get("rippling") == r1.get("floorStrandsOpen") and r1.get("rippleDraws", 0) > 0 and
             r1.get("rippleSkippedStatic") == r1.get("rippling") and
             (r1.get("rippleHash") != r2.get("rippleHash") or (r1.get("windSpeed") or 0) < 0.01) and
             r3.get("rippling", 0) < r1.get("rippling", 0) and r3.get("rippling") == r3.get("floorStrandsOpen") and
             r4.get("rippleDraws") == 0 and r4.get("rippling") == 0 and r4.get("rippleSkippedStatic") == 0)
    rk = ("floorRipple", "floorStrands", "floorStrandsOpen", "rippling", "rippleDraws", "rippleVerts", "rippleHash", "rippleSkippedStatic", "windSpeed")
    row(rows, "B7c_floor_ripple", ("PASS" if rp_ok else "FAIL") if cpu.get("plantWindSway") else "UNMEASURED", "MOD",
        {"default_off": {k: r0.get(k) for k in rk}, "on": {k: r1.get(k) for k in rk}, "on_30ticks": {k: r2.get(k) for k in rk},
         "roofed": {k: r3.get(k) for k in rk}, "off_again": {k: r4.get(k) for k in rk}})


# ============================================================================ lane C: art styles (live)
STYLES = ["StarWarsJawa", "StarWars", "ExtensionCord", "Cybertek"]


def style_live(B, rows, log, shots_prefix=None):
    """ST rows: every style loads every texture it needs (no null / bad / missing material, fallbacks only to
    the Jawa slots no family has art for), switching re-prints the section meshes with that style's strand,
    the extension-cord colour modes, the settings file round trip, and a clean return to the default."""
    per, st1 = {}, {}
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
        st1[st] = {"ok": bool(ok), "strandTex": sp.get("strandTex"), "fallbacks": sorted(fb), "nulls": sp.get("nulls"),
                   "bad": sp.get("bad"), "missing": sp.get("missing"), "layerVerts": c.get("layerVerts")}
        if shots_prefix:
            shots_prefix(st)
    # ST1 x4 -> ONE row (consolidation doc section 2 "Core": "ST1 x4 (each look's textures load) -> 1 consolidated
    # row"); the detail names every look and the failing one(s), so no detection is lost.
    row(rows, "ST1_styles_textures_load", "PASS" if all(v["ok"] for v in st1.values()) else "FAIL", "MOD",
        {"failing": [k for k, v in st1.items() if not v["ok"]], "perStyle": st1})
    strand_sets = {st: tuple(per[st].get("strandTex") or []) for st in STYLES}
    distinct = len(set(strand_sets.values())) == len(STYLES)
    printed_ok = {st: any(t in (per[st].get("printedTex") or {}) for t in strand_sets[st]) and
                  not any(t in (per[st].get("printedTex") or {}) for o in STYLES if o != st for t in strand_sets[o] if t not in strand_sets[st])
                  for st in STYLES}
    plug_ids = {st: ((per[st].get("slots") or {}).get("Plug") or {}).get("id") for st in STYLES}
    # owner review 2026-10-04 B12: the Modern (ExtensionCord) look's overhead lines stay BLACK while its floor cords are
    # multi-coloured, so its span cable is the black rubber strand, not its first floor strand
    span_want = {st: ("Strand_BlackRubber" if st == "ExtensionCord" else (strand_sets[st][0] if strand_sets[st] else None)) for st in STYLES}
    span_ok = {st: per[st].get("aerialSpanTex") == span_want[st] for st in STYLES}
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
    hits = [blob[max(0, i - 120):i + 80].decode("utf-8", "replace") for i in _find_all(blob, b"GimmeSomeSlack")]
    res["save_mentions"] = hits
    # Run 2026-10-02: the save held <li Class="RimMandrake.GimmeSomeSlack.RM_MapComponent_CordGraph" />, which made a
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


# ============================================================================ modcheck suite
suite = Suite("GimmeSomeSlack")
suite.toggles = list(SHIPPED)          # every Mod Settings field; floor.uncovered() names the ones no row flips

# rows whose check flips a Mod Settings field (the component's `toggle`)
ROW_TOGGLES = {"M7_off_restores_vanilla": "enabled", "M7b_on_again_invisible": "enabled",
               "B3_whip_live_ends": "whip", "B7_sway_cpu_two_frame": "sway", "B7b_sway_shader_path": "swayMode", "B7c_floor_ripple": "floorRipple", "M10_tangle_threshold_setting": "tangleMin",
               "ST2_switch_changes_textures": "style", "ST3_extcord_colour_modes": "extCordColorMode"}
ROW_TOGGLES["ST1_styles_textures_load"] = "style"
NOT_MEASURED = ("UNMEASURED", "UNBUILT", "UNCOVERED")

# North star (DRAFT, agent-seeded 2026-10-05; design/validation_walks/RimMandrake/GimmeSomeSlack.md `## north star`):
# which must-show / cannot-show ids each row is evidence for (`shows=`, north_star_validation_spec.md section 2).
# Every id named here is a row that already exists; no check was added or relaxed to claim a bar. Binds nothing
# in the floor until the owner validates the section (a DRAFT bar is empty by design).
ROW_SHOWS = {
    # offline tier (this suite's offline chain)
    "O3_core_selftest": ["hose_joiner_reads_brass_screwed_together", "reel_hose_leaves_brass_outlet_nozzle"],
    "O5_style_art_sane": ["four_styles_distinguishable"],
    "O6_review_round1": ["hose_joiner_reads_brass_screwed_together"],
    # core (validation.live_battery: this suite's live chain, and proof_all's core block)
    "M1_conduit_transparent": ["conduit_reads_invisible"],
    "M7b_on_again_invisible": ["conduit_reads_invisible"],
    "B1_rope_settle": ["cord_lies_slack_in_loops", "never_taut_straight_cord"],
    "M1c_end_pieces": ["cord_meets_wall_at_its_face"],
    "M2b_no_vertex_unwalkable": ["never_cord_across_impassable"],
    "B6_tangle_lit_strips": ["dense_grid_reads_as_tangle"],
    "M8_break_two_ends_live_dead": ["break_live_and_dead_ends_differ"],
    "B6b_strips_dark_when_dead": ["break_live_and_dead_ends_differ"],
    "B4_downed_wire_bursts": ["break_live_and_dead_ends_differ"],
    "ST1_styles_textures_load": ["four_styles_distinguishable"],
    "ST2_switch_changes_textures": ["four_styles_distinguishable"],
    # rows only proof_all.py produces (matrix, aerial, hose, relay, carry, style, style-hose blocks)
    "MX_F00_T0_S0": ["cord_lies_slack_in_loops", "never_taut_straight_cord"],
    "MX_F21_T5_S1": ["cord_lies_slack_in_loops"],
    "MX_D15_n1000_S3": ["dense_grid_reads_as_tangle"],
    "R1_span_altitude_above_pawns_below_blueprints": ["overhead_span_above_everything"],
    "R2_spans_and_heads_drawn": ["overhead_span_above_everything"],
    "RL9_overhead_drawn_over_hose": ["overhead_span_above_everything"],
    "M14b_dead_pole_drops_live_and_dead_cords": ["downed_span_lies_on_ground"],
    "M15_explosion_cuts_span": ["downed_span_lies_on_ground"],
    "MX_A04_N3_R12_fallen": ["downed_span_lies_on_ground"],
    "H2_hose_laid_as_hose_cord": ["hose_thicker_stiffer_than_cord"],
    "MX_H01_Flat_corner_L14": ["hose_thicker_stiffer_than_cord"],
    "H9_stiffness_setting": ["hose_thicker_stiffer_than_cord"],
    "MX_H00_Flat_straight_L6": ["hose_plump_when_flowing_flat_when_not"],
    "MX_H03_Plump_straight_L14": ["hose_plump_when_flowing_flat_when_not"],
    "H6_plump_within_transition": ["hose_plump_when_flowing_flat_when_not"],
    "H8_collapse_after_release": ["hose_plump_when_flowing_flat_when_not"],
    "MX_H04_Plump_corner_L24": ["hose_joiner_reads_brass_screwed_together"],
    "MX_H02_Flat_water_L24": ["never_cord_across_impassable"],
    "R3_laid_out_per_look": ["reel_laid_and_wound_look_differ", "reel_hose_leaves_brass_outlet_nozzle"],
    "R5_reeled_in_per_look": ["reel_laid_and_wound_look_differ"],
    "CR6_retract_stored": ["reel_laid_and_wound_look_differ"],
    "RL3_hose_onto_relay_B": ["relay_chain_reads_connected"],
    "RL4_relay_B_onward_to_C": ["relay_chain_reads_connected"],
    "RL8_chain_beyond_one_hose": ["relay_chain_reads_connected"],
    "R2_built_reels_stored_art": ["four_styles_distinguishable"],
    "S6_spans_in_pole_look": ["four_styles_distinguishable"],
    "S9a_two_runs_two_styles": ["one_run_one_style"],
    "S9b_bridge_largest_wins": ["one_run_one_style"],
    "S9c_split_keeps_styles": ["one_run_one_style"],
    "S9d_restyle_and_materials": ["one_run_one_style"],
    "CR7_no_instant_gizmos_without_devmode": ["reel_offers_choose_style"],   # records the reel's gizmo labels; asserts no label
}
# The declared bar nothing can prove yet: a hose plumps only from a powered pump. FlowWorks ships no pump
# (walk E4), so the row is UNBUILT by design and the bar stays claimed, failing, until the pump exists.
PUMP_ROW = {"id": "NS_hose_plumps_only_from_powered_pump", "status": "UNBUILT", "class": "MOD",
            "detail": "UNBUILT: no FlowWorks pump (RM_PumpPortable) to drive a hose; the reel's flow is a DEV gizmo today"}
ROW_SHOWS[PUMP_ROW["id"]] = ["hose_plumps_only_from_powered_pump"]
CORE_SHOW_IDS = ["M1_conduit_transparent", "M7b_on_again_invisible", "B1_rope_settle", "M1c_end_pieces",
                 "M2b_no_vertex_unwalkable", "B6_tangle_lit_strips", "M8_break_two_ends_live_dead",
                 "B6b_strips_dark_when_dead", "B4_downed_wire_bursts", "ST1_styles_textures_load",
                 "ST2_switch_changes_textures"]
OFFLINE_SHOW_IDS = ["O3_core_selftest", "O5_style_art_sane", "O6_review_round1"]
PROOF_ALL_SHOW_IDS = [r for r in ROW_SHOWS if r not in CORE_SHOW_IDS and r not in OFFLINE_SHOW_IDS
                      and r != PUMP_ROW["id"]]
MIRROR_POSIX = "/mnt/d/Luke/dev/RimMandrake"       # read-only origin/main mirror: the offline tier writes exports


def _report_rows(t, rows, declare=()):
    """One component per standalone row, same id. FAIL raises (-> FAIL + finding); UNMEASURED/UNBUILT/UNCOVERED
    record UNMEASURED with the status in the detail. The rows are already-measured, independent results, so a
    FAIL row does not blank the rows after it (it would under the chain's upstream rule, which exists for
    components that still drive the game). Under the declaration probe (no game) `declare` lists the ids to
    declare, so toggle coverage is answerable offline."""
    if not t._guard() and not rows:
        for rid in declare:
            with t.component(rid, toggle=ROW_TOGGLES.get(rid), shows=ROW_SHOWS.get(rid)):
                pass
        return
    for r in rows:
        st = r["status"]
        with t.component(r["id"], toggle=ROW_TOGGLES.get(r["id"]), shows=ROW_SHOWS.get(r["id"])):
            if t._guard() and st == "FAIL":
                raise ExpectationFailed("[%s] %s" % (r.get("class"), str(r.get("detail"))[:600]))
        c = t.components[-1]
        c.evidence.append({"call": "row %s" % r["id"], "result": r})
        if c.verdict == "FAIL":
            t.upstream_failed = False        # this row only; it touched nothing
        elif c.verdict == "PASS":
            if st in NOT_MEASURED or st not in ("PASS", "FAIL"):
                c.verdict, c.detail = "UNMEASURED", "%s: %s" % (st, str(r.get("detail"))[:400])
            else:
                c.detail = str(r.get("detail"))[:400]


def _posix(p):
    import re
    m = re.match(r"^\\\\wsl(?:\.localhost|\$)\\[^\\]+\\(.*)$", p)
    if m:
        return "/" + m.group(1).replace("\\", "/")
    m = re.match(r"^([A-Za-z]):[\\/](.*)$", p)
    if m:
        return "/mnt/%s/%s" % (m.group(1).lower(), m.group(2).replace("\\", "/"))
    return p


def offline_rows():
    """run_offline()'s rows. Under python.exe (the bridge side: no numpy, no WSL selftest toolchain) the same
    function runs in WSL python3 through `--rows-json -`."""
    if os.name != "nt":
        return run_offline()
    me = _posix(os.path.abspath(__file__))
    if me.startswith(MIRROR_POSIX):
        rows = []
        row(rows, "O0_offline_tier_reachable", "UNMEASURED", "HARNESS",
            "validation.py was loaded from the read-only mirror (%s); the offline tier re-exports into its own tree, "
            "so it runs only from a seat clone" % me)
        return rows
    r = subprocess.run(["wsl.exe", "python3", me, "--rows-json", "-"], capture_output=True, text=True, timeout=3600)
    for ln in reversed(r.stdout.splitlines()):
        if ln.startswith("ROWS_JSON "):
            return json.loads(ln[len("ROWS_JSON "):])
    raise ExpectationFailed("offline tier in WSL printed no ROWS_JSON (exit %s): %s"
                            % (r.returncode, (r.stdout + r.stderr).strip()[-400:]))


OFFLINE_IDS = ["O1_mod_files", "O2_settings_defaults", "O5_style_art_sane", "O6_review_round1", "O3_core_selftest",
               "O3n_selftest_can_fail", "O4_python_oracle"]


@suite.chain("offline_O1_O5")
def offline_O1_O5(t):
    """O1 files/csproj/DLL/textures, O2 shipped defaults, O5 style art sanity (+ planted negatives), O3 the C#
    core SelfTest against the Python oracle (+ --probe must turn red), O4 the oracle's own selftest. 0 ticks."""
    rows = []
    with t.component("offline_tier_ran"):
        if t._guard():
            rows = offline_rows()
    if t.components and t.components[-1].verdict == "PASS":
        _report_rows(t, rows, declare=OFFLINE_IDS)


@suite.chain("live_battery")
def live_battery_chain(t):
    """validation.py --live on the runner's map: scene built around the anchor, M1-M3, M5-M8, D1, phase-1b lane A
    (B1-B9, M10), lane C styles (ST1-ST5), log budget."""
    rows = []
    built = False
    try:
        with t.component("live_battery_ran"):
            if t._guard():
                info = t.session.call("jawa/map_info") or {}
                if isinstance(info, dict) and info.get("content"):
                    info = json.loads(info["content"][0]["text"])
                ox, oz = origin_for_anchor(t.anchor, int(info.get("sizeX", 250)), int(info.get("sizeZ", info.get("sizeX", 250))))
                _set_origin(ox, oz)
                built = True
                res = live_battery(SuiteBridge(t), fresh_map=False, rows=rows)
                if res.get("aborted"):
                    raise ExpectationFailed("live tier aborted: %s" % res["aborted"])
        ran = t.components[-1] if t.components else None
        if ran is not None and ran.verdict in ("PASS", "FAIL") and ran.surprises is None:
            t.upstream_failed = False        # the rows measured before a crash/abort are still real results
            _report_rows(t, rows, declare=sorted(set(ROW_TOGGLES) | set(CORE_SHOW_IDS)))
    finally:
        if built and t.session is not None:
            try:                             # teardown is absolute: the whole scene (SITE holds every build)
                t.session.call("jawa/destroy_batch", rects="%d,%d,%d,%d" % SITE, categories="All")
            except Exception:                # noqa: BLE001 - the runner's own sweep still follows
                pass
            _set_origin(150, 150)


@suite.chain("proof_all_only_rows")
def proof_all_only_rows(t):
    """North-star coverage for rows that only proof_all.py measures (matrix, aerial, hose, relay, carry, style,
    style-hose blocks) plus the declared UNBUILT pump bar. This suite's own chains never measure them, so on a live
    `modcheck run` each records UNMEASURED naming where its measurement lives -- never PASS. 0 ticks."""
    rows = []
    if t._guard():
        rows = [{"id": rid, "status": "UNMEASURED", "class": "HARNESS",
                 "detail": "measured only by proof_all.py --live (block row); record that result with `modcheck record`"}
                for rid in PROOF_ALL_SHOW_IDS] + [dict(PUMP_ROW)]
    _report_rows(t, rows, declare=PROOF_ALL_SHOW_IDS + [PUMP_ROW["id"]])


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
    ap.add_argument("--rows-json", default=None, metavar="-",
                    help="offline tier, then print its rows as one 'ROWS_JSON <json>' line (the suite's WSL hop)")
    a = ap.parse_args(argv)
    if a.rows_json:
        rows = run_offline()
        print("ROWS_JSON " + json.dumps(rows, default=str))
        return 0
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
