# The first-look savegame: the one standard for a save that the owner looks at

This is the one standard for every savegame that the owner opens to look at a mod: above all the first human look,
after the system judges the mod ready. The Maturation Pipeline builds that save in Stage 6 and he uses it in Stage 8
(`design/specs/2026-11-13-maturation-pipeline.md`, rule 5). A save for a later look, or a save of options for him to
judge, follows the same standard.

A biome mod adds the rules of its biome profile, `design/RimMandrake/biome_review_save_standard.md`: the biome's site
fixture, the required station kinds, the creature pens, the pre-walk gates and the shared builder. Where the profile is
silent, this standard applies. No other file holds review-save rules.

## The owner's words

- 2026-10-04 (typed), the first review map: *"a 'for the human' review configuration that is prepared for me to quickly
  look at a well presented tilemap to assess what things look like, act like, etc. It should be set up for me to easily
  interact with, explore, and see the various key combinations to understand what it looks/acts like."* Layout, by
  card: **gallery plus free area**.
- 2026-10-15: *"Not just a "hey look it's the Pyrelands" but a nice, orderly station-by-station demonstration of the
  mechanics to test, the art to examine, etc. That showed more hidden bugs than anything."* and *"I need text signs
  added to the savegame to tell me what to DO at each station."*
- 2026-11-12, the matrix scene (lesson
  `infrastructure/state/lessons/20261112T184403Z-CONDUCTOR-owner-looks-are-matrix-not-one.md`): a scene for his look is
  one prepared cell replicated over the variables that matter, with a grid key. Then, on this standard: *"this is the
  generalized version of the matrix scenes... combine. It's important for "first human look" after the system thinks a
  mod is ready for the human to have a well prepared savegame like this that's dense and informative and intuitive and
  well labeled"*.

## What the save is, and what it is not

- **It is a place to look and poke.** It is not a test, and it records no verdict. The mod's functional script and its
  bars carry every pass and fail. The save is the "does it look and act right" layer that only a human can judge
  (`design/RimMandrake/debug_process.md` §4, the visual-quality boundary).
- **It is dense.** One save shows the whole version of the mod: every capability that a player can see, as a station
  or as a matrix grid (§Density).
- **It is a deliverable.** The first-look save is kept until he says delete (`standing_rulings.md` §Options he must LOOK
  at ship as a savegame). A working map that is not his look is disposable and is rebuilt at any time.
- **It reaches him only after a pre-look** (§The pre-look). Nothing he finds on his look should be a missing texture, a
  stale file, an unlabelled thing or a cell that the agents did not look at.

## What the save holds

1. **The title sign** at the map's start: the mod, its Design Version, the value of each global setting that changes
   every station, the map's grid key (which block of the map holds which stations and grids), and the key sheet's path.
2. **The gallery**: numbered stations, one per key look or state (§Stations).
3. **Matrix grids**: one prepared cell replicated over the variables that change the look (§Matrix grids).
4. **Boards**: a sign with no build, for a thing that has no place on the ground (Mod Settings, events, world map).
5. **The free area**: open ground, stocked, for him to build and try things (§The free area).
6. **Creature pens**, for a mod that adds or changes creatures: one pen for each creature kind, staged by
   `src/RimMandrake/Utils/modcheck/walk_pens.py` (owner, 2026-11-24). A biome mod's pens follow its profile §5.

North is up. Blocks read top to bottom, then left to right, in walking order.

## Stations

- **One station per key look or state** that he would want to compare. Stations are numbered 1..n in walking order.
- **Rows are families.** Inside a row, stations that differ in ONE thing stand next to each other (powered, then
  unpowered, then cut). The eye then compares neighbours, and nobody has to remember a picture from 100 cells away.
- **A comparison has a control.** A station that claims a difference (X heats, Y grows faster, Z protects) has a
  station beside it whose title starts `CONTROL:`. The control changes ONE thing, and its sign names that thing. Both
  start where the mechanic visibly works: a control that only repeats the ambient compares nothing.
