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

## owed
- NEXT: next time the game is up, run a live pawn read for the nickname "Mookee" (or any trader animal) on
  the Rot map, then record its race/kindDef here.
- Then: if it is a donor race with no port, port it with our own realistic painted render
  (normal port path; art through the art ledger). Do not queue art before the species is known.
