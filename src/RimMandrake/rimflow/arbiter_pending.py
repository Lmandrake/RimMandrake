#!/usr/bin/env python3
"""arbiter_pending.py - what makes an Arbiter batch due (item ARBITER_BUILD_LAUNCH_ON_ANY_PENDING_WORK).

role_launch.py's `slot_when: "pending_work"` asks this module whether a scheduled slot has work. The answer comes from
STATE, never from a cursor, so a launch consumes nothing: a launch that is refused, dies or never writes a verdict
leaves every piece of work pending for the next slot (arbiter.md "A launch consumes nothing").

The four kinds (schedule `pending_work`, default all four, in the order the batch works them, arbiter.md When you run):
  escapes         a `file` (from / caused_by) or `spawn` (from) whose cause is an item with a PASS or CONDITIONAL-PASS
                  line in verdicts.jsonl, filed after that verdict; pending until a check spec is filed against the
                  escape (a later `file` / `spawn` whose from / caused_by is the escape's id).
  unresolved      an item+sha whose newest line in verdicts.jsonl is UNRESOLVED (no window: it waits until judged).
  done_claims     the newest `close` of each item AT OR AFTER THE CUTOFF, with no final verdict line for that item
                  and sha and no tiers_history decision PASS (the no-AI tiers passed it; BOUNCE, AI and HOLD still
                  need the Arbiter). Oldest close first. No age limit: a claim waits until judged
                  (ARBITER_FIX_CLAIMS_AGE_OUT_UNJUDGED; the old 7-day window dropped unjudged claims silently).
  verify_backlog  an item in state built or validated, built (implemented) at or after the cutoff, that owes L1, L2,
                  L3, GREEN-MIN or GREEN-FULL (L4 is his).

The cutoff (ARBITER_DECIDE_BACKLOG_NEVER_DRAINS, BENCH delegated ruling 2026-10-27): the Arbiter's queue is the work
after the moment it is enabled. CUTOFF (env RM_ARBITER_CUTOFF) is stamped once, at enable, by `stamp`, and never
moved. The pre-enable backlog (closes and built items before it) is NOT the Arbiter's: it goes to the Auditor's
risk-ranked sampling and audit_prescreen's hard flags; nothing here drops or bulk-judges it. With no stamp the kinds
that need it raise NoCutoff and role_launch HOLDS the slot with an alarm: launching would put the whole pre-enable
backlog in front of the Arbiter, which is exactly what the ruling forbids.

Stores: D:\\ClaudeWork\\rimmandrake\\arbiter\\verdicts.jsonl (the Arbiter's lines, fields in arbiter.md) and
D:\\ClaudeWork\\rimmandrake\\arbiter_tiers\\tiers_history.jsonl (arbiter_tiers.py). An ABSENT file is empty (the Arbiter
or the tiers never ran: every claim is unjudged); an unreadable or torn one raises, and role_launch launches anyway
(work may be pending; launching is the safe direction) with the reason in the trigger.

    python3 src/RimMandrake/rimflow/arbiter_pending.py                 # print what the next slot would see
    python3 src/RimMandrake/rimflow/arbiter_pending.py stamp --by BENCH --why "advisory enable" [--at ISO]
"""
import argparse, calendar, json, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from contracts import compat as CC, jsonl as CJ   # noqa: E402 - stdlib only: the dispatcher tick imports this module

VERDICTS = "/mnt/d/ClaudeWork/rimmandrake/arbiter/verdicts.jsonl"
TIERS_HISTORY = "/mnt/d/ClaudeWork/rimmandrake/arbiter_tiers/tiers_history.jsonl"
KINDS = ("escapes", "unresolved", "done_claims", "verify_backlog")
DISPOSITIONS = CC.DISPOSITIONS
PASSING = ("PASS", "CONDITIONAL-PASS")
BACKLOG_LEVELS = ("L1", "L2", "L3", "GREEN-MIN", "GREEN-FULL")
CUTOFF = "/mnt/d/ClaudeWork/rimmandrake/arbiter/cutoff.json"
CUTOFF_ENV = "RM_ARBITER_CUTOFF"
NEEDS_CUTOFF = ("done_claims", "verify_backlog")


class NoCutoff(Exception):
    """No cutoff stamp: the Arbiter's queue is undefined. Deliberately NOT a ValueError/OSError (those launch)."""


def cutoff_path():
    return os.environ.get(CUTOFF_ENV) or CUTOFF