- **Every station is self-contained.** It has its own power, fuel or supply, so a poke at one station (a cut, an empty
  battery) changes no other station. The stations are spaced so that no effect of the mod reaches a neighbour. Read
  the reach from the mod's code (Gimme Some Slack: lateral cord reach R = 5 cells in `CordLayer.cs`, and the 20-cell
  mast link range).
- **A state that changes over time is staged frozen**, through the mechanic's own route, and named for its age
  ("burned 8000 ticks ago"). A station that shows an aftermath (a blast, a collapse, a flood) has a START twin beside
  it that shows the moment before; `save_keeper` refuses a save that lacks the twin (`src/RimMandrake/Utils/walk_twins.py`,
  owner, 2026-11-23).
- **No orphan station.** A station shows only content that a player's game can reach (a roster, patch, recipe,
  research, GenStep, incident or setting). Content that is built but not wired into play, or wired but not built, gets
  a line on the key sheet with its item id, not a station.

## Matrix grids

A single case hides the defect at the case next to it. A single-case showing of a pit missed the north ladder that was
drawn behind the pit wall at 2 m of water (2026-11-12). So, where a variable changes the look, the save holds a grid.

- **Prepare one cell.** The cell holds every fitting the mod has, in every facing (N, E, S, W), in each material that
  draws differently, with goods in it where the thing holds goods. Example: a pit with ladders on its N, S, E and W
  walls in steel and in wood, ramps, spikes, gates, every installed fitting, and goods inside.
- **Replicate the cell over the variables that matter.** A variable matters when it changes what is drawn or how a
  thing acts: depth, fill, liquid, ground, look or style, power state. Read the candidates from the mod's bars and from
  its declared range of situations (`src/RimMandrake/rimflow/roles/builder.md`, the offline model).
- **Two variables per grid**: one along the rows, one along the columns. A third variable makes a second grid, never a
  cube. A setting that is global and cannot differ per cell is one switch, not a grid (§Interaction).
- **Choose the values where the look changes**: both ends of the range, and each edge between them where the drawing
  or the behaviour changes (empty, a little, half, at the brim; each depth band). Do not choose evenly spaced values
  that skip an edge.
- **Every cell is the same prepared cell.** Only the grid's variables differ between cells. Any other difference is a
  fault of the grid.
