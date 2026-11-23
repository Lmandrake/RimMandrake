# History: evidence and old lines that left `SKILL.md`

The lessons are in `../SKILL.md`. This file holds only the old lines that are no longer true, and evidence that no rule
needs. Git holds the rest. Each line below is a record, not a rule. Every correction below is of 2026-11-23.

- The skill once said "no 25-minute load", and that a load costs 23–30 minutes. A cold load on the full list takes many
  minutes; a small tier takes seconds (the `rimworld-load-round` skill).
- The skill once said that our one export never populated `quality`, `compSettings` and `exportedStorageSettings`. The
  later exports hold 14 to 51 storage blocks and 11 to 23 comp blocks each. Until 2026-11-23 the library dropped both
  kinds of block at each save, and `--roundtrip` did not see the loss.
- The skill once said that `validate()` catches the off-by-one in every layout. `validate()` asked for a `GravEngine` thing
  in the cell, and an export holds none ("verified zero in both of ours"). So `validate()` reported each real export.
- The skill once said that the choose page comes after `Page_CreateWorldParams`. The code looks for
  `Page_SelectStoryteller`.
- The skill once said that each room with no pawn spawns under fog, and that previews must be placed by hand. Both lines
  came from the README. The code clears all fog and writes the preview.
- The skill once said that `ShipLayoutDefV2` is never registered as a Def. The class is a Def (`ShipLayoutDefV2 : Def`), and
  `1.6/Defs` holds 4 layouts. Only a loose file is never registered.
- The skill once said that a landing consumes "the choose-page's ship marker". The source lesson (2026-08-28) is about the
  landing marker of a ship in flight.
- The section on the model fields was once headed "Fields this project has never seen populated".
- The skill once quoted the README as "obviously with a limit". The README says "obviously there will be a limit".
- The section on the live stamp was once headed "SUPERSEDED 2026-08-27".
- The skill once said that mid-game import does not exist, "is ours to build", and is a CHECK job, queued as **B-v2** in
  `infrastructure/state/queue/CHECK.md`. The file and the job are gone. It also said that a layout can only enter the game
  at world creation, and that `BuildFromLayout` is a pure function. Both were false.
- The skill once said "Colour the hull with STUFF, not paint". `repaint_hull.py` replaced the material route on 2026-08-28,
  after the owner's line about megabone. The deletion commit e9bd037b77 (2026-09-02) calls the paint proven live and
  owner-approved. The ledger holds no such ruling.
- The skill once said that an extender adds +500. The measured cap 51,480 does not fit: 4,680 plus nine times 500 is 9,180.
  The settings of 2026-11-23 fit exactly with a factor: (4500 + 9 × 5000) × 1.04 = 51,480, and 4500 × 1.04 = 4,680. The
  source of the factor 1.04 is unknown.
- The skill once cited, in a sentence about the export, that the licence "permits use and adaptation". The licence is the
  public-domain text.
