#!/usr/bin/env python3
"""relentless_wake.py — a state change wakes Relentless in seconds, not at the next clock (RELENTLESS_WIRE_WAKE_ON_STATE_CHANGE).

Owner, 2026-11-05: "WHY must we wait 10 minutes?! All these arbitrary pauses cost us a lot of time! Please stop building
arbitrary pauses into the system..."

Origin is GitHub, so a blocker closed in any clone changes no file Relentless can watch until something says so. The
moves:
  - `poke(source)`: whoever made the change drops one small file in <store>/wake/ (publish.py and land.sh after every
    PUBLISHED, relentless_jobs after a detached job ends). One file per source, overwritten: the directory never grows.
    Never raises, never slows the caller.
  - rm-relentless-wake.path watches that directory and starts rm-relentless-wake.service, whose `fire` starts the tick
    unit at once when it is idle. A tick already running ABSORBS the trigger: it serves the poke itself at its next
    phase or step boundary (`serve`), because the tick's own enrol comes ~3 minutes into a 4-10 minute tick.
  - `serve`, called by the tick under tick.lock: an unserved poke -> the caller's `do()` (books sync, block sweep, enrol)
    now, recorded with its lag. Bursts coalesce: one serve covers every poke up to the newest it read.
  - Rate caps, because rm-relentless.service is live and a trigger loop would hammer the machine: `fire` starts the tick
    at most once per fire_min_gap_s and fire_max_per_hour times an hour; `serve` runs at most once per serve_min_gap_s
    and serve_max_per_tick times a tick. The fire/serve state lives OUTSIDE the watched directory, so serving or firing
    can never wake anyone. rm-relentless.timer (15 s after each tick) stays as the durable heartbeat: a capped or lost
    trigger costs one heartbeat, never a stall.
Off switch: relentless_wake.json "mode": "off" (poke still writes; nothing fires or serves).

    python3 relentless_wake.py poke <source> [why]
    python3 relentless_wake.py fire          # the wake unit's ExecStart
    python3 relentless_wake.py status
"""
import contextlib
import fcntl
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(HERE, "relentless_wake.json")
DEFAULT_ROOT = "/home/mandrake/rm/relentless"
WAKE_DIR = "wake"               # watched by rm-relentless-wake.path: pokes only
TMP_DIR = "wake_tmp"            # a poke is written here and renamed in: the watch sees one finished file
STATE = "wake_state.json"       # fire/serve bookkeeping, deliberately outside WAKE_DIR
TICK_UNIT = "rm-relentless.service"
DEFAULTS = {"mode": "live", "fire_min_gap_s": 10, "fire_max_per_hour": 60, "serve_min_gap_s": 20,
            "serve_max_per_tick": 6}


def config(path=CONFIG):
    try:
        with open(path, encoding="utf-8") as f:
            got = json.load(f)
    except (OSError, ValueError):
        got = {}
    return dict(DEFAULTS, **{k: v for k, v in got.items() if not k.startswith("_")})


def store_dir(root=None):
    return os.path.join(root or os.environ.get("RELENTLESS_ROOT") or DEFAULT_ROOT, "store")


def poke(source, why="", root=None, now=None):
    """-> the poke's path, or None when there is no Relentless store on this host. Never raises."""
    if os.environ.get("RELENTLESS_NO_WAKE"):     # the supervisor's own flush: it already holds what it landed
        return None
    try:
        d = store_dir(root)
        if not os.path.isdir(d):        # a laptop or a clone with no supervisor: nothing to wake
            return None
        src = "".join(c if c.isalnum() or c in "-_" else "_" for c in str(source))[:60] or "unknown"
        for sub in (WAKE_DIR, TMP_DIR):
            os.makedirs(os.path.join(d, sub), exist_ok=True)
        tmp = os.path.join(d, TMP_DIR, "%s.%d" % (src, os.getpid()))
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"at": time.time() if now is None else now, "source": src, "why": str(why)[:200],
                       "pid": os.getpid()}, f)
        dst = os.path.join(d, WAKE_DIR, src + ".json")
        os.replace(tmp, dst)
        return dst
    except Exception:  # noqa: BLE001  a wake is a courtesy: the heartbeat still comes
        return None


def pokes(sdir):
    """-> [poke dict] in the wake directory (torn or foreign files skipped)."""
    out = []
    try:
        names = os.listdir(os.path.join(sdir, WAKE_DIR))
    except OSError:
        return out
    for n in sorted(names):
        if not n.endswith(".json"):
            continue
        try:
            with open(os.path.join(sdir, WAKE_DIR, n), encoding="utf-8") as f:
                p = json.load(f)
            p["at"] = float(p["at"])
            out.append(p)
        except (OSError, ValueError, KeyError, TypeError):
            continue
    return out


@contextlib.contextmanager
def _state(sdir):
    os.makedirs(sdir, exist_ok=True)
    with open(os.path.join(sdir, "wake.lock"), "a") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        path = os.path.join(sdir, STATE)
        try:
            with open(path, encoding="utf-8") as f:
                st = json.load(f)
        except (OSError, ValueError):
            st = {}
        st.setdefault("served_at", 0.0)
        st.setdefault("fires", [])
        before = json.dumps(st, sort_keys=True)
        yield st
        if json.dumps(st, sort_keys=True) != before:
            tmp = path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(st, f)
            os.replace(tmp, path)


