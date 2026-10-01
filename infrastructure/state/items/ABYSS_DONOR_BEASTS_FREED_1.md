# ABYSS_DONOR_BEASTS_FREED_1 — ghorrumak and nighthrumbo/zhurrakor become our own creatures, zero donor dependency

Biome: the Abyss (`RM_Abyss` in `src/RimMandrake/Abyss/`, composed into `mandrake.rm.biomes`; campaign twin `RUT_Abyss`). Review: `design/Jawa/worldbuilding/biomes/blackcrags_bedazzle_review_2026-09-30.md` section 8 (turn 2 rulings, 2026-10-01 07:24 PDT; the report predates the rename). Sitting: `BLACKCRAGS_BEDAZZLE_SITTING_1`. Rule: every mod ships Mod Settings; the free `RM_` tier carries invented content.

## spec

Owner, typed (turn 2, 2026-10-01): "Fully regenerate art and names for those two beasts. No donor dependencies tolerable. Free us."

**Interpretation to confirm with him (BENCH):** "those two beasts" is read as the two donor-bodied creatures in the card's housekeeping question: the ghorrumak (donor `AA_Behemoth`) and the nighthrumbo / zhurrakor (donor `GR_Nighthrumbo`), both roster-placed but wired into neither def. If he meant cindermare and skarnix instead, those are already invented and covered by `ABYSS_INVENTED_CREATURES_TO_RM_1`.

Build: two NEW invented creatures in the RM_ tier (new invented names, not ghorrumak/zhurrakor/behemoth/nighthrumbo), own ThingDef/PawnKindDef/race (no ParentName or graphic from a donor mod, no donor texPath), fully regenerated art (all three facings), wired into `RM_Abyss` and `RUT_Abyss`, with no `MayRequire`/patch dependency on the donor mods. The giant is the storm-call beast of `ABYSS_DARK_BUILD_1` (alien megafauna, never a dragon, no fire breath) (its thunder in Witchfire storms): that item must point at the new def, not `AA_Behemoth`.

## already built (found 2026-10-01, cited so nothing is re-invented)

- No absorbed port of either exists in `src/`: the only references are the rename patch `src/RimUtinni/UtinniPatches/Patches/Abyss_Rename.xml` (relabels the DONOR defs `AA_Behemoth`, `GR_Nighthrumbo`), `AnimalTolerances_Ashkarr.xml`, `MegafaunaYield.xml` and `BehemothArtUpres_StarWarsAnimalCollection.xml` (all donor-keyed). `DONOR_DEFS_PORT_TO_OURS_1` (open) is the campaign-wide port item both feed.
- Art exists only of the DONOR-bodied versions: artpipe `crags_ghorrumak_{south,east,north}` and `crags_zhurrakor_{south,east,north}` (source `DONOR_DEFS_PORT_TO_OURS_1`). It does NOT count: the owner confirmed "fully regenerate" means new art under the new names (review §9). Fresh jobs are on the Abyss art list.
- Roster rows: `design/Jawa/worldbuilding/biomes/noncanon_beast_names_crags_nightside_contagion_slime.md` and the report's section 4.

## criteria

- New names chosen (proposed in `design/Jawa/worldbuilding/biomes/abyss_cast_bible_2026-10-01.md` §5, owner to confirm; note the chosen ones here), defs in `src/RimMandrake/Abyss/`.
- Art regenerated and validated per facing.
- Zero donor packageId/defName in the Abyss defs for these two.

## verify

Offline build + selftests green; sweep `src/RimMandrake/Abyss` for `AA_`/`GR_` prefixes.
