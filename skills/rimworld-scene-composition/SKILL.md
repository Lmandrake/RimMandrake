---
name: rimworld-scene-composition
description: Make a scattered/scenic site (a ruin, a bone field, a wreck, a camp) read as ONE authored place at a glance instead of a props bag, using verticality tools (SimpleStairs, Simple Visual Stairs, Decorative Cliffs) and set-dressing principles, then grade the result against five named metrics with a critical-reviewer pass. Use whenever authoring a rimplace template, KCSG structure, or any scattered/decorative site content; whenever a built scene "just looks like items on the ground" or has a part that reads as bizarre/disconnected; before shipping any stairs, cliff, or raised/lowered platform; and whenever scoring a screenshot of built content.
---

# Scene composition — reading as a place, not a props bag

**Owner's founding complaint, 2026-09-06, looking at this project's own first attempt:**
*"The waste camp barely reads as anything more than some items on the ground, not
inspiring at all. Boneyard is incoherent due to two skulls present."* That is the
failure mode this skill exists to catch, and it is caught by LOOKING at a screenshot,
never by reading a def dump — see `rimworld-debug-testing` §4a for why a screenshot is
observation and everything else is inference.

## 0. The tools this skill assumes are active

Three mods, added 2026-09-06 for exactly this work. Confirm they're in the live mod
list before using their defNames (`grep <packageId> ModsConfig.xml`); none has a C#
assembly, none has a hard dependency.

| mod | packageId | what it actually is |
|---|---|---|
| **SimpleStairs (Fork)** | `rw.mod.simplestairs` | `Gomi_SimpleStair` (Standable, `altitudeLayer=FloorEmplacement`, stuff-based) + `Gomi_Handrail`/`Gomi_HighWall`/`Gomi_FloorFence` (linked/auto-tiling). 🔑 **The mod author's own words: "a staircase that looks like there is a difference in height."** It is a visual lie with zero mechanical backing — no real elevation, no changed pathing cost beyond what any floor gives. |
| **Simple Visual Stairs** | `Kutte.Stairs` | `REIK_Stairs_Straight`/`_Corner`/`_Straight_Two`/`_Corner_Two`/`_Corner_Three`. Author's words: **"no costs, nothing fancy just for visuals."** Same deal — a floor decal, not a mechanism. |
| **Decorative Cliffs (Continued)** | `Mlie.DecorativeCliffs` | Already active. Pure XML, `DecorativeCliff` designation tab. Four material families (Stone/Brick/Smooth/Metal) + Dirt hills, each shipped as **face + top pairs** (`Stone_Cliff_Right/Left` = the vertical face, `Stone_CliffTop_Right/Left` = the plateau surface behind/above it) with `Graphic_Single` + `CornerFiller` linking for edge-blending between adjacent same-def pieces. **No procedural placement logic exists in the mod at all** — every cliff you will ever see from it is hand-placed, by you, cell by cell. |

⚠️ **Because none of these three mods has a real elevation mechanic**, every "level
change" this skill produces is 100% illusion, sold entirely by which pieces sit next
to which other pieces. That is not a limitation to work around quietly — it is the
central fact that governs every rule below.

## 1. The one sentence this skill is built to enforce

**A stair is a claim about what is on both sides of it, and a cliff face is a claim
about what is above and below it.** Since the mods that make these pieces cannot check
that claim for you, you must satisfy it by construction, every time:

- 🔴 **Never place a stair on open, uniform ground with nothing at either end.**
  It must terminate against something that *already* signals a level change: a cliff
  face piece, a distinct floor-material change (dirt → cut stone, sand → plating), or
  a foundation/wall edge. A stair floating in the middle of a flat field reads as
  exactly what it is — a prop with no reason to exist — because there is no "up" or
  "down" on either side of it for the eye to resolve.
