# SUMP_GASLIGHT_1 — the gaslight economy: tar + acid → green gas → the warbling light

Owner rulings 2026-09-24, typed in chat at the Sump sitting. The founding ruling,
verbatim (answering a proposal to offset filth mood with burning-wick lamplight):

> "Yes but beef not up. Burning tar doesn't sound great for smoke and stink and
> there are many other oils. So the tar should be easily processed into a special
> oil with unusually beautiful properties. I'm thinking more gas here. There are
> green gas geysers that have their own economy already present in this mod stack.
> They were supposed to be present near the terminator right where the sump tends
> to be. So perhaps we can leverage that. Gaslight from the green gas geysers has
> the property you are speaking of. And tar, processed a certain way, can make this
> gas. Ah! By reacting it with some acid, the same as used for cleaning. That's how
> the cleaner works. So mixing a bit of the two in a lamp produces an unusually
> beautiful light. And we should implement that light too. A dancing, pulsing,
> beautifully warm light that warbles between adjacent colors. Nice! One could
> imagine not just lamps for this but a line of statue art driven by artistic skill
> where the flames come out of various parts of the statue and are shown. I'm
> really liking this. That could be a holy act to the evil sun god. There should be
> places in the map where this is happening naturally, little dancing beautiful
> flames to inspire the characters to realize this. Perhaps a technology they
> realize upon first meeting one of these flames."

Follow-ups, same sitting, typed: the green gas is Helixien (Vanilla Helixien Gas
Expanded, adopted 2026-08-10 — `design/Jawa/proposals/tar_pits_deep_design.md`
§3B(5)) and **the free mod may require it** — *"It is ok for the free mod to
require other mods. It is free of the utinni scenario and Star Wars entanglement
that's all. But the utinni layer should rename it to our own form of gas. Let's
call it Sumpgas."* (rename is `SUMP_UTINNI_LAYER_1`'s). Discovery scope: *"Yes
pilot here (the flickering light or geyser both can teach) and some specific tech
will unlock when meeting tar. I should not say unlock trees that may be, but often
it will just be specific technologies."* Statues/worship split ruled by card:
flame statuary ships RM-tier; the holy-act-to-the-evil-sun-god meaning is an
Utinni ideoligion patch (`SUMP_UTINNI_LAYER_1`).

## spec

1. **The reaction**: tar + acid → green gas (Helixien-compatible). One acid, three
   uses — this reaction IS how the cleaner works (cleaning tar converts it to
   gas), it is how vault extraction works (`SUMP_TAR_VAULT_1`), and a small
   tar+acid mix in a lamp is the light. Weak acid renders from thrummel seepwax —
   ruled generous: *"one raid should give you a lot. Not meant as a starvation
   mechanism."* Strong acid arrives by trade (Poison Forest,
   `BIOME_NUISANCE_NORMALIZATION_1`).
