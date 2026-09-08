# RustChrome — validation walk
subject: src/RimMandrake/RustChrome  (packageId mandrake.rm.rustchrome)
deps: none declared (no modDependencies in About.xml; loads LAST by convention so its textures win ContentFinder's walk — no hard load-order constraint enforced by the mod itself)
list: minimal
status-hint: rusted-iron-and-brass UI skin — Tier 1 is 14 loose PNG overrides at vanilla UI texture paths (zero code), Tier 2 is a `[StaticConstructorOnStartup]` class that reflection-sets six `Verse.Widgets` colour fields plus `RimWorld.InspectPaneUtility`'s tab-fill texture once at startup.

## must be true
- All 14 Tier-1 PNGs exist on disk at the exact vanilla paths named in About.xml, confirmed present: `UI/Widgets/ButtonBG`, `ButtonBGMouseover`, `ButtonBGClick`, `ButtonSubtleAtlas`, `TabAtlas`, `DesButBG`, `AbilityButBG`, `CheckOn`, `CheckOff`, `CheckPartial`, `RadioButOn`, `RadioButOff`, and `UI/Buttons/SliderRail`, `SliderHandle` (`RustChrome/Textures/`).
- On startup, `RustChromeColors`'s static constructor reflection-sets all six named fields on `Verse.Widgets` — `WindowBGFillColor`, `WindowBGBorderColor`, `MenuSectionBGFillColor`, `MenuSectionBGBorderColor`, `OptionUnselectedBGFillColor`, `OptionSelectedBGFillColor` — plus `RimWorld.InspectPaneUtility.InspectTabButtonFillTex`, and logs `"[RimMandrake.RustChrome] colour fields set."` only if every `SetColorField`/`SetTexField` call found its field (`RustChrome/Source/RustChromeColors.cs:20-40`).
- Any field-name mismatch (e.g. after a RimWorld version bump renames a `Widgets` field) logs `Log.Error("[RimMandrake.RustChrome] field not found: " + type.FullName + "." + fieldName)` rather than throwing and killing the load (`RustChromeColors.cs:50,61`).
- Ships zero Defs, zero Harmony patches — a plain static field set, not a draw-code patch (About.xml, confirmed no `Defs/` folder on disk).

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rm.rustchrome" and no XML error naming RustChrome's About.xml   # load-time
2. [L] Player.log after load contains "[RimMandrake.RustChrome] colour fields set." and NOT "[RimMandrake.RustChrome] field not found:" — proves all six `Widgets` fields plus the `InspectPaneUtility` tex field resolved by reflection under the currently-installed RimWorld build; a field-not-found line means the game's own field names drifted underneath this mod
3. [D] a live RimDefDump capture confirms zero defs carry `modName` "RimMandrake: Rust Chrome"
4. [S] (human pass) open the main menu and any dev-mode window; every button, checkbox, radio button, slider and section background should read as rusted iron/brass, not vanilla blue-grey — this is the mod's entire deliverable and cannot be verified any other way
