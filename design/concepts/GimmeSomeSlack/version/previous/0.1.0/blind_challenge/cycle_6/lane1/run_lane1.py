#!/usr/bin/env python3
"""Run blind lane 1 (cycle 6) against the shipped GimmeSomeSlack, or against planted copies.
    python3 run_lane1.py [--kernel <AerialMath.cs>] [--shockrule <ShockRule.cs>] [--mod-root <dir>] [--dll <dll>] [--out <rows.jsonl>]
Two halves: BlindLane1.py (the no-hose scan of the shipped surface, its guards included) and BlindLane1.cs (the kernels,
staged with the kernel files under /mnt/d/ClaudeWork/rimmandrake/scratch/gimmesomeslack_blind_c6_lane1/ because dotnet.exe
cannot build from a WSL path, plus the shipped DLL's metadata). One JSON row per line; prints the verdict counts.
Exit 0 = every decided row PASS."""
import argparse, glob, json, os, shutil, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
MOD = os.path.join(REPO, "src/RimMandrake/GimmeSomeSlack")
STAGE = os.environ.get("GSS_LANE1_STAGE", "/mnt/d/ClaudeWork/rimmandrake/scratch/gimmesomeslack_blind_c6_lane1")
CSPROJ = """<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework>
<LangVersion>latest</LangVersion><Nullable>disable</Nullable><ImplicitUsings>disable</ImplicitUsings></PropertyGroup></Project>"""

