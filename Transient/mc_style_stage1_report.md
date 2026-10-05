# MessyConduit style stage 1 report (2026-10-04)

## Status
Stage 1 built offline, committed and pushed (7edf12aa8 source, 029db7213 DLL). NOT deployed, NOT run live.

## Reading notes
- Design read (B chosen; merge = largest run wins, tie = older; stage 1 = poles only, mixed-style span uses older pole).
- Current pole art: Aerial/Styles/<Look>/{AerialMast,AerialMastTop,AerialLampMast,AerialLampMastTop,WallBracket_<n|e|s>} exist for all 4 looks.
- Today: AerialMaterials.ApplyPoles rewrites the SHARED ThingDef.graphicData + AerialAnchorExtension.attachZ/topOffsetZ per global Look.
  Consumers of the global Look: InsulatorsFor, BracketInsulator, TopPathFor, Span/SpanWidth, LampHead, mesh sigs in RM_MapComponent_Aerial, ConduitVisuals hookup cable.

## Engine facts (RimSage, decompiled 1.6, this pass)
- Designator_Build.ThingStyleDefNonPreceptSource: returns `styleDef` only if classicMode && styleOverridden, else PrimaryIdeo style. Used by DesignateSingleCell for BOTH god mode (thing2.StyleDef=) and blueprint (blueprint_Build.StyleDef=), and by ThingStyleDefForPreview (button icon) when sourcePrecept null.
- Deselected() resets styleOverridden=false. BuildCopyCommandUtility.BuildCommand writes `des.styleDef = style` at GIZMO CREATION (every frame a building is selected) and the click calls SetTemporaryVars(stuff, styleOverridden). So des.styleDef is NOT a reliable 'last picked' store -> we keep our own per-def last pick.
- Copy gizmos: Building/Frame/Blueprint_Install pass styleOverridden:true; Blueprint_Build passes its own `styleOverridden` field (usually false) -> prefix forces true for our defs.
- Thing.Graphic: StyleDef.graphicData.GraphicColoredFor(this), cached in styleGraphicInt. Blueprint uses StyleDef.blueprintGraphicData (auto-made in ThingStyleDef.PostLoad). Frame.cs:317 thing.StyleDef = StyleDef. Blueprint_Install.StyleDef forwards to ThingToInstall.
- ThingStyleDef.PostLoad defaults shaderType to Cutout; uiIcon from graphic. CanBeStyled = def has CompProperties_Styleable.

- **Frame.CompleteConstruction copies the style ONLY if `GetIdeoForStyle(worker) != null`** (worker.Ideo, or a colony mech's overseer's ideo). A worker with no ideo would drop the picked style -> stage 1 adds a guard postfix (Frame style re-applied to the built thing for our defs).
- MinifyUtility.Uninstall -> MakeMinified keeps the Thing (comps incl. CompStyleable) inside MinifiedThing; Blueprint_Install.StyleDef forwards to the inner thing.

## Plan (as built)
- 12 ThingStyleDefs `<Anchor>_<Look>` (RM_AerialStyles.xml); CompProperties_Styleable on RM_AerialAnchorBase.
- Verse-free `Aerial/AerialStyles.cs`: look list, style def naming, span-look rule (older = lower thingIDNumber), picker resolve rule. Selftested.
- `Aerial/StylePicker.cs`: per-def last pick (session), float menu on ProcessInput, getter postfix on ThingStyleDefNonPreceptSource, copy prefix, legacy postfix on Thing.StyleDef (null -> default-look style def, NOT written to the save), Frame guard, bracket per-look draw offsets injected into the bracket style defs' own GraphicData at startup.
- AerialMaterials: per-look material sets; no shared-def edit; geometry looked up by (look, def).

