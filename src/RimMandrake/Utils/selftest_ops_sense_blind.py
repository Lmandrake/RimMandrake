#!/usr/bin/env python3
"""The sense families read cheaply, and a family that stays unread raises an alarm
(RIMMANDRAKE_WATCH_OPS_SENSE_OVERRUN_MOST_FAMILIES_BLIND). Page: design/specs/2026-11-22-sense-families-cheap/boundary.md;
each check is named for its promise. Fixture-only: stub collectors, temp dirs, a temp git repo, no live store."""
import calendar
import json
import os
import signal
import subprocess
import sys
import tempfile as _tf
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "sim"))
sys.path.insert(0, str(HERE.parent / "rimflow"))
_TMP = Path(_tf.mkdtemp(prefix="selftest_ops_sense_blind_"))
os.environ["RM_OPS_WATCH_DIR"] = str(_TMP / "ops")
os.environ["RM_OPS_WATCH_LIVE_DIR"] = str(_TMP / "live_elsewhere")
os.environ.pop("METRONOME_DEADLINE", None)
import ops_watch as OW  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else "  %s" % (detail,)))
    if not cond:
        FAILS.append(name)


_stat = os.stat
REAL = dict(OW.COLLECTORS)
calls = []


def stub(fam):
    def c(now, rules, ctx):
        calls.append(fam)
        return {"%s.stub" % fam: OW.M(1, "n")}
    return c


OW.COLLECTORS = {f: stub(f) for f in OW.ORDER}
rules = OW.load_rules()
ops = _TMP / "ops"
t0 = time.time() - 6 * 3600
OW.run(now=t0, rules=rules)             # a whole pass seeds every series
bound = OW.compose_max_age_s(rules)[0]
t1 = t0 + bound + 600                   # past the bound for every family
for i, f in enumerate(OW.ORDER):        # every family but pager read again recently: pager's sense passes were killed
    if f != "pager":
        OW.run(now=t1 - 300 + i, rules=rules, families=[f], compose=True)
kills = ops / "sense_kills.jsonl"
with open(kills, "a") as fh:
    for k in range(3):
        fh.write(json.dumps({"t": t1 - 900 + k * 60, "at": OW.iso(t1 - 900 + k * 60), "families": ["pager", "accounts"],
                             "stage": "collector pager", "seconds": 15.1}) + "\n")

def t_a_family_left_unread_raises_the_blind_alarm():
    filed = []


    def filer(todo, conf):
        filed.extend(todo)
        return dict({a["name"]: None for a in todo}, _publish="published")


    calls.clear()
    OW.run(now=t1, rules=rules, families=["flow"], compose=True, filer=filer)
    st = json.loads((ops / "status.json").read_text())
    bp = st["points"].get("sense.families_blind") or {}
    check("a-family-left-unread-raises-the-blind-alarm: the count names the unread family",
          bp.get("m") == "MEASURED" and bp.get("v") == 1 and "pager" in str((bp.get("x") or {}).get("names")), bp)
    names = [a["name"] for a in filed if a.get("key") == "sense.families_blind"]
    check("a-family-left-unread-raises-the-blind-alarm: the alarm pass files it on its fixed item",
          len(names) == 1 and names[0].startswith("OPS_SENSE_FAMILY_READING_RESTORE_"), [a.get("name") for a in filed])
    first = names[:1]
    filed.clear()
    OW.run(now=t1 + 60, rules=rules, families=["flow"], compose=True, filer=filer)
    check("a-family-left-unread-raises-the-blind-alarm: it files once while it holds",
          not [a for a in filed if a.get("key") == "sense.families_blind"], filed)
    OW.run(now=t1 + 120, rules=rules, families=["pager"], compose=True, filer=filer)
    OW.run(now=t1 + 180, rules=rules, families=["flow"], compose=True, filer=filer)
    st = json.loads((ops / "status.json").read_text())
    check("a-family-left-unread-raises-the-blind-alarm: a family inside the bound does not count",
          st["points"]["sense.families_blind"].get("v") == 0, st["points"]["sense.families_blind"])
    al = json.loads((ops / "alarms.json").read_text())
    cur = [a for k, a in al.items() if k.endswith(":sense.families_blind")]
    check("a-family-left-unread-raises-the-blind-alarm: the item id is fixed (same name on the next crossing)",
          cur and cur[0].get("name") == (first[0] if first else None), cur)


