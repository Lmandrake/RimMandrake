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
| Messiness slider | slack, excursion cap (0.38 tidy → ~2.6 cells owner level, §8.11), loop/heap chance | live (dirty all sections) |
| Load bundles (§8.10) | on/off (off = 2 strands), strand rating W per strand, linear or log | live |
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
- Override `GetBoundaryRect()` to return the real extent of every vertex printed (as `SectionLayer_Things`
  does), not a fixed margin: excursions reach up to 3 cells (§8.11.3). `Section` encapsulates every layer's
  boundary rect into its draw bounds, so overflow is not culled early at the screen edge.

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
   - **Sag and excursions:** the owner level lays 1.9× the run's length as walkability-bounded excursions,
     loops, figure-eights and heaps up to about 2.6 cells out, settled as a relaxed rope (§8.11). "Tidy"
     keeps a small sag capped at 0.38 cell. No strand vertex ever enters an unwalkable cell.
   - **Loops** happen on runs of 4 cells or more with a chance set by the messiness slider: a small 360° loop
     (radius 0.2) laid flat on the floor.
   - **Coils** are a decal on isolated cells and capped stubs.
5. **Bundles.**
   - Each run carries **1-10 strands, set by the watts flowing along it** (§8.10), never by a random pick.
   - Each strand has a fixed lateral slot across the bundle (the bundle stays under 0.62 cell wide at 10). It also has its own phase
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
- Excursions reach 1-3 cells (§8.11), so a loop is not clickable by itself. While a conduit is selected,
  highlight its whole run (required now, see below).
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
| 4 | sprawl disappears **under walls** or into rock and looks cut | excursions are clipped to walkable floor and the settle projects every vertex out of unwalkable cells (§8.11); a grommet decal at rock faces; a drape decal at wall edges | state: no strand vertex inside an unwalkable cell that holds no conduit (geometry assert in the selftest, base and sprawl scenes) |
| 5 | **doors** chop the cable | floor level under the threshold, covered by the leaves | visual |
| 6 | multi-cell furniture over conduit | floor wires stay at Conduits height and show through gaps, which is realistic | visual |
| 7 | **fog** leak: strands reveal hidden conduit | skip fogged cells; FogOfWar is in the rebuild mask | state: zero vertices from fogged cells |
| 8 | **culling pop** at screen edges from overflow (excursions reach 3 cells) | `GetBoundaryRect` returns the real printed extent, as `SectionLayer_Things` does (§8.11.3) | visual |
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
| **1b. Load bundles** (§8.10) | subtree-sum flow on trees, linear rating, hysteresis, port/peel matching, 250-tick poll, settings | +2-3 days | 0 new |
| **1c. Owner excursions** (§8.11) | slack, walkability-bounded excursions/loops/heaps, rope settle, per-run cache, 3-cell dirty reach, real `GetBoundaryRect`, fog-as-obstacle, run highlight on select | +4-6 days | 0 new (coil/heap are strands) |
| **3b. Kirchhoff loops** (§8.10) | CG solve on the reduced graph for meshed nets; EMA + dwell; debug flow overlay | +1-2 days | 0 new |
| 4. Overhead spans (experiment only) | pole-to-pole catenaries over open cells only | — | not recommended |

Break-sparking is in **phase 1** because it is cheap: the router already finds dead ends, the sparks are
vanilla flecks, and the poll is 250-tick. It is also the highest-value debugging aid in the mod.

### 8.8 Aesthetic: "truck drivers in space" (owner requirement 3)

**Direction.** Ugly on purpose. Nothing matches, everything is repaired, and it has been working for twenty
years.
- **Structure (owner, 2026-10-02):** three style families: 1 Cybertek, 2 Extension cord and 3 Star Wars.
  **Jawa is a variant of the Star Wars family**, not a separate set. In his words: *"Jawa is certainly more
  option 3. Though there should be no white versions and many should be smooth black cables with less
  shine."*
