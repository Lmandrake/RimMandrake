# Where should Claude Code run on Windows?

Four candidate homes: **WSL2**, **native Windows (Git Bash)**, **Cygwin**, and
**cloud/Cowork sessions**. This is the honest comparison, with the measurements
that exist and explicit marks on everything that is only reasoning.

Machine under discussion, MEASURED 2026-08-14: Windows 10.0.26200, 63.4 GB RAM,
RTX 5080 16 GB, WSL 2.7.11.0, kernel 6.18.33.2, cgroup v2, VM ceiling 31.7 GB.

---

## 1. The decision table

| | WSL2 (today) | native Windows + Git Bash | Cygwin | cloud / Cowork |
|---|---|---|---|---|
| **per-seat memory cap** | ✅ cgroup v2 — MEASURED working | ❌ no cgroup equivalent; Job Objects exist but nothing wires them up | ❌ none | n/a — someone else's box |
| **one seat can kill the fleet** | ✅ only if unbounded (fixable, §OOM) | ⚠️ INFERRED: a runaway hits the *host* — Windows swaps rather than OOM-killing, so the whole desktop degrades | ⚠️ same as native | no |
| **access to Windows files** | via 9P, ~55× slower on writes (MEASURED) | ✅ native speed | ✅ native speed | ❌ **cannot see mounted project drives** |
| **can commit / delete in the repo** | ✅ | ✅ | ✅ | ❌ **write-only** — MEASURED limitation here |
| **bash/python toolchain** | ✅ full Linux | ⚠️ Git Bash is MSYS2 — most of it works, some does not | ⚠️ POSIX emulation, quirky | ✅ |
| **Node.js for Claude Code** | ✅ present | ❌ **not installed on this box** (MEASURED) | ⚠️ needs native win32 Node; Cygwin-built Node is not the supported path | ✅ |
| **maintained / mainstream in 2026** | ✅ | ✅ | ⚠️ largely superseded | ✅ |

**MEASURED on this box:** `C:\Program Files\Git\bin\bash.exe` **is** installed;
`git` resolves to `C:\Program Files\Git\cmd\git.exe`. **Node is not installed
natively** — `/mnt/c/Program Files/nodejs/` does not exist and
`Get-Command node` returns nothing.

⇒ **A native-Windows migration is possible but not free: install Node first.**

---

## 2. 🔴 The counter-intuitive part: the cgroup is a WSL *advantage*

The OOM story reads like "WSL is fragile". It is the opposite.

**Linux gives you a per-process-tree memory cap you can actually apply**, in one
line, to an arbitrary program you did not write:

```bash
systemd-run --user --scope -p MemoryMax=6G -p MemorySwapMax=2G -- claude …
```

**Native Windows has no equivalent that is usable this way.** The nearest
primitive is a **Job Object** with `JOBOBJECT_EXTENDED_LIMIT_INFORMATION`
(`ProcessMemoryLimit` / `JobMemoryLimit`) — real, documented, and:

- **Claude Code does not create one for you** (INFERRED — no such feature is
  documented, and nothing in the launcher suggests it).
- There is **no out-of-the-box PowerShell cmdlet** that caps an arbitrary
  process's memory. You would write a small launcher against the Win32 API, or
  use a third-party wrapper. UNVERIFIED whether a maintained wrapper exists.
- Windows Job Objects were used by `start /affinity`-era tooling and by Windows
  Sandbox / containers, but not exposed as a general per-app RAM cap.

⇒ **Moving to native Windows would mean giving up the containment described in
`oom-diagnosis.md` and rebuilding it.** That is the strongest single argument
for staying on WSL, and it is the argument that runs against intuition.

---

## 3. The filesystem tax — real, modest, and NOT the crash cause

MEASURED, 400 small files, this box, reproduced twice:

| location | 400 writes | stat pass |
|---|---|---|
| ext4 `~` (inside the VM) | **0.01 s** | 0.01–0.05 s |
| 9P `/mnt/d` (repo) | **0.47–0.55 s** | 0.35–0.54 s |
| 9P `/mnt/c` | **0.78 s** | 0.42–0.78 s |