## Changes
- `Source/Aerial/AerialStyles.cs` (Verse-free rules), `Source/Aerial/StylePicker.cs` (menu + 4 Harmony patches + bracket offset injection), `Defs/Aerial/RM_AerialStyles.xml` (12 style defs), CompProperties_Styleable on RM_AerialAnchorBase. (built, 0 errors)
- AerialMaterials: ApplyPoles (the shared-ThingDef graphic + extension edit) DELETED. Per-look `LookMats` (span cable + width); AttachZ/TopOffsetZ/TopPathFor/InsulatorsFor/BracketInsulator/LampHeadFor take the ANCHOR and look up by its look. Globals Look/Span/SpanWidth = default look (legacy + switch hookup cable).
- CompAerialAnchor.BasePoint reads the drawn style's GraphicData offset; AttachPoint uses AttachZ(a).
- RM_MapComponent_Aerial: span mesh carries its look's material/width (SpanLookOf); fallen wires + local drops use the anchor's look; mesh sigs include both poles' looks.
- `Source/Aerial/StyleProbeAerial.cs` + AerialProbe verbs: styles | place:def:Look:x,z[:rot]:god|build | finishbuild | reinstall:id:x,z | copy:id:x,z | clearpicks.

## Selftests / build
- winbuild MessyConduit: 0 errors. selftest_messyconduit.py 520/520 (new StyleStage1Checks: naming, per-look geometry over the REAL generated tables via a 2-field UnityEngine.Vector2 shim, span rule, picker rule; each with a can-fail).
- validation_style.py --offline (S0): PASS (12 style defs, art on disk, no <StyleCategoryDef> lists them across 1813 Defs xml, no shared-def edit). Hooked into validation.py O5.
- run_selftests.py 173/177: northstar_matrix C2 (dirty live shots), MandrakePatches, UtinniPatches dump = pre-existing (round 4 report); StarWarsPatches semantics fails only in the parallel run (passes solo).
- Commits: 7edf12aa8 source (pushed with the DLL), 029db7213 DLL+.srchash from committed source.

## Live check (not run -- the main window holds the bridge)
After deploy (game closed) on the `messyconduit` tier, on a map WITH a free colonist:
    python.exe src\RimMandrake\MessyConduit\validation_style.py --live --save MC_STYLE1_<date>
Rows: S1 pick -> designator style -> blueprint; S2 blueprint -> frame -> building draws its look (+ workerHasIdeo, frameStyleRestored);
S3 god mode; S4 Copy carries Industrial while the button's last pick is Futuristic; S5 Uninstall + install keeps Futuristic (same thing id);
S8 a jawa/build_batch (unstyled) mast stores NO style yet draws the default look; S6 spans: same-look and mixed (older pole wins), cable tex + width per look;
S7 save/load: every mast's raw style, drawn graphic path and span look/tex/width identical after reload.
Probe verbs (AerialProbe): styles | place:def:Look:x,z[:rot]:god|build | finishbuild | reinstall:id:x,z | copy:id:x,z | clearpicks.


## Unproven / stage 2 needs
Unproven live: everything above (S1-S8), the menu itself (opening on click, icons from ThingStyleDef.UIIcon, bracket icon = north facing), the
bracket's per-look offsets injected into the style defs' GraphicData (BasePoint and drawn plate must still coincide; ReviewRound4 offline check still
passes but it reads the tables, not the injected GraphicData), the Thing.StyleDef getter postfix's cost (one array read per call), Ideology
classic-mode behaviour of the vanilla "Change style" gizmo on our blueprints (expected hidden: no category lists our defs).
Not done in stage 1: review-map row 2 (four masts side by side) in human_review.py.

Stage 2 needs from this stage:
- AerialStyles.Looks / StyleDefName / LookOfStyleDefName (extend StyledDefs with the conduit + switch defs and their 4 'marker' styles).
- StylePicker: IsStyled/StyleFor/LookOfThing/RawStyle, the per-def last pick, the getter + copy + Thing.StyleDef(legacy) + Frame guard patches all key on StyleIndex, so adding defs to StyledDefs (and CompProperties_Styleable by guarded patch on PowerConduit/WaterproofConduit/PowerSwitch) is the whole wiring.
- AerialStyles.SpanLook is the ONE place to swap 'older pole wins' for the run rule (largest run wins, tie = older, owner 2026-10-04); a span's look then comes from its run.
- Restyle gizmo: write t.StyleDef on every run member, then (anchors) the span mesh sig already includes both poles' looks, so spans rebuild by themselves; ground layer needs DirtyGround.
- Modern colour per run (owner Q4) is NOT in stage 1: the menu has 4 entries; stage 2 adds the colour entries (incl. 'random' = mixed colours) to MenuFor.
