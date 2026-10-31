"""testq/retest.py -- what counts as a verdict at a code version (RETEST_RULE_ONCE_PER_CODE_VERSION).

Owner ruling by card 2026-10-31, "Retest only after a code change": an item is tested once per code version; a
harness-invalid run is repaired, never counted.

A CODE VERSION is modcheck's gate.code_version: the chain's runtime hash, the runtime hash of every mod composed with
it, its own code slice and its declared inputs. The harness is deliberately not in it: a harness change must not
retest what stood, and what it broke was never counted.

A row is the HARNESS's when it says the run did not measure (CAUSES). Such a chain has no verdict, unless a row FAILED:
a real FAIL stands whatever else broke. ingest records no verify for it and files one repair item per distinct cause;
the filler holds its chains while that item is open. A row owed a live check, or a map without the feature, is a
real GAP and so a verdict: nothing a rerun at the same code can change.
"""
import hashlib
import re

CAUSES = (("canary", r"canary red"),
          ("site_hold", r"could not hold the site quiet"),
          ("surprise", r"\bsurprise: |a surprise ended this chain"),
          ("selftest_not_run", r"SelfTest did not run"),
          ("absent_from_sheet", r"absent from the sheet"),
          ("run_aborted", r"\(run aborted"))
UPSTREAM = re.compile(r"upstream failed|an UNMEASURED component ended this chain")
ORPHAN = "<no chain>"           # split_rows key: rows the sheet never reached carry no chain
NOT_A_FAULT = ("BLOCKED_SELECTION",)        # the selection was refused: no run happened
LANE_CAUSES = ("CANARY",)                   # testq.PAUSE_ON with an INVALID outcome: lane_finding has these


def normal(text):
    """Text with what differs between two sightings of one cause taken out."""
    t = re.sub(r"\S*[\\/]\S*", "<path>", str(text or ""))
    t = re.sub(r"\b(?:0x)?[0-9a-fA-F]{8,}\b", "#", t)
    return re.sub(r"\s+", " ", re.sub(r"\d+(?:\.\d+)?", "#", t)).strip()


def row_cause(row):
    """-> the cause signature of a row that did not measure, or None."""
    if row.get("verdict") in ("PASS", "FAIL", "SKIP"):
        return None
    detail = str(row.get("detail") or "")
    for name, pat in CAUSES:
        if re.search(pat, detail):
            return "%s: %s" % (name, normal(detail)[:80])
    if row.get("validity") == "invalid":
        return "invalid_run: %s" % normal(detail)[:80]
    return None


def split_rows(rows):
    """-> (kept, held, {chain or ORPHAN: cause}): the rows that may carry a verdict, those that may not, and why."""
    by, order = {}, []
    for r in rows or []:
        k = r.get("chain") or ORPHAN
        if k not in by:
            order.append(k)
        by.setdefault(k, []).append(r)
    causes = {}
    for k in order:
        if k == ORPHAN or not any(r.get("verdict") == "FAIL" for r in by[k]):
            kinds = {}          # every KIND of fault: closing the repair of one must not release the other
            for c in map(row_cause, by[k]):
                if c:
                    kinds.setdefault(c.split(":")[0], c)
            if kinds:
                causes[k] = " + ".join(kinds.values())
    if causes:          # a chain stopped by a harness chain's failure: not a verdict on it either
        first = next(iter(causes.values()))
        for k in order:
            if k not in causes and k != ORPHAN and not any(r.get("verdict") == "FAIL" for r in by[k]) \
                    and any(UPSTREAM.search(str(r.get("detail") or "")) for r in by[k]):
                causes[k] = first
    kept, held = [], []
    for k in order:
        if k == ORPHAN:
            for r in by[k]:
                (held if row_cause(r) else kept).append(r)
        else:
            (held if k in causes else kept).extend(by[k])
    return kept, held, causes


def job_cause(res):
    """-> the cause signature of a job that ended with no sheet to read, or None (DONE, a refusal, a paused lane)."""
    if (res or {}).get("outcome") != "INVALID" or res.get("cause") in NOT_A_FAULT + LANE_CAUSES:
        return None
    note = str(res.get("note") or "")
    m = re.match(r"modcheck exit (\S+) and no sheet JSON", note)
    if m:
        err = re.search(r"\b[A-Z]\w*Error\b", note)
        return "%s: modcheck exit %s, no sheet%s" % (res.get("cause"), m.group(1), " (%s)" % err.group(0) if err else "")
    return "%s: %s" % (res.get("cause"), normal(note)[:80])


def repair_base(cause):
    """The repair item's name: the cause's, not a job's, so a second sighting finds the first."""
    return "HARNESS_REPAIR_CAUSE_%s" % hashlib.sha1(cause.encode("utf-8")).hexdigest()[:8].upper()


def _generations(items, base):
    """-> the names of BASE's repair items that exist: BASE, BASE_2, BASE_3 ..."""
    names = []
    while (base if not names else "%s_%d" % (base, len(names) + 1)) in (items or {}):
        names.append(base if not names else "%s_%d" % (base, len(names) + 1))
    return names


def repair_slot(items, base, terminal=("done", "dropped", "superseded")):
    """-> (name, "note") for an open repair of this cause, else (the next free name, "file"). A cause back after its
    repair closed is a new item: a closed item stays closed."""
    for name in _generations(items, base):
        if items[name].state not in terminal:
            return name, "note"
    gen = len(_generations(items, base)) + 1
    return (base if gen == 1 else "%s_%d" % (base, gen)), "file"


def repair_open(items, cause, terminal=("done", "dropped", "superseded")):
    """True while an item is open for CAUSE. No item yet (a run from before this rule, or ingest still to come) holds
    nothing: a hold nobody can see or release would be a silent stop."""
    return any(items[n].state not in terminal for n in _generations(items, repair_base(cause)))
