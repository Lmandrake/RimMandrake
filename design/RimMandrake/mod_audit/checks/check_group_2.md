# Mod audit check, group 2 (batches 05-09)

Checker: claude-opus-5-5, 2026-10-10/11, offline only. The check rows are in `check_group_2.jsonl`, one per
mod with `check_verdict`, what was verified, and the corrected fields as old/new with evidence. The assessor
files are unchanged; a later step merges these amendments.

## Counts

| batch | category | mods | AGREE | AMEND | CHALLENGE |
|---|---|---|---|---|---|
| 05 | code_tweaks_qol_ui_4 | 40 | 36 | 4 | 0 |
| 06 | star_wars_donors | 10 | 3 | 7 | 0 |
| 07 | vanilla_expanded | 48 | 47 | 0 | 1 |
| 08 | biomes_world | 14 | 10 | 4 | 0 |
| 09 | creatures_animals | 13 | 9 | 3 | 1 |
| **total** | | **125** | **105** | **18** | **2** |

## How it was checked

- **Mechanical pass over all 125 rows:** every `patched_by_ours_refs N` claim was checked against the facts
  file (0 mismatches). Memory and size severities were checked against the RUBRIC bands (2 size-band slips:
  alphabiomes 106 MB scored 3, quarry 13 MB scored 2). Source URLs were checked against facts, and against the
  known false matches.
- **A packageId sweep of `src/`** (6,208 XML/C#/py files, lower-cased; sanity probes `brrainz.harmony` = 138,
  `mlie.starwarsanimalcollection` = 692), plus `<li>ModName</li>` FindMod hits, so that "nothing of ours
  uses it" could be tested against the source rather than against `dependants_ours`.
- **Every ELIMINATE, every card_worthy row, and every cited ruling** was opened at the cited path.

## Systematic errors in the first pass

1. **"Nothing of ours depends on it" was read off `dependants_ours`, which only holds `modDependencies`.** That
   field cannot see `loadAfter`, class references or patches that name the mod in comments or Conditionals. It
   was wrong for 5 mods: jecstools, mineablesor, mines2patchouterrim, btd.gbp.shippack.kotor.vge and archon.
   The src sweep finds each of them.
2. **Facts `dependants` ignores `modDependenciesByVersion`.** That is how `aoba.framework` came to be graded
   ELIMINATE while `aoba.fortress.industrial` hard-requires it for v1.6. Universe-wide, the only non-Harmony
   gaps are `aoba.framework` and `zetrith.prepatcher` (via krkr.rule56). Worth fixing in `assemble.py`.
3. **A rejected false-match source still fed the scores.** On techlevelenforcement the assessor dropped the
   MonoMod URL, but scored maintenance with MonoMod's push date. Its 433 MB "texture" figure is NuGet
   `icon.png` files under `Source/packages`, which diskfacts counts as textures.
4. **Owner rulings were missed, or cited at the wrong path.**
   - The 2026-09-11 Wave-4 permanent-resident KEEP (`design/Jawa/mods/mod_config_rulings.md:71`) is cited
     for regrowth, vfe.tribals and vmemese. It is not cited for alphabiomes, grimterra or morevanillabiomes,
     which it also names.
   - The 2026-09-02 lightsaber "STAYS UPSTREAM" card was left as an open question.
   - The 2026-09-11 Archon rename ruling was missed.
   - The mechanoid ruling is cited to `V2_DREAMS.md`, which does not contain it. It is in
     `design/Jawa/droid_ruling.md:190-194`.
5. **`retirement_cost.dependants` was filled with the wrong things:** dependencies (niceresearchtab,
   searchablemenus) and patchers (factionterritories).
6. **Def census blind spot:** the btd KotOR VGE pack declares 0 defs, but it has 7 defs in a folder gated by
   LoadFolders. jecstools shows 25 defs against 92 Defs XML files.

## The 10 highest-impact corrections

1. **`aoba.framework`: ELIMINATE is CHALLENGED, proposed KEEP.** `aoba.fortress.industrial` hard-requires it
   for v1.6, and our Armoury loads after Fortifications and references its defs 30 times. Unticking it would
   drop Fortifications at load.