- 🔴 **Always place a cliff's face and top pieces together, face below/in-front, top
  behind/above.** A lone face piece with ordinary floor behind it reads as a wall
  standing in a field, not a plateau edge — the TOP piece is what tells the eye
  "there is more raised ground back there," and the mod ships both halves precisely
  because neither one alone completes the claim.
- 🔴 **Decorative Cliffs pieces only link into a solid face along a HORIZONTAL run
  (same z, varying x) of the same defName.** Live-tested 2026-09-06: a VERTICAL
  column (fixed x, varying z) of `Dirt_Hill_Right` rendered as a broken, disconnected
  zigzag/ladder shape — bizarre and clearly a defect, not a dune. The identical pieces
  placed as a horizontal row linked into one continuous mound. `Graphic_Single` +
  `CornerFiller` evidently blends adjacent SAME-row neighbors, not same-column ones.
  **Orient every cliff/hill run east-west, never north-south**, until a counter-example
  is found and recorded here.
- 🔴 **A terrain-type boundary must be JAGGED, never a straight or rectangular line.**
  A ruler-straight edge between two floor types (or a rectangular "cleared zone" left
  behind by a scatter template's own CLEAR step) reads as a UI grid or a foundation
  slab, not a natural landform. Stagger the boundary by 1–2 cells at irregular
  intervals; the irregularity IS the naturalism.

## 2. Elevation is the cheapest way to make a small site feel authored

Independently confirmed by both this project's own experience and outside
environmental-storytelling sources: **a one-tile rise, a shallow dug-in pit, or a
single stair down** is the lowest-cost signal available that a location was placed on
purpose rather than dropped flat onto the map. It works because it forces the site to
have a *boundary* — the moment the ground itself changes, the eye registers "this is a
place," before it has looked at a single prop inside it.

⇒ **Before adding one more prop to a scene that "isn't reading," ask whether the
ground plane itself has changed at all.** The Waste Camp's founding failure was
exactly this: every prop was individually fine (a real def, correctly placed, not
overlapping), and the whole scene still read as litter, because the dirt under it was
identical to the dirt for 40 tiles in every direction. A camp whose floor is sunk one
cell into the surrounding grade — even without a single stair or cliff piece — already
reads more as "a place" than the same props on flat, undifferentiated ground.

## 3. A prop scene needs an implied structure, not scatter-brush density

Set-dressing across every game-design source found on this (2026-09-06 web research;
RimWorld-specific doctrine is thin to nonexistent on this exact question, so this
leans on general environmental-storytelling principles): **a scene is readable when
the props sit INSIDE or AROUND an implied shape, and unreadable when they sit at even
density with no shape at all.**

- A camp needs an implied footprint: a hearth reads as a hearth because it is a RING
  or a cluster with something at its center, not props sprinkled independently around
  a point. A collapsed shelter reads as a shelter if its frame pieces still trace the
  wall/doorway it used to have — even collapsed and askew, the pieces should describe
  a shape a viewer could re-draw the missing walls onto.
- 🔑 **A skeleton or corpse pile is not a props bag — it is ONE dead body.** Skull at
  one end, spine/ribcage as the visual backbone of the whole composition, everything
  else trailing consistently outward from that line in a single directional sprawl —
  "a kill happened here and something settled/dragged it," never an even scatter of
  bone-type props at uniform density. **This project's own Boneyard defect was exactly
  a violation of this rule**: the skull sat 5 cells from the ribcage, bridged by a
  single thin neck-bone, which read as visually disconnected enough to look like a
  SECOND skull/animal rather than the same one's head — see §6.

## 4. The five scoring metrics

Score every built scene, per screenshot, on these five, each 1–5. This is the rubric
a critical-reviewer pass (§5) grades against — write the score AND a one-line reason
for each, because the reason is what improves the next iteration, not the number.

| # | metric | 1 (fails) | 5 (excellent) | what it is NOT |
|---|---|---|---|---|
| 1 | **Relevance to intent** | Nothing here matches the design brief (e.g. narrative in an item's spec) | A viewer who read the brief would recognize this as its depiction | NOT "does every prop from the brief appear" — a smaller, tighter scene that nails the FEELING beats a checklist scene that doesn't |
| 2 | **Visual recognizability** | Cannot tell what this is meant to be without being told | Instantly identifiable as its subject (a ruined camp, a dead beast, a wreck) at normal play zoom, no caption needed | NOT resolution/sprite quality — a technically crisp scene can still fail this if its SHAPE doesn't read |
| 3 | **Visual coherence** | Contains something bizarre or nonsensical (floating disconnected pieces, an object that implies a second unrelated thing, an impossible arrangement) | Every element's presence and position makes sense together; nothing needs an explanation | NOT "is it realistic" — a fantastical scene can be fully coherent; an ordinary one can still be incoherent (two skulls) |
| 4 | **Interest** | Flat, forgettable, no reason to stop and look | Draws POSITIVE attention — a viewer would screenshot it or want to explore it | NOT "is it busy" — restraint can be more interesting than clutter |
| 5 | **Distraction/defect** (score is "how CLEAN," 5 = no defects) | Something visibly stands out as wrong — a render glitch, a misplaced prop, ground that clashes, an obvious tiling seam | Nothing pulls the eye away from the intended read | The inverse of the others: this metric exists to catch what a "does it look good overall" score can hide inside an average |

**Gate**: nothing ships as a finished promise/whisper below a 3 on ANY metric.
A scene can be simple and still pass every metric; it cannot be impressive on four and
broken on the fifth and call itself done — metric 5 exists precisely so a single loud
defect cannot hide inside a good average.

## 5. The critical-reviewer pass — how to run it

Don't self-grade only. After building and screenshotting (per `rimworld-debug-testing`
§4a: clear the debug log, unique screenshot filenames, look at the actual image), spawn
a **fresh** reviewer agent — fresh context matters, because you already know what you
meant to build and cannot un-know it. Give it:

1. The screenshot(s), read via the `Read` tool so the review is grounded in the actual
   pixels, never a description of them.
2. The ORIGINAL design intent (the one or two sentences that started the build), so
   metric 1 has something to grade against.
3. The five metrics table above, verbatim — do not let the reviewer invent its own
   rubric.
4. An explicit instruction to name what specifically drove any score below 4, not just
   the number — "the skull reads as a second animal because it sits 5 cells from the
   ribcage with nothing visually bridging them" is usable; "coherence: 3" is not.

Treat the reviewer's low scores as work orders, not opinions to weigh — a fresh set of
eyes catching "this reads as two skulls" is exactly the failure mode a builder who
already knows it's one animal cannot self-detect. Iterate: fix, rebuild, re-screenshot,
re-review, until every metric clears the gate in §4.

🔴 **But verify a reviewer's low score before acting on it, the same way you'd verify
your own claim — a fresh reviewer has a failure mode too.** Live-caught 2026-09-06: a
critical-reviewer pass scored Waste Camp 2/5 on every metric, describing a tent-pole
frame and a dark "collapsed mass" sitting 15-20 tiles from the actual sunken pit. On
inspection those objects were a large ambient decoration and a pre-existing map prop
that happened to sit in the same wide screenshot — NOT anything the template placed.
The reviewer had no way to tell "built by this template" from "already on the
quicktest map" from a wide shot, and reasonably scored what it saw. **Fix: frame the
screenshot tightly enough to exclude ambient map scatter, or tell the reviewer
explicitly which defNames belong to the build**, before trusting a low score as a
real defect. A reviewer's job is to catch what the builder can't self-see, not to
replace checking the claim — the same discipline `verify-before-you-escalate` asks
of everything else in this project.

## 6. Worked example — two rounds so far, and what's still open

Recorded so the next builder does not re-discover any of this the slow way. Status as
of 2026-09-06, end of round 2 (a fresh critical-reviewer pass, §5).

- **Waste Camp** (`design/Jawa/templates/waste_camp.lua`) — ROUND 1 fix: sank the
  camp's floor into a jagged, non-rectangular pit and clustered every prop inside it
  (§2/§3). ROUND 2 finding: a critical-reviewer pass scored this 2/5 across the board,
  but on inspection the reviewer had mistaken nearby AMBIENT MAP SCATTER (unrelated to
  this template) for the camp's own tent frame — see §5's verification note. The pit
  and props ARE correctly co-located. **Still genuinely open**: the pit's own edge
  reads as subtle ("a flat, near-rectangular patch of slightly lighter soil" per the
  reviewer, before the misattribution) — the jaggedness needs to read more strongly
  at normal play zoom, and someone needs to re-review with a tightly-framed shot that
  can't be confused with the map's own furniture.
- **Boneyard** (`design/Jawa/templates/boneyard.lua`) — ROUND 1 fix: closed the
  skull-to-ribcage gap to zero (was 5 cells). ROUND 2 finding, CONFIRMED by a fresh
  reviewer independent of the round-1 fix: a bone-fragment prop (`AB_AncientBrokenBone`
  or `AB_AncientVerticalBone` — not yet pinned down to one) sitting at the tail's far
  end has its OWN sprite art close enough to the real skull's that it still reads as
  "a second head" even though only one true skull object exists — confirmed by direct
  game-data query. **Two items still open**: (1) swap or remove that tail-end prop so
  its silhouette doesn't echo the skull's; (2) the tree (`TreeDead`, the silverbole
  stand-in) still does not spawn via the live bridge path at all — a silent failure,
  same class as `waste_camp`'s mined-rock CLEAR gap, root cause not yet found (a
  terrain-fertility refusal is the leading theory, unconfirmed).
