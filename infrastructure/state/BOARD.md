# BOARD.md — the roster the owner reads at a glance

_Rendered by `python3 src/RimMandrake/Utils/board.py`. **This file is the planned
roster; the live seat status is NOT in here** — that comes from the session
registry and the per-seat stamps, so it cannot go stale by neglect._

**Format is `id | text | owner | state`, pipe-delimited, one item per line.**
States: `open` `wip` `done` `held` `blocked`. A `done` row may carry a commit
hash in the text. **Edit this file by hand — it is short on purpose.** Anything
that needs a paragraph belongs in the owning seat's queue, not here.

⚠️ **Work that is not on this list is fine and expected.** The list exists to be
compared against, not to be complete. What it must never do is show an item as
open that is closed, so **close rows here in the same commit that closes them.**

---

## GAME
_Removed 2026-08-14. Game state is MEASURED by `gamestate.py`, not written here —
a fact you can measure must not also be a sentence someone remembers to update.
The board reads it with its age and who measured it._

## V1
1 | Empire reskin | — | done
2 | Faction exclusion | VISION | held
3 | The Claim quest — built, deployed, never seen | BRIDGE | open
4 | Three terrain overrides — scrapfields open | OPS | wip
5 | Jawa xenotype | — | done
6 | Weapons / gear | — | done
7 | Ordinary worldgen | OPS | held
8 | Gravship | CREATE | done

## LOAD
C1 | CALL #1 tool census — 26 jawa, exact set-match | BRIDGE | done
C2 | Startup log harvested before any spawn — all baselines clean | BRIDGE | done
L1 | SmallThruster at stern x45 z131 -> WarningThrusterInside | CREATE | open
L2 | order_pawn canReach on pilot console, pathEndMode interactioncell | CREATE | open
L3 | Empire raid — read the faction BACK, pass points explicitly | VISION | open
L4 | O12 CONFIRMED — 2nd droid threw NRE as predicted | OPS | done
L5 | MEASURED: 4 chunks on the 13:54 quicktest. Row 4 does NOT close | OPS | wip
L6 | Never-run tools: list_things, clear_ui, roof batch | BRIDGE | open
L7 | Re-run P1 AV_DogSled through the reflection path | BRIDGE | open
W1 | Sea baseline read on a disposable world — 25.0% water, 2 bodies | VISION | wip
E1 | Xenotype picker — 2 icons, pink square is the defect | owner | open
O18 | Scoped patch sweep — 585/585, 0 errors (cbe6f1c) | OPS | done

## SHUTDOWN
S1 | JawaSeaShaper.dll — SOLO, not live, gates any worldgen | OPS | open
S2 | jawa/ideo_of | BRIDGE | wip
S3 | jawa/biome_probe | BRIDGE | wip
S4 | warnOnFail=true on the scatter defs — then 90s quicktests | OPS | open
S5 | world_stats unit fixes: centroidLat deg->frac, raggedness | BRIDGE | open

## OWNER
12 | O12 droid raids — which of 3 routes? v1 KEEP faction is broken | BRIDGE confirmed | tell PROJECT · detail: OWNER_DECISIONS.md #12
10 | Discarded measurement world? ANSWERABLE YES — quicktest builds a world | unblocks rows 2+7 | tell PROJECT or VISION · OWNER_DECISIONS.md #10
11 | StrandedQuest — enable or stay inert? | no deadline | tell OPS · OWNER_DECISIONS.md #11
-- | Real colony/worldgen — still YOURS to lift, sea unsolved | separate | tell PROJECT · needs S1 deployed first
