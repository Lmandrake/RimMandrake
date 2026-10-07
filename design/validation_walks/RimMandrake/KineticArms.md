# RimMandrake: Kinetic Arms — validation walk
subject: src/RimMandrake/KineticArms  (packageId `mandrake.rm.kineticarms`)
deps: Harmony, Explosive Knockback (hard); soft: FlowWorks (pits are where throws kill), Gimme Some Slack
list: modset_builder tier `explosiveknockback` plus `mandrake.rm.kineticarms`, all DLC, dev quicktest map
status-hint: first script, 2026-10-06

Sources: `design/RimMandrake/kinetic_blast_weapons_design_2026-10-06.md` (§3 range, §9 owner decisions, §10 build v1),
`About/About.xml`, `Source/RM_KineticMath.cs` (kernel; offline KA-01..KA-16 in `selftest_kineticarms_kernel.py`),
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
- Only pirate-gang raiders (Pirate and its children, incl. Blackstar Company and the Junkers) and the Hutt Cartel ever carry a looted kinetic weapon, at the settings chance (default 2% per armed pawn); grenadiers get thudders, others one they could afford (never the grav-ram); no other faction. → factions.pirates_only_rarely_carry_looted
- AI raiders use the weapons sensibly. → not_driven.ai_use (UNMEASURED: needs a live pirate raid)
- A palm thumper shove into a wall stops at the wall with zero impact and no wound (impactFactor 0: the arrest tool). → bolts.palm_shove_into_wall_hurts_nobody
- The grav-ram throws an animal of body size 2.5–3.5 (override 3.6); a repulsor bolt on the same kind does not (too_big). → bolts.grav_ram_moves_a_3_body_repulsor_cannot
- Ancient-danger temple loot (vanilla MapGen_AncientTempleContents) can hold one kinetic weapon, or 5–12 thump shells, at the setting's chance (35%, PROVISIONAL); a toggled-off weapon never appears; "found in ruins" off gives none (owner: found in Ancient Danger ruins). → ruins.ancient_temple_loot_holds_kinetic_weapons
- A generated temple actually holds the loot (kicker mine and pulse cannon minified). → not_driven.temple_generates_live (UNMEASURED: needs a shrine map)
- A kicker mine is hidden from raiders by default; with "hidden" off every raider knows it. → kicker.hidden_from_raiders_unless_setting_off
- A shield belt absorbs the throw (owner Q4). → Explosive Knockback guards.shield_belt_absorbs_throw_and_drains (EK owns throws)
- Every kinetic DamageDef carries the cord marker Gimme Some Slack reads, the "cut cords" setting removes it, and the thump cannon's Thump is not marked (owner Q3). → settings.kinetic_blasts_marked_to_spare_cords
- Kinetic blasts sway Gimme Some Slack cords instead of cutting them, live. → not_driven.cords_sway_live (UNMEASURED: needs a strung span; no visual sway exists, the span is simply not cut)
- Every Kinetic Arms blast draws the pale shock ring, and its texture resolves. → fx.kinetic_ring_fleck_texture_resolves

## the walk
1. [B] per scene: `jawa/static_call RM_KineticArmsProof.Stage "<scene>,x,z"`; `rimworld/step_game_ticks 300`; `.Verdict "<scene>"`   # every chain
2. [S] (human pass) a repulsor line reads as a moving wall; a kicker mine at a pit lip reads as an ejection gate; owner decides.

## criteria by level
Printed by `python3 src/RimMandrake/KineticArms/validation.py --criteria` (single source; this list mirrors it).
- KA.K L0: kernel selftest KA-01..KA-16 PASS — **passing 2026-10-06 (34/34)**
- KA.static L0: validation.py STATIC PASS (per-weapon impactFactor / body override, cord marker, every texPath has a PNG, ruins patch, every setting saved + reset + shown, GSS hook)
- KA.mock L0: validation.py --mock stages every scene
- KA.load L1: explosiveknockback tier + kineticarms loads, no red error; fleck and ruins maker resolve — owed
- KA.scenes18 L2: the 18 v1 scenes still PASS on the rebuilt DLLs — owed
- KA.new6 L2: palm_arrest_wall, gravram_big_body, ruins_loot, kicker_hidden, cords_marker, ring_fleck PASS — owed
- KA.cords L2: with Gimme Some Slack, a repulsor blast under a span leaves it whole; a frag cuts it — owed
- KA.temple L2: a debug-generated ancient temple (chance 100) holds one kinetic weapon or a minified mine/cannon — owed
- KA.shield L2: a repulsor hit on a shield-belted raider: not thrown, belt drained — owed
- KA.feel L4: owner — a repulsor line reads as a moving wall; a kicker mine at a pit lip as an ejection gate — owed

## north star
state: DRAFT
validated-hash:

No owner north-star bars are drafted for this mod yet.

## anti-guessing notes
RULED OUT: "ruins placement belongs in the Utinni layer" (design §10's first wording) — Ancient Dangers and MapGen_AncientTempleContents are vanilla, and an RM mod must stand alone (Q11a); the campaign's ancients are already Rakata by its own patch, so the RM option is the Rakatan source with no second patch.
RULED OUT: "toggle a weapon off by clearing its thingSetMakerTags" for ruins — a ThingFilter resolves its tag list once at load, so RM_ThingSetMaker_KineticRuins picks among enabled weapons at generate time instead.
RULED OUT: "Gimme Some Slack can test for Kinetic Arms' marker by type" — it cannot reference that assembly, and an XML extension whose Class is missing discards the whole def, so GSS matches the extension's class NAME.
RULED OUT: "harmsHealth false makes a blast woundless" — DamageWorker_AddInjury injures pawns regardless; harmsHealth gates only HitPoints things. The Repulse family uses RM_DamageWorker_KineticOnly instead.
RULED OUT: "affectedAngle gives the cone" — DamageWorker.ExplosionCellsToHit skips every cell within 0.5 of the centre when affectedAngle is set, so the directly hit pawn would get nothing; Kinetic Arms passes its own overrideCells.
RULED OUT: "a ParentName=\"Bomb\" damage def is safe" — Explosive Knockback patches an extension onto Bomb, which a child would inherit beside its own; the families use their own abstract bases.
