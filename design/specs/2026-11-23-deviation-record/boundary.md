# Deviation record

The deviation-record section of [Bridge v2](../2026-11-23-bridge-v2/05_build_design.md) is implemented here for settings.
The owning files are `JawaBenchDeviationCore.cs`, `JawaBenchDeviations.cs`, and the deviation lines of
`JawaBenchModSettingsFieldTools.cs`, `JawaBenchHands.cs` and `Utils/scene.py`.
The offline checks are in `bridgetools/selftest_deviation_record.py`.

## ACCEPTS

- `scene.open(needs={"overlay": {"name": "fall", "entries": [{"typeName": "...", "field": "...", "value": "2"}]}})`
  sends the declaration to `jawa/session`. Omit it for the old call or use `"none"` to require a clean game.
  Entries take the settings tool's string values and optional dictionary key.
- `jawa/mod_settings_field` requires `typeName`. `action=deviations` reads the process record and `action=revert`
  puts back the holder's settings. These two actions take the required `typeName` but operate on the whole record.
  `driver` identifies the session holder for set and revert in an open session. Standalone callers share one record
  regardless of caller name. Their successful writes stay in effect until overwritten, explicitly reverted, or the
  process exits. An ordinary session can open with these entries live. A session cannot take over the overlay.
- The receipt gives the live overlay name/hash, every live entry, taint, dirty reach, SPOILED, and settings
  differing from their declared compiled defaults. An unreadable value has its own state.
  The JSON-lines journal is under the game's JawaBench data folder. The next process reports any outstanding debt
  from its predecessor. The settings themselves were in memory and the write guard protects the config.
- The record accepts calm, force and time/rate entries for later producers. This slice connects the settings
  writer. Behavioural effect is UNVERIFIED until a live recipe has been proved.

## DOES NOT SURVIVE

- A hang inside a write requires outside recovery. A failed undo leaves the journal and blocks further runs.
- Compiled defaults are read from the mod’s shipped-default snapshot, `DefaultValueAttribute` or a matching constant. Arbitrary field initializers
  and dictionary defaults cannot be recovered by reflection.
- A mod that writes its config without `Verse.LoadedModManager.WriteModSettings`, or another patch that writes
  independently, is outside the settings guard.
  The existing batch settings tool has its own write path.
- The on-screen stamp needs the display driver. If it cannot start, the write still has a journal and record.

## PROMISES

- **entries-apply-in-order-and-roll-back.** A failed entry is named and the attempted writes are undone in reverse order.
- **failed-revert-marks-spoiled.** A failed undo leaves the game SPOILED and records the debt.
- **taint-stays-after-revert.** Putting values back leaves the process mark. Saves carry the mark.
- **none-with-taint-is-not-clean.** An empty overlay does not clear taint.
- **receipt-lists-four-kinds-and-their-classes.** Live entries keep their kind and class. An active overlay shows its name and hash.
- **save-dirt-clears-on-fixture-load.** Loading a clean fixture clears save reach.
- **process-dirt-survives-fixture-load.** Loading a fixture cannot clear process reach.
- **const-is-refused-by-name.** A literal is refused before writing.
- **static-readonly-is-refused-by-name.** Replacing a static readonly field is refused before writing. A writable dictionary entry is its own target.
- **canonical-save-refuses-overlay.** A canonical save cannot receive an overlay.
- **second-holder-is-refused.** A different holder cannot apply during an overlay.
- **journal-precedes-first-write.** The debt is durable before the first write.
- **settings-write-to-disk-is-blocked.** The guard sits on `Verse.LoadedModManager.WriteModSettings` and skips the
  file write while an open session holds a settings entry of that mod.
- **mod-writesettings-override-body-runs.** A mod's own `WriteSettings` override always runs its body, and a set
  with no session never blocks the disk write. Callers that need this: `LuminousPigment` `validation.py` `_apply`
  (WriteSettings then ApplySettings), BlueDesert `weather_apply` (RM_BlueDesertWeatherTable.Apply, reads the config
  file) and FlowWorks `live_session.py` `b2_settings_dialog` (disk round trip). Seen red on two planted faults on
  2026-11-24: the guard on `Mod.WriteSettings` and its overrides (2 checks red), and a block that ignores the
  session (1 check red); green on the fix.
