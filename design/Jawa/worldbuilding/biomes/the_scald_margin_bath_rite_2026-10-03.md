# The Margin Bath: a found rite for the Scald (SCALD_BATHING_RITE_1, 2026-10-03)

_Status: FOUNDRY design, nothing built, nothing deployable yet. Source ruling: sitting agenda
`the_scald_floor_sitting_agenda_2026-10-02.md` Q4 (b), "a bathing rite for the water pilgrims at the cool
margins; waits on the margin cove". Sheet image: `the_scald.md` §7 "The baths", §8 "The two-faith shore"._

## Where it lives, and why
**`mandrake.rut.rites` (`src/RimUtinni/Rites/`), RUT tier, and nowhere else.** The register
(`salvation_rites_2026-10-01.md` (a)) rules that every Salvation rite, found rites included, has exactly one
home there, and that a biome mod holds only the free-tier physics a rite reads. A rite names a god, and an
`RM_` mod may not (tier grammar); the Scald's terrain/vents are already in `TerminalBiomes`
(`RUT_ScaldMargin`, `HotSpring` thought) and stay there untouched. Repo search (2026-10-03): no found rite,
inscription, `RUT_ResearchMod_GrantRite` or `RitualPatternDef` exists yet in `src/` (only `RUT_TheReturn.xml`,
another faith's rite, and SacredGraffiti's Dark Vigil outcome). So this item produces the design and the
register row; the code arrives with the shared found-rite machinery, in that mod.

## The rite: The Margin Bath
- **God and kind:** Ta'Baa the Unrooted, consolation. Why not Oomo (the obvious water god): Oomo carries five
  found rites, the cap (B16). Why Ta'Baa: the sheet calls the baths a *pilgrimage* (a leaving, then a
  washing-off), Ta'Baa has three found rites and no water one, and the Scald has no other rite, so no kind
  repeats in the biome. **Owner may reassign; this is the one real choice.**
- **Needs (the gate):** participants stand in `RUT_ScaldMargin` cells (the sealed cool cove), no
  boil-suit or armor worn (apparel is the only thing they set down; it is placed beside the water, not
  consumed), at least three participants, ritual leader any adult. The cove must be unreachable across open
  boil (the terrain file's own map-authoring constraint), so the gate cannot be satisfied on a boil cell.
- **Found:** a pilgrim's bathing-stone at the cove's land edge, scratched with a drawn vessel and the
  line *"the sea burns, the margin forgives"*. Studied in place via `CompStudiable` (register (d)).
- **Outcomes (four vanilla tiers; no hediff, no heat, no power):** Poor, the cove is crowded or hot weather
  spoils it: ordinary `HotSpring` thought only. Fair, a lasting memory "washed at the margin". Good, plus a
  small mood for every participant who arrived by launch within the last 15 days ("the road washed off").
  Excellent, plus one participant's lingering injury-pain mood is eased. Ninefold: `ApplyDelta(Ta'Baa)` up,
  sized by that arrival count. Nothing vanishes without a sign: set-down gear is a visible pile.
- **Laws checked:** one kind of heat (reads vanilla temperature; adds no hediff); no fantasy power; the Forge's
  rim site and the Anvil Gift stay Sh'kaar's, the two-faith shore keeps both churches (this rite never mentions
  the forge).

## Dependencies and honest unknowns
- **Waits on the margin cove being placed** (map painting is the end pass, S3 in the sitting). Nothing here
  forces it; the rite's gate reads the terrain wherever it appears.
- Shared machinery not yet built: found-rites research row, `RUT_ResearchMod_GrantRite`, per-condition
  `RUT_RitualConditionDef`. `AddPrecept(init:true)` at runtime filling obligations is UNMEASURED (register (d)).
- Whether pawns can stand/bathe in a sealed cove at all (`JoyGiver_GoSwimming`, KnownDangerAt) is UNMEASURED live.
- Art: none owed now (a stone inscription sprite later; artpipe searched for "bath" and "scald": only
  unrelated creature/blanket jobs).
