# Northstar: the "for the human" review map

status: **MessyConduit worked example; to be generalised into Northstar once the owner approves.**
Everything below was learned building ONE review map, for Messy Conduit, on 2026-10-04. It is a draft rulebook, not
yet a Northstar rule for every mod.

Owner, 2026-10-04 (typed): *"a 'for the human' review configuration that is prepared for me to quickly look at a well
presented tilemap to assess what things look like, act like, etc. It should be set up for me to easily interact with,
explore, and see the various key combinations to understand what it looks/acts like."* Layout chosen by question card:
**gallery plus free area**.

The worked example is `src/RimMandrake/GimmeSomeSlack/human_review.py`. Its key sheet is written to
`Transient/mc_human_review/` (`KEYSHEET.md` and `keysheet.html`).

## What it is, and what it is not

- **It is a place to look and poke.** It is not a test and it records no verdict. The functional script and the
  matrix still carry every pass/fail. The review map is the "does it look and act right" layer that only a human can judge
  (`debug_process.md` §4, the visual-quality boundary).
- **It is cheap and disposable.** It builds on a throwaway quicktest map in about 30 s on the mod's own tier, and it
  can be rebuilt at any time. Nothing is kept in a save unless the owner asks for one.
- **It covers the key looks, not every combination.** One station per look or state the owner would want to compare.
  The combinatorial board is the matrix's job (and `northstar-tests-must-be-economical` says even that must stay lean).

## Layout: a gallery and a free area

1. **Gallery.** Numbered stations sit in rows, and each row is one family (MessyConduit has floor cords, overhead lines
   and flexible hoses). Inside a row, put stations that differ in ONE thing next to each other: powered, then unpowered,
   then cut. The eye then compares neighbours, and nobody has to remember a picture from 100 cells away.
2. **Every station is self-contained.** It has its own battery and its own little grid, so poking one station (cutting
   it, emptying its battery) never changes another. The stations are spaced so that no effect of the mod can reach a
   neighbour. For cords that spacing is lateral reach R = 5 cells, read from `CordLayer.cs`. For overhead masts it is
   the 20-cell link range, and it applies between the gallery and the free area.
3. **Free area.** Open ground next to the gallery, stocked so the owner can build without fetching anything: a
   charged power source (solar plus full batteries), a conduit stub labelled *plug in here*, and stacks of every
   material the mod's buildables cost. It runs on the shipped defaults (for MessyConduit, aerial auto-link back ON),
   and it is placed where nothing he builds can interact with a station.
4. **North up, rows read top to bottom**, with a title label above everything that names the mod, the current global
   setting that changes every station (for MessyConduit, the cable style), and the key sheet's path.

## Labelling

- **Every station is labelled in the world**, never only on the key sheet. The labeller is
  `jawa/review_label` (JawaBench companion, dev only: `JawaBenchReviewLabels.cs`). It draws a dark box with a gold title
  and one short cream sub-line at a cell, every frame, until it is cleared.
- **A label has two lines: a number with a SHORT TITLE, then one clause.** The first build used the station's whole
  description, cut at 70 characters, as the sub-line. It cut off mid-sentence on screen ("...three lamps and a"). Write
  the in-world line as its own short field (`SHORT` in the script) and leave the long text to the key sheet.
- **Put a label above its station, outside the footprint.** Never put one over the thing to be judged. The first
  *plug in here* label sat on top of the very conduit end it pointed at, so it was moved one cell down and right.
- **Labels are process memory, not save data.** A MapComponent or GameComponent would be found by reflection and
  written into the savegame, so a review save would carry a class name from a dev assembly. The labels are drawn by a
  Harmony postfix on `MapInterface.MapInterfaceOnGUI_BeforeMainTabs` instead. They do not survive a restart or a load,
  and `--labels` re-pins them.
- **The station number is the shared key** between the world label, the key sheet card and `--goto N`.

## The calm world

On the review map, nothing moves unless the owner moves it:

- Weather is Clear and locked. The clock is pinned to noon with `time_set_ticks`, which scrubs the clock and simulates
  nothing.
