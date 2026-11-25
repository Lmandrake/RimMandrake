# Tools with surprising side effects — RimMandrake

This file lists tools and machines that act differently from what an agent expects. Each entry names the trap, its
measurement, and the safe route.

The entries moved here from the project `CLAUDE.md` on 2026-10-11 (weekly cleaning). CLAUDE.md keeps a one-line rule
and points here. Entries state what IS: delete a line the moment it turns false, never annotate it.

## Machine and research facts

- 🔴 **RimSage answers on the Windows Desktop only. On the Mac laptop it has never connected.** The evidence was
  measured 2026-09-16: five timed-out session logs 2026-09-02→09-16. `mcp.rimsage.com` was TCP-dead while general
  egress was fine. The toolset had no `mcp__rimsage__*` tool at all, and no cached decompiled tree existed.
  - So on the laptop, an **engine-internals question is UNMEASURABLE**. Say so. Do not reason from a doc instead.
  - Never brief a subagent to "use RimSage" on the laptop. The subagent spends a whole run to find this out again.
  - Two sources still work offline on either machine: the def dump (`measure`, `refresh.py`) for DEFS, and our own
    source.
  - **Several docs assert engine facts that trace to an earlier agent's prose, not a decompiler.** Two examples:
    `About.xml`'s "vanilla ignition already works on any flammable terrain", and the claim that `Flood.noPossibleCell`
    is private with no accessor. Do not launder those claims into measurements.
- ✅ **Canon research does work from the Mac, and directly.** Wookieepedia's
  `action=parse&page=<X>&format=json&prop=wikitext` API answers over plain `curl`, unauthenticated, with **no size
  cap**. Measured 2026-09-23: 13 dianoga pages came back clean.
  - Prefer that API over Fetcher. Fetcher **silently truncates at 50,000 chars**, and it once lost the whole Biology
    section of a species.
  - Resolve titles with `action=query&list=search&srsearch=<name>`. A guessed exact page title returns MISSING for real
    subjects constantly. A MISSING result is not evidence that a subject is non-canon.
  - On macOS, `timeout` does not exist, and its failure **resets the shell's cwd**. Use `curl --max-time`.
- 🔴 **The SteveDesktop runner's Python has no third-party packages unless someone installed them.** A proof row that
  imports such a package fails there. That FAIL is a machine fact, not a mod defect. Measured in the findings fold:
  - `No module named 'PIL'` on four FlowWorks diptych rows, job J20261026T004751Z-6e5292;
  - `No module named 'lxml'` on Cuisine `rotting_bed_grows_marsh_fungus/offline_patch_shape`, 2026-11-06.

  Before you judge such a row, read the import. A `ModuleNotFoundError` row is a runner-environment finding for
  Operations. Make a validation script import an optional package inside the row. When the package is absent, the row
  reports UNMEASURED, never FAIL.
- 🔴 **If a driver reads UNMEASURED 'no result at the current mod hash' although it ran and its rows PASS, compute
  `mod_hash` twice with the same interpreter that stamped it.** On one Windows desktop, `python.exe` gave a different
  hash on every run with identical file bytes. The cause: logical CPU 18 returned wrong SIMD hash results. Pinned with
  `start /affinity`, sha256 gave 60 different digests out of 60. md5 and crc32 stay stable, so they hide the fault. To
  probe, hash the same buffer N times, pinned per core. Do not probe by rereading files.
- ⚠️ **RimSage's index predates Odyssey 1.6 reading policies.** `read_csharp_symbol RimWorld.ReadingPolicyDatabase`
  returns not-found. So RimSage cannot answer Odyssey-internals questions. Reason from a Player.log diff instead, and
  say UNMEASURED.
- **Hasleo Backup Suite Free 6.0.2 cannot do an unattended system-disk clone with bad sectors.** By hand, Hasleo does
  clone a system disk (Clone > Disk clone), despite the vendor table.
  - A Hasleo clone shrinks the big partition and gives the target new partition GUIDs. Hasleo also rewrites the
    target's BCD and offline MountedDevices (C: -> new partition).
  - Hasleo has no CLI, no backup filters and no ignore-bad-sectors option.
  - Hasleo reported 'completed successfully' while the source logged 30 bad-block events. So its success message says
    nothing about file integrity. Verify the copy file by file.
  - The UI lets you walk to the final Proceed page. So a run that reaches that page proves nothing.
  - For an unattended clone with an unreadable cluster, use wimlib VSS capture piped to apply, with exclude and restart
    on a read error. A pipable capture reads everything twice, because it hashes all data before it writes.
- **A root-disk fall is not necessarily scratch.** A root-disk fall is a drop of free space on `/` (`disk.root_free_gb`). Two falls
  (578->140 GB at ~3.3 GB/min, back in one step) left `ops_watch` `series/disk.jsonl` `pool_gb` and `scratch_total`
  flat. So no reaper could free the space, and the grower vanished unnamed.
  - Before you blame clones, read `disk.root_free_gb` against `pool_gb`/`scratch_total_gb`.
  - On a fast fall, the 10-minute pressure tick writes `~/.local/state/rm-scratch-reap/growth_capture.json`. That file
    names the top `/proc` `write_bytes` writers.
