#!/usr/bin/env python3
"""THROWAWAY (Maturation Pipeline pilot row 2, 2026-11-14): build ExplosiveKnockback 0.1.0's test-and-stage table.
The bar -> test placement below is hand judgment; runs_today is MEASURED by running every offline test now.
Usage: python3 make_test_table.py <repo>   writes design/concepts/ExplosiveKnockback/version/test_table.{json,md}"""
import json, os, re, subprocess, sys, time, datetime
REPO = os.path.abspath(sys.argv[1]); os.chdir(REPO)
C = "design/concepts/ExplosiveKnockback"; M = "src/RimMandrake/ExplosiveKnockback"
PROOF = M + "/Source/RM_KnockbackProof.cs"; MATH = M + "/Source/RM_KnockbackMath.cs"; MC = M + "/Source/RM_MapComponent_Knockback.cs"
MOD = M + "/Source/RM_KnockbackMod.cs"; DMG = M + "/Patches/RM_Knockback_DamageDefs.xml"
SELFTEST_SRC = [MATH, M + "/Source/SelfTest/Program.cs", M + "/Source/SelfTest/KnockbackFuzz.cs"]

# ---- offline tests (stage 4-5 = proven at the blind offline stage; 2 = a static preflight-class check) ----
OFF = {
 "T_KERNEL": dict(stage="4-5", file=M + "/selftest_explosiveknockback_kernel.py", observes="K-01..K-20 kernel checks: throw cells, falloff, mass scale, path walk (walls, doors, water, sandbags, pits), dedupe, recovery window, shield debit, rebound, creature mass limit, blast power", reads=SELFTEST_SRC),
 "T_FUZZ": dict(stage="4-5", file="src/RimMandrake/Utils/selftest_explosiveknockback_fuzz.py", observes="42001 seeded random cases of the kernel against independent oracles (distance, line, grid walk, cap, lookup, guards)", reads=SELFTEST_SRC),
 "T_LINT": dict(stage="2", file="src/RimMandrake/Utils/lint_explosiveknockback_defs.py", observes="defs and patches against the C#: every RM_KnockbackExtension field and range, the damage-def patches, the flyer def, reset-to-defaults inside sliders, kernel Verse-free", reads=[DMG, M + "/Defs/ThingDefs/RM_PawnFlyer_Knockback.xml", MOD, MATH]),
 "T_LINT_PLANTED": dict(stage="2", file="src/RimMandrake/Utils/selftest_explosiveknockback_lint.py", observes="the lint goes red on 20 planted defects and stays clean on the real mod", reads=[DMG, "src/RimMandrake/Utils/lint_explosiveknockback_defs.py"]),
 "T_CENSUS": dict(stage="4-5", file=M + "/selftest_explosiveknockback_storage_census.py", observes="every storage def is closed exactly when it hides its contents (Shelf, ShelfSmall, Hopper, Cold Storage open)", reads=[MC, "src/RimMandrake (every storage ThingDef)"]),
 "T_SCRIPT": dict(stage="2", file=M + "/selftest_explosiveknockback_script.py", observes="validation.py STATIC (walk coverage, csproj, scene and toggle names, settings saved and reset) and --mock (every proof scene stages through a fake session)", reads=[M + "/validation.py", PROOF, MOD, "design/validation_walks/RimMandrake/ExplosiveKnockback.md"]),
 "T_PROOFGATE": dict(stage="4-5", file=M + "/selftest_explosiveknockback_proofgate.py", observes="the release DLL carries no proof code, a proof build carries all of it, the gate reads the bridge's answer", reads=[M + "/Assemblies/RimMandrakeExplosiveKnockback.dll", M + "/proof_build_gate.py", PROOF]),
 "T_RESTORE": dict(stage="4-5", file="src/RimMandrake/Utils/selftest_proof_restore_check.py", observes="every proof scene restores what it staged even when it throws", reads=[PROOF], known_red="RIMMANDRAKE_RESTORE_ON_THROW_IN_KNOCKBACK_PROOF_TWO_LEAKS"),
 "T_SETTINGS_SCREEN": dict(stage="4-5", file="src/RimMandrake/Utils/selftest_settings_screens.py", observes="the Mod Settings screen: every setting grouped, resettable, scopes as audited", reads=[MOD], known_red="RIMMANDRAKE_REGROUP_SETTINGS_SCREENS_FOUR_MODS_OUTGREW_AUDIT"),
 "T_FW_COVER": dict(stage="4-5", file="src/RimMandrake/FlowWorks/selftest_flowworks_cover_breaks.py", observes="FlowWorks: a pit cover breaks on every fall, before the descent", reads=["src/RimMandrake/FlowWorks/Source/Pits/Building_PitCover.cs", "src/RimMandrake/FlowWorks/Source/Superdeep/RM_PitPathing.cs"]),
 # ---- specified, not built (Stage 3 builds them, failing first) ----
 "T_SETTINGS_SWEEP_OFFLINE": dict(stage="4-5", file=M + "/selftest_explosiveknockback_settings_sweep.py", new=False, item="RIMMANDRAKE_SPLIT_KNOCKBACK_SWEEP_OFFLINE_TABLE_LIVE_WIRING",
     observes="sc_settings_sweep's lane as kernel inputs, run once at default and once per kernel-side setting; each changes only its own outcomes with the scene's numbers; a mutant coupling two settings goes red; the saved Scribe fields equal the sweep list plus enabled and shieldsAbsorbThrow, with no per-explosion, per-tick or body-size field", reads=SELFTEST_SRC + [MOD, C + "/scenes.json"]),
 "T_GAS_TAG_CENSUS": dict(stage="4-5", file=M + "/selftest_explosiveknockback_gas_census.py", new=False, item="RIMMANDRAKE_CHAIN_FLAMMABLE_GAS_CLUMPS",
     observes="every flammable gas source of ours (Gas ThingDefs, our gas grids, the Cauldron's vent gas) carries the opt-in flammable tag, and nothing else does (the leaf our_gases_burn's own offline clause)", reads=["src/RimMandrake (Gas ThingDefs and gas grids)", "src/RimMandrake/Cauldron"]),
 "T_GAS_CLUMP_ORDER": dict(stage="4-5", file=M + "/selftest_explosiveknockback_gas_clumps.py", new=False, item="RIMMANDRAKE_CHAIN_FLAMMABLE_GAS_CLUMPS",
     observes="the clump plan of a lit cloud as pure logic: one burst per clump cell, ordered by distance from the lit edge, a fire not touching the cloud lights nothing, goods within 1.9 cells of a burst moved, people shoved one cell unhurt", reads=[MC]),
 "T_HEAVY_KNOCK_RULE": dict(stage="4-5", file=M + "/selftest_explosiveknockback_kernel.py", new=False, item="RIMMANDRAKE_KNOCK_PEOPLE_HEAVY_GOODS",
     observes="the heavy-stack rule as kernel cases: over the heavy threshold blunt 2 to 5 and a stagger and the stack stops; under it no damage and it passes", reads=SELFTEST_SRC),
 "T_STAGE3_SCENES": dict(stage="2", file=M + "/selftest_explosiveknockback_stage3_scenes.py", item="RIMMANDRAKE_BUILD_KNOCKBACK_STAGE_THREE_ELEVEN_BARS_UNRUN",
     observes="the five Stage 3 scenes (hose drop, closed containers, settings sweep, frame probe, barrage) and their control lanes are named and routed, carry their start assertions, set a restore, the sweep list equals the saved keys, and the runner can wait in real time", reads=[PROOF, M + "/Source/RM_KnockbackProof_StageThree.cs", MOD, M + "/knockback_runner.py", C + "/scenes.json"]),
 "T_ONLY_EXPLOSIONS_STATIC": dict(stage="2", file=M + "/selftest_explosiveknockback_hook_scope.py", new=False, item="RIMMANDRAKE_THROW_ALL_HARMFUL_BLASTS",
     observes="the only Harmony patch that queues a throw is on the explosion's damage step (no melee or bullet damage worker is patched)", reads=[M + "/Source/RM_Patch_DamageWorker_ExplosionKnockback.cs", MC]),
}
# ---- in-game tests: every scenes.json scene is one (stage 6 on the minimal list unless marked full; 8 = his look) ----
FULL = {"sc_barrage_perf": "frame time is meaningful only on the real list and machine (leaf barrage_frame_budget)",
        "sc_walk_raid": "the walk is the full list, played (leaf walk_storeroom_raid)"}
