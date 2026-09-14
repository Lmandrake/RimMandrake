# Pit trap visual interface — design spec (PIT_TRAP_VISUAL_REDESIGN_1)

For the owner's Thursday sitting. Owner's ask, verbatim (2026-09-13): *"we need
to think now about very deeply what it looks like. It can't just be a simple
trap graphic you get stuck on. So we need a big dark pit... thoroughly dream up
the interface for this."*

Scope: the LOOK and player interface of `RimMandrake.Pits` (RM_OpenPit_* traps,
RM_PitCell_* prisoner pits). Mechanism design is settled
(`design/Jawa/covered_pit_traps_spec.md`); this spec proposes what the player
sees, marks every element BUILDABLE-AS-XML or NEEDS-C#, and ends in three
candidate directions with a recommendation. Implementation is a follow-on build
item once the owner picks.

Every mechanism named here was verified against decompiled 1.6 source
(RimSage) or the mod's own code on 2026-09-14; file:line cites are given where
it matters.

---

## 0. One fact that dissolves the central tension

**Raiders and animals never see pixels.** Whether a hostile walks onto a trap
is decided entirely by game logic — vanilla's `Building_Trap.KnowsOfTrap`
(`RimWorld/Building_Trap.cs:143-178`) is a pile of faction/state checks plus a
per-lord random roll; our pits' `CompPitCoverTrigger` likewise springs on
summed mass, not vision. Rendering is one screen, drawn once, for the player
only.

So "covered must read to the PLAYER but not to raiders" is **not a rendering
problem at all**. Any tell we draw is mechanically free — it costs nothing in
trap effectiveness. The only real constraints on the covered look are:

1. **Fiction** — it should look like something a sharp-eyed Jawa knows about
   and a charging raider plausibly misses (subtle, not a painted X).
2. **The owner's own ruled design** (2026-08-30, covered_pit_traps_spec.md §3)
   — covered pits mimic terrain. That ruling stands; the options below add a
   tell ON TOP of the mimic, they never replace it.

Vanilla's second relevant precedent: deep ore deposits render **only while a
scanner/drill is selected** (`Verse/DeepResourceGrid.cs:106-118`). Player-only,
context-conditional display is an established vanilla pattern, not a hack.

## 1. The states the thing actually has

From `Building_OpenPit.cs` (read in full): `covered` is a bool, `Sprung` means
the container is non-empty, and the arm gizmos only appear when
`!covered && !Sprung` — so **covered+occupied cannot occur**, and "re-covered"
is identical to "covered". The real state inventory:

