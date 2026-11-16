# RIMMANDRAKE_WIDEN_GSS_NOHOSE_SCAN_LOAD_FOLDERS_SAID_PIPES

## spec

Found by the GimmeSomeSlack 0.1.0 blind cycle 5 judge (2026-11-16), Problem against T_NO_HOSE, the sole decider of the
offline bars `no_hose` and `no_hose_in_gss`. Planted faults it left green (lane2/planted_results.jsonl):
NH_VERSION_FOLDER_HOSE_DEF (a hose ThingDef under `1.6/Defs`, a folder the game loads beside the root),
NH_EXTRA_ASSEMBLY_HOSE_DLL (a leftover DLL in `Assemblies/` holding hose types), NH_JOINED_PATH_LITERAL (a hose texture path
joined from slash-free pieces), NH_HEADER_SAYS_HOSES (Mod Settings text saying the mod draws hoses). And the shipped mod's
own settings header read "Drawn flexible pipes and wires ..." (lane-1 row NH_SOURCE_NO_TEXT_SAYING_GSS_DRAWS_PIPES): the
mod told the player it draws flexible pipes, against the bar's "it draws power cords only".

Fix: T_NO_HOSE scans every content root (root, version folders, Common/, LoadFolders.xml), every Assemblies/*.dll's names
(the shared draw-order altitudes and the legacy settings-file name allowed by name), bare hose/reel literals, and
player-facing text claiming a hose or flexible pipe (port and FlowWorks text allowed); mutants M16-M20 and green G3 added.
The header drops "flexible pipes and" (his 2026-10-04 B27 line; the hoses moved to FlowWorks by his 2026-10-10 ruling).

## verify

Acceptance test: `python3 design/concepts/GimmeSomeSlack/version/blind_challenge/cycle_5/lane2/check_nohose_at.py --sha <tree> --test-from <fix sha>`
rc 1 on the parent tree (T1 red on the header), rc 0 on the fix sha; `python3 src/RimMandrake/GimmeSomeSlack/northstar/selftest_gss_no_hose.py`
25 PASS rows, rc 0. Recorded in the cycle's lane2/fixes.jsonl.
