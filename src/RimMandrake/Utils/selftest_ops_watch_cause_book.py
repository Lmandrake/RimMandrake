#!/usr/bin/env python3
"""selftest_ops_watch_cause_book.py -- OPSWATCH_BUILD_ALARMS_KEYED_BY_CAUSE: one repair item per alarm cause.

Owner, 2026-11-06: "Merging duplicate alarms just seems like common sense". The arena removal (1f0e666566) filed 9
items in 13 minutes on tests that no longer exist: 3 alarm ids (two build-cop red groups, the overdue chase), and 5+2
successor twists from held-filing passes killed after the spawn and before the save.

Real ops_watch.run_alarms / settle_filing / real_filer, real cause_book, jam_classes and incident.step, over a fake
ledger (a stub filer) and a fake ingest module; temp dirs only. Sections:
  A  cause_key: exact signature by default; "gone|<root>" only on a tree that lacks every path the reading names
  B  replay, collapse corpus (selftest_ops_watch_cause_book_corpus.json): 9 spawns on 3 ids -> ONE item
  C  replay, distinct corpus: 20 build-cop reds on 20 present tests stay 20 items; with B beside them, 21
  D  a cause record left in `filing` (the pass killed after the spawn) completes on restart: no second spawn
  E  duplicates filed before the book: attached and blocked on the repair (WP-04 block), a failed block retried
  F  the repair closes: the record closes with it, and the still-crossing cause reopens the repair ONCE
  G  incident rows close with their repair (incident.step, closed_by "repair")
  H  real_filer adopts the successor twist an earlier killed pass spawned, and files the block edge
Each section is proven red under a planted break (--plant NAME; the self-proof at the end runs them all)."""
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "rimflow"))
TMP = Path(tempfile.mkdtemp(prefix="selftest_ops_watch_cause_book_"))
os.environ["RM_OPS_WATCH_DIR"] = str(TMP / "ops")
os.environ["RM_DATA_ROOT"] = str(TMP / "data")
os.environ.pop("METRONOME_DEADLINE", None)
(TMP / "ops").mkdir()
(TMP / "data").mkdir()
import ops_watch as OW  # noqa: E402
import cause_book as CB  # noqa: E402
import jam_classes as JC  # noqa: E402
import incident as IN  # noqa: E402

PLANT = sys.argv[sys.argv.index("--plant") + 1] if "--plant" in sys.argv else None
# plant -> the section it must turn red
PLANTS = {"per_alarm": "B", "all_one": "C", "no_reconcile": "D", "no_block": "E", "no_close": "F",
          "no_repair_close": "G", "next_twist": "H", "gone_blind": "A"}
if PLANT == "per_alarm":        # every alarm its own cause: the arena fan-out returns
    JC.cause_key = lambda aid, pt=None, exists=None: aid
elif PLANT == "all_one":        # every alarm one cause: distinct faults merge
    JC.cause_key = lambda aid, pt=None, exists=None: "one"
elif PLANT == "no_reconcile":   # a record left in filing is never completed
    CB.reconcile = lambda book, known, open_ids, alarms, now: []
elif PLANT == "no_block":       # queued dependents never get their block edge
    CB.queued_blocks = lambda book: []
elif PLANT == "no_close":       # an open record ignores its repair closing
    _rec2 = CB.reconcile

    def _no_close(book, known, open_ids, alarms, now):
        return _rec2(book, known, None if open_ids is None else set(open_ids) | {r.get("item") for r in book.values()},
                     alarms, now)
    CB.reconcile = _no_close
elif PLANT == "no_repair_close":
    IN.repaired = lambda events, items, since: None
elif PLANT == "next_twist":     # an already-filed twist is not recognised: the filer cannot adopt it
    OW.already_filed = lambda out, name: False
elif PLANT == "gone_blind":     # the tree reader sees every path, so nothing is ever gone
    JC.tree_exists = lambda clone: (lambda p: True)

FAILS = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else "  -- %s" % (str(detail)[:600],)))
    if not cond:
        FAILS.append(name)


CORPUS = json.loads((HERE / "selftest_ops_watch_cause_book_corpus.json").read_text(encoding="utf-8"))
PRESENT = set(CORPUS["present"])


def recorded_tree(p):
    """The committed tree the replay reads: a file of `present`, or a directory above one."""
    return p in PRESENT or any(q.startswith(p + "/") for q in PRESENT)