- **Gauges and sheaths (Star Wars family and Jawa variant):**
  - smooth **matte** black cable dominates (low, broad sheen and no specular line);
  - a few dark corrugated-steel hoses and coiled black cords;
  - **no white cable or tape anywhere in the family.**
  - The Jawa variant adds the jury-rigging below, with dark, ochre or oil-stained tape.
- **Repairs:** dark and ochre electrical tape in lumpy wraps, hose clamps, zip ties, rag bandages, solder
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
  - matte black cable;
  - dark corrugated steel hose;
  - coiled black cord;
  - bare copper (frayed ends only);
  - a taped strand.
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
- **Strand strips, 2:** greasy black and heavy black (the extension-cord and Cybertek families need their own
  strips if they ship).
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
- **Everything in §8.10-8.11 runs in Python only.** The C# solve and settle costs are arithmetic. The equal-
  conductance loop split is a modelling choice, not an engine fact. `CameraDriver.CurrentViewRect`'s own body
  and the vanilla battery def's comps (whether it also has a `CompPowerTrader`) were not read.

### 8.10 Load-proportional bundles (owner question of 2026-10-02)

Owner, verbatim: *"This seems to vary the number of cables between nodes. Is that an algorithm? It would be
better to have it vary from one to ten, depending entirely on how much flows along there. That would really
be the realism."*

Answer to his question: in phase 0 the count (2-4) was a seeded random per run, purely cosmetic. This
section replaces it: **every run carries 1-10 strands, set by the watts flowing along it.**

**Verdict: MODERATE.** Phase 1 is a tree/Kirchhoff solve on a graph the router already builds; nothing in the
engine has to change. Mock-ups: `05_load_*.png` (§8.10.8).

#### 8.10.1 What the engine gives us (decompiled 1.6, RimSage)

- **No per-conduit flow exists anywhere.** `PowerNet` is a flat bag: `transmitters`, `connectors`,
  `powerComps` (`CompPowerTrader`) and `batteryComps` (`CompPowerBattery`), with whole-net totals only
  (`CurrentEnergyGainRate()`, `CurrentStoredEnergy()`). Nothing in `PowerNet`, `PowerNetManager`,
  `PowerNetGrid`, `PowerNetMaker` or `CompPower` stores a flow per cell or per edge. **Flow must be derived.**
- **Per device:** `CompPowerTrader.PowerOutput` is negative for consumers and positive for producers
  (`SetUpPowerVars` sets `-Props.PowerConsumption`, or `-idlePowerDraw` when off). It reads 0 when EMP-stunned.
  Only comps with `PowerOn` count toward the net's gain.
- **Producers update every tick** in `CompPowerPlant.CompTick`. Solar is `Lerp(0, max, skyGlow)` times the
  unroofed fraction. Wind is recached every 250 ticks. Geothermal is constant.
- **Batteries:** surplus is spread by `DistributeEnergyAmongBatteries`, which shuffles the batteries and fills
  them evenly. A deficit is drawn in equal shares (`DrawEnergyFromBatteries`). So per battery, flow is about
  net gain divided by the non-full (or non-empty) batteries. Charging has an efficiency loss; discharge has none.
- **Shortfall (brown-out):** `PowerNetTick` turns off about 5% of the powered consumers, chosen at random,
  every 20 ticks until the net balances. It turns them back on gradually when there is power. We read the real
  `PowerOn`, so the bundles follow what the engine actually powers.
- **Topology:** a net is the 4-neighbour flood fill of transmitting buildings (`PowerNetMaker`). A switched-off
  `Building_PowerSwitch` stops transmitting (`TransmitsPowerNow`) and splits the net in two, so a switch is
  just a cut in the graph. Machines join a transmitter through `CompPower.connectParent`, up to
  `PowerConnectionMaker.ConnectMaxDist` (6) cells away.
