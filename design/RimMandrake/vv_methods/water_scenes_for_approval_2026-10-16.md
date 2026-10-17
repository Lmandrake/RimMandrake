# Six water scenes for your approval (about 10 minutes)

**What this is.** Six small, concrete situations, each with what you should see happen. If you approve
them, a later agent writes tests from them **without ever reading the FlowWorks engine code**, so the
tests check *your rulings*, not the code's own idea of itself. This is decision 1 of
`D:\Luke\dev\RimMandrake\design\RimMandrake\vv_methods\STAGE3_gpt_skeptical_review_2026-10-16.md` §7.

**How to answer.** Each scene ends with one line. Put an `x` in one box, and add words after `note:` if
you pick *change*. Four scenes also carry a question where your rulings say nothing or disagree.
Those are marked **NEEDS A RULING**. A scene you strike is never tested.

**What I read.** Only your rulings: the FlowWorks design doc, the north-star walk, the 2026-10-11 hose/pump
rulings, the 2026-10-12 pond-volume rulings, the item texts and your quotes in the ledger. I did not read
the engine or the Python copy of it.

**The machine copy** is
`D:\Luke\dev\RimMandrake\design\RimMandrake\vv_methods\water_scenes_2026-10-16.scenes.json`, sealed
`sha256 5244a13e6fdf097ef64089654c8f19552f06edf7c37a2de2fbcda08adc4c7184`. Changing a scene breaks the
seal, and you approve it again.

## How to read the pictures

| mark | means |
|---|---|
| `\|` | map edge |
| `~` | a big lake or river touching the map edge: never runs out |
| `P` | one square of an enclosed natural pond, deep water, 4 levels when full: it can run out |
| `.` | undug ground |
| `1` `2` `4` | a dug cell of that depth, dry at the start |
| `G` / `#` | sealed sluice gate / metal grate gate, standing in the canal |
| `U` `=` `<` `>` | pump, hose, hose end set to Intake, hose end set to Outflow |

A **level** is one notch of depth. It is 1,000 L. A 1-deep cell holds 1 level. A deep square holds 4.
A **pulse** is one step of the water engine. Each "by pulse N" is a deadline, not a speed: earlier is fine.

**True in every scene:** water never stands on undug ground. A cell never holds more than its depth.
Where nothing is fed from a never-ending lake, the total water never goes up. It goes down only by
an amount the game tells the player was destroyed.

**Not judged by any scene:** looks and art, pawns and movement, fire, liquids other than water, rain,
refill and seepage (all switched off), and the order in which two equally good cells fill.

---

## S1. A canal dug from a lake fills end to end

```
|~~~~~~~~..........
|~~~~~~~~11111111..      an 8-cell, 1-deep canal off a lake that never runs out
|~~~~~~~~..........
```

**From your words.** *"liquid then flows into the canal to fill it, extending the source ... Any source
that touches the map edge is determined to be limitless."* (2026-09-16, the FlowWorks walk, "the
experience"). Also *"it's limitless once and for all"* (2026-09-16, ruling 16).

**You should see.** By pulse 10 all 8 cells are wet. At every moment the wet part is one unbroken run
from the lake end, never a puddle with a gap. A wet cell never dries again. The lake never shrinks.

**It fails if** the canal wets only its first cell and stops there. That bug happened on 2026-10-16.

**Not claimed:** how fast inside the 10 pulses.

`S1 verdict: [ ] approve  [ ] change  [ ] strike | note:`

## S2. A shallow trench beside a lake-fed pond fills

```
|~~~~~~~~..........
|~~~~~~~~44........      a dug 2x2 pond, 4 deep, touching the lake
|~~~~~~~~44111111..      and a 6-cell, 1-deep trench off its far side
|~~~~~~~~..........
```

