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
import re
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
            "%s round 1 end: RM_DONE_ITEM_ONE closed sha=abc1234def56789012abc1234def5678901234ab tokens=1.2M weighted=2000000 cost_usd=12.50" % stamp(41),
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
    for name, stop in (("steveon", None), ("stevestop", "Owner parked this lane until the disk move is done."), ("stevedead", None), ("steveon_halting", "No offline agents for now")):
        d = os.path.join(root, name)
        os.makedirs(d)
        json.dump({"worker": name, "unit": "rm-whittle-" + name, "machine": "SteveDesktop", "lane": "offline", "state": "working"},
                  open(os.path.join(d, "worker.json"), "w"))
        open(os.path.join(d, "loop.log"), "w").write("%s round 1 start, open=3 item=RM_EDGE_ITEM_TWO\n" % stamp(5))
        if stop:
            open(os.path.join(d, "STOP"), "w").write(stop)
    os.makedirs(os.path.join(root, "tools"))


TRANSCRIPT_AGE = [None]   # seconds old the planted claude transcript is; None = unknown


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

    def transcripts(recs, sources):
        for r in recs:
            r["transcript_t"] = TRANSCRIPT_AGE[0] and time.time() - TRANSCRIPT_AGE[0]
    return {"ledger": fake_ledger, "transcripts": transcripts, "history": lambda sources: {"system": (30.0, None)}, "machines": lambda state, sources: {},
            "accounts": lambda sources: [{"name": "system", "used": 42.0, "resets": time.time() + 86400, "t": time.time(),
                                          "why": None, "slope": None}],
            "codex": lambda sources: {"used": 30.0, "t": time.time(), "exact": True, "reset": None},
            "notice": lambda sources: {"account": "steven", "pct_left": 80.0, "line": 30}}


def narrow_tables(text):
    """Table rows that would run off the right edge: over 200 chars, or holding a run of 28+ non-space chars."""
    bad = []
    for l in text.splitlines():
        if l.startswith("|"):
            plain = l.replace("\u200b", " ")
            if len(plain) > 200 or re.search(r"[^\s|]{28,}", plain) or re.search(r"[0-9a-f]{40}", plain):
                bad.append(l[:80])
    return bad


def head_of(page):
    return next(l for l in page.splitlines() if "Spent since start" in l)


def midnight_keeps(mod, stubs, page):
    """Local midnight falls 30 minutes ago, between rounds of every worker: the headline must not change."""
    old = mod.midnight
    mod.midnight = lambda: time.time() - 1800
    try:
        page2, _, _ = mod.build(stubs)
    finally:
        mod.midnight = old
    strip = lambda h: re.sub(r"\(Nov.*?\)|FlowWorks lane.*", "", h)
    return strip(head_of(page)) == strip(head_of(page2)) and "none yet" not in head_of(page2) and "$0.00" not in head_of(page2)


