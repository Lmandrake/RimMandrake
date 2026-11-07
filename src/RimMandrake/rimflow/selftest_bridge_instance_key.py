#!/usr/bin/env python3
"""selftest_bridge_instance_key.py - a second game has its own bridge lock: 'stevedesktop.b' beside 'stevedesktop'.

On a throwaway ledger and throwaway locks, as if this machine were SteveDesktop (RM_HOST). Nothing real is touched.
"""
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
CLI = os.path.join(HERE, "cli.py")
HG = os.path.join(HERE, "host_guard.py")
FAILS = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def main():
    tmp = tempfile.mkdtemp(prefix="rf_instancekey_")
    try:
        os.makedirs(os.path.join(tmp, "items"))
        a_lock, root = os.path.join(tmp, "a_lock.json"), os.path.join(tmp, "instances")
        b_lock = os.path.join(root, "b", "DRIVER_LOCK.json")
        base = {k: v for k, v in os.environ.items()
                if k not in ("RIMFLOW_SEAT", "AGENT_SEAT", "CLAUDE_SESSION_ID", "RM_HOST_GUARD_GEN", "RM_GAME_INSTANCE",
                             "GABP_SERVER_PORT", "GABP_TOKEN", "RIMFLOW_DRIVER_LOCK")}
        base.update(RIMFLOW_LEDGER=os.path.join(tmp, "events.jsonl"), RIMFLOW_ITEMS=os.path.join(tmp, "items"),
                    RIMFLOW_SHARED_BRIDGE=os.path.join(tmp, "shared.json"), RIMFLOW_PROBE="no-reading",
                    RM_HOST="stevedesktop", RM_INSTANCES_ROOT=root, RIMFLOW_DRIVER_LOCK=a_lock, PYTHONDONTWRITEBYTECODE="1")
        saved = dict(os.environ)
        os.environ.clear()
        os.environ.update(base)
        try:
            import model as M
            import host_guard as H
            import driver_lock as D
            for raw, want in (("stevedesktop", "stevedesktop"), ("stevedesktop.b", "stevedesktop.b"), ("SteveDesktop.B", "stevedesktop.b"),
                              ("stevedesktop.a", "stevedesktop"), (None, "archmagi"), ("archmagi", "archmagi")):
                check(M.bridge_host_key(raw) == want, "bridge key %r -> %s" % (raw, want))
            for raw in ("stevedesktop.", "stevedesktop.bb", "stevedesktop.1", "steve.b", "typo"):
                try:
                    M.bridge_host_key(raw)
                    check(False, "a typo'd key %r opens no imaginary lock" % raw)
                except M.SchemaError:
                    check(True, "a typo'd key %r opens no imaginary lock" % raw)
            check(M.split_bridge_host("stevedesktop.b") == ("stevedesktop", "b") and M.split_bridge_host("stevedesktop") == ("stevedesktop", None), "split")
            check(M.ambient_bridge_host() is None and H.local_host() == "stevedesktop", "nothing set: today's key")
            os.environ["RM_GAME_INSTANCE"] = "a"
            check(M.ambient_bridge_host() is None and H.local_host() == "stevedesktop", "instance a is today's key too")
            os.environ["RM_GAME_INSTANCE"] = "b"
            check(M.ambient_bridge_host() == "stevedesktop.b" and H.local_host() == "stevedesktop.b" and H.local_machine() == "stevedesktop", "RM_GAME_INSTANCE=b: this machine's b")
            del os.environ["RM_GAME_INSTANCE"]

            # the two ledgers' worth of world keep apart
            evs = [{"event": "bridge", "state": "taken", "host": "stevedesktop", "seat": "BENCH", "ts": "2026-11-07T00:00:00Z"},
                   {"event": "bridge", "state": "taken", "host": "stevedesktop.b", "seat": "FOUNDRY", "ts": "2026-11-07T00:00:01Z"}]
            world = M.World()
            for ev in evs:
                M._apply_itemless(ev, ev["seat"], world)
            check(world.bridge_hosts["stevedesktop"]["holder"] == "BENCH" and world.bridge_hosts["stevedesktop.b"]["holder"] == "FOUNDRY"
                  and world.bridge_holder is None, "a take of b moves neither a's holder nor Archmagi's")

            # remote: the same verbs, aimed at that game's lock on the far machine
            argv = H.remote_argv("stevedesktop.b", ["status"])
            check("RM_GAME_INSTANCE=b python3" in argv[-1] and argv[-2] == H.SSH_TARGETS["stevedesktop"], "remote b: %s" % argv[-1])
            check("RM_GAME_INSTANCE" not in H.remote_argv("stevedesktop", ["status"])[-1], "remote a sets nothing")
            older = subprocess.run(["bash", "-c", H.remote_argv("stevedesktop.b", ["status"])[-1].replace(H.RUNNER_DIR, tmp, 1)],
                                   capture_output=True, text=True, timeout=30)
            check(older.returncode == 2 and "no game_instance.py" in older.stdout, "a far clone older than the name refuses, never takes a's lock: %s" % older.stdout[:100])

            # the lock path: a typo cannot reach game a's lock; the env pin holds; a selftest's ledger redirect disables it
            pin = {k: os.environ.pop(k, None) for k in ("RIMFLOW_DRIVER_LOCK", "RIMFLOW_LEDGER")}
            os.environ["RM_GAME_INSTANCE"] = "b"
            check(D.lock_path() == b_lock and os.path.isdir(os.path.dirname(b_lock)), "RM_GAME_INSTANCE=b alone reaches b's own lock: %s" % D.lock_path())
            del os.environ["RM_GAME_INSTANCE"]
            check(D.lock_path() != b_lock, "nothing set: not b's lock")
            os.environ.update({k: v for k, v in pin.items() if v})

            with H.instance_env("b"):
                check(D.lock_path() == b_lock and H.local_host() == "stevedesktop.b", "instance_env aims this process at b")
            check(D.lock_path() == a_lock and "RM_GAME_INSTANCE" not in os.environ, "and restores it")
            with H.instance_env(None):
                check(D.lock_path() == a_lock, "the game this process already means changes nothing: a pinned lock stays pinned")
            os.environ.update(RM_GAME_INSTANCE="b", RIMFLOW_DRIVER_LOCK=b_lock)
            with H.instance_env(None):
                check("RM_GAME_INSTANCE" not in os.environ and "RIMFLOW_DRIVER_LOCK" not in os.environ, "a shell on b can name a's lock")
            check(os.environ.get("RM_GAME_INSTANCE") == "b" and os.environ.get("RIMFLOW_DRIVER_LOCK") == b_lock, "and is put back")
            os.environ.update(RIMFLOW_DRIVER_LOCK=a_lock)
            del os.environ["RM_GAME_INSTANCE"]
        finally:
            os.environ.clear()
            os.environ.update(saved)

        # two scripts, two games: each take excludes only its own game's other driver
        env_b = dict(base, RM_GAME_INSTANCE="b", RIMFLOW_DRIVER_LOCK=b_lock)
        other = json.dumps({"pid": 4242, "start": 7.0, "boot_id": "x", "platform": "wsl", "host": "SomeOtherBox"})

        def hg(env, *args):
            return subprocess.run([sys.executable, HG] + list(args), env=env, capture_output=True, text=True, timeout=60)
        r = hg(base, "take", "--seat", "RUNNER", "--for", "a's job", "--identity-json", other)
        check(r.returncode == 0 and os.path.exists(a_lock), "a script holds a's lock: %s" % r.stdout.strip()[:80])
        r = hg(env_b, "take", "--seat", "RUNNER", "--for", "b's job", "--identity-json", other.replace("4242", "4243"))
        check(r.returncode == 0 and os.path.exists(b_lock), "a's lock does not stop a take of b's: %s %s" % (r.stdout.strip()[:80], r.stderr[-120:]))
        r = hg(env_b, "take", "--seat", "BENCH", "--for", "second on b", "--identity-json", other.replace("4242", "4244"))
        check(r.returncode == 75 and "RUNNER" in r.stdout, "b's lock stops a second driver of b: %s" % r.stdout.strip()[:100])
        st = json.loads(hg(env_b, "status", "--json").stdout)
        check(st.get("host") == "stevedesktop.b" and st.get("path") == b_lock and st.get("state") == "HELD", "status under b reads b's lock: %s" % st.get("state"))
        r = hg(base, "release", "--seat", "RUNNER", "--identity-json", other)
        check(r.returncode == 0 and not os.path.exists(a_lock) and os.path.exists(b_lock), "releasing a's leaves b's")
        hg(env_b, "release", "--seat", "RUNNER", "--identity-json", other.replace("4242", "4243"))
        check(not os.path.exists(b_lock), "and b's releases on its own")

        # the CLI: the ledger, the guard and the mirror
        def rf(seat, *args, env=base):
            return subprocess.run([sys.executable, CLI] + list(args), env=dict(env, RIMFLOW_SEAT=seat), capture_output=True,
                                  text=True, timeout=120)
        mirror = os.path.join(tmp, "BRIDGE")
        r = rf("BENCH", "bridge", "take", "--host", "stevedesktop.b", "--for", "loop on b")
        check(r.returncode == 0 and os.path.exists(b_lock) and not os.path.exists(a_lock), "take --host stevedesktop.b takes b's lock alone: %s" % (r.stdout + r.stderr)[-200:])
        shards = glob.glob(os.path.join(tmp, "**", "*.jsonl"), recursive=True)   # the ledger is sharded by seat
        check(shards, "the ledger wrote somewhere: %s" % shards)
        last = [e for e in (json.loads(ln) for f in shards for ln in open(f)) if e.get("event") == "bridge"][-1]
        check(last.get("host") == "stevedesktop.b" and last.get("state") == "taken", "the event names the game")
        text = open(mirror).read()
        check("other   stevedesktop.b  BENCH" in text and "for: loop on b" in text and text.splitlines()[5].startswith("FREE"), "the mirror grows a line, under the same status line: %r" % text.splitlines()[5:])
        r = rf("FOUNDRY", "bridge", "take", "--host", "stevedesktop.b", "--for", "second")
        check(r.returncode != 0, "another seat is refused b")
        r = rf("FOUNDRY", "bridge", "take", "--host", "stevedesktop", "--for", "loop on a")
        check(r.returncode == 0 and os.path.exists(a_lock), "game a stays takeable beside it: %s" % (r.stdout + r.stderr)[-200:])
        r = rf("BENCH", "bridge", "who", "--host", "stevedesktop.b")
        check("stevedesktop.b bridge held by BENCH" in r.stdout and "stevedesktop.b HELD" in r.stdout, "who --host b: %s" % r.stdout[:160])
        check(M_bridge_gate(base, "BENCH", "stevedesktop.b") is None and M_bridge_gate(base, "BENCH", "stevedesktop") is not None, "bridge_gate is per game")
        env_b2 = dict(base, RM_GAME_INSTANCE="b", RIMFLOW_DRIVER_LOCK=b_lock)     # as `game_instance.py env b` exports it
        r = rf("BENCH", "bridge", "release", "--mine", env=env_b2)
        check("stevedesktop.b bridge released" in r.stdout and not os.path.exists(b_lock), "RM_GAME_INSTANCE=b with no --host means this machine's b: %s %s" % (r.stdout[-100:], r.stderr[-100:]))
        check("other   stevedesktop.b" not in open(mirror).read(), "a free game's line goes")
        r = rf("BENCH", "bridge", "take", "--for", "b by name", env=env_b2)
        check(r.returncode == 0 and os.path.exists(b_lock), "a host-less take under b takes b, never Archmagi's: %s" % (r.stdout + r.stderr)[-160:])
        check("stevedesktop.b" in r.stdout and rf("BENCH", "bridge", "release", "--mine", env=env_b2).returncode == 0, "and says so")
        rf("FOUNDRY", "bridge", "release", "--host", "stevedesktop")
        r = rf("BENCH", "bridge", "take", "--for", "x", env=dict(env_b2, RM_HOST="nosuchbox"))
        check(r.returncode != 0 and "nosuchbox.b" in (r.stdout + r.stderr), "RM_GAME_INSTANCE=b on an unknown machine refuses by name, never Archmagi's lock")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("%s selftest_bridge_instance_key: %d failed" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


def M_bridge_gate(env, seat, host):
    code = ("import sys; sys.path.insert(0, %r); import model; print(repr(model.bridge_gate(%r, %r)))" % (HERE, seat, host))
    out = subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True, timeout=60).stdout.strip()
    return None if out == "None" else out


if __name__ == "__main__":
    sys.exit(main())
