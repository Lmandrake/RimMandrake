# RM_GENSTEP_PLACED_SETPIECES_1 — the shared def-list set-piece scatterer

Filed by FOUNDRY, 2026-09-13. Two mechanics kits both name this class as a
hard prerequisite and neither has built it: `MIASMA_MECHANICS_1`'s own spike
pass (M6, warden-mother placement) and `SUMP_MECHANICS_1`'s own spike pass
(S3 tar-beast placement, and S4 mouse-line dread fields which needs S3's
dread sources per that kit's own build order) both confirmed via `grep -rn
"RM_GenStep_PlacedSetPieces" src/` that no class definition exists anywhere
— only comments and kit-spec prose naming it. Both kit specs describe it
**consistently** (read `design/Jawa/worldbuilding/biomes/kits/miasma_kit_spec.md`
§M6 and `design/Jawa/worldbuilding/biomes/kits/sump_kit_spec.md` §S3 for the
exact wording), which is why this item builds ONE shared class rather than
two divergent ones.

## spec

`RM_GenStep_PlacedSetPieces : GenStep_Scatterer` — base class already
verified by both kit specs against real engine source
(`Source/Verse/GenStep_Scatterer.cs`; `GenStep_ScatterThings` shows the
concrete shape a subclass follows). A generic, def-list-driven site
scatterer:

- Per map, N sites (count is per-consumer tuning, not this class's job to
  hardcode — expose it as a field/props) placed according to a **caller-
  supplied validity predicate** (Miasma wants brine-side shallow water,
  ordered strictly after `RM_GenStep_GradientAxis`; Sump wants deep-tar
  regions far from map edge) — this is the actual reuse contract: the class
  owns "pick N valid sites, spawn what's asked at each," not any specific
  biome's notion of what a valid site is.
- **Never random per ban text both kits cite**: zero commonality, no
  faction, GenStep-only entry point — sites exist because the GenStep placed
  them, never because an ambient incident rolled one.
- At each chosen site, spawns whatever the caller configures (Miasma: one
  warden-mother pawn + a juvenile cluster + a `RUT_CrecheMarker` invisible
  building holding site identity; Sump: a dormant beast Thing via stock
  `CompCanBeDormant`/`CompWakeUpDormant`, already verified elsewhere in
  `SUMP_MECHANICS_1`'s own spike). **This item builds the GENERIC scatterer
  only — not Miasma's warden-mother roster content or Sump's tar-beast
  ThingDef/`RM_CompStationEater`, both of which are named as separate,
  larger build items (M6/S3's own remaining scope) in their kit specs.**

## verify

Compiles clean (`dotnet build` on `RM_EnvironmentalHazards.csproj`, 0
warnings/0 errors — this is the ruled kit home both consumers already build
into). No live/bridge/quicktest verification — same posture as every kit
spike tonight; that's owed once a consumer kit's full build lands and uses
this class for real.

## criteria

A compiling `RM_GenStep_PlacedSetPieces` class exists, generic enough that
both `MIASMA_MECHANICS_1`'s M6 and `SUMP_MECHANICS_1`'s S3/S4 can consume it
without forking it — re-read both kit specs' own description of the class
before finalizing the shape, since they are the two customers whose actual
needs define "generic enough."

## built, 2026-09-13

`src/RimMandrake/EnvironmentalHazards/Source/RM_GenStep_PlacedSetPieces.cs`.
Confirmed against the live decompile
(`/mnt/d/Luke/dev/reference/rimworld-decompiled/Verse/GenStep_Scatterer.cs`,
`GenStep_ScatterThings.cs`) that the base class already does almost
everything the spec asked this item to expose as fields:

- **Site count** — inherited `count` / `countPer10kCellsRange`, already
  XML-settable per `GenStepDef` instance. No new field needed.
- **Validity predicate** — inherited `validators` / `fallbackValidators`
  (`List<Verse.ScattererValidator>`), also already per-instance XML content.
  Each kit writes its own `ScattererValidator` subclass (brine-shallow-water
  for Miasma, deep-tar-far-from-edge for Sump) and lists it in its own
  `GenStepDef` — this class never references either.
- **What gets spawned** — the one real gap in the base class, filled by a
  new hook: `public List<RM_SetPieceElement> elements`, where
  `RM_SetPieceElement` is a new abstract one-method class
  (`abstract void SpawnAt(IntVec3 loc, Map map, GenStepParams parms)`)
  modeled deliberately on `Verse.ScattererValidator`'s own pattern — XML
  `Class=`-instantiated per `<li>`, so the framework class never sees kit
  content. `ScatterAt` just iterates `elements` and calls `SpawnAt` on each.
  Miasma's `GenStepDef` would list a warden-mother-pawn element + a
  juvenile-cluster element + a `RUT_CrecheMarker` element; Sump's would list
  one dormant-beast element. No `PawnKindDef` or `ThingDef` appears in this
  file — only in each kit's own `RM_SetPieceElement` subclass, which is
  M6/S3's own remaining build scope, not this item's.

Surveyed and rejected vanilla's own "configurable content" subclasses
(`GenStep_ScatterGroup`, `GenStep_ScatterGroupPrefabs`) as the model: both
pick ONE weighted-random group per site (`RandomElementByWeight`), which is
exactly the "sometimes random" shape both kits' ban text forbids. This
class's `elements` list spawns everything named, every time, at every site
— no roll.

**Never random is structural, not disciplined**: no commonality/chance field
exists anywhere in this class or its `GenStep_Scatterer` base, no faction is
assigned, and the only entry point is `Generate()` being called by the
`GenStepDef` pipeline like any other GenStep.

No divergence found — both kits' own spec language ("pick N valid sites,
spawn what's asked at each") maps directly onto one class; the
`RM_SetPieceElement` hook is the seam that made a shared class possible
without forcing Miasma's multi-part site (pawn + cluster + marker) and
Sump's single-Thing site into the same shape.

`dotnet build RM_EnvironmentalHazards.csproj -c Release`: **0 warnings, 0
errors.**
