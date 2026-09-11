# BIOME_FAUNA_ASSIGNMENT_SITTING_1 — the morning sitting, prepped

Owner's plan (2026-09-05, verbatim on the filing): review all biome sheets, finish the
remaining biome descriptions, then assign the animals and plants.

## The table is set (overnight 2026-09-05→06)

1. **Sheet review** — ten sheets done through `wasteland.md`; the dryland ladder is complete.
2. **Remaining descriptions** — `_openers_prep.md` has the measured table for every
   undefined biome; candidates by the slowly-vary rule: `AB_RockyCrags`, `AB_MycoticJungle`.
   `NIGHTSIDE_BLUE_DESERT_1` (BiomeGRimond, investigated) rides this.
3. **Assignment** — `_assignment_prep.md` (611 lines): per-biome admission tests +
   KEEP/EVICT/IMPORT menus with cited laws, the ubiquity-25 disposition menu, the
   NEW-ART/DEF ledger (feeds the graphics pipeline), and the homeless census:
   **~205 of 767 live wild creatures (27%) have no home once the sheets bind** (MEASURED).
4. **First call of the sitting** (flagged in the pack): `ExtremeDesert` is ONE def carrying
   TWO sheets (dune sea + deep desert) — split or share.
5. ~~Standing contradiction: `biome_and_fauna_roster.md`~~ — resolved 2026-09-09 by
   deleting the doc (owner: remove inaccurate material, don't supersede).
6. **2-minute cards also waiting**: GRAPHICS_GEMINI_BILLING_DECISION_1 (cost math done).

## Instrument caveats carried into the sitting
Register `flies` special broken (all flier reasoning UNMEASURED); juvenile sizes absent
(huge-young exemptions UNMEASURED); two rows statsResolved:false. Both register defects
ride REGISTER_CORPSE_CROSSCHECK_1.

## sequence rider (owner, 2026-09-06)
Blocked until `BIOME_FREEZE_FABLE_REVIEW_1` AND `SETTLEMENT_REJIGGER_ROUND2_1` close — the
sheets freeze first, the settlements move to fit them, then the animals and plants land.
**SATISFIED 2026-09-09 — both closed at `d88d0117`. Unblocked.**

---

# 2026-09-09 — owner rulings: BENCH EXECUTES NOW, SOLO. No joint sitting.

Owner, verbatim: *"It's time to do the animal placement work RIGHT NOW... YOU are to do
this pre-assignment work, not foundry, using the biome sheets as guides... Conduct that
immediately and completely for all game biomes."* This retires the "joint sitting" framing:
BENCH makes every call from sheet law + `_assignment_prep.md` + `_freeze_rulings_2026-09-07.md`,
lands it, and the owner's review runs on per-biome review sheets AFTER.

**Context that triggered it:** FOUNDRY's `4d739565` divvy doc was written from the raw
census in ignorance of the sheets (already marked SUPERSEDED in its own header, same day;
no XML was ever generated from it — nothing to revert).

## The four ruled calls (owner, 2026-09-09, by card)

1. **Land now, review after.** Roster data + generated wildAnimals/wildPlants patches are
   committed on BENCH's calls; per-biome animal + plant review sheets, prefilled with what
   landed and why, are the owner's override surface afterwards. *Test: every biome's landed
   roster row cites the sheet law it passed.*
2. **Homeless pool defaults to RESERVE-FOR-EVENTS** (no wild spawn anywhere, def stays live
   for quests/raids/traders). Cherry Picker cuts only where already ruled: Earth-nameable,
   retextured Earth twins (`RETEXTURED_EARTH_FAUNA_BANNED_1`), Blizzarisk (freeze R20),
   0%-recognizability mods. Grindterra (**`GRim*` prefix — NOT `GR_*`**) fauna are
   homeless-by-default — Earth analogs, deprioritized (owner, 2026-09-09) — which is what
   enables retiring Grindterra biomes after the pass. ⚠️ Prefix correction 2026-09-09:
   `GR_*` is Vanilla Genetics Expanded — chimeras, NOT Earth animals
   (`RETEXTURED_EARTH_FAUNA_BANNED_1`: "leave them") — judged per sheet law normally.
   The first roster batch enforced the wrong prefix; corrected on resume. *Does NOT
   change: livestock/faction-kind creatures (Tellurox etc.) — wild rosters only.*
3. **SW staples: adjust-and-keep.** Wraid/Gutkurr slowed <4.5 → legal burst predators in
   `Desert`; Massiff → shrubland medium band; WarWyrm ruled a burrower → `ExtremeDesert`
   giant; Mudhorn kept as the shrubland's ONE huge-predator icon exception; Scurrier
   trimmed to comm ≤0.1 grain-scale in `ExtremeDesert`. Icons survive by fitting the law.
4. **Flora: purge Earth-nameable planet-wide now; refill from best-available alien donor
   flora per sheet law; thin is acceptable** (sparseness is doctrine in half the biomes);
   every sheet-demanded signature plant becomes a NEW-ART/DEF queue item. Aligns with
   `DESERT_PLANTS_SCRAGGLY_1` (which stays the art-authoring item for the ~8 new scragglies).

## Standing dispositions applied without further asking (recommendations accepted in bulk)
- Ubiquity-25 (prep §9): EVICT the nameable Earth five (Rat/Hare/WildBoar/Raccoon/Warg)
  planet-wide; KEEP Muffalo + Boomalope reskinned (in-joke lane); TRIM the rest to ≤2
  named home biomes.
- `ExtremeDesert`: one merged strict-intersection roster (freeze R22, already ruled).
- Rosters bind PER DEF (freeze R19a) — pending repaints (HorrorWastes dissolve, Contagion
  move, Blue Desert + Pyrelands world switches) do not block. HorrorWastes gets NO roster.
  Blue Desert roster targets `RUT_BlueDesert`; while `BiomeGRimond` is still painted it
  gets the same roster so the switch is a rebind, not a redesign.
- Mlie SW animals keep their bare live defNames (no `RSW_` anticipation —
  `MLIE_FAUNA_ABSORPTION_1` renames later).
- Fish: every watered biome gets an explicit fish list or a ruled "no fish, because…"
  (`FISH_BY_BIOME_1` rides this pass as data). Mechanoids/ancient dangers are a separate
  axis (`MECHANOID_BIOME_PRESENCE_REVIEW_1`) — wild rosters here never cover them.
- New creatures/plants are NOT authored in this pass — the NEW ART/DEF ledger (prep §12)
  becomes queue items; rosters land from existing defs only.
- Fliers cross biomes (freeze R17) — a cross-biome appearance is not a conflict.

## Enforcement gap the build lane MUST close (found 2026-09-09, BENCH)
Replacing `BiomeDef.wildAnimals` does not evict an animal whose own
`race.wildBiomes` names a painted biome with weight > 0 — the load-time padder
(`WILD_ANIMALS_PADDED_LISTS_1` spec) materializes those weights back INTO
`wildAnimals` at load. So the cast patch alone under-enforces every eviction.
Fix: an animal-side patch stripping `wildBiomes` entries that point at any of the
29 painted defs for every creature NOT in that biome's roster — the same
animal-side removal `biome_animal_conflicts.py` already performs for duplicates,
generalized. Verify post-load with a fresh def dump, not disk XML.

## Execution safety rails (binding)
- After ANY cast/roster regen: re-run the de-dup union over ALL previously-found pairs
  (`BIOME_DUPLICATES_STILL_LIVE_1` — the `ChooseWildAnimalSpawns` static-ctor crash).
- Check Cherry-Picker-zeroed rows (`biome_commonality_zeroed.py --ours`) before spending
  weight on a suppressed def.
- Generate to a temp path and diff before any in-place write; diff the LOSSES
  (freeze R36 spirit). `validate_patch.py` with both `--live` and `--defs` before deploy.
- ⚠️ The runtime padder (`WILD_ANIMALS_PADDED_LISTS_1`, suspect
  `kopp.biomecompatibilityproject`) materializes every animal into every biome at
  commonality 0 at load — a live dump of `wildAnimals` is NOT our cast; compare against
  the XML we author, and never audit placement from a padded live dump.

## Removed (owner ruling 2026-09-09: delete inaccurate material, never leave-and-supersede)
- `design/Jawa/worldbuilding/biome_and_fauna_roster.md` — DELETED (KEEP-ALL-SW etc.
  inverted by the sheets; git holds the history).
- `design/Jawa/worldbuilding/biome_fauna_flora_divvy_2026-09-09.md` — DELETED (the
  census-blind FOUNDRY divvy; no XML was ever generated from it).
- `design/Jawa/worldbuilding/biome_flora_rosters.md` — DELETED; `biome_flora.py --doc`
  regenerates it once FAMILIES is rewritten to sheet law.
- This item's own "joint sitting" framing and the sequence rider (satisfied).

## 2026-09-09 instrument findings (post-landing; the new portfolio caught both)
- ✅ fig6 regression gate: Desert 0/45 violations, AridShrubland 0/42, ExtremeDesert
  1/12 (AA_Dunealisk, self-documented exception). fig7 max spread collapsed 45 → 5.
- 🔴 **Flora defect 1 — arid shrubland ban 9 (no flammable living flora) is violated
  by 10 of 10 landed flora** (figF3, MEASURED off resolved statBases; the dryland
  batch had flagged flammability UNMEASURED). Fix wave owed: per-def Flammability→0
  patch for the interim stand-ins (they are near-single-biome post-pass) OR re-pick;
  the sheet's own designed flora (the fuzz…) is non-flammable by design.
- 🔴 **Flora defect 2 — 46 of 126 judged flora rows cannot grow at their biome's
  measured temps** (figF2; 31 are the Rot's fungi, minGrowthTemp 0 vs −18.8 °C
  median; 4 propane-lake plants 19° short). Silent dead flora in game. Fix wave:
  per-def grow-temp tolerance patch (the NORMALIZE_TEMPERATURE_TOLERANCES_1 job,
  now with a measured worklist in `review/biome_climate.json` +
  `review/plant_flammability.json`).
- ⚠️ Sheet gap: PoisonForest, the Forge (3 defs), Wasteland state no median temp in
  §0 — 73 flora rows unjudgeable by figF2. Sheets are the owner's conversation loop;
  flagged here, not solo-edited.
- ⚠️ Fix-wave sequencing: roster edits shift positional sheet row-ids — regenerate
  both review sheets after any roster fix, BEFORE the owner's verdict pass.

## 2026-09-09 FIX WAVE — what it found and closed

- ✅ **Ban 9 (shrubland flammability): CLOSED by patch, not by re-pick.** All 10 rows
  were re-checked against the pool for a Flammability-0 alien donor fitting the sheet's
  low-shrub/fuzz law. **None exists** — only 32 of 647 pool defs are non-flammable and
  every one is a fungus, a fire/anima form or an Earth-nameable cactus, most already
  bound to another flora family. So all 10 are KEPT and zeroed by
  `BiomeFloraStatAdjustments_Generated.xml`; safe because every one is single-biome on
  the landed planet (MEASURED). `BMT_GreyLady`'s Flammability 40 (26× the pool maximum)
  clamped to 1.0 in the same patch as a donor bug.
- 🔴 **figF2's "46 dead flora rows" was measured off a STALE source and the real number
  was 6.** `plant_pool.csv` was built 2026-08-23, *before* any tolerance patch existed;
  the live def dump already carried the widening. 40 of the 46 were alive. This is the
  "instruments can read the wrong file" failure, and figF2 should read the DUMP for
  liveness and the POOL only for donor (as-shipped) values.
- 🔴 **The real defect was worse than the reported one: `plant_tolerances.py` was
  dissolving its own output.** Two faults, both fixed. (1) Its `PATCH` constant still
  pointed at the retired `src/Jawa/Jawa_Patches/`, so every `--write` since
  JAWA_PATCHES_SPLIT_1 wrote to a dead directory — the deployed patch went stale through
  the whole roster rewrite. (2) It read current values from the live dump, which already
  contains its own patch, so 67 plants looked like they "already survived their home"
  and would have been dropped from the next regeneration — reverting them to donor bands
  that cannot reach their biome. It now reads shipped values from `plant_pool.csv`,
  unions the tile demand with the sheets' median ±10 (`biome_climate.json`), and
  ASSERTS the outcome: 0 of 122 landed flora rows fail their biome's median.
- ✅ **One genuine re-pick: `BMT_Blastpod` → `Boomshroom`** (the_rot). Blastpod ships
  50…352 °C; reaching the Rot's −18.8 °C median needed a 78.8 °C stretch, past the 30 °C
  re-pick limit. Boomshroom is literally the same asset (Blastpod's own texPath is
  `.../Boomshroom/BoomshroomGrown`) with the same chemfuel yield and a 0…58 °C band.
- ✅ **The Rot's fungi are EXTENDED, not re-picked, and the sheet is why.** `the_rot.md`,
  "Thermogenesis — the warmth is metabolic": the mycelial mat is a heated floor the
  jungle makes for itself, and *"air temperature is a lie about the ground"*; the cold
  edge (Frostcaps) is where that heat fails. Cold air over warm substrate is the biome's
  own story, so a sub-zero floor on its fungi is in character.
- ✅ **RUT_PropaneLake grows nothing** (new roster key `flora_def_exclusions`): its four
  flora rows were the fuel-snow SHORE's, handed to the liquid sea by def-binding.
- ✅ **animalDensity**: RUT_NightsideIce 0→0.2, RUT_TwilightSea/RUT_GreySea undeclared
  →0.1, RUT_TheScald →0.15, each citing its sheet and recording a quicktest tune owed.
  ⚠️ The reference figure "Desert ≈1.5" used to size these is WRONG — live resolved
  Desert is **0.4** (MEASURED); IceSheet 0.2 and SeaIce 0.1 are right. The chosen values
  still sit correctly on the live scale, so none was changed.
- ⚠️ **445 operations dropped from `PlantTolerances_Ashkarr.xml` (577 → 139)** and this
  is deliberate: the old file was generated from the pre-2026-09-09 whole-pool FAMILIES.
  Every dropped def is unrostered, so nothing spawns wild that did before, and each
  reverts to the value its own mod ships — never below it. Two rostered defs are among
  the drops (`AB_TinkleGrass`, `Plant_FelucianGlowspore_Wild`) and both are correct:
  their shipped bands already cover their homes.

## Cross-item verification (2026-09-09): RETEXTURED_EARTH_FAUNA_BANNED_1 (FOUNDRY's, already closed)
Re-verified against the REGENERATED cast at `90727e48`: the five twins are in
EARTH_FAUNA_EXCLUDED.txt (lines 125–129), the new cast greps 0 for GRim*/Wolf_Great,
rosters refilled every touched biome, and GRimStoneCrab (Miasma) — a sixth twin the
original spec missed — was caught and evicted by this pass. Note for FOUNDRY: the
deployed cast now lives at `src/RimUtinni/UtinniPatches/Patches/BiomeCast_Ashkarr.xml`;
that item's verify snippet still greps the old src/Jawa path and would false-pass.

## Deploy status (2026-09-09, end of the solo pass)
REPO COMPLETE, GAME COPY NOT UPDATED — deliberately. The deploy plan for
UtinniPatches is entangled with the other window's in-flight ownership wave (their
new RUT_Sump/TheForge/TheRot/Umbra/Wasteland/Webwork/WeepingStones defs +
GeothermalDensityField + SandFishing sit in the same `+` list) and the game is
RUNNING under their session. Applying would ship their mid-work. The assignment
patches ride the NEXT load round's batched deploy (rimworld-load-round protocol);
nothing here needs the game before the owner's verdict sitting anyway.