def t_a_blind_familys_points_say_why():
    global t2, joined
    t2 = t1 + 180 + bound + 600
    with open(kills, "a") as fh:
        fh.write(json.dumps({"t": t2 - 100, "families": ["timers"], "stage": "collector timers", "seconds": 15.0}) + "\n")
    calls.clear()
    OW.run(now=t2, rules=rules, families=["accounts"], compose=True)
    joined = list(calls)
    st = json.loads((ops / "status.json").read_text())
    why = str(st["points"].get("timers._collector", {}).get("why"))
    check("a-blind-familys-points-say-why: the carried UNMEASURED points name the kills and the stage",
          st["points"].get("timers._collector", {}).get("m") == "UNMEASURED" and "killed" in why
          and "collector timers" in why, why)


def t_the_alarm_family_joins_when_it_is_blind():
    check("the-alarm-family-joins-when-it-is-blind: a pass measures flow when flow is unread past the bound",
          sorted(joined) == ["accounts", "flow"], joined)
    calls.clear()
    OW.run(now=t2 + 60, rules=rules, families=["v3"], compose=True)
    check("the-alarm-family-joins-when-it-is-blind: once flow reads, it no longer joins", calls == ["v3"], calls)


def t_a_killed_pass_leaves_its_stage():
    child = _TMP / "slow_child.py"
    child.write_text(
        "import sys, time\nsys.path.insert(0, %r)\nimport ops_watch as OW\n"
        "OW.COLLECTORS = {f: (lambda fam: lambda now, rules, ctx: {'%%s.stub' %% fam: OW.M(1)})(f) for f in OW.ORDER}\n"
        "def slow(now, rules, ctx):\n    print('slow started', flush=True)\n    time.sleep(60)\n    return {}\n"
        "OW.COLLECTORS['pager'] = slow\n"
        "sys.exit(OW.main(['run', '--compose', '--family', 'pager']))\n" % str(HERE))
    n_before = len(kills.read_text().splitlines())
    p = subprocess.Popen([sys.executable, str(child)], stdout=subprocess.PIPE, text=True, start_new_session=True)
    line = p.stdout.readline()
    time.sleep(0.3)
    os.killpg(p.pid, signal.SIGTERM)
    try:
        rc = p.wait(timeout=10)
    except subprocess.TimeoutExpired:
        os.killpg(p.pid, signal.SIGKILL)
        rc = "hung"
    new = [json.loads(x) for x in kills.read_text().splitlines()[n_before:]]
    check("a-killed-pass-leaves-its-stage: one kill line with its families, stage and seconds",
          line.startswith("slow started") and len(new) == 1 and new[0].get("families") == ["pager"]
          and new[0].get("stage") == "collector pager" and isinstance(new[0].get("seconds"), (int, float)), (line, new))
    check("a-killed-pass-leaves-its-stage: the pass exits non-zero", rc not in (0, "hung"), rc)


