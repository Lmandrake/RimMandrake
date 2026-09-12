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

## FOUNDRY offline investigation, 2026-09-12 (second pass, needs:offline)

**Root cause found and fixed in src, NOT yet live-verified — bridge held by
another FOUNDRY window on the minimal 25-mod list for DROID_SYSTEM_BUILD_1
(not stale, so not taken). Leaving `doing`. Do not close until the next
bridge session confirms 3x clean per this item's own `verify`.**

**MEASURED, not guessed:** built the full ResearchProjectDef prerequisite
graph from the freshest live-fingerprint-matched def dump
(`DefDump/captures/2026-09-12T11-53-17Z`, 592 mods, same set that reproduced
the crash twice) and ran a DFS cycle check over all 397 projects. Exactly
one cycle in the whole graph:

    RR_ElectricityBasics -> RR_ElectricityBasics   (self-loop)

`RR_ElectricityBasics` ("Research Reinvented: Stepping Stones",
`petetimessix.researchreinvented.steppingstones`) lists itself as its own
prerequisite. On disk (workshop 2868389782, v1.6, ResearchProjectDefs_Electricity.xml)
its authored prerequisite is plain `Smithing` — the self-reference is
injected at runtime by that mod's own `Patches_ResearchProjectDefs.xml`,
which uses a custom `RR.PatchOperationResearchPrereg` operation to re-point
every project that used to require vanilla `Electricity` onto
`RR_ElectricityBasics` (its "stepping stones" mechanism). The exact internal
step by which that walk also lands on `RR_ElectricityBasics` itself is
inside that closed custom PatchOperation class and was not traced further —
not needed to fix it, and grep confirms no OTHER installed mod references
`RR_ElectricityBasics` at all, so the self-reference is entirely internal to
that one mod's own patch file.

**Why this is a silent, unloggable native-looking crash — verified against
1.6 decompiled source (RimSage), `RimWorld/ResearchManager.cs:403-410`:**
`FinishProject` recurses into unfinished prerequisites with **no cycle or
visited-set guard**, and only marks `proj` itself finished (`progress[proj]
= proj.baseCost`) *after* that recursive loop returns. For a self-referencing
prerequisite this is unconditional infinite recursion — `proj.prerequisites[0]
== proj`, `proj` is not yet finished, so the very first check recurses into
`FinishProject(proj)` again forever. That is a `StackOverflowException`,
which .NET cannot catch or log even with a top-level try/catch — it
terminates the process immediately and completely silently. This matches
**every** recorded symptom: no managed exception, no crash-handler line,
process gone within seconds, right after a burst of real completions (the
non-cyclic prerequisites earlier in the chain finish and log normally on the
way down/up the recursion; the self-loop node itself never returns, so
nothing further logs before the crash — exactly "six research completed
lines in a row, then the log ends abruptly").

`RR_ElectricityBasics` is tagged `ClassicStart` — a project vanilla/scenario
auto-setup pre-completes for a non-tribal quickstart, squarely in
`rimworld/start_debug_game_ready`'s own auto-research path (confirmed via
`Root_Play.SetupForQuickTestPlay` → Crashlanded scenario, decompiled source)
and NOT in the real `CANONICAL_ASHKARR` save's path (research there was
already resolved turn-by-turn over real playtime, never re-walking
`FinishProject`'s prerequisite recursion on a cold graph) — exactly the
quicktest-crashes/real-save-does-not asymmetry already recorded.

**Ruled out this pass:** the `Dialog_NodeTree` "forcePause modal on the
stack" crash family (2026-08-31, `skills/rimbridge/references/traps.md:737`)
— same outward symptom (`ConnectionResetError`, clean log, process gone) but
confirmed (via decompiled `ResearchManager.FinishProject` and
`ScenPart_StartingResearch.PostGameStart`) that the scenario's own
starting-research grant calls `FinishProject(doCompletionDialog: false,
doCompletionLetter: false)` — no `Dialog_NodeTree` is ever created by that
path, so no modal pile-up is possible here. Also ruled out: anything in our
own `Ninefold` mod's `Patch_ResearchCompleted.cs` — its own hook only logs
and queues a `LetterStack` letter (not a blocking dialog), and is not
recursive itself.

