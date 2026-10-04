# MessyConduit test extension: consult and proposal (2026-10-04)

CONSULT workstream of the MessyConduit round-2 review. Docs only; no src edits.

**Top recommendations** (detail in §4.1 and §5):
1. Hose maze then blocked route: one hose scene; tests the corridor-hash re-lay and the cached failed lay, and forces
   the reroute/retract/report decision.
2. Modern colour stability under extend/split, testable today: run colour is a hash of the net's smallest end token,
   so one added cell can recolour a whole run. Per-run colour must be STORED on the pieces before stage 2 is coded.
3. Per-run style: one `runs` probe verb + one lifecycle scene (`validation_style.py`) covering adopt/merge/tie/
   split/restyle/reinstall/save-load; style becomes a per-scene property of the existing 109-scene live matrix at
   zero extra scenes; human row E = per-family style quartets + Modern colours + merge/restyle + art-slot board.

## 1. What the mod does today (verified from code)

Read from `src/RimMandrake/MessyConduit/Source/` and `Defs/` on 2026-10-04 (foundry clone at `08895c0c1`), not from
the design docs.

**Ground cords (the core).** Vanilla `PowerConduit` / `WaterproofConduit` are drawn invisible (transparent conduit
PNG; `HiddenConduit` stays as the tidy "buried" option). `RM_MapComponent_CordGraph` rebuilds a graph from the conduit
grid every time the grid changes (`CordGraph.cs`): it reduces conduit cells to nodes (terminals, junctions, devices,
wall and rock entries, live/dead ends) and edges, then `CordPlanner` routes each edge with an 8-connected A* over
walkable cells (no corner cutting) and `CordBuilder` settles a rope (slack, sprawl cap, 1-3 cords per connection,
needless loops, tangles once a net has `tangleMin` = 9+ cells). `SectionLayer_RM_MessyCords` prints the ribbons plus
decals (plug, two junction kinds, wall stub, rock stub, power strip lit/dark, frayed end live/dead). Lateral reach is
5 cells. Nothing about the cords is saved; the component is kept out of the save on purpose (`M9` defect fixed
2026-10-02). Motion and effects: rope sway (CPU or shader path), floor ripple (off by default), whip of live tails,
downed-wire spark bursts with a cap of 24 sparking ends, selection highlight, far-zoom LOD. Hookup wires of
connectors are hidden by default.

**Styles.** `CordStyle { StarWarsJawa, ExtensionCord, Cybertek, StarWars }` (UI labels Scrapper / Modern / Industrial /
Futuristic since B19; saved key `style` unchanged). It is ONE global Mod Setting read in `CordMaterials.Build` and
`AerialMaterials.Build`; pole art is changed by editing the shared ThingDef graphic (`AerialMaterials.ApplyPoles`), so
every pole on every map looks the same. Modern colour: `ExtCordColorMode { Mixed, Single }` + `extCordColor`; each net
gets one colour or cable kind via `CordMaterials.VariantFor(netSeed)`. Missing per-style art falls back to another
style's texture (row `U_style_missing_art` records it as UNBUILT).

