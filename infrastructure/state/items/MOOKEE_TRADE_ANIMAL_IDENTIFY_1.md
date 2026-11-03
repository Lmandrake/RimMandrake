# MOOKEE_TRADE_ANIMAL_IDENTIFY_1 — the Rot trader animal named "Mookee"

Owner, 2026-10-09 (relayed): in the Rot he saw a "Mookee" with cartoonish donor art, standing beside
trade animals carrying packs.

## measured (2026-10-09, offline)
- **"Mookee" is not a species. It is a pet NAME**: one `loreName` in
  `src/RimStarWars/StarWarsPatches/Defs/RulePackDefs/Jawa_PetNames.xml` (`RSW_Jawa_NamerPetSW`), which
  `Patches/PetNames_Ashkarr.xml` puts on every race that had Star Wars Animal Collection's
  `SWAnimalNamerMale` (267 races, donor and our `RSW_` ports). Scan: 75,290 XML files across both mod roots
  and `src/`. The only hits were that rulepack and its deployed copy. Sanity probe: `bantha` hit 141 files.
- Pack carriers: the only Star Wars carrier anywhere is the Bantha in Sand People
  (`zal.sandpeople`), and that mod is **inactive**. Active traders' carriers are vanilla
  Muffalo/Dromedary/Alpaca/Elephant, including all of our `Jawa*` factions. So the named animal is most likely
  **trader STOCK** (a tame Star Wars animal for sale), not a carrier.
- 62 Star Wars-namer races are pack animals. The ones with **no `RSW_` port** (still donor art):
  Aiwha, Behemoth, Bordok, Brezak, CorellianHound, Gualaar, HarvesterBeetle, IthorianReek, Kaadu,
  KellDragon, Mastmot, Narglatch, Reek, Tauntaun, Thranta, TuskCat. The donor versions still exist
  beside every port too.
- The name is in none of the 8 newest autosaves, so the caravan was never saved.

## resolved (2026-11-03, offline)
- **Species: donor `Dewback`** (pawn `Dewback211868`, mlie.starwarsanimalcollection), FOUNDRY live read
  2026-10-10 (ledger note). It was a PlayerColony animal, not a trader carrier.
- It has a port: `RSW_Dewback` (`src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Dewback.xml`), drawn from
  `RimStarWars/SWBestiary/Dewback/Dewback_{east,north,south}.png`, the owner's set C (34bb644a86, sheet
  `infrastructure/state/art/sheets/dewback_reconcile_sheet_2026-10-16.snapshot.json`). `art_fold_check.py`: Dewback ok.
- The donor mod is retired (3265277e01). It is absent from `ModsConfig.FULL.CANDIDATE_DONORS_RETIRED_2026-10-18.xml`
  and from the live list. No def in `src/` is the bare `Dewback`. Both canonical saves have 0 `<def>Dewback</def>`
  and 0 `<kindDef>Dewback</kindDef>` (probe: `<def>RSW_Dewback</def>` = 1 in each). So the cartoonish donor
  Dewback cannot appear any more. The item's "donor race with no port" branch does not apply; no art is owed.
