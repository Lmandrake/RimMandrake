# The OOM diagnosis, in full

Measured 2026-08-14 on: Windows 10.0.26200, host 63.4 GB RAM, RTX 5080 16 GB,
WSL 2.7.11.0, kernel 6.18.33.2, VM ceiling 31.7 GB, cgroup v2.

Primary record: `D:\Luke\dev\Rimworld\observed\2026-08-14_wsl_oom.md` (commit `1378ecb`).
This file is the reusable method; that file is the incident.

---

## 1. The symptom, and what it actually was

**As experienced:** all five Claude Code seats die at once. The owner reboots
Windows to recover. It had been attributed to "WSL running out of memory" with
no measurement behind it, and separately — wrongly — to GPU pressure.

⚠️ **Two occurrences, not three, and the correction is instructive.** MEASURED
from `journalctl --list-boots`: boot `-3` logged 3 OOM kills, boot `-1` logged
1, and **boot `-4` (Aug 10 13:05 → Aug 13 02:44) logged zero and ended on a
clean `poweroff.target`** — that Aug 13 restart was Windows Update (Event 1074,
`TrustedInstaller.exe`). **Count incidents from the journal, never from how
often it felt broken.** An incident count is the first number an investigation
takes on trust and the easiest one to inflate.

**MEASURED**, boot `-1`:

```
Aug 14 11:26:41 kernel: HTTP Client invoked oom-killer: gfp_mask=0x140cca, order=0
Aug 14 11:26:41 kernel: oom-kill:constraint=CONSTRAINT_NONE, ..., global_oom, task=2.1.232, pid=25380
Aug 14 11:26:41 kernel: Out of memory: Killed process 25380 (2.1.232)
                        total-vm:38083000kB, anon-rss:27445504kB
```

The OOM table from that kill:

| pid | RSS | process |
|---|---|---|
| 25380 | **27.4 GB** | `2.1.232` ← one seat |
| 12890 | 2.5 GB | `python3` (repo tooling) |
| 4628 / 1662 / 1209 / 908 / 692 | 386 / 377 / 297 / 269 / 230 MB | `claude` |

**`2.1.232` is the Claude Code binary named by its version** —
`~/.local/share/claude/versions/2.1.232`. A process named after a version number
is not a mystery process; grep your `versions/` directory.

### 🔴 Why the victim's name differs from the seats' — the process tree

MEASURED, one seat at rest with three background jobs:

```
430    ppid=422       0.65 GB  claude    <- the Windows Terminal tab (AGENT PROJECT)
26499  ppid=430       0.33 GB  claude    <- `claude daemon run`, a CHILD of the tab
26536/45/47  ppid=26499   ~0.20 GB ea  2.1.232   <- bg-pty-host
26597/606/608 ppid=pty  0.30/0.52/0.42  2.1.232   <- one per BACKGROUND SESSION
                                        --------
                                          2.81 GB total for one IDLE seat
```

`~/.local/bin/claude` is a symlink into `versions/`, so `comm` reads `claude`
for the tab and `2.1.232` for the versioned binary underneath.

⇒ **The 27.4 GB victim was named `2.1.232` while all five tabs appeared as
`claude` in the same table — the runaway was a BACKGROUND SESSION beneath a
seat, not the tab itself.** This pays twice: it reads the OOM table for you, and
it is *why the fix works at all* — **children inherit the parent's cgroup**, so
bounding the tab bounds the daemon and every background session below it.

**Generalises to:** before concluding "process X is not one of mine", resolve
the symlink and walk the `ppid` chain. Two names for one program is the normal
case for a versioned launcher.

**Same pattern the previous night**, boot `-3` — MEASURED:

```
Aug 14 01:37:27 kernel: Out of memory: Killed process 3151 (2.1.232) anon-rss:20455936kB
Aug 14 01:38:36 kernel: Out of memory: Killed process 3151 (2.1.232) anon-rss:20455936kB
Aug 14 01:40:25 kernel: Out of memory: Killed process 3151 (2.1.232) anon-rss:20455936kB
```

### Why all five die together

`constraint=CONSTRAINT_NONE` + `global_oom` means **the VM** ran out, not a
cgroup. So init goes down and takes every seat with it. A per-cgroup OOM kill
would have taken exactly one.

**MEASURED:** all five seats shared **one unbounded cgroup** — `/init.scope`,
`memory.max=max` — because `wsl.exe -- bash -lc` never opens a per-session
scope. Check with `cat /proc/self/cgroup`.

### The trigger — and what it is NOT

Per the owner: both events had **RimWorld running, all five seats up, and seats
spawning subagents**.

