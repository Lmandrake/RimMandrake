#!/usr/bin/env python3
"""selftest_ops_episodes: the episodes list and the judge's graded notes (ops_episodes.py, strategy §3 / §8 step 7,
OPS_JUDGE_NOTES_MEASURE_VS_NO_CHANGE), planted case by case: a flapping reading folds to one line, an unresolved
episode is never evicted or cut, the cut is counted, a blind store moves nothing, incidents fold per cause; notes are
refused on a guessed or blind key and past ten a run; held / missed / ungradable / pending; ten easy notes score no
better than assuming no change; the open incidents the notes left out are counted; and ops_memory.publish puts both
on the page in the same generation. Everything in a temp dir; never the live ops_watch dir."""
import json
import os
import sys
import tempfile
import time
from pathlib import Path

os.environ["TZ"] = "UTC"
time.tzset()
TMP = tempfile.mkdtemp(prefix="ops_episodes_selftest_")
os.environ["RM_OPS_WATCH_DIR"] = TMP
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ops_episodes as oe  # noqa: E402
import ops_memory as om  # noqa: E402

H = 3600.0
D = 24 * H
NOW = 1793577600.0 + 12 * H
FAILS = []


def ok(cond, what):
    if not cond:
        FAILS.append(what)
    print(("PASS " if cond else "FAIL ") + what)


def gen(readings, store_error=None):
    m = {"readings": readings, "written_at": NOW}
    if store_error:
        m["store_error"] = store_error
    return m


OUT = {"state": "outside", "v": 90.0, "band": {"lo": 10.0, "hi": 20.0}}
NORM = {"state": "normal", "v": 15.0, "band": {"lo": 10.0, "hi": 20.0}}

# 1. a reading that flaps every minute takes one line, with its count
st = {}
for i in range(50):
    st = oe.update(st, gen({"t.x": OUT}), [], NOW + i * 120)
    st = oe.update(st, gen({"t.x": NORM}), [], NOW + i * 120 + 60)
e = st["readings"]["t.x|outside"]
page = oe.render_episodes(st)
ok(len(st["readings"]) == 1 and e["count"] == 50 and e["closed_t"] is not None
   and sum("t.x outside" in x for x in page) == 1, "flapping: 50 excursions fold to one line, count 50 (%s)" % e["count"])

# 2. an unresolved episode is never evicted (20 d open), a closed one is evicted 14 d after closing
st = oe.update({}, gen({"t.old": OUT, "t.gone": OUT}), [], NOW - 20 * D)
st = oe.update(st, gen({"t.old": OUT, "t.gone": NORM}), [], NOW - 19 * D)
st = oe.update(st, gen({"t.old": OUT, "t.gone": NORM}), [], NOW)
ok("t.old|outside" in st["readings"] and st["readings"]["t.old|outside"]["closed_t"] is None,
   "unresolved: an episode open 20 d is kept")
ok("t.gone|outside" not in st["readings"] and st["evicted"] == 1, "evicted: closed 19 d ago is gone and counted")

# 3. the page never cuts an open line, cuts the oldest closed ones and says how many
st = {"readings": {}, "incidents": {}}
for i in range(60):
    st["readings"]["c%02d|outside" % i] = {"subject": "c%02d" % i, "kind": "outside", "first_t": NOW - 5 * D,
                                           "opened_t": NOW - 5 * D + i, "closed_t": NOW - 4 * D + i, "count": 1}
for i in range(45):
    st["readings"]["o%02d|blind" % i] = {"subject": "o%02d" % i, "kind": "blind", "first_t": NOW - D,
                                         "opened_t": NOW - D + i, "closed_t": None, "count": 1}
page = oe.render_episodes(st, max_lines=40)
ok(sum(x.startswith("- OPEN") for x in page) == 45 and any("60 older closed lines cut" in x for x in page),
   "cut: all 45 open lines kept past a 40-line page, 60 closed cut and said")

# 4. a store that did not answer moves nothing; open episodes say unread
st = oe.update({}, gen({"t.x": OUT}), [], NOW)
st2 = oe.update(st, gen({}, store_error="ConnectionRefused"), [], NOW + 600)
ok(st2["readings"]["t.x|outside"]["closed_t"] is None and st2["unread"]
   and any("store unread" in x for x in oe.render_episodes(st2)), "blind store: an open episode stays open, unread")

# 5. steps: a kept step opens one episode, closes when it leaves the window
st = oe.update({}, gen({"t.s": dict(NORM, step={"from": 100.0, "to": 140.0, "at": NOW - 3 * D})}), [], NOW)
ok(st["readings"]["t.s|step"]["closed_t"] is None and "100 to 140" in st["readings"]["t.s|step"]["detail"],
   "step: a kept step is an open episode")