RULES = OW.load_rules()
for _t in RULES.get("targets") or []:
    if isinstance(_t, dict):
        _t.pop("conductor_log", None)       # never the real Conductor log from a fixture


def epoch(s):
    return OW.epoch(s)


def red_pt(tests, said="1 red since 2026-11-01, due 2026-11-04T11:00: FAIL x", due="2026-11-04T11:00"):
    return OW.M(len(tests), "nightly reds with one first error line", night="2026-11-06T04:00:00Z",
                subject=OW.red_subject(tests), said=said, news=["%s (due %s)" % (t, due) for t in tests], due=due)


def overdue_pt(tests):
    lines = ["%s red since 2026-11-01T11:00:00Z, due 2026-11-04T11:00:00Z" % t for t in tests]
    return OW.M(len(tests), "nightly reds red past their fix deadline", night="2026-11-06T04:00:00Z",
                said="; ".join(lines), news=lines)


def pt_of(row):
    tests = row.get("tests") or [row["test"]]
    return overdue_pt(tests) if row["aid"].startswith("NIGHTLY_RED_OVERDUE:") else red_pt(tests)


class Ledger:
    """A stub filer over a fake ledger: spawns, reopens, notes and block edges, as real_filer reports them."""

    def __init__(self, block_fail=0, kill_after_spawn=False):
        self.known, self.open = set(), set()
        self.spawns, self.reopens, self.notes, self.blocks = [], [], [], []
        self.block_fail = block_fail
        self.kill = kill_after_spawn

    def filer(self, todo, conf):
        res = {"_publish": "published"}
        for a in todo:
            n = a["name"]
            if a.get("note_only"):
                self.notes.append((a["item"], a["aid"]))
                res[n] = None
            elif a.get("block_only"):
                if self.block_fail:
                    self.block_fail -= 1
                    res[n] = "rimflow block refused: ledger busy"
                else:
                    self.blocks.append((a["item"], a["on"]))
                    res[n] = None
            elif a.get("reopen"):
                self.reopens.append(n)
                self.open.add(n)
                res[n] = None
            elif n in self.known:
                res[n] = None
                res.setdefault("_already", []).append(n)
            else:
                self.spawns.append(n)
                self.known.add(n)
                self.open.add(n)
                res[n] = None
                if self.kill:           # the beat's deadline kills the pass after the spawn, before the save
                    self.kill = False
                    raise SystemExit("killed at the beat deadline")
        return res

    def close(self, item):
        self.open.discard(item)


def fresh_ops(name):
    d = TMP / name
    d.mkdir()
    os.environ["RM_OPS_WATCH_DIR"] = str(d)
    return d


def pass_(L, points, now, tree):
    return OW.run_alarms(points, RULES, now, set(L.known), L.filer, set(L.open), None, cause_tree=tree)


def logrows(d):
    p = d / "alarms_log.jsonl"
    return [json.loads(x) for x in p.read_text().splitlines()] if p.exists() else []


def replay(rows, tree, L=None, name="replay"):
    """Each recorded spawn is a pass at its time, every alarm seen so far still red (as they were)."""
    d = fresh_ops(name)
    L = L or Ledger()
    seen = {}
    for r in sorted(rows, key=lambda r: r["ts"]):
        seen[r["aid"].split(":", 1)[1]] = pt_of(r)
        try:
            pass_(L, dict(seen), epoch(r["ts"]), tree)
        except SystemExit:
            pass
    return d, L