def t_tps_reads_only_the_recent_segments():
    import tps_record as TR  # noqa: E402
    td = _TMP / "tps"
    td.mkdir()
    now = time.time()
    sess = "abc123"


    def row(seq, t, **kw):
        r = {"kind": "sample", "session": sess, "seq": seq, "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t)),
             "state": "run", "ratio": 0.9, "tps": 54, "target": 60, "dReal": 5.0, "speed": 1}
        r.update(kw)
        return json.dumps(r) + "\n"


    old = td / ("tps_20261101T000000Z_%s_100_000.jsonl" % "def456")
    old.write_text("".join(row(i, now - 9 * 86400 + 5 * i, session="def456") for i in range(50)))
    os.utime(old, (now - 9 * 86400, now - 9 * 86400))
    mid = td / ("tps_20261122T000000Z_%s_200_000.jsonl" % sess)
    mid.write_text("".join(row(i, now - 3000 + 5 * i) for i in range(100)))
    os.utime(mid, (now - 2500, now - 2500))
    new_seg = td / ("tps_20261122T000000Z_%s_200_001.jsonl" % sess)
    new_seg.write_text("".join(row(100 + i, now - 280 + 5 * i) for i in range(50)))
    opened = []
    _open = TR._open
    TR._open = lambda p, mode="rb": (opened.append(os.path.basename(p)), _open(p, mode))[1]
    whole = TR.summarise(TR.read_record(str(td), now=now)["rows"], now=now)
    opened.clear()
    recent = TR.summarise(TR.read_record(str(td), now=now, recent_s=300 + TR.TPS_RECENT_SLACK_S)["rows"], now=now)
    TR._open = _open
    same = {k: whole.get(k) for k in ("coverage", "ratioMedian", "stalls", "stallMaxS", "speed", "run", "samples")}
    check("tps-reads-only-the-recent-segments: only the segment written in the window is opened",
          opened == [new_seg.name], opened)
    check("tps-reads-only-the-recent-segments: the fresh session's summary equals the whole read's",
          same == {k: recent.get(k) for k in same} and same["coverage"] == "FRESH", (same, recent))
    r = subprocess.run([sys.executable, str(HERE / "tps_record.py"), "--recent", "--json", "--dir", str(td)],
                       capture_output=True, text=True, timeout=60)
    check("tps-reads-only-the-recent-segments: the --recent flag reads on the command line",
          r.returncode == 0 and json.loads(r.stdout)["summary"]["coverage"] == "FRESH", (r.returncode, r.stderr[-300:]))


def t_the_week_of_commits_is_read_once():
    repo = _TMP / "repo"
    repo.mkdir()
    G = ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false"]
    subprocess.run(G + ["init", "-q", "-b", "main"], check=True)


    def commit(path, msg, when):
        (repo / path).parent.mkdir(parents=True, exist_ok=True)
        (repo / path).write_text("%s %s\n" % (msg, when))
        subprocess.run(G + ["add", path], check=True)
        env = dict(os.environ, GIT_COMMITTER_DATE="@%d" % when, GIT_AUTHOR_DATE="@%d" % when)
        subprocess.run(G + ["commit", "-q", "-m", msg], check=True, env=env)


    os.environ["RM_STREAMS_BENCH"] = str(repo)
    now = time.time()
    commit("src/RimMandrake/Utils/a.py", "tools: one", now - 3 * 86400)
    commit("design/x.md", "content: two", now - 2 * 86400)
    commit("infrastructure/state/ledger/events/BENCH.jsonl", "ledger: three", now - 86400)
    rx = rules["process_regex"]
    gl = []
    _run = subprocess.run


    def spy(argv, *a, **k):
        if argv[:1] == ["git"] and "log" in argv:
            gl.append(argv)
        return _run(argv, *a, **k)


    subprocess.run = spy
    w1 = OW.git_window(now - 7 * 86400, rx, now=now)
    commit("src/RimMandrake/Utils/b.py", "tools: four", now - 60)
    gl.clear()
    w2 = OW.git_window(now - 7 * 86400, rx, now=now)
    inc = list(gl)
    cache = ops / "git_window_cache.json"
    cache.unlink()
    gl.clear()
    w3 = OW.git_window(now - 7 * 86400, rx, now=now)
    subprocess.run = _run
    check("the-week-of-commits-is-read-once: a new head reads only the commits since the cached one",
          len(inc) == 1 and any(".." in str(x) for x in inc[0]) and len(w2) == 4, (inc, len(w2)))
    check("the-week-of-commits-is-read-once: the incremental answer equals a whole read", w2 == w3, (w2, w3))
    subprocess.run(G + ["reset", "-q", "--hard", "HEAD~2"], check=True)
    commit("design/y.md", "content: five", now - 30)
    w4 = OW.git_window(now - 7 * 86400, rx, now=now)
    cache.unlink()
    w5 = OW.git_window(now - 7 * 86400, rx, now=now)
    check("the-week-of-commits-is-read-once: a head not descended from the cached one reads whole", w4 == w5
          and len(w4) == 3, (w4, w5))
    wx = OW.git_window(now - 7 * 86400, "^design/", now=now)
    check("the-week-of-commits-is-read-once: a changed process regex reads whole",
          [c[2] for c in wx] == [False, True, True], wx)
    OW.COLLECTORS = dict(REAL)
    pp = OW.c_process(now, rules, {})
    check("the-week-of-commits-is-read-once: process reads from it",
          pp["process.share_7d"].get("m") == "MEASURED" and pp["process.share_7d"]["x"].get("commits") == 3, pp["process.share_7d"])
    texts, bad = OW.tt_texts(now, rules, {"events": [{"ts": OW.iso(now - 10), "seat": "BENCH", "event": "note", "id": "X",
                                                       "text": "hi"}]})
    check("the-week-of-commits-is-read-once: tokentalk reads from it (ledger commits skipped)",
          not [k for k in bad if k.startswith("commits.")] and not any("ledger:" in m for k, v in texts.items()
                                                                        for m in v if k.startswith("commits.")), (texts, bad))


