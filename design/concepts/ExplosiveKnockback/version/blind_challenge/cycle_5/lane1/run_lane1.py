#!/usr/bin/env python3
"""Run blind lane 1 (cycle 5, judge-1794890427) against the shipped ExplosiveKnockback, or against planted copies.
    python3 run_lane1.py [--kernel <RM_KnockbackMath.cs>] [--mod-root <dir>] [--out <rows.jsonl>]
Two halves: BlindLane1.py (shipped settings, the per-type patch, the proof build gate and the proof scenes' entry points) and
BlindLane1.cs (the Verse-free kernel, staged with RM_KnockbackMath.cs under
/mnt/d/ClaudeWork/rimmandrake/scratch/explosiveknockback_blind_c5_lane1/ because dotnet.exe cannot build from a WSL path).
One JSON row per line; prints the verdict counts. Exit 0 = every decided row PASS."""
import argparse, glob, json, os, shutil, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
MOD = os.path.join(REPO, "src/RimMandrake/ExplosiveKnockback")
STAGE = os.environ.get("EK_LANE1_STAGE", "/mnt/d/ClaudeWork/rimmandrake/scratch/explosiveknockback_blind_c5_lane1")
CSPROJ = """<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework>
<LangVersion>latest</LangVersion><Nullable>disable</Nullable><ImplicitUsings>disable</ImplicitUsings></PropertyGroup></Project>"""

