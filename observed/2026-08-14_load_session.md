# Live session ledger - 2026-08-14

> 🔴 **DO NOT SPEND EYES ON THE TWELVE SCREENSHOTS BELOW. THEY ARE NON-EVIDENCE.**
> Found 2026-08-14 by BRIDGE, by opening the pictures instead of reading the row.
>
> The camera was aimed correctly — `look()` jumps to the subject's cell and puts
> it dead centre — and **RimWorld's Debug log window covers the centre of the
> screen**, roughly 940x650 px of scrolling text over the thing being
> photographed. The pawn inspect pane covers the bottom-left and the dev palette
> the top-left. In `p5_004.png` (VAEA_Apparel_ToolBelt) and `p13_012.png`
> (VRESaurids_Littlefoot) **the subject is not visible anywhere in frame.**
>
> Every one of those rows says `NEEDS EYES`, which reads as *collected, awaiting
> judgement*. They were collected. There is nothing in them. Judging art from
> them would have produced twelve confident verdicts about pictures of a debug
> log — and "the art is fine" is the answer that costs the most to be wrong about.
>
> **Fixed for next session, not for these files:** `jawa/clear_ui` closes every
> dev window and drops the selection, and `rimbench.core.look()` now calls it
> before every screenshot. ⚠️ Closing the log by hand does not survive —
> auto-open-on-error reopens it, and a modded startup throws errors all session.
> **The twelve rows must be re-shot; they cannot be rescued.**

_Written by `src/RimMandrake/bridgetools/load_session.py`. `NEEDS EYES` is a real verdict: the evidence is collected and the picture has not been looked at yet._

**ERROR** 3  **NEEDS EYES** 13  **PASS** 8  **SKIP** 3