def t_few_old_progress_names_are_restatted():
    now = time.time()
    qd = _TMP / "done"
    qd.mkdir()
    for i in range(2000):
        (qd / ("j%04d.json" % i)).write_text("{}")
    pc = {}
    OW.newest_progress_mtime(qd, pc, now)
    stats = []
    _stat = os.stat
    os.stat = lambda p, *a, **k: (stats.append(p), _stat(p, *a, **k))[1]
    (qd / "jnew.json").write_text("{}")
    OW.newest_progress_mtime(qd, pc, now)
    os.stat = _stat
    check("few-old-progress-names-are-restatted: a pass stats the new name and at most PROGRESS_RESTAT old ones",
          any(str(s).endswith("jnew.json") for s in stats) and len(stats) <= min(OW.PROGRESS_RESTAT + 1, 1000), len(stats))


def t_codex_skips_day_folders_past_the_lookback():
    import csuite_codex_limits as CX  # noqa: E402
    cd = _TMP / "codex"
    now = time.time()
    for days in (2, 20, 60):
        t = now - days * 86400
        d = cd / time.strftime("%Y/%m/%d", time.gmtime(t))
        d.mkdir(parents=True, exist_ok=True)
        f = d / ("rollout-%d.jsonl" % days)
        f.write_text("")
        os.utime(f, (t, t))
    late = cd / time.strftime("%Y/%m/%d", time.gmtime(now - 60 * 86400)) / "rollout-resumed.jsonl"
    late.write_text("")         # written now in an old folder: past CODEX_LATE_WRITE_DAYS, not promised
    stats = []
    os.stat = lambda p, *a, **k: (stats.append(str(p)), _stat(p, *a, **k))[1]
    recs, nfiles = CX.readings([str(cd)], newer_than=now - 8 * 86400)
    os.stat = _stat
    check("codex-skips-day-folders-past-the-lookback: no rollout in an old day folder is statted",
          not [s for s in stats if "rollout-60" in s or "rollout-20" in s or "resumed" in s], stats)
    check("codex-skips-day-folders-past-the-lookback: every rollout in a newer folder is read",
          nfiles == 1 and any("rollout-2." in s for s in stats), (nfiles, stats))
    recs, nfiles = CX.readings([str(cd)])
    check("codex-skips-day-folders-past-the-lookback: with no lookback every rollout is read", nfiles == 4, nfiles)