NOT_KERNEL = [
    ("conduit_invisible", "vanilla conduit art hidden and the power overlay intact: a render read in game"),
    ("invisible_conduit", "as conduit_invisible"),
    ("cords_lie_slack", "cord shapes are laid by CordBuilder over the live map (not in AerialMath)"),
    ("cord_slack_lay", "as cords_lie_slack"),
    ("no_unforced_sharp_turn", "cord turn angles come from the live lay against walls, buildings and sockets"),
    ("cords_meet_walls_at_face", "floor cords against real walls; the fallen-wire half is K_FALLEN_WIRE_LIES_ON_GROUND"),
    ("strip_at_every_junction", "junction art per look on a live 3/4-way junction"),
    ("junction_strips", "as strip_at_every_junction"),
    ("dense_block_tangle", "an eye judgement of a dense block in game"),
    ("cord_shape_variation_probe", "the shape-distance probe runs on laid cords in game"),
    ("cords_never_repeat", "shape distance across a real room"),
    ("drawing_true_to_grid", "cords vs the live PowerNet graph, pipe ports of real buildings"),
    ("connectivity_truth", "as drawing_true_to_grid; the watchdog half is K_WATCHDOG_CUT_STAYS_SPLIT"),
    ("cut_live_and_dead_ends", "which end reaches a power source is a live PowerNet read"),
    ("break_ends_live_dead", "as cut_live_and_dead_ends"),
    ("floor_end_shocks_crossers", "pawn paths, jobs and hediffs; the rule table is K_SHOCK_REACH_TABLE / K_SHOCK_JOINING_CONDUIT_ONLY"),
    ("floor_end_shock", "as floor_end_shocks_crossers"),
    ("no_stall_on_rewire", "frame time on a 2000-cell base is measured in game"),
    ("rebuild_cost", "as no_stall_on_rewire"),
    ("spans_above_everything", "draw altitude against pawns and buildings in game"),
    ("overhead_spans", "the span mesh in game; link rules are K_LINK_RULES / K_AUTOLINK_*"),
    ("fallen_span_on_ground", "ground layer below pawns, live/dead ends in game; the lay is K_FALLEN_WIRE_LIES_ON_GROUND"),
    ("downed_spans", "as fallen_span_on_ground; the removal plan is K_REMOVAL_PLAN"),
    ("fallen_wire_shocks_crossers", "which wire a re-string job targets (LayTouches over that cut) is a live job read"),
    ("fallen_wire_shock", "as fallen_wire_shocks_crossers"),
    ("shock_reach_setting", "the live setting read without restart and FlowWorks' dropped deck cords; the table is K_SHOCK_REACH_TABLE"),
    ("live_wire_lights_fuel", "fuel ignition under a live end is a game fire read"),
    ("restring_cut_span", "the Wire down alert, the camera jump and the RM_RestringSpan job in game"),
    ("restring_job", "as restring_cut_span; the job time is K_RESTRING_IS_A_JOB"),
    ("wire_down_alert", "the alert lists and clears in game"),
    ("tap_steals_and_costs_goodwill", "power flow between real nets and faction goodwill in game; the arithmetic is K_TAP_* / K_THEFT_*"),
    ("power_theft", "as tap_steals_and_costs_goodwill"),
    ("four_looks_one_run", "four looks told apart by eye, one look per run, in game"),
    ("four_styles", "as four_looks_one_run"),
    ("settings_switch_cleanly", "patch ownership and vanilla art restored without restart; the kind switches are K_SWITCHES_OWN_THEIR_KIND"),
    ("mod_settings", "the settings window in game; ranges are K_RANGE_SAG_SETTINGS_SWEEP"),
    ("pipe_pole_switch", "FlowWorks' registered switch read live; the rule is K_SWITCHES_OWN_THEIR_KIND"),
    ("gravship_keeps_connections", "a real gravship launch and landing; the plan is K_REMOVAL_PLAN"),
    ("gravship_connectivity", "as gravship_keeps_connections"),
    ("owner_change_coils_wires", "a faction change of a real pole and its message"),
    ("owner_change_cut", "as owner_change_coils_wires"),
    ("statics_clear_between_games", "statics across a new game or load in one session"),
    ("game_statics_reset", "as statics_clear_between_games"),
    ("uninstall_clean", "a save loading without the mod"),
    ("cords_draw_under_things", "cord draw order under items in game"),
    ("walk_scavenger_base", "a week of live play"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kernel", default=os.path.join(MOD, "Source/Aerial/AerialMath.cs"))
    ap.add_argument("--shockrule", default=os.path.join(MOD, "Source/Aerial/ShockRule.cs"))
    ap.add_argument("--mod-root", default=MOD)
    ap.add_argument("--dll", default=None)
    ap.add_argument("--out", default=os.path.join(HERE, "lane1_rows.jsonl"))
    a = ap.parse_args()
    dll = a.dll or os.path.join(a.mod_root, "Assemblies/RimMandrakeGimmeSomeSlack.dll")
    rows = []
    s = subprocess.run([sys.executable, os.path.join(HERE, "BlindLane1.py"), "--mod-root", a.mod_root, "--guard"], capture_output=True, text=True, timeout=400)
    rows += [json.loads(l) for l in s.stdout.splitlines() if l.startswith("{")]
    if not rows:
        sys.exit("SCAN FAILED rc %s\n%s" % (s.returncode, s.stderr[-2000:]))
    os.makedirs(STAGE, exist_ok=True)
    for f in glob.glob(os.path.join(STAGE, "*.cs")) + glob.glob(os.path.join(STAGE, "*.dll")):
        os.remove(f)
    shutil.copy(os.path.join(HERE, "BlindLane1.cs"), STAGE)
    shutil.copy(a.kernel, os.path.join(STAGE, "AerialMath.cs"))
    shutil.copy(a.shockrule, os.path.join(STAGE, "ShockRule.cs"))
    # AerialMath reads two wall-plate constants from Core/WallMount.cs (whose own chain reaches CordBuilder): hand the two
    # shipped numbers over in a stub, read from that file, never retyped
    import re
    wm = open(os.path.join(a.mod_root, "Source/Core/WallMount.cs"), encoding="utf-8-sig").read()
    consts = {k: re.search(r"public const double %s = ([\d.]+);" % k, wm).group(1) for k in ("SouthBand", "SideBevel")}
    open(os.path.join(STAGE, "WallMountStub.cs"), "w").write(
        "namespace RimMandrake.GimmeSomeSlack.Core { public static class WallMount { public const double SouthBand = %s; public const double SideBevel = %s; } }\n"
        % (consts["SouthBand"], consts["SideBevel"]))
    gdll = os.path.join(STAGE, "shipped_gss.dll.bin")
    shutil.copy(dll, gdll)
    open(os.path.join(STAGE, "BlindLane1.csproj"), "w").write(CSPROJ)
    dn = sorted(glob.glob("/mnt/c/Users/*/.dotnet/dotnet.exe"))[0]
    win = subprocess.run(["wslpath", "-w", STAGE], capture_output=True, text=True, check=True).stdout.strip()
    b = subprocess.run([dn, "build", win + "\\BlindLane1.csproj", "-c", "Release", "--nologo", "-v", "q"], capture_output=True, text=True, timeout=400)
    if b.returncode:
        rows.append({"id": "K_BUILD", "bars": ["no_hose"], "kind": "fixed", "verdict": "FAIL", "cases": 1, "detail": "kernel build failed: " + (b.stdout[-600:] + b.stderr[-300:])})
    else:
        env = dict(os.environ, GSS_DLL=win + "\\shipped_gss.dll.bin")
        env["WSLENV"] = ":".join(filter(None, [os.environ.get("WSLENV", ""), "GSS_DLL"]))
        r = subprocess.run([dn, win + "\\bin\\Release\\net8.0\\BlindLane1.dll"], capture_output=True, text=True, env=env, timeout=400)
        k = [json.loads(l) for l in r.stdout.splitlines() if l.startswith("{")]
        if not k:
            k = [{"id": "K_RUN", "bars": ["no_hose"], "kind": "fixed", "verdict": "FAIL", "cases": 1, "detail": "kernel run produced no rows rc %s %s" % (r.returncode, r.stderr[-500:])}]
        rows += k
    # Bars whose logic is game-side (drawing, Things, jobs, maps, Harmony, saves): one not_kernel row each, owed to Stage 6.
    # The kernel rows above test what part of them is Verse-free; these rows say the rest was not decided here.
    for bar, why in NOT_KERNEL:
        rows.append({"id": "NK_" + bar.upper(), "bars": [bar], "kind": "not_kernel", "verdict": "UNSETTLED", "cases": 0,
                     "detail": "game-side, not decidable from a Verse-free kernel offline: " + why})
    with open(a.out, "w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")
    c = {}
    for row in rows:
        c[row["verdict"]] = c.get(row["verdict"], 0) + 1
    print("LANE1", json.dumps(c), "rows", len(rows), "->", a.out)
    for row in rows:
        if row["verdict"] == "FAIL":
            print("FAIL", row["id"], row["detail"][:400])
    sys.exit(1 if c.get("FAIL") else 0)


main()
