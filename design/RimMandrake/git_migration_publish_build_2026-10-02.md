# Git migration — publish wrapper, build route, mirror, codex staging (2026-10-02)

Implements `design/RimMandrake/git_workflow_plan_2026-10-01.md` §2.6, §2.3 (build route + mirror
tooling) and the codex staging of §2.3/§5. Owner authorized full implementation 2026-10-02.

## 1. `./publish` (thin wrapper) — DONE

`src/RimMandrake/Utils/publish.py` (596 → ~200 lines): `git add --all -- <paths>` + `git commit -- <paths>`
+ `git pull --rebase --autostash origin main` + push, ≤8 retries on non-ff, never forced.
- Seat clone → `HEAD:main`. Pool slot (`/home/mandrake/rm/pool/<seat>/slotN`, branch `agent/<name>`) →
  `refs/heads/submit/<seat>/<name>`; a non-ff on a submit ref refuses (the seat has not landed the prior one).
- Any failed push is first checked for ambiguity: fetch, `merge-base --is-ancestor HEAD <target>`; ancestor ⇒ landed.
- Rebase conflict → `rebase --abort`, conflicted paths named, commit left on HEAD.
- Refuses when the repo's realpath is under `/mnt/`, naming `/home/mandrake/rm/<seat>`.
- Deleted: temp-index plumbing, `--catchup`, `--sync`, `--commit`, `--worktrees`, `--no-catchup`.
  `shared_sync.py` prints its retirement and exits 1. `selftest_publish.py` rewritten: 11/11.
- CLAUDE.md Git section rewritten to match (the documented-commands selftest checks it).

## 2. Build route — `winbuild.py` — DONE, proven

`src/RimMandrake/Utils/winbuild.py <Mod | csproj> [-c Release] [--dry-run] [-- <dotnet args>]`
- dotnet: `C:\Users\Mandrake\.dotnet\dotnet.exe` (exists; `/mnt/c/Program Files/dotnet/dotnet.exe` fallback).
- Staging: the csproj's dir, every `..` Include/HintPath/ProjectReference target (recursive through
  ProjectReferences; OutputPath skipped), plus `src/Directory.Build.targets`, rsynced with `-R` into
  `D:\Luke\dev\_rmbuild\<Mod>\` **keeping repo-relative layout** — the stamp's `# project:` line is the
  csproj path relative to `src/`, so the stage must keep `src/` as its root. bin/obj stay as warm cache;
  Textures/Sounds/png/ogg are excluded.
- Passes `-p:SourceRevisionId=<clone HEAD>` (no `.git` on the stage), so InformationalVersion still
  ends `+<sha>`.
- Copy-back: every DLL/.srchash written under an `Assemblies/` dir, **always as a pair** (a no-op
  incremental build rewrites the stamp but not the DLL), after checking the stamp's `# dll:` line
  equals the staged DLL's sha256. `BUILD_SOURCE.json` in the stage records source sha + dirty flag.
- Repo on `/mnt/`: builds in place, no staging.
- **Proof (2026-10-02):** `winbuild.py NightsideIce` from `/home/mandrake/wt/impl-pub` → built in 1.2 s;
  `.srchash` `# dll:` = sha256 of the copied DLL (`4523aa2e…`); committed on a throwaway local branch,
  `dll_source_stamp.py check` → `MATCH src/RimMandrake/NightsideIce/Assemblies/RimMandrake.NightsideIce.dll`.
  Branch deleted; no DLL pushed (§2.7: FOUNDRY alone commits DLLs).

Callers routed:
- `src/RimMandrake/bridgetools/build.py` (JawaBench companion): under WSL python3 from an ext4 clone it
  now stages through `winbuild.stage_build` (copy-back of `artifacts/BridgeTools/JawaBench/`), game
  paths become `/mnt/c/...`; `ORACLE_MOD_DIR`/`INHABITED_MOD_DIR` pointing into the repo are staged too.
  Proven: full build + bundle check + GM-gate + deploy plan from the ext4 clone (plan only, nothing
  deployed); the embedded build stamp reads the clone sha. On `/mnt/d` it still wants python.exe.
