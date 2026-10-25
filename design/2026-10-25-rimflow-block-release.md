# RimFlow: typed `block --on --until` and the block frontier (RIM-1 design pass, 2026-10-25)

Ticket: `tickets/RIM-1.md`. Approved direction: proposal C2 in
`design/2026-10-24-beads-and-rimflow.md` (sections 4 and 5). Every number here was measured on
2026-10-25 against the ledger as of commit `623a146740` (25,875 events, 4,302 items), replayed
read-only through `model.read()` + `model.replay()`. The script is
`src/RimMandrake/rimflow/retro_block_frontier.py`. It never calls `append`, `check` or the CLI.

## 1. What the code does today (kept)

- `block <ID> --reason R [--on X]` sets a FLAG (`blocked`, `blocked_reason`, `blocked_on`), not a
  state. `needs` is a separate axis: a closed window, not a defect. Nothing here changes that.
- **Nothing ever lifts a block automatically.** Only `unblock`, or the dependent itself closing,
  dropping or being superseded, clears the flag. `_announce_unblocks` (cli.py) printed the
  waiting items ONCE, at the moment their blocker went terminal (close, drop, supersede,
  `implemented` straight to done, the last criterion pass). Its docstring: "the blocker closing is
  EVIDENCE that the block may be stale, never proof". It already treated a dropped blocker the
  same as a done one in its wording ("If X delivered what they were waiting for, lift it").
- `rank()` skips every blocked item. `claim` and `start` do NOT refuse a blocked item (the
  completeness gate was removed by owner ruling 2026-08-21, and `claim` has never gated on the
  flag). The retro found 10 items claimed, started or implemented while formally blocked.
- `block --on` accepts any string; the target need not exist. No cycle check.

**Decision: keep announce-only.** The current behaviour never lifts, and the owner's rule (a
blocker ending is evidence, not proof; a dropped or superseded blocker never releases) agrees.
This change only makes the announcement typed, repeated and level-aware.

## 2. Design decisions

| Question | Decision | Why |
|---|---|---|
| Event field | `until` on `block`, one of `built`, `validated`, `done`; absent means `done` | One optional field on an existing verb. `validated` was added to the ticket's `built|done` because an item can owe L1 then L4, and "the defs resolve" (validated) is a real prerequisite level |
| Writing the default | The CLI writes `until` ONLY when it is not `done` | A default block stays byte-identical to what every old reader already accepts |
| Old readers | Any reader from step 2 on (`_tolerate_unknown_fields`) strips `until` and keeps the block; measured against the reader at `623a146740` (0 errors, one `tolerated` entry, block intact). A reader older than step 2 (`577d72d2f`) would refuse the WHOLE block event into `world.errors` | That is the same documented, accepted degradation as `verify --level`; only non-default blocks carry the field |
| How replay folds it | `item.blocked_until = ev.get("until")`, cleared everywhere `blocked_on` is cleared (6 sites) | No new state, no transition. Validation: enum check, and `until` without `on` is refused |
| Where the frontier lives | **Derived at read time**: `priority.block_frontier(world, seat=, on=)`, pure, about 25 lines. Never stored | Stored state drifts; replay is 0.5 s and every reader already has a `World`. Same reason `rank()` is derived |
| Satisfaction rule | `satisfied` when the blocker's state is in `SATISFIES[until]` (`built` accepts built/validated/done; `validated` accepts validated/done; `done` accepts done). `confirm` when the blocker is `dropped` or `superseded`, regardless of level | A dead blocker will never deliver, so it can never be "satisfied" |
| Lifting | **Never.** The item stays `blocked`; `rank()` still skips it; `next` keeps naming it until a seat runs `unblock`, re-blocks, or drops it | Owner rule. Authority and provenance on the lift are unchanged: `unblock` is still the owner-seat verb, with `--owner-said`/`--why` as RimFlow already requires |
| What `next` prints | After the offer (or the empty answer), up to 6 lines for the asking seat's items: `blocker now satisfied: X  (on B, now done; block asked for done). Evidence, not proof: lift it if it delivered, rimflow unblock X ...` and `blocker dropped, confirm: X  (on B, dropped; it will never deliver). NOT released: unblock it, block it again --on the real prerequisite, or drop it.` Confirm lines sort first | The 2026-10-07 analysis: a report beside `next` is not read; a line inside it is |
| `next --bench` | New section `BLOCKERS ENDED (the block may be stale; a seat decides): N`, up to 8 lines, all seats | BENCH and the owner triage the whole board |
| `why <ID>` | The frontier line under `BLOCKED:` | The command a stuck seat runs |
| One-shot announce | `_announce_unblocks` now goes through the frontier, so it is level-aware, and also fires on `implemented` (to built) and on a criterion pass that moves built to validated | A `--until built` block ends at `implemented`, not at close |
| Cycles | `cmd_block` follows the `blocked_on` chain of OPEN blocked items from the target; a path back to the item, or `--on` itself, is refused with the path printed. Writing path only | 0 of 78 historical `--on` blocks formed a cycle (measured), so nothing old is affected. A cycle can never satisfy, so refusing it costs nothing |
| Target not in the ledger | **Warned, not refused.** The frontier resolves the id at read time and skips an unknown one | Another clone may have filed it unpulled; the existing selftest blocks on an unfiled id; 0 of 78 historical targets were missing |
| Target already dropped/superseded | Refused at write time, naming the successor when there is one | Blocking on something that will never deliver is the error the frontier exists to catch |
| Target already at the level | Accepted, and the write prints `already ended: ...` | Blocking on a built item with the default `done` is legitimate ("wait for acceptance") |
| Leases and claims | Unchanged: a blocked item may still be claimed (no gate reinstated). `claim` now prints one warning line when the item is blocked. A frontier entry is never in `rank()` (asserted on the real ledger by the retro) | Owner ruling 2026-08-21 forbids reinstating gates on starting work; the 10 claimed-while-blocked cases suggest the flag was often already stale, which is what the frontier now surfaces |