- **Hooks:** `PowerNetManager.RegisterPowerNet` and `DeletePowerNet` are public, non-virtual and fire on every
  transmitter-side change; Harmony postfixes catch them. Connector changes need `CompPower.ConnectToTransmitter`
  and `PowerConnectionMaker.DisconnectFromPowerNet`. `PowerNetGrid.TransmittedPowerNetAt(c)` is a cheap
  per-cell net lookup.

#### 8.10.2 Deriving per-segment flow

The graph is the one §8.2 already builds: conduit cells as nodes, orthogonal neighbours as edges. Each
device's `PowerOutput` is injected at its `connectParent` cell (producers +, consumers −). Batteries take the
balance: −(net gain) shared over the batteries. The flow on each edge is then computed by one of three methods:

| method | what it does | tree | loop | cost |
|---|---|---|---|---|
| **A. Subtree sums** (BFS spanning tree from the biggest source) | an edge carries the net injection of everything beyond it | exact | **wrong**: one side of the loop carries all, the closing edge 0 | O(V) |
| **B. Equal split at loops** (heuristic) | at a node with k downstream edges, split equally | exact | plausible on symmetric loops, wrong on lopsided ones | O(V) |
| **C. Kirchhoff, equal conductance** (resistive network) | solve `L·φ = b` (graph Laplacian, one grounded node per net); flow on edge = `φa − φb` | exact (identical to A) | physical: splits by path length | sparse solve |

- **Recommended: C.** It equals A on every tree (asserted in the selftest), and on a loop it gives the split a
  player expects: the short side of a ring carries more. A shows a loop as one fat side and one empty side
  (`05_load_method_ring.png`). B is not worth having beside C.
- **Size of the solve.** Collapse every chain of degree-2 cells that holds no hookup into one edge with
  conductance 1/length. The nodes are then only junctions, dead ends and hookup cells: typically 10-20% of the
  cells. A 200-conduit base has about 20-40 nodes; a 5,000-conduit base about 500-1,000.
- **Solver.** Use conjugate gradient on the reduced Laplacian (symmetric positive-definite once grounded). It
  needs about 20-60 iterations at about 2E flops each, so even a 1,000-node net is well under 1 ms. A dense
  solve at 1,000 nodes (10⁹ flops) is not acceptable. Shortcuts:
  - if E = V − 1 (a tree, which most bases are), use A directly and skip the solve;
  - if CG fails to converge in 200 iterations, fall back to A.
  These costs are arithmetic, not measured.
- **Edge cases:**
  - **Flow reversal:** a battery that switches from charging to discharging reverses its branch. The magnitude
    sets the strand count and the sign only matters for the debug arrows.
  - **Multiple sources:** handled by superposition; they are just several positive injections.
  - **Dead ends and the live side of a break:** these carry 0 W and draw the minimum, 1 strand.
  - **Unpowered nets** (no source, or `CurrentStoredEnergy` 0 with no gain): 1 strand everywhere. The
    live/dead break readout of §8.4b is unchanged.
  - **Brown-out:** consumers that the engine switched off read `PowerOn` false and inject 0, so their branch
    thins. That is correct.
  - **Switches:** an off switch is a gap in the graph, so each side is solved as its own net.
  - **Idle draw:** `PowerOutput` already includes it.
  - **Wire-connected but untagged transmitters** (modded conduit we do not draw) are still graph nodes and
    carry flow. They are simply not drawn.

#### 8.10.3 Watts to strands

| mapping | behaviour | verdict |
|---|---|---|
| **Absolute, linear "strand rating"**: n = ceil(W / R), clamp 1..10 | a 10-strand trunk always means real load (≥ 9R); thickness is comparable across nets and saves | **recommended default**, R = 250 W |
| Absolute, logarithmic: n = 1 + log₂(W / W₀) | spans 100 W to 50 kW; big modded bases never saturate | setting ("huge base" mode) |
| Relative to the net's max: n = 10 · W / Wmax | the trunk is always 10 | rejected: switching one machine changes every run on the net (non-local popping), and the 10 means nothing |