- `.claude/hooks/block_dll_source_mismatch.py`: rebuild advice names `winbuild.py <csproj>` when the
  repo is not on `/mnt/`.
- `deploy_custom_mods.py` builds nothing; dry runs from the ext4 clone work (`--mod Graffiti` in sync,
  `--compose biomes` plans normally).
- The `selftest_*.py` that `dotnet run` a SelfTest project already pass from ext4 (5 checked). The one
  that failed, `selftest_sun_heat.py`, did `Assembly.LoadFrom` on a `\\wsl.localhost` DLL ("remote
  source"); now `UnsafeLoadFrom` → 46/46.
- Skills (`rimbridge-companion`, `rimworld-deploy`) still describe the python.exe/in-place route; skills
  are edited only in curation sessions — lesson filed below.

## 3. Mirror — `./mirror sync` — DONE, tested on a scratch target (NOT run against D:\…\RimMandrake)

`./mirror sync [--timer] [--target DIR] [--seed CLONE]`, `./mirror status` (`src/RimMandrake/Utils/mirror.py`).
- Bare fetch-only `/home/mandrake/rm/mirror.git` (refspec `+refs/heads/main:refs/remotes/origin/main`),
  `git --git-dir=… --work-tree=<target> checkout -f --detach origin/main`, with `core.autocrlf` read from
  the seat clone (unset there ⇒ `false`). Index lives on ext4, **one per target**
  (`mirror.git/index.<sha1(target)[:12]>`), so a test target never poisons the real one.
- `flock /home/mandrake/rm/mirror.lock`: blocking on demand, non-blocking skip with `--timer`.
- Failure ⇒ previous tree kept + `MIRROR_STALE` (timestamp + error) in the target; next good run clears it.
  `MIRROR_HEAD` records the sha the tree holds; an unchanged origin is a <1 s no-op.
- **Refuses any target containing `.git`** — so it cannot touch the live shared tree until the drain
  renames its `.git` (§5).
- **Adopting an existing tree** (the drain's first run): with no index yet and a non-empty target it
  `read-tree`s + `update-index --refresh`es first, so only differing files are rewritten.
- 🔴 **Trap found and fixed: drvfs reports every file as mode 0755.** With git's default
  `core.fileMode=true` the index never comes clean, so every `checkout -f` rewrites the whole tree.
  The bare repo is forced to `core.fileMode=false`.
- `--seed <clone>` (first run only) fetches objects from a local clone instead of 3.2 GB from GitHub.

Measured on the real repo (29,508 files, 4.26 GB) into `D:\Luke\dev\_mirrortest` (deleted after):
- **Cold checkout does not fit a 10-min foreground call**: 16,202 files landed in ~9 min (including
  the 3.2 GB local seed fetch) before `timeout 580` killed it; the resumed adopt run finished the rest
  in 4 min 55 s. ⇒ **the drain must run the first sync in the background** (`TimeoutStartSec=30min`
  in the unit), or adopt the existing D:\ tree (most files already match, so it is mostly hashing).
- Steady state: no-op sync 0.97 s; a forced full re-check (`diff-files` over all 29.5k) 6.9 s and found
  **0** differing files — the export is byte-identical to the clone's checkout.
- Lock-held ⇒ `--timer` skips; bad origin ⇒ `MIRROR_STALE` written, rc 1, `status` rc 1; next good
  run clears it; upstream delete removes the file; a locally edited tracked file is restored;
  untracked files are left alone.

systemd (written, **not enabled** — the drain enables it):
`~/.config/systemd/user/rm-mirror.service` (oneshot, `python3 /home/mandrake/rm/foundry/src/RimMandrake/Utils/mirror.py
sync --timer`, Nice 10, idle IO, `TimeoutStartSec=30min`) and `rm-mirror.timer` (`OnBootSec=2min`,
`OnUnitInactiveSec=5min`). `systemd-analyze --user verify` clean; `is-enabled` = disabled.
⚠️ The service runs the FOUNDRY clone's copy, which exists only after `/home/mandrake/rm/foundry` pulls past
this commit — the drain must pull first.

## 4. Codex staging
(in progress)

## 5. Left open
(in progress)
