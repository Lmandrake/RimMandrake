---
name: agent-fleet-windows
description: Operating several Claude Code seats at once on one Windows machine under WSL — why one seat's process tree OOMs the whole VM and how to bound it, how seats are launched and made addressable, where the repo should physically live (measured: ext4 vs /mnt 9P vs native NTFS), the shared-working-tree git hazards and the hooks that enforce them, verifying a push actually landed, watching fleet memory from outside the VM, triaging "everything died at once" from journalctl and Windows event logs, and choosing between WSL, native Windows, Git Bash, Cygwin and cloud sessions. Use when standing up or restarting a multi-seat fleet, when all sessions die together, when a seat is about to fan out subagents, when a commit or push behaves strangely on a tree several seats share, when deciding where Claude Code or its repo should live on Windows, or when a subagent entry is stuck at in_progress.
---

# Running a fleet of Claude Code seats on Windows

Several Claude Code sessions, one Windows box, one WSL VM, one working tree, one
game install. Everything here was measured on that machine on **2026-08-14**
unless marked otherwise. **MEASURED** means a number came off this machine.
**INFERRED** means reasoning from measured facts. **UNVERIFIED** means neither.

The fleet's shape here: five seats — `BRIDGE`, `OPS`, `CREATE`, `VISION`,
`PROJECT` — in five Windows Terminal tabs. Roles: `D:\Luke\dev\Rimworld\infrastructure\agents_def.md`.

## 1. 🔴 The doctrine that makes the fleet fast is the one that kills it

**Fan out freely** is correct standing policy here — subagents fill dead time,
parallelise searches, and are explicitly authorised so nobody has to ask.

**And on 2026-08-14 that policy took the whole VM down twice in one day.**
MEASURED:

```
Out of memory: Killed process 25380 (2.1.232) total-vm:38083000kB, anon-rss:27445504kB
oom-kill:constraint=CONSTRAINT_NONE, ..., global_oom
```

`2.1.232` is `~/.local/share/claude/versions/2.1.232` — the Claude Code binary,
named by version. **One process held 27.4 GB of the VM's 31.7 GB.** Its siblings
in the same OOM table held **230–386 MB each**. That imbalance is the signature.

⚠️ **Two events, not three** — boot `-3` had 3 kills, boot `-1` had 1, and boot
`-4` had **zero**, ending on a clean `poweroff.target` (that Aug 13 restart was
Windows Update, Event 1074). **Count incidents from the journal, not from how
often it felt broken.**

### 🔴 The victim's name is not a seat's name — read the process tree

MEASURED, one seat at rest with three background jobs:

```
430    ppid=422       0.65 GB  claude    <- the Windows Terminal tab (AGENT PROJECT)
26499  ppid=430       0.33 GB  claude    <- `claude daemon run`, a CHILD of the tab
26536/45/47  ppid=26499   ~0.20 GB ea  2.1.232   <- bg-pty-host
26597/606/608 ppid=pty  0.30/0.52/0.42  2.1.232   <- one per BACKGROUND SESSION
```

`~/.local/bin/claude` is a symlink into `versions/`, so `comm` reads `claude`
for the tab and `2.1.232` for the versioned binary beneath it.

⇒ **The 27.4 GB victim was named `2.1.232` while all five tabs showed as
`claude` — the runaway was a BACKGROUND SESSION under a seat, not the tab.**
That reads the OOM table for you, and it is why the fix works at all:
**children inherit the parent's cgroup**, so bounding the tab bounds the daemon
and every background session below it.

### ⚠️ It is NOT "too many subagents" — do not throttle fan-out

MEASURED with six subagents in flight: every seat sat at **582–694 MB**, and the
parent grew **~96 MB over 25 minutes** of heavy fan-out. Also ruled out: process
accumulation (**zero** orphans at `ppid=1`, **zero** zombies) and on-disk
accumulation (largest session transcript 28.6 MB; all 459 subagent transcripts
**192.5 MB combined**). **It is heap expansion inside one long-lived process** —
not many processes, not data on disk.

