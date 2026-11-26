#!/usr/bin/env python3
"""mod_park.py: an item that a run gave to its mod is parked on that mod, by a program, with no hand.

Item RIMMANDRAKE_PARK_ITEM_GIVEN_TO_MOD_TWO_WAKES_OWED_A_HAND. Why: 2026-11-25 8:26 PM and 8:28 PM PST, two Shape runs of
the lane's age line (list_dispatch.py) gave a stale-blocked item to its mod (`rimflow home --home mod:<Mod>`) and stopped,
because one mod's work waits for that mod's Maturation Pipeline run (CLAUDE.md §Mods keep their own state). Each left
the item in state `doing`, so the run-end wake printed `OWED:` and the Conductor window wrote the `LEFT OPEN:` note and
the wait by hand, twice. The route is any run that writes a `home mod:<Mod>` event and ends with the item still open,
so the fix is at the run's end (detached_helper.finish), not in one brief.

  plan(...)   pure: which of note / wait / reclaim an open item still needs to be parked on its mod
  park(...)   runs those steps as the program (RM_FILING_PROGRAM), in the run's clone; -> step lines
  sweep       `mod_park.py sweep [--apply]`: every open `doing` item with a mod home (dry run unless --apply)

After a park: a note that starts `LEFT OPEN:`, a dated wait that names the mod and its Design Version, and the item
in state `ready` (reclaim: the wait stays). The wait is not the Conductor's: its reason names the mod's pipeline.
"""
import argparse
import datetime
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
LEFT_OPEN = "LEFT OPEN:"
PROGRAM = "mod_park"
# The wait must lie ahead (cmd_wait refuses a past date). 14 days is the Conductor's own hand choice of 2026-11-25
# (wait until 2026-12-09 on both items). Danger guarded: a date too near re-offers the item to the lane before its mod's
# run; the lane's age line then sends a Shape run that parks it again, so a short date costs one run, not a loss.
WAIT_DAYS = 14
CLI_TIMEOUT_S = 300     # hang guard of one rimflow write; the longest measured write is about 5 s (cmd_home's comment)


def mod_of(home):
    """-> <Mod> from a home record {home: "mod:<Mod>", ...}, or None (no home, another kind, unreadable)."""
    h = home.get("home") if isinstance(home, dict) else None
    if isinstance(h, str) and h.startswith("mod:") and h[4:].strip():
        return h[4:].strip()
    return None


def _epoch(ts):
    try:
        return datetime.datetime.fromisoformat(str(ts).replace("Z", "+00:00")).timestamp()
    except (TypeError, ValueError):
        return None


def left_open_since(notes, item, since):
    """True when a note on `item` written at or after `since` starts LEFT OPEN: (a note with no readable time is no excuse)."""
    for e in notes or []:
        t = _epoch(e.get("ts")) if isinstance(e, dict) else None
        if (t is not None and t >= since and e.get("id") == item and e.get("event") == "note"
                and str(e.get("text") or "").strip().upper().startswith(LEFT_OPEN)):
            return True
    return False


def plan(item, state, home, wait_until, notes, since, now):
    """-> (steps, why). steps: the subset of ["note", "wait", "reclaim"] still needed, in order; why: words when it is
    empty. A home written before `since` is an older act, not this run's. Pure over its inputs."""
    mod = mod_of(home)
    if mod is None:
        return [], "no mod home"
    at = _epoch(home.get("at"))
    if at is None:
        return [], "its home has no readable time: could not look"
    if since is not None and at < since:
        return [], "its mod home is older than this run"
    if state not in ("ready", "doing"):
        return [], "it is %s: only ready or doing work waits" % state
    waiting = _epoch(wait_until) is not None and _epoch(wait_until) > now
    steps = []
    if not left_open_since(notes, item, at):
        steps.append("note")
    if not waiting:
        steps.append("wait")
    if state == "doing":
        steps.append("reclaim")
    return steps, "" if steps else "already parked"


def version_line(mod, repo=REPO):
    """-> "Design Version X (state)" from design/concepts/<Mod>/version/VERSION.json, or "Design Version UNMEASURED (cause)"."""
    p = os.path.join(repo, "design", "concepts", mod, "version", "VERSION.json")
    try:
        with open(p, encoding="utf-8") as f:
            v = json.load(f)
        return "Design Version %s (%s)" % (v["version"], v.get("state") or "state not recorded")
    except (OSError, ValueError, KeyError, TypeError) as e:
        return "Design Version UNMEASURED (%s: %s)" % (type(e).__name__, e)


