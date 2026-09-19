# CANONICAL_SAVE_CAVERNS_SCRUB_1 — scrub `BMT_CaveSpiderHead` from the start save

Item: `CANONICAL_SAVE_CAVERNS_SCRUB_1`. Date: 2026-09-18.
Target: `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\CANONICAL_ASHKARR_START_2026-09-12.rws`
Mod removed for good: Biomes! Caverns (`biomesteam.biomescaverns`).

## Backup

Backup: `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\CANONICAL_ASHKARR_START_2026-09-12.rws.bak-pre-caverns-scrub-2026-09-18`

| file | bytes | sha256 |
|---|---|---|
| original (pre-edit) | 17600552 | `06b0cea0339145ec19547fb655b16484a19dec8255b383be560208b08bb43e00` |
| backup | 17600552 | `06b0cea0339145ec19547fb655b16484a19dec8255b383be560208b08bb43e00` |

Byte-identical (`cp -p`).

## Inventory

MEASURED (Python, whole-file byte count + `ElementTree` parse): the string `BMT_CaveSpiderHead` occurs **89** times, one per line, in 89 lines — not the 64 in the brief (the 64 was presumably a partial-tag count; every one of the 89 is listed below and they sum exactly). File is CRLF, 17,600,552 bytes.

| # | wrapping tag | XML path | owner | what it is |
|---|---|---|---|---|
| 5 | `<def>` | `world/worldPawns/pawnsDead/li/equipment/equipment/innerList/li/def` | 5 DEAD world pawns, kind `RUT_Jawa_DeepDesert_Heavy`, Faction_9: Mariya Gilmore (`Human668751`), Rina Palmer (`Human668755`), Stepan Woodard (`Human668761`), Marty "Arty" Blythe (`Human668766`), Brenton "Narvre" Moore (`Human668772`) | the weapon Thing itself |
| 5 | `<id>` | same `li/id` | same 5 things | thing ids `BMT_CaveSpiderHead668754/668758/668764/668769/668776` |
| 10 | `<loadID>` | same `li/verbTracker/verbs/li/loadID` | same 5 things (2 verbs each: `_0_ToxicBite`, `_1_Smash`) | verb load ids |
| 10 | `<loadId>` | same `.../MVCF_ManagedVerb/loadId` | same | MVCF managed-verb ids |
| 13 | `<peq>` | `taleManager/tales/li/secondPawnData/peq` | 13 tales (ids 4,5,7,8,9,11,12,13,14,15,17,20,21; 10 `Wounded` + 3 `Downed`), second pawn = `Thing_Human121675` Hernan "Fugly" Perkins (AncientSoldier, Faction_16, DEAD world pawn) | `TaleData_Pawn.primaryEquipment` — a ThingDef ref, NOT a thing id; unused by `GetRules` (RimSage: `TaleData_Pawn.cs`) |
| 13 | `<defName>` | `taleManager/tales/li/defData/defName` | same 13 tales | `TaleData_Def` — ThingDef ref; `GetRules` is null-safe, `ExposeData` skips lookup when defName absent (RimSage) |
| 19 | `<ownerDef>` | `battleLog/battles/li/entries/li/ownerDef` | 19 `BattleLogEntry_MeleeCombat` entries, initiator `Thing_Human121675`, recipients dead colonists `Human922/925/929` | `ownerEquipmentDef` ThingDef ref; `GenerateGrammarRequest` null-checks it (RimSage: `BattleLogEntry_MeleeCombat.cs`). Entries themselves are referenced by hediff `<combatLogEntry>` ids, so they must STAY |
| 10 | `<source>` | `worldPawns/pawnsDead/li/healthTracker/hediffSet/hediffs/li/source` | dead colonists Ashly "Gender" Rock `Human929` (4), François "Zeiph" Schmitt `Human925` (3), Brandy Marsh `Human922` (3) | injury `source` ThingDef (null is normal) |
| 1 | `<thing>` | `worldPawns/pawnsDead/li/rememberedWeapons/li/thing` | `Human121675` (Simple Sidearms memory) | `ThingDefStuffDefPair.thing` ThingDef ref |
| 1 | `<li>` | `components/li[CaravanAdventures.InitGC]/packUpFilter/allowedDefs/li` | game component | ThingFilter allowed-def set entry |
| 1 | `<li>` | `components/li[VanillaTradingExpanded.TradingManager]/priceHistoryRecorders/keys/li` | game component, dict index 4222 of 7654 | dictionary key |
| 1 | `<thingDef>` | same component `priceHistoryRecorders/values/li/thingDef` | index 4222 (aligned with the key) | dictionary value's def |
| **89** | | | | |

No live colonist, no map pawn and no caravan holds one. Every holder is under `worldPawns/pawnsDead` (former colonists of a scrapped test colony, the AncientSoldier that fought them, and five dead Jawa Heavies) — the "disarm" consequence of the brief does not apply to anyone alive. `<peq>` and `<defName>` are def-name references from tales, not equipment-tracker thing-id refs; there is no `<primary>` element anywhere (the equipment tracker stores only `innerList`). No thing id `BMT_CaveSpiderHead######` is referenced outside its own `<li>` block.

