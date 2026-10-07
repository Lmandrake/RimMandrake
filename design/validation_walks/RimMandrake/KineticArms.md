# RimMandrake: Kinetic Arms — validation walk
subject: src/RimMandrake/KineticArms  (packageId `mandrake.rm.kineticarms`)
deps: Harmony, Explosive Knockback (hard); soft: FlowWorks (pits are where throws kill), Gimme Some Slack
list: modset_builder tier `explosiveknockback` plus `mandrake.rm.kineticarms`, all DLC, dev quicktest map
status-hint: first script, 2026-10-06

Sources: `design/RimMandrake/kinetic_blast_weapons_design_2026-10-06.md` (§3 range, §9 owner decisions, §10 build v1),
`About/About.xml`, `Source/RM_KineticMath.cs` (kernel; offline KA-01..KA-13 in `selftest_kineticarms_kernel.py`),
`Source/RM_KineticArmsProof.cs` (scenes; each fires the REAL projectile via Projectile.Launch, or the mine's own Kick()).

## must be true
- A thump cannon bomb one cell from a human throws them at least 4 cells away (force 2.5: 5 expected, mortar 3) (owner Q1). → thump.thump_bomb_beside_human_throws_farther_than_mortar
- With "Thump cannons throw farther" off, the thump bomb throws nothing (vanilla). → thump.thump_off_throws_nothing
- A thudder grenade in a 4-raider cluster throws at least 3 of them 3+ cells and kills none. → grenades.thudder_clears_a_cluster_without_killing
- A palm thumper hit shoves the target 2+ cells straight away from the shooter with no wound, and leaves a pawn beside the shooter's side untouched. → bolts.palm_shove_along_shot_no_wound
- A slam charge beside a human throws them 3+ cells. → grenades.slam_charge_throws
- A repulsor bolt shoves its target 3+ cells along the shot, unwounded. → bolts.repulsor_pushes_along_shot
- The same holds for a shot fired due west (the ±180 degree wrap). → bolts.repulsor_westward_wraps
- A grav-ram pulse shoves its target 5+ cells along the shot. → bolts.grav_ram_throws_hardest
- A thump shell beside a human throws them 3+ cells. → grenades.thump_shell_throws
- A kicker mine launches the pawn on it 3+ cells in its facing, for each of the four facings, and spends one kick of chemfuel. → kicker.kicks_north, kicker.kicks_east, kicker.kicks_south, kicker.kicks_west
- An empty kicker mine is a dud; refuelled it kicks again and is still there. → kicker.dud_when_empty_rearms_with_fuel
- A pulse wave shoves its target 3+ cells away from the cannon. → pulse.pulse_wave_pushes_away_from_turret
- A pulse cannon with no stored charge picks no target; charged, it does (owner Q6). → pulse.no_charge_no_target
- Kinetic throw strength 0: a repulsor hit throws nothing. → settings.strength_zero_throws_nothing
- A pawn walking onto an armed kicker mine springs it (vanilla trap rules, enemies only). → not_driven.walk_on_spring (UNMEASURED: needs pathing onto the plate)
- Only pirate-gang raiders (Pirate and its children) ever carry a looted kinetic weapon, at the settings chance (default 2% per armed pawn); grenadiers get thudders, others one they could afford; no other faction. → factions.pirates_only_rarely_carry_looted
- AI raiders use the weapons sensibly. → not_driven.ai_use (UNMEASURED: needs a live pirate raid)
- A shield belt absorbs the throw (owner Q4). → UNCOVERED: owed to Explosive Knockback (FOUNDRY), not built
- Kinetic blasts sway Gimme Some Slack cords instead of cutting them (owner Q3). → UNCOVERED: owed to Gimme Some Slack, not built

## the walk
1. [B] per scene: `jawa/static_call RM_KineticArmsProof.Stage "<scene>,x,z"`; `rimworld/step_game_ticks 300`; `.Verdict "<scene>"`   # every chain
2. [S] (human pass) a repulsor line reads as a moving wall; a kicker mine at a pit lip reads as an ejection gate; owner decides.

## north star
state: DRAFT
validated-hash:

No owner north-star bars are drafted for this mod yet.

## anti-guessing notes
RULED OUT: "harmsHealth false makes a blast woundless" — DamageWorker_AddInjury injures pawns regardless; harmsHealth gates only HitPoints things. The Repulse family uses RM_DamageWorker_KineticOnly instead.
RULED OUT: "affectedAngle gives the cone" — DamageWorker.ExplosionCellsToHit skips every cell within 0.5 of the centre when affectedAngle is set, so the directly hit pawn would get nothing; Kinetic Arms passes its own overrideCells.
RULED OUT: "a ParentName=\"Bomb\" damage def is safe" — Explosive Knockback patches an extension onto Bomb, which a child would inherit beside its own; the families use their own abstract bases.
