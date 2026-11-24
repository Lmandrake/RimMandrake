#!/usr/bin/env python3
"""Telemetry takes a game name: one test per promise of design/specs/2026-11-23-telemetry-any-game/boundary.md.
Offline: real ingest, real CLI verbs and the real pull/serve pair (a local subprocess in place of ssh), against fixture
streams in a temp dir with a fake VictoriaMetrics that honours the game filter.

  python3 src/RimMandrake/Utils/telemetry/selftest_telemetry_games.py            offline
  python3 src/RimMandrake/Utils/telemetry/selftest_telemetry_games.py --live     + `telemetry games` on this machine
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ["RM_HOST"] = "archmagi"          # the store's machine, whatever box runs this
for _k in ("RM_GAME_INSTANCE", "TELEMETRY_STORE_SSH"):
    os.environ.pop(_k, None)
FAILS: list[str] = []
N = 0
NAMES = ("ArchBig", "ArchSmall", "Steve1", "Steve2")


def check(name, cond, detail=""):
    global N
    N += 1
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else f"  -- {detail}"))
    if not cond:
        FAILS.append(name)


def iso(ts):
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(ts)) + ".000Z"


def w(path, rows, mode="a"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, mode, encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


def sample(ts, sess, tps, **kw):
    return {"kind": "sample", "utc": iso(ts), "session": sess, "tps": tps, "ratio": 1.0, "dTicks": 300, "dReal": 5,
            "mult": 1, "state": "run", "tickMs": 3.0, **kw}


class FakeVM:
    """Keeps what VMSink posts and answers store.vm_query with the label filter VM's extra_filters[] applies."""
    def __init__(self):
        self.lines = []

    def __call__(self, body):
        self.lines.extend(json.loads(x) for x in body.decode().splitlines() if x)

    def query(self, expr, start=None, end=None, step=None, url=None, game=None):
        import games
        name = re.match(r"\w+", expr).group(0)
        rx = games.label_re(game) if game else ".*"
        by: dict = {}
        for x in self.lines:
            if x["metric"]["__name__"] == name and re.fullmatch(rx, x["metric"].get("game", "")):
                by.setdefault(json.dumps(x["metric"], sort_keys=True), []).append(
                    [x["timestamps"][0] / 1000, str(x["values"][0])])
        return {"data": {"result": [{"metric": json.loads(k), "values": v, "value": v[-1]} for k, v in by.items()]}}


class World:
    def __init__(self):
        self.tmp = tempfile.mkdtemp(prefix="telemetry_games_")
        j = os.path.join
        self.dirs = {"archmagi": j(self.tmp, "jb_a"), "archmagi.b": j(self.tmp, "jb_b"),
                     "stevedesktop": j(self.tmp, "inbox", "games", "stevedesktop", "a"),
                     "stevedesktop.b": j(self.tmp, "inbox", "games", "stevedesktop", "b")}
        self.c = {"root": self.tmp, "db": j(self.tmp, "events.db"), "raw": j(self.tmp, "raw"),
                  "state": j(self.tmp, "state"), "inbox": j(self.tmp, "inbox"), "logs": j(self.tmp, "logs"),
                  "archive": j(self.tmp, "arch", "x"), "jawabench": self.dirs["archmagi"], "game_dirs": self.dirs,
                  "bridge_calls": j(self.tmp, "scratch", "bridge_calls.jsonl"), "artpipe": j(self.tmp, "art"),
                  "mirror": j(self.tmp, "mirror"), "vm_url": "http://fake", "game_mods": j(self.tmp, "Mods"),
                  "modsconfig": j(self.tmp, "ModsConfig.xml"), "dirs": {}, "volumes": {},
                  "vhdx": j(self.tmp, "none.vhdx"), "ops_watch_series": j(self.tmp, "ops")}
        os.makedirs(self.c["state"], exist_ok=True)
        w(j(self.tmp, "cfg.json"), [self.c], "w")
        os.environ["TELEMETRY_CONFIG"] = j(self.tmp, "cfg.json")
        import tcommon
        tcommon.reset_cfg()
        import store
        self.vm = FakeVM()
        store.vm_query = self.vm.query
        store.vm_get = lambda *a, **k: b"{}"
        import telemetryd
        self.d = telemetryd.Daemon(store.VMSink(post=self.vm))
        self.now = time.time()

    def seg(self, key, sess, pid, name=None):
        return os.path.join(self.dirs[key], "tps", name or f"tps_20261124T000000Z_{sess}_{pid}_000.jsonl")

    def step(self):
        self.d.step(force=True)

    def pulled(self, machine="stevedesktop", at=None, error=None, pids=(), games=None, skew=0.0, last_ok=None):
        at = self.now if at is None else at
        p = os.path.join(self.c["state"], "games_pull.json")
        d = json.load(open(p)) if os.path.exists(p) else {}
        d[machine] = {"last_try": at, "last_ok": at if error is None else last_ok, "error": error, "skew": skew,
                      "pids": None if pids is None else list(pids),
                      "games": games or {"a": {"state": "ok"}, "b": {"state": "ok"}}}
        json.dump(d, open(p, "w"))

    def cli(self, *argv):
        import cli
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                rc = cli.main(list(argv))
            except SystemExit as e:
                rc = e.code if isinstance(e.code, int) else 1
                if not isinstance(e.code, int) and e.code is not None:
                    print(e.code, file=err)
        return rc, out.getvalue() + err.getvalue()


