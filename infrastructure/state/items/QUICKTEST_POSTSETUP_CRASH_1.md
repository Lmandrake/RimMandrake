# QUICKTEST_POSTSETUP_CRASH_1 — start_debug_game_ready crashes RimWorldWin64 after auto-research completes

Found live 2026-09-12 (FOUNDRY), chasing live-test blockers for the deploy
backlog. Reproduced identically **twice**, back to back, after fixing two
OTHER real crashes that were sitting in front of it on the same code path:

1. **`RUT_Webwork_{Anchor,Web,Gutter,Nest}` missing `thingClass`**
   (`257bbbc7f`) — NREd `ReadingPolicyDatabase.GenerateStartingPolicies()`
   on EVERY `Game..ctor()`, blocking both quicktest and real save loads.
   Fixed.
2. **A stale `CreatureBehaviors.dll`** missing the compiled fix for
   `RM_Alert_VerminPopulationBase` (`3e05542a6`) — the committed DLL
   predated a rebuild that should have included
   `RM_Alert_VerminPopulation_Inert.cs` (itself a fix for a near-identical
   crash found 2026-09-11). Rebuilding from current source produced a
   different DLL. Fixed.

**This crash is a third, still-unfixed one.** After both fixes,
`rimworld/start_debug_game_ready` gets much further — full quicktest
colony scenario generates, starting pawns take combat damage
("downed in battle"/"violent death" Ninefold log lines), and a long burst
of auto-completed starting research fires (six `[Ninefold] Ozzik/Ohm
satiation ... research completed` lines in a row) — then the log ends
**abruptly, mid-stream, with no exception, no crash-handler message, no
Unity fatal-error line**. `RimWorldWin64.exe` is confirmed gone
(`Get-Process` empty) within ~10-15s of the last log line both times, and
the bridge connection drops with `ConnectionResetError`/`WinError 10061`
immediately before that. This is consistent with a **native crash**
(access violation or similar) that Unity's managed exception handler
cannot catch or log — nothing here is a normal Harmony/XML error.

**Loading the real `CANONICAL_ASHKARR_2026-09-09` save via
`rimworld/load_game` does NOT hit this** — done successfully twice
tonight, once before either fix (proving the thingClass bug affected BOTH
paths) and once after. Only `start_debug_game_ready`'s own additional
scenario/combat/research auto-setup path reaches whatever this is.

## Why this matters
Blocks the live quicktest verify for `SHRINE_GUARDIAN_BIOME_GATE_1`
(needs a Desert-biome map), `SHOKKWEAVE_SOLE_SOURCE_1` (needs a
`RUT_Webwork`-biome map for its web-cutting/nest-raid routes), and
`WEBWORK_KIT_BUILD_1` (same biome need) — none of which can be tested by
substituting the real colony map, since all three test a BIOME-gated
mechanism the real colony's own tile doesn't carry. `start_debug_game_ready`
also has no biome-selection parameter, so even a stable quicktest would
land on an arbitrary biome unless combined with a fresh world/site pick —
untested here, moot until the crash itself is understood.

## What wasn't tried, and why
- **A managed-code root cause was not found** — no exception, no log
  line, nothing for RimSage or a source read to point at. This needs
  either a Windows crash dump (none was configured/captured) or narrowing
  by bisection (disable mod groups, retry) — both expensive, not attempted
  under tonight's time budget.
- **The minimal+target mod list workaround** (per
  `quicktest-crashes-full-modlist-use-cheap-mechanism-list`, the filed
  lesson this matches) was not attempted this pass — it requires a
  mod-list swap + two more cold-load cycles, and tonight's budget went to
  the two crashes that WERE fixed plus the world-map batch instead.

## spec
Make `start_debug_game_ready` reach a playable quicktest map on the full
592-mod list without crashing, OR document that quicktest on this list is
permanently unsupported and the minimal+target swap is mandatory for any
future mechanism live-test (in which case this item closes by updating
`rimworld-load-round`/`rimworld-debug-testing` doctrine to say so plainly,
not by fixing the crash).

## verify
`rimworld/start_debug_game_ready` reaches `programState: Playing` /
`jawa/list_pawns` succeeding, on the full mod list, at least 3 times in a
row (this session's own two-crashes-in-a-row precedent means a single
clean run is not enough evidence).

## criteria
Either a real fix (a third load-blocking bug found and corrected, same
shape as the two already fixed tonight) or a doctrine update ruling
quicktest OUT for this mod list and naming the minimal-list swap as the
only supported route — not both left silently true at once.