st = oe.update(st, gen({"t.s": NORM}), [], NOW + H)
ok(st["readings"]["t.s|step"]["closed_t"] == NOW + H, "step: closes when ops_memory no longer keeps it")

# 6. incidents fold per cause: opened, closed, reopened = one open line, twice; an old open one is never evicted
rows = [{"ev": "opened", "id": "disk-1", "cause": "disk", "t": NOW - 3 * D},
        {"ev": "joined", "id": "disk-1", "t": NOW - 3 * D + 60},
        {"ev": "closed", "id": "disk-1", "t": NOW - 2 * D},
        {"ev": "reopened", "id": "disk-1", "t": NOW - D},
        {"ev": "opened", "id": "tps-1", "cause": "tps", "at": oe.iso(NOW - 30 * D)},
        {"kind": "signal-row", "why": "no ev: a signal, not an incident row"}]
st = oe.update({}, gen({}), rows, NOW)
ok(st["incidents"]["disk|incident"]["count"] == 2 and st["incidents"]["disk|incident"]["closed_t"] is None,
   "incident: closed then reopened folds to one open line, count 2")
ok("tps|incident" in st["incidents"], "incident: open 30 d (ISO time only) is never evicted")
st2 = oe.update({}, gen({}), rows[:2] + [{"ev": "opened", "id": "disk-2", "cause": "disk", "t": NOW - 2.5 * D},
                                         {"ev": "closed", "id": "disk-1", "t": NOW - 2 * D}], NOW)
ok(st2["incidents"]["disk|incident"]["closed_t"] is None and st2["incidents"]["disk|incident"]["count"] == 2,
   "incident: one cause stays open while disk-2 is still open; the second incident counted")
st2 = oe.update({}, gen({}), rows[:2] + [{"ev": "relapsing", "id": "disk-1", "t": NOW - 2 * D}], NOW)
ok(st2["incidents"]["disk|incident"]["count"] == 2, "incident: a relapse while open is counted")
st2 = oe.update(oe.update({}, gen({"t.x": OUT}), [], NOW), gen({"t.y": NORM}), [], NOW + H)
ok(st2["readings"]["t.x|outside"]["closed_t"] is None and any("absent from this generation" in x
                                                              for x in oe.render_episodes(st2)),
   "absent: a reading missing from a generation keeps its episode open, said (never resolved by absence)")
st = oe.update(st, gen({}), None, NOW)
ok(st["told_unread"] and "disk|incident" in st["incidents"]
   and any("told.jsonl did not read" in x for x in oe.render_episodes(st)), "torn told.jsonl: last episodes kept, said")

# review fixes: going blind is not recovery; a missing told.jsonl is unread; a second step is counted
st = oe.update(oe.update({}, gen({"t.x": OUT}), [], NOW), gen({"t.x": {"state": "blind", "why": "stale"}}), [], NOW + H)
ok(st["readings"]["t.x|outside"]["closed_t"] is None, "blind: an outside reading going blind keeps its episode open")
st = oe.update(oe.update({}, gen({}), rows, NOW), gen({}), [], NOW + H)
ok("disk|incident" in st["incidents"] and st["told_unread"], "told.jsonl missing: known incidents kept, said unread")
s1 = dict(NORM, step={"from": 100.0, "to": 140.0, "at": NOW - 3 * D})
s2 = dict(NORM, step={"from": 140.0, "to": 190.0, "at": NOW - D})
st = oe.update(oe.update({}, gen({"t.s": s1}), [], NOW), gen({"t.s": s2}), [], NOW + H)
ok(st["readings"]["t.s|step"]["count"] == 2 and st["readings"]["t.s|step"]["opened_t"] == NOW - D,
   "step: a second step while one is open is counted and opens at its own time")

# ---------------------------------------------------------------------------------------------------- judge notes
d = Path(TMP) / "notes"
d.mkdir()
MEM = {"generation": 7, "written_at": NOW - 60, "readings": {
    "disk.free_gb": {"state": "normal", "kind": "number", "v": 50.0, "stale_s": 1800.0},
    "flow.queue": {"state": "normal", "kind": "number", "v": 3.0, "stale_s": 1800.0},
    "t.ctr": {"state": "normal", "kind": "counter", "v": 2.0, "stale_s": 1800.0},
    "t.blind": {"state": "blind", "why": "stale"}}}
INC = {"open": [{"id": "disk-1", "metric": "disk.free_gb", "metrics": {"disk.free_gb": {}}},
                {"id": "tps-1", "metric": "tps.health_breaches", "metrics": {}},
                {"id": "acc-1", "metric": "accounts.runway", "metrics": {}},
                {"id": "flow-1", "metric": "flow.stuck_min", "metrics": {}}]}