def four_games(W):
    import host
    t = W.now - 20
    pids = {"archmagi": 11, "archmagi.b": 22, "stevedesktop": 33, "stevedesktop.b": 44}
    for i, (k, pid) in enumerate(pids.items()):
        s = f"{i}{i}aaaaaa{k.replace('.', '')}"
        w(W.seg(k, s, pid), [{"kind": "session", "utc": iso(t - 5), "session": s, "modDigest": f"m{i}"},
                             sample(t, s, 100 + i),
                             {"kind": "incident", "utc": iso(t), "session": s, "type": "stall", "gapS": 3 + i}])
    port = {"archmagi": 5174, "archmagi.b": 5175}
    for k, p in port.items():
        w(W.c["bridge_calls"], [
            {"ev": "start", "cid": "c" + k, "tool": "jawa/" + k, "t": iso(t), "endpoint": f"127.0.0.1:{p}"},
            {"ev": "end", "cid": "c" + k, "status": "ok", "ms": 5, "success": True, "t": iso(t)}])
    for k, p in (("stevedesktop", 5174), ("stevedesktop.b", 5175)):
        w(os.path.join(W.tmp, "inbox", "games", "stevedesktop", "machine", "bridge_calls.jsonl"), [
            {"ev": "start", "cid": "c" + k, "tool": "jawa/" + k, "t": iso(t), "endpoint": f"127.0.0.1:{p}"},
            {"ev": "end", "cid": "c" + k, "status": "ok", "ms": 5, "success": True, "t": iso(t)}])
    W.pulled(pids=(33, 44))
    host.process_pids = lambda names: {"rimworldwin64.exe": [11, 22]}
    W.step()


# ---------------------------------------------------------------- promises

def t_a_game_name_reads_that_games_rows_and_no_others(W):
    four_games(W)
    for i, n in enumerate(NAMES):
        for typed in (n, n.lower(), n.upper()):
            rc, o = W.cli("query", "rm_game_tps", "--game", typed)
            check(f"query --game {typed} reads {n} only", rc == 0 and f"last={100 + i}" in o
                  and not any(f"last={100 + k}" in o for k in range(4) if k != i), o)
        rc, o = W.cli("events", "--kind", "incident", "--game", n, "--detail")
        check(f"events --game {n}: its incident only", rc == 0 and f'"gapS":{3 + i}' in o
              and not any(f'"gapS":{3 + k}' in o for k in range(4) if k != i), o)
        rc, o = W.cli("bridge", "--game", n, "--since", "1h")
        key = ["archmagi", "archmagi.b", "stevedesktop", "stevedesktop.b"][i]
        tools = re.findall(r"jawa/([\w.]+)", o)
        check(f"bridge --game {n}: its calls only", rc == 0 and tools == [key], o)
        rc, o = W.cli("at", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(W.now - 20)), "--game", n)
        check(f"at --game {n}: its series, events and calls only", rc == 0 and f"med={100 + i}" in o
              and not any(f"med={100 + k}" in o for k in range(4) if k != i) and "bridge calls: 1" in o
              and o.count("incident") == 1, o)
    rc, o = W.cli("query", "rm_game_tps", "--game", "stevedesktop.b")
    check("an old key reaches the same rows", rc == 0 and "last=103" in o and "last=102" not in o, o)
    rc, o = W.cli("query", "rm_game_tps")
    check("no --game: every game, each line labelled", rc == 0 and all(f"game={n}" in o for n in NAMES), o)
    import games
    check("ArchBig's rows from before the label are ArchBig's and nobody else's",
          re.fullmatch(games.label_re("ArchBig"), "") and not re.fullmatch(games.label_re("Steve1"), ""))