| # | State | Today | Should read as |
|---|-------|-------|----------------|
| S1 | Being dug (`Building_PitDigSite`, staged) | dig-site placeholder | a growing spoil mound / deepening scrape |
| S2 | Open + empty ("the big dark pit") | vanilla 64px spike-trap icon | a hole: dark mouth, earthen rim, fitting visible at the bottom |
| S3 | Covered / armed | pixel-perfect terrain mimic, **no tell** (`TerrainMimicPrinter`, confirmed: prints the TerrainDef's own material per cell, nothing else) | invisible at combat zoom; findable by its own player at close zoom |
| S4 | Sprung + occupied | same graphic as S2; first pawn drawn at `DrawPos.y − 0.05` | someone visibly DOWN THERE, struggling |
| S5 | Occupant died inside | **renders as empty** — `HeldPawn` only matches live `Pawn` objects (`Building_OpenPit.cs:66-77`); a Corpse in the container draws nothing | needs a ruling: eject the corpse on death, or show a grim tell (see §6) |
| S6 | Per-fitting bottoms (Bare/Spiked/Oiled/Poison/Water/Oubliette) | all six inherit the same placeholder | the fitting IS the bottom of the hole — visible only when open |

## 2. The big dark pit (S2) — how to fake depth top-down

Vanilla already ships the canonical answer: Anomaly's **PitGate** — an 8x8
`Graphic_Single` with `drawSize (8,8)` at `altitudeLayer FloorEmplacement`,
whose entire depth read is painted into one texture. The grammar, readable in
that art and standard for top-down holes:

- **Near-black mouth** — the center is flat, very dark, low-detail. Darkness
  *is* the depth cue; any visible floor detail flattens it.
- **One lit inner-wall strip** along the top (north) inner edge — the far wall
  catching overhead light. This single band is what turns a dark disc into a
  hole.
- **Disturbed-earth rim** — a lighter, rougher ring of spoil just outside the
  mouth, breaking the terrain texture so the hole feels dug, not decaled.
- **Slight overhang**: `drawSize` a touch larger than footprint so the spoil
  rim bleeds over surrounding cells. `<drawSize>` is plain GraphicData XML
  (PitGate uses it) — **BUILDABLE-AS-XML**.

Altitude: move pits from `<altitudeLayer>Building</altitudeLayer>` to
**`FloorEmplacement`** (PitGate's layer, value 7 vs Building's 15 in
`Verse/AltitudeLayer.cs`). A hole should sit under filth, items and every pawn;
today's Building layer is why anything on the cell fights the graphic.
BUILDABLE-AS-XML, one line — but re-verify the terrain-mimic print altitude
still wins over terrain after the change (mimic prints at `thing.DrawPos.y`,
which follows the layer).

**"Big":** a 1x1 pit can read *dark* and *deep* but never *big* — 128 screen
pixels at mid zoom is the physics of it. The honest lever for "big" is the 2x2
pit (§5). At 1x1 we buy apparent size with drawSize 1.5 (rim overhang) and
maximum value contrast against Pyrelands ochre.

**Palette** (Pyrelands/desert ground is light warm ochre — high contrast comes
free): mouth `#1a120c`–`#241812` near-black umber; lit wall strip burnt sienna
`#7a4a2a`; spoil rim dry sand `#c9a06a` roughened with `#8a6a42` clods. Warm
browns throughout — nothing cool/grey, this is dug desert earth, and it sits
comfortably in the owner's preferred warm-brown range.

## 3. Covered (S3) — the player-facing tell

The mimic stays (owner's ruling). Three tell options, cumulative not exclusive:

- **T1 — baked seam decal.** One extra plane printed over the mimic: a ~12%
  alpha texture of hairline cracks and four corner pegs, invisible at combat
  zoom, readable when zoomed to a pawn. This is exactly the
  covered_pit_traps_spec §3 line ("slight seam/discoloration at high zoom")
  that was specced and never built. **NEEDS-C#, tiny**: one more
  `Printer_Plane.PrintPlane` call inside the existing
  `TerrainMimicPrinter.PrintTerrainMimic` loop, one 256px tileable texture.
- **T2 — selection reveal.** While any pit (or the arm gizmo's owner) is
  selected, draw a thin outline on every covered pit on the map — the
  DeepResourceGrid pattern cited in §0. **NEEDS-C#** (new overlay code, still
  small). Best quality-of-life once the owner fields trap FIELDS rather than
  single pits; not needed for v1.
- **T3 — nothing** (status quo). Player finds own traps by click/memory only.
  Cheapest and already true; the owner has already called the result
  unsatisfying implicitly by asking "how does it show covering yet?"

Recommendation inside this axis: **T1 now, T2 when trap counts grow.**

## 4. Occupied (S4) — someone is down there

What the engine actually offers (all verified):

- `IThingHolderWithDrawnPawn` draws exactly ONE held pawn, at the y our
  building returns (`PawnRenderer.cs:459-463`). Vanilla uses both directions:
  holding platform/growth vat draw the pawn **above** the building
  (`DrawPos.y + 0.0366`), the biosculpter pod draws it **below** and lets the
  pod art with a transparent window occlude it
  (`CompBiosculpterPod.cs:236`). One altitude step is `Altitudes.AltInc =
  0.03658537`.
- Our pit currently draws the pawn below (`SunkenYOffset = −0.05f`) — the
  biosculpter pattern — so **an opaque-centered pit texture would hide the
  occupant entirely.** Whatever direction is picked must keep texture opacity
  and pawn altitude consistent; this is the one place "just swap the texture"
  breaks a mechanic.
- There is no stencil/mask clipping for pawns. The only real "pawn cut off at
  the waist by the pit mouth" mechanism is the sandwich: pawn drawn BETWEEN a
  lower floor plane and an upper rim plane whose center is alpha-cutout
  (transparent pixels don't occlude; opaque rim does). All planes are
  `Printer_Plane` calls we already make — **NEEDS-C#, but it is the same API
  the mod already uses**, no Harmony, no shaders.
- **Posture:** keep `PawnPosture.LayingOnGroundFaceUp` — top-down, a supine
  pawn framed by a dark mouth reads instantly as "in the hole."
- **At-a-glance empty-vs-occupied** (item §4): the pawn itself is the primary
  signal; reinforce with dust/struggle motes thrown from
  `RunStruggleInterval` (a hook that already exists and fires on the escape
  cadence — `FleckMaker.ThrowDustPuff`, ~3 lines, **NEEDS-C#, trivial**).
  Motes also solve the "is that pawn IN the pit or standing on it" ambiguity
  at far zoom.

## 5. Size — the 2x2 stance

Measured in the item file and re-confirmed: occupancy, trigger scan and mimic
are already footprint-generic; a 2x2 trap def is XML-only. Two visual gaps:

1. **drawSize** — no pit def sets it, so any multi-cell def draws its texture
   in one corner. Newly measured this pass: the SHIPPED 2x2/1x2 cell defs
   (`Pit_Cell.xml` — `RM_PitCellBase` and both children) have no drawSize
   either, so the existing prisoner pits are corner-drawing today.
   **BUILDABLE-AS-XML, fix now regardless of direction.**
2. **Second occupant never renders** (`IThingHolderWithDrawnPawn` is
   single-pawn by interface shape). A 2-capacity pit shows one prisoner while
   holding two. Rendering a second pawn means bypassing the interface and
   drawing via `pawn.Drawer.renderer` manually in `DrawAt` — no verified
   vanilla precedent, **NEEDS-C#, the riskiest item in this spec.**

**Stance offered for ruling:** v1 ships 1x1 trap pits with real art plus the
drawSize fix on the existing cell defs; the 2x2 TRAP pit ("the big dark pit"
in its literal, room-swallowing sense) becomes its own build item gated on the
multi-occupant rendering decision — either build the manual second-pawn draw,
or ship 2x2 with capacity 1 and honest flavor ("wide enough that one victim
can't brace the walls"), which needs zero new C#. The capacity-1 dodge is the
cheap path to "big" that keeps every renderer vanilla-shaped.

## 6. Corpse-in-pit (S5) — needs one ruling

A pawn that dies in the pit leaves the pit rendering as empty while the
inspect string still counts an occupant. Options: (a) eject the corpse on
death (`Building_Casket`-style, small C#), keeping the pit visually honest and
the body haulable; (b) draw a corpse decal / blood pool overlay. Recommend
**(a) eject** — cheapest, no art, and a body beside a dark pit is better
Pyrelands storytelling than one invisible inside it.

## 7. The three directions (cards)

### Direction A — Painted Hole
One finished composite texture per pit variant: rim, lit wall, dark mouth and
the fitting all painted into a single `Graphic_Single`. Flip `SunkenYOffset`
positive (one constant) so the occupant draws on top of the mouth, holding-
platform style. Tell: T3 (none) or T1.
**Trade: shippable in days, all-XML plus one constant — but the occupant lies
ON the dark disc rather than IN it, and six variants means six full repaints
whenever the look changes.**
Sprites: 6 variant composites (1x1, drawSize 1.5 → author 256px per the
enhanced-zoom advisory; 192px is the strict drawSize×128 floor), 1 cell 1x2
(drawSize 1.5x2.5 → 256x448), 1 cell 2x2 (drawSize 2.5 → 448px), optional T1
seam 256px. **Total 8-9 textures.**

### Direction B — Layered Well  ← recommended
`Print()` lays a sandwich: fitting floor plate at the bottom, held pawn above
it (existing −0.05 draw), shared rim plane on top with alpha-cutout mouth.
The rim genuinely clips the occupant's edges — the only real "down inside it"
read the engine can produce — and fittings become cheap floor plates under a
shared rim instead of six repaints. Tell: T1 baked in (one more plane in the
same loop).
**Trade: the best depth illusion and the cheapest art per variant — but it's a
contained C# print pass (same Printer_Plane API the mimic already uses), so
it lands next build cycle, not this week.**
Sprites: rim 1x1 + rim 2x2 (256 / 448px, cutout centers), 6 fitting floor
plates (128px, mouth-sized), T1 seam (256px), optional dark gradient ring for
the mouth wall (256px). **Total 10-11 textures, but variants share the
expensive ones.**

### Direction C — Marked Ground
Direction A's cheap painted hole, plus T2: a player-side overlay that outlines
every covered pit while any pit is selected (DeepResourceGrid pattern). Spends
the C# budget on INTERFACE rather than rendering depth.
**Trade: the best experience for managing a FIELD of traps — but the pit
itself stays Direction A's flatter look, and overlay UI is new code with no
existing hook in the mod.**
Sprites: Direction A's list + 1 overlay outline atlas. **Total 9-10.**

**Recommendation: Direction B**, with T1 as the covered tell, mote puffs on
struggle, corpse-eject, the cell-def drawSize fix immediately, and the 2x2
trap pit filed as its own gated item per §5. Direction A is the fallback if
Thursday's ruling is "I want it in the game this week." C's overlay folds into
either direction later without rework — it is deferrable, not exclusive.

## 8. Mockup loop (per the item's own process requirement)

Owner rules on direction Thursday from THIS document; then, per his standing
design loop, the build item opens with **offline PNG mockups** — the chosen
direction rendered over a captured Pyrelands terrain screenshot at three
vanilla zooms (empty / covered / occupied side by side), he picks, then the
palette pass. No in-engine work before a mockup is picked. Art generation goes
through `generating-rimworld-sprites` (alpha-safe, canvas-validated); new
texPaths are mod-local (e.g. `Pits/OpenPit_Rim`), NEVER the vanilla
`Things/Building/Security/TrapSpikeArmed` path (see item Watch-out — editing
that skins every vanilla spike trap).

## 9. Scope ledger

| Element | Scope |
|---|---|
| drawSize on all multi-cell defs | BUILDABLE-AS-XML — do now |
| altitudeLayer → FloorEmplacement | BUILDABLE-AS-XML — verify mimic after |
| New textures, per-variant overrides | BUILDABLE-AS-XML |
| A: pawn-above flip | NEEDS-C# (one constant) |
| B: print sandwich | NEEDS-C# (contained, existing API) |
| T1 seam plane | NEEDS-C# (one PrintPlane call) + 1 texture |
| T2 selection overlay | NEEDS-C# (new UI code) — deferrable |
| Struggle motes | NEEDS-C# (trivial, hook exists) |
| Corpse eject on death | NEEDS-C# (small) |
| Second-occupant rendering | NEEDS-C# (novel, no vanilla precedent) — gate 2x2 traps on it or ship capacity-1 |
| Dig-site staged art (S1) | separate follow-on; per-stage graphic swap needs C# — out of this ruling |