- **A remote one-time-bootsequence trial of a cloned disk is only safe if someone can reach the power button.** If the
  clone does not come back, nothing remote can recover the machine (SteveDesktop, 2026-11-01: offline 27+ min).
  Before the reboot, arrange owner hands (or a smart plug).
- **`verify_clone.py` on two NVMe drives is latency-bound, not CPU-bound.** One shard ran at ~55 MB/s per side, with
  CPU 13% and queue 0.6. 6 parallel shards by top folder reached 225 GB in ~65 min.
  - Budget hours for a whole-disk hash verify, or verify a sample.
  - Shard by size, not by folder. (Users held most of the bytes.)
- **Backblaze's local logs (`C:\ProgramData\Backblaze\bzdata\bzbackup\bzdatacenter\bz_done_*.dat`) record size,
  SHA-1, path and time for every version of a backed-up file, deleted ones included.**
  - Use these logs to date a lost file and to prove a rebuild byte-exact.
  - `robocopy /L /S /MIN /MAX` scans `D:` by exact size in about a minute. `find` over `/mnt/d` timed out at 500 s.
  - A count of a path name in those logs is not coverage. About 1M lines named `Desktop/old_computer`, but the
    folder's current path had no records. The entries were for earlier locations. Check the records of the current
    path, or restore a file.
- **Check a Windows folder's contents and size before a recursive copy off a failing drive.** `OneDrive\Desktop` held
  the 168k-file `old_computer`. A '19 own files' count had excluded that folder, and `robocopy` took all of it.
- **Do not hunt the ~46,000 `Harddisk1\DR1 has a bad block` events of SteveDesktop. The flood stopped on 2026-11-01.**
  - The events are Windows System log events from source `disk`, event ID 7. They are one repeated message, not
    distinct blocks. The flood ran from 2026-10-31 06:49 to 2026-11-01 17:25.
  - The Samsung 970 that the events named is not in SteveDesktop now (`Get-Disk` by serial, 2026-11-17: a Kingston
    SNV3S1000G NVMe and a WDC SATA). Verify a drive by serial before you spend a session on its symptom.
  - Also measured: the ME update's first reboot took ~19 min dark.
  - The 'Reset' text of `stage_on_steve.ps1` is stale. The text says PCI-E=Disabled, Wait F1=Enabled; the
    instructions say Enabled/Disabled.
  - One USB stick read gave an I/O device error and then 5 clean hashes.

## Tools with surprising side effects

By tool family: Git, publish and clones (3) · Ledger, rimflow, handoffs and lessons (2) · GPT, Codex and image tools (7) · Windows, WSL and paths (24) · Units, timers, hooks and processes (4) · Everything else (11).

### Git, publish and clones

- **Stale reads on the drvfs mount can mimic a revert.** `grep`, `tail` and `git status` all reported uncommitted
  edits gone. Minutes later, the same tools showed the edits intact.
  - Before you act on any "my file lost its changes" signal, wait about a minute. Then re-read from a fresh process.
  - When several stale readers agree, that is one reader, not corroboration.
  - A wrong revert diagnosis leads to destructive recovery or a double-applied wave.
  - Your ext4 clone is never stale.
- **`selftest_art_ledger_fixes.py` crashes before its verdict** (`git add
  infrastructure/state/art/events/BUILD.jsonl: pathspec did not match`). Two causes act together:
  - its `git_fixture` needs the shard to exist before `git add`;
  - `artledger.seat()` reads `RIMFLOW_SEAT` before `ART_SEAT`.

  So under `run_selftests` in a seat session, the fixture's `ART_SEAT=BUILD` loses to the inherited
  `RIMFLOW_SEAT=BENCH`. The event then lands in BENCH.jsonl. The selftest passes with `env -u RIMFLOW_SEAT`. A fixture
  that sets `ART_SEAT` must also pop `RIMFLOW_SEAT`/`AGENT_SEAT`.
- **`gpt_consult.py` and `code_review_status.py mark-clean --gpt-job` path traps.**
  - From a scratch clone (no `skills/`), gpt_consult fails with `ModuleNotFoundError codex_image`. Run the bench copy
    by absolute path, with cwd in the scratch clone and repo-relative `-f` paths. The receipt matches by repo-relative
    path, so absolute paths can never mark clean.
  - `--gpt-job` wants the bare job name from the `[consult] receipt job consult-...` line. If you give the full path
    that the first output line prints, the tool refuses it as 'no verifiable receipt'.
  - The receipt must cover the committed files themselves. A review of a diff file does not count. So after the
    commit, the last review before mark-clean must inline the files (`-f <path>`).

### Ledger, rimflow, handoffs and lessons

- **`refusal_contract.py calibrate --help` runs the calibration.** The command ignores `--help`. The command runs every row's
  free check and rewrites `infrastructure/state/judge_calibration.json` (measured 2026-11-21). Read the module's
  docstring instead.
