# Messy Conduit — design pass (2026-10-02)

Owner idea, 2026-10-02: *"I normally hate how they make conduit invisible, but now that I think about it,
Jawa should celebrate that. I almost want to make it weirder like snakey, ropey loose conduit on the floor.
Spawn out a design pass to consider how hard it would be to make MESSY CONDUIT, an alternative mod that would
make conduit sprawl all over the floor in loose wirey mess like it does in real life."*

Status: PHASE 1a BUILT 2026-10-02 (owner chat go-ahead; build pause lifted for this mod), item
`MESSY_CONDUIT_MOD_1`. Mod: `src/RimMandrake/MessyConduit` (`mandrake.rm.messyconduit`). The model is the **nodal
cord model** (§8.2): conduit reduced to a node graph, one too-long extension cord per edge planned over the floor,
buried conduit never drawn. What 1a built and where it departs from this design: §8.13.

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
  `RimMandrake.MessyConduit`, prefix `RM_` (`SectionLayer_RM_MessyCords`, `RM_MessyConduitExtension`,
  `RM_MapComponent_CordGraph`).
- It is franchise-free and is a public-use mod.
- Hard dependency: Harmony (one prefix, for hookup wires, §8.1). No DLC dependency needed, though Odyssey's
  substructure rule is honoured by reuse.

**Settings** ("superb Mod Settings"):

| Setting | Effect | Applies |
|---|---|---|
| Master enable | — | restart |
| Slack | spare cord per cord: off (path-tight) / some / **owner level (default: 1.4-2.4x the path, at least 7 and at most 16 cells spare)** / feral; loop, figure-eight and heap chance | live (rebuild cords) |
| Cords per connection | 1, 1-2, **1-3 (default)**; seeded per edge, never by load | live |
| Style family | Cybertek / Extension cord / Star Wars / **Star Wars: Jawa** (campaign default) | live |
| Tangles | dense conduit fields drawn as one heap (on) or as ordinary cords (off); size threshold (default 9 cells) | live |
| Needless conduit as loops | short spurs and 2x2 blocks drawn as pointless loops (on) or as terminals (off) | live |
| Unfinished runs spark | a dead end that is not a needless spur sparks when live (**on**) or wears a taped cap | live |
| Per-def toggles | power conduit, waterproof, "all isPowerConduit defs" | — |
| Sway (lifted spans) / floor ripple | §8.4 | live |
| Break sparks / whip / downed-wire bursts / spark rate / only-with-power-overlay | §8.5 | live |
| Leave the power-overlay lines alone | fixed on; it is a guarantee, not a toggle | — |

Defaults equal the shipped behaviour, and all-off degrades to vanilla.

**First functional script** (`debug_process.md` §2): `src/RimMandrake/MessyConduit/validation.py` plus the
walk `design/validation_walks/RimMandrake/MessyConduit.md`.

`## must be true` lines, each with a cheap state read:
1. The cord graph of the current map exists (`RM_MapComponent_CordGraph`) and its node census matches a
   recount from the conduit grid: every conduit end is a terminal node, every buried run has a stub at each
   place it surfaces. `PowerConduit` renders transparent.
2. **No cord edge joins two nodes in different `PowerNet`s, and no cord crosses a gap**: for every cord edge
   both endpoint cells report the same `TransmittedPowerNetAt` (or the same conduit component when unpowered).
3. `HiddenConduit` stays invisible: its colour alpha is 0 and it is excluded from the graph.
4. The same map yields the same cord polylines after a save/load: hash the laid points per edge before and after.
5. Placing a conduit cell far from a cord does not change that cord's hash (local invalidation, §8.2.7).
6. With the power overlay on, connector lines are still printed (the `SectionLayer_ThingsPowerGrid` sub-mesh
   for `MatConnectorLine` is non-empty). This is a guard against Invisible Conduit's bug.
7. Master toggle off → the layer's `Visible` is false and conduit renders as vanilla.
8. Break readout: destroy one conduit in a powered line; the graph gains 2 terminal nodes, the registry reads
   1 live end. Turn the source off and within 250 ticks it reads dead (§8.5).
9. Removing the mod from a save that used it: the load is clean and `Player.log` shows no errors.

Lines 1, 2, 3, 5 and 7 are offline-selftestable against a synthetic grid (the mock-up selftest already does
1, 2 and 5); 4, 6, 8 and 9 need the bridge. Visual judgement ("does it read as messy") is a screenshot or a
keeper savegame for the owner, never a pass bar.

`## anti-guessing notes`, seeded:
- `RULED OUT: custom graphicClass with linkType None — CanAffectLinker false ⇒ no adjacent-cell regen
  (ThingDef.CanAffectLinker, Thing.cs SpawnSetup)`.
- `RULED OUT: drawSize enlarges linked art — Graphic_Linked.Print hard-codes Vector2(1,1)`.

## 6. Recommendation and build plan

**Recommendation: the nodal cord model (§8.2).** The conduit is vanilla and invisible. A cosmetic layer
reduces the conduit network to a node graph (machines, junctions, terminals, stubs where buried conduit
surfaces, tangles) and draws one too-long extension cord per graph edge, path-planned over walkable floor
between its two nodes. Buried conduit is never drawn. Breaks are terminal nodes that spark when live. Tier A
cannot sprawl past the cell. Tier C (hazards) stays a later, separate opt-in (`MessyConduit.Hazards`), if ever.

Phase 1a is built (§8.13); 1b onward follows §8.10.

**Build order, phases, effort and the art list:** §8.10 and §8.11.

**Artpipe.**
- Run `artpipe_state.py find` first. It was run this pass: no conduit, cable or wire art exists, and the 9
  "conduit" hits are only description mentions in other jobs.
- Then queue through `fill_queue.py` with `style_notes` naming the painterly lawset, top-lit, seamless
  horizontal tiling, transparent background, and the palette in §4.
- Strips must tile. Validate offline by tiling ×4 and checking the seam columns, plus a real-alpha check
  (`generating-rimworld-sprites` validator).
- Small textures. Expected cost is one batch.

## 7. Open questions for the owner

1. **Machine hookup cords:** the nodal model already runs a cord into each machine. Does it plug in with a
   visible plug (current mock-up) or vanish into the casing?
2. **Looks only, or later some danger?** Trip hazard, sparks in rain, vermin chewing cable, a tidy-up job.
   This is a separate later add-on; say no and it never gets built.
3. **Waterproof conduit:** messy too, or left clean as the "proper" option?
4. **Should vanilla's own Hidden Conduit stay invisible**, so players keep a tidy choice, or should
   everything be messy?
5. **Unfinished runs:** should every live dead end spark (current default, his 2026-10-02 rule), or only
   ends at a real gap, with deliberate ends taped?

## 8. The overlay model and the nodal cords (owner, 2026-10-02)

Owner, verbatim (the overlay idea): *"I had wondered if we could actually have little drawn wires decoratively
put over otherwise-invisible-conduits as usual. So the visible wires would only be aesthetic. In theory then the
drawer could be very smart and have them bend around corners and do other multi-cell-physics things to look
even more realistic, depending on how difficult that is. Swaying in the wind would be amazing, or looping
around tree trunks or poles. Things like that. Assess that as even realistic or possible, given that art can be
anything. We certainly wouldn't want annoying clipping issues."*

Owner, verbatim (the nodal ruling, after approving `06_sprawl_jawa.png` as the look): *"I agree. The
06_sprawl_jawa.png is definitely the look I was going for. Any cheaper ways to get there? Ignore the load
calculations, the cables shouldn't change as the power flux changes. It's just about cords roughly connecting
to/from where they belong. Honestly they don't even need to go over where the conduit is... it's really the
nodal map of sources, destinations, places where they go into walls, places where they emerge, and then
corners that they must traverse. So maybe it could be better served as a path-planning problem between nearest
connected neighbors with conduit under walls being a special case. Perhaps we don't need to show it "over the
wall" after all, we just say "it's in there" and show where it comes out/goes in. How's that as an improvement
for doability? But do let's aim for that extra loopy slack look. I'm not going for taught cables. Quite the
opposite. Everything is a too-long extension cord."*