def add(run, reading, cmp, value, dl="+6h", mode="at", incident=None):
    return oe.add_note(run, reading, cmp, value, dl, mode, incident, memory=MEM, incidents=INC, now=NOW, d=d)


def refused(fn, what):
    try:
        fn()
    except ValueError as e:
        ok(True, "refused: %s (%s)" % (what, e))
        return
    ok(False, "refused: %s" % what)


refused(lambda: add("r0", "disk.free_gbb", "<", 5), "a key memory.json does not hold")
refused(lambda: add("r0", "t.blind", "<", 5), "a blind reading")
refused(lambda: add("r0", "disk.free_gb", "<", 5, dl="-1h"), "a deadline in the past")
refused(lambda: add("r0", "disk.free_gb", "~", 5), "an unknown comparison")
refused(lambda: add("r0", "disk.free_gb", "<", 5, dl="+400h"), "a deadline past the 14-day scoreboard")
refused(lambda: oe.add_note("r0", "disk.free_gb", "<", 5, "+6h", memory=dict(MEM, written_at=NOW - 3 * H),
                            incidents=INC, now=NOW, d=d), "a v0 from a memory generation 3 h old")
for i in range(10):
    add("easy", "disk.free_gb", ">", 10)           # already true of v0 = 50, and stays so
refused(lambda: add("easy", "disk.free_gb", ">", 10), "an eleventh note in one run")
n_change = add("bold", "flow.queue", ">=", 8, mode="before", incident="flow-1")    # v0 3: the queue will grow
n_wrong = add("bold", "disk.free_gb", "<", 30, incident="tps-1")        # says disk will fall below 30; it will not
n_blind = add("bold", "disk.free_gb", "==", 50, dl="+2h")               # no reading near its deadline
n_ctr = add("bold", "t.ctr", ">", 5, dl="+10h")                         # a counter: graded on its rate per hour
n_late = add("late", "disk.free_gb", ">", 10, dl="+48h")
import threading  # noqa: E402
dl_ = Path(TMP) / "lock"
ths = [threading.Thread(target=lambda: [oe.add_note("race", "disk.free_gb", ">", 1, "+6h", memory=MEM, incidents=INC,
                                                    now=NOW, d=dl_) for _ in range(5)]) for _ in range(2)]
[t.start() for t in ths]
[t.join() for t in ths]
ids = [n["id"] for n in oe.read_notes(dl_ / "judge_notes.jsonl")]
ok(len(ids) == 10 and len(set(ids)) == 10, "lock: two writers racing leave 10 notes with 10 distinct ids")
notes = oe.read_notes(d / "judge_notes.jsonl")
with open(d / "judge_notes.jsonl", "a") as f:
    f.write('{"torn": ')                                                 # a writer killed mid-line
ok(len(oe.read_notes(d / "judge_notes.jsonl")) == len(notes) == 15, "notes: a torn last line leaves the 15 standing")
oe.add_note("aftertorn", "disk.free_gb", ">", 1, "+6h", memory=MEM, incidents=INC, now=NOW, d=d)
ok(any(n["run"] == "aftertorn" for n in oe.read_notes(d / "judge_notes.jsonl")),
   "notes: a note appended after a torn tail is not swallowed")


def samples(key):
    out = []
    t = NOW
    while t <= NOW + 12 * H:
        if key == "disk.free_gb" and not (NOW + 1.4 * H < t < NOW + 3 * H):     # a gap around n_blind's deadline
            out.append((t, "MEASURED", 50.0, False))
        if key == "flow.queue":
            out.append((t, "MEASURED", 3.0 + (t - NOW) / H * 2.0, False))        # reaches 8 at +2.5 h
        if key == "t.ctr":
            out.append((t, "MEASURED", (t - NOW) / H * 9.0, False))              # 9 per hour
        t += 600.0
    return out


g_early = oe.grade(notes, {}, samples, NOW + 3 * H, rate_fn=om.to_rates)
ok(g_early.get(n_change["id"], {}).get("grade") == "held", "before: held as soon as a sample satisfies it (+3 h)")
ok(n_wrong["id"] not in g_early and n_late["id"] not in g_early, "at: nothing graded before its deadline")
ok(oe.grade(notes, {}, lambda k: None, NOW + 13 * H) == {}, "a store that did not answer grades nothing")
g = oe.grade(notes, g_early, samples, NOW + 12 * H, stale_of=lambda k: 1800.0, rate_fn=om.to_rates)
ok(g[n_wrong["id"]]["grade"] == "missed" and g[n_wrong["id"]]["no_change_says"] == "missed",
   "at: disk < 30 missed on 50 (no change said missed too)")