- With R = 250 W, a vanilla generator's 1,000 W reads as 4 strands, and a 2.5 kW trunk saturates at 10.
  Settings: **strand rating (W per strand)** with a slider of 100-2,000 W, **cap** fixed at 10, **minimum**
  fixed at 1 so every wire always shows, plus linear or log mode.
- **Quantisation with hysteresis** (`strands_hyst`, selftested): step up as soon as W passes n·R; step down
  only once W is below (n − 1 − 0.15)·R. A load hovering at a threshold never flickers.
- **Smoothing:** feed the quantiser an exponential moving average over about 2 polls, so a solar panel at dusk
  steps down a strand at a time.
- **Minimum dwell:** a run changes its count at most once per 2,500 ticks, unless the topology changed.

#### 8.10.4 Peeling off at junctions

The router stops each run at its junction cell's **edge** (the port), with its n strands in fixed lateral slots
there. Wander and sag fade to 0 over the last 0.45 cell, so the slots are exact. Inside the junction cell:

1. Each slot is typed **in** (its flow enters the junction) or **out**. A machine hooked at a junction or
   mid-run tap is one more port, and its strands sink into the knot.
2. All slots are sorted by angle around the cell. In-slots and out-slots are paired by a **planar,
   non-crossing matching**: a parenthesis stack run twice around the circle. The strands on the side of the
   trunk facing a branch peel into that branch, and the rest carry straight on. n strands in become n1 + n2 out.
3. Each pair is joined by a short cubic Bézier from port to port, using the port tangents.
4. Leftover slots, where quantisation makes the in-count differ from the out-count, end under the junction
   decal. In the Jawa set that is a tape lump; in the Star Wars set a greeble box.
5. **One strand keeps one look end to end.** A union-find over (run, slot) through every matched pair picks
   one strand kind per connected strand, so a corrugated hose stays corrugated as it peels off.

Phase 0's random 2-4 count, and its tape-ball junction that hid every mismatch, are both superseded by this.

#### 8.10.5 Recompute policy and cost

- **Topology** (the graph and the reduced Laplacian) is rebuilt on `RegisterPowerNet` / `DeletePowerNet` /
  connect / disconnect postfixes, and cached per net.
- **Flow** is re-solved per net **every 250 ticks**, from the current `PowerOutput`s. It is never per frame.
  The CG solve warm-starts from the previous φ, so it usually needs only a few iterations.
- **Mesh:** only runs whose quantised count changed dirty their sections (`MapMeshDirty` on one cell of the
  run, custom flag or `PowerGrid`). Changes are rare because of the hysteresis and dwell above.
- **Cost:**

| base size | reduced nodes | per 250-tick solve | sections re-meshed per change |
|---|---|---|---|
| 200 conduit | 20-40 | ~µs (tree: no solve) | 1-3 |
| 5,000 conduit | 500-1,000 | < 1 ms CG (tree path O(V)) | only the sections holding changed runs |

These are arithmetic estimates, not measured.

- **Geometry cost grows with strand count.** At about 60 tris per strand-cell, a 10-strand trunk is about
  600 tris per cell. A 5,000-conduit base averaging 3 strands is about 900k tris. The LOD sub-mesh (§8.4)
  collapses to a single fat strip at far zoom.
- **Save-compat is unchanged.** Flow is derived from live state on load, and nothing is saved.

#### 8.10.6 What it teaches the player, and where it misleads

**Teaches:**
- **Where the main trunk is:** follow the fat bundle back to the generators.
- **Which branch is the hog:** a 5-strand spur off to the smelter.
- **That a branch is idle:** it is 1 strand.
- **What a cut would cost:** a break in a 10-strand trunk is visibly worse than one in a 1-strand spur.
- **Day/night:** the solar run thins at dusk, and the battery run reverses.

