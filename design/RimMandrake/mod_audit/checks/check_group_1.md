# Mod audit check, group 1 (batches 01-04, 152 mods)

Independent checker pass over `assessments/batch_01..04.jsonl` (first-pass assessor: claude-sonnet-5-5).
Row-level results: `check_group_1.jsonl` (one row per mod: `check_verdict`, `verified`, `corrections[{field, old,
new, evidence}]`, `confidence`). The assessor files are untouched; a later step merges the corrections.

## Counts

| | n |
|---|---|
| mods checked | 152 (29 + 41 + 41 + 41) |
| AGREE | 117 |
| AMEND | 33 |
| CHALLENGE (verdict change proposed) | 2 |

First-pass verdicts were KEEP 111, KEEP-TEMPORARILY 34, ELIMINATE 7, REPLACE 0. Of the 7 ELIMINATEs, 4 stand as
written (arti.shrinez, zal.largeoutpost, kopp.biomecompatibilityproject, leo.raidprotectionfee), 1 stands with
amended evidence (biomesteam.coreframework), and 2 are challenged (deon.rimtek.core, prepare landing).

## What was checked, and how

- **Every number of the form "N dependants / N refs / N times"** was recomputed from `facts/mod_facts.jsonl` by script
  (`dependants`, `dependants_ours`, `patched_by`, `patched_by_ours_refs`). Every one matched. No miscount found.
- **"Our mods use it" claims** were recounted with a census of 6,404 `src/` code and XML files for each packageId
  and for each mod's display name inside FindMod lists. A sanity probe ran with it: `brrainz.harmony` gave 51 About.xml hits
  and `mlie.starwarsanimalcollection` gave 164 XML hits. 35 of the 152 mods have a `src/` reference. The assessor cited every one
  that matters.
- **Every cited doc line and ruling** was opened at the cited path and line. These are desert_world_design.md:488,
  required_mods.md:355/930/1057-1063/1127-1131/1346/1358, WILD_ANIMALS_PADDED_LISTS_1.md:372-395,
  GRAVSHIP_LANDING_CRUSH_1.md:3-11, SCENARIO_SETTINGS_SPEC.md:410-413, protected_mods.json:12,
  AftermathRuleRunner.cs:230, RM_PyrelandsDensityEnforcer.cs:9-11, JawaBenchIncidentTools.cs:141, UtinniPatches
  About.xml:81-82, and others listed in the rows.