2. **`vanillaracesexpanded.archon`: ELIMINATE is CHALLENGED, proposed PHASE-OUT plus a card.** The owner
   ruled on 2026-09-11 "Yes, draft them now", and `VREArchon_MortisRename.xml` rethemes the faction. Our
   `OnlyOurFactions.xml` also suppresses it, so our own patches pull both ways.
3. **`lee.theforce.lightsaber`: KEEP is now ruling-backed, and `card_worthy` goes to false.** The owner card
   of 2026-09-02 in `STARWARS_DONOR_SUNSET_1.md` says "STAYS UPSTREAM ... Do not absorb, do not retire."
4. **`jecrell.jecstools`: the real holder is our StarWarsPatches,** which loads after it and calls
   `JecsTools.PlaceWorker_Outline` for the absorbed blast doors. It is not only the lightsaber DLL.
5. **`grimterra.biomesmod` and `zylle.morevanillabiomes`: `card_worthy` false becomes true.** The 09-11
   permanent-resident ruling names both, which makes them the same conflict as regrowth.
6. **`sarg.alphabiomes`: add the 09-11 KEEP ruling to the card.** This is the largest biome donor, with
   1,155 refs from our mods.
7. **`btd.gbp.shippack.kotor.vge`: ELIMINATE still stands, but its retirement cost was understated.** Our
   Droidworks `BTD_DistressCall_Repoint.xml` (Ruling 13) patches its quest. The replacement,
   `DROIDWORKS_WILD_DROIDS_1`, is done, so the patch goes inert. Removing the pack also kills the remix
   pack's duplicate quest copy.
8. **`summersausages2ttv.techlevelenforcement`: memory severity 3 becomes 1 and maintenance 1 becomes 2.**
   Both scores came from false-match evidence (NuGet icons, MonoMod's push date).
9. **`leutiankane.mines2patchouterrim` and `mineablesor`: our own patches use both.** Our
   `TibannaEmbargo_CutMineableRoute.xml`, the UtinniPatches loadAfter and Armoury's
   `RSW_DurasteelConvert_OuterRim.xml` all depend on them. "Nothing of ours uses it" is false.
10. **`neronix17.outerrim.galacticempire`: `card_worthy` goes to false.** Its only open question, whether the
    faction is cut or kept for its armour, is already answered (brief §2, galactic-empire-is-reskinned-vanilla).

## Ruling conflicts found (for the owner card step)

- **2026-09-11 permanent residents vs 2026-09-20 port-everything.** One question covers six mods in this group:
  regrowth.botr.core, sarg.alphabiomes, grimterra.biomesmod, zylle.morevanillabiomes, vanillaexpanded.vmemese
  and oskarpotocki.vfe.tribals, plus Alpha Animals and Alpha Memes elsewhere. Today the same ruling yields
  KEEP for two of them and PHASE-OUT for four. That split is defensible: the four are biome donors on the
  paint-once port plan. It should still be one card, not six. Note that the ruling file's header says
  "Nothing here has been re-verified" (brief §5.9).
- **Better Infestations, ADOPT (2026-08-04) vs the planet-wide infestation ban (2026-09-24).** No src patch
  names `BI_SwarmingHorde`, `BI_InsectRaid` or `BI_WorldInfestation`, so the ban does not reach them. The
  card is valid as filed.
- **Archon, retheme vs suppress.** The Mortis rename (owner, 2026-09-11) and the `OnlyOurFactions` suppression
  both stand.
- **Already answered, so these should not be carded:** lightsaber (2026-09-02), the OuterRim Empire faction
  (cut, mod kept for its armour), and the spaceworms "six IncidentDefs" question (facts says 1).

## Not checked or left open

- **Placed Things in the save stay UNMEASURED for every ELIMINATE.** That covers beltextractors, the btd pack,
  fancyrats, beastsoftherim and fungoid, plus aoba and archon if they stay ELIMINATE.
- **Log attribution covers 100 of 344 error blocks.** Several "0 errors, MEASURED" rows are really "not
  attributed". Quarry is the case where the deploy record names an error that the probe did not attribute.