def t_an_unknown_game_is_refused_by_name(W):
    four_games(W)
    for argv in (["query", "rm_game_tps"], ["events"], ["bridge"], ["at", "12:00"], ["flight"], ["exc"],
                 ["around", "deploy:1"], ["tier", "test"], ["series"]):
        rc, o = W.cli(*argv, "--game", "Steve3")
        check(f"{argv[0]} --game Steve3 refused by name", rc == 2 and "Steve3" in o and all(n in o for n in NAMES), (rc, o))
    rc, o = W.cli("games", "Steve3")
    check("games Steve3 refused by name", rc == 2 and "Steve3" in o and all(n in o for n in NAMES), (rc, o))


def t_an_unreachable_machine_reads_could_not_look_with_its_cause(W):
    W.pulled(error="ssh exit 255: connect timed out", last_ok=None)
    W.step()
    for argv in (["games", "Steve1"], ["query", "rm_game_tps", "--game", "Steve1"], ["events", "--game", "Steve1"],
                 ["bridge", "--game", "Steve1"], ["flight", "--game", "Steve1"], ["exc", "--game", "Steve1"]):
        rc, o = W.cli(*argv)
        check(f"{argv[0]}: could not look, exit 3, with the cause",
              rc == 3 and "COULD NOT LOOK" in o and "connect timed out" in o, (rc, o))
        check(f"{argv[0]}: no zero and no empty list", not re.search(r"\b0 (shown|series|completed|calls)|\(0\)", o), o)
    four_games(W)
    W.pulled(error="ssh exit 255: connect timed out", last_ok=W.now - 900)
    rc, o = W.cli("query", "rm_game_tps", "--game", "Steve1")
    check("rows held from before are shown, with the cause and their age",
          "last=102" in o and "COULD NOT LOOK" in o and re.search(r"last look 15m ago", o), o)
    W.pulled(at=W.now - 3600)
    rc, o = W.cli("games", "Steve1")
    check("a pull that stopped running is could not look, not a reading", rc == 3 and "pull" in o and "1.0h" in o, (rc, o))
    W.pulled(games={"a": {"state": "error", "error": "no RM_GAME_USERDATA"}, "b": {"state": "ok"}})
    rc, o = W.cli("games", "Steve1")
    check("a machine reached whose game could not be found is could not look", rc == 3 and "no RM_GAME_USERDATA" in o, (rc, o))
    hb = os.path.join(W.c["state"], "heartbeat.json")
    d = json.load(open(hb))
    d["at"] -= 900
    json.dump(d, open(hb, "w"))
    rc, o = W.cli("games", "ArchBig")
    check("a dead daemon is could not look for a local game", rc == 3 and "telemetryd" in o, (rc, o))
    os.remove(os.path.join(W.c["state"], "games_pull.json"))
    json.dump({**d, "at": time.time()}, open(hb, "w"))
    rc, o = W.cli("games", "Steve2")
    check("a pull that never ran is could not look", rc == 3 and "COULD NOT LOOK" in o, (rc, o))
    rc, o = W.cli("games")
    check("games: the list still shows the games that could be read", "ArchBig" in o and "up" in o and rc == 3, (rc, o))


def t_a_game_with_no_data_yet_reads_no_data_yet(W):
    W.pulled(pids=(33,), games={"a": {"state": "absent"}, "b": {"state": "ok"}})
    W.step()
    for n in ("Steve1", "Steve2", "ArchSmall"):
        rc, o = W.cli("games", n)
        check(f"games {n}: no data yet, exit 4", rc == 4 and "no data yet" in o and "COULD NOT LOOK" not in o, (rc, o))
        rc, o = W.cli("query", "rm_game_tps", "--game", n)
        check(f"query {n}: no data yet, exit 4", rc == 4 and "no data yet" in o, (rc, o))
        rc, o = W.cli("bridge", "--game", n)
        check(f"bridge {n}: no data yet, exit 4, no zero", rc == 4 and not re.search(r"\b0 completed", o), (rc, o))