Owner, verbatim (edge cases, same day): *"Yes, conduit that suddenly ends has a "node" at its terminal point
that must be reached by a "broken" cord lying on the ground. Sparking if live, dead if not. We'd need to think
what it looks like when a cord ends in a wall suddenly (probably hangs sparking out of the wall, not a
continuous shining arc, but a pulsing, flashing, spark-dripping pattern like a real downed power line). How
about when the conduit "goes under" a large impassable area? (hopefully it "goes into" the device somehow)
Flesh out other tricky configurations to think through. How to handle a "grid of conduit beneath the ground"
(ideally a huge tangle of nasty wires and power strips all swirled together terribly). A needless conduit square
along a linear strip (a pointless loop in the wire on the ground perhaps). Things like that."*

Standing requirements carried from the first round:
1. **Break detection as a readout.** The end still on a powered net sparks and whips; the dead end lies limp.
   The point is finding breaks at a glance (§8.5).
2. **Aesthetic:** deliberately ugly, "truck drivers in space", very Jawa (§8.11).

The conduit def stays functionally vanilla and is made invisible (the Invisible Conduit texture swap, plus the
hookup-wire suppression). All the looks come from a separate cosmetic layer that reads the conduit grid and
owns its own geometry.

### 8.0 Verdicts

| # | question | verdict | one line |
|---|---|---|---|
| 1 | Overlay hook | **EASY** | A `SectionLayer` subclass is instantiated by the engine for every section automatically. It needs no Harmony and is rebuilt on existing dirty flags. |
| 2 | Node reduction | **EASY-MODERATE** | One flood over conduit cells plus a degree-2 collapse; the special cases (§8.7) are local rules. |
| 3 | Cord planning | **MODERATE** | A* over the path grid between two nodes, string-pulled, then the rope settle of §8.6. Pure math on copied grids. |
| 4 | Buried conduit ("it's in there") | **EASY** | Nothing is drawn on walls, rock, water or buildings; a stub decal where conduit surfaces. The wall-top rendering and its occlusion problems are gone. |
| 5 | Sway | **EASY if the vanilla plant shader behaves as inferred, else HARD** | `CutoutPlant` already sways any mesh by vertex alpha, driven by the map's wind, with no per-frame CPU cost. |
| 6 | Break sparking + downed wire | **EASY to MODERATE** | Terminals come out of the reduction; poll live/dead every 250 ticks; vanilla spark flecks; only a few live ends animate per frame. |
| 7 | Clipping | **EASY-MODERATE** | Cords only ever lie on walkable floor at one altitude; the remaining risks are listed in §8.8. |
| — | Overhead spans between poles | **NOT ADVISABLE** | Wires floating over everything cannot be occluded correctly in a top-down sprite game. |

### 8.1 Where the drawer hooks

**Options compared** (engine facts from RimSage, decompiled 1.6):

| hook | how it draws | cost | verdict |
|---|---|---|---|
| **custom `SectionLayer` subclass** | `Section`'s constructor does `foreach (Type t in typeof(SectionLayer).AllSubclassesNonAbstract()) Activator.CreateInstance(t, this)`, so **any mod's subclass is created for every 17×17 section of every map**. `MapDrawLayer.DrawLayer` then calls `Graphics.DrawMesh` per sub-mesh. `MapDrawer.DrawMapMesh` draws a section only when `view.Overlaps(section.Bounds)` | zero per frame (static mesh); rebuild only when dirty | **chosen** for the cords |
| `MapComponent.MapComponentUpdate` + `Graphics.DrawMesh` with our own cached meshes | we reimplement sections, dirtying and culling | the same GPU cost plus our own bookkeeping | only for the few **animated** pieces (live ends, downed-wire bursts, §8.5) |
| `DynamicDrawManager` / `drawerType RealtimeOnly` | per-thing `DrawAt` every frame | O(conduits) each frame | rejected |
| Harmony on `Graphic_LinkedTransmitter.Print` (Tier B) | inside the conduit's own print | zero per frame | rejected: it cannot see neighbours or obstacles |
| `MapComponentOnGUI` | screen-space IMGUI | — | wrong space; never |

**Who owns what.** A `RM_MapComponent_CordGraph` (runtime only, no `ExposeData`) holds the node graph, the
planned and laid polylines per edge, and the dirty set. Each `SectionLayer_RM_MessyCords` prints the cords
**owned** by its section: a cord is owned by the section holding the lower-index endpoint of its edge, so every
cord is printed exactly once.

**Rebuild triggers** use existing flags. The layer sets `relevantChangeTypes = Buildings | PowerGrid | FogOfWar |
Terrain | RM_MessyCords` (our own `MapMeshFlagDef`). `Things` is left out on purpose: it fires on every haul, and
each of our regenerates snapshots the map.
- **Conduit placed or removed:** the conduit keeps `linkType Transmitter`, so it still satisfies
  `def.CanAffectLinker`, and `Thing.SpawnSetup` and `DeSpawn` call `MapMeshDirty(Position, Things,
  regenAdjacentCells: true)`.
- **Net change:** `PowerNetManager.NotifyDrawersForWireUpdate` dirties `Things` and `PowerGrid`.
- **Buildings, walls, doors:** `Building.SpawnSetup` dirties `Buildings` on every occupied cell.
- **Terrain** (water, bridges): dirties `Terrain` on the cell and neighbours.
- **Trees:** dirty only `Things`, which the layer ignores; a tree change reaches a cord's plan only when that
  cord is re-planned for another reason (its corridor hash also covers walkability, not trees).
- **Fog:** `FogGrid` dirties `FogOfWar|Things`.
- 🔑 A section rebuild does **not** re-plan everything: it asks the map component for the cords it owns, and
  the component re-plans only edges in its dirty set (§8.2.7). An unchanged cord re-emits its cached polyline.
- Vanilla dirties only the 8 neighbour cells' sections. A cord can run several sections away from the change
  that affects it (a new wall across its path), so the component marks dirty **edges**, then calls
  `MapMeshDirty` on the owning section of each dirty edge itself.

**How it reads the network.** All of these are O(1) per cell from existing grids:
- `map.linkGrid.LinkFlagsAt(c) & LinkFlags.PowerConduit` tells whether a cell is conduit.
- `map.thingGrid` gives the def at that cell, used to exclude `HiddenConduit` and untagged defs.
- `map.powerNetGrid.TransmittedPowerNetAt(c)` gives the net, for live/dead state and for the "same net" guard.
- `CompPower.connectParent` and `connectChildren` give the machine hookups (machines up to
  `PowerConnectionMaker.ConnectMaxDist` = 6 cells from their conduit).
- `map.pathing.Normal.pathGrid.WalkableFast(idx)` gives walkability for planning (§8.6).
- The Odyssey substructure rule (`Graphic_Linked.ShouldLinkWith`) is NOT applied by the reduction: power flows
  across a hull edge, so splitting the graph there would put two sparking "break" ends at every gravship hull
  (§8.13).

**Culling.** `SectionLayer_RM_MessyCords` accumulates a `CellRect` of every vertex it prints and returns it
from `GetBoundaryRect()`, exactly as `SectionLayer_Things` does for oversized prints. `Section.Bounds`
encapsulates every non-dynamic layer's boundary rect, so a cord reaching far out of its owning section keeps
that section drawn whenever any of the cord is on screen. Do **not** use `SectionLayer_Dynamic`: dynamic layers
are excluded from `Section.Bounds`.

**Save compatibility and removal.**
- Nothing is saved: no comp, no MapComponent data and no def that a save references. The whole graph and every
  polyline is rebuilt from the conduit grid on load, and the seeds (§8.2.5) make it identical.
- Removing the mod drops the layer class. The conduit def's texture swap reverts with it, so conduit becomes
  visible vanilla conduit again.
- A setting turns the whole layer off: `Visible => settings.enabled`.

**Hookup wires** (machine to conduit).
- Vanilla prints these in `CompPower.PostPrintOnto` through
  `PowerNetGraphics.PrintWirePieceConnecting(..., forPowerOverlay:false)`. It already skips them for
  `ThingDefOf.HiddenConduit` by def identity.
- For our invisible conduit we need **one Harmony prefix** on `PrintWirePieceConnecting` that returns false
  only when `!forPowerOverlay` and the connect parent is one of our tagged defs. The machine is then a node of
  the graph and its cord is planned like any other (§8.2.6).