WHY_GAME = {  # why an offline test cannot decide the scene's remaining clause (hand judgment; the Stage 4 challenger re-asks it)
 "sc_mortar_throw": "landing cell, alive and stunned are the PawnFlyer's runtime; the kernel only gives the planned cells",
 "sc_over_sandbags": "the flyer passing a real sandbag thing; the kernel's sandbag rule is K-06",
 "sc_pawn_arc": "mid-flight drawn position inside RM_PawnFlyer_Knockback exists only in a running game",
 "sc_spared": "in_pit, carrying, in_bed and flying are live pawn states read by the map component, not kernel inputs",
 "sc_mass_and_power": "the explosion's real damage and the Mass stat as the game computes it reach the kernel only in game (the cell table itself is K-19, offline)",
 "sc_recovery": "the stamps on the map component and their save and reload are runtime",
 "sc_hose_drop": "a colonist mid CarryHoseEnd job is a live job state",
 "sc_settings_off": "the master switch silencing the real explosion hook (not the kernel) is runtime",
 "sc_settings_sweep": "THIN after the move: only game-side settings (throwAnimals/Mechanoids/Downed/Items/Corpses, landingStunMin and landingStunMax, doorsTakeDamage, debugDrawVectors, vanillaCratesClosed, heavy threshold, goods in air, closed guard, heavy knock, gas chain, fire at half) and one Settings -> Kernel() read-back per kernel-side setting; the kernel-side lines move to T_SETTINGS_SWEEP_OFFLINE",
 "sc_wall_stop": "impact damage applied to a real pawn by the flyer; the stop cell is K-07 offline",
 "sc_pawn_hits_pawn": "two real pawns and the flyer's stop; the stop rule is K-09 offline",
 "sc_door_water": "door hit points and the colonist's injury are runtime; stop cells are K-07 offline",
 "sc_shield": "a real shield belt's energy after a real absorb; the debit maths is K-16 offline",
 "sc_storeroom_mortar": "a per-tick trace of real thrown things (height, rotation, rebound) exists only in game; the rebound maths is K-17 offline",
 "sc_all_fly_no_cap": "over 60 real things reached in one tick, all moved; the no-cap rule is K-11 offline",
 "sc_open_storage": "real furniture emptied by a real blast; the open rule is K-14 and the census offline",
 "sc_closed_containers": "real lockers keeping contents and sliding; the hold and shove rules are K-14 offline",
 "sc_heavy_knock": "blunt damage and stagger on a real pawn",
 "sc_blast_kinds": "the real damage defs reaching the hook at their real strengths; the patch values are T_LINT offline",
 "sc_only_explosions": "a real melee hit and a real bullet producing no request line (the static half is T_ONLY_EXPLOSIONS_STATIC)",
 "sc_lookup": "which def on a real projectile, weapon and damage type the hook reads; the lookup order is K-13 offline",
 "sc_gas_chain": "a real gas grid lit by a real fire, bursts over ticks",
 "sc_cauldron_gas": "the Cauldron's registered vent gas burning by registration, not by its own scan",
 "sc_cover_breaks": "a real cover deck and a real descent (FlowWorks' break rule is T_FW_COVER offline)",
 "sc_pit_fall": "a real descent recorded by FlowWorks after a real throw; the stop-in-pit cell is K-08 offline",
 "sc_pit_enemy": "a real raider's descent",
 "sc_no_careless_fall": "real pathing around real pits",
 "sc_pit_fetch": "a hauler's job and ladder route over up to a day of game time",
 "sc_frame_probe_check": "frames exist only in a running game",
 "sc_gas_shove_into_pit": "a gas burst shoving a real pawn into a real pit",
 "sc_killed_thrown": "a pawn killed by a real blast becoming a corpse that is thrown",
 "sc_goods_obstacles": "real things in flight meeting real walls, pawns and doors",
 "sc_storeroom_bomb_pit": "the flagship interaction of every part at once, his chosen face of the mod",
 "sc_barrage_perf": FULL["sc_barrage_perf"], "sc_walk_raid": FULL["sc_walk_raid"],
}
# ---- bars: decides (all must pass) + supports; hand placement ----
B = {
 # tree leaves
 "people_thrown_three_cells": (["T_KERNEL", "sc_mortar_throw", "sc_over_sandbags"], ["T_FUZZ", "sc_storeroom_bomb_pit"]),
 "pawn_flight_arc": (["sc_pawn_arc"], ["sc_storeroom_bomb_pit"]),
 "the_spared": (["T_KERNEL", "sc_spared"], ["T_SETTINGS_SWEEP_OFFLINE"]),
 "heavier_flies_less": (["T_KERNEL", "sc_mass_and_power"], ["T_FUZZ"]),
 "recovery_immunity": (["T_KERNEL", "sc_recovery"], []),
 "hose_drops_at_takeoff": (["sc_hose_drop"], ["T_STAGE3_SCENES"]),
 "wall_stops_dead": (["T_KERNEL", "sc_wall_stop"], ["T_FUZZ"]),
 "pawn_hits_pawn_stops": (["T_KERNEL", "sc_pawn_hits_pawn"], ["T_FUZZ"]),
 "doors_and_deep_water_stop": (["T_KERNEL", "sc_door_water"], ["T_FUZZ"]),
 "shield_belt_holds": (["T_KERNEL", "sc_shield"], []),
 "goods_arc_spin_rebound": (["T_KERNEL", "sc_storeroom_mortar", "sc_killed_thrown"], ["sc_goods_obstacles", "sc_storeroom_bomb_pit"]),
 "every_good_moves": (["T_KERNEL", "sc_all_fly_no_cap"], ["sc_storeroom_bomb_pit"]),
 "open_shelf_scatters": (["T_CENSUS", "T_KERNEL", "sc_open_storage"], ["sc_storeroom_bomb_pit"]),
 "closed_container_holds": (["T_CENSUS", "T_KERNEL", "sc_closed_containers"], ["sc_storeroom_bomb_pit", "T_STAGE3_SCENES"]),
 "heavy_stack_knocks": (["T_HEAVY_KNOCK_RULE", "sc_heavy_knock"], ["sc_storeroom_bomb_pit"]),
 "every_harmful_blast_throws": (["T_LINT", "T_KERNEL", "sc_blast_kinds"], ["T_LINT_PLANTED"]),
 "only_explosions_throw": (["T_ONLY_EXPLOSIONS_STATIC", "sc_only_explosions"], []),
 "per_weapon_tuning": (["T_KERNEL", "T_LINT", "sc_lookup"], ["T_FUZZ"]),
 "gas_goes_clump_by_clump": (["T_GAS_CLUMP_ORDER", "sc_gas_chain"], ["sc_gas_shove_into_pit"]),
 "our_gases_burn": (["T_GAS_TAG_CENSUS", "sc_cauldron_gas"], []),
 "blast_breaks_pit_cover": (["T_FW_COVER", "sc_cover_breaks"], []),
 "thrown_into_pit_falls": (["T_KERNEL", "sc_pit_fall", "sc_pit_enemy"], ["sc_gas_shove_into_pit", "sc_storeroom_bomb_pit"]),
 "pit_goods_fetched": (["sc_pit_fetch"], []),
 "no_teleport": (["sc_storeroom_mortar", "sc_gas_chain"], []),
 "no_careless_fall": (["sc_no_careless_fall"], []),
 "settings_scale_and_switch": (["T_SETTINGS_SWEEP_OFFLINE", "T_SETTINGS_SCREEN", "sc_settings_sweep", "sc_settings_off"], ["T_SCRIPT", "T_STAGE3_SCENES"]),
 "barrage_frame_budget": (["sc_barrage_perf"], ["sc_frame_probe_check", "T_STAGE3_SCENES", "T_KERNEL"]),
 "frame_time_probe": (["sc_frame_probe_check"], ["T_STAGE3_SCENES", "T_KERNEL"]),
 "walk_storeroom_raid": (["sc_walk_raid", "LOOK_STAGE8"], ["sc_storeroom_bomb_pit"]),
 # record.json inventory rows
 "inv_kernel": (["T_KERNEL", "T_FUZZ"], ["T_LINT"]),
 "inv_hook": (["sc_mortar_throw"], ["sc_blast_kinds", "T_ONLY_EXPLOSIONS_STATIC"]),
 "inv_pawn_flyer": (["T_LINT", "sc_pawn_arc", "sc_wall_stop"], []),
 "inv_which_blasts": (["T_LINT", "T_KERNEL", "sc_blast_kinds"], ["T_LINT_PLANTED"]),
 "inv_items_teleport": (["sc_storeroom_mortar", "sc_gas_chain"], []),
 "inv_shelf_skip": (["T_KERNEL", "T_CENSUS", "sc_open_storage"], []),
 "inv_who_is_spared": (["T_KERNEL", "sc_spared"], []),
 "inv_shield": (["T_KERNEL", "sc_shield"], []),
 "inv_recovery": (["T_KERNEL", "sc_recovery"], []),
 "inv_caps": (["T_KERNEL", "T_SETTINGS_SWEEP_OFFLINE", "sc_all_fly_no_cap"], []),
 "inv_settings": (["T_SETTINGS_SWEEP_OFFLINE", "T_SETTINGS_SCREEN", "sc_settings_sweep", "sc_settings_off"], ["T_SCRIPT", "T_LINT", "T_STAGE3_SCENES"]),
 "inv_pits_receive": (["T_FW_COVER", "sc_pit_fall", "sc_cover_breaks"], ["sc_pit_enemy"]),
 "inv_pit_floor_haul": (["sc_pit_fetch"], []),
 "inv_hose_drop": (["sc_hose_drop"], ["T_STAGE3_SCENES"]),
 "inv_proof_scenes": (["T_SCRIPT", "T_PROOFGATE", "T_RESTORE"], []),
 "inv_gas_chain": (["T_GAS_CLUMP_ORDER", "sc_gas_chain"], ["sc_gas_shove_into_pit"]),
 "inv_goods_fly": (["T_KERNEL", "sc_storeroom_mortar"], ["sc_goods_obstacles"]),
 "inv_closed_guard": (["T_CENSUS", "T_KERNEL", "sc_closed_containers"], ["T_STAGE3_SCENES"]),
 "inv_container_shove": (["T_KERNEL", "sc_closed_containers"], ["T_STAGE3_SCENES"]),
 "inv_heavy_knock": (["T_HEAVY_KNOCK_RULE", "sc_heavy_knock"], []),
 "inv_gas_tags": (["T_GAS_TAG_CENSUS", "sc_cauldron_gas"], []),
 "inv_perf_all_fly": (["sc_barrage_perf"], ["sc_frame_probe_check", "T_STAGE3_SCENES", "T_KERNEL"]),
 "inv_weapon_ext_fields": (["T_KERNEL", "T_LINT", "sc_lookup"], []),
 "inv_killed_corpse": (["sc_killed_thrown"], []),
 "inv_pit_floor_goods_stay": (["sc_spared"], []),
 "inv_big_corpse_spared": (["T_KERNEL", "sc_spared"], []),
 "inv_mass_limit_skip": (["T_KERNEL", "sc_settings_sweep"], ["T_SETTINGS_SWEEP_OFFLINE", "T_STAGE3_SCENES"]),
 "inv_too_weak_skip": (["T_KERNEL", "sc_all_fly_no_cap"], []),
 "inv_creature_mass_limit": (["T_KERNEL", "sc_mass_and_power"], ["T_SETTINGS_SWEEP_OFFLINE"]),
 "inv_blast_power_damage": (["T_KERNEL", "sc_mass_and_power"], ["T_SETTINGS_SWEEP_OFFLINE"]),
}
HELD = [
 {"file": "design/RimMandrake/validation_holding/owner_look_defects_2026-11-12_explosive_knockback.md", "row": 1,
  "words": "1: Anything that draws its contents is open.", "bars": ["closed_container_holds", "open_shelf_scatters", "inv_closed_guard"],
  "test": "T_CENSUS", "stage": "4-5", "kind": "offline selftest (runs today)"},
 {"file": "design/RimMandrake/validation_holding/owner_look_defects_2026-11-12_explosive_knockback.md", "row": 2,
  "words": "4: I am confused. Items should be blown off a shelf, and a shelf should be ruled as open, period. So the scene is staged misleadingly.",
  "bars": ["open_shelf_scatters", "closed_container_holds"], "test": "sc_closed_containers + sc_open_storage, plus the Stage 2 staging check (a closed-container scene stages only a def that hides its contents)",
  "stage": "2 and 6", "kind": "static staging check + fast in-game state read"},
]
CORRECTIONS = [  # the six judge gaps of rm-coverage-judge-1794599960, checked against the current scenes.json text
 ("g1", "sc_settings_sweep", ["an animal under 90 kg (asserted: mass read)", "a mech under 90 kg (asserted: mass read)"], "applied 39886c4919"),
 ("g2", "sc_gas_chain|sc_cauldron_gas|sc_cover_breaks|sc_gas_shove_into_pit|sc_settings_sweep", ["mandrake.rm.flowworks"], "applied dea7804728"),
 ("g3", "sc_mass_and_power", ["no new hediff on any of them"], "applied dea7804728"),
 ("g4", "sc_mass_and_power", ["creatureMassLimit 250", "colonist"], "applied dea7804728, REOPENED by 92fe261f36 (band 45 to 76 kg; under 63.5 kg the kernel gives 6 at damage 100, tying the capped light animal, while the expect says light > colonist and the leaf oracle says colonist 5)"),
 ("g5", "sc_settings_sweep", ["or at the cap", "exactly as far"], "applied dea7804728"),
 ("g6", "coverage_rest+showcases", [], "applied dea7804728 (inv_who_is_spared by the_spared and sc_spared; one showcase)"),
]