def _one(s, n):
    s = re.sub(r"\s+", " ", str(s or "")).strip()
    return s if len(s) <= n else s[:n - 1] + "…"


def texts(item, mod, home, vline, who):
    """-> (note text, wait reason): the words, one place."""
    note = ("%s %s is the work of mod %s (%s; home %s, group %s): %s. Next act: the Maturation Pipeline run of %s takes "
            "it; nothing is left for the lane. Parked by mod_park.py at the end of %s."
            % (LEFT_OPEN, item, mod, vline, home.get("home"), home.get("group") or "-", _one(home.get("reason"), 300),
               mod, who))
    reason = ("until the Maturation Pipeline works mod %s (%s); the item is that mod's work, and the pipeline takes it then"
              % (mod, vline))
    return note, reason


def park(clone, seat, item, steps, mod, home, who, vline=None, runner=subprocess.run, now=None):
    """Run `steps` (from plan) as the program, in `clone`. -> [one line per step]. A step that fails is said, and the
    steps after it still run (a note without its wait is still better than neither)."""
    vline = vline or version_line(mod, clone)
    note, reason = texts(item, mod, home, vline, who)
    until = datetime.datetime.fromtimestamp((now or time.time()) + WAIT_DAYS * 86400, datetime.timezone.utc).strftime("%Y-%m-%d")
    cli = os.path.join(clone, "src", "RimMandrake", "rimflow", "cli.py")
    why = "a run gave the item to mod %s: parked by mod_park.py" % mod
    argvs = {"wait": ["wait", item, "--until", until, "--reason", reason],
             "note": ["note", item, "--text", note],
             "reclaim": ["reclaim", item, "--reason", why]}
    out = []
    for s in steps:
        try:
            r = runner([sys.executable, cli] + argvs[s] + ["--seat", seat, "--why", why], cwd=clone, capture_output=True,
                       text=True, timeout=CLI_TIMEOUT_S, stdin=subprocess.DEVNULL,
                       env=dict(os.environ, RM_FILING_PROGRAM="detached_helper." + PROGRAM))   # filing_gate.py: a program
        except (OSError, subprocess.SubprocessError) as e:
            out.append("%s FAILED (%s: %s)" % (s, type(e).__name__, e))
            continue
        out.append(s + (" ok" if not r.returncode else " FAILED (exit %d: %s)" % (
            r.returncode, _one((r.stderr or "") + (r.stdout or ""), 300))))
    return out


def sweep(apply=False, repo=REPO, seat_of=None):
    """Every open item in `doing` with a mod home. -> [(item, mod, steps, lines)]; writes only with apply. A `doing`
    item with a running detached unit of its own is skipped (its run ends by itself, and finish parks it)."""
    sys.path.insert(0, HERE)
    import model
    evs = model.read()
    w = model.replay(evs)
    live = running_items()
    rows = []
    for iid, it in sorted(w.items.items()):
        mod = mod_of(it.home)
        if it.state != "doing" or mod is None:
            continue
        if iid in live:
            rows.append((iid, mod, [], ["skipped: a detached run of it is live"]))
            continue
        if it.owner != "BENCH":      # only the owning seat reclaims (cli refuses): a half park would leave a wait and no reclaim
            rows.append((iid, mod, [], ["skipped: owned by seat %s, which alone may reclaim it" % it.owner]))
            continue
        notes = [e for e in evs if e.get("id") == iid and e.get("event") == "note"]
        steps, why = plan(iid, it.state, it.home, it.wait_until, notes, None, time.time())
        # a hand-parked item (wait + note present) still needs the reclaim: plan says so, it keeps `doing` out
        lines = [why] if not steps else []
        if steps and apply:
            lines = park(repo, (seat_of or (lambda i: "BENCH"))(it), iid, steps, mod, it.home, "the sweep of mod_park.py")
        rows.append((iid, mod, steps, lines))
    return rows


def running_items():
    """-> the set of items with a live detached unit, read from the unit records; raises when they cannot be read."""
    import detached_helper as DH
    out = set()
    for rec in DH.all_records():
        if rec.get("status") == "running" and rec.get("item"):
            out.add(rec["item"])
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sweep", help="park every open `doing` item that has a mod home (dry run unless --apply)")
    s.add_argument("--apply", action="store_true")
    args = ap.parse_args(argv)
    rows = sweep(args.apply)
    for iid, mod, steps, lines in rows:
        print("%s mod:%s needs %s%s" % (iid, mod, ",".join(steps) or "nothing", " | " + "; ".join(lines) if lines else ""))
    print("%d item(s) in doing with a mod home; %d need parking" % (len(rows), sum(1 for r in rows if r[2])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