- The overlay's blue connector line stays intact, which avoids Invisible Conduit's bug (§2).

### 8.2 The nodal cord model

**The idea in one line.** Conduit cells only decide *which things are connected to which*; cords are drawn
between those things over the floor, too long, and never on top of walls.

#### 8.2.1 Node types

| node | what it is in the conduit | where its cord end sits | look |
|---|---|---|---|
| **power source** | a machine with a `CompPowerPlant` (generator, solar, geothermal, wind) whose `connectParent` is a conduit | just outside the machine footprint, on the side nearest its connect cell | the cord plugs into the casing (plug decal) |
| **consumer** | a machine with a `CompPowerTrader` | same | plug |
| **battery** | a `CompPowerBattery` building | same | plug |
| **switch** | `Building_PowerSwitch` (a transmitter building) | on its footprint edge, one end per side | plug on each side; an off switch splits the net (two nets, no break) |
| **junction** | a conduit cell with 3 or 4 conduit neighbours, or a conduit cell where a machine taps a straight run | the cell centre plus a seeded jitter | tape lump / ration tin / power strip / hex pod (per style) |
| **terminal** | a conduit cell with one neighbour that is not a needless spur (§8.7.5) | the cell centre pushed 0.36 cell out of the open side | the cord lies broken: live = whip + sparks, dead = limp (§8.5) |
| **stub** | the boundary between a walkable conduit cell and a **buried** conduit cell (under a wall, natural rock, deep water, or an impassable building) | the face between the two cells | a grommet in a built wall, a drilled hole in rock, ripples on water, a power strip at a building's base (§8.7.3) |
| **wall terminal** | a stub whose buried run ends inside the wall/rock and not at the map edge | the face | the cord hangs out of a scorched hole: downed-wire bursts if live (§8.7.2) |
| **tangle** | a dense conduit field (§8.7.4) | one exit point per cord, on the field cell the exit leaves from | a heap of cords and power strips |
| **lamp / post** | a lamp's connect cell | the lamp base | the cord climbs the post (taped) |

**Waypoints** are not nodes; they are produced by the planner and belong to one cord:
- **corner waypoints** where a string-pulled path bends round an obstacle;
- **doorway waypoints**: a door cell on the path; the cord is pinned through the doorway (no loops in it);
- **knot waypoints**: needless conduit on the cord's own chain (§8.7.5); the cord gets a pointless loop there;
- **via waypoints**: the midpoint of a ring edge's own chain, so two cords between the same nodes go round
  their own sides (§8.7.6).

#### 8.2.2 Reduction: from conduit cells to nodes and edges

1. **Classify cells.** `buried` = conduit cells that are not walkable (`!WalkableFast`), i.e. under a wall,
   rock, deep water or an impassable building. The rest are floor conduit.
2. **Dense fields** (§8.7.4): find components of dense floor conduit; a component of ≥ 9 cells becomes one
   **tangle** vertex, a smaller one containing a 2x2 block becomes a **blob** vertex.
3. **Vertices and links.** Floor conduit cell, buried cell, tangle, blob and machine are vertices. Orthogonal
   conduit neighbours link. A link between a floor cell and a buried cell is split by a **stub** vertex. A
   machine links to its connect cell.
4. **Keep** machines, stubs and tangles, and any cell/buried/blob vertex whose degree is not 2. Walk every chain
   of degree-2 vertices between kept vertices into one **edge**. An edge whose chain contains a buried cell is
   **hidden** (never drawn); every other edge is a **cord edge**.
5. **Prune needless spurs** (§8.7.5): a dead end of ≤ 2 cells off a junction that does not face a gap is
   removed; if that leaves the junction as a plain pass-through, its two edges merge into one cord edge with a
   knot waypoint where the junction was.
6. **Classify** the kept vertices into the node types of §8.2.1. A buried end that is not at the map edge turns
   the stub leading to it into a wall terminal.

🔑 **Cords exist only between truly connected nodes.** Every cord edge *is* a chain of 4-adjacent conduit
cells, so its two endpoints are always in the same conduit component, and in the same `PowerNet` (a net is the
4-neighbour flood of transmitters, `PowerNetMaker`). A missing conduit cell splits the chain: each side ends in
a terminal node, so a gap always yields **two dangling ends and never a cord across it**. Selftested in the
mock-up (`selftest.py`: "cords only between connected nodes", "no cord across the gap"), and line 2 of the
north-star script re-checks it against the live `PowerNet`s.

Cost: one pass over conduit cells plus one walk per chain, O(cells). It is redone per **net** when that net
changes, not per map.

#### 8.2.3 Planning one cord

1. **A*** on the walkable grid (8-connected, no corner cutting past an unwalkable cell) from the cell of one
   endpoint to the cell of the other. Tree and post cells cost a little more, so cords prefer to go round them.
   Mandatory stops (knot and via waypoints) split the search into legs.
2. **String-pull** each leg: from the current point keep the furthest path point that is in clear line of
   sight (clearance 0.2 cell from any unwalkable cell), never skipping a door cell. The surviving points are the
   corner and doorway waypoints.
3. **Round corners** (corner cut + centripetal Catmull-Rom, which never overshoots).