| id | verdict | item | evidence |
|---|---|---|---|
| A0 | PASS | companion census | 22 jawa tools of 22 expected (147 on the bridge overall) |
| A1 | PASS | Rebel Alliance stays suppressed | OuterRim_RebelAlliance absent (absent is CORRECT, VISION R2); 54 factions, countAllIncludingHidden=54 |
| A1b | PASS |   ...control: Galactic Empire generated | OuterRim_GalacticEmpire present |
| A2 | SKIP | NoPathToPilotConsole | no --console-id given; find the PilotConsole ThingID first (select it in game, or spawn one) |
| A4 | PASS | order_pawn moves a pawn | Paige {'x': 111, 'z': 139} -> {'x': 117, 'z': 139}, ticksElapsed=240, canReach=True |
| A4b | PASS |   ...and put back, undrafted | home=(111,139) end={'x': 111, 'z': 139} leftDrafted=[] |
| A5-Desert | PASS | dune seas widened in Desert | SoftSand min = pm0:0.55, want 0.55 (vanilla 0.65); 2 patchmaker(s) |
| A5-ExtremeDesert | PASS | dune seas widened in ExtremeDesert | SoftSand min = pm0:0.5, want 0.50 (vanilla 0.65); 2 patchmaker(s) |
| A6 | PASS | Cherry Picker: no total-loss line | 0 Cherry Picker line(s); 0 FAILED; no master-list error |
| A6c | SKIP |   ...and silence proves nothing | an unresolvable key logs NOTHING. The keys are read back below. |
| A6 | ERROR | Cherry Picker actually removed things | NameError: name 'ok' is not defined |
| A7 | ERROR | world_stats: the sea, measured | NameError: name 'ok' is not defined |
| P1 | NEEDS EYES | AV_DogSled | spawn_batch placed nothing: [{'op': 0, 'def': 'AV_DogSled', 'x': 120, 'z': 140, 'error': 'NullReferenceException: Obje -- a VehicleDef may not construct through spawn_batch at all; that is a TOOL gap, not a verdict on the art. |
| P2 | NEEDS EYES | PH_DoorBlastCDoor | rotated EAST. rotated EAST, open and closed |
| P3 | NEEDS EYES | PH_DoorThickBlastBDoor | rotated EAST. rotated EAST, open and closed |
| P4 | NEEDS EYES | PH_DoorBlastDDoor | rotated EAST. EAST; the iris ring must survive |
| P5 | NEEDS EYES | VAEA_Apparel_ToolBelt | WORN, facing WEST. ⚠️ NOT `ToolBelt`, which exists nowhere. Two mods label an item 'tool belt', so never spawn this by label. WORN, pawn facing WEST. |
| P5 | ERROR | VAEA_Apparel_ToolBelt | UnicodeEncodeError: 'charmap' codec can't encode characters in position 64-65: character maps to <undefined> |
| P6 | NEEDS EYES | RR_FieldResearchKitSimple | WORN, facing EAST. WORN, facing EAST |
| P7 | NEEDS EYES | RR_FieldResearchKitHiTech | WORN, facing EAST. WORN, facing EAST |
| P8 | NEEDS EYES | RR_FieldResearchKitMultiAnalyzer | WORN, facing EAST. WORN, facing EAST |
| P9 | NEEDS EYES | RR_FieldResearchKitRemote | WORN, facing EAST. WORN, facing EAST |
| P10 | NEEDS EYES | VGE_Astronaut | facing NORTH. facing NORTH, and spawn BOTH life stages -- the adult's north was never broken, so a juvenile-only shot can pass on art nobody fixed |
| P11 | NEEDS EYES | OuterRim_MSEDroid | facing NORTH. facing NORTH |
| P12 | NEEDS EYES | OuterRim_CereanMane | facing SOUTH. facing SOUTH; donor is 1,514 B of fully transparent pixels, so the failure is a bald head |
| P13 | NEEDS EYES | VRESaurids_Littlefoot | facing NORTH. facing NORTH; centre frill |
| F1 | SKIP | v1 row 7 desert worldgen (HELD -- do not run) | phase=fresh, this run is any |

## Screenshots - open these

- `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Screenshots\p2_001.png` - PH_DoorBlastCDoor
- `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Screenshots\p3_002.png` - PH_DoorThickBlastBDoor
- `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Screenshots\p4_003.png` - PH_DoorBlastDDoor
- `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Screenshots\p5_004.png` - VAEA_Apparel_ToolBelt
- `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Screenshots\p6_005.png` - RR_FieldResearchKitSimple
- `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Screenshots\p7_006.png` - RR_FieldResearchKitHiTech
- `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Screenshots\p8_007.png` - RR_FieldResearchKitMultiAnalyzer
- `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Screenshots\p9_008.png` - RR_FieldResearchKitRemote
- `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Screenshots\p10_009.png` - VGE_Astronaut
- `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Screenshots\p11_010.png` - OuterRim_MSEDroid
- `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Screenshots\p12_011.png` - OuterRim_CereanMane
- `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Screenshots\p13_012.png` - VRESaurids_Littlefoot

## Awaiting a look - 13 item(s)

🔴 **Record what you actually saw, INCLUDING "this looked normal".** Owner's directive 2026-08-13: art fixes are stopped until someone verifies the art was broken in the first place, so a normal-looking row is the evidence being asked for. A blank entry loses it.

| id | item | what I saw |
|---|---|---|
| P1 | AV_DogSled |  |
| P2 | PH_DoorBlastCDoor |  |
| P3 | PH_DoorThickBlastBDoor |  |
| P4 | PH_DoorBlastDDoor |  |
| P5 | VAEA_Apparel_ToolBelt |  |
| P6 | RR_FieldResearchKitSimple |  |
| P7 | RR_FieldResearchKitHiTech |  |
| P8 | RR_FieldResearchKitMultiAnalyzer |  |
| P9 | RR_FieldResearchKitRemote |  |
| P10 | VGE_Astronaut |  |
| P11 | OuterRim_MSEDroid |  |
| P12 | OuterRim_CereanMane |  |
| P13 | VRESaurids_Littlefoot |  |

## Left on the map

- PH_DoorBlastCDoor x1 at (126,140)
- PH_DoorThickBlastBDoor x1 at (132,140)
- PH_DoorBlastDDoor x1 at (138,140)
- pawn Human37567 (VAEA_Apparel_ToolBelt wearer) at (144,140)
- pawn Human37571 (RR_FieldResearchKitSimple wearer) at (150,140)
- pawn Human37577 (RR_FieldResearchKitHiTech wearer) at (120,146)
- pawn Human37581 (RR_FieldResearchKitMultiAnalyzer wearer) at (126,146)
- pawn Human37586 (RR_FieldResearchKitRemote wearer) at (132,146)
- pawn VGE_Astronaut37590 (VGE_Astronaut) at (138,146)
- pawn OuterRim_MSEDroid37591 (OuterRim_MSEDroid) at (144,146)
- pawn Human37592 (OuterRim_CereanMane) at (150,146)
- pawn Human37596 (VRESaurids_Littlefoot) at (120,152)

⚠️ **The release message is written from the list above, not from memory.**