def t_the_ledger_and_the_stamps_are_read_once():
    import role_use as RU  # noqa: E402
    import wrapup as WU  # noqa: E402
    st_calls = []
    _strp = time.strptime
    time.strptime = lambda *a: (st_calls.append(a), _strp(*a))[1]
    vals = [RU.epoch("2026-11-22T10:00:00Z") for _ in range(5)] + [RU.epoch("2026-11-22T10:00:00.123+00:00"), RU.epoch(None),
                                                                    RU.epoch("garbage")]
    time.strptime = _strp
    check("the-ledger-and-the-stamps-are-read-once: role_use.epoch parses a stamp once, same answers",
          len([c for c in st_calls if c[0] == "2026-11-22T10:00:00"]) <= 1
          and vals[:6] == [float(calendar.timegm((2026, 11, 22, 10, 0, 0)))] * 6 and vals[6:] == [None, None], (st_calls, vals))
    import model as MODEL  # noqa: E402
    reads = []
    _mr, _mp = MODEL.read, MODEL.replay
    MODEL.read = lambda *a, **k: (reads.append(1), [])[1]
    MODEL.replay = lambda evs: type("W", (), {"items": {}})()
    w = WU.World()
    a1 = w.doing_claims("BENCH", "2026-11-22T00:00:00Z")
    a2 = w.doing_claims("BENCH", "2026-11-22T00:00:00Z")
    MODEL.read, MODEL.replay = _mr, _mp
    check("the-ledger-and-the-stamps-are-read-once: one World reads the ledger once", len(reads) == 1 and a1 == a2 == [],
          (reads, a1, a2))


def t_a_light_pass_files_nothing_inside_the_beat():
    import fcntl
    os.environ["RM_OPS_WATCH_DIR"] = str(_TMP / "ops_held")
    od = _TMP / "ops_held"
    OW.COLLECTORS = {f: stub(f) for f in OW.ORDER}
    now = time.time()
    OW.run(now=now - 120, rules=rules)
    held = {"MATURATION_PAUSED:maturation.paused": {"state": "PENDING", "name": "OPS_SELFTEST_HELD_ITEM_ABCD",
                                                     "title": "held a", "deferred_at": OW.iso(now - 100), "deferred_n": 9,
                                                     "reopen": True, "tries": 0}}
    (od / "alarms.json").write_text(json.dumps(held))
    filer_calls, spawned = [], []
    _spawn = OW.spawn_held_filer
    OW.spawn_held_filer = lambda argv: (spawned.append(argv), "started")[1]
    os.environ["METRONOME_DEADLINE"] = "%.3f" % (time.time() + 15)
    OW.run(now=now, rules=rules, families=["companion"], compose=True, held_detach=True,
           filer=lambda todo, conf: (filer_calls.append(todo), {a["name"]: None for a in todo})[1])
    check("a-light-pass-files-nothing-inside-the-beat: the light pass starts the detached filer and files nothing",
          filer_calls == [] and len(spawned) == 1 and spawned[0][-1] == "file-held", (filer_calls, spawned))
    with open(od / OW.HELD_FILER_LOCK, "a") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        r = OW.start_held_filer()
    check("a-light-pass-files-nothing-inside-the-beat: a second filer is not started while one runs",
          r == "running" and len(spawned) == 1, (r, spawned))
    OW.spawn_held_filer = lambda argv: "not started: Unit rm-ops-held-filer.service already exists"
    OW.run(now=now + 60, rules=rules, families=["companion"], compose=True, held_detach=True,
           filer=lambda todo, conf: (filer_calls.append(todo), {})[1])
    fl = json.loads((od / "flags.json").read_text())["flags"]
    check("a-light-pass-files-nothing-inside-the-beat: a filer that cannot start is said in the flags",
          any(f.get("key") == "alarms.held_filer" for f in fl) and filer_calls == [], [f.get("key") for f in fl])
    OW.spawn_held_filer = _spawn
    seen = []
    _rf = OW.real_filer
    OW.real_filer = lambda todo, conf: (seen.append((OW.beat_deadline(), [a["name"] for a in todo])),
                                        dict({a["name"]: None for a in todo}, _publish="published"))[1]
    out = OW.file_held_detached(now=now + 120)
    OW.real_filer = _rf
    st = json.loads((od / "alarms.json").read_text())["MATURATION_PAUSED:maturation.paused"]
    check("a-light-pass-files-nothing-inside-the-beat: file-held files the held alarms with no beat deadline",
          seen == [(None, ["OPS_SELFTEST_HELD_ITEM_ABCD"])] and st.get("state") == "OPEN" and "0 still held" in out,
          (seen, st, out))
    check("a-light-pass-files-nothing-inside-the-beat: nothing held starts nothing", OW.start_held_filer() == "nothing held")
    os.environ.pop("METRONOME_DEADLINE", None)
    os.environ["RM_OPS_WATCH_DIR"] = str(_TMP / "ops")