**From your words.** *"We replaced 'sources' with just placed deep liquid reservoirs ... Filled very deep
tiles. Everything follows from that."* (2026-09-17, ruling 34). So a full deep cell must spill into a
shallower one beside it, or water could never leave a source (the design's "sort plus overflow").

**You should see.** By pulse 30 the pond is full (4 levels in each square) and all 6 trench cells hold 1
level. The wet trench is always one run from the pond end. After that, nothing changes.

**It fails if** the pond fills and the trench stays dry, or the trench wets only its first cell.

**Not claimed:** whether the pond is full before the trench starts.

`S2 verdict: [ ] approve  [ ] change  [ ] strike | note:`

## S3. A pump fills a canal that touches no water

```
...................
.PPPP..............      an enclosed pond of 12 squares (48 levels)
.PPP<====U====>11111.    hose with an Intake end in the pond -> pump -> hose with an Outflow end in a 6-cell canal
.PPPP..............
```

**From your words.** *"No, intake needs a pump. Adding liquid to any storage takes work (pump)."*
(2026-10-11, ruling 3). *"How could we also support having a pump suck water from a lake and put it in
a disconnected canal? ... Wouldn't even need to have a tank in the mix really."* (2026-10-11, the
liquid-network design). *"pumping water between two equal-volume reservoirs through a tank gets you
the same water in the end"* (2026-10-12, ledger).

**You should see.**
- Pump off for 20 pulses: nothing moves.
- Pump on: by 6 pump cycles + 10 pulses all 6 canal cells are wet. At every moment, what the canal
  and the hoses gained equals what the pond lost. The ground between them stays dry.
- Round trip: two equal dug 3x3 reservoirs, 4 deep, with a pump and one tank between them. Pump full
  A into B, then back. A ends with all 36 levels again. B, the tank and the hoses end empty.

**It fails if** water reaches the canal with the pump off, or the pond loses less than the canal gains.

**Not claimed:** which pond squares give up their water. The shape of A after the round trip (only its
total is checked). How fast the pump runs.

**NEEDS A RULING (S3.Q1).** A drill (your ruling 3, "part of Many Waters") or the new mapmaker
**Source** tap (2026-10-16) stands beside a dug canal. Does it pour into the canal?
(a) straight into the dug cell it touches · (b) only into a pipe or hose network, so the canal needs an
Outflow end · (c) both: the touching cell if there is one, else the network.
*Until you rule, the drill and tap are not tested.*

`S3 verdict: [ ] approve  [ ] change  [ ] strike | note:`
`S3.Q1 answer: [ ] a  [ ] b  [ ] c | note:`

## S4. A sluice gate shut, then open, then shut again

```
|~~~~~~~~..........
|~~~~~~~~111G1111..      3 cells, a sealed sluice gate, 4 cells; all 1 deep
|~~~~~~~~..........
```

**From your words.** *"There are sealed sluice gates (standard) and the ones made of metal grates that
always allow liquid ... Yes, both, two kinds of door."* (2026-10-06, ledger). This replaces the
2026-09-17 note that both doors pass water while closed. Also: a gate *"holds liquid back until
opened"* (2026-09-16, ruling 12, in summary form).

**You should see.**
- Shut: by pulse 6 the 3 upstream cells are wet, and the 4 downstream cells stay dry for as long as the
  gate is shut.
- Opened: by 8 pulses later all 4 downstream cells are wet.
- Shut again: the upstream cells stay full.
- A metal grate in the same place, never opened: by pulse 12 the downstream cells are wet anyway.

**It fails if** water gets past a shut sealed sluice, or a grate holds water back.

**Not claimed:** how full the gate's own cell is, the gate's art, or which way it turns.

**NEEDS A RULING (S4.Q1).** You shut the gate again while the downstream cells are full. That water is
now cut off from the lake. What does it do?
(a) stays exactly where it is until the gate opens, or a pump or the map-edge drain moves it ·
(b) leaks slowly back through the shut gate to the lake ·
(c) slowly dries up and vanishes. That would be a **second** case of water being destroyed. Today the
only case is overflow from filling in.
*Until you rule, the test says nothing about the downstream cells after the gate shuts again.*

`S4 verdict: [ ] approve  [ ] change  [ ] strike | note:`
`S4.Q1 answer: [ ] a  [ ] b  [ ] c | note:`

## S5. Nothing appears or vanishes: a pond pays for its canal

