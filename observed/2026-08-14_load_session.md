# Live session ledger - 2026-08-14

_Written by `src/RimMandrake/bridgetools/load_session.py`. `NEEDS EYES` is a real verdict: the evidence is collected and the picture has not been looked at yet._

**ERROR** 2  **FAIL** 2  **NEEDS EYES** 14  **PASS** 10  **SKIP** 2

| id | verdict | item | evidence |
|---|---|---|---|
| A0 | PASS | companion census | 26 jawa tools of 26 expected (151 on the bridge overall) |
| A0b | PASS | settle window | waited 40s after first bridge contact before mutating (owner: the game is not reactive for ~40s, whatever the ready flags say) |
| A1 | PASS | Rebel Alliance stays suppressed | OuterRim_RebelAlliance absent (absent is CORRECT, VISION R2); 54 factions, countAllIncludingHidden=54 |
| A1b | PASS |   ...control: Galactic Empire generated | OuterRim_GalacticEmpire present |
| A2p | PASS |   ...console located | PilotConsole id=PilotConsole44499 at (129,149) |
| A2 | FAIL | NoPathToPilotConsole | 0 of 1 colonists reach Pilot console (pathEndMode=InteractionCell). No movement, game left paused. |
| A4 | FAIL | order_pawn moves a pawn | Alex {'x': 116, 'z': 146} -> {'x': 116, 'z': 146}, ticksElapsed=245, canReach=False |
| A4b | PASS |   ...and put back, undrafted | home=(116,146) end={'x': 116, 'z': 146} leftDrafted=[] |
| A5-Desert | PASS | dune seas widened in Desert | SoftSand min = pm0:0.55, want 0.55 (vanilla 0.65); 2 patchmaker(s) |
| A5-ExtremeDesert | PASS | dune seas widened in ExtremeDesert | SoftSand min = pm0:0.5, want 0.50 (vanilla 0.65); 2 patchmaker(s) |
| A6 | PASS | Cherry Picker: no total-loss line | 0 Cherry Picker line(s); 0 FAILED; no master-list error |
| A6c | SKIP |   ...and silence proves nothing | an unresolvable key logs NOTHING. The keys are read back below. |
| A6A-GhoulInfusion | PASS | RecipeDef/GhoulInfusion absent | absent from the DefDatabase, as intended. ⚠️ 1,144 defs reference it in <recipes> as direct object references resolved before startup, so absence here does NOT mean the surgery is gone -- check a pawn. |
| A6 | ERROR | Cherry Picker actually removed things | UnicodeEncodeError: 'charmap' codec can't encode characters in position 107-108: character maps to <undefined> |
| A7 | NEEDS EYES | sea vs the owner's spec (~25%, 3 bodies) | water 16.67% in 2 bodies >=8 tiles (2 total), largest 8.33% of planet; seed=sandal coverage=0.3. Spec is ~25% in 3. |
| P1 | NEEDS EYES | AV_DogSled | VehicleDef, not a ThingDef. Want TWO EOPIE not four dogs, and a BROWN body -- the brown is a def patch (graphicData/color 99,65,24), so grey means the patch did not apply, NOT that the art is wrong. |
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

- `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Screenshots\p1_001.png` - AV_DogSled
- `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Screenshots\p2_002.png` - PH_DoorBlastCDoor
- `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Screenshots\p3_003.png` - PH_DoorThickBlastBDoor
- `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Screenshots\p4_004.png` - PH_DoorBlastDDoor
- `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Screenshots\p5_005.png` - VAEA_Apparel_ToolBelt
- `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Screenshots\p6_006.png` - RR_FieldResearchKitSimple
- `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Screenshots\p7_007.png` - RR_FieldResearchKitHiTech
- `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Screenshots\p8_008.png` - RR_FieldResearchKitMultiAnalyzer
- `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Screenshots\p9_009.png` - RR_FieldResearchKitRemote
- `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Screenshots\p10_010.png` - VGE_Astronaut
- `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Screenshots\p11_011.png` - OuterRim_MSEDroid
- `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Screenshots\p12_012.png` - OuterRim_CereanMane
- `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Screenshots\p13_013.png` - VRESaurids_Littlefoot

## Awaiting a look - 14 item(s)

🔴 **Record what you actually saw, INCLUDING "this looked normal".** Owner's directive 2026-08-13: art fixes are stopped until someone verifies the art was broken in the first place, so a normal-looking row is the evidence being asked for. A blank entry loses it.

| id | item | what I saw |
|---|---|---|
| A7 | sea vs the owner's spec (~25%, 3 bodies) |  |
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

- AV_DogSled x1 at (100,120)
- PH_DoorBlastCDoor x1 at (106,120)
- PH_DoorThickBlastBDoor x1 at (112,120)
- PH_DoorBlastDDoor x1 at (118,120)
- pawn Human47017 (VAEA_Apparel_ToolBelt wearer) at (124,120)
- pawn Human47022 (RR_FieldResearchKitSimple wearer) at (130,120)
- pawn Human47027 (RR_FieldResearchKitHiTech wearer) at (100,126)
- pawn Human47031 (RR_FieldResearchKitMultiAnalyzer wearer) at (106,126)
- pawn Human47037 (RR_FieldResearchKitRemote wearer) at (112,126)
- pawn VGE_Astronaut47042 (VGE_Astronaut) at (118,126)
- pawn OuterRim_MSEDroid47043 (OuterRim_MSEDroid) at (124,126)
- pawn Human328 (OuterRim_CereanMane) at (130,126)
- pawn Human340 (VRESaurids_Littlefoot) at (100,132)

⚠️ **The release message is written from the list above, not from memory.**