def t_an_alarm_pass_in_a_beat_files_nothing_inside_it():
    os.environ["RM_OPS_WATCH_DIR"] = str(_TMP / "ops_alarm_pass")
    od = _TMP / "ops_alarm_pass"
    OW.COLLECTORS = {f: stub(f) for f in OW.ORDER}
    now = time.time()
    OW.run(now=now - 3 * bound, rules=rules)
    for i, f in enumerate(OW.ORDER):            # all read again but pager: pager is blind, and the target crosses
        if f not in ("pager", "flow"):
            OW.run(now=now - 200 + i, rules=rules, families=[f], compose=True)
    filer_calls, spawned = [], []
    _spawn = OW.spawn_held_filer
    OW.spawn_held_filer = lambda argv: (spawned.append(argv), "started")[1]
    os.environ["METRONOME_DEADLINE"] = "%.3f" % (time.time() + 15)
    OW.run(now=now, rules=rules, families=["flow"], compose=True, held_detach=True,
           filer=lambda todo, conf: (filer_calls.append(todo), {a["name"]: None for a in todo})[1])
    st = json.loads((od / "alarms.json").read_text())
    cur = [v for k, v in st.items() if k.endswith(":sense.families_blind")]
    check("an-alarm-pass-in-a-beat-files-nothing-inside-it: the crossing is held for the detached filer, not filed",
          filer_calls == [] and cur and cur[0].get("state") == "PENDING" and cur[0].get("deferred_at")
          and len(spawned) == 1, (filer_calls, cur, spawned))
    OW.spawn_held_filer = _spawn
    note = {"note_only": True, "item": "OPS_SELFTEST_OPEN_ITEM_WXYZ", "name": "note:X:y.z", "aid": "X:y.z", "text": "hi"}
    st["X:y.z"] = {"state": "OPEN", "item": "OPS_SELFTEST_OPEN_ITEM_WXYZ", "name": "OPS_SELFTEST_OPEN_ITEM_WXYZ"}
    (od / "alarms.json").write_text(json.dumps(st))
    r = OW.queue_filer([note, dict(note, text="newer")], {})
    check("an-alarm-pass-in-a-beat-files-nothing-inside-it: a note is queued once, newest wording, and deferred",
          r == {"note:X:y.z": OW.FILING_DEFERRED} and [a["text"] for a in OW.queued_notes(st)] == ["newer"],
          (r, OW.queued_notes(st)))
    seen = []
    _rf = OW.real_filer
    OW.real_filer = lambda todo, conf: (seen.append((OW.beat_deadline(), sorted(a["name"] for a in todo))),
                                        dict({a["name"]: None for a in todo}, _publish="published"))[1]
    out = OW.file_held_detached(now=now + 60)
    OW.real_filer = _rf
    st = json.loads((od / "alarms.json").read_text())
    cur = [v for k, v in st.items() if k.endswith(":sense.families_blind")]
    check("an-alarm-pass-in-a-beat-files-nothing-inside-it: file-held files the held crossing and says the queued note",
          len(seen) == 1 and seen[0][0] is None and "note:X:y.z" in seen[0][1]
          and any(n.startswith("OPS_SENSE_FAMILY_READING_RESTORE_") for n in seen[0][1])
          and cur and cur[0].get("state") == "OPEN" and OW.queued_notes(st) == [], (seen, cur, out))
    os.environ.pop("METRONOME_DEADLINE", None)
    os.environ["RM_OPS_WATCH_DIR"] = str(_TMP / "ops")


