#!/usr/bin/env python3
"""ledger_state.py - one screen of ledger state for a waking window (HANDOFF_SHRINK_HALF_THE_BYTES_WERE_GIT, half 2).

Owner, by card 2026-11-07 ("How should handoffs change? -> Trim now, generate later"): a waking window reads ledger state
rather than a narrated copy of it. A handoff's prose says what an item was doing when it was written; this file says what
the ledger says NOW, so it is generated, never written by hand, and never committed.

Four sections, each a count and at most CAP lines, so the whole file is at most MAX_LINES (one screen) on any ledger:
  Open items      this seat's open items by state; in progress first (doing, or a live lease), newest start first
  Owner-pending   what waits on the owner, every seat: owner_queue.needs_you, the same answer the status board gives
  Live helpers    every live lease on the ledger, any seat: a worker that holds an item right now
  NEXT            the newest `NEXT:` written in a ledger note on each of this seat's open items, newest first

    python3 src/RimMandrake/Utils/ledger_state.py [--seat S]     write the file, print its path
    python3 src/RimMandrake/Utils/ledger_state.py --print        build it to stdout, write nothing

`handoff.py --wake` runs write() on every wake and names the file in its pointer lines, so nobody has to remember to
regenerate it. The ledger is the one `RIMFLOW_LEDGER` names (default: the repo's); the file goes beside it, in
`<state>/derived/state_now/<SEAT>_STATE_NOW.md` (gitignored), so a test ledger never writes the real one.
"""
import argparse
import os
import re
import sys
import time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
from rimflow import model, priority  # noqa: E402

MAX_LINES = 50
CAP = 7             # rows in each one-line section
NEXT_CAP = 6        # NEXT rows are two lines each: header 3 + 3 x (2 + 7 + 1) + (2 + 12 + 1) = 48 <= MAX_LINES
WIDTH = 120         # 160 wrapped past one screen on a 120-column terminal (fresh-reader test, 2026-11-11)
REGEN = "python3 src/RimMandrake/Utils/ledger_state.py"
# "NEXT:" and its spoken forms, "NEXT then:", "NEXT (after the load):" — an owner note said "NEXT then:" and the first
# reader missed it (fresh-reader test, 2026-11-11). Never across a line: an empty NEXT: borrows nothing.
NEXT_RE = re.compile(r"\bNEXT\b[^:\n]{0,24}:[ \t]*([^\n]*)")
PACIFIC = ZoneInfo("America/Los_Angeles")     # the owner's clock (2026-11-06), whatever TZ the host runs


def ledger_head():
    """The ledger in use: RIMFLOW_LEDGER when set (the CLI's own redirect), else the repo's. It is bound onto
    model.EVENTS, because only model.read() with NO path merges the per-seat shards: read(path) reads that one file,
    the history frozen at the 2026-09-23 cutover (the first draft of this file showed BENCH as of that day)."""
    if os.environ.get("RIMFLOW_LEDGER"):
        model.EVENTS = os.environ["RIMFLOW_LEDGER"]
    return model.EVENTS


def out_path(seat, head=None):
    """<state root of the ledger in use>/derived/state_now/<SEAT>_STATE_NOW.md (the root by shape, as cli._state_root)."""
    d = os.path.dirname(os.path.abspath(head or ledger_head()))
    root = os.path.dirname(d) if os.path.basename(d) == "ledger" else d
    return os.path.join(root, "derived", "state_now", "%s_STATE_NOW.md" % seat)


def local(ts):
    """A ledger UTC stamp (or epoch) -> Pacific 'YYYY-MM-DD HH:MM PST' (PDT in summer); '?' when unreadable."""
    e = ts if isinstance(ts, (int, float)) else model.epoch(ts)
    return datetime.fromtimestamp(e, timezone.utc).astimezone(PACIFIC).strftime("%Y-%m-%d %H:%M %Z") if e is not None else "?"


def clip(s, n=WIDTH):
    """One line of at most n characters, whitespace collapsed; a leading indent is kept (a NEXT row's second line)."""
    raw = str(s or "")
    s = raw[:len(raw) - len(raw.lstrip(" "))] + " ".join(raw.split())
    n = max(n, 2)
    return s if len(s) <= n else s[:n - 1].rstrip() + "…"


def short_title(it, n=70):
    return clip(it.title or "(no title)", n)


def section(title, rows, more_cmd, total=None, cap=CAP):
    """A heading, at most `cap` rows, and one 'and N more' line naming where the rest are. A row may be a tuple of
    lines (a NEXT row is two); each line is clipped to WIDTH."""
    total = len(rows) if total is None else total
    out = ["", clip(title)]
    for r in rows[:cap]:
        out += [clip(x) for x in (r if isinstance(r, tuple) else (r,))]
    if not rows:
        out.append("- none")
    if total > min(len(rows), cap):
        out.append("- … and %d more: %s" % (total - min(len(rows), cap), more_cmd))
    return out


