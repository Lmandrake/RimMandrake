# Where should Claude Code run on Windows?

Four candidate homes: **WSL2**, **native Windows**, **Cygwin**, and **cloud /
Cowork sessions**. Honest comparison, with the measurements that exist and
explicit marks on everything that is only reasoning or only vendor documentation.

Machine under discussion, MEASURED 2026-08-14: Windows 10.0.26200, 63.4 GB RAM,
RTX 5080 16 GB, WSL 2.7.11.0, kernel 6.18.33.2, cgroup v2, VM ceiling 31.7 GB.

---

## 1. The decision table

| | WSL2 (today) | native Windows | Cygwin | cloud / Cowork |
|---|---|---|---|---|
| **officially supported** | ✅ | ✅ Win 10 1809+, native installer + `winget` | ❌ never named in Anthropic docs | ✅ |
| **per-process-tree memory cap** | ✅ cgroup v2 — MEASURED working here | ⚠️ Job Objects exist, but **nothing shipped wires them up** (§3) | ❌ `RLIMIT_AS` does not cover a win32 binary (§5) | n/a |
| **one runaway kills…** | the VM, if unbounded — fixable in one shell script | the whole desktop: Windows fails the allocation rather than OOM-killing | same | nobody |
| **Claude Code sandboxing** | ✅ supported (WSL2 only) | ❌ **not supported** — DOCUMENTED | ❌ | n/a |
| **Windows file access** | 9P: ~55× slower writes, ~7× stat (MEASURED, §4) | ✅ native speed | ✅ native speed | ❌ **cannot see mounted project drives** |
| **can commit / delete in the repo** | ✅ | ✅ | ✅ | ❌ **write-only** (MEASURED here) |
| **bash/python toolchain** | ✅ full Linux | ⚠️ Git Bash (MSYS2) or the PowerShell tool | ⚠️ POSIX emulation; **shell builtins broken** under Claude Code (§5) | ✅ |
| **Node.js needed** | ❌ not at runtime | ❌ not at runtime — the installer ships a native binary | ⚠️ no Cygwin-native Node exists at all | ❌ |

**MEASURED on this box:** `C:\Program Files\Git\bin\bash.exe` is installed;
`git` resolves to `C:\Program Files\Git\cmd\git.exe`; **Node is not installed
natively** (`/mnt/c/Program Files/nodejs/` absent, `Get-Command node` empty).

