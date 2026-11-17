#!/usr/bin/env python3
"""Run Pyrelands blind lane 1 (cycle 3).
    python3 run_lane1.py [--kernel <file.cs> ...] [--mod <mod root>] [--out <rows.jsonl>]
Stages BlindLane1.cs + the shipped Verse-free kernels (any --kernel replaces the staged file of the same name) under
/mnt/d/ClaudeWork/rimmandrake/scratch/pyrelands_blind_c3_lane1 (dotnet.exe cannot build from a WSL path; LANE1_STAGE overrides),
builds and runs it with the per-user Windows dotnet, then runs blind_lane1_files.py over the mod, then writes one not_kernel
row per bar no lane-1 test reaches. Exit 0 = no FAIL row."""
import argparse, glob, json, os, re, shutil, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
MOD = os.path.join(REPO, "src/RimMandrake/Pyrelands")
KERNELS = ["Source/Kernel/RM_FireEcoKernel.cs", "Source/Kernel/RM_BurnKernel.cs", "Source/Kernel/RM_FireHawkKernel.cs",
           "Source/Kernel/RM_FireHawkRewardsKernel.cs", "Source/Kernel/RM_FurnaceKernel.cs", "Source/FurnaceWarmthMath.cs",
           "Source/PyrelandsTuning.cs"]
CSPROJ = """<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework>
<LangVersion>latest</LangVersion><Nullable>disable</Nullable><ImplicitUsings>disable</ImplicitUsings></PropertyGroup></Project>"""