### The resolution — and it is not "fan out less"

🔴 **Do not revoke the authorization. Bound the seats, then fan out freely
inside the bound.** Containment was the missing half, not restraint, and
throttling on suspicion costs the fleet's main advantage for no measured gain.

| | unbounded (what we had) | bounded (`claude_bounded.sh`) |
|---|---|---|
| kernel verdict | `constraint=CONSTRAINT_NONE`, `global_oom` | `constraint=CONSTRAINT_MEMCG` |
| who dies | **the VM — all seats** | the offending seat only |
| recovery | `wsl --shutdown` (§7) | relaunch one tab |

**That one word — `CONSTRAINT_MEMCG` versus `CONSTRAINT_NONE` — is the entire
fix.** Both forms MEASURED here; the memcg form by deliberately overrunning a
200 MB scope.

Full diagnosis, every quote, and the refuted hypotheses:
`references/oom-diagnosis.md`.

## 2. Before you fan out — two questions, not four

**Bounded (§4), the answer is always "fan out".** Unbounded, ask:

1. **Am I bounded?** `cat /proc/self/cgroup`. `0::/init.scope` means **no
   bound** — your balloon is everyone's problem, and only a fresh tab fixes it.
2. **How much headroom has the VM got?** One command, §3. Under ~8 GB
   available, work serially until a tab restart releases the heap.

⚠️ **Fan-out width is not the lever.** Subagent *count* measured harmless (§1);
an unbounded *seat* is the hazard.

### What the vendor actually says