**Fix applied (unverified live):**
`src/RimMandrake/MandrakePatches/Patches/RRElectricityBasicsSelfPrereq_Fix.xml`
— removes the one self-referencing `<li>RR_ElectricityBasics</li>` from its
own `<prerequisites>`, `MayRequire`-guarded on
`petetimessix.researchreinvented.steppingstones` (no-op if inactive), placed
in `mandrake.rm.patches` (loads last) so it is the final word on the def.
Added that packageId to `MandrakePatches/About.xml`'s `loadAfter`.
`validate_patch.py` (static + `--live` against the same 592-mod dump):
0 errors — the live `ModsConfig.xml` is currently the minimal 25-mod list
(another window's quicktest), so the guard reads a harmless no-op right now
by design; it activates once the full list is loaded again.

**What the next bridge session must do to close this:** restore the full
mod list, re-take a def dump, re-run the DFS cycle check (0 cycles
expected), then `rimworld/start_debug_game_ready` 3x in a row to
`programState: Playing` per this item's own `verify`. If it still crashes,
re-run the same DFS cycle check against the NEW dump first — this fix only
removes the one cycle found tonight; a different cycle elsewhere would need
the identical treatment.

## FOUNDRY live verification, 2026-09-12 (third pass) — CLOSED

**The XML-only fix (`RRElectricityBasicsSelfPrereq_Fix.xml`) did NOT take
effect and does NOT close this item on its own.** Deployed it
(`deploy_custom_mods.py --mod MandrakePatches --apply`), restarted the full
592-mod list cold (confirmed `activeMods` count 592 both before and after),
and BEFORE running any quicktest, read the live resolved def:
`jawa/get_defs ResearchProjectDef/RR_ElectricityBasics` still showed
`prerequisites: ["RR_ElectricityBasics"]` — the self-loop survived the
patch pass. Ran `rimworld/start_debug_game_ready` once to confirm: it
crashed identically (`RimWorldWin64.exe` gone from `tasklist.exe`,
`jawa/list_pawns` failing with `WinError 10061` connection-refused, log
ending mid-stream after a burst of `[Ninefold] ... research completed`
lines — the exact recorded signature). **Not traced further** why the
per-mod XML patch pass cannot out-order whatever RR's own custom
`RR.PatchOperationResearchPrereg` operation does — not needed, given the
fix below made it moot.

**Real fix: a Harmony prefix on `ResearchManager.FinishProject` itself**,
added to `src/RimMandrake/Ninefold/Source/Patch_ResearchManager_NoSelfPrereq.cs`
(lives in the already-loaded Ninefold Harmony assembly for build-cost
reasons only — it is NOT a Ninefold feature). On every call it strips any
prerequisite entry equal to the project itself from `proj.prerequisites`
*before* the unguarded recursive loop runs, regardless of which mod or
mechanism put a self-reference there and regardless of patch load order.
Logs a `Log.Warning` once per def it ever fires on (harmless no-op on every
other def). Built with
`"%USERPROFILE%\.dotnet\dotnet.exe" build ...\Ninefold\Source\Ninefold.csproj -c Release`,
deployed with `deploy_custom_mods.py --mod Ninefold --apply` while the game
was down (crashed from the confirmation run above), restarted cold on the
same 592-mod list.

**Verified 3x clean, per this item's own `verify` bar:**
`rimworld/start_debug_game_ready` → polled `jawa/list_pawns` to success
three times in a row, `RimWorldWin64.exe` staying alive throughout
(`tasklist.exe` confirmed after run 3). Player.log shows the guard fired
exactly once (`[RimMandrake.Ninefold] QUICKTEST_POSTSETUP_CRASH_1 guard:
stripped 1 self-referencing prerequisite entry from RR_ElectricityBasics`)
— expected, since it mutates the shared `ResearchProjectDef` object in
place, so runs 2 and 3 simply never had anything left to strip. Re-read the
live def afterward: `jawa/get_defs` now shows
`RR_ElectricityBasics.prerequisites: []`, confirmed empty for the rest of
this process's life.

Left the XML patch (`RRElectricityBasicsSelfPrereq_Fix.xml`) in place as
harmless defense-in-depth (still a no-op removal if RR ever ships the
self-reference as a literal, non-runtime-injected `<li>` in a future
version) — the Harmony prefix is the operative fix.

**Resting state:** full 592-mod list still active (confirmed), game left
on the quicktest map from verification run 3 (disposable debug map per
`map-state-is-disposable-debug`, nothing to save). Bridge released.

**CLOSED** — `rimflow close QUICKTEST_POSTSETUP_CRASH_1`.