- **`./pipe why <Mod>` and `./pipe show` cut the tick's reason line** (about 200 characters). The printed release
  command and the true cause sit past the cut. On 2026-11-20, the cut hid that FlowWorks was stuck at an offline stage,
  not waiting for a free game. Read `python3 src/RimMandrake/rimflow/maturation_dispatch.py status | grep "^<Mod>" |
  fold -w 250` or `maturation.py next <Mod>`.

### GPT, Codex and image tools

- **`codex exec --json` doubles every backslash in a command_execution's command** (`C:\\WINDOWS...`). Under disabled
  features, a refused tool appears only as an `error` item ('Code Mode is unavailable...'). The refusal also shows
  on stderr as `tools::router: error=`.
  - Never vet what shell code touched by a regex over that string.
  - When tools are meant to be off, a transcript-vetting tool must treat any command_execution as a violation.
- **GPT review misses most defects and times out often; Opus is the second reader.** Measured on 4 builder diffs with
  9 known later-found defects:
  - an Opus subagent caught 8 of 9, in 33-59 s (mean 48 s);
  - `gpt_consult` at default effort, with the diff only, caught 2 of 9, in 20-53 s;
  - 7 of 48 logged GPT calls (15%) hit the 500 s timeout with no answer, and 3 more were near-empty.

  The sample is n=4, and the ground truth came from tester and GPT rounds. So the result is indicative. Use Opus as
  the fallback when GPT times out. Also use Opus as a second reader always, not only when GPT is slow.