## CLOSED d19997bd (2026-09-09) — the solo pass is complete; the owner half is its own item
28 rosters landed and validated; cast/defs/patches generated, validated, dedup-unioned,
eviction-stripped; flora chain rewritten + normalized (flammability, temps); analyses
portfolio migrated + extended; both review sheets built, click-tested, regenerated
post-fixes. Deploy held for the next load round (see above). Successor for everything
remaining: ASSIGNMENT_SHEETS_VERDICT_SITTING_1 (owner verdicts → applier → regen).

---

# 2026-09-10 round-2 live sitting — owner rulings (BENCH at the bench)

**1. Insect ruling.** Owner, verbatim: *"I should NOT have allocated any of the base
game's insects: they should remain the Insect faction, as should the Black Hive, as
those are special 'factions' essentially for infestation events. So please de-select
those for all biomes other than themselves."* Applied 2026-09-10: 8 VFEI2 resident
rows → `out`, 4 VFEI2 homeless moves VOIDED (Acidspitter/RoyalSpelopede→Scarlands,
Silverfish→Grey Deep, Macrofly→arid), 20 homeless insect rows marked FACTION-RESERVED
(incl. Megaspider, Spelopede) in `round2/decisions_propagated.json`; `move_mapping_v2.md`
amended (160 live moves); `biome_findings.md` casts corrected. Round-1 verdict file
(`fauna_assignment_register.decisions.json`) left untouched — it is the owner's record.
Open flags: Megascarab sits at `out` (= cut entirely) — confirm it should instead be
faction-reserved; GiantAnt_Race greentide "raid events only" left standing (consistent
with the ruling).

**2. Art "redo" semantics** (owner, verbatim intent): redo = the art is particularly
bad and must be FULLY REGENERATED, possibly the whole creature. Star Wars creatures
are NEVER renamed — instead look up inspirational reference images online to converge
on the right look. Non-SW creatures: redo may mean a whole rename+redefine based on
the creature's function. **When in doubt, ask the owner — that is the default.**
Review surfaces show creatures in SIDE PROFILE (east-facing) from now on; the
south-facing headshot is illegible for many body plans.
