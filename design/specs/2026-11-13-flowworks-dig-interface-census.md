# FlowWorks dig interface: census of every player-facing control (2026-11-13)

Scope: `src/RimMandrake/FlowWorks` at origin/main as of 2026-11-13. Everything below is [measured] from the C#, defs and
patches unless tagged [guess] or [unverified]. No game was run, no mod code changed. This is a census, not a proposal.
Trigger: the owner's live look, 2026-11-13 ~9:45 PM PST (see "Owner's words" at the end).

## Summary in plain words

- **Dig and fill orders: 5 buttons, all in one place, Architect > Orders** (`Patches/FlowWorks_OrdersPatch.xml:9-15`):
  Dig pit, Dig to depth, Fill in pit, Restore ground, Repair breach. Vanilla's own Orders tab already has Mine, Smooth, Plan etc.
  around them.
- **"Dig to depth" opens a menu of 40 entries at the shipped defaults** (one per half-metre, "Dig to 0.5 m" ... "Dig to 20 m"),
  or 4 entries if "Machines dig deeper" is off (the list length is the deepest depth anyone may dig, in half-metre notches).
  This is the "vast grid" he met: 40 lines in one float menu, each carrying a "(N digger-days a square of soil ...)" estimate.
  `Designator_DigCanal.cs:207-225`.
- **11 more special designators in Architect > Structure** (6 bridges, 2 jetties, 2 drawbridges, 1 tower), plus **33 ordinary
  buildables** spread over 6 Architect categories (Structure 13, Production 5, Power 1, Security 3, Misc 1, and the mod's own
  "pipe networks" tab 10).
- **Gizmos**: about 22 player-facing buttons on 13 kinds of selected thing (ladder, gate, drawbridge, bridge, hose reel, pump, tank, adapter,
  pipe/weir look, sprinkler, a colonist beside a pit), plus 3 player float-menu actions on right-click; **plus ~30 more that
  exist only in Dev Mode or God Mode** (map controls, DEV hose, DEV ladder, tank fill).
- **Digging is work type `Mining`** (no work type of its own); filling in is also `Mining`. Ladders and sluice gates are `BasicWorker`.
- **Default speed: the first half-metre of soil is 12,800 work, about 7,529 ticks (3.0 game hours) for a digger at 100% mining
  speed; rock is 4x that, 30,118 ticks (12 h)**. Cost rises with depth: notch k costs k times the first.

## 1. Where the Dig and Fill controls are: Architect > Orders (5)

All five are `Designator_Cells` subclasses added to vanilla's `Orders` category by `Patches/FlowWorks_OrdersPatch.xml` (guarded by
`PatchOperationFindMod Core`). Drag-over-squares tools; each also draws a bracket on the hovered square.

| Label as shown | What it does | Opens | Hidden or changed by a Mod Setting | file:line |
|---|---|---|---|---|
| Dig pit (hotkey Misc6) | Marks a square to be dug one half-metre deeper; on an already-dug square it deepens by another half-metre, to the deepest dig allowed | nothing (drag) | "Dig deeper" (`digToDepthEnabled`) refuses deepening; "Deepest colonist dig" (`maxDigDepth`, default 2 m) and "Machines dig deeper"/`maxMachineDigDepth` (20 m) set the refusal depth; map-edge sinks (`edgeSinksEnabled`) open the edge band; rock ground (`digRockGroundEnabled`) adds a "Rock ground: slow to dig (x4 work)" tag at the cursor | `Source/Designator_DigCanal.cs:13-174` (label :17, desc :18-25, hotkey :31, cap :93, rock tag :162) |
| Dig to N m (constructor label "Dig to depth"; the `Label` property shows "Dig to <chosen depth>") | Orders squares dug, half a metre a cut, down to a depth chosen from the menu; squares already ordered take the new depth | a **float menu of 40 entries** (see section 2) | refused outright when "Dig deeper" is off; list length = `DesignationCap` = machine cap if "Machines dig deeper" on, else colonist cap; per-entry estimate uses "Each half-metre deeper costs more" (`digCostRisesWithDepth`) | `Designator_DigCanal.cs:183-246` (label :190, :199, menu :201-226) |
| Fill in pit (hotkey Misc7) | Fills a dug square back in by half a metre; to the surface restores the original terrain | nothing (drag) | "Fill in channels" (`fillInEnabled`) refuses it; fill cost follows the labour slider; "Filling in costs gravel or chunks" | `Source/Designator_FillInCanal.cs:31-110` (label :35, desc :36-41) |
| Restore ground | Fill-in repeated, half a metre per job, until solid ground again (the "island in a hole" tool) | nothing (drag) | same as Fill in pit | `Source/Designator_RestoreGround.cs:12-154` (label :16) |
| Repair breach | Digs a causeway that raiders shovelled into your trench or pit back to the depth it had; only squares raiders filled take it | nothing (drag) | **hidden** when `breachRepairEnabled` is off (default on) | `Source/Superdeep/RM_LadderParity.cs:731-760`, setting :811 |

