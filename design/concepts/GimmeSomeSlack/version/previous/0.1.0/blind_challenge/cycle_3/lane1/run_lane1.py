#!/usr/bin/env python3
"""Run blind lane 1 (Gimme Some Slack 0.1.0, cycle 3).
    python3 run_lane1.py [--kernel <AerialMath.cs>] [--root <mod dir>] [--dll <shipped dll>] [--out <rows.jsonl>]
1. BlindLane1.cs + the kernel, staged under <agent storage>/scratch/gimmesomeslack_blind_c3_lane1 (dotnet.exe cannot build
   from a WSL path), built and run with the per-user Windows dotnet: the AerialMath rows.
2. The same binary reads the shipped DLL's metadata (type names, user strings); BlindNoHose.py scans the mod tree and
   those dumps: the rows of the two offline bars.
3. A sanity probe: the scan run on a throwaway copy with a hose reel planted (def, texture folder, class) must FAIL, or
   the scanner is blind and its PASS rows mean nothing.
4. One not_kernel row per remaining bar whose logic is game-side (UNSETTLED, owed to Stage 6).
Exit 0 = every decided row PASS."""
import argparse, glob, json, os, re, shutil, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
MOD = os.path.join(REPO, "src/RimMandrake/GimmeSomeSlack")
CSPROJ = """<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework>
<LangVersion>latest</LangVersion><Nullable>disable</Nullable><ImplicitUsings>disable</ImplicitUsings></PropertyGroup></Project>"""
# AerialMath.BracketInset reads two WallMount constants (Core/WallMount.cs pulls in RimMandrake.Shared); no lane-1 row
# tests the bracket inset, so a stub with placeholder values keeps the kernel compiling without them.
STUB = """namespace RimMandrake.GimmeSomeSlack.Core { public static class WallMount { public const double SouthBand = 0.3, SideBevel = 0.18; } }"""
BARS_DONE_ELSEWHERE = None  # filled from the rows
LEAF_REASON = {
    "conduit_invisible": "conduit graphic alpha and per-edge cord meshes: ConduitVisuals / SectionLayer_RM_MessyCords (game side), no *Math kernel",
    "cords_lie_slack": "cord length/chord and excursions: CordBuilder/CordShape (Core, not a *Math or *Kernel file), read live by sc_cords_slack",
    "no_unforced_sharp_turn": "bend tally CordShapeAudit.Bends over live strands: game-side geometry, not the aerial kernel",
    "cords_meet_walls_at_face": "wall-face stubs and dives: CordBuilder routing over the live map",
    "strip_at_every_junction": "junction pieces per look: CordBuilder.PoseJunction + art, live capture",
    "dense_block_tangle": "tangle pieces and a judge's read of a capture",
    "cord_shape_variation_probe": "a bridge read of sampled curves (instrument)",
    "cords_never_repeat": "pairwise shape distance from the live probe plus a judge",
    "drawing_true_to_grid": "cord ends against live PowerNets: game side",
    "cut_live_and_dead_ends": "live/dead end flags from PowerNet state after a cut: game side",
    "floor_end_shocks_crossers": "FloorEndShock contacts and the constructor exemption: game side",
    "no_stall_on_rewire": "SliceWindow ms per frame on his machine: live_minimal",
    "spans_above_everything": "draw altitude above pawns/buildings and the lamp lit: game side (the link and sag halves are kernel rows)",
    "live_wire_lights_fuel": "fire on a puddle cell under a live end: game side",
    "restring_cut_span": "the Wire down alert, its jump and the RM_RestringSpan job: game side",
    "four_looks_one_run": "style per connected run and a judge's read: game side",
    "settings_switch_cleanly": "master off restoring vanilla art, the Harmony patch-to-switch map: game side (the pipe-pole switch rule is a kernel row)",
    "owner_change_coils_wires": "OwnerMismatchSweep on a faction change: game side",
    "statics_clear_between_games": "statics across new/loaded games in one session: game side",
    "shock_reach_setting": "None / Only downed lines / All decided per contact kind in the shock comps: game side",
    "walk_scavenger_base": "the week-long walk on his full list",
    "gravship_keeps_connections": "the landed ship's true-to-grid read (the removal-plan half is a kernel row): live_minimal",
    "fallen_span_on_ground": "ground draw layer and live/dead ends per net (the lay geometry is a kernel row)",
    "fallen_wire_shocks_crossers": "contacts and the targeted exemption (the ShockTakes table is a kernel row)",
    "tap_steals_and_costs_goodwill": "net wiring and faction choice (the theft maths are kernel rows)",
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kernel", default=os.path.join(MOD, "Source/Aerial/AerialMath.cs"))
    ap.add_argument("--root", default=MOD)
    ap.add_argument("--dll", default=None)
    ap.add_argument("--out", default=os.path.join(HERE, "lane1_rows.jsonl"))
    a = ap.parse_args()
    dll = a.dll or os.path.join(a.root, "Assemblies/RimMandrakeGimmeSomeSlack.dll")
    root = subprocess.run(["python3", os.path.expanduser("~/dev/Lodestar/bin/lib/agent_storage.py")], capture_output=True, text=True, check=True).stdout.strip()
    stage = os.path.join(root, "scratch", "gimmesomeslack_blind_c3_lane1")
    os.makedirs(stage, exist_ok=True)
    for f in glob.glob(os.path.join(stage, "*.cs")) + glob.glob(os.path.join(stage, "*.txt")) + glob.glob(os.path.join(stage, "*.dll")): os.remove(f)
    shutil.copy(os.path.join(HERE, "BlindLane1.cs"), stage); shutil.copy(a.kernel, os.path.join(stage, "AerialMath.cs"))
    open(os.path.join(stage, "WallMountStub.cs"), "w").write(STUB)
    open(os.path.join(stage, "BlindLane1.csproj"), "w").write(CSPROJ)
    dn = sorted(glob.glob("/mnt/c/Users/*/.dotnet/dotnet.exe"))[0]
    win = subprocess.run(["wslpath", "-w", stage], capture_output=True, text=True, check=True).stdout.strip()
    b = subprocess.run([dn, "build", win + "\\BlindLane1.csproj", "-c", "Release", "--nologo", "-v", "q"], capture_output=True, text=True, timeout=400)
    if b.returncode: sys.exit("BUILD FAILED\n" + b.stdout[-3000:] + b.stderr[-2000:])
    exe = win + "\\bin\\Release\\net8.0\\BlindLane1.dll"
    r = subprocess.run([dn, exe], capture_output=True, text=True, timeout=400)
    rows = [json.loads(l) for l in r.stdout.splitlines() if l.startswith("{")]
    if r.returncode not in (0, 1) or not rows: sys.exit("RUN FAILED rc %s\n%s" % (r.returncode, r.stderr[-2000:]))

    # the shipped DLL's metadata, then the scan of the offline bars
    shutil.copy(dll, os.path.join(stage, "shipped.dll"))
    d = subprocess.run([dn, exe, "--dll", win + "\\shipped.dll", win + "\\dll_types.txt", win + "\\dll_strings.txt"], capture_output=True, text=True, timeout=200)
    scan = [sys.executable, os.path.join(HERE, "BlindNoHose.py"), "--root", a.root]
    if d.returncode == 0: scan += ["--dll-types", os.path.join(stage, "dll_types.txt"), "--dll-strings", os.path.join(stage, "dll_strings.txt")]
    s = subprocess.run(scan, capture_output=True, text=True, timeout=200)
    rows += [json.loads(l) for l in s.stdout.splitlines() if l.startswith("{")]

    # sanity probe: the scanner must see a planted hose reel in each place it looks
    with tempfile.TemporaryDirectory() as tmp:
        cp = os.path.join(tmp, "mod")
        for sub in ("Defs", "Patches", "Textures", "Source"): shutil.copytree(os.path.join(a.root, sub), os.path.join(cp, sub), ignore=shutil.ignore_patterns("SelfTest"))
        planted = {
            "def": ("Defs/PlantedHoseReel.xml", '<Defs><ThingDef><defName>RM_HoseReel</defName><graphicData><texPath>X/Y</texPath></graphicData></ThingDef></Defs>'),
            "texture_folder": ("Textures/RimMandrake/GimmeSomeSlack/Hoses/a.png", ""),
            "class": ("Source/PlantedReel.cs", "namespace X { class HoseReelDrawer {} }"),
            "pipe_texpath": ("Source/PlantedPipe.cs", 'class Q { string p = "RimMandrake/GimmeSomeSlack/PipeSpan"; }'),
        }
        seen = {}
        for name, (rel, body) in planted.items():
            p = os.path.join(cp, rel); os.makedirs(os.path.dirname(p), exist_ok=True); open(p, "w").write(body)
            pr = subprocess.run([sys.executable, os.path.join(HERE, "BlindNoHose.py"), "--root", cp], capture_output=True, text=True, timeout=200)
            fails = [json.loads(l)["id"] for l in pr.stdout.splitlines() if l.startswith("{") and json.loads(l)["verdict"] == "FAIL"]
            seen[name] = fails
            os.remove(p)
        blind = [k for k, v in seen.items() if not v]
        rows.append({"id": "NH_SCANNER_SEES_PLANTED", "bars": ["no_hose", "no_hose_in_gss"], "kind": "fixed",
                     "verdict": "PASS" if not blind else "FAIL", "cases": len(planted),
                     "detail": ("blind to planted: %s" % blind) if blind else "each planted hose/reel/pipe (def, texture folder, class, pipe texture literal) turns a scan row FAIL: %s" % seen})

    # one not_kernel row per game-side leaf; the kernel rows above cover their kernel halves
    for leaf, why in LEAF_REASON.items():
        rows.append({"id": "NK_" + leaf.upper(), "bars": [leaf], "kind": "not_kernel", "verdict": "UNSETTLED", "cases": 0,
                     "detail": "not decidable from the aerial kernel: " + why + "; owed to Stage 6 (proves_at to be read in lane 2)"})
    with open(a.out, "w") as f:
        for row in rows: f.write(json.dumps(row) + "\n")
    c = {}
    for row in rows: c[row["verdict"]] = c.get(row["verdict"], 0) + 1
    print("LANE1", json.dumps(c), "rows", len(rows), "->", a.out)
    for row in rows:
        if row["verdict"] == "FAIL": print("FAIL", row["id"], row["detail"][:400])
    sys.exit(1 if c.get("FAIL") else 0)
main()
