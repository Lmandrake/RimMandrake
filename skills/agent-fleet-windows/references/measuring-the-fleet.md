# Measuring the fleet — the instruments, where they live, and how they lied

Three tools, one architectural rule, two traps that produced confident wrong
numbers, and an honest record of what this skill scored against no skill at all.
All measured 2026-08-14 unless marked.

---

## 1. 🔴 The monitor must not live inside the thing it monitors

MEASURED: during the OOM the VM spent **6m53s** thrashing — five of those
minutes with **zero free swap** — while the Windows host stayed fully
responsive with ~32 GB free the entire time.

⇒ Anything sampling from **inside** the VM is competing for the memory that has
just run out, exactly when its output matters most.

**Corollary, and it is a design rule not a preference: "a seat checks
sometimes" is wrong by construction.** The seat that would warn you is the seat
that dies. A watcher that shares a fate with its subject is not a watcher.

| tool | runs on | job |
|---|---|---|
| `src/RimMandrake/Utils/wsl_monitor.ps1` | **Windows** | *watch* — live glanceable readout |
| `src/RimMandrake/Utils/resource_watch.sh` | inside the VM | *forensics* — the last line before the log stops is the evidence |
| `src/RimMandrake/Utils/fs_bench.sh` | both, by design | settle WSL-vs-native with a number |

### `wsl_monitor.ps1` (commit `67fb7a7`)

Always-on-top WinForms readout of the `vmmemWSL` process, green/amber/red,
5 s refresh. Design constraints, from the owner: **no modal dialogs** (the
colour *is* the notification), nothing to reload, remembers its position, and it
comes back by itself — the `schtasks /sc onlogon` install line is in its header.
`-NoGui` runs it headless for logging. Calibration: idle 5 seats ~4.6 GB; the
fatal event ~31 GB; WARN 16 GB / CRIT 22 GB, chosen because the climb is slow
and restarting one tab at WARN costs a session instead of the fleet.

⚠️ **`vmmemWSL` is the WHOLE VM, not one agent.** MEASURED: 3.16 GB reported
against 3.07 GB summed across every process inside the VM — the gap is kernel
and page cache. Read it as a fleet total, then go to `SKILL.md` §3 to find who.

### `resource_watch.sh`

Samples WSL + Windows + GPU every 15 s into `observed/resource_watch/`
(gitignored — it is cache, not a work product). One batched PowerShell call per
tick, deliberately: each interop launch costs ~0.7 s, so four calls would cost
more than the sample is worth. The CSV header carries `wsl_boot=` and
`win_boot=` provenance lines, without which "WSL restarted" and "Windows
rebooted" are indistinguishable when you read the log back.

**Alarm on free swap, not on RSS.** MEASURED (`oom-diagnosis.md` §3a): swap went
full → empty in 1 min 55 s and then sat at zero for five minutes before the
kill. RSS growth is slow and ambiguous; swap hitting zero is neither. It fires
CRITICAL below 25%.

---

## 2. Two instrumentation traps, both hit for real

### Fixed column indices produced confident garbage

A reader parsed the sampler CSV **by column position**. Two swap columns were
added to `resource_watch.sh`; the reader kept running and reported

```
seats=1.17MB  swapfree=1932/3MB
```

— numbers that are not merely wrong but *impossible*, and it did not notice.

**Fix:** resolve columns **by header name**, and **return nothing rather than a
number you cannot justify.**

> **A monitor that misreports silently is worse than one that is absent.** An
> absent monitor sends you to look; a lying one sends you home.

**Generalises to:** any consumer of a schema it does not own. The producer is
free to add a column; only positional readers break, and they break quietly.

### `pkill -f <pattern>` matches its own shell

MEASURED, twice: `pkill -f resource_watch.sh` killed **the tool session that ran
it** (exit 144) — the pattern appears in the killer's own command line.
Separately, a shell-precedence bug in a restart's kill loop left **two
`resource_watch.sh` instances appending different schemas to one CSV**, which is
what produced the file the parser above then misread.

Safe form — match the program, not the string:

```bash
for p in $(pgrep -x bash); do
  tr '\0' ' ' < /proc/$p/cmdline | grep -q resource_watch.sh && kill "$p"
done
```

**Generalises to:** never `pkill -f` on a pattern your own command line
contains. Filter on `comm` and read `/proc/<pid>/cmdline`.

---

## 3. `fs_bench.sh` — the comparison that decides where the repo lives

Full results and conclusion: `windows-hosting.md` §4. The method matters
because the question had been argued from folklore for months:

- **The same workload text is run verbatim by both bash environments**, so the
  only variable is the path to the disk.
- 🔴 **Row 2 vs row 3 is the whole experiment**: the *same physical disk* (`D:`)
  reached through the 9P bridge from WSL, versus reached natively by Git Bash —
  which is what a native-Windows Claude Code would use for its Bash tool. That
  pair isolates the bridge from everything else.
- Row 1 (ext4) is the ceiling; row 4 (PowerShell via .NET `[IO.File]`, **not**
  cmdlets) exists so a slow PowerShell number is not misread as a slow
  filesystem.
- ⚠️ **The first run was unfair and was redone.** A clone-based comparison put
  6,044 files on ext4 against 25,254 on 9P. The published `git status` figure is
  from **identical 25,254-file trees** — the full working tree copied, untracked
  files included.

**Generalises to:** when a benchmark's two sides are prepared by different
means, the difference you measure includes the preparation.

---

## 4. What this skill scored against no skill at all

Recorded because a skill that cannot say what it is worth is asking to be
trusted on faith.

**Six runs, three scenarios, with-skill vs baseline: 15/16 both. Delta +0.00.**

The baselines were not blind: they could read `CLAUDE.md`, the `observed/`
write-ups and a heavily commented `.wslconfig`, so the knowledge was already
discoverable in the repo. **The baseline even beat the with-skill run** on two
findings — that there were two incidents rather than three, and that
`wsl --shutdown` would have saved 38 minutes over the Windows reboot. Both are
now in `SKILL.md` (§1, §7).

⇒ **This skill's value is consolidation and portability, not teaching something
otherwise unreachable.** Two consequences for anyone editing it:

1. **Do not restate what `CLAUDE.md` already tells the reader** — it is loaded
   every session and the duplicate costs tokens on every read
   (`infrastructure/DOC_BUDGET.md` rule 1). `references/shared-tree-git.md` was
   trimmed to evidence-and-procedure for exactly this reason.
2. **The measurements are the durable part.** A number off this machine cannot
   be re-derived by a reader; a rule restated from a file they already have can.