Other facts about the five: Dig pit, Dig to depth and Repair breach are all `Designator_DigCanal` (the other two inherit from it),
so they share one gate, one designation def (`RM_DigCanal`) and one job (`RM_DigCanalJob`). Fill in, Restore ground share
`RM_FillInCanal`. A new dig order removes a fill order on the same square and vice versa (`Designator_DigCanal.cs:143`,
`Designator_FillInCanal.cs:~108`). Harmony postfixes in `Source/Pits/Suspension/RM_SuspensionPatches.cs:139-174` add extra refusals to
Dig pit / Dig to depth / Fill in pit.

## 2. What "Dig to depth" opens: the depth menu

- A `FloatMenu` built in `ProcessInput` every time the tool button is clicked (`Designator_DigCanal.cs:201-226`).
- Generated by a loop `for n = 1 .. cap` (one entry per half-metre notch). Entry text:
  `"Dig to " + <n as metres> + " (" + <digger-days for n notches of soil> + " digger-days a square of soil" + [machine note when n > colonist cap] + ")"`.
- `cap` = `RM_DigLabor.DesignationCap` (`RM_DigLabor.cs:46`) = machine cap (default 40 notches = 20 m) when "Machines dig deeper"
  is on; otherwise the colonist cap (default 4 notches = 2 m). **Defaults: 40 entries**; machines off: 4 entries; if both caps
  set to the ceiling, 40. Minimum possible list: 4. Setting range is 2 m to 20 m in half-metres (`RM_DigDepthMath.cs`: `MinMaxDigDepth` 4, `MaxDigCeiling` 40).
- Entries 5 to 40 (2.5 m to 20 m) carry the suffix "; machines only past 2 m, and you have none: it will wait" (or "...only past 2 m") because colonists dig only to 2 m by default.
- The chosen entry is remembered in a static `chosenTarget` (initial value 8 notches = 4 m, held to the cap when used, so 2 m at default settings); the tool's label then reads "Dig to <that depth>", and the normal drag follows.
- Fact worth knowing: the digger-days figure in each entry is computed from `WorkToDig` only (3,200 x notch, 1.7 work per tick,
  60,000 ticks a day) and **does not include the labour multiplier (x4 default) or the rock multiplier**. At defaults, entry
  "Dig to 2 m" says 0.3 digger-days; the real work is 128,000 (about 1.25 digger-days at 100% mining speed) [measured from the formula].
  The Mod Settings page (`RimMandrakeFlowWorksMod.cs:1131-1137`) does include the multiplier.

## 3. Where digging is done: work types and work givers