# ---- older proof scenes still in RM_KnockbackProof.Names (validation.py SCENES): runnable live today, SUPPORT only ----
OLD = {
 "heavy_skip": ["the_spared", "inv_who_is_spared", "inv_creature_mass_limit", "inv_mass_limit_skip"],
 "emp_no_throw": ["every_harmful_blast_throws", "inv_which_blasts"],
 "fire_half": ["every_harmful_blast_throws", "inv_which_blasts"], "harmful_unpatched": ["every_harmful_blast_throws", "inv_which_blasts"],
 "items": ["every_good_moves", "inv_mass_limit_skip", "inv_goods_fly"],
 "shelf": ["open_shelf_scatters", "inv_shelf_skip"],
 "in_pit_skip": ["the_spared", "inv_pit_floor_goods_stay", "inv_who_is_spared"],
 "no_cross": ["thrown_into_pit_falls"], "corpse_into_pit": ["thrown_into_pit_falls", "inv_pits_receive"],
 "body_override": ["per_weapon_tuning", "inv_weapon_ext_fields"], "impact_factor": ["per_weapon_tuning", "inv_weapon_ext_fields"],
 "lookup_zero_wins": ["per_weapon_tuning", "inv_weapon_ext_fields"],
 "goods_fly_midair": ["goods_arc_spin_rebound", "inv_goods_fly", "no_teleport", "inv_items_teleport"],
 "goods_fly_lands": ["goods_arc_spin_rebound", "inv_goods_fly"], "goods_fly_wall": ["goods_arc_spin_rebound", "inv_goods_fly"],
 "goods_fly_rebound": ["goods_arc_spin_rebound", "inv_goods_fly"], "goods_fly_off": ["settings_scale_and_switch", "inv_settings"],
 "container_thrown": ["closed_container_holds", "inv_container_shove", "inv_closed_guard"],
 "land_no_bump": ["goods_arc_spin_rebound"], "land_no_bump_pit": ["thrown_into_pit_falls"],
 "gas_clumps": ["gas_goes_clump_by_clump", "inv_gas_chain"],
}