⚠️ **The absent Node is NOT a blocker, and an earlier draft of this file said it
was.** DOCUMENTED (https://code.claude.com/docs/en/setup): since v2.1.198 the
npm package downloads a native binary that does not use your Node at runtime,
and the PowerShell / CMD / `winget` installers need no Node at all. Git for
Windows is *recommended, not required* — without it Claude Code falls back to a
**PowerShell tool** (`CLAUDE_CODE_USE_POWERSHELL_TOOL`), which documents two
limits: PowerShell profiles are not loaded, and **sandboxing is unsupported on
Windows**.

⇒ **A native-Windows migration is cheaper than it looks on the install side, and
more expensive than it looks on the containment and sandbox side.**

---

## 2. 🔴 The counter-intuitive part: the cgroup is a WSL *advantage*

The OOM story in `oom-diagnosis.md` reads like "WSL is fragile". It is the
opposite.

Linux gives you a per-process-tree memory cap you can apply in one line to a
program you did not write:

```bash
systemd-run --user --scope -p MemoryMax=6G -p MemorySwapMax=2G -- claude …
```

**And the runaway is not a WSL phenomenon.** DOCUMENTED user reports on
*native Windows* (GitHub issue #42169, Apr 2026, Win 11 Pro / 64 GB): a single
`claude.exe` at **13.3 GB growing to 14.2 GB over ~4 h**, a second instance at
6+ GB, a third at 4.2+ GB, **Non-Paged Pool 31.5 GB** against a 200–500 MB norm,
Resource-Exhaustion-Detector warnings every ~30 min, and zombie `claude.exe`
processes needing a reboot to clear. Closed as not planned.

⇒ **Migrating to native Windows does not fix the memory problem. It removes the
only cheap fix.** That is the strongest single argument for staying on WSL.

**Against WSL, and it is real and DOCUMENTED by Anthropic:** search across the
mount is degraded — *"Disk read performance penalties when working across file
systems on WSL may result in fewer-than-expected matches… Search still
functions, but returns fewer results than on a native filesystem."*
(https://code.claude.com/docs/en/troubleshooting). Anthropic's own remedy list
includes "use native Windows instead". **This bites a repo on `D:` reached as
`/mnt/d` — which is exactly this repo.** Weigh it against §4's absolute numbers.

---

## 3. Windows Job Objects — the native analogue, and its four sharp edges

DOCUMENTED, learn.microsoft.com. Job Objects **are** the right primitive:
`JOBOBJECT_EXTENDED_LIMIT_INFORMATION` carries `ProcessMemoryLimit`
(`JOB_OBJECT_LIMIT_PROCESS_MEMORY`) and `JobMemoryLimit`
(`JOB_OBJECT_LIMIT_JOB_MEMORY`). Children inherit by default; jobs nest since
Windows 8, most-restrictive limit winning.

But four things make them **not** a drop-in cgroup:

1. 🔴 **They cap COMMIT CHARGE, not working set.** MS wording: "the limit for
   the *virtual memory that can be committed*". A cgroup's `MemoryMax` caps
   resident anonymous memory. Different quantity, different failure point.
2. 🔴 **Exceeding the limit is an ALLOCATION FAILURE, not a kill.** The process
   gets a failed commit (`OutOfMemoryException` in .NET) and a
   `JOB_OBJECT_MSG_JOB_MEMORY_LIMIT` notification on an attached completion
   port. **Kill-on-limit is something you build**, with `TerminateJobObject`.
   Contrast: *time* limits do terminate. A Linux memcg kills; a Job Object
   merely refuses.
3. **`JOB_OBJECT_LIMIT_WORKINGSET` is a trimming hint, not a cap** — same
   semantics as `SetProcessWorkingSetSize`, and under no memory pressure the
   process sits above its stated max. So does `$p.MaxWorkingSet` in PowerShell:
   **useless for containment.**
4. **Breakaway holes:** `JOB_OBJECT_LIMIT_BREAKAWAY_OK` /
   `SILENT_BREAKAWAY_OK`, and — the quiet one — **children created via WMI
   `Win32_Process.Create` are not associated with the job at all.**

🔴 **There is no shipped, no-code, per-process memory cap on Windows 10/11.** No
PowerShell cmdlet; `start` sets priority only; Task Scheduler and Group Policy
have nothing; WMI's `Win32_NamedJobObjectLimitSetting` is read-only reporting;
**WSRM was deprecated in Server 2012, removed in 2012 R2, and never shipped on
client Windows**; Sysinternals has no equivalent. Windows Sandbox's
`<MemoryInMB>` and Hyper-V cap a *VM*, not a process.

**The one credible third-party route** — DOCUMENTED project, **UNVERIFIED
behaviour, not tested here**: `procgov`
(https://github.com/lowleveldesign/process-governor), MIT, single NativeAOT exe,
`--maxmem` (per-process commit), `--maxjobmem` (job-wide), and crucially
`-p|--pid` to attach to an **already-running** process — which the cgroup route
cannot do. Process Lasso is commercial and leans on trimming rules rather than a
commit cap.

---

## 4. The filesystem tax — real, modest, and NOT the crash cause

MEASURED, 400 small files, this box, reproduced twice:

| location | 400 writes | stat pass |
|---|---|---|
| ext4 `~` (inside the VM) | **0.01 s** | 0.01–0.05 s |
| 9P `/mnt/d` (repo) | **0.47–0.55 s** | 0.35–0.54 s |
| 9P `/mnt/c` | **0.78 s** | 0.42–0.78 s |

So 9P is roughly **55× slower on writes** and **7× on stat** than ext4.

**State the absolute cost, not just the ratio:** `git status --porcelain` over
this repo takes **1.50–1.53 s** (MEASURED twice). Count the tree yourself rather
than quoting a number from here:

```bash
find . -path ./.git -prune -o -type f -print | wc -l ; git ls-files | wc -l
```

That is a tax, not a crisis.

⚠️ **The 9P page cache was tested as an OOM cause and REFUTED** — three full
repo read passes moved `Cached` 1071 → 1073 MB. Flat. Do not blame 9P for
memory. **Do** weigh it against §2's documented search-recall penalty, which is
a correctness effect rather than a speed one.

**Cheap mitigations:** keep build scratch and caches on ext4 (`~`), keep the
repo where the humans and the Windows tools expect it, and batch filesystem
operations instead of looping shell calls over `/mnt`.

---

## 5. Cygwin — actively maintained, and still the wrong choice here

⚠️ **"Cygwin is dead" is folklore and it is false.** DOCUMENTED: stable DLL
**3.6.10-1 announced 13 Jul 2026**, Setup **2.939 (4 Jun 2026)**, 41 package
announcements in the first 13 days of Aug 2026. It is maintained.

It is still wrong for a Claude Code fleet, for reasons that are specific:

- **No Cygwin-native Node exists.** DOCUMENTED: no `nodejs` package in the
  release tree; upstream dropped Cygwin support in node v0.5 and npm does not
  officially support it. The practical route is aliasing the **native win32
  `node.exe`** from a Cygwin shell — which reintroduces every `/cygdrive/…`
  path-translation problem Cygwin exists to hide.
- **Its memory limit does not cover the binary you care about.** Correction to
  the folklore in *both* directions: `ulimit -v` is **no longer** a no-op —
  Cygwin 3.4.0 (Dec 2022) implemented `setrlimit(RLIMIT_AS)`. (The page
  `cygwin.com/cygwin/cygwin-api/std-notes.html` still says unsupported and is
  **stale — do not cite it**.) But it is **per-Cygwin-process, not per-tree**,
  and **a win32 `claude.exe` is not a Cygwin process, so it is not covered at
  all.** INFERRED from the mechanism, but it follows directly.
- 🔴 **Claude Code launches under Cygwin and is broken there.** DOCUMENTED:
  issue **#26482** — CC 2.1.45 on Cygwin 3.6.6, the Bash tool's `echo`,
  `printf`, `type` and `date` all exit 1 with no output while `git --version`
  works; every workaround failed; **closed as not planned / stale with no
  Anthropic response.** Also #78737 / #78738 (mintty + tmux display corruption,
  open) and #86631 (2.1.232's symlink-following security fix false-positives on
  Cygwin-style symlinks and kills auto-approval).
- **fork() is slow** — MEASURED third-party 2020: ~25–30 processes/sec,
  degrading across runs. An agent fleet forks constantly.

⇒ **Do not pick Cygwin.** If you want POSIX over native Windows, Git Bash
(MSYS2) is the maintained answer and is already installed here. ⚠️ Note Git Bash
is MSYS2-derived and therefore **does not ship `cygpath`**, which several
open Claude Code issues depend on (#9883, #22681, #24738).

---

## 6. Cloud / Cowork sessions

MEASURED constraints in this project:

- **Mounted project drives are not visible** to a cloud session's shell.
- Files there **cannot be deleted or committed** by the assistant — **only
  written**. Deletions and all `git` operations must be done locally.

⇒ Useful for **authoring and research**, not for anything that has to land in
the tree. Treat their output as a draft another seat commits.

---

## 7. `.wslconfig` — the knobs, with the defaults corrected

`C:\Users\Mandrake\.wslconfig`. **Every change needs `wsl --shutdown`** (or the
"8 second rule" — wait for the subsystem to fully stop).

```ini
[wsl2]
memory=36GB
swap=16GB

[experimental]
autoMemoryReclaim=gradual
```

DOCUMENTED — https://learn.microsoft.com/en-us/windows/wsl/wsl-config :

- ⚠️ **A malformed `.wslconfig` is silently ignored** and WSL launches
  unconfigured. There is no error. Verify the effect (`free -g`), never the file.
- `memory` — **default is 50% of host RAM.** Size unit is omissible and then
  means *bytes*; write `36GB`, never `36`.
- `swap` — **default is 25% of the VM's memory, rounded up to the nearest GB.**
  `0` disables. Backing file defaults to `%Temp%\swap.vhdx`.
- `autoMemoryReclaim` — 🔴 **the default is `dropCache`, not `disabled`**; older
  guides (and an earlier draft of this file) say otherwise. Values: `disabled`,
  `gradual` (slow automatic reclaim of cached memory), `dropCache` / any
  unrecognised value (immediate).

⚠️ **Raising `memory` is not a fix on its own.** A process that reaches 27 GB
will reach 40 GB. Raise the ceiling *and* bound the seats, or you have only
moved the same kill later.

---

## 8. 🔴 The workaround everyone recommends is probably dead

Every GitHub issue about Claude Code memory recommends
`NODE_OPTIONS="--max-old-space-size=4096"`. **It is very likely inert on a
current build**, and the fleet should stop reaching for it.

**MEASURED here**, on `~/.local/share/claude/versions/2.1.232` (323 MB):

```
file:    ELF 64-bit LSB executable, dynamically linked, not stripped
strings: 226 matches for JavaScriptCore|WebKit
         1505 matches for "bun"
           4 matches for max-old-space-size|v8_flags
```

The binary is a **Bun `--compile` single-file executable running
JavaScriptCore, not V8** — so a V8 heap flag has no engine to configure. The
four residual flag-name hits are consistent with a Node-compatibility shim.

**UNVERIFIED:** that the flag is *entirely* ignored — that would need an A/B
memory test on a current build. **What is MEASURED is that the engine is not
V8**, which is enough to stop treating the flag as the answer.

**What Anthropic actually recommends instead** — DOCUMENTED,
https://code.claude.com/docs/en/troubleshooting §"High CPU or memory usage":
`/compact` regularly · **close and restart Claude Code between major tasks** ·
keep large build directories out of the scanned tree · `claude --safe-mode` to
test whether a plugin, MCP server or hook is the source.

**And `/heapdump`** — a real command, absent from the menu, type it in full. It
writes `<session-id>.heapsnapshot` and `<session-id>-diagnostics.json` to
`~/Desktop` and prints RSS, JS heap, array buffers, unaccounted native memory
and leak indicators.

🔴 **The `.heapsnapshot` contains your full conversation and your credentials.
Attach only the `-diagnostics.json` to an issue, and never commit either.**