## Edit plan

Raw-text edit (bytes, CRLF preserved, no re-serialisation), script `scrub.py` kept in this report's folder as `Transient/canonical_save_caverns_scrub_2026-09-18_scrub.py`. Every removal is a whole line or a whole block; nothing is rewritten in place; no replacement weapon is invented.

| step | removes | lines w/ needle | extra lines |
|---|---|---|---|
| A | the 5 weapon `<li>…</li>` blocks in `equipment/innerList` (block bounded by the `<li>` line before `<def>BMT_CaveSpiderHead</def>` and its matching `</li>`) | 30 | block bodies (health, stackCount, verbs…) |
| B | 10 hediff `<source>BMT_CaveSpiderHead</source>` lines | 10 | 0 |
| C | the 3-line `<li><thing>BMT_CaveSpiderHead</thing></li>` in `rememberedWeapons` | 1 | 2 |
| D | 19 `<ownerDef>BMT_CaveSpiderHead</ownerDef>` lines (entries kept — hediffs reference them by `combatLogEntry` id) | 19 | 0 |
| E | 13 `<peq>` lines; 13 `<defName>` lines plus their `<defType>Verse.ThingDef</defType>` sibling (so `defData` is an empty element, which `TaleData_Def.ExposeData` treats as "no def") | 26 | 13 |
| F | 1 `<li>BMT_CaveSpiderHead</li>` in the CaravanAdventures `packUpFilter/allowedDefs` | 1 | 0 |
| G | VTE `priceHistoryRecorders`: key `<li>` at index 4222 AND the values `<li>` block at index 4222 (6 lines) so the dictionary stays aligned | 2 | 5 |
| | | **89** | |

Assertions in the script: exactly 89 needle lines before, 0 after; each step's count matches the table; VTE keys/values counts equal before and after; total bytes removed == sum of removed lines' lengths (incl. CRLF). Output is written to the scratchpad first, verified, then copied over the original.

## Applied

Script run → `scratchpad/scrubbed.rws`, verified there, then `cp` over the original. Script output:

```
EOL b'\r\n' lines_removed 239 needle_lines_removed 89 bytes_removed 10197
  A weapon blocks 5   (32 lines each = 160)
  B hediff source 10
  C rememberedWeapons 1 (3 lines)
  D battlelog ownerDef 19
  E tale peq 13
  E tale defData 13 (26 lines)
  F packUpFilter allowedDefs 1
  G VTE priceHistory key+value 1 (7 lines)
in 17600552 out 17590355
```

Removed weapons (all from DEAD world pawns, `worldPawns/pawnsDead`, kind `RUT_Jawa_DeepDesert_Heavy`, Faction_9): Mariya Gilmore, Rina Palmer, Stepan Woodard, Marty "Arty" Blythe, Brenton "Narvre" Moore — 5 pawns, 5 weapons. Nobody alive was disarmed. No replacement weapon invented.

Edited save: `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\CANONICAL_ASHKARR_START_2026-09-12.rws` — 17,590,355 bytes, sha256 `220703b4f454023d904bc48ab183d77cce9a5177185502c5839933ae6ec4e735`.

## Verification

| check | result |
|---|---|
| (a) `grep -c BMT_CaveSpiderHead` on the edited save (run with `MEASURE_ALLOW_SCAN=1`, exact-literal case per the skill) | **0** (was 89) |
| (b) `ElementTree.iterparse` streaming parse of the edited save | OK, 425,086 end events, no ParseError |
| (c) size delta | 17,600,552 − 17,590,355 = **10,197** = sum of the 239 removed lines incl. CRLF (asserted in-script); `diff` original↔edited: 239 `<` lines, **0** `>` lines, 64 hunks — deletions only |
| (d) dangling ids | `BMT_CaveSpiderHead\d+` → 0; `CompEquippable_BMT_CaveSpiderHead` → 0; VTE `priceHistoryRecorders` keys 7,653 = values 7,653 (was 7,654/7,654); the 13 emptied `<defData>` join 15 that the game itself had already written empty (natively `<defData />`) |
| (e) `validate_save_artifact.py` | Accepts only `.rid`/`.xtp` by design (its `--help` says so) but does not refuse a `.rws`; ran it anyway with `--json`. It walks every leaf, so on a save its "missing" list is 24,170 hits / 12,637 names dominated by thing ids, faction handles and enums — **not a pass/fail instrument for a `.rws`**. Useful signals: `BMT_CaveSpiderHead` absent from every list; `referencesChecked` 117,795, `typeMismatch` 0, `provenanceNoLongerActive` 0. ⚠️ **The 2026-09-18T21-57-04Z dump was captured with Biomes! Caverns still ACTIVE** (manifest lists `biomesteam.biomescaverns` at loadOrder 473, modCount 632) while the live parsed `ModsConfig.xml` (632 active) has no Caverns entry — so this dump resolves every Caverns def and cannot detect Caverns-dead references in the save. A fresh dump after the next load is needed before any validator verdict about Caverns means anything. |
| not done | no in-game reload test (the game is running another session; the brief forbade touching it). The skill's step "reload-test in game" is owed to whoever next loads this save. |

