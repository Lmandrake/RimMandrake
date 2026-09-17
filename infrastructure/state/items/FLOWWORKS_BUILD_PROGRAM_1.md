# FLOWWORKS_BUILD_PROGRAM_1 — one liquid mod, built on depth

Filed by BENCH 2026-09-16 from a full bench design session with the owner. **Read
`design/RimMandrake/fluid_canals_mod_definition.md` first** — it carries all 27 of his rulings from
that date, each traceable to his words, plus the measured facts about the existing code. This item is
the build order, not the design.

Supersedes `FLUIDITY_MOD_CONSOLIDATION_1`. Absorbs the scope of `FLUID_SOURCE_STOCK_MODEL_1`,
`CANAL_CONSTRAINED_SPREAD_1`, `LIQUID_SINK_DRAINAGE_1`, `CANAL_FILL_IN_DISPLACEMENT_1` and
`CANYON_FLOOD_ERASES_CANALS_1` as phases — those stay filed as the trackable units.

## The one-paragraph version

**FlowWorks** is one mod owning the whole liquid domain, built on a single primitive: an **excavated
cell with a depth**. Depth is the only Z-level in the game, and it is what makes liquid behaviour
possible. Every excavated cell carries `depth` D (0=surface, then shallow/mid/deep/SUPERDEEP) and
`fill` F, with `0 ≤ F ≤ D`. Crossing cost, capture, escape chance, capacity, drawn terrain and
climb-out all read from those two integers. Canals, pits, terraces and dig sites stop being types and
become *shapes*. Liquid moves by a **sort plus an overflow** at pulse boundaries — never a simulation.

## 🔴 Two laws that bound the scope. Every future request will try to erode them.

1. **We dig down. We never build up.** Depth belongs to excavated cells only; the surface is 0 forever.
   No hills, no berms, no ramps of raised earth. This asymmetry is what keeps a Z-system's cost out of
   pathing, rendering, line of sight, cover and roofing. "Can we have a raised berm?" is a Z-system in
   disguise; the answer is a wall, or nothing.
2. **Depth affects movement and liquid. Never sight or shooting** — with exactly one exception (ruling
   23): a pawn in a SUPERDEEP cell may only exchange fire with pawns in its own 8 neighbours. That is a
   *restriction*, never a bonus, which is why it does not drag in an elevation model. Stay cut: height
   advantage, cover from below, falling damage, thrown objects across levels, multi-level buildings,
   pressure/siphons/head-height flow.

## Phase 0 — DESKTOP ONLY, and it blocks real decisions

**✅ BOTH BLOCKERS MEASURED — BENCH on the Desktop via RimSage, 2026-09-16:**

1. **Temp terrain is CORE, not Odyssey.** `Map.tempTerrain` is constructed and
   ticked unconditionally (`Map.cs:585`, `Map.cs:972`, scribed at 889);
   `TempTerrainManager.Tick()`'s removal queue and `QueueRemoveTerrain` carry NO
   DLC gate — the only `ModsConfig.OdysseyActive` checks in the class guard the
   ice `FreezeManager` steady effects. `TerrainGrid.SetTempTerrain/
   RemoveTempTerrain/TempTerrainAt` are ungated (TerrainGrid.cs's Odyssey checks
   at 553/558 are substructure paths). The Odyssey lock on `ShallowFloodwater`/
   `MarshFlood` is def-level `[MayRequireOdyssey]` CONTENT gating. ⇒ FlowWorks
   ships its own `temporary="true"` terrains DLC-free; the recede policy unifies
   on `SetTempTerrain` + `QueueRemoveTerrain`.
