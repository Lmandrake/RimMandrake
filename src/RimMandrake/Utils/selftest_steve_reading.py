#!/usr/bin/env python3
"""selftest_steve_reading.py: one test per promise on design/specs/2026-11-24-fleet-now-stevedesktop/boundary.md.

Offline, on fixtures: no ssh, no Windows, no /mnt/d.
    python3 src/RimMandrake/Utils/selftest_steve_reading.py      exit 0 all pass, 1 a test failed
"""
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import steve_reading as R  # noqa: E402

NOW = 1793741698.0


def iso(t):
    return R.time.strftime("%Y-%m-%dT%H:%M:%SZ", R.time.gmtime(t))


def lockrow(g, state, seat=None, purpose=None, **kw):
    return dict({"game": g, "state": state, "seat": seat, "purpose": purpose, "line": state}, **kw)


def good():
    return {"up": "20000", "load": "0.5", "cores": "18", "ram": "1000 64000", "disk": "900 1000", "game": "1", "claude": "2",
            "gpu": "NVIDIA GeForce RTX 2080 Ti, 27, 4400, 11264", "stat": "cpu 10 0 10 80 0 0 0 0 0 0",
            "locks_json": json.dumps({"out": json.dumps({"games": [lockrow("a", "HELD", "RUNNER", "testq J-run0.a1"), lockrow("b", "FREE")]})}),
            "status_json": json.dumps({"out": "Steve1 running pid 29576 port 5174\nSteve2 stopped port 5175\n"}),
            "services_json": json.dumps({"out": "testq-J-run0_a1.service loaded active running lane\ndbus.service loaded active running dbus\n"
                                                "list-item-FlowWorks.service loaded active running item\n"})}


def job(i, **kw):
    return dict({"id": i, "mod": "FlowWorks", "purpose": "guard", "selector": {"chains": ["water", "power"]}, "submitted": iso(NOW - 120)}, **kw)


class Fake(R.Env):
    """Every door to the world is shut unless the fixture opens it."""

    def __init__(self):
        self.clock, self.calls, self.fail, self.reading = NOW, [], False, good()
        self.files = {R.TESTQ + "/running/r0.json": {"job": job("J-run0"), "sent": iso(NOW - 60), "attempt": "J-run0.a1", "host": "stevedesktop"},
                      R.TESTQ + "/running/r9.json": {"job": job("J-arch"), "sent": iso(NOW - 60), "attempt": "J-arch.a1", "host": "archmagi"},
                      R.TESTQ + "/pending/p0.json": job("J-wait0", lane="stevedesktop")}
        self.dirs = {R.TESTQ + "/running": ["r0.json", "r9.json"], R.TESTQ + "/pending": ["p0.json"]}

    def now(self):
        return self.clock

    def run(self, argv, timeout=20):
        raise R.Unmeasured("no commands in a selftest: %s" % argv[0])

    def tailscale_status(self):
        raise R.Unmeasured("no tailscale in a selftest")

    def port_open(self, host, port=22):
        return not self.fail

    def read_json(self, path):
        if path not in self.files:
            raise OSError("no such file " + path)
        return self.files[path]

    def listdir(self, path):
        if path not in self.dirs:
            raise OSError("no dir " + path)
        return self.dirs[path]

    def steve_probe(self):
        self.calls.append("ssh")
        if self.fail:
            raise R.Unmeasured("ssh exited 255: no route")
        return "\n".join("%s=%s" % kv for kv in self.reading.items()) + "\n"

    def write_atomic(self, path, data):
        self.files[path] = json.loads(data)


def view_of(env):
    """The view one due probe writes."""
    env.files.get(R.STEVE_CACHE, {}).pop("t", None) if isinstance(env.files.get(R.STEVE_CACHE), dict) else None
    R.probe_steve(env)
    return env.files[R.STEVE_CACHE]["view"]


def game(view, name):
    return {r["name"]: r for r in view["games"]["rows"]}[name]


def t_steve_games_up_and_driver():
    v = view_of(Fake())
    a, b = game(v, "Steve1"), game(v, "Steve2")
    assert a["up"] is True and a["driver"] == "RUNNER" and a["for"] == "testq J-run0.a1", a
    assert a["job"] == "FlowWorks guard; chains water,power", a
    assert b["up"] is False and b["driver_state"] == "FREE" and b["driver"] is None, b
    e = Fake()
    e.reading["locks_json"] = json.dumps({"out": "{broken JSON"})
    v = view_of(e)
    assert all(g["driver_state"] is None and "JSON" in g["driver_why"] for g in v["games"]["rows"]), v["games"]
    assert game(v, "Steve1")["up"] is True and v["machine"]["load1"] == 0.5, "the machine and process readings survive a broken lock reading"
    e = Fake()
    e.reading["status_json"] = json.dumps({"out": "Steve1 running pid 29576 port 5174\n"})
    assert game(view_of(e), "Steve2")["up"] is False, "a game a successful status omits is down"


