# Pyrelands Mechanics: plan (stage 3)

Tree `design/concepts/PyrelandsMechanics/tree.json`, sheet `sheet.md`, scenes `scenes.json`, floor `floor.json`.
North star (new, DRAFT): `design/validation_walks/RimUtinni/PyrelandsMechanics.md`. The rite is built; this plan is
four owed changes and the proof work.

## Owed changes (Relentless builds them from the tree)

1. **Arson count removed, both tiers** (d_no_arson_count, OWNER:1793895903357725756). Delete
   `src/RimUtinni/PyrelandsMechanics/Source/IncidentWorker_FireRaid.cs`, its IncidentDef, its keyed letter, its switch
   and `arsonDebtRaidThreshold`; delete the arson tally from `src/RimMandrake/Pyrelands/Source/Kernel/RM_BurnKernel.cs`
   and every caller (fire-hawk twig, furnace-beast bed, colony fires). `save_compat`: a save holding the tally's
   WorldComponent loads it as missing; state the outcome. Leaf `no_arson_tally`.
2. **The visit picks and carries off** (d_visit_picks, OWNER:1793898838472369653). Replace
   `IncidentWorker_FlameHarvest`'s `LordJob_TravelAndExit` with the rite's harvest duty around the destination (reuse
   `LordJob_RUT_FireRite`'s harvest and exit toils, without the lighting toil). Leaf `visit_picks_and_leaves`.
3. **Fruit defence** (d_fruit_defence, d_defence_reach_scar, d_drive_off_no_goodwill, d_warning_form,
   d_visit_defends_its_burn, d_fight_back_is_self_defence). In the rite and visit lords: a colonist harvest job on
   scorch-fruit inside the party's scar raises a message naming the Tribes and sends one harvester to the picker; if it
   keeps picking, nearby harvesters get a melee/ranged duty on that pawn only, ended when it leaves the scar; no
   goodwill change, no faction relation change, the turned-hostile exit is not triggered by self-defence. A pawn's
   faction is checked (colonist), never "colony-owned", so animals never trigger it (leaf `no_animal_blame`). Its own
   Mod Settings switch.
4. **Thornvine patch moves tier** (c_thornvine_wrong_tier): `Patches/RUT_Thornvine_Edible.xml` to
   `src/RimMandrake/Pyrelands/Patches/` with an `RM_` name. Scene `sc_thornvine_tier`.

## Order

1. `rite_force_hook` (instrument; first): send the next front as a rite through `PyrelandsFireRiteHook.TrySend`, and a
   read of lord toil, scar cells, carried fruit per pawn and goodwill. Item `TRIBES_RITE_SCENES_BUILD_FORCE_THE_FIRE`.
2. The four owed changes above.
3. Every scene in `scenes.json` as a named entry point in `src/RimUtinni/PyrelandsMechanics/validation.py`, with its
   start assertion, control and snapshot restore (same item). The two UNMEASURED rows there
   (`arson_debt_past_threshold_fires_fireraid`, `flameharvest_needs_flameHarvestMinFires`) are replaced by
   `no_arson_tally` and `visit_picks`.
4. The walk on his full list. Close the stale fix items once their scenes pass (c_fix_items_never_closed):
   `FIRE_RITE_FIX_DEFENDERS_MISS_THE_WAR` by `sc_attack_raids`, `RITE_HARVEST_FIX_PICKS_PAST_FULL` by `sc_rite_party`.

## Reuse

The rite lord's harvest duty (`JobGiver_RUT_HarvestScorchFruit`) already avoids burning cells and stops at
`fireRiteCarryPerPawn`; the visit reuses it. `validation_core.py` gives the log tap, site prep and teardown; teardown
restores settings, weather and fire only, so the snapshot restore for terrain, things and goodwill is part of step 3.

## Risks

- A rite comes only at `fireRiteFraction` of fronts, with a present non-hostile Tribes faction (failure mode 1): the
  walk waits for a real roll and records when it had to use the hook.
- The defence must not become a war (failure mode 2): every defence scene reads goodwill and relation after.
- The fire-hawk flies: its scene reads its drop job only; no flight is watched without him.
- `max_overlap` and `min_new_after_first` are UNMEASURED first guesses.

## Showcases

1. `rite_party` (waits on his pick): a party walks in, lights the grass, picks behind the front, warns a colonist off
   their scar and walks off with the fruit. No second showcase: the visit adds one new capability (its picking) over
   the rite, below the three a second needs. The visit, the arson removal, the switches and the thornvine patch are in
   `coverage_rest`.