def read_cutoff(path=None):
    """-> the cutoff as epoch, or None when no stamp exists. A torn or unparsable stamp raises ValueError."""
    path = path or cutoff_path()
    try:
        with open(path, encoding="utf-8") as f:
            raw = f.read()
    except FileNotFoundError:
        return None
    try:
        t = epoch(json.loads(raw)["cutoff"])
    except (ValueError, KeyError, TypeError):
        t = None
    if t is None:
        raise ValueError("%s is not a cutoff stamp (want {\"cutoff\": ISO UTC, ...})" % path)
    return t


def stamp(path=None, at=None, by="", why=""):
    """Write the cutoff once (O_EXCL): a second stamp raises FileExistsError, so the cutoff never moves. -> ISO."""
    path = path or cutoff_path()
    iso = at or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    if epoch(iso) is None:
        raise ValueError("cutoff %r is not ISO UTC" % iso)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(fd, "w") as f:
        f.write(json.dumps({"cutoff": iso, "by": by, "why": why,
                            "stamped": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}) + "\n")
    return iso


def epoch(ts):
    try:
        return calendar.timegm(time.strptime(str(ts)[:19], "%Y-%m-%dT%H:%M:%S"))
    except (TypeError, ValueError):
        return None


def sha_match(a, b):
    """A verdict may carry a short sha and a close the full one: equal on the shorter, at least 7 characters."""
    a, b = str(a or ""), str(b or "")
    n = min(len(a), len(b))
    return n >= 7 and a[:n] == b[:n]


def read_jsonl(path, need=()):
    """-> rows in file order. Absent file -> []. A line that is not a JSON object or lacks a `need` field raises
    ValueError; an unreadable file raises OSError."""
    try:
        fh = open(path, encoding="utf-8")
    except FileNotFoundError:
        return []
    rows = []
    with fh:
        for i, line in enumerate(fh):
            r = CJ.decode(line, i + 1, need_object=False)
            if not r.ok and r.code == CJ.BLANK:
                continue
            if not r.ok:
                raise ValueError("%s line %d is not JSON" % (path, i + 1))
            if CC.truthy_problems(r.value, need):
                raise ValueError("%s line %d lacks %s" % (path, i + 1, "/".join(need)))
            rows.append(r.value)
    return rows


def read_stores(verdicts=VERDICTS, history=TIERS_HISTORY, cutoff=None):
    """-> {"verdicts": rows, "tiers_history": rows, "cutoff": epoch or None}; raises like read_jsonl. A verdict line
    needs item, sha and a known disposition (arbiter.md), so a misspelt one is a torn store, not a silent non-verdict."""
    v = read_jsonl(verdicts, ("item", "sha", "disposition"))
    bad = [d for d in v if CC.verdict_row_problems(d)]
    if bad:
        raise ValueError("%s: disposition %r is not one of %s" % (verdicts, bad[0]["disposition"],
                                                                   "/".join(DISPOSITIONS)))
    return {"verdicts": v, "tiers_history": read_jsonl(history, ("item", "sha", "decision")),
            "cutoff": read_cutoff(cutoff)}


def _newest(rows, item, sha):
    found = None
    for d in rows:
        if d["item"] == item and sha_match(d["sha"], sha):
            found = d
    return found


def done_claims(events, verdicts, history, cutoff):
    """Pure. -> [(item, sha)] the newest close per item at/after the cutoff, not yet acknowledged, oldest first.
    No age limit: it stays until a verdict or a no-AI PASS acknowledges it."""
    latest = {}
    for ev in events:
        if ev.get("event") == "close" and ev.get("id") and ev.get("sha"):
            t = epoch(ev.get("ts"))
            if t is not None:
                latest[ev["id"]] = (t, ev["sha"])
    out = []
    for item, (t, sha) in sorted(latest.items(), key=lambda kv: (kv[1][0], kv[0])):
        if t < cutoff:
            continue
        v = _newest(verdicts, item, sha)
        if v is not None and v["disposition"] != "UNRESOLVED":
            continue
        h = _newest(history, item, sha)
        if v is None and h is not None and h["decision"] == "PASS":
            continue
        out.append((item, sha))
    return out


def unresolved(verdicts):
    """Pure. -> [(item, sha)] whose newest line for that item and sha is UNRESOLVED."""
    out = []
    for d in verdicts:
        k = (d["item"], d["sha"])
        if k not in out and _newest(verdicts, *k)["disposition"] == "UNRESOLVED":
            out.append(k)
    return sorted(out)