2. **The warbling light — implement the light itself**: dancing, pulsing,
   beautifully warm, warbling between adjacent colors. A glower whose color/
   radius animates (small comp; check `BiomeGlowMultiplierExtension` and existing
   glower patterns in `mandrake.rm.environmentalhazards` before new C#).
3. **Gaslight lamps**: fueled by the mix; the biome's mood answer — warm lamplight
   offsetting the squalor a Sump colony cannot escape.
4. **Flame statuary**: an art line driven by artistic skill where flames issue from
   parts of the statue — quality scales the fire show. RM-tier, secular.
5. **Natural flames**: map features where seep gas burns on its own — little
   dancing flames. These and the geysers are the discovery triggers.
6. **Discovery pilot**: witnessing a natural flame or geyser unlocks the gaslight
   chemistry tech; first meeting tar unlocks a specific tar tech. Specific
   technologies, not trees (his ruling). Engine shape: hidden research +
   discovery comp (Anomaly's encounter-unlock is the precedent). Planet-wide
   generalization is GATED: `INDIGENOUS_TECH_REVISIT_1`.
7. **Ship-buildable** (`BIOME_SHIP_CONTRIBUTIONS_1`): the lamps and statues are
   buildable aboard the gravship — the burning statues are one of the owner's two
   named ship gifts from this biome.

## verify

Quicktest: the reaction recipe runs; a lamp casts visibly animated warm light that
warbles; a statue's flame display scales with art quality; a natural flame exists
on Sump maps and its first witness fires the tech unlock letter; all
feature-gated in Mod Settings.

## criteria

The Sump's answer to permanent dusk and permanent filth is the most beautiful
light on the planet — made from its two nastiest substances.

## build status — FOUNDRY, 2026-09-24, pieces 1-4 offline-complete, needs live proof

Pieces 1-4 (the mechanical core, per this build pass's own brief) built, offline-
validated, and deployed this pass. Pieces 5-7 deferred, per spec.

**1. The reaction** — `RM_RecipeDef_HediffByproduct.cs` / `RM_Recipe_
RemoveHediffWithByproduct.cs` (mandrake.rm.environmentalhazards): a generic
RecipeDef/RecipeWorker pair (not Sump-specific) that spawns a configurable
byproduct Thing on a successful hediff removal, reading pre/post `HasHediff`
state rather than trusting a void return to detect surgery failure.
`RUT_Tarred_Surgery.xml` repointed from plain `Recipe_RemoveHediff` to this pair
(Class + workerClass both changed, MayRequire moved onto the whole RecipeDef) —
scrubbing off tar now spawns 1-2 `RUT_Sumpgas`. `RUT_Sumpgas.xml` (new resource
ThingDef, UtinniPatches) carries its own `recipeMaker` (Bitumen + WeakTarSolvent
-> 3 Sumpgas at TableMachining, gated behind the new `RUT_GaslightChemistry`
research) — "one acid, three uses" now covers two of the three (cure + craft);
`SUMP_TAR_VAULT_1` owns the third. "Helixien-compatible" investigated, not
assumed: the live def dump's own `VHGE_Helixien` (vanillaexpanded.helixiengas,
active) carries `CompProperties_CompDestroyOnSpawn` — an internal scatter/
pipenet-feed marker that deletes itself on spawn, not a haulable crafting
product — so `RUT_Sumpgas` is its own real stackable ThingDef (same green-gas
flavor/name) rather than a disguised `VHGE_Helixien`. Literal PipeSystem/
`VHGE_HelixienNet` interop is flagged NOT built — would need that mod's
`CompResourceTrader` wiring studied live, out of scope for an offline pass.

**2. The warbling light** — `RM_CompProperties_WarblingGlow.cs` / `RM_Comp_
WarblingGlow.cs`: a sibling ThingComp (not a CompGlower subclass) that reads a
sibling `CompGlower`'s own base color/radius and warbles hue ±18° and radius/
brightness on two independent, phase-offset sine waves, verified against
`Verse/CompGlower.cs` and `Verse/GlowGrid.cs` (both read in full) — `GlowColor`'s
setter re-registers itself; `GlowRadius`'s setter does not, so the comp calls
`CompGlower.ForceRegister(map)` explicitly whenever radius actually changes.
`qualityScalingEnabled` reads a sibling `CompQuality` (0.5x Awful .. 2x
Legendary) with no duplicate quality tracking, driving piece 4's "quality
scales the fire show" for free. Gated by new Mod Settings `warblingGlowEnabled`
+ `warblingGlowSpeedMultiplier`. `BiomeGlowMultiplierExtension`/
`BiomeGlowPatches` (checked first, per the item's own instruction) is a
whole-map Harmony darkness multiplier, confirmed NOT reusable for a per-Thing
animated light.

**3. Gaslight lamps** — `RUT_GaslightLamp.xml` (UtinniPatches, RUT-tier per the
existing "RM_TheSump doesn't exist yet" stopgap): `CompProperties_Glower` (warm
amber base) + the new WarblingGlow comp + `CompProperties_Refuelable` (fuel
`RUT_Sumpgas`, cribbed from `RUT_DryAirBlower.xml`'s own fueled-building shape)
+ `CompProperties_Flickable`. Mood-positive via a real vanilla mechanism, not
new code: `Beauty` statBase 14 (well above a torch), feeding vanilla's own
room-beauty mood family — "offsets squalor" needed no bespoke ThoughtDef.
Gated behind `RUT_GaslightChemistry` research.

**4. Flame statuary** — `RM_FlameStatuary.xml` (EnvironmentalHazards' own
Defs/, RM-tier per the statues/worship split ruling — this mod already ships
RM_-content directly, `RM_Leachmoss`/`RM_Venomvine` precedent). Ground truth
for the sculpture shape read from `Data/Core/Defs/ThingDefs_Buildings/
Buildings_Art.xml` (ArtBuildingBase/SculptureBase, read in full) rather than
`ParentName`-inherited — RimWorld XML list-field inheritance REPLACES a
parent's `<comps>` entirely the moment a child declares its own, and nothing
in this repo demonstrates a safe way to add a comp on top of an inherited
`<comps>` list, so every field (thingClass Building_Art, CompQuality,
CompProperties_Art with vanilla's own `NamerArtSculpture`/
`ArtDescription_Sculpture`, the TableSculpting recipeMaker shape,
stuffCategories/costStuffCount) is declared explicitly. WarblingGlow comp has
`qualityScalingEnabled=true` — "flames issue from the statue, quality scales
the fire show" is the animated glow itself scaling with `CompQuality`, no
duplicate mechanism. A literal `FleckMaker.ThrowFireGlow` particle lick is
flagged as the honest next visual step, NOT built this pass (cosmetic-only,
time budget went to the four mechanical pieces first).

**Deferred, per this pass's own brief:**

- **5. Natural flames** — NOT built. A ThingDef reusing the same WarblingGlow
  comp would be cheap, but real map-gen SCATTER placement (where/how it
  appears on a Sump map) needs a verified vanilla mechanism this pass did not
  study (risk of guessing the wrong GenStep wiring, the exact failure this
  item's own brief and CLAUDE.md's "never guess a RimWorld API" both warn
  against). No stub def created — recorded here instead, honestly, rather than
  a half-built placeholder that implies more than it delivers.
- **6. Discovery pilot** — STUBBED, per the item's own explicit fallback
  instruction. Two ordinary (not hidden, not auto-completing)
  ResearchProjectDefs in `RUT_Sump_Research.xml`: `RUT_GaslightChemistry`
  (real — gates `RUT_Sumpgas`'s own recipe, piece 1) and `RUT_TarRendering`
  (defined but deliberately UNWIRED to anything, so as not to retroactively
  gate `SUMP_TAR_NASTINESS_1`'s already-shipped recipes). The auto-complete-
  on-first-encounter mechanism (Anomaly's discovery-comp precedent) is NOT
  built — verifying that C# against the live decompile/a bridge test was out
  of scope for an offline-only pass, and generalizing it is explicitly gated
  to `INDIGENOUS_TECH_REVISIT_1` anyway.
- **7. Ship-buildable** — NOT touched, per the item's own instruction to defer
  entirely. Flagged here: once `BIOME_SHIP_CONTRIBUTIONS_1` lands, both
  `RUT_GaslightLamp` and `RM_FlameStatuary` should be reviewed for the
  ship-buildable flag it introduces — the burning statues are one of the
  owner's two named ship gifts from this biome.

**Validated offline**: `dotnet build RM_EnvironmentalHazards.csproj -c Release`
— 0 warnings/errors (4 new .cs files + csproj entries + 2 new Mod Settings
toggles + checkbox/slider + view-height bump). `validate_patch.py` against the
live 621-mod set (Data+Workshop+Mods) on all 5 new/touched XML files: 0 errors,
0 warnings on every file — the two "info" lines (`RUT_Tarred_Surgery.xml`,
`RUT_GaslightLamp.xml`, `RM_FlameStatuary.xml` each naming an unresolvable-to-
the-validator own-assembly Class) are the expected, harmless shape this repo's
validator always gives a mod that "ships Assemblies/" (same as
`SUMP_TAR_NASTINESS_1`'s own build note), not errors.

**Deployed**: `deploy_custom_mods.py --apply --mod EnvironmentalHazards --mod
UtinniPatches`. UtinniPatches: 9 files written (`+`/`~`, all new/touched XML +
2 new placeholder textures + the pre-existing `WildAnimals_Greentide.xml`
comment fix riding along), `-> VERIFIED in sync`. EnvironmentalHazards: the new
`RM_FlameStatuary.xml` + its texture deployed and verified in sync, but
`Assemblies/RimMandrake.EnvironmentalHazards.dll` **FAILED to write** —
`RimWorldWin64.exe` is confirmed running right now (`tasklist`, PID present)
and holds the DLL locked, the documented "assemblies cannot be written while
the game runs" limitation, not a bug. 🔴 **So the four new C# classes (both
WarblingGlow classes, both byproduct-recipe classes) are NOT yet in the live
deployed assembly** — the currently-running game's copy of the DLL predates
this pass. The new/changed XML is deployed and would resolve those classes
correctly once the DLL catches up, but until a shutdown window lets the
assembly redeploy, loading a save against the CURRENT mixed state (new XML +
old DLL) would drop `RUT_ScrubTarred`, `RUT_GaslightLamp` and
`RM_FlameStatuary` silently (unresolvable Class discards the whole def) —
**do not load a save before the DLL redeploys.**

Texture: all three new content pieces (`RUT_Sumpgas`, `RUT_GaslightLamp`,
`RM_FlameStatuary`) ship simple procedurally-drawn placeholder art, same
posture as `SUMP_TAR_NASTINESS_1`'s own new resources — real (hand-authored,
reviewed) art is still owed.

**What a live proof needs** (no bridge access this pass):

1. A shutdown window to redeploy `Assemblies/RimMandrake.EnvironmentalHazards.
   dll` — required before ANY of this item's content can load at all.
2. Confirm `RUT_ScrubTarred` still appears on a tarred pawn's health-tab
   operations list and, on completion, spawns 1-2 `RUT_Sumpgas` near them
   (this item's own new byproduct wiring — not yet confirmed to fire in a
   live game).
3. Confirm `RUT_Sumpgas`'s bench recipe appears at TableMachining once
   `RUT_GaslightChemistry` is researched and `RUT_Bitumen`/`RUT_WeakTarSolvent`
   are in inventory.
4. Confirm `RUT_GaslightLamp` actually animates in-game — color visibly
   warbling through adjacent hues, radius visibly pulsing — not just that it
   glows. `RM_Comp_WarblingGlow`'s own correctness (does `GlowColor`'s
   auto-reregister and the explicit `ForceRegister` call after a radius change
   actually repaint the glow grid smoothly) is unconfirmed outside the
   `dotnet build`'s clean compile.
5. Confirm `RM_FlameStatuary` is craftable at a TableSculpting bench, takes a
   quality roll, and that its flame visibly dances harder at higher quality
   (the `qualityScalingEnabled` path specifically — untested at runtime).
6. Confirm the two `researchPrerequisites`/`researchPrerequisite` gates
   (`RUT_GaslightChemistry` on both the lamp and the Sumpgas recipe) actually
   block/unlock correctly in the research tab.

Item stays in `doing` — pieces 1-4 are real, offline-validated, and XML-
deployed, but need the pending DLL redeploy plus the live checks above before
this item's own `verify` section is satisfied. Pieces 5-7 explicitly deferred,
reasons above.