# A ----------------------------------------------------------------------------------------------------------------
def sec_a():
    gone = red_pt(["src/RimMandrake/Utils/arena/selftest_arena_judge.py"])
    here = red_pt(["src/RimMandrake/Utils/selftest_stun_scaling.py"])
    mixed = overdue_pt(["src/RimMandrake/Utils/arena/selftest_arena_judge.py", "src/RimMandrake/Utils/selftest_stun_scaling.py"])
    check("A: no tree given, every alarm is its own cause (its id)", JC.cause_key("NIGHTLY_RED:testing.red_a", gone) == "NIGHTLY_RED:testing.red_a")
    check("A: every named test gone: the removed subtree is the cause",
          JC.cause_key("NIGHTLY_RED:testing.red_a", gone, recorded_tree) == "gone|src/RimMandrake/Utils/arena")
    check("A: a present test is its own exact signature", JC.cause_key("NIGHTLY_RED:testing.red_b", here, recorded_tree) == "NIGHTLY_RED:testing.red_b")
    check("A: one present test among gone ones keeps the alarm its own",
          JC.cause_key("NIGHTLY_RED_OVERDUE:testing.nightly_reds_overdue", mixed, recorded_tree) == "NIGHTLY_RED_OVERDUE:testing.nightly_reds_overdue")
    check("A: a reading naming no path is its own cause", JC.cause_key("DISK:disk.full", OW.M(97, "%"), recorded_tree) == "DISK:disk.full")
    # sanity probe: the live reader sees this clone's committed tree (a sparse checkout is not a deletion)
    ex = JC.tree_exists(str(HERE.parent.parent.parent))
    check("A: tree_exists sees a committed file", ex("src/RimMandrake/Utils/ops_watch.py"))
    check("A: tree_exists sees the arena subtree gone (1f0e666566)", not ex("src/RimMandrake/Utils/arena")
          and not ex("src/RimMandrake/Utils/arena/selftest_arena_judge.py"))
    check("A: a path outside a sparse checkout still exists", ex("src/RimMandrake/FlowWorks/northstar/selftest_scenarios_map.py"))
    blind = JC.tree_exists(str(TMP / "no_such_clone"))
    check("A: an unreadable clone judges nothing gone", blind("src/RimMandrake/Utils/arena"))


# B ----------------------------------------------------------------------------------------------------------------
REPLAY = {}


def sec_b():
    rows = CORPUS["collapse"]
    _, before = replay(rows, None, name="b_before")
    d, after = replay(rows, recorded_tree, name="b_after")
    REPLAY.update(spawned=len(rows), ids=len({r["aid"] for r in rows}), before=len(before.spawns), after=len(after.spawns))
    check("B: the corpus is the 9 arena spawns on 3 alarm ids", len(rows) == 9 and REPLAY["ids"] == 3, REPLAY)
    check("B: without the tree (per alarm id) the replay files 3", len(before.spawns) == 3, before.spawns)
    check("B: keyed by cause the replay files ONE item (9 -> 1)", len(after.spawns) == 1, after.spawns)
    st = json.loads((d / "alarms.json").read_text())
    rep = after.spawns[0] if after.spawns else None
    check("B: all 3 alarms stand OPEN on that one repair item",
          sorted((st[a].get("state"), st[a].get("item")) for a in {r["aid"] for r in rows}) == [("OPEN", rep)] * 3, st)
    book = CB.load(d / "causes.json")
    r = book.get("gone|src/RimMandrake/Utils/arena") or {}
    check("B: one cause record, open, holding the 3 ids, the lead first", list(book) == ["gone|src/RimMandrake/Utils/arena"]
          and r.get("state") == "open" and r.get("item") == rep and len(r.get("aids") or []) == 3, book)
    check("B: the duplicates are said on the repair item, filing nothing", after.notes and {i for i, _ in after.notes} == {rep}, after.notes)
    att = [x for x in logrows(d) if x["event"] == "attached"]
    check("B: each duplicate's attachment is logged", {x["aid"] for x in att} == {r["aid"] for r in rows} - {r.get("aids", [None])[0]}, att)


# C ----------------------------------------------------------------------------------------------------------------
def sec_c():
    rows = CORPUS["distinct"]
    d, L = replay(rows, recorded_tree, name="c_distinct")
    REPLAY.update(distinct=len(rows), distinct_after=len(L.spawns))
    check("C: 20 distinct faults on present tests stay 20 items", len(rows) == 20 and len(L.spawns) == 20, (len(rows), L.spawns))
    book = CB.load(d / "causes.json")
    check("C: one record per alarm id, each its own lead", sorted(book) == sorted(r["aid"] for r in rows)
          and all(v["aids"] == [k] for k, v in book.items()), sorted(book))
    check("C: nothing attached", not [x for x in logrows(d) if x["event"] == "attached"], logrows(d)[-4:])
    st = json.loads((d / "alarms.json").read_text())
    check("C: each alarm's news goes to its own item only", all(st[aid]["item"] == i for i, aid in L.notes), L.notes)
    _, both = replay(CORPUS["distinct"] + CORPUS["collapse"], recorded_tree, name="c_both")
    REPLAY.update(both=len(CORPUS["distinct"]) + len(CORPUS["collapse"]), both_after=len(both.spawns))
    check("C: the two corpora together: 29 spawns -> 21 items", len(both.spawns) == 21, both.spawns)


