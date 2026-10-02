# Windows binaries run from an ext4 (WSL) directory — probe, 2026-10-01

Question (owner: *"Be careful. I wonder about codex, python..."*): if checkouts move off
`D:\` onto WSL ext4, do the Windows-side tools still work when their cwd is
`\\wsl.localhost\Ubuntu\...`? MEASURED on Archmagi, test dir `/home/mandrake/wt/exetest`.

| binary | from ext4 cwd | evidence |
|---|---|---|
| `python.exe` (WindowsApps) | ✅ works | cwd reads `\\wsl.localhost\Ubuntu\home\mandrake\wt\exetest`; relative `open()` OK; 0.15 s vs 0.10 s from drvfs |
| `powershell.exe` | ✅ works | `Get-Location` = `FileSystem::\\wsl.localhost\...`; `Get-Content` relative OK |
| `cmd.exe` | ⚠️ falls back to `C:\Windows` | "UNC paths are not supported". Only use in tree: `cmd.exe /c start steam://…` in two `Transient/` scripts, which is cwd-independent |
| `codex.exe exec -s read-only` 0.153.4 | ❌ **fails** | sandbox helper `codex-windows-sandbox-setup.exe` → `orchestrator_helper_launch_failed … error=program not found` with the UNC cwd. **Control:** identical call from `/mnt/d/Luke/dev/_exetest` returned `hello`, exit 0 |

Side finding: `codex.exe exec` with no `-m` fails — the configured default `gpt-6.1-sol`
is "not supported when using Codex with a ChatGPT account". `-m gpt-5.5` works.

⇒ Anything that shells out to `codex.exe` (GPT consults, `skills/generating-images/scripts/codex_image.py`,
the artpipe codex worker) must run with a **Windows-drive cwd** and read inputs from a
Windows-drive path. A design that moves checkouts to ext4 must keep a `D:\` location for
those callers (a pinned read mirror, or a `D:\` scratch dir the caller copies inputs into).
Cross-read, cwd on `D:\`, prompt naming the absolute `\\wsl.localhost\...\probe.txt`:
**hung to the 240 s timeout with no answer** (exit 124; the same task from a `D:\` path
answers in seconds). Treat codex reading ext4 as NOT WORKING — inputs must be copied to `D:\`.

**Correction, 2026-10-02:** the sandbox helper is flaky from `D:\` too. A consult run from
`D:\Luke\dev\_rmscratch\codex\gitplan` with stdin `-` failed with the same
`orchestrator_helper_launch_failed … program not found` and could not read its input files.
So the earlier "works from D:\" is one success, not a guarantee. Robust pattern: **inline every
input into the prompt** (no file reads needed) — that run succeeded.
