# Owner-asks audit against delegation_policy.md §2 — 2026-11-04

Item `OWNER_ASKS_AUDIT_FIFTY_NINE_DEEP` (GPT rec 4, `design/RimMandrake/rimpulse_gpt_review_2026-10-22.md`).
The 59 items GPT counted on 2026-10-22 no longer exist as a set: by this audit the ledger replay held **54** open
`needs=owner` items, and the `*_TITAN_POPULATE_*` family named in the item (18 items, not 20) had already left his
list: all 18 are `proposed`, `needs offline`, so there was nothing left to fold.

Rule applied: an item stays his only if a line of `design/RimMandrake/delegation_policy.md` §2 reserves it; anything
else went back to agents through `rimflow needs --to offline` (or `drop` when his own card had already answered it).

## KEPT — reserved

| item | §2 line | what he owes |
|---|---|---|
| `PIT_ACCESS_BUILD_LADDERS_CLIMBING_JUMPS` | 1 (L4) | A5: the portable ladder and climbing gear seen in place; A1–A4 pass at L2 |
| `TITAN_CAMPS_SCAVENGERS_EVENTS_1` | 1 (L4) | A6: a titan passage and a scavenged site in play |
| `DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS` | 1 (L4) | A3: timber and steel drawbridges in game |
| `THRIXWEAVE_RESELL_BUILD_DEARLY_SOLD` | 1 (L4) | A2: thrixweave dearly priced at a rare exotic trader |
| `WATER_SCENES_S5_JUDGE_THIRD_DRAFT` | 1 (L4) | approve scene S5, third draft (published 0ca30b1fd0) |
| `WEEPINGSTONES_NET_FLEEING_FLIER_1` | 6 (flyer) | the skarrin is a flyer: its live test needs him present |
| every `<FOLDER>_DESIGN_FIRST_TOUCH` (38 at the audit, 40 by its end) | 7 (new) | certifying the Designer's first-touch pass |

Line 7 was added to §2 by this audit. It records his ruling of 2026-11-04 (`FIRST_TOUCH_BUILD_DESIGNER_READS_FIRST`:
*"… certifies it with the user/clarifies confusion …"*) and changes nothing in it. Each sitting certifies a different
mod's spec, so this is not a one-ruling family and is not folded.

## RETURNED — to agents (`needs offline`)

| item | why it is not his |
|---|---|
| `ICON_OUTLINE_REPAINT_1` | answered by his card 2026-11-03 (*"Fix any live art that needs fixing…"*) |
| `GRAFFITI_PUNK_ART_REVIEW_1` | art is delegated (owner 2026-10-22); the move to his bucket came from FOUNDRY's retirement, not from a ruling |
| `DRAWBRIDGE_SWING_DESIGN_LESS_RIDICULOUS` | his own order: motion study offline first, then build, then his look (L4 at the end) |
| `DRAWBRIDGE_UP_FIX_RAISED_LOOKS_LOWERED` | direction ruled 2026-11-03 (v3 option B); building it is agent work |
| `DRAWBRIDGE_EDGE_FIX_RAISED_READS_AS_POLE` | a render defect with evidence; the fix is technical |
| `DRAWBRIDGE_BUTTON_FIX_CLICK_SEEMS_DEAD` | a UI feedback bug |
| `STEVE_LANE_UNSTICK_BRAKED_OWNER_20EE` | Operations work on a machine we can reach (also reassigned OWNER → BENCH) |

The generator behind that last row (the steward's T+120 rung) is filed as `STEWARD_RUNG_FIX_ASKS_THE_WRONG_GROWNUP`.

## DROPPED

| item | why |
|---|---|
| `SANDLION_ART_RETIRE_OWNER_KEPT_ORPHANS` | his card 2026-11-03: unused art is "not something to solve"; the note on the card names these six sprites |

## The 14-day cutoff

`classify_ledger()` in `src/RimMandrake/Utils/pulse/pulse_core.py` dropped an ask from his list silently once it was
14 days old (`RULE_WINDOW_SECS`). That cutoff is gone. Each ask now carries `blocks`, the open items that are blocked
on it, and the row text names them. `order_rows` puts asks that block an agent first and then sorts oldest first (it
used to sort newest first). Checks: `src/RimMandrake/Utils/pulse/selftest_pulse.py` (a 40-day-old ask is still listed;
the constant is gone; an ask with a blocked item outranks an older free one and names that item).
