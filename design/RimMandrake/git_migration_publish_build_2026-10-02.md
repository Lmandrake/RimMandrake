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

## 3. Mirror — `./mirror sync`
(in progress)

## 4. Codex staging
(in progress)

## 5. Left open
(in progress)
