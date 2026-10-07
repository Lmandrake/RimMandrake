# RimMandrake: Explosive Knockback — validation walk
subject: src/RimMandrake/ExplosiveKnockback  (packageId `mandrake.rm.explosiveknockback`)
deps: Harmony; soft: FlowWorks (pit scenes; `blastsBreakPitCovers` is FlowWorks' setting), Gimme Some Slack (hose drop)
list: modset_builder tier `explosiveknockback` (bridge + FlowWorks + Gimme Some Slack + this mod, all DLC), dev quicktest map
status-hint: first script, 2026-10-06

Sources: `design/RimMandrake/explosive_knockback_design_2026-10-06.md` (§3, §5, §8, §11 owner rulings), `About/About.xml`,
`Source/RM_KnockbackMath.cs` (kernel; offline K-01..K-12 in `selftest_explosiveknockback_kernel.py`), `Source/RM_KnockbackProof.cs` (scenes).

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

## north star
state: DRAFT
validated-hash:

No owner north-star bars are drafted for this mod yet.

## anti-guessing notes
RULED OUT: "a 60 kg reference mass gives the owner's 3 cells" — a clothed colonist weighs ~65-70 kg (worn gear counts), which rounded to 2; refMass is 70 (K-01 pins 60, 68 -> 3 and 90 -> 2).
RULED OUT: "sandbag cells are standable, so a pawn may land on one" — vanilla Sandbags are PassThroughOnly (walkable, not standable); the kernel backs any throw off a Partial cell (K-06).
RULED OUT: "a postfix on ExplosionDamageThing can tell an already-hit thing" — the base adds the thing to damagedThings before its ignoredThings check, so eligibility is read in a PREFIX (GPT #2).
RULED OUT: "the flyer lands where we aimed" — vanilla PawnFlyer.CheckDestination re-targets any invalid destCell within 3.9 cells every 15 ticks; skipped for RM_PawnFlyer_Knockback only.