So 9P is roughly **55× slower on writes** and **7× on stat** than ext4.

**But state the absolute cost, not just the ratio:** `git status --porcelain`
over 24,905 files takes **1.50 s** (MEASURED; reproduced at 1.53 s). That is a
tax, not a crisis.

⚠️ **The 9P page cache was tested as an OOM cause and REFUTED** — three full
repo read passes moved `Cached` 1071 → 1073 MB. Flat. Do not blame 9P for
memory.

**Mitigations that are cheap:** keep build scratch and caches on ext4 (`~`),
keep the repo where the humans and the Windows tools expect it, and batch
filesystem operations rather than looping shell calls over `/mnt`.

---

## 4. The lock-in argument, stated honestly

**Against WSL, and it is a real point:** this project's entire subject matter is
Windows files — the game install under `C:\Program Files (x86)\Steam\…`,
`Player.log` in `AppData\LocalLow`, `ModsConfig.xml`, the Workshop tree. Every
one of them is reached over 9P. A native host would touch them directly.

**For staying, and this is the stronger point:** the whole toolchain — every
script under `src/RimMandrake/Utils/`, the hooks, the samplers — is bash and
python **written from scratch because WSL was the choice**. The lock-in is real
but it is *self-inflicted and recent*, not inherited from a vendor. It could be
ported. It would cost days.

**The tiebreaker is §2:** the containment. A native fleet would need a Job
Object launcher written before it was as safe as the WSL fleet is with one shell
script.

**Recommendation: stay on WSL. Install the bound (`claude_bounded.sh`).**
Revisit only if 9P latency becomes a measured bottleneck on a real task — it is
not one today at 1.5 s per `git status`.

---

## 5. Cygwin — current standing

- **Largely superseded.** WSL2 for a real Linux userland; MSYS2 / Git Bash for a
  POSIX shell over native Windows binaries. Cygwin remains maintained but is a
  niche choice for new work. *(General ecosystem position; UNVERIFIED against a
  2026 primary source.)*
- **No cgroups, no memory-cap primitive.** Cygwin is a POSIX emulation layer
  over Win32; it cannot offer a resource controller Windows does not have.
- **Node story is poor.** Claude Code needs Node; the practical route under
  Cygwin is the native win32 Node binary driven from a Cygwin shell, which
  reintroduces every path-translation problem Cygwin exists to hide.
  **UNVERIFIED that Claude Code runs under Cygwin at all** — no report either
  way was found.

⇒ **Do not pick Cygwin for this.** If you want POSIX over native Windows, Git
Bash (MSYS2) is the maintained answer and is already installed here.

---

## 6. Cloud / Cowork sessions

MEASURED constraints in this project:

- **Mounted project drives are not visible** to a cloud session's shell.
- Files there **cannot be deleted or committed** by the assistant — **only
  written**. Deletions and all `git` operations must be done locally.

⇒ Cloud sessions are useful for **authoring and research**, not for anything
that has to land in the tree. Treat their output as a draft another seat commits.

---

## 7. `.wslconfig` — the knobs that matter

`C:\Users\Mandrake\.wslconfig`, and **every change needs `wsl --shutdown`**:

```ini
memory=36GB
swap=16GB

[experimental]
autoMemoryReclaim=gradual
```

- `memory` — hard ceiling on the VM's RAM. Default is a fraction of host RAM.
- `swap` — size of the VM's swap file. **Not a substitute for a memory cap**;
  unbounded swap is what turns a fast OOM kill into a seven-minute crawl.
- `autoMemoryReclaim` — returns freed guest memory to the host. Values seen:
  `disabled` / `gradual` / `dropcache`. **UNVERIFIED against current Microsoft
  documentation**; `gradual` is what is set here and it has not misbehaved.

⚠️ **Raising `memory` is not a fix on its own.** A process that reaches 27 GB
will reach 40 GB. Raise the ceiling *and* bound the seats, or you have only
moved the same kill later.