def _cause(ev):
    """-> (escape id, cause ids) of a filing event, or (None, ())."""
    if ev.get("event") == "file":
        return ev.get("id"), tuple(x for x in (ev.get("from"), ev.get("caused_by")) if x)
    if ev.get("event") == "spawn":
        return ev.get("name"), tuple(x for x in (ev.get("from"), ev.get("caused_by")) if x)
    return None, ()


def escapes(events, verdicts):
    """Pure. -> [(escape id, passed item)] work filed against an item after the Arbiter passed it, with no check spec
    filed against the escape yet."""
    passed = {}
    for d in verdicts:
        t = epoch(d.get("ts"))
        if d["disposition"] in PASSING and t is not None:
            passed[d["item"]] = min(t, passed.get(d["item"], t))
    found, specced = [], set()
    for ev in events:
        eid, causes = _cause(ev)
        if not eid:
            continue
        specced.update(causes)
        t = epoch(ev.get("ts"))
        for c in causes:
            if c in passed and t is not None and t > passed[c]:
                found.append((eid, c))
    return sorted(set(e for e in found if e[0] not in specced))


def verify_backlog(world, cutoff):
    """Pure but for the World. -> [(item, "L1,L2")] built/validated items, built at/after the cutoff, owing an Arbiter
    level. An item with no build time is pre-cutoff (the Auditor's backlog), never silently the Arbiter's."""
    out = []
    for iid, it in world.items.items():
        built = epoch(getattr(it, "built_at", None))
        if getattr(it, "state", None) in ("built", "validated") and built is not None and built >= cutoff:
            owed = [L for L in it.owed_levels() if L in BACKLOG_LEVELS]
            if owed:
                out.append((iid, ",".join(owed)))
    return sorted(out)


def pending(lr, stores, now, kinds=KINDS):
    """lr = role_launch.read_ledger()'s {"events", "world"}; stores = read_stores()'s dict.
    -> {kind: [entries]} for the asked kinds that have any (empty dict = nothing pending). Raises NoCutoff when a
    kind needs the cutoff and none is stamped. `now` is kept for callers; no kind ages out."""
    cutoff = stores.get("cutoff")
    if cutoff is None and any(k in NEEDS_CUTOFF for k in kinds):
        raise NoCutoff("no Arbiter cutoff stamp at %s: its queue (work after enable) is undefined. Stamp it at enable: "
                       "python3 src/RimMandrake/rimflow/arbiter_pending.py stamp --by SEAT --why ..." % cutoff_path())
    out = {}
    for k in kinds:
        if k == "escapes":
            got = escapes(lr["events"], stores["verdicts"])
        elif k == "unresolved":
            got = unresolved(stores["verdicts"])
        elif k == "done_claims":
            got = done_claims(lr["events"], stores["verdicts"], stores["tiers_history"], cutoff)
        elif k == "verify_backlog":
            got = verify_backlog(lr["world"], cutoff)
        else:
            raise ValueError("pending_work kind %r is not one of %s" % (k, ", ".join(KINDS)))
        if got:
            out[k] = got
    return out


def summary(p):
    """'2 escapes (first X), 1 unresolved (Y), ...' for a trigger line (done claims: first = oldest)."""
    return ", ".join("%d %s (first %s)" % (len(v), k.replace("_", " "), v[0][0]) for k, v in p.items())


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:1] == ["stamp"]:
        s = argparse.ArgumentParser(prog="arbiter_pending.py stamp")
        s.add_argument("--at", help="ISO UTC (default now)")
        s.add_argument("--by", required=True)
        s.add_argument("--why", required=True)
        s = s.parse_args(argv[1:])
        try:
            print("cutoff stamped %s at %s" % (stamp(None, s.at, s.by, s.why), cutoff_path()))
        except FileExistsError:
            print("REFUSED: %s exists (cutoff %s); a cutoff is stamped once and never moved" % (
                cutoff_path(), open(cutoff_path()).read().strip()), file=sys.stderr)
            return 2
        return 0
    a = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    a.parse_args(argv)
    from rimflow import role_launch
    lr = role_launch.read_ledger()
    try:
        stores = read_stores()
    except (OSError, ValueError) as ex:
        print("stores UNMEASURED (%s): a slot launches anyway" % ex)
        return 2
    try:
        p = pending(lr, stores, time.time(), KINDS)
    except NoCutoff as ex:
        print("HOLD: %s" % ex)
        return 2
    print(json.dumps({k: len(v) for k, v in p.items()}))
    print(summary(p) if p else "nothing pending: a slot would hold")
    return 0


if __name__ == "__main__":
    sys.exit(main())
