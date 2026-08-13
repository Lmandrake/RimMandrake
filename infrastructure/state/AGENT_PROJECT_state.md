# AGENT_PROJECT_state.md — where PROJECT is

**Cross-session address:** `uds:/run/user/1000/cc-socks/89547.sock`
_(PID-based; republish on every resume — a dead socket routes silently to whoever
inherits the PID, which is worse than none.)_

Identity: `infrastructure/agents/PROJECT.md`, injected automatically. Queue: `infrastructure/state/queue/PROJECT.md`.
Shared rules: `agents_def.md`. Closed items: `CLOSED.md`.

---

## Live state

**Game is DOWN.** No RimWorld process; `Player.log` baseline is clean at 25 xrefs
(OPS, `AGENT_OPS_state.md`).

**A WRAP was ordered by the owner and completed.** OPS (`afe1879`) and CREATE
(`106bc63`, `ef9f1be`) both replied `WRAP DONE`; neither held the bridge and
neither left anything on a map. BRIDGE and VISION were not live. This file is my
own step 5.

**v1 is 2/8 verified and the shape of the remainder changed today.** Row 2 moved
from "closable offline" to **blocked on the owner** — it is now
`OWNER_DECISIONS.md` #11, not a work item. Rows 3 and 4 are still genuinely
offline-authorable and still at zero, which is now the *whole* offline surface.

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

## What I owe

1. **11 owner decisions** in `OWNER_DECISIONS.md`; #11 blocks a v1 row outright
   and three others cost one word each.
2. **Execute the restructure** — plan in `infrastructure/output/RESTRUCTURE_PLAN.md`, staged,
   nothing moved yet. Owner adopted option B revised, with `Jawa/` vs
   `RimMandrake/` on **new work only**.
3. **`STRUCTURE.md` is stale and blocked** — three passes deferred because the
   file was `M` under other agents. Still lists `promo/`, misses `infrastructure/state/queue/`,
   `infrastructure/agents/`, `infrastructure/output/`.
4. **20 broken references** in `infrastructure/output/REF_AUDIT.md`, mostly line citations into
   files that shrank 80% today.
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
