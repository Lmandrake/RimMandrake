# LAUNCH_HELD_COLONIST_WARNING_1 — the launch dialog names colonists held inside something

Decision taken by question card 2026-10-08: "Warn at launch". Gap left by `HOLDER_SAFETY_LAUNCH_1`
(closed: vanilla records a held colonist lost, with a letter, when the map closes; nothing warned
before the launch).

## spec

1. Hook (RimSage, decompiled 1.6): `GravshipUtility.PreLaunchConfirmation(Building_GravEngine,
   Action)` builds the launch confirmation and adds a `Dialog_MessageBox` in the same call (only caller
   `RitualOutcomeEffectWorker_GravshipLaunch`). GimmeSomeSlack's launch handling (9401f7a73) is not on
   this hook: it rides `CompAerialAnchor.PostDeSpawn` during `GenerateGravship`, after the confirm.
2. `RM_Patch_LaunchHeldColonistWarning` (EnvironmentalHazards) postfixes it and appends one red
   warning block to that dialog's `text`: every colonist or colony prisoner, alive and unspawned, not
   in a transporter, whose `SpawnedParentOrMe` is a spawned thing on that map NOT of the player's
   faction, named as "Name (inside <holder>)". Generic: covers the brine jacket
   (`RM_Building_BrineEncasement`), Hwelgrue (`RM_CompGutSwallow`), Titanoslime (`RM_CompEngulfer`)
   with no dependency on their mods. It never blocks the launch.
3. Mod Setting: "Warn at gravship launch about held colonists", default on.

## criteria

- A1 L0: EnvironmentalHazards DLL builds; envhazards fuzz `held` family passes (exactly one of 64 flag combinations is named)
- A2 L1: on a load, Player.log has no "[RM EnvironmentalHazards] launch held-colonist warning" error (the patch armed)
- A3 L2: live, a colonist sealed in a brine jacket (or swallowed by a Hwelgrue) is named in the gravship launch confirmation with what holds them; with nobody held, the dialog is vanilla
- A4 L2: live, with the setting off the dialog is vanilla

## verify

Run each criterion at its stated level and record it with `rimflow verify LAUNCH_HELD_COLONIST_WARNING_1 --criterion <ID> --result pass|fail|partial --config <list> --evidence <path>`:
- L0: offline build, selftest/fuzz/lint (already run at implementation).
- L1: one minimal-list load, read Player.log for config/cross-reference errors and the specific line, or one spawn-and-read bridge probe.
- L2: one quicktest map via the bridge or modcheck: set up the scenario in the criterion, step ticks, read the state named.
Evidence is the Player.log line or bridge read the criterion names; a screenshot is not evidence of state.
