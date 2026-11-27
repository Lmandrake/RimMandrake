#!/usr/bin/env python3
"""conductor_stops.py: the stops that no program ends, for the Conductor first. No model, no tokens.

Page design/specs/2026-11-26-conductor-stops/boundary.md; selftest selftest_conductor_stops.py. Item
RIMMANDRAKE_BUILD_STUCK_STOP_REPAIRS_HE_RULED_SIX, parts 1, 3 and 4. His words, 2026-11-26: "The conductor is always told
1st. It decides if owner is needed or conductor can do it itself." and "Conductor sorts after 1 hour."

    python3 src/RimMandrake/rimflow/conductor_stops.py show                       the rows (also on `rimflow queue CONDUCTOR --owed`)
    python3 src/RimMandrake/rimflow/conductor_stops.py sort <ID> --to lane --why "..."   a small fix of a passed mod: the ticket lane works it
    python3 src/RimMandrake/rimflow/conductor_stops.py sort <ID> --to next --why "..."   the mod's next-version list

The Conductor ends a lane stop by its own act: route the ticket to the owner (then his page shows it), `list_dispatch.py
clear <ID>` for one more run, a dated wait, or a drop. A resting mod's tickets are sorted with `sort`. The next version
still opens only on his answer to its scope page.
"""
import argparse
import datetime as dt
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for _p in (HERE, os.path.join(REPO, "src", "RimMandrake", "Utils"), os.path.join(REPO, "src", "RimMandrake")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

CONCEPTS = os.path.join(REPO, "design", "concepts")
KINDS = {"chain_stop": "at the chain limit: list_dispatch.py clear <ID> for one more run, route it, or drop it",
         "stopped": "a run ended with no next act: list_dispatch.py clear <ID>, route it, or drop it",
         "no_bundle": "the host's sort left it out of its work bundle: act on the host's reason in its row, or drop it",
         "adopt_too_heavy": "its check is too heavy to attach: `rimflow shape <ID> --enter` for a lighter check",
         "close_refused": "its check holds and the close was refused: the reason names the cause and its repair"}
# His words (2026-11-26): "Conductor sorts after 1 hour." A clock, not a limit: it ends no work. Danger without it: a
# passed mod rests and its tickets wait for a run that never comes (Gimme Some Slack: 3 tickets, 45 h).
REST_S = 3600
# Danger: a lane tick that stopped would show its old stops as now. Evidence: ticks.jsonl, 471 ticks in 81 h to
# 2026-11-26, no gap over 1.5 h; three hours is twice the longest gap.
READING_STALE_S = 3 * 3600  # budget: danger=a stopped tick's stops shown as now; ends no work: a view's freshness
SORTED = "tickets.md"
SORT_CMD = "conductor_stops.py sort <ID> --to lane|next --why \"...\""


OWN = "; its own: "     # list_dispatch.launch_bundle_row: a lead row the host left out ends with the host's reason
WHY_CUT = 160


def _why(why):
    """-> the row's reason for a view line, at most WHY_CUT characters before the host's own reason. That reason stays
    whole (the host bounds it at 200): the no_bundle hint sends the Conductor to it."""
    s = str(why or "")
    head, sep, own = s.partition(OWN)
    return head[:WHY_CUT] + sep + own  # cut-ok: a view line; the whole reason stays in reading.json


def _age(t, now):
    if not isinstance(t, (int, float)):
        return "age?"
    s = max(0, now - t)
    if s < 3600:
        return "%dm" % (s // 60)
    if s < 86400 * 2:
        return "%dh%02d" % (s // 3600, (s % 3600) // 60)
    return "%dd" % (s // 86400)


def _epoch(v):
    """ISO time -> epoch; raises ValueError on a time that cannot be read."""
    t = dt.datetime.fromisoformat(str(v).replace("Z", "+00:00"))
    return (t if t.tzinfo else t.replace(tzinfo=dt.timezone.utc)).timestamp()


def rests(root=CONCEPTS):
    """-> {mod folder: epoch since it passed} for each concept whose stage_record reads stage passed."""
    out = {}
    try:
        names = os.listdir(root)
    except OSError:
        return out
    for n in names:
        try:
            with open(os.path.join(root, n, "version", "stage_record.json"), encoding="utf-8") as f:
                r = json.load(f)
        except (OSError, ValueError):
            continue
        if isinstance(r, dict) and r.get("stage") == "passed":
            try:
                out[n] = _epoch(r.get("since"))
            except ValueError:
                out[n] = None       # it rests, its start unread: rows lists it with age "age?", never drops it
    return out


def sorted_path(root, mod):
    return os.path.join(root, mod, "version", "next_version", SORTED)


def sorted_ids(root, mod):
    """-> the ticket ids on the mod's next-version list, in file order ([] when the file does not exist). A file that
    exists and cannot be read raises: load() then says could not look."""
    if not os.path.exists(sorted_path(root, mod)):
        return []
    with open(sorted_path(root, mod), encoding="utf-8") as f:
        text = f.read()
    out = []
    for ln in text.splitlines():
        ln = ln.strip()
        if ln.startswith("- "):
            iid = ln[2:].split(":", 1)[0].strip().strip("`")
            if iid and iid not in out:
                out.append(iid)
    return out


def rows(rd, now, rests=None, sorted_of=None):
    """-> [{"kind", "items", "mod", "why", "age", "_t"}], oldest first. Pure over its inputs.
    rd: the lane reading; rests: {mod: epoch}; sorted_of: mod -> ids already on its next-version list."""
    rests = rests or {}
    sorted_of = sorted_of or (lambda m: [])
    out, by_mod = [], {}
    for iid, r in sorted(((rd or {}).get("items") or {}).items()):
        d = (r or {}).get("decision")
        if d in KINDS:
            t = r.get("since")
            out.append({"kind": d, "items": [iid], "mod": None, "why": "%s; %s" % (_why(r.get("why")), KINDS[d]),
                        "age": _age(t, now), "_t": t if isinstance(t, (int, float)) else 9e18})
        elif d == "mod_work" and r.get("mod"):
            wu = r.get("wait_until")
            if isinstance(wu, (int, float)) and wu > now:
                continue                    # its own dated wait stands (the Explosive Knockback hunt has one)
            by_mod.setdefault(r["mod"], []).append(iid)
    for mod, ids in sorted(by_mod.items()):
        t = rests.get(mod)
        if mod not in rests or (isinstance(t, (int, float)) and now - t < REST_S):
            continue                    # not resting, or rested less than an hour; an unread start is listed
        done = set(sorted_of(mod))
        ids = [i for i in ids if i not in done]
        if ids:
            out.append({"kind": "mod_rest", "items": ids, "mod": mod, "age": _age(t, now),
                        "_t": t if isinstance(t, (int, float)) else 9e18,
                        "why": "%s rests since its pass, and %d ticket%s wait%s for a run that does not come: %s"
                               % (mod, len(ids), "" if len(ids) == 1 else "s", "s" if len(ids) == 1 else "", SORT_CMD)})
    out.sort(key=lambda r: (r["_t"], r["items"][0]))
    return out


def reading_path():
    d = os.environ.get("RM_LIST_DISPATCH_DIR")
    if not d:
        import doorbell
        d = os.path.join(doorbell.state_dir(), "list_dispatch")
    return os.path.join(d, "reading.json")


def from_reading(rd, now, rests=None, sorted_of=None):
    """-> (rows, None), or (None, cause) when the reading is missing or older than READING_STALE_S."""
    if not isinstance(rd, dict) or not isinstance(rd.get("at"), (int, float)):
        return None, "could not look: no lane reading"
    if now - rd["at"] > READING_STALE_S:
        return None, "could not look: the lane reading is %d min old" % ((now - rd["at"]) // 60)
    return rows(rd, now, rests, sorted_of), None


def load(now=None, root=CONCEPTS):
    """The live rows for the owed view: (rows, None) or (None, cause). Never raises."""
    now = time.time() if now is None else now
    try:
        with open(reading_path(), encoding="utf-8") as f:
            rd = json.load(f)
    except (OSError, ValueError) as e:
        return None, "could not look: the lane reading could not be read (%s)" % type(e).__name__
    try:
        return from_reading(rd, now, rests(root), lambda m: sorted_ids(root, m))
    except Exception as e:      # noqa: BLE001 - a view must not fail its caller
        return None, "could not look: %s: %s" % (type(e).__name__, e)


def asks(evs, world, now=None):
    """-> (the lane asks to him that nobody has read against now, None) or (None, cause). Never raises."""
    try:
        import owner_queue as OQ
        n = OQ.needs_you(world.items, {}, {}, evs, now=now)
        return n.get("unvetted") or [], None
    except Exception as e:      # noqa: BLE001
        return None, "could not look: %s: %s" % (type(e).__name__, e)


# A hang guard, never a speed bar: a publish waited 30 minutes in the door's line on 2026-11-26
# (RIMMANDRAKE_UNJAM_PUBLISH_DOOR_LEDGER_WAITED_THIRTY_MINUTES); 10 times that is 5 h.
# budget: danger=a publish that never returns holds the Conductor's sort; evidence=a publish waited 30 min in the line
# budget: on 2026-11-26; longest=1800s (RIMMANDRAKE_UNJAM_PUBLISH_DOOR_LEDGER_WAITED_THIRTY_MINUTES)
PUBLISH_DEADLINE_S = 6 * 3600


def _publish(argv):
    try:
        return subprocess.run(argv, cwd=REPO, timeout=PUBLISH_DEADLINE_S).returncode
    except subprocess.TimeoutExpired:
        print("UNMEASURED: %s did not end inside the %d s hang guard" % (argv[0], PUBLISH_DEADLINE_S))
        return 3


def sort(iid, to, why, item=None, mod=None, root=CONCEPTS, runner=None, rests_of=None):
    """The Conductor's sort of a resting mod's ticket. -> (rc, line). to: lane | next."""
    runner = runner or _publish
    rs = rests(root) if rests_of is None else rests_of
    if mod not in rs:
        return 2, "refused: %s is not a mod that rests after its pass (rests now: %s); nothing changed" % (
            mod, ", ".join(sorted(rs)) or "none")
    if not why or not why.strip():
        return 2, "refused: give --why (the call and its reason); nothing changed"
    if to == "lane":
        argv = [sys.executable, os.path.join(HERE, "cli.py"), "home", iid, "--home", "fix:%s" % mod,
                "--group", "passed-correction", "--flag", "LOOKS CURRENT",
                "--reason", "a correction of %s's passed version that moves no bar: %s" % (mod, why),
                "--seat", "BENCH", "--per-ruling", "RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS",
                "--why", "conductor sort of a resting mod's ticket: %s" % why, "--publish"]
        rc = runner(argv)
        return rc, "%s: home fix:%s, the ticket lane works it (rc %s)" % (iid, mod, rc)
    if to == "next":
        p = sorted_path(root, mod)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        if iid not in sorted_ids(root, mod):
            new = not os.path.exists(p)
            with open(p, "a", encoding="utf-8") as f:
                if new:
                    f.write("# Tickets the Conductor sorted to %s's next version\n\nThe version opens only on the "
                            "owner's answer to its scope page.\n\n" % mod)
                f.write("- %s: %s\n" % (iid, " ".join(why.split())))
        rel = os.path.relpath(p, REPO)
        rc = runner(["./publish", "-m", "RIMMANDRAKE_BUILD_STUCK_STOP_REPAIRS_HE_RULED_SIX: %s sorted to %s's next "
                     "version" % (iid, mod), rel])
        return rc, "%s: on %s (rc %s)" % (iid, rel, rc)
    return 2, "refused: --to is lane or next; nothing changed"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("show")
    s = sub.add_parser("sort")
    s.add_argument("id")
    s.add_argument("--to", required=True, choices=("lane", "next"))
    s.add_argument("--why", required=True)
    a = ap.parse_args(argv)
    if a.cmd == "show":
        got, cause = load()
        if got is None:
            print(cause)
            return 2
        for r in got:
            print("%-7s %-15s %s  %s" % (r["age"], r["kind"], ",".join(r["items"]), r["why"]))
        print("%d stop row(s)" % len(got) if got else "[] no stop that only the Conductor ends")
        return 0
    import mod_work as MW
    import fleet_mods
    _, w = fleet_mods.ledger()
    it = w.items.get(a.id)
    if it is None or not it.open:
        print("refused: %s is not an open ticket; nothing changed" % a.id)
        return 2
    mod = MW.reading(it, MW.mods()).get("mod")
    rc, line = sort(a.id, a.to, a.why, item=it, mod=mod)
    print(line)
    return rc


if __name__ == "__main__":
    sys.exit(main())
