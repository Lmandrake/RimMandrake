# Messy Conduit — Phase 2 design (1b polish, aerial lines, flexible hoses, Northstar fast-track)

*Design helper for FOUNDRY, 2026-10-02. Status: DESIGN, nothing built. Builds on `messy_conduit_design_2026-10-02.md` (phase 1a as built, §8.13) and `power_poles_and_flexible_pipe_assessment_2026-10-02.md`.*

## 0. Owner brief and what was read

Owner, 2026-10-02, typed (verbatim): *"Superb! Yes, go ahead and work on those. This mod is going to get
fast-tracked through Northstar testing as a premier mod. We're going to exercise Northstar on it aggressively
since it's mostly just graphics. But I'd like the powerlines included, swaying in the wind, etc. Much of this
won't be Northstar testible, I'll tell you that up front. Movement/animation is not appropriate for Northstar,
unfortunately. But throwing up a complex series of well defined power grids and then taking a screenshot to show
the various stages of tangling, the power line connections, etc. in a combinatorially useful pattern absolutely IS
possible and valuable. So go ahead and write all that now too. No reason to wait. Fan out some sub-agents and make
this mod shine! The flexible water hoses should be much thicker and stiffer than the wires, much like the fire
hoses they use. And they SHOULD "plump up" when water is flowing through them and "collapse down" when it's not."*

**What this quote settles** (each is his word, not an inference):
- Aerial power lines are **IN this mod** (`mandrake.rm.gimmesomeslack`), not a separate mod. This answers the
  "split it out as `mandrake.rm.aeriallines`?" fork the assessment (§3.2) left open: same mod, own settings
  toggle. It also **reverses** the "Overhead spans: NOT ADVISABLE" row of the phase-1 design (§8.0, §8.3, §8.10
  phase 4): that verdict was about spans *draped over floor objects*; an aerial span drawn above everything is
  the correct occlusion for a wire that really is overhead (assessment §2A).
- The build pause (`debug_process.md` §1) is lifted **for this mod's work** by his own word: *"go ahead and work
  on those … No reason to wait."* Quote it on the item when filing.
- Motion and animation are **not Northstar bars** (his ruling). The screenshot matrix is.
- Hoses: thicker and stiffer than wires, fire-hose look, **plump when flowing, collapsed when not**.

**Read for this pass:** `messy_conduit_design_2026-10-02.md` (all; §8.13 as built),
`power_poles_and_flexible_pipe_assessment_2026-10-02.md`, the live README and the polish log
(`Transient/messy_conduit_live_20261002/README.md`, `Transient/belt_messyconduit_polish_20261002.md`), the walk
`design/validation_walks/RimMandrake/GimmeSomeSlack.md`, `debug_process.md` §0-1, `north_star_validation_spec.md`
§1-4b, `modcheck/bland_world.py`, the MessyConduit source tree (read, not edited), and the FlowWorks facts listed
in §3.1 (from a subagent read of `src/RimMandrake/FlowWorks` and the three FlowWorks design docs). Engine facts in
§2 come from a RimSage read of decompiled 1.6 (a subagent; marked VERIFIED/UNVERIFIED per line).

**Ownership boundaries this doc keeps:**
- Messy Conduit owns: floor cords (1b), aerial lines (anchors, spans, the power postfix), the cord **kit** (planner,
  layer, materials, the hose *look* and its state machine).
- FlowWorks owns (ruling 20, 2026-09-16): hose/pump/tank **behaviour** — `RM_HoseSpool`, `RM_PumpPortable`,
  `RM_ShipTank`. §3 specs the hose's visual half against FlowWorks' built API and names the FlowWorks pieces it
  waits on; it does not move them.

## 1. Phase 1b — finishing the cord net

**Verdict: MODERATE, ~4-5 agent-days** (the original +3-4 d estimate, plus the pieces phase 1a revealed).
**Risk:** low-medium; the only real unknown is the `CutoutPlant` sway shader (§1.5), which has a fallback.

### 1.1 What 1a already shipped (do NOT rebuild)

Read off `src/RimMandrake/GimmeSomeSlack/Source` at `09a832f6d` plus the polish pass in flight
(`Transient/belt_messyconduit_polish_20261002.md`):

| piece | where | state |
|---|---|---|
| tangle reduction (dense ≥ 9 cells → one node) + heap piece + power strips on top | `CordGraph.Reduce(tangleMin)`, `CordBuilder.TanglePiece` | BUILT (power-strip art is a placeholder; LEDs not keyed to live) |
| needless spurs → knot waypoints; blobs | `CordGraph` (`LoopAt`, `SpurKnots`), `CordBuilder` knot splice | BUILT |
| stub kinds wall / rock / water / device | `CordGraph` `NodeType.Stub*`, device stub = power strip decal | BUILT (water ripple art missing) |
| canned slack: excursions, loops, figure-eights, heaps, 6-round bend smoothing, centreline fallback | `CordLayer` | BUILT (no PBD settle) |
| live/dead poll every 250 ticks, flip dirties only the owner section | `RM_MapComponent_CordGraph.PollLive` | BUILT |
| live ends: periodic `MicroSparks` + `LightningGlow`, per-frame glow while paused, cap 24 | `Sparks`, `DrawLiveGlow` | BUILT (periodic, not the drip schedule) |
| dead end curled 0.7 cell; junction art posed to arms; plugs into casing; face decals at `BuildingOnTop` with explicit render queues | polish pass | IN FLIGHT (another helper; do not touch) |
| unroutable flag | `CordPlanner`, probe | BUILT |

### 1.2 The 1b task list (ordered; each a builder-sized unit)

Every task: Verse-free logic goes in `Source/Core/` with a `SelfTest/Program.cs` check that **fails first**
(debug_process §0); Verse glue in the component/layer; each new setting added to `GimmeSomeSlackMod.cs`, the
`SHIPPED` table in `validation.py` (O2) and the settings table in the design doc in the same commit.

| # | task | files | builder | days | done when |
|---|---|---|---|---|---|
| B1 | **Rope settle (PBD).** Port `rope.py`'s settle: inextensible segments (target length = laid length / n), bend smoothing, hard projection out of unwalkable cells and round trunk/post obstacles along the clearance gradient (`CordWorld.Clearance`/`ClearanceGradient` exist), pins at both ends and doorways, 70 iterations. Runs AFTER the canned splice in `CordLayer`, replacing the 6-round smoothing; keep the centreline fallback. Length budget `clamp(slack×path, 7, 16)` already in `CordLayer.Params`; assert it survives the settle (±5%). | `Core/CordLayer.cs` (new `Settle`), `SelfTest` | Opus | 1.5 | oracle parity: laid length within 5% of budget on all 7 scenes; 0 vertices unwalkable; 0 fallbacks; per-edge hash stable across two runs |
| B2 | **Long-run heaps + stub merge.** Cords > 40 cells get one extra heap within 6 cells of each end. Stubs of one buried run that surface on the same floor chain within 2 cells merge into one (§8.7.3). | `Core/CordBuilder.cs`, `Core/CordGraph.cs` | Sonnet | 0.5 | selftest scene "wall-hugging run" shows 1 stub, not a comb; 60-cell scene shows ≥ 2 heaps near ends |
| B3 | **Whipping live tail.** The last ~0.4 cell of a live floor terminal is removed from the static mesh and drawn per frame from `MapComponentUpdate`: a cached 8-point ribbon bent by `Σ sin(ωᵢ·t + φ)` + a seeded random snap every 0.6-2.0 s, keyed to `Time.realtimeSinceStartup` (works paused). Dead tails stay static (built). Cap: the existing 24 live ends. | `RM_MapComponent_CordGraph.cs` (new `DrawWhips`), `Core/CordBuilder.cs` (split tail out of the piece; `CordEnd.TailPts`) | Sonnet | 0.75 | probe `census` reports `whipDraws` = live ends on screen (≤ 24); toggling `whip` off makes it 0 and puts the tail back into the static mesh |
| B4 | **Downed-wire drip schedule** for live **wall terminals**: replace the periodic spark with a per-terminal seeded state machine — DRIP (1-4 `MicroSparks` thrown with downward velocity at 0.15 s spacing), FLASH (`ThrowLightningGlow` 0.8 + glow mesh ×2 for 4 frames), QUIET (ember: glow at 0.3), CRACKLE (3 sparks in 0.2 s); gaps exponential, mean 0.9 s, clamped 0.3-2.5 s. Real-time clock for glow, game ticks for flecks (flecks need ticks). The hanging tail on the wall face is a short lifted span (sway weight 1 at the tip, §1.5). | `RM_MapComponent_CordGraph.cs` (`DownedWire` struct per wall terminal) | Sonnet | 0.5 | probe exposes per-terminal `state` + `nextAt`; selftest of the schedule generator (Verse-free, `Core/DownedWireSchedule.cs`): seeded, gaps within bounds, all 4 states reached in 200 draws |
| B5 | **Selection highlight of the whole net.** When the selection holds a conduit (or any building with `CompPower` on a tagged net), every cord whose edge's net == that net is redrawn with a highlight material (strand texture, `ShaderDatabase.Transparent`, colour (1, 0.85, 0.35, 0.55), +0.02 width) from `MapComponentUpdate` via cached `Mesh`es built once per (net, rebuild-serial). Also highlights stubs and the far end of hidden edges with a small ring, so a buried run's two openings read as one. | `RM_MapComponent_CordGraph.cs`, `CordMaterials.cs` | Sonnet | 0.75 | probe `highlight` op: select a conduit (`jawa/select`), read `highlightCords` == cords on that net and 0 for a second net |
| B6 | **Tangle LEDs keyed to live** + power-strip real art: the strip decal picks `PowerStrip_Lit` / `PowerStrip_Dark` from the field's live flag (the live flag is already in the edge cache key, so a flip re-prints only the owner section). | `Core/CordBuilder.cs` (decal kind split), `CordMaterials.cs` | Sonnet | 0.25 | census counts lit vs dark strips; battery setPct 0 → all dark after one poll |
| B7 | **Sway — lifted spans only** (§1.5): lamp climbs, wall-terminal hanging tails, trunk wraps if phase 3 lands. Strand material for lifted pieces built with `ShaderDatabase.CutoutPlant` so `WindManager` registers it; vertex alpha = sway weight (0 at pins, rising to the free end or span middle), UV z = per-cord phase; **0 under a roof**. Floor cords never sway (optional "floor ripple" setting, default OFF). | `SectionLayer_RM_MessyCords.cs` (a second sub-mesh per lifted piece), `CordMaterials.cs`, `Core/CordBuilder.cs` (`LaidPiece.Lifted` + per-vertex weight) | Opus | 1 (+1 CPU fallback) | probe `sway`: material shader name == CutoutPlant, registered in `WindManager.plantMaterials` (reflection read), lifted vertex alpha max > 0, roofed lifted vertex alpha == 0 |
| B8 | **LOD.** A second decimated sub-mesh (1 strand, every 3rd point, no decals); switch on `Find.CameraDriver.CurrentZoom >= CameraZoomRange.Far` by setting `LayerSubMesh.disabled`. | `SectionLayer_RM_MessyCords.cs` | Sonnet | 0.5 | probe reports which set is enabled at two zoom levels |
| B9 | **Gravship cutscene guard** (risk 14): hide the layer while `WorldComponent_GravshipController.CutsceneInProgress`. | `SectionLayer_RM_MessyCords.Visible` | Sonnet | 0.1 | read the member name in RimSage first; UNVERIFIED until then |
| B10 | **Settings completion**: tangle size threshold (6-20, default 9; feeds `Reduce(tangleMin)`), whip on/off, downed-wire bursts on/off, sparks only with power overlay, max sparking ends (8-48, default 24), sway on/off, floor ripple (default off), LOD on/off. | `GimmeSomeSlackMod.cs`, `validation.py` SHIPPED | Sonnet | 0.25 | O2 green |
| B11 | **Art for 1b** (§1.4). | artpipe | — | queue | artpipe_state find first |

