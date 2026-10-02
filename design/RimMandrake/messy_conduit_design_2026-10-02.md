# Messy Conduit — design pass (2026-10-02)

Owner idea, 2026-10-02: *"I normally hate how they make conduit invisible, but now that I think about it,
Jawa should celebrate that. I almost want to make it weirder like snakey, ropey loose conduit on the floor.
Spawn out a design pass to consider how hard it would be to make MESSY CONDUIT, an alternative mod that would
make conduit sprawl all over the floor in loose wirey mess like it does in real life."*

Status: DESIGN ONLY. Nothing built. Filed as `MESSY_CONDUIT_MOD_1` (ledger event, `3bb58a7e5`). The current
recommendation is the overlay model in §8.
Engine facts below are from RimSage (decompiled 1.6) unless marked otherwise.

## 0. Retired-mod fact

- **Invisible Conduit Continued** (workshop `3506645273`, packageId `GlitchGoblin.InvisibleConduitCont`)
  was retired from the canonical list at `ff56ec8fa`, which touched only
  `infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml`.
- **No `src/` mod depends on it**: no `About.xml` `modDependencies`/`loadAfter`, no patch, no def names it.
  The only two hits under `src/` are `src/Jawa/ideoligion/MandrakeJawa.xtp` and
  `src/Jawa/ideoligion/The Salvation.rid`. Those are ideoligion exports, and RimWorld writes the mod list
  active at save time into their header. That is metadata and gates nothing. Leave both files alone.
- Removing it changes gameplay as well as looks. Its patch also set `PowerConduit` Beauty -2 → 0 and
  Flammability 0.7 → 0 (§2), so those values now go back to vanilla.

## 1. How 1.6 conduit renders (engine facts)

**The defs.**
- `PowerConduit`: `thingClass Building`, `drawerType MapMeshOnly`, `altitudeLayer Conduits`.
  `graphicData` is `texPath Things/Building/Linked/PowerConduit_Atlas`, `graphicClass Graphic_Single`,
  `linkType Transmitter`, `linkFlags [PowerConduit]`, `damageData rect (0,0.35,1,0.3)`. It sets
  `building.isPowerConduit`, comp `CompPowerTransmitter`, `Beauty -2`, `Flammability 0.7`, 80 HP, 1 steel,
  `canLandGravshipOn true`, and the blueprint atlas `PowerConduit_Blueprint_Atlas`.
- `WaterproofConduit` (`ParentName="PowerConduit"`) changes only `texPath` to `WaterproofConduit_Atlas`,
  plus its terrain affordance and a 10-steel cost.
- `HiddenConduit` (`ParentName="PowerConduit"`) keeps the parent's texture and sets `color (0,0,0,0)` with
  `shaderType Transparent`. Vanilla 1.6 already ships an invisible conduit as a deliberate 2-steel option.
  `CompPower.PostPrintOnto` also skips the small connecting wire for exactly `ThingDefOf.HiddenConduit`.

**The graphic build** (`GraphicData.Init`). The engine calls `GraphicDatabase.Get(graphicClass, texPath, …)`.
Then, because `Linked` (`linkType != None`) is true, it calls `GraphicUtility.WrapLinked(…, Transmitter)`,
which returns a `Graphic_LinkedTransmitter`. `WrapLinked` is a fixed `switch` over the `LinkDrawerType`
enum, so a mod cannot add its own link type without Harmony.

**The print path.** Nothing here draws per frame.
- `SectionLayer_ThingsGeneral` (`MapMeshFlag Things`) calls `Thing.Print` for each `MapMeshOnly` thing.
  That bakes the geometry into the section mesh (17×17 cells), and it is rebuilt only when that section is
  dirtied. Steady-state cost is zero.
- `Graphic_Linked.Print` prints one fixed 1×1 plane at `TrueCenter` (`new Vector2(1f,1f)`), so `drawSize`
  is ignored. Its material comes from `LinkedDrawMatFrom`: a 4-bit N/E/S/W neighbour mask indexes one of 16
  sub-materials of a 4×4 atlas (`MaterialAtlasPool`).
- Each sub-material samples its quadrant with `1/32` padding (`mainTextureScale 0.1875`). An atlas tile
  therefore has a never-sampled border, and **the art can never cross the cell edge**.
- `Graphic_LinkedTransmitter` links to a neighbour when the link grid says so OR when
  `powerNetGrid.TransmittedPowerNetAt(c) != null`. It also prints an extra stub plane into each adjacent cell
  holding a transmitter building whose own graphic is not linked (a battery, for example). That is why
  conduit visibly "plugs into" machines.
- **Odyssey (1.6):** `Graphic_Linked.ShouldLinkWith` refuses to link across a substructure/non-substructure
  boundary (`ModsConfig.OdysseyActive` and `FoundationAt(c)?.IsSubstructure`). Conduit visually breaks at the
  gravship hull edge. Any replacement must keep that rule.
- **Neighbour regeneration:** `Thing.SpawnSetup`/`DeSpawn` call `linkGrid.Notify_LinkerCreatedOrDestroyed`
  and `MapMeshDirty(Position, Things, regenAdjacentCells: true)` **only if `def.CanAffectLinker`**, which is
  `graphicData.Linked || IsDoor`. 🔴 **Setting `linkType None` breaks neighbour refresh**: an adjacent cell
  in the next section keeps a stale join. This is why the conduit keeps `linkType Transmitter` under every option (§3, §8.1).

**The small wires** (machine → nearest conduit). `CompPower.PostPrintOnto` calls
`PowerNetGraphics.PrintWirePieceConnecting(layer, A, B, forPowerOverlay:false)`. That is one straight
`Printer_Plane.PrintPlane`, width 1, stretched A→B, using material `Things/Special/Power/Wire` at
`AltitudeLayer.SmallWire`. The power-grid overlay (`SectionLayer_ThingsPowerGrid`, drawn only while
`OverlayDrawHandler.ShouldDrawPowerGrid`) calls the **same function** with `forPowerOverlay:true`, which
draws the blue connector line.

**Printer API.** `Printer_Plane.PrintPlane` just appends 4 verts and 2 tris to
`layer.GetSubMesh(mat)`. A section layer accepts any vertex list, so arbitrary procedural geometry
(ribbons, curves) is possible inside a `Print` override. Nothing in the engine limits it to quads.

## 2. How Invisible Conduit Continued does it

The installed copy at `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3506645273` takes
almost nothing.

- **XML** `1.6\Patches\zzz_Conduit_Invisible.xml` (4 operations):
  - `PatchOperationReplace` swaps `texPath` on `PowerConduit` and on `WaterproofConduit` to
    `Things/Building/Power/ConduitInvisible`. That is a 32×32 RGBA PNG with every channel 0 (MEASURED with
    PIL: extrema all `(0,0)`).
  - It also replaces `PowerConduit` `Beauty` with 0 and `Flammability` with 0. **That is a gameplay change
    hidden inside a "graphics" mod.**
