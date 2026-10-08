# Web research: Claude Code memory / OOM / tmp (2026-10-08)

Tags: [OFFICIAL] = Anthropic docs/changelog. [USER] = GitHub issue/blog by a user. VERIFIED = read from the source text this session (changelog fetched raw from GitHub; docs fetched raw from code.claude.com/docs/en/*.md; issues read via `gh api`). INFERRED = my reading, not stated by the source.
Latest changelog entry at fetch time is 2.1.294; our seats run 2.1.286.

## 1 CLAUDE_CODE_TOOL_MEMORY_LIMIT / tool cgroup

It IS documented (our assumption "undocumented" is wrong).
- [OFFICIAL, VERIFIED] Added v2.1.233: "opt-in memory cgroup support for Bash tool commands on Linux (`CLAUDE_CODE_TOOL_MEMORY_LIMIT`) so a runaway build can't stall the session". https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md (2.1.233)
- [OFFICIAL, VERIFIED] Docs: Linux and WSL; value like `4G`, plain digits = bytes, or K/M/G/T suffix; `0 off false no none` disables; unparseable values (e.g. `4e9`) are ignored. All Bash, PowerShell and Monitor commands of a session count against ONE shared cap, not per command. Monitor covered only from v2.1.246. https://code.claude.com/docs/en/tools-reference (section "Memory limit on Linux and WSL"), https://code.claude.com/docs/en/env-vars
- [OFFICIAL, VERIFIED] Applied "with a memory cgroup. When it can't set the cgroup up, commands run without a cap, and the debug log from `claude --debug` says why." Result is latched at the first process start; a changed value needs a relaunch. When the cap is hit "the kernel kills a command, and nothing in its result names the cap."
- [OFFICIAL, VERIFIED] `CLAUDE_CODE_TOOL_MEMORY_CGROUP_EXCLUDE` (v2.1.246+): comma list of kinds exempt: `mcp, lsp, hooks, plugin, helper, agent`; `none` = cap every kind; `all-new` = cap only Bash/PowerShell/Monitor. If the var is unset, which other kinds are capped comes from server-delivered config "that can change over time" (so set it explicitly for a stable behaviour). Permission-gating hooks and MCP servers they call are never capped.
- DEFAULT: no default cap; opt-in. Server-side set for other kinds when EXCLUDE is unset (see above). The feature flag `tengu_tool_memory_cgroup` in the binary is presumably that server config (INFERRED).
- DELEGATION REQUIREMENTS: NOT stated anywhere in the docs. Whether it needs a systemd-delegated subtree (`Delegate=yes`) or just a writable cgroup2 mount is unknown. "host too small for the default cap" and "nested: already capped" strings are not in the docs (INFERRED: nested = Claude detects it already sits in a capped cgroup and skips). Only evidence-based check: `claude --debug` log.
- [USER] Blog confirming v2.1.233 release and bytes example (2147483648), says it constrains only the Bash child tree, not the claude process: https://claudcod.com/blog/claude-code-bash-memory-limit/ (secondary, adds nothing beyond docs).
- GitHub issue search for `TOOL_MEMORY_LIMIT` / `tool_memory_cgroup`: zero results (absence only).
- CONTRADICTS/COMPLICATES our plan: the cap does not cover the claude node process itself, nor (by default) possibly MCP/LSP/hook/agent children. Tmpfs shmem charged by tool commands: the cap is a memcg limit so shmem written by a capped tool IS charged to the tool cgroup (INFERRED from kernel behaviour, not from a source) and would then be reclaimed/uncharged only when files are deleted, not when the cgroup dies. Do not rely on the cap to solve problem (1).

## 2 CLAUDE_CODE_TMPDIR

- [OFFICIAL, VERIFIED] "Override the temp directory used for internal temp files. Claude Code appends `/claude-{uid}/` to this path on Unix." Default `os.tmpdir()` on Linux. "Claude Code's own temp files always use your override." Unsandboxed Bash commands inherit YOUR shell's `$TMPDIR` if set (so TMPDIR must be set separately for tools/tests); sandboxed commands get a short fallback if the path is long. Ignored in project/local settings `env` (since 2.1.251, "set them in your shell, user, or managed settings"). https://code.claude.com/docs/en/env-vars
- [OFFICIAL, VERIFIED] Task output files live at `<tmp>/claude-<uid>/<project>/<session>/tasks/<id>.output` (path shape confirmed by issues below), so CLAUDE_CODE_TMPDIR relocates them (INFERRED from path shape; docs say "internal temp files").
- Known problems, all [OFFICIAL changelog, VERIFIED]: deep CLAUDE_CODE_TMPDIR broke cross-session SendMessage and `EADDRINUSE` on unix sockets under $TMPDIR (fixed 2.1.161/2.1.162): keep the path SHORT; sandboxed Bash could not write $TMPDIR when set (fixed 2.1.281, and issue #92590 [open, USER] says `sandbox.enabled` leaves $TMPDIR read-only with it set, 2026-09-20); cross-session messaging falls back to a private /tmp dir if default unusable (2.1.248); sockets dir under /tmp has first-come squat issue #91223 (USER, open).
- [USER] #18115 plugin install EXDEV when ~/.claude and /tmp on different filesystems (open, 2026-06). Relevant if /tmp-on-ext4 vs ~/.claude on drvfs. https://github.com/anthropics/claude-code/issues/18115
- [USER] #63909 task runner reports ENOSPC on subprocess output despite free disk (open).
- Practical: put it on ext4 (not /mnt/d, drvfs is slow and a 'task output swap refused' class of errors, 2.1.260/2.1.2xx, appeared with linked/moved tasks dirs and shared project dirs).

## 3 Memory growth, task output in /tmp, WSL2

Task output files:
- [USER, VERIFIED] #40108 (2026-03-28, v2.1.84, closed "not planned"): one task output in tmpfs reached 31 GB, eating half of 61 GB RAM. This is exactly our failure shape. https://github.com/anthropics/claude-code/issues/40108
- [USER] Many sibling reports (278 GB, 224 GB, 405 GB, 459 GB, 1.4 TB, 537 GB, 771 GB): #41737 #33038 #42388 #35121 #26911 #34544 #46479 #41540. Most closed; #100290 (2026-10-07, v2.1.291, Windows, 17 GB) is OPEN: no size cap yet in 2.1.291 for task output files (VERIFIED from issue; changelog 2.1.294 not checked for a fix beyond grep, nothing found). https://github.com/anthropics/claude-code/issues/100290
- [OFFICIAL, VERIFIED] Mitigations that do exist: background bash killed if output exceeds 5 GB (v2.1.77); 1 GB cap on tool results saved to disk (v2.1.265); background Bash/PowerShell stop after timeout, default 30 min, max 2 h (v2.1.285); "leaving large output files in temp" fixed for full-disk case (v2.1.282); `bashOutputMaxChars`/`taskOutputMaxChars` only control the INLINE size (v2.1.261). 5 GB per file is far above a 10 GB memcg budget, so on tmpfs two files still sink a seat.
- [USER, VERIFIED] #51760 background children survive session close and keep writing (Windows). Linux analogue not verified.
- [USER] Cleanup one-liner posted for Windows only (#100290 comment); no official TTL/cleanup exists in sources found. Cleaning `/tmp/claude-<uid>/*/*/tasks/*.output` by age/size from a timer is a user-side recipe (our own idea; INFERRED).

Process memory / OOM:
- [OFFICIAL, VERIFIED] Troubleshooting: critical-memory warning when heap passes 2.5 GB; `/heapdump`; `claude --continue` in fresh process. https://code.claude.com/docs/en/troubleshooting
- [USER, VERIFIED] #83280 (2026-08-02, open): claude grows to 11-31 GB anon RSS on WSL2 (kernel 6.18.33.1, 2.1.181/215/220). KEY WSL FACT: every WSL process is under `init.scope` which has `OOMPolicy=stop`, so a global OOM SIGKILLs the whole scope = all shells and servers. Recommended workaround there: run every claude inside a memory-capped transient cgroup so OOM is cgroup-local. https://github.com/anthropics/claude-code/issues/83280
- [USER, VERIFIED] #70523 (2026-06-24, WSL2): 6 parallel subagents spawned ~70 node processes, 43.5 GB aggregate, OOM killed systemd, WSL distro collapsed; no aggregate ceiling or concurrency cap in Claude Code. Subagents share the parent's MCP set. https://github.com/anthropics/claude-code/issues/70523
- [USER] #62193 3,000 parallel bash processes in 17 s; #64832 ~115 node processes; #86643 (closed 2026-10-04) child process 6.6 to 10.4 GB in 30 s froze Ubuntu; #86238 / #54394 / #67021 bundled ugrep with no memory limit, model-generated regex 13.6 GB (closed). #30470 49 GB invisible kernel (slab/VMA) memory.
- [OFFICIAL, VERIFIED] Memory work in changelog: native builds 40-70 MB less (2.1.2xx), many leak fixes; nothing about a global cap on subagents.
- .wslconfig: no Anthropic text. [USER, generic blogs, not Claude-specific] `memory=`, `swap=`, and `[experimental] autoMemoryReclaim=gradual` (returns cache to Windows; helps idle cache, does nothing for tmpfs shmem that is still charged). Not verified against Microsoft docs this session.

## 4 Terminal left in mouse-tracking mode

- [USER, VERIFIED] #72268 (2026-06-29, WSL2 + Windows Terminal, 2.1.195, closed stale/locked): resize, suspend/resume or subprocess exit leaves `?1000/1002/1003/1006` and focus `?1004` on. Recovery: `reset` or `printf '\e[?1000l\e[?1002l\e[?1003l\e[?1006l\e[?1004l'`. WSL2-specific per reporter. https://github.com/anthropics/claude-code/issues/72268
- [USER, VERIFIED] #72648 (macOS clean exit, same printf), #77344 (iTerm2, tied to `.mcp.json` auto-discovery; claims `reset` did not clear it and `--mcp-config --strict-mcp-config` avoids it), #59720 leak on kill. A killed (SIGKILL / OOM) process can run no cleanup by definition (INFERRED), so a post-kill reset is the only fix.
- [OFFICIAL, VERIFIED] Related changelog: 2.1.248 `claude logs` no longer leaves mouse tracking on; 2.1.83 "mouse tracking escape sequences leaking to shell prompt after exit" fixed; `CLAUDE_CODE_DISABLE_MOUSE=1` disables mouse tracking in fullscreen; `CLAUDE_CODE_DISABLE_MOUSE_CLICKS` keeps wheel only (2.1.1xx). https://code.claude.com/docs/en/env-vars
- Recommended reset (user-sourced, consistent): `printf '\e[?1000l\e[?1002l\e[?1003l\e[?1006l\e[?1004l\e[?2004l\e[?1049l\e[?25h'` (the last three, bracketed paste, alt screen, cursor, are my addition, INFERRED) or `reset`/`stty sane`.

## 5 systemd-run / cgroups / containers / sandboxing

- !! [USER, VERIFIED] #60488 (2026-05-19, v2.1.144, Fedora, cgroup v2, closed as stale/inactive, never acknowledged by Anthropic in comments): `systemd-run --user --scope -p MemoryMax=...` wrapper is defeated: ~2 s after start the claude PID moved itself into the terminal's session scope, the transient scope emptied and was GC'd, so the cap was irrelevant. https://github.com/anthropics/claude-code/issues/60488
  CONTRADICTS/RISKS our plan (scope under 10G MemoryMax). Not verified on 2.1.286 or on WSL. Suggest a 10-second test on a live seat: `cat /proc/<claude pid>/cgroup` at +1 s and +30 s, and check the `.scope` still has members and `memory.max` is 10G. (Possibly related to the tool-cgroup feature moving things; INFERRED, no source says so.) The Zenn recipe below does not mention it.
- [USER, VERIFIED] Zenn (2026-02-19, pre-2.1.144): two layers, `tmux.slice` MemoryHigh=28G/MemoryMax=30G umbrella + per-invocation `systemd-run --scope` with MemoryMax=8G and MemorySwapMax=0 ("so OOM kill is immediate rather than a near-frozen swap state"). Matches your 24G slice + scope design; note their MemorySwapMax=0 vs your 2G. https://zenn.dev/tjst_t/articles/260219-claude-code-cgroup-memory-limit
- [USER, VERIFIED] oteme/codex-wsl-bootstrap #28: `agents.slice` MemoryMax=12G, MemoryHigh=10G, MemorySwapMax=4G, TasksMax=4096, `loginctl enable-linger`, wrappers using `systemd-run --user --scope --slice=agents.slice`; plus a hook denying `node -e` containing jest/runCLI/fork( (fork-bomb via inherited execArgv, 917+ processes, 22 GB). https://github.com/oteme/codex-wsl-bootstrap/issues/28
- [OFFICIAL, VERIFIED] Sandboxing docs (bubblewrap/seatbelt) are about filesystem/network isolation; text found says nothing about memory limits. Per-user temp dir is writable inside sandbox. https://code.claude.com/docs/en/sandboxing . Devcontainer doc: no resource-limit text found. https://code.claude.com/docs/en/devcontainer
- [USER, secondary] Container-per-agent isolation (swarm-mcp: own container, memory limit, CPU quota) as the alternative; no systemd needed. https://glama.ai/mcp/servers/y873tnbn4x
- Anthropic offers no setting that caps parallel subagents (feature request #15487 `maxParallelAgents` seen in search, status not checked).

## 6 Guardrail recipes

- Hook blocking dangerous `node -e` fork patterns: see oteme #28 above [USER].
- No shared recipe found for blocking `git clone` into /tmp or capping test-runner parallelism; search returned nothing specific (absence of search hits only). The PreToolUse hook mechanism is documented officially (https://code.claude.com/docs/en/hooks) but I did not fetch it.
- Suggested by #70523 reporter: concurrency cap and aggregate ceiling are NOT built in; so the only limits are external (cgroup/slice) and hook-based.

## What this changes for us

- CLAUDE_CODE_TOOL_MEMORY_LIMIT is documented and supported (v2.1.233+; we have 2.1.286). Use a size like `6G`; it is one shared cap for all tool commands in the session. Add `CLAUDE_CODE_TOOL_MEMORY_CGROUP_EXCLUDE=all-new` (or `none`) explicitly so server-side config can't change which kinds are capped. Check `claude --debug` to confirm the cgroup was actually created; failure is silent otherwise (commands run uncapped).
- It does not cap claude itself, and does not make tmpfs residue go away. Fix for problem (1) remains moving TMPDIR and CLAUDE_CODE_TMPDIR to ext4 (both: CLAUDE_CODE_TMPDIR relocates Claude's own files and task outputs; tools inherit only your shell's TMPDIR). Keep the path short, set it in shell/user settings, not project env.
- Anthropic still ships no size cap on task `.output` files (#100290 open on 2.1.291; only a 5 GB kill from 2.1.77). A timer/hook that prunes `<tmp>/claude-<uid>/*/*/tasks/*.output` by size is justified.
- VERIFY the systemd scope actually holds: #60488 reports claude migrating itself out of a `systemd-run --scope` in 2.1.144. Check `/proc/<pid>/cgroup` of a live seat now, and that `memory.max`=10G applies to the cgroup holding claude. If it escaped, the 10G cap is not protecting you and the global OOM on WSL `init.scope` (OOMPolicy=stop) kills everything.
- Consider MemorySwapMax=0 (Zenn recipe) instead of 2G to get a prompt kill rather than a thrash; and put test runs in a separate slice with TasksMax (oteme: 4096) as well as MemoryMax.
- Parallel fan-out has no built-in cap (#70523): 16 test workers inside a seat is the exact multiplier users report; keep the separate-slice plan and also hook-limit worker counts.
- Terminal reset after a kill is user-side only; use `printf '\e[?1000l\e[?1002l\e[?1003l\e[?1006l\e[?1004l'` (plus `reset`). Optionally set `CLAUDE_CODE_DISABLE_MOUSE=1` for seats to avoid the problem entirely.
- Do not trust `.wslconfig autoMemoryReclaim` for this: it returns page cache, not charged shmem; keep the memcg caps as the real control.
