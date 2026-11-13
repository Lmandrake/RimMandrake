# Explosive Knockback: plan (stage 3)

Tree `design/concepts/ExplosiveKnockback/tree.json`, sheet `sheet.md`, scenes `scenes.json`, floor `floor.json`,
record `record.json`. The throw of people, the pit side and the proof scenes are built; this plan is what his card
answers of 2026-11-11 (record `d_c_*`, OWNER:1794468835221748501 .. 1794468874358971350) change, and the proofs owed.
Each step is one rimflow item, built by Relentless from the tree; none needs worldgen and none live-tests a flyer.

## Owed builds

1. **Goods truly fly, wild tuning** (`RIMMANDRAKE_FLY_KNOCKBACK_GOODS_WILD`; d_c_wild, d_c_all_fly). Replace the
   despawn and re-place hop at `src/RimMandrake/ExplosiveKnockback/Source/RM_MapComponent_Knockback.cs` (about line
   474) with a thrown-thing carrier that draws each good and corpse along an arc, spinning fast, rebounding off walls
   keeping about 70 percent per bounce until spent; throws about 1.6x the person kernel's distance; each good's request line logs its kernel and wild cells. Remove the
   per-tick overflow drop (`maxItemThrowsPerMapTick`) and the 40-throw per-explosion cap (`maxThrowsPerExplosion`):
   his "All of them fly" (d_c_all_fly) leaves no cap, and frame time is a proven bar (item 6), not a limit; every
   light good the wave reaches with a throw of a cell or more flies (scene `sc_all_fly_no_cap`, a 5.9-radius blast reaching
   over 60 in one tick, with a test hook re-imposing the old cap as its control; inventory `inv_caps` scoped out; the
   mass limit and the rim too_weak skip stay, `inv_mass_limit_skip`, `inv_too_weak_skip`). The carrier survives a
   save mid-air (one thing, never two). Walk row `caps.per_tick_item_cap_drops_overflow` flips. Leaves
   `goods_arc_spin_rebound`, `every_good_moves`, `no_teleport`; scene `sc_storeroom_mortar`.
2. **Closed containers only, plus the shove** (`RIMMANDRAKE_LIMIT_KNOCKBACK_STORAGE_CLOSED`; d_c_closed_containers,
   dl_closed_means_hidden, dl_container_shove). The in_storage skip (about line 399) becomes a closed-container
   guard: storage that does not draw its contents, plus an opt-in tag. A 1x1 container under the mass limit slides
   one cell when the cell behind is free, else jolts; never into a pit, a wall or onto a pawn; each held container logs one journal container line, action slide or jolt. Walk row
   `light_things.item_on_a_shelf_stays` (which still states the old rule) is rewritten in
   design/validation_walks/RimMandrake/ExplosiveKnockback.md's must-be-true list, outside its validated north-star
   section, to "an item on an open shelf scatters; an item in a closed container stays". Leaves `open_shelf_scatters`, `closed_container_holds`.
3. **All harmful explosions** (`RIMMANDRAKE_THROW_ALL_HARMFUL_BLASTS`; d_c_which_blasts, dl_modded_strength).
   `Patches/RM_Knockback_DamageDefs.xml`: Flame and incendiary at 0.5; the other-mods default goes from 0 to 100
   percent for any damaging explosion; EMP, smoke, stun, extinguish and toxic gas stay 0. Leaf
   `every_harmful_blast_throws`.
4. **The gas chain** (`RIMMANDRAKE_CHAIN_FLAMMABLE_GAS_CLUMPS`; d_gas_per_clump, d_c_gas_shove, d_c_gas_source,
   dl_gas_census, dl_clump_strength, dl_gas_ignores_belts). An opt-in flammable-gas DefModExtension, put on our
   fitting gases by census (TheForge, the Scarlands bileworm, EnvironmentalHazards, and the Cauldron's, by his
   words). When fire reaches a tagged clump, a small burst per clump cell, radius 1.9, goods at most 2 cells,
   people shoved one cell with no damage at most once per 2 s, never a pit cover broken. This mod adds no gas of
   its own. Leaves `gas_goes_clump_by_clump`, `our_gases_burn`; the gas half of `blast_breaks_pit_cover`.