- **C#** `GoAwaySmallWire.dll` (4.6 KB, same file in `1.6\Assemblies` and `Assemblies`). It was read with a
  .NET metadata reader (`dnfile`), not `strings`. It contains one Harmony patch:
  `[HarmonyPatch(typeof(RimWorld.PowerNetGraphics), "PrintWirePieceConnecting")]` with a `Prefix` whose IL
  is `ldc.i4.0; ret`. That is an **unconditional `return false`**.
  - ⚠️ **Side effect:** it ignores `forPowerOverlay`, so it also erases the **power-grid overlay connector
    lines**. With it loaded, the overlay no longer shows which machine connects to which conduit.
  - The attribute string names a 1.1 `Assembly-CSharp` build (`Version=1.1.7372…`). The "1.6" DLL is the
    old binary re-shipped, and it works only because the method signature never changed.
- **Takeaway:** retexturing conduit takes one `texPath` replace. Changing the small wires takes one Harmony
  patch on one static method. Both are tiny, and both are safely removable because they add no saved data.

## 3. Feasibility tiers

### Tier A: pure XML plus art (random atlas variants)

**Mechanism.** Patch `PowerConduit/graphicData`: `graphicClass` becomes `Graphic_Random` and `texPath`
becomes a folder holding N full 4×4 atlases. This works unmodified in 1.6. `Graphic_Linked.LinkedDrawMatFrom`
calls `subGraphic.MatSingleFor(parent)`, and `Graphic_Random.MatSingleFor` picks a variant by
`thing.OverrideGraphicIndex ?? thing.thingIDNumber % count`. `thingIDNumber` is saved, so a cell's variant
stays the same across frames, reloads and saves.

**Cost and limits.**
- The mess is **locked inside each cell**: a 1×1 plane plus padded atlas sampling.
- Every variant must obey a **port contract**: every strand bundle crosses each cell edge at the same
  points, or neighbours will not join.
- So it gives loops, kinks, slack, tape wraps and several twisted strands *within* the cell, but no sprawl
  across cells.
- Long straight runs read as a chain of random beads unless the art is careful.

**Settings.** XML alone **cannot** have Mod Settings, and every mod must ship real settings. Tier A
therefore needs a tiny C# shim.
- At `StaticConstructorOnStartup` the shim chooses the texture folder by setting: off, tidy, messy or
  feral. It rewrites `graphicData.texPath`/`graphicClass` and re-resolves.
- Changes would be "restart required", which is acceptable and common.
- Waterproof gets its own toggle and art set.

**Risk.**
- `Graphic_Random.MatSingle` is `Rand`-based, and `Graphic_Linked.MatSingle` uses it for the `None`-link
  sub-material (UI, ghosts). That could flicker. UNMEASURED: confirm in the first script.
- `HiddenConduit` inherits the patched `graphicData`, because patches run before inheritance. It stays
  hidden through its transparent colour, but the first script should check that.

**Other properties.**
- **Effort:** S (1–2 days plus art).
- **Perf:** the same as vanilla (2 tris per cell). N× more sub-materials per section is negligible.
- **Save-compat:** trivially removable. No defs, comps or saved data.

### Tier B: C# procedural printer (not chosen; see §8)

