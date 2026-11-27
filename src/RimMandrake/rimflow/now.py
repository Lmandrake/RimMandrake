#!/usr/bin/env python3
"""now.py: one screen of state in place of the poll round (`./now`; item RIMMANDRAKE_BUILD_NOW_SCREEN_935_POLLS_IN_A_WEEK).

WHY. In the 7 days to 2026-11-26 the Conductor windows made 935 state polls (`detached_helper.py status` 319,
`./pipe why` 263, `./pipe show` 227, queue/next, `game_lock query`, accounts): model time 77.9 min, wall 6.2 h
(design/specs/2026-11-26-script-candidates/one_page.md, candidate 2).

WHAT. One command prints, each line stamped with the local Pacific time of its reading:
  * locks, pipe, accounts: the readers of the run-end wake (`run_end_wake.default_readers`);
  * runs: each detached run whose record is launching or running, with its age (a unit that is gone reads DEAD);
  * queue: the head of the Conductor's queue (seat BENCH), in `priority.rank()` order, read from the ledger only.
A reader that raises, returns None or does not answer before the deadline reads COULD NOT LOOK with its name and cause;
an empty answer reads none (looked) (`run_end_wake.state_block`). It only prints: it reserves no lease (`rimflow next`
does), renders no view and writes no file. Page: design/specs/2026-11-27-now/boundary.md.

    ./now
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (HERE, os.path.dirname(HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import run_end_wake as W  # noqa: E402

SEAT = "BENCH"
TITLE_N = 100            # a cut of a shown title; it says so and names `rimflow show <ID>`, which prints it whole
QUEUE_HEAD_N = 5          # a cut of what is shown; the rest is counted, with the command that lists it whole
# budget: danger=a hung reader (a ledger load on a stuck disk, a remote run's ssh) holds the screen with no end;
# budget: measured need 3.7 s (the ledger load, the slowest reader, SteveDesktop 2026-11-27 10:58 AM PST); 12x it
DEADLINE_S = 45


def _age(seconds):
    m = max(0, seconds) / 60.0
    return "%d min" % m if m < 120 else "%.1f h" % (m / 60.0)


def live_runs(records=None, status=None, now=None):
    """-> one line per detached run whose record reads launching or running: unit, item, model, state and age. A run
    whose unit is gone (finish never ran) reads DEAD. [] when none is live (the screen reads it none (looked)).
    An OSError when the record folder cannot be listed: could not look is never "no runs"."""
    import detached_helper as DH
    records = records or DH.all_records
    status = status or DH.live_status
    now = now or time.time()
    out = []
    for rec in records():
        if rec.get("status") not in ("launching", "running"):
            continue
        st = status(rec)
        word = "DEAD (finish never ran: detached_helper.py finish --unit %s)" % rec["unit"] if st == "dead" else st
        where = " on %s" % rec["host"] if rec.get("host") else ""
        out.append("%s  item %s  %s  %s%s  %s" % (rec["unit"], rec.get("item"), rec.get("model"), word, where,
                                                  _age(now - (rec.get("at") or now))))
    return out


def _load():
    from rimflow import cli
    return cli.load()


def _rank(world, seat):
    from rimflow import priority
    return priority.rank(world, seat, "v1", {})


def queue_head(load=None, rank=None, n=QUEUE_HEAD_N, seat=SEAT):
    """-> the first `n` items of the seat's queue in `priority.rank()` order (id, state, title), and one line that counts
    the rest with the command that lists them. [] when the queue is empty. Reads the ledger only."""
    _, world = (load or _load)()
    ranked = list((rank or _rank)(world, seat))
    import fulltext
    out = ["%s  %s  %s" % (i.id, i.state, fulltext.clip(" ".join((i.title or "").split()), TITLE_N,
                                                        "rimflow show %s" % i.id)) for i in ranked[:n]]
    if len(ranked) > n:
        out.append("... %d more (python3 src/RimMandrake/rimflow/cli.py queue %s lists them)" % (len(ranked) - n, seat))
    return out


def readers():
    """-> the readers of the screen, in print order."""
    r = dict(W.default_readers())
    r["runs"] = live_runs
    r["queue"] = queue_head
    return r


def screen(rs=None, now=None, deadline_s=DEADLINE_S):
    return W.state_block(readers() if rs is None else rs, now=now, deadline_s=deadline_s)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] in ("-h", "--help"):
        print(__doc__.strip())
        return 0
    print(screen())
    sys.stdout.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