def t_steve_jobs_by_name():
    v = view_of(Fake())["jobs"]
    assert v["running"] == [{"name": "FlowWorks guard; chains water,power", "where": "Steve1", "since": NOW - 60, "id": "J-run0"}], v
    assert [(r["where"], r["since"], r["id"]) for r in v["queued"]] == [("either game", NOW - 120, "J-wait0")], v
    for lane, word in (("any", "any machine"), (None, "lane UNMEASURED")):
        e = Fake()
        e.files[R.TESTQ + "/pending/p0.json"]["lane"] = lane
        assert [r["where"] for r in view_of(e)["jobs"]["queued"]] == [word], (lane, word)
    e = Fake()
    e.dirs = {R.TESTQ + "/running": [], R.TESTQ + "/pending": []}
    v = view_of(e)["jobs"]
    assert v["running"] == [] and v["queued"] == [] and v["running_why"] is None and v["queued_why"] is None, v


def t_steve_services_in_view():
    v = view_of(Fake())
    assert v["services"] == ["list-item-FlowWorks.service"] and v["services_why"] is None, v["services"]
    for text, want, why in ((json.dumps({"out": "dbus.service loaded active running bus\n"}), [], None),
                            (json.dumps({"why": "systemctl exited 1: no bus"}), None, "no bus"),
                            (json.dumps({"out": None}), None, "readable services_json"),
                            (json.dumps({"out": "what is this\n"}), None, "broken systemctl")):
        e = Fake()
        e.reading["services_json"] = text
        v = view_of(e)
        assert v["services"] == want and ((why or "") in (v["services_why"] or "")) and bool(why) == bool(v["services_why"]), (text, v["services"], v["services_why"])


def t_steve_every_reading_has_its_time():
    v = view_of(Fake())
    assert v["written_at"] == NOW and v["machine"]["observed_at"] == NOW and v["games"]["observed_at"] == NOW and v["jobs"]["observed_at"] == NOW


def t_steve_unread_is_unknown_with_cause():
    # a failed ssh keeps the last good numbers in the cache, and the view withholds them once they are old
    e = Fake()
    view_of(e)
    e.fail, e.clock = True, NOW + R.STEVE_STALE + 1
    v = view_of(e)
    c = e.files[R.STEVE_CACHE]
    assert c["good"]["load"] == "0.5" and c["routes"]["wsl"] is False and "no route" in c["why"], c
    assert "no route" in v["machine"]["unknown"] and v["machine"]["last_at"] == NOW and "load1" not in v["machine"], v["machine"]
    assert "unknown" in v["games"] and v["services"] is None and v["services_why"] and len(v["jobs"]["running"]) == 1, v
    e.fail = False
    e.clock += R.PROBE_EVERY + 1
    v = view_of(e)
    assert "why" not in e.files[R.STEVE_CACHE] and v["machine"]["load1"] == 0.5, "a returning ssh clears the failure"
    # a status or lock reading of the wrong shape is never DOWN, FREE or empty
    for output in ({"out": ""}, {"out": "unexpected output"}, {"why": "process list denied"}):
        e = Fake()
        e.reading["status_json"] = json.dumps(output)
        v = view_of(e)
        assert all(g["up"] is None and g["up_why"] for g in v["games"]["rows"]), (output, v["games"])
    for games in ("broken shape", [lockrow("a", "FREE"), lockrow("a", "FREE")], [lockrow("a", "ODD")]):
        e = Fake()
        e.reading["locks_json"] = json.dumps({"out": json.dumps({"games": games})})
        assert all(g["driver_state"] is None and "broken game lock JSON" in g["driver_why"] for g in view_of(e)["games"]["rows"]), games
    e = Fake()
    e.reading["locks_json"] = json.dumps({"out": json.dumps({"games": [lockrow("a", "UNKNOWN", cause="unreadable lock")]})})
    v = view_of(e)
    assert game(v, "Steve1")["driver_why"] == "unreadable lock" and "omitted" in game(v, "Steve2")["driver_why"], v["games"]
    # a lane folder that is missing, or holds a broken job, is null with its cause, never an empty list
    e = Fake()
    del e.dirs[R.TESTQ + "/pending"]
    e.files[R.TESTQ + "/running/r0.json"] = {"job": "broken"}
    v = view_of(e)["jobs"]
    assert v["queued"] is None and "no dir" in v["queued_why"] and v["running"] is None and "broken job record" in v["running_why"], v
    e.reading = good()
    assert "UNMEASURED" in game(view_of(e), "Steve1")["job"], "an unreadable lane leaves the driver's job UNMEASURED"
    # unreadable figures are left out and named, never 0
    e = Fake()
    e.reading.update(ram="garbage", gpu="none", load="x")
    m = view_of(e)["machine"]
    assert not {"mem_free_pct", "gpu_pct", "load1"} & set(m) and {"ram", "gpu", "load", "cpu_pct"} <= {x.split()[0] for x in m["issues"]}, m
    # a broken cache file is replaced, not trusted
    e = Fake()
    e.files[R.STEVE_CACHE] = ["broken cache"]
    assert view_of(e)["machine"]["load1"] == 0.5
    # the game count is omitted when the process list fails
    assert "if t=$(timeout 5" in R.STEVE_SCRIPT and "</dev/null" in R.STEVE_SCRIPT