# Stage-6 bars whose logic is game-side (PawnFlyer, Things, maps, jobs, Harmony, saves, the explosion wave, the live gas grid).
# The kernel rows test their Verse-free part; these rows say the rest was not decided here. No offline bar is named.
NOT_KERNEL = [
    ("people_thrown_three_cells", "the PawnFlyer launch, the landing alive and stunned"),
    ("pawn_flight_arc", "the carrier's drawn arc, no re-target, the stun ending and the job resuming"),
    ("the_spared", "in pit, carrying, airborne, in bed are pawn-state reads in the hook"),
    ("heavier_flies_less", "the mass read from the Mass stat less inventory and the damage read off the live explosion"),
    ("recovery_immunity", "the landing tick and stun end saved and reloaded"),
    ("hose_drops_at_takeoff", "FlowWorks' hose end dropped by the launch"),
    ("wall_stops_dead", "the impact applied as damage, no second move"),
    ("pawn_hits_pawn_stops", "the impact applied to both pawns"),
    ("doors_and_deep_water_stop", "door hit points, the terrain read as Water"),
    ("shield_belt_holds", "the belt's absorb and its energy read"),
    ("goods_arc_spin_rebound", "the thrown-thing carrier's arc, spin and bounce chain, the killed pawn's corpse"),
    ("every_good_moves", "the wave's reach over a stockpile and the hook's candidate list"),
    ("open_shelf_scatters", "whether a building draws its contents"),
    ("closed_container_holds", "ThrowContainer walking the path and the jolt drawing"),
    ("heavy_stack_knocks", "the carrier meeting a pawn's cell"),
    ("every_harmful_blast_throws", "the live DamageDefs and modded explosions"),
    ("only_explosions_throw", "the hook firing for explosions only"),
    ("per_weapon_tuning", "reading the extension off projectile, weapon and DamageDef"),
    ("gas_goes_clump_by_clump", "the gas grid, the fire front and the clump bursts"),
    ("our_gases_burn", "the census of our gas sources and the Cauldron's registration"),
    ("blast_breaks_pit_cover", "FlowWorks' cover hit points and descents"),
    ("thrown_into_pit_falls", "FlowWorks' descent of a landed thing; the gas shove onto a pit"),
    ("pit_goods_fetched", "a hauler's job off a pit floor"),
    ("no_teleport", "the despawn/spawn trace of moved goods"),
    ("no_careless_fall", "colonist pathing round pits"),
    ("settings_scale_and_switch", "each switch's off state in game"),
    ("barrage_frame_budget", "frame times measured on the full list"),
    ("frame_time_probe", "the probe's rows against rendered frames"),
    ("walk_storeroom_raid", "a live raid with a reload"),
    ("inv_hook", "the Harmony hook on the explosion"),
    ("inv_pawn_flyer", "the PawnFlyer def and launch"),
    ("inv_which_blasts", "the live DamageDefs"),
    ("inv_items_teleport", "the goods carrier replacing the hop"),
    ("inv_shelf_skip", "the storage read under a good"),
    ("inv_who_is_spared", "pawn-state skips in the hook"),
    ("inv_shield", "the belt in game"),
    ("inv_recovery", "saved immunity"),
    ("inv_caps", "the caps removed from the hook"),
    ("inv_settings", "the settings page in game"),
    ("inv_pits_receive", "FlowWorks pits receiving a landing"),
    ("inv_pit_floor_haul", "a haul off a pit floor"),
    ("inv_hose_drop", "the hose drop at launch"),
    ("inv_gas_chain", "the gas chain in game"),
    ("inv_goods_fly", "the goods carrier"),
    ("inv_closed_guard", "the closed-container read"),
    ("inv_container_shove", "the container throw in game"),
    ("inv_heavy_knock", "the knock in the carrier"),
    ("inv_gas_tags", "the gas DefModExtension on our gases"),
    ("inv_perf_all_fly", "the all-fly frame cost"),
    ("inv_weapon_ext_fields", "the extension fields read in game"),
    ("inv_killed_corpse", "the corpse of a pawn the blast kills"),
    ("inv_pit_floor_goods_stay", "goods on a pit floor skipped"),
    ("inv_big_corpse_spared", "the corpse's mass read"),
    ("inv_mass_limit_skip", "the mass read in the hook"),
    ("inv_too_weak_skip", "the rim skip logged"),
    ("inv_creature_mass_limit", "the creature's Mass stat less inventory"),
    ("inv_blast_power_damage", "the explosion's damage and its type's default"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kernel", default=os.path.join(MOD, "Source/RM_KnockbackMath.cs"))
    ap.add_argument("--mod-root", default=MOD)
    ap.add_argument("--out", default=os.path.join(HERE, "lane1_rows.jsonl"))
    a = ap.parse_args()
    rows = []
    s = subprocess.run([sys.executable, os.path.join(HERE, "BlindLane1.py"), "--mod-root", a.mod_root], capture_output=True, text=True, timeout=300)
    rows += [json.loads(l) for l in s.stdout.splitlines() if l.startswith("{")]
    if not rows or s.returncode:
        rows.append({"id": "S_RUN", "bars": ["inv_proof_scenes"], "kind": "fixed", "verdict": "FAIL", "cases": 1,
                     "detail": "python half rc %s %s" % (s.returncode, s.stderr[-800:])})
    os.makedirs(STAGE, exist_ok=True)
    for f in glob.glob(os.path.join(STAGE, "*.cs")):
        os.remove(f)
    shutil.copy(os.path.join(HERE, "BlindLane1.cs"), STAGE)
    shutil.copy(a.kernel, os.path.join(STAGE, "RM_KnockbackMath.cs"))
    open(os.path.join(STAGE, "BlindLane1.csproj"), "w").write(CSPROJ)
    dn = sorted(glob.glob("/mnt/c/Users/*/.dotnet/dotnet.exe"))[0]
    win = subprocess.run(["wslpath", "-w", STAGE], capture_output=True, text=True, check=True).stdout.strip()
    b = subprocess.run([dn, "build", win + "\\BlindLane1.csproj", "-c", "Release", "--nologo", "-v", "q"], capture_output=True, text=True, timeout=400)
    if b.returncode:
        rows.append({"id": "K_BUILD", "bars": ["inv_kernel"], "kind": "fixed", "verdict": "FAIL", "cases": 1, "detail": "kernel build failed: " + (b.stdout[-900:] + b.stderr[-300:])})
    else:
        r = subprocess.run([dn, win + "\\bin\\Release\\net8.0\\BlindLane1.dll"], capture_output=True, text=True, timeout=400)
        k = [json.loads(l) for l in r.stdout.splitlines() if l.startswith("{")]
        if not k or r.returncode:
            k.append({"id": "K_RUN", "bars": ["inv_kernel"], "kind": "fixed", "verdict": "FAIL", "cases": 1, "detail": "kernel run rc %s %s" % (r.returncode, r.stderr[-800:])})
        rows += k
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
            print("FAIL", row["id"], row["detail"][:500])
    sys.exit(1 if c.get("FAIL") else 0)


main()
