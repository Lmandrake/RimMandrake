# YOBSHRIMP_DEFNAME_COLLISION_1

## Found

During DIRTY_CODE_REVIEW_STANDING_LOOP_1 full-file review of
`src/RimStarWars/SWBestiary/Defs/SeaBeasts/ThingDefs_Races/SeaBeasts_NurseryJuveniles.xml`
(reviewing `RSW_YobshrimpJuv`'s `ParentName="RSW_Yobshrimp"`).

## Mechanism

Two SEPARATE `ThingDef`s, and two separate `PawnKindDef`s, are both defined with
`<defName>RSW_Yobshrimp</defName>` inside the same mod (`mandrake.rsw.swbestiary`):

- `src/RimStarWars/SWBestiary/Defs/SeaBeasts/ThingDefs_Races/SeaBeasts_Swarm.xml`
  line 10 (`ThingDef ParentName="AnimalThingBase" Name="RSW_Yobshrimp"`, label
  "pale yobshrimp") and line 84 (`PawnKindDef ... Name="RSW_Yobshrimp_Kind"`,
  defName `RSW_Yobshrimp`) — the aquatic SeaBeasts swarm variant.
- `src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Yobshrimp.xml` line 41
  (`ThingDef ParentName="AnimalThingBase" ADogSaidBody="LegsTail"`, NO `Name=`
  attribute, label "yobshrimp") and line 159 (`PawnKindDef`, defName
  `RSW_Yobshrimp`) — a land crustacean added later by the MLIE_FAUNA_ABSORPTION_1
  Wave C absorption pass, which evidently never checked for a collision with the
  earlier SeaBeasts merge.

`DefDatabase<T>.AddAllInMods()` (`Verse/DefDatabase.cs`, decompiled reference at
`/mnt/d/Luke/dev/reference/rimworld-decompiled/Verse/DefDatabase.cs` lines 20-40)
builds a per-mod `HashSet<string>` of defNames across ALL of that mod's own XML
files before adding any of them to the database. The second `ThingDef`/
`PawnKindDef` it enumerates with the colliding defName fails `hashSet.Add(...)`
and is **silently skipped entirely** — logged as `Mod <X> has multiple ThingDefs
named RSW_Yobshrimp. Skipping.`, never added to `DefDatabase<ThingDef>` at all
(not even the "add with a randomized suffix" path `DefDatabase<T>.Add` takes for
a same-defName collision from DIFFERENT mods). Enumeration order across a single
mod's own def files was not established this pass (would need a fresh def-dump
load-order check) — this item does not know which of the two currently survives,
only that exactly one of them is silently absent from every load right now.

## The ParentName inheritance itself is NOT ambiguous

`RSW_YobshrimpJuv`'s `ParentName="RSW_Yobshrimp"` resolves at the earlier
XML-inheritance stage, which matches on the `Name=` XML attribute, not
`defName`. Only `SeaBeasts_Swarm.xml`'s ThingDef carries `Name="RSW_Yobshrimp"` —
`RSW_Yobshrimp.xml`'s ThingDef has no `Name=` attribute at all, so it can never
be a `ParentName` target. `RSW_YobshrimpJuv` unambiguously inherits from the
aquatic SeaBeasts swarm variant. The live bug is purely the defName-registration
collision, not the inheritance.

## Evidence the split is intentional, not an accident to merge away

`src/RimUtinni/UtinniPatches/Patches/BiomeCast_Ashkarr.xml` (generated,
**do-not-hand-edit** per this file's own DEPLOY/generator convention) already
carries TWO separate `<RSW_Yobshrimp>` wildAnimals entries in two different
biome blocks, under different comments:

```
line 271:  <RSW_Yobshrimp>0.3</RSW_Yobshrimp> <!-- pale yobshrimp - nursery, import -->
line 285:  <RSW_Yobshrimp>0.8</RSW_Yobshrimp> <!-- yobshrimp - arthropod-floor, import -->
```

The generator's own source data (`design/Jawa/fauna/` cast assignment) already
treats these as two distinct species that happen to share a defName — the
comments track the SeaBeasts nursery variant separately from the arthropod-floor
land variant. This is a naming collision to FIX, not a duplicate to delete.

## Other referencers found (repo-wide grep for bare `RSW_Yobshrimp`, excluding
`RSW_Yobshrimp_Kind`/`RSW_YobshrimpJuv`)

