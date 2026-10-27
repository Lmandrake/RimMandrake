#!/usr/bin/env python3
"""deadman_check: the outside dead-man for the Dispatcher and ops_watch (DISPATCHER_BUILD_OUTSIDE_DEADMAN_HEARTBEAT).

An arm cannot report its own death. This is a separate, tiny, no-AI program on its own systemd timer
(rm-deadman.timer, every 10 min). It reads each arm's LAST-RUN STAMP and, when one is older than its limit (or
missing, or unreadable), files ONE ledger alarm the same way ops_watch does (ops_watch.real_filer: spawn as RUNNER
from the dispatch clone under ingest.lock, published). Edge-triggered: one item per outage, a note when it clears.

    ops_watch   $RM_OPS_WATCH_DIR/status.json  key "t" (epoch of the last pass; timer every 15 min)  limit 50 min
    dispatcher  $RM_DISPATCHER_STATE/state.json key "last_tick" (ISO; timer every 2 min), live or dry/  limit 15 min

    python3 src/RimMandrake/Utils/deadman_check.py run [--file-alarms]
    python3 src/RimMandrake/Utils/deadman_check.py install [--apply]    systemd user timer (plan unless --apply)
"""
import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "rimflow"))

LIMITS = {"ops_watch": 50 * 60, "dispatcher": 15 * 60}


def ops_dir():
    return Path(os.environ.get("RM_OPS_WATCH_DIR", "/mnt/d/ClaudeWork/rimmandrake/ops_watch"))


def dispatcher_dir():
    import doorbell
    return Path(doorbell.state_dir())


def state_file():
    return ops_dir() / "deadman.json"


