---
name: rimworld-scene-composition
description: Make a scattered/scenic site (a ruin, a bone field, a wreck, a camp) read as ONE authored place at a glance instead of a props bag, using verticality tools (SimpleStairs, Simple Visual Stairs, Decorative Cliffs) and set-dressing principles, then grade the result against five named metrics with a critical-reviewer pass. Use whenever authoring a rimplace template, KCSG structure, or any scattered/decorative site content; whenever a built scene "just looks like items on the ground" or has a part that reads as bizarre/disconnected; before shipping any stairs, cliff, or raised/lowered platform; and whenever scoring a screenshot of built content.
---

# Scene composition — reading as a place, not a props bag

**Owner's founding complaint, 2026-09-06.** He looked at this project's own first attempt.
*"The waste camp barely reads as anything more than some items on the ground, not inspiring at all. Boneyard is
incoherent due to two skulls present."*

This skill exists to catch that failure: a scene that reads as loose props. Only a LOOK at a screenshot catches that
failure. A def dump never shows it. `rimworld-debug-testing` §4a says why a screenshot is observation and other evidence
is inference. Evidence, dates and corrected lines: [references/history.md](references/history.md).

## 0. The tools this skill assumes are active

This work uses three mods. None of them has a C# assembly, and none has a hard dependency. Before you use a defName of
one of them, confirm that the mod is in the live mod list. Parse `activeMods` of `ModsConfig.xml`, and compare the
packageIds in lower case. The file writes each id in lower case, so a search for `Kutte.Stairs` finds nothing.

Decorative Cliffs and Simple Visual Stairs are in `ModsConfig.FULL.LATEST.xml`, and SimpleStairs is not. All three are
in `ModsConfig.MINIMAL.xml` (both lists are in `infrastructure/state/modlists/`, read 2026-11-23).

| mod | packageId | what it actually is |
|---|---|---|
| **SimpleStairs (Fork)** | `rw.mod.simplestairs` | `Gomi_SimpleStair` is Standable, uses `altitudeLayer=FloorEmplacement`, is made from stuff, and adds no path cost. `Gomi_Handrail`, `Gomi_HighWall` and `Gomi_FloorFence` are linked pieces (they join their neighbours automatically). The linked pieces slow a pawn and give some cover. 🔑 **The mod author's own words: "a staircase that looks like there is a difference in height."** The stair has no real elevation. |
| **Simple Visual Stairs** | `Kutte.Stairs` | `REIK_Stairs_Straight`/`_Corner`/`_Straight_Two`/`_Corner_Two`/`_Corner_Three`. The author's words: **"no costs, nothing fancy just for visuals."** (Neither author quote is in the installed files; see the history.) Each piece lies on the floor, not on a level, and has `pathCost` 20. |
| **Decorative Cliffs (Continued)** | `Mlie.DecorativeCliffs` | Pure XML, with its own `DecorativeCliff` tab in the architect menu. Four material families (Stone, Brick, Smooth, Metal) and Dirt hills. Each family has four pieces. Two pieces are the **face**, for example `Stone_Cliff_Right/Left`: the vertical front. Two pieces are the **top**, for example `Stone_CliffTop_Right/Left`: the back edge of the plateau. The pieces use `Graphic_Single` with `CornerFiller` links, which join neighbour pieces. The cliff pieces slow a pawn (`pathCost` 90) and give cover. **The mod has no procedural placement logic at all.** You place every cliff by hand, cell by cell. |

⚠️ **None of these three mods has a real elevation mechanic.** So every "level change" that this skill makes is 100%
illusion. Only the choice of which pieces sit next to which other pieces sells that illusion. Do not work around this
quietly: it is the central fact behind every rule below.

## 1. The one sentence this skill is built to enforce

**A stair is a claim about what is on both sides of it, and a cliff face is a claim about what is above and below it.**
The mods cannot check that claim for you. So make the claim true by construction, every time:

- 🔴 **Never place a stair on open, uniform ground with nothing at either end.**
  - The stair must end against something that *already* signals a level change:
    - a cliff face piece;
    - a distinct change of floor material (dirt to cut stone, sand to plating);
    - the edge of a foundation or wall.
  - A stair in the middle of a flat field reads as a prop with no reason to exist. Neither side gives the eye an "up" or
    a "down".
