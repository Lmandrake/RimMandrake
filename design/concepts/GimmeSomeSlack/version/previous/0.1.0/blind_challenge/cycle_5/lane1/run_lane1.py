#!/usr/bin/env python3
"""Run blind lane 1 (GimmeSomeSlack 0.1.0, cycle 5).
    python3 run_lane1.py [--kernel <AerialMath.cs>] [--mod <GSS folder>] [--out <rows.jsonl>]
Part A: blind_nohose.py over the mod folder (the two offline bars).
Part B: BlindLane1.cs + the kernel, staged under <agent storage>/scratch/gimmesomeslack_blind_c5_lane1 (dotnet.exe cannot
build from a WSL path), built and run with the Windows dotnet.
Part C: one not_kernel row per stage-6 bar whose logic is game-side.
Exit 0 = no FAIL row."""
import argparse, glob, json, os, re, shutil, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
MOD = os.path.join(REPO, "src/RimMandrake/GimmeSomeSlack")
KERNEL = os.path.join(MOD, "Source/Aerial/AerialMath.cs")
CSPROJ = """<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework>
<LangVersion>latest</LangVersion><Nullable>disable</Nullable><ImplicitUsings>disable</ImplicitUsings></PropertyGroup></Project>"""
# bars whose logic lives in game-side code (pawn jobs, PowerNets, map meshes, CordBuilder over a map, Harmony, saves)
NOT_KERNEL = [
    ("conduit_invisible", "conduit hiding is a Harmony/graphic swap on live Things"),
    ("invisible_conduit", "as conduit_invisible"),
    ("cords_lie_slack", "cord lay is CordBuilder over a map snapshot, not AerialMath"),
    ("cord_slack_lay", "as cords_lie_slack"),
    ("no_unforced_sharp_turn", "cord bends are CordBuilder/CordShapeAudit, not the kernel named for lane 1"),
    ("cords_meet_walls_at_face", "floor cords meet walls in CordBuilder; fallen wires are tested in L1_FALLEN_ON_GROUND_NOT_IN_WALLS"),
    ("strip_at_every_junction", "junction art is chosen from the live conduit graph"),
    ("junction_strips", "as strip_at_every_junction"),
    ("dense_block_tangle", "a look judgement over a live map"),
    ("cord_shape_variation_probe", "an instrument over drawn cords"),
    ("cords_never_repeat", "pairwise cord shapes from CordBuilder"),
    ("drawing_true_to_grid", "PowerNet membership against drawn cords: live game"),
    ("connectivity_truth", "as drawing_true_to_grid (the kernel's watchdog rule is in L1_WATCHDOG_REPAIRS_SPLIT_UP_SPANS)"),
    ("cut_live_and_dead_ends", "live/dead from PowerNet state after a destroyed cell"),
    ("break_ends_live_dead", "as cut_live_and_dead_ends"),
    ("floor_end_shocks_crossers", "pawn jobs and FloorEndShock contacts"),
    ("floor_end_shock", "as floor_end_shocks_crossers"),
    ("fallen_wire_shocks_crossers", "per-wire exemption keyed on the pawn's job target (the kernel's ShockTakes table is L1_SHOCK_TAKES_TABLE)"),
    ("fallen_wire_shock", "as fallen_wire_shocks_crossers"),
    ("shock_reach_setting", "ShockReach is applied by game-side callers (RM_FallenWireShock, FloorEndShock), not AerialMath"),
    ("live_wire_lights_fuel", "fire on a filth cell: live game"),
    ("wire_down_alert", "an Alert over live anchors"),
    ("restring_cut_span", "the job driver and alert are game-side (job length is L1_RESTRING_TICKS_SWEEP)"),
    ("restring_job", "as restring_cut_span"),
    ("four_looks_one_run", "style picking over live conduit runs"),
    ("four_styles", "as four_looks_one_run"),
    ("settings_switch_cleanly", "each switch's observable change is game-side (the pipe/power split is L1_PIPE_POLE_SWITCH_ITS_OWN)"),
    ("mod_settings", "the settings window and its saved values (the span slider's reach is L1_SPAN_RANGE_SLIDER_INSIDE_CLAMP)"),
    ("gravship_keeps_connections", "gravship lift and landing (the kernel's keep/ground split is L1_REMOVAL_CONSERVES_SPANS)"),
    ("gravship_connectivity", "as gravship_keeps_connections"),
    ("owner_change_coils_wires", "the owner sweep runs over live factions"),
    ("owner_change_cut", "as owner_change_coils_wires"),
    ("statics_clear_between_games", "static reset on new game/load: game-side"),
    ("game_statics_reset", "as statics_clear_between_games"),
    ("no_stall_on_rewire", "frame time of the rebuild"),
    ("rebuild_cost", "as no_stall_on_rewire"),
    ("uninstall_clean", "removing the mod from a save"),
    ("cords_draw_under_things", "draw order against items and buildings: altitude layers in game"),
    ("walk_scavenger_base", "the human walk, stage 8"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kernel", default=KERNEL); ap.add_argument("--mod", default=MOD)
    ap.add_argument("--out", default=os.path.join(HERE, "lane1_rows.jsonl"))
    a = ap.parse_args()
    rows = []
    r = subprocess.run([sys.executable, os.path.join(HERE, "blind_nohose.py"), "--mod", a.mod], capture_output=True, text=True)
    rows += [json.loads(l) for l in r.stdout.splitlines() if l.startswith("{")]
    if not rows:
        sys.exit("NOHOSE SCAN FAILED\n" + r.stderr[-2000:])

    root = subprocess.run(["python3", os.path.expanduser("~/dev/Lodestar/bin/lib/agent_storage.py")], capture_output=True, text=True, check=True).stdout.strip()
    stage = os.environ.get("LANE1_STAGE") or os.path.join(root, "rimmandrake", "scratch", "gimmesomeslack_blind_c5_lane1")
    os.makedirs(stage, exist_ok=True)
    for f in glob.glob(os.path.join(stage, "*.cs")):
        os.remove(f)
    shutil.copy(os.path.join(HERE, "BlindLane1.cs"), stage); shutil.copy(a.kernel, os.path.join(stage, "AerialMath.cs"))
    # AerialMath reads two WallMount constants; WallMount itself needs the shared slack library, so stub just those two
    wm = open(os.path.join(a.mod, "Source/Core/WallMount.cs")).read()
    consts = "".join("        public const double %s = %s;\n" % (n, re.search(r"const double %s = ([\d.]+);" % n, wm).group(1)) for n in ("SouthBand", "SideBevel"))
    open(os.path.join(stage, "WallMountStub.cs"), "w").write("namespace RimMandrake.GimmeSomeSlack.Core {\n    public static class WallMount {\n" + consts + "    }\n}\n")
    open(os.path.join(stage, "BlindLane1.csproj"), "w").write(CSPROJ)
    dn = sorted(glob.glob("/mnt/c/Users/*/.dotnet/dotnet.exe"))[0]   # the per-user SDK; Program Files holds a runtime only
    win = subprocess.run(["wslpath", "-w", stage], capture_output=True, text=True, check=True).stdout.strip()
    b = subprocess.run([dn, "build", win + "\\BlindLane1.csproj", "-c", "Release", "--nologo", "-v", "q"], capture_output=True, text=True, timeout=400)
    if b.returncode:
        sys.exit("BUILD FAILED\n" + b.stdout[-3000:] + b.stderr[-2000:])
    k = subprocess.run([dn, win + "\\bin\\Release\\net8.0\\BlindLane1.dll"], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=400)
    krows = [json.loads(l) for l in k.stdout.splitlines() if l.startswith("{")]
    if k.returncode not in (0, 1) or not krows:
        sys.exit("KERNEL RUN FAILED rc %s\n%s" % (k.returncode, k.stderr[-2000:]))
    rows += krows
    for bar, why in NOT_KERNEL:
        rows.append({"id": "NK_" + bar.upper(), "bars": [bar], "kind": "not_kernel", "verdict": "UNSETTLED", "cases": 0,
                     "detail": "game-side, proves at stage 6 or later: " + why})
    with open(a.out, "w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")
    c = {}
    for row in rows:
        c[row["verdict"]] = c.get(row["verdict"], 0) + 1
    print("LANE1", json.dumps(c), "rows", len(rows), "->", a.out)
    for row in rows:
        if row["verdict"] == "FAIL":
            print("FAIL", row["id"], row["detail"][:300])
    sys.exit(1 if c.get("FAIL") else 0)


main()
