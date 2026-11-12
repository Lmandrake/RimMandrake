#!/usr/bin/env python3
"""selftest_whittle_now.py: plant Whittle workers with known faults and see the page say each one in plain words.

A temp folder holds three workers: one stuck on an item (three rounds, four failed ledger runs, a question for the
owner), one that claims a close the ledger does not have and whose unit lives on an unreachable SteveDesktop, and
one with a broken worker.json sitting exactly on the stuck boundary (two rounds, three failed runs), which must NOT
be called stuck. An empty folder must give "no workers yet". systemd, ssh, the ledger, the machines and the
accounts are stubbed; nothing outside the temp folder is read or written. Then two mutants of whittle_now.py (the
stuck boundary moved, unreachable read as stopped) must each turn a check red.
"""

import json
import os
import shutil
import sys
import tempfile
import time
import types

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE_PATH = os.path.join(HERE, "whittle_now.py")
SOURCE = open(SOURCE_PATH, encoding="utf-8").read()
sys.path.insert(0, HERE)


def load(source):
    mod = types.ModuleType("whittle_now_under_test")
    mod.__file__ = SOURCE_PATH
    exec(compile(source, SOURCE_PATH, "exec"), mod.__dict__)
    return mod


def stamp(ago_min):
    return time.strftime("%Y-%m-%d %H:%M", time.localtime(time.time() - ago_min * 60))


def iso(ago_min):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - ago_min * 60))


class Run:
    def __init__(self, result):
        self.result, self.ts, self.sha = result, iso(5), None


class Item:
    def __init__(self, iid, title, state, runs=(), done_index=None, sha=None):
        self.id, self.title, self.state = iid, title, state
        self.open = state not in ("done", "dropped", "superseded")
        self.runs = [Run(r) for r in runs]
        self.done_index, self.closed_sha = done_index, sha
        self.lease, self.needs, self.blocked, self.superseded_by = None, None, False, None


class World:
    pass


def fake_ledger(sources):
    evs = [{"ts": iso(40)}]
    w = World()
    w.items = {i.id: i for i in (
        Item("RM_STUCK_ITEM_ONE", "Make the stuck thing work", "doing", runs=("fail", "fail", "fail", "fail")),
        Item("RM_DONE_ITEM_ONE", "A thing really closed", "done", done_index=0, sha="abc1234"),
        Item("RM_CLAIM_ITEM_ONE", "A thing only claimed", "built"),
        Item("RM_EDGE_ITEM_TWO", "On the boundary", "doing", runs=("pass", "fail", "fail", "fail")),
        Item("RM_FWLIVE_LANE_ONE", "A lane item", "ready"),
    )}
    w.bridge_hosts = {"archmagi": {"holder": None, "since": iso(90)}}
    return evs, w