def t_an_unreadable_series_is_not_blind():
    """2026-11-24 08:18 PST: 9p reads of /mnt/d failed with ENOMEM, read_series returned [] for 5 families that had
    read 1 to 11 min before, and the pass alarmed them as "no record in the series window"
    (OPS_SENSE_FAMILY_READING_RESTORE_XAOE)."""
    import builtins
    import errno
    os.environ["RM_OPS_WATCH_DIR"] = str(_TMP / "ops_unreadable")
    store = _TMP / "ops_unreadable"
    tu = time.time() - 3600
    OW.run(now=tu, rules=rules)                    # a whole pass: every family read now
    bad = {str(OW.series_path("disk")), str(OW.series_path("timers"))}
    real_open = builtins.open

    def enomem_open(f, *a, **k):
        if str(f) in bad:
            raise OSError(errno.ENOMEM, "Cannot allocate memory", str(f))
        return real_open(f, *a, **k)
    filed = []

    def filer(todo, conf):
        filed.extend(todo)
        return dict({a["name"]: None for a in todo}, _publish="published")
    OW.open = enomem_open
    try:
        OW.run(now=tu + 120, rules=rules, families=["flow"], compose=True, filer=filer)
    finally:
        del OW.open
    st = json.loads((store / "status.json").read_text())
    bp = st["points"].get("sense.families_blind") or {}
    why = str(bp.get("why"))
    check("an-unreadable-series-is-not-blind: the count reads UNMEASURED, naming each family and its error",
          bp.get("m") == "UNMEASURED" and "disk" in why and "timers" in why and "Cannot allocate memory" in why
          and "no record in the series window" not in why, bp)
    check("an-unreadable-series-is-not-blind: no blind alarm is filed on a read that failed",
          not [a for a in filed if a.get("key") == "sense.families_blind"], [a.get("name") for a in filed])
    dw = str((st["points"].get("disk._collector") or {}).get("why"))
    check("an-unreadable-series-is-not-blind: the family's carried points say its series could not be read",
          "could not read" in dw and "round robin has not reached it" not in dw, dw)
    OW.run(now=tu + 240, rules=rules, families=["flow"], compose=True, filer=filer)
    st = json.loads((store / "status.json").read_text())
    bp = st["points"].get("sense.families_blind") or {}
    check("an-unreadable-series-is-not-blind: once the series reads again, the count is a measured 0",
          bp.get("m") == "MEASURED" and bp.get("v") == 0, bp)
    OW.series_path("pager").unlink()               # a missing file is the empty set: looked, found no record
    OW.run(now=tu + 360, rules=rules, families=["flow"], compose=True, filer=filer)
    st = json.loads((store / "status.json").read_text())
    bp = st["points"].get("sense.families_blind") or {}
    check("an-unreadable-series-is-not-blind: a family with no series file still counts as blind (no record)",
          bp.get("m") == "MEASURED" and bp.get("v") == 1 and "pager no record in the series window"
          in str((bp.get("x") or {}).get("cause")), bp)
    os.environ["RM_OPS_WATCH_DIR"] = str(_TMP / "ops")


def main():
    for t in (t_a_family_left_unread_raises_the_blind_alarm,
              t_a_blind_familys_points_say_why,
              t_the_alarm_family_joins_when_it_is_blind,
              t_a_killed_pass_leaves_its_stage,
              t_tps_reads_only_the_recent_segments,
              t_the_week_of_commits_is_read_once,
              t_few_old_progress_names_are_restatted,
              t_codex_skips_day_folders_past_the_lookback,
              t_the_ledger_and_the_stamps_are_read_once,
              t_a_light_pass_files_nothing_inside_the_beat,
              t_an_alarm_pass_in_a_beat_files_nothing_inside_it,
              t_an_unreadable_series_is_not_blind):
        try:
            t()
        except (Exception, SystemExit) as e:  # noqa: BLE001  a test that raises is a red, named
            check("%s raised %s: %s" % (t.__name__, type(e).__name__, e), False)
    print("selftest_ops_sense_blind: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