```
...............
.PPP...........          an enclosed 3x3 pond (36 levels), touching no edge,
.PPP1111111111.          and a 10-cell, 1-deep canal off it
.PPP...........
...............
```

**From your words.** Ruling 4, in summary form: *conservation of mass is true everywhere* (2026-09-16).
*"It does not destroy liquid if there's a place for it to go, but if it would 'overflow' it is
destroyed."* (2026-09-16, filling in). *"1 tank square, 1 deep water square/pond, 1 deep canal square
should all be the same volume."* (2026-10-12). *"levelset down to a smooth 0 or 1 across a too-wide
field like this, not 0, deep, 0"* (2026-10-16).

**You should see.**
- **A.** By pulse 14 the whole canal is wet and the pond holds exactly 26 levels (36 − 10). The pond
  visibly holds less water than at the start.
- **B.** The same canal off a 1-square pond (4 levels): exactly cells 1–4 end wet, the pond is empty,
  and the wet front then stays put for 40 more pulses.
- **C.** Then fill in canal cell 1: nothing is destroyed. Canal and pond still hold 4 levels between
  them, and no overflow message appears.
- **D.** A 3-cell, 1-deep run, full, touching nothing. Fill in the middle cell: exactly 1 level is
  destroyed, and the player gets a message giving the amount.
- **E.** A wide 6x6 basin, 2 deep, holding 8 levels heaped in its centre: it settles by pulse 20 into one
  connected shallow patch. No cell stays 2 deep while any cell of the basin is dry. Still 8 levels.

**It fails if** any total changes except D's announced level, or E stays "0, deep, 0".

**Not claimed:** which pond squares dry first. Which 8 basin cells end wet. Whether C's displaced level
lands in the canal or the pond. The wording of the message.

**NEEDS A RULING (S5.Q1).** How many 1-deep canal cells does one full deep pond square fill?
On 2026-09-16 you said *"Each source's square can supply up to five canal squares"*. On 2026-10-12 you
made a deep pond square 4 levels, the same as a deep canal square.
(a) **4**: the 2026-10-12 volume ruling replaces "five" · (b) **5**: the old supply rule still stands
on top of it.
*Until you rule, A and B are tested against 4.*

`S5 verdict: [ ] approve  [ ] change  [ ] strike | note:`
`S5.Q1 answer: [ ] a  [ ] b | note:`

## S6. Save and reload mid-flow, and the flow carries on

```
(S5 part A, saved at pulse 4 with the canal part-wet;
 plus S4 with the gate shut and the downstream half full)
```

**From your words.** None of your rulings mention save and reload. This scene rests only on ruling
4: water is neither made nor lost. That is why it carries a question.

**You should see.** Straight after the reload, every cell, the pond's stock and the gate's open or shut
state are exactly as they were at the save. No water is gained or lost across the reload. By pulse 30
the reloaded run ends exactly where a run that was never saved ends, cell for cell.

**It fails if** the fill front restarts from the lake end, water appears or vanishes, or a shut gate
comes back open.

**Not claimed:** load time, the save format, or saves from older versions of the mod.

**NEEDS A RULING (S6.Q1).** Must the reloaded run match the never-saved run at **every** pulse, or only
at the end?
(a) every pulse: the strictest test · (b) the same totals and the same end state; small differences on the
way are fine.
*Until you rule, only the end state is tested.*

`S6 verdict: [ ] approve  [ ] change  [ ] strike | note:`
`S6.Q1 answer: [ ] a  [ ] b | note:`

---

### For the agent that reads his answers

Parse the lines matching
`^(S\d)(?:\.(Q\d))? (verdict|answer): (.*?) \| note:(.*)$`; a box is chosen when it reads `[x]`. One
chosen box per line. A line with none or two chosen goes back to him; never guess it. Copy the verdicts
into `water_scenes_2026-10-16.scenes.json` under a new top-level `owner_verdicts` key (outside the seal).
Re-seal only when the owner changes a scene. Then hand the file to a blind test writer who has not seen
`RM_FlowKernel.cs` or the oracle.
