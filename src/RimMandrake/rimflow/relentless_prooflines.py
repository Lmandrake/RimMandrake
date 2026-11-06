#!/usr/bin/env python3
"""A built item owing a live criterion with no `live-proof <id>:` line waits for ever: `relentless.eligible()` admits only
proposed/ready, and the live round never turns a missing line into work (a guessed line would pass a clause nobody proved).
PROOFLESS_WIRE_ENROL_487_BUILT_STRANDED (measured 2026-11-06: 487 items, 858 criteria) enrols such an item as a
PROOF-LINES JOB: a store flag (`proof_lines`), never a ledger move. The lease issues no `rimflow start` (which would move
built -> doing and lose built_sha), the worker writes only the missing lines (and `.criteria` where needed), and its
checked PASS marks the store done with no `close`/`implemented`: the ledger stays built and the next live round finds the
lines. A per-tick cap (rules `proof_lines_per_tick`) keeps the backlog from flooding the pool.

Pure functions here; relentless.py calls them from enrol(), _lease(), retire() and the closing step."""
import re

TESTABLE = ("built", "validated")       # relentless_live.TESTABLE: the states the live round reads
LIVE_LEVELS = ("L1", "L2", "GREEN-MIN", "GREEN-FULL")       # relentless_live.LIVE_LEVELS
PROOFS_DIR = "infrastructure/state/live_proofs"
# relentless_live_round.PROOF_LINE's two spellings: `live-proof A1: cmd` and `- live-proof A1: cmd` (backticks optional)
_LINE = re.compile(r"^\s*(?:[-*]\s+)?`?live-proof\s+(?P<cid>[A-Za-z0-9_.-]+)\s*:\s*\S")
FLAG = "proof_lines"


def lined(text, proof_lines=None):
    """-> the set of criterion ids with a proof line in `text`. `proof_lines` is relentless_live_round.proof_lines when
    the caller has it (the round's own reader, so the two never disagree); this module's regex otherwise."""
    if proof_lines is not None:
        return set(proof_lines(text or ""))
    return {m.group("cid") for m in map(_LINE.match, (text or "").splitlines()) if m}


def owed_lines(item, text, proof_lines=None):
    """item: {"state", "built_sha", "criteria": [{"id", "level", "cut"?}], "outstanding": [ids]}. -> the outstanding
    live criteria with no line, in ledger order. A cut criterion (the ledger text truncated, no prose to extend it) is
    owed too: its line is still missing, and the worker reads the prose."""
    if item.get("state") not in TESTABLE or not item.get("built_sha"):
        return []
    level = {c["id"]: c.get("level") for c in item.get("criteria") or []}
    have = lined(text, proof_lines)
    return [c for c in item.get("outstanding") or [] if level.get(c) in LIVE_LEVELS and c not in have]


def stranded(items, proofs_of, proof_lines=None):
    """-> [(item id, [owed criterion ids])] for every item owing a line. proofs_of(id) -> its live_proofs text or ''."""
    out = []
    for it in items:
        if it.get("state") not in TESTABLE or not it.get("built_sha"):
            continue
        owed = owed_lines(it, proofs_of(it["id"]), proof_lines)
        if owed:
            out.append((it["id"], owed))
    return out


def eligible(it, owed, r, blocked=False, excluded=False, leased=False, hand=None):
    """The sibling of relentless.eligible() for a proof-lines job. `it` is a model item (or anything with owner, state,
    needs); `owed` its owed_lines(). Admits a built/validated item in a pool seat that owes at least one line; refuses
    one whose lines are all present, an owner item, a blocked, excluded, leased or hand-check one."""
    if not r.get("proof_lines_per_tick"):
        return False
    return bool(owed) and it.owner in r["pool_seats"] and it.state in TESTABLE and getattr(it, "needs", None) != "owner" \
        and not blocked and not excluded and not leased and not hand


def enrol(store, fx, r, now, new_state, iso, ours, queued):
    """Enrol up to rules `proof_lines_per_tick` stranded items as proof-lines jobs, inside the line's cap `max_queued`.
    `ours`: items the store already carries (any status but done); `queued`: how many wait in line now. -> [ids]."""
    cap = int(r.get("proof_lines_per_tick") or 0)
    room = min(cap, int(r["max_queued"]) - queued)
    if room <= 0 or not hasattr(fx, "proof_lines_order"):
        return []
    took = []
    for item, owed in fx.proof_lines_order(r):
        if len(took) >= room:
            break
        if item in ours:
            continue
        with store.lock():
            cur = store.load(item)
            if cur is not None and cur["status"] != "done":
                continue
            if cur is not None and is_job(cur) and set(owed) <= set(cur[FLAG].get("owed") or ()):
                continue    # a checked PASS wrote these lines: the books lag or the round reads them, never a second job
            st = new_state(item, now, "proof lines owed: %s" % ", ".join(owed))
            st[FLAG] = {"owed": list(owed)}
            if cur is not None:     # a done life (an earlier lines job, or a closed build): a new life keeps the count
                st["gen"] = cur["gen"] + 1
                st["attempts"] = cur.get("attempts", 0)
                st["spent"] = cur.get("spent", 0)
            store.save(st)
            store.journal({"at": iso(now), "do": "enrol", "item": item, FLAG: list(owed)})
        took.append(item)
    return took


def is_job(st):
    return bool(st and st.get(FLAG))


def still_owed(st, led):
    """retire()'s test for a proof-lines job: it stays while the ledger holds it built/validated with no seat lease."""
    return bool(led) and led.get("state") in TESTABLE and not led.get("lease")


def brief(st):
    """The worker's extra paragraph: lines only, never the ledger."""
    owed = ", ".join((st.get(FLAG) or {}).get("owed") or []) or "(see the item's criteria)"
    return "\n".join([
        "",
        "--- PROOF-LINES JOB ---",
        "This item is already BUILT on the ledger. It owes only live-proof lines for these criteria: %s." % owed,
        "Write one `live-proof <crit>: <command>` line per owed criterion in %s/<ID>.txt (and `<crit> L1|L2: what is "
        "observed` in <ID>.criteria where a clause is not on the ledger criteria), a read-only command that exits 0 when "
        "the clause holds, 1 when it does not, 2 with `UNMEASURED: <reason>` when it could not ask. Lint each line with "
        "relentless_live.refused_proof (your contract's proof should run that lint). Change no code and no mod." % PROOFS_DIR,
        "A criterion no honest line can prove (an owner look, a stale criterion) is put down on the ledger with its reason "
        "(`rimflow note`), never a guessed line. The ledger stays built: no rimflow start, close or implemented, and no "
        "contract --game (the live round runs the lines once they land).",
    ])
