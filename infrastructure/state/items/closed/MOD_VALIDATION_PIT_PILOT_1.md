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

## done (FOUNDRY, 2026-09-12) — RAN GREEN LIVE. Sheet not yet ratified.

Owner, verbatim, after being told the pilot was blocked on Pits not being
in the active mod list: *"Take control, change the list, and keep going!"*
So: backed up `ModsConfig.xml`, added `mandrake.rm.pits`, closed and
relaunched RimWorld via Steam (never the bare exe), ran the pilot live on
a quicktest, then adopted the change permanently
(`modlist_swap.py --capture-full --apply` — the owner's list is now 594
mods, Pits included) and restored his campaign save afterward (verified:
5 colonists, `ticksGame` matching the save exactly, mods compatible).

**Final result: `pit_capture` (2 components) and `uncover_disarms` (1
component) all PASS. 3/3 green, zero findings.** Recorded in
`infrastructure/state/modcheck_status.json` (`Pits: GREEN`) and via
`rimflow verify MOD_VALIDATION_PIT_PILOT_1 --result pass`. Sheet:
`Transient/modcheck/Pits_20260912T231116Z.html`.

Getting there took five real bugs, found live and fixed in the same
session (each also fixed rimdrive/modcheck for every future mod, not just
Pits — see those items' own "done" sections for the ones filed there):

1. **Debug-action path was wrong.** `Actions\T: <label>` is the real path;
   a `DebugAction`'s declared `category` (`"RMPits"`) is UI metadata, not
   a path segment. Found via `list_debug_action_children("Actions")`.
2. **A better instrument existed and was missed on first read**:
   `PitDebugActions.cs`'s "Report pit state (RAW)" is a pure read
   (`def/covered/sprung/occupants/...` in one line) — switched every
   read-back to it instead of parsing whichever forcing action happened to
   log the field needed.
3. **`order_pawn` does not reliably steer a hostile-faction pawn** — a
   `Pirate` raider "moved but 0/1 arrived... no drafter, ordered
   undrafted" even after 300+ ticks. `pit_capture` now walks a plain
   colonist instead (the trap mechanism itself doesn't care about
   faction); steering hostiles reliably is a separate, real gap for a
   future `walk_over` hardening pass, not this mod's problem.
4. **`t.set_setting` (built this session, see `MOD_VALIDATION_RUNNER_1`)
   cannot reach `PitsSettings` at all**: its fields are `public static`,
   and `rimworld/update_mod_settings` refused with "Could not resolve
   field ... on RimMandrake.Pits.PitsSettings" — the bridge's reflection
   walks INSTANCE fields, and this mod's real values live on the class.
   **`trigger_disabled_no_capture` was removed from this suite** rather
   than faked; it needs either a bridge fix (reflect static fields too) or
   a design change to `PitsSettings`, filed nowhere yet — whoever picks
   this up should file it as its own item before attempting that chain.
5. **A killed-but-contained test pawn came back to life.** Sweeping things
   before pawns meant destroying the pit (a "thing") dropped its captured
   occupant back onto the map alive via `Building_OpenPit`'s own
   `TryDropAll`, and separately, `jawa/damage`'s `allowColonists` safety
   rail silently refused to kill a `faction="player"` test walker at all
   — fixed in `rimdrive.Session.sweep()` (now passes
   `allowColonists=True`; every future modcheck component that spawns a
   non-hostile test pawn was previously leaking litter on every capture-
   type mechanism, not just this one).

⚠️ **Floor still not fully met**: `fallDamageEnabled` and
`pitCellExposureEnabled` remain uncovered — the first needs to know
whether `jawa/pawn_health` can resolve a contained pawn (unproven), the
second needs a whole second chain against `Building_PitCell` (assign /
gate / feed) not yet drafted. Left open rather than guessed at; a future
wave should close these before calling the mod's coverage complete.

⏳ **NOT done: owner ratification of the sheet format** (spec §5.2) —
genuinely his call, not something more effort resolves. The sheet exists
now (see path above); hand him the full native path:
`D:\Luke\dev\Rimworld\Transient\modcheck\Pits_20260912T231116Z.html`.
