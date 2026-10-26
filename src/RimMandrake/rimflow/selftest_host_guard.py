#!/usr/bin/env python3
"""selftest_host_guard.py - one bridge per HOST (BRIDGE_LOCK_WIDEN_ONE_PER_HOST).

Proves, on a throwaway ledger and throwaway lock files (nothing real is touched):
  * a lock holder on ANOTHER machine is not judged by this machine's /proc or boot_id (it used to read as dead);
  * a script take (host_guard) excludes a second driver, is inherited by its children, and frees on release;
  * `host_guard.py run` holds the guard for its child's lifetime and refuses a concurrent outsider;
  * a `bridge` event with host=stevedesktop never moves the Archmagi holder, and bridge_gate is per host;
  * `rimflow bridge take|who|release --host stevedesktop` writes a host-stamped event and takes that host's own
    driver lock (run here as if this machine were SteveDesktop, RM_HOST=stevedesktop).
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
CLI = os.path.join(HERE, "cli.py")
HG = os.path.join(HERE, "host_guard.py")
FAILS = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def main():
    import driver_lock as D
    tmp = tempfile.mkdtemp(prefix="rf_hostguard_")
    try:
        # 1. a foreign holder is not inspected locally
        foreign = {"pid": 1, "start": 1.0, "boot_id": "other-boot", "platform": "wsl", "host": "SomeOtherBox"}
        check(D.process_alive(foreign) is None, "another machine's process reads 'not inspectable', not dead")
        alive, how = D._alive({"identity": foreign, "heartbeat": now()})
        check(alive is True, "a foreign holder with a fresh heartbeat is alive (boot_id not compared): " + how)
        alive, how = D._alive({"identity": foreign, "heartbeat": "2020-01-01T00:00:00Z"})
        check(alive is False, "a foreign holder with a stale heartbeat is not: " + how)
        mine = dict(D.my_identity(), boot_id="not-this-boot")
        alive, how = D._alive({"identity": mine, "heartbeat": now()})
        check(alive is False, "a LOCAL holder from a previous boot still reads dead: " + how)

        # 2. host_guard in-process
        os.makedirs(os.path.join(tmp, "items"))
        lock = os.path.join(tmp, "DRIVER_LOCK.json")
        env = {k: v for k, v in os.environ.items()
               if k not in ("RIMFLOW_SEAT", "AGENT_SEAT", "CLAUDE_SESSION_ID", "RM_HOST_GUARD_GEN")}
        env.update(RIMFLOW_LEDGER=os.path.join(tmp, "events.jsonl"), RIMFLOW_ITEMS=os.path.join(tmp, "items"),
                   RIMFLOW_SHARED_BRIDGE=os.path.join(tmp, "shared.json"), RIMFLOW_PROBE="no-reading",
                   RIMFLOW_DRIVER_LOCK=lock, RM_HOST="stevedesktop")
        saved = dict(os.environ)
        os.environ.clear()
        os.environ.update(env)
        try:
            import host_guard as H
            check(H.local_host() == "stevedesktop", "RM_HOST names this machine's bridge host")
            with H.held("RUNNER", "job A") as r:
                check(r["ok"] and not r["reentrant"] and os.path.exists(lock), "a script take holds the lock")
                check(os.environ.get(H.ENV_GEN) == str(r["generation"]), "the take is exported to children")
                check("RM_HOST_GUARD_GEN" in os.environ.get("WSLENV", ""), "and through WSLENV to Windows children")
                r2 = H.acquire("RUNNER", "nested")
                check(r2["ok"] and r2["reentrant"], "a nested acquire inherits the take")
                other = {"pid": 4242, "start": 7.0, "boot_id": D.current_boot_id(), "platform": "wsl",
                         "host": os.uname().nodename}
                saved_gen = os.environ.pop(H.ENV_GEN)
                r3 = H.acquire("BENCH", "outsider", identity=other)
                os.environ[H.ENV_GEN] = saved_gen
                check(not r3["ok"], "an outsider is refused while the script holds it: " + r3["why"])
            check(not os.path.exists(lock), "leaving the block releases the lock")
            win = D.my_identity()
            D.acquire(lock, "BENCH", "window take", win)
            r4 = H.acquire("BENCH", "modcheck from the window's shell")
            check(r4["ok"] and r4["reentrant"], "a tool started by the holding WINDOW drives under its take")
            D.release(lock, "BENCH", win)
            check(H.ENV_GEN not in os.environ, "and un-exports the generation")
            os.environ["RIMFLOW_DRIVER_LOCK"] = ""
            r = H.acquire("RUNNER", "nowhere")
            check(not r["ok"] and "unguarded" in r["why"], "no lock path fails CLOSED")
            os.environ["RIMFLOW_DRIVER_LOCK"] = lock
        finally:
            os.environ.clear()
            os.environ.update(saved)

        # 3. `run` holds for the child's lifetime
        child = ("import subprocess,sys,os; "
                 "a=subprocess.run([sys.executable,%r,'run','--seat','RUNNER','--for','inner','--',sys.executable,'-c','0']).returncode; "
                 "e=dict(os.environ); e.pop('RM_HOST_GUARD_GEN'); "
                 "b=subprocess.run([sys.executable,%r,'take','--seat','BENCH','--for','x','--identity-json',"
                 "'{\"pid\":4242,\"start\":7.0,\"boot_id\":null,\"platform\":\"wsl\",\"host\":\"elsewhere\"}'],env=e,capture_output=True).returncode; "
                 "print(a,b)") % (HG, HG)
        p = subprocess.run([sys.executable, HG, "run", "--seat", "RUNNER", "--for", "outer", "--",
                            sys.executable, "-c", child], env=env, capture_output=True, text=True, timeout=60)
        check(p.stdout.strip() == "0 75", "inside `run`: nested run inherits (0), an outsider take is refused (75): "
              + repr(p.stdout.strip()) + " " + p.stderr.strip()[-200:])
        check(not os.path.exists(lock), "`run` releases when its child exits")

        # 4. model: per-host replay and gate
        sys.path.insert(0, os.path.dirname(HERE))
        from rimflow import model as M
        try:
            M.bridge_host_key("stevedesktopp")
            check(False, "an unknown host is refused")
        except M.SchemaError:
            check(True, "an unknown host is refused")
        check(M.bridge_host_key("SteveDesktop") == "stevedesktop" and M.bridge_host_key(None) == "archmagi",
              "host keys are normalised; absent means archmagi")
        w = M.World() if hasattr(M, "World") else None
        if w is not None:
            M._apply_itemless({"event": "bridge", "state": "taken", "host": "stevedesktop", "ts": now(),
                               "purpose": "batch"}, "BENCH", w)
            check(w.bridge_holder is None and w.bridge_hosts["stevedesktop"]["holder"] == "BENCH",
                  "a SteveDesktop take does not move the Archmagi holder")
            M._apply_itemless({"event": "bridge", "state": "taken", "ts": now()}, "FOUNDRY", w)
            check(w.bridge_holder == "FOUNDRY" and w.bridge_hosts["archmagi"]["holder"] == "FOUNDRY"
                  and w.bridge_hosts["stevedesktop"]["holder"] == "BENCH",
                  "a host-less take is Archmagi's, and both hosts are held at once")
        else:
            check(False, "model.World exists")

        # 5. the CLI, as if on SteveDesktop
        def rf(seat, *args):
            return subprocess.run([sys.executable, CLI] + list(args), env=dict(env, RIMFLOW_SEAT=seat),
                                  capture_output=True, text=True, timeout=60)
        r = rf("BENCH", "bridge", "take", "--host", "stevedesktop", "--for", "drill")
        check(r.returncode == 0 and os.path.exists(lock), "bridge take --host stevedesktop takes that host's lock: "
              + (r.stdout + r.stderr).strip()[-200:])
        evs = [json.loads(x) for x in open(env["RIMFLOW_LEDGER"]) if x.strip()] \
            if os.path.exists(env["RIMFLOW_LEDGER"]) else []
        shard_dir = os.path.join(tmp, "events")
        if os.path.isdir(shard_dir):
            for fn in os.listdir(shard_dir):
                evs += [json.loads(x) for x in open(os.path.join(shard_dir, fn)) if x.strip()]
        br = [e for e in evs if e.get("event") == "bridge"]
        check(br and br[-1].get("host") == "stevedesktop", "the ledger event names the host")
        r = rf("FOUNDRY", "bridge", "take", "--host", "stevedesktop", "--for", "second")
        check(r.returncode != 0, "a second window's take of the same host is refused")
        r = rf("FOUNDRY", "bridge", "take", "--for", "archmagi at the same time")
        check(r.returncode == 0, "while Archmagi's bridge is still free for another window: "
              + (r.stdout + r.stderr).strip()[-200:])
        g = subprocess.run([sys.executable, "-c", "import sys; sys.path.insert(0,%r); from rimflow import model as m; "
                            "print(m.bridge_gate('BENCH','stevedesktop') is None, m.bridge_gate('FOUNDRY','stevedesktop') is None,"
                            " m.bridge_gate('FOUNDRY') is None)" % os.path.dirname(HERE)],
                           env=env, capture_output=True, text=True).stdout.strip()
        check(g == "True False True", "bridge_gate is per host: " + g)
        r = rf("BENCH", "bridge", "who", "--host", "stevedesktop")
        check("held by BENCH" in r.stdout and "HELD" in r.stdout, "who --host reports ledger and guard: "
              + r.stdout.strip()[-200:])
        r = rf("BENCH", "bridge", "release", "--host", "stevedesktop")
        check(r.returncode == 0 and not os.path.exists(lock), "release --host frees that host's lock: "
              + (r.stdout + r.stderr).strip()[-200:])
        # a typo'd host is a plain refusal (exit 2, names the known hosts), not a SchemaError traceback
        r = rf("BENCH", "bridge", "take", "--host", "stevedeskop", "--for", "typo")
        check(r.returncode == 2 and "unknown bridge host" in r.stderr and "Traceback" not in r.stderr,
              "an unknown --host is refused cleanly: rc %s %s" % (r.returncode, r.stderr.strip()[-200:]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("\n%d failed" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