def plant(root):
    def worker(name, wj, log, progress=None, questions=None, raw_wj=None):
        d = os.path.join(root, name)
        os.makedirs(d)
        with open(os.path.join(d, "worker.json"), "w") as f:
            f.write(raw_wj if raw_wj is not None else json.dumps(wj))
        with open(os.path.join(d, "loop.log"), "w") as f:
            f.write("\n".join(log) + "\n")
        if progress:
            open(os.path.join(d, "progress.md"), "w").write(progress)
        if questions:
            open(os.path.join(d, "OWNER_QUESTIONS.md"), "w").write(questions)

    worker("stuckone", {"worker": "stuckone", "unit": "rm-whittle-stuckone", "machine": "Archmagi", "lane": "fwlive",
                        "game": "Archmagi RimWorld", "item": "RM_STUCK_ITEM_ONE", "item_started_at": iso(50),
                        "round": 3, "state": "working", "note": "trying the third way"},
           ["%s round 1 start, open=9 item=RM_STUCK_ITEM_ONE" % stamp(50),
            "%s round 1 end: RM_STUCK_ITEM_ONE parked sha=- tokens=200k" % stamp(40),
            "%s round 2 start, open=9 item=RM_STUCK_ITEM_ONE" % stamp(39),
            "%s round 2 end: RM_STUCK_ITEM_ONE parked tokens=150000" % stamp(30),
            "%s round 3 start, open=9 item=RM_STUCK_ITEM_ONE" % stamp(29)],
           progress="# Progress\n\n## Step one\nTried the obvious fix.\n",
           questions="# Questions\n\n## Which pipe should win?\nThe north pipe or the south pipe, and why it matters.\n")
    worker("closer", {"worker": "closer", "unit": "rm-whittle-closer.service", "machine": "SteveDesktop",
                      "lane": "offline", "item": None, "round": 4, "state": "working"},
           ["%s round 1 start, open=5 item=RM_DONE_ITEM_ONE" % stamp(48),
            "%s round 1 end: RM_DONE_ITEM_ONE closed sha=abc1234 tokens=1.2M" % stamp(41),
            "[%s:07] round #2 started open=4 item=RM_CLAIM_ITEM_ONE" % stamp(38),
            "%s round 2 end: RM_CLAIM_ITEM_ONE closed sha=def5678 tokens=300k" % stamp(25),
            "%s note: drained the easy ones" % stamp(24),
            "%s round 3 start, open=4 item=RM_DONE_ITEM_ONE" % stamp(23),
            "%s round 3 end: RM_DONE_ITEM_ONE released sha=- tokens=5k" % stamp(22),
            "%s round 4 start, open=4 item=RM_DONE_ITEM_ONE" % stamp(21),
            "%s round 4 end: RM_DONE_ITEM_ONE wobbled sha=- tokens=5k" % stamp(20),
            "garbage line without a stamp"])
    worker("edgy", None, ["%s round 1 start, open=3 item=RM_EDGE_ITEM_TWO" % stamp(20),
                          "%s round 1 end: RM_EDGE_ITEM_TWO parked tokens=10" % stamp(15),
                          "%s round 2 start, open=3 item=RM_EDGE_ITEM_TWO" % stamp(14)],
           raw_wj="{ this is not json")
    worker("alarmer", {"worker": "alarmer", "unit": "rm-whittle-alarmer", "machine": "Archmagi", "lane": "offline", "state": "working"},
           ["%s round 1 start, open=3 item=RM_EDGE_ITEM_TWO" % stamp(5)],
           questions="# Questions\n\n## 2026-11-11 SteveDesktop WSL root is read-only (not a question; an alarm)\n- mount says emergency_ro.\n\n"
                     "## Which colour should the plant be?\nGreen or red.\n")
    with open(os.path.join(root, "workers.json"), "w") as f:
        json.dump({"workers": [{"worker": "stuckone"}, {"worker": "closer"}, {"worker": "alarmer"}, {"worker": "edgy", "unit": "rm-whittle-edgy",
                                                                               "machine": "Archmagi", "lane": "offline"}]}, f)
    os.makedirs(os.path.join(root, "tools"))


def plant_steve(root):
    for name, stop in (("steveon", None), ("stevestop", "Owner parked this lane until the disk move is done."), ("stevedead", None)):
        d = os.path.join(root, name)
        os.makedirs(d)
        json.dump({"worker": name, "unit": "rm-whittle-" + name, "machine": "SteveDesktop", "lane": "offline", "state": "working"},
                  open(os.path.join(d, "worker.json"), "w"))
        open(os.path.join(d, "loop.log"), "w").write("%s round 1 start, open=3 item=RM_EDGE_ITEM_TWO\n" % stamp(5))
        if stop:
            open(os.path.join(d, "STOP"), "w").write(stop)
    os.makedirs(os.path.join(root, "tools"))