def t_a_game_that_is_down_reads_down_with_the_age_of_its_last_row(W):
    four_games(W)
    W.pulled(pids=())
    rc, o = W.cli("games", "Steve1")
    check("the process that wrote the newest row is gone: down, with an age", rc == 0 and "down" in o
          and re.search(r"newest row \d+s", o), (rc, o))
    W.pulled(pids=None)
    rc, o = W.cli("games", "Steve1")
    check("an unread process list is not down", rc == 0 and "process unread" in o and "down" not in o, (rc, o))
    import host
    host.process_pids = lambda names: {"rimworldwin64.exe": [22]}
    W.step()
    rc, o = W.cli("games", "ArchBig")
    check("a local game's process is read too", rc == 0 and "down" in o, (rc, o))
    rc, o = W.cli("games", "ArchSmall")
    check("and its neighbour stays up", rc == 0 and "up" in o and "down" not in o, (rc, o))


def t_every_answer_carries_its_age(W):
    four_games(W)
    for argv in (["query", "rm_game_tps"], ["events"], ["bridge"], ["flight"], ["exc"], ["at", "12:00"]):
        rc, o = W.cli(*argv, "--game", "Steve2")
        check(f"{argv[0]}: newest row's age and the last look's", re.search(r"newest row \d+s ago", o)
              and re.search(r"last look \d+s ago", o), o)
    W.pulled(pids=(33, 44), skew=10.0)
    _, o = W.cli("games", "Steve1")
    a = int(re.search(r"newest row (\d+)s", o).group(1))
    check("the age is corrected for the other machine's clock", 28 <= a <= 60, o)
    key = "game:Steve1"
    import store
    d = store.kv_get(W.d.con, key)
    store.kv_set(W.d.con, key, {**d, "ts": W.now - 400})
    W.d.con.commit()
    W.pulled(pids=(33, 44))
    _, o = W.cli("games", "Steve1")
    check("an old row of a game that is up reads STALE", "STALE" in o and re.search(r"newest row [67]m", o), o)


def t_one_games_alarm_state_never_mixes_with_anothers(W):
    four_games(W)
    s = "22aaaaaastevedesktop"
    w(W.seg("stevedesktop", s, 33), [{"kind": "incident", "utc": iso(W.now - 5), "session": s, "type": "stall", "gapS": 40}])
    W.step()
    al = json.load(open(os.path.join(W.c["state"], "alerts.json")))["alerts"]
    hit = [a for a in al if a["id"].startswith("stall")]
    check("Steve1's stall raises no alarm of the store's own game", not hit, al)
    check("it is an event of Steve1's", W.d.con.execute("SELECT COUNT(*) FROM events WHERE kind='incident' AND "
          "game='Steve1' AND detail LIKE '%\"gapS\":40%'").fetchone()[0] == 1)
    a0 = "00aaaaaaarchmagi"
    w(W.seg("archmagi", a0, 11), [{"kind": "incident", "utc": iso(W.now - 5), "session": a0, "type": "stall", "gapS": 30}])
    W.step()
    al = json.load(open(os.path.join(W.c["state"], "alerts.json")))["alerts"]
    check("ArchBig's stall still alarms, once", len([a for a in al if a["id"].startswith("stall")]) == 1, al)
    check("ArchBig's own state holds no stall of Steve1's",
          not any(i.get("gapS") == 40 for i in W.d.latest.get("incidents", [])), W.d.latest.get("incidents"))
    low = [sample(W.now - 130 + 5 * i, s, 10, ratio=0.1) for i in range(26)]
    w(W.seg("stevedesktop", s, 33), low)
    W.step()
    check("Steve1's low speed is not in ArchBig's speed history",
          not any(h[1] == 0.1 for h in W.d.latest["tps_hist"]), W.d.latest["tps_hist"][-2:])
    import analysis
    lat = {"game_running": True, "game_running_since": W.now - 4000}
    quiet = {"tps": {"last_row_ts": W.now - 4000}, "tps.archmagi.b": {"last_row_ts": W.now - 5}}
    ids = [a["id"] for a in analysis.evaluate(dict(lat), W.d.con, quiet, None, W.now)]
    check("ArchSmall alone is not 'ArchBig's record is silent'", "blind:tps" not in ids, ids)
    ids = [a["id"] for a in analysis.evaluate(dict(lat), W.d.con, {"tps": {"last_row_ts": W.now - 4000},
           "tps.stevedesktop": {"last_row_ts": W.now - 5}}, None, W.now)]
    check("another machine's rows do not hide a silent record here", "blind:tps" in ids, ids)


