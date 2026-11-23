## spec

GimmeSomeSlack visit 2 (2026-11-19 20:04 PST, game a, tier gimmesomeslack_flowworks, 13 mods): `proof_all.py --live
--skip-offline --only scenes` logged one error, `Tried to get ThingsOfDef of MinifiedThing, use
ThingsMatching(ThingRequest.ForGroup(ThingRequestGroup.MinifiedThing)) instead`, with no stack trace (Player.log line 664,
throwers `?`), so `Z_log_budget` read FAIL on that tier. The same scenes on tier gimmesomeslack (runs 2 and 4) logged no
such error. Also in that window: "Two power nets on the same cell (30,162) / (34,162): Battery and Battery" and
"Tried to register transmitter PowerConduit at (14,165)/(30,162)", at the cells of the SC_under_liquid_pit staging.

Not traced. No `ThingsOfDef(` call in GimmeSomeSlack or FlowWorks source reads MinifiedThing by name (grep 2026-11-19).
The deployed FlowWorks DLL was older than origin/main (game copy 2026-11-16 02:26, sha256 a5b9bda2…; repo 4b33b22f00,
3e32b642…); visit 2 did not deploy FlowWorks (not its mod). [guess ~60%] a FlowWorks or JawaBench call in the pit or
deck-cord staging; [guess ~25%] GSS.

## verify

Acceptance test: on tier gimmesomeslack_flowworks with FlowWorks deployed from origin/main, `proof_all.py --live --skip-offline
--only scenes` prints `Z_log_budget  PASS`. It printed FAIL at 20:08 PST 2026-11-19 (D:\ClaudeWork\scratch\gss_v2\run5_fw_scenes.json).
First step: rerun with FlowWorks deployed; if the error stays, read a Harmony stack (Prefs devMode, or a postfix on
ListerThings.ThingsOfDef that logs Environment.StackTrace for MinifiedThing).

## criteria

- The caller is named, or the error is gone on the current FlowWorks build.

## refs

file: src/RimMandrake/GimmeSomeSlack/northstar/scene_rows.py
file: src/RimMandrake/FlowWorks/Source/Thirst/RM_ThirstUtility.cs

## ticket sweep 2026-11-22: the cause, the fix, one ticket

- Merged into this item: `RIMMANDRAKE_TRACE_SLACK_MINIFIED_LOOKUP_ERROR_WITH_FLOWWORKS` (2026-11-17, the same error on 2 of 5
  scenes runs on the same tier; duplicate cause).
- The cause is named (GSS visit 3, note of 2026-11-20 08:45 PST) and still on origin/main 2026-11-22:
  `src/RimMandrake/FlowWorks/Source/Superdeep/RM_PitAccess.cs:277`, `SparePortable()`, calls
  `map.listerThings.ThingsOfDef(ThingDefOf.MinifiedThing)`, which vanilla refuses with exactly that error. It is the only such call
  in `src/RimMandrake` (grep 2026-11-22). The fix is one line: `map.listerThings.ThingsInGroup(ThingRequestGroup.MinifiedThing)`.
  The grep note of 2026-11-19 above (no such call by name) was wrong: the call names `ThingDefOf.MinifiedThing`.
- This is a FlowWorks defect (ordinary play reaches it: pit rescue looking for a spare ladder logs an error). GSS only reads it, in
  `Z_log_budget` on the FlowWorks tier. Not fixed by the sweep: FlowWorks is being rebuilt by live fixer runs today (its second
  walk sent it back), and a FlowWorks DLL edit belongs in that lane. Ready for the FlowWorks lane as it stands.

Acceptance test (red today, watched 2026-11-22: prints `1`):

    grep -c "ThingsOfDef(ThingDefOf.MinifiedThing)" src/RimMandrake/FlowWorks/Source/Superdeep/RM_PitAccess.cs

passes at `0` with the FlowWorks C# selftest green; live, `Z_log_budget` PASS on tier gimmesomeslack_flowworks (UNRUN until then).