# D ----------------------------------------------------------------------------------------------------------------
def sec_d():
    rows = CORPUS["collapse"]
    L = Ledger(kill_after_spawn=True)
    d = fresh_ops("d_restart")
    pts = {r["aid"].split(":", 1)[1]: pt_of(r) for r in rows}
    t = epoch("2026-11-06T05:01:00Z")
    try:
        pass_(L, pts, t, recorded_tree)
        killed = False
    except SystemExit:
        killed = True
    book = CB.load(d / "causes.json")
    rec = book.get("gone|src/RimMandrake/Utils/arena") or {}
    check("D: the pass died after the spawn with its record saved in filing", killed and len(L.spawns) == 1
          and rec.get("state") == "filing" and rec.get("item") == L.spawns[0], (killed, L.spawns, rec))
    pass_(L, pts, t + 60, recorded_tree)
    rows_ = logrows(d)
    book = CB.load(d / "causes.json")
    rec = book.get("gone|src/RimMandrake/Utils/arena") or {}
    check("D: on restart the record completes (cause_completed_on_restart)",
          any(x["event"] == "cause_completed_on_restart" and x["item"] == L.spawns[0] for x in rows_), rows_)
    check("D: ... and is open before the pass's filing: the duplicates note the repair that same pass",
          {aid for _, aid in L.notes} >= set(rec.get("aids", [])[1:]) and len(rec.get("aids", [])) == 3
          and {i for i, _ in L.notes} == {L.spawns[0]}, (L.notes, rec))
    check("D: no second spawn; the alarm finds its item filed", len(L.spawns) == 1 and rec.get("state") == "open"
          and any(x["event"] == "found_filed" for x in rows_), (L.spawns, rec))
    # a record whose lead stopped filing that name (cleared unfiled) is dropped, not completed into a ghost
    book = {"gone|x": {"state": "filing", "item": "OPS_GHOST_ABCD", "aids": ["NIGHTLY_RED:testing.red_gh"]}}
    out = CB.reconcile(book, {"OTHER"}, set(), {}, t)
    check("D: a filing record whose alarm no longer files it is dropped", book == {} and out[0]["event"] == "cause_dropped_unfiled", out)


# E ----------------------------------------------------------------------------------------------------------------
def sec_e():
    d = fresh_ops("e_block")
    rows = CORPUS["collapse"]
    by = {}
    for r in rows:
        by.setdefault(r["aid"], r)
    L = Ledger(block_fail=1)
    t = epoch("2026-11-06T06:00:00Z")
    st = {}
    for k, (aid, r) in enumerate(sorted(by.items())):      # each OPEN on an item of its own, filed before the book
        L.known.add(r["item"])
        L.open.add(r["item"])
        st[aid] = {"state": "OPEN", "item": r["item"], "name": r["item"], "title": "t", "filed": OW.iso(t - 3600 + k),
                   "since": OW.iso(t - 3600), "tries": 1, "told": {"v": 1, "class": None}, "noted": pt_of(r)["x"]["news"]}
    (d / "alarms.json").write_text(json.dumps(st))
    pts = {r["aid"].split(":", 1)[1]: pt_of(r) for r in by.values()}
    pass_(L, pts, t, recorded_tree)
    book = CB.load(d / "causes.json")
    rec = book.get("gone|src/RimMandrake/Utils/arena") or {}
    lead = sorted(st, key=lambda a: st[a]["filed"])[0]
    deps = sorted(r["item"] for a, r in by.items() if a != lead)
    check("E: the earliest-filed item holds the cause", rec.get("item") == st[lead]["item"] and rec.get("state") == "open", rec)
    check("E: the other two are its dependents", sorted(rec.get("dependents") or {}) == deps, rec)
    check("E: a refused block stays queued (one refused, one written)", len(L.blocks) == 1
          and sorted((rec.get("dependents") or {}).values()) == ["blocked", "queued"], (L.blocks, rec))
    check("E: the refusal is logged", any(x["event"] == "cause_block_failed" for x in logrows(d)))
    pass_(L, pts, t + 60, recorded_tree)
    rec = CB.load(d / "causes.json").get("gone|src/RimMandrake/Utils/arena") or {}
    check("E: the next pass retries it: both dependents blocked on the repair",
          sorted(L.blocks) == [(x, st[lead]["item"]) for x in deps] and set(rec["dependents"].values()) == {"blocked"}, (L.blocks, rec))
    pass_(L, pts, t + 120, recorded_tree)
    check("E: a written block is not written again", len(L.blocks) == 2 and not L.spawns, L.blocks)


