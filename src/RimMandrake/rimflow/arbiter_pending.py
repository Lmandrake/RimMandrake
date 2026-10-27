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
  done_claims     the newest `close` of each item within `claim_window_days` (default 7 = arbiter_tiers.py --days),
                  with no final verdict line for that item and sha and no tiers_history decision PASS (the no-AI tiers
                  passed it; BOUNCE, AI and HOLD still need the Arbiter).
  verify_backlog  an item in state built or validated that owes L1, L2, L3, GREEN-MIN or GREEN-FULL (L4 is his).

Stores: D:\\ClaudeWork\\rimmandrake\\arbiter\\verdicts.jsonl (the Arbiter's lines, fields in arbiter.md) and
D:\\ClaudeWork\\rimmandrake\\arbiter_tiers\\tiers_history.jsonl (arbiter_tiers.py). An ABSENT file is empty (the Arbiter
or the tiers never ran: every claim is unjudged); an unreadable or torn one raises, and role_launch launches anyway
(work may be pending; launching is the safe direction) with the reason in the trigger.

    python3 src/RimMandrake/rimflow/arbiter_pending.py [--days 7]     # print what the next slot would see
"""
import argparse, calendar, json, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

VERDICTS = "/mnt/d/ClaudeWork/rimmandrake/arbiter/verdicts.jsonl"
TIERS_HISTORY = "/mnt/d/ClaudeWork/rimmandrake/arbiter_tiers/tiers_history.jsonl"
KINDS = ("escapes", "unresolved", "done_claims", "verify_backlog")
DISPOSITIONS = ("PASS", "CONDITIONAL-PASS", "FAIL-module", "FAIL-check", "RESTART-environment", "BAR-defect",
                "UNRESOLVED")
PASSING = ("PASS", "CONDITIONAL-PASS")
BACKLOG_LEVELS = ("L1", "L2", "L3", "GREEN-MIN", "GREEN-FULL")
CLAIM_WINDOW_DAYS = 7


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
            if not line.strip():
                continue
            try:
                d = json.loads(line)
            except ValueError:
                raise ValueError("%s line %d is not JSON" % (path, i + 1))
            if not isinstance(d, dict) or any(not d.get(k) for k in need):
                raise ValueError("%s line %d lacks %s" % (path, i + 1, "/".join(need)))
            rows.append(d)
    return rows


def read_stores(verdicts=VERDICTS, history=TIERS_HISTORY):
    """-> {"verdicts": rows, "tiers_history": rows}; raises like read_jsonl. A verdict line needs item, sha and a
    known disposition (arbiter.md), so a misspelt one is a torn store, not a silent non-verdict."""
    v = read_jsonl(verdicts, ("item", "sha", "disposition"))
    bad = [d for d in v if d["disposition"] not in DISPOSITIONS]
    if bad:
        raise ValueError("%s: disposition %r is not one of %s" % (verdicts, bad[0]["disposition"],
                                                                   "/".join(DISPOSITIONS)))
    return {"verdicts": v, "tiers_history": read_jsonl(history, ("item", "sha", "decision"))}


def _newest(rows, item, sha):
    found = None
    for d in rows:
        if d["item"] == item and sha_match(d["sha"], sha):
            found = d
    return found


def done_claims(events, verdicts, history, now, days=CLAIM_WINDOW_DAYS):
    """Pure. -> [(item, sha)] the newest close per item in the window, not yet acknowledged."""
    latest = {}
    for ev in events:
        if ev.get("event") == "close" and ev.get("id") and ev.get("sha"):
            t = epoch(ev.get("ts"))
            if t is not None and t > now - days * 86400:
                latest[ev["id"]] = ev["sha"]
    out = []
    for item, sha in latest.items():
        v = _newest(verdicts, item, sha)
        if v is not None and v["disposition"] != "UNRESOLVED":
            continue
        h = _newest(history, item, sha)
        if v is None and h is not None and h["decision"] == "PASS":
            continue
        out.append((item, sha))
    return sorted(out)


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


def verify_backlog(world):
    """Pure but for the World. -> [(item, "L1,L2")] built/validated items owing an Arbiter level."""
    out = []
    for iid, it in world.items.items():
        if getattr(it, "state", None) in ("built", "validated"):
            owed = [L for L in it.owed_levels() if L in BACKLOG_LEVELS]
            if owed:
                out.append((iid, ",".join(owed)))
    return sorted(out)


def pending(lr, stores, now, kinds=KINDS, days=CLAIM_WINDOW_DAYS):
    """lr = role_launch.read_ledger()'s {"events", "world"}; stores = read_stores()'s dict.
    -> {kind: [entries]} for the asked kinds that have any (empty dict = nothing pending)."""
    out = {}
    for k in kinds:
        if k == "escapes":
            got = escapes(lr["events"], stores["verdicts"])
        elif k == "unresolved":
            got = unresolved(stores["verdicts"])
        elif k == "done_claims":
            got = done_claims(lr["events"], stores["verdicts"], stores["tiers_history"], now, days)
        elif k == "verify_backlog":
            got = verify_backlog(lr["world"])
        else:
            raise ValueError("pending_work kind %r is not one of %s" % (k, ", ".join(KINDS)))
        if got:
            out[k] = got
    return out


def summary(p):
    """'2 escapes (oldest X), 1 unresolved (Y), ...' for a trigger line."""
    return ", ".join("%d %s (first %s)" % (len(v), k.replace("_", " "), v[0][0]) for k, v in p.items())


def main(argv=None):
    a = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    a.add_argument("--days", type=float, default=CLAIM_WINDOW_DAYS)
    a = a.parse_args(argv)
    from rimflow import role_launch
    lr = role_launch.read_ledger()
    try:
        stores = read_stores()
    except (OSError, ValueError) as ex:
        print("stores UNMEASURED (%s): a slot launches anyway" % ex)
        return 2
    p = pending(lr, stores, time.time(), KINDS, a.days)
    print(json.dumps({k: len(v) for k, v in p.items()}))
    print(summary(p) if p else "nothing pending: a slot would hold")
    return 0


if __name__ == "__main__":
    sys.exit(main())