## Other donors

Inventory only, nothing edited. Attribution from the 2026-09-18T21-57-04Z dump's `packageId`: `BMT_HermeticArmor`/`Helmet` = `biomesteam.biomescore` (Biomes! Core, active); `BMT_BufoBile`/`BMT_Toxwood` = `biomesteam.biomespollutedlands` (active). `BMT_HermeticSuitHediff` is a HediffDef (Biomes! Core).

| def | refs | holders |
|---|---|---|
| `BMT_HermeticArmor` | 3 `<def>` Things: `BMT_HermeticArmor62207` worn by Erika Belsaas (`Human62203`, TradersGuild_Magister, Faction_23, pawnsAlive); `…469114` worn by Fauna "Furr" Wells (`Human469111`, CASacrilegHunters_ExperiencedHunterVillage, Faction_22, pawnsAlive); `…663122` worn by Ernesto Noble (`Human663121`, AncientSoldier, Faction_15, ON THE MAP inside a container thing — a casket/pod). Plus 2 tale `<app>`, 2 outfit-filter `<li>`, 1 packUpFilter `<li>`, 1 VTE key + 1 value | |
| `BMT_HermeticHelmet` | 1 Thing `BMT_HermeticHelmet62205` worn by Erika Belsaas (`Human62203`); 3 outfit-filter `<li>`, 1 packUpFilter, 1 VTE key + value | |
| `BMT_HermeticSuitHediff` | 4 hediffs (severity 0.5): Erika Belsaas `Human62203` (alive), Fauna Wells `Human469111` (alive), Hernan "Fugly" Perkins `Human121675` (dead), Ernesto Noble `Human663121` (map, in container) | |
| `BMT_BufoBile` | 1 Thing `BMT_BufoBile469119` in the inventory of Fauna Wells (`Human469111`, alive); 4 drug-policy `<drug>`; 1 packUpFilter; 1 VTE key + value | |
| `BMT_Toxwood` | 1 Thing `BMT_Toxwood668840` in the inventory of Darcie "Sappy" Carter (`Human668835`, RUT_Jawa_Junkers_Grunt, Faction_1, DEAD); 1 Simple-Sidearms `rememberedWeapons/thing` on the same pawn; 1 VTE key + value | |

**Beyond the brief — the rest of Biomes! Caverns is still in this save.** Joining the save against the dump's 781 `biomesteam.biomescaverns` defNames: **3,279 references to 575 Caverns defNames remain** (detail: `scratchpad` run, summarised here). By location:

| n | where | risk on load |
|---|---|---|
| 2164 | `foodRestrictionDatabase/…/filter/allowedDefs/li` | ThingFilter def-list: one "Could not load reference" line each, then dropped |
| 369 | CaravanAdventures `packUpFilter/allowedDefs/li` | same |
| 281+281 | VTE `priceHistoryRecorders` keys/values | dictionary keyed by ThingDef; null keys — mod-dependent |
| 80 | `maps/li/autoSlaughterManager/configs/li/animal` | 80 animal configs for Caverns creatures |
| 37 | `outfitDatabase/…/allowedDefs/li` | as ThingFilter |
| 28 | `drugPolicyDatabase/…/drug` | drug policy entries |
| 16 | `components/…/Priorities/…/Workgiver` | WorkGiverDef `BMT_FillMushroomFermentingBarrel` / `BMT_TakeMushroomWineOutOfFermentingBarrel` × 8 pawns (a work-priorities mod) |
| 3 | `<stuff>` on worn apparel | `BMT_CrimsonSilk` on `Apparel_TribalHeaddress886` (Exorus "Huntsman" Hawke `Human885`, RUT_Jawa_Tribal_Elder, dead); `BMT_MoonlessSilk` on `Apparel_BasicShirt956` (Nina Marsh `Human954`, Colonist, mothballed); `BMT_BatWool` on `Apparel_Parka668696` (Kazuya "Zippy" Sexton `Human949`, Colonist, mothballed) — **null stuff on a stuffed apparel is the one class here likely to NRE**, and two of the three are mothballed COLONISTS |
| 3+3 | `worldGenerationData/biomeCommonalities|biomeScoreOffsets` keys | BiomeDefs `BMT_CrystalCaverns`, `BMT_EarthenDepths`, `BMT_FungalForest` |
| 3 | `researchManager/progress` keys | `BMT_ResearchMushrooms`, `BMT_AdvancedFungi`, `BMT_CrystalIncubator` |
| 3 | `priceModifiers` keys | `BMT_SpiderSilk`, `BMT_BatWool`, `BMT_CrimsonSilk` |
| 2+2 | Big&Small `BS_OriginalThing`; `npcSubmittedContracts/item` | `BMT_FacetMothLarvae`, `BMT_FungalFerret`; `Meat_BMT_Crystalope`, `BMT_Apparel_ArmorHelmetChitinphract` |

Not measured: map terrain/biome grids (shortHash-encoded; `savemap.py` territory, not text). That is a separate item, not this one.