# F ----------------------------------------------------------------------------------------------------------------
def sec_f():
    rows = CORPUS["collapse"]
    d, L = replay(rows, recorded_tree, name="f_close")
    rep = L.spawns[0]
    pts = {r["aid"].split(":", 1)[1]: pt_of(r) for r in rows}
    L.close(rep)
    t = epoch("2026-11-06T07:00:00Z")
    pass_(L, pts, t, recorded_tree)
    ev = logrows(d)
    check("F: the record closes with its repair", any(x["event"] == "cause_closed_with_repair" and x["item"] == rep for x in ev), ev[-6:])
    check("F: the cause still crossing reopens the repair ONCE (not once per alarm)", L.reopens == [rep] and len(L.spawns) == 1,
          (L.reopens, L.spawns))
    book = CB.load(d / "causes.json")
    rec = book.get("gone|src/RimMandrake/Utils/arena") or {}
    check("F: a new record of the cause, open on the reopened repair", rec.get("state") == "open" and rec.get("item") == rep, rec)
    st = json.loads((d / "alarms.json").read_text())
    check("F: every alarm of the cause stands on it", {st[a]["item"] for a in {r["aid"] for r in rows}} == {rep}, st)


# G ----------------------------------------------------------------------------------------------------------------
def sec_g():
    table = IN.load_table()
    table["routes"] = [{"match": "m.*", "route": "role", "reader": "Operations", "cause": "m"}] + table["routes"]
    t0 = float(int(time.time())) - 7200
    row = {"ev": "opened", "id": "m-1", "at": IN.iso(t0), "t": t0, "state": "open", "rung": 1, "rung_t": t0, "told_t": t0,
           "told_at": IN.iso(t0), "cause": "m", "class": "distressed", "metrics": {"m.x": {"class": "distressed", "event": False}},
           "items": ["OPS_REPAIR_ABCD"], "reader": "Operations", "ack_min": 30, "acked_t": t0 + 60, "recover_by_t": t0 + 3600,
           "recover_by": IN.iso(t0 + 3600), "ack_by": "OPERATIONS", "plan": "fixing"}
    now = t0 + 600
    quiet = {"t": now, "points": {}, "alarms": {}}
    closed = [{"id": "OPS_REPAIR_ABCD", "event": "close", "seat": "BENCH", "ts": IN.iso(t0 + 300)}]
    res = IN.step(table, [row], quiet, now, events=lambda: closed)
    c = [x for x in res["rows"] if x["ev"] == "closed"]
    check("G: the incident closes with its repair (closed_by repair)", len(c) == 1 and c[0].get("closed_by") == "repair"
          and c[0].get("repaired") == {"OPS_REPAIR_ABCD": IN.iso(t0 + 300)}, res["rows"])
    res = IN.step(table, [row], quiet, now, events=lambda: [])
    check("G: no close on the ledger, no close with repair", not [x for x in res["rows"] if x.get("closed_by") == "repair"], res["rows"])
    old = [{"id": "OPS_REPAIR_ABCD", "event": "close", "seat": "BENCH", "ts": IN.iso(t0 - 300)}]
    res = IN.step(table, [row], quiet, now, events=lambda: old)
    check("G: a close from before the incident is not its repair", not [x for x in res["rows"] if x.get("closed_by") == "repair"], res["rows"])
    standing = {"t": now, "points": {}, "alarms": {"X:m.x": {"state": "OPEN", "item": "OPS_REPAIR_ABCD"}}}
    res = IN.step(table, [row], standing, now, events=lambda: closed)
    check("G: its alarm still standing holds it open though the item closed", not [x for x in res["rows"] if x.get("closed_by") == "repair"], res["rows"])