- **other-hand-differs-from-compiled-default.** A default comparison reads the live field, including changes by another hand.
- **standalone-settings-outlive-default-lease.** Putting back session settings at lease end leaves standalone settings in effect.
- **standalone-writes-accept-two-callers.** Two callers outside a session can each write a field and both values are retained.
- **legacy-settings-replies-keep-their-shape.** Set replies retain the legacy fields. Campaign refusals still carry `details.profile` and `details.profileWhy`.
- **legacy-settings-refusals-keep-their-scope.** A missing overlay display driver does not refuse a write. Instance readonly is left to the runtime. Standalone settings allow a plain session open, and session drain allows standalone writes.
- **companion-tool-schema-is-backward-compatible.** The manifest and C# preserve the required `typeName` and all existing parameters. `driver` on settings and `overlay` on session are optional additions.

## Caller audit of `31b5949637`

The call sites below are under `src/RimMandrake/` unless prefixed with `design/`. The review read the settings calls
and `set_settings` wrappers in the pre-ticket tree, including proof, northstar and modcheck runners. The table gives
existing call sites for each affected path. No existing caller was found that deliberately targets an immutable field
or writes settings inside `jawa/session`.

| Reply or refusal introduced by the ticket commit | Existing call site and disposition |
|---|---|
| `deviation` on a successful scalar or keyed set | `FlowWorks/northstar/live_session.py:494`, `design/concepts/Pyrelands/version/in_game/visit_8/scripts/settings_peek.py:18`. Removed from set. Scene receipts and the new `deviations` and `revert` actions return the record. |
| Campaign refusal lost `details.profile` and `details.profileWhy`, and introduced `CANONICAL_SAVE` or `COULD_NOT_LOOK` in its place | `Utils/modcheck/suite.py:537`, `ExplosiveKnockback/proof/storeroom_pit_proof.py:102`. Restored the legacy Campaign reply, including the reason. The plan's explicit `CANONICAL_SAVE` refusal and unreadable-save guard remain. |
| `NOT_THE_DRIVER` on a second standalone caller, or a caller writing during someone else's session or overlay | `FlowWorks/northstar/deep_lake_proof.py:220`, `Utils/northstar_driver/site.py:213`. Standalone callers share the record. The ticket requires retaining the active-session and overlay ownership checks. |
| `NO_SESSION` during session drain and `OVERLAY_HELD` opening a session with live standalone settings | `Utils/modcheck/suite.py:537` (set), `bridgetools/prove_run_until.py:150` (open). Removed. Closing, aborting and expiring a session put back its own entries. |
| `REFUSED: const <name>`, `REFUSED: static readonly <name>` and `REFUSED: readonly <name>` | `Utils/modcheck/suite.py:537` passes a field name through. Kept the named const and static readonly refusals the ticket orders. Removed the added instance readonly refusal. |
| `COULD_NOT_LOOK: no deviation frame driver` | `ExplosiveKnockback/proof/storeroom_pit_proof.py:102`. Removed the prerequisite. The companion still tries to start the display driver. |
| `COULD_NOT_LOOK` installing guards, a target-named journal or write failure (including `read-back differed`), and `SPOILED` after failed undo | `FlowWorks/northstar/live_session.py:494`, `Utils/modcheck/suite.py:537`. Retained for the required disk guard, journal, checked write and rollback. The target-named failure replaces the scalar `SetValue threw <type>` message. |
| `Give 'typeName'`, revised unknown-action and disallowed-type messages, earlier value/profile failures | `bridgetools/prove_companion_safety_fixes.py:70` exercises the disallowed-type branch. The tool again requires `typeName`. Legacy messages and validation order are restored apart from the required new guards. |

No existing settings writer intentionally loads a canonical save. `FlowWorks/northstar/tank_theft_live.py:56–59`
and `FlowWorks/northstar/pump_outflow_live.py:152–154` inspect protected files, then load `RM_TestSite_calm_v3`
(`Utils/modcheck/test_site_saves.py:67`). `Pyrelands/validation.py:3417–3429` reads the canonical save from disk.
Runners accepting a caller-supplied `--save`, such as `ExplosiveKnockback/proof/storeroom_pit_proof.py:40`, already
had their settings writes refused by the CAMPAIGN gate when pointed at a canonical save.

## LIVE

UNRUN: `python.exe src\RimMandrake\bridgetools\prove_overlay_settings.py` (E1 and E2 of
[Live tuning](../2026-11-23-bridge-v2/04_live_tuning.md)). Read actual injury and landing distance,
the unchanged config hash, the receipt and visible stamp, and the read-back after revert. Exercise an actual
settings save attempt with the overlay live, and reload a marked save in a fresh process. For legacy callers,
read two distinct fields after separate standalone writes and again beyond 600 seconds, then read them after explicit revert.
