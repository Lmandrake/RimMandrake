# Statue Art Expansion — Assessment (STATUE_ART_EXPANSION_1)

Read-only research pass, 2026-09-25. Sources: live `ModsConfig.xml` (parsed with
`ElementTree`, 628 active mods), both candidate mods' own files, RimSage (MEASURED —
connected this session, so this window is the Windows Desktop), and our own
`SUMP_GASLIGHT_1` / `SUMP_UTINNI_LAYER_1` item files.

## 1. The installed statue-choice mod(s)

Two are active, and they work together:

- **`[LC] Selectable Sculpture Graphic`** — packageId `lc.tammybee.selectablesculpturegraphic`,
  `/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/3239359525`.
  Harmony C# mod. Its one patch file (`v1.6/Patches/Building_Patches.xml`) does nothing but
  `PatchOperationAdd` a single comp, `SelectableSculptureGraphic.CompSculpture`, onto the
  `<comps>` of `SculptureBase`, `SculptureBase_mores` (a courtesy hook for More Sculpture,
  below), `BuildingFloorCoveringBase`, `BabyDecoration`, `SteleLarge`, plus DLC-gated adds for
  Ideology's `SculptureTerror`, Anomaly's `VoidSculpture`/`CubeSculptureBase`, and a long list of
  Odyssey/Biotech "ancient" clutter props. The comp almost certainly puts a gizmo on the built
  thing letting the player cycle its `Graphic_Random` variant pool by hand — UNMEASURED beyond
  the patch surface (the compiled DLL cannot be read; `.claude/hooks/block_blind_scan.py`
  correctly refused a `strings` census of it, and this is a census question, not a literal-string
  one). License: About.xml states **CC BY-NC-SA / MIT** (both cited, Copyright 2017 TammyBee).
- **`More Sculpture`** — packageId `Bichang.MoreSculpture`,
  `/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/1612316880`. Pure
  XML+texture, no C#: drops 74 extra texture variants into
  `Textures/Things/Building/Art/{SculptureSmall,SculptureLarge,SculptureGrand}/`, the same
  folders vanilla's own `Graphic_Random` sculptures already scan. Under Ideology it also
  `PatchOperationReplace`s every ideoligion-specific `ThingStyleDef`'s `texPath`
  (`Christian_SculptureSmall`, `Islamic_...`, `Totemic_...`, `Animalist_...`, etc.) to point at
  this same shared pool — so it trades ideoligion-specific art for one big randomized pool. No
  license stated in About.xml.

Together: More Sculpture supplies the *variety* (a bigger random pool), LC supplies the
*choice* (a gizmo to pick a specific variant instead of taking whatever rolled). Neither adds a
new sculpture *subject* — both only reshuffle vanilla's existing sculpture defs.

## 2. Vanilla 1.6 statue styling mechanism (MEASURED via RimSage)

Vanilla already has a zero-C# "many styles, chosen by culture" system: `ThingStyleDef`. 43 are
indexed (`Christian_SculptureSmall/Large/Grand`, `Islamic_...`, `Buddhist_...`, `Hindu_...`,
`Morbid_...`, `Totemic_...`, `Animalist_...`). Each is trivial XML —
```xml
<ThingStyleDef>
  <defName>Christian_SculptureGrand</defName>
  <graphicData><texPath>Things/Building/BuildingStyles/Christian/Sculptures/Grand</texPath>
    <graphicClass>Graphic_Random</graphicClass><drawSize>(4,4)</drawSize></graphicData>
  <uiIconScale>1.23</uiIconScale>
</ThingStyleDef>
```
— grouped under a `StyleCategoryDef` that a colony's ideoligion selects, which then reskins
every `CompProperties_Styleable` building automatically (our `RM_FlameStatuary` already carries
`CompProperties_Styleable`, so it is already eligible). Ideology DLC only — already always-on
per the "all expansions, no ablation" ruling, so this route has zero new dependency.

## 3. Patch-into-existing-mod vs. build-our-own — recommendation

**Both, split by what each layer actually is:**

