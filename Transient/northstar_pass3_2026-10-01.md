# Northstar pass 3 log 2026-10-01
- 22:10:15 start
- 22:10:39 fetched; shared tree HEAD b246bc4 behind origin/main f5aeeeb; syncing modcheck/bridgetools paths
- 22:12:32 step1 done: shared tree paths synced to origin/main; worktree /home/mandrake/wt_p3
- 22:12:47 step2: old RimWorld (pid 17456) killed, no old python procs, bridge taken (lock was ~10min idle)
- 22:12:56 step3: DLL built+deployed
- 22:16:36 step4 prep: FINDING prep_wsl died on Pyrelands (folded into Biomes; --mod refuses) and registry had stale Pits; fixed prep_wsl (compose biomes once, pid mandrake.rm.biomes), registry synced from origin; re-running prep --apply
- 22:17:40 prep running (slow /mnt/d deploys)
- 22:21:35 prep done (7 composed). launching via Steam. Coordinator notes received: time ledger; per-suite load, relaunch between runs, summary before verify, ticks/s per suite
- 22:22:58 game up (token present)
- 22:25:20 J6 attempt1 UNMEASURED: game at main menu (no world); added runner.ensure_playing_map to j3 body (J6 shares it); attempt2 running
- 22:5x game killed, modlist_swap --restore --apply done (612 active), bridge released.

## Final (pass 3 ended early, owner: unstable, hand off)
PROVEN: nothing live. No suite ran, no save made (J6 never got a world), world_reset() unproven, ticks/s unmeasured.
FOUND (root cause of owner's 'Error while generating map'): the SHARED TREE's src/ was ~304 commits behind origin/main, so prep deployed stale Stillsand/CreatureBehaviors/TheForge DLLs (8 KB vs 140 KB on origin) -> ~64 'Could not find type named RimMandrake.*' -> defs lose thingClass -> ReadingPolicyDatabase.GenerateStartingPolicies NRE. NOT a compose-biomes bug: Biomes.compose ships each mod's Assemblies under Biomes/<Mod>/Assemblies; they were just old. Fix applied: `git checkout origin/main -- src` in the shared tree (was still running at wrap-up; verify `ls -l src/RimMandrake/Stillsand/Assemblies` = ~140 KB and `git diff --stat origin/main -- src` empty before prep).
FIXED IN TOOLING (committed): prep_wsl composes folded mods (Pyrelands) once via `--compose biomes` (was: died on 'folded into Biomes'); J3/J6 call runner.ensure_playing_map (game launches at main menu); NEW modcheck/launch_gate.py + selftest_launch_gate.py (7/7) and ensure_playing_map REFUSES to start a map when Player.log has 'Could not find (a) type named RimMandrake|RimStarWars|RimUtinni' (selftest.py 22/22 incl. refusal case).
NOT DONE, next agent: (1) stale-source gate in prep_wsl (refuse when worktree src differs from origin/main for suite mods + compose entries); (2) after src sync: `git fetch; git checkout origin/main -- src`, rerun prep_wsl --apply (the Biomes compose redeploys current DLLs; it only KEEPS stale extra files, harmless), launch via Steam, run `launch_gate.py` after 'Bridge token:' (must be CLEAN), then J6 (python.exe, WSLENV=RIMFLOW_SEAT RIMFLOW_SEAT=FOUNDRY); (3) saved_base.save_base: ignore Autosave-*.rws in the 'existing saves changed' check and in the 1.7 GB backup (the game rotates autosaves -> false failure); (4) coordinator time-ledger items: runner.run write summary BEFORE emit_verify and make verify non-fatal, per-suite world_reset + ticks/s log in J1 (--saved-base), Antiquities/FlowWorks wait-until-done instead of fixed ticks, J0/J2-J5 caching, bigger idle chunks. Do not probe the bridge while a runner drives.
Note: the shared tree has modcheck_status.json synced from origin (local copy of the stale one is not kept in repo).
