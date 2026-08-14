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
state | menu
note  | stack loaded, bridge answers, hasCurrentGame=false — BRIDGE measured
bridge | BRIDGE

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
L4 | KotOR droid x2, the 2nd must NRE or O12 re-opens | OPS | open
L5 | Full-map slag count — ONLY on a map generated this session | OPS | open
L6 | Never-run tools: list_things, clear_ui, roof batch | BRIDGE | open
L7 | Re-run P1 AV_DogSled through the reflection path | BRIDGE | open
E1 | Xenotype picker — 2 icons, pink square is the defect | owner | open
O18 | Scoped patch sweep — 585/585, 0 errors (cbe6f1c) | OPS | done

## SHUTDOWN
S1 | JawaSeaShaper.dll — SOLO, not live, gates any worldgen | OPS | open
S2 | jawa/ideo_of | BRIDGE | wip
S3 | jawa/biome_probe | BRIDGE | wip

## OWNER
10 | Is a DISCARDED measurement world permitted? | blocks v1 rows 2+7
11 | StrandedQuest — enable or stay inert? | no deadline tonight
-- | Start a game? BRIDGE is at the menu awaiting your word | one call, ~30s