2. **Ruling 23's patch point confirmed**: `public virtual bool
   Verb.CanHitTargetFrom(IntVec3 root, LocalTargetInfo targ)` at
   `Verse/Verb.cs:710` — virtual, prefix-able; the AI-selection side should
   also gate (see Phase 5's invalid-target note).

Still open from this phase: the FlowWorks Workshop name check (needs Fetcher/web).

🔴 **RimSage has never connected from the Laptop** (five session logs, 2026-09-02 → 09-16, all
timeouts; the hosted service returns HTTP 000; no decompiled tree on disk). So engine internals are
**UNMEASURABLE** there. Both facts below need ILSpy/dnSpy on the real `Assembly-CSharp.dll`, or
runtime reflection through the bridge.

1. **`TEMP_TERRAIN_DLC_GATE_1` — can we ship our OWN `temporary="true"` terrains?** Every base-game
   temporary terrain (`ShallowFloodwater`, `MarshFlood`) is `[MayRequireOdyssey]`, which is why
   FloodedCanyon went permanent-`SetTerrain` and DLC-free while FluidCanals went temp-terrain and
   Odyssey-locked. If `TerrainDef.temporary` and `TempTerrainManager` are Core, the whole family drops
   its hard Odyssey dependency and both terrain models unify. **This decides the engine's recede
   policy; do not guess it.**
2. **The exact member for the shooting restriction** — `Verb.CanHitTargetFrom` is the presumed patch
   point for ruling 23. Confirm the real signature before writing the prefix.

⚠️ Do NOT resolve either from repo prose. Several existing docs assert things about vanilla `Flood`
and terrain flammability that trace to an earlier agent's writing, not to a decompiler.

**Also unmeasured, and cheap to settle there:** whether any Workshop mod already uses the name
FlowWorks (WebSearch is dead on this model group; use Fetcher or the Desktop).

## Phase 1 — Consolidate, then rename

**✅ EXECUTED — BENCH-orchestrated lane, 2026-09-16.** Rename (ruling 20), ruling-24
deletions, and the Pits+ManyWaters+LiquidTypes merge into `src/RimMandrake/FlowWorks`
(one assembly, `RimMandrakeFlowWorks.dll`) landed together: build 0 errors, 54/54
selftests, validate_patch 0 errors, both silent-failure hazards cleared (DLL rebuilt
same pass; bridge reflection strings reworked, `jawa/canal_dig` stubbed to an honest
ruling-24 refusal). Deploy-time obligations and the open escalations (newly-live
LiquidCorrosion/LiquidIgnition MapComponents, the now-applying CompatIndex patch,
the Odyssey hard dependency pending the Phase-3 decouple, Phase-9 validation-walk
regrouping) are recorded in the Phase-1 closing commit's lane report. The measured
blast-radius table below is a point-in-time record of the PRE-rename state — do not
"fix" its old names.

His ruling 27 is merge-before-art, and consolidating first also avoids building the primitive in one
mod and moving it. Into **one mod**: `FluidCanals` + `Pits` + `ManyWaters` + `LiquidTypes` (the
registry). `GelatinousSlime` stays a sibling that *registers rows* and keeps its genes.
`WreckedMachines` keeps distillation. `FloodedCanyon` keeps its biome and becomes a **flood-driver
client** depending on FlowWorks.

The boundary is a principle, not a list: **FlowWorks owns what a liquid IS and DOES; a machine that
TRANSFORMS one liquid into another is technology and lives elsewhere.** That settles desalination,
detox, tar-cracking and boiling without another ruling.

### 🔴 The rename executes HERE, in this phase. There is no gate.

This phase previously said renaming was `NAMING_SCHEME_EXECUTION_1`'s job and must not run ahead of it.
**That item closed 2026-08-31 at `54a8e28d`** on the owner's word (*"Deploy the full rename."*) — 16
days before FlowWorks was even named. The gate was dead language copy-pasted forward, and it is why the
mod still ships as `fluidcanals`. Owner, 2026-09-16, on being shown this: *"No... we rename right now.
That's crazy."* He then ruled the execution into this phase rather than the Mac session, because two
compiled assemblies are involved.

Target (ruling 20): `RimMandrake: FlowWorks`, `mandrake.rm.flowworks`, namespace
`RimMandrake.FlowWorks`, prefix stays `RM_`.

**Blast radius, MEASURED on the Mac 2026-09-16 — do not re-derive this:**

| What | Where |
|---|---|
| Mod folder | `src/RimMandrake/FluidCanals/` |
| `namespace RimMandrake.FluidCanals` | 10 `.cs` under `Source/` (incl. `Debug/`) |
| XML naming the namespace in class fields | 5 files: `ThingDefs/FluidCanal_ThingDefs.xml`, `FluidDefs/FluidCanal_Fluids.xml`, `WorkGiverDefs/FluidCanal_WorkGivers.xml`, `JobDefs/FluidCanal_JobDefs.xml`, `Patches/FluidCanal_OrdersPatch.xml` |
| Display name + packageId | `About/About.xml` (`RimMandrake Fluid Canals`, `mandrake.rm.fluidcanals`) |
| Filenames carrying the old name | `RimMandrake_FluidCanals.csproj`, `RimMandrakeFluidCanals_DefOf.cs`, `RimMandrakeFluidCanalsMod.cs`, `FluidCanalsDebugActions.cs`, `Flood_FluidCanal.cs`, the `FluidCanal_*.xml` set |
| Live mod-id list | `src/RimMandrake/Utils/loadsweep/batch1.txt` line 7 |
| Prose cross-refs in other mods | `Graffiti/validation.py`, `StructureInjections/validation.py`, `Greentide/Source/RM_{JobDriver,WorkGiver}_DigOutBuried.cs`, `MovingDunes/Source/RimMandrake_MovingDunes.csproj`, `ManyWaters/Defs/TerrainDefs/RM_ColoredWater.xml`, `Utils/loadsweep/DECISION_STRINGS.md` |
| Docs | `design/RimMandrake/fluid_canals_mod_definition.md` (filename too), `pit_trap_visual_interface_spec.md`, `liquids_framework_design.md`, plus ~44 other `.md` |

🔴 **Two silent-failure hazards, both assembly-bound — this is why it is Desktop work:**

1. **`src/RimMandrake/FluidCanals/Assemblies/RimMandrakeFluidCanals.dll` is tracked in the repo** and
   exports the OLD namespace. Rename the XML class fields without rebuilding and the mod throws config
   errors on load. Rebuild in the same window.
2. **The JawaBench bridge companion resolves this mod by REFLECTION STRING**, so a rename breaks it with
   no compile error at all — it just returns "type not found".
   `bridgetools/JawaBench.BridgeTools/JawaBenchFluidCanalTools.cs` holds
   `"RimMandrake.FluidCanals.CompFluidReservoir"` and `"RimMandrake.FluidCanals.Flood_FluidCanal"`;
   `bridgetools/prove_fluid_canal.py` probes `"RimMandrake.FluidCanals.FluidCanalsDebugActions"`.
   ⚠️ Both are *already* doomed by ruling 24, which deletes `CompFluidReservoir` — so fold their rework
   into this phase rather than porting the strings twice.

⚠️ **`mandrake.rm.fluidcanals` is in the live `ModsConfig.xml`.** A packageId change desyncs the active
mod list; update it in the same window (`rimworld-start-prep`), or the mod silently drops out.

⛔ **Do NOT rewrite the old name in:** `Transient/**` (`.log` captures, `.rws.bak` savegames — they are
point-in-time evidence), `infrastructure/state/modlists/**` (ModsConfig snapshots, same reason),
`infrastructure/state/ledger/events.jsonl` (append-only), or `infrastructure/state/derived/**`
(regenerated). Rewriting history there falsifies the record.

**Deletions this phase requires** (ruling 24): `CompFluidReservoir` and `RM_FluidSpring_Test` go away —
a source is a SUPERDEEP cell at `F = D`. ⚠️ This removes the mod's only live-proven path: all three
current modcheck components assert against that comp, and the walk is written around the test spring.
Expect no live proof until Phase 9.

## Phase 2 — The depth grid

A per-map depth grid (4 levels) plus fill, persisted through `ExposeData`. The dig designator writes D;
the new **fill-in** designator lowers it. No liquid yet — the deliverable is that you can dig terraces
and *see* them. Art owed: a dry-excavation edge/shadow treatment at four depths (nothing exists; the
channel currently borrows `Terrain/Surfaces/Gravel`).

**Prior art to port, not reinvent:** `RM_MapComponent_CanyonFlood` in FloodedCanyon already owns a
phased flood on a `MapComponent` with per-cell dictionaries persisted across save/load, stale-entry
pruning, and debug arm/start surfaces. Port it.

## Phase 3 — Flow: a sort plus an overflow

Per pulse (never per tick — framework pillar 2), over the connected excavated set: sort deepest-first,
pour to `F = D`, and **a full cell overflows into neighbours with room**.

🔑 The overflow step is not optional. Without it, sources at SUPERDEEP would never feed a shallower
canal — water would not run uphill and the entire canal fantasy dies. With it, a natural source is
simply a full deep cell that spills into any channel dug at its edge.

Delivers for free: terraces filling bottom-up, a breach draining the shallower cell, spillways, and
drain-the-moat. Viscosity is `ticksPerTile` (already a real per-fluid field).

## Phase 4 — Stock and conservation

Volume accounting in fill-units; the **5:1 budget** (each source cell supplies five canal cells);
**sticky limitless** (edge contact AND a minimum size, classified once, never re-evaluated — no
hysteresis, no flicker); recession cell-by-cell from the outside in, recording original terrain so a
receding body does not launder the map; refill from rain, season and seepage, slowest for a small body;
**rain filling unroofed excavations only** (ruling 25); **fill-in displacement** (credit what has room,
destroy only the overflow — the single exception to conservation in the whole design, and it must be
*disclosed*, not silent); **sinks** at the map edge (the inverse of a limitless source, so liquid
leaving is transferred off-map, not destroyed).

## Phase 5 — Movement, capture, ladders, and the one shooting rule

`pathCost` by depth (**30 for a dry trench**, matching what Pits already uses — today's flat 6 is a
fifth of a dug pit, which is why his "unfilled pit slows movement" line is currently false).
**SUPERDEEP captures regardless of fill** (ruling 26), reusing Pits' `Building_OpenPit` despawn-into-
`innerContainer` machinery and `PitEscapeUtility`'s struggle clock — FlowWorks writes **no new capture
or escape system**. `BlocksEscape` derives from the liquid's viscosity instead of `CompPitFitting`'s
hardcoded `Water` enum. **Ladders**: a building that makes a dug cell exitable — one boolean, and
removing it strands whatever is down there, which is a jailer mechanic for free and unifies with the
prisoner pit-cell gate.

The shooting restriction (ruling 23): **SUPERDEEP only**, and "at the edge" means **8-way adjacency to
the pawn's own cell** — region adjacency needs a flood fill and the targeting check runs constantly, so
it must be O(1). ⚠️ Make a SUPERDEEP occupant an invalid ranged *target* for AI selection, not merely an
illegal shot, or raiders will try and fail and it will read as broken pathing.

## Phase 6 — Fire

Per-liquid ignition behaviour from the registry row: a **creeping fuse** (tar, propane) or a
**detonation** (astrofuel, chemfuel) — one travelling front, speed the only difference, so a player can
just outrun it. Burn is a rate on the tier ladder: **one canal tier per day, one source level per five
days** (the same 5:1 relation), so a small moat fed by a larger source burns indefinitely by design and
a limitless source burns effectively forever. Fire travels back to the source. Liquid acting on a
trapped occupant should be **very effective** (ruling 22).

⚠️ **UNMEASURED premise**: `About.xml:25-26` claims vanilla ignition already works on any flammable
terrain. That is an earlier agent's prose, never verified, and `Fire` attaches to Things and cells. If
false, ignition itself is new mechanism. Settle with Phase 0's instruments.
⚠️ **Owed as a measured proof, not a note**: a 200-cell detonation means many simultaneous blasts.
Drive them centrally from the component; do not spawn a Thing per cell.

## Phase 7 — Roster and registry

Absorb the `LiquidDef` registry and generator; bring ManyWaters' rows in **with a tinted-vanilla
fallback per row**, or slime and tar vanish for a player without Alpha Biomes (its rows tint
`AB_SlimeRamp` under `MayRequire`). **Tar first** — his ruling: *"Tar needs the viscosity most of all."*
Adopt Alpha Biomes' `AB_Tar`/`AB_TarPits` surfaces by the pattern ManyWaters already uses, and author
bespoke art only if adoption cannot carry it. Today every liquid is a colour multiply on the vanilla
water ramp, so **tar ripples like water**.

Fill tiers should reuse vanilla's own depth terrains (`WaterShallow` / `WaterMovingChestDeep` /
`WaterDeep`) whose edge-aware ramp art, wade cost and depth reading come free.

## Phase 8 — Hardware

Universal containers, flexible tubing, pumps, per-net adapters, **sluice gates** (which retire the
"leave the last cell undug" trick and give the defense spine a real trigger). Keep the §8 interface as
an internal boundary even though it is no longer cross-mod — it is what stops the hardware writing
stock bookkeeping directly.

## Phase 9 — Validation, and the pit's art

Rewrite the walk and `validation.py` against the new primitive (the old ones assert a deleted comp).
Rewrite the north star: the DRAFT checklist in `design/validation_walks/RimMandrake/FlowWorks.md` is
13 must-show + 3 cannot-show lines distilled from his own words, and it needs regrouping once depth is
the primitive. Then the pit's visual redesign inside FlowWorks (`PIT_TRAP_VISUAL_REDESIGN_1`).

🔑 **Do not let this phase be the first proof of the north-star system.** Validating Pits' *existing*
DRAFT checklist today takes it GREEN → REFUSED on the visual floor with no sprite work at all, which
IS the falsification test of `north_star_validation_spec.md` §9. One command, owner-authorised:
`modcheck validate Pits --owner-said "…"`. Recommended before any of this starts.

## verify

```
PROVE   dig a terraced run from a natural lake and watch it fill bottom-up, the source
        recede, a SUPERDEEP cell take a pawn, a ladder let one out, and a fill-in
        displace liquid back rather than deleting it
EXPECT  every phase quicktests alone on the minimal list (~90 s a map, ~22 s to load
        13 mods) — the framework's own "each slice lands + quicktests alone" rule
LIES    a flood that leaves the channel; a source that never runs down; conservation
        that leaks anywhere except a disclosed overflow; a burn timer that is really a
        rate divisor (this project has been bitten by exactly that once already)
```

## Watch out

- 🔴 **`Designator_DigCanal` may currently ALLOW digging onto a pit's cell** — it refuses edifices, but
  Pits' buildings are `passability` Standable and may not read as one. Needs an explicit refusal or an
  explicit conversion.
- 🔴 **A canyon flood erases canals today** (`CANYON_FLOOD_ERASES_CANALS_1`): permanent `SetTerrain`
  over every flood cell. One engine fixes it; two owners for one cell is the disease.
- **A roofed pit full of liquid** is a visual lie waiting to happen (ruling 25 makes roofs meaningful).
  Decide which is drawn.
- **Fire reaching an occupied pit** must know there is an occupant, or it will be found later as "fire
  does nothing to a trapped pawn".
- **Filling in a canal that contains a pit** — RULED 2026-09-16 (ruling 29, by card): the fill
  DESTROYS the pit. Code owed: `Designator_FillInCanal` still refuses edifice cells and must be
  changed to destroy a Pits building on the filled cell.
- **Every mechanic ships its own Mod Settings toggle**, defaults equal to shipped behaviour, all-off
  leaving a mod that still digs dry channels (standing rule, 2026-09-12). With this many mechanics the
  settings screen is large by design — group it by phase.
- **Ruling 7's burn numbers depend on ruling 19's tier count.** A change to the depth ladder changes
  burn duration. Do not let one slider move both silently.