- The incident queue is cleared, difficulty is set to **Peaceful** (`storyteller_swap`), and every non-colonist is
  destroyed. Use `destroy_bulk`, never a kill: killing explosive wildlife ignites the map.
- The game is **paused** when the build ends. Anything that changes over time is staged to a frozen state, for example
  the hose that stops half-filled. The key sheet tells him what unpausing will do.
- The review region is unfogged, unroofed and laid with plain Soil. Do not use `unfogAll`, which has wedged the game
  before.
- Colonists are left at the map centre, outside the region, and the script checks that no pawn stands inside it.
- **Screenshot mode is turned OFF at the end.** Runners switch it on for clean frames, but the owner needs the UI to
  select things and use gizmos.

## Interaction affordances

- **God mode is ON and research is finished.** He can place, break or deconstruct anything instantly. Masts need
  Electricity researched.
- **`--goto N`** frames station N, `F` the free area and `0` an overview. The overview is only as wide as the camera's
  zoom limit allows, so on a 175-cell gallery it shows part of it. Per-station framing is the real navigation.
- **One switch for global settings.** When a setting is global and changes every station (MessyConduit's cable
  style), do not fake several copies side by side. Show the current value in the title label, and offer one command
  (`--style X`) that flips it everywhere at once, plus the Mod Settings path. Four styles cannot stand side by side
  without changing the shipped mod. A per-region style override in the mod would be a behaviour change, and it would
  need the owner's ruling.
- **Every card says how to poke the station**: which gizmo, which setting, what to deconstruct, and what will happen.
  Dev-only levers (the hose's "DEV: flow through hose" gizmo, because there is no pump yet) are labelled as dev-only.

## Build discipline

- **Reuse the proven call shapes.** The script uses `run_live.LiveBridge` (the probe request/serial protocol) and
  `placer._ops`, and it batches builds per def in transmitter-before-connector order (`PowerConnectionMaker` wires a
  connector at spawn). Batteries are resolved by position and then charged. Masts are linked by id with auto-link OFF,
  and auto-link is turned back ON for the free area afterwards.
- **It is idempotent.** `--build` always clears the region first, so a rerun replaces the map rather than stacking a
  second copy on top. `--clear` wipes the region and its labels.
- **It checks itself offline first.** `--plan` checks the layout (every station inside the region, spacing, and no
  gallery mast within link range of the free area) and writes the key sheet, all without a bridge. It caught 7
  spacing faults before any bridge minute was spent.
- **It reports what did not build.** Every `build_batch` reports survived against wanted, and every refusal lands in
  the run's notes and the key sheet's "This build" block.
- **It keeps the mod's hash.** The builder changes nothing the mod does, so `human_review.py` is excluded from
  `modcheck.status.mod_hash`, like `validation.py`. Otherwise adding the review map would have made the recorded run
  STALE.
- **Verify by looking, once.** After the build, take an OS screenshot (`system_screenshot.py`) of a few stations and
  read it: are the labels legible, and is each thing where the card says it is?

## What NOT to do

- Do not make it a test. It has no verdicts, no pass bars and no recorded result.
- Do not cram every combination in. The owner asked for the key looks, and the matrix owns the combinations.
- Do not let stations share a grid or sit within reach of each other.
- Do not put labels over the subject, or let the in-world text run longer than one clause.
- Do not leave screenshot mode on, the game running, or weather and incidents live.
- Do not write a MapComponent or GameComponent for review tooling, because it would end up in the save.
- Do not hand the owner a command to paste. The agent builds it and frames it, and the owner looks.
- Do not live-test flyers here unattended, and do not run removal checks here (`debug_process.md` §6b, extended).

## Generalising (once approved)

Per mod, owe: a `human_review.py` (or a family script) with `--build/--goto/--labels/--clear/--plan`, a station list
whose stations are the mod's key looks and states, a free area stocked for that mod's buildables, and the key sheet.
The labeller and the calm-world steps are mod-independent and would move into a shared helper.