| Def | Work type | Label in the Work tab | Priority in type | Notes | file |
|---|---|---|---|---|---|
| `RM_DigCanalWorkGiver` | **Mining** | "dig pits" | 20 | needs a shovel when `shovelRequired` (default on): fetches one first; refuses when the digger's own cap is below the target | `Defs/Canals/WorkGiverDefs/FlowWorks_WorkGivers.xml:4-17`; `Source/WorkGiver_DigCanal.cs` |
| `RM_FillInCanalWorkGiver` | **Mining** | "fill in pits" | 19 | same shovel rule | `...WorkGivers.xml:24-37` |
| `RM_OperateLadderWorkGiver` | BasicWorker | "raise and lower ladders" | 499 | carries out the ladder gizmo | `...WorkGivers.xml:41-52` |
| `RM_OperateGateWorkGiver` | BasicWorker | "lift and lower sluice gates" | 499 | carries out the sluice gizmo | `...WorkGivers.xml:57-68` |

Jobs: `JobDriver_DigCanal` and `JobDriver_FillInCanal`, both derived from vanilla `JobDriver_AffectFloor`, speed stat `MiningSpeed`.
Hose and bottle work givers are separate (`Defs/Hose/RM_HoseJobs.xml`, `Defs/LiquidTypes/WorkGiverDefs/`), type Hauling/other, not dig-related.

## 4. Dig-speed numbers

| Quantity | Default | Where | file:line |
|---|---|---|---|
| Base work per half-metre notch | 3,200 | const `WorkPerNotch` | `RM_DigDepthMath.cs` |
| Cost of notch k | 3,200 x k (rises with depth; flat past 2 m, i.e. 12,800 per notch, if "Each half-metre deeper costs more" `digCostRisesWithDepth` is off) | `WorkToCut` | `RM_DigDepthMath.cs`; setting `RimMandrakeFlowWorksMod.cs:64` |
| Labour multiplier "Digging and filling labour" (`digLabourMultiplier`) | **x4**, slider 0.25 to 8 | the "hours of shovel work" setting (owner card 2026-10-25) | `RM_DigDepthMath.cs` (`DefaultLabourMultiplier`); `RimMandrakeFlowWorksMod.cs:511`, slider :1131-1138 |
| Rock multiplier "Rock digging takes x the work" (`digRockWorkMultiplier`) | **x4**, slider 1 to 10; applied before the labour multiplier; also applies to rubble and ice; on only if `digRockGroundEnabled` | `RM_DigDiscoveryMath.RockWork`, `JobDriver_DigCanal.cs:47-51` | `RimMandrakeFlowWorksMod.cs:496-497, 1084-1090` |
| Fill work | half the dig work of the notch being removed, x the labour multiplier | `JobDriver_FillInCanal.cs:17-41` | |
| Work per tick | 1.7 x MiningSpeed stat | vanilla `JobDriver_AffectFloor`, as stated in the mod's comments [unverified against decompile] | `RM_DigDepthMath.cs` (`WorkPerTickAtSpeedOne`) |
| Shovel required | on | `shovelRequired` | `RimMandrakeFlowWorksMod.cs:516`; no shovel speed bonus found in `RM_ShovelMath.cs`/`RM_Shovels.cs` [measured: no speed term there] |
| Colonist depth cap / machine cap | 4 notches (2 m) / 40 notches (20 m) | `maxDigDepth`, `maxMachineDigDepth` | `RimMandrakeFlowWorksMod.cs:57-61` |

Derived at defaults, digger at MiningSpeed 1.0 (1 hour = 2,500 ticks) [measured by arithmetic from the above; not timed in game]:

| Cut | Work | Ticks | Game hours |
|---|---|---|---|
| Soil, notch 1 (0 to 0.5 m) | 3,200 x 1 x 4 = 12,800 | 7,529 | 3.0 |
| Soil, notch 2 | 25,600 | 15,059 | 6.0 |
| Soil, notch 4 (1.5 to 2 m) | 51,200 | 30,118 | 12.0 |
| Soil, all four notches to 2 m | 128,000 | 75,294 | 30.1 (about 1.25 days of one digger) |
| Rock, notch 1 | 3,200 x 4 x 4 = 51,200 | 30,118 | 12.0 |
| Fill, notch 1 | 6,400 | 3,765 | 1.5 |
| Soil to 20 m (machines) | 3,200 x 820 x 4 = 10,496,000 | 6.17 million | about 2,470 h (about 103 days of one digger) |

