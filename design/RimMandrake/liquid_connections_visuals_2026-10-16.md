# Liquid connections: pump, hose and joins (HOSE_JOINTS_REDESIGN_PUMP_TOO_PUNY)

Owner 2026-10-16, from two screenshots of a pump, hose, pipe and tank in game:

> "I'm afraid the flexible hose seems absolutely enormous when attached to things like pumps and the like. The pump needs to
> be made to be commeasurate with such a think tube. And we might need to shrink the tube diameter a bit to make it less
> fire-hydrant-thick as it is now. But the pump should definitely be significantly heftier in appearance. There definitely
> needs to be thought given to what they look like when connected: anything the hoses can connect to (pumps, tanks, reels) as
> well as when you place a tank, reel, or pump next to each other some kind of connection should be visually apparent. The
> hard-built pipe I just built: I can't change the style on it even though there is such a button. It doesn't seem to do
> anything. I also just placed a flexible hose to connect to a solid pipe and it just lays the flexible hose on the pipe. The
> pipe needs connectors that show where it's connecting. Same thing if you build a pipe alongside a tank but not under it:
> the pipe looks like it doesn't even connect, but it should."

Status: **mockups on the review sheet, awaiting his ruling.** The pipe style bug is fixed and shipped in source.

## Measured (source, 2026-10-16)

| thing | today | where |
|---|---|---|
| hose visible width | 0.38 cell flat, 0.465 plump | `HoseMath.FlatVisible`, `PlumpExtra` |
| hose end coupling | about 2.4 x the visible width (1.13 cells at 0.465) | `HoseMath.FittingSize`, `Coupling_Bare` |
| rigid pipe band | 0.227 cell (40 of 176 px per atlas tile) | `Pipe/<Look>/UniversalPipe_Atlas.png` |
| pump | 1 x 1 footprint, drawSize 1, one look, no styles | `RM_LiquidPump.xml` |
| hose reel | 2 x 2, drawSize 2.8, four looks | `RM_HoseReel.xml` |
| tanks | 2 x 2 (tall: drawn 2 x 3 / 2 x 4), four looks | `RM_LiquidTank.xml`, `RM_LiquidLogistics.xml` |

So the plump hose is **twice the pipe** and nearly half the pump's whole drawing.

## Join types, how each connects, how each draws today

| join | connects when (net rule, `RM_LiquidNetKernel`) | draws today |
|---|---|---|
| hose to pump | hose free end beside or on it (`HosePorts.FindAt`, Machine kind) | the hose coupling butts the 1-cell pump edge |
| hose to tank | same, Tank kind | coupling at the tank edge, no port on the tank |
| hose to reel (relay) | end on the relay reel's intake | coupling into the reel's west inlet (separate item redrew it) |
| hose to pipe | end on or beside a pipe cell | the hose just lies on the pipe; coupling points along the hose |
| reel to pipe/tank | reel perimeter scan (`HosePorts.Find`) | a short flat feed hose and coupling (`DrawFeed`) |
| pipe to tank | pipe cardinal to or under the tank | under: hidden. Beside: the atlas ends in a cap short of the tank (the tank has no link flag) |
| pipe to pump | pipe 8-way around or under the machine | same cap, short of the pump |
| pump to tank | machine touches tank 8-way | nothing drawn |
| pipe to pipe | cardinal | the linked atlas joins them (fine) |

## Proposal (the sheet's rows)

1. **Pump**: footprint **2 x 1**, drawn **2 x 2** (drawOffset z +0.5); a squat motor-plus-volute station on a skid, four looks
   matching the tanks and reels (Scrapper rust/wood skid, Industrial gunmetal with hazard stripes, Modern red enamel, Futuristic
   white with cyan lines). Inlet flange west, outlet flange east, each about 0.26 cell across: sized to the thinner hose.
   Footprint change is gameplay-visible (placement), so it is his call; a 1 x 1 footprint with a 2-cell drawing would overlap
   neighbours.
2. **Hose**: **0.65 x** today, i.e. **0.25 flat / 0.30 plump**, still a little thicker than the rigid pipe. Every fitting, wrap
   and clearance scales with it (`HoseMath.WidthScale`). The reel outlets were drawn for the 0.465 hose and will look large
   on a 0.30 one; if he takes the thinner hose, the reel coupling needs the same rescale.
3. **Connectors**, per look (art at `RimMandrake/FlowWorks/Joins/<Look>/`):
   - **Flange** (0.5 x 0.5 cell): where a pipe meets a tank or machine, its face on the shared edge; a pipe beside a tank also
     runs its arm on to that edge instead of ending in a cap.
   - **Flange pair / Coupler**: where a pump (or reel) shares an edge with a tank. The mock uses two flanges back to back; a
     dedicated `Coupler` piece can replace it.
   - **Saddle** (1 x 1 cell): a clamped tee on the pipe cell a hose end couples onto, its spigot pointing at the viewer, the
     hose rising into it.
   - **Tank port**: the hose-to-tank mock shows a flange on the tank edge; the tank sprites themselves carry no port.

Mockups: `Transient/liquid_connections_2026-10-16/` (`gen.py` renders, `conform.py` sizes, `mock.py` composites,
`register.py` builds the sheet manifest). Sheet: `Transient/biome_ffar/liquid_connections_sheet_2026-10-16.html`.

## Built now (no art ruling needed)

- **Pipe style fix**: `PipeLook.SetLook` now calls `Notify_ColorChanged()`. `ThingStyleHelper.SetStyleDef` stores the style
  but never clears `Thing.styleGraphicInt`, so the redrawn mesh used the cached old look.
- **Draw hooks** (`Machinery/RM_LiquidJoins.cs`, geometry in Verse-free `LiquidJoinRule.cs`, selftested):
  - `pipeLinksIntoMachines` (setting, **on**): a pipe cardinal to a tank or liquid machine links its atlas arm to the shared
    edge (Harmony postfix on `Graphic_Linked.ShouldLinkWith`); tanks and machines spawning or despawning dirty the cells round
    them.
  - `joinFittings` (setting, **off**): `SectionLayer_RM_LiquidJoins` prints flanges and pump-tank couplers; the hose end draws a
    saddle or flange on a pipe port. With no art installed every piece draws the hose `Coupling_Bare` as a stand-in.
  - `hose_thickness` (setting, **1.0**, slider 0.5 to 1): scales every hose width. The proposal is 0.65; the shipped value stays
    1 until he rules.

## Owed after his ruling

- Install the picked art through the art ledger; give the pump its four `ThingStyleDef`s and join it to `PipeLook`'s picker.
- Change the pump def (footprint, drawSize, drawOffset), the hose thickness default, and `joinFittings` default.
- Rescale the reel's outlet coupling if the hose shrinks.
- Live rows in `FlowWorks/validation.py` for the join meshes.