- `src/RimStarWars/SWBestiary/Defs/Bodies/RSW_MlieWaveC_Bodies.xml:10264` — a
  `BodyDef` named `RSW_Yobshrimp` ("clawed crustaceous animal"). BodyDef is a
  separate DefDatabase<T> from ThingDef/PawnKindDef, so this does NOT collide
  with either ThingDef — flagged only so the eventual rename keeps this BodyDef
  paired with whichever ThingDef it actually belongs to (reads as the land one,
  by description).
- `src/RimStarWars/SWBestiary/Defs/ThingDefs_Items/RSW_MlieWaveC_Resources.xml:2659`
  — `<hatcherPawn>RSW_Yobshrimp</hatcherPawn>` (Wave C egg/hatcher item).
- `src/RimStarWars/SWBestiary/art/SeaBeasts/tools/sea_creatures.py:202` — art
  tooling keyed on `("RSW_Yobshrimp", "pale yobshrimp", ...)` — the SEA variant.
- `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Miasma.xml` — also references
  `RSW_Yobshrimp`; not yet checked which variant it means.
- `design/Jawa/fauna/BiomeCast_Ashkarr.xml` — the design-side copy of the
  generated patch above (same generated-do-not-hand-edit status).

## Fix shape (not done this pass — needs the generator, not a hand-edit)

1. Rename ONE pair (recommend the Wave-C land ThingDef+PawnKindDef in
   `RSW_Yobshrimp.xml`, e.g. to `RSW_YobshrimpLand`) and its own BodyDef.
2. Update `RSW_MlieWaveC_Resources.xml`'s `hatcherPawn` and any other same-file
   cross-references to match.
3. Check `RUT_Miasma.xml`'s reference and correct it to whichever variant it
   actually means.
4. Update the generator's own source data (design/Jawa/fauna's cast-assignment
   input, whatever feeds `gen_cast_patch.py`) so the arthropod-floor wildAnimals
   entry emits the renamed defName, THEN regenerate
   `BiomeCast_Ashkarr.xml` via the real generator — never hand-edit either
   committed copy (design/ or src/RimUtinni/UtinniPatches/Patches/).
5. Confirm via a fresh def dump (not a grep) which ThingDef/PawnKindDef pair is
   CURRENTLY the one DefDatabase kept, since the other has been silently absent
   from every load until this rename lands — that pawn kind may need a
   from-scratch reintroduction to biomes/trade rather than "restoring" something
   that was ever actually reachable in play.

## Status

**FIXED 2026-09-19.** Renamed the Wave-C land ThingDef/PawnKindDef/BodyDef to
`RSW_YobshrimpLand`. No existing suffix convention was found among sibling
Wave-C ports (they're all a bare `RSW_<DonorName>` rename with no
disambiguating suffix — this is apparently the first same-mod defName
collision this mod has hit), so `RSW_YobshrimpLand` was chosen as the
clearest label for "the terrestrial one" per the item's own suggestion.

Per-step results:

1. **Done.** `src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Yobshrimp.xml`:
   ThingDef defName, `<race><body>`, PawnKindDef defName and `<race>` all
   renamed `RSW_Yobshrimp` → `RSW_YobshrimpLand`. Header comment updated (was
   citing the old BodyDef name) and a dated addendum added recording this fix.
   `src/RimStarWars/SWBestiary/Defs/Bodies/RSW_MlieWaveC_Bodies.xml:10264`
   BodyDef defName renamed to match.
2. **Done.** `RSW_MlieWaveC_Resources.xml:2659` `<hatcherPawn>` repointed to
   `RSW_YobshrimpLand`. No other same-file cross-references found.
3. **Checked, no change needed.** `RUT_Miasma.xml` does NOT contain a bare
   `RSW_Yobshrimp` reference — its "arthropod-floor, import" wildAnimals entry
   (line 215, commonality 0.8) uses the DONOR's own bare `Yobshrimp` defName
   gated `MayRequire="mlie.starwarsanimalcollection"`, a third, unrelated
   entity from the live donor mod itself, not either RSW_ pair. Its only RSW_
   reference is `RSW_YobshrimpJuv` (line 226, the aquatic nursery juvenile),
   which is correct as-is. `validate_patch.py` confirms 0 errors/warnings.
