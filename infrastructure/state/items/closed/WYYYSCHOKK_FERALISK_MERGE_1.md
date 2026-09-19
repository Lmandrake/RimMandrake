# WYYYSCHOKK_FERALISK_MERGE_1

Owner sitting ruling, 2026-09-10 (`decisions_propagated.json` round2, keys
`fauna:the_forge:AA_Cinderlisk`, `fauna:the_forge:BMT_Maguana`,
`homeless:AB_Feralisk`, and the `Wyyyschokk` move-note): retire Alpha
Animals' whole `-lisk` clade, since the local name "Feralisk" belongs to
`Wyyyschokk` (canon Star Wars species, SWAC) by standing ruling
(`design/Jawa/worldbuilding/biomes/the_webwork.md` header: "Wyyyschokk to
the galaxy, Feralisk on this world").

## Thin item — what was assumed

The queue title read "Wyyyschokk duplicates AA_Feralisk's properties/attacks
(stats+verbs), then AA_Feralisk retires entirely" with no `## spec`, `##
verify` or `## criteria`. Read literally that could mean "copy AA_Feralisk's
combat numbers onto Wyyyschokk." Checked both defs before assuming that:

- `Wyyyschokk` (`mlie.starwarsanimalcollection`, canon Kashyyyk giant
  spider): baseBodySize 3.0, combatPower 600, lifeExpectancy 400, 4 tools
  (power 20/15/15/12), dormant-until-triggered ambush comps, shearable wool,
  its own SWAC-authored ability and biome placement already curated in this
  campaign (`RUT_Webwork.xml` commonality 0.4; independently evicted from
  wrong biomes in `BiomeCastEvictions_WildBiomes.xml`).
- `AA_Feralisk` (Alpha Animals): baseBodySize 1.00, combatPower 200,
  lifeExpectancy 12, 4 weaker tools (power 12/12/15/10).

Wyyyschokk is already a richer, more powerful, independently-placed
creature that already occupies the "giant venomous ambush spider" niche —
copying the *weaker* AA_Feralisk's numbers onto it would be a downgrade,
not a merge, and would fight the standing header ruling that already made
Wyyyschokk the canonical Feralisk before this item existed. **Assumed: "duplicates"
describes an existing fact (Wyyyschokk already covers Feralisk's thematic
role), not an instruction to copy stats — so no changes were made to
Wyyyschokk.** If that reading is wrong, reopen this item; Wyyyschokk's
current def is otherwise untouched.

## What was cut

Alpha Animals' whole `-lisk` clade, swept from `Races_Feralisk.xml` and its
sibling files by defName pattern (`*[Ll]isk*`) rather than the three names
named in the queue title, per "cut Cinderlisk, Maguana, AB_Feralisk and
**every other 'lisk**'". Plus their egg products (single producer each, all
producers cut) and their manhunter-encounter IncidentDefs. Plus the two
other-mod entries the sitting explicitly named.

Added to the **LIVE** Cherry Picker config (not `CherryPicker.SHIP.xml` —
see below), backed up first to
`Transient/Mod_CherryPicker_before_lisk_cull_2026-09-10.xml`:

```
ThingDef/AA_Feralisk
ThingDef/AA_FeraliskClutchMother
ThingDef/AA_FeraliskEggFertilized
ThingDef/AA_FeraliskEggUnfertilized
ThingDef/AA_FeraliskSuperEggFertilized
ThingDef/AA_Cinderlisk
ThingDef/AA_CinderliskEggFertilized
ThingDef/AA_Animalisk
ThingDef/AA_AnimaliskEggFertilized
ThingDef/AA_Dunealisk
ThingDef/AA_DunealiskClutchMother
ThingDef/AA_DunealiskEggFertilized
ThingDef/AA_DunealiskSuperEggFertilized
ThingDef/AA_Junglelisk
ThingDef/AA_JungleliskEggFertilized
IncidentDef/AA_IncidentAnimaliskEnters
IncidentDef/AA_IncidentDunealiskClutchMother
IncidentDef/AA_IncidentFeraliskClutchMother
ThingDef/BMT_Maguana
ThingDef/BMT_EggMaguanaFertilized
ThingDef/BMT_EggMaguanaUnfertilized
ThingDef/AB_Feralisk
```

