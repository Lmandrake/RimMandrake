# progress tap cert session
- step0: reading core
## step: sigs read (sig1.txt, sig2.txt). all fixture tools wait?False except order_pawn/ordered_job (waitTicks=0). next: spawn thing tool, write C# scene_gate+harmony_unpatch, then script.
## decisions (after compaction)
- new C# file JawaBenchTapFixtureTools.cs (#if JAWA_GM_TOOLS): jawa/scene_gate (arm|release|state), jawa/tap_fixture (unpatch|quest_add_again|fire|explosion). Register FTestOnly in SafetyCore; scene_gate state in RunLockCore.ReadActions.
- message via static_call Verse.Messages.Message 3-arg, twice same tick -> hidden (same frame).
- incident fired judged from jawa/incident_journal rows (no scene trace row for incidents); held = gate row + journal workerEntered false.
- campaign refusal: companion_handshake effectiveProfile != "test" -> refuse.
- defs verified live by jawa/get_def preflight.
- C# tool file + registrations written 23:47:20
- build plan ok (RM_STEAMAPPS=/mnt/d/SteamLibrary/steamapps), hooks selftest PASS, HOOKS.md note 23:49:15
- read rec shapes; writing prove_tap_certificate.py now 23:53:27
- FINDING: is_ours misses mandrake.jawabench.* (kill=eventrecorder, incident=awareness) -> false 'our hook is not on' + own patches as foreign. Fixing test-first in selftest + OUR_OWNERS 23:58:10
- is_ours fix landed: selftest 12/12, 14 plants red; ACT_TOOLS updated 23:58:37. next: write prove script
- verified: acts {id,tool,args,at} at=relative; NOT_ONE_HOP unless waitTicks 0 (ordered_job); gate rows {gate,outcome,name}; kill culprit hediff-first; map_fire rect x,z,w,h; FindPawn any population. writing script 00:00:18
2026-11-25T00:04:58-08:00 prove_tap_certificate.py written; py_compile ok; --dry rc0 13 fixtures 26/26 routes problems 0 (plan_check plants red: dropped fixture, arm-read act); selftest --no-plants 12/12. DONE, reporting.
## LIVE TASK (coordinator, after landing 022ed2e6bc)
Run on ArchBig (Archmagi, ssh mandrake@archmagi-wsl). Own scratch clone there. ArchSmall/Steve1/Steve2 off limits. ~/rm/bench on Archmagi read-only.
Steps: lock ArchBig -> build.py --gm --apply -> ./game down|up -> run prove_tap_certificate --host ArchBig -> classify not-shown, fix, rerun -> audit exit 0 -> publish -> release lock.
Attempt log: (path TBD on Archmagi clone)
2026-11-25T00:19:32-08:00 ArchBig CLAIMED by holder sleep pid 3965938 on Archmagi (RM_DRIVER_PID); clone ~/rm/scratch/UNKNOWN/tapcert; run dir ~/rm/scratch/UNKNOWN/tapcert_run. RELEASE: game_lock release ArchBig with RM_DRIVER_PID + kill pid.
2026-11-25T00:22:56-08:00 ArchBig stopped (pid 11388), companion 85bc2c9466 deployed (sha d54656d4). launching.
00:27 run1 (Archmagi ~/rm/scratch/UNKNOWN/tapcert_run/run1.txt): 21/26. NOT SHOWN: job_start.ordered (2nd ordered_job refused), reserve.refused, letter both (act refused), incident.fired; companion None in identity. R3 PASS (blind reported, restored), R4 88.9s. Invoke: PATH+=WindowsApps; python.exe; RIMFLOW_SEAT=BENCH RM_DRIVER_PID=holder.
2026-11-25T00:29:39-08:00 run2 (companion mvid fix + send_letter): 19/26, dumps ~/rm/scratch/UNKNOWN/tapcert_run/dump2
## attempt 3 (theory, change) 2026-11-25
- job: ordered Goto to ax+5 errored pather (fixture: cell not walkable) -> targets now the gun cells. ordered judge wanted giver "player"; real giver of an ordered job is ThinkNode_QueuedJob (fixture judge). TAP DEFECT: a job that ends inside StartJob is pooled by the postfix -> recorded "?#-1" def null: C# StartPre now snaps newJob+giver.
- kill.by_hediff: TOOL DEFECT pawn_health add on a pawn that has the hediff merges; severity lost (read back {}). C# fix: set severity on merged-into hediff.
- reserve.refused: A's Equip ended InterruptForced same tick, so B was never refused (fixture) -> B first at t1, A at t2.
- letter: game capitalises label (fixture judge case-blind). incident.fired: journal booleans are strings (fixture judge).
2026-11-25T00:39:11-08:00 run3: 25/26; only reserve.refused
2026-11-25T00:41:20-08:00 attempt 4: reserve.refused theory = player-forced Reserve steals (vanilla), ordered_job always forces; added tap_fixture reserve_unforced (C#), fixture uses it
2026-11-25T00:45:49-08:00 run4: 26/26 R1 PASS R3 PASS R4 66.8s audit PASS