- 🔴 **Always place a cliff's face and top pieces together, with the face below (in front) and the top above (behind).**
  - On the map, "above" and "behind" are north, which is a higher z.
  - A face piece alone, with ordinary floor behind it, reads as a wall in a field. Such a piece does not read as the
    edge of a plateau. The TOP piece tells the eye "there is more raised ground back there," behind the face. The mod
    ships both halves because neither half completes the claim alone.
  - Do not put the top row south of the face row. Then the face draws small posts and the top draws a thin rail with
    posts. Such a rail is the picture of a fence. (Source: the mod's texture sheets, not a live test.)
- 🔴 **Orient every cliff or hill run east-west (same z, different x). Never use a north-south run (same x, different z)
  as a face.**
  - In a live test (2026-09-06), a north-south column of `Dirt_Hill_Right` drew a broken, disconnected zigzag or ladder
    shape. The shape is bizarre and clearly a defect, not a dune. The same pieces in an east-west row linked into one
    continuous mound.
  - The pieces do link in both directions, and any two cliff pieces link, whatever their defName. The probable
    cause is the texture sheet. In an east-west run, each cell draws the full front face. In a north-south run, each
    cell but the south end draws a thin side edge (read from the sheet).
  - This rule holds until someone finds a counter-example in a live test and files it as a lesson. A closed outline,
    with side edges that join a face row and a top row, is a likely counter-example. Nobody has tested one.
- 🔴 **Make a terrain-type boundary JAGGED, never a straight or rectangular line.**
  - A ruler-straight edge between two floor types reads as a UI grid or a foundation slab. The line does not read as a
    natural landform. A rectangular "cleared zone" reads the same. The CLEAR step of a scatter template leaves such a zone.
  - Move the boundary by 1–2 cells at irregular intervals. The irregularity is what looks natural.

## 2. Elevation is the cheapest way to make a small site feel authored

**A one-tile rise, a shallow dug-in pit, or a single stair down** is the cheapest signal that someone placed a location
on purpose. Without that signal, the location looks dropped flat onto the map. The signal works because it gives the
site a *boundary*. When the ground itself changes, the eye registers "this is a place," before it looks at one prop.
This project's own experience and outside sources on environmental storytelling agree, independently.

**Before you add one more prop to a scene that "isn't reading," ask one question. Has the ground plane itself changed
at all?**

- The Waste Camp failed in exactly this way. Every prop was fine on its own: a real def, correctly placed, with no
  overlap. The whole scene still read as litter. The dirt under it was the same as the dirt for 40 tiles in every
  direction.
- Sink a camp floor one cell below the ground around it. Then the camp already reads more as "a place" than the same
  props on flat, undifferentiated ground. No stair or cliff piece is necessary.

## 3. A prop scene needs an implied structure, not scatter-brush density

**A scene is readable when the props sit INSIDE or AROUND an implied shape. A scene is unreadable when the props sit at
even density with no shape at all.** Every game-design source that web research found on this says so. RimWorld-specific
doctrine on this exact question is thin to nonexistent. So this rule rests on general principles of environmental
storytelling.

- A camp needs an implied footprint. A hearth reads as a hearth because it is a RING, or a cluster with something at its
  center. Props sprinkled independently around a point do not read as a hearth.
- A collapsed shelter reads as a shelter if its frame pieces still trace the wall or doorway that it had. Even
  collapsed and askew, the pieces describe a shape. A viewer can draw the missing walls again on that shape.
- 🔑 **A skeleton or corpse pile is not a props bag. Each skeleton or pile is ONE dead body.** Put the skull at one end. The spine and
  ribcage are the visual backbone of the whole composition. Everything else trails outward from that line, in one
  consistent direction. The story is:
  "a kill happened here and something settled/dragged it," never an even scatter of bone-type props at one density.
- **Leave no gap between the skull and the spine.** In this project's own Boneyard, the skull sat 5 cells from the
  ribcage, with a single thin neck-bone between them. The two parts looked disconnected. So the skull looked like a
  SECOND skull or animal, not the head of the same one (§6).

## 4. The five scoring metrics

Score every built scene on these five metrics, for each screenshot, from 1 to 5. The critical-reviewer pass (§5) grades
against this rubric. Write the score AND a one-line reason for each. The reason improves the next iteration, not the
number.

| # | metric | 1 (fails) | 5 (excellent) | what it is NOT |
|---|---|---|---|---|
| 1 | **Relevance to intent** | Nothing here matches the design brief (e.g. narrative in an item's spec) | A viewer who read the brief would recognize this as its depiction | NOT "does every prop from the brief appear" — a smaller, tighter scene that nails the FEELING beats a checklist scene that doesn't |
| 2 | **Visual recognizability** | Cannot tell what this is meant to be without being told | Instantly identifiable as its subject (a ruined camp, a dead beast, a wreck) at normal play zoom, no caption needed | NOT resolution/sprite quality — a technically crisp scene can still fail this if its SHAPE doesn't read |
| 3 | **Visual coherence** | Contains something bizarre or nonsensical (floating disconnected pieces, an object that implies a second unrelated thing, an impossible arrangement) | Every element's presence and position makes sense together; nothing needs an explanation | NOT "is it realistic" — a fantastical scene can be fully coherent; an ordinary one can still be incoherent (two skulls) |
| 4 | **Interest** | Flat, forgettable, no reason to stop and look | Draws POSITIVE attention — a viewer would screenshot it or want to explore it | NOT "is it busy" — restraint can be more interesting than clutter |
| 5 | **Distraction/defect** (score is "how CLEAN," 5 = no defects) | Something visibly stands out as wrong — a render glitch, a misplaced prop, ground that clashes, an obvious tiling seam | Nothing pulls the eye away from the intended read | The inverse of the others: this metric exists to catch what a "does it look good overall" score can hide inside an average |

**Gate**: nothing ships as a finished promise or whisper with a score below 3 on ANY metric. A promise is a site that
the world map shows. A whisper is a site that appears only when the map generates
(`design/Jawa/worldbuilding/structure_injection_roster.md` §1). A simple scene can pass every metric. A scene that is
impressive on four metrics and broken on the fifth is not done. Metric 5 exists so that one loud defect cannot hide
inside a good average.

This gate is the builder's own bar. The rubric has no row in `infrastructure/state/judge_calibration.json`. So a low
score does not by itself send work back through the pipeline. Only a calibrated brief does that (root
`CLAUDE.md`, "A refusal carries its path to pass"). The builder still repairs a score below 3 before the scene ships.
A judge look before the owner sees the scene uses `design/RimMandrake/scene_look_judge_brief.md`.

## 5. The critical-reviewer pass — how to run it

Do not only grade your own work. Build the scene and take screenshots as `rimworld-debug-testing` §4a says. Clear
the debug log, use unique screenshot filenames, and look at the actual image. Then spawn a **fresh** reviewer agent.
Fresh context matters, because you already know what you meant to build, and you cannot un-know it. Give the reviewer:

1. The screenshots. The reviewer opens them with the `Read` tool. So the review rests on the actual pixels, never on a
   description of them.
2. The ORIGINAL design intent (the one or two sentences that started the build). Metric 1 then has something to grade
   against.
3. The table of the five metrics above, verbatim. Do not let the reviewer invent a rubric.
4. An explicit instruction: name what specifically drove any score below 4, not just the number.
   - "the skull reads as a second animal because it sits 5 cells from the ribcage with nothing visually bridging them"
     is usable; "coherence: 3" is not.

Treat the low scores of the reviewer as work orders, not as opinions to weigh. A fresh set of eyes
catches "this reads as two skulls". A builder cannot detect that failure alone. The builder already knows that the scene
is one animal. Then iterate: fix, rebuild, take screenshots again, and review again, until every metric clears the gate
in §4. §7 step 6 says when to stop sooner.

🔴 **But verify a low score of a reviewer before you act on it, the same way you verify your own claim.** A fresh
reviewer has a failure mode too. In a wide shot, a reviewer cannot tell "built by this template" from "already on the
quicktest map". (A quicktest is a throwaway dev colony.)

- The failure happened once. A reviewer scored Waste Camp 2/5 on every metric. The reviewer described a tent-pole frame and a
  dark "collapsed mass" 15-20 tiles from the actual sunken pit. Those objects were a large ambient decoration and a map
  prop that was there before. The template placed NEITHER of them.
- **Before you trust a low score as a real defect, do one of these.** Frame the screenshot tightly enough to exclude
  ambient map scatter. Or tell the reviewer explicitly which defNames belong to the build.
- The job of a reviewer is to catch what the builder cannot see. A reviewer does not replace a check of the claim. The
  `verify-before-you-escalate` skill asks the same of everything else in this project.

## 6. Worked example — two rounds, and what they taught

Three Deep Desert templates went through two rounds of this pass. The fixes, the findings and the parts that nobody
finished are in `references/history.md`. The lessons:

- **Waste Camp** (`design/Jawa/templates/waste_camp.lua`). The fix was a sunk floor in a jagged, non-rectangular pit,
  with every prop inside that pit (§2, §3). A jagged edge can still be too subtle. The reviewer called the pit "a flat,
  near-rectangular patch of slightly lighter soil". Make the jaggedness strong enough to read at normal play zoom.
- **Boneyard** (`design/Jawa/templates/boneyard.lua`). The fix was a zero gap from skull to ribcage. One skull object
  can still read as two heads. A bone-fragment prop (`AB_AncientBrokenBone` or `AB_AncientVerticalBone`) at the far end
  of the tail has a sprite close to the skull's. So the prop read as "a second head". So check that no other silhouette
  echoes the main one.
- **Long Crossing** (`design/Jawa/templates/long_crossing.lua`). The site is a truck hull that stalled in sand.
  - A dune lip that linked correctly still read as a wooden fence rail. Its horizontal run was ONE CELL THICK. A dune
    needs BULK: 2-3 rows of depth, not only correct links. The top row of that dune lip was also on the wrong side of
    the face (§1).
  - To get depth, put distance between the face row and the top row, or use separate ridges. Face rows that touch draw
    posts (texture sheets, not a live test). With distance between the rows, join the ends with side edges. That closed
    outline is untested (§1).
  - A drift chance that changed only with x painted a uniform band across the WHOLE rect. Taper a drift in z too, or
    mask it to the z-span of the hull. Then the sand reads as caused by the truck hull, not as an unrelated background
    gradient.
- **A thing that a template places can fail to spawn through the live bridge, silently.** The tree (`TreeDead`) of
  Boneyard did. Check each placed thing in the live game, not only in the plan.

## 7. Process for this whole skill going forward

1. Build offline first with rimplace `lint`, `render` and `verify`, as `src/RimMandrake/Utils/rimplace/README.md` (the
   `rimplace` README) says. The mechanism needs no game.
2. Prove the scene live on a quicktest (`rimworld-debug-testing`). A disposable map is fine. Nothing here needs the real
   campaign world.
3. Take a screenshot as `rimworld-debug-testing` §4a says. Clear the UI, use a unique filename, and frame the subject
   (jump the camera to it). Choose a zoom that shows the WHOLE footprint, not just its center.
4. Run the critical-reviewer pass (§5) against the five metrics (§4).
5. Fix the named defects, not a guess at what is possibly wrong. Rebuild, take a screenshot again, and review again.
6. Stop when every metric clears the gate, or when the returns visibly diminish. Say so explicitly. Do not iterate
   forever on diminishing returns. Write what you left undone and why. The doctrine is §Threshold discipline in
   `skills/live-debugging-proof-harness/references/validation-plan-and-thresholds.md`.

## Keeping this skill honest

- Every rule above traces to one of three things:
  - a real defect that this project shipped and someone pointed out (Waste Camp, Boneyard);
  - outside game-design research (§1–3, 2026-09-06);
  - the XML and the texture sheets of the mods. A rule from this third source says so.
- That research found little or nothing for RimWorld on this exact question. So most of this skill rests on general
  principles of tile games and environmental storytelling. Do not present those principles as RimWorld facts.
- If a critical-reviewer pass finds a new defect, file it with its evidence:
  `python3 src/RimMandrake/Utils/lessons.py add "…"`. A curation session adds it here. The traps of `rimbridge` grow the
  same way.
