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
   0%-recognizability mods. Grindterra (`GR_*`) fauna are homeless-by-default — Earth
   analogs, deprioritized (owner, 2026-09-09) — which is what enables retiring Grindterra
   biomes after the pass. *Does NOT change: livestock/faction-kind creatures (Tellurox
   etc.) — wild rosters only.*
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