def wire(mod, root, lane_file, steve_up=False):
    mod.ROOT = root
    mod.OUT_DIR = root
    mod.LANE_FILE = lane_file
    mod.ITEMS_DIR = os.path.join(root, "items")
    os.makedirs(mod.ITEMS_DIR, exist_ok=True)
    open(os.path.join(mod.ITEMS_DIR, "RM_FWLIVE_LANE_ONE.md"), "w").write("live\n")

    def local(units):
        return {u: ({"Id": u, "LoadState": "loaded", "ActiveState": "active", "SubState": "running",
                     "ActiveEnterTimestamp": "Wed 2026-11-11 18:00:00 PST"} if "stuckone" in u
                    else {"Id": u, "LoadState": "loaded", "ActiveState": "inactive"} if "edgy" in u
                    else {"Id": u, "LoadState": "not-found", "ActiveState": "inactive"}) for u in units}

    def remote(units):
        if not steve_up:
            raise mod.Unmeasured("ssh: connect timed out")
        return {u: {"Id": u, "LoadState": "loaded", "ActiveState": "active" if "steveon" in u else "inactive"} for u in units}

    mod.units_local, mod.units_remote = local, remote
    return {"ledger": fake_ledger, "machines": lambda state, sources: {},
            "accounts": lambda sources: [{"name": "system", "used": 42.0, "resets": time.time() + 86400, "t": time.time(),
                                          "why": None, "slope": None}],
            "notice": lambda sources: {"account": "steven", "pct_left": 80.0, "line": 30}}


def checks(mod, tmp):
    root = os.path.join(tmp, "w")
    os.makedirs(root)
    lane = os.path.join(tmp, "lane.json")
    json.dump({"seat": "X", "id_patterns": ["^RM_FWLIVE_", "^RM_STUCK_"]}, open(lane, "w"))
    plant(root)
    stubs = wire(mod, root, lane)
    page, phone, _ = mod.build(stubs)
    needs = page.split("## Needs you", 1)[1].split("## Workers at a glance", 1)[0].split("\n## Alarms", 1)[0]
    edge_part = page.split("## edgy", 1)[1] if "## edgy" in page else ""
    near_midnight = time.localtime().tm_hour == 0 and time.localtime().tm_min < 55
    out = [
        ("questions asked in needs", "stuckone asks you 1 question" in needs and "Which pipe should win?" in needs),
        ("question text in full", "The north pipe or the south pipe, and why it matters." in page),
        ("stuck by rounds", "stuckone is stuck on `RM_STUCK_ITEM_ONE` (Make the stuck thing work)**: 3 rounds on it" in needs),
        ("stuck by runs", "has failed 4 ledger runs in a row" in needs),
        ("edge not stuck by rounds", "edgy is stuck" not in needs),
        ("edge not stuck by runs", "RM_EDGE_ITEM_TWO" not in needs),
        ("bad worker.json said", "edgy: worker.json unreadable" in needs),
        ("edge item from log", "`RM_EDGE_ITEM_TWO` (On the boundary)" in edge_part),
        ("unreachable not stopped", "**unreachable**" in page and "closer: stopped" not in page.lower()),
        ("stopped unit said", "`rm-whittle-edgy.service` on Archmagi: **inactive**" in page),
        ("claim not accepted", near_midnight or "closer said it closed `RM_CLAIM_ITEM_ONE`" in needs),
        ("ledger close accepted", "closed in the ledger" in page and "commit abc1234" in page),
        ("closed today split", near_midnight or "2 said, 1 in ledger" in page),
        ("tokens summed", near_midnight or "~1.51M" in page),
        ("drifted start line read", "| 2 |" in page.split("## closer", 1)[1]),
        ("other log line kept", "drained the easy ones" in page),
        ("odd line counted", "1 line with no time stamp" in page),
        ("tools folder not a worker", "## tools" not in page),
        ("lane count", "Left to work: 1** FlowWorks" in page and "(1 ready)" in page),
        ("unfiled lane items apart", "1 more is open in the ledger but has no live item file (1 doing)" in page),
        ("system account", "Claude System account: 42%" in page),
        ("svg one line", page.count("<svg") == 1 and not any(l.strip() == "" for l in page.split("<svg", 1)[1].split("</svg>", 1)[0].splitlines())),
        ("phone has needs", "NEEDS YOU" in phone and "stuckone" in phone),
        ("item titles beside ids", "`RM_DONE_ITEM_ONE` (A thing really closed)" in page),
    ]
    empty = os.path.join(tmp, "empty")
    os.makedirs(empty)
    stubs = wire(mod, empty, lane)
    page2, phone2, _ = mod.build(stubs)
    sroot = os.path.join(tmp, "s")
    os.makedirs(sroot)
    plant_steve(sroot)
    json.dump({"workers": [{"worker": n, "machine": "SteveDesktop"} for n in ("steveon", "stevestop", "stevedead")]},
              open(os.path.join(sroot, "workers.json"), "w"))
    stubs = wire(mod, sroot, lane, steve_up=True)
    pageS, _, _ = mod.build(stubs)
    needsS = pageS.split("## Needs you", 1)[1].split("## Workers at a glance", 1)[0]
    out += [
        ("released is handed back", "handed back" in page and "wobbled" in page.split("</svg>", 1)[0] and "other end" not in page),
        ("alarm not a question", "alarmer asks you 1 question" in needs and "Which colour" in needs and "read-only" not in needs),
        ("alarm in its own section", "## Alarms" in page and "alarmer" in page.split("## Alarms", 1)[1].split("## Workers at a glance", 1)[0]),
        ("steve unit asked on steve", "`rm-whittle-steveon.service` on SteveDesktop: running" in pageS),
        ("stop file is on purpose", "stevestop" not in needsS and "stopped on purpose" in pageS and "Owner parked this lane" in pageS),
        ("real contradiction stays", "stevedead's file says it is working, but its unit `rm-whittle-stevedead.service` is stopped** on SteveDesktop" in needsS),
        ("steve down not crash", "steveon" not in needs and "**unreachable**" in page),
    ]
    out.append(("empty root", "No Whittle workers yet" in page2 and "none yet" in phone2))
    stubs["ledger"] = lambda sources: (_ for _ in ()).throw(mod.Unmeasured("planted ledger failure"))
    page3, _, _ = mod.build(stubs)
    out.append(("ledger failure said", "The ledger could not be read" in page3 and "UNMEASURED" in page3))
    return out


