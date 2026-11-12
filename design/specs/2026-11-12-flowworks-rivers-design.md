# FlowWorks rivers: final design report (2026-11-12)

Ledger item: `RIMMANDRAKE_DESIGN_NATURAL_WATER_AS_PITS_NOT_FLAT_PONDS`. Design only; no mod code, deploy or live game was touched.
Every claim is tagged `[measured: where]` or `[guess ~N%]`. Anything not measured says UNMEASURED.
"GPT" below is the outside reviewer (model `gpt-6.1-sol`); both of its calls succeeded, nothing was substituted.

## Summary (15 lines)

1. Yes: water can really move. One model can hold the true volume of every river square, move it between squares, and give the current that shoves pawns, all from the same numbers.
2. Recommended: "design 7", a per-square level model solved once per pulse so that it is stable at any pulse length, in exact whole decilitres.
3. The current is not printed. It is read off the water that actually crossed each square edge in the last pulse. No flow, no shove; fast gap, fast shove.
4. Dams, weirs and sluices are rules on a square edge (wall: nothing passes; weir: the weir formula; gate: the orifice formula).
5. Your printed-vector design is sound only for an untouched river. With player works it shows wrong currents; the offline twin measured this (section 4.1).
6. Your instinct about the dam was right in outcome: upper side holds the edge level with no current, lower side drains off the map. The recommended model reproduces exactly that, by computation and not by a rule.
7. Your "thin surface water" hunch is right in spirit: the recommended model is that same idea made deep, with a solver that does not need 166,000 passes to settle.
8. A full wave-carrying fluid model is affordable in arithmetic but fragile: three false floods in one afternoon of tests. It stays an offline research branch.
9. Waves: ship a drawn surge (no extra water, no extra shove). Real travelling waves only if the research branch later passes its proof.
10. The offline twin of the recommended model passes: plain river, full dam, dam closed and opened mid-run, narrow gap, moat breach, weir. Books close to 0 dL in every scene.
11. The open risk is solver cost: my twin needs about 1,600 inner iterations per pulse even when the river is settled. That must be fixed offline (sleep, caching, better solver) before any C#.
12. Second open risk: how long a pit takes to fill depends on pulse length today (625 s against 3,753 s). The final level does not. Needs sub-stepping.
13. Inside the game nothing is measured: C# speed, repaint cost, and whether the vanilla river shader follows a changed flow map are all UNMEASURED.
14. GPT agreed on the choice, corrected several of my conclusions, and proposed parts not yet tested in any twin (section 6).
15. Three decisions are genuinely yours: what the upstream map edge does, how fast the current carries, and whether waves are drawn or simulated (section 10).

Files to open (all under `D:\ClaudeWork\rimmandrake\conductor\rivers_20261112\`):
`00_research.md`, `01_designs.md`, `02_gpt_skeptic.md`, `03_gpt_improve.md`, `FINAL_REPORT.md`, twin code `py\implicit_v3.py`, results `py\out_implicit3_a.txt`, `py\out_implicit3_e.txt`, `py\out_implicit3_wl.txt`, `py\out_implicit3_cg.txt`.

## 1. The recommended design in plain words

Every natural-water square is a small tank with a bottom height and a true volume in decilitres. Neighbouring squares share an edge. Once per pulse the model asks one question for the whole river at once: "given the levels now, the inflow at the upstream edge and the outflow at the downstream edge, what levels make every edge's flow agree with the level difference across it?" It solves that as one linked set of equations, then moves whole decilitres across each edge to reach the answer.

Because all squares are solved together, a change at one end reaches the other end in one pulse. That is what removes the 166,000-pass crawl of the simple neighbour-to-neighbour kernel [measured: `py\out_D.txt`] and the false floods of the wave kernel [measured: `py\out_diagI.txt`, `py\out_diagI4.txt`].

```
  one river square                       one edge between two squares
 +---------------------+                +-----------------------------------+
 | bed height  (fixed) |                | kind: open / wall / weir / gate   |
 | volume, dL  (exact) |---- edge ------| sill or crest height              |
 | level = bed + depth |                | roughness                         |
 +---------------------+                | dL moved last pulse   -> CURRENT  |
                                        | rounding carry (fraction of 1 dL) |
                                        +-----------------------------------+

 upstream map edge                                          downstream map edge
 [ SOURCE rule ] -> sq -> sq -> sq -|weir|-> sq -> sq -> sq -> [ OUTLET rule ]
                          |
                          +-> sq -> sq (dug canal, moat)      closed elsewhere

 per pulse:  1) solve all levels together   2) move whole dL across edges
             3) current on a square = dL crossed its edges / (width x depth)
             4) settled, closed bodies go to sleep