**Overhead lines (L5).** Defs `RM_AerialMast`, `RM_AerialLampMast`, `RM_AerialWallBracket`, `RM_PowerTapClamp`,
`RM_AerialLines`. Anchors carry `CompAerialAnchor` (gizmos: Link wire, Unlink wire, Unlink all, Re-string cut wires,
Auto-link selected). `RM_MapComponent_Aerial` owns links, span states (`Up`/`Cut`) and cached ribbon meshes; a Harmony
patch on `GenAdj.CellsAdjacentCardinal(Thing)` makes linked anchors adjacent for `PowerNetMaker`, scoped to net
rebuilds. Link verdicts: Ok, Self, AlreadyLinked, OutOfRange (range = `maxSpan` 20, clamped 4-40), FullA/FullB,
Foreign, NotAnchor, Roofed. Spans sag (`sag` 0.06) and sway (`WireSwayMode` Auto/CPU/Off); explosions cut spans
(`explosionsCut`). Strands per span = `maxStrands` (default 3): `AerialMath.SpanStrands` puts 1 strand on the middle
insulator, 2 on the outer pair, 3 on one insulator each. **There is no per-terminal assignment of local devices**: the
strand count is cosmetic and the whole span is one electrical link (owner's question in round 2). Wall brackets
use `BracketGeometryTable` per facing; masts use `PoleGeometryTable` for insulator positions. A
`SectionLayer_RM_AerialGround` draws ground-level pieces (fallen cords under a dead pole). **Power tap clamp**:
`CompPowerTap`, a plain `CompPowerTrader` with negative consumption, guarded so it only connects to our faction's net
while it debits a foreign net through a patch on `PowerNet.CurrentEnergyGainRate` (`tapRate` 500 W, `tapEvents`).

**Hoses (L6).** `RM_HoseReel` with `CompHoseReel` (gizmos: Lay hose (targeted cell, up to `maxLength` 30), Reel in,
Free end: nozzle/end cap/open, DEV: flow through hose). The lay uses the same cord planner (A*) and rope settle with
stiff hose parameters plus a bend-radius pass (`minBendRadius` 1.2). State machine `HoseVis { Flat, Filling, Plump,
Draining }` with hysteresis (`transitionTicks` 30, `releaseTicks` 500, `minPlumpDwell` 600). Flow comes from
`FlowWorksPumpFlow` when `useFlowWorksPumps` and a FlowWorks pump is the source, else `DebugHoseFlow` (dev gizmo).
Tint by contents, fill wobble, couplings every 8 cells. The reel does NOT join static pipes or tanks today (owner
round 2).

**Settings.** Three tabs (Cables, Overhead lines, Flexible hoses): 24 core fields (`MessyConduitMod.cs`), 11 aerial
(`AerialSettings.cs`), 13 hose (`HoseSettings.cs`), each with a master switch.

## 2. Tests we run today

| Suite | What it runs | Rows |
|---|---|---|
| `validation.py` offline | O1 mod files (csproj compile list, DLL `.srchash`, textures, transparent conduit), O2 settings defaults = shipped table, O3 C# core SelfTest vs Python oracle (+ O3n planted-mismatch negative), O4 oracle selftest, O5 style art sanity, O6 review-round-1 checks | 7 |
| `validation.py --live` | one fresh quicktest map, ~270 ticks: battery, 9x7 room + door, branch, lamp, run into a wall, far isolated run. M1 census/end pieces/transparency, M2 cords only inside a net and never on unwalkable, M5 local invalidation, M6 overlay intact, M7 off restores vanilla, M8 break = live end + dead end, source off reads dead, M10 tangle threshold, B1-B9 motion/LOD/highlight/strips/whip/sparks/cutscene guard (state reads, not pixels), ST2-ST5 style switch, Modern colour modes, settings round trip, Z log budget | ~40 |
| `--save-load` / `--removal-check` | M4 cord set hash identical across save/load, save written as a NEW file only; M9 the save holds nothing of ours and loads clean on a tier without the mod | 4 |
| `validation_aerial.py` | M13 link across a gap, far consumer powered, unlink/relink, refusals, hostile mast never auto-linked; M14 despawn-gap control (fix off must fail) and fix on; dead pole drops live/dead cords; M15 explosion cuts a span, re-string rejoins; M16 save/load of links; M19 tap drains one way + taps-off control; M9b removal with anchors | 19 |
| `validation_hose.py` | H1 reels + install validity, H2 hose laid as hose cord, H3 width >= 4x wire, H4 bend radius, H5-H8 flat/plump/no flicker/collapse, H9 stiffness setting, H10 save/load, H11 removal | 16 |
| `northstar_matrix/` offline | `matrix.py` 84-case pairwise array over 7 axes (21 topologies x tangle x style x density x break x aerial x hose; 586 pairs, optimal), `design_spec.py` 109-scene design matrix (floor 64, density 16, aerial 18, hose 9, controls 2), oracle from `nodal.reduce`, `fakegame.py` round trip, `selftest.py` 47 checks (15 negative) | offline |
| `northstar_matrix/run_live.py` | places the 109 design scenes on a 226x100 region, census per scene vs oracle, ON/OFF screenshots + contact sheets. Last two runs (`matrix_live_20261004T1152.json`): 122 rows, **121 PASS, 1 SKIP** | 122 |
| `human_review.py` | not a test: 18 numbered stations (row A floor cords 1-6, B overhead 7-11, C hoses 12-15, D hose crossings 16-18) + a free area, calm world, in-world labels, key sheet; `--style X` flips the ONE global style | 18 stations |

What all of this shares: every verdict is a **state read** through a probe (`MessyConduitProbe`, `AerialProbe`,
`HoseProbe`) on a scene built for the test. Pixels are judged only by the owner. Style is tested as a global switch
(ST2: printed meshes carry only the chosen style's textures), never as a per-object property, because there is none
yet.

## 3. GPT consult: where high-value tests could go

Asked 2026-10-04 via `gpt_consult.py -m gpt-6.1-sol --effort high`, with sections 1-2 of this file, the style design and
the round-2 owner notes inlined. Prompt asked for (A) 12-20 ranked high-value tests that would open NEW questions,
under our constraints (state reads, scarce bridge time, economical tests), and (B) how to extend the matrix and the
human sheet for user-selectable art. Answer recorded verbatim; it is evidence, not a ruling.

<details><summary>GPT answer (verbatim)</summary>

```text
For A, ranked by expected value. Reuse fixtures within one quicktest map; several entries can share the same mutation sequence.

1. Block an existing route.
   Lay a hose through a two-route maze, then build a wall across its preferred route; subsequently block both routes. Repeat with ground cords and a door changing walkability. Read occupied cells, clearance and endpoint connectivity. This could expose stale routing or drawing through walls because paths are settled and cached. Decide whether hoses reroute, retract or report blockage before asserting an outcome. Cost: one quicktest scene; owner reviews the maze.

2. Remove endpoints through real engine operations.
   Destroy, minify, reinstall and replace a linked anchor; include one anchor with several links. Assert reciprocal links, no references to despawned things, correct electrical connectivity and correct fallen-cord ownership. Explicit unlink tests need not exercise these lifecycle paths. Cost: one quicktest scene.

3. Remove the mod with unfinished construction.
   Save completed styled conduit alongside styled blueprints and frames, then load without the mod. Assert surviving vanilla construction, working power and acceptable logs. Finished conduit loses the added style comp; blueprints and frames already have engine style comps and might still attempt to resolve missing style definitions. Cost: needs a cold load; extend the existing removal check.

4. Keep two maps alive simultaneously.
   Put different styles and settings-sensitive objects on both maps; alternate edits and map activation. Assert unchanged materials, links and geometry on the untouched map, including when it is inactive. Shared ThingDef graphics and global material caches make cross-map leakage particularly plausible. Cost: one quicktest session with two maps.

5. Give electricity an alternate route.
   Build a ground-plus-aerial loop, cut one branch, then the last branch; restore them in reverse order. Assert actual consumer power and connected components after every step. Simple gap tests can miss stale synthetic adjacency, duplicate links or a cut span that still conducts. Cost: one quicktest scene.

6. Check tap accounting over elapsed ticks.
   Use two taps on one foreign source, call energy-rate probes repeatedly without advancing time, then advance a fixed interval. Read source and recipient battery changes; repeat with taps disabled and ownership changed. This could reveal repeated debits, incorrect aggregation or stale faction permissions in the energy-rate patch. Cost: one quicktest scene.

7. Run bounded lifecycle churn.
   Repeatedly lay/reel hoses, link/cut/re-string spans and build/remove branches; finish in the original topology. Compare graph fingerprints and count retained links, meshes, materials and motion/spark entries. Growth or history-dependent output would expose caches surviving invalidation. Add one save/load checkpoint. Cost: one quicktest scene plus one load.

8. Measure large edits, not just large steady scenes.
   Use one roughly 2,000-cell run and many smaller runs of equal total size. Measure rebuild counts, processed cells, elapsed rebuild time, allocations and subsequent steady ticks during bulk construction, one break and restyle. Per-placement flood fills or global section invalidation could make otherwise cheap operations quadratic. Cost: offline scaling checks plus one quicktest scene.

9. Accept conduit from outside the build menu.
   Spawn an unstyled conduit through an external construction path; replace ordinary with waterproof conduit; include a representative third-party isPowerConduit def and one already containing Styleable. Assert graph inclusion, adoption and exactly one style comp. Def-name assumptions or duplicate comp patches could exclude or corrupt these objects. Cost: offline def checks plus one quicktest scene.

10. Check attachment geometry with awkward footprints.
    Cluster rotated 1×1 and larger devices around poles, including a battery and batten. Read connector endpoints against building centroids, drawing altitude, insulator positions and bracket attachment planes. Review wall mounts in all four facings. Fixed offsets and shared geometry can fail when footprints, facing or style change. Cost: one quicktest scene plus owner review.

11. Change faction after construction.
    Capture an anchor, switch ownership of a tapped source, then attempt manual and automatic linking. Assert current permissions, accounting and absence of unintended cross-faction restyles. Existing Foreign refusals test initial ownership; cached links may retain privileges after ownership changes. Cost: one quicktest scene.

12. Move a connected assembly by gravship.
    Carry styled conduit, anchors and a laid reel to another map, leaving at least one linked endpoint behind. Assert destination membership, style preservation, explicit handling of stranded links and no source-map references. Spawn-time adoption and saved endpoint references may behave differently during whole-base movement. Cost: one dedicated transfer scene; include it in a save/load session.

13. Change roofs and reveal mountain cells.
    Use a heavy-rock tunnel with fog around it; reveal cells, mine an entrance and roof an existing aerial span. Assert routing legality, graph changes and render membership against the intended visibility rule. Roofed-placement refusals do not establish what happens when an existing span becomes roofed. Cost: one quicktest scene plus owner review.

14. Test hydraulic integration as a conservation problem.
    Once static pipe/tank hookup exists, connect two reservoirs through a reel; stop flow, disconnect the source and change contents. Read volume, contents, flow and hose state. A pump signal can make a hose look plump while transferring nothing, duplicating liquid or retaining stale contents. Universal-liquid compatibility needs a defined mixing contract. Cost: one integration scene; currently a feature gap.

15. Toggle systems while they have live state.
    Disable and re-enable cords, aerials and hoses with laid hoses, cut spans and active sparks present. Assert preserved functional state, correct rebuilt render state and no continuing disabled motion/effect work. Shared planners and caches make subsystem interference plausible beyond the existing ground-cord OFF check. Cost: one quicktest scene.

16. Run a targeted full-mod-list sentinel.
    After small-tier checks pass, replay construction/copy, external conduit replacement, aerial power and real pump hookup once on the full tier. Compare state with the small-tier result. Harmony patch order, XML changes and alternate builders are risks offline or isolated tests cannot settle. Cost: one full-tier cold load, approximately 15 minutes; avoid a full matrix replay.

For B, use a small action-based array rather than multiplying the existing 84 cases or 109 scenes.

1. Settle the few unresolved contracts first.
   Define equal-size ties; simultaneous merges of three or more runs; Modern-colour conflicts between runs of the same style; random-mixture assignment granularity; and connectivity through HiddenConduit, switched-off switches and cut spans. The proposed “older wins” tie rule remains unapproved. These determine expected results, rather than adding matrix dimensions.

2. Add targeted axes.
   Track carrier path (blueprint/frame, god mode, copy, reinstall, external spawn), relationship (isolated, adopt, merge, split, same power net but separate runs), style/colour policy, persistence epoch and render slot. Give each risky interaction one fixture; do not take their Cartesian product.

3. Use eight dedicated fixtures.
   F1: four styles built through the real picker, with construction, god mode, copy and reinstall distributed across them.
   F2: placement chooses Modern but touches Industrial; adoption wins, while a disconnected neighbour stays unchanged.
   F3: a larger conduit run merges with a smaller run containing many anchors; conduit-cell count decides.
   F4: manual aerial linking merges unequal runs; automatic linking refuses incompatible styles.
   F5: a three-way bridge and an equal-size merge exercise the agreed winner rules.
   F6: two differently styled runs share power through a battery; restyling one leaves the other unchanged.
   F7: Modern single-colour and mixed runs undergo restyle, split and reconnect, including a same-style colour conflict.
   F8: four reels undergo lay/reel transitions; add an unstyled legacy run and known missing-art pieces nearby.

4. Read both stored identity and effective rendering.
   Probes should expose map/member IDs, run membership, conduit-cell count, raw StyleDef, effective style, Modern policy, material/texture per printed piece, fallback provenance and rebuild counters. Assert one style/policy per run, correct winner propagation, untouched neighbouring runs and matching ground/anchor/span materials. Random mixture must remain a single run policy, not a uniform random colour per run.

5. Assert art-only changes and Modern stability.
   Restyle must preserve building IDs, costs, hit points, power topology, stored energy, hose contents and endpoints. Check fixed-colour output against the chosen palette entry. Use a fixed mixed fixture known to produce multiple colours; do not require every tiny run to contain every colour. Specify and check mixture stability across unrelated rebuilds and save/load.

6. Consolidate persistence and negative controls.
   Save once with disconnected styles, Modern mixed/single policies, laid hoses and unfinished construction; reload and compare state fingerprints. Verify colour policy has a persistent representation—the four style markers alone do not explain it. Extend removal assertions from “nothing of ours saved” to “no transient graph saved; vanilla conduit survives.”
   Plant wrong-style output and uniform mixed output offline to prove detection. Exercise known missing slots: valid fallback, unchanged requested identity, correct geometry and bounded logs. Add an Ideology override candidate and an unrelated styleable building as patch-scope controls. Replace the draft screenshot-hash verdict with state fingerprints.

7. Human station 19: matched ground quartet.
   Show the same compact layout in all four styles: device attachments, junctions, wall/rock entries and live/dead ends. Add Modern fixed-colour swatches and a visibly mixed run.

8. Human station 20: overhead quartet over a populated room.
   Include nearby and distant devices, battery/batten connectors, all bracket facings and one-, two- and three-strand spans. Labels should distinguish cosmetic strand count from any implemented terminal assignment.

9. Human station 21: reel quartet.
   Pair stored and laid reels in each style, with flat and plump hose examples. Make inlet continuity, coil removal, couplings and end pieces easy to inspect.

10. Human station 22: merge/restyle demonstration.
    Provide labelled before/after areas showing larger-run victory, split inheritance and free restyle. Include Modern single-to-mixture change.

11. Human station 23: fallback examples.
    Label requested style, requested piece and actual fallback. Include missing live ends, switch frames, clamp and hose/reel slots so stand-ins are judged knowingly.

12. Human station 24: mountain and maze.
    Combine the blocked-route hose exercise with rock-entry alignment and legal overhead/ground paths around a fogged mountain corridor. Owner judges appearance; probes separately judge routing and state.
```

</details>

Where it agrees with our own list (4.0, written first): route blocking (our 2), endpoint lifecycle and gravship
(our 5), two maps (our 6), large edits (our 7), roof/mountain (our 3), Modern stability (our 1, which GPT
reached only as a requirement, not as the net-seed mechanism). New to us: removal with styled **blueprints and
frames** (A3), the ground-plus-aerial loop (A5), faction change after building (A11), toggling subsystems with live
state (A15), and on the style side three-way merges, two runs sharing a power net through a battery (F6) and
auto-link refusing across styles (F4).

## 4. Critical filter: what is worth building, ranked

### 4.0 Our own candidate list, written BEFORE reading GPT's answer (so agreement means something)

1. Net-seed instability: extend or split a Modern Mixed run and read each edge's colour (see §5.3; code-read
   hazard, testable today).
2. Hose maze (owner's request): a spiral with two routes, then a wall built on the short route while the hose is laid.
   Read from code: a laid hose re-lays only when the **corridor hash** changes (its bounding box + 2 cells,
   `RM_MapComponent_Hoses.CorridorHash`), checked every 250 ticks; a failed lay is cached as `lay = null`. So the
   questions are: does a wall on the short route re-route it within 250 ticks; does a wall just OUTSIDE the box +2
   that closes the long route go unnoticed (it should not matter, but a later edit inside the box then re-plans onto
   a route that no longer exists); does the long route exceed `maxLength` and fail; and what does a laid hose with a
   failed re-lay look like (null lay: does the hose vanish while `laid` stays true?).
3. Under-the-mountain span (owner's request): masts under overhead mountain with fog around them. `Roofed` is a link
   verdict, so the question is what happens when a roof forms over an existing span (mining collapse, roof build).
4. Dense room under a span (owner's request): many devices, messy floor cords, poles overhead. Checks draw order
   and that floor cords never route under the span's footprint differently.
5. Gravship move / minify of a pole with live links: do links follow, drop, or point at a dead id.
6. Two maps: a pole on a caravan/temporary map and the home map; the static `TapRegistry` and any static caches
   across maps (`TapRegistry` is a static class).
7. Large-grid performance: a 2,000-cell conduit base, toggle one cell, time the rebuild (M5 proves locality on a
   small scene only).

### 4.1 GPT's suggestions, filtered and ranked

Ranking = (chance it finds a real defect or forces an unasked design decision) / (bridge minutes + build cost).
Costs: **S** = rows added to an existing scene, **M** = one new quicktest scene (~0.5 agent-day, ~3-5 bridge
minutes per run), **L** = needs a cold load or new infrastructure.

| rank | test | source | why it earns its place | cost | home |
|---|---|---|---|---|---|
| 1 | **Hose maze, then block the route** (spiral with two routes; wall on the short route while laid; then block both; then a door) | owner, GPT A1, ours 2 | Owner asked. The corridor-hash re-lay (box + 2, every 250 ticks) and the cached failed lay are untested mechanisms with a concrete failure each (stale route through a wall; laid hose with null lay). Also forces a design answer: reroute, retract or report? | M | `validation_hose.py` + human station |
| 2 | **Modern colour stability under extend and split** | ours 1, GPT B5 | Code read: the run colour comes from a hash of the net's ordinal-smallest end token, so one added cell can recolour a whole run. Testable on today's build, and it decides how per-run colour must be stored before stage 2 is coded | S | `validation.py` live scene, 2 rows |
| 3 | **Anchor lifecycle through engine ops**: destroy, minify, reinstall, replace a multi-link anchor; then capture it (faction change) and try links | GPT A2 + A11, ours 5 | Explicit unlink is tested; engine despawn paths and ownership change are not. The style design leans on reinstall keeping comps, so this scene is reused by SR8 | M | `validation_aerial.py` |
| 4 | **Removal with styled blueprints and frames in the save** | GPT A3 | Real and specific: blueprints/frames carry the engine's own `CompStyleable`, so on a mod-less load they would reference our `ThingStyleDef`s that no longer exist. Rides the existing M9 removal lane, so no extra cold load once stage 2 lands | S (on L lane) | `validation.py --removal-check` |
| 5 | **Ground-plus-aerial loop**: cut one branch, then the other, restore in reverse; read consumer power per step | GPT A5 | The aerial adjacency is a Harmony patch on `GenAdj.CellsAdjacentCardinal` scoped to net rebuilds; redundant paths are where a stale or duplicated synthetic link would conduct through a cut | S | aerial scene |
| 6 | **Two live maps**: different styles and settings-sensitive objects on each, alternate edits and map focus | GPT A4, ours 6 | Today pole art is a shared-def edit (`ApplyPoles`) and several caches are static (`TapRegistry`, materials). Stage 1 removes `ApplyPoles`; this is the test that proves it. Before stage 1 it would just confirm a known global | M | after stage 1 |
| 7 | **Large edits at scale**: ~2,000-cell run vs many small runs; time rebuild, bulk build, one break, one restyle | GPT A8, ours 7 | M5 proves locality on a small scene only. The restyle/merge flood fill is new per-placement work. Do the scaling half offline in the C# SelfTest (CordGraph is Verse-free) and one live timing | S offline + S live | SelfTest + lifecycle scene |
| 8 | **Toggle subsystems with live state** (laid hose, cut span, sparks present) | GPT A15 | Cheap rows on scenes that already exist; M7 covers only the ground-cord toggle | S | existing scenes |
| 9 | **Roof forms over an existing span; mountain tunnel with fog** | owner, GPT A13, ours 3 | `Roofed` refuses a NEW link; nothing says what happens to an existing span when roofed (mining, roof build). Owner asked for the fogged mountain image anyway, so the station is owed regardless | M | aerial scene + human station |
| 10 | **Churn back to the original topology** and compare fingerprints | GPT A7 | Not its own scene: append as the final row of scenes 1 and 3 (return to start, fingerprint must equal the start) | S | appended |
| 11 | **External conduit**: spawned without the designator, waterproof replacing ordinary, a def that already has `CompStyleable` | GPT A9 | Becomes SR11 plus one offline def check (exactly one style comp per conduit def after patching). Only meaningful from stage 2 | S | style lifecycle scene |

**Deferred or declined, with reason:**
- *Tap accounting over ticks (GPT A6)*: code read weakens it. `TapRegistry.Owed` is read-only and keyed per tick, so
  repeated calls to `CurrentEnergyGainRate` do not repeat the debit. Keep one row in M19 (victim battery loss over N
  ticks = rate x N within tolerance), no new scene.
- *Gravship move (GPT A12)*: real question, but needs gravship launch/landing tooling we do not have in a test tier.
  File it for when that exists; minify/reinstall (rank 3) covers the comp-carriage half now.
- *Hydraulic conservation (GPT A14)*: correct framing, but the reel does not join static pipes yet (HOSE workstream).
  Write it as the HOSE workstream's acceptance test, not now.
- *Full-mod-list sentinel (GPT A16)*: worth one run per shipped stage, not a recurring suite. It is a release step.
- *Attachment geometry (GPT A10)*: already the AERIAL workstream's job (centroid connectors, bracket planes). Ask
  that workstream to add a state read (connector end point vs footprint centroid, bracket anchor vs wall face) so
  its fix lands with a bar, not only a screenshot.
- *Terminal assignment (owner)*: today strand count is cosmetic (§1). Nothing to test until a design exists; the
  human station should say so in its label (GPT B8 makes the same point).

## 5. User-selectable art: test and human-sheet extension

Applies to design B as ruled (`messyconduit_style_per_build_design.md`, owner decisions at its foot). Nothing here can
run before stage 1 lands; the probe additions are part of each stage, not separate work.

### 5.1 What changes about testing

Today style is a global switch, so one invariant covered it: *after `set:style=X`, every printed mesh carries only
X's textures* (ST2). Per-run style turns it into a per-object property with rules (adopt, merge, split, restyle,
default for unstyled), and the failures move from "wrong texture" to "wrong owner of a texture": a run that disagrees
with itself, a span drawn in the other pole's style, a colour that reshuffles on every rebuild, a style lost at
frame-to-building or reinstall.

### 5.2 Probe additions (one verb each; prerequisite for every check below)

- `runs`: per run, `{run id, cell count, member count by kind, set of StyleDefs on members, colour mode, colour per
  edge, printed material ids per section}`. Every invariant below is a read of this one verb.
- `restyle:<thing id>=<style>[,<colour>]` and `place:<def>@x,z style=<s>` (through the real designator path when
  `mode=blueprint`, straight spawn when `mode=god`).

### 5.3 Invariants to assert (state reads)

| id | invariant | negative control |
|---|---|---|
| SR1 | every run's member style set has exactly 1 element, after every operation | plant a mixed run with a test-only `skipadopt` switch; SR1 must FAIL |
| SR2 | printed materials of each section belong to its run's style (ST2 made per run) | two runs side by side, swap one; the other's material ids must not change |
| SR3 | a span's strand material and both poles' drawn texPaths belong to the run's style; two masts of different styles on ONE map draw different textures (proves `ApplyPoles` is gone) | same scene with both masts one style: textures equal |
| SR4 | **restyle changes art only**: cord geometry hash, edge set, node types and power net ids identical before and after | a deliberate geometry change (add a cell) must change the hash |
| SR5 | merge: the run with more conduit cells wins; tie goes to the older run; one message names both styles | reverse the sizes in a second scene; the winner must flip |
| SR6 | split (deconstruct, fire, explosion): both halves keep the style they had; no member is re-defaulted | — |
| SR7 | Modern 'random' is a mixture (more than 1 colour over the run's edges) and **stable**: the same colour per edge after an unrelated rebuild elsewhere, after a restyle round trip, and after save/load | Modern single colour: exactly 1 colour |
| SR8 | carriage: StyleDef survives blueprint → frame → building, god-mode place, minify/reinstall, copy (gizmo), save/load | an unstyled legacy piece reads null and draws the default |
| SR9 | default setting only moves unstyled runs: `set:style=X` changes the legacy run's materials and leaves every styled run's material ids unchanged | — |
| SR10 | fallback table: every (style, piece) slot resolves to a non-null texture, and the set of slots that resolve to another style's art equals the `U_style_missing_art` table exactly | an art slot known to exist reported as fallback, or the reverse, is a FAIL |
| SR11 | foreign conduit (spawned without the designator, as another mod or a gravship would) adopts its neighbour's style, or the default with no neighbour | — |
| SR12 | removal: a save with styled conduit of all four styles **plus styled blueprints and frames** loads on a tier without the mod; vanilla conduit cell count unchanged, unfinished construction survives or is cleanly dropped, no log line names the mod (M9 extended, rides the existing removal lane) | — |
| SR13 | runs are not power nets: two runs of different styles joined only through a battery stay two runs; restyling one leaves the other's materials unchanged | — |
| SR14 | auto-link joins only same-style runs; a manual cross-style link is a merge and obeys SR5 | auto-link with all styles equal links as today |
| SR15 | patch scope: no `StyleCategoryDef` lists our defs or conduit; with an ideoligion that has style categories active, our getter still returns the picked style; an unrelated styleable building keeps vanilla behaviour | the unrelated building is the control |
| SR16 | legacy look: an unstyled scene's **state fingerprint** (materials per section, geometry hash) is unchanged from today's build. This replaces the design's "screenshot hash" check, which our own rules say is not a verdict | — |

**Contracts to settle before the checks can have expected values** (GPT B1, and true): the equal-size tie (the
owner's card left it open with "use the older run"; "older" needs a definition, e.g. lowest thing id); a placement
that bridges three or more runs at once; two runs of the SAME style but different Modern colours merging; what
'random' means at what grain (per edge, per piece, per cell); and whether HiddenConduit, a switched-off switch and a
cut span end a run. These are owner or design calls, not matrix axes; each is one row once decided.

SR4 and SR7 are the two most likely to find a real bug. Read from code: a net's variant (Modern colour or cable kind)
is `VariantFor(netSeed)`, and `netSeed` is an FNV hash of the **ordinal-smallest end token in the net**
(`RM_MapComponent_CordGraph.ComputeNetSeeds`, union keeps the smaller root). So today, adding one conduit cell whose
token sorts lower, or splitting a run, can recolour the whole run (and both halves of a split get new seeds). With
per-run colour as a stored choice that becomes visible as "I built one cell and my orange run turned blue". SR7's
"stable after an unrelated rebuild" and SR6's "halves keep their look" should therefore include an **extension and
a split of a Modern run**, and the colour should be stored on the pieces (as the style is), never re-derived from the
net seed. This needs no style work to check: it is testable on today's build with `extCordColorMode = Mixed`.

### 5.4 Matrix: economical changes

- **`matrix.py`**: the existing `style` axis (4 levels) changes meaning from "global setting for the case" to "the run's
  style"; add ONE 4-level axis `style_event` = {uniform, bridged_two_styles, restyled, legacy_unstyled} and a 3-level
  `modern_colour` = {single, mixed, random} that is only read when style = Modern. The lower bound stays
  21 topologies x 4 = 84, so pairwise coverage should cost 0 to ~6 extra cases (the greedy search decides; `--prove`
  checks it).
- **`design_spec.py` / `run_live.py`**: assign each of the 109 scenes a run style (round-robin within each block,
  so every topology block shows all four styles). This costs **zero** extra scenes and zero extra bridge minutes,
  and it turns every live board into a four-style side-by-side contact sheet. SR1/SR2 are added to the per-scene
  census check.
- **One dedicated lifecycle scene** (`validation_style.py`, ~10 rows, one quicktest map, ~3 min): place four masts
  through the real designator (two by blueprint and construction, two in god mode); build two runs of unequal size in
  two styles and bridge them; build an equal-size pair and bridge it (tie); split one by deconstruction; restyle;
  minify and reinstall a mast; set Modern random on a run; save and load; read `runs` after every step. Add a
  three-way bridge, two runs joined only through a battery (SR13), a cross-style manual link (SR14), one externally
  spawned conduit (SR11) and four reels laid and reeled. This one scene covers SR1, SR3-SR8, SR11, SR13, SR14. It is
  the stage 1+2+3 checks of the design merged into one scene with stage gates (rows read UNBUILT until their stage
  exists), and it reuses the anchor-lifecycle scene of §4.1 rank 3 for the reinstall half.
- **Offline negative controls** (C# SelfTest, no bridge): feed the run-rule code a planted mixed run, a uniform
  "random" run and a wrong-style material, and require each check to fail (the O3n pattern).
- **Not worth it**: a full 4-style cross of the 109 scenes (436 scenes, ~100 min live) proves nothing the round-robin
  plus SR1/SR2 does not.

### 5.5 Human review sheet (`human_review.py`)

The old rule "one switch for global settings" stops applying to style. Proposed changes:

1. **`--style` becomes "style to build the gallery in"**: stations 1-18 are placed with that style written on them
   (through `place ... style=`), so rebuilding the whole gallery in another style is one command (~1-2 min). The title
   label shows the gallery's style and the default setting separately.
2. **New row E, "STYLES" (6 stations)**. Quartets are per family, not one composite per style, so the same piece
   in four styles sits side by side (the review map's own "neighbours differ in ONE thing" rule; GPT B7-B9 reached the
   same layout):
   - **19 Ground quartet**: the same compact floor build four times: device plugs, junctions, a wall entry, a rock
     entry, a live end and a dead end, one switch.
   - **20 Overhead quartet over a populated room**: per style a mast, a span over a room full of devices with messy
     floor cords, a lamp mast, a bracket on each wall facing, a battery/batten connector, a clamp on a hostile stub.
     One span each with 1, 2 and 3 strands, labelled *strand count is cosmetic; no terminal assignment yet*. This
     also serves the owner's round-2 request for the populated-room image.
   - **21 Reel quartet**: per style one reel stored and one laid (hose flat), plus one plump; inlet continuity and the
     coil overlay are what to judge.
   - **22 Modern colours**: three Modern runs: single colour (brown), mixed (today's look), random (a mixture inside
     one run). A fourth run labelled *build one conduit here to extend it* shows colour stability (rank 2).
   - **23 Merge, split, restyle**: two runs, Industrial (12 cells) and Scrapper (5 cells), with one missing cell
     labelled *build one conduit here*; an equal-size pair beside it for the tie; a run labelled *deconstruct the
     marked cell* for the split; a run labelled *select any piece, press Restyle this run*.
   - **24 Art slots board**: every styled piece (live end, dark strip, switch on/off, clamp, reel stored/laid, hose
     flat/plump, 5 hose pieces) in a 4-column grid, one column per style; each fallback labelled in world with the
     requested style and the style actually drawn. Missing art is judged knowingly, and the board shrinks as stage 4
     art lands.
   Not style work but owed to the same sheet (SHEET workstream): a mountain-and-fog station (aerial through heavy
   rock) and the hose maze station of §4.1 rank 1.
3. **Legacy run**: one unstyled run beside station 19 (built with no style), labelled *older save: follows the default
   setting*, so `--style-default X` can be seen moving it and nothing else.
4. **Free area**: unchanged; the owner tests the build-button menu himself there, which is the one thing only a
   human can judge (does the 4-item menu read clearly, does the cursor say "joins Industrial run").
