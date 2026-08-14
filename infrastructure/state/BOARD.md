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
L1 | ANSWERED OFFLINE: no deck re-lay. Swap 1 hull cell per thruster | CREATE | done
L2 | DEAD: the export holds ZERO pilot consoles. Nothing to path to | CREATE | done
L3 | Empire raid — read the faction BACK, pass points explicitly | VISION | open
L4 | O12 CONFIRMED — 2nd droid threw NRE as predicted | OPS | done
L5 | DIAGNOSED: minSpacing 4 == hardcoded cluster radius 4, step aborts. Fix 8a7a5ee | OPS | done
L6 | PROVEN LIVE: list_things, clear_ui (4 windows), roof batch (16 cells, read back) | BRIDGE | done
L7 | PROVEN LIVE: AV_DogSled spawned as Vehicles.VehiclePawn at 60,120 | BRIDGE | done
W1 | Sea baseline read on a disposable world — 25.0% water, 2 bodies | VISION | wip
E1 | Xenotype picker — 2 icons, pink square is the defect | owner | open
O18 | Scoped patch sweep — 585/585, 0 errors (cbe6f1c) | OPS | done

## SHUTDOWN
S1 | JawaSeaShaper.dll — SOLO, not live, gates any worldgen | OPS | open
S2 | jawa/ideo_of — BUILT, undeployed | BRIDGE | built
S3 | jawa/biome_probe — BUILT, undeployed, 3-state find | BRIDGE | built
S4 | ⛔ CANCELLED — warnOnFail CANNOT fire on the cluster branch. Superseded by S9 | OPS | done
S9 | Jawa_Patches: scrapfields minSpacing 4->1 (8a7a5ee). THE row 4 fix | OPS | open
S5 | world_stats units FIXED: perimeterTiles + centroidLatNorm | BRIDGE | built
S6 | jawa/set_faction_relation — unblocks L3's aimed raid | BRIDGE | built
S7 | jawa/inspect_string — reads comp status; gates CREATE's thruster test | BRIDGE | built
S8 | DEPLOY ALL: BridgeTools 30 tools md5 d7e7c6c1, --gm REQUIRED | BRIDGE | open

## OWNER
12 | O12 droid raids — which of 3 routes? v1 KEEP faction is broken | BRIDGE confirmed | tell PROJECT · detail: OWNER_DECISIONS.md #12
10 | Discarded measurement world? ANSWERABLE YES — quicktest builds a world | unblocks rows 2+7 | tell PROJECT or VISION · OWNER_DECISIONS.md #10
11 | ✅ ANSWERED BY OPS — STAYS INERT, tag [v2]. V1_SCOPE:86 gives v1 ONE QuestScriptDef and row 3 (*The Claim*) already fills it. Not a fresh design call. Residual for VISION: want it in v2, or swapped for The Claim? | resolved | no owner input needed
-- | Real colony/worldgen — still YOURS to lift, sea unsolved | separate | tell PROJECT · needs S1 deployed first