def t_steve_one_ssh_per_probe():
    e = Fake()
    R.probe_steve(e)
    e.clock += R.PROBE_EVERY - 1
    R.probe_steve(e)
    assert e.calls == ["ssh"], "no second ssh inside PROBE_EVERY: %s" % e.calls
    e.clock += 2
    R.probe_steve(e)
    assert e.calls == ["ssh", "ssh"], e.calls
    assert not re.search(r"^\s*ssh\b", R.STEVE_SCRIPT, re.M), "the probe opens no further ssh"
    assert all(w in R.STEVE_SCRIPT for w in ("game_lock.py", "game_instance.py", "services_json", "RM_HOST", "~/rm/runner"))
    # the Python body of the probe, run here with fixture programs on PATH
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(d + "/rm/runner")
        for name, body in (("python3", "import json, sys\nprint(json.dumps({'games': []}) if 'game_lock.py' in sys.argv[1] else 'Steve1 stopped port 5174')\n"),
                           ("systemctl", "print('dbus.service loaded active running bus')\n")):
            with open(d + "/" + name, "w") as f:
                f.write("#!" + sys.executable + "\n" + body)
            os.chmod(d + "/" + name, 0o755)
        body = R.STEVE_SCRIPT.split("python3 - <<'PY'\n", 1)[1].rsplit("\nPY", 1)[0]
        body = body.replace("os.path.expanduser('~/rm/runner')", repr(d + "/rm/runner"))
        run = lambda: R.parse_probe(subprocess.run([sys.executable, "-c", body], env=dict(os.environ, PATH=d), capture_output=True, text=True).stdout)  # noqa: E731
        got = run()
        assert all("out" in json.loads(got.get(k, "{}")) for k in ("locks_json", "status_json", "services_json")), got
        os.rmdir(d + "/rm/runner")
        got = run()
        assert all("why" in json.loads(got[k]) for k in ("locks_json", "status_json")) and "out" in json.loads(got["services_json"]), got


def t_steve_view_for_augur():
    e = Fake()
    v = view_of(e)
    m = v["machine"]
    assert v["schema"] == "augur.remote_host/1" and v["host"] == "SteveDesktop" and e.files[R.STEVE_CACHE]["view"] == v
    assert m["load1"] == 0.5 and m["ncpu"] == 18 and abs(m["mem_free_pct"] - 98.4) < 0.1 and m["gpu_pct"] == 27.0 and m["agents"] == 2, m
    assert m["cpu_pct"] is None and any("cpu_pct" in x for x in m["issues"]), "one sample is no CPU rate"
    # I/O wait is not busy; guest time is inside user time
    e = Fake()
    e.reading["stat"] = "cpu 100 0 0 0 0 0 0 0 0 0"
    view_of(e)
    e.clock += R.PROBE_EVERY + 1
    e.reading["stat"] = "cpu 110 0 0 0 90 0 0 0 10 0"
    assert view_of(e)["machine"]["cpu_pct"] == 10
    real, R.collect_steve_games = R.collect_steve_games, lambda *a, **k: 1 / 0
    try:
        e = Fake()
        v = view_of(e)
    finally:
        R.collect_steve_games = real
    assert "ZeroDivisionError" in v["unknown"] and e.files[R.STEVE_CACHE]["t"] == NOW, "the probe still writes its file"


def t_steve_check_tells_old_unread_and_decoded_apart():
    with tempfile.TemporaryDirectory() as d:
        p = d + "/s.json"
        out = subprocess.run
        run = lambda: out([sys.executable, "-c", "import sys; sys.path.insert(0, %r); import steve_reading as R; sys.exit(R.check(%r))" % (HERE, p)], capture_output=True, text=True)  # noqa: E731
        r = run()
        assert r.returncode == 1 and "UNMEASURED" in r.stdout, r
        with open(p, "w") as f:
            json.dump({"view": {"machine": {"load1": 1}}}, f)
        r = run()
        assert r.returncode == 0 and "decoded" in r.stdout, r
        os.utime(p, (1, 1))
        r = run()
        assert r.returncode == 1 and "STALE" in r.stdout, r
        with open(p, "w") as f:
            json.dump({"view": {"machine": {"unknown": "no route"}}}, f)
        r = run()
        assert r.returncode == 1 and "no route" in r.stdout, r


def main():
    bad = 0
    tests = [t_steve_games_up_and_driver, t_steve_jobs_by_name, t_steve_services_in_view, t_steve_every_reading_has_its_time,
             t_steve_unread_is_unknown_with_cause, t_steve_one_ssh_per_probe, t_steve_view_for_augur,
             t_steve_check_tells_old_unread_and_decoded_apart]
    for t in tests:
        try:
            t()
            print("PASS %s" % t.__name__)
        except Exception as e:  # noqa: BLE001 - a crash of one promise's test is that promise's failure
            bad += 1
            print("FAIL %s %s: %s" % (t.__name__, type(e).__name__, e))
    print("FAILED %d" % bad if bad else "ALL PASS (%d)" % len(tests))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