ok(g[n_blind["id"]]["grade"] == "ungradable", "at: no measured reading within staleness of the deadline is ungradable")
ok(g[n_ctr["id"]]["grade"] == "held" and abs(g[n_ctr["id"]]["v"] - 9.0) < 0.5,
   "counter: graded on its rate per hour (%s)" % g[n_ctr["id"]].get("v"))
ok(all(g["easy#%d" % i]["grade"] == "held" for i in range(1, 11)), "easy: ten restatements all held")
ok(n_late["id"] not in g, "pending: a deadline still ahead is not graded")
g2 = dict(g)
g2[n_wrong["id"]] = dict(g2[n_wrong["id"]], grade="held")     # a final grade is never rewritten
ok(oe.grade(notes, g2, samples, NOW + 13 * H, rate_fn=om.to_rates)[n_wrong["id"]]["grade"] == "held",
   "final: a written grade is kept")

runs = {r["run"]: r for r in oe.score(notes, g, NOW + 12 * H)}
e, b = runs["easy"], runs["bold"]
ok(e["held"] == 10 and e["no_change"] == 10 and e["foresaw"] == 0,
   "no change: ten easy notes score 10 of 10, exactly what assuming no change scores, foresaw 0")
ok(b["held"] == 2 and b["missed"] == 1 and b["ungradable"] == 1 and b["foresaw"] == 2 and b["no_change"] == 1,
   "bold: held 2 (both foreseen changes), missed 1, ungradable 1; no change 1 of 3 (%s)" % {
       k: b[k] for k in ("held", "missed", "ungradable", "foresaw", "no_change")})
ok(e["left_out"] == ["acc-1", "flow-1", "tps-1"], "left out: easy named disk.free_gb only (%s)" % e["left_out"])
ok(b["left_out"] == ["acc-1", "tps-1"],
   "left out: --incident flow-1 from a flow note covers it; --incident tps-1 on a disk note is forged, still left out (%s)"
   % b["left_out"])
page = "\n".join(oe.render_notes(notes, g, NOW + 12 * H))
ok("assuming no change" in page and "foresaw a change 2" in page and "left out: 3 (acc-1, flow-1, tps-1)" in page,
   "page: totals beside no change, foresaw and left-out are shown")

# ------------------------------------------------------------------------------------------- through ops_memory
pd = Path(TMP) / "pub"
pd.mkdir()
(pd / "told.jsonl").write_text("\n".join(json.dumps(r) for r in rows[:4]) + "\n")
oe.add_note("pub", "disk.free_gb", "<", 30, "+1h", memory=MEM, incidents=INC, now=NOW, d=pd)
mem = {"written_at": NOW + 2 * H, "families": {"disk": {"normal": 1}}, "built_from": {},
       "readings": {"disk.free_gb": {"state": "normal", "kind": "number", "v": 50.0, "stale_s": 1800.0,
                                     "band": {"lo": 40.0, "hi": 60.0, "kind": "pooled"}, "side_h": 9.0,
                                     "trend_6h": "flat", "trend_24h": "flat"},
                    "t.x": OUT | {"kind": "number", "side_h": 1.0, "band": {"lo": 10.0, "hi": 20.0, "kind": "pooled"}}},
       "_samples": {"disk.free_gb": [(NOW + H, "MEASURED", 50.0, False)]}}
gnum, md = om.publish(mem, pd)
j = json.loads((pd / "memory.json").read_text())
ok("_samples" not in j and j["notes"]["total"] == 1 and j["notes"]["graded"] == 1, "publish: samples never written; the note graded")
ok("## Episodes, 14 d" in md and "OPEN disk incident" in md and "OPEN t.x outside" in md,
   "publish: episodes on the page, incident and reading")
ok("## Your notes, graded against assuming no change" in md and "pub#1" in md and "MISSED" in md,
   "publish: the graded note is on the page")
ok(om.check(pd, NOW + 2 * H + 60)[0], "publish: still one generation by check")
# a pending note's reading is always listed, even normal-and-flat
oe.add_note("pub2", "disk.free_gb", ">", 10, "+9h", memory=dict(MEM, written_at=NOW + 2 * H), incidents=INC,
            now=NOW + 2 * H, d=pd)
mem["written_at"] = NOW + 3 * H
mem.pop("_samples", None)
_g, md = om.publish(mem, pd)
sec = md.split("## Not normal and flat")[1].split("## Blind")[0]
ok("disk.free_gb 50" in sec, "publish: a pending note's reading is listed on the page")
# a broken notes part fails alone, said on the page
(pd / "judge_grades.json").write_text("{not json")
_g, md = om.publish(mem, pd)
ok("## Your notes: NOT GRADED" in md and "## Episodes, 14 d" in md, "publish: a broken grades file fails alone, said")

print("selftest_ops_episodes: %s (%d failed)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
sys.exit(1 if FAILS else 0)