🔴 **"Too many concurrent subagents" was the obvious theory and it is REFUTED.**
MEASURED with six subagents in flight: every seat sat at **582–694 MB**, and the
parent grew **~96 MB over 25 minutes** of heavy fan-out. Concurrent subagents
alone do not balloon a seat. ⇒ **Do not advise throttling fan-out** — it costs
the fleet's main advantage for no measured benefit.

**What remains, by elimination:** heap expansion inside one long-lived process.

| accumulation theory | MEASURED disproof |
|---|---|
| **process accumulation** (upstream #19926's signature: many leaked processes) | **zero** orphans at `ppid=1`, **zero** zombies. And the OOM table shows **one** process at 27.4 GB, not many at ~400 MB — the opposite shape |
| **on-disk / transcript accumulation** | largest session transcript **28.6 MB**; all **459** subagent transcripts **192.5 MB combined**. Three orders of magnitude short |

⚠️ **The upstream issue whose title matches your symptom may not match your
data.** #19926 describes real orphan accumulation; this machine has none. Check
the *signature*, not the title, before adopting an issue's diagnosis.

**INFERRED, not documented:** that a subagent's returned results are retained in
the parent session's heap and are what grows. That is consistent with one
process at 27 GB and siblings at ~300 MB, but it is **UNVERIFIED against
Anthropic documentation** and no heap profile was taken.

---

## 2. 🔴 Ruled out, with evidence — do not re-investigate

| hypothesis | disproof (all MEASURED) |
|---|---|
| **Windows crashed / BSOD** | `C:\Windows\Minidump\` empty, dir untouched since Jul 16; no `MEMORY.DMP`. Last Kernel-Power 41: **2026-06-09**. The 12:06 reboot is Event 1074 from `StartMenuExperienceHost.exe` — **the owner clicking Start → Restart** |
| **GPU / VRAM / driver** | Event 4101 (`Display`, TDR) count **0** across full retention (2025-12-29 →). Last real `nvlddmkm` TDR **2026-07-20**, 25 days prior. One isolated `NVDisplay.Container.exe` fault 2026-08-12 08:56, no repeat. Nothing on 8/13 or 8/14. And VRAM pressure cannot kill a Linux kernel in a separate VM |
| **Host RAM exhaustion** | Resource-Exhaustion-Detector count **0** in System *and* Application, confirmed three ways. Host 63.4 GB, commit limit 86.4 GB vs 16.6 GB committed. **The VM starved inside its own ceiling while ~32 GB of host RAM sat unused** |
| **Pagefile too small** | 23 GB, system-managed. Never implicated |
| **9P page cache from `/mnt/d`** | Three full read passes over the repo moved `Cached` 1071 → 1073 MB and `MemAvailable` 28169 → 28182 MB. **Flat.** This hypothesis was the investigator's own and the test killed it |
| **RimWorld itself** | WER hang history shows `AppHangB1` on 8/9, 8/10, 8/12 — **none on 8/13 or 8/14**. RimWorld runs on the Windows host and cannot consume the VM's 31.7 GB. Its presence in all three events is correlation: it is when the owner is working |

**The host-RAM row is the one worth internalising.** A VM starves inside its own
ceiling. Task Manager showing plenty of free RAM is not evidence of anything
about the guest.

---

## 3. The fix, and the experiment that verified it

The ceiling was never the problem — **a process that reaches 27 GB will reach
40 GB.** What was missing was *isolation*.

`D:\Luke\dev\Rimworld\src\RimMandrake\Utils\claude_bounded.sh` launches each seat in its
own scope:

```bash
exec systemd-run --user --scope --quiet \
  --unit="claude-seat-${AGENT_SEAT:-unknown}-$$" \
  -p MemoryMax="$MEM_MAX" -p MemorySwapMax="$SWAP_MAX" -p MemoryAccounting=yes \
  -- "$CLAUDE_BIN" "$@"
```

**MEASURED**, deliberately overrunning a 200 MB scope on this machine:

```
oom-kill:constraint=CONSTRAINT_MEMCG, oom_memcg=/user.slice/.../run-p10162.scope
Memory cgroup out of memory: Killed process 10482 (python3)
```

`CONSTRAINT_MEMCG` instead of `CONSTRAINT_NONE` **is the entire fix**: the
offending seat dies, the VM and the other four survive.

### 3a. 🔴 Swap is the sharper alarm, and it buys 115 seconds

MEASURED, boot `-1`, free swap straight from the journal:

| time | free swap |
|---|---|
| 11:19:48 | 8,370,456 kB (untouched) |
| 11:20:14 | 7,067,864 kB |
| 11:21:26 | 2,213,956 kB |
| **11:21:43** | **0 kB** |
| 11:26:41 | 0 kB — the kill |

Pid 25380's own OOM-table row carries `swapents:1879328` pages = **7.2 GB of
swap held by that one process.**

Two conclusions, and the second is the one people get wrong:

1. **Swap went full → empty in 1 min 55 s.** Raising `swap=` buys minutes, not
   safety. A bigger swap file makes the crawl longer, not the kill less likely.
2. 🔴 **The VM then ran FIVE MINUTES with zero swap before dying.** That window
   — not the kill — is what the owner experiences as "completely hosed". By the
   time the OOM killer fires, the outage is already five minutes old.

⇒ **Alarm on free swap, not on RSS growth.** RSS climbs slowly and ambiguously;
swap hitting zero is unambiguous and earlier. `resource_watch.sh` samples it and
fires CRITICAL below 25%.

### ⚠️ `MemorySwapMax` is not optional either

**MEASURED:** with swap unbounded, the same 200 MB-capped scope allocating
600 MB was **not killed at all** — it spilled into the 8 GB swap and kept
running. That is exactly the page-allocation-failure window above.

**Generalises to:** any `MemoryMax` without a matching `MemorySwapMax` buys you
a slow death instead of a fast one.

### 3b. 🔴 Recovery is `wsl --shutdown`, not a Windows reboot

MEASURED: the VM's last journal entry on boot `-1` is **11:28:21**; the Windows
reboot was **12:06:21** — **38 minutes of avoidable downtime.** Once the VM is
dead, `wsl --shutdown` from PowerShell recovers it in seconds *and* applies a
pending `.wslconfig` in the same step. Reboot Windows only if that fails; none
of these events needed one.

⚠️ It is also the reboot that wipes `dmesg` (§4) — so the unnecessary recovery
destroyed evidence as well as time.

### Preconditions, MEASURED present here

- cgroup v2, controllers `cpuset cpu io memory hugetlb pids rdma`
- `memory` delegated to `user.slice`
- systemd `--user` session reachable (WSL with systemd enabled)

### 3c. 🔴 The guard that would have defeated the whole fix, silently

`claude_bounded.sh`'s **first** version gated on
`systemctl --user is-system-running`. On this machine that returns **`degraded`
and exits 1** — a perfectly ordinary state on a WSL distro — while scope
creation works fine: `systemd-run --user --scope --quiet -- true` exits **0**.

**Every seat would have launched UNBOUNDED**, announced by a one-line stderr
notice that scrolls past in a fresh tab before anyone reads it. The script would
have been installed, believed, and inert.

The shipped guard probes the capability directly, and on fallback prints in bold
red and `sleep 3` so the message cannot be missed:

```bash
if ! systemd-run --user --scope --quiet -- true >/dev/null 2>&1; then
  printf '\033[1;31m%s\033[0m\n' "!!! claude_bounded: cannot create a scope — starting UNBOUNDED." >&2
  sleep 3
  exec "$CLAUDE_BIN" "$@"
fi
```

🔴 **Generalises to: when a guard protects something expensive, probe the
capability itself — never a status string that summarises it.** A summary
answers a question adjacent to yours, its false negative is silent, and a
fallback nobody sees is the same as no protection at all.

(Also a candidate for `skills/rimworld-modding/references/traps-tooling.md`,
where it is filed as *"A guard that tests a status string instead of the
capability fails safe-looking and silent"*.)

### Fallback policy

`claude_bounded.sh` falls back to launching **unbounded with a loud warning**
if a scope cannot be created — a seat that will not start is a worse failure
than one that is merely unprotected, provided the warning is impossible to miss.

### 3d. Budget — raised to 10G, and the arithmetic that no longer closes

`MemoryMax=10G`, `MemorySwapMax=2G`, **raised from 6G on 2026-08-14 (commit
`b507e15`)**, because the bound covers the whole *tree*, not the tab: one idle
seat with three background jobs MEASURED **2.81 GB** — already **47% of a 6 GB
bound while doing nothing**, which would have made spurious kills likely. 10G is
~3.5× the idle tree and far below the ~27 GB a real runaway reached.

⚠️ **State the cost of the raise.** At 6G the claim "even all five ballooning at
once cannot reach a global OOM" was arithmetically true (5 × 6 + 3 < 36). At 10G
it is not: 5 × 10 = 50 GB against a 36 GB VM.

INFERRED from the measured baseline (~14 GB of idle trees): **two** concurrent
runaways still fit under 36 GB; **three do not**. The bound reliably contains
the failure that actually happened — one process running away — and is not a
proof against every shape. **Raise `MEM_MAX` for a known-heavy seat; never
remove it.**

### 3e. Installed — and what was verified

MEASURED after `install_wt_seat_profiles.py --apply` wrote all five profiles
(commit `6a291e9`; backup left beside `settings.json`). Supersedes any text
saying the wrapper is written but not wired in:

- `LAUNCH` at `install_wt_seat_profiles.py:103` routes through
  `claude_bounded.sh`; every `AGENT *` profile's `commandline` contains it;
- **a TTY survives the scope** — `STDIN_TTY_OK` / `STDOUT_TTY_OK` under
  `script` — so interactive Claude Code works bounded. This was the real risk:
  a scope that broke the TTY would have been discovered by five seats at once;
- a launched process lands in a scope with `memory.max=6442450944` /
  `memory.swap.max=2147483648`.

⚠️ **Only NEW tabs are protected**; a running session cannot be moved into a
cgroup retroactively. `C:\Users\Mandrake\.wslconfig` (`memory=36GB`,
`swap=16GB`, `[experimental] autoMemoryReclaim=gradual`) still **pends
`wsl --shutdown`**.

---

## 4. 🔴 The forensics lesson that outlives this incident

**`dmesg` is wiped by a WSL restart. `journalctl --list-boots` persists across
them.**

Two earlier investigations concluded the evidence had died with the kernel.
**Both were wrong** — boots `-1` and `-3` held everything quoted above.

```bash
journalctl --list-boots
journalctl -b -1 -k | grep -iE 'oom|Killed process|page allocation'
journalctl -b -3 -k | grep -A25 'invoked oom-killer'      # the OOM table
```

The recovery reboot is what destroys `dmesg`, and the recovery reboot is
mandatory — so **any diagnostic that lives only in `dmesg` is guaranteed to be
gone by the time you look.** Design for that: reach for `journalctl` first, and
run a sampler (`resource_watch.sh`) for anything the journal will not hold.

**Generalises to:** before concluding "the evidence is lost", enumerate which
stores survive the recovery action. Usually one does.

---

## 5. Windows-side forensics — the discriminating events

Run from WSL through `powershell.exe`, piped through `tr -d '\r'`.

```bash
PS=/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe
```

| question | command | discriminates |
|---|---|---|
| unexpected shutdown? | `$PS -NoProfile -Command "Get-WinEvent -FilterHashtable @{LogName='System';Id=41} -MaxEvents 5 \| Select TimeCreated"` | Kernel-Power 41 = power loss or hard hang |
| **who restarted it?** | `$PS -NoProfile -Command "Get-WinEvent -FilterHashtable @{LogName='System';Id=1074} -MaxEvents 5 \| Select TimeCreated,Message"` | **names the initiating process** |
| BSOD ever? | `ls -la /mnt/c/Windows/Minidump/` | empty dir = never |
| GPU TDR count | `$PS -NoProfile -Command "(Get-WinEvent -FilterHashtable @{LogName='System';ProviderName='Display';Id=4101} -EA 0).Count"` | `0` clears the GPU entirely |
| host memory pressure | `$PS -NoProfile -Command "(Get-WinEvent -FilterHashtable @{LogName='System';ProviderName='Microsoft-Windows-Resource-Exhaustion-Detector'} -EA 0).Count"` | `0` clears the host |
| host commit headroom | `$PS -NoProfile -Command "Get-CimInstance Win32_OperatingSystem \| Select TotalVisibleMemorySize,FreePhysicalMemory,TotalVirtualMemorySize"` | is the *host* actually short? |
| app hangs | `$PS -NoProfile -Command "Get-WinEvent -FilterHashtable @{LogName='Application';Id=1002} -MaxEvents 10 \| Select TimeCreated,Message"` | `AppHangB1` per app |

**Event 1074 is the highest-value one and the least known.** It names the
process that initiated the restart:

| names | means |
|---|---|
| `StartMenuExperienceHost.exe` | a human clicked Start → Restart |
| `explorer.exe` | user-initiated from the shell |
| `TrustedInstaller.exe` | Windows Update |
| nothing (41 with no 1074) | genuine unexpected power loss or hard hang |

⚠️ **`-MaxEvents` with an empty result throws rather than returning nothing.**
Add `-EA 0` when you are counting, or the count reads as a failure.

⚠️ **A count of `0` is only meaningful with the retention window stated.** Here
it was full retention back to 2025-12-29 — check, do not assume.