Mining speed below or above 100% scales these inversely (a colonist with a low Mining skill is slower). [guess: typical colonist
MiningSpeed is not 1.0; not measured here.]

## 5. Architect > Structure: 11 special designators (bridges, drawbridges, jetties, tower)

Added by `Patches/Pits/RM_SuspensionBridges.xml:6-18` to `Structure.specialDesignatorClasses`; each deck def sets
`canGenerateDefaultDesignator=false`. Each is a `Designator_Build` that takes anchor-to-anchor drags. Shown label = the def label.

| Label as shown | What it does | Opens | Hidden by | file:line |
|---|---|---|---|---|
| rope suspension bridge | Spans a pit or water between two anchors | nothing (two-point drag) | `suspensionBridgesBuildable` off | `Source/Pits/Suspension/Designator_SuspensionBridge.cs:18-29, 594` |
| timber suspension bridge | same | | same | `:601` |
| steel suspension bridge | same | | same | `:608` |
| heavy truss bridge | same | | same | `:615` |
| grated steel suspension bridge | same, open grate | | same | `:622` |
| grated heavy truss bridge | same, open grate | | same | `:629` |
| steel jetty | A jetty out over water | | same | `:643-651, 791` |
| heavy jetty | same | | same | `:798` |
| timber drawbridge | A drawbridge span with winch house and gate | | `drawbridgesEnabled` off | `:449-473, 580` |
| steel drawbridge | same | | same | `:587` |
| suspension bridge tower | Tower to carry a bridge | | `suspensionBridgesBuildable` off | `:808-814` |

## 6. Architect buildables with ordinary designators (33)

From direct `designationCategory` tags in `Defs/**` (a def that inherits its category from a parent would not show here).