Its routing and determinism ideas carry into §8. Its install point (the conduit's own `Print`) does not.

**Mechanism.** A subclass `RM_Graphic_MessyConduit : Graphic_LinkedTransmitter` overrides `Print`. Instead of
one atlas quad it emits ribbon geometry: 2–4 strands per cell, each a cubic Bezier sampled at 8–12 points
and extruded into a textured strip.
- Endpoints sit at the linked neighbour edges, jittered.
- Control points push past the cell edge by up to 0.3–0.6 cells for sprawl.
- Occasional slack loops and S-snakes appear, plus a "coil" decal on dead-ends.
- It keeps `linkType Transmitter`, which keeps `CanAffectLinker`, neighbour regeneration, the power-net link
  test and the Odyssey substructure rule.

**How it gets installed** (choose one; both are construction-time only, with zero per-frame Harmony):
1. **Preferred:** one Harmony postfix on `GraphicUtility.WrapLinked`. When the sub-graphic's `data` belongs
   to a conduit def carrying our `DefModExtension`, it returns our subclass instead of
   `Graphic_LinkedTransmitter`. This runs once per graphic build.
2. A prefix on `Graphic_LinkedTransmitter.Print` gated on the same extension. It is simpler, but runs at
   every section regeneration (still not per frame).

`graphicClass` alone cannot do it. A custom `graphicClass` gets wrapped by `WrapLinked` anyway, unless
`linkType None`, and `None` breaks neighbour refresh (§1).

**Determinism.**
- Seed from `Gen.HashCombineInt(cell.x, cell.z, map.uniqueID)` (or `thingIDNumber`), so it is stable across
  frames and saves and stores nothing.
- Each shared edge's crossing point is seeded from the **edge**, not the cell, so both neighbours compute
  the same join.
- Mesh cost is paid at section regeneration only.

**Interactions.**
- **Small wires:** a second Harmony prefix on `PrintWirePieceConnecting` replaces the straight plane with a
  sagging curve. It runs **only when `forPowerOverlay == false`**, so the overlay is left alone and
  Invisible Conduit's bug is not repeated.
- **Altitude:** stays `Conduits`. Items, filth and pawns draw over it, which reads correctly as cables
  under clutter.
- **Overflow:** geometry spilling into an adjacent cell or section is drawn by the owning section. The only
  cost is slight culling pop at screen edges.

**Perf, measured by reasoning and owed a live number.**
- About 3 strands × 10 segments × 2 tris = 60 tris per cell, against vanilla's 2.
- A 2,000-conduit base is about 120k tris spread across sections: trivial for the GPU, static and batched
  per material.
- CPU cost is at regeneration only: a fully conduited section (289 cells) is about 17k verts per rebuild.
  Allocations should be kept off the hot path (cached `Vector3` buffers).
- Settings offer a strands/segments level of detail.

**Settings.** Master on/off; messiness 0–100% (sprawl distance, strand count, loop chance); per-def
toggles (conduit, waterproof, modded children); sagging small wires on/off; colour mode (salvage-mixed or
uniform).

**Other properties.**
- **Effort:** M (about 3–5 days of C# plus a small art set).
- **Risk:** low-medium. The surface is two well-understood static or virtual methods.
- **Save-compat:** removable. It has no comps and no saved state, only a def extension plus graphics.

### Tier C: dynamic mess and gameplay

**What it adds.**
- Heaps that coil.
- Tangles that grow with age.
- Trip hazard (path cost).
- Fire or short-circuit risk when wet or damaged.
- A "tidy the cables" job.
- Wire spools as an item.
- Hooks: vanilla `IncidentWorker_ShortCircuit` already picks a conduit (`ShortCircuitUtility`), and our
  `RSW_Mynock` (ShipVermin) already feeds on live power and could chew loose cable.

**Engine cost.**
- **Tangle state** is a saved comp or map component, so the mod is **no longer safely removable** without
  a cleanup path.
- **Jobs and hazards** need balance passes and a north-star bar each.

**Mod compatibility.** It touches pathing and incidents, so conflicts become real: power mods that replace
`CompPowerTransmitter` or the short-circuit logic.

**Other properties.**
- **Effort:** L–XL (weeks).
- **Risk:** high.
- **Multiplayer:** irrelevant to us, and A/B are visual-only anyway. Tier C's RNG would need the MP-safe
  pattern only if we ever cared.

### Compatibility across tiers

| neighbour | A | B | C |
|---|---|---|---|
| Invisible Conduit (retired) | last `texPath` patch wins | our swap wins if our def extension is present; small wires conflict (both prefix) | same as B |
| `HiddenConduit` (vanilla) | inherits our graphic and stays transparent: verify | exclude via extension (only defs we tag) | exclude |
| `WaterproofConduit` | own atlas set | own strand texture | same |
| Modded conduits with `ParentName="PowerConduit"` | inherit our art (opt-out setting) | inherit only if tagged; a settings "tag all `isPowerConduit` defs" toggle | same |
| Dubs Bad Hygiene pipes, VE pipe nets | untouched (own defs) | untouched; could opt in later via the same extension | — |
| Conduit retexture mods | load order decides | our class ignores their atlas | — |

Any cost/risk statement about a specific power mod in our list is **UNMEASURED** until a sweep of the
installed `About.xml` files and conduit-patching XML is run. The 1,410-file About sweep this pass found 7
mods mentioning "conduit" (sanity probe: 53 mention gravship), and none is a conduit renderer apart from
Invisible Conduit.

## 4. Jawa angle: art direction

- **Fiction.** Jawas do not install cable. They *accumulate* it. Every run is salvage: mismatched gauges,
  stripped ship harness, droid wiring looms, bare copper where insulation burned off, splices wrapped in rag
  and tape, bundles zip-tied with scrap. The mess is a boast: *we powered this from junk*. That is the
  owner's "celebrate it" read.
- **Palette.** Desaturated sand-and-rust base plus a few strong insulation accents (faded red, mustard, dull
  cyan) and **bright copper** at splices. That matches the salvage register of `design/Jawa/art/` and the
  70s-brown preference.
- **Style.** It follows the painterly lawset restored 2026-09-14 (`ART_PAINTERLY_RESTORATION_1`): soft
  rendered cylinders with a top-lit highlight line and a slight drop shadow onto the floor. No toy-cel
  outline. At conduit scale (64 px a cell) the read is **value, not detail**: a dark strand with a bright
  highlight line, and copper glints.
- **Franchise-free.** The mod itself stays generic "messy cable". Jawa-flavoured junk (droid harness, rag
  wraps) can be a `RUT_`/campaign art set selected through a setting or a patch from the campaign layer.
  The `RM_` art must stand alone.

## 5. Naming, packaging, settings, north star

**Naming.**
- packageId `mandrake.rm.messyconduit`, folder `src/RimMandrake/MessyConduit`, C# namespace
  `RimMandrake.MessyConduit`, prefix `RM_` (`SectionLayer_RM_MessyWires`, `RM_MessyConduitExtension`).
- It is franchise-free and is a public-use mod.
- Hard dependency: Harmony (one prefix, for hookup wires, §8.1). No DLC dependency needed, though Odyssey's substructure rule is
  honoured by reuse.

**Settings.** This is the full set for every tier ("superb Mod Settings"):

| Setting | Effect | Applies |
|---|---|---|
| Master enable | — | restart |
| Messiness slider | sprawl distance, strand count, loop/snake chance | live (dirty all sections) |
| Variant count / LOD | — | live |
| Per-def toggles | power conduit, waterproof, "all isPowerConduit defs" | — |
| Sagging machine wires | — | — |
| Sway (lifted spans) / floor ripple | §8.4 | live (dirty all sections) |
| Break sparks / whip / spark rate / only-with-power-overlay | §8.4b | live |
| Colour mode | salvage-mixed or uniform | — |
| Leave the power-overlay lines alone | fixed on; it is a guarantee, not a toggle | — |

Defaults equal the shipped behaviour, and all-off degrades to vanilla.

**First functional script** (`debug_process.md` §2): `src/RimMandrake/MessyConduit/validation.py` plus the
walk `design/validation_walks/RimMandrake/MessyConduit.md`.

`## must be true` lines, each with a cheap state read:
1. Every section of the current map holds a `SectionLayer_RM_MessyWires` (`Section.GetLayer`), and a
   conduit cell produces non-zero vertices in it. `PowerConduit` renders transparent.
2. `HiddenConduit` stays invisible: its colour alpha is 0 and it is excluded from our class.
3. The same cell yields the same mesh after a save/load: hash the section layer's vertex count and a sample
   of positions before and after.
4. Neighbour joins update across a section boundary when a conduit is placed or removed (place at x=16|17
   and read the adjacent section's dirty/regen state).
5. With the power overlay on, connector lines are still printed (the `SectionLayer_ThingsPowerGrid`
   sub-mesh for `MatConnectorLine` is non-empty). This is a guard against Invisible Conduit's bug.
6. Master toggle off → the layer's `Visible` is false and conduit renders as vanilla.
8. Break readout: destroy one conduit in a powered line, and the end registry reads 1 live end. Turn the source
   off and within 250 ticks it reads dead (§8.4b).
7. Removing the mod from a save that used it: the load is clean and `Player.log` shows no errors.

Steps 2 and 6 are `--mock`-selftestable, and the routing geometry is selftestable offline; 3–5 and 7 need the bridge. Visual judgement ("does it read as
messy") is a screenshot or a keeper savegame for the owner, never a pass bar.

`## anti-guessing notes`, seeded:
- `RULED OUT: custom graphicClass with linkType None — CanAffectLinker false ⇒ no adjacent-cell regen
  (ThingDef.CanAffectLinker, Thing.cs SpawnSetup)`.
- `RULED OUT: drawSize enlarges linked art — Graphic_Linked.Print hard-codes Vector2(1,1)`.

## 6. Recommendation and build plan

**Recommendation: the overlay model (§8).** The conduit is vanilla and invisible, and a cosmetic section
layer draws the wires: walls on top, trunk wraps, sway, and the break readout. Tier A cannot sprawl past the
cell. Tier C (hazards) stays a later, separate opt-in (`MessyConduit.Hazards`), if ever.

🔴 **This is gated by the 2026-10-01 build pause.** A new mod is new content, and the pause holds it until
every mod has a first script with a recorded run (`debug_process.md` §1, "DONE"). The phase-0 mock-ups are
design work and can go ahead now. Everything after waits for the lift, or for the owner's explicit word.

**Build order, phases, effort and the art list:** §8.7 and §8.8.

**Artpipe.**
- Run `artpipe_state.py find` first. It was run this pass: no conduit, cable or wire art exists, and the 9
  "conduit" hits are only description mentions in other jobs.
- Then queue through `fill_queue.py` with `style_notes` naming the painterly lawset, top-lit, seamless
  horizontal tiling, transparent background, and the palette in §4.
- Strips must tile. Validate offline by tiling ×4 and checking the seam columns, plus a real-alpha check
  (`generating-rimworld-sprites` validator).
- Small textures. Expected cost is one batch.

## 7. Open questions for the owner

1. **How messy is the default?** Neat-but-ropey (cables mostly follow the line, with gentle loops), or a
   real rat's nest (cables wander half a cell, pile up at junctions)? Mock-ups will show both.
2. **Should cable spill visibly over floors and under furniture**, or stay mostly within its own lane?
3. **Machine hookup wires:** keep vanilla's straight thin line, or make them sag and droop too?
4. **Looks only, or later some danger?** Trip hazard, sparks in rain, vermin chewing cable, a tidy-up job.
   This is a separate later add-on; say no and it never gets built.
5. **Waterproof conduit:** messy too, or left clean as the "proper" option?
6. **Should vanilla's own Hidden Conduit stay invisible**, so players keep a tidy choice, or should
   everything be messy?

## 8. The overlay model (owner idea of 2026-10-02)

Owner, verbatim: *"I had wondered if we could actually have little drawn wires decoratively put over
otherwise-invisible-conduits as usual. So the visible wires would only be aesthetic. In theory then the drawer
could be very smart and have them bend around corners and do other multi-cell-physics things to look even more
realistic, depending on how difficult that is. Swaying in the wind would be amazing, or looping around tree
trunks or poles. Things like that. Assess that as even realistic or possible, given that art can be anything.
We certainly wouldn't want annoying clipping issues."*

Three requirements he added the same day (relayed by the coordinator):
1. **Break detection as a readout.** Where a line is broken, the end still on a powered net sparks and whips
   about, and the dead end lies limp. The point is finding breaks at a glance.
2. **Wires in walls lie on top of the walls.** Conduit under a wall cell is drawn over the wall.
3. **Aesthetic:** deliberately ugly, "truck drivers in space", very Jawa. Jury-rigged, taped, patched,
   mismatched gauges and colours, grease.

**This model replaces Tier B as the recommendation.** The conduit def stays functionally vanilla and is made
invisible (the Invisible Conduit texture swap, plus the hookup-wire suppression). All the looks come from a
separate cosmetic drawer that reads the conduit grid and owns its own geometry. Under Tier B the conduit's own
`Print` was the drawer, which tied every wire to its own cell's graphic. The overlay can see the whole
neighbourhood (trees, walls, nets) when it decides how a wire looks. Tier B's routing math (§3) carries over
unchanged.

### 8.0 Verdicts

| # | question | verdict | one line |
|---|---|---|---|
| 1 | Overlay hook | **EASY** | A `SectionLayer` subclass is instantiated by the engine for every section automatically. It needs no Harmony and is rebuilt on existing dirty flags. |
| 2 | Routing | **MODERATE** | This is pure geometry run at section rebuild time. The only real design work is edge-seeded joins and the strand offsets. |
| 3 | Trunk and pole wraps | **MODERATE** | The two-layer wrap works if the front half's height is matched to the tree's own sloped plane. Real poles do not exist in vanilla 1.6. |
| 3b | Wires on top of walls | **MODERATE** | One altitude rule plus a drape piece at the wall's edge. Natural rock is excluded. |
| 4 | Sway | **EASY if the vanilla plant shader behaves as inferred, else HARD** | `CutoutPlant` already sways any mesh by vertex alpha, driven by the map's wind, with no per-frame CPU cost. |
| 4b | Break sparking | **EASY to MODERATE** | Find dead ends at rebuild time, poll live/dead every 250 ticks, use vanilla spark flecks, and whip only the few live ends each frame. |
| 5 | Clipping | **MODERATE, manageable** | Every failure mode has a mitigation (table in §8.5). The ones left over need eyes, not a state read. |
| — | Overhead spans between poles | **NOT ADVISABLE for phase 1-3** | Wires floating over everything cannot be occluded correctly in a top-down sprite game. |

### 8.1 Overlay model: where the drawer hooks

**Options compared** (engine facts from RimSage, decompiled 1.6):

| hook | how it draws | cost | verdict |
|---|---|---|---|
| **custom `SectionLayer` subclass** | `Section`'s constructor does `foreach (Type t in typeof(SectionLayer).AllSubclassesNonAbstract()) Activator.CreateInstance(t, this)`, so **any mod's subclass is created for every 17×17 section of every map**. `MapDrawLayer.DrawLayer` then calls `Graphics.DrawMesh` per sub-mesh. `MapDrawer.DrawMapMesh` draws a section only when `view.Overlaps(section.Bounds)` | zero per frame (static mesh); rebuild only when dirty | **chosen** |
| `MapComponent.MapComponentUpdate` + `Graphics.DrawMesh` with our own cached meshes | we reimplement sections, dirtying and culling | the same GPU cost plus our own bookkeeping | only for the few **animated** pieces (live ends that whip, §8.4b) |
| `DynamicDrawManager` / `drawerType RealtimeOnly` | per-thing `DrawAt` every frame | O(conduits) each frame | rejected, as before |
| Harmony on `Graphic_LinkedTransmitter.Print` (Tier B) | inside the conduit's own print | zero per frame | superseded: it cannot see neighbours or obstacles cleanly |
| `MapComponentOnGUI` | screen-space IMGUI | — | wrong space; never |

**Rebuild triggers** use existing flags. The layer sets `relevantChangeTypes = Things | Buildings | PowerGrid |
FogOfWar | Roofs` (`MapMeshFlagDefOf`).
- `Section.TryUpdate` ORs the section's `dirtyFlags` against that mask, and rebuilds immediately only when the
  section is in view. An off-screen section stays dirty and is rebuilt when it next draws.
- **Conduit placed or removed:** the conduit still satisfies `def.CanAffectLinker` (it keeps
  `linkType Transmitter`), so `Thing.SpawnSetup` and `DeSpawn` call
  `MapMeshDirty(Position, Things, regenAdjacentCells: true)`.
- **Net change:** `PowerNetManager.NotifyDrawersForWireUpdate` dirties `Things` (adjacent cells) and
  `PowerGrid` (adjacent cells and adjacent sections).
- **Buildings:** `Building.SpawnSetup` dirties `Buildings` on every occupied cell, which covers walls, lamps and
  furniture.
- **Trees:** spawn, despawn and growth-stage changes dirty `Things` (`Plant.cs` lines 617, 662, 797 and 829).
- **Fog and roofs:** `FogGrid` dirties `FogOfWar|Things`.
- 🔑 **No Harmony and no custom flag is needed for any rebuild.** A mod can add a `MapMeshFlagDef`, since it is
  a Def with an index-derived bit. That is only worth doing if we ever want "rebuild wires only". The `Things`
  flag also fires for item drops and filth, so the layer will rebuild more often than strictly needed. Keep a
  per-section cache keyed by a hash of (conduit cells, obstacle cells, live-end set), so an unchanged hash
  re-emits the cached vertices and skips routing.

**How it reads the network.** All of these are O(1) per cell from existing grids:
- `map.linkGrid.LinkFlagsAt(c) & LinkFlags.PowerConduit` tells whether a cell is conduit.
- `map.thingGrid` gives the def at that cell, used to exclude `HiddenConduit` and untagged defs.
- `map.powerNetGrid.TransmittedPowerNetAt(c)` gives the net, for live/dead state.
- `CompPower.connectParent` and `connectChildren` give the machine hookups.
- Copy the Odyssey rule from `Graphic_Linked.ShouldLinkWith`: never join across a
  substructure/non-substructure edge.

**Overflow and culling.**
- Each conduit cell's geometry is emitted by the section that owns the cell, even when sprawl crosses into
  the next section.
- Override `GetBoundaryRect()` to return `section.CellRect.ExpandedBy(1)`. `Section` encapsulates every
  layer's boundary rect into its draw bounds, so overflow is not culled early at the screen edge.

**Save compatibility and removal.**
- Nothing is saved: no comp, no MapComponent data and no def that a save references.
- Removing the mod drops the layer class. The conduit def's texture swap reverts with it, so conduit
  becomes visible vanilla conduit again.
- A setting turns the whole layer off: `Visible => settings.enabled`. `Section.RegenerateSingleLayer` and
  `DrawLayer` both honour `Visible`.

**Hookup wires** (machine to conduit).
- Vanilla prints these in `CompPower.PostPrintOnto` through
  `PowerNetGraphics.PrintWirePieceConnecting(..., forPowerOverlay:false)`. It already skips them for
  `ThingDefOf.HiddenConduit` by def identity.
- For our invisible conduit we still need **one Harmony prefix** on `PrintWirePieceConnecting` that returns
  false only when `!forPowerOverlay` and the connect parent is one of our tagged defs. Our layer then draws a
  sagging hookup itself.
- The overlay's blue connector line stays intact, which avoids Invisible Conduit's bug (§2).
### 8.2 Routing: cell graph to smooth wires

**Verdict: MODERATE.** It is pure C# geometry with no engine risk.

1. **Graph.** Nodes are our conduit cells. An edge joins two orthogonal neighbours that are both ours and
   pass the substructure rule. Degree splits the cells into four kinds:
   - **0** is an isolated cell, drawn as a coil.
   - **1** is a dead end (§8.4b).
   - **2** is either a straight run or a corner.
   - **3 or 4** is a junction.
2. **Runs.** Walk the chains between junctions and dead ends into polylines of cell centres. Pass them through
   a **centripetal Catmull-Rom** spline, which never overshoots or loops at sharp corners the way a uniform
   spline does.
3. **Corners.** Cut each 90° corner into an arc with a **minimum bend radius**: 0.35 cell for a thin strand,
   0.5 for a fat cable. A tight double corner (an S inside 2 cells) flattens rather than kinks.
4. **Slack and sag.**
   - **Sag** offsets each run's midpoint sideways by `seed(edge) * messiness * 0.3` cells, capped so a strand
     never enters a cell blocked by a full-fill edifice.
   - **Loops** happen on runs of 4 cells or more with a chance set by the messiness slider: a small 360° loop
     (radius 0.2) laid flat on the floor.
   - **Coils** are a decal on isolated cells and capped stubs.
5. **Bundles.**
   - Each run carries 2-4 strands, a count picked once per run from its seed.
   - Each strand has a fixed lateral offset across the bundle (−0.12…+0.12 cell). It also has its own phase
     and amplitude for a low-frequency wander (a sine along the arc length), so strands cross and re-cross
     instead of running parallel.
   - Each strand also gets its own Y increment, a fraction of `Altitudes.AltInc` (0.0366), so crossings never
     z-fight.
   - Gauges and colours are mixed per strand (§8.8).
6. **Junctions.** Strands entering a T or X are routed to a shared **knot point** jittered inside the cell,
   and a junction decal sits over it: a taped lump, or a ration-tin box at X junctions. That hides every
   discontinuity where splines meet.
7. **Determinism.**
   - Seed with `Gen.HashCombineInt(x, z, map.uniqueID)` for cells and `HashCombine(min(a,b), max(a,b))` for
     edges, so the two neighbours agree on a shared edge whichever section draws it.
   - It is stable across frames, reloads and saves, and nothing is stored.
   - Avoid `Rand` (global state). Use a local hash-based PRNG.
8. **Cost.** About 3 strands × 10 segments × 2 tris is about 60 tris per cell, plus decals. A 200-conduit base
   is about 12k tris and a 5,000-conduit base about 300k tris. Only visible sections are drawn, and the mesh
   is static. CPU work happens at rebuild only, and a full section is about 17k vertices. Reuse vertex
   buffers.

### 8.3 Obstacles, wrapping and walls

**The relevant altitude layers** (`Verse.AltitudeLayer`). `Altitudes.AltitudeFor` = index × 0.3659, so a
higher Y draws over a lower one. `AltInc` = 0.0366, which gives 10 sub-steps per layer.

| idx | layer | y | relation to wires |
|---|---|---|---|
| 2 | Terrain | 0.73 | the floor; **snow is drawn here too** (`SectionLayer_Snow`, `AltitudeLayer.Terrain`), so snow is under the wires |
| 4 | Floor | 1.46 | |
| **5** | **Conduits** | **1.83** | **floor wires live here**, like vanilla conduit |
| 6 | FloorCoverings | 2.20 | rugs over the wires (reads right) |
| 8 | Filth | 2.93 | filth over the wires (grease and dirt on cable reads right) |
| **10** | **SmallWire** | **3.66** | vanilla hookup wires; **our hookups live here** |
| 11 | LowPlant | 4.02 | grass over the floor wires |
| 13 | Shadows | 4.76 | sun and edge shadows |
| 14 | DoorMoveable | 5.12 | door leaves cover wires at the threshold |
| **15** | **Building** | **5.49** | walls, trees, lamps, furniture. Planes **tilt**: top vertices +0.01 by default, and **+0.1 for plants** (`Plant.Print` passes `topVerticesAltitudeBias 0.1`). Wall corner fillers sit at +1 AltInc |
| 17 | BuildingOnTop | 6.22 | |
| 18 | Item | 6.59 | items always over the wires |
| 20/23 | LayingPawn / Pawn | 7.3 / 8.4 | **pawns, including carried things, always walk over the wires** |
| 34 | FogOfWar | 12.4 | fog covers everything |
| 38 | MapDataOverlay | 13.9 | the power overlay. We never draw here |

**Trunks.**
- **Which plants are trees:** `def.plant.IsTree`, which is `harvestTag == "Wood" || forceIsTree`.
- **Where a tree sits:**
  - `Plant.Print` (`maxMeshCount == 1`) centres the sprite at `TrueCenter` plus a 0.05 random horizontal
    jitter, using `Rand` seeded by `Position.GetHashCode()`.
  - It clamps the sprite so its bottom does not fall below the cell's south edge. The trunk base is therefore
    at about (x+0.5, z+0.05…0.15).
  - The sprite size is `drawSize.x × visualSizeRange.LerpThroughRange(growth)`. Oak, for example, is 1.5~2.0.
  - The UV is mirrored by `Rand.Bool`.
  - We can reproduce the exact jitter and flip by replaying that seed. The trunk's **pixel width and x
    position inside the art are not in any def**, so a small per-def anchor table is needed (default: centred,
    radius 0.08 × sprite size).
- **The wrap**, the two-layer trick done correctly:
  - **Back half** of the loop: at Conduits/SmallWire height. It sits far below the tree plane, so the trunk's
    opaque pixels hide it naturally, while it still shows through the cut-out gaps beside the trunk.
  - **Front half:** at **the tree plane's own Y at that z, plus ε (~0.002)**, which is
    `Building.AltitudeFor() + 0.1 × (z − spriteBottomZ) / spriteHeight + ε`. Do **not** put it on a fixed
    higher layer.
  - 🔑 Why the matched Y matters: a tree or lamp **south** of the wrapped trunk has its upper sprite (higher
    tilted Y) overlapping our cell. With the matched Y it still covers our front half, as it covers the trunk.
    A fixed BuildingOnTop front half would paint over that southern canopy, which is the classic clipping bug.
  - Items and pawns (higher layers) still draw over the wrap.
- **Rebuild:** tree growth, chopping and burning all dirty `Things`, so the wrap follows the trunk size and
  disappears with it.

**Poles.**
- **No power pole exists in vanilla 1.6.** RimSage search: `pole` returns no def. `Pylon` returns only Biotech's
  `MechPylon`.
- The pole-like 1×1 `Building`-altitude things are `StandingLamp`, `TorchLamp`, `Column`, `AncientLamppost` and
  `AncientCraneColumn`. Mod poles are UNMEASURED.
- **Phase-1 "pole" behaviour:** a powered lamp's hookup wire **climbs the post**. A short vertical strand on the
  lamp's front face uses the same matched-Y front rule, with a tape decal. A wire passing a column or lamp
  can take a single wrap, like a trunk.
- **Overhead spans** pole-to-pole are **NOT ADVISABLE**. A span floating above the floor has no correct
  occlusion against walls and furniture between the poles in a top-down sprite game. Every fixed altitude for it
  is wrong somewhere. If ever wanted, restrict spans to runs where every cell between is open floor, and treat
  it as a later experiment.

**Wires in walls** (owner requirement 2).
- `PowerConduit` is `isEdifice false`, and its description says it "can be placed under walls and other
  buildings".
- **Constructed wall** (an edifice with `Fillage Full` and not `building.isNaturalRock`):
  - The strand runs along the wall's top surface at Y = `Building + AltInc + 0.01 + ε`, just above the wall
    plane and its corner fillers.
  - The same tilt logic applies: anything south of the wall whose sprite reaches up over the wall still has a
    higher Y on its upper part and stays in front.
  - Where the run leaves the wall into an open cell, a **drape piece** (a decal) bends the cable over the
    wall's edge. On the south face it hangs down the face. On north, east and west edges it is a short bend.
  - Walls dirty `Buildings`, so building or removing a wall over a conduit rebuilds the wire correctly.
- **Natural rock and mountains** (`isNaturalRock`):
  - Draw nothing inside rock. Where a conduit run meets a rock face, place a **grommet** decal: a cable
    plunging into a drilled hole.
  - Rock tops are usually fogged anyway.
  - Whether conduit can even be built under natural rock is UNVERIFIED. It is rare either way.
- **Doors:** draw at floor level. The door leaves (DoorMoveable) cover the cable when closed, and it reads as a
  cable under the threshold.
- **Roofs:** RimWorld does not draw roofs over the map, so there is no interaction. Roofed cells only zero the
  sway (§8.4).
- **Fog:** like `SectionLayer_Things`, skip any conduit cell that is `fogGrid.IsFogged`. Otherwise a strand
  sprawling out of a fogged cell would reveal hidden conduit. FogOfWar is in the rebuild mask.
- **Multi-cell buildings and furniture over conduit:** floor wires stay at Conduits height. They are hidden by
  the opaque pixels and show through the gaps, such as between table legs, which is realistic. Wall-top
  treatment applies only to `Fillage Full` edifices.

**Mouse-over and selection.**
- Wires are not Things. Selection, tooltips and deconstruction still go through the invisible conduit's cell,
  as now.
- Keep sprawl at 0.35 cell or less so a wire stays mostly over its own cells.
- Optional: while a conduit is selected, redraw its cached strand segment in a highlight material from
  `MapComponentUpdate`, so players see what they clicked.
### 8.4 Sway

**How the engine sways plants** (RimSage):
- `MaterialPool.MatFrom` calls `WindManager.Notify_PlantMaterialCreated(mat)` for **any** material built with
  `ShaderDatabase.CutoutPlant` or `TransparentPlant`. Every such material joins a static list.
- `WindManager.WindManagerTick` advances `plantSwayHead += min(WindSpeed, 1)` each tick, or zeroes it when
  `Prefs.PlantWindSway` is off. On the current map it calls `SetFloat(ShaderPropertyIDs.SwayHead, …)` on every
  listed material.
- `PlantUtility.SetWindExposureColors` writes the **vertex alpha**: 0 on the two bottom vertices,
  `topWindExposure × 255` on the two top vertices.
- `Plant.Print` also passes `HashOffset() % 1024` as the UV z payload, which is almost certainly a per-plant
  phase.
- Plants are printed into the static section mesh. **The motion is entirely in the vertex shader. No CPU work
  happens per frame.**

**So the cheapest wire sway is free.**
- Build the strand material with `ShaderDatabase.CutoutPlant` and give it the strand texture. It joins the
  wind list automatically.
- Write **vertex alpha** as the sway weight per vertex:
  - 0 where a strand lies on the floor, is taped or is anchored;
  - rising toward the middle of any lifted span (trunk loops, pole climbs, wall drapes);
  - **0 under a roof** (`roofGrid.Roofed`), since there is no wind indoors.
- Write the UV z as a per-run phase.
- What this gives:
  - wind-speed-driven sway that respects the game's own "plant sway" preference;
  - storms sway harder (`WindSpeed` includes weather and `CompWindSource`);
  - zero CPU per frame on a 200- or a 5,000-conduit base.
- **What to sway:** realistically, cable lying on a floor does not sway. Sway the lifted bits: trunk-wrap
  loops, pole climbs and wall drapes. Optionally add a faint ripple on outdoor floor runs, behind a setting.
- **Caveat:** the shader is a compiled asset. Its displacement formula (the axis, and how it uses vertex alpha
  and UV z) is **not in the decompiled C#**, and is inferred from how `Plant.Print` feeds it.
  - If it displaces only along world x, east-west spans would stretch along their own axis rather than sway.
    Keep amplitudes small and weight north-south spans more.
  - `CutoutPlant` also carries fall-colour parameters. We do not set `_FallBehaviorEnabled`, so it should stay
    off. UNVERIFIED.

**Fallbacks if the plant shader misbehaves.**
- **Our own vertex shader in an AssetBundle:** HARD. It is a new toolchain for us and needs the Unity version
  matched to the game.
- **CPU mesh deformation per frame for lifted spans only**, from `MapComponentUpdate`: MODERATE.
  - Even a 5,000-conduit base has perhaps 50-200 lifted spans, each about 40 verts. That is under 10k verts a
    frame and cheap.
  - Animating all floor strands on the CPU (about 150k verts on a 5,000-conduit base) is **not** acceptable.

**Level of detail and culling.**
- Sections are culled by the engine (`DrawMapMesh`).
- For LOD, emit two sub-meshes per material: full strands, and a 1-strand simplified bundle. Override
  `DrawLayer` to set `LayerSubMesh.disabled` by `Find.CameraDriver.CurrentZoom`. At far zoom, thin strands
  alias into shimmer, so drop to the simplified bundle and hide decals.
- Settings: sway on/off, which only rebuilds with alpha 0; floor ripple on/off; LOD threshold.

### 8.4b Break detection: live ends spark and whip, dead ends lie limp (owner requirement 1)

**What a "break" is when the conduit is invisible.** The wires are drawn only where conduit exists, so a break
is a **gap**: a cell with no conduit between two conduit runs. At rebuild time the router already finds every
**dead end** (a degree-1 cell). A dead end is classed by what lies beyond its open side:

| case | test | drawn as |
|---|---|---|
| terminates into a machine or transmitter building | the neighbour cell holds a `CompPower` (connector or transmitter, including power switches and batteries) | normal plug-in, no end |
| **paired break** | the straight continuation, within 1-3 non-conduit cells, reaches another of our conduit cells, **on a different net** or the same one | **frayed ends reaching into the gap**, leaving a visible gap |
| **planned or auto-rebuild break** | a `Blueprint_Build` or `Frame` of a conduit def sits in the gap cell. Vanilla `ThingUtility.CheckAutoRebuildOnDestroyed` leaves exactly that when a player conduit is destroyed with auto-rebuild on | frayed end |
| lone stub | none of the above | **taped cap**. A deliberate end never sparks |

How breaks arise:
- **A conduit destroyed** (fire, explosion, raid): two dead ends face a 1-cell gap → paired.
- **Deconstructed:** paired. If the gap is wider than 3 cells, the ends become lone capped stubs. That is
  correct, since a long gap is a layout and not a break.
- **A transmitter building removed** from the middle of a run, a battery for example: paired across its old
  footprint.
- **Wall or building removed:** no break. Conduit under a wall was continuous all along.

**Live or dead per end.**
- `powerNetGrid.TransmittedPowerNetAt(cell)` returns the end's net.
- **live** = `net.HasActivePowerSource`. That is a battery with `StoredEnergy > 0` that is not EMP-stunned,
  or a trader with `PowerOutput > 0`.
- 🔴 **Live/dead flips without any mesh-dirty event:** solar at night, batteries draining, an EMP. So:
  - The layer publishes each section's frayed ends to a small `MapComponent` registry. This is runtime only,
    with **no `ExposeData`**, so nothing is saved.
  - Every **250 ticks** the component re-evaluates live/dead once per distinct net. `HasActivePowerSource`
    loops transmitters, but only until it finds a source, so this is negligible.
  - A flip **does not** rebuild the static mesh. Limp ends are part of the static mesh; live ends are drawn
    dynamically.
  - To make that possible, the layer omits the last ~0.4 cell of every frayed end from the static mesh, and the
    component draws that tail itself.
- **Live end:** the component draws the frayed tail each frame in `MapComponentUpdate` with
  `Graphics.DrawMesh`:
  - a small cached ribbon mesh, rotated and bent by a jittery whip function (sum of sines plus random snaps,
    keyed to **real time**, so a broken line is still findable **while paused**);
  - every 40-120 ticks, `FleckMaker.ThrowMicroSparks(tip, map)`, plus an occasional
    `ThrowLightningGlow(tip, map, 0.4)`.
  - Both are vanilla flecks, with no new art needed. `ShouldSpawnMotesAt` already culls off-screen positions.
  - Cost is O(visible live ends), which is a handful on any real base.
- **Dead end:** a static limp, slightly curled tail with a dull frayed-copper decal. No motion, no light.
- **Brownout or power off:** a net with a source that is not active (night solar, empty batteries) reads
  **dead**, which is physically right: no current, no sparks. A tripped or flicked-off power switch splits the
  net at a building, so it is not a break.
- Settings: break sparks on/off, whip on/off (sparks only), spark rate, and an "only when the power overlay is
  open" option for players who find it noisy.

**Gameplay clarity.**
- The whole readout is cosmetic. No danger, damage or fire comes from sparks (Tier C stays separate).
- A break can be seen at a glance from across the map at normal zoom, because the flecks are bright.
- Bars for Northstar (state reads, no eyes needed):
  - destroy one conduit in a live line, then read the registry: 1 live end, plus 1 dead end if the far side
    has no source;
  - after 250 ticks, flip the source off and see the live end turn dead.
### 8.5 Clipping and artifact risk register

| # | failure mode | mitigation | check |
|---|---|---|---|
| 1 | strands z-fight at crossings | per-strand Y increment (a fraction of AltInc) | visual |
| 2 | wire paints over a **tree or lamp to the south** whose sprite overlaps the wrap or wall cell | front-wrap and wall-top Y **matched to the occluder's own tilted plane + ε**, never a fixed higher layer (§8.3) | visual; keeper save with a tree row south of a wrapped trunk and of a wired wall |
| 3 | wall-top wire fights with **wall corner fillers** (+1 AltInc) | wall-top Y above `Building + AltInc + 0.01` | visual |
| 4 | sprawl disappears **under walls** or into rock and looks cut | the router never pushes sag into `Fillage Full` cells; a grommet decal at rock faces; a drape decal at wall edges | state: no strand vertex inside a full-fill cell that holds no conduit (geometry assert in the selftest) |
| 5 | **doors** chop the cable | floor level under the threshold, covered by the leaves | visual |
| 6 | multi-cell furniture over conduit | floor wires stay at Conduits height and show through gaps, which is realistic | visual |
| 7 | **fog** leak: strands reveal hidden conduit | skip fogged cells; FogOfWar is in the rebuild mask | state: zero vertices from fogged cells |
| 8 | **culling pop** at screen edges from overflow | `GetBoundaryRect` expanded by 1 | visual |
| 9 | stale join across a section edge | the conduit keeps `linkType Transmitter`, so its neighbours rebuild; edge-seeded joins | state: place a conduit at x=16 or 17 and compare both sections' join points |
| 10 | **transparent** strand material sorts wrongly against filth, shadows and gas (also transparent) | strands use a **cutout** family shader (`CutoutPlant`), which is alpha-tested. The soft drop shadow is a separate transparent strip at Conduits height | visual |
| 11 | **far zoom** shimmer and aliasing | LOD sub-mesh swap; mipmapped strip textures | visual |
| 12 | **snow and sand** | snow is drawn under Conduits (`AltitudeLayer.Terrain`), so wires show on top of snow, as vanilla conduit does. Optionally fade wires where the snow is deep | visual |
| 13 | pawns, carried items, laying pawns | always above (layers 18-23) | none needed |
| 14 | **Gravship cutscene** (Odyssey): `SectionLayer_Things.DrawLayer` has special cutscene handling (disables `renderQueue 2950` sub-meshes) that our layer would not get | hide the layer while `WorldComponent_GravshipController.CutsceneInProgress`, then verify | UNVERIFIED, owed a live look |
| 15 | wire drawn across the substructure/hull edge | reuse the `ShouldLinkWith` substructure test | state |
| 16 | the power overlay loses its connector lines (Invisible Conduit's bug) | the prefix acts only when `!forPowerOverlay` | state: the `MatConnectorLine` sub-mesh is non-empty |
| 17 | sway shader displaces along the wrong axis or fall colours tint the wires | small amplitudes; CPU fallback for lifted spans | visual, first test |
| 18 | spark flecks spam the screen in big breakdowns | per-map cap on concurrently sparking ends; settings | state |

**Testing split.**
- **Northstar state reads** cover these, all cheap and deterministic:
  - the layer class exists on a section;
  - vertex and hash stability across save and load;
  - no vertices from fogged cells or inside full-fill non-conduit cells;
  - section-edge joins;
  - overlay lines intact;
  - break registry contents and the live/dead flip;
  - toggle off leaves the sub-meshes empty.
- **Visual review is unavoidable** for rows 1-3, 5, 6, 8, 10-12, 14 and 17. That review is **a keeper
  savegame** with one test bed per row, laid out on a grid, for the owner to walk. A screenshot is never a pass
  bar.

### 8.6 Compatibility

**Active mods relevant here.** MEASURED by parsing `infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml`
(610 active mods): `vanillaexpanded.vfepower`, `dubwise.dubsbadhygiene.lite`, `dubwise.rimefeller`,
`noneobsidiaexpansion.ledlightsstrip` and `dubwise.dubsmintminimap`. Invisible Conduit is **not** active.

| neighbour | interaction |
|---|---|
| vanilla `HiddenConduit` | excluded by def, so it stays the tidy invisible option. Vanilla already skips its hookup wire |
| Invisible Conduit Continued (inactive) | both make conduit invisible, which is harmless. Its unconditional `PrintWirePieceConnecting` prefix also kills our hookups' replacement test and the overlay lines. Declare it incompatible in About |
| Underground Wires-style mods (none active) | different defs; drawn only if tagged |
| **VFE Power** (active) | any extra conduit defs it adds are UNMEASURED. The default target set is "defs with `building.isPowerConduit` and `linkType Transmitter`", with a settings checklist listing every match so the player can opt out |
| **LED Lights Strip** (active) | "placed like conduit". If its defs set `isPowerConduit` we would cover them in wires. UNMEASURED: check its defs before choosing the default target set |
| **Dubs Bad Hygiene Lite, Rimefeller** pipes | their own link flags and defs, so untouched. The same layer could later draw messy *pipes* through an opt-in extension |
| conduit retexture mods | we replace the conduit texture with a transparent one. Load order decides, so put our patch in a `zzz` file and `loadAfter` known retextures |
| overlay or minimap mods (Dubs Mint Minimap) | the minimap reads grids, not our meshes, so no interaction expected |
| Multiplayer | visual only. The layer uses no `Rand`, and the 250-tick poll only reads state |

### 8.7 Phased plan

🔴 This is still gated by the 2026-10-01 build pause (§6). These are effort estimates for when it lifts.

| phase | scope | effort | art |
|---|---|---|---|
| **0. Mock-ups** | Python prototype of §8.2 rendering 3 messiness levels, plus a trunk wrap and a wall run, to PNG. The owner picks | 1 day | uses the phase-1 strips once generated, or flat placeholders |
| **1. Static overlay + break readout** | invisible conduit (XML texture swap and transparent PNG); `SectionLayer_RM_MessyWires`; bundles, corners, junction knots, capped stubs; wall-top runs with drapes and rock grommets; trunk wraps (matched-Y front half); hookup prefix with sagging hookups that climb lamp posts; **break detection: frayed ends, live/dead poll, vanilla sparks, whip on live ends**; settings; first script | **5-7 days** | **13** (below) |
| **2. Sway** | `CutoutPlant` strand material, vertex-alpha weights on lifted spans, roof zeroing, settings; CPU fallback if the shader misbehaves | 1-2 days (4-5 with the fallback) | 0 new |
| **3. Richer physics and decoration** | floor loops and coils by slider; per-def trunk anchor table; column and lamp wraps; snow fade; LOD sub-mesh; selection highlight; Jawa campaign art set (`RUT_`) | 3-5 days | +10 |
| 4. Overhead spans (experiment only) | pole-to-pole catenaries over open cells only | — | not recommended |

Break-sparking is in **phase 1** because it is cheap: the router already finds dead ends, the sparks are
vanilla flecks, and the poll is 250-tick. It is also the highest-value debugging aid in the mod.

### 8.8 Aesthetic: "truck drivers in space" (owner requirement 3)

**Direction.** Ugly on purpose. Nothing matches, everything is repaired, and it has been working for twenty
years.
- **Gauges and sheaths:** a fat orange extension-cord sheath, grey ribbed armoured cable, red-and-black twin
  lead, a sun-faded braided green, and bare copper where insulation has burned or been stripped.
- **Repairs:** black and yellow electrical tape in lumpy wraps, hose clamps, zip ties, rag bandages, solder
  blobs, and a splice twisted by hand.
- **Grime:** grease smears and fingerprints on the cable and the floor around junctions.
- **Junctions:** a "box" made from a ration tin or a droid's chest plate.
- **Stencil marks:** hand-painted arrows and tally marks.

Style rules:
- Still the painterly lawset: top-lit cylinders, value over detail at 64 px a cell, the 70s-brown palette with
  loud accent sheaths.
- The franchise-free `RM_` set stays generic and dirty. Overtly Jawa trinkets (droid plating, rag-and-bead
  wraps) go in the `RUT_` set (§4).

**Phase-1 art (13).**
- **Strand strips, 5:** tileable 128×32 strips with alpha edges and mipmaps:
  - orange cord;
  - grey armoured;
  - red/black twin;
  - bare copper;
  - a taped bundle.
- **Drop-shadow strip, 1:** soft shadow.
- **Decals, 7:**
  - tape lump (junction T);
  - tin box (junction X);
  - taped cap (lone stub);
  - frayed end, dead (dull copper, limp);
  - frayed end, live (bright copper, scorch);
  - wall drape over an edge;
  - rock grommet.

**Phase-3 additions (10).**
- **Strand strips, 2:** braided green and greasy black.
- **Decals, 7:**
  - hose clamp;
  - zip tie;
  - rag wrap;
  - floor coil;
  - trunk-wrap front;
  - trunk-wrap back;
  - pole-climb tape.
- **Grease decals, 2:** on the floor.
- **`RUT_` Jawa set:** 2-3 more strips.

Notes:
- Sparks reuse vanilla `MicroSparks`/`LightningGlow`, so they need **0** new art. One custom spark fleck is
  optional.
- The total is about 23-26 textures. A static-only Tier B set would be 10-14.

### 8.9 What this pass could not verify

- **The `CutoutPlant` shader's displacement function**, meaning its axis and how it uses vertex alpha and UV z.
  It is a compiled asset, and only its C# feeding side was read. The sway verdict depends on it.
- **Whether cutout map shaders write depth** (ZWrite), which the matched-Y occlusion argument assumes. The
  engine's design strongly implies it: plants get a +0.1 tilt that would be pointless without a depth test.
  It is still not read from a shader.
- **The gravship cutscene path** for a custom section layer (risk 14).
- **Trunk pixel positions and widths** in vanilla and modded tree art. These are not in defs.
- **Whether conduit can be placed under natural rock.**
- **The conduit defs of VFE Power and LED Lights Strip.** A full-disk XML sweep for `isPowerConduit` was
  started and abandoned at 600 s on the slow drvfs mount; run it from a narrower root.
- **Any performance number.** All triangle and vertex counts are arithmetic, not measured.
- The overlay was not tried in game. This pass did not touch the game, the bridge or `src/`.
