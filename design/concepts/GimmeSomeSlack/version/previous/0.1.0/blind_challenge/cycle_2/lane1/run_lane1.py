#!/usr/bin/env python3
"""Run blind lane 1 (Gimme Some Slack 0.1.0, cycle 2): the AerialMath kernel tests and the no-hose scan.
    python3 run_lane1.py [--kernel <AerialMath.cs>] [--mod <mod folder>] [--out <rows.jsonl>]
Stages BlindLane1.cs + the kernel under $GSS_LANE1_STAGE or /mnt/d/ClaudeWork/rimmandrake/scratch/gimmesomeslack_blind_c2_lane1
(dotnet.exe cannot build from a WSL path), builds and runs it with the per-user Windows dotnet, runs blind_no_hose.py on the
mod folder, appends the not_kernel rows (bars whose logic is game-side), writes one JSON row per line and prints the counts.
Exit 0 = no row FAILs."""
import argparse, glob, json, os, shutil, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
MOD = os.path.join(REPO, "src/RimMandrake/GimmeSomeSlack")
KERNEL = os.path.join(MOD, "Source/Aerial/AerialMath.cs")
STAGE = os.environ.get("GSS_LANE1_STAGE", "/mnt/d/ClaudeWork/rimmandrake/scratch/gimmesomeslack_blind_c2_lane1")
CSPROJ = """<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework>
<LangVersion>latest</LangVersion><Nullable>disable</Nullable><ImplicitUsings>disable</ImplicitUsings></PropertyGroup></Project>"""

# Bars whose logic is game-side (Verse, pawns, PowerNet, draw layers): one not_kernel row each group, owed to Stage 6.
NOT_KERNEL = [
    (["conduit_invisible", "invisible_conduit"], "the conduit's own graphic and the power overlay are game-side draws"),
    (["cords_lie_slack", "cord_slack_lay", "no_unforced_sharp_turn", "cords_meet_walls_at_face", "dense_block_tangle",
      "cords_never_repeat", "cord_shape_variation_probe", "drawing_true_to_grid", "connectivity_truth", "cords_draw_under_things"],
     "the floor-cord lay lives in Core/CordBuilder + CordSlacken + _Shared/SlackGeometry, not in a *Math/*Kernel file the brief "
     "opens for lane 1; its shape and truth-to-grid bars are drawings of the live map"),
    (["strip_at_every_junction", "junction_strips"], "junction posing is CordBuilder (game-side drawing)"),
    (["cut_live_and_dead_ends", "break_ends_live_dead"], "which end still reaches power is a PowerNet read"),
    (["floor_end_shocks_crossers", "floor_end_shock", "shock_reach_setting"],
     "the floor-end contact set, the constructor exemption keyed on the joining blueprint and the three-way reach are in "
     "RM_FallenWireShock / FloorEndShock / ShockRule (game-side); AerialSettings.SyncDerived makes fallenWireShock = reach != None"),
    (["live_wire_lights_fuel"], "fire on a filth cell is live state"),
    (["no_stall_on_rewire", "rebuild_cost"], "milliseconds per frame on a 2000-cell base is a live measurement"),
    (["wire_down_alert"], "the alert and its jump are UI"),
    (["four_looks_one_run", "four_styles"], "telling four looks apart by eye is a capture judged"),
    (["settings_switch_cleanly", "mod_settings"], "master off restoring vanilla art without a restart is a live read (the pipe-pole switch rule is tested above)"),
    (["owner_change_coils_wires", "owner_change_cut"], "a faction claim is live"),
    (["statics_clear_between_games", "game_statics_reset"], "new game / load in one session is live"),
    (["uninstall_clean"], "removing the mod from a save is live"),
    (["walk_scavenger_base"], "a week of play on the full list"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kernel", default=KERNEL); ap.add_argument("--mod", default=MOD)
    ap.add_argument("--out", default=os.path.join(HERE, "lane1_rows.jsonl"))
    a = ap.parse_args()
    os.makedirs(STAGE, exist_ok=True)
    for f in glob.glob(os.path.join(STAGE, "*.cs")): os.remove(f)
    shutil.copy(os.path.join(HERE, "BlindLane1.cs"), STAGE); shutil.copy(a.kernel, os.path.join(STAGE, "AerialMath.cs"))
    open(os.path.join(STAGE, "BlindLane1.csproj"), "w").write(CSPROJ)
    # AerialMath reads two wall-face constants from Core/WallMount.cs (which needs the Verse-side Shared.Slack): stub just
    # those two, their values read from the shipped file (BracketInset is not among the tested properties)
    wm = open(os.path.join(a.mod, "Source/Core/WallMount.cs")).read()
    import re
    sb = re.search(r"const double SouthBand = ([\d.]+);", wm).group(1); sv = re.search(r"const double SideBevel = ([\d.]+);", wm).group(1)
    open(os.path.join(STAGE, "BlindStubs.cs"), "w").write(
        "namespace RimMandrake.GimmeSomeSlack.Core { public static class WallMount { public const double SouthBand = %s; public const double SideBevel = %s; } }" % (sb, sv))
    dn = sorted(glob.glob("/mnt/c/Users/*/.dotnet/dotnet.exe"))[0]
    win = subprocess.run(["wslpath", "-w", STAGE], capture_output=True, text=True, check=True).stdout.strip()
    b = subprocess.run([dn, "build", win + "\\BlindLane1.csproj", "-c", "Release", "--nologo", "-v", "q"], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=400)
    rows = []
    if b.returncode:
        rows.append({"id": "L1_KERNEL_BUILD", "bars": [], "kind": "info", "verdict": "FAIL", "cases": 0,
                     "detail": "the kernel did not compile: " + (b.stdout[-1500:] + b.stderr[-500:]).replace("\n", " ")})
    else:
        r = subprocess.run([dn, win + "\\bin\\Release\\net8.0\\BlindLane1.dll"], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=400)
        got = [json.loads(l) for l in r.stdout.splitlines() if l.startswith("{")]
        if r.returncode not in (0, 1) or not got:
            got.append({"id": "L1_KERNEL_RUN", "bars": [], "kind": "info", "verdict": "FAIL", "cases": 0,
                        "detail": "kernel run crashed rc %s: %s" % (r.returncode, r.stderr[-1500:].replace("\n", " "))})
        rows += got
    h = subprocess.run([sys.executable, os.path.join(HERE, "blind_no_hose.py"), "--mod", a.mod], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=400)
    rows += [json.loads(l) for l in h.stdout.splitlines() if l.startswith("{")]
    for bars, why in NOT_KERNEL:
        rows.append({"id": "L1_NOT_KERNEL_" + bars[0].upper(), "bars": bars, "kind": "not_kernel", "verdict": "UNSETTLED", "cases": 0,
                     "detail": "game-side, owed to Stage 6: " + why})
    with open(a.out, "w") as f:
        for row in rows: f.write(json.dumps(row) + "\n")
    c = {}
    for row in rows: c[row["verdict"]] = c.get(row["verdict"], 0) + 1
    print("LANE1", json.dumps(c), "rows", len(rows), "->", a.out)
    for row in rows:
        if row["verdict"] == "FAIL": print("FAIL", row["id"], row["detail"][:400])
    sys.exit(1 if c.get("FAIL") else 0)


main()
