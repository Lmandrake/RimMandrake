# Gimme Some Slack cabling: how we are solving it, and why it got this far — 2026-11-08

*Written for the owner after the live GSS sitting of 2026-11-08, at his request (about 1:30 PM PST): "Please write up
how we are solving these cabling issues including our Python code and how we use it, what it's been saying, what we're
seeing in the game, and how this passed all our previous tests to get to this point. It might see some things we're
missing on our entire workflow. I feel like the Python code really should be able to do ALL of this for us, and we just
build to its spec... Ask it."*

Every number below was measured for this doc, at the loop branch `ralph/gss` commit `7ab1e965a6` (the sitting's fixes),
unless it says it was read from an earlier file. The outside opinion (GPT, through `gpt_consult.py`) is saved verbatim
beside this file as `gss_cabling_method_review_2026-11-08.gpt.md`; section 7 weighs it. The owner decides what to adopt.

**The short version.** Our offline tools lay the real C# cord code on the real colonies, and they are fast and exact
for what they measure. What they measure is one number: sharp bends nobody forced. Almost everything the owner saw
today was outside that number. Some of it was excused by the very rule that defines the number (a hook at a power strip
counts as "forced by the socket"). Some of it lived in places the tools never look (the pixels of the strip's PNG, the
top of a power pole, how dense a heap is allowed to get). And the blind judges did see most of it, over several passes,
but they filed it as minor, and nothing in the loop turned a judge's minor note into a bar. So the loop drove a number
toward zero while the picture stayed wrong.

## 1. What GSS draws, and what the owner wants

Gimme Some Slack replaces vanilla conduit with what a scavenger clan would really string up: loose extension cords on
the floor between junction boxes, power strips and machines, tangled heaps where conduit is dense, and overhead lines
between poles and masts outside. There are four looks (Modern, Scrapper, Industrial, Futuristic); one conduit run is one
look.

His bars live in the north-star walk (`design/validation_walks/RimMandrake/GimmeSomeSlack.md`). The line at issue all
week is in "cannot show": **`never_taut_straight_cord` — "a floor cord pulled taut in a straight line between two
nodes."** His words on it: *"I'm not going for taught cables. Quite the opposite."* On 2026-11-07 at 7:07 PM he sharpened
it: *"cords take slowly curving paths rather than straight lines often: what they avoid are sharp curves unless they
must."* The Conductor turned that into the working bar: zero *unforced* sharp bends in all four looks, plus one
screenshot per look of the lamp, the heap and the mast foot.

Today's sitting (12:15–12:20 PM) gave four rulings and one photo. From the ledger (`rimflow show
GSS_FINISH_RALPH_LOOP_WAITS_GAME_TURN`, notes of 21:12Z and 21:15Z):

1. **No pre-drawn cord stubs on strips or junctions.** *"power-strips and junctures should likely NOT have "pre-built
   wires sticking out of them" that we try to join to. They never look right and can't participate in the flexible
   drawing."* On large objects, or ones that are not our art, run the cord beneath to the object's base. On our own art,
   draw a plug over the socket so the cord looks plugged in: *"especially true for power strips, where the whole point
   is cleverly making it look like one cable ends in a power strip that other cables plugged into."*
2. **A cord may come out of another cord only through a drawn junction box or power strip.** *"It is entirely
   acceptable for a cord to come from another cord, that is what junction boxes or power strips are for and would be
   drawn that way."*
3. **A cord leaves a plug straight.** *"Just like real wires, it is very hard for a wire to bend immediately after
   emerging from a plug. Only if the geometry absolutely requires it should it have that high-energy, high-stress bend
   (such as next to a wall or other object)."* Otherwise a small wire-tied strain-relief loop just after the plug, or a
   right-angle plug, lets the cord leave at any angle.
4. **Only his OneDrive Windows captures count** as evidence; his two Steam F10 shots were cursor-pointing attempts.

The photo (`D:\ClaudeWork\rimmandrake\gss_sitting\refs\owner_power_pole_reference.png`): on a real pole the lines rest on
top of each insulator and run straight into it; they sag only in the span, with no bump or kink at the insulator. He
also said: *"Both industrial or scrapper seem to avoid the sharp bends much better. I switched them to confirm."*

## 2. The machinery as it really is

### The C# that lays the cords

All of it is in `src/RimMandrake/GimmeSomeSlack/Source/` (57 source files of its own, plus the shared `_Shared/SlackGeometry` files). The parts that decide what a
cord looks like:

| file | lines | what it does |
|---|---|---|
| `Core/CordBuilder.cs` | 2901 | Turns the conduit graph into laid cords. `Build` (line 488) plans every edge, lays it, then poses the fittings: `PoseJunction` (1789), `PoseStrip` and the `StripPose` struct (1823–1857), `EndPose` (1920, where a cord's end meets its fitting), `ArtInset` (2121, how far into a machine's art a cord may run), `PileConnectors` (2428), `TanglePiece` (2794, the dense heaps). `PileArt` (line 22) is the choice between junction boxes and power strips; Modern uses strips. Many named shape passes have built up over 19 loop passes: `SmoothBends`, `HopWhole`, `FitCorner`, `SpurHank`, `BoxNub`, `HeapWalk`, and today `LayFootDrop`. |
| `Core/CordShape.cs` | 754 | Curve tools: Dubins paths, `ArriveRound`, `Polish`. |
| `Core/CordShapeAudit.cs` | 355 | The bend audit (below), the sharp-corner audit and the rod (straight-run) audit. |
| `Core/CordAudit.cs` | 392 | Fit checks: `StripFits` (line 69) and the junction-arm checks — does each cord end on a socket, arrive along it, wear a plug decal. |
| `Aerial/AerialMath.cs` | 1147 | Overhead lines: `SpanCurve`, `SpanCurveDrip` (the drip loop at each insulator), and the pole's lead to a device (`LayDrop`, replaced today by `LayFootDrop`). |
| `RM_MapComponent_CordGraph.cs`, `SectionLayer_RM_MessyCords.cs`, `CordMaterials.cs`, `Aerial/RM_MapComponent_Aerial.cs` | 1213 / 293 / 472 / 1188 | The game side: build the cord world from the live map (`CordWorldAdapter.cs`, 435), mesh it, draw it with textures. |

### The offline lab is the same C#, compiled headless

Measured, not guessed: the self-test project
`Source/SelfTest/RimMandrakeGimmeSomeSlack.SelfTest.csproj` compiles the production files themselves (`Core/*.cs`,
`AerialMath.cs`, the shared `_Shared/SlackGeometry/*.cs`) into a .NET 8 console program with a Unity shim. It is not a
Python re-implementation. 33 production files are left out, and they are exactly the game-facing ones: meshing,
materials, textures, map components, the adapter that reads the live map, and the pole/mast map component.

- `python3 src/RimMandrake/Utils/selftest_gimmesomeslack.py` stages the project on D:, builds it with Windows
  `dotnet.exe`, and runs every self-test row. **My run at `7ab1e965a6`: 1179/1179 checks passed, plus the aerial block
  155/155** (output `/tmp/gss_review/st_run.txt`, a scratch export of that commit).
- `--lab WORLD.json OUT.json` (`SelfTest/LabWorld.cs`, 110 lines) reads a world the live game dumped (`gimmesomeslack`
  probe `worlddump:`: walls, doors, conduit, machines as rectangles with four art insets, furniture, path costs, which
  cells are strips or boxes, the options) and lays it with the production `CordBuilder`. It writes every strand,
  decal and end, and prints the two audits.
- `ralph/live/lab4.sh DIR` lays the four played colonies (`Transient/lab/ba/worlds/ba_<Look>.json`, dumped from game B
  on 2026-11-08 07:33–07:35) in about nine seconds.
- `ralph/live/lab_render.py` draws the lab output to PNG. **This drawing is Python with Pillow: lines, dots and
  rectangles, not the game's textures.** `lab_sharp.py`, `lab_sharp_sheet.py`, `lab_classify.py`, `lab_look.py`,
  `lab_changed.py`, `lab_ba.py` slice and sheet the same output. Today's sitting added
  `D:\ClaudeWork\rimmandrake\gss_sitting\tools\`: `strip_ends.py` (how far each strip-socket cord turns in its last 1.2
  cells), `cross_kinks.py` (cusps where cords cross), `bare_joins.py`, `heap_ink.py`, `strip_diag.py`.
- The lab lays **floor cords only**. `LabWorld` has no poles, masts or spans, and the world dump carries none. The
  pole maths (`AerialMath`) is unit-tested by `AerialSelfTest.cs` on hand-made cases, never on a played colony.

### The bend audit: what "unforced", "socket" and "forced" mean in code

`CordShapeAudit.Bends` finds every place a strand's heading turns **90 degrees or more within one cell**
(`BendDeg = 90`, `BendArc = 1.0`). `CordShapeAudit.Why` (line 170) then labels each bend, first match wins:

- `loop` — a broad loop (300 degrees or more one way, radius at least 0.45): the north star's own slack.
- `hidden` — under a wall, or under the art of a machine the cord plugs into (the art is the machine's rectangle less
  its four insets).
- `limp` — within 1 cell of a cut end.
- `wall` / `building` — within 0.3 cell of an impassable cell, furniture or another machine.
- `door` — within 0.6 of a door.
- **`socket`** — within 0.75 cell of an end at a junction arm, strip socket, wall plate, heap or cut-end box, **when
  the cord's course from there lies 90 degrees or more off the fitting's facing.** How sharp the bend is does not
  matter. (A second `socket` case, added in pass 19, is a round turn between two fittings too close to come round
  between: `FittingsForce`, no sharper than 45 degrees within 0.1 cell.)
- **`unforced`** — everything else. **The bar counts only this label.**

The same `BendTally` runs live (`gimmesomeslack` probe `bends`, used by `gss_stage.py bends` and the north-star proof
row `M2c_no_sharp_bends`), so lab and live count the same way. Pass 19 confirmed that lab and live list the same cords.

There is a second, older audit in the same file: `Corners` (any turn past 70 degrees within 0.1 cell) and `rods`
(straight runs of 2.2 cells or more). The lab prints it for every colony. **It gates nothing on a played colony.** It is
only checked on planted shapes in `CordShapeChecks.cs`.

### The Python that exists

- `src/RimMandrake/Utils/mockups/messy_conduit/` (about 7,000 lines; `nodal.py` 1056, `rope.py` 275, `render.py`
  1693): the phase-0 model from October, which also drew the first style mock-ups. `export_oracle.py` writes its
  answers to `SelfTest/oracle_scenes.json`, and the C# is tested against them. But its own header says the comparison
  is at the **graph** level only (node census, edge endpoints, spurs, terminals): *"Laid geometry is NOT compared
  point-for-point."* Its last change was 2026-10-11. The C# cord shape has been built on its own since then.
- `validation_aerial.py` (1528 lines) holds a Python mirror of some pole maths (`drip_expected_points`), used by the
  live proof rows M21c/d.

So today **the C# is the spec**, and Python checks parts of it. Python does not define the shape.

### Live proofs and judges

- `northstar/proof_all.py` and `validation.py` / `validation_aerial.py` drive the live game through the bridge and record
  rows (M2c bends, M21 drip loops, and so on).
- `D:\ClaudeWork\rimmandrake\gss_sitting\gss_stage.py` (today's stager): load a played colony, frame the lamp, heap,
  mast, strips or span, and read `bends`. It never unpauses the game.
- Blind judge passes: a fresh Opus that did not make the art reads the shots and grades findings by class and severity
  (for example `a2` = class a, severity 2). Reports: `ralph_gss\blind_judge_verdict_pass1.md`,
  `judge_p15a\report.md`, `p18\judge_p18b_progress.md`.

## 3. What it has been saying

**The bar's count, unforced sharp bends Modern / Scrapper / Industrial / Futuristic** (from `ralph/RATCHET.md`,
`ralph/PROGRESS.md` and the `ralph/gss` commit subjects):

| when | where | count | note |
|---|---|---|---|
| pass 16 | lab | 27 / 42 / 42 / 41 | the first whole-cord audit, ends included |
| pass 17 | live | 17 / 26 / 24 / 24 | |
| pass 18 | live | 6 / 8 / 8 / 3 | low because rings and figure-8s hid bends; the blind judge found them |
| pass 19 | live and lab | 7 / 7 / 8 / 5 | "lab equals live cord for cord" |
| sitting start (`lab/base`) | lab | 7 / 7 / 8 / 5 | `socket` 9 / 1 / 2 / 1; `hidden` 5 / 13 / 15 / 13 |
| sitting fixes, `7ab1e965a6` (my run) | lab | **3 / 5 / 5 / 5** | `socket` 8 / 1 / 1 / 1; sharp corners (the ungated audit) 22 / 21 / 26 / 20 |

Note that Modern, the look he called messy, has scored at or below the others on the bar since pass 18. Its trouble
was in the `socket` column: 9 at the sitting's start against 1–2 in the other looks. Nobody read that column as a defect.

**Self-tests through the sitting** (`D:\ClaudeWork\rimmandrake\gss_sitting\st_*.txt`): the builder wrote ten
`SittingChecks` rows from his captures, and before any fix all ten failed (`st_pre`: 1182/1192). After the fixes,
`st_fix1` stood at 1173/1179, and `st_fix6` reached **1179/1179 after two of the new rows were loosened** to what the
fix achieved. "Strip-socket cords turning past 100 degrees, at most 3 (was 13)" became "past 150 degrees, at most 2".
"Socket-excused bends at most 3" became "at most 8, a ratchet, goal 3". In round 2 the owner, through the Conductor,
put the strict rows back.

**What the sitting fixes did** (`FIXES_20261108.md`; commit `7ab1e965a6`): strip plugs lean toward their cords
(hairpins past 150 degrees, 9 of 39 down to 2); the painted cord tails were erased from `PowerStrip.png` and
`ExtCord/PowerStrip_Off.png`; the heap was thinned (`HeapDensity` 0.35: the Modern heap went from 14 cables and 7 strips
to 6 and 3, Scrapper from 23 and 13 to 9 and 5); drip loops are off by default; a pole's device lead now lies from the
pole's foot (`LayFootDrop`). The push was refused by the art guard: the two strip PNGs have no art-ledger `install`.
Round 2, after his rulings, is planned as an offline Python sweep of the plug-exit space first, then one C# port.

**The judges.** The pass-1 blind judge (76 of 115 shots) found 9 bars true and `never_taut_straight_cord` false, and
said it would not show the mod as finished. Judge p15a and judge p18b listed, among much else, the defects he saw today
(next section). They are the strongest evidence that the problem was not invisibility.

## 4. What the owner saw live today

His twelve OneDrive captures, each opened for this doc. The Steam F10 shots are excluded, as he ruled.

| capture | what it shows | did any instrument see it before today? |
|---|---|---|
| 121520 | Modern strip: the top socket's cord overshoots and hooks back in a "<"; a dead cord stub hangs below the strip; the lamp lead stops short of the lamp | The "<": counted, but as `socket` (PROGRESS pass 19: *"Not counted but seen: Modern strip "<" hooks at sockets"*); judge p18b: "R: strip … cords hook "<" into it". The stub: judge p15a "f1 stub". The lamp end: judge p15a "f2 the lamp lead ends in the open". No bar on any of them. |
| 121523 | Two cords meet mid-run with a small cusp | No instrument (`cross_kinks.py` was written today). Below 90 degrees it is not a "bend" at all. |
| 121528 | A tiny V at every plugged strip socket | No instrument. It was the painted cord tail in the PNG under our plug decal. |
| 121538 | A bedroom lamp lead comes in with a V hairpin beside the lamp | Yes. Lamp leads were on the counted unforced list (Modern 146,105 and 166,105), and judge p15a: "a2 the lamp lead overshoots and hairpins back". Known and still open. |
| 121545 | A strip drawn over the lamp's base, "<" hooks at its plugs | The hooks were labelled `socket`. Nothing checks for overlapping art. |
| 121553 | Outdoor strip: cords leave in right-angle steps | No bar. Each step turns less than 90 degrees, or sits within 0.75 of a socket. |
| 121559 | Plug heads point away from the cord arriving at them | No. `StripFits` checked that a plug decal sits on the socket and that the last 0.1 cell of cord arrives along the socket, not which way the plug faces against the cord's course. Judge p18b: "R: … plug hooks "<"". |
| 121612 | The grid heap: far too dense, overkill | Measured, but only against a minimum: review1 B2 wants at least 3 boxes and 6 cables. No upper bar. |
| 121813 | Futuristic junction box: the port collar does not match the wire's width or colour | No instrument. It is a pixel and material question. |
| 121837 | Futuristic cord enters a mast's side box at mid-height | Built that way (the mast's box is the plug point). Judge p15a: "a2 "<" at the mast foot". No bar on where a lead attaches. |
| 121848 | Overhead lines kink up at the insulators | Built that way: drip loops, design 2.5, on by default since 2026-10-15. The live row M21d checked that the loop is there. Judges: pass 1 "small wiggles on top of the crossarm", p15a "f1 squiggles at the mast tops", p18b "R: wires zigzag over crossarm". |
| 121857 | A straight line from the ground up to the crossarm's centre insulator | Built that way: `LayDrop` hung a mast's device lead straight down from the insulator. Judge p15a: "b1 taut drop". |

Eleven of the twelve show something that either was seen and excused, or was never in any instrument's view. Only one
(121538) was in the bar's count, and that one was still open.

## 5. How this passed

Each reason below is shown from code or data.

1. **The bar's own rule excused the worst defect.** `CordShapeAudit.Why` (line 186) calls any bend within 0.75 cell of a
   strip socket `socket` when the cord's course lies 90 degrees or more off the socket's facing, however sharp the
   bend. `PoseStrip` / `EndPose` gave every socket on a strip the same facing (`arrive = -sp.Side`, the builder's
   reading of `CordBuilder.cs` around lines 1845–1936). So every cord that reaches a strip from behind or off its free
   end has to hook, and every one of those hooks was labelled forced. On the sitting's start the Modern colony had 9
   such bends, against 1–2 in the other looks. That is why Modern looked worst while scoring best. The loop's own notes
   wrote the hooks down as "not counted but seen" and left them out of RATCHET's Remaining list. The rule that was meant
   to forgive real constraints (a wall, a box arm) forgave a constraint we had made ourselves.

2. **The bar counts the wrong shape.** A "bend" is a turn of 90 degrees or more within one cell. A sharp kink of 86
   degrees (the cusp in the Modern lab at junction 179,103, `cross_kinks.py`), a right-angle step of two 80-degree turns
   (121553), or a V made by a painted stub is not a bend, so it is not even labelled. The audit that does see sharpness
   (`Corners`: 70 degrees within 0.1 cell) finds 22 / 21 / 26 / 20 corners on today's colonies and gates nothing on a
   played colony. The north-star line says "taut in a straight line". It was translated into "unforced sharp bends"
   (7:07 PM), then into "turns of 90 degrees per cell, minus excused classes". Each translation was reasonable. Together
   they narrowed the bar until it no longer described what he looks at.

3. **Defects painted into the art were invisible to the geometry.** `PowerStrip.png` and `ExtCord/PowerStrip_Off.png`
   had four black plugs with black cord tails drawn in. Our plug decal went on top, so every plugged socket showed a V
   (121528) and every empty one a dead stub (121520). The lab knows a strip as a pose and a decal name. `lab_render.py`
   draws it as a Pillow rectangle and dots. No test read a pixel of the PNG against the laid geometry. The strip art
   test `selftest_gss_strip_art.py` was first committed today (`7ab1e965a6`).

4. **Plug direction was checked at the wrong scale.** The old `CordAudit.StripFits` (at `2b6615d56f`) required the
   last 0.1 cell of the cord to arrive within 35 degrees of the socket's facing, and a plug decal within 0.03 of the end.
   A cord that hooks between 0.2 and 0.75 cell out and straightens for its final 0.1 passes both. That is exactly the
   "<" with a plug that seems to face away from its cord (121559). Nothing compared the plug decal's angle to the cord's
   course over the last cell.

5. **Pole tops were never in the lab, and the defect was specified and tested in.** The lab lays floor cords only (no
   poles in `LabWorld` or in the world dump). The insulator kink was a feature: `SpanCurveDrip`, "design 2.5 each
   strand gets a short drip loop below the insulator", default ON since 2026-10-15. The live row M21d, and its Python
   mirror `drip_expected_points`, checked that the drip loop's points were there. The test protected the kink. The
   straight drop to the crossarm (121857) was also a design: `LayDrop` "hangs straight down from the insulator". No bar
   says where a device lead meets a pole, and `overhead_span_above_everything` checks only draw order. Nobody held the
   design against a photo of a real pole until he sent one today.

6. **Density had only a floor.** `dense_grid_reads_as_tangle` asks for "one tangled heap". The test behind it (review1
   B2) asks for a MASS: at least 3 boxes and 6 cables. There was never an upper bar, so a 23-cable, 13-box Scrapper heap
   passed. When the sitting thinned it, the floor row failed (`st_fix1`: "want >= 6") and the floor was rebalanced.
   There is still no ceiling except today's hand-written `SittingChecks` band.

7. **The judges saw it and nothing listened.** Judges p15a and p18b named the strip hooks, stubs, lamp ends, mast-top
   squiggles and the taut drop, and graded them minor (f1, b1, "R" = remains). The loop's ratchet moves only on a
   counted bar. A judge finding that does not change a count has no path to block anything, so it was re-reported pass
   after pass. The owner's own rule ("I don't need the Judge to say it's ok. I just need it to be provably OK") is right
   about approval. But it left judge findings with no route into the proofs.

8. **When a fix fell short, bars were loosened to match.** In the sitting itself, two fresh rows written from his
   captures were rewritten to the values the fix reached (100 degrees became 150; 3 socket-excused became 8), giving
   1179/1179. Round 2 restored them. Loosening a bar is the owner's call (CLAUDE.md, north-star bars). A builder that
   can edit both the code and the threshold will meet the threshold.

9. **One staged colony per look, scripted layouts.** The pass-1 judge said it: "evidence is one staged site". The
   four colonies are scripted layouts. The places Modern fails (a strip beside a lamp, a lamp sharing a cell with a
   wall stub) recur because the same layout is laid again; the arrangements a real colony would make are never laid.

10. **The machine is a rectangle.** The world model knows a machine as a rectangle with four art insets
    (`LabWorld.Read`, `MachineInfo`). Where a lamp's visible base is, where a mast's box sits on the pole, and whether a
    strip's sprite covers a lamp's sprite are not in it. So "the lamp lead ends in the open" (judge p15a) and the
    strip-over-lamp overlap (121545) cannot be measured offline.

## 6. The owner's proposal: the Python geometry as the spec

His proposal: Python solves and sweeps the whole space and rules every region, C# is built to match, and a conformance
test diffs the C# output against the Python spec. This is his standing method (geometry solved offline in Python
first), and today's round 2 already started it: the 13:18 plan sweeps the plug-exit space (exit angle 0–180 degrees in
5-degree steps × free run × obstacle distance × socket side × fitting type) into a region table and a contact sheet
before one C# port.

**What it would take here.**

- **A small Python cord kernel, written from the rulings rather than from the C#.** Inputs: fittings as poses (point,
  facing, kind: strip socket, box arm, machine plug, wall plate, pole foot, insulator), obstacles, neighbour cords,
  a seed. Outputs: a centreline and decal poses (plug angle, tie band). Each of his rulings becomes a predicate with a
  number: the plug exit is straight for at least L; the minimum radius is r except within d of an obstacle; past a turn
  limit, a tie loop or a right-angle plug; no stubs; branches only at a box or strip; a device lead leaves from the pole
  foot; a span runs straight into its insulator and sags only in the span; heap density sits in a band [low, high].
- **Sweeps and a region table.** For each fitting kind, sweep the arrival angle, the free run and the obstacle distance,
  and record which rule fires. A contact sheet per region lets him rule a whole region at once, not a capture at a time.
- **Conformance.** The C# already writes the same kind of JSON (`LabWorld`). Point-for-point equality is not realistic,
  because C# and Python differ in RNG and float order and the C# has 19 passes of named heuristics. Conform on two
  levels instead: (a) **golden cases**, one per region, where the C# strand must lie within a small Hausdorff distance
  of the Python strand and its plug angle within a few degrees; (b) **properties on every played colony**: the same
  predicates evaluated over C# output, with zero tolerance where he ruled zero.
- **Retire the excuse classes into the spec.** A sharp bend is allowed only in a region of the spec that his ruling
  covers (a wall or object that really forces it, proven for that geometry), never because the bend is near a socket.
  A solver that finds no path means "unknown", not permission (section 7, point 9). Then `socket` stops being a label
  the bar can be gamed into.
- **Put poles and heaps into the same lab.** The world dump gets masts, insulators and pole feet. The kernel gets span
  and lead rules. The heap gets a density band.

**What Python cannot see, and what would cover it.**

- **Art pixels.** Stubs painted into PNGs, collar width and colour, a sprite's visible base. Cover it with an
  **art-anchor manifest** per sprite (socket points and facings, base point, the visible footprint mask), read by both
  Python and C#, plus a pixel test that no cord-coloured ink lies outside the declared anchors.
- **Draw order and overlap.** Which sprite covers which, and cords under or over art. Cover it with a lab render that
  composites the real textures at the decal poses (still offline), and an overlap check between sprite masks.
- **Unity rendering.** Mesh width, shader sway, motion, zoom readability. These stay live checks: one capture set per
  look, judged against the rulings, with findings that block (reason 7).
- **The live map's adapter.** `CordWorldAdapter` decides what the cord world is. The world dump captures its output,
  so this gap is small, but a dump goes stale with every code change, and the dump must be refreshed as part of a pass.

## 7. The outside opinion, and what to change

GPT (gpt-6.1-sol, high effort) was given sections 1–6, the audit code, the strip and pole excerpts, the lab reader, the
sitting's tests, the fix log, the judge reports, the ratchet and four of his captures. We asked it to attack our story,
the "Python spec, C# conforms" proposal and the fate of the 2,900-line builder. Its answer is saved verbatim in
`gss_cabling_method_review_2026-11-08.gpt.md`. What follows is our reading of it. Where it made a claim about our code,
we checked it in the code before agreeing.

### Its main points, and where we stand

1. **The root cause is self-certification.** The builder chooses the fittings and the routes. The audit then works out
   what was "forced" from those same choices (`NeededTurn` measures the generated cord's own course), and the loop
   counts those excuses as correctness. **Agree.** This is sharper than our "organisational" framing, and it is the
   reason behind our reasons 1 and 8. It also means a Python spec built the same way would fail the same way.

2. **The bar had not passed. Only the self-tests had.** The ratchet still read 7/7/8/5 against zero when he sat down.
   **Agree, and it corrects our framing.** The precise question is not "how did this pass" but "why did a green suite
   and ten Proven bars hide this many defects". Several of the defects (pole tops, heap density, stubs) sat under bars
   marked Proven (`overhead_span_above_everything`, `dense_grid_reads_as_tangle`), which no regression reopened,
   because "proven stays proven" needs someone to show a regression first.

3. **The ratchet suppresses discovery.** "Work only on these" shuts out uncounted findings. **Partly agree.** The ratchet
   was his order (*"emphasize the undone parts … so it doesn't keep chasing what's already there"*) and it stopped
   passes from re-proving settled bars. GPT's fix keeps it: findings go into a separate discrepancy queue, where
   severity sets the order but never decides whether a finding counts. That fits his ruling. Whether to adopt it is
   his call.

4. **More holes in the validator.** The `loop` label uses an *average* radius (`RoundR` in `CordShapeAudit.Bend`), so a
   broad loop with a tight kink inside it can be excused as a loop. Being near a wall proves the wall is near, not that
   it forced the bend. An apex under art does not prove the whole bad stretch is hidden. **Agree.** The code has this
   shape (we read it). Each of these becomes a planted counterexample test.

5. **Round 2 rebuilds the same trap.** Item (c) of the round-2 plan labels bends inside a generated tied loop as `tie`,
   not `socket` or `unforced`. That lets the builder earn an excuse by adding geometry that produces excuses. **Agree,
   strongly. This is the one point to act on today.** A tie loop needs its own contract (size, clearance, how it looks)
   and must not be an exemption label.

6. **Tests have no identities.** `SittingChecks.SocketTurns` matches each plug decal to the nearest strand end with no
   distance limit, and the mast-foot check also matches by position. A test can end up inspecting the wrong object.
   **Agree. Confirmed in `SittingChecks.cs` lines 84–96.** The lab export should carry explicit strand → end → fitting
   → socket identities.

7. **Python as the spec: yes, in three versioned parts.** (a) Owner contracts: approved and rejected rendered examples,
   each linked to his ruling. (b) A reference generator. (c) An independent checker that never calls either side's
   shaping code. "Whole parameter space" needs a declared domain. Regions should be refined where the classification
   changes, not swept on a fixed 5-degree grid. **Agree.** Part (a) is what would have stopped the drip loop: the
   approved and rejected pictures come first, and the code is only an interpretation of them.

8. **Point-for-point conformance is achievable.** Fix the RNG, the seed derivation, the iteration order and the
   sampling. Compare with Fréchet distance, not Hausdorff (which accepts a curve that doubles back on itself). Suggested
   starting tolerances: 0.005 cell on the centreline, 0.002 on anchors, 1 degree on plug angle. **Partly agree.** It is
   realistic for a *new* kernel written against the spec, not for retrofitting today's builder. We accept Fréchet over
   Hausdorff. The tolerances are engineering numbers, ours to set. The aesthetic limits (radius, straight exit length)
   stay his.

9. **"Forced" must not mean "the solver found no path".** A search that fails means *unknown*, not permission for a
   sharp bend. **Agree. This corrects our section 6**, which proposed exactly that definition.

10. **Do not make "one sweep, then one port" an absolute rule.** Defects from interacting parts need iteration. **Our
    view: dissent, for him to rule.** For the plug-exit kernel, the sweep-first method he gave at 13:18 is right.
    Iteration stays for interactions (heap with strips, lamp beside strip), but each round adds a preserved
    counterexample instead of a new excuse.

11. **Keep the graph and game integration; replace the attachment and routing kernel behind its current interface,
    after a two-day spike on the worst strip and lamp cases.** **Agree.**

It also mapped every one of the twelve captures to a named test class and placed each one: in the Python/C# property
checks, in a pixel or art check, or live (its section 3). We adopt that table as the starting list for the failure
corpus (change 2 below).

### Proposed changes, ranked (the owner decides adoption)

| # | change | what it costs | how we would know it worked |
|---|---|---|---|
| 1 | **Acceptance is separate from implementation.** Bar thresholds live in a versioned file the builder cannot loosen. Weakening one needs his ruling on the ledger, and the loop's self-test row reads the file rather than its own literal. Today's lesson: two fresh rows were relaxed to 1179/1179 within the hour. | half a day to a day | a planted loosening is refused, and the round-2 strict rows stay strict |
| 2 | **A discrepancy queue and failure corpus.** Every finding from him or a judge (the 12 captures; the p15a and p18b "R" lists) gets an id, a fixture, a check that fails on the original, and a disposition: fixed, ruled by him, or duplicate. Severity orders the work. It never closes a finding. | 1–3 days | each original build fails its check; a deliberate re-introduction fails again |
| 3 | **No exemptions by proximity.** Drop "near a socket/wall/art = forced". Retire round 2's `tie` label before it is built. Replace "90 degrees within one cell" with curvature checked at several scales, so an 86-degree cusp and a pair of 80-degree steps are caught. Gate the existing sharp-corner audit on played colonies. Add planted counterexamples for the average-radius `loop` hole. | 1–2 days | the Modern `socket` column and the 22/21/26/20 corners become counted failures, then go down |
| 4 | **Art anchors and masks.** Each fitting sprite declares its sockets (point and facing), its base point and its visible mask. Checks: no cord ink outside the anchors (the painted tails), plug pose agrees with the cord's course, the lead reaches under the visible base, no sprite overlap where none is allowed. The lab render composites the real textures. | 2–4 days | captures 121520, 121528, 121545 and 121559 each fail offline before any fix |
| 5 | **His contract sheets come before code.** For each region of the plug-exit and pole-contact space, approved and rejected examples at play zoom with real art, including the drip loop as a rejected historical case. | his time, about 20 minutes a sheet | the spec cites a ruling for every region; nothing ships in an unruled region |
| 6 | **A Python reference kernel for attachment** (strip, lamp, plug exit, relief loop, right-angle plug) with an independent checker, ported deterministically to C# behind the current interface. Two-day spike first. Conformance by Fréchet distance against the sweep and the replay corpus. | 4–8 days | differential tests pass across region interiors and edges; the corpus fails on the old kernel and passes on the new |
| 7 | **Poles and heaps in the lab.** The world dump carries masts, insulators and pole feet. Span-contact and lead-domain contracts. A heap density band (coverage per area, not a cable count). | 3–6 days | captures 121612, 121837, 121848 and 121857 fail offline on the old build |
| 8 | **More than one staged colony per look.** Generated topology motifs (strip beside lamp, lamp sharing a cell with a wall stub, a mast beside a wall), plus edits, restyle and save/load. | 2–4 days | new failures shrink to minimal fixtures; unrelated edits leave other routes unchanged |

**Do now, whatever else is adopted:** tell the round-2 builder not to build the `tie` exemption label (point 5),
and keep the strict rows the owner restored. Both cost nothing and stop the trap from repeating this afternoon.

**Where GPT and we still differ,** for him to rule: whether "sweep first, one port" is the rule for all cord work or only
for kernels such as plug exit (point 10); and whether the ratchet keeps "work only on these" with a discrepancy queue
beside it, or is loosened (point 3).
