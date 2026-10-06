# FlowWorks art commission B — River Works / Pit / Canal art (2026-10-05)

Owner, 2026-10-05: *"commission all needed art so we can start reviewing more"*.
Agent B (FOUNDRY art-commission). Status: DONE — 10 jobs queued; install is a follow-up.

Art list (the briefs): `infrastructure/artpipe/art_lists/flowworks_rivers_pits_art_2026-10-05.json`.
Queue at filing: 316 pending / 8 active; these sit at priority 90-95 (default is 100), so they do not jump the queue ahead of 60-priority work.

## Inventory (asset → state)

| asset | def | today | action |
|---|---|---|---|
| weir (also the fish catch: the catch spawns as items on its bank end, no separate building) | `RM_BankWeir` 1x2, drawSize (1.4,2.2), Graphic_Single rotatable | placeholder PNG (512x512) | QUEUED `RM_BankWeir_v1` 256x400 |
| stake-line / levee (a continuous line of stakes IS the levee) | `RM_BankStake` 1x1, drawSize 0.6, lamp glower | placeholder PNG | QUEUED `RM_BankStake_v1` 128 |
| silt-trap | `RM_SiltTrap` 1x1, drawSize 1.2 | placeholder PNG | QUEUED `RM_SiltTrap_v1` 256 |
| ferry post | `RM_FerryPost` 1x1, drawSize 0.8 | placeholder PNG | QUEUED `RM_FerryPost_v1` 128 |
| ferry rope | none; drawn only as a selection line (`RM_FerryAndLevee.cs` DrawExtraSelectionOverlays → GenDraw.DrawLineBetween) | invisible in world | QUEUED `RM_FerryRope_v1` 256x64 tileable strip; a C# rope drawer is owed before it shows (not mine to write) |
| ford stones | `RM_FordStones` TerrainDef | vanilla `Terrain/Surfaces/Flagstone` | QUEUED `RM_FordStones_v1` 1024 opaque seamless |
| pit spikes | `RM_Spikes` | Ideology `Skullspike` | ALREADY QUEUED (`pending/RM_Spikes.json`, EXCAVATION_WALL_ART_1) — not refiled |
| wall faces | none (SectionLayer strips) | — | ALREADY QUEUED (`RM_WallFace_North`, `RM_WallFace_Side`) — but see "Wall faces" below: no code reads them |
| sluice door | `RM_Sluice` (DoorBase, stuffable) | vanilla `DoorSimple_Mover` + `DoorSimple_MenuIcon` | QUEUED `RM_Sluice_Mover_v1` 256, `RM_Sluice_MenuIcon_v1` 128 |
| security grate door | `RM_SecurityGrateDoor` (DoorBase, stuffable) | vanilla `DoorSimple_Mover` + `DoorSimple_MenuIcon` | QUEUED `RM_SecurityGrateDoor_Mover_v1` 256, `RM_SecurityGrateDoor_MenuIcon_v1` 128 |
| pit covers ×3 | `RM_PitCover_*` | `Terrain/Surfaces/Soil` | NONE OWED — by design the cover prints the surrounding terrain (`RM_PitCovers.xml` header, `Building_PitCover.cs`) |
| swale | `RM_Swale` | vanilla `GraveEmpty` | NOT QUEUED — existing render + owner ruling, see below |
| ladder | `RM_Ladder` | vanilla `TrapSpikeArmed` | DEFERRED — owner's A/B pick |
| sluice box + panning | (builder Y helper, not on origin yet) | — | nothing to brief yet; FLOWWORKS_QUARRY_DIGGING_1 rivers half is gated on MINERALS_WHERE_THEY_BELONG_1 |

Search evidence: `artpipe_state.py find` for WallFace, Spikes, Weir, StakeLine, SiltTrap, FishCatch, Ferry, FordStone, Levee, Sluice, PitCover — no finished art for any river works piece (the 11 "weir" hits are unrelated creature/seismograph prompts).

## Existing art found (wire via art ledger, no regen)