def far(tmp):
    """A stand-in for SteveDesktop: a folder of records and the argv that serves it without ssh."""
    root = os.path.join(tmp, "far")
    stub = os.path.join(root, "utils")
    os.makedirs(stub, exist_ok=True)
    with open(os.path.join(stub, "game_paths.py"), "w") as f:
        f.write("LOCALLOW = %r\n" % os.path.join(root, "a"))
    with open(os.path.join(stub, "game_instance.py"), "w") as f:
        f.write("import os\ndef data_dir(n):\n    return os.path.join(%r, n)\n" % root)
    with open(os.path.join(stub, "rmpaths.py"), "w") as f:
        f.write("import os\ndef rm_str(*a):\n    return os.path.join(%r, *a)\n" % os.path.join(root, "data"))
    return root, stub


def pull(stub, argv=None):
    import pull_games
    src = open(os.path.join(HERE, "games_serve.py")).read()
    return pull_games.pull("stevedesktop", argv or [sys.executable, "-c", src], cwd=stub)


def t_a_pull_copies_each_byte_once(W):
    import ingest
    root, stub = far(W.tmp)
    seg = os.path.join(root, "a", "JawaBench", "tps", "tps_20261124T000000Z_s1_33_000.jsonl")
    bc = os.path.join(root, "data", "scratch", "bridge_calls.jsonl")
    w(seg, [sample(W.now - 9, "s1", 50)])
    w(bc, [{"ev": "start", "cid": "q1", "tool": "t", "t": iso(W.now - 9), "endpoint": "127.0.0.1:5174"}])
    r = pull(stub)
    mine = os.path.join(W.dirs["stevedesktop"], "tps", os.path.basename(seg))
    mbc = os.path.join(W.tmp, "inbox", "games", "stevedesktop", "machine", "bridge_calls.jsonl")
    check("the first pull copies the whole record", r["error"] is None and open(mine).read() == open(seg).read()
          and open(mbc).read() == open(bc).read(), r)
    ino = os.stat(mine).st_ino
    w(seg, [sample(W.now - 4, "s1", 51)])
    n0 = r["bytes"]
    r = pull(stub)
    check("the next pull appends only what is new, in place", r["bytes"] == os.path.getsize(seg) - len(
        open(seg).readline()) and open(mine).read() == open(seg).read() and os.stat(mine).st_ino == ino and n0 > 0, r)
    r = pull(stub)
    check("nothing new copies nothing", r["bytes"] == 0 and r["error"] is None, r)
    old = os.stat(mbc).st_ino
    os.rename(bc, bc + ".1")
    w(bc, [{"ev": "end", "cid": "q1", "status": "ok", "ms": 3, "success": True, "t": iso(W.now - 3)}])
    r = pull(stub)
    check("a rotated file is renamed here, not copied again", os.stat(mbc + ".1").st_ino == old
          and r["bytes"] == os.path.getsize(bc) and open(mbc).read() == open(bc).read(), r)
    full = open(seg, "rb").read()
    w(seg, [sample(W.now - 3, "s1", 52), sample(W.now - 2, "s1", 53)])
    cut = open(os.path.join(HERE, "games_serve.py")).read().replace("CUT_AFTER = None", "CUT_AFTER = 40")
    r = pull(stub, [sys.executable, "-c", cut])
    check("a cut transfer is an error, keeping what arrived", r["error"] is not None
          and os.path.getsize(mine) == len(full) + 40, (r, os.path.getsize(mine), len(full)))
    r = pull(stub)
    check("and the next pull resumes it, byte for byte", r["error"] is None and open(mine).read() == open(seg).read(), r)
    os.remove(seg)
    w(seg + ".keep", [{"hold": "the inode"}])
    w(seg, [sample(W.now - 1, "s1", 99)])
    r = pull(stub)
    check("a replaced file is copied whole", open(mine).read() == open(seg).read(), r)
    r = pull(stub, [sys.executable, "-c", "import sys; sys.exit(255)"])
    st = json.load(open(os.path.join(W.c["state"], "games_pull.json")))["stevedesktop"]
    check("a failed route is recorded with its cause and keeps the last good look", "255" in st["error"] and st["last_ok"], st)
    r = pull(stub, [sys.executable, "-c", "print('motd: welcome'); import sys; sys.stdin.read()"])
    check("an answer that is not the serve's is an error, not an empty machine", r["error"], r)
    r = pull(stub)
    shutil.rmtree(os.path.join(root, "b"), ignore_errors=True)
    st = json.load(open(os.path.join(W.c["state"], "games_pull.json")))["stevedesktop"]
    check("a game with no record there is 'absent', not an error", st["games"]["b"]["state"] == "absent"
          and st["games"]["a"]["state"] == "ok", st)
    W.step()
    n = W.d.con.execute("SELECT ms, game FROM bridge_calls WHERE cid='q1'").fetchone()
    check("what was pulled is ingested as that game's", n is not None and n[0] == 3 and n[1] == "Steve1", n and tuple(n))
    S = {s.name: s for s in ingest.make_sources()}
    check("its points carry the game", any(x["metric"].get("game") == "Steve1" for x in W.vm.lines), sorted(S))


