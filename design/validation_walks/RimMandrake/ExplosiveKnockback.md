# RimMandrake: Explosive Knockback — validation walk
subject: src/RimMandrake/ExplosiveKnockback  (packageId `mandrake.rm.explosiveknockback`)
deps: Harmony; soft: FlowWorks (pit scenes; `blastsBreakPitCovers` is FlowWorks' setting), Gimme Some Slack (hose drop)
list: modset_builder tier `explosiveknockback` (bridge + FlowWorks + Gimme Some Slack + this mod, all DLC), dev quicktest map
status-hint: first script, 2026-10-06

Sources: `design/RimMandrake/explosive_knockback_design_2026-10-06.md` (§3, §5, §8, §11 owner rulings), `About/About.xml`,
`Source/RM_KnockbackMath.cs` (kernel; offline K-01..K-16 in `selftest_explosiveknockback_kernel.py`), `Source/RM_KnockbackProof.cs` (scenes).

## must be true
- A Bomb blast (mortar, r 2.9) one cell from a human throws them 3 cells straight away from the centre, alive (owner Q7). → throw.mortar_beside_human_throws_3_cells
- A wall behind the pawn stops the throw on the cell before it, with impact damage. → throw.wall_stops_throw_with_impact
- A closed door stops the throw like a wall and takes a hit. → throw.closed_door_stops_throw_and_takes_a_hit
- Pawns are thrown over sandbags and barricades (owner Q3). → throw.thrown_over_sandbags
- A pawn of body size >= 2.5 is not thrown. → throw.body_size_2_5_is_not_thrown
- EMP (and every zero-force blast) throws nothing and enqueues nothing. → throw.emp_blast_throws_nothing
- Light items are thrown by the same kernel (lighter flies farther, stack intact); an item over 75 kg stays (owner Q4). → light_things.items_thrown_by_mass_heavy_stays
- An item on a shelf stays in the shelf. → light_things.item_on_a_shelf_stays
- A pawn the blast kills is thrown as a corpse. → light_things.pawn_killed_by_blast_thrown_as_corpse
- A colonist thrown into an open pit lands on its floor and FlowWorks records exactly one descent. → pits.colonist_thrown_into_open_pit_falls
- An enemy thrown into an open pit lands on its floor and falls (one descent). → pits.enemy_thrown_into_open_pit_falls
- Nothing is thrown across a pit: a throw stops IN the first open pit cell. → pits.throw_stops_inside_a_1_wide_pit
- A pawn already in a pit is never thrown (you can't climb out). → pits.pawn_already_in_pit_not_thrown
- A corpse thrown toward a pit lies on the pit floor (owner Q10). → pits.corpse_thrown_onto_pit_floor
- A damaging blast that reaches a pit cover breaks the whole deck and anyone on it falls (owner Q5/Q9, FlowWorks). → pits.blast_breaks_cover_and_pawn_on_it_falls
- One explosion throws at most `maxThrowsPerExplosion` things, pawns first. → caps.per_explosion_cap_holds_pawns_first
- At most `maxItemThrowsPerMapTick` items move per tick; the overflow is dropped. → caps.per_tick_item_cap_drops_overflow
- Master switch off: the blast still damages, nothing moves. → settings.master_off_nothing_moves_but_wave_hit
- A projectile ThingDef's own knockback extension beats its DamageDef's, and the request journal names the source (design §2.1 lookup: projectile → weapon → DamageDef → unpatched). → config.projectile_extension_wins_over_damagedef
- An explicit force 0 on the projectile wins over a DamageDef that throws: nothing is requested. → config.explicit_zero_on_projectile_throws_nothing
- A blast with impactFactor 0 stops at a wall with zero impact damage. → config.impact_factor_zero_no_wall_impact
- A blast with immuneBodySizeOverride 3.6 throws a 2.5–3.5 body; a plain Bomb beside the same kind does not (too_big). → config.body_override_throws_a_3_body_global_does_not
- A pawn thrown once cannot be thrown again until its landing stun ends plus the recovery window: a second blast inside it journals "immune" and does not move it. → guards.second_blast_in_recovery_window_is_immune
- A shield belt that absorbs a blast absorbs the throw: the wearer does not move, and the belt loses extra charge (owner Q4). → guards.shield_belt_absorbs_throw_and_drains
- The recovery-window stamps survive a save/reload. → not_driven.immunity_survives_reload (UNMEASURED: save/load)
- A colonist carrying a hose end drops it where they stood (owner Q6). → not_driven.hose_carry_drops_at_takeoff (UNMEASURED: no carry scene yet)
- A flyer saved mid-air reloads with the pawn existing once. → not_driven.save_mid_flight (UNMEASURED: save/load)
- Raiders resume their lord's duty after landing. → not_driven.raid_lord_resumes_duty (UNMEASURED: raid site)
- Results are the same with VEF active (it patches PawnFlyer). → not_driven.vef_active_same_results (UNMEASURED: VEF tier)
- A barrage costs little per tick. → not_driven.barrage_perf_ms_per_tick (UNMEASURED: performance is not a Boolean check)
- Items/corpses on a pit floor can be hauled out by colonists (owner Q10 "stay retrievable"). → UNCOVERED: FlowWorks routes non-held pawns around open pit cells (RM_PitPathing), so a hauler reaches the floor only down a ladder; needs a ladder-haul scene

## the walk
1. [B] per scene: `jawa/static_call RM_KnockbackProof.Stage "<scene>,x,z"`; `rimworld/step_game_ticks 300`; `.Verdict "<scene>"`   # every chain
2. [B] `knockback_runner.py` runs all scenes in one go and copies the journal to `Transient/explosive_knockback/`
X. [S] (human pass) a blast reads as a blast: bodies fly, loot scatters, a cover caves in; owner decides.

## criteria by level
Printed by `python3 src/RimMandrake/ExplosiveKnockback/validation.py --criteria` (single source; this list mirrors it).
- EK.K L0: kernel selftest K-01..K-16 PASS — **passing 2026-10-06 (88/88)**
- EK.static L0: validation.py STATIC PASS (config lookup order, shield/landing hooks, every setting saved + reset + shown, walk coverage)
- EK.mock L0: validation.py --mock stages every scene
- EK.load L1: explosiveknockback tier loads with no red error from this mod; Harmony patches applied — owed
- EK.scenes18 L2: the 18 v1 scenes still PASS after the 2026-10-06 change — owed
- EK.config L2: lookup_projectile, lookup_zero_wins, impact_factor, body_override PASS — owed
- EK.guards L2: immunity_window, shield_counter PASS — owed
- EK.reload L2: recovery-window stamps survive save/reload — owed, no scene yet
- EK.feel L4: owner watches a blast and a shield belt — owed

## north star
state: DRAFT
validated-hash:

No owner north-star bars are drafted for this mod yet.

## anti-guessing notes
RULED OUT: "a shield that is still active after the blast absorbed it" — vanilla CompShield.PostPreApplyDamage sets absorbed=true even when the hit breaks the shield, so absorption is captured AT DAMAGE TIME (postfix on PostPreApplyDamage while our ExplosionDamageThing prefix watches that pawn), never read afterwards.
RULED OUT: "CompShield.PawnOwner identifies the wearer" — it is protected in 1.6; TakeDamage(t) reaches only t's own shields, so the watch on t is enough.
RULED OUT: "per-weapon tuning needs a DamageDef per weapon" — Explosion carries `projectile` and `weapon` ThingDefs (decompiled 1.6), so an extension on the projectile is read first; Kinetic Arms still tunes on its per-weapon DamageDefs, which is the third lookup step and equally valid.
RULED OUT: "a 60 kg reference mass gives the owner's 3 cells" — a clothed colonist weighs ~65-70 kg (worn gear counts), which rounded to 2; refMass is 70 (K-01 pins 60, 68 -> 3 and 90 -> 2).
RULED OUT: "sandbag cells are standable, so a pawn may land on one" — vanilla Sandbags are PassThroughOnly (walkable, not standable); the kernel backs any throw off a Partial cell (K-06).
RULED OUT: "a postfix on ExplosionDamageThing can tell an already-hit thing" — the base adds the thing to damagedThings before its ignoredThings check, so eligibility is read in a PREFIX (GPT #2).
RULED OUT: "the flyer lands where we aimed" — vanilla PawnFlyer.CheckDestination re-targets any invalid destCell within 3.9 cells every 15 ticks; skipped for RM_PawnFlyer_Knockback only.