def _json(p):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _iso_epoch(s):
    try:
        return datetime.fromisoformat(str(s).replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


def stamps():
    """-> {arm: epoch | None}. None = missing or unreadable (reported as such, never as fresh)."""
    out = {}
    st = _json(ops_dir() / "status.json")
    t = st.get("t") if isinstance(st, dict) else None
    out["ops_watch"] = float(t) if isinstance(t, (int, float)) and not isinstance(t, bool) else None
    best = None
    for p in (dispatcher_dir() / "state.json", dispatcher_dir() / "dry" / "state.json"):
        d = _json(p)
        e = _iso_epoch(d.get("last_tick")) if isinstance(d, dict) and d.get("last_tick") else None
        if e is not None and (best is None or e > best):
            best = e
    out["dispatcher"] = best
    return out


def judge(st, now, limits=None):
    """-> {arm: None (alive) | reason string}. Pure (tested). A stamp in the future by over 5 min is also a fault."""
    limits = limits or LIMITS
    res = {}
    for arm, lim in limits.items():
        t = st.get(arm)
        if t is None:
            res[arm] = "%s has no readable last-run stamp" % arm
        elif now - t > lim:
            res[arm] = "%s last ran %d min ago (limit %d min)" % (arm, (now - t) // 60, lim // 60)
        elif t - now > 300:
            res[arm] = "%s stamp is %d min in the future (clock or file wrong)" % (arm, (t - now) // 60)
        else:
            res[arm] = None
    return res


def known_ids():
    import pulse_core as pc
    return set(pc._model().replay(pc.read_ledger()).items)


def check(now, filer, ids=None, stamp_map=None):
    """One pass. -> deadman state. filer(todo, conf) -> {name: None|error}; None files nothing."""
    import ops_watch as OW
    verdict = judge(stamps() if stamp_map is None else stamp_map, now)
    p = state_file()
    state = _json(p) if p.exists() else {}
    if not isinstance(state, dict):
        return {"_state": "UNREADABLE: %s is not a JSON object; filing held" % p}
    conf = OW.alarm_conf(OW.load_rules())
    todo = []
    for arm, why in verdict.items():
        cur = state.get(arm)
        if why is None:
            if cur:
                if cur.get("item") and filer:
                    todo.append({"note_only": True, "item": cur["item"], "name": "note:" + arm,
                                 "text": "deadman_check: %s is running again (%s)" % (arm, OW.iso(now))})
                state.pop(arm)
            continue
        if cur and cur.get("state") == "OPEN":
            cur["last_seen"] = OW.iso(now)
            continue
        if not cur:
            cur = state[arm] = {"state": "PENDING", "since": OW.iso(now), "tries": 0}
        ids_ = ids if ids is not None else known_ids()
        if cur.get("name") in ids_:
            cur.update(state="OPEN", item=cur["name"])
            continue
        if not cur.get("name"):
            taken = set(ids_) | {a.get("name") for a in state.values() if isinstance(a, dict)}
            cur["name"] = OW.mint_name(arm, taken, "OPS_DEADMAN_REVIVE")
        cur["title"] = ("Dead man: %s" % why)[:160]
        todo.append({"aid": arm, "name": cur["name"], "title": cur["title"]})
    if todo:
        OW.atomic_json(p, state)       # the name is on disk before the spawn: a retry reuses it
        if filer:
            try:
                res = filer(todo, conf)
            except Exception as e:  # noqa: BLE001
                res = {a["name"]: "filer raised %s: %s" % (type(e).__name__, str(e)[:200]) for a in todo}
        else:
            res = {a["name"]: "filing off (run without --file-alarms)" for a in todo}
        for a in todo:
            if a.get("note_only"):
                continue
            cur = state[a["aid"]]
            err = res.get(a["name"])
            cur["tries"] = cur.get("tries", 0) + (1 if filer else 0)
            if err is None:
                cur.update(state="OPEN", item=a["name"], error=None, filed=OW.iso(now))
            else:
                cur["error"] = err
    OW.atomic_json(p, state)
    return state


UNIT = """# rm-deadman: outside dead-man for the Dispatcher and ops_watch (DISPATCHER_BUILD_OUTSIDE_DEADMAN_HEARTBEAT). No AI.
[Unit]
Description=Dead-man check for the Dispatcher and ops_watch

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 {deploy}/src/RimMandrake/Utils/deadman_check.py run --file-alarms
TimeoutStartSec=300s
Nice=10
"""
TIMER = """[Unit]
Description=Dead-man check every 10 min

[Timer]
OnCalendar=*:03/10
Persistent=true

[Install]
WantedBy=timers.target
"""


def install(apply, deploy):
    d = Path.home() / ".config/systemd/user"
    files = {d / "rm-deadman.service": UNIT.format(deploy=deploy), d / "rm-deadman.timer": TIMER}
    for p, body in files.items():
        old = p.read_text() if p.exists() else None
        print(("unchanged " if old == body else "write ") + str(p))
        if apply and old != body:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(body)
    if apply:
        for cmd in (["daemon-reload"], ["enable", "--now", "rm-deadman.timer"]):
            r = subprocess.run(["systemctl", "--user"] + cmd, capture_output=True, text=True, timeout=60)
            print("systemctl --user %s: exit %d %s" % (" ".join(cmd), r.returncode, r.stderr.strip()))
            if r.returncode:
                return 1
    else:
        print("plan only: pass --apply to write and enable")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--file-alarms", action="store_true")
    i = sub.add_parser("install")
    i.add_argument("--apply", action="store_true")
    i.add_argument("--deploy", default=os.environ.get("RM_PULSE_DEPLOY", "/mnt/d/ClaudeWork/rimmandrake/pulse-deploy"))
    a = ap.parse_args(argv)
    if a.cmd == "install":
        return install(a.apply, a.deploy)
    import ops_watch as OW
    st = check(time.time(), OW.real_filer if a.file_alarms else None)
    bad = {k: v for k, v in st.items()}
    print("deadman: %s" % ("all arms alive" if not bad else json.dumps(bad, sort_keys=True)[:400]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
