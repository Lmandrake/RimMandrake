# DONOR_PHASE0_FINISH_AWAITING_HIS_RULINGS

## Donor-off L1 round, 2026-10-16 (FOUNDRY, live, tier donor_off_phase0 = 21 mods)

Evidence: `Transient/phase0_L1_result_20261016T085647.json` (pre..mapgen + save, no flight) and the second-look run
`Transient/phase0_L1_result_20261016T090004.json`. Cold load on the tier: 79-135 s.

- **PASS 249 / FAIL 11 / UNMEASURED 6** on the round; the second look turned all 7 new FAILs to PASS:
  - `SPAWN_RM_Danglemaw`, `_RM_Zrrik`, `_RSW_Fanback`, `_RSW_Lothcat`, `_RSW_WarWyrm`, `_RSW_Warbird` (1 of 2 alive):
    **SITE** - all 2/2 alive on a fresh quicktest.
  - `MAPGEN_RM_BlueDesert`: **SITE** - the scratch tile 21434 carried a River mutator with null river links
    (`TileMutatorWorker_River.GenerateRiverGraph` ArgumentNullException); PASS on tile 17421.
- **Still FAIL (MOD, known):** `L04_TEX_OURS` (38 lines: RM_ plants pointing at vanilla `SnakePlant`/`Echeveria`/
  `PincushionPlant`/`Hay` paths that do not exist in 1.6, plus RM_Glasmaw, RM_Murrowbulb, RM_Thrannagourd,
  RM_Salvessa, RM_CorriskTree, RM_DustveilEgg, RM_AngelMothEggFertilized, RM_Leather_RaptorPlates*);
  `ROSTER_RM_Cauldron`/`ROSTER_RM_Miasma` (RM_Bileworm absent), `ROSTER_RM_Greentide` (RM_Zrrik absent).
- **UNMEASURED:** OOMB_GROWTH/SPLIT (compressed feeding), PORTAL_ENTER/EXIT (governor stop: ToxicBuildup on the Rot
  map), SPAWN_BADTEX_CONTROL (the pawn graphic instrument cannot read pawns), FLIGHT x23 (owner present only).
- **SAVE_LOAD PASS** (was UNMEASURED/stuck on the menu - `PHASE0_L1_SAVE_LOAD`): two causes, both fixed:
  1. the bridge's `load_game` refused with `save.missing_mods` (no dialog at all); the driver now passes
     `ignoreModCompatibility` and reads the reply (`54f642f2b`);
  2. the save's world has Deep Orbit's `Orbit2` planet layer; without `broms.deeporbit` the load NREd in
     `WorldGrid.CreateRequiredLayers` and fell back to Entry. Deep Orbit is now in the tier (`54f642f2b`).
  `SAVE_DONOR_REFS` is UNMEASURED by design: a 614-mod save on a 21-mod tier caps Verse.Log and the journal
  tap loses ~7000 entries (`c7beb1cf3`). The donor-ref grade is the offline save grep (P6).
- **Renamed defs sanity (live):** RM_SikkaSikka, RM_Rakeshank, RM_Dhoggur, RM_Zisska spawn; RM_Zisska gets
  `RM_FireSpit` (canCast) after its first ticks; RM_Ismerrow resolves 7 variants (A..D seen); RM_Braskeen folder
  resolves; no Player.log texture or xref line names any of them. RM_Dhoggur logged 4 config errors (claws on
  `FrontLeft/RightLeg`, a group QuadrupedAnimalWithPaws lacks) - fixed to `*Paw` (`37199ecfb`).

**Not done:** the runbook's step 6 (replace the ikee with RSW_Ikee, re-bond with Yeku, save over the donor-free
name). Note the loaded save shows only 1 player Human on the map where the file holds 3 (+ a droid-race pawn from a
mod outside the tier); expected tier loss, but the ikee swap must run on the FULL list, not this tier.

NEXT: run the ikee swap (runbook step 6) on the full list; owner-present FLIGHT rows; then P7.