**Misleads (say so in the tooltip and the docs):**
- **The battery bank.** When a big machine switches off, its spur drops to 1 strand, but the trunk keeps its
  thickness and the **battery branch gets fatter**: the surplus now charges the bank. This is realistic, but
  players may read it as a "battery is consuming power" bug (`05_load_beforeafter_jawa.png`, middle panel).
  Once the bank is full the surplus goes nowhere, and the trunk then thins. Generators do not throttle, so that
  surplus is wasted.
- **Equal conductance is fiction.** Real conduit has no resistance in RimWorld, so the loop split is a
  plausible picture, not a game fact.
- **Thickness is load, not capacity.** A 10-strand trunk is not "maxed out". RimWorld conduit has no capacity
  limit, so nothing explodes from thickness.
- **A long thin run feeding a far big load** looks wrong to anyone expecting a fat feeder all the way. It is in
  fact fat all the way, which is right. A mesh with a short parallel path takes most of the flow.
- **A dead end on the live side of a break** shows 1 strand: it is drawn, it carries nothing.

#### 8.10.7 Verdict, phases and art

**MODERATE.** The phases slot into §8.7:

| phase | scope |
|---|---|
| **1** | Load bundles with method A (subtree sums) on trees, which most bases are, and A as the loop fallback. Linear rating, hysteresis, the port and peel matching, union-find kinds, 250-tick poll. Settings: rating, linear/log, on/off (off = fixed 2 strands). |
| **3** | Kirchhoff CG on the reduced graph for nets with loops; warm start; EMA and dwell; a debug overlay with the per-run W labels and arrows of the mock-up. |

- **Art: recommend procedural assembly, no new art.** Every strand is the same single-strand strip texture
  (§8.8 strand strips) laid along its own spline, so 1-10 strands is just 1-10 ribbons.
- Pre-drawn "n-strand bundle" strips would need 10 counts × strand kinds × junction transitions, which is
  hundreds of textures, and they still could not peel at junctions.
- The junction decals become smaller: they only cover leftover ends, not a whole bundle.
- **The art count of §8.8 is unchanged.**

#### 8.10.8 Mock-ups

In `Transient/messy_conduit_mockups_20261002/`, rendered by
`src/RimMandrake/Utils/mockups/messy_conduit/load.py`:
- `05_load_starwars_day.png`, `05_load_jawa_day.png` and `05_load_extcord_day.png`. Each is the base scene plus
  a solar array and a smelter. Every run is labelled with its watts, strand count and flow direction, and there
  is a strand legend.
- `05_load_beforeafter_jawa.png`: smelter on, then off, then night (battery discharging, trunk reversal).
- `05_load_method_ring.png`: Kirchhoff against the spanning tree on the ring.

### 8.11 Owner excursions: big walkability-aware slack (owner, 2026-10-02)

Owner, verbatim, with a photo of an orange extension cord lying in big loose loops, figure-eights and a heap
on a dirt floor (`Transient/messy_conduit_mockups_20261002/00_owner_reference_orange_cord.png`): *"Yes, I want
it to have much larger excursions that avoid unwalkable areas or even pile up against them. I think you know
what I'm wanting."*

This **supersedes the 0.35-0.38 cell sprawl cap** of §8.2, §8.3 and §8.5 row 4. Wires may now wander 1-3
cells from their conduit.

**Verdict: MODERATE-HARD.** The routing itself is moderate. The hard parts are invalidation reach, fog and
selection (below). Mock-ups: `06_sprawl_jawa.png` and `06_sprawl_extcord.png`.

#### 8.11.1 Model

Implemented in `rope.py`.

1. **Slack.** Each strand gets more cable than its run needs: length = run × (1 + slack). The default is
   slack 0.9 and the excursion cap 2.6 cells. A fat bundle is stiffer: its slack is divided by
   (1 + 0.15·(n − 1)), so a 10-strand trunk lies straighter than a 1-strand spur. That agrees with §8.10.