**Order and parallelism:** B1 alone touches `CordLayer.cs` (do it first, Opus). B2 and B6 share `CordBuilder.cs`
(one Sonnet, sequential). B3+B4+B5 share `RM_MapComponent_CordGraph.cs` (one Sonnet, sequential). B7+B8+B9 share
the section layer (one Opus). B10 last (touches settings + `validation.py`). B11 can be queued day 0.

### 1.3 Settings added by 1b

| setting | default | applies |
|---|---|---|
| Tangle threshold (cells) | 9 | live (rebuild) |
| Whipping live ends | on | live |
| Downed-wire bursts at wall ends | on | live |
| Sparks only while the power overlay is open | off | live |
| Max sparking ends per map | 24 | live |
| Sway lifted cords in the wind | on (also obeys vanilla's own "plant sway" preference) | live |
| Floor cords ripple outdoors | off | live |
| Far-zoom simplification (LOD) | on | live |

### 1.4 Art list for 1b

Check `python3 src/RimMandrake/Utils/artpipe/artpipe_state.py find powerstrip ripple scorch fray` first; the
polish log says `EndFrayed_Live`, `SparkGlow`, `PowerStrip` are still placeholders.

| texture | size | brief |
|---|---|---|
| `PowerStrip_Lit` / `PowerStrip_Dark` | 128×64 | dark grey scrap power strip, 4 sockets, amber LED lit / unlit; matte, top-lit, no white |
| `EndFrayed_Live` | 64×64 | bright copper splayed wire ends, scorched insulation lip, orange-hot tips |
| `SparkGlow` | 64×64 | soft radial white-yellow glow, additive-friendly, alpha falloff |
| `StubWater` | 128×128 | ring ripple where a black cable enters still water, faint, transparent centre |
| `HoleScorched` | 128×128 | ragged hole in a wall face with soot fan, for wall terminals |
| `Strand_Jawa_Highlight` | reuse `Strand_Jawa` | tinted at runtime; no new art |

### 1.5 Sway, decided

The phase-1 design (§8.4) relies on `CutoutPlant` swaying any mesh by vertex alpha. The RimSage read for this
pass is in §2.7; summary of the decision: **use `CutoutPlant` for lifted pieces first** (cost: a material flag and
per-vertex alpha); if the first live look shows wrong-axis or no motion, fall back to **CPU deformation of lifted
spans only** from `MapComponentUpdate` (≤ 200 spans × ~40 verts; rebuild one dynamic `Mesh` per map per frame, or
per 2 frames). The aerial lines (§2) use the same choice, so one probe and one setting cover both.

### 1.6 Northstar angle for 1b

State-readable (probe ops, all new): `whipDraws`, downed-wire `state` histogram over 600 ticks (all 4 states seen),
`highlightCords` per net, lit/dark strip counts after a battery flip, sway material + registration + vertex-alpha
extremes, LOD set per zoom, settle residual (max segment stretch < 2%). Visual: the tangling stages and slack
levels in the screenshot matrix (§4). **Not testable:** whip look, drip rhythm, sway motion (§4.7 gives proxies).

## 2. Aerial power lines

**Verdict: MODERATE.** Power across distance is EASY (one adjacency hook, VERIFIED below) but has a real
net-rebuild gap the assessment did not see (§2.2). Drawing and sway are EASY. Cut/fall is MODERATE. The one-way
theft tap is MODERATE and optional.
**Effort: A1 3.5 d · A2 2.5 d · A3 1.5 d (optional) · sway shared with 1b B7.**
**Risk:** medium on the power hook (it changes real power behaviour, so the mod stops being purely cosmetic for
anyone who builds an anchor); low on the rest.

Same mod, own master toggle **"Aerial power lines"**. Turning it off removes the anchors from the architect menu
and hides spans; it never deletes a placed anchor (anchors are real buildings and are saved). Namespace
`RimMandrake.GimmeSomeSlack.Aerial`; defs `RM_Aerial*`.

### 2.1 Engine facts (RimSage, decompiled 1.6, this pass)

| fact | status |
|---|---|
| `GenAdj.CellsAdjacentCardinal(Thing t)` just forwards to `CellsAdjacentCardinal(t.Position, t.Rotation, t.def.size)`; both `public static IEnumerable<IntVec3>` | VERIFIED |
| Power-code callers of the **Thing** overload: `PowerNetMaker.ContiguousPowerBuildings(Building root)` (private static flood fill: for each cell in `CellsAdjacentCardinal(b)`, every `Building { TransmitsPowerNow: true }` in `GetThingList` joins) and `PowerNetManager.UpdatePowerNetsAndConnections_First` first pass (RegisterTransmitter → `TryDestroyNetAt` on each adjacent cell) | VERIFIED |
| The second pass (`TryCreateNetAt` at the position and each adjacent cell) uses the **(IntVec3, Rot4, IntVec2)** overload, which cannot carry a Thing, so a Thing-overload postfix does not reach it | VERIFIED |
| `PowerConnectionMaker` (hookups, `ConnectMaxDist` 6) does not use adjacency at all | VERIFIED |
| Force a rebuild for one building: `map.powerNetManager.Notfiy_TransmitterTransmitsPowerNowChanged(CompPower)` (typo is vanilla's) enqueues deregister + register; only acts if `parent.Spawned`. `TryDestroyNetAt`/`TryCreateNetAt` are private | VERIFIED |
| Non-power callers of the Thing overload | NOT enumerated (it is a general `GenAdj` helper) |
| No vanilla 1.6 catenary. Every in-game line (`Pawn_RopeTracker` at `PawnRope`, `Building_MechCharger` wire at `BuildingOnTop`, mechanitor links) is `GenDraw.DrawLineBetween`: a straight `plane10` quad. Curves exist only as `GenMath.BezierCubicEvaluate` | VERIFIED |
| Wind: `map.windManager.WindSpeed` float, base 0.04-2.0 × weather factor; **no wind direction** in 1.6. `plantSwayHead += min(WindSpeed, 1)` per tick when `Prefs.PlantWindSway`, written per material as `_SwayHead` to materials registered via `WindManager.Notify_PlantMaterialCreated` | VERIFIED |
| Plant sway weight = vertex colour **alpha** (bottom verts 0, top verts `255 × topWindExposure`, default 0.25); `uv.z` = `HashOffset % 1024` (phase); top verts lifted by `topVerticesAltitudeBias` 0.1 | VERIFIED (C# side) |
| How the plant **shader** turns alpha + `_SwayHead` + uv.z into displacement (which axis) | UNVERIFIED — shader source not indexed |
| Spark flecks: `FleckMaker.ThrowMicroSparks(Vector3, Map)` (`FleckDefOf.MicroSparks`, velocity angle 35-45°, speed 1.2); `FleckDefOf.MicroSparksFast`; XML-only fleck defs `ElectricalSpark`, `SparkFlash`, `YellowSparkFlash`, `Fleck_RadialSparks` (`DefDatabase<FleckDef>.GetNamed`) | VERIFIED |

**AltitudeLayer order** (VERIFIED; y = index × 0.36585, `AltInc` 0.03659): … 15 Building · 16 BuildingBelowTop ·
17 BuildingOnTop · 18 Item · 19 ItemImportant · 20 LayingPawn · 21 PawnRope · 22 Projectile · **23 Pawn** ·
24 PawnUnused · **25 PawnState** · **26 Blueprint** · 27 MoteOverheadLow · 28 MoteOverhead · **29 Gas** ·
30 Skyfaller · **31 Weather** · 32 LightingOverlay · 33 VisEffects · **34 FogOfWar** · 35 Darkness · 36
WorldClipper · 37 Silhouettes · 38 MapDataOverlay · 39 MetaOverlays. The roof-overlay altitude is UNVERIFIED and
does not matter: RimWorld draws no roof over the map.

### 2.2 Power across distance — the hook, corrected

The assessment's technique (postfix on `GenAdj.CellsAdjacentCardinal(Thing)`, append linked anchors' cells) is
right for **joining** but has a **despawn gap** found this pass:
- When anchor B is despawned, vanilla destroys the net at B's position and re-creates nets only at B's
  **natural** ring (second pass, the non-Thing overload). A, far away, held the same `PowerNet` object, which is
  now destroyed, and nothing re-seeds A. A's side sits **net-less** until something else touches it.
- Same for **unlinking** two live anchors and for a span cut (§2.6): nothing re-derives either side.

**Design:**
1. **Postfix** `GenAdj.CellsAdjacentCardinal(Thing)`: if `t` has `CompAerialAnchor` and the scope flag is set,
   append each linked partner's `Position` (partners on the same map, spawned, span state `Up`).
2. **Scope flag** (`[ThreadStatic] static int depth`): incremented by a Prefix and decremented by a **Finalizer**
   on `PowerNetManager.UpdatePowerNetsAndConnections_First` and on `PowerNetMaker.NewPowerNetStartingFrom`. Outside
   that scope the postfix returns the vanilla list untouched, so no unrelated caller ever sees a remote
   "neighbour". (Cheaper than a transpiler on the private flood fill, and immune to its IL changing.) Builder:
   confirm in RimSage that every net build on load and on spawn goes through one of those two methods.
3. **Re-seed on every topology change:** link, unlink, span cut/restored, anchor despawn → for the anchor AND every
   (former) partner still spawned: `Notfiy_TransmitterTransmitsPowerNowChanged(partner.PowerComp)`. For despawn
   this runs from `CompAerialAnchor.PostDeSpawn` with the partner list captured before links are cleared.
4. **Watchdog:** every 250 ticks the `RM_MapComponent_Aerial` checks each `Up` span: both ends'
   `PowerComp.PowerNet` are the same non-null net, else re-seed both and bump `netRepairs` (probe-visible). A
   non-zero `netRepairs` in a clean test is a defect signal, not a success.
5. **Refuse merges with foreign grids:** a link target must be a `CompAerialAnchor` building of the player
   faction. (Adjacency to someone else's conduit still merges, exactly as vanilla conduit does; that is vanilla
   behaviour and not ours to change.)

### 2.3 Buildings (defs)

| def | size | role | key fields |
|---|---|---|---|
| `RM_AerialMast` | 1×1 | the standard pole: bent scrap pipe, crossarm, 2 bottle insulators | `CompPowerTransmitter` (`transmitsPower`), `CompAerialAnchor` (maxLinks 4), `passability PassThroughOnly`, `PlaceWorker_NotUnderRoof`, `RM_PlaceWorker_AerialRange`, 25 steel, 200 HP, 600 work, minifiable, research Electricity, `altitudeLayer Building` |
| `RM_AerialLampMast` | 1×1 | mast + scrap lamp head | as mast, maxLinks 3, + `CompPowerTrader` (−60 W) + `CompGlower` (radius 9) + `CompFlickable` |
| `RM_AerialWallBracket` | 1×1 | span starts at a wall: a bracket bolted to a wall | maxLinks 2. **Placement model UNVERIFIED:** builder first checks RimSage for 1.6's wall-attachment mechanism (search `PlaceWorker_*Wall*`, `isAttachment`, vanilla wall lamp). Fallback: a 1×1 building that must be cardinally adjacent to a wall, rotation facing away from it, drawn overlapping the wall face |
| `RM_PowerTapClamp` (A3) | 1×1 | the one-way theft tap (§2.7) | not a transmitter; `CompPowerPlant` with dynamic output |

The **floor net sees anchors as machines** (`CordWorldAdapter`: `MachineKind.Transmitter`), so floor cords from
nearby conduit run to the mast base and the cord climbs the mast (lamp-climb tape, a lifted piece that sways).

### 2.4 UX: build, link, dismantle

- **Auto-link on build** (setting, default on): a completed anchor links to the nearest player anchor in range
  that has a free slot and a clear line (no anchor-to-anchor line through a roofed cell's **anchor**; spans may
  pass over roofed cells). This is what makes poles "just work" like conduit.
- Gizmos: **Link** (targeter, highlights valid anchors in range), **Unlink** (dropdown of partners),
  **Unlink all**, and on a multi-selection **Auto-link selected** (Kruskal minimum spanning tree over the selection,
  edges ≤ range, respecting maxLinks).
- **Range ring while placing** (`RM_PlaceWorker_AerialRange.DrawGhost`: `GenDraw.DrawRadiusRing(range)` plus a
  dashed preview span to every anchor that auto-link would choose).
- **Range** (setting, 8-40, default **20**, a playtest guess) and **sag** (setting, default 0.06 × length).
- **Cost of a link:** free in v1 (the cost is in the anchor). A cable-item cost is a later balance pass.
- **Roof built over an anchor later:** its spans are cut (state `Cut`, §2.6) with a message, as Epicguru does.
- **Dismantle/minify an anchor:** its spans are removed (not dropped: a deliberate dismantle coils the cable).
  Destruction is different (§2.6).
- **Save:** `CompAerialAnchor.PostExposeData`: `Scribe_Collections.Look(ref partners, "rmAerialLinks",
  LookMode.Reference)` and a parallel `List<SpanState>` (`Up`/`Cut`/`Fallen`, hp, seed). A span is **owned** by
  the end with the lower `thingIDNumber` (drawing, HP, state); the other end keeps only the reference. Load fixup
  drops references that resolved to null.
- **Mod removal:** a save with placed anchors loads with vanilla's missing-def errors and loses them. The removal
  check (M9) therefore runs on a save **without** anchors (cords only), and the M9 text in the walk is narrowed to
  say so; a second row M9b records the expected behaviour with anchors (errors name only our defs, game loads).

### 2.5 Drawing: altitude, curve, layers, sway

**Altitude decision** (from the verified order): spans at `AltitudeLayer.PawnState.AltitudeFor(+5)` — **above
pawns (23) and the pawn state icons (25), below blueprints (26), motes (27-28), gas/smoke (29), skyfallers (30),
weather (31) and fog (34).** So rain, snow and smoke fall in front of the wires, drop pods fall past them, fog
hides spans over unexplored ground, and a span never covers a player's blueprint. The mast's **top** (crossarm +
insulators) is a second graphic printed at the same altitude − 1 inc so the wire sits on its insulators and
pawns walk behind the mast head; the mast's lower shaft stays at `Building`.

**Curve:** top-down RimWorld fakes height as +z on screen. Attachment points are the insulator positions at
base + (±0.18, 0, +1.15) (from the art; per-def offsets in a `DefModExtension`). A span is
`P(t) = lerp(A, B, t) + (0, 0, −sag·4t(1−t))` with `sag = sagFactor × |AB|` (screen-down droop, which reads as a
hanging wire from any direction), sampled every 0.5 cell. 1-3 strands per span (seeded), each with its own sag
×(0.9-1.15) and a 0.04-cell lateral offset at the insulator; 10% of spans carry a **hanging charm** decal (rag,
old boot, a droid part) near the low point; each strand gets a short **drip loop** below the insulator.
**Ground shadow:** a 0.12-wide soft strip along the straight base-to-base projection, at `AltitudeLayer.Shadows`,
alpha 0.25 — this is what makes a span read as *overhead*, not as a cord on the ground.

**Layers:** a static `SectionLayer_RM_AerialSpans` (owner = section of the owning anchor; `GetBoundaryRect` covers
the whole span, as the cord layer already does) prints body + shadow. Rebuilt on the existing `RM_MessyCords`
mesh flag when a span changes. Zero CPU per frame.

**Sway — recommendation:**
1. **Shader path (cheapest, zero CPU):** span material built from `ShaderDatabase.CutoutPlant` and registered with
   `WindManager.Notify_PlantMaterialCreated`; vertex alpha = `255 × amp × sin(πt)` (0 at both insulators),
   `uv.z` = span seed % 1024. **Risk:** the shader's displacement axis is unverified. If it moves vertices along
   world x only, an east-west span sways *along itself* (invisible) and a north-south span sways sideways (right).
   The first live look (two frames, sway on) decides.
2. **CPU fallback (default if the shader fails the look):** `RM_MapComponent_Aerial.MapComponentUpdate` builds one
   dynamic `Mesh` per frame for spans whose rect overlaps `Find.CameraDriver.CurrentViewRect`: offset each sample
   **perpendicular to the span in the ground plane** by
   `amp × WindSpeed × sin(πt) × sin(ω·time + φ)` (ω 1.1-1.6 rad/s seeded, `amp` 0.12 cell × setting), plus a
   second harmonic at 2.3ω × 0.3 for a living look. Swaying spans are then left out of the static layer. Budget:
   200 visible spans × 3 strands × 40 points ≈ 24k verts per frame, well under 1 ms. Respect
   `Prefs.PlantWindSway` (off → no motion), roofed span middles still sway (they are above the roof), paused game
   → the motion holds (use `Find.TickManager` time, not real time, so a paused screenshot is stable).
3. **Setting:** "Wire sway: Auto / Shader / CPU / Off" (default **Auto** = CPU until the shader is proven, then
   Shader). The 1b lifted floor pieces use the same switch.

### 2.6 Cut, fall, fire, explosions

| event | detection | result |
|---|---|---|
| **Anchor destroyed** (not dismantled) | `CompAerialAnchor.PostDestroy(mode == Kill/KillFinalize)` | each span owned by or linked to it becomes **Fallen**: the surviving anchor keeps one end; the cable lies on the floor as a **floor cord** laid by the cord planner from the surviving anchor's base toward the dead anchor's cell, length = span length × 1.05, stopping at the first unwalkable cell (the rest "is over the wall" and is not drawn). Its free end is a **terminal**: live → the 1b whip + sparks; dead → limp. Both anchors re-seed nets (§2.2.3) |
| **Explosion** | postfix on `GenExplosion.DoExplosion` (signature UNVERIFIED — builder reads it in RimSage first) → for each `Up` span whose ground projection passes within `radius` of the centre: hp −= damage × falloff | at hp ≤ 0 the span is **Cut** at the closest point: each half hangs from its anchor as a **downed wire** (a short lifted piece swinging below the insulator, length = half span × 0.4, then a floor cord to the ground) with the 1b drip/flash schedule on the live side. Lightning strikes go through the same explosion path (UNVERIFIED) |
| **Fire** | anchors are flammable buildings: vanilla burns them → the anchor-destroyed row | no separate span fire model in v1 |
| **Roof over an anchor** | `RM_MapComponent_Aerial` 250-tick sweep: `roofGrid.Roofed(anchor.Position)` | spans **Cut** (both ends coil at the anchor, no sparks), message |
| **Re-string** | gizmo "Re-string cut span" on either anchor → a pawn job (300 ticks at the anchor) | state back to `Up`, nets re-seeded |
| **Shock** (optional, later) | a pawn stepping on a live fallen cord | not in v1 (gameplay; Tier C territory) |

### 2.7 The one-way theft tap (A3, optional)

Linking to a foreign grid **merges** nets both ways (vanilla's flood ignores faction), which is why §2.2.5
refuses it. A tap that steals without merging:
- `RM_PowerTapClamp` must be placed cardinally adjacent to a **non-player** transmitter (`PlaceWorker` checks
  `TransmittedPowerNetAt` of a neighbour cell holds a net whose transmitters' faction ≠ player). It is **not** a
  transmitter, so it never enters any flood fill.
- It carries `CompPowerPlant`; it hooks to **our** grid like any generator (within 6 cells of our conduit or an
  anchor), so a span from a ship-side mast brings the stolen power home.
- Every `CompTick` (or rare tick): `stolen = min(setting rate (default 500 W), victim net's spare)`, where spare =
  `CurrentEnergyGainRate` surplus plus battery `StoredEnergy`; debit the victim's batteries (`CompPowerBattery`
  draw member — name UNVERIFIED, builder confirms) and set our `PowerOutput = stolen`.
- Look: a heavy scrap crocodile clamp on their conduit with our cord running off it; their lamps brown-out is
  vanilla's own reaction to the drain.
- **Consequences** (goodwill, guards hunting the tap) are **not designed here**: they belong with FlowWorks' theft
  consequences and need the owner's ruling (assessment §2B, risk 5).

### 2.8 Art list (aerial)

`artpipe_state.py find` this pass: no hose, pole, mast, insulator or coupling art exists (the "hose" hits are the
substring in "those"); existing MessyConduit jobs are the Jawa/Cybertek/Extension-cord floor families.

| id | canvas | facings | brief |
|---|---|---|---|
| `RM_MessyConduit_Jawa_AerialMast` | 128×256 | none (1 graphic) | a scrap power mast seen top-down-oblique: a bent dark steel pipe with welded patches, a crooked crossarm of angle iron at the top, guy-wire stub, tape and hose clamps; base plate bolted to the ground; matte black and rust |
| `RM_MessyConduit_Jawa_AerialMastTop` | 128×128 | none | the crossarm and 2-3 insulators alone (drawn above pawns): green-brown glass bottle insulators and a ceramic cup, wire lashings |
| `RM_MessyConduit_Jawa_AerialLampMast` | 128×256 | none | the mast with a salvaged lamp head (dented reflector, amber glass) on a bent arm |
| `RM_MessyConduit_Jawa_WallBracket` | 128×128 | east, north, south | a riveted angle-iron bracket bolted to a wall face with one bottle insulator |
| `RM_MessyConduit_Jawa_SpanStrand` | reuse `Strand_Jawa` | — | no new art; the span uses the floor strand |
| `RM_MessyConduit_Jawa_SpanShadow` | reuse `StrandShadow` | — | no new art |
| `RM_MessyConduit_Jawa_SpanCharm` | 64×64 | none | three hanging charms in one sheet row: a rag knot, an old boot, a droid finger joint, each hanging from a short wire |
| `RM_MessyConduit_Jawa_TapClamp` (A3) | 64×64 | none | a heavy rusted crocodile clamp with copper jaws biting a conduit, our black cord taped to its handle |

Style notes for all rows: the existing Jawa `style_notes` string (above) verbatim, `rimflow_item_id`
`MESSY_CONDUIT_AERIAL_LINES_1` (file it).

### 2.9 Settings (aerial)

| setting | default |
|---|---|
| Aerial power lines (master) | on |
| Max span length | 20 cells |
| Sag | 0.06 × length |
| Auto-link new anchors | on |
| Strands per span | 1-3 |
| Hanging charms | on |
| Wire sway | Auto (CPU until the shader is proven) |
| Sway strength | 1.0 |
| Spans cut by explosions | on |
| Allow power taps on foreign grids (A3) | on |
| Tap rate | 500 W |

### 2.10 Ordered build steps

**A1 — power + draw (3.5 d; Opus for 1-3, Sonnet for 4-7):**
1. RimSage reads first (30 min, write findings into the walk's anti-guessing notes): every net-build entry point
   goes through `UpdatePowerNetsAndConnections_First` or `NewPowerNetStartingFrom`; the wall-attachment
   mechanism; `GenExplosion.DoExplosion` signature; `CompPowerBattery` draw member.
2. `Aerial/AerialPowerPatch.cs`: the postfix + scope prefix/finalizer pair (§2.2.1-2). Selftest-able part: none
   (Verse); prove live.
3. `Aerial/CompAerialAnchor.cs` + `RM_MapComponent_Aerial.cs`: links, save/load, re-seed on every change,
   watchdog, roof sweep.
4. `Defs/Aerial/RM_AerialAnchors.xml`: 3 defs; place worker; research.
5. Gizmos + auto-link + MST auto-link selected.
6. `Core/SpanGeometry.cs` (Verse-free: sag curve, strands, drip loops, charms, shadow) + SelfTest checks
   (endpoints at insulators, lowest point at t≈0.5, sag ∝ length, deterministic by seed).
7. `SectionLayer_RM_AerialSpans.cs` + materials; CPU sway path in the component; settings.
8. Probe ops: `aerial` (anchors, spans by state, per-span net ids, `netRepairs`, sway mode, swayDraws).

**A2 — cut/fall (2.5 d; Sonnet):** 9. anchor-death → Fallen span as floor cord (the cord kit lays it; add a
`CordWorldAdapter` input for "extra cord from a point"); 10. explosion postfix + span HP; Cut halves as downed
wires; 11. re-string job; 12. probe rows.

**A3 — tap (1.5 d; Sonnet, optional):** 13. clamp def + place worker + `CompPowerTap`; 14. probe: victim
stored energy falls, our net gains, nets stay separate.

### 2.11 Northstar angle (aerial)

State reads (each a `must be true` line): two anchors N ≤ range apart and linked share one `PowerNet`; a linked
pair beyond range is refused; destroy one → the survivor's side still has a net within 2 ticks (the despawn-gap
regression), `netRepairs == 0`; unlink → two nets; a link to a non-player transmitter is refused; save/load keeps
links; explosion on a span → state `Cut`, two downed-wire ends, live side sparking-registered; tap → nets stay
distinct, victim energy falls. Visual: matrix axis "aerial" (§4). Not testable: sway motion (proxy §4.7).

## 3. Flexible hoses

**Verdict: the LOOK is MODERATE (~3 d) and buildable now in this mod; the PLUMBING is FlowWorks' and is not
built.** No pump, hose or ship-tank class exists in `src/` (§3.1). So this section specs the hose **look** as a
cord-kit feature with a neutral, assembly-free API, proven with a dev-only test hose, and names exactly what
FlowWorks owes before a real hose can drive it.
**Risk:** low for the look; the flow signal (§3.3) is the dependency.

### 3.1 FlowWorks facts this depends on (read 2026-10-02)

| fact | source |
|---|---|
| `RM_LiquidBody` (natural body): `id`, `limitless`, `stock`, `capacity`, `cells`; **no fluid and no rate on a body** — the fluid is one per map (`RM_MapComponent_Excavation.ActiveFluid`, default `RM_Fluid_Water`) | `FlowWorks/Source/RM_LiquidBody.cs` |
| `RM_LiquidStock` (held by the excavation component as `Stock`): `BodyAt`, `CanSupply`, `TryDebit(map, c, units, owner)` (no debit on false), `TryCredit` | `RM_LiquidStock.cs` |
| Pulse: `RM_MapComponent_Excavation.MapComponentTick` → `DoPulse()` every `PulseIntervalTicks` (default **250**, floor 60) | `RimMandrakeFlowWorksMod.cs` |
| **No pump class.** The only sinks are map-edge excavated cells; `SinkTransferredTotal` is cumulative; **per-pulse flow is not observable** (locals discarded in `ResolveComponent`) | excavation component |
| `Building_LiquidTank` / `RM_LiquidTank` (2×2): `storedLiquid` (`LiquidDef`), `storedUnits`, `CanAccept`, `CanProvide`, `TryAddLiquid`, `TryRemoveLiquid`; bottle/barrel jobs only, no hose interop | built |
| `RM_HoseSpool`, `RM_PumpPortable`, `RM_ShipTank` | **design only** (`liquids_framework_design.md` §4; ruling 20: FlowWorks owns them; order tank → pump → hose → tanker loop) |
| `LiquidDef.color` exists ("tint for generated art, flecks and bottle fill") but **no row sets it**: every liquid reads white today | `RM_LiquidDefRegistry.xml` |
| MessyConduit has no reference to FlowWorks (About: Harmony only) | `About.xml`, csproj |

### 3.2 The kit API (no compile-time dependency either way)

`RimMandrake.GimmeSomeSlack.Kit.HoseKit` (public static, Verse types only):

```
int  HoseKit.Register(Map map, IntVec3 endA, Rot4 faceA, IntVec3 endB, Rot4 faceB, float maxLength, string styleId)
void HoseKit.SetFlow(Map map, int hoseId, bool flowingThisPulse, Color? fluidTint)
void HoseKit.SetLaidFraction(Map map, int hoseId, float f)   // deploy/reel animation, 0..1
void HoseKit.Cut(Map map, int hoseId, float atFraction)      // spill look, both halves limp
void HoseKit.Unregister(Map map, int hoseId)
```

FlowWorks calls it through delegates resolved once with
`AccessTools.Method("RimMandrake.GimmeSomeSlack.Kit.HoseKit:SetFlow")` etc.; a null lookup (Messy Conduit absent)
falls back to FlowWorks' own plain line. MessyConduit never references FlowWorks. The kit saves nothing: the
hose owner (FlowWorks' `RM_HoseSpool`, which saves its own endpoints) re-registers on `SpawnSetup`/load, and the
look is deterministic from (endpoints, seed), so it comes back identical.

### 3.3 The flow signal FlowWorks must provide (owed by FlowWorks, not built)

`flowingThisPulse` = all of: hose connected at both ends **and** the pump powered and switched on **and** the
pump's last pulse moved > 0 units (its `TryDebit`/`TryRemoveLiquid` returned true and the downstream
`TryAddLiquid`/`TryCredit` accepted > 0). The pump records `lastMovedUnits` and `lastMovedTick` and calls
`SetFlow` once per pulse. This is a two-field addition to the future `RM_PumpPortable`; file it on that item.

### 3.4 The visual state machine

States: **Flat** → **Filling** → **Plump** → **Draining** → **Flat**. Driven by game ticks (a paused game holds
the pose, so screenshots are stable).

| from | to | condition |
|---|---|---|
| Flat | Filling | `SetFlow(true)` once |
| Filling | Plump | 90 ticks elapsed (≈1.5 s at 1×) |
| Plump | Draining | `SetFlow(false)` for **2 consecutive pulses** (≥ 500 ticks), and ≥ 600 ticks in Plump |
| Draining | Flat | 150 ticks elapsed |
| Draining | Filling | `SetFlow(true)` (re-pressurise from wherever it is) |
| any | Flat (instant) | `Cut`, unregister-and-reregister, load |

The 2-pulse release plus the 600-tick minimum dwell is the **hysteresis**: a pump that stalls for one pulse (a
short `TryDebit`) does not make the hose flicker.

**Per-state geometry** (fire-hose physics: a flattened hose is *wider* than a round one, width_flat ≈ π/2 ×
diameter):

| | Flat (collapsed) | Plump (charged) |
|---|---|---|
| ribbon width | **0.34 cell** | **0.22 cell** (still ~2× a wire's 0.10) |
| texture | `Hose_Flat`: flat woven canvas, two crease lines along the edges, matte, low value | `Hose_Plump`: round ribbed jacket, top-lit cylinder highlight, slight sheen |
| path | the laid slack path (relaxed S-curves) | blended 35% toward the planned centreline: straighter and ~5% shorter, ends pinned |
| shadow | thin (it lies flat) | wider, offset (it stands proud of the floor) |
| couplings | lie flat, rotated with the hose | same |

**Transitions:** width, texture blend (two sub-meshes cross-faded by alpha) and path blend interpolate over the
transition time; **Filling** adds a travelling bulge from the pump end to the far end
(`offset = 0.06 × sin(k·s − ω·t) × e^(−t/40 ticks)`, perpendicular to the hose) — the "brief wobble". Drawn per
frame only while in Filling/Draining (a handful of hoses at most); Flat and Plump are static and printed into
the section layer like cords (zero CPU).

**Per-fluid tint (optional, setting default ON but subtle):** the jacket keeps its own colour; the fluid shows
as (a) a wet darkening of the jacket by 15% when Plump, and (b) drip/wet decals at couplings tinted by the fluid.
Tint source: `LiquidDef.color` when FlowWorks authors it; until then a MessyConduit table keyed by defName
string — water `#3E5C6B`, salt water `#46606A`, tar `#1A1410`, chemfuel `#7A5A1E`, propane `#8C8C70`, brine
`#5E6A60`, slimes red/green/white-as-pale-grey/yellow muted — passed as `fluidTint`.

### 3.5 Stiffness in the planner — a separate cord kind

Same planner (A*, string-pull, corner rounding, settle), new `CordKind.Hose` parameter set in `CordLayer.Params`:

| parameter | wire (cord) | hose |
|---|---|---|
| min bend radius | ~0.15 cell | **1.2 cells** (corner rounding radius and a bend constraint in the B1 settle with stiffness 0.8) |
| slack budget | `clamp(1.4-2.4 × path, 7, 16)` extra | **`clamp(0.15-0.30 × path, 1, 6)` extra** |
| loops / figure-eights / heaps | yes | **none** |
| slack shape | loops, bunches, piles against walls | **big gentle S-curves** (lateral excursion amplitude 0.6-1.2 cells, wavelength 6-10 cells) plus one **flake** near the pump end: spare length laid as 2-3 tight back-and-forth folds, the way crews flake a fire hose |
| sample spacing | ~0.1 cell | 0.25 cell |
| crossing liquid cells | never (stub) | **allowed** (hoses float): canal/water cells walkable for hoses at extra cost 3; walls, rock and impassable buildings still blocked |
| doorways | pinned | pinned, and a hose through a doorway keeps the door from closing — **look only**; whether it really blocks the door is FlowWorks/gameplay, not decided here |
| couplings | — | at both ends and every **8 cells** of laid length (a hose is lengths joined by couplings; setting 6-12) |
| length cap | — | `maxLength` from the spool: if the planned path exceeds it, the hose is drawn taut-straight along the path to the cap and the far end lies short (a visible "too short" state; the job should refuse earlier) |

### 3.6 Hookups

| end | look | where |
|---|---|---|
| `RM_PumpPortable` outlet (not built) | brass `Coupling` decal on the pump's outlet face; the pump def gets a `RM_HookupPoint` `DefModExtension` (offset per rotation) that the kit reads | FlowWorks def |
| `RM_LiquidTank` 2×2 (built) | `TankHookup` brass manifold decal on the footprint edge facing the hose's other end, chosen by the kit from the footprint | kit, no FlowWorks change |
| `RM_ShipTank` (not built) | same as tank | FlowWorks def |
| loose intake end in a body | `Nozzle`/strainer decal lying in the liquid cell | kit |
| packed | `HoseSpool` item sprite (coiled flat hose on a reel) | FlowWorks item def, art from here |

### 3.7 Deploy / reel jobs (FlowWorks owns; the look hooks)

FlowWorks' "Deploy hose" job (pawn carries the spool along the planned path; work ∝ length) calls
`SetLaidFraction(f)` as the pawn advances: the hose is drawn only up to `f` of its length, **unrolling** behind
the pawn, Flat. "Reel in" runs it backwards. Cheap and reads well. The kit plans the path at `Register` so the job
can walk the same polyline (`HoseKit.PathCells(map, id)` read-only accessor).

### 3.8 Theft-use sketch (kept within FlowWorks' ruled design)

Tanker raid (ruled design, `liquids_framework_design.md` §4): land → carry `RM_PumpPortable` (found or stolen) to a
body or a foreign `RM_LiquidTank` → deploy hose to `RM_ShipTank` → pump pulses N units per interval → the hose
**plumps** the moment the first pulse moves liquid and **collapses** two pulses after the pump stops or the
source runs dry (stock is the limit, ruling 4) → reel in → fly. An aerial span (§2) powers the pump from the
ship. A cut hose (explosion/melee, FlowWorks HP) calls `Cut`: both halves go Flat at once with a fluid-tinted
spill decal at the cut — the liquid twin of the sparking downed wire. Consequences for stealing are FlowWorks'
and the owner's (not designed here).

### 3.9 Art list (hoses) and artpipe job briefs

Style notes (all rows): the Jawa `style_notes` string verbatim, **except** one change the owner's "like the fire
hoses they use" calls for: *"fire-hose look: flat-woven canvas jacket, brass couplings (dull, tarnished, the one
warm metal allowed)"*. `rimflow_item_id`: `MESSY_CONDUIT_FIRE_HOSE_LOOK_1` (file it). Priority 70.

| id | canvas | prompt (ready to queue) |
|---|---|---|
| `RM_MessyConduit_Jawa_Hose_Flat` | 256×64 | Seamless horizontal tiling strip of a collapsed, empty fire hose lying flat, seen from directly above: a flat woven canvas jacket the full height of the strip minus a thin transparent margin, two darker crease lines running along both edges where the hose is folded flat, visible coarse weave texture, faded dark ochre-red canvas with grime and oil stains, slightly wrinkled; it must tile left-to-right with no visible seam. |
| `RM_MessyConduit_Jawa_Hose_Plump` | 256×64 | Seamless horizontal tiling strip of a charged, round fire hose full of water, seen from directly above: a round ribbed jacket about 65% of the strip height centred vertically, top-lit cylinder shading with a soft highlight line along its length, faint ring ribs every few pixels, same faded dark ochre-red canvas with grime as the flat hose, slightly wet sheen; tiles left-to-right with no visible seam. |
| `RM_MessyConduit_Jawa_Hose_Coupling` | 64×64 | Top-down view of a dull tarnished brass fire-hose coupling joining two hose ends left and right: two short ribbed brass collars with lugs, centred, hose ends leaving the left and right canvas edges at the vertical centre. |
| `RM_MessyConduit_Jawa_Hose_Nozzle` | 64×64 | Top-down view of a dented tarnished brass hose nozzle / strainer end: a tapered brass pipe with a perforated strainer cap pointing right, the hose entering from the left edge at the vertical centre. |
| `RM_MessyConduit_Jawa_Hose_TankHookup` | 64×64 | Top-down view of a scrap brass manifold flange bolted to a tank wall: a square bolted plate with a short brass spigot and coupling pointing right, the plate along the left edge. |
| `RM_MessyConduit_Jawa_Hose_Spill` | 128×128 | Top-down soft irregular wet splash stain on the ground, greyscale mid-grey with darker centre and soft transparent edges, to be tinted at runtime by the liquid colour. |
| `RM_MessyConduit_Jawa_Hose_Drip` | 64×64 | Small top-down wet drip stain with a few droplets, greyscale, soft edges, for tinting at runtime. |
| `RM_MessyConduit_Jawa_HoseSpool` | 128×128 | Top-down item sprite: a flat fire hose coiled tightly on a scrap steel reel with a crank handle, brass coupling visible on the outer end, faded dark ochre-red canvas. |

Validation: strips via the 4× tiling seam check (as the cord strips), real alpha, `generating-rimworld-sprites`
validator.

### 3.10 Settings (hoses)

| setting | default |
|---|---|
| Messy hose look (when FlowWorks hoses exist) | on |
| Hoses plump when flowing | on |
| Fill wobble | on |
| Tint by contents (wet darkening + coloured drips) | on |
| Coupling spacing | 8 cells |
| Hose slack | 1.0 (scales the S-curve budget) |

### 3.11 Ordered build steps (look only; 3 d)

1. `Core/CordLayer.cs`: `CordKind.Hose` params (§3.5), S-curve + flake shapes, liquid-cell crossing in
   `CordWorld` (a `hoseWalkable` mask), SelfTest scenes: min bend radius ≥ 1.2 measured on the laid polyline, no
   loops (no self-intersection), extra length within budget. (Opus, 1 d — after B1, same file.)
2. `Kit/HoseKit.cs` + `RM_MapComponent_Hoses` (runtime only, kept out of the save like the cord component):
   registry, state machine (§3.4) as a Verse-free `Core/HoseState.cs` with a SelfTest (a flow trace
   `T F T T F F F …` produces the expected state sequence; one-pulse stall never leaves Plump). (Sonnet, 0.75 d)
3. `SectionLayer_RM_Hoses` (static Flat/Plump) + per-frame transition drawing, couplings every N cells,
   hookup decals, laid-fraction clipping. (Sonnet, 0.75 d)
4. **Dev test hose** `RM_DebugHose` (DevMode-only placeable, two ends, a gizmo "flow on/off" that calls `SetFlow`
   every 250 ticks) so the look is provable and screenshot-able with no FlowWorks pump. Probe op `hoses`: id,
   state, width, path length, coupling count, laid fraction. (Sonnet, 0.5 d)
5. FlowWorks side (filed, not here): pump `lastMovedUnits/lastMovedTick`, calls into the kit, `LiquidDef.color`
   values.

### 3.12 Northstar angle (hoses)

State reads: a test hose registered between two cells → laid polyline min bend radius ≥ 1.2, no loops, couplings
= ⌊length/8⌋+2; flow trace on → state Plump after 90 ticks and width 0.22; one missed pulse → still Plump;
two missed pulses → Flat after 150 ticks; cut → Flat at once, spill decal present. Visual: matrix axis "hose
state" (Flat / Plump / mid-Filling frozen) (§4). Not testable: the wobble motion.

## 4. Northstar fast-track — the screenshot matrix

**Verdict: EASY-MODERATE, ~3 d** (generator 0.5, runner 1.5, sheet + image sanity 0.5, walk + must-show seed 0.5).
**Matrix size: 109 scenes** (64 floor + 16 density + 18 aerial + 9 hose + 2 controls), every factor pair covered
(verified by brute force this pass), **one cold load, < 2,500 game ticks, ~15-20 min wall time.**

### 4.1 Principles

- **Each scene has two oracles, both state reads:** (a) an **intrinsic** expectation written by the generator
  from what it built (it laid a T, so 1 junction and 3 terminals; it cut a gap in a live line, so 1 live + 1 dead
  end, 0 cords across) — independent of our code; (b) a **parity** expectation from running the same scene spec
  through the Verse-free `Core/` offline (the SelfTest path), which catches adapter defects (map → `CordWorld`)
  that (a) is too coarse to see. A scene PASSes only if live == both.
- **Screenshots are evidence for the owner's eyes, never a pixel assertion** (spec §4: the judge and the owner
  read them; GREEN needs his eyes once). Cheap automated **image sanity** only catches broken captures (§4.6).
- **Golden screenshots** = frames the owner accepted on the contact sheet (keep / flag, `review-sheets`
  decisions file). Later runs put golden and new side by side for his eyes; nothing auto-compares pixels.
- **Motion is not a bar** (owner). Motion features get state proxies (§4.7).
- **Stills are staged deterministically:** bland world (`modcheck/bland_world.py`), each scene on its own cleared
  soil plot, unfogged, unroofed (except where the scene needs a roof), paused, clock 12:00 (`jawa/time_clock`),
  weather Clear (`jawa/weather_set`), sway **Off** for stills, fixed zoom per scene class
  (`rimworld/set_camera_zoom`), `rimworld/screenshot_cell_rect` on the scene's rect + 1-cell pad, UI cleared
  (`jawa/clear_ui`, `jawa/screenshot_mode` — check its schema).

### 4.2 Factors and the generator rule

**A. Floor scenes — 64 = 16 topologies × 4 tangle stages, other factors assigned by formula.**

| factor | levels |
|---|---|
| **T** topology (16) | 0 line · 1 T · 2 4-way · 3 ring · 4 lattice/mesh (5×5 grid) · 5 star (hub + 6 spokes) · 6 needless spur + 2×2 blob on a run · 7 gap, live side · 8 gap, both dead · 9 two nets crossing in one room · 10 device-attached (battery, generator, 3 consumers, one machine hooked 5 cells away, lamp) · 11 doorway pass-through · 12 wall entry/exit + a wall terminal · 13 rock entry/exit (granite block) · 14 under an impassable building (device stub) · 15 deep-water crossing (stands in for a canal; a FlowWorks canal board is optional, §4.5) |
| **S** tangle stage (4) | 0 tidy (slack 0 = path-tight, 1 cord per edge, tangles off) · 1 ropey (shipped defaults) · 2 rat's nest (slack max, 3 cords per edge) · 3 lattice tangle (defaults, tangle threshold 6) |
| **F** style family (4) | 0 Star Wars: Jawa · 1 Star Wars · 2 Extension cord · 3 Cybertek (a family without real art yet renders placeholders; the row still runs and is labelled "art pending") |
| **P** power (2) | 0 live (battery 100%) · 1 dead (battery 0%) |
| **V** view (3) | 0 normal · 1 power overlay on · 2 net selected (1b highlight) |
| **Z** zoom (2) | 0 close (root 11) · 1 far (LOD on) |

Rows: for `t in 0..15, s in 0..3`: `F = (t+s) % 4`, `P = (s + t//4) % 2`, `V = (t + s + t//4) % 3`,
`Z = (s//2 + t) % 2`. **All 15 factor pairs fully covered with 64 rows** (the lower bound, since T×S alone needs
64) — checked by enumerating every pair this pass, 0 missing. The generator re-runs that check and refuses to
emit on a gap.

**B. Density ladder — 16 = {1, 10, 100, 1000 conduit cells} × 4 stages**, full cross, Jawa, live, normal view.
Fields are a seeded mix (60% lattice, 40% runs) inside a square plot (1, 4×4, 12×12, 34×34 cells); the 1000 rows
use far zoom. This is the "stages of tangling" board the owner described, and the perf canary (§4.4).

**C. Aerial — 18 rows**: factors **P** power (2) · **N** poles in the chain (2 / 3 / 5) · **R** span length
(6 / 12 / 19 cells) · **St** state (all up / one span cut by an explosion / one anchor destroyed → fallen span) ·
**G** ground under spans (open / over a walled room / over deep water). Rule for `i in 0..17`: `P = i // 9`,
`N = (i % 9) // 3`, `R = i % 3`, `St = (N + R + P) % 3`, `G = (N + 2R) % 3`. All pairs covered (verified). The
"over-range link refused" case is a state row (§2.11), not a scene, because a refused link has nothing to show.

**D. Hose — 9 rows** (L9 orthogonal array, all pairs covered, verified): **St** Flat / Plump / Filling frozen at
50% · **Ro** route open-straight / around a wall corner / across a water strip · **Le** 6 / 14 / 24 cells ·
**Fl** water / tar / chemfuel tint. `St = x`, `Ro = y`, `Le = (x+y) % 3`, `Fl = (x + 2y) % 3` for `x, y in 0..2`.
Uses the dev test hose (§3.11.4); no FlowWorks needed.

**E. Controls — 2:** an empty plot (expects 0 cords; proves the "wires present" sanity check can fail) and the
line scene with the master switch OFF (expects vanilla conduit art, 0 cords).

### 4.3 Scene spec JSON (generator output, runner input)

`src/RimMandrake/GimmeSomeSlack/matrix/scenes.json`, emitted by `gen_matrix.py` (offline, deterministic, committed
with its own hash so a run can name the spec it ran):

```json
{
  "spec_version": 1, "generator": "gen_matrix.py", "spec_hash": "…",
  "board_pitch": [40, 30],
  "scenes": [
    {
      "id": "F07_T1_S3",                         "group": "floor",
      "factors": {"T": "tee", "S": "lattice_tangle", "F": "StarWarsJawa", "P": "live", "V": "selected", "Z": "close"},
      "plot": [0, 0, 18, 14],                     "zoom_root": 11,
      "settings": {"slack": "1f", "cordsPerConnection": "3", "tangles": "true", "tangleMin": "6", "style": "CordStyle.StarWarsJawa"},
      "build": [
        {"op": "terrain", "def": "Soil", "rect": [0, 0, 18, 14]},
        {"op": "build", "def": "Battery", "cells": [[2, 7]], "rot": 0},
        {"op": "build", "def": "PowerConduit", "cells": [[4,7],[5,7],[6,7],[7,7],[8,7],[8,8],[8,9],[9,7],[10,7]]},
        {"op": "build", "def": "Wall", "stuff": "Steel", "cells": []},
        {"op": "destroy", "cells": []},
        {"op": "battery", "at": [2, 7], "pct": 1.0}
      ],
      "view": {"overlay": "none", "select_at": [6, 7]},
      "expect": {
        "intrinsic": {"junctions": 1, "terminals": 3, "terminals_live": 3, "stubs": 0, "tangles": 0,
                      "cord_edges": 4, "cords_min": 4, "cords_max": 12, "nets": 1, "cross_net_edges": 0,
                      "unwalkable_vertices": 0, "highlight_cords_eq_net_cords": true},
        "parity": "core"                          
      },
      "shows": ["cords_loopy_slack", "junction_reads_as_join"]
    }
  ]
}
```

- Coordinates are **plot-relative**; the runner adds the board origin. `"parity": "core"` tells the runner to
  compute the parity census offline from the same `build` list (a `CordWorld` built from the ops) before the run.
- Aerial scenes add `{"op": "anchor", "def": "RM_AerialMast", "cells": [...]}`, `{"op": "link", "pairs": [...]}`,
  `{"op": "explode", "at": [x, z], "radius": 2.9}` (`jawa/explosion_at`) or `{"op": "kill", "at": [x, z]}`; expect
  `{"spans_up": n, "spans_cut": n, "spans_fallen": n, "nets": n, "net_repairs": 0}`.
- Hose scenes add `{"op": "debug_hose", "a": [...], "b": [...], "maxLength": 30, "fluid": "RM_Liquid_FreshWater",
  "force_state": "Plump"}`; expect `{"state": "Plump", "width": 0.22, "min_bend_radius_ge": 1.2, "couplings": n,
  "self_intersections": 0}`.
- `force_state` / probe staging ops exist **only** to freeze a frame for a still. The behaviour itself (that
  flow really plumps the hose, that an explosion really cuts) is proven by separate must-be-true rows that use
  real ticks (§4.8). A still never stands in for a behaviour.

### 4.4 Runner

`validation.py --matrix [--groups floor,density,aerial,hose,controls] [--only ID…]` (the same functional script;
`debug_process.md` §0 wants one script per mod), with helpers in `src/RimMandrake/GimmeSomeSlack/matrix/`:
`gen_matrix.py` (offline), `stage.py` (bridge ops per scene), `sheet.py` (contact sheet + image sanity).

1. **Preflight (offline, 0 ticks):** spec hash, pairwise coverage re-check, parity census for every scene via the
   Core SelfTest binary (`--matrix-oracle scenes.json` mode added to `SelfTest/Program.cs`, writes
   `matrix_parity.json`).
2. **World:** one cold load on the `messyconduit` tier (Core + 5 DLC + Harmony + bridge + the mod; FlowWorks NOT
   needed), `bland_world.setup` once.
3. **Boards:** scenes are packed onto boards of plots at `board_pitch` (40×30) with gutters; the 34×34 density
   plots get their own board. A board is built in one batch per op type (`jawa/build_batch`, `destroy_batch`,
   `set_terrain_batch`, `set_fog`, `set_roof_batch`), then `step_game_ticks 2` (nets are built on the next tick —
   LEARNED in run 1), then the probe `poll` + `rebuild`.
4. **Per scene:** apply its `settings` through the probe (`set:` op; settings are global, so scenes on a board
   are **grouped by settings tuple** — the generator orders boards so each board has one tuple; 64 floor rows
   have 16 distinct (S, F) tuples → 16 small floor boards), frame the plot, census restricted to the plot rect
   (new probe op `census:x,z,w,h`), compare with both oracles, set the view (overlay / select), zoom, screenshot.
5. **Behaviour rows** (real ticks, §4.8) run after the stills on dedicated plots.
6. **Write** `northstar/matrix_<ts>/results.json` (per scene: factors, expected, actual, PASS/FAIL per field,
   image path, image-sanity verdicts) and the PNGs; `modcheck record` as today.

**Tick budget:**

| block | boards | ticks each | ticks |
|---|---|---|---|
| floor stills | 16 | 2 (nets) + 0 (probe ops are frame-serviced) | 32 |
| density stills | 2 | 2 | 4 |
| aerial stills | 3 | 2, + 30 after explosions/kills to let nets re-seed and flecks settle | 96 |
| hose stills | 1 | 2 (states forced) | 2 |
| controls | 1 | 2 | 2 |
| behaviour rows (§4.8) | — | hose trace 1,200 · live/dead poll 250 · aerial despawn/explosion 2 × 60 · sway two-frame 2 × 30 · sparks counter 300 | ~2,130 |
| **total** | **23 boards** | | **≈ 2,270 ticks** |

Wall time is dominated by bridge calls: ~109 framed screenshots (~3 s each) + 23 board builds (~30-60 s) ≈ 15-20
min after the cold load. **Perf canary:** the probe reports rebuild ms per board; the 1000-cell density boards log
`rebuildMs` and `laidPoints` into the results (first real C# perf number for the mod; not a pass bar until the
owner sets one).

**Determinism:** all cord geometry is seeded by endpoints (no `Rand`), so the same spec on any fresh bland map
gives the same per-edge hashes — the runner records `geometryHash` per scene and diffs it against the previous
run's results (a changed hash with unchanged code is a defect; with changed code it is listed for the owner's
eyes). Sparks/glow use real time and are excluded from stills by `breakReadout` glow being drawn but sparks not
flying while paused (LEARNED: paused shots never show flecks).

### 4.5 Contact sheet

`sheet.py` writes `Transient/messy_conduit_matrix_<date>/sheet.html` (+ a PNG per group) per the
`review-sheets` skill: one tile per scene, labelled with its id and plain-language factors ("T junction · rat's
nest · Jawa · live · net selected · close"), a green/red badge for the state oracle, an amber badge for any
image-sanity warning, and **keep / flag / note** controls saving a `.decisions.json`. Grouped so stages read left
to right (tidy → ropey → rat's nest → tangle) for the same topology — the owner's "various stages of tangling" in
one row. Kept tiles become the golden set; a later run's sheet shows golden | now side by side.
Optional board (not in the 109): the same 16 floor topologies over FlowWorks canals on the `flowworks` tier, once
the canal passability question (§8.12 of the phase-1 doc) is answered.

### 4.6 Cheap automated image sanity (tripwires, not bars)

Per screenshot, with PIL + numpy, in `sheet.py`:
1. **Non-blank:** luminance std-dev > 6 and not > 98% one colour.
2. **Wires where the state says:** the runner knows the camera rect, so it projects every laid cord vertex
   (from the census) to pixels and builds a 3-px-wide mask; mean luminance inside the mask must be ≥ 12% darker
   than the plot's floor outside it (Jawa cords are matte black on soil). For hoses: inside-mask saturation/hue
   band check instead. Proven able to fail by the **empty control** (no mask → must report "no wires") and by a
   planted check that runs it against the master-off control (mask from the ON census, OFF image → must fail).
3. **No missing texture:** fraction of magenta pixels (R > 200, G < 60, B > 200) < 0.05%.
4. **Histogram band:** mean luminance and the 5th/95th percentiles within ±25% of that scene's golden stats (no
   band until the owner keeps a golden; first run only records).
5. **Frame correctness:** image size equals `plot × px_per_cell` within 2%, so a zoom or framing slip is caught.
A failure marks the tile amber and the scene's `image_sanity` field; it never flips a state verdict.

### 4.7 What is NOT Northstar-testable, and the proxies

Owner: *"Movement/animation is not appropriate for Northstar."* So these get **state proxies** and, at most, a
two-frame smoke test; the real judgement is a live look **with the owner present** when he wants one.

| feature | why not testable | proxy (state read) | smoke test |
|---|---|---|---|
| wire sway (aerial spans, lifted cords) | motion | sway mode setting read; CPU path: `swayDraws > 0` with wind forced ≥ 1 (`jawa/weather_set` windy weather), `0` with sway Off or `Prefs.PlantWindSway` off; shader path: material shader == CutoutPlant, material present in `WindManager.plantMaterials` (reflection), lifted vertex alpha max > 0, roofed = 0; amplitude parameter read | 2 frames 30 ticks apart, unpaused, sway ON: mean abs pixel diff inside the span mask > 2 levels; sway OFF: < 0.5 (`t.capture_frames`, spec §4b) |
| whipping live ends | motion | `whipDraws` == visible live ends (≤ cap), 0 with whip off | same two-frame diff on the tail mask |
| sparks / drip / flash timing | timing, particles | our own counters: `sparksThrown`, downed-wire state histogram over 300 ticks (all 4 states seen at ≥ 1 live wall terminal; 0 at dead ones) | none |
| hose fill wobble / plump transition | motion | state timeline from the probe: Flat → Filling at the first flow pulse, Plump at +90 ticks, hysteresis holds through one missed pulse, Flat 150 ticks after the second | still of the frozen 50% Filling frame (scene D) |
| LED flicker, glow pulse | motion | lit/dark strip counts; `glowDraws` | none |

### 4.8 Behaviour rows (must be true, real ticks) added to the walk

Beside M1-M9: **M10** tangle threshold setting changes the census (6 vs 9 on the same field); **M11** whip/drip
counters as §4.7; **M12** selection highlight equals the selected net's cords and nothing else; **M13** two linked
anchors share one `PowerNet`, unlink → two, link beyond range refused, link to a non-player transmitter refused;
**M14** destroy one anchor → the survivor's side has a net within 2 ticks and `netRepairs == 0` (the despawn-gap
regression, §2.2), a fallen floor cord with a terminal exists; **M15** explosion on a span → `Cut`, two downed
ends; **M16** save/load keeps links and span states; **M17** hose flow trace → state timeline as §3.4; **M18** hose
min bend radius ≥ 1.2, no self-intersections, coupling count; **M19** (A3) tap: victim energy falls, nets distinct;
**M20** the matrix ran: every scene's state oracle PASS (the screenshots ride along as evidence).

### 4.9 North star seed (DRAFT, for the owner to validate)

Add a `## north star` section to `design/validation_walks/RimMandrake/GimmeSomeSlack.md` with `state: DRAFT` and
empty `validated-hash:`. `### the experience` holds only his typed words (the nodal ruling's "everything is a
too-long extension cord", the edge-case paragraph, and today's quote). Seeded `### must show` (distilled, no new
claims; each claimed by matrix scenes via `shows=`):
- `cords_loopy_slack` — cords lie in loose loops and heaps, never taut, at the default stage
- `tangle_stages_distinct` — tidy, ropey, rat's nest and lattice tangle are distinguishable side by side
- `junction_reads_as_join` — cords visibly meet at junction pieces
- `break_live_vs_dead` — a live broken end and a dead one are distinguishable at a glance
- `cord_enters_wall_or_rock` — a cord visibly goes into a wall or rock face where conduit is buried
- `aerial_span_reads_overhead` — a span reads as hanging in the air between poles, not lying on the ground
- `aerial_fallen_span_on_ground` — after a pole dies its wire lies on the ground with a broken end
- `hose_thicker_than_wire` — a hose is clearly thicker than a power cord
- `hose_flat_vs_plump` — an empty hose lies flat and wide; a flowing one is round and fuller
`### cannot show`: `cord_across_gap` (a cord bridging a break), `cord_on_wall_top`, `missing_texture`.
Motion lines are **deliberately absent** (his ruling). Only he validates (`modcheck/cli.py validate
MessyConduit --owner-said "…"`).

## 5. Work plan, lanes, owner decisions

**Gate:** every lane starts **after the polish helper's MessyConduit commit lands** (it is editing
`CordBuilder`, `CordLayer`, `CordMaterials`, the section layer, the component, the probe and the SelfTest right
now). Starting earlier means two writers in one file in one clone (worktrees are off).

**Items to file** (none exist yet): `MESSY_CONDUIT_PHASE_1B_1`, `MESSY_CONDUIT_AERIAL_LINES_1`,
`MESSY_CONDUIT_FIRE_HOSE_LOOK_1`, `MESSY_CONDUIT_NORTHSTAR_MATRIX_1` (all quoting the owner's 2026-10-02 go-ahead as
the build-pause exception), and for FlowWorks a note on the pump item: the two-field flow signal of §3.3 and the
kit call.

### 5.1 Lanes (disjoint files, so they can run side by side in one clone)

| lane | model | owns these files | work | agent-days |
|---|---|---|---|---|
| **L1 rope** | Opus | `Core/CordLayer.cs` | B1 PBD settle → hose cord kind and S-curve/flake shapes (§3.11.1) | 2.5 |
| **L2 graph** | Sonnet | `Core/CordGraph.cs`, `Core/CordBuilder.cs`, `CordWorldAdapter.cs` | B2 long-run heaps + stub merge, B6 lit/dark strips, then the A2 "fallen span as a floor cord" adapter input | 1.5 |
| **L3 live ends** | Sonnet | `RM_MapComponent_CordGraph.cs`, new `Core/DownedWireSchedule.cs` | B3 whip, B4 drip schedule, B5 selection highlight | 2 |
| **L4 render** | Opus | `SectionLayer_RM_MessyCords.cs`, `CordMaterials.cs` | B7 sway (shader path + CPU fallback shared with spans), B8 LOD, B9 cutscene guard | 2 |
| **L5 aerial** | Opus (A1 1-3), Sonnet (rest) | new `Aerial/*`, `Core/SpanGeometry.cs`, `Defs/Aerial/*` | A1 (3.5) → A2 (2.5; step 9 waits for L2) → A3 if ruled (1.5) | 6-7.5 |
| **L6 hose look** | Sonnet | new `Kit/HoseKit.cs`, `Core/HoseState.cs`, `RM_MapComponent_Hoses.cs`, `SectionLayer_RM_Hoses.cs`, debug hose def | §3.11 steps 2-4 (step 1 is L1's) | 2 |
| **L7 harness** | Sonnet | `GimmeSomeSlackProbe.cs`, `GimmeSomeSlackMod.cs` (all settings), `validation.py`, new `matrix/*`, the walk file, `SelfTest/Program.cs` matrix-oracle mode, **the csproj** | matrix generator, runner, sheet, image sanity; every probe op the other lanes need (they expose public counters; L7 wires the ops); B10 settings; M10-M20 rows; north-star DRAFT seed | 3 |
| **L8 art** | — | artpipe queue | 1b (6) + aerial (6 ids; the wall bracket has 3 facings) + hose (8) = 20 ids, filed day 0 after `artpipe_state.py find` | queue |

Shared-file rules: only L7 edits the probe, the settings class, `validation.py` and the csproj (others hand it
their new file names and counter names); SelfTest checks for Core changes are added by the lane that changes Core,
in its own clearly separated block, and L7's matrix-oracle mode goes in last.

### 5.2 Calendar (agent-days; live runs are load rounds on the `messyconduit` tier, batched)

| day | L1 | L2 | L3 | L4 | L5 | L6 | L7 |
|---|---|---|---|---|---|---|---|
| 0 | — | — | — | — | RimSage reads (§2.10.1) | — | art queue; `gen_matrix.py` + coverage check |
| 1 | B1 settle | B2 | B3 | B7 shader path | A1 hook + anchor comp | HoseState + kit API | runner on today's features (floor + density + controls) |
| 2 | B1 parity | B6 | B4 | B7 CPU fallback | A1 defs, gizmos, auto-link | debug hose | probe ops, B10 settings |
| 3 | hose kind | A2 adapter input | B5 | B8, B9 | A1 span geometry + layer | hose layer (needs L1 day 3) | sheet + image sanity |
| 4 | — | — | — | — | **live round 1**: matrix floor/density/controls + M1-M12 + A1 rows (M13, M16) | | |
| 5 | | | | | A2 cut/fall | hose look finish | aerial + hose scene groups |
| 6 | | | | | A3 (if ruled) | | M14-M19 |
| 7 | — | — | — | — | **live round 2**: full 109-scene matrix + M1-M20, contact sheet to the owner | | |

**Totals:** ~18-20 agent-days of work; **~7 calendar days** with these lanes, 2 cold loads. Critical path:
L1 → L6 (the hose kind) and L5 (aerial A1 → A2).

### 5.3 Decisions for the owner (defaults marked; everything else here is decided)

1. **Fallen live wire:** when a pole dies and its wire lands sparking on the ground, is that **look only**
   (**default**), or should it also shock pawns who step on it?
2. **Wires over roofed rooms:** poles must stand outside; may a wire stretch over a roofed room between them
   (**default: yes**, like a power line over a house), or must the whole span be over open sky?
3. **Power-theft clamp:** build the clamp that quietly drains another faction's power now, in this mod, or
   **wait and build it with the tanker-raid theft work** in FlowWorks, where the consequences live (**default:
   wait**)?
4. **Hose colour:** **faded dark red canvas with brass couplings, like a real fire hose (default)**, or black
   rubber to match the Jawa cables?

## 6. What could not be verified

- **The plant sway shader's displacement axis** (and its use of vertex alpha and uv.z): shader source is not in
  RimSage. The C# side (alpha weight, `_SwayHead` per registered material, uv.z phase) is VERIFIED. This is why
  aerial sway defaults to the CPU path until a live two-frame look.
- **Every net-build entry point** passing through `UpdatePowerNetsAndConnections_First` or
  `NewPowerNetStartingFrom` (the scope-flag design of §2.2 assumes it); non-power callers of
  `GenAdj.CellsAdjacentCardinal(Thing)` were not enumerated. Builder step A1.1 reads both.
- The **despawn gap** (§2.2) is reasoned from the verified second-pass code, not observed live. M14 is the test.
- **`GenExplosion.DoExplosion` signature**, lightning going through it, the **wall-attachment** placement
  mechanism in 1.6, the **`CompPowerBattery` draw** member, and `WorldComponent_GravshipController.CutsceneInProgress`
  (B9): named, not read.
- **`jawa/screenshot_mode`, `jawa/weather_set`, `jawa/explosion_at`** exist in `tool_schemas.json`; their argument
  shapes were not read.
- **The roof overlay altitude** (irrelevant: RimWorld draws no roofs over the map).
- **FlowWorks:** no pump, hose or ship tank exists, per-pulse flow is not observable today, and `LiquidDef.color`
  is unset on every row (subagent read of `src/RimMandrake/FlowWorks`, spot-read here). Canal passability by depth
  for cords/hoses is still open (phase-1 doc §8.12).
- **Every number** in this doc that is not marked VERIFIED is a design guess: 20-cell range, sag 0.06, hose widths
  0.34/0.22, bend radius 1.2, coupling every 8 cells, transition ticks, day estimates, wall times, image-sanity
  thresholds. The pairwise coverage counts (64 / 18 / 9, 0 missing pairs) **were** checked by enumeration.
- **No C# performance number** for 1000-cell density exists yet; the density board is designed to produce the
  first one.
- Nothing here was run in game or against the bridge (by brief), and no `src/` file was edited.
