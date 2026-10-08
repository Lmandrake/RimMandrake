# claude_bounded.sh — tool cgroup, ext4 seat temp, terminal reset (SEAT_MEMORY_CLONES_DRIVES_1)

Files: `D:\Luke\dev\RimMandrake\src\RimMandrake\Utils\claude_bounded.sh`,
`D:\Luke\dev\RimMandrake\src\RimMandrake\Utils\claude-seat-tmp.conf` (new tmpfiles rule).
`claude-seats.slice` NOT changed: it has no "8 GB swap" comment; the stale one was in
`claude_bounded.sh` (now "8 GB then, 16 GB now"). Caps unchanged (10G / 24G).

## 1. What Claude Code 2.1.286 does with CLAUDE_CODE_TOOL_MEMORY_LIMIT (read from the binary)

- Activates when the env var parses as a size (or flag `tengu_tool_memory_cgroup` is on); `none`/falsy disables.
- cgroup v2: tool cgroup = **`dirname(own cgroup)/claude-code-bash`** — a SIBLING of Claude's cgroup,
  because v2 forbids processes in a cgroup that hands memory to children. Writes `memory.max` only.
  Tools join via `sh -c 'echo 0 > "$0"/cgroup.procs; exec "$@"'`.
- Logs via debug log only: `tool cgroup: <dir> limit=<bytes>` on success, `tool cgroup: disabled (<err>)`
  on failure (then tools run uncapped). Visible with `claude --debug-file <path>`.
- **Consequence for the OLD launcher:** Claude sits directly in `claude-seat-X.scope`, so its sibling is
  `claude-seats.slice/claude-code-bash` — one cgroup shared by all seats, outside the seat's 10G,
  last writer's limit wins. MEASURED (before run with env=1G): `tool cgroup: …/claude-seats.slice/claude-code-bash limit=1073741824`.
- **Swap trap, MEASURED:** in that run the 1.5G bomb under a 1G cap still printed `BOMB SURVIVED` —
  cgroup `memory.peak 1073741824`, `memory.swap.peak 549806080`, `memory.swap.max max`. Claude never
  sets swap.max, so the cap is soft unless the launcher does.

**Fix:** scope gets `-p Delegate=yes`; an inner shell moves itself to leaf `<scope>/seat`, enables
`+memory` in the scope's subtree_control, pre-creates `<scope>/claude-code-bash` with
`memory.swap.max=0`, then execs Claude (which reuses the existing dir). Any failure prints red and sets
`CLAUDE_CODE_TOOL_MEMORY_LIMIT=none`; the seat still starts. Unbounded fallback also runs with `none`.

## 2. CLAUDE_CODE_TMPDIR on 2.1.286 (validated in a TEST seat)

TMPDIR = CLAUDE_CODE_TMPDIR = `/home/mandrake/.seat-tmp/<SEAT>` (0700). Claude appends `claude-1000/`.
- foreground Bash: `TMPDIR=/home/mandrake/.seat-tmp/TEST`, python `tempfile.gettempdir()` same ✓
- background task output: `/home/mandrake/.seat-tmp/TEST/claude-1000/-home-mandrake-rm-bench/52caf5c0-…/tasks/bfnne4uu0.output`, read back OK ✓
- subagent: `SUBAGENT_OK TMPDIR=/home/mandrake/.seat-tmp/TEST` ✓
- `claude -p` ✓; `--resume 52caf5c0-…` recalled the earlier turn ✓
- messaging socket did NOT move: stays `/run/user/1000/cc-socks/<pid>.sock` (XDG_RUNTIME_DIR), so the
  sun_path concern does not bite. Only sandboxed Bash warns above ~30 bytes; `.seat-tmp/FOUNDRY` = 30,
  `EMERGENCY` = 32 (seats run without sandbox). Kept the design's path rather than `~/.st`.
- scratchpad: `-p` sessions get none, so not directly observed; it lives under the same
  `claude-1000/<project>/<session>/` root as tasks/ (cf. this session's `/tmp/claude-1000/…/scratchpad`). UNMEASURED directly.

Aging (`claude-seat-tmp.conf`, installed to `~/.config/user-tmpfiles.d/`; launcher enables the user
`systemd-tmpfiles-clean.timer`, which was disabled): `d %h/.seat-tmp 0700 - - 3d` plus
`e %h/.seat-tmp/*/claude-%U/*/*/tasks - - - 2d`. Each launcher holds `flock -s` on its seat dir (fd 9,
closed for Claude). Proven with a mtime-only copy of the rules: unlocked old file deleted, fresh kept,
**locked dir's old file kept**, stale task .output deleted even under a locked seat (by design: outputs have no size cap).
Note: real ages use atime/mtime/ctime, so `touch -d` alone cannot fake age.

## 3. Planted-break checks (TEST seat: `AGENT_SEAT=TEST MEM_MAX=3G CLAUDE_CODE_TOOL_MEMORY_LIMIT=1G`, sibling scope)

### (a) tool memory bomb (python allocating 1.5G)
- BEFORE, old launcher, env unset: `BOMB SURVIVED rc=0` — nothing capped the tool. **FAIL**
- BEFORE, old launcher, env=1G: `BOMB SURVIVED rc=0` — slice-level shared cgroup, swapped 524 MB. **FAIL**
- AFTER: Bash printed `rc=137`; claude -p reported it and exited 0. Kernel:
  `oom-kill:constraint=CONSTRAINT_MEMCG … oom_memcg=…/claude-seat-TEST-1246678.scope/claude-code-bash … task=python3`. **PASS**

### (b) tool cgroup exists while the seat runs
- BEFORE: no `tool cgroup:` line in the debug log; no claude-code-bash under the scope. **FAIL**
- AFTER (+30 s): scope children `claude-code-bash`, `seat`; `memory.max=1073741824 swap.max=0`;
  tool procs in claude-code-bash; Claude pid 1248799 in `<scope>/seat`; `Delegate=yes`, scope `MemoryMax=3221225472`.
  Tool's `/proc/self/cgroup` = `…/claude-seat-TEST-1248788.scope/claude-code-bash`. Debug log:
  `tool cgroup: …/claude-seat-TEST-1246678.scope/claude-code-bash limit=1073741824`. **PASS**
- Scope escape (#60488) not seen: Claude still in `<scope>/seat` at +20 s and +30 s.

### (c) seat temp on ext4
- BEFORE: background Bash printed `TMPDIR=` (unset → /tmp tmpfs). **FAIL**
- AFTER: see §2 — TMPDIR, task output, subagent all under `/home/mandrake/.seat-tmp/TEST`. **PASS**

### (d) terminal reset after kill -9 (under `script`, kill -9 of the claude pid)
- BEFORE: typescript ends `…\x1b[?u\x1b[c` then `LAUNCHER_EXIT=137` — no reset sequence. **FAIL**
- AFTER: typescript ends `\x1b[?1000l\x1b[?1002l\x1b[?1003l\x1b[?1006l\x1b[?1015l\x1b[?1004l\x1b[?2004l\x1b[?1049l\x1b[?25hLAUNCHER_EXIT=137` — exit status preserved. **PASS**
- Caveat: in both runs Claude was still on its MCP-trust dialog, so mouse tracking had not been switched
  on yet; the check proves the reset is emitted after a kill -9, not a visual before/after of a mouse-stuck tab.

## 4. What landed / cleanup
TEST scopes gone (systemd removed the delegated subtree on exit); `~/.seat-tmp/TEST`, `TESTLOCK` removed.
Live seats pick this up on their next launch. Side effect kept on purpose: user `systemd-tmpfiles-clean.timer` now enabled.