2. **Excursions.** Broad lateral bumps, 1.2-2.6 cells long, are shared by the whole bundle, so the strands
   travel together. Their side is biased toward open floor: the router probes free distance on both sides. 30%
   go toward the obstacle side, which makes the cable pile up against it.
   - **Bounded by walkability:** an excursion is clipped to the open floor in its direction, found by marching
     along the normal. It never jumps a wall.
   - **The clipped excess is kept as length.** The settle step below then buckles it into a bunch along the
     wall base or rock face. That is the "pile up against them".
3. **Loops, figure-eights, heaps.** Per strand and seeded:
   - slack loops of radius up to about 0.8 cell;
   - figure-eights (35% of the loops);
   - a heap (3-5 overlapping loops) with probability 0.35.
   Each is spliced in only where all of its points lie on walkable floor. Otherwise it shrinks by 0.7, up to 5
   times, and is then dropped.
4. **Relaxed-rope settle** (position-based dynamics, 70 iterations):
   - **inextensible segments:** the cable cannot stretch, so excess must go somewhere;
   - **bend smoothing**, which gives a minimum bend radius and no kinks;
   - **hard projection out of unwalkable cells** along the signed-distance gradient;
   - **pins:** both ends (junction ports and plugs, which keeps §8.10's peel slots exact) and any span lying
     on its own wall-top conduit (§8.3's wire-over-wall case is the only crossing).
   - **No self-avoidance**, by design. Real cords cross themselves (see the photo), and per-strand Y order
     already handles the overlap.
5. **Seeded per run** with the edge hashes of §8.2. It is stable across rebuilds and saves, and nothing is saved.

#### 8.11.2 Walkability in game (decompiled 1.6)

- **Cheapest per-cell read:** `map.pathing.Normal.pathGrid.WalkableFast(idx)` (`pathGrid[idx] < 10000`). It
  has no bounds check, so do our own `InBounds`.
- `GenGrid.Walkable(c, map)` also requires `FenceBlocked`. That is two reads, and it treats fences as walls,
  which is optional for us.
- The cost becomes `ImpassableCost` (10000) for impassable terrain (deep water, through
  `TerrainDef.passability`), impassable things (walls, rock, most production buildings), and fences.
- For the rebuild, copy the needed window of the path grid into a small signed-distance field once per
  section. The mock-up uses 10 samples per cell and a chamfer transform.
- **Invalidation.** Subscribe the layer to `Buildings | Terrain`:
  - `Building.SpawnSetup` and `DeSpawn` dirty `Buildings` on their cells;
  - terrain changes dirty `Terrain` on the cell and its neighbours.
  - `PathGrid.RecalculatePerceivedPathCostAt` does not dirty map meshes.
  - Vanilla only dirties the sections of the **8 neighbour cells**. A wall placed 2-3 cells from a run in
    another section would not reach it.
  - So a postfix on `MapDrawer.MapMeshDirty`, or on `Building.SpawnSetup` / `DeSpawn`, must dirty our layer in
    every section within the excursion cap (3 cells). Use `MapMeshDirty(c, flag, regenAdjacentCells: true,
    regenAdjacentSections: true)`, or our own flag over a 3-cell box.
- Walkability changes from **pawns, items and plants do not count**: items and pawns are not impassable, and
  plants are not checked. Wires lie under them as now.

#### 8.11.3 Section edges and culling (the open question)

**No pop-in, if the layer reports its real extent.**
- `MapDrawer.DrawMapMesh` draws a section when `ViewRect` (`CurrentViewRect.ExpandedBy(1)`) overlaps
  `section.Bounds`.
- `Section.Bounds` is the 17×17 rect **encapsulated with every non-dynamic layer's `GetBoundaryRect()`**.
- `MapDrawLayer.RefreshSubMeshBounds` sets the Unity mesh bounds to that rect `ExpandedBy(2)`.
- This is exactly how vanilla `SectionLayer_Things` handles oversized prints: it keeps a `bounds` field
  encapsulating each thing's `OccupiedDrawRect()`.
- So `SectionLayer_RM_MessyWires` accumulates a `CellRect` of every vertex it prints and returns that from
  `GetBoundaryRect()`. A loop reaching 3 cells into the next section keeps its owner section drawn whenever
  the loop is on screen, so it never pops.
- §8.1's old `ExpandedBy(1)` rule is replaced by this. The cost is that a section with far-reaching wires is
  drawn a little more often, which is negligible.
- Do **not** use `SectionLayer_Dynamic`: dynamic layers are excluded from `Section.Bounds`.
- Each run is still printed only by the section owning its first cell. Nothing is printed twice.

#### 8.11.4 Cost and caching

- **Mock-up measurement (Python + numpy, not C#):** 18 strands on a 52-cell scene settle in about 300 ms, or
  17 ms per strand. That is about 7,500 points: ~48 per strand-cell at 0.05-cell spacing, 70 iterations.
- **C# estimate, arithmetic only:**
  - points × iterations × ~60 flops comes to roughly 15-30 ms for that scene;
  - a fully wired 289-cell section is 100-170 ms;
  - with 0.08-cell spacing and 30 iterations it is about 6× less: 15-30 ms per section.
  - That is fine for an occasional rebuild, but **too slow to redo on every dirty**.
- **Cache per run.** Store the settled polylines in a `Dictionary<runKey, Vector2[][]>` on a MapComponent,
  in memory only and never saved. The key hashes:
  - the run's cells;
  - its strand count (§8.10);
  - the seed;
  - the walkability bits of the run's bounding box expanded by the cap.
- A section rebuild re-meshes from cached polylines, which costs the same as phase 1. It re-settles only runs
  whose key changed, typically the one or two next to a new wall.
- Settle off the main thread is possible: it is pure math on copied grids. The cached result is then swapped
  in on the next rebuild. It is not needed at the estimates above.
- A load-change (§8.10) that changes the strand count re-settles only that run.

#### 8.11.5 New risks this adds

| risk | mitigation |
|---|---|
| **Fog leak.** A loop from a visible run sprawls into fogged cells, or a fogged run's loop reaches into view | treat fogged cells as unwalkable for the settle, and add FogOfWar to the cache key |
| **Selection.** A loop 3 cells out is not clickable: the conduit is still its cell | while a conduit is selected, highlight its whole run (§8.3's optional highlight becomes required) |
| **Visual clutter** on dense bases where runs are 1-2 cells apart: loops of neighbouring runs interleave | the messiness slider scales slack and cap. "Tidy" is the old 0.38 cap; the default is the owner level. Optionally treat other runs' conduit cells as soft obstacles |
| **Bundles diverge**: per-strand loops pull a bundle apart | excursions are shared by the bundle and only loops and heaps are per strand. It reads as one bundle with stray loops (mock-up) |
| **Doors**: a heap in a doorway | a door cell is walkable, so loops may pass through it, but they pile against the jambs. Optionally make door cells "no heaps" |
| **Rebuild reach**: a wall 3 cells away does not dirty our section | the 3-cell dirty postfix (§8.11.2) |

#### 8.11.6 Mock-ups

`06_sprawl_jawa.png` and `06_sprawl_extcord.png` show BEFORE (phase-0 routing, 0.38 cap) above AFTER (owner
excursions) on a new scene:
- a rock outcrop and a rock pillar;
- runs one cell off the west and north wall bases, where the slack bunches against the walls;
- a generator run through the doorway, where the excess piles against the outer wall beside the door;
- an open-hall run with big loops and figure-eights;
- an outdoor heap.

The renderer is `src/RimMandrake/Utils/mockups/messy_conduit/sprawl.py`. The selftest asserts that no settled
vertex lands in an unwalkable cell.

