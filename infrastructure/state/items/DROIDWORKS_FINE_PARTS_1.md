## spec
Thin when filed — no spec/verify/criteria in the queue entry itself, but
fully specced as packet B4a of
`design/Jawa/droids/DROID_UNIFIED_FRAMEWORK_DESIGN.md` §5 (inputs: ruling 5,
§1.3's part set; outputs: part items per family with quality, drop tables,
`CompPartEffects` stats+personality per quality tier; verify: "every family
drops a legal set; inferior sensor lowers Sight"; after: B3, closed earlier
today). Built directly from that packet, FOUNDRY, 2026-09-08.

## Built
- **6 generic part items** (`ThingDefs/Parts_Droidworks.xml`): `RSW_DW_Part_
  {Leg,Manipulator,Sensor,Motivator,Servo,PowerCell}`. Generic across
  families rather than 7x reskinned per family — a spare servo is spare
  salvage regardless of chassis (unlike a head, which carries identity —
  B3). Arm and Manipulator collapsed to one item ("Leg/Arm/Manipulator" in
  the design text reads as one slot idea, not three mandatory ones). All
  carry `CompQuality` (vanilla).
- **Legal per-family drop sets + drop table** (`Source/Droidworks/
  CompDWPartDropper.cs`, new comp on `DW_Race_Base`, same `Notify_Killed`
  hook as `CompDWHeadDropper`): each of the 6 part types rolled
  independently at 60% on death ("never all of them", section 1.3), quality
  via `QualityUtility.GenerateQualityTraderItem()` (the vanilla found-loot
  roll). **Per-family legal sets are FOUNDRY's own call** (nothing in the
  design doc enumerates them), built from each family's real shape:
  Astromech/Probe (domed/limbless donor races) never drop Leg or
  Manipulator; Power/Gonk never drops Manipulator or Sensor. Full table in
  `CompDWPartDropper.LegalSetFor`.
- **Quality-scaled effects** (`Effects_Droidworks.xml`, 15 HediffDefs: 3
  tiers × 5 effectful types — PowerCell carries none, see below):
  Inferior/Standard/Superior per type, capacity offset (Leg→Moving,
  Manipulator→Manipulation, Sensor→Sight) or stat offset (Motivator→
  MoveSpeed, Servo→WorkSpeedGlobal). Offsets (±0.15 capacity, ±0.5
  MoveSpeed, ±0.10 WorkSpeedGlobal) are FOUNDRY's own numbers — nothing in
  the design doc gives a figure.
- **Install recipes** (`RecipeDefs/PartRecipes_Droidworks.xml`, 5 RecipeDefs,
  one `Recipe_InstallDroidPart` C# class shared by all — `Source/
  Droidworks/Recipe_InstallDroidPart.cs`): reads the consumed part's
  `CompQuality` at bill completion, buckets Awful/Poor→inferior,
  Normal/Good→standard, Excellent/Masterwork/Legendary→superior, replaces
  (never stacks) whichever tier hediff of that type is already present.
  Wired onto `DW_Race_Base.recipes`, same as bolt/wipe/reboot/format.

## Not touched, deliberately
- **PowerCell** carries no install recipe or hediff — nothing in the design
  doc gives it a mechanical hook beyond flavor/market value. It still drops
  and carries quality (for resale), same as the other five.
- No shop-bench part-swap job (`Recipe_ShopRebuild`, B4b, unbuilt) — the
  install route here is the standard vanilla surgery-bill pattern, same as
  every other Droidworks recipe; B4b is a convenience UI on top, not a
  prerequisite for parts to work.

## verify (live, minimal 25-mod list + quicktest, FOUNDRY 2026-09-08)
Build: `dotnet build Droidworks.csproj -c Release` — 0 errors.

**One real bug caught and fixed live**: `<li Class="CompProperties_Quality" />`
(the XML class-attribute shortcut) does not resolve in this game version —
`Exception loading def from file Parts_Droidworks.xml: ... Could not find
type named CompProperties_Quality`, which silently dropped **the entire
file**, all 6 part ThingDefs. Vanilla itself only ever writes quality as
`<li><compClass>CompQuality</compClass></li>` (confirmed against Core's own
`Buildings_Art.xml`) — fixed to match, redeployed, relaunched, resolved.

- **"inferior sensor lowers Sight"**: spawned a Protocol droid, read Sight
  capacity via `jawa/list_pawns includeHealth=true` before/after adding each
  tier hediff directly (`jawa/pawn_health`, add/remove) — **baseline 1.0,
  Inferior 0.85, Superior 1.15**, live, exact match to the authored offsets.
- **"every family drops a legal set"**: killed a Protocol droid (full
  6-type legal set) and a Power/GNK droid (4-type legal set, excludes
  Manipulator and Sensor) 5 times each. Every drop observed was inside that
  family's legal set; **Manipulator and Sensor never once appeared on a
  Power/GNK kill** across 5 kills. An Astromech kill (4-type set, excludes
  Leg/Manipulator) also dropped cleanly inside its set.
- **Player.log, literal check**: same 12 pre-existing `Config error in`
  lines as before this item (6 unrelated quest defs, 6 unrelated
  `RSW_DW_Module_*` smeltable warnings) — zero new errors from this item's
  defs or C#.
- Recipe install path (quality→hediff bucketing) verified by code review
  only, same as B3's data-spike gating — no bridge tool exists to force a
  `Recipe_Surgery` bill to completion (A1's own finding, still the case).
  The mechanism it drives (capMods/statOffsets on a HediffDef) is the exact
  thing proven live above via direct hediff add/remove.

## Assumptions recorded (Charter: "record what you assumed")
1. Per-family legal part sets (which of the 6 types each family can drop)
   are FOUNDRY's own call — no source specifies them.
2. Stat/capacity offset magnitudes per tier are FOUNDRY's own numbers.
3. PowerCell has no mechanical effect, flavor/market value only.
4. Drop chance (60% per type, independent) and quality curve
   (`GenerateQualityTraderItem`) are FOUNDRY's own choices, not ruled.
