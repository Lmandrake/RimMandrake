#!/usr/bin/env python3
"""GIT_DARK_FIX_STALL_ITEM_STILL_HELD: BRIDGE_STALL_DIAGNOSTIC_1 stayed held on git reach after
CHECKER_REACH_FIX_GIT_DARK_SECOND closed. Its Judge went looking for git history in the D: mirror and wrote the mirror
ROOT into its blind text ("no .git in the export; mirror.git not a repo; /mnt/d/Luke/dev/RimMandrake permission
denied"). The git_history grant covered only <mirror>/.git, so uncovered() kept the root as a gap and the sweep filed a
successor instead of releasing it. The mirror is a .git-less export of one origin/main commit (MIRROR_HEAD): what
that Judge sought there was history, which the git_history grant gives at the candidate, so git_history now covers the root exactly, and nothing under it but its .git (a seat clone root is
seat_clone_state's, through fill(), not the grant's).
Rows: (a) the pre-fix regex leaves the root uncovered (the instance is seen); (b) BRIDGE_STALL's verbatim stored
proposal and blind text, put through sweep() as the owner of a closed git ticket, comes out reach_repaired with no
successor; (c) a blind on a mirror CHILD (Transient: untracked, not history) still gets a successor; (d) an
item blind on a Relentless transcript and ~/.ssh is still not released; (e) the grant names no mirror child."""
import json
import os
import re
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless_reachfix as RF  # noqa: E402

FAILS = []
TICKET = "CHECKER_REACH_FIX_GIT_DARK_SECOND"
MIRROR = "/mnt/d/Luke/dev/RimMandrake"
OLD_RX = ("^((/mnt/d/Luke/dev/RimMandrake|/home/mandrake/rm/(bench|foundry|dispatch)|/home/mandrake/rm/scratch/[^/]+/"
          "[^/]+|/home/mandrake/rm/relentless/(books|clones/[^/]+))/\\.git|/home/mandrake/rm/store\\.git)"
          "(/objects(/.*)?)?/?$")
# verbatim from the live store, 2026-11-06 (items/BRIDGE_STALL_DIAGNOSTIC_1/state.json)
STALL = {"reach": {"class": "git", "proposal": {"adapters": ["git_log_candidate", "git_origin_main"], "by": "judge",
                                                 "grants": ["git_history"], "paths": [], "refused": {}}},
         "blind": {"what": "git object 472474378b^ (JawaBenchStallProbe.cs, JawaBenchTpsProfiler.cs) for the "
                           "whole-commit-revert mutant: no .git in the export; mirror.git not a repo; "
                           "/mnt/d/Luke/dev/RimMandrake permission denied; the live A1 round on the running game "
                           "(needs bridge, deployed companion)"}}


def ok(cond, name):
    print(("ok   " if cond else "FAIL ") + name)
    if not cond:
        FAILS.append(name)


class Lock:
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class Store:
    def __init__(self, states):
        self.root = tempfile.mkdtemp(prefix="st_reach_mirror_")
        self.states_ = {k: json.loads(json.dumps(v)) for k, v in states.items()}

    def p(self, name):
        return os.path.join(self.root, name)

    def lock(self):
        return Lock()

    def load(self, item):
        st = self.states_.get(item)
        return json.loads(json.dumps(st)) if st else None

    def save(self, st):
        self.states_[st["item"]] = json.loads(json.dumps(st))

    def states(self):
        return [json.loads(json.dumps(s)) for s in self.states_.values()]

    def attempt(self, item, rec):
        pass

    def journal(self, rec):
        pass


class Fx:
    books = "/books"

    def item_state(self, item):
        return {"state": "done", "closed_sha": "0" * 40, "event": "close"}

    def reach_probe(self, r, paths, adapters, values, store_root, grants=()):
        return True, "fake probe: reads"       # only the supervisor's coverage verdict is judged here

    def __getattr__(self, name):
        return lambda *a, **k: None


def rules(rx=None):
    with open(os.path.join(HERE, "relentless_rules.json"), encoding="utf-8") as f:
        r = json.load(f)
    if rx is not None:
        r["grant_covers"] = dict(r["grant_covers"], git_history=rx)
    return r


def run_one(item, st, r):
    s = {"item": item, "status": "blocked", "gen": 1,
         "wait": {"kind": RF.WAIT, "class": "git", "on": TICKET, "attributed_at": 1.0},
         "reach": dict(st["reach"], status="ticket", sha="ec3e5f1482867d7ef44509d570473d6eb10e4cdf"),
         "blind": dict(st["blind"], said="UNMEASURED", n=1),
         "candidate": {"sha": "ec3e5f1482867d7ef44509d570473d6eb10e4cdf"}}
    store = Store({item: s})
    RF.save(store, {"git": {"owner": item, "status": "ticket", "ticket": TICKET, "ticket_at": 1.0, "since": 1.0,
                            "waiters": [], "why": "selftest",
                            "successors": [{"ticket": TICKET, "after": "CHECKER_REACH_BUILD_GIT_AND_GH_ADAPTERS",
                                            "at": 1.0}]}})
    acts = []
    RF.sweep(store, Fx(), r, time.time(), acts, lambda t: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t)))
    dos = [a.get("do") for a in acts]
    return "reach_repaired" in dos and not any(d in ("reach_successor", "reach_ticket_failed") for d in dos), dos


def main():
    r = rules()
    ok(RF.on(r), "precondition: reach_repair is on in relentless_rules.json")
    texts = [STALL["blind"]["what"]]
    old = RF.uncovered(rules(OLD_RX), RF.refreshed(rules(OLD_RX), dict(STALL, item="X")), texts)
    ok(old == [MIRROR], "(a) the pre-fix regex leaves the mirror root uncovered: %s" % old)
    released, dos = run_one("BRIDGE_STALL_DIAGNOSTIC_1", STALL, r)
    ok(released, "(b) BRIDGE_STALL_DIAGNOSTIC_1 is released (reach_repaired), no successor: %s" % dos)
    kid = {"reach": STALL["reach"],
           "blind": {"what": "/mnt/d/Luke/dev/RimMandrake/Transient needed by the proof (ls: Permission denied)"}}
    released, dos = run_one("CONTROL_MIRROR_CHILD", kid, r)
    ok(not released, "(c) a mirror child (untracked Transient, not history) is still not released: %s" % dos)
    dark = {"reach": {"class": "git", "proposal": {"adapters": ["git_log_candidate"], "by": "judge", "paths": [],
                                                    "refused": {}}},
            "blind": {"what": "/home/mandrake/rm/relentless/transcripts/RUNX/session.jsonl needed by the proof "
                              "(ls: Permission denied); /home/mandrake/.ssh/id_ed25519 needed by a git push case "
                              "(Permission denied); git rev-parse HEAD: not a git repository"}}
    released, dos = run_one("CONTROL_DARK", dark, r)
    ok(not released, "(d) an item blind on a transcript and ~/.ssh is still not released: %s" % dos)
    rx = r["grant_covers"]["git_history"]
    kids = [p for p in (MIRROR + "/src", MIRROR + "/infrastructure/state", MIRROR + "X", MIRROR + "/.git/config")
            if re.search(rx, p)]
    ok(re.search(rx, MIRROR) and re.search(rx, MIRROR + "/.git/objects/ab") and not kids,
       "(e) git_history covers the mirror root and its .git objects, no mirror child: %s" % kids)
    print("RESULT: %s" % ("GREEN" if not FAILS else "RED %d: %s" % (len(FAILS), ", ".join(FAILS))))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