- **`codex.exe` with expired ChatGPT auth prints a plausible session header, then 401 refresh-token spam, and exits
  1.** Grade the answer body, not the header.
  - Re-login is the agent's act. `python3 ~/dev/Dispatch/providers/chatgpt/bin/gpt_door.py renew --side
    linux|windows` opens the device page in the owner's Windows Chrome, which is already signed into ChatGPT. Finish
    the device page, then run `status --probe`.
  - Only a password or a 2FA code is his (owner, 2026-11-22).
  - Procedure: the chatgpt-consult skill, section Sign-in.
- **`codex.exe exec` needs every input inlined into the prompt.**
  - From an ext4 (`\\wsl.localhost`) cwd, its sandbox helper fails (`orchestrator_helper_launch_failed`).
  - From a D: cwd, a read of a `\\wsl.localhost` path hangs. Even from D:, the sandbox is flaky.
  - Use `gpt_consult.py`. It inlines text files and stages the call on D:.
  - `gpt_consult.py` defaults to `gpt-6.1-sol` at high effort (owner ruling). Art (`codex_image.py`) stays on gpt-5.5.
  - To show GPT images, call `codex exec` with `-i <winpath>` per image, a `--` terminator, then `-` for a stdin
    prompt. `codex_image.py` uses that run pattern. A 3-image art review answered in 50 s.
- **A `gpt_consult` that is too big or lets codex roam returns late, empty or silently truncated.**
  - Keep a consult under ~700k chars. At that size, 5 parallel runs took 438-970 s. A 777k-char consult had its
    middle silently dropped, and still answered.
  - Ask GPT to list anything that it could not see ('Outside this slice'). Then re-run a smaller consult for what GPT
    names.
  - At high effort, a ~150 KB prompt (dossier plus four whole .cs files) ran past a 580 s `--timeout` and returned
    nothing. The answer file is written only at the end. Inside a 600 s foreground limit, trim to ~50 KB of excerpts
    and give a word budget. The consult then ran in under 10 min.
  - Full-file reviews time out because codex goes web-searching decompiled game source, or runs PowerShell/python on
    the files. A 2,000+ line file took 520 s. 7 files of ~100k chars took 500 s, twice.
  - For a full-file review, add `--lockdown` and the line 'Do NOT run any tools or commands; just read and answer'. Send
    at most 4 files. Such reviews answered in 51-150 s at medium effort (measured 2026-10-25). The effort floor is now
    high (owner by card 2026-11-25: "No medium anywhere"), which is `gpt_consult.py`'s default.
  - Verify every GPT claim against the file or vanilla Data before you accept it. GPT reported an extra closing brace
    in a file whose braces balance 27/27. GPT called MeleeDodgeChance 8 an 800% bug, but vanilla uses 15 and 8 on the
    unfinalized scale.
- **`gpt_consult` is refused under a low Codex runway unless given `--required "<rule>"`.** Low is a reading under
  `codex_conserve_runway` in `src/RimMandrake/Utils/slot_rules.json`. A code review is
  rule-required, because code is not clean until a review says so.
- **`gpt_consult --out` answer files end without a trailing newline.** So `cat a.txt b.txt` joins the last JSON line
  of one batch to the first line of the next (24 verdict lines read as 20). Join with an explicit newline
  (`for f; do cat $f; echo; done`). Count the lines against the item count before you trust a merged verdict file.

### Windows, WSL and paths

- 🔴 **What outlives a dead parent (measured 2026-11-01, real `claude_bounded` runs;
  `D:\ClaudeWork\rimmandrake\helpers_dead_parent\probe`).**
  - SIGTERM (goodbye, ticket restart, backstop): background Bash and a subagent's running Bash die with exit 137, with
    no report.
  - SIGKILL (crash, kill fallback): the LLM loops die. But both Bash commands run on as orphans and finish, and nobody
    reads them.
  - `/clear`: the only route that lost helpers in 7 days. `/clear` has no restart record.
  - Reboot or WSL restart: all of it dies, `setsid` included.
  - Only `setsid`/`systemd-run` outlives TERM and KILL.
  - A watcher in `run_in_background` dies at the next goodbye, while the remote work that it watches carries on.
  - `helper_receipts.py` reports all of these to the next window. `helper_receipts.py` does not keep them alive.
- ⚠️ **A `/proc/<pid>/environ` scan for a marker env var is never clean on this WSL box.** Same-uid systemd (user
  manager), `(sd-pam)` and `ssh-agent` are non-dumpable, so `open(environ)` raises PermissionError.
  - Rule a process out only on positive evidence: it exited, it has another uid, or it started too early.
  - "Started too early" means: the start time from `/proc/<pid>/stat` field 22 plus btime is older than the run's
    start minus 5 s. The rule works because the marker is inherited.
  - Any other unreadable process is UNMEASURED.
  - systemd 259 user scopes honour `RuntimeMaxSec`: TERM at the bound, then KILL `TimeoutStopSec` later. A
    TERM-ignoring child bounded at 5 s died at 35.4 s.
- ⚠️ **WSL drvfs (`/mnt/d`) is the wrong place for watched or hot state.**
  - TLC `-metadir` under `/mnt/d` pushed a liveness run past 480 s, against 15 s on a local tmp dir (`run_tlc.py`
    uses `tempfile.mkdtemp`).
  - Liveness checking also grows far faster than safety checking. With 2 candidates, safety took 2.5M states in ~60 s,
    and liveness took over 8 min. So check liveness at 1 candidate.
  - A systemd `.path` unit (inotify) never fires for a file written under `/mnt/d`. On ext4 (`~/rm/restart-now`) the
    unit fired 1.5 ms after the write. Watch a Linux-native dir. Probe any WSL path watcher before you trust it.
- **A systemd user unit or `systemd-run --user` one-shot starts with the manager's bare PATH.** That PATH has no
  `~/.local/bin` (34 of 39 units here set none), and on WSL it has no Windows dirs. So a bare `claude`,
  `claude-account`, `gh` or `shutil.which('curl.exe')` dies FileNotFoundError / returns None. (claude_bounded.sh exits
  127; every ops_memory generation was blind.)
  - Resolve with `shutil.which(name)` or `os.path.expanduser('~/.local/bin/'+name)`.
  - For a Windows exe, fall back to a fixed `/mnt/c/Windows/System32/...` path. `powershell.exe` is under
    `/mnt/c/Windows/System32/WindowsPowerShell/v1.0`. Without that path, `verify_from_archmagi.sh --wake` fails 'send
    failed'.
  - Pass `--setenv=PATH=...` to `systemd-run`. Test with `env -i PATH=/usr/bin:/bin <cmd>`.
  - Read the log of the first real run before you call the unit armed.
  - `selftest_systemd_path_bins.py` guards the repo's own units.
  - A child of a oneshot dies with the unit's cgroup, even under setsid. So start the child as its own transient unit
    (`systemd-run --user --collect`).
- **WSL 'page allocation failure: order:7' (vmbus_alloc_ring from hvs_probe, every new hv_sock channel: /mnt drvfs and
  interop) is watermark starvation, not fragmentation alone.** Page cache holds MemFree at the low watermark. So
  `compact_memory` finds nothing, and `drop_caches` refills in minutes.
  - Fix: `min_free_kbytes=1GiB` + `watermark_scale_factor=200` (`src/RimMandrake/Utils/systemd/90-rm-order7.conf`,
    `/etc/sysctl.d`, `rm-order7.timer`).
  - To get root without sudo, use `wsl.exe -u root`.
- **`tasklist.exe` cannot see the art daemon.** `artpiped.py` is a plain WSL Linux process. So an empty
  `tasklist.exe | grep artpip` proves nothing. Check with `systemctl --user is-active rm-artpiped.service` from WSL. Empty `pending/` and
  `active/` with a live PID means that the daemon is fed and waiting, not stopped. Feed it with `fill_queue.py`. Do not
  launch a duplicate daemon.
- **ASCII `strings` cannot see .NET string literals; they are UTF-16LE.** The `#US` heap stores literals as UTF-16LE.
  So default `strings` reads `w\0i\0l\0d\0...` and matches nothing. Three whole-tree sweeps for the literal
  `wildAnimals` across every mod DLL found zero hits. In that time, `ChooseWildAnimalSpawns.dll` was overwriting that
  field on all 81 biomes.
  - Use `strings -el` as well as the default.
  - Confirm with a real decompile: `ilspycmd.exe -t <Namespace.Type>` reads the method body.
  - A clean ASCII sweep of a managed binary is not evidence of absence. Say UNMEASURED.
  - Attribute names are the opposite case: they are UTF-8 blobs (see the rimbridge traps).
