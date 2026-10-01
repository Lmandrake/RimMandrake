# ABYSS_HIDDEN_SHIP_PROBES_1 — hidden-ship cover in the Abyss, with probe droids that still come and must be avoided

Biome: the Abyss (`RM_Abyss` in `src/RimMandrake/Abyss/`, composed into `mandrake.rm.biomes`; campaign twin `RUT_Abyss`). Review/spec: `design/Jawa/worldbuilding/biomes/blackcrags_bedazzle_review_2026-09-30.md` (written under the old names Forsaken Crags / Black Crags; paths there predate the rename). Owner rulings of volley turn 1 (2026-09-30): the sitting item `BLACKCRAGS_BEDAZZLE_SITTING_1` and the report's 'Turn 1 rulings' section. Rule: every mod ships Mod Settings; the free `RM_` tier carries invented content, canon only through Utinni (Q11a).

## spec

Owner typed 2026-09-30: *"Yes but probe droids will still come that must be avoided."*
A gravship landed in the Abyss slowly **vanishes from pursuit and orbit**: raids are slow to find the ship, trade ships cannot reach it, and starting the engine breaks the cover (report §5 item 5; concept: `design/Jawa/worldbuilding/hiding_the_gravship.md`, hiding must cost salvage/progress and must not be permanent).
**Exception that makes it a game:** probe droids still come and must be avoided (hidden is not safe). Existing content to build on, do not duplicate: Droidworks `probe droid`, `assassin probe`, `saboteur probe` PawnKindDefs (`src/RimStarWars/Droidworks/Defs/PawnKinds_KotOR.xml`, race `K-X12 utility probe droid` in `Races_KotOR.xml`), the EmpirePursuit sensor-shadow list `surveyShadowBiomes` (`src/RimUtinni/EmpirePursuit/Defs/Scenarios/ScenParts_EmpirePursuit.xml`, matcher in `RuthlessPursuingMechanoids.cs`; now lists `RUT_Abyss`, `RM_Abyss`, donor `AB_RockyCrags`). Probe droids belong to the campaign tier (Star Wars IP, Utinni layer), the cover mechanic to whichever tier the gravship hiding kit lives in. Decide where probes spawn from (search EmpirePursuit first) and how the player avoids them (stay still, stay cold and dark, shoot them down before they report).

## criteria

- Cover mechanic works on a landed gravship in the Abyss and breaks on engine start.
- Probe droid encounters still occur under cover and are avoidable; a reported probe collapses the cover.
- Mod Settings toggle for the cover; defaults = shipped.
- Note: `surveyShadowBiomes` correctness fix (names our defs) landed with the rename commit.

## verify

Offline build + selftests green; live proof is a joint session, never an unattended flyer/visual hunt.