```

How water crosses an open edge: the standard river-friction formula (Manning), flow rising with depth and with the square root of the slope. How it crosses a weir: Q = 1.705 x width x (head over crest)^1.5, reduced when the lower side drowns the crest. A wall passes nothing.

Your connection idea survives inside it: a flood-fill of connected water decides which squares are solved together and which bodies may sleep. It no longer decides the current.

What the twin measured, 100 x 100 squares, 12-wide river, pulse of 41.7 river-seconds [measured: `py\out_implicit3_a.txt` unless stated]:

| Scene | Result |
|---|---|
| Plain river | 16.75 m3/s, level -0.192 m upstream to -0.248 m downstream, settled in 1 pulse |
| Full dam | upper pool -0.0999 m, lower -0.400 m, no reversals of flow, no overshoot |
| Dam closed mid-run | both sides go straight to their held levels, no surge, no jitter [measured: `py\out_implicit3_e.txt`] |
| Dam opened mid-run | back to the plain-river state within 1 pulse [measured: `py\out_implicit3_e.txt`] |
| Narrow gap (3 of 12) | 15.9 m3/s still passes; current in the gap rises accordingly |
| Canal to a dug moat | pit fills steadily to -0.156 m in 625 s, never overshoots, no land wet |
| Weir as an edge rule | 0.64 m3/s against 0.66 by hand formula; levels -0.101 / -0.398 m; identical at pulses of 4.17 s and 41.7 s [measured: `py\out_implicit3_wl.txt`] |
| Books | 0 dL error and 0 safety clips in every scene above |

Known defects of the twin, stated plainly:
- A weir modelled as a raised square (an 8 cm film of water) jitters 4 to 6 mm. Modelled as an edge rule it is clean. So weirs must be edge rules. [measured: `py\out_implicit3_a.txt`, `py\out_implicit3_wl.txt`]
- At a pulse of 417 s the weir shows 3 to 4 mm of jitter and one unconverged pulse. [measured: `py\out_implicit3_wl.txt`]
- Fill TIME depends on pulse length: the moat takes 625 s at a 41.7 s pulse and 3,753 s at a 417 s pulse. The final level is the same. [measured: `py\out_implicit3_e.txt`]
- In the dam-closing test the books show -267,455 dL. That is the water my test code deleted under the 12 new dam squares, not a solver leak; the real rule (push it aside, or refuse to build in deep water) is still to be written. [measured: `py\out_implicit3_e.txt`]
- Cost when settled does not fall: 1,647 inner iterations per pulse on average for the plain river, 1,615 in the last ten pulses. [measured: `py\out_implicit3_cg.txt`]
- Flow at 45 degrees to the grid may run up to about 19% off [guess ~60%, GPT's estimate, no twin test yet].

## 2. Comparison after review

| # | Design | Does volume really move | Currents right with player works | Stable | Verdict after review |
|---|---|---|---|---|---|
| 1 | Your printed current + connection test | No (levels by separate rule) | No: 54 flowing squares had no arrow, 10 slack squares had one, worst speed error 9.2 times; a gap runs up to 4.2 times the printed speed [measured: `py\out_OPR.txt`] | Yes | Keep the connection test as bookkeeping and the printed arrows as the look of an untouched river. Not the model. |
| 2 | Simple neighbour seeping | Yes, exact | Yes in shape | Yes | Right state, hopeless speed: a dam needs 166,000 passes [measured: `py\out_D.txt`]. It is the foundation that design 7 solves properly. |
| 3 | Pools and links | Between pools only | Only at built structures | Yes | Keep for tanks, isolated basins and the structure formulas. A pool has one level, so no slope and no current inside it. |
| 4 | Wave-carrying grid model | Yes | Yes, and real waves (dam-break front 3.2 m/s against 3.3 by theory) [measured: `py\out_diagI4.txt`] | No: false floods of 370 to 1,500 land squares unless step, speed cap and damping are all right [measured: `py\out_diagI.txt`, `py\out_diagI2.txt`, `py\out_diagI4.txt`] | Offline research branch only. |
| 5 | Pools + solved steady flow field | Between pools only | Good picture, but as I specified it the field ignores water being stored, so it is wrong while levels change (GPT, section 6) | Yes | Not for the first build. Possible later as a cheap display for huge calm bodies. |
| 6 | Design 5 with design 4 in "windows" | Partly | Partly | Unknown at the seams | Retired: two models, a seam between them, twice the proof work. |
| 7 | Per-square levels solved together each pulse | Yes, exact dL | Yes: read from the water moved | Yes at every pulse length tested [measured: `py\out_implicit3_a.txt`, `py\out_implicit3_e.txt`] | Recommended. Cost unproven. |

## 3. What changed between my first write and now

- I first ranked design 5 or 6 highest. GPT's skeptical pass showed the steady field in 5 is only valid when nothing is filling or draining, and that 6 doubles the proof burden. I checked the argument against the twin behaviour and accept it.
- GPT's first verdict on design 7 was "fails" because it saw my first twin (one solver step per pulse). The third twin (`py\implicit_v3.py`) passes the scenes it listed. GPT did not see those results before its second answer was mostly formed; its statuses in section 7 of `03_gpt_improve.md` are out of date for dam, moat and weir-as-edge.
- GPT caught a labelling slip of mine: in the pools twin the -0.828 m level is the LOWER pool, not the upper. Checked: section 11 of `01_designs.md` is right, my note to GPT was wrong. [measured: `py\out_pools.txt` lines 4 and 12]
- GPT was right that the wave twin's default speed cap is 0.7 [measured: `py\river_models.py`].

## 4. Direct answers

### 4.1 Is your vector design sound, and what breaks?

Sound for a river nobody has touched, and it is nearly what the game and FlowWorks already do [measured: `D:\Luke\dev\RimMandrake\src\RimMandrake\FlowWorks\Source\Rivers\RM_MapComponent_RiverCurrent.cs`]. It is cheap: the connection test took 0.003 s in plain Python for 3,000 squares [measured: `py\out_OPR.txt`].

What breaks:
- "Connected to both edges" says nothing about how much or which way. A one-square leak past a dam keeps the whole lower river at full printed current.
- A narrowing keeps the printed speed although the water must run 2.5 to 4.2 times faster through it [measured: `py\out_diagI2.txt`, `py\out_OPR.txt`].
- Any channel the player digs has no printed vector at all. In the dam-plus-bypass scene 54 squares that really flow had none. [measured: `py\out_OPR.txt`]
- "Nothing to do with the bulk redistribution of water" is the root trouble: once the arrows and the volumes are separate, they can disagree, and the player sees a river flowing into a full pit that does not fill, or a draining reach with no current.

What you had right: the dam outcome (upper side holds, zero velocity; lower side drains off the map) is what the recommended model produces [measured: `py\out_implicit3_a.txt`]; and limitless source and sink at the map edges is the correct frame, with one caveat in question 1 of section 10.

### 4.2 Can water really move?

Yes. In the twin every decilitre that leaves a square arrives in a neighbour or crosses a map edge and is counted; the ledger error is 0 dL in all scenes [measured: `py\out_implicit3_a.txt`]. A moat fills because river water goes into it, and the river dips while it does.

### 4.3 Can the "thin surface water" layer be extended to something deeper?

That layer is ours (the Sheet kernel), not the game's; the game's shallow water is plain terrain and the Odyssey flood is a terrain layer with no simulation [measured: engine doc 10-17; feasibility study section 2, `D:\Luke\dev\RimMandrake\design\specs\2026-11-12-flowworks-natural-water-as-pits-feasibility.md`]. Extending the Sheet kernel as it stands (move one fifth of the level difference per pass) is design 2: correct but 26,000 to 166,000 passes to settle [measured: `py\out_D.txt`]. The idea itself, levels per square with exact volumes, is exactly the recommended design; what changes is the solver. Whether Sheet and river should then become one kernel is a build question, not answered here.

### 4.4 Can we afford a fluid simulation after all?

- Arithmetic of one pass over the largest census river (13,271 squares): 0.06 to 0.23 ms in C [measured: `py\bench_kernels_out.txt`]. Not the problem.
- The recommended model needs many passes per pulse. My twin: about 1,600 inner iterations per pulse, not falling when settled [measured: `py\out_implicit3_cg.txt`]. At [guess ~50%] 20 ns per square per iteration that is about 0.5 s per pulse for 13,000 squares: too slow as it stands.
- GPT's estimate with a better solver, sleeping and caching: 10 to 100 ms per 250-tick pulse for an ordinary adjustment, under 1 ms when settled, 0.1 to 1 s for a severe breach [guess ~35%, GPT's own low confidence].
- C# in the game: UNMEASURED. Repainting changed terrain: limited to 400 writes per pulse today, so re-typing 13,000 squares takes about 33 pulses [measured: feasibility study; arithmetic].

Answer: a volume-conserving model of the whole river is plausibly affordable [guess ~70%] if a settled river costs nearly nothing, which the twin does not yet show. A wave-carrying model is affordable in arithmetic and not yet in reliability.

### 4.5 Waves?

Wind chop: drawn only; the squares are too coarse for it. Flood surge after a dam break: draw a surge front (no extra water, no extra shove) on top of the recommended model. Real travelling waves need design 4, which produced one correct dam-break and three false floods [measured: `py\out_diagI.txt`, `py\out_diagI2.txt`, `py\out_diagI4.txt`]; keep it offline until it passes the textbook cases in section 8.

## 5. GPT's proposals that are NOT yet in any twin

All are reasonable; none is measured. They are work for stage B below.

| Proposal | My position |
|---|---|
| Solve with Newton's method and a general matrix solver | My own Newton attempt stalled on the moat and blew up on the weir [measured: `py\out_implicit2_b.txt`]. The simpler repeated-solve method in v3 converged everywhere. Try GPT's variant offline; do not assume it. |
| Cap edge speed at the wave speed for that depth | Sensible guard for breaches. Untested. |
| Source that responds to the level at the edge (gives less as the edge backs up) | See question 1. Untested. |
| Outlet as a one-way rating (takes water, never gives) | Agree. My twin already behaves this way at a fixed outlet level. |
| Round all edges together so no square can go negative | My simple truncate-and-carry rounding gave 0 dL error and 0 clips in the main scenes, but the safety limiter fired with the weir at a 417 s pulse [measured: `py\out_implicit3_wl.txt`]. GPT's method is the robust answer; its cost is UNMEASURED. |
| Check each pulse by also doing two half pulses, shorten on disagreement | Would fix the fill-time defect. Triples solver cost when active. Untested. |
| One "water speed" factor applied alike to inflow, movement, animation and shove when the game is under load | Agree; this is your "only slowly updating" idea done consistently. |

Same results on every machine (needed for multiplayer-safe and replay-safe saves): UNPROVEN for any design that uses fractional arithmetic inside the solve. The committed volumes are whole decilitres, which helps, but the solve itself is not yet shown to be bit-identical.

## 6. Staged build plan

No C# before stage C passes.

- Stage A (done): three twins, scenes in section 1.
- Stage B, offline Python, the proof: (1) cut settled cost: sleep closed bodies, reuse the last solution, better solver; target a settled river at under 5% of the cost of a disturbed one. (2) sub-stepping so fill time changes by under 10% between pulses of 25 and 2,500 ticks. (3) the edge-rounding method, with 1,000 random build sequences and 0 negative squares. (4) gate/sluice edge rule. (5) source and outlet rules from question 1. (6) a river at 45 degrees. (7) the acceptance matrix of section 7. (8) two rivers, river into sea, frozen river.
- Stage C, offline C# console program, no game: same scenes, bit-compared to the Python twin; timing at 3,000, 13,000 and 62,500 squares.
- Stage D, in game, minimal mod list: shader question (does the vanilla river animation follow a changed flow map?), repaint cost, pawn shove at computed speeds. These three UNMEASURED items decide the look.
- Stage E: replace the printed-current reader, then structures, then player digging.
- Research branch, any time, offline only: design 4 against the textbook dam-break and basin cases.

## 7. Acceptance matrix (stage B and C)

Scenes: plain river; full dam; dam closed mid-run; dam removed mid-run; weir; sluice half open; 3-square gap; side canal that rejoins; moat breach; overbank bypass; two rivers joining; river into sea; frozen river; closed lake at rest.

Run every scene over this grid, three seeds each for bed roughness:

| Variable | Values |
|---|---|
| Pulse length (ticks) | 25, 250, 2,500, 25,000 |
| River width (squares) | 3, 12, 30 |
| Depth (m) | 0.2, 0.6, 1.5, 10 (pit) |
| Direction | along the grid, 45 degrees |
| Size (wet squares) | 3,000, 13,000, 62,500 |

Pass lines:
- Books: 0 dL error over 100,000 pulses.
- Lake at rest: bit-identical after 10,000 pulses.
- No square ever above the highest or below the lowest level around it without a source (no false floods, no land wet).
- Plain channel discharge within 2% of the hand formula; 45-degree channel within 20%.
- Weir discharge within 5% of the hand formula.
- Final levels identical (within 1 mm) across pulse lengths; fill times within 10%.
- Settled river cost under 5% of disturbed cost.
- 1,000 random build-and-demolish sequences: no negative volume, no unconverged pulse left uncorrected.

## 8. Mod settings

| Setting | Default | Note |
|---|---|---|
| River water speed | 1.0 | One factor for inflow, movement, animation and shove together |
| Current carry strength | to be decided (question 2) | Physical value is about 1.05 m/s = about 81 ticks per square; today's lanes are 45 [measured: `py\out_I.txt`; `RM_MapComponent_RiverCurrent.cs`] |
| Minimum depth that carries | 2 cm | Below this pawns are not shoved |
| Upstream edge rule | to be decided (question 1) | |
| Solver time budget per tick | UNMEASURED until stage C | The game may lower water speed when over budget |
| Surge visuals | on | Drawn only |
| Debug overlay: levels, edge flows, sleeping bodies | off | |

## 9. Findings filed

Filed as `D:\Luke\dev\RimMandrake\infrastructure\state\lessons\20261112T211737Z-BENCH-river-solver-twin-findings.md`. The durable ones are: weirs must be edge rules, not raised squares; one solver step per pulse is not enough; never iterate the edge depth inside the solve (it gave a false zero flow and a +35 m transient) [measured: `py\out_implicit3_w.txt`].

## 10. Questions that are genuinely yours, ranked

**1. What does the upstream map edge do when the player backs the river up?**
- (a) Held level, your proposal ("that's the level the map edge would be set to"). Safe: a full dam leaves the upper pool at -0.100 m [measured: `py\out_implicit3_a.txt`]. Cost: a dam can never raise water, so no reservoirs, no flooding a valley, and a weir cannot raise the head for a mill.
- (b) Held discharge. Real reservoirs. Cost: a full dam with no spillway floods the map: +4.2 m in 10 river-minutes [measured: `py\out_OPR.txt`].
- (c) In between (GPT): full flow normally, tapering to zero as the edge level rises to a set height above normal. Reservoirs up to that height, no runaway. Untested.
My recommendation: (c) with the height as a mod setting, (a) as its zero value.

**2. How fast should the current carry things?**
The physically computed centre speed is about 1.05 m/s; today's shove is 1.89 m/s. Options: keep today's feel with a multiplier of about 1.8 (default), or go physical and slower. Either way speeds now vary: slack behind a dam wing, fast in a gap.

**3. Waves: drawn surge now, or hold the feature for a simulated wave?**
Drawn surge ships with the recommended model. Simulated waves need the research branch to pass, with no date I can promise.

**4. May a settled river cost a brief hitch when disturbed?**
A dam closing on a 13,000-square river may cost 0.1 to 1 s of solve spread over several ticks [guess ~35%]. Alternative: slow water for a few seconds instead. Your call on which is less ugly.

**5. Building a dam in deep water: where does the displaced water go?**
Pushed to neighbours (conserves, small local rise) or build refused above some depth. Not a physics question.