- **Long Crossing** (`design/Jawa/templates/long_crossing.lua`) — ROUND 1 added a
  Decorative Cliffs dune-lip as a VERTICAL column, which rendered as a broken zigzag
  (§1's horizontal-run finding) — fixed by reorienting to a horizontal row, confirmed
  live to link into one solid mound. ROUND 2 finding: even linked correctly, a
  ONE-CELL-THICK horizontal run reads as a wooden fence rail, not an earthen dune — a
  dune needs BULK (multiple rows of depth), not just correct linking. **Still open**:
  widen the dune to 2-3 rows deep; also the sand-drift chance function varies only
  with x (distance from the hull), never z, so it paints a uniform band across the
  WHOLE rect regardless of whether the hull is even at that z-row — it needs to taper
  in z too, or be masked to the hull's own z-span, so it reads as caused by the truck
  specifically rather than an unrelated background gradient.

## 7. Process for this whole skill going forward

1. Build offline first (rimplace `lint`/`render`/`verify` — no game needed for the
   mechanism, per the `rimplace` README).
2. Prove it live on a quicktest (`rimworld-debug-testing`) — a disposable map is fine,
   nothing here needs the real campaign world.
3. Screenshot per `rimbridge` §4a discipline (clear UI, unique filename, jump camera,
   reasonable zoom to see the WHOLE footprint, not just its center).
4. Run the critical-reviewer pass (§5) against the five metrics (§4).
5. Fix the named defects, not a guess at what might be wrong — rebuild, re-screenshot,
   re-review.
6. Stop iterating once every metric clears the gate, or once returns are visibly
   diminishing — say so explicitly rather than iterating forever on diminishing
   returns; note what's left undone and why, per the threshold-discipline doctrine in
   `rimworld-debug-testing` §9.

## Keeping this skill honest

Every rule above traces to either a real defect this project shipped and had pointed
out (Waste Camp, Boneyard) or an external, cited source (§1–3's game-design research,
2026-09-06 — RimWorld-specific doctrine on this exact question was confirmed thin to
nonexistent, so most of this leans on general tile-game/environmental-storytelling
principles, flagged as such rather than presented as RimWorld fact). When a new defect
is found by a critical-reviewer pass, add it here with its evidence, the same way
`rimbridge`'s traps file grows.
