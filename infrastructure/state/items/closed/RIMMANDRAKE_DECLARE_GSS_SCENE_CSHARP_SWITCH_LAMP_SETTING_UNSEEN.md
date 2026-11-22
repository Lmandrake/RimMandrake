# RIMMANDRAKE_DECLARE_GSS_SCENE_CSHARP_SWITCH_LAMP_SETTING_UNSEEN

Filed by the run of item RIMMANDRAKE_DECLARE_FLOWWORKS_SCENE_CSHARP_PIT_REDRAW_UNSEEN (2026-11-21 ~6:50 PM PST), step 4 of its brief.

## spec

The same gap as RIMMANDRAKE_DECLARE_FLOWWORKS_SCENE_CSHARP_PIT_REDRAW_UNSEEN, in GimmeSomeSlack. Measured 2026-11-21 ~6:50 PM PST.
`build_match.py check --mod GimmeSomeSlack` reads "203 count, 0 to run" and lists 4 changed C# files that no check declares:
`Source/GimmeSomeSlackMod.cs`, `Source/Core/SwitchLight.cs`, `Source/Core/SwitchLampArt.cs`, `Source/GssSessionReset.cs`.
No GSS in-game check declares C# in `exercises` (only `P_Z_log_budget` declares "*" in version/exercises.json).

The concrete case: `sc_settings` (scene_settings: each feature's switch flips its state and back) and
`P_ST4_settings_roundtrip` count from rows on 934b35e053 (2026-11-20 6:06 PM PST). 2e073c2b60 (2026-11-20 11:23 PM PST,
"GSS switch lamp") then added the `switchLight` setting to `GimmeSomeSlackMod.cs`: a new scribed field, its reset, its
checkbox and its place in the Independent group. Both checks drive that settings class, and neither reruns.
197 of 204 GSS rows predate 2e073c2b60.

The fix: declare in `design/concepts/GimmeSomeSlack/version/exercises.json` (beside the locked table, so no entry
changes) the C# each in-game check's scene exercises, read from the scene script. Then run build_match and move the mod
per the Conductor's ruling if checks are named to rerun. Not done in the filing run (that run's brief covered FlowWorks).

## verify

Run the acceptance test below. Also, after the declarations, `build_match.py check --mod GimmeSomeSlack` names
`sc_settings` and `P_ST4_settings_roundtrip` as RERUN, or they carry rows made on a build that holds 2e073c2b60.

## criteria

Acceptance test: `bash infrastructure/state/items/RIMMANDRAKE_DECLARE_GSS_SCENE_CSHARP_SWITCH_LAMP_SETTING_UNSEEN.acceptance.sh`
(repo root). Exit 0 = pass: no UNDECLARED line names the 4 files, and build_match printed its verdict line. Expected 4 of
4 ok. Seen red on the base (origin/main 204f893012): 0 of 4, exit 1.

## refs


file: design/concepts/GimmeSomeSlack/version/exercises.json
file: src/RimMandrake/GimmeSomeSlack/Source/GimmeSomeSlackMod.cs
