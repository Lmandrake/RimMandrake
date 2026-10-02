# Messy Conduit — design pass (2026-10-02)

Owner idea, 2026-10-02: *"I normally hate how they make conduit invisible, but now that I think about it,
Jawa should celebrate that. I almost want to make it weirder like snakey, ropey loose conduit on the floor.
Spawn out a design pass to consider how hard it would be to make MESSY CONDUIT, an alternative mod that would
make conduit sprawl all over the floor in loose wirey mess like it does in real life."*

Status: DESIGN ONLY. Nothing built, nothing filed. No item exists yet (proposed name below).
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
  in the next section keeps a stale join. This decides how Tier B must be built (§3).

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

### Tier B: C# procedural printer (recommended core)

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
  under clutter. Walls hide it, as vanilla does.
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
- Draped wires that sway.
- Heaps that coil.
- Tangles that grow with age.
- Trip hazard (path cost).
- Fire or short-circuit risk when wet or damaged.
- A "tidy the cables" job.
- Wire spools as an item.
- Hooks: vanilla `IncidentWorker_ShortCircuit` already picks a conduit (`ShortCircuitUtility`), and our
  `RSW_Mynock` (ShipVermin) already feeds on live power and could chew loose cable.

**Engine cost.**
- **Sway** means per-frame drawing: `drawerType` RealtimeOnly or a dynamic draw for every conduit. That is
  O(conduits) per frame and **bad on large bases**. The alternative is a custom vertex-sway shader shipped in
  an AssetBundle, which carries high risk and is a new toolchain for us.
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
  `RimMandrake.MessyConduit`, prefix `RM_` (`RM_Graphic_MessyConduit`, `RM_MessyConduitExtension`).
- It is franchise-free and is a public-use mod.
- Hard dependency: Harmony (Tier B). No DLC dependency needed, though Odyssey's substructure rule is
  honoured by reuse.

**Settings.** This is the full set for every tier ("superb Mod Settings"):

| Setting | Effect | Applies |
|---|---|---|
| Master enable | — | restart |
| Messiness slider | sprawl distance, strand count, loop/snake chance | live (dirty all sections) |
| Variant count / LOD | — | live |
| Per-def toggles | power conduit, waterproof, "all isPowerConduit defs" | — |
| Sagging machine wires | — | — |
| Colour mode | salvage-mixed or uniform | — |
| Leave the power-overlay lines alone | fixed on; it is a guarantee, not a toggle | — |

Defaults equal the shipped behaviour, and all-off degrades to vanilla.

**First functional script** (`debug_process.md` §2): `src/RimMandrake/MessyConduit/validation.py` plus the
walk `design/validation_walks/RimMandrake/MessyConduit.md`.

`## must be true` lines, each with a cheap state read:
1. `PowerConduit`'s live `Graphic` is our class (Tier B), or a `Graphic_Random` with N>1 (Tier A). Read the
   def's graphic type through the bridge.
2. `HiddenConduit` stays invisible: its colour alpha is 0 and it is excluded from our class.
3. The same cell yields the same mesh after a save/load: hash the section layer's vertex count and a sample
   of positions before and after.
4. Neighbour joins update across a section boundary when a conduit is placed or removed (place at x=16|17
   and read the adjacent section's dirty/regen state).
5. With the power overlay on, connector lines are still printed (the `SectionLayer_ThingsPowerGrid`
   sub-mesh for `MatConnectorLine` is non-empty). This is a guard against Invisible Conduit's bug.
6. Master toggle off → vanilla `Graphic_LinkedTransmitter`.
7. Removing the mod from a save that used it: the load is clean and `Player.log` shows no errors.

Steps 1–2 and 6 are `--mock`-selftestable; 3–5 and 7 need the bridge. Visual judgement ("does it read as
messy") is a screenshot or a keeper savegame for the owner, never a pass bar.

`## anti-guessing notes`, seeded:
- `RULED OUT: custom graphicClass with linkType None — CanAffectLinker false ⇒ no adjacent-cell regen
  (ThingDef.CanAffectLinker, Thing.cs SpawnSetup)`.
- `RULED OUT: drawSize enlarges linked art — Graphic_Linked.Print hard-codes Vector2(1,1)`.

## 6. Recommendation and build plan

**Smallest version that delivers the feel: Tier B-lite, with no gameplay.** Tier A cannot sprawl past the
cell, and sprawl is the whole point of "snakey, ropey loose conduit on the floor". Tier B's printer is small
and safe, and it is where the feel lives. Tier C stays a later, separate opt-in (`MessyConduit.Hazards`), if
ever.

🔴 **This is gated by the 2026-10-01 build pause.** A new mod is new content, and the pause holds it until
every mod has a first script with a recorded run (`debug_process.md` §1, "DONE"). Steps 1–2 below are design
work and can go ahead now. Steps 3 onward wait for the lift, or for the owner's explicit word.

**Build order.**
1. File the item (proposed `MESSY_CONDUIT_MOD_1`). Owner answers the questions in §7.
2. Mock-up loop, offline, before any C#: render 3 messiness levels on a 20×20 sample base to PNG from a
   Python prototype of the same Bezier math. The owner picks (owner design loop: mockups first).
3. Skeleton mod: About, Harmony dependency, Settings class, `RM_MessyConduitExtension` patched onto
   `PowerConduit` and `WaterproofConduit`.
4. `RM_Graphic_MessyConduit` and the `WrapLinked` postfix. Strand ribbons, edge-seeded joins, transmitter
   stubs into machines, Odyssey rule reused.
5. Sagging small wires (prefix, `forPowerOverlay == false` only).
6. Decals: splices, tape, coils at dead-ends, junction lumps at T/X junctions.
7. First script (§5), `--mock` selftest, then one bridge run on a minimal list (FOUNDRY, when the bridge is
   free).
8. A keeper savegame with all messiness levels side by side for the owner.

**Art needed (Tier B), about 10–14 textures:**
- 3–4 tileable **cable strip** textures (thin, medium, thick bundle, bare copper), each a 64×16 or 128×32
  horizontal tile with alpha edges.
- 1 **sagging machine wire** strip, replacing `Things/Special/Power/Wire`.
- About 6 **decals** at 64×64: tape wrap, splice with copper, coil (dead-end), junction knot (T), junction
  knot (X), zip-tie bundle.
- Optional waterproof set: 2 strips with heavier insulation.
- Optional Jawa campaign set (RUT): 2–3 strips (droid harness, rag-wrapped).

For comparison, Tier A would need 4–6 full 4×4 atlases (64–96 hand-matched tiles under the port contract),
which is far more art for less feel.

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