The path does **not** follow the conduit cells. Conduit under a room can be laid in a straight trunk while its
cord wanders across the floor in a different route; the owner ruled this fine ("they don't even need to go
over where the conduit is").

If A* finds no path (the endpoints are in walkable regions that do not connect, e.g. a stub opening into a
sealed rock pocket), the cord is drawn as a short stub at each end and the edge is flagged `unroutable` (debug
view only).

#### 8.2.4 Laying the slack: "everything is a too-long extension cord"

The laid cord is the rope settle of §8.6 applied to the planned path:
- **Length:** extra cord = `clamp(slack × path, 7, 16)` cells, with `slack` seeded per cord in 1.4-2.4. A
  short cord therefore lies at about 2-3x its path (one heap's worth even on a 1-cell hop); a 60-cell run carries
  at most 16 extra cells (about 1.25x) and reads as a long cord with a few loose bunches, not 120 cells of
  coil. Measured on the mock-up scene: 13 cords at 1.2-3.7x, median 2.6x.
- **Shape:** broad excursions shared by the cords of one edge, slack loops (0.35 per cell), figure-eights, a
  heap with probability 0.8, each spliced in only where it lies on walkable floor and fits the length budget
  (a loop that does not fit shrinks, then is dropped).
- **Settle:** inextensible segments, bend smoothing, hard projection out of unwalkable cells and out of round
  trunk/post obstacles, so excess piles against walls, rock, trees and posts. Ends and doorways are pinned.
- **Cords per edge:** 1-3, seeded per edge. Fixed: the count never changes with power flow.
- **No self-avoidance and no cord-cord avoidance.** Cords may cross themselves and each other, as real cords
  do; a per-cord altitude increment (a fraction of `AltInc`) orders them without z-fighting. Cords may **not**
  enter an unwalkable cell (asserted by the selftest on every scene).

#### 8.2.5 Determinism

- Every random choice comes from a local hash PRNG (never `Rand`), seeded from **the two endpoint cells of the
  edge plus their node types** (and the index among parallel edges).
- So an unrelated edit never reshuffles a cord: placing a machine across the map leaves every other cord's
  polyline bit-identical (selftested). Only cords whose endpoints, chain or planned corridor changed are re-laid.
- Stable across frames, reloads and saves; nothing is stored.

#### 8.2.6 Machines, doorways, crossings

- **Hookups:** a machine is a node; its cord is planned from its footprint edge to the next node like any
  other cord. A machine whose connect cell is the end of a run collapses into that run (one cord from the
  machine to the next junction). A machine tapping the middle of a run makes that cell a junction.
- **Machines connected from up to 6 cells away** (`ConnectMaxDist`) without conduit between: the cord simply
  runs that distance over the floor. That is the vanilla hookup wire, now a too-long cord.
- **Doorways:** a door cell is walkable, so cords pass through it on the floor. The doorway is a pinned
  waypoint: no loops or heaps in the doorway, and the closed door leaves (`DoorMoveable`) cover the cord at the
  threshold. Conduit *under* a door is just floor conduit.
- **Crossings:** cords may overlap and cross each other and themselves. They never cross an unwalkable cell:
  there they stop at a stub.
- **Fences** (`FenceBlocked`) are walkable for cords: cords pass under fences.

#### 8.2.7 What a change invalidates

| change | invalidates |
|---|---|
| conduit cell placed/removed/destroyed | the net's reduction; then only edges whose chain or endpoints changed (compare by endpoint key + chain hash) are re-planned |
| machine connected/disconnected | its one edge (and the merge/split of the run it taps) |
| wall, rock, building, door placed/removed (walkability change) | edges whose **planned corridor** (path bounding box expanded by 3 cells) contains the cell; their laid polylines |
| water/terrain change | same as a walkability change |
| tree grows/falls, lamp placed | edges whose corridor contains it (trunks and posts are obstacles) |
| fog revealed | edges touching the cell (fogged cells are treated as unwalkable and hide their cords, §8.3) |
| live/dead flip (night solar, empty battery, EMP) | **nothing geometric**: only the terminal registry (§8.5) |
| power flux | nothing. Cords never change with load (owner ruling) |

The map component keeps `Dictionary<edgeKey, CordCache>` (planned path, laid polylines, corridor rect) in
memory only. Dirty edges are re-planned lazily when their owning section next draws, so off-screen changes cost
nothing until seen.

### 8.3 Layering, obstacles and walls

**The relevant altitude layers** (`Verse.AltitudeLayer`). `Altitudes.AltitudeFor` = index × 0.3659, so a
higher Y draws over a lower one. `AltInc` = 0.0366, which gives 10 sub-steps per layer.

| idx | layer | y | relation to cords |
|---|---|---|---|
| 2 | Terrain | 0.73 | the floor; **snow is drawn here too** (`SectionLayer_Snow`), so snow is under the cords |
| 4 | Floor | 1.46 | |
| **5** | **Conduits** | **1.83** | **floor cords live here**, like vanilla conduit |
| 6 | FloorCoverings | 2.20 | rugs over the cords (reads right) |
| 8 | Filth | 2.93 | filth over the cords (grease and dirt on cable reads right) |
| 10 | SmallWire | 3.66 | vanilla hookup wires (suppressed for our defs) |
| 11 | LowPlant | 4.02 | grass over the floor cords |
| 13 | Shadows | 4.76 | sun and edge shadows |
| 14 | DoorMoveable | 5.12 | door leaves cover cords at the threshold |
| **15** | **Building** | **5.49** | walls, trees, lamps, furniture; stub decals print here at the wall face + ε |
| 18 | Item | 6.59 | items always over the cords |
| 20/23 | LayingPawn / Pawn | 7.3 / 8.4 | **pawns always walk over the cords** |
| 34 | FogOfWar | 12.4 | fog covers everything |
| 38 | MapDataOverlay | 13.9 | the power overlay. We never draw here |

- **Everything a cord does happens on the floor at Conduits height.** Nothing is drawn on top of a wall, so the
  matched-Y wall-top rendering, wall drapes and wall-corner-filler fights of the per-cell model are gone.
- **Stubs** are the only pieces at Building height: a decal on the wall/rock face, printed after the wall.
- **Trees and posts** are round obstacles in the settle (trunk base ≈ (x+0.5, z+0.1), radius ~0.17; posts
  ~0.1). Cords pile against them. **Trunk wraps** (a loop round a trunk with a matched-Y front half; `Plant.Print`
  tilts its plane +0.1, so the front half must sit at the tree plane's own Y at that z + ε, never a fixed higher
  layer) stay an optional phase-3 decoration.
- **Lamps:** a powered lamp is a node; its cord climbs the post with a tape decal (matched-Y front, same rule).
- **Multi-cell furniture over floor conduit:** furniture is walkable or not per the path grid; an impassable
  one buries the conduit under it (stubs, §8.7.3), a passable one (tables, beds) lets cords lie under it,
  showing through the gaps.
- **Fog:** fogged cells are unwalkable for planning and their nodes are not drawn, so a cord never reveals
  hidden conduit or wanders into fog. FogOfWar is in the rebuild mask.
- **Roofs:** RimWorld does not draw roofs over the map; roofed cells only zero the sway (§8.4).
- **Overhead spans** pole-to-pole are **NOT ADVISABLE**: a span floating above the floor has no correct
  occlusion against walls and furniture between the poles in a top-down sprite game.

**Mouse-over and selection.** Cords are not Things. Selection, tooltips and deconstruction still go through
the invisible conduit's cell. Because a cord may lie far from its conduit, while a conduit is selected the
component redraws every cord of that cell's net-component edges in a highlight material (from
`MapComponentUpdate`), so players see what they clicked. Required, not optional.

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

**So the cheapest cord sway is free.**
- Build the strand material with `ShaderDatabase.CutoutPlant` and give it the strand texture. It joins the
  wind list automatically.
- Write **vertex alpha** as the sway weight per vertex: 0 where a cord lies on the floor, is taped or pinned;
  rising toward the middle of any lifted span (lamp climbs, cords hanging out of a wall face, trunk-wrap loops);
  **0 under a roof**.
- Write the UV z as a per-cord phase.
- What this gives: wind-speed-driven sway that respects the game's own "plant sway" preference; storms sway
  harder; zero CPU per frame on any base size.
- **What to sway:** cord lying on a floor does not sway. Sway the lifted bits. Optionally a faint ripple on
  outdoor floor cords, behind a setting.
- **Caveat:** the shader is a compiled asset. Its displacement formula (the axis, and how it uses vertex alpha
  and UV z) is **not in the decompiled C#**, and is inferred from how `Plant.Print` feeds it. If it displaces
  only along world x, keep amplitudes small. `CutoutPlant` also carries fall-colour parameters; we do not set
  `_FallBehaviorEnabled`, so it should stay off. UNVERIFIED.

**Fallbacks if the plant shader misbehaves.**
- **Our own vertex shader in an AssetBundle:** HARD. It is a new toolchain for us and needs the Unity version
  matched to the game.
- **CPU mesh deformation per frame for lifted spans only**, from `MapComponentUpdate`: MODERATE. Even a big base
  has perhaps 50-200 lifted spans of about 40 verts each.

**Level of detail.** Sections are culled by the engine (`DrawMapMesh`). For LOD, emit a second sub-mesh per
material with cords decimated to 1 strand and no decals, and switch by `Find.CameraDriver.CurrentZoom`
(`LayerSubMesh.disabled`). At far zoom thin strands alias into shimmer.

### 8.5 Break readout: terminals spark, dead ends lie limp

**A break is a terminal node.** The reduction (§8.2.2) turns every conduit end into a terminal, except a
needless spur (§8.7.5). The cord to a terminal lies broken on the ground; its last ~0.4 cell is the **tail**.
- **A conduit destroyed** (fire, explosion, raid): two terminals face a 1-cell gap. Vanilla
  `ThingUtility.CheckAutoRebuildOnDestroyed` leaves a `Blueprint_Build`/`Frame` in the gap; the terminals stay
  until the conduit is rebuilt.
- **Deconstructed or never finished:** a terminal at the end of the run. It sparks when live (owner rule; the
  "Unfinished runs spark" setting can tape them instead).
- **A transmitter building removed** from the middle of a run (a battery): terminals across its old footprint.
- **Wall or building removed over conduit:** no break. Buried conduit was continuous all along; the two stubs
  simply become ordinary floor conduit and the cord re-plans.
- **A run that ends inside a wall or rock** is a wall terminal (§8.7.2).

**Live or dead per terminal.**
- `powerNetGrid.TransmittedPowerNetAt(cell)` returns the terminal's net.
- **live** = `net.HasActivePowerSource` (a battery with `StoredEnergy > 0` that is not EMP-stunned, or a trader
  with `PowerOutput > 0`).
- 🔴 **Live/dead flips without any mesh-dirty event** (solar at night, batteries draining, an EMP). So:
  - the map component keeps a terminal registry (runtime only, no `ExposeData`);
  - every **250 ticks** it re-evaluates live/dead once per distinct net;
  - a flip **does not** rebuild any mesh. The cord body is static; the tail is not in the static mesh, the
    component draws it.
- **Live floor terminal:** the tail whips (a cached ribbon bent by a sum of sines plus random snaps, keyed to
  **real time**, so a broken line is findable **while paused**); every 40-120 ticks
  `FleckMaker.ThrowMicroSparks(tip, map)` plus an occasional `ThrowLightningGlow(tip, map, 0.4)`. A lightning
  arc is drawn only between two live tips across the same gap (≤ 1.5 cells apart). Vanilla flecks, no new art;
  `ShouldSpawnMotesAt` culls off-screen positions. Cost O(visible live ends).
- **Dead terminal:** a static limp, slightly curled tail with a dull frayed-copper decal. No motion, no light.
- **Brownout or power off:** a net with no active source reads **dead** everywhere: no current, no sparks. An
  off power switch splits the net at a building; that is two nets, not a break.
- Settings: break sparks on/off, whip on/off, downed-wire bursts on/off, spark rate, "only when the power
  overlay is open".

**Gameplay clarity.** The whole readout is cosmetic: no danger, damage or fire (Tier C stays separate). The
flecks are bright, so a break is seen at a glance from across the map at normal zoom.

### 8.6 Slack laying: walkability-aware loops and the rope settle

Owner, verbatim, with a photo of an orange extension cord lying in big loose loops, figure-eights and a heap
on a dirt floor (`Transient/messy_conduit_mockups_20261002/00_owner_reference_orange_cord.png`): *"Yes, I want
it to have much larger excursions that avoid unwalkable areas or even pile up against them. I think you know
what I'm wanting."* `06_sprawl_jawa.png` (AFTER panel) is the owner-approved look; the nodal model lays every
cord with this machinery (implemented in `rope.py`, called from `nodal.py`).

1. **Slack.** Each cord gets more cable than its path needs, budgeted per §8.2.4.
2. **Excursions.** Broad lateral bumps, 1.2-2.6 cells long, shared by the cords of one edge so they travel
   together. Their side is biased toward open floor (30% go toward the obstacle side, which makes the cord pile
   up against it). An excursion is clipped to the open floor in its direction; the clipped excess is kept as
   length and buckles into a bunch along the wall base or rock face.
3. **Loops, figure-eights, heaps**, seeded per cord, spliced in only where every point lies on walkable floor
   and within the length budget; otherwise shrunk by 0.7 up to 5 times, then dropped.
4. **Relaxed-rope settle** (position-based dynamics, 70 iterations): inextensible segments; bend smoothing;
   hard projection out of unwalkable cells and round trunk/post obstacles along the signed-distance gradient;
   pins at both ends and through doorways. No self-avoidance, by design.

**Walkability in game** (decompiled 1.6):
- Cheapest read: `map.pathing.Normal.pathGrid.WalkableFast(idx)` (`pathGrid[idx] < 10000`); no bounds check, so
  do our own `InBounds`. The cost becomes `ImpassableCost` (10000) for impassable terrain (deep water,
  `TerrainDef.passability`), impassable things (walls, rock, most production buildings) and fences;
  `GenGrid.Walkable` additionally reads `FenceBlocked`, which we ignore (cords pass under fences).
- For a re-plan, copy the corridor window of the path grid into a small signed-distance field (the mock-up
  uses 10 samples per cell and a chamfer transform).
- Walkability changes from pawns, items and plants do not count: items and pawns are not impassable, and
  plants are not checked. Cords lie under them.

**Cost** (mock-up measurement, Python + numpy, not C#): the 07 scene's 13 cord edges, 18 cords, 4,055 laid
points, reduce + plan + lay in **0.23 s**; the per-cell overlay on the same conduit took 0.35 s for 25 strands
and 8,178 points. C# estimate (arithmetic only): points × iterations × ~60 flops ≈ 5-15 ms for that scene,
once, then cached per edge. A re-plan touches only dirty edges.

### 8.7 Tricky configurations

Rules 8.7.1-8.7.5 and the ring rule of 8.7.6 are implemented in the mock-up's reduction and planner, so
`Transient/messy_conduit_mockups_20261002/08_tricky_*.png` comes out of the same code path as the main scene,
and `selftest.py` asserts the census of each. The stub-merging rule of 8.7.3, the long-run heaps and the rest
of 8.7.6 are design only.

#### 8.7.1 Terminal node (any conduit end)

- **DETECT:** a floor conduit cell with one conduit neighbour (graph degree 1) that is not a needless spur. A
  gap is two such cells facing each other across 1-3 non-conduit cells.
- **TREAT:** a node at the cell, pushed 0.36 cell toward the open side. Its cord is planned like any other.
- **LOOK:** the cord lies broken on the ground; live = the tail whips and sparks; dead = limp, dull copper
  (`07_nodal_breaks_jawa.png`, `08_tricky_downed_wire.png`).
- **COST:** none beyond the reduction; the registry poll is per net every 250 ticks.
- **RISK:** a base with many unfinished runs sparks a lot. Mitigation: per-map cap on concurrently sparking
  ends; the "Unfinished runs spark" setting.

#### 8.7.2 Cord ending inside a wall (downed wire)

- **DETECT:** a hidden edge from a stub ends at a buried vertex of degree 1 that is not at the map edge.
- **TREAT:** the stub becomes a wall terminal; live/dead from the walk cell's net.
- **LOOK:** a scorched, ragged hole with soot; the cord goes in and its broken end **hangs out of the hole**,
  drooping down the face. Live: a pulsing, flashing, spark-**dripping** pattern like a downed power line, never
  a steady arc: irregular cycles of drip (sparks fall down the face and bounce on the floor), flash (a burst,
  the wall face lights up), quiet (an ember) and crackle. Driven by real time with a per-terminal seeded random
  schedule (exponential gaps 0.3-2.5 s), vanilla `MicroSparks` for the drips and `LightningGlow` for the flash.
  Dead: hangs still (`08_tricky_downed_wire.png`, 4 frames + dead).
- **COST:** O(visible live wall terminals) per frame, a few flecks each.
- **RISK:** the face decal on a wall's north/east/west side is less visible (top-down view sees the south face).
  The hole sits on the visible south face strip when the wall is north of the floor cell, else at the cell
  line; the drip direction is always screen-down.

#### 8.7.3 Conduit under a large impassable area

- **DETECT:** buried cells are any unwalkable conduit cells; the stub's type comes from what buries the cell:
  natural rock, deep water (terrain passability), a built wall, or an impassable building footprint.
- **TREAT:** the buried run is a hidden edge (any length; nothing drawn). The stubs are exactly where the
  conduit surfaces: entry and exit points are chosen by the conduit itself, never invented. Several stubs of
  one buried run that surface on the same floor chain within 2 cells are merged into one (no "comb" of holes
  along a wall that conduit runs beside).
  - **powered building on its own conduit** (the building's `connectParent` is one of the buried cells):
    the cord **goes into the device**: a power strip at the building's base with the cord plugged in.
  - **unpowered impassable building** (a sculpture, a ship part): a grommet at its base, as for a wall.
  - **rock**: a drilled cable hole with chipped rim. **Wall**: a grommet plate. **Deep water**: the cord dives
    in under ripples.
- **LOOK:** `08_tricky_under_mountain.png` (rock mass, lake, 3x3 machine; render + graph).
- **COST:** cheaper than floor conduit: a buried run of any length is one hidden edge and two decals.
- **RISK:** a stub that opens into a sealed pocket has nowhere to route (flagged `unroutable`, short stubs only).
  Long buried runs show nothing between their ends; the vanilla power overlay still shows the cells.

#### 8.7.4 A grid of conduit under the floor (tangle)

- **DETECT:** dense floor conduit = cells in a full 2x2 block, or with ≥ 6 conduit cells in their 3x3 window;
  closed over lattice crossings (≥ 2 dense 4-neighbours) and over the conduit inside the field's bounding box.
  A dense component of **≥ 9 cells** is a tangle.
- **TREAT:** the whole field is **one node**. Every conduit link from the field to outside conduit, and every
  machine hooked into it, is one exit edge whose cord starts on the field cell it leaves from.
- **LOOK:** a huge swirled heap of cords over the field's cells (4 + cells/3 cords, max 14, heaped and settled),
  with power strips (1 per 7 cells) lying on top, LEDs lit when the field's net is live
  (`08_tricky_grid_tangle.png`: live, generator off, and the graph).
- **Brownout:** strips go dark, no sparks. **A break inside the field** splits it into two components, so it
  becomes two tangles (or a tangle plus terminals), each reading its own net; terminals facing the seam spark as
  usual. An off power switch inside a field is the same.
- **COST:** the lattice in the mock-up is 40 cells: **45 cord edges** without the rule, **4 exit cords + 1
  heap** with it. The heap is laid once per field change.
- **RISK:** a legitimately dense but tidy layout (two parallel runs touching) reads as a tangle. The 9-cell
  threshold and the setting cover it; parallel touching runs only form 2-wide strips, which pass the 2x2 test,
  so the threshold matters.

#### 8.7.5 Needless conduit

- **DETECT:** (a) a dead-end spur of **≤ 2 cells** off a junction that is not a machine's connect cell and does
  not face another conduit cell within 3 cells (that would be a gap); (b) a dense component under the tangle
  threshold that contains a 2x2 block (a "blob"); (c) a zigzag of degree-2 cells.
- **TREAT:** (a) the spur is pruned; if its junction is left as a pass-through, the two edges merge and the cord
  gets a **knot waypoint** there; if the junction still branches, it gets a pointless spare coil. (b) a blob of
  degree 2 is a knot waypoint on the cord through it; of degree ≥ 3 it is a junction with a spare coil. (c)
  nothing: degree-2 cells collapse anyway.
- **LOOK:** a pointless loop or figure-eight in the cord at the knot, taped (`08_tricky_needless_loop.png`).
- **The rule that separates a harmless spur from a true break:** length > 2 cells, or facing a gap, or ending at
  a buried end → terminal; otherwise needless. The mock-up's 4-cell spur stays a sparking terminal.
- **COST:** one pass after the reduction. **RISK:** a player's deliberate 1-2 cell stub (to be extended later)
  shows as a loop rather than a spark. That is the intended reading; the setting can turn it off.

#### 8.7.6 Other configurations

| configuration | DETECT | TREAT / LOOK | RISK |
|---|---|---|---|
| **4+-way junctions** | conduit degree 4 | one junction node, X decal (ration tin / greeble / hex pod / power strip) | none |
| **rings and cycles** | two edges between the same node pair, or an edge from a node to itself | each cord is forced through a **via** waypoint at the midpoint of its own chain, so the two cords go round their own sides (mock-up: the ring in `08_tricky_needless_loop.png`) | a long ring whose chain hugs walls on both sides: both cords may still end up near each other; harmless |
| **batteries** | `CompPowerBattery` | an ordinary node with a plug; a full or empty battery changes nothing visual except live/dead of its net | none |
| **power switches** | `Building_PowerSwitch` | a node with one cord per side; off = two nets, both sides read their own live/dead; never a break | none |
| **transformers / modded relays** | any transmitter building with a `CompPower` | treated like a switch: a node | modded behaviour UNMEASURED |
| **conduit under doors** | a door cell is walkable | ordinary floor conduit; cords pass through the doorway pinned (§8.2.6) | none |
| **diagonal adjacency to a device** | power links are orthogonal; machines connect via `connectParent` up to 6 cells | the machine's cord goes to its connect cell's node; diagonal contact means nothing | none |
| **multi-cell buildings with several connection cells** | vanilla gives one `connectParent` per `CompPower` | one cord per `CompPower`; a building with several comps (modded) gets several | modded, UNMEASURED |
| **deep water and FlowWorks canals and pits** | the cell is unwalkable (deep water; canal/pit depths the path grid marks impassable) | buried: stubs at both banks; water = the cord dives in under ripples; a canal or pit lip = a drilled hole in the lip | shallow canal cells are walkable: cords lie in them. The FlowWorks depth→passability mapping is UNMEASURED here |
| **two unconnected nets in one room** | separate conduit components | separate graphs; their cords may cross each other on the floor freely, never join | a reader may think crossing cords are connected; the selection highlight (§8.3) answers it |
| **very long runs** | path length | extra cord capped at 16 cells, so a 60-cell run is ~1.25x and mostly a gently wandering cord with a few bunches; cords > 40 cells add one extra heap near each end, where people look | none |
| **traffic lanes, stockpiles, zones** | not read | cords lie under items and pawns as conduit does; no avoidance (zones are not walkability) | visual clutter on stockpiles; acceptable |
| **fire** | burning conduit is destroyed by vanilla | becomes terminals (§8.7.1) | none |
| **snow** | drawn under Conduits | cords on top of snow, as vanilla conduit | deep-snow fade optional (phase 3) |
| **roofs** | `roofGrid.Roofed` | sway weight 0 | none |
| **fog of war** | `fogGrid.IsFogged` | fogged cells are unwalkable for planning and their nodes undrawn | none |
| **map edge** | buried run reaching the edge | a normal stub (it continues off-map); not a wall terminal | none |
| **blueprints / frames of conduit** | `Blueprint_Build` / `Frame` of a conduit def | not conduit: ignored by the graph; a gap with a blueprint in it is still two terminals | none |
| **underground-wire mods** | their own defs | only defs tagged with our extension join the graph; untagged transmitters are still graph vertices (so connectivity is right) but buried | modded, UNMEASURED |
| **save/load** | — | nothing saved; graph and cords rebuilt on load, bit-identical by seeding | none |

#### 8.7.7 Performance on a 5,000-conduit base

Arithmetic, not measured. A 5,000-cell base reduces to roughly 500-1,000 nodes (junctions, machines, stubs,
terminals are 10-20% of cells) and 600-1,200 cord edges; dense fields collapse further (the mock-up lattice:
40 cells → 1 node). Laying every cord once: ~1,000 cords × ~250 points × 70 iterations × 60 flops ≈ 1 Gflop,
about 0.5-1 s of C# **at map load**, spread over sections as they first draw (lazy) or a background task.
After that, a change re-lays only dirty edges (typically 1-5 cords, a few ms). Geometry: ~1,000 cords × 250
points × 2 tris ≈ 0.5M tris static, culled per section, about half the per-cell model's estimate. Live terminals
and downed wires animate per frame, a handful at a time.

### 8.8 Clipping and artifact risk register

| # | failure mode | mitigation | check |
|---|---|---|---|
| 1 | cords z-fight at crossings | per-cord Y increment (a fraction of AltInc) | visual |
| 2 | a cord vertex inside a wall, rock, water or building | the settle projects out of unwalkable cells; buried conduit is never drawn | state: no laid vertex in an unwalkable cell (selftest, every scene) |
| 3 | **doors** chop the cord | pinned through the doorway at floor level, covered by the leaves | visual |
| 4 | multi-cell furniture over cords | walkable furniture: cords at Conduits height show through gaps; impassable: buried | visual |
| 5 | **fog** leak | fogged cells unwalkable; fogged nodes undrawn | state: zero vertices in fogged cells |
| 6 | **culling pop** when a cord reaches far from its owning section | `GetBoundaryRect` returns the real printed extent | visual |
| 7 | a cord far from its conduit confuses selection | the selection highlight draws the whole net's cords (§8.3) | visual |
| 8 | **cord wanders far from the conduit route** (a trunk laid along a wall, its cord crossing the room) | owner-ruled acceptable; A* takes the shortest walkable route, and the slack stays near it | visual |
| 9 | doorway pass-through: a heap jams the doorway | doorway pins; loops are spliced only where `ramp ≥ 0.9` (away from pins) | visual |
| 10 | **rock stubs** in dark rock read poorly | chipped light rim on the hole | visual |
| 11 | **wide open rooms with many machines**: dozens of cords crossing | 1-3 cords per edge, slack budget, tangles for dense fields; the slack setting | visual, owner sitting |
| 12 | transparent material sorts wrongly against filth and gas | cutout family shader (`CutoutPlant`); soft drop shadow is a separate transparent strip | visual |
| 13 | far-zoom shimmer | LOD sub-mesh; mipmapped strips | visual |
| 14 | **Gravship cutscene** (Odyssey): `SectionLayer_Things.DrawLayer` has special cutscene handling that our layer would not get | hide the layer while `WorldComponent_GravshipController.CutsceneInProgress` | UNVERIFIED, owed a live look |
| 15 | a cord across the substructure/hull edge | the reduction never links across it (`ShouldLinkWith` rule); the planner treats the hull edge as unwalkable for cords of the other side | state |
| 16 | the power overlay loses its connector lines (Invisible Conduit's bug) | the prefix acts only when `!forPowerOverlay` | state: the `MatConnectorLine` sub-mesh is non-empty |
| 17 | sway shader displaces along the wrong axis | small amplitudes; CPU fallback for lifted spans | visual, first test |
| 18 | spark flecks spam the screen in big breakdowns | per-map cap on concurrently sparking terminals; settings | state |

**What the nodal model removed** from the per-cell register: wire paints over a tree/lamp south of a wall-top
run (matched-Y wall tops), wall-top vs wall-corner-filler fights, sprawl cut by walls, stale joins at section
edges (edge-seeded bundle joins), bundle divergence and junction port matching. **What it adds:** rows 7-11.

**Testing split.** Northstar state reads: graph census, connected-only, no vertex in an unwalkable cell, hash
stability across save/load and unrelated edits, overlay lines intact, terminal registry and the live/dead flip,
toggle off. Visual review (rows 1, 3, 4, 6-14, 17) is a **keeper savegame** with one test bed per row for the
owner to walk; a screenshot is never a pass bar.

### 8.9 Compatibility

**Active mods relevant here.** MEASURED by parsing `infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml`
(610 active mods): `vanillaexpanded.vfepower`, `dubwise.dubsbadhygiene.lite`, `dubwise.rimefeller`,
`noneobsidiaexpansion.ledlightsstrip` and `dubwise.dubsmintminimap`. Invisible Conduit is **not** active.

| neighbour | interaction |
|---|---|
| vanilla `HiddenConduit` | excluded by def, so it stays the tidy invisible option. Vanilla already skips its hookup wire |
| Invisible Conduit Continued (inactive) | both make conduit invisible, which is harmless. Its unconditional `PrintWirePieceConnecting` prefix also kills the overlay lines. Declare it incompatible in About |
| Underground Wires-style mods (none active) | different defs; graph vertices but buried unless tagged |
| **VFE Power** (active) | any extra conduit defs it adds are UNMEASURED. The default target set is "defs with `building.isPowerConduit` and `linkType Transmitter`", with a settings checklist listing every match |
| **LED Lights Strip** (active) | "placed like conduit". If its defs set `isPowerConduit` we would draw cords for them. UNMEASURED: check its defs before choosing the default target set |
| **Dubs Bad Hygiene Lite, Rimefeller** pipes | their own link flags and defs, so untouched. The same graph code could later draw messy *pipes* through an opt-in extension |
| conduit retexture mods | we replace the conduit texture with a transparent one. Put our patch in a `zzz` file and `loadAfter` known retextures |
| overlay or minimap mods (Dubs Mint Minimap) | the minimap reads grids, not our meshes |
| Multiplayer | visual only. No `Rand`; the 250-tick poll only reads state |

### 8.10 Effort, cost verdict and phased plan

Phase 1a was built 2026-10-02 (§8.13). Days below are the original estimates.

**Is the nodal model cheaper than the per-cell overlay? Yes.**

| | per-cell overlay (06 look, previous plan) | nodal cords (this plan) | factor |
|---|---|---|---|
| **code to the 06 look** | phase 1 overlay 5-7 d + excursions 4-6 d + load bundles 2-3 d + Kirchhoff 1-2 d = **12-18 d** | **7-9 d** (phase 1 below) | **~1.8x less**; ~1.4x less even with load bundles struck from the old plan (9-13 d) |
| **cheapest first version that already reads as messy** | phase 1 without excursions, 5-7 d, and it looked tidy | **4-5 d** (phase 1a) with the loopy look | — |
| **hard subsystems** | wall-top runs with matched-Y occlusion + drapes; edge-seeded joins across sections; bundle port matching + union-find; per-cell Bezier strands; flow solve | A*, string-pull, rope settle (exists in Python), stub decals | 5 hard pieces → 1 moderate one |
| **perf** (mock-up, same conduit) | 25 strands, 8,178 points, 0.35 s | 18 cords, 4,055 points, 0.23 s | **~2x less geometry, ~1.5x less laying time**; dense fields up to ~10x less (45 cords → 4 + 1 heap) |
| **risks** | 18-row register, 7 rows needing matched-Y or section-edge joins | 18 rows, none needing matched-Y; 5 removed, 5 new and visual-only | the expensive-to-fix class (occlusion bugs) is gone |
| **invalidation** | every conduit cell's strands + a 3-cell dirty reach + per-run settle cache | per edge, by endpoint key and corridor | simpler |

**Phases.**

| phase | scope | effort | art |
|---|---|---|---|
| **0. Mock-ups (now, done)** | Python: reduction, planner, slack laying, stubs, terminals, downed wire, tangles, needless loops; 07 and 08 sheets; selftest | done | procedural placeholders |
| **1a. Cheapest first version** | invisible conduit (XML texture swap + transparent PNG); hookup prefix; `RM_MapComponent_CordGraph` with reduction + A* + string-pull; slack as **canned** loop/figure-eight/heap shapes spliced at seeded points that pass a walkability test (no PBD settle); one strip texture; plugs and stub decals; terminals with **static** live sparks via vanilla flecks; settings; first script | **4-5 d** | 6 (strand strip, shadow strip, plug, junction, stub wall, stub rock) |
| **1b. Full static nodal cords + break readout** | port the rope settle (PBD, SDF of the corridor) and the length budget; per-edge cache and corridor invalidation; tangles; needless-conduit knots; device/water stubs; whipping live tails; downed-wire bursts; selection highlight; LOD | **+3-4 d** (7-9 d total) | +7 (§8.11) |
| **2. Sway** | `CutoutPlant` strand material, vertex-alpha weights on lifted spans (lamp climbs, hanging wall terminals), roof zeroing; CPU fallback if the shader misbehaves | 1-2 d (3-4 with the fallback) | 0 |
| **3. Decoration** | trunk wraps, per-def trunk anchor table, snow fade, Jawa campaign art set (`RUT_`), grease decals | 2-4 d | +8 |
| 4. Overhead spans | experiment only | — | not recommended |

Break-sparking is in phase 1 because it is cheap: terminals come out of the reduction, sparks are vanilla
flecks, and the poll is 250-tick. It is also the highest-value debugging aid in the mod.

### 8.11 Aesthetic: "truck drivers in space"

**Direction.** Ugly on purpose. Nothing matches, everything is repaired, and it has been working for twenty
years. Everything is a too-long extension cord.
- **Structure (owner, 2026-10-02):** three style families: 1 Cybertek, 2 Extension cord and 3 Star Wars.
  **Jawa is a variant of the Star Wars family**, not a separate set. In his words: *"Jawa is certainly more
  option 3. Though there should be no white versions and many should be smooth black cables with less
  shine."*
- **Star Wars family and Jawa variant:** smooth **matte** black cable dominates (low, broad sheen, no specular
  line); a few dark corrugated-steel hoses and coiled black cords; **no white cable, tape or power-strip body
  anywhere in the family** (the Jawa power strips are dark grey with an amber LED).
- **Jawa jury-rigging:** dark and ochre electrical tape in lumpy wraps, hose clamps, zip ties, rag bandages,
  solder blobs, hand-twisted splices; grease smears around junctions; a ration-tin or droid-chest-plate box at
  X junctions; hand-painted arrows and tally marks.
- Still the painterly lawset: top-lit cylinders, value over detail at 64 px a cell, the 70s-brown palette.
- The franchise-free `RM_` set stays generic and dirty. Overtly Jawa trinkets go in the `RUT_` set (§4).

**Art list, ruled from the mock-ups** (07/08). One strip per cord kind; a cord is one ribbon, so there are
**no strand-count variants** and no bundle textures.

| group | phase 1 | later |
|---|---|---|
| **strands** (tileable 128×32, alpha edges, mipmaps) | matte black cable; drop-shadow strip | dark corrugated hose; coiled black cord; bare copper (tails); taped strand; family strips for Extension cord and Cybertek if they ship |
| **nodes / junction pieces** | tape lump (T); ration tin (X) | greeble box, hex pod, power strip (lit / dark LED) for tangles and device stubs |
| **plugs** | plug into a casing | lamp-post climb tape |
| **stubs** | wall grommet plate; rock cable hole | scorched ragged hole + soot (wall terminal); water ripple ring |
| **decals** | frayed end, dead (dull copper) | frayed end, live (bright copper, scorch); hose clamp; zip tie; rag wrap; grease (2) |

Sparks, drips and the downed-wire flash reuse vanilla `MicroSparks`/`LightningGlow`: **0** new art. Total:
6 textures for phase 1a, 13 for phase 1b, about 21 with phase 3.

### 8.12 What this pass could not verify

- **The `CutoutPlant` shader's displacement function** (axis, use of vertex alpha and UV z). The sway verdict
  depends on it.
- **Whether cutout map shaders write depth** (ZWrite). Only the optional trunk-wrap and lamp-climb front halves
  rely on it now.
- **The gravship cutscene path** for a custom section layer (risk 14).
- **Trunk pixel positions and widths** in vanilla and modded tree art. These are not in defs.
- **Whether conduit can be placed under natural rock** in vanilla (the mock-up assumes it can; the rule costs
  nothing if it never happens).
- **FlowWorks canal and pit passability by depth** (§8.7.6).
- **The conduit defs of VFE Power and LED Lights Strip.**
- **Any C# performance number.** All C# costs are arithmetic; only the Python mock-up timings are measured.
- `CameraDriver.CurrentViewRect`'s own body and the vanilla battery def's comps were not read.
- Phase 1a was tried in game on 2026-10-02 (§8.13); the sway, the gravship cutscene and the multi-family art were not.

**Mock-ups:** `Transient/messy_conduit_mockups_20261002/07_nodal_*.png` (main scene in three families, break
readout, per-cell vs nodal, node-graph debug view) and `08_tricky_*.png` (§8.7). Renderer:
`src/RimMandrake/Utils/mockups/messy_conduit/nodal.py` and `tricky.py`; `selftest.py` covers the reduction
census, connected-only cords, the gap, geometry, determinism under unrelated edits and the tricky rules.

### 8.13 Phase 1a as built (2026-10-02)

**Where it lives.** `src/RimMandrake/MessyConduit/`: `Source/Core/` (Verse-free: `CordWorld` snapshot, `CordGraph`
reduction, `CordPlanner` A* + string-pull + corner rounding, `CordLayer` slack, `CordBuilder` per-edge cache);
`CordWorldAdapter` (map -> `CordWorld`, the only power-specific piece, so hoses or suspended wires can reuse the
core with their own adapter); `RM_MapComponent_CordGraph`; `SectionLayer_RM_MessyCords`; `ConduitVisuals` (+ the
hookup-wire prefix); settings; `MessyConduitProbe` (the functional script's state-read channel). Offline oracle
parity: `Source/SelfTest/` compiles `Core/` against `export_oracle.py`'s scenes (`selftest_messyconduit.py`).

**Departures from the design above, each chosen after the engine said so:**
- **The conduit texture swap is C#, not an XML patch.** An XML `texPath` replace can only be undone by a restart;
  the settings contract is "all-off restores vanilla". `ConduitVisuals` swaps each target def's `GraphicData` for a
  copy pointing at a fully transparent PNG, keeps the original to put back, and calls `Notify_ColorChanged` on
  spawned conduit. `linkType Transmitter` is kept (§1). Beauty/Flammability untouched (§2).
- **Slack is canned shapes, not the PBD settle** (as §8.10 phase 1a planned): excursions clipped to the open
  floor, loops/figure-eights/heaps spliced where every point clears unwalkable cells, 6 rounds of bend smoothing
  with a hard projection out of obstacles, and a fallback to the planned centreline if any vertex still sits in
  an unwalkable cell (0 fallbacks on all 7 oracle scenes and in game). Clearance is an exact box distance over a
  5x5 window, not the oracle's sampled SDF.
- **Rebuild = the first regenerate of a frame.** The component rebuilds once per frame on demand (snapshot +
  reduce; unchanged edges re-emit their cached polylines by key + corridor walkability hash) and dirties every
  OTHER section whose owned pieces changed with `RM_MessyCords`.
- **Live/dead flips rebuild only the owner section:** a terminal's live flag is part of its edge's cache key, so
  a dead end lies limp (curled tail, dull fray) and a live end is straight with the bright fray, a per-frame glow
  and vanilla `MicroSparks`/`LightningGlow` on a deterministic per-end schedule (max 24 sparking ends per map). No whip yet.
- **Substructure rule not applied** (see §8.1): a hull edge would read as a break.
- **Machine-to-machine hookups** (a heater wired to a battery) keep vanilla's thin wire; only hookups to our
  conduit are suppressed and drawn as cords.
- **Section meshes regenerate only in view** (engine: `Section.TryUpdate`), so a state read of the drawer's
  meshes needs the camera on the scene; the functional script frames it first.

**Proven live** (fresh quicktest map, messyconduit tier, `validation.py --live`, 19/19 live rows PASS, ~270
ticks): transparent conduit; cords and end pieces printed; node census incl. a live wall terminal; no cord across
nets; no vertex in an unwalkable cell; fresh-builder determinism; local invalidation (1 edge re-planned); hookup
wire hidden with overlay connector lines intact; a destroyed conduit gives a live and a dead end, no cord across;
source off reads dead within one 250-tick poll; master off restores vanilla art and on restores the cords; clean
log. Recorded with `modcheck record`: REFUSED (6 UNBUILT, 2 UNCOVERED bars, by design).

**Save/load and mod removal (live pass 2, 2026-10-02)** found two defects, both fixed in
`RM_MapComponent_CordGraph.cs` and re-proven: a loaded save drew NO cords (the first section regenerate of a load
dirtied sections `MapDrawer.RegenerateEverythingNow` had not created yet, NRE, pieces lost), and the save carried
the component's `<li Class=...>` so a mod-less load logged two red errors (now kept out of
`Map.ExposeComponents` while saving). `validation.py --save-load` (M4: same geometry hash after load, the save
holds nothing of ours) and `--removal-check` (M9: 0 errors naming the mod on the `flowworks` tier) both PASS.

**Art-fit polish (2026-10-02, after the real art landed).** The live pass 2 defects are fixed in the core and
proven offline (`CordAudit`, shared by the SelfTest and the probe's `artfit`) and live (artfit 0 faults on the
keeper scene and a fresh map; 19/19, `--save-load`, `--removal-check` re-run PASS):
- **Junctions are posed from their cords**: four arm directions take the tin cross, fewer the taped T turned so its
  missing arm faces the empty side, the art's junction point on the node; every cord ends at an arm tip arriving
  along the arm (`CordBuilder.PoseJunction`, `AttachEnd`, `CordLayer.Approach`). The +-0.08 knot jitter is gone.
- **Draw order is a render queue, not altitude.** `MapDrawLayer.RefreshSubMeshBounds` gives every section submesh
  the same bounds, so transparent submeshes tie on sort distance; the Transparent shader and the wall/granite
  `Custom/Cutout` materials all sit at queue 2900 (measured live). Shadow 2899, strand 2900, end pieces 2901,
  face pieces 2902; face pieces also at `BuildingOnTop` altitude. Pawns and items still draw over all of them
  (checked live).
- **Stub art turned along the cord** (the real art's cord runs along its +X), plate/hole on the face line.
- **One plug per machine end, its head pointing into the footprint** and pushed past the edge.
- **Dead ends curl over** (0.7 cell, tip 0.27-0.38 cell off the conduit line, dull-tinted fray); **live ends run
  straight out of the conduit end** and pulse a glow every frame (works paused) besides the sparks. No whip yet.

**Known defects / not verified:** the dead end's curl is clear close up and subtle at far zoom; a wall terminal
inside natural rock hangs its tail down the rock face like a wall's (reads as a thin line); plug heads tuck under
the machine sprite; performance on a large base not measured; Jawa art family only (8 real textures, 4
placeholders: EndFrayed_Live, SparkGlow, PowerStrip, ConduitTransparent).