- **`RM_Swale`** — `D:\Luke\dev\_artpipe\_artsrc\RM_Swale\RM_Swale.png` (2026-09-28). Owner ruled `regen` on the cracked-lands sheet (`infrastructure/state/art_rulings/2026-09-28_bedazzle_art_sheets_2026-09-28__cracked_lands__sheet.decisions.json`), verbatim: *"I think you're going to need to take screenshots of what canals look like before you can actually generate this art. You can use this as placeholder as long as you make a ticket to work with Flowworks to make an actual canal and take snapshots of a live example so you can spec out the art."* ⇒ installable as a PLACEHOLDER now (better than GraveEmpty); the real regen waits on a live canal capture (no bridge in this pass). `D:\Luke\dev\_artpipe\_artsrc\RM_Swale_v2\RM_Swale_v2.png` (2026-09-30) also exists, provenance not traced — check before installing either.
- **Sluice gate concepts** `D:\Luke\dev\RimMandrake\src\RimMandrake\FlowWorks\art_source\phone_review_2026-09-16\RUT_SluiceGate_{A,B}_{closed,open}.png` (+ done jobs `flowworks_sluicegate_stonemetal_{open,closed}`, an edit of A). These predate FLOWWORKS_DOOR_FAMILY_1 (2026-09-17: the sluice became a stuffable DoorBase), so they are abutment-and-gate drawings, not door movers, and cannot be wired as a door's mover. No owner ruling found on A vs B. The new mover jobs are neutral greyscale panels and do not pick between A and B.

## Wall faces — no consumer in code

`RM_WallFace_North` / `_Side` are pending (EXCAVATION_WALL_ART_1). The visuals pass (principle 2, `Transient\belt_fwvisuals_20261005.md`) now draws each face from the neighbour ground's **own terrain material** plus strata/joints, and no `.cs` file references a `WallFace_` texture. So those two strips will render into nothing as things stand. Left queued, not withdrawn (another agent's jobs; generated art is not disposable). The note is in the visuals file; it is that agent's call to withdraw them or wire them in.

## Deferred

- **Ladder** (`D:\Luke\dev\RimMandrake\src\RimMandrake\FlowWorks\art_source\phone_review_2026-09-16\RUT_Ladder_A.png` vs `RUT_Ladder_B.png`) — WAITING ON THE OWNER'S PICK. Not commissioned, nothing picked.
- **Swale regen** — waits on a live canal capture (owner ruling above).
- **Ferry rope in world** — art queued; a C# drawer is owed (FlowWorks builder), today only a selection line.
- **Sluice box / panning** — nothing built to brief against.

## Install follow-up (offered) — defs whose texPath changes on install

Install through `art install` only (`design/RimMandrake/art_ledger_design_2026-10-04.md` §2.1), after a review/ruling.

| def | field | today | after install |
|---|---|---|---|
| `RM_BankWeir` | graphicData/texPath | `Things/Building/FlowWorks/Rivers/RM_BankWeir` | unchanged path, new PNG |
| `RM_BankStake` | graphicData/texPath | `…/Rivers/RM_BankStake` | unchanged path, new PNG |
| `RM_SiltTrap` | graphicData/texPath | `…/Rivers/RM_SiltTrap` | unchanged path, new PNG |
| `RM_FerryPost` | graphicData/texPath | `…/Rivers/RM_FerryPost` | unchanged path, new PNG |
| `RM_FordStones` | texturePath | `Terrain/Surfaces/Flagstone` | `Terrain/Surfaces/RM_FordStones` — and its `<color>(128,124,112)</color>` tint was there to make flagstone read as river stone; drop it or set white, or the new art is darkened |
| `RM_Sluice` | graphicData/texPath, uiIconPath | `Things/Building/Door/DoorSimple_Mover`, `…/DoorSimple_MenuIcon` | `Things/Building/FlowWorks/Doors/RM_Sluice_Mover`, `…/RM_Sluice_MenuIcon` |
| `RM_SecurityGrateDoor` | graphicData/texPath, uiIconPath | same vanilla pair | `Things/Building/FlowWorks/Doors/RM_SecurityGrateDoor_Mover`, `…/RM_SecurityGrateDoor_MenuIcon` |
| `RM_Spikes` | graphicData/texPath | `Things/Building/Misc/Skullspike/Skullspike` | `Things/Building/FlowWorks/RM_Spikes` (from the earlier job); drop `CutoutComplex` unless the art ships a mask |
| `RM_Swale` (placeholder) | graphicData/texPath + graphicClass | `Things/Building/Misc/GraveEmpty`, Graphic_Multi | e.g. `Things/Building/FlowWorks/RM_Swale`, Graphic_Single (one render, not rotatable) |

⚠️ Door movers: the briefs ask for a left-right symmetric panel because the engine slides and mirrors the mover; the exact vanilla mover canvas and draw were not measured this pass (no resources.assets read). Check against `DoorSimple_Mover` before installing.
