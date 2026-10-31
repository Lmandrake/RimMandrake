# ARENA_CSHARP_CHECK_BUILD_IN_JUDGE_SANDBOX

## Question (Conductor brief 2026-10-30, owner authority CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM)
Can a C# arena task build from inside the sandbox through the existing, deliberately unhardened interop step
(ARENA_SANDBOX_HARDEN_INTEROP_STEP_LEGACY), the only requirement being that the step cannot read the answer store?

## Answer: YES (8feebe816d)
Hidden checks that build C# (selftest_coldstorage, selftest_world_args_core, *_fuzz, ...) call winbuild.stage_build.
In the judge check sandbox they failed at base AND fix for three reasons:
1. BUILD_ROOT (/mnt/d/ClaudeWork/rimmandrake/build) is read-only there (rsync "Read-only file system");
2. src/Directory.Build.props/.targets were not materialised;
3. kind=check gets `--tmpfs /proc`, so WSL interop's /init dies ("MountEnum ... No such file") and every .exe
   reports "Invalid argument".
Change (arena_judge.py): a check whose body matches BUILDS_CSHARP_RE (`winbuild` / `dotnet[.exe]`) gets a fresh
per-check WINBUILD_ROOT under `$ARENA_WIN_STAGE_ROOT` (default build/arena_check; refused with JudgeError if it overlaps
any judge mask; removed after the check), WINBUILD_LOCK_DIR in its own scratch, and the real /proc. materialise always
writes BUILD_FILES. Every other check is unchanged. Linux-side masks are unchanged.
Selftest: src/RimMandrake/Utils/arena/selftest_arena_csharp_check.py (forced control: the same cmd.exe from a check that
does not name the build fails).

## vet --task under the new judge (runner a8c4afc28b8ace7a, 2026-10-31T00:49Z), fix=pass, base=fail
- RP_CARBON_PRESS_FIX_NO_WORKGIVER_RUNS_BILLS
- RP_COLD_INSPECT_FIX_PARTIAL_SAYS_ALL_HELD
- RP_FEATURES_IMPORT_FIX_REGIONS_SEEING_DOUBLE (base genuinely fails: unit count 43, expected >= 56)
Experiment (not cached): DIVINGFUZZDOC, TETCHIK_GATE, TPSWRITERUNIT, SAVEADOPTTEST now build but pass at both sides
(non-discriminating by content, no longer infra); RP_SELFTEST_FILTER_BUILD_SERIAL_DLL exceeded 170 s.

## Owed
- vet_runner_id hashes arena_judge.py, so every other vet record is now stale: a full re-vet (Conductor to schedule)
  before census trusts the pool again.
- arena_judge.py / the selftest are DIRTY (no full-file review yet).
- RESIDUAL (accepted, owner threat model = non-adversarial): dotnet.exe runs on Windows outside bwrap and could read D:\
  (incl. the arena root) from a csproj Exec target. The arm sandbox still has no interop; the gate builds.
