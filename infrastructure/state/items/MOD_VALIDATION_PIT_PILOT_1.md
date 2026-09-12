# MOD_VALIDATION_PIT_PILOT_1 — the pit mod proves modcheck end-to-end

Blocked on MOD_VALIDATION_RUNNER_1 shipping. Spec:
`design/RimMandrake/mod_validation_runner_spec.md`.

## spec
Write the pit mod's `validation.py` (Python on the modcheck library): one component per settings toggle
(the floor) plus beyond-toggle components for everything the mod defines —
falls-in on walk-over, climb-out succeeds for a pawn that can, climb-out fails
for one that cannot, and the rest of its functionality hit once each. Run it
green on the minimal list; put the HTML sheet in front of the owner ONCE to
ratify the report format before the retrofit wave adopts it.

## verify
- `rimflow verify` event N/N green recorded; sheet path handed to the owner
  with a full native path.
- The script exercises every settings toggle (library floor check passes),
  and every chain tears down to a verified-empty area (spec 1b).

## done so far (FOUNDRY, 2026-09-12) — script drafted from source, NOT run, NOT ratified

`src/RimMandrake/Pits/validation.py` written against `modcheck` (see
`MOD_VALIDATION_RUNNER_1`, built same session). Grounded in the mod's actual
source, not guessed: `PitsMod.cs` for the four real toggles
(`trapTriggerEnabled`, `fallDamageEnabled`, `escapeEnabled`,
`pitCellExposureEnabled`) and their defaults; `PitDebugActions.cs` for the
exact debug-action labels, its `CAT="RMPits"` category, and its
`[RMPitsDebug] TAG ...` log lines, which turned out to be this mod's own
purpose-built read-back channel (`jawa/drain_log`), so `modcheck.suite`
grew two new verbs for it: `expect_log_contains` and `expect_pawn_despawned`.

**The obvious first design was wrong, and reading the source caught it
before it shipped**: `Building_OpenPit.Spring()` calls `p.DeSpawn()` then
moves the pawn into `innerContainer` — a captured pawn is CONTAINED, not
merely relocated, so it has no map position at all and the spec's own
worked example (`expect_in_cell_of`) would have silently asserted the wrong
thing forever (a captured pawn always fails an in-cell check, for the
wrong reason — despawned, not "not there"). Caught by reading
`Building_OpenPit.cs` before writing the chain, not by a live run.

3 chains drafted: `pit_capture` (arm → walk a hostile over it → verify
`sprung=True` in the log AND independently via `expect_pawn_despawned` →
force a struggle interval and read `occupantsBefore=1`),
`trigger_disabled_no_capture`, `uncover_disarms`.

⚠️ **Floor NOT fully met**: `floor.uncovered()` against this script reports
`fallDamageEnabled` and `pitCellExposureEnabled` still uncovered.
`fallDamageEnabled`'s natural test (compare a captured pawn's health
before/after) needs to know whether `jawa/pawn_health` can resolve a pawn
once it's inside `innerContainer` — genuinely unclear from source, and
guessing wrong here means asserting something false with a straight face,
which this whole system exists to prevent. `pitCellExposureEnabled` needs
a second building entirely (`Building_PitCell`, the holding-platform family
— assign/gate/feed) not yet drafted. Left open rather than covered with an
unverified guess.

⏳ **NOT done, and cannot honestly be claimed done right now:**
1. **A live green run.** Needs a modlist swap to MINIMAL+Pits and a
   restart — the owner's live campaign colony was up throughout this
   build; discarding it for a quicktest is not this seat's call to make
   unilaterally (same reasoning as `RIMDRIVE_LIBRARY_BUILD_1` and
   `MOD_VALIDATION_RUNNER_1`'s own live-run gaps).
2. **Owner ratification of the HTML sheet format** — an explicit
   human-in-the-loop step in the spec (§5.2: "sheet reviewed by the owner
   once to ratify the report format"). No sheet exists yet to review,
   since nothing has run. `report.py`'s renderer is offline-tested for
   structure (mod name, verdict colour, component rows) but the FORMAT
   itself — what a sheet should show, laid out how — has not been shown
   to the owner at all.

Both gates are genuinely his and the environment's, not more effort on
this seat's part — see `RIMDRIVE_LIBRARY_BUILD_1` and
`MOD_VALIDATION_RUNNER_1` for the same shape of deferral. Whoever has a
safe quicktest window next: run
`python.exe src/RimMandrake/Utils/modcheck/cli.py run Pits --debug`,
expect the two uncovered-toggle chains to need adding first (or accept a
`floor.uncovered()` warning), fix whatever the first real run gets wrong
about the assumptions flagged above, THEN take the sheet to the owner.

## found live (FOUNDRY, 2026-09-12) — Pits isn't even in the active mod list

While proving `RIMDRIVE_LIBRARY_BUILD_1` live (owner-authorized quicktest,
same session), checked whether this pilot could ALSO be run live on that
quicktest: `mandrake.rm.pits` is **deployed to disk**
(`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\Pits` exists)
but is **absent from the live `ModsConfig.xml`** — `jawa/get_def` on
`RM_OpenPit_Bare` returned "No ThingDef named" on the quicktest, and a
direct grep of `ModsConfig.xml` for "pits" found nothing.

This is a NEW blocker beyond the two already listed above, and it changes
what "a safe quicktest window" can even prove: a quicktest reuses whatever
mod set the RimWorld PROCESS already loaded at its last full start — going
to the main menu and back does NOT reload `ModsConfig.xml`, so enabling
Pits there would do nothing until an actual process restart. Proving this
pilot live therefore needs the owner's NEXT full-list restart to have
`mandrake.rm.pits` enabled first (a one-line `ModsConfig.xml` addition,
zero risk, but still his mod list to change) — not just "a spare
quicktest moment" the way `RIMDRIVE_LIBRARY_BUILD_1`'s proof was.