- **Cells are spaced like stations**: the reach of the mod's effects decides the pitch, and no cell changes another.
- **Each grid has a grid key in the world and on the key sheet.** A label at the head of each row and each column names
  the variable and its value. Each cell has a coordinate (`B3`) and a label that gives its values ("B3: depth 4, water
  at the brim").
- **The agents look at every cell first** (§The pre-look). A grid is pre-looked cell by cell, never as one overview.

Worked example: the FlowWorks VISUALS block, pits D1 to D4 x dirt or stone x dry, water, tar or scorched
(`src/RimMandrake/FlowWorks/review_map.py`, data `review_map_stations_visuals.json`).

## Density

*"dense and informative and intuitive and well labeled"* (owner, 2026-11-12). Density is a rule for what the save
covers, not a count of things on the map.

- **Every capability of the version that a player can see has a station, a grid cell or a board.** A capability that
  is only on a screenshot or only in a test is not in the save. The key sheet lists each capability that has no place,
  with its reason ("a mapgen census: the script's row").
- **The combinations that change the look are on grids.** The combinations that do not change the look stay with the
  scripts.
- **Each station and each grid is visible as a whole at one zoom level.** The whole save is walkable in one sitting.
- **No filler.** A station or a cell that teaches nothing that a neighbour does not already show is removed.

## The free area

- Open ground next to the gallery, with nothing he can build there able to reach a station or a cell. For aerial or
  ranged links, the link range applies between the gallery and the free area.
- Stocked so that he builds without fetching anything: a charged power source where the mod uses power, a stub
  labelled *plug in here*, and stacks of every material that the mod's buildables cost.
- It runs on the shipped defaults.

## Labels, signs and the key sheet

Every station, cell and board carries its sign in three places:

1. **In the save, with no agent needed:** one vanilla book on the gap cell north of the station's west corner. Its title
   is `SIGN <key> <name> - DO: <do>`, so a mouse-over shows what to do. Its info card holds the whole sign. The builder
   makes the book with `sign_book` and places it with `place_signs` (`src/RimMandrake/Utils/modcheck/reviewmap.py`). The
   book is the sign of record.
2. **Floating labels** from the JawaBench labeller (`jawa/review_label`, `JawaBenchReviewLabels.cs`, dev only): a dark
   box with a gold title and a cream sub-line. `save_keeper` writes them to a sidecar beside the save, and `--labels`
   pins them again after a load. Labels are process memory, not save data, so they are a convenience.
3. **The key sheet**, word for word.

Text rules:

- **The key is shared.** The station number or the cell coordinate is the same on the book, the label, the key sheet
  and `--goto`.
- **A sign has a short title (at most 24 characters) and one clause (at most 56)**, then LOOK, DO and DECIDE. LOOK
  names the thing to look at. DO is one imperative with the exact menu path. DECIDE is the question he answers, and it
  ends in "?". Write each field as its own short field: a long description cut to fit ends mid-sentence on screen.
- **A suspected weak spot is the DECIDE** ("does young grass read as young, or just small?"), so he is pointed at it.
- **Plain words.** No defName unless the DO needs it. A dev-only lever is labelled as dev-only.
- **A label sits above its subject, outside the footprint.** Never put a label over the thing to be judged.
- **A changed cell says so.** Each station and cell is a cell record for `src/RimMandrake/Utils/look_changed_labels.py`.
  A cell whose inputs changed since his last look is labelled *changed since your last look*, a new one *new*, and a
  removed one is named on the notes sign (`design/RimMandrake/validation_map_and_rules.md` rule 2f).

The key sheet (`KEYSHEET.md`, and `keysheet.html` to read once) names every station, every grid and every grid cell.
It starts with the map's grid key and each grid's axes. For each station and cell it gives the sign, *Look for*,
*Poke it* and *If you unpause*. It ends with a "This build" block: what was verified, what was refused, and each fault
that is known and not fixed. The sheet repeats the save; it does not replace it.

## The calm world

On the save, nothing moves unless he moves it.

- Weather Clear and locked. The clock pinned to daylight with `time_set_ticks`, which simulates nothing (noon, or the
  biome's brightest hour).
- Peaceful storyteller (`storyteller_swap`) and the incident queue cleared. Every non-colonist removed with
  `destroy_bulk`, never a kill: killing explosive wildlife ignites the map. Every fire out unless a station stages it.
- The region unfogged, unroofed where nothing needs a roof, and laid with the mod's or the biome's common ground. Do not
  use `unfogAll`: it has wedged the game.
- Colonists outside the stations and grids. No station needs a colonist; a DO line that needs one says so.
- The save is paused-only. It is not built to survive running. Each sign's *If you unpause* says what unpausing does,
  the bad things included.
- Mod Settings at the shipped defaults.
- Screenshot mode OFF at the end: he needs the UI to select things and use gizmos. The game is never fullscreened or
  focused.

## Interaction

- **God mode ON, research finished.** He places, breaks and deconstructs anything at once.
- **`--goto <key>`** frames a station, a cell, a board, the free area (`F`) or the overview (`0`). The overview is only
  as wide as the camera's zoom limit, so per-station framing is the real navigation.
- **One switch for a global setting.** When a setting is global and changes every station, do not fake several copies
  side by side. Show its value on the title sign, and give one command (`--style X`) that flips it everywhere, plus the
  Mod Settings path. A per-region override would change the mod, and it is decided as a change to the mod.
- **Every sign says how to poke**: which gizmo, which setting, what to deconstruct, and what happens.

## The pre-look

Nothing reaches him unread (`standing_rulings.md` §Nothing reaches the owner unread).

1. **The builder looks once at every station and every cell**: an OS screenshot (`system_screenshot.py`) of each, read
   for legible labels and for each thing where its sign says it is.
2. **A fresh judge pre-looks the save** by `design/RimMandrake/scene_look_judge_brief.md`: a first judge with the open
   question, then a different judge with the checklist. Each gets the uncropped frame and one labelled crop per
   station and per grid cell, with the grid key, and is never told what was changed or fixed.
3. **A station or cell that fails the pre-look is fixed, or it is named on the key sheet's "This build" block and in
   the walk brief's known-not-fixed list** (`src/RimMandrake/rimflow/roles/walk_brief.md`). Then he is told that the
   save exists.

## Keeping and filing the save

- **Back up the Saves folder first.** `save_keeper` (`reviewmap.py`) saves the game, refuses to overwrite a save of the
  same name, proves that exactly one save is new, and writes the label sidecar.
- **The save is on the game where he looks**: ArchBig or ArchSmall, on the mod's small list
  (`design/concepts/<Mod>/version/small_list.json`, which holds the advanced-zoom mod).
- **Name**: `RM_<tag>_review_<YYYYMMDD>`, with the mod's short tag.
- **Filing**: the builder writes the key sheet in `Transient/<tag>_human_review/`, then files `KEYSHEET.md` (and
  `COVERAGE.md` where the builder makes one) into the mod's `src/RimMandrake/<Mod>/review/`, held from deploy. The
  `review/` copy is the one to open. The save itself stays in the Saves folder of its game, and `KEYSHEET.md` names the
  save and that game. `look_changed_labels.record` writes the save's cell records to
  `design/concepts/<Mod>/look_cells/<save>.json`. The Stage 6 visit's `SUMMARY.md` names the save in its Exit block, and
  the walk brief gives its absolute Windows path.
- **A builder made before this standard keeps its folder** (FlowWorks: `northstar/review/map/`) until it next changes.

## Build discipline

- **One builder per mod**, `human_review.py` or `review_map.py`, with `--plan`, `--build`, `--goto`, `--labels`,
  `--clear`, and a save step (`--save`, or Gimme Some Slack's `save_review_map.py`). A biome mod uses the shared biome builder of its profile §9.
- **`--plan` checks offline first**: every station and cell inside the region, the pitch, no reach between stations,
  and the key sheet written, with no bridge. On Gimme Some Slack it caught 7 spacing faults before any bridge minute.
- **`--build` is idempotent.** It clears the region first, so a rerun replaces the map. `--clear` wipes the region and
  its labels.
- **It reports what did not build.** Each batch reports survived against wanted, and each refusal goes to the key
  sheet's "This build" block.
- **Reuse the proven call shapes**: `reviewmap.LiveBridge`, batched builds per def in the order the mod's wiring needs.
- **It keeps the mod's hash.** The builder changes nothing that the mod does, so it is excluded from
  `modcheck.status.mod_hash`, like `validation.py`, and `review/` is in `.hashignore`.
- **No MapComponent or GameComponent** for review tooling: the game would write its class name into the save.

## What NOT to do

- Do not make the save a test: no verdicts, no pass bars, no recorded result.
- Do not show one hand-picked case where a variable changes the look: make the grid.
- Do not let stations or cells share a supply or sit within reach of each other.
- Do not put a label over the subject, or let the in-world text run longer than one clause.
- Do not leave screenshot mode on, the game running, or weather and incidents live.
- Do not hand him a command to paste. The agent builds and frames; he looks.
- Do not live-test a flyer's flight here, and do not run removal checks here (`debug_process.md` §6b, extended).

## Worked examples

- Stations, free area, labels: `src/RimMandrake/GimmeSomeSlack/human_review.py` (first built 2026-10-04), its key sheet
  in `src/RimMandrake/GimmeSomeSlack/review/`.
- Matrix grid: the FlowWorks VISUALS block (`src/RimMandrake/FlowWorks/review_map.py`).
- Biome profile: `src/RimMandrake/Pyrelands/human_review.py`, its `review/KEYSHEET.md` and `review/COVERAGE.md`.
- The first save built to this whole standard is the first-look save of the first mod that reaches Stage 6 (owner's
  design decision of 2026-11-18). Gimme Some Slack's waits until every MOD row of its proof passes (his card of
  2026-11-13).
