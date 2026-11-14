# RimMandrake: Explosive Knockback — validation walk
subject: src/RimMandrake/ExplosiveKnockback  (packageId `mandrake.rm.explosiveknockback`)
deps: Harmony; soft: FlowWorks (pit scenes; `blastsBreakPitCovers` is FlowWorks' setting), Gimme Some Slack (hose drop)
list: modset_builder tier `explosiveknockback` (bridge + FlowWorks + Gimme Some Slack + this mod, all DLC), dev quicktest map
status-hint: first script, 2026-10-06

Sources: `design/RimMandrake/explosive_knockback_design_2026-10-06.md` (§3, §5, §8, §11 owner rulings), `About/About.xml`,
`Source/RM_KnockbackMath.cs` (kernel; offline K-01..K-20 in `selftest_explosiveknockback_kernel.py`), `Source/RM_KnockbackProof.cs` (scenes).

## must be true
- A Bomb blast (mortar, r 2.9) one cell from a human throws them 3 cells straight away from the centre, alive (owner Q7). → throw.mortar_beside_human_throws_3_cells
- A wall behind the pawn stops the throw on the cell before it, with impact damage. → throw.wall_stops_throw_with_impact
- A closed door stops the throw like a wall and takes a hit. → throw.closed_door_stops_throw_and_takes_a_hit
- Pawns are thrown over sandbags and barricades (owner Q3). → throw.thrown_over_sandbags
- A living creature heavier than the creature mass limit (150 kg, the game's Mass stat less carried inventory; owner card 2026-11-13) is not thrown: a bantha (240 kg) journals too_heavy_creature. → throw.creature_over_mass_limit_is_not_thrown
- EMP (and every zero-force blast) throws nothing and enqueues nothing. → throw.emp_blast_throws_nothing
- Light items are thrown by the same kernel (lighter flies farther, stack intact); an item over 75 kg stays (owner Q4). → light_things.items_thrown_by_mass_heavy_stays
- An item on an open shelf scatters; an item in a closed container stays. → light_things.item_on_an_open_shelf_scatters
- A pawn the blast kills is thrown as a corpse. → light_things.pawn_killed_by_blast_thrown_as_corpse
- Thrown goods truly fly (RIMMANDRAKE_FLY_KNOCKBACK_GOODS_WILD): mid-flight the stack is inside a carrier, count intact. → flying_goods.stack_inside_carrier_mid_flight
- A flown stack lands on the cell the instant move would choose, count intact, no carrier left. → flying_goods.lands_on_the_instant_cell_count_intact
- A flight cut short by a wall (rebound off) lands beside it and takes today's wall impact there. → flying_goods.wall_cut_short_applies_impact
- With rebound on, a cut-short flight bounces back with about 70% of the cells it had left; the impact applies at the bounce. → flying_goods.rebound_off_wall_at_keep_percent
- flyingGoods off is today's instant move (no carrier). → flying_goods.off_is_the_instant_move
- A closed container (a stasis locker, a sealed crate) that survives the blast is thrown whole, shorter than the same goods loose, its goods still in it and unhurt by the blast (owner 2026-11-12). → light_things.closed_container_thrown_whole_contents_inside_unhurt
- A flying stack of 10 kg or more that reaches a person hits them lightly, staggers them and drops there; a light stack flies past. → flying_goods.heavy_stack_hits_and_stops_light_passes
- A thrown stack never shoves a stack already lying where it lands (a stackLimit-1 thing into a full cell lands beside it). → flying_goods.landing_never_shoves_a_resident
- The same in a pit: a good already on the pit floor stays there when a thrown thing lands on its cell. → pits.landing_in_a_pit_never_shoves_a_resident_out
- Burning flammable gas (the Cauldron's vent gas) goes off clump by clump: a burst per burning cell over several ticks, goods at most 2 cells, people shoved 1 cell with no shove damage and at most once per 2 s, no pit cover damaged. → gas.burning_gas_bursts_clump_by_clump_no_damage
- Fire and incendiary blasts throw at half a Bomb's force (owner card 2026-11-11). → throw.fire_and_incendiary_throw_at_half
- A damaging explosion this mod does not patch throws at full force by default (owner card 2026-11-11). → throw.unpatched_harmful_blast_throws_at_full
- A save taken mid-flight reloads with the carrier and its stack, which then lands intact. → not_driven.save_mid_flight_keeps_the_stack (proof/goods_flight_saveload.py)
- A colonist thrown into an open pit lands on its floor and FlowWorks records exactly one descent. → pits.colonist_thrown_into_open_pit_falls
- An enemy thrown into an open pit lands on its floor and falls (one descent). → pits.enemy_thrown_into_open_pit_falls
- Nothing is thrown across a pit: a throw stops IN the first open pit cell. → pits.throw_stops_inside_a_1_wide_pit
- A pawn already in a pit is never thrown (you can't climb out). → pits.pawn_already_in_pit_not_thrown
- A corpse thrown toward a pit lies on the pit floor (owner Q10). → pits.corpse_thrown_onto_pit_floor
- A damaging blast that reaches a pit cover breaks the whole deck and anyone on it falls (owner Q5/Q9, FlowWorks). → pits.blast_breaks_cover_and_pawn_on_it_falls
- No cap (owner 2026-11-12, "No caps please."): a 5.9 blast over 10 people and 80 stacks throws every one it reaches, all item throws in the one tick the wave lands (over the old 40 and 60 caps). → caps.no_cap_every_throw_in_one_tick
- Master switch off: the blast still damages, nothing moves. → settings.master_off_nothing_moves_but_wave_hit
- A projectile ThingDef's own knockback extension beats its DamageDef's, and the request journal names the source (design §2.1 lookup: projectile → weapon → DamageDef → unpatched). → config.projectile_extension_wins_over_damagedef
- An explicit force 0 on the projectile wins over a DamageDef that throws: nothing is requested. → config.explicit_zero_on_projectile_throws_nothing
- A blast with impactFactor 0 stops at a wall with zero impact damage. → config.impact_factor_zero_no_wall_impact
- A blast with creatureMassLimitOverride 216 (the grav-ram's) throws a 150–216 kg animal (a dewback, 180); a plain Bomb beside the same kind does not (too_heavy_creature). → config.mass_override_throws_a_dewback_global_does_not
- Heavier flies less, and a bigger blast throws farther (owner cards 2026-11-13, sc_mass_and_power): one Bomb r 2.9 at damage 50 one cell from a scurrier (12 kg), a colonist (45-76 kg), a gelagrub (144) and a bantha (240) throws 5 / 3 / 2 / spared. → mass_power.heavier_flies_less_scurrier_colonist_gelagrub_bantha_spared
- The same blast at damage 100 throws 6 (the cap) / 5 / 4 / spared, damage ratio 2.0. → mass_power.double_damage_throws_each_creature_farther
- With "Bigger blasts throw harder" off, damage 50 throws 5 / 3 / 2 / spared. → mass_power.power_off_damage_50_throws_as_before
- With it off, damage 100 throws the same as damage 50 (ratio 1.0). → mass_power.power_off_damage_100_throws_as_damage_50
- With the creature mass limit at 250 kg, damage 50 throws the bantha 1 cell. → mass_power.limit_250_throws_the_bantha_1_cell
- With the limit at 250 kg, damage 100 throws the bantha 3 cells. → mass_power.limit_250_double_damage_throws_the_bantha_3_cells
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
- EK.K L0: kernel selftest K-01..K-20 PASS
- EK.mass L0: kernel K-18..K-20 PASS (creature mass limit, blast power)
- EK.massLive L2: the six mass_and_power scenes PASS — owed (the owner looks at them in a sitting)
- EK.static L0: validation.py STATIC PASS (config lookup order, shield/landing hooks, every setting saved + reset + shown, walk coverage)
- EK.mock L0: validation.py --mock stages every scene
- EK.load L1: explosiveknockback tier loads with no red error from this mod; Harmony patches applied — owed
- EK.scenes18 L2: the 18 v1 scenes still PASS after the 2026-10-06 change — owed
- EK.config L2: lookup_projectile, lookup_zero_wins, impact_factor, body_override PASS — owed
- EK.guards L2: immunity_window, shield_counter PASS — owed
- EK.reload L2: recovery-window stamps survive save/reload — owed, no scene yet
- EK.feel L4: owner watches a blast and a shield belt — owed

## north star
state: VALIDATED
validated-hash: 5d06c98d8b13c2ef219df6639d4164548ccf3cc25eadeb675a172c558a492585
validated-by: BY CARD: Approve the 16 Explosive Knockback north-star bars (14 must-show, 2 cannot-show)? -> Approve as written (Thu 2026-11-12 ~00:0x PST)

Drafted 2026-11-11 by the Designer from the root he approved by card ("Approve as written",
OWNER:1794468835221748501) and his card answers that night (record.json `d_c_*`). Each line is
one thing a player can watch in ordinary play. DRAFT until he validates these lines.

### must show

**People**
- [ ] `ek_blast_throws_people` — a mortar shell landing beside a colonist throws them about three
      cells straight away from it, clean over sandbags, and they land alive and briefly stunned.
- [ ] `ek_wall_stops_hard` — a person thrown into a wall stops dead at it and takes an impact
      hit; people never rebound.
- [ ] `ek_shield_belt_holds` — a shield belt that absorbs the blast keeps its wearer in place
      and loses extra charge for it.

**Goods**
- [ ] `ek_goods_fly_wild` — loose goods and corpses near a blast visibly fly: they arc through
      the air, spin fast and rebound off walls, losing speed each time, before they come to rest.
- [ ] `ek_every_good_flies` — every loose good the blast reaches moves; no stack sits still in
      the blast while its neighbours fly.
- [ ] `ek_open_storage_no_cover` — goods on open shelves, racks and tables scatter like goods on
      the floor.
- [ ] `ek_closed_container_holds` — goods inside a closed container (a crate, locker, fridge or
      deep storage) stay inside it; the container itself may shift a little.
- [ ] `ek_heavy_goods_knock` — a heavy flying stack that strikes a person gives a light knock and
      a stagger; light goods fly past.

**Which blasts**
- [ ] `ek_every_harmful_blast_throws` — grenades, mortars and other bombs throw at full strength,
      fire and incendiary blasts at about half, and other mods' damaging explosions throw too;
      EMP, smoke and other harmless bursts throw nothing.

**Gas**
- [ ] `ek_gas_clump_by_clump` — when a flammable gas cloud catches, it goes off clump by clump as
      the fire runs through it; each small burst scatters the goods near it and shoves people
      one cell without hurting them.
- [ ] `ek_our_gases_burn` — the Cauldron's gas, and our other gases that ought to burn, catch and
      go off clump by clump.

**Pits**
- [ ] `ek_blast_breaks_pit_cover` — a damaging or fire blast over a covered pit breaks its cover
      and whoever stands on it falls in; a gas burst never breaks a cover.
- [ ] `ek_thrown_into_pit_falls` — a person or a good thrown into a pit falls to its floor, and a
      colonist can fetch goods back out of it.

**Cost**
- [ ] `ek_barrage_stays_smooth` — a mortar barrage into a full stockpile, and a long gas chain,
      stay smooth to watch at normal speed.

### cannot show
- [ ] `ek_goods_teleport` — goods vanishing from one cell and reappearing on another under a puff
      of dust.
- [ ] `ek_careless_fall` — a colonist walking into a pit by ordinary pathing; only a blast or
      another force puts anyone in.

## anti-guessing notes
RULED OUT: "a shield that is still active after the blast absorbed it" — vanilla CompShield.PostPreApplyDamage sets absorbed=true even when the hit breaks the shield, so absorption is captured AT DAMAGE TIME (postfix on PostPreApplyDamage while our ExplosionDamageThing prefix watches that pawn), never read afterwards.
RULED OUT: "CompShield.PawnOwner identifies the wearer" — it is protected in 1.6; TakeDamage(t) reaches only t's own shields, so the watch on t is enough.
RULED OUT: "per-weapon tuning needs a DamageDef per weapon" — Explosion carries `projectile` and `weapon` ThingDefs (decompiled 1.6), so an extension on the projectile is read first; Kinetic Arms still tunes on its per-weapon DamageDefs, which is the third lookup step and equally valid.
RULED OUT: "a 60 kg reference mass gives the owner's 3 cells" — a clothed colonist weighs ~65-70 kg (worn gear counts), which rounded to 2; refMass is 70 (K-01 pins 60, 68 -> 3 and 90 -> 2).
RULED OUT: "sandbag cells are standable, so a pawn may land on one" — vanilla Sandbags are PassThroughOnly (walkable, not standable); the kernel backs any throw off a Partial cell (K-06).
RULED OUT: "a postfix on ExplosionDamageThing can tell an already-hit thing" — the base adds the thing to damagedThings before its ignoredThings check, so eligibility is read in a PREFIX (GPT #2).
RULED OUT: "the flyer lands where we aimed" — vanilla PawnFlyer.CheckDestination re-targets any invalid destCell within 3.9 cells every 15 ticks; skipped for RM_PawnFlyer_Knockback only.