- **Live mod settings** were read from
  `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\`. The assessors never opened
  this source. It changed 4 rows (see the top-10 list).
- **Source claims** were checked against `source_confidence` and `source_candidates[].verify.status`. No bundled-lib
  false match (pardeike/Harmony, rwmt/Publicise) is cited as a mod's own source in this group. The assessor correctly
  rejected 3 name-search mismatches: Milky Way, Layered Apparel and HugsLibChecker.
- **Severity bands** were checked against RUBRIC §3 for `size` and `memory`. Every memory severity is labelled as a proxy, and none
  claims MEASURED. No TPS claim is labelled MEASURED.

## Systematic first-pass errors

1. **Card-worthy with no question.** 10 of 30 `card_worthy` rows have an empty `needs_owner` (all in batch 03: Faction Raid
   Cooldown, LightsOut, Map Designer, Map Preview, MinifyEverything, three MiningCo., MutatorWorldIcons, My Little
   Planet). A card cannot be built from them. Check rows supply plain-worded questions or merge them into an existing card.
2. **Schema drift.** Batch 02 writes `needs_owner` as a **string**; batches 01, 03 and 04 write a list. The merge step must normalise it.
3. **Searched-and-found-nothing labelled MEASURED.** Six batch-01 rows set `source.confidence: MEASURED` for "steam-only",
   but facts say INFERRED (SEARCHED, no candidates). Two batch-04 rows say `available: yes` for repos that `gh api`
   returned NOT_FOUND (Standalone Hot Spring, Stealing Mod).
4. **Live configuration never consulted.** Assessors reasoned from docs about values that sit in the Config folder.
   One doc value was stale (Bigger Gravships), one owner-ruled setting is not in effect (Land On Anything), and two
   open questions were answerable by listing the folder (Better Ambushes, More Slaves: no settings file, so defaults apply).
5. **Adoption records missed.** `required_mods.md` records adoptions the rows did not find: Call Trade Ships
   (:1358) and Prepare Landing (:355, ACCEPTED). One of these led to an ELIMINATE.
6. **Frameworks do not follow their dependants across batches.** RimTek Core is ELIMINATE while its dependant DocMate is KEEP
   (batch 12). Genetic Heads Framework is KEEP while its consumer is KEEP-TEMPORARILY (batch 14). Nightmare Core is KEEP while
   its only dependant is KEEP-TEMPORARILY (batch 12).
7. **Duplicate cards for one question.** Three MiningCo. cards ask one retheme-or-own question. Four or five world-map-tool cards
   (Map Preview, Mutator icons, Prepare Landing, plus the authoring tools) ask one audience question (§5.1). Three cards
   (Alien Worlds, My Little Planet, Sensible Factions) ask the §5.8 remake question. Two "are you still editing X" cards
   ask one question. Merging them would turn about 30 cards into about 20.
8. **Re-asking settled rulings.** Mines 2.0 re-asks the owner's own 2026-08-12 override with no new evidence. Storyteller Enhanced
   asks "which storyteller", which R-S7 already ratifies (Randy). RimAI asks about transport, which the 2026-09-05
   `claude -p` ruling already covers ("any future consumer", no local Ollama).
9. **Dependants blind spot.** As predicted, `dependants: []` hid a real consumer: Genetic Heads Biotech's XML uses
   `FacialAnimationGeneticHeads.*` classes from the framework 11 times. The census of version-folder defs held up in this group.
   biomesfossils and geneticheadsbiotech defs sit in `1.5/` folders and were still counted.
10. **Minor misreads.** Biomes Fossils was called "XML-only" but ships its own DLL; "dll_flags empty" was read as "no code". Two
    severity bands are off: Face Addon size 3, where 61 MB is band 2; Alien Worlds memory 2, where 34.5 MB is band 1.

## The 10 highest-impact corrections

1. **nep.landonanything: the owner's ruling is not in effect.** `GRAVSHIP_LANDING_CRUSH_1` (owner 2026-09-06) says
   `allowedToSqishRoofs` and `allowedToLandOnAnyTerrain` must be forced OFF. The live
   `Mod_3545384484_LandOnAnythingMod.xml` (mtime 2026-09-12) has both **True**, and no `src/` code overrides them. The item
   is closed as done, not "doing" as the row said. A fix is needed (proposed unfiled: `LANDONANYTHING_RULED_FLAGS_OFF`).
2. **redmattis.biggergravship: the "four numbers" are stale and there are twelve.** The live
   `Mod_3522759531_GravshipSizeSettings.xml` (2026-08-15) stores 100/100/12/100, not ship_designs.py's 34/30/12/85. It also stores
   chemfuel tank capacities (1140.6 / 8805.5), a thruster cap (20) and shield values. The fuel values touch the brief's
   "free fuel" exclusion, so the owner card must ask about them before they are frozen into an RM patch.
3. **m00nl1ght.unofficialupdates.preparelanding: CHALLENGE ELIMINATE → KEEP-TEMPORARILY.** It is ACCEPTED in required_mods.md:355
   and listed in the world-map authoring toolset. The row's own question (does the owner use it?) is still open, and
   comparable tools in this group were graded KEEP-TEMPORARILY.
4. **deon.rimtek.core: CHALLENGE ELIMINATE → KEEP-TEMPORARILY.** Its dependant DocMate is KEEP in batch 12. A framework
   cannot be removed under a KEEP dependant.
5. **cain.mineshaft: drop the card.** The owner overrode exactly this objection on 2026-08-12 (desert_world_design.md:488).
6. **mlie.storytellerenhanced: narrow the card.** The storyteller is ratified as Randy (SCENARIO_SETTINGS_SPEC R-S7). Ask only
   about its 8 incident patches.
7. **kilokio.rimai.framework: narrow the card.** The transport question is answered by the 2026-09-05 `claude -p`
   ruling. Note that required_mods.md contradicts itself, ADOPTED at :1127 and PARKED at :930.
8. **sd.fa.geneticheadsframework: dependency is MEASURED, not UNVERIFIED** (11 class refs from geneticheadsbiotech).
   Its verdict should follow that mod (KEEP-TEMPORARILY).
9. **mlie.factionraidcooldown: the mod is actively tuned.** The live setting is `extraHoursPerDeath 13`. Our Aftermath already
   bypasses it. The empty card gets a plain question.
10. **zal.calltradeships: drop the card.** It was adopted with explicit pillar reasoning (price is a silver sink,
    required_mods.md:1358). Re-raise only if the Bazaar design is shown to conflict.

Smaller corrections are recorded in the rows. My Little Planet has supporting evidence: 21,872 tiles is not a vanilla
coverage size, so the saved world likely depends on MLP's size settings (INFERRED). MiningCo. MMS already has a partial
Czerka retheme (`UtinniPatches/Patches/MiningCo_CzerkaRename.xml`). Bones Unofficial declares 2 abstract defs and is patched
by survivaltools. Leo Raid Protection Fee's "pick one" source is a proposal, not a ruling, and since it has 0 defs, Cherry Picker
cannot cut it; it must be unticked.

## Ruling conflicts found

| conflict | sources | effect |
|---|---|---|
| Land On Anything flags: ruled OFF, live ON | GRAVSHIP_LANDING_CRUSH_1.md:5-11 vs live Config | ruling silently not in effect |
| Bigger Gravships values | ship_designs.py (2026-08-13) vs live Config (2026-08-15) | doc stale; owned-patch scope wrong |
| RimAI | required_mods.md:1127 ADOPTED vs :930 PARK vs CLAUDE.md 2026-09-05 `claude -p` ruling | doc contradicts itself and a later ruling |
| Storyteller | required_mods.md:871 adopts Storyteller Enhanced vs SCENARIO_SETTINGS_SPEC R-S7 (Randy, ratified) | the spec is the later, ratified one |
| Prepare Landing | required_mods.md:355 ACCEPTED vs first-pass ELIMINATE | resolved by the CHALLENGE |
| Anomaly | 01_campaign.md header vs canon_reintegration_plan.md ruling ② (owner card 2026-09-04) | brief §5.7; verdict-neutral, so not a mod card |

## Not checked (stated so nobody reads silence as a pass)

- Placed Things in the campaign save, for every ELIMINATE (still UNMEASURED; needs `rimworld-savegame`).
- Compiled default values inside DLLs, for mods with no Config file (Better Ambushes' default multiplier).
- Whether each `required_mods.md` "ADOPTED" was the owner's decision or an agent's recommendation. Several entries are
  Fetcher-era recommendations.