def run(cmd, timeout=600):
    t = time.time(); r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    out = (r.stdout + r.stderr).strip().splitlines()
    return dict(ran=True, rc=r.returncode, seconds=round(time.time() - t, 2), last=(out[-1] if out else "")[:200])

def main():
    scenes = json.load(open(C + "/scenes.json")); S = {s["id"]: s for s in scenes["scenes"]}
    tree = json.load(open(C + "/tree.json")); rec = json.load(open(C + "/record.json"))
    proof = open(PROOF).read()
    names = re.search(r"Names\s*=\s*\{(.*?)\};", proof, re.S); names = set(re.findall(r'"(\w+)"', names.group(1))) if names else set()
    val = open(M + "/validation.py").read()
    tests = {}
    # Stage 3 reconcile (2026-11-14): scenes built by rename or with lanes left out; what each does NOT yet check
    PARTIAL = {
        "goods_fly_wild": "rename of goods_fly_rebound: checks a wall rebound at about the keep percent, the stack ends on the blast side, no carrier left. Not yet: height and rotation mid-path, no despawn-spawn pair, wild/kernel ratio 1.3-2.0, the near-row good against the colonist, the mortar over a 5x5 stockpile with a corpse, the hop control",
        "gas_chain": "rename of gas_clumps: checks 3 or more bursts on 2 or more ticks, goods moved within the goods cap, the colonist shoved at most 1 cell with no impact and the cooldown kept, the pit cover intact. Not yet: one burst per clump cell in distance order (offline in T_GAS_CLUMP_ORDER), goods beyond unmoved, colonist B's belt, no despawn-spawn pair, the igniter lane",
        "gas_census": "gas_clumps plus the vent gas's registration read; the census list itself is offline (T_GAS_TAG_CENSUS). Not yet: the registration-removed control as its own lane",
        "no_cross_ordered": "both walk orders and the covered pit are staged. Not yet: the concealed-pit raider control",
        "spared_states": "too_heavy_creature, in_pit (pawn and stack), carrying_pawn, in_bed and the heavy corpse. Not yet: the flying lane (a flyer's flight is never live-tested without the owner present)",
        "blast_kinds": "frag, BombSuper, Flame against the Bomb-swapped shell, and EMP, smoke, stun, extinguish, toxic gas. Not yet: the Outer Rim sonic and plasma lanes, the modded damaging explosion, the unpatched-percent-0 control",
        "pawn_arc": "holder and in-between drawn position, landing on the planned cell with a land_on_pawn line naming the walker, stun end within landingStunMax, a haul job of the same stack after, the teleport control. Not yet: 'the stack it dropped at takeoff' (the flyer carries the stack: flyWithCarriedThing; a journal question)",
        "pit_goods_fetch": "the ladder is found by trying placements until FlowWorks reads it lowered (INVALID if none); 'the hauler used the ladder' is read as the hauler standing on a pit cell at a 30-tick sample",
        "hose_carry_drop": "the carrier is on a real RM_CarryHoseEnd job and the blast is fired when it has walked 4 cells; the takeoff cell is read from the reel 3 ticks after the blast",
        "closed_containers": "'slid one cell (action slide)' is read as moved exactly one cell away from the blast; the shipped code journals that move as action thrown (owner 2026-11-12, crates thrown whole), so the word is reported, not judged. Not yet: 'a drawn offset above zero in the thing trace' for a jolt: no thing trace exists and a jolt draws nothing (reported UNMEASURED)",
        "settings_sweep": "the game-side lanes only (the kernel-side lines are T_SETTINGS_SWEEP_OFFLINE) plus the Settings -> Kernel() read-back of 9 kernel fields and the saved-field equality. Lanes closedGuard and fireHalf answer INVALID: no such Mod Settings field (journal question 10; fire at half is a def-patch value). The heavy-knock lane reads the heavy_hit line, not the stagger length",
        "frame_probe_selfcheck": "the probe is a proof-build MonoBehaviour; its arithmetic is K-22 offline. Rows go to RM_FrameProbe_<stamp>.csv in the game's data folder",
        "barrage_perf": "the 40-cell cloud is a radius-3 seed (the seed's own cell count is printed, not asserted); the machine name is printed, not asserted (the bar says Archmagi); a full-list run is asserted as 60 or more active mods",
        "open_storage": "four open furniture defs, the guard's class read, no in_storage line. The floor control's cells are printed, not compared",
    }
    TICKS = {"no_cross_ordered": 2000, "pawn_arc": 900, "pit_goods_fetch": 60000}
    R = "python.exe src\\RimMandrake\\ExplosiveKnockback\\knockback_runner.py --scenes "
    CMD = {  # Stage 3 eleven bars (RIMMANDRAKE_BUILD_KNOCKBACK_STAGE_THREE_ELEVEN_BARS_UNRUN): each scene with its control lane
        "hose_carry_drop": R + "hose_carry_drop,hose_carry_drop_off --ticks 300   (proof build, minimal list + FlowWorks)",
        "closed_containers": R + "closed_containers,closed_containers_control --ticks 300   (proof build, minimal list + FlowWorks, LWM's Deep Storage, Jawa Armoury Rebalance and its 4 dependencies)",
        "settings_sweep": R + "settings_sweep," + ",".join("settings_sweep_" + l for l in ("throwAnimals", "throwMechanoids", "throwDowned", "throwItems", "throwCorpses", "landingStun", "doorsTakeDamage", "debugDrawVectors", "vanillaCratesClosed", "heavyGoodsMinMass", "heavyGoodsKnock", "flyingGoods", "shoveClosedContainers", "gasChain", "lightMassLimit20", "closedGuard", "fireHalf")) + ",settings_sweep_after --ticks 300   (proof build, minimal list + LWM's Deep Storage + the Cauldron and its 3 dependencies, dev mode)",
        "frame_probe_selfcheck": R + "frame_probe_selfcheck,frame_probe_selfcheck_paused --ticks 0 --real-seconds 8   (proof build, minimal list)",
        "barrage_perf": R + "frame_probe_selfcheck,barrage_perf_off,barrage_perf --ticks 0 --real-seconds 25   (proof build, the owner's full list on Archmagi)",
    }
    now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    for tid, t in OFF.items():
        t = dict(t, id=tid, kind="offline", command="python3 " + t["file"].split(" ")[0])
        if t.get("new"):
            t["runs_today"] = dict(ran=False, why="specified, not built: Stage 3 builds it failing first")
        else:
            t["runs_today"] = run(["python3", t["file"]]); t["runs_today"]["at"] = now
            t["runs_today"]["result"] = "PASS" if t["runs_today"]["rc"] == 0 else ("KNOWN RED " + t["known_red"] if t.get("known_red") else "FAIL")
        tests[tid] = t
    for sid, s in S.items():
        ep = s.get("entry_point", ""); f, _, meth = ep.partition("::")
        exists = (meth in names) if f.endswith("RM_KnockbackProof.cs") else (("def %s" % meth) in val)
        full = sid in FULL
        tests[sid] = dict(id=sid, kind="live_full" if full else "live_minimal", stage="6", file=f, entry=meth,
            observes=s.get("expect", "")[:240], reads=[f, C + "/scenes.json", MC, MATH],
            command=CMD[meth] if meth in CMD else ("python.exe src\\RimMandrake\\ExplosiveKnockback\\knockback_runner.py --scenes %s --ticks %d   (proof build, minimal list)" % (meth, TICKS.get(meth, 300))) if not full else "python.exe src\\RimMandrake\\ExplosiveKnockback\\validation.py --live %s   (full list)" % meth,
            why_game=WHY_GAME.get(sid, "UNSTATED"), why_full_list=FULL.get(sid), entry_exists=exists, partial=PARTIAL.get(meth) if exists else None, item=s.get("entry_point_item"),
            runs_today=dict(ran=False, why="live: this pilot is offline only; entry %s in the proof code" % ("EXISTS" if exists else "ABSENT")))
    for nm, bl in OLD.items():
        ex = nm in names
        tests["P_" + nm] = dict(id="P_" + nm, kind="live_minimal", stage="6", file=PROOF, entry=nm, observes="older proof scene (validation.py SCENES): see RM_KnockbackProof.Verdict(\"%s\")" % nm,
            reads=[PROOF, MC, MATH], command="python.exe src\\RimMandrake\\ExplosiveKnockback\\knockback_runner.py --scenes %s   (proof build)" % nm,
            why_game="older scene kept as support; the locked scenes.json scene decides", entry_exists=ex, support_only=True,
            runs_today=dict(ran=False, why="live: this pilot is offline only; entry %s in the proof code" % ("EXISTS" if ex else "ABSENT")))
        for b in bl: B[b][1].append("P_" + nm)
    tests["LOOK_STAGE8"] = dict(id="LOOK_STAGE8", kind="look", stage="8", file="(his walk)", observes="his walk of the flagship save: a bomb in a storeroom with people beside a pit", reads=[], runs_today=dict(ran=False, why="Stage 8"))
    bars = []
    src = [(l["id"], "tree.json", l.get("leaf_kind")) for l in tree["leaves"]] + [(i["id"], "record.json", "inventory") for i in rec["inventory"]]
    order = {"2": 2, "4-5": 4, "6": 6, "8": 8}
    for bid, where, kind in src:
        dec, sup = B[bid]
        held = [h for h in HELD if bid in h["bars"]]
        st = max((tests[t]["stage"] for t in dec), key=lambda x: order[x])
        def ok(t):
            r = tests[t]["runs_today"]; return r.get("ran") and r.get("rc") == 0
        def runnable(t):
            r = tests[t]["runs_today"]; return (r.get("ran")) or tests[t].get("entry_exists", False)
        bars.append(dict(id=bid, source=where, kind=kind, proves_at=st, decides=dec, supports=sup,
            held=[h["words"] for h in held],
            offline_decides=[t for t in dec if tests[t]["kind"] == "offline"],
            offline_green_today=all(ok(t) for t in dec if tests[t]["kind"] == "offline") and any(tests[t]["kind"] == "offline" for t in dec),
            every_decider_runnable_today=all(runnable(t) for t in dec if t != "LOOK_STAGE8"),
            any_test_runnable_today=any(runnable(t) for t in dec + sup if t != "LOOK_STAGE8")))
    corr = []
    for gid, where, needles, status in CORRECTIONS:
        txt = json.dumps([S[x] for x in where.split("|") if x in S]) if where in S or "|" in where else json.dumps(scenes)
        corr.append(dict(gap=gid, where=where, needles=needles, present=all(n in txt for n in needles), status=status))
    out = dict(mod="ExplosiveKnockback", version="0.1.0", made=now, made_by="rm-builder, Maturation pilot row 2 (throwaway make_test_table.py)",
        stages={"2": "preflight (a program)", "4-5": "blind offline challenge and game-logic testing", "6": "in-game acceptance", "8": "his live walk"},
        rule="a bar passes when every test in decides passes; proves_at is the highest stage among them; supports add evidence but decide nothing",
        settings_move="settings_scale_and_switch and inv_settings: the kernel-side lines are decided offline by T_SETTINGS_SWEEP_OFFLINE (specified, RIMMANDRAKE_SPLIT_KNOCKBACK_SWEEP_OFFLINE_TABLE_LIVE_WIRING); sc_settings_sweep keeps only the game-side wiring. The leaf's text is not edited.",
        held_statements=HELD, corrections=corr, tests=tests, bars=bars)
    json.dump(out, open(C + "/version/test_table.json", "w"), indent=1)
    # read view
    L = ["# Explosive Knockback 0.1.0: test-and-stage table", "", "Generated %s from `test_table.json` (the record; this is its read view). Stages: 2 preflight, 4-5 blind offline, 6 in-game, 8 his walk. A bar passes when every deciding test passes." % now, "",
         "## Counts (measured)", ""]
    n = len(bars)
    L += ["- bars: %d" % n,
          "- with at least one test runnable today (an offline test that ran, or an in-game scene whose entry exists in the proof code): %d" % sum(b["any_test_runnable_today"] for b in bars),
          "- with every deciding test runnable today: %d" % sum(b["every_decider_runnable_today"] for b in bars),
          "- with an offline deciding test, all green today: %d" % sum(b["offline_green_today"] for b in bars),
          "- decided offline only (no game needed): %d" % sum(b["proves_at"] in ("2", "4-5") for b in bars),
          "- in-game scenes: %d, entry exists %d, absent %d" % (sum(1 for t in tests.values() if t["kind"].startswith("live")), sum(1 for t in tests.values() if t.get("entry_exists")), sum(1 for t in tests.values() if t["kind"].startswith("live") and not t.get("entry_exists"))),
          "- offline tests: %d built (ran today: %d PASS, %d known red), %d specified for Stage 3" % (sum(1 for t in tests.values() if t["kind"] == "offline" and not t.get("new")), sum(1 for t in tests.values() if t["runs_today"].get("rc") == 0), sum(1 for t in tests.values() if t["runs_today"].get("ran") and t["runs_today"].get("rc") != 0), sum(1 for t in tests.values() if t.get("new"))), ""]
    L += ["## Bars", "", "| bar | from | proves at | decides | supports | runnable today |", "|---|---|---|---|---|---|"]
    for b in bars:
        L.append("| `%s` | %s | %s | %s | %s | %s |" % (b["id"], b["source"].split(".")[0], b["proves_at"], ", ".join(b["decides"]), ", ".join(b["supports"]) or "-", "all" if b["every_decider_runnable_today"] else ("some" if b["any_test_runnable_today"] else "none")))
    L += ["", "## Tests", "", "| test | stage | kind | file :: entry | runs today | observes |", "|---|---|---|---|---|---|"]
    for t in tests.values():
        r = t["runs_today"]; rt = ("%s rc=%s %ss" % (r.get("result", ""), r["rc"], r["seconds"])) if r.get("ran") else r["why"]
        L.append("| `%s` | %s | %s | `%s`%s | %s | %s |" % (t["id"], t["stage"], t["kind"], t["file"], (" :: " + t["entry"]) if t.get("entry") else "", rt, t["observes"][:160].replace("|", "/")))
    L += ["", "## Held look statements placed", ""] + ["- %s row %d, \"%s\" -> bars %s; test %s (stage %s, %s)" % (h["file"], h["row"], h["words"], ", ".join(h["bars"]), h["test"], h["stage"], h["kind"]) for h in HELD]
    L += ["", "## The six judge corrections (rm-coverage-judge-1794599960), checked against the current text", ""] + ["- %s (%s): text present %s; %s" % (c["gap"], c["where"], c["present"], c["status"]) for c in corr]
    L += ["", "## The settings sweep, moved offline", "", out["settings_move"], ""]
    open(C + "/version/test_table.md", "w").write("\n".join(L) + "\n")
    print("bars", n, "runnable-any", sum(b["any_test_runnable_today"] for b in bars), "runnable-all", sum(b["every_decider_runnable_today"] for b in bars), "offline-green", sum(b["offline_green_today"] for b in bars))
main()