def run_checks(source):
    tmp = tempfile.mkdtemp(prefix="selftest_whittle_now_")
    try:
        return checks(load(source), tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


MUTANTS = [
    ("steve unit asked on steve", 'str(r["info"].get("machine", "")).lower().startswith("steve"))]', 'False)]'),
    ("stop file is on purpose", 'r.get("stop") is not None:\n        pass', 'r.get("stop") is None:\n        pass'),
    ("alarm not a question", 'if not ALARM_RE.search(q["text"])]', 'if True]'),
    ("edge not stuck by rounds", 'r["rounds_on_item"] > STUCK_ROUNDS', 'r["rounds_on_item"] >= STUCK_ROUNDS'),
    ("released is handed back", '"released": "handed back"', '"released": "other end"'),
    ("unreachable not stopped", '{"word": "unreachable", "host": host', '{"word": "inactive", "host": host'),
]


def main():
    results = run_checks(SOURCE)
    bad = [n for n, ok in results if not ok]
    for n, ok in results:
        print("%s %s" % ("PASS" if ok else "FAIL", n))
    for name, old, new in MUTANTS:
        if SOURCE.count(old) != 1:
            print("FAIL mutant %r: its anchor is not in whittle_now.py once" % name)
            bad.append("mutant " + name)
            continue
        caught = dict(run_checks(SOURCE.replace(old, new))).get(name) is False
        print("%s mutant caught by %r" % ("PASS" if caught else "FAIL", name))
        if not caught:
            bad.append("mutant " + name)
    print("selftest_whittle_now: %s" % ("OK" if not bad else "FAILED: " + ", ".join(bad)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