4. **Done, scoped.** `design/Jawa/fauna/cast_assignment.csv` row 17 (biome
   `AB_MiasmicMangrove`, band `arthropod-floor`, the land port) updated to
   `RSW_YobshrimpLand`. Ran the real generator
   (`python3 design/Jawa/fauna/gen_cast_patch.py`) — it correctly REFUSED to
   emit the renamed entry (today's freshest capture, `2026-09-19T04-19-13Z`,
   predates this rename and has no `RSW_YobshrimpLand` PawnKindDef yet, so the
   generator's own resolve-against-live-dump check skipped it rather than
   emit something unresolvable). The full regen also produced a large,
   unrelated diff against both committed `BiomeCast_Ashkarr.xml` copies (the
   underlying capture/cast data has drifted independently since either file
   was last generated — reordered/renamed entries across many other species,
   nothing to do with yobshrimp) that is **out of scope for this item and was
   NOT committed**. Instead, made the single scoped edit both a clean regen
   would produce for this one entry: `<RSW_Yobshrimp>0.8</RSW_Yobshrimp>
   <!-- yobshrimp - arthropod-floor, import -->` →
   `<RSW_YobshrimpLand>0.8</RSW_YobshrimpLand>` (same comment, same value) in
   both `design/Jawa/fauna/BiomeCast_Ashkarr.xml` and
   `src/RimUtinni/UtinniPatches/Patches/BiomeCast_Ashkarr.xml`, confirmed via
   `git diff` to be exactly a 1-line change in each file. The nursery entry
   (`RSW_Yobshrimp` 0.3, aquatic) was left untouched — it now correctly
   resolves to the aquatic pair once this rename lands.
   ⚠️ Whoever next runs `gen_cast_patch.py` for an unrelated reason will pick
   up BOTH this cast_assignment.csv fix AND the large independent drift
   flagged above in the same regen — that drift should get its own review
   pass, not be nodded through as part of this collision fix.
5. **Determined.** A fresh def dump already existed on disk from today's
   restart-validation cycle (`.../DefDump/captures/2026-09-19T04-19-13Z`,
   captured before this rename). Querying it directly: `RSW_Yobshrimp`
   resolved to exactly one ThingDef (label "yobshrimp", body `RSW_Yobshrimp`
   matching the now-renamed BodyDef) and one PawnKindDef (label "yobshrimp")
   — **the LAND crustacean was the one DefDatabase kept; the aquatic "pale
   yobshrimp" SeaBeasts swarm pair was the one silently absent from every
   load until this fix.** No from-scratch reintroduction is needed for the
   aquatic pair's biome/trade wiring: `BiomeCast_Ashkarr.xml`'s nursery
   wildAnimals entry (`RSW_Yobshrimp` 0.3, `AB_MiasmicMangrove`) was already
   present and unchanged by this fix, so it starts resolving to the aquatic
   pair the next time the mod loads with these changes deployed. One real
   gap found in passing, NOT fixed here (outside this item's scope — a
   content/balance call, not a collision fix): the aquatic ThingDef
   (`SeaBeasts_Swarm.xml`) has no `<tradeTags>` block, unlike the land one
   (`AnimalUncommon`), so it won't be purchasable/sellable via traders even
   once it starts spawning.

`validate_patch.py` (full mod folder + `--live` against the 2026-09-19T04-19
capture): all four touched def files
(`RSW_Yobshrimp.xml`, `RSW_MlieWaveC_Bodies.xml`, `RSW_MlieWaveC_Resources.xml`,
`BiomeCast_Ashkarr.xml`) report **0 errors, 0 warnings**. The mod-wide
FAIL TOTAL (77 errors/54 warnings) is pre-existing and unrelated (missing
textures for other creatures such as Wyyyschokk/Zakkeg/Zeer, an unrelated
`RSW_SWanimals_RawMeatBase` ParentName gap) — none of it touches yobshrimp.

Closed.
