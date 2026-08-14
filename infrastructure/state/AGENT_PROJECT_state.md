# AGENT_PROJECT_state.md — where PROJECT is

**Cross-session address:** `uds:/run/user/1000/cc-socks/427.sock` (name: `AGENT PROJECT`)
_(PID-based; republish on every resume — a dead socket routes silently to whoever
inherits the PID, which is worse than none.)_

Identity: `infrastructure/agents/PROJECT.md`, injected automatically. Queue: `infrastructure/state/queue/PROJECT.md`.
Shared rules: `agents_def.md`. Closed items: `CLOSED.md`.

---

## Live state

**Game state: NOT DECLARED.** `RimWorldWin64.exe` PID 16112 is running at ~9 GB,
and a full load session ran overnight (`observed/2026-08-14_load_session.md`,
3 ERROR / 13 NEEDS EYES / 8 PASS). **That is a process, not a measurement** —
BRIDGE is not in `peers.py` and rule 1b binds the declaration to BRIDGE. Do not
say LIVE until BRIDGE measures it.

**This session is the SECOND crash restart of 2026-08-14** — WSL itself died on a
memory error and rebooted at 01:51. Nothing of PROJECT's was lost: `3d756f1` is
pushed, `origin/main..HEAD` = 0. **The crash's evidence died with the kernel** —
`dmesg` is empty on the fresh boot and there is no `.wslconfig`, so WSL2 ran at
its default cap (31.7 GB of the host's 63.4 GB) and nothing recorded what filled
it. Seats up: **OPS (632) and PROJECT (427) only.** BRIDGE, CREATE and VISION
died with the VM and must be relaunched from their Windows Terminal profiles.

⚠️ **Three dead seats left work in the shared tree, some of it STAGED** —
`src/Jawa/Jawa_Armoury/` (4 files, staged), `src/Jawa/Jawa_Patches/Patches/BuzzerApostrophe_Fix.xml`,
five `REVIEW_*.png` under `src/RimMandrake/KotORBandolierNorthFix/Source/`, and
`observed/2026-08-14_load_session.md`. **Nobody is holding them.** Any seat that
commits a pathspec near those paths adopts them silently — read
`git status --porcelain <paths>` first.

**v1 is 4 of 8 closed (rows 1, 5, 6, 8) and BOTH open non-worldgen rows moved
overnight 2026-08-14:**
- **Row 4 → 2 of 3 seen.** Dune seas closed on a live `get_def` read needing no
  map. **Scrapfields is a measured DEFECT, not a blank** — 11 chunks against a
  75–125 prediction put on record before the look. OPS **O15**, `a82f50b`.
  **Do not green row 4 until it resolves.**
- **Row 3 UNBLOCKED.** It was filed as *"waits for the owner at the keyboard"*;
  BRIDGE is building `jawa/fire_quest`, deploying with `jawa/get_defs`.

🔴 **Rows 2 and 7 are the whole remaining bulk and they are ONE held event.** The
hold is W1, the sea step — **VISION specs, and VISION is the seat that is down.**
That is the top thing to tell the owner in the morning.

## ⛔ Read this before you try to message a peer by seat name

**You are almost certainly not addressable as `AGENT PROJECT`, and neither are
they.** Sessions launched before `7273f17` carry generated names (`rimworld-b8`).
`sessionTitle` names the conversation only; the messaging name is set at launch
by `--name`, which the seat profiles now pass. **Reinstall the profiles once —
`python3 src/RimMandrake/Utils/install_wt_seat_profiles.py --apply` — and it is fixed from the
next launch of each tab.** It cannot be fixed mid-session by anything.

Until then: `python3 src/RimMandrake/Utils/peers.py` prints `SEAT` beside `NAME` and flags the
mismatch. **Send to NAME.** Do not trust the older docs on this; the ones that
were wrong are corrected in place, but `git log` before 7273f17 still reads the
other way.

## What I own that is new

`src/RimMandrake/Utils/status.py` (one-command project state) · `src/RimMandrake/Utils/whats_new.py` (per-seat
doctrine delta) · `src/RimMandrake/Utils/check_refs.py` + `src/RimMandrake/Utils/doc_budget.py` (mechanical
enforcement) · `src/RimMandrake/Utils/check_git_locks.py` · `src/RimMandrake/Utils/wrap_order.sh` (WRAP protocol,
§9 of the messaging skill) · `OWNER_DECISIONS.md` · `infrastructure/output/` and `infrastructure/disposing/`
tiers.

## ✅ The queue debt is LARGELY PAID — 2,843 → 1,061 overnight, 2026-08-14

**The previous entry here said 2,843 lines against a 750 combined budget, with
`CREATE.md` at 1,027. Both numbers are now dead** — kept only as the baseline.

| queue | was | now |
|---|---|---|
| `BRIDGE.md` | 690 | **148** ✅ (BRIDGE, `c4e8ced`) |
| `PROJECT.md` | 200 | **145** ✅ (this seat) |
| `CREATE.md` | 1,027 | **169** (+19) |
| `VISION.md` | 465 | **465** — 🔴 the seat is DOWN and cannot compact it |
| **total** | **2,843** | **1,061** |

**Method that worked, in one line:** closed items become ONE line in `CLOSED.md`,
live reference moves to the seat's `AGENT_<SEAT>_state.md`, provenance goes in the
commit. It is not PROJECT's to edit another seat's queue — but asking, with the
measured number and a named first cut, moved 542 lines in one exchange.

⚠️ **`CLOSED.md` then hit its own 150 budget** — the two oldest days are split into
`infrastructure/state/CLOSED_archive_2026-08-12_13.md` (68 rows). **Grep all of
`infrastructure/state/`, not just `CLOSED.md`, before re-filing anything.** The
archive is the designed answer (`doc_budget.py:79`); suppressing a closure to fit
is never.

## What I owe

1. **Owner decisions** in `OWNER_DECISIONS.md`. **#5 and #7 were ruled and executed
   2026-08-13** — `TODO.md` retired, the stale-file set deleted. #8 and #9 remain,
   both pure taste, both `[v2]`.
2. **Execute the restructure** — plan in `infrastructure/disposing/RESTRUCTURE_PLAN.md`, staged,
   nothing moved yet. Owner adopted option B revised, with `Jawa/` vs
   `RimMandrake/` on **new work only**.
3. **`STRUCTURE.md` is stale and blocked** — three passes deferred because the
   file was `M` under other agents. Still lists `promo/`, misses `infrastructure/state/queue/`,
   `infrastructure/agents/`, `infrastructure/output/`.
4. **12 broken references** in `infrastructure/output/REF_AUDIT.md` (regenerate with
   `python3 src/RimMandrake/Utils/check_refs.py --markdown > infrastructure/output/REF_AUDIT.md`),
   mostly line citations into files that shrank 80% today.
5. **3 docs over budget** (`python3 src/RimMandrake/Utils/doc_budget.py`).
6. **Deferred renames** — `JawaBench.BridgeTools` → `RimMandrake.Bridge`, the
   `jawa/` tool namespace (35 files, 3 generated), five `Jawa*` mod folders whose
   packageIds ARE live in `ModsConfig.xml`.

## Standing method

- **Re-read the source before raising anything from a list of other seats' work.**
  Two settled items went to the owner in one session from a stale list. One grep
  is cheaper than a decision cycle. This cuts both ways: two items filed AT me
  during the wrap were also re-verified before I acted, and both held.
- **A ledger line is how a wrong answer becomes permanent.** `CLOSED.md` exists to
  stop re-investigation, so an entry that closes a question the wrong way is worse
  than no entry. When a finding is overturned, correct the ledger in the same
  commit.
- **Provenance goes in the commit, not the doc.** Delete the sentence; if the doc
  still tells you what to do, it was provenance.
- `git status` a shared doc before editing; hold it for minutes, not hours.
- Commit explicit paths, read `--cached --stat`, push immediately.
