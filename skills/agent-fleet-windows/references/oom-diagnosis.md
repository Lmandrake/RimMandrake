# The OOM diagnosis, in full

Measured 2026-08-14 on: Windows 10.0.26200, host 63.4 GB RAM, RTX 5080 16 GB,
WSL 2.7.11.0, kernel 6.18.33.2, VM ceiling 31.7 GB, cgroup v2.

Primary record: `D:\Luke\dev\Rimworld\observed\2026-08-14_wsl_oom.md` (commit `1378ecb`).
This file is the reusable method; that file is the incident.

---

## 1. The symptom, and what it actually was

**As experienced:** all five Claude Code seats die at once. The owner reboots
Windows to recover. Three times in 48 h. It had been attributed to "WSL running
out of memory" with no measurement behind it, and separately — wrongly — to GPU
pressure.

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

### The trigger

Per the owner: all three events had **RimWorld running, all five seats up, and
seats spawning subagents**.

**INFERRED:** subagent contexts accumulate inside the *parent* seat's single
process, which is exactly the shape of the data — one process at 27 GB, siblings
at ~300 MB. The standing "fan out freely, do not ask" authorization is what
drives a seat there. **UNVERIFIED against Anthropic documentation**; the
accumulation is inferred from process RSS, not from a documented model.

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

### ⚠️ `MemorySwapMax` is not optional

**MEASURED:** with swap unbounded, the same 200 MB-capped scope allocating
600 MB was **not killed at all** — it spilled into the 8 GB swap and kept
running. That is the seven minutes of page-allocation failures (11:19:48 → the
11:26:41 kill) during which the box is unusable but not yet dead.

**Generalises to:** any `MemoryMax` without a matching `MemorySwapMax` buys you
a slow death instead of a fast one.

### Preconditions, MEASURED present here

- cgroup v2, controllers `cpuset cpu io memory hugetlb pids rdma`
- `memory` delegated to `user.slice`
- systemd `--user` session reachable (WSL with systemd enabled)

`claude_bounded.sh` falls back to launching **unbounded with a stderr warning**
if systemd `--user` is unreachable — a seat that will not start is a worse
failure than one that is merely unprotected, and the warning makes it visible
rather than silent.

### Budget

5 seats × 6 GB = 30 GB, plus ~3 GB of python tooling, inside a 36 GB VM. Even
all five ballooning at once cannot reach a global OOM. 6 GB is ~10× a seat's
MEASURED steady state (~600 MB).

`C:\Users\Mandrake\.wslconfig`, written 2026-08-14, **needs `wsl --shutdown`**:
`memory=36GB`, `swap=16GB`, `[experimental] autoMemoryReclaim=gradual`.

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