def t_the_tps_report_takes_a_game_name_too(W):
    """tps_record.py reads one game's record file by file; the same four answers."""
    sys.path.append(os.path.dirname(HERE))
    import tps_record
    four_games(W)

    def run(*argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                rc = tps_record.main(list(argv))
            except SystemExit as e:
                rc = e.code
        return rc, out.getvalue() + err.getvalue()
    for n, k in zip(NAMES, W.dirs):
        rc, o = run("--game", n.lower())
        check(f"tps_record --game {n} reads its folder", rc == 0 and f"[{os.path.join(W.dirs[k], 'tps')}]" in o, (rc, o))
    rc, o = run("--game", "Steve3")
    check("an unknown game is refused by name", rc == 2 and "Steve3" in o and "ArchSmall" in o, (rc, o))
    W.pulled(error="ssh exit 255", last_ok=W.now - 900)
    rc, o = run("--game", "Steve1")
    check("an unreachable machine is could not look", rc == 3 and "COULD NOT LOOK" in o and "255" in o, (rc, o))
    shutil.rmtree(W.dirs["archmagi.b"])
    rc, o = run("--game", "ArchSmall")
    check("a game with no record is no data yet", rc == 4 and "no data yet" in o, (rc, o))


def t_a_backlog_being_read_is_a_live_daemon(W):
    """The heartbeat moves between files, so a long first pass is never read as a dead telemetryd."""
    for i in range(3):
        w(W.seg("stevedesktop", f"b{i}", 33, f"tps_20261124T00000{i}Z_b{i}_33_000.jsonl"), [sample(W.now - 9, f"b{i}", 50)])
    beats = []
    hb = os.path.join(W.c["state"], "heartbeat.json")
    real = W.d.beat
    W.d.tailer.beat = lambda: (setattr(W.d, "beaten", 0.0), real(), beats.append(os.path.exists(hb)))
    W.d.tailer.pass_source([s for s in W.d.sources if s.game == "Steve1"][0])
    check("a beat before each file of a pass, with no step ended", beats == [True] * 3, beats)
    import telemetryd
    keep = telemetryd.write_json_atomic

    def denied(*a):
        raise PermissionError(5, "Access is denied")
    telemetryd.write_json_atomic = denied
    W.d.beaten = 0.0
    try:
        real()
        check("a heartbeat a reader holds open stops nothing and is tried again", W.d.beaten == 0.0)
    except OSError as e:
        check("a heartbeat a reader holds open stops nothing and is tried again", False, e)
    telemetryd.write_json_atomic = keep
    W.d.beaten = time.time()
    os.remove(hb)
    real()
    check("at most one write a period", not os.path.exists(hb))


def t_no_machine_path_or_game_is_hard_wired(W):
    import game_names
    import games
    import ingest
    bad = []
    for f in ("games.py", "pull_games.py", "games_serve.py", "ingest.py", "analysis.py", "cli.py", "telemetryd.py", "store.py"):
        for i, line in enumerate(open(os.path.join(HERE, f), encoding="utf-8"), 1):
            code = re.sub(r"#.*", "", line)
            if re.search(r"[\"'](ArchBig|ArchSmall|Steve[12]|stevedesktop)\b|sjlewis|RimTest|SteamLibrary", code):
                bad.append(f"{f}:{i}: {line.strip()}")
    check("no game, machine or path of another machine is written in the code", not bad, bad)
    keep = game_names.GAMES
    try:
        game_names.GAMES = keep + (("Steve3", "stevedesktop.c", "stevedesktop", "c"),)
        check("a fifth game gets a source", any(s.game == "Steve3" for s in ingest.make_sources()))
        rc, o = W.cli("games", "Steve3")
        check("a fifth game gets a reading", rc in (3, 4) and "Steve3" in o, (rc, o))
        rc, o = W.cli("games", "Steve9")
        check("and a place in the refusal", rc == 2 and "Steve3" in o, (rc, o))
    finally:
        game_names.GAMES = keep
    check("each game has exactly one record source", sorted(s.game for s in ingest.make_sources() if s.game) == sorted(NAMES))
    check("a third game's port reads as its key, never as another game's name",
          games.game_of_endpoint("archmagi", "127.0.0.1:5176") == "archmagi.c"
          and games.game_of_endpoint("archmagi", "junk") is None and games.game_of_endpoint("archmagi", None) is None)


def t_a_machine_without_the_store_asks_the_one_that_has_it(W):
    """The wrapper, run where the store's root is absent, with a fake ssh on PATH."""
    b = os.path.join(W.tmp, "bin")
    os.makedirs(b, exist_ok=True)
    cfgp = os.path.join(W.tmp, "nostore.json")
    json.dump({**W.c, "root": os.path.join(W.tmp, "absent")}, open(cfgp, "w"))

    def run(body):
        with open(os.path.join(b, "ssh"), "w") as f:
            f.write("#!/bin/sh\n" + body + "\n")
        os.chmod(os.path.join(b, "ssh"), 0o755)
        env = {**os.environ, "PATH": b + ":" + os.environ["PATH"], "TELEMETRY_CONFIG": cfgp, "RM_HOST": "stevedesktop"}
        r = subprocess.run([os.path.join(HERE, "telemetry"), "query", 'rm_game_tps{mult="1"}', "--game", "Steve1"],
                           capture_output=True, text=True, timeout=60, env=env)
        return r.returncode, r.stdout + r.stderr
    rc, o = run('echo "SSH $@"; exit 4')
    check("the command goes to the store's machine whole, quoting kept, and its exit code comes back",
          rc == 4 and "SSH" in o and """'rm_game_tps{mult="1"}'""" in o and "'--game' 'Steve1'" in o, (rc, o))
    rc, o = run("echo 'ssh: connect to host: timed out' >&2; exit 255")
    check("a store that cannot be reached is could not look, exit 3, with the cause",
          rc == 3 and "COULD NOT LOOK" in o and "timed out" in o, (rc, o))


def main():
    for fn in (
            t_a_game_name_reads_that_games_rows_and_no_others,
            t_an_unknown_game_is_refused_by_name,
            t_an_unreachable_machine_reads_could_not_look_with_its_cause,
            t_a_game_with_no_data_yet_reads_no_data_yet,
            t_a_game_that_is_down_reads_down_with_the_age_of_its_last_row,
            t_every_answer_carries_its_age,
            t_one_games_alarm_state_never_mixes_with_anothers,
            t_a_pull_copies_each_byte_once,
            t_the_tps_report_takes_a_game_name_too,
            t_a_backlog_being_read_is_a_live_daemon,
            t_no_machine_path_or_game_is_hard_wired,
            t_a_machine_without_the_store_asks_the_one_that_has_it,
    ):
        name = fn.__name__
        print(f"== {name[2:].replace('_', '-')}")
        W = None
        try:
            W = World()
            fn(W)
        except Exception as e:  # noqa: BLE001
            import traceback
            check(name[2:], False, f"{type(e).__name__}: {e}\n{traceback.format_exc()[-900:]}")
        finally:
            if W is not None:
                W.d.con.close()
                shutil.rmtree(W.tmp, ignore_errors=True)
            import ingest
            ingest._BRIDGE_OPEN.clear()
            ingest._BRIDGE_PARKED.clear()
            import importlib
            import host
            importlib.reload(host)
    if "--live" in sys.argv:
        r = subprocess.run([os.path.join(HERE, "telemetry"), "games"], capture_output=True, text=True, timeout=120,
                           env={k: v for k, v in os.environ.items() if k not in ("TELEMETRY_CONFIG", "RM_HOST")})
        print(r.stdout)
        check("live: every game of the map has a line", all(n in r.stdout for n in NAMES), r.stdout + r.stderr)
    print(f"\n{'OK' if not FAILS else 'FAILED'}: {N - len(FAILS)}/{N} passed")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