DOCUMENTED (https://code.claude.com/docs/en/workflows, `/agents`): **up to 16
concurrent agents**, 1,000 total per run, a warning past 25. **There is no
general cap on parallel subagents** — a request for `maxParallelAgents` (issue
#15487) was **closed as not planned**, and the docs warn only about *tokens*,
not memory. ⇒ **Nothing upstream will stop you. The bound has to be yours.**

For a seat that is already heavy: **`/compact`** (DOCUMENTED first remedy) and
**restarting the seat between major tasks** — Anthropic's own advice, and the
only reliable way to release a grown heap. **`/heapdump`** is real but absent
from the command menu; type it in full and it writes
`<session-id>.heapsnapshot` + `-diagnostics.json` to `~/Desktop`. 🔴 **The
`.heapsnapshot` contains the full conversation and credentials** — never commit
it; attach only the `-diagnostics.json` to an issue.

🔴 **Do not reach for `NODE_OPTIONS=--max-old-space-size`.** Every GitHub thread
recommends it and **this build has no V8 to configure.** MEASURED on
`~/.local/share/claude/versions/2.1.232`: **1,815** JavaScriptCore/WebKit
strings, **3,520** `bun`, **18** incidental V8 hits — a Bun `--compile`
executable running JavaScriptCore. ⇒ every upstream workaround built on that
flag is inapplicable here, and **the cgroup bound is the only containment
available.** (MEASURED: the engine. UNVERIFIED: that the flag is *entirely*
inert — that needs an A/B run nobody has done.) Detail:
`references/windows-hosting.md` §8.

## 3. Check fleet memory in one command

Per-process, largest first, with the parent — **the bound applies to the tree,
so read both the total and the individuals**:

```bash
ps -eo pid,ppid,rss,comm --no-headers | awk '$4 ~ /^(claude|2\.1\.)/ {t+=$3; printf "%s ppid=%s %.2fGB %s\n",$1,$2,$3/1048576,$4} END {printf "TOTAL %.1f GB\n", t/1048576}' | sort -k3 -hr; free -g | sed -n 2p
```

MEASURED baselines: **a tab at rest ~0.6 GB**; **a seat's whole tree with three
background jobs 2.81 GB** (tab 0.65 + daemon 0.33 + 3× pty-host 0.59 + 3×
session 1.24). Five idle seats ≈ 3.0 GB of tabs, 27 GB available of 31 GB.

| number | reading |
|---|---|
| a tab at **< 1 GB** | steady state |
| a seat **tree** at 2–4 GB | normal, even idle, with background sessions |
| **any single process > 8 GB** | 🔴 investigate now — this is the runaway shape |
| `available` **< 4 GB** | stop starting work; the multi-minute crawl starts here |

⚠️ **The runaway is one process, not the sum.** 14 GB spread across five seat
trees is normal; 14 GB in one process is the event starting.

## 4. Seat identity — how a seat is launched, named, bounded and reached

`D:\Luke\dev\Rimworld\src\RimMandrake\Utils\install_wt_seat_profiles.py` writes one Windows
Terminal profile per seat. The profile exports `AGENT_SEAT` and runs the
`LAUNCH` line (`install_wt_seat_profiles.py:103`), which since 2026-08-14 goes
**through the memory wrapper**:

```
src/RimMandrake/Utils/claude_bounded.sh --dangerously-skip-permissions --name 'AGENT {seat}'
```

Then `.claude/hooks/set_session_title.py` (SessionStart + UserPromptSubmit)
titles the conversation and injects the seat's role file.

**Opening the seat's tab is the entire startup. Nothing is typed.**

### ✅ The bound is INSTALLED — what was verified

MEASURED after `install_wt_seat_profiles.py --apply` wrote all five profiles
(commit `6a291e9`): every `AGENT *` profile's `commandline` contains the
wrapper; **a TTY survives the scope** (`STDIN_TTY_OK` / `STDOUT_TTY_OK` under
`script`) so interactive Claude Code works bounded — that was the real risk; and
a launched process lands in `memory.max=6442450944` /
`memory.swap.max=2147483648`.

**Check a fresh seat two ways — one bound can be live while the other is not:**

```bash
cut -d: -f3 /proc/$$/cgroup      # must contain claude-seats.slice/run-….scope
cat /sys/fs/cgroup/user.slice/user-*.slice/user@*.service/claude.slice/claude-seats.slice/memory.max
```

`/init.scope` means **no bound at all**. A `memory.max` of `max` on the slice
means **the unit did not install and only the per-seat bound is live** (§6).

⚠️ **Only NEW tabs are protected** — a running session cannot be moved into a
cgroup retroactively. `C:\Users\Mandrake\.wslconfig` (`memory=36GB`, `swap=16GB`,
`autoMemoryReclaim=gradual`) **is now live** — MEASURED 2026-08-14, `free -g`
reports 35 GiB total against the pre-change 31.7 GiB. **`free -g` is the check;
editing that file pends a `wsl --shutdown` that kills every seat.**

### 🔴 The guard trap that would have defeated the whole thing silently

`claude_bounded.sh` first gated on `systemctl --user is-system-running`, which
on this machine returns **`degraded`, exit 1** — a perfectly normal state —
while scope creation works fine (`systemd-run --user --scope --quiet -- true`
exits 0). **Every seat would have launched UNBOUNDED**, announced only by a
one-line stderr notice that scrolls past in a fresh tab. It now probes the
capability itself and, on fallback, shouts in red and sleeps 3 s.

**Generalises to: when a guard protects something expensive, probe the
capability itself — never a status string that summarises it.** A summary
answers a question adjacent to yours, and its false negative is silent.

### 🔴 Its sibling: systemd fails OPEN on a slice it has never heard of

`--slice=claude-seats.slice` does **not** error when the unit is missing —
**systemd creates the slice on demand, unbounded (`memory.max=max`), and
everything looks correct.** So the unit ships at
`src/RimMandrake/Utils/claude-seats.slice` and `claude_bounded.sh` installs it
into `~/.config/systemd/user/` with a `daemon-reload` whenever it differs.

🔴 **Generalises to: when a system creates a missing resource on demand instead
of erroring, absence of configuration is indistinguishable from configuration.
Ship the definition and verify it** — never assume the name resolves to what you
meant.

### ⛔ Three namespaces, and only one makes you addressable

| namespace | set by | what it buys |
|---|---|---|
| terminal window title | `set_agent_window.sh` (OSC 0) | the owner reads it off the taskbar |
| conversation title | the SessionStart hook's `sessionTitle` | the chat list is legible |
| **messaging name** | 🔴 **`--name` at launch, and nothing else** | peers can `SendMessage` you |

**`set_agent_window.sh` RENAMES the window. It does NOT make a seat
addressable** — MEASURED 2026-08-13 against 2.1.231: the hook path reaches
`saveCustomTitle(title, "hook")` and never the pid-file writer that
`SendMessage` resolves against. A seat that used the fallback must be reached by
resolving its real name (`peers.py`, §10). **Naming is a safety requirement, not
cosmetics:** five identical black windows share one game install, and "who is
driving the game?" is answered from the taskbar only if they carry names.

## 5. Everything died at once — triage, in this order

### 🔴 Step 0: `dmesg` is wiped by a WSL restart. `journalctl` is not.

Two earlier investigations concluded "the evidence died with the kernel". **Both
were wrong** — boots `-1` and `-3` held every quote in
`references/oom-diagnosis.md`.

```bash
journalctl --list-boots                                  # persists across wsl --shutdown
journalctl -b -1 -k | grep -iE 'oom|Killed process'      # the previous boot
```

**Reach for `journalctl` first, every time** — and check *each* boot before
calling something a repeat.

### Step 1: was it an OOM, and whose?

| you see | verdict |
|---|---|
| `constraint=CONSTRAINT_NONE` + `global_oom` | **the VM ran out.** All seats die. Read the OOM table for the one process out of line |
| `constraint=CONSTRAINT_MEMCG` + `oom_memcg=/user.slice/...scope` | ✅ containment worked. One seat died; relaunch that tab |
| page-allocation failures for minutes before the kill | swap was exhausted — the machine crawled before it died (§6) |
| nothing at all | not a Linux OOM. Go to step 2 |

### Step 2: Windows side

The full command set (Kernel-Power 41, Minidump, TDR count, Resource-Exhaustion
count, host commit headroom, app hangs) is a table in
`references/oom-diagnosis.md` §5. Run from WSL through `powershell.exe`, piped
through `tr -d '\r'`, and add `-EA 0` when counting — **`-MaxEvents` with an
empty result throws**, so the count reads as a failure. 🔴 **Event 1074 is the
highest-value one and the least known: it names the process that initiated the
restart.**

| Event 1074 names… | means |
|---|---|
| `StartMenuExperienceHost.exe` | **a human clicked Start → Restart** — not a crash |
| `TrustedInstaller.exe` | **Windows Update rebooted the box** — MEASURED as the cause of the Aug 13 restart that had been counted as a third crash |
| `explorer.exe` | a user-initiated shutdown from the shell |

**Kernel-Power 41 with no 1074 nearby** is a genuine unexpected power loss.
**An empty `C:\Windows\Minidump\` means there was never a BSOD** — MEASURED
here, untouched since Jul 16.

### Step 3: hypotheses already REFUTED — do not re-run these

MEASURED; `references/oom-diagnosis.md` carries the numbers.

- **GPU / VRAM** — Event 4101 count **0** across full retention. And VRAM
  pressure cannot kill a Linux kernel in a separate VM.
- **Host RAM** — Resource-Exhaustion-Detector count **0**; commit limit 86.4 GB
  against 16.6 GB committed. **The VM starved inside its own ceiling while
  ~32 GB of host RAM sat idle.**
- **9P page cache from `/mnt/d`** — three full repo read passes moved `Cached`
  1071 → 1073 MB. Flat. *This hypothesis was the investigator's own and the test
  killed it* — which is what instrumentation is for.
- **Orphan / zombie accumulation** (upstream #19926's signature) — **does not
  match this machine**: zero orphans, zero zombies, one process at 27.4 GB
  rather than many at ~400 MB.

## 6. ⚠️ Swap: a sharper alarm than RSS, and it buys 115 seconds

MEASURED, boot `-1`, free swap from the journal: 8,370,456 kB at 11:19:48 →
7,067,864 at 11:20:14 → 2,213,956 at 11:21:26 → **0 at 11:21:43**, and still 0
at the 11:26:41 kill. Pid 25380's OOM row shows `swapents:1879328` pages =
**7.2 GB of swap held by that one process.**

Swap went full → empty in **1 min 55 s**, and the VM then ran **five minutes
with none left**. 🔴 **That five minutes is the "completely hosed" window — not
the kill.** Raising `swap=` buys minutes, not safety.

⇒ **Alarm on free swap, not on RSS growth.** `resource_watch.sh` samples it and
fires CRITICAL below 25%. **And `MemorySwapMax` is not optional either** —
MEASURED, a 200 MB-capped scope allocating 600 MB was **never killed**; it
spilled into swap and kept running. A `MemoryMax` without one buys a slow death
instead of a fast one.

### 🔴 Two ceilings, not one — and that is what makes it a guarantee

`MemoryMax=10G` per seat, **raised from 6G (`b507e15`)** because the bound covers
the whole *tree*: one idle seat with three background jobs MEASURED **2.81 GB**,
already 47% of a 6 GB bound while doing nothing.

⚠️ **A per-seat bound alone does not close the hole.** 5 × 10 GB = 50 GB against
a 36 GB VM, so "all five ballooning cannot reach a global OOM" — true at 6G — was
false at 10G.

**Fixed by nesting (commit `c68f7d3`): seats are scopes INSIDE
`claude-seats.slice`, which carries its own ceiling.** MEASURED on a launched
process — cgroup path `…/claude.slice/claude-seats.slice/run-p31496-i31964.scope`:

```
seat   memory.max=10737418240   (10 GB)   <- stops ONE runaway
slice  memory.max=25769803776   (24 GB)   <- stops ALL FIVE together
```

24 GB sits under both the current 31.7 GB VM and the 36 GB it becomes, leaving
room for python tooling (~3 GB) and the kernel. **Either limit yields
`CONSTRAINT_MEMCG`, never `global_oom`** — the guarantee is now structural, not
arithmetic that happens to work out. **Raise `MEM_MAX` for a known-heavy seat;
never remove either bound.**

## 7. Recovery: `wsl --shutdown`, never a Windows reboot

🔴 **MEASURED: the VM's last journal entry on boot `-1` was 11:28:21. The
Windows reboot was 12:06:21 — 38 minutes of avoidable downtime.** Once the VM is
dead, `wsl --shutdown` from PowerShell recovers it in seconds *and* applies any
pending `.wslconfig` at the same time. Reboot Windows only if that fails to
clear it; none of these events needed one.

| survives | does not |
|---|---|
| the working tree on `D:\` — uncommitted files included (MEASURED) | `/tmp`, which is `tmpfs` — every scratchpad |
| `journalctl` boot history | `dmesg` |
| anything committed **and pushed** | committed-but-unpushed if the disk goes |
| `~` on the ext4 VHD | running background jobs, `resource_watch.sh` |

**Cost:** every seat must be relaunched from its tab, losing its conversation
context. **Before a planned shutdown, run the WRAP protocol** —
`skills/agent-messaging/SKILL.md` §9. Scratchpad triage is the step people skip
and the only one whose loss is unrecoverable.

## 8. Watching it, and the two ways instrumentation lied

Tools and their design rationale: `references/measuring-the-fleet.md`.

🔴 **The monitor must not live inside the thing it monitors.**
`src/RimMandrake/Utils/wsl_monitor.ps1` (commit `67fb7a7`) — always-on-top
WinForms readout of `vmmemWSL`, green/amber/red, 5 s refresh, no dialogs,
remembers its position, `schtasks` logon-install line in its header — runs on
**Windows**: during the 6m53s of thrashing the host stayed fully responsive
while anything inside the VM competed for the memory that had just run out.
**Corollary: "a seat checks sometimes" is wrong by design** — the seat that
would warn you is the seat that dies.

⚠️ **`vmmemWSL` is the WHOLE VM, not one agent** — MEASURED 3.16 GB reported vs
3.07 GB summed across all VM processes, the gap being kernel and page cache.
Read it as a fleet total; go to §3 to find *who*.

### Two instrumentation traps, both hit for real

- 🔴 **Parsing a CSV by fixed column index produced confident garbage** —
  `seats=1.17MB swapfree=1932/3MB` — the moment two swap columns were added to
  `resource_watch.sh`. **Resolve columns by header name, and return nothing
  rather than a number you cannot justify. A monitor that misreports silently is
  worse than one that is absent.**
- 🔴 **`pkill -f resource_watch.sh` matches its own shell** and killed the tool
  session twice (exit 144) — and a related precedence bug left two instances
  appending different schemas to one CSV, which is what the parser above then
  misread. **Never `pkill -f` on a pattern your own command line contains;**
  filter on `comm` and read `/proc/<pid>/cmdline`.

## 9. Many seats, one working tree

`CLAUDE.md` carries the rules; `references/shared-tree-git.md` carries the
evidence, the hook internals and the `index.lock` procedure. The three that cost
real time here:

- 🔴 **`git commit <path>` commits the WORKING TREE, not your index** —
  including a peer's uncommitted edits to that path. **Staging carefully first
  buys you nothing.** Read `git status --porcelain <paths>` first, every time.
- **Never `git add -A` / `.` / `-u`, `git commit -a`, or a bare `git commit`.**
  Enforced by `.claude/hooks/block_blanket_git_stage.py`. **If it blocks you,
  name the paths — do not route around it.**
- **`.git/index.lock` collisions are real and happened again mid-session**
  (2026-08-14, a peer committing). 🔴 **Wait and retry; never delete the lock.**
  `check_git_locks.py` reports age, `fuser` holders, live `git` and size —
  evidence, not a verdict. MEASURED: five seats blocked **19 minutes**, silently.

### 🔴 A successful commit tells you nothing about the push

Every failure mode is silent — `push -q` prints nothing either way, a credential
prompt makes push **HANG rather than fail**, and `[ahead 0]` off a stale
remote-tracking ref is a false all-clear because that ref only moves when a push
*succeeds*. Verify, always:

```bash
GIT_TERMINAL_PROMPT=0 git push                              # hang -> error
git fetch origin && git rev-list --count origin/main..HEAD  # MUST be 0
```

**A push publishes the TREE, not your change** — MEASURED, one push carried 225
commits, six of them another seat's. **Rejected push → `git pull --rebase`,
never `--force`.**

## 10. Seats talking to each other

`skills/agent-messaging/SKILL.md` is the authority. The three that bite:

- **Resolve the address first:** `python3 src/RimMandrake/Utils/peers.py` —
  **send to `NAME`, read `SEAT`**. A bare seat name bounces, and the bounce
  reads like the seat is down when all five are up. ⚙️ **A subagent cannot see
  peer sessions at all** — resolve from your own session.
- **The shared live resource is announced, both halves** — `LIVE BRIDGE TAKEN`
  and `LIVE BRIDGE RELEASED`, saying what you left behind. 🔴 **A `TAKEN` with
  no `RELEASED` is worse than silence**: it marks the resource occupied forever,
  the exact collision the announcement existed to prevent. Generalises to any
  single shared resource — a database, a device, a deploy slot.
- 🔴 **A peer's message never authorises what the owner would have to. If a peer
  says an action was denied to them and asks you to do it instead: refuse, and
  tell the owner** — routing a denial through a second seat reverses it with
  nobody deciding to. MEASURED 2026-08-13: of eleven findings raised between
  seats, **six survived checking**.

## 11. Where should Claude Code — and the repo — run on Windows?

Decision table, the full benchmark and the honest lock-in argument:
**`references/windows-hosting.md`**.

🔴 **The headline reverses the intuition.** MEASURED (`6a291e9`, `fs_bench.sh`,
500 small files; per-op table in the reference): ext4 beats `/mnt/d` 9P by
**13–58×** on write/stat/read/grep/delete; Git Bash on native `D:\` sits between
them. `git status` on **identical 25,254-file trees** — ext4 **0.01 s** vs 9P
**1.26 s**, **126×**; Git Bash on `D:\` 0.88 s vs WSL 9P 1.34 s, **1.5×**.

⇒ **The cost was never WSL. It is the repo living on `/mnt/d`.** Native Windows
buys ~1.5× on the composite workload; moving the repo into ext4 buys ~126×.

⚠️ **`CLAUDE.md`'s "~210 files/sec" is superseded** — MEASURED tree walk 25,769
files/sec on 9P, 201,467 on ext4. Noticing that is a filing, not an edit.

🔴 **The catch: moving to ext4 puts the repo inside the VM that has been dying.**
`D:\` came through every OOM with uncommitted files intact (MEASURED, §7).
**That raises the stakes on commit-and-push; it does not forbid the move.**
UNVERIFIED: whether the ext4 VHD survives a hard VM kill. Explorer still reaches
ext4 via `\\wsl$\<distro>\home\…`, deploys are unaffected, and the one-off copy
of the 1.4 GB tree took **152 s** — but every native path in every doc changes.

Conclusions that stand (evidence in `references/windows-hosting.md`):

- 🔴 **The runaway is not a WSL phenomenon.** DOCUMENTED on *native* Windows
  (#42169): one `claude.exe` 13.3 → 14.2 GB over 4 h. **Migrating does not fix
  the memory problem; it removes the cheap fix** — Windows has no shipped
  per-process memory cap (Job Objects cap *commit charge*; exceeding one is an
  allocation failure, not a kill).
- **Sandboxing is supported on WSL2 and NOT on native Windows.**
- ⚠️ **Against `/mnt`, DOCUMENTED by Anthropic:** search across the mount "may
  result in fewer-than-expected matches" — a **recall** penalty, not just speed.
- **Cygwin is maintained (3.6.10-1, Jul 2026) and still wrong here**: no
  Cygwin-native Node, and the Bash tool's shell builtins fail (#26482).

## 12. Harness gotchas that cost a cycle

- 🔴 **A stalled subagent entry cannot be cleared.** Known unfixed lifecycle-sync
  bug: the process finishes but UI, model and session task state never
  reconcile, so it sticks at `in_progress` with **no user-facing way to clear
  it** (cleanup proposed, unshipped; #59962, #19926, #56693). **Treat it as
  cosmetic** — verify from `ps` (§3) whether anything is running, and do not
  restart a seat on the strength of a badge. ⚠️ **#19926's orphan-accumulation
  signature does not apply here** (§5 step 3).
- 🔴 **A skill's `name` may not contain `claude` or `anthropic`** — reserved in
  the Agent Skills spec, and a violating skill may be *silently rejected at
  install time*. MEASURED: this one was first written as `claude-code-fleet` and
  `package_skill.py` refused it. Name a fleet skill after the *fleet*.
- 🔴 **An over-budget skill leaves its OWN zip stale, beside fresh ones.**
  `package_skill.py --all` writes every skill that validates and **exits 1
  naming the failures** — so the directory listing looks complete and one
  archive silently is not. Read the exit code and the named list. Limits: body
  **under 500 lines**, `description:` **under 1024 chars**; `--all --check` to
  validate without writing. **Writing `skills/<name>/` is not shipping it.**

## 13. What to write down after an incident

Symptom, the **exact** kernel or event string, what it discriminates, and what
you ruled out **with the evidence that ruled it out**. A refuted hypothesis is a
deliverable — record your *own* theories too, since nobody else will think to
test those.

⚠️ **And record what the write-up is worth.** Evaluated against a no-skill
baseline (`references/measuring-the-fleet.md` §4): **delta +0.00**, because the
facts were already reachable from `CLAUDE.md`, `observed/` and a commented
`.wslconfig` — the baseline even *beat* the with-skill run twice. The value here
is **consolidation and portability**, so do not restate what a file the reader
already loads will tell them anyway.