def standing(i, now, short=False, reason=50):
    """The item's state as it stands now, with what would stop a reader acting on it: blocked (and why), needs, and
    whose live lease it is. A row without these read a blocked, owner-gated item as plain `doing` (GPT broaden, 2026-11-11)."""
    out = [i.state]
    if i.blocked:
        out.append("BLOCKED" if short else "BLOCKED: %s" % clip(i.blocked_reason or "unexplained", reason))
    if i.needs and i.needs != "offline":
        out.append("needs %s" % i.needs)
    if model.lease_status(i, now) == "live":
        out.append("leased" if short else "leased by %s" % (i.lease.get("seat") or "?"))
    return ", ".join(out)


def open_items(world, seat, now):
    mine = [i for i in world.items.values() if i.owner == seat and i.open]
    live = {i.id for i in mine if model.lease_status(i, now) == "live"}
    counts = {}
    for i in mine:
        k = "blocked" if i.blocked else i.state
        counts[k] = counts.get(k, 0) + 1
    order = ("doing", "ready", "proposed", "built", "validated", "blocked")
    tally = " · ".join("%s %d" % (k, counts[k]) for k in order if counts.get(k)) or "none"
    inprog = sorted((i for i in mine if i.state == "doing" or i.id in live),
                    key=lambda i: i.started_at or i.created_at or "", reverse=True)
    blocked = sorted((i for i in mine if i.blocked and i not in inprog), key=lambda i: i.created_at or "")
    seen = {i.id for i in inprog + blocked}
    ranked = [i for i in priority.rank(world, seat, "v1", {"now": now}) if i.id not in seen]
    rows = []
    for i in inprog + blocked:
        rows.append("- `%s` — %s: %s" % (i.id, standing(i, now), short_title(i)))
    for i in ranked:
        rows.append("- `%s` — %s, next to offer: %s" % (i.id, standing(i, now), short_title(i)))
    # then the rest, newest first: a seat holding only proposed or built work must still see some of it by name
    seen |= {i.id for i in ranked}
    rest = ("ready", "proposed", "built", "validated")
    for i in sorted((i for i in mine if i.id not in seen and i.state in rest),
                    key=lambda i: (rest.index(i.state), -(model.epoch(i.created_at) or 0))):
        rows.append("- `%s` — %s: %s" % (i.id, standing(i, now), short_title(i)))
    return section("## Open items — this seat's %d (%s)" % (len(mine), tally), rows,
                   "rimflow queue %s" % seat, total=len(mine))


def owner_pending(world, evs):
    """owner_queue.needs_you over the ledger and Relentless's holds: the status board's own answer."""
    try:
        import owner_queue
        import fleet_mods
        rel = fleet_mods.relentless_states()
        n = owner_queue.needs_you(world.items, rel, questions=owner_queue.load_questions(), evs=evs,
                                  turns=owner_queue.designer_turns())
    except Exception as e:      # noqa: BLE001  a reader that fails says so; it never reads as "nothing waits"
        return ["", "## Owner-pending — UNMEASURED (%s)" % clip(e, 100)]
    rows = []
    for t in n["topics"]:
        if len(t["items"]) == 1:
            rows.append("- `%s`: %s" % (t["items"][0], clip(t["q"], 110)))
        else:
            rows.append("- %s_* (%d items, e.g. `%s`): %s" % (t["topic"], len(t["items"]), t["items"][0],
                                                            clip(t["q"], 80)))
    head = "## Owner-pending — %d item%s in %d topic%s, every seat" % (
        n["count"], "" if n["count"] == 1 else "s", len(n["topics"]), "" if len(n["topics"]) == 1 else "s")
    if n["answered"]:
        head += " (%d more answered by him, ours to move)" % len(n["answered"])
    return section(head, rows, "python3 src/RimMandrake/Utils/owner_queue.py")


def live_helpers(world, now):
    held = sorted((i for i in world.items.values() if i.open and model.lease_status(i, now) == "live"),
                  key=lambda i: i.lease.get("expires") or "")
    rows = ["- %s holds `%s` (%s), lease to %s" % (i.lease.get("seat") or i.owner, i.id, i.state,
                                                  local(i.lease.get("expires"))[11:])
            for i in held]
    return section("## Live helpers — %d unexpired lease%s, every seat (a lease is a claim, not a running process)"
                   % (len(held), "" if len(held) == 1 else "s"),
                   rows, "rimflow queue <SEAT> (IN PROGRESS)")


# Events that only keep a claim alive say nothing new about the work, so they never mark a NEXT as overtaken.
QUIET = ("lease", "renew", "claim", "start")


