# PEN_ANIMALS_UNSTICK_STATUES_LEARN_TO_WALK

Review-save pen animals are placed by `jawa/artboard_stage` (pawn ops) with a 60000-tick `JobDefOf.Wait`
so each holds its planned facing (`JawaBenchArtboardTools.cs`, the `kind == "pawn"` branch). A keeper save
keeps them frozen for a game day and `jawa/order_pawn` refuses wild animals (0/64,
`infrastructure/state/lessons/20261016T035329Z-BENCH-review-save-pens-hold-animals-with.md`), so the owner
cannot watch them move. Progress log: `Transient/release_pens_2026-10-16/PROGRESS.md`.

## spec

- `jawa/pen_release(rects | pawns | allMap, includeHumanlike=false)` — ends the CURRENT Wait job
  (`EndCurrentJob(InterruptForced, startNewJob: true)`), reads back the next job, remembers cell + rotation
  in memory. Returns selected / released / notReleased / skipped[reason] / jobsBefore / jobsAfter.
- `jawa/pen_pin(rects | pawns | allMap, restore=true, ticks=60000)` — the inverse: optional return to the
  release cell and facing, then the same Wait pin the artboard gives.
- Source: `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchPenTools.cs`.
- Wiring: `python3 src/RimMandrake/Pyrelands/human_review.py --release-pens` / `--pin-pens` (one footprint
  rect per pen station, `pen_rects(S)`). FlowWorks `review_map.py` spawns pens with `jawa/spawn_pawn`
  (no Wait pin), so it needs nothing.

## verify (live, owed: needs a deploy while the game is closed)

1. `build.py --gm --apply` with the game down; the live tool list shows both tools.
2. Load a Pyrelands review keeper save; `human_review.py --release-pens`: `released` == the pen specimen
   count (16 facing pens x 4 + 1 ashwallow), `notReleased` 0, `jobsAfter` holds no `Wait`.
3. Unpause ~600 ticks: positions change, every animal still inside its pen rect (doors hold wild animals).
4. `--pin-pens`: `pinned` == selected, `returnedHome` == released count, rotations read back as S/E/N/W.
5. Refusal path: `jawa/pen_release allMap=true` a second time selects 0 and says so (success false).

## criteria

- O1 L0: companion builds clean with both tools in the DLL tool table; `selftest_pyre_review_map.py` section 11 passes (done at a2b4a7cd22).
- A1 L1: deployed with the game closed; on a quicktest map, animals given a Wait pin are released (`released` == selected, no `Wait` in `jobsAfter`), re-pinned with `returnedHome` and rotations read back, and a second `allMap` release selects 0 and reports it.
- A2 L2: on a Pyrelands review keeper save, `human_review.py --release-pens` releases every pen specimen, and after ~600 unpaused ticks they have moved yet each is still inside its pen rect; `--pin-pens` restores S/E/N/W facings.