5. **Heavy-stack light knock** (`RIMMANDRAKE_KNOCK_PEOPLE_HEAVY_GOODS`; d_c_heavy_knock, dl_heavy_threshold). In
   the carrier: a stack of 10 kg or more reaching a pawn's cell deals 2 to 5 blunt and about 0.5 s stagger, then
   stops there; lighter goods pass. A setting. Leaf `heavy_stack_knocks`. Needs build 1.

5a. **Creature mass limit and blast power from damage** (`RIMMANDRAKE_BUILD_KNOCKBACK_CREATURE_MASS_AND_BLAST_POWER`;
   d_mass_limit, d_type_x_damage, d_mass_power_scene, dl_mass_power_defaults). `RM_KnockbackMath.cs`: drop
   `immuneBodySize`, add `creatureMassLimit` (150 kg, weighs living pawns only; corpses by the 75 kg goods limit
   alone); `ThrowCells` multiplies by this explosion's damage over its type's `defaultDamage` (per-type `refDamage`
   override) when `blastPowerFromDamage` is on. `RM_KnockbackExtension.immuneBodySizeOverride` becomes
   `creatureMassLimitOverride` (the grav-ram's 3.6 becomes 216 kg in KineticArms). Settings page, Scribe keys, reset,
   fuzz selftest and About.xml follow. Skip reason `too_heavy_creature`. Proof entry point `mass_and_power` (scene
   `sc_mass_and_power`, showcase 2). Leaves `heavier_flies_less`, `the_spared`, `per_weapon_tuning`. Every default
   and the measured masses and damages: `D:\ClaudeWork\rimmandrake\conductor\ek_mass_20261113\DEFAULTS.md` and
   record.json dl_mass_power_defaults.

## Owed proofs

6. **All-fly performance** (`RIMMANDRAKE_PROVE_KNOCKBACK_ALL_FLY_PERF`; d_c_all_fly, dl_perf_budget). Builds the
   `frame_time_probe` instrument and measures `barrage_frame_budget` (no frame over 50 ms through a 6-shell barrage
   into a full 10x10 stockpile and a 40-cell gas chain on the full list), then the walk scene `sc_walk_raid`
   (reload, repeat, second order; the hose-carry check rides on it). Needs builds 1 and 4.
7. **Goods in a pit stay retrievable** (`RIMMANDRAKE_PROVE_PIT_GOODS_RETRIEVABLE`; Q10 2026-10-06). Scene
   `sc_pit_fetch`: a hauler fetches a thrown stack off a pit floor by the lowered ladder. If FlowWorks' haulers
   cannot (`RM_PitPathing.cs` routes non-held pawns around open pit cells), the fix is FlowWorks', filed from the
   finding.
8. **Proof scenes with real controls** (`RIMMANDRAKE_REWRITE_KNOCKBACK_PROOFS_REAL_CONTROLS`; the 24-row
   `script_audit` in record.json). Rewrites `RM_KnockbackProof.cs` so every scene in scenes.json asserts its start
   and runs its named control: edits calibration, wall_stop, over_sandbags (barricade lane), door_stop (deep-water
   lane), shield_counter, immunity_window (reload), lookup_projectile, emp_no_throw (into `blast_kinds`), cover_breaks
   (incendiary, EMP lane), pit_colonist (covered cell), settings_off; removes tick_cap and the caps/shelf/items assertions
   that his answers reverse; adds pawn_arc, pawn_hits_pawn, spared_states (airborne state by a test hook, never a
   live flight), settings_sweep, no_cross_ordered and hose_carry_drop; extends pit_enemy (its own scene sc_pit_enemy), corpse_into_pit, killed_by_blast (trace), lookup_zero_wins,
   impact_factor and body_override (lanes of `sc_lookup`), and adds the proof's debug-vector draw counter. Runs the NOT YET RUN LIVE scenes live.

## Settled since

- Showcase 1 is his write-in (d_c_flagship, OWNER:1794470697182934051): a bomb into a stocked storeroom with
  colonists, beside a pit; some goods and some people end in the pit. Scene `sc_storeroom_bomb_pit`, staged by
  `RIMMANDRAKE_PROVE_KNOCKBACK_ALL_FLY_PERF` once builds 1, 2 and 5 land. The north-star bars are VALIDATED as
  written (d_c_bars, OWNER:1794470702467936205; hash 5d06c98d8b13).
