#!/usr/bin/env python3
"""Blind lane 1: blind_no_hose.py (the two offline bars) plus BlindLane1.cs over the Verse-free kernels.
    python3 run_lane1.py [--kernel <AerialMath.cs>] [--src <Source dir>] [--out <rows.jsonl>] [--skip-cs]
Exit 0 = every decided row PASS, 1 = a FAIL row, 2 = could not look (build or run failed)."""
import argparse, glob, json, os, shutil, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
RM = os.path.join(REPO, "src/RimMandrake")
NAME = os.environ.get("GSS_LANE1_STAGE", "gimmesomeslack_blind_c1_lane1")
CSPROJ = """<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework>
<LangVersion>latest</LangVersion><Nullable>disable</Nullable><ImplicitUsings>disable</ImplicitUsings><NoWarn>CS0649;CS0219;CS0168</NoWarn></PropertyGroup></Project>"""
NOT_KERNEL = {  # game-side stage-6 bars: one row, no kernel decides them
 "GAME_SIDE_BARS": ["invisible_conduit","conduit_invisible","uninstall_clean","game_statics_reset","statics_clear_between_games","look_menu_icons","wall_lamp_takes_looks","pole_buttons_show_icons","poles_draw_in_front_when_south","no_roof_over_pole","switch_light_reads_state","switch_off_cords_stay_connected","cords_draw_under_things","live_wire_lights_fuel","wire_down_alert","floor_end_shock","floor_end_shocks_crossers","shock_reach_setting","walk_scavenger_base"],
 "FLOOR_CORD_SHAPE_BARS": ["cord_slack_lay","cords_lie_slack","no_unforced_sharp_turn","junction_strips","strip_at_every_junction","dense_block_tangle","cord_shape_variation_probe","cords_never_repeat","drawing_true_to_grid","cut_live_and_dead_ends","cords_join_stubs_on_position_and_slope"]}
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--kernel"); ap.add_argument("--src", default=os.path.join(RM, "GimmeSomeSlack/Source"))
    ap.add_argument("--out", default=os.path.join(HERE, "lane1_rows.jsonl")); ap.add_argument("--skip-cs", action="store_true"); a = ap.parse_args()
    p = subprocess.run([sys.executable, os.path.join(HERE, "blind_no_hose.py"), "--mod", os.path.dirname(a.src)], capture_output=True, text=True)
    rows = [json.loads(l) for l in p.stdout.splitlines() if l.startswith("{")]
    if not rows: print("UNMEASURED: blind_no_hose.py\n" + p.stderr[-1500:]); sys.exit(2)
    if not a.skip_cs:
        root = "/mnt/d/ClaudeWork/rimmandrake"  # dotnet.exe cannot build from a WSL path
        stage = os.path.join(root, "scratch", NAME); os.makedirs(stage, exist_ok=True)
        for f in glob.glob(os.path.join(stage, "*.cs")): os.remove(f)
        shutil.copy(os.path.join(HERE, "BlindLane1.cs"), stage); shutil.copy(a.kernel or os.path.join(a.src, "Aerial/AerialMath.cs"), os.path.join(stage, "AerialMath.cs"))
        for f in glob.glob(os.path.join(a.src, "Core/*.cs")): shutil.copy(f, stage)
        for f in glob.glob(os.path.join(RM, "_Shared/SlackGeometry/*.cs")): shutil.copy(f, stage)
        open(os.path.join(stage, "BlindLane1.csproj"), "w").write(CSPROJ)
        dn = sorted(glob.glob("/mnt/c/Users/*/.dotnet/dotnet.exe"))[0]
        win = subprocess.run(["wslpath", "-w", stage], capture_output=True, text=True, check=True).stdout.strip()
        b = subprocess.run([dn, "build", win + "\\BlindLane1.csproj", "-c", "Release", "--nologo", "-v", "q"], capture_output=True, text=True)
        if b.returncode: print("UNMEASURED: BUILD FAILED\n" + b.stdout[-3000:]); sys.exit(2)
        r = subprocess.run([dn, win + "\\bin\\Release\\net8.0\\BlindLane1.dll"], capture_output=True, text=True)
        cs = [json.loads(l) for l in r.stdout.splitlines() if l.startswith("{")]
        if r.returncode not in (0, 1) or not cs: print("UNMEASURED: RUN FAILED rc %s\n%s" % (r.returncode, r.stderr[-2000:])); sys.exit(2)
        rows += cs
    for k, bars in NOT_KERNEL.items():
        rows.append({"id": k, "bars": bars, "kind": "not_kernel", "verdict": "UNSETTLED", "cases": 0, "detail": "decided on the game side (defs, map components, drawing, jobs) or by the floor-cord builder's drawn result on a map; undecided here: each bar's scene; settled by its stage-6 scene in scenes.json run in a live game"})
    with open(a.out, "w") as f:
        for row in rows: f.write(json.dumps(row) + "\n")
    c = {}
    for row in rows: c[row["verdict"]] = c.get(row["verdict"], 0) + 1
    print("LANE1", json.dumps(c), "rows", len(rows), "->", a.out)
    for row in rows:
        if row["verdict"] == "FAIL": print("FAIL", row["id"], row["detail"][:400])
    sys.exit(1 if c.get("FAIL") else 0)
main()