- **Windows `python.exe` misreads WSL absolute paths: `/mnt/d/Luke/...` becomes `D:\mnt\d\Luke\...` ("can't open
  file").**
  - Every script that shells to `python.exe` (the bridge client, the companion `build.py`) must `cd` to the repo and
    pass a relative path.
  - Never send a driver's client output to `/dev/null`. Capture it per cycle. If you do not, the real error hides
    behind a generic "map never became ready".
  - `bridgetools/build.py` has a "would remove tools" guard. The guard derives the tool set by a regex over DLL bytes
    (`jawa/[a-z_]{3,40}`). So the guard can refuse a deploy for a fictitious loss (`LOSES jawa/pawn_`, a fragment)
    when a description string changed.
  - The guard can name a lost tool that ends in `_` or is shorter than any declared name. Then prove the set from
    source before you override: compare the `[Tool("jawa/...")]` declarations with the live tool dump. Put the evidence
    in the commit message.
- **A process just returned by `subprocess.Popen` may not have a readable argv yet.** `/proc/<pid>/cmdline` read short on 8%
  of fresh spawns on this WSL kernel (25/300 alone, 92/1200 at 12 threads).
  - A test that judges a child by its cmdline must wait for it.
  - An unsettled read answered False. On one run of three, a selftest (`selftest_relentless_live_round`, since
    removed) went green past its own AttributeError.
- **Never create a folder whose name differs from an existing one only by case** (`src/RimMandrake/FlowWorks/tools/`
  beside `Tools/`). The Windows build stage rsyncs to case-insensitive NTFS. NTFS folds the two folders, and
  `--delete` drops files. (The selftest failed 'Could not find file ...\Tools\generate_liquid_suite.py'.) Put new
  files in the existing-cased dir.
- **`tail -F` (and a Monitor on it) on a file under `/mnt/d` never sees appends made by a Windows process.** A Monitor
  on a Windows-written serve.log sat silent 30 min while a process wrote to the file. Poll the file's size/mtime, or
  read its end, instead.
- **Env vars meant for a Windows `python.exe` launched from WSL must be named in `WSLENV`, or the child never sees
  them.** `MODCHECK_SKIP_DEPLOY=1` was silently ignored until `WSLENV=$WSLENV:MODCHECK_SKIP_DEPLOY` was set. Path vars
  need the `/p` suffix.
- **A WSL crash leaves Claude Code transcripts (`~/.claude/projects/*.jsonl`, incl. `subagents/`) ending in one
  all-NUL line with no newline.**
  - `spend_census` counts each such line as a bad line.
  - A meter that treated any bad line as blocking let 6 stale transcripts from weeks earlier void a real verdict.
  - A meter that scans a whole shared directory inherits every old corruption in it. So judge a bad line by where and
    when it is. A stale NUL tail in an old transcript is a flag, not a blocker.
- **Killing a Windows `python.exe` runner launched from WSL: kill the WSL-side `/init` proxy pid (`ps aux | grep
  <script>`), and count `Get-Process python*` after every kill.** A PowerShell `Stop-Process`/`Get-CimInstance`
  filter on `CommandLine '*run_live*'` or `Name='python.exe'` matches nothing for runs launched from a UNC path. The
  image of such a run is `python3.13.exe`. So a 'stopped' run keeps driving the same game, and several concurrent runs
  corrupt one map.
- 🔴 **A tool run from WSL with `RM_DATA_ROOT` unset, or set to a Windows-style literal (`D:\ClaudeWork\rimmandrake`),
  creates a directory named that string inside the repo root.** One such directory held player-log archives and
  launch receipts. Resolve the path through the agent-storage helper (`/mnt/d/ClaudeWork` on WSL). Move any stray
  repo-root dir out. Never commit it.
- ⚠️ **`review_map.py --save` / `--labels` under Windows `python.exe` spends minutes in `human_review`
  `derive_status` (an `os.walk` over `\\wsl` paths) before any output.** The `--save` step alone took over 280 s. WSL
  `python3` does that step in seconds, but WSL `python3` cannot reach the bridge. Give these commands a 590 s timeout
  and run them `-u`. Do not read silence as a hang until 590 s pass.
- **Playwright's bundled chromium (`chromium_headless_shell-1234`) cannot start in this WSL (`libasound.so.2` missing,
  no sudo), so headless screenshots of a page fail.** This trap bit the retired RimPulse widget. That widget was then
  proved through its daemon's `/api/now` JSON. A route that needs no root:
  - `apt-get download libasound2t64`, and `dpkg-deb -x` it;
  - copy `libasound.so.2*` into `~/.local/lib/pwlibs` (done on this box);
  - run with `LD_LIBRARY_PATH=~/.local/lib/pwlibs`.

  The shot script is `D:\ClaudeWork\rimmandrake\stream-metrics\shot.py` (url out width, full page).