1972 -> 1994 keys, confirmed with `cherrypicker.py --source live --is-cut`
on a spot sample. `ThingDef/AB_Feralisk` does not currently resolve
anywhere in the live 575-mod set (grepped the full Workshop tree, no hit) —
matches the roster's own note ("def had no register row, added for the
record"); the key is inert until/unless a future mod change ever ships it,
same as ~445 other keys already in the ratified list per `cherrypick_build.py`.

`AA_Blizzarisk`-family incident workers exist in the same donor file
(`Incidents_Map_Misc.xml`) but were left alone — "Blizzarisk" does not
contain the `-lisk` substring; it's a different word, a different clade,
not named by this ruling.

## Why the LIVE config, not `CherryPicker.SHIP.xml`

`CHERRYPICKER_SHIP_BASELINE_STALE_1` (blocked, needs-owner) already
established that SHIP is currently stale against LIVE by 617
added/178 removed, bundling an unconfirmed backstory un-cut. Re-baselining
SHIP now, or hand-adding these 22 keys to SHIP directly, would either
clobber tonight's other legitimate LIVE drift (Alpha Mechs research/recipe
cuts) or bake the disputed backstory reversal into a ratified file before
the owner confirms it. Editing LIVE directly sidesteps that dispute
entirely — these 22 keys take effect on the next load regardless of how
the SHIP question resolves, and become part of SHIP automatically whenever
that re-baseline eventually happens.

## The wildAnimals cross-reference sweep (would have broken mapgen)

Before closing, checked whether any of the 22 cut defNames still appear as
a **wildAnimals dictionary VALUE** (not the safe `race/wildBiomes` eviction
pattern) anywhere in this repo's own biome files — this project has already
been burned by exactly this class of bug
(`BIOME_CAST_REFS_BREAK_MAPGEN_1`, 2026-09-02): a single unresolved
cross-ref in a `BiomeDef.wildAnimals` list throws an `ArgumentNullException`
in `CommonalityOfAnimal`'s cache build the first time anything asks that
biome for a commonality, breaking every mapgen path that touches it.

Found and fixed **10 live dictionary entries** across 3 files (all confirmed
gone by a follow-up sweep, and all 3 files re-validated at 0 errors against
the live 575-mod set):

- `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_TheForge.xml` — removed
  `AA_Cinderlisk` and `BMT_Maguana` from `wildAnimals`.
- `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_ExtremeDesert.xml` —
  removed `AA_Dunealisk` from `wildAnimals`.
- `src/RimUtinni/UtinniPatches/Patches/BiomeCast_Ashkarr.xml` — removed
  `AA_Dunealisk` from `ExtremeDesert`'s cast; removed `AA_Cinderlisk` from
  three donor biomes' casts (`AB_PyroclasticConflagration`, `LavaField`,
  `Volcano`); removed three now-empty `PatchOperationConditional` blocks
  whose SOLE entry was `BMT_Maguana` (same three donor biomes) rather than
  leaving an empty shell operation behind.

`AA_Feralisk` itself was never placed in this repo's own wildAnimals lists
(Wyyyschokk already fills that role) — nothing to remove there. The
`race/wildBiomes` eviction-style patches in
`BiomeCastEvictions_WildBiomes.xml` (dozens of hits) are a DIFFERENT,
harmless pattern: `PatchOperationRemove` against a target `ThingDef` that
no longer exists simply matches nothing once Cherry Picker cuts it — not a
cross-reference resolution, no risk.

## verify

Next full-list game load: `Player.log` prints `[Cherry Picker] The database
was processed in ... the following defs were removed:` with all 22
`- <DefType>/<defName>,` lines present (18 will show; `AB_Feralisk` will
not, since it never resolved to begin with — that's expected, not a
failure). No `Could not resolve cross-reference` naming any of the 22, and
no `ArgumentNullException` in `CommonalityOfAnimal` when generating a map
on The Forge, the Extreme Desert, or any biome touched by
`BiomeCast_Ashkarr.xml`'s edited operations.
