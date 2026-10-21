## spec
Build the ruled drawbridge: `design/RimMandrake/flowworks_drawbridge_design_2026-10-20.md` §Ruled design (R1-R13). That
section is the spec; the option bodies it replaced are gone. Summary:
- Timber and steel only; one structure with a **bascule leaf + winch**, a **gate leaf** (custom multi-cell door on the
  hinge-bank anchors, not vanilla semantics) and **planks drawn beside the bridge** (art, never an item, no
  `MinifiedThing`). Max leaf length by material; longer = two leaves, each tipping to its own hinge.
- Raise from either side, lower only from the winch side. Timber hand-winched; steel powered; **steel without power and
  any leaf whose winch is lost freeze where they are**.
- Raising **never calls `Collapse`**. Riders (chosen by band, not position) tip deterministically to legal hinge-bank
  squares, keep faction and gear; **overflow falls** through the ordinary descent event. Underpass pawns untouched.
- Peace mode auto-lowers/opens for own pawns; **any free hostile locks it** (trapped or captive hostiles do not); lock is
  atomic and cancels a pending auto-lower; it never raises by itself.
- Raiders: trench rules + winch sappers/breachers + raid planks (single reserved deployment, span limits, exactly once).
- Pathing: **force an immediate pocket-grid rebuild on toggle** (today 60-tick limit, `RM_PocketGrid.cs:31,216`), new
  immutable offset snapshots, re-path pawns over changed squares, revalidate results from the old generation (1.6
  pathing is batched jobs, MEASURED).
- Per-leaf versioned save record; map-scoped; re-key on gravship `PostSwapMap`, never anchor-loss.
- Hoses and power cords on a leaf disconnect while raised and rejoin when lowered; rigid pipe/conduit never on a leaf.
Dependencies: `POWER_CORD_BUILD_BENDS_WHERE_CONDUIT_BREAKS` for the cord rule; art as a separate item after the build.
Engine checks: `design/RimMandrake/flowworks_drawbridge_pipes_gpt_review_2026-10-20.gpt_read.md` §GPT's engine claims.
ESTIMATE 8 to 11 agent-days plus art; about 1 day live on the minimal list. Open owner questions: design doc §Open owner
questions (planks' use, winch loss, two-leaf control, gravship edge).

## verify
- L0: offline spike — list every `Decked`/`ThingGrid` reader bypassing `DeckAt`; time one pocket rebuild on the largest dug
  test map.
- L1: selftests — tipping order and destinations (six riders, one free square: one lands, five fall); band selection;
  lock predicate (free vs trapped hostile); per-leaf record round-trip; forced rebuild on toggle.
- L2 (live rows, design R13): RAISE_PATH, RAISE_TIPS_RIDERS, RAISE_SPARES_UNDERPASS, LOWER_ONLY_FROM_WINCH,
  TWO_LEAF_TIPS_OWN_HINGE, HOSTILE_LOCKS, STEEL_UNPOWERED_FREEZES, WINCH_LOST_FREEZES, RAID_UP, RAID_PLANK, SAVE_MIDRAISE.