def next_lines(world, evs, seat, now):
    """The newest NEXT: on each open item of this seat. A NEXT is advice as it was written: a row says so when the item
    has moved since (a later note, block, needs, verify...) or when the action is cut, and the heading says what to do."""
    mine = {i.id: i for i in world.items.values() if i.owner == seat and i.open}
    last, later = {}, {}
    for e in evs:       # model.read() is in ledger order (ts, tsn): the last NEXT read is the newest
        iid = e.get("id")
        if iid not in mine:
            continue
        m = None
        if e.get("event") == "note":
            for m in NEXT_RE.finditer(str(e.get("text") or "")):
                pass
        if m and m.group(1).strip():
            last[iid] = (e.get("ts") or "", m.group(1).splitlines()[0].strip(), e.get("seat") or "?")
            later[iid] = 0
        elif iid in last and e.get("event") not in QUIET:
            later[iid] += 1
    rows = []
    for iid, (ts, nxt, who) in sorted(last.items(), key=lambda kv: kv[1][0], reverse=True):
        # line 1: the item, how it stands now, when and by whom the NEXT was written, and whether the ledger moved on;
        # line 2: the action, which alone is cut to fit. The stamp and the warning are what make an old NEXT safe to read.
        tail = " (NEXT %s by %s%s)" % (local(ts)[5:16], who, "; ⚠ %d later event%s" % (later[iid], "" if later[iid] == 1 else "s")
                                                          if later[iid] else "")
        it, nxt = mine[iid], nxt.rstrip(".… ")
        head = "- `%s` — %s" % (iid, standing(it, now))
        over = len(head) + len(tail) - WIDTH
        if over > 0 and it.blocked:                 # too long: the block's reason gives way first, then the flags
            head = "- `%s` — %s" % (iid, standing(it, now, reason=len(clip(it.blocked_reason or "unexplained", 50)) - over))
        if len(head) + len(tail) > WIDTH or "BLOCKED: …" in head:
            head = "- `%s` — %s" % (iid, standing(it, now, short=True))
        if len(head) + len(tail) <= WIDTH:
            rows.append((head + tail, "    NEXT: " + clip(nxt, WIDTH - 10)))
        else:                                       # a long id: the stamp moves to the action's line, never cut
            lead = "    " + tail.strip() + " NEXT: "
            rows.append((head, lead + clip(nxt, WIDTH - len(lead))))
    return section("## NEXT — newest NEXT note on %d of this seat's open items, as written then (Pacific time)" % len(rows),
                   rows, "rimflow show <ID>; a ⚠ or a cut (…) row: rimflow show <ID> before acting", cap=NEXT_CAP)


def build(seat, evs=None, world=None, now=None):
    """-> the file's text, at most MAX_LINES lines. Pure over (seat, events, now) apart from the Relentless store."""
    if evs is None:
        ledger_head()
        evs = model.read()
    world = world if world is not None else model.replay(evs)
    now = now if now is not None else model.epoch_now()
    as_of = next((e["ts"] for e in reversed(evs) if e.get("ts")), None)
    seat = model.canonical(seat) or seat      # CONDUCTOR and RELENTLESS are BENCH on the ledger
    L = ["# %s — ledger state now (generated; never edit, never commit)" % seat,
         "ledger as of %s · generated %s · game %s · bridge %s" % (local(as_of), local(now), world.game or "?",
                                                                  world.bridge_holder or "free"),
         "regenerate: %s --seat %s (handoff.py --wake does it)" % (REGEN, seat)]
    L += open_items(world, seat, now)
    L += owner_pending(world, evs)
    L += live_helpers(world, now)
    L += next_lines(world, evs, seat, now)
    L = [clip(x) for x in "\n".join(L).split("\n")]      # a stray newline in any field is a line, and is counted
    if len(L) > MAX_LINES:      # cannot happen with the caps above; kept so a new section can never scroll him
        L = L[:MAX_LINES - 1] + ["(cut at %d lines: %s --print)" % (MAX_LINES, REGEN)]
    return "\n".join(L) + "\n"


def write(seat, path=None):
    """Build and write atomically; -> the path written."""
    path = path or out_path(model.canonical(seat) or seat)
    text = build(seat)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp.%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(text)
    os.replace(tmp, path)
    return path


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--seat", help="default: RIMFLOW_SEAT or AGENT_SEAT")
    ap.add_argument("--print", action="store_true", help="build to stdout, write nothing")
    a = ap.parse_args(argv)
    seat = (a.seat or os.environ.get("RIMFLOW_SEAT") or os.environ.get("AGENT_SEAT") or "").strip().upper()
    if not seat:
        print("REFUSED: no seat. Pass --seat or set RIMFLOW_SEAT; a guessed seat shows another seat's items.",
              file=sys.stderr)
        return 2
    if a.print:
        sys.stdout.write(build(seat))
    else:
        print(write(seat))
    return 0


if __name__ == "__main__":
    sys.exit(main())