## 3. Alternatives considered

**A. Auto-lift on satisfaction (Beads' behaviour, restricted to `satisfied`).** Replay would clear
the flag when the blocker reaches the level; `confirm` cases stay blocked.
Pros: zero seat effort; the 7 long-stale items would have been offered automatically.
Cons: makes the projection depend on a rule the old readers do not know (an old clone would show
the item blocked while a new one offers it, so two clones disagree on `rank()`); a done blocker
that did not deliver what was needed releases work silently; contradicts the existing
`_announce_unblocks` doctrine and the owner's "evidence, not proof".

**B. Stored frontier: a new `released`/`satisfied` event written by whichever CLI call notices.**
Pros: the moment of satisfaction is recorded in the ledger; RimPulse could read it without
computing.
Cons: a second, separately forgettable write for a fact replay already knows; a new verb (an
unknown verb to every old reader, collected into `world.errors`); union-merge can duplicate or
reorder it; it can disagree with the blocker's actual state after a later correction.

**C. Typed blocks as a separate dependency verb (`depends --on X --until L`), leaving `block`
untouched.** Pros: `block` keeps meaning only "something is wrong"; a dependency need not be a
defect. Cons: the 78 historical `block --on` events ARE the dependency record and would not be
covered; two verbs for the same wait splits every reader; a new verb is a design change the
VERBS comment warns against.

**Chosen: an optional `until` field on `block`, a derived read-time frontier, announce-only (the
design in section 2).** It covers all historical data with no migration, adds one tolerated
field, keeps `rank()` identical on every clone, and puts the signal inside the commands seats
already run.

## 4. The retro experiment (read-only)

`python3 src/RimMandrake/rimflow/retro_block_frontier.py --json <out>`, on `623a146740`:

- `block --on` intervals: **78** (the 2026-10-24 retro counted 73; it closed an interval only on
  `unblock` or terminal events and so merged re-blocks).
- Intervals that outlived their blocker's end, where the frontier would have named the item:
  **23**, of which **11** by more than 1 h (2026-10-24: 21).
- Stale for more than 170 h, each surfaced at the blocker's end, all `satisfied`: **7** (the six
  from 2026-10-24 plus `SALVATION_RITES_UNIFICATION_1`, 255.9 h, which the old script missed
  because it was ended by a re-block): `BIOME_DEFNAME_MIGRATION_WAVE_1` 507.3 h,
  `DESIGN_MATERIALS_REVIEW_1` 469.8 h, `FALL_LINE_FERAL_SURVIVOR_PAWNKIND_1` 388.6 h,
  `HOSTILE_MOBILE_PLANTS_1` 387.9 h, `SALVATION_RITES_UNIFICATION_1` 255.9 h,
  `SEADIVEHATCH_CACHES_FIRST_SEA_FLOOR_1` 234.8 h, `VAPOR_EMITTER_PLACEMENT_1` 174.3 h. Total
  lead: **100.8 item-days**.
- Dead-blocker intervals (blocker dropped or superseded): **2** (`B55` on `FINAL_WORLD_PREP_1`,
  dropped 1 s later; `JAWA_CULTURES_LEAK_TO_STRANGERS_1` on `ASHKARR_IDEOLOGY_MODE_CALL_1`,
  unblocked 3 s later). The rule names both `confirm` and **releases 0**. A release-on-any-close
  rule would have freed both unasked.
- On the final world: the frontier released **no** item and none of its entries is in `rank()`.
- Claimed, started or implemented while blocked: **10**, 4 of them after the blocker had ended.
- Counterfactual: had those blocks said `--until built`, **14** intervals would have surfaced
  97 to 430 h earlier still (mostly `CATHEDRAL_*`, `BAZAAR_*` and four items on
  `BRIDGE_TPS_REVIEW2_FIXES_1`). Not applied retroactively: historical blocks keep `done`.
- Today: the frontier is empty (0 lines of new noise); 12 open items are blocked on a
  built or validated item and stay silent under their default `done` level, by design.

**Bar from C2: passed.** It re-surfaces all 6 (now 7) intervals stale over 170 h at the moment
the blocker reached the level, and releases none of the dropped or superseded cases.
**Not shown by this:** that a seat would ACT on a surfaced line sooner. The lead hours are an
upper bound on the gain. C2's abandon rule stands: drop the frontier if, after 30 days, no
surfaced item was acted on within a day of surfacing.

## 5. Implementation map

- `model.py`: `BLOCK_UNTIL`; `block` opt field `until`; enum and `until`-needs-`on` validation;
  `Item.blocked_until`, set on `block`, cleared at the 6 sites that clear `blocked_on`.
- `priority.py`: `SATISFIES`, `block_frontier()`, `frontier_line()`; `why_not` prints it.
- `cli.py`: `cmd_block` (cycle and dead-target refusals, unfiled warning, default field omitted,
  `already ended` notice); `_print_frontier` in every `next` exit path; `BLOCKERS ENDED` in
  `next --bench`; `_announce_unblocks` via the frontier, also after `implemented` and a
  built-to-validated pass; `claim` warns on a blocked item; `--until` flag.
- `docs/AGENTS.md`: one paragraph under rule 5.
- `selftest_block_frontier.py`: 13 cases (model fold, levels, confirm-never-released, never
  applied, CLI refusals and output, default byte-compatibility, base-reader tolerance).