def checks(mod, tmp):
    root = os.path.join(tmp, "w")
    os.makedirs(root)
    lane = os.path.join(tmp, "lane.json")
    json.dump({"seat": "X", "id_patterns": ["^RM_FWLIVE_", "^RM_STUCK_"]}, open(lane, "w"))
    plant(root)
    r2 = os.path.join(root, "stuckone", "rounds", "2")
    os.makedirs(r2)
    json.dump({"total": {"cost_usd": 3.25, "weighted": 500000}}, open(os.path.join(r2, "spend.json"), "w"))
    stubs = wire(mod, root, lane)
    mstubs = stubs
    page, phone, _ = mod.build(stubs)
    needs = page.split("## Needs you", 1)[1].split("## Workers at a glance", 1)[0].split("\n## Alarms", 1)[0]
    edge_part = page.split("## edgy", 1)[1] if "## edgy" in page else ""
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
        ("claim not accepted", "closer said it closed `RM_CLAIM_ITEM_ONE`" in needs),
        ("ledger close accepted", "closed in the ledger" in page and "`abc1234def`" in page and "abc1234def5" not in page),
        ("closed today split", "1 in the ledger (2 said by workers)" in page),
        ("spend from round-end line + spend.json", "Spent since start: $15.75 (2.50M weighted tokens)" in page),
        ("unmeasured rounds counted, not guessed", "rounds unmeasured" in page),
        ("dollars per close", "$15.75 per close" in page),
        ("headline counts since the fleet started", "since the fleet started (" in page and "last 24 h: $15.75" in page and "Closed today" not in page),
        ("midnight between rounds keeps the totals", midnight_keeps(mod, stubs, page)),
        ("raw token sum gone", "Tokens today" not in page),
        ("accounts line is first under the title", page.splitlines()[2].startswith("**Accounts left") and page.index("<svg") > page.index("Accounts left")),
        ("drifted start line read", "| 2 |" in page.split("## closer", 1)[1]),
        ("other log line kept", "drained the easy ones" in page),
        ("odd line counted", "1 line with no time stamp" in page),
        ("tools folder not a worker", "## tools" not in page),
        ("lane count", "Left to work: 1** FlowWorks" in page and "(1 ready)" in page),
        ("unfiled lane items apart", "1 more is open in the ledger but has no live item file (1 doing)" in page),
        ("system account", "Claude System account: 42%" in page),
        ("svg one line", page.count("<svg") == 1 and not any(l.strip() == "" for l in page.split("<svg", 1)[1].split("</svg>", 1)[0].splitlines())),
        ("phone has needs", "NEEDS YOU" in phone and "stuckone" in phone),
        ("item titles under the table", "`RM_\u200bDONE_\u200bITEM_\u200bONE`: A thing really closed" in page),
        ("tables fit: short rows, no long unbreakable run, no 40-hex", narrow_tables(page) == [] and narrow_tables(phone) == []),
    ]
    # liveness: files 2 h old, unit up; the claude transcript decides
    for n in ("worker.json", "loop.log", "progress.md", "OWNER_QUESTIONS.md"):
        os.utime(os.path.join(root, "stuckone", n), (time.time() - 7200,) * 2)
    TRANSCRIPT_AGE[0] = 60
    pageL, _, _ = mod.build(mstubs)
    TRANSCRIPT_AGE[0] = 3 * 3600
    pageH, _, _ = mod.build(mstubs)
    TRANSCRIPT_AGE[0] = None
    out.append(("fresh transcript: not hung", "stuckone has written nothing" not in pageL))
    out.append(("stale files and stale transcript: hung", "stuckone has written nothing, and its claude transcript is quiet" in pageH))
    empty = os.path.join(tmp, "empty")
    os.makedirs(empty)
    stubs = wire(mod, empty, lane)
    page2, phone2, _ = mod.build(stubs)
    sroot = os.path.join(tmp, "s")
    os.makedirs(sroot)
    plant_steve(sroot)
    json.dump({"workers": [{"worker": n, "machine": "SteveDesktop"} for n in ("steveon", "stevestop", "stevedead", "steveon_halting")]},
              open(os.path.join(sroot, "workers.json"), "w"))
    stubs = wire(mod, sroot, lane, steve_up=True)
    pageS, _, _ = mod.build(stubs)
    needsS = pageS.split("## Needs you", 1)[1].split("## Workers at a glance", 1)[0]
    out += [
        ("released is handed back", "handed back" in page and "wobbled" in page.split("</svg>", 1)[0] and "other end" not in page),
        ("alarm not a question", "alarmer asks you 1 question" in needs and "Which colour" in needs and "read-only" not in needs),
        ("alarm in its own section", "## Alarms" in page and "alarmer" in page.split("## Alarms", 1)[1].split("## Workers at a glance", 1)[0]),
        ("steve unit asked on steve", "`rm-whittle-steveon.service` on SteveDesktop: running" in pageS),
        ("stop file is on purpose", "stevestop" not in needsS and "stopped by owner" in pageS and "Owner parked this lane" in pageS),
        ("stop file, round running -> stopping after this round", "STOPPING AFTER THIS ROUND" in pageS and "halting" not in needsS),
        ("real contradiction stays", "stevedead's file says it is working, but its unit `rm-whittle-stevedead.service` is stopped** on SteveDesktop" in needsS),
        ("steve down not crash", "steveon" not in needs and "**unreachable**" in page),
    ]
    out.append(("empty root", "No Whittle workers yet" in page2 and "none yet" in phone2))
    line = [l for l in page.splitlines() if l.startswith("**Accounts left")]
    out.append(("accounts line: remaining, drop since start, ? for missing source, live marked",
                len(line) == 1 and re.search(r"system 58% \(\u221212 since (Nov 11 )?19:48", line[0]) and "steven ?" in line[0] and "lukas ?" in line[0]
                and "Codex 70%" in line[0] and "live: steven" in line[0] and "OLD" not in line[0] and phone.splitlines()[1].startswith("Accounts left")))
    sa = dict(stubs)
    sa["accounts"] = lambda sources: [{"name": "system", "used": 42.0, "resets": None, "t": time.time() - 1200, "why": None, "slope": None}]
    old_line = [l for l in mod.build(sa)[0].splitlines() if l.startswith("**Accounts left")][0]
    out.append(("old reading flagged in the line", "20 min OLD" in old_line))
    stubs2 = dict(stubs)
    stubs2["codex"] = lambda sources: (_ for _ in ()).throw(mod.Unmeasured("planted codex failure"))
    pageC, _, _ = mod.build(stubs2)
    out.append(("codex missing -> ?", "Codex ?" in pageC))
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
    ("stop file is on purpose", 'if r.get("stop") is not None and us.get("word") != "active":', 'if False:'),
    ("fresh transcript: not hung", 'alive = max([t for t in (r["last_write"], r.get("transcript_t")) if t] or [0]) or None', 'alive = r["last_write"]'),
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