| Category | Things (label) | file |
|---|---|---|
| Structure (13) | wooden ladder, steel fire-escape ladder, portable ladder, pit ramp, swale, pit spikes, pit guardrail, sluice box, ford stones (terrain), bank stake, weir, silt-trap, ferry post | `Defs/Canals/ThingDefs/FlowWorks_ThingDefs.xml`, `FlowWorks_PitAccess.xml`, `Defs/Rivers/RM_PlacerWorks.xml`, `RM_FordStones.xml`, `RM_BankWorks.xml` |
| Security (3) | concealed pit (woven scrap / planks / reinforced) | `Defs/Pits/ThingDefs/RM_PitCovers.xml` |
| Production (5) | liquid drill, bleed well, reaction vat, liquid pump, ice melter | `Defs/Drilling/`, `Machinery/Kits/`, `LiquidTypes/ThingDefs/RM_LiquidPump.xml`, `Pits/ThingDefs/RM_CrushedIce.xml` |
| Power (1) | power cord | `Defs/Machinery/RM_PowerCord.xml` |
| Misc (1) | panning spot | `RM_PlacerWorks.xml` |
| "pipe networks" (10; the mod's own tab `VCHE_PipeNetworks`) | pipe faucet, hose reel, sprinkler head, pipe pole, universal pipe, universal cargo tank, extra-tall cargo tank, liquid tank, tall liquid tank, chemfuel pipe adapter | `Defs/Machinery/RM_PipeNetworksTab.xml` and the files named in each def; adapter `Patches/Machinery/RM_PipeNetAdapters.xml:39` |
| Not in Architect | drawbridge winch houses and gate, bridge anchors/decks/railing (placed by section 5 designators); map controls (flow source, flow sink, flow meter, level holder, timer switch, map-edge setter, current painter, liquid thermostat: dev-mode debug actions only, "NOT buildable: no designationCategory") | `Defs/Canals/ThingDefs/FlowWorks_MapControls.xml:1-12` |

## 7. Gizmos on selected things (player-facing)

| Selected thing | Label as shown | What it does | Setting that hides or changes it | file:line |
|---|---|---|---|---|
| Ladder (built, not portable) | "Ladder up" / "Ladder down" (toggle) | orders a colonist (BasicWorker) to raise or lower it | `ladderRaiseLowerEnabled` | `Source/Superdeep/RM_LadderUtility.cs:436-460` |
| Sluice gate | "Gate lifted" / "Gate down" (toggle, replaces vanilla hold-open) | orders a colonist to lift or lower | (none found) | `Source/Superdeep/RM_FlowDoors.cs:170-190` |
| Drawbridge leaf | "Raise drawbridge", "Lower drawbridge", "Hold raised" (toggle), "Place winch house" | a colonist raises or lowers it; hold locks it up; winch house places the winch | `drawbridgesEnabled` | `Source/Pits/Drawbridge/RM_Drawbridges.cs:898-925`; `RM_DrawbridgePackage.cs:181-192` |
| Suspension bridge | "Railings: on/off" (toggle) | shows or hides the railings | bridge settings | `Source/Pits/Suspension/RM_MapComponent_SuspensionBridges.cs:1202` |
| Hose reel | "Deploy hose", "Move hose end", "Retract hose", "Choose style", "Cancel hose order", "End look: nozzle/cap/plain", "Free end: <role>" (7) | lays, moves, pulls in, restyles the hose | hose settings | `Source/Hose/CompHoseReel.cs:818-880` |
| Liquid pump | "Drawing into the tank" / "Pouring into the channel" (toggle) | pump direction | | `Source/LiquidTypes/Building_LiquidPump.cs:678` |
| Liquid tank | "Job: Store / Fill / Empty / Dump" | tank job mode | | `Source/LiquidTypes/Building_LiquidTank.cs:177` |
| Pipe adapter | "Mode: feed pipe net / draw from pipe net / shut" | direction | | `Source/Machinery/CompLiquidPipeAdapter.cs:272` |
| Pipes, tanks, weir | "Choose style" (float menu of looks; offers "this section" or "whole joined wall" / "every selected one") | repaints | | `Source/Machinery/PipeLook.cs:164, 238`; `Source/Rivers/RM_Weir.cs:821` |
| Smart sprinkler | "Daily budget: N L", "Reserve floor: N L" (float menus) | water use limits | | `Source/Sprinklers/CompRM_SmartSprinkler.cs:304, 312` |
| A colonist beside a pit | "Jump into pit" | jumps down (hurts) | `superdeepCaptureEnabled` | `Source/Superdeep/RM_SuperdeepTrap.cs:1235-1260` |

Dev/God only (not for a normal player): hose "DEV: lay hose instantly", "reel in instantly", "flow through hose" (`CompHoseReel.cs:893-911`, Dev Mode);
"DEV: ladder up/down now" (`RM_LadderUtility.cs:461`); gate "Force open", "Force close" (God Mode, `RM_FlowDoors.cs:191-205`); "DEV: make
drawbridge", "DEV: raise/lower leaf" (God Mode, `RM_Drawbridges.cs:1037-1062`); tank "Dev: fill", "Dev: empty" (`Debug/FlowWorksTankDebug.cs:122-130`);
map-control gizmos ("On", "Remove", "Radius: N", "Rate...", "Liquid: X", "Takes: X", "Hold at N%", "Hold at N C", "Flows <compass>", "Fast", "Schedule...",
"Invert", "<edge>: <mode>", "Read now") in `Source/MapControls/*.cs`.

## 8. Right-click (float menu) options

| Label as shown | Where | What it does | Setting | file:line |
|---|---|---|---|---|
| a climb-over-wall option (label built at line 484 from a translation key; exact text not read; roofed variant) | right-click a wall | colonist climbs over | wall-climb settings | `Source/Superdeep/RM_WallClimb.cs:460-490` |
| "Capture down" (translated, with a verdict in brackets) | right-click a pawn in a pit | capture a downed pawn in a pit | pit room rules | `Source/Superdeep/RM_PitRooms.cs:649-690` |
| "Soak in the hot pool" | right-click a geyser pool | colonist soaks | | `Source/Superdeep/JobDriver_RM_SoakInGeyserPool.cs:202-225` |
| Hose right-clicks | on hose ends / reel | see file | | `Source/Hose/Jobs/FloatMenuOptionProvider_Hose.cs:14-80` |
| Fixes vanilla "go to" for drafted pawns in pits | drafted pawn move | not a new option; patches `FloatMenuOptionProvider_DraftedMove` | | `Source/Superdeep/RM_PitDepthDraw.cs:249` |

## 9. Obvious overlaps and duplicates (facts only)

- Three Orders buttons run the same `RM_DigCanal` designation and job: Dig pit (one notch), Dig to depth (up to N notches), Repair breach (dig-to restricted to raider scars). Dig pit and Dig to depth are the same tool with and without a menu.
- Two Orders buttons run the same fill job: Fill in pit (one notch), Restore ground (repeat to surface).
- Fill and dig on the same square cancel each other (newer wins).
- A dig order and Mine/Smooth/Plan/Remove-floor are four different mechanics in one tab; the mod's five sit beside them.
- Digging is one work type (Mining) with two work givers (dig pits, fill in pits), shared with vanilla mining.
- The depth menu estimate and the Mod Settings labour line disagree by the x4 labour multiplier (section 2).
- Ladders, ramps, spikes, guardrails, covers, bridges and drawbridges all serve a dug pit but live under Structure and Security, not Orders.

## 10. How vanilla does comparable things (unverified: from memory of RimWorld 1.5/1.6, not checked against decompiled source)

- **One Mine order** (Orders > Mine): a single drag tool, no menu; the job runs at MiningSpeed. Vanilla has no depth. [unverified]
- **Smooth**: one tool "Smooth floor" (and "Smooth wall" separate), no menu. [unverified]
- **Plan** (Architect > Orders-adjacent "Plan"): one tool; Dig, Plan, and Remove floor/Remove roof etc. are small one-click tools in Orders. [unverified]
- **Remove floor**: one tool, no depth. [unverified]
- Depth-like or amount choices in vanilla use a **gizmo with a slider or a small float menu** on the selected thing: the zone Stockpile/Growing zone filters and "Set target count" dialogs, bill "Do until X" popups (Dialog with a slider), the "Hold fire/Move to" quick choices; a Growing zone's plant choice is a small float menu on a gizmo. Designators with sub-choices (e.g. the mod "Wall" with material) use a **material picker as a small float menu or sub-tab** shown under the designator, not a long list. [unverified]
- Architect also offers `designatorDropdown` (a grouped button with a small arrow: for example Floors/Wall/Door variants group into one dropdown button); a mod can fold related tools into one dropdown instead of separate buttons. FlowWorks' five Orders designators do not use one (grep: no `designatorDropdown` in the FlowWorks defs, [measured]).

## Owner's words (verbatim, 2026-11-13 ~9:45 PM PST, live at the game)

"Colonist DID start digging, and it's slow. We will want to think about what the dig interface should be. The vast grid of options when I selected Digging was... daunting and not how the game usually is. Worth some deeper design. There's also a LOT of options for dig, repair, fill in, all sorts of things. So a full consolidation of the UI is worth it once we know all the options we need."

## Limits of this census

- Section 6 counts only defs that carry `designationCategory` themselves; defs that inherit it via an abstract parent in another file may be missed [guess: few].
- Section 7 lists gizmo sites found by `new Command_Action/Toggle` in `Source/` (not SelfTest), with labels from the same lines or from `Languages/English`; some gizmos build their labels dynamically (tank, pump, adapter).
- Not covered: Mod Settings pages themselves (a separate surface), alerts, letters, the Work tab beyond the work givers named, other mods' designators, DLC-patched content.