def unserved(sdir, served_at):
    return [p for p in pokes(sdir) if p["at"] > served_at]


def fire(sdir, now=None, active=None, start=None, cfg=None):
    """The wake unit's body. -> {"do": started|absorbed|capped|idle|off, ...}. `active()` -> is a tick running;
    `start()` starts one without waiting."""
    cfg = cfg or config()
    now = time.time() if now is None else now
    active = active or tick_active
    start = start or start_tick
    if cfg.get("mode") == "off":
        return {"do": "off"}
    with _state(sdir) as st:
        new = unserved(sdir, float(st["served_at"]))
        if not new:
            return {"do": "idle"}
        if active():        # the running tick serves it at its next boundary
            return {"do": "absorbed", "pokes": len(new)}
        st["fires"] = [t for t in st["fires"] if now - t < 3600]
        if st["fires"] and now - max(st["fires"]) < float(cfg["fire_min_gap_s"]):
            return {"do": "capped", "why": "last start %.0f s ago < fire_min_gap_s" % (now - max(st["fires"]))}
        if len(st["fires"]) >= int(cfg["fire_max_per_hour"]):
            return {"do": "capped", "why": "%d starts in the last hour" % len(st["fires"])}
        st["fires"].append(now)
        why = start()
        if why:
            return {"do": "error", "why": why}
        return {"do": "started", "pokes": len(new), "lag_s": round(now - min(p["at"] for p in new), 1)}


def serve(sdir, now, do, acts, tick_state, cfg=None, wall=time.monotonic):
    """Under tick.lock, at a phase or step boundary. `do()` -> the items enrolled (or a dict with "why" on refusal).
    `tick_state`: a dict the tick keeps for its own lifetime (serve count and last serve time). -> True if it served."""
    cfg = cfg or config()
    if cfg.get("mode") == "off":
        return False
    if tick_state.get("n", 0) >= int(cfg["serve_max_per_tick"]):
        return False
    last = tick_state.get("last")
    if last is not None and wall() - last < float(cfg["serve_min_gap_s"]):
        return False
    if not pokes(sdir):     # the common case touches nothing: no lock file, no state file
        return False
    with _state(sdir) as st:
        new = unserved(sdir, float(st["served_at"]))
    if not new:
        return False
    upto = max(p["at"] for p in new)       # pokes landing while do() runs stay unserved for the next boundary
    tick_state["n"] = tick_state.get("n", 0) + 1
    tick_state["last"] = t0 = wall()
    try:
        got = do()
    except Exception as e:  # noqa: BLE001  a failed serve costs the early enrol, never the tick
        got = {"why": "%s: %s" % (type(e).__name__, e)}
    took = round(wall() - t0, 1)        # poke -> enrolled = lag_s (to the serve's start, +-1 s tick clock) + took_s
    with _state(sdir) as st:
        st["served_at"] = max(float(st["served_at"]), upto)
        st["last_serve"] = {"at": now, "lag_s": round(now - min(p["at"] for p in new), 1),
                            "sources": sorted({p.get("source", "?") for p in new})}
    row = {"do": "wake_serve", "lag_s": round(now - min(p["at"] for p in new), 1), "took_s": took,
           "sources": sorted({p.get("source", "?") for p in new})}
    if isinstance(got, dict):
        row["why"] = str(got.get("why"))[:300]
    else:
        row["enrolled"] = list(got or [])
    acts.append(row)
    return True


def mark_served_through(sdir, at):
    """The tick's own enrol read the ledger at `at`: every poke before it is served. No poke, no write."""
    if not any(p["at"] <= at for p in pokes(sdir)):
        return
    with _state(sdir) as st:
        st["served_at"] = max(float(st["served_at"]), at)


# ---------------------------------------------------------------- systemd

def tick_active():
    got = subprocess.run(["systemctl", "--user", "is-active", TICK_UNIT], capture_output=True, text=True, timeout=20)
    return got.stdout.strip() in ("active", "activating", "deactivating", "reloading")


def start_tick():
    got = subprocess.run(["systemctl", "--user", "start", "--no-block", TICK_UNIT], capture_output=True, text=True,
                         timeout=20)
    return None if got.returncode == 0 else (got.stderr or got.stdout).strip()[:300] or "exit %d" % got.returncode


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    if not a:
        print(__doc__)
        return 2
    sdir = store_dir()
    if a[0] == "poke" and len(a) >= 2:
        print(poke(a[1], " ".join(a[2:])) or "no store")
        return 0
    if a[0] == "fire":
        got = fire(sdir)
        print(json.dumps(got))
        if got["do"] in ("started", "capped", "error"):
            try:        # the journal is the tick's; a line here keeps the wake's decisions countable
                log = os.path.join(sdir, "wake_fires.jsonl")
                if os.path.exists(log) and os.path.getsize(log) > 1 << 20:     # bounded: the newest half stays
                    with open(log, encoding="utf-8") as f:
                        keep = f.readlines()
                    with open(log, "w", encoding="utf-8") as f:
                        f.writelines(keep[len(keep) // 2:])
                with open(log, "a", encoding="utf-8") as f:
                    f.write(json.dumps(dict(got, at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))) + "\n")
            except OSError:
                pass
        return 0
    if a[0] == "status":
        with _state(sdir) as st:
            print(json.dumps({"state": st, "pokes": pokes(sdir), "config": config()}, indent=1))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