# every bar of 0.1.0 (version/bars.md), and the lane-1 reason a bar is game-side when no kernel row reaches it
BARS = {
    "burn_line_walks": None, "ash_ground_and_blowing_ash": "ash depth, drifts and dimming are engine-side (sand grid, weather overlay, ash cover); only the clear-weight split is kernel",
    "ash_fertile_when_watered": None, "fresh_burn_compounds_with_black_rain": None,
    "grass_carpets_and_regreens": "regrowth speed, the gentle burst and withering under a roof are plant ticks on the map",
    "scorchfruit_born_of_fire": "pods spawning in the scar and rotting are fire-tick and rot ticks on the map",
    "populations_are_the_biomes_own": "the cast on a fresh map and its counts are map generation",
    "ruins_stand_blackened": "ruin scorching is a genstep on a generated map", "firehawk_lights_ahead": None,
    "furnacebeast_warms": None, "ashwallow_dives_unharmed": "the dive, the dome and surviving the front are job drivers on the map",
    "ullai_graze_old_burns": "the herd drive reads a burn history on the map", "three_skies": "the skies are weather overlays read by eye",
    "no_ordinary_rain": "the weather decider runs in the game; the kernel half (RainBecomesBlackRain) is in gate_fixed_every_switch_off_reads_off",
    "ash_fertility_probe": None, "walk_season_on_the_pyre": "two weeks of play on the full list",
    "firefoam_sprayer_reaches_the_fruit": "a colonist foaming into a burn is a job on the map",
    "sand_shovel_yields_glass_sand": "the dig order's yield is a job on the map (RM_TerrainDig)",
    "fire_rite_hook_silent_alone": "the hook's silence is load-time behaviour with no listener",
    "biome_text_says_engineered": None, "flamefang_bite_carries_venom": "the bite's hediff is damage resolution in the game",
    "ullai_cross_the_map_as_vanilla_herds": "herd migration is the vanilla incident on the map",
    "inv_biome_self_contained": "load-order self-containment needs a load", "inv_plant_roster": "the wild plant list resolves at map generation",
    "inv_embergrass_regrow": "regrowth is plant ticks", "inv_animal_roster": "the animal list resolves at map generation",
    "inv_ash_field": "the ash field's grid and postfix are engine-side; the kernel half is in the probe and compound rows",
    "inv_burn_line_fire_clock": None, "inv_scorchfruit": "pods are fire-tick spawns", "inv_ruins_scorched": "a genstep",
    "inv_firehawk_ember": "the carry job is a job driver; the drop choice is in hawk_random_drop_goes_to_largest_unburnt_fuel (bar firehawk_lights_ahead)",
    "inv_furnacebeast": "the thermal circuit runs on comps; warmth math is in warmth_random_falls_off_to_radius (bar furnacebeast_warms)",
    "inv_burrowers_heat_dome": "job drivers", "inv_ullai_herd_giant": "race defs resolved at load and herd spawning",
    "inv_weather": "weather defs resolved at load", "inv_firebreak_firefoam": None, "inv_firefoam_sprayer": "a sprayer verb in the game",
    "inv_sand_shovel": "a designator and job in the game", "inv_lightning_breaker": None, "inv_fire_rite_hook": "an event hook in the game",
    "inv_settings_gate": None, "inv_art_and_text": None, "inv_firehawk_hunt_rewards": None,
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kernel", action="append", default=[])
    ap.add_argument("--mod", default=MOD)
    ap.add_argument("--out", default=os.path.join(HERE, "lane1_rows.jsonl"))
    a = ap.parse_args()
    stage = os.environ.get("LANE1_STAGE", "/mnt/d/ClaudeWork/rimmandrake/scratch/pyrelands_blind_c3_lane1")
    os.makedirs(stage, exist_ok=True)
    for f in glob.glob(os.path.join(stage, "*.cs")):
        os.remove(f)
    shutil.copy(os.path.join(HERE, "BlindLane1.cs"), stage)
    over = {os.path.basename(k): k for k in a.kernel}
    for k in KERNELS:
        name = os.path.basename(k)
        path = over.pop(name, os.path.join(a.mod, k))
        text = open(path, encoding="utf-8").read()
        if name == "PyrelandsTuning.cs":  # the one Verse call (a Pawn's body size) is not game logic the lane reads
            text = re.sub(r"public static float FurnaceSizeRatio\(Verse\.Pawn beast\)\s*\{[^}]*\}", "", text)
        open(os.path.join(stage, name), "w", encoding="utf-8").write(text)
    if over:
        sys.exit("--kernel names no staged kernel: " + ", ".join(over))
    open(os.path.join(stage, "BlindLane1.csproj"), "w").write(CSPROJ)
    dn = sorted(glob.glob("/mnt/c/Users/*/.dotnet/dotnet.exe"))[0]
    win = subprocess.run(["wslpath", "-w", stage], capture_output=True, text=True, check=True).stdout.strip()
    b = subprocess.run([dn, "build", win + "\\BlindLane1.csproj", "-c", "Release", "--nologo", "-v", "q"], capture_output=True, text=True, timeout=400)
    rows = []
    if b.returncode:
        rows.append({"id": "lane1_build", "bars": ["ash_fertility_probe", "inv_settings_gate"], "kind": "fixed", "verdict": "FAIL", "cases": 1,
                     "detail": "the kernels do not compile with the lane-1 tests: " + (b.stdout[-800:] + b.stderr[-400:]).replace("\n", " ")})
    else:
        r = subprocess.run([dn, win + "\\bin\\Release\\net8.0\\BlindLane1.dll"], capture_output=True, text=True, timeout=400)
        got = [json.loads(l) for l in r.stdout.splitlines() if l.startswith("{")]
        if r.returncode not in (0, 1) or not got:
            got.append({"id": "lane1_run", "bars": ["ash_fertility_probe", "inv_settings_gate"], "kind": "fixed", "verdict": "FAIL", "cases": 1,
                        "detail": "the kernel run crashed rc %s: %s" % (r.returncode, r.stderr[-800:].replace("\n", " "))})
        rows += got
    p = subprocess.run([sys.executable, os.path.join(HERE, "blind_lane1_files.py"), "--mod", a.mod], capture_output=True, text=True, timeout=300)
    frows = [json.loads(l) for l in p.stdout.splitlines() if l.startswith("{")]
    if not frows:
        frows.append({"id": "lane1_files_run", "bars": ["inv_settings_gate"], "kind": "fixed", "verdict": "FAIL", "cases": 1,
                      "detail": "blind_lane1_files.py crashed: " + p.stderr[-800:].replace("\n", " ")})
    rows += frows
    covered = set(b for r in rows for b in r["bars"])
    for bar, why in BARS.items():
        if bar not in covered:
            rows.append({"id": "not_kernel_" + bar, "bars": [bar], "kind": "not_kernel", "verdict": "UNSETTLED", "cases": 0,
                         "detail": "game-side: " + (why or "no kernel") + "; settled by its live scene at stage 6"})
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