# H ----------------------------------------------------------------------------------------------------------------
def sec_h():
    clone = TMP / "clone"
    ing = clone / "src/RimMandrake/Utils/testq"
    ing.mkdir(parents=True)
    (ing / "ingest.py").write_text('''import json, os
D = os.path.dirname(os.path.abspath(__file__))
CFG = json.load(open(os.path.join(D, "cfg.json")))
def rimflow(*a):
    with open(os.path.join(D, "calls.jsonl"), "a") as f:
        f.write(json.dumps(a) + "\\n")
    if a[0] == "live" and a[1] in CFG["retired"]:
        return 1, "%s is dropped: a retired item holds no promise" % a[1]
    if a[0] == "spawn":
        n = a[a.index("--name") + 1]
        if n in CFG["existing"]:
            return 1, "%s already exists" % n
    return 0, "ok"
def publish(n, message=""):
    return "published"
''')
    conf = dict(OW.alarm_conf(RULES))
    conf["clone"] = str(clone)
    OW.alarm_receiver_problem = lambda c: None
    OW.qhome = lambda: TMP
    base = "NIGHTLY_COP_FIX_RED_WARIWE_XVFM"
    tw = ["%s_%s" % (base, OW.alarm_twist("%s#%d" % (base, k))) for k in (1, 2)]

    def run(retired, existing, todo):
        (ing / "cfg.json").write_text(json.dumps({"retired": retired, "existing": existing}))
        cp = ing / "calls.jsonl"
        if cp.exists():
            cp.unlink()
        res = OW.real_filer(todo, conf)
        return res, [json.loads(x) for x in cp.read_text().splitlines()]

    def reopen():
        return [{"aid": "NIGHTLY_RED:testing.red_wariwe", "name": base, "title": "t", "reopen": True, "expedite": None}]
    res, calls = run([base], [tw[0]], reopen())
    spawns = [c for c in calls if c[0] == "spawn"]
    check("H: a twist an earlier killed pass spawned is adopted, not a new one",
          (res.get("_renamed") or {}).get(base) == tw[0] and res.get(tw[0]) is None, res)
    check("H: one spawn tried, none of the next twist; the adopted twist is reopened",
          [c[c.index("--name") + 1] for c in spawns] == [tw[0]] and ["live", tw[0]] in [c[:2] for c in calls], calls)
    res, calls = run([base, tw[0]], [tw[0]], reopen())
    check("H: the next twist only when the adopted one is retired too", (res.get("_renamed") or {}).get(base) == tw[1], res)
    blk = [OW.cause_block_todo("gone|src/x", "OPS_DUP_ABCD", "OPS_REPAIR_ABCD")]
    res, calls = run([], [], blk)
    check("H: a block edge is filed as WP-04's block, lifting when the repair is done",
          res.get("block:OPS_DUP_ABCD") is None and calls and calls[0][:8] == ["block", "OPS_DUP_ABCD", "--kind", "item", "--on",
                                                                              "OPS_REPAIR_ABCD", "--until", "done"], calls)


for tag, fn in (("A", sec_a), ("B", sec_b), ("C", sec_c), ("D", sec_d), ("E", sec_e), ("F", sec_f), ("G", sec_g), ("H", sec_h)):
    print("-- section %s" % tag)
    try:
        fn()
    except Exception as e:  # noqa: BLE001  a section that raises is that section red, the rest still run
        import traceback
        traceback.print_exc()
        check("%s: section ran" % tag, False, "%s: %s" % (type(e).__name__, e))

print("REPLAY: collapse %(spawned)s spawns on %(ids)s ids -> %(before)s items per id, %(after)s keyed by cause" % REPLAY
      if "after" in REPLAY else "REPLAY: not run")
if "distinct_after" in REPLAY:
    print("REPLAY: distinct %(distinct)s -> %(distinct_after)s; both corpora %(both)s -> %(both_after)s" % REPLAY)

if PLANT is None:
    # the self-proof: each planted break must turn its own section red
    for plant, sec in sorted(PLANTS.items()):
        p = subprocess.run([sys.executable, __file__, "--plant", plant], capture_output=True, text=True, timeout=240)
        red = [x for x in p.stdout.splitlines() if x.startswith("FAIL %s:" % sec)]
        check("PROOF: planted break %s turns section %s red" % (plant, sec), p.returncode != 0 and red,
              "rc=%s %s" % (p.returncode, (p.stdout + p.stderr)[-400:]))

print("ALL PASS" if not FAILS else "FAILED: %s" % FAILS)
sys.exit(1 if FAILS else 0)