- **Player-facing manual variant SELECTION** (picking among our art with a gizmo): patch into
  LC, don't fork it. It is a thin, additive comp keyed by `PatchOperationAdd` on `/comps` — our
  own compat patch can add the same `SelectableSculptureGraphic.CompSculpture` to our own statue
  defs, gated `PatchOperationFindMod` on `lc.tammybee.selectablesculpturegraphic` so it is inert
  without LC installed. Needs our art shipped as a normal `Graphic_Random` texture-folder pool
  (several numbered variants, vanilla's own naming convention) rather than the current
  `Graphic_Single`. Cheap, low-risk, no fork, no license entanglement (we ship no LC assets).
- **New sculpture SUBJECTS** (the actual art — RM flame-statue line, Utinni gods): neither donor
  mod can supply this; it is necessarily our own content regardless of which selector plumbs it.
- **Utinni-culture statues specifically**: prefer vanilla's own `StyleCategoryDef`/`ThingStyleDef`
  route over depending on either Workshop mod. It is the doctrinally right fit — culture-driven,
  zero third-party dependency, and matches `SUMP_UTINNI_LAYER_1`'s existing "additive,
  ideoligion-tier, free mod stays whole without it" pattern precisely. An LC compat patch can
  still sit on top for players who want manual override.

## 4. Flame emergence points — how they would attach

`RM_FlameStatuary` today carries exactly one glow source: sibling `CompProperties_Glower` +
`RM_CompProperties_WarblingGlow` (`src/RimMandrake/EnvironmentalHazards/Source/
RM_Comp_WarblingGlow.cs`), a single hue/radius-pulsing point comp with no positional structure
at all — there is no second flame point, and no particle system. The item's own build note
(`SUMP_GASLIGHT_1`) already flags the honest next step: "*a literal `FleckMaker.ThrowFireGlow`
particle lick... NOT built this pass.*"

Shape for "flame emergence points" (plural, positioned on the sculpture): a new
`CompProperties`/`ModExtension` carrying a `List<Vector3>` (or `IntVec3` + local offset) of
attachment points authored per-def alongside the art — same idea as a pawn's apparel-attachment
offsets, just simpler (static building, no rotation/animation rig to fight). A tick comp reads
that list and calls `FleckMaker.ThrowFireGlow` (or a small custom `FleckDef`) at each point on
an independently phased interval, with amplitude/frequency driven by the same
`CompQuality`-scaling pattern `RM_Comp_WarblingGlow.qualityScalingEnabled` already establishes —
no new quality-tracking code, just a second consumer of the same sibling `CompQuality`. This is
new C#, but small, and independent of whichever statue-selection mod is installed.

## 5. Fuel hookup options (Sump / Helixian gas / manual refuel)

`RM_FlameStatuary` itself is **not fuel-gated today** — no `CompProperties_Refuelable` on it;
the glow is always-on once built and quality-rolled. Three routes exist for making the flame
(and any future emergence-point particles) consume fuel:

- **Manual refuel — the proven route.** `CompProperties_Refuelable` is already live and working
  on the sibling `RUT_GaslightLamp` (UtinniPatches), fueled by `RUT_Sumpgas`; a 2026-09-25 live
  pass confirmed a real `Refuel` job running ("Sumpgas: 6 / 6 (21 days)"). Adding the same comp
  to `RM_FlameStatuary` is a small, low-risk change and the cheapest way to make the statue
  actually consume something.
- **"Sump" gas (`RUT_Sumpgas`)** — the Sump biome's own tar+acid gas economy
  (`SUMP_GASLIGHT_1`, EnvironmentalHazards + UtinniPatches): a real craftable/byproduct resource,
  offline-validated and deployed. **Caveat**: the 2026-09-25 live pass found its byproduct-spawn
  path (scrubbing tar off a pawn → `RUT_Sumpgas`) **fails live** — the bill completes but no gas
  spawns, root cause not yet isolated (Player.log hit its message cap). Usable as a fuel item
  today via crafting, but the "free" acquisition route is currently broken.
- **"Helixian" gas** — the third-party **Vanilla Helixien Gas Expanded** mod (packageId
  `vanillaexpanded.helixiengas`, adopted 2026-08-10 per `design/Jawa/proposals/
  tar_pits_deep_design.md` §3B(5)). Its `VHGE_Helixien` def carries
  `CompProperties_CompDestroyOnSpawn` — a pipenet scatter/feed marker, **not** a haulable
  `CompRefuelable` fuel item — so a statue cannot burn it directly with the comp above. Real
  interop needs that mod's `PipeSystem`/`CompResourceTrader` studied live; `SUMP_GASLIGHT_1`
  already flagged this **NOT built, out of scope**, and this pass finds no reason to reopen it
  yet.

**Recommendation**: ship manual refuel via `CompProperties_Refuelable` + `RUT_Sumpgas` as the
real, working fuel route now; treat literal VHGE pipenet interop as a gated stretch goal, not a
prerequisite.

## 6. The "Steel Flame statuary" finding

Found it: `RM_FlameStatuary`,
`src/RimMandrake/EnvironmentalHazards/Defs/ThingDefs_Buildings/RM_FlameStatuary.xml`. "Steel
Flame statuary" is simply this def's vanilla stuff-prefixed display name when built in steel
(one of its three `stuffCategories`: Metallic/Woody/Stony) — there is no separate "Steel Flame"
def. It belongs to `mandrake.rm.environmentalhazards` (EnvironmentalHazards), built by FOUNDRY
2026-09-24 under item `SUMP_GASLIGHT_1`.

**Yes — confirmed placeholder, by the def's own header:** *"Texture: same placeholder posture as
this whole kit's other new content this pass... since only one placeholder image exists."* It
ships `Graphic_Single` (not even vanilla's own 3-variant `Graphic_Random`) pointing at one PNG,
`src/RimMandrake/EnvironmentalHazards/Textures/Things/Building/Art/RM_FlameStatuary/
RM_FlameStatuary.png`, and the item's own build-status note says outright: "real (hand-authored,
reviewed) art is still owed." Two more facts worth carrying into any follow-up: the flame is
currently a single ambient glow with no particles (§4 above), and it is not fuel-gated at all
(§5 above) — so what the owner saw and judged "awful" is a one-texture placeholder standing in
for a mechanic that isn't finished either.

## 7. Proposed build order

### 7a. RM base art mod

1. Real hand-authored flame-statuary art replacing the placeholder PNG; ship as a proper
   `Graphic_Random` variant folder (a handful of numbered variants) so both vanilla's own random
   pick and LC's selector gizmo have something real to work with.
2. Flame-emergence-point comp (§4): positioned, quality-scaled particle licks, built as its own
   small `CompProperties`/tick-comp pair alongside the existing `RM_Comp_WarblingGlow`.
3. Add `CompProperties_Refuelable` to `RM_FlameStatuary` (default fuel `RUT_Sumpgas`, kept
   fuel-agnostic in the RM-tier def per its own existing doctrine — no Sump/Utinni flavor text
   in the RM def itself).
4. Optional thin compat patch adding `SelectableSculptureGraphic.CompSculpture` to our statue
   defs, `PatchOperationFindMod`-gated on LC's packageId — inert without it installed.

### 7b. Utinni-culture statues

New RUT-tier ThingDefs depicting named Utinni gods, built on the same RM mechanism/comps (art +
emergence points + refuelable) rather than re-deriving it. Two additive layers, matching
`SUMP_UTINNI_LAYER_1`'s existing shape (free RM mod stays whole without either):

1. A `StyleCategoryDef`/`ThingStyleDef` set (§2) for automatic culture-driven reskinning once the
   Utinni ideoligion is chosen — zero new dependency, pure vanilla mechanism.
2. The "holy act to the evil sun god" ritual/precept meaning as an ideoligion patch over the RM
   flame-statuary def, per `SUMP_UTINNI_LAYER_1` item §2 (already scoped, not yet built).

Prerequisite worth flagging, not blocking: the live `RUT_Sumpgas` byproduct-spawn failure (§5)
should get a root-cause pass before either layer leans on Sumpgas as a *renewable* fuel source in
front of the owner.