- ⚠️ **`src/RimMandrake/Utils/system_screenshot.py` refuses under WSL (Windows-only, `ctypes.windll`), though
  an OS desktop capture is always allowed (`CLAUDE.md` §Tools).** From WSL, use PowerShell `CopyFromScreen` with
  `SetProcessDPIAware`, and save under `D:\ClaudeWork\scratch`.
- **A post-read 'same game?' recheck must use `live_log_check.same_game(started)`, never compare `game_started()` to
  the start time directly.** `game_started()` returns `None` for a flaky `powershell.exe` read too. So one hiccup read
  as 'the running game changed while the log was read'. `same_game` re-asks a `None`.
- **`taskkill /IM python.exe` from WSL kills every Windows python.exe** (other seats' harnesses, artpipe workers), not
  just your stuck probe. Kill by PID (`taskkill /PID <pid>`).
- **To time FlowWorks math under Mono offline:**
  - Build net472 with `C:\Users\Mandrake\.dotnet\dotnet.exe`. The Program Files dotnet.exe has no SDKs ('No .NET SDKs
    were found').
  - Then run `out/X.exe` with the scratch Mono: `source mono/env.sh`, and call `root/usr/bin/mono` by absolute path.
  - The bundled mcs cannot compile the tuple syntax in `RM_PitTrapMath`/`RM_PocketGridMath`.
  - The math files pull in `RM_RelativeRulesMath`, `RM_Volume`, `RM_StockMath`, `RM_LadderWallMath` and
    `RM_CliffMaskMath`.
  - Template: `D:\ClaudeWork\rimmandrake\excavation_slice\labelbench`.
  - Mono ran the label floods about 1.5x slower than CLR net472.
- **Pass `RM_DATA_ROOT` to `python.exe` per call, never `export` it for WSL python3.** The python.exe bridge scripts
  and preflight O13 (the `deploy_match` check of `preflight_bridge.py`) need `RM_DATA_ROOT='D:\ClaudeWork\rimmandrake' WSLENV=RM_DATA_ROOT` on that one command. If you
  export the variable shell-wide, WSL python3 tools read the backslash path as relative. They then create a literal
  `D:\ClaudeWork\rimmandrake` folder in the clone.
- **`winbuild.py` fails because the Harmony workshop folder `2009463077` has no `Current/Assemblies`.** That folder now
  holds `1.4`..`1.7`, `About` and `LoadFolders.xml`. Every csproj defaults `HarmonyDll` to the `Current` path. Until
  someone repoints the csproj defaults, pass the path explicitly after `--`:
  `python3 src/RimMandrake/Utils/winbuild.py <Mod> -- "/p:HarmonyDll=C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\2009463077\1.6\Assemblies\0Harmony.dll"`.
- **`src/RimMandrake/Utils/show.sh` opens Explorer with the file selected; it does not open the file.** When the
  owner asks to see an image or a page, open it with `powershell.exe Start-Process '<native path>'`. After `show.sh`,
  the owner saw only one of two images.

### Units, timers, hooks and processes

- **`cp -r` of a symlinked directory copies the link, not the files.**
  `~/.claude/projects/-home-mandrake-rm-bench/memory` is a symlink. So `cp -r` of it made a "backup" that changed with
  the original. Back up with `cp -rL`. Before you delete anything, check the copy with `ls -la`: the copy must show a
  directory, not `->`.
- 🔴 **`pkill -f` / `pgrep -f <pattern>` match the agent's own shell (exit 144), and a self-matching wait loop never
  ends.** The Bash tool runs each command as `<shell> -c '... eval "<my whole command>"'`. So the pattern sits in the
  agent's own argv.
  - On Linux, add `-A` (`--ignore-ancestors`): `pkill -A -f pat` / `pgrep -A -f pat`. Measured: `-f` alone matched 2
    (the wrapper plus the `$(...)` fork); `-A -f` matched 0.
  - `pgrep -f pat | grep -v $$` is not enough. A `$(...)` fork has its own PID with the same argv. Also, `grep -v $$`
    drops PIDs that contain those digits.
  - Other routes: break the literal (`"litel[l]m"`), use `ps -eo pid,args | grep '[p]attern'`, and wait on a PID.
  - On macOS, BSD pgrep excludes ancestors by default, and `-a` means include them. So BSD pgrep acts the opposite of
    Linux pgrep (UNMEASURED).
  - `setsid nohup cmd &` then `ps -p $!` shows nothing, even though the job lives. setsid forks when it leads a
    process group, so `$!` is the pid of setsid itself. Check liveness with `pgrep`, or launch with `systemd-run --user
    --slice=rm-harness.slice`. Never delete a job's clone on a `ps -p $!` miss.
  - `/tmp` is tmpfs. A full clone of the repo there fills it (8 GB).
  - The same trap holds for a `claude -p` loop. Its prompt text sits in its own command line. So a pass's `pgrep -f`
    on a command named in the prompt matches itself and waits forever. `--setting-sources project` also drops the
    global `bash_guard` that would have refused that command.
- **`safe_load` never complains about duplicate YAML keys. Hunt them with `yaml.compose` plus a duplicate-key walk.**
  An insert in `canon.yml` replaced the `cradle_memory:` header line. That left the owner's ship-memory ruling as a
  second ruled/src pair under `cathedral_voice`, and every YAML reader silently dropped one of the two.
- **A polling loop that reads a growing file with `tail -c +$((START_SIZE+1))` must update `START_SIZE` after every
  read.** If the loop does not, each poll re-reads from the original offset and re-emits the same matched lines
  forever. (Seen in a watch on Player.log for a restart to finish.)

### Everything else

- **Parsing a UTC `...Z` timestamp with `time.mktime(strptime(...)) + time.timezone` is an hour off whenever DST is
  in force.** `time.timezone` is the standard offset, and `mktime` applies DST. Use
  `calendar.timegm(time.strptime(s, fmt))`. When an age looks exactly 1 h too big, grep for `mktime` near `timezone`.
- **`canon.yml` can hold two keys of one name (it had two `start_tile`, one a struck `null`); YAML keeps the last.**
  So every parser read `start_tile=None`, while a human grep saw 17007. Read canon values with `yaml.safe_load`, never
  grep. Delete a struck value. Do not re-key it beside its successor.
- **In bash, `"$(basename $x) exit=$?"` always reads exit=0.** The command substitution runs first and resets `$?`.
  Capture `rc=$?` on the line right after the command, then echo it.
- **A nightly traceback describes the code as of its run (03:00), not HEAD.** Before you theorise, compare its line
  numbers with the file at the run's commit. A hold looked escaped for a day, but the hold was placed after the
  crashing run.
- **A deadline written as a wall-clock time can straddle DST.** '8 AM PDT Sunday Nov 1' fell after DST ended at 2 AM,
  so 15:00Z read 7:00 AM PST. State a deadline as an instant with its UTC offset, and display it that way.
- **Rerunning stored proof commands in a bash `while read i c` loop mangles them.** `read` without `-r` turns a `\n`
  in the command (e.g. `tr '\n' ' '`) into `n`. So a green proof reads red. Use `while IFS=$'\t' read -r`, or run each
  command from Python with `subprocess`.
- **zsh word-expansion traps kill a compound command.**
  - A bare all-equals token (`echo ===`) is command-path expansion, and it errors `== not found`. Quote it.
  - `L="python3 x.py add"; $L "..."` fails (`no such file or directory: python3 x.py add`), because zsh does not
    word-split variables. Use a shell function, or write the command out.
- **A Bash call with a timeout above 600 s is clamped and killed at 600 s, and a Python `finally` cleanup may not
  run.** A control run left its daemon alive and 120 job files held aside. Split long runs into separate start, poll
  and collect calls.
- **`WebFetch` can be dead for the whole model group.** Every call fails `400 Invalid model name passed in
  model=us.anthropic.claude-haiku-4-5…`, because the summarizer model is unavailable to the key. The error says
  nothing about the URL. Use `curl -sS --max-time 25 <url>` directly. Mintlify-hosted docs serve clean markdown if you
  append `.md` to the page path.
- **`broadcast.py` stores some emoji in comments as literal `\uXXXX` escape text, and the Edit tool fails to match
  those regions** in both raw and rendered form. Patch such comment blocks with a python `re.sub` instead.
- **robocopy's default `/R:1000000 /W:30` turns one unreadable file into a hang of hours.** A background robocopy of a
  USB stick held a seat past its hard restart for 3.6 h. Always pass `/R:2 /W:5`.

## NVIDIA free-tier endpoint (Nemotron workforce)

- **Nemotron is the viable free NVIDIA workforce, not Kimi.**
  - Re-run `src/RimMandrake/Utils/nemotron_probe.py` before you trust any model name. The catalog shrinks daily (102
    models, then 83 the next day). Models that answered 200 vanished. Listed names can 404 for this account
    (`kimi-k2.6`).
  - Pick `nvidia/nemotron-3-super-120b-a12b`: 20/20 tool calls, ~1.2 s, and it retrieves a needle at 616k prompt
    tokens.
  - 503 `ResourceExhausted` is shared capacity: transient and retryable. A seat degrades.
  - A 429 on `moonshotai/kimi-k3` is a per-model quota wall (15 of 20 rapid calls). Retrying makes it worse: a seat
    stalls.
  - The endpoint never errors on an over-long prompt, so acceptance proves nothing. Only a retrieval test separates
    long context from silent truncation.
- **Qualify a model for agentic work with a loop containing a deliberate bad argument, never a single tool call**
  (`src/RimMandrake/Utils/nemotron_agent_trial.py`). The discriminator is error recovery.
  - All four usable nemotrons emit valid calls. But `nemotron-3-nano-30b-a3b` dropped a path prefix and thrashed seven
    turns repeating one grep.
  - Under Claude Code, its failure mode is a polite empty answer (`is_error: false`, exit 0) after it loses the prompt.
    So grade the answer, never the exit code.
- **Gateway traps (LiteLLM in a venv, config `src/RimMandrake/Utils/litellm_nemotron.yaml`).**
  - Claude Code does not recognise the model name and silently assumes a 200k window. So pass
    `CLAUDE_CODE_MAX_CONTEXT_TOKENS`.
  - Set `ANTHROPIC_API_KEY=` empty. If you do not, the claude.ai OAuth login wins, and the window never reaches the
    gateway.
  - A Sonnet fallback is not buildable through LiteLLM here. The fallback needs an API key, and auth here is OAuth.
  - System pip refuses under PEP 668, so use a venv.

## Probing filters, sandboxes and meters

- **Test an env or path filter with the production directory layout, not a tmp dir outside the filtered root.**
  `judge_env` dropped every value that named `clones_root`, and the judge work root sat under it. So `RM_GPT_CALL_LOG`
  was dropped, and no judge GPT call was ever metered. The fix lets a caller-supplied value survive when it is inside
  the call's own workspace.
- **Probe a spend meter by injecting spend where each helper really writes.** A meter that reads only transcripts
  under one root is blind to some helpers. Testers, for example, get a fresh HOME in a tempdir and are rmtree'd. The
  verdict still DECIDEs with no blocking diagnostics.
- **`gpt_call_log` `tokens_used` is None on about half of `gpt_consult` calls** (1046 of 2167 on one day).
  `codex.log` does not always print the figure that `TOKENS_RE` expects. `gpt_consult_rounds.py report` counts these
  calls as `tok?` and never fills them from the chars/4 estimate. So the per-round token cost is a lower bound until
  `--json` events (`events_tokens`) or another real source is used.
- **A sandbox probe counts only after its mutation is shown to leak.**
  - Under `bwrap --unshare-user`, `/proc/<host pid>/root` is already EACCES. So dropping `--unshare-pid` changed
    nothing that the probe looked at. Show that the mutant leaks (e.g. `/proc/1/cmdline` is bwrap) before a clean probe
    counts.
  - Run a Windows interop probe with no args. `whoami` with args exits nonzero, and that hid live interop.
  - `bwrap --unshare-net` does not close AF_VSOCK on WSL2: the Windows host answers on CID 2, ports 50000-50005. So add
    a seccomp filter that returns EAFNOSUPPORT for `socket(AF_VSOCK)`.
  - A sandbox that hides local copies of an answer is defeated if the repo is public and the network is shared. An
    unauthenticated `git fetch https://github.com/...` fetched the fix commit. So probe the internet copy
    (`git ls-remote`) and `/var/log` (syslog/journal hold dispatch briefs and ledger events).
- **A locked-down codex is still steered by instruction files.**
  - With every tool feature off, `--ignore-rules` and `--ephemeral`, two files each changed the reply: an `AGENTS.md`
    in its cwd, and a `CODEX_HOME/skills/<x>/SKILL.md`.
  - `project_doc_max_bytes=0` and `[skills] include_instructions=false` each stopped that.
  - `models_cache.json` also carries per-model instruction templates
    (`models[].model_messages.instructions_template`).
  - An isolated judge needs those knobs, plus an allow-listed home and an instruction-free cwd chain. Filename scans
    alone cannot beat a same-user plant/read/remove race.
- **A Player.log 'no errors from mod X' check built on record grouping keeps passing broken loads.** New unindented
  continuation shapes appear every pass ([Ref], Full node:, Unity frames, Harmony wrapper frames).
  - Use a forward window: an error-worded line with the mod named on it or in the next few lines.
  - Add 'any stack frame of ours'.
  - Accept the conservative false FAIL (see graffiti_v1_live_proof.py log_verdict).

## Simulators (src/RimMandrake/Utils/sim)

- **Check a sim assumption against the ledger, and test that every event kind fires.** A fan-out
  defect-rise-per-worker (kappa) was set by assumption. It sat well below the 0.33 that the verify data shows.
  `Sim.run` silently ignores unknown event kinds. So add a test that sees each new event fire.
- **Split ensemble members by position, never by odd/even id (ids are all even), and test exemptions per arm.** An
  unattended sim with no stocked queue ranks proposers, not builders. A blanket exemption for process tickets hid
  fair-check cost from one arm class.
- **TLA+ liveness: an unfair environment loop can starve a fair obligation, and TLC then reports a spurious L1/L2
  violation.** L1 and L2 are two liveness properties of `Handoff.tla`, a model removed on 2026-11-05. L1: each candidate
  is settled in the end. L2: each owner message is handled in the end. Fix with guards, not more fairness:
  - Begin requires the old inbox empty. That stops Begin/Cancel ping-pong.
  - Reload requires no pending C# fix. That stops the StopGame/Reload loop.
  - Yield fires for any context that still holds work, not only for drivers. (After Release then Cancel, a context
    held a candidate with no driver.)

  Before you call a liveness failure real, read the lasso trace for the cause. Require a lost input in the trace of
  any mutant.

- **`detached_helper.py launch` under a wrapping `timeout`.** When the machine is loaded (load 47 to 64 on 14 cores,
  measured 2026-11-23), one launch ran past 100 s, and `timeout 100` killed it before the run started. The launch
  printed nothing, and `detached_helper.py status` showed no run. Launch with no `timeout`, as a background command,
  and read `status` to confirm that the run started.
