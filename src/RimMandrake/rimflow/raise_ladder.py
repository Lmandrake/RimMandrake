#!/usr/bin/env python3
"""raise_ladder.py — raising a dead seat window with memory, one at a time, on a ladder that never loops
(OPS_RAISE_REWIRE_WITH_DEATH_LADDER; design/RimMandrake/operations_metronome_strategy_2026-11-02.md §4, §8 step 4).

It replaces the flat `caps.recovers_per_seat_day` cap the Dispatcher used: three raises a day, whatever the deaths
were, and a fourth death any later day started the count again.

The register (Dispatcher state `lives.<SEAT>`): every death is a line {at, ending, cause, model, raise_id}. `ending`
is how it ended (`login_or_quota`, `out_of_memory`, `server_error`, `raise_failed`, `window_gone`), read from what the
dead window left; `cause` is kept apart and is `unknown` unless something names it. A death within `raise_blame_s` of
a raise carries that raise's id: it counts against the raise, not the thing.

The ladder, per seat (rule() defaults; schedule key `raise_ladder` overrides):
  life 2 and 3 in 24 h  raise, with the life note; the 2nd life waits 2 min after the death, the 3rd 8 min
  life 4 in 24 h        STOP, any causes mixed: one alarm quoting every death; sticky
  7 deaths in 7 days    the same STOP, however spread out (three deaths every 25 h cannot slip under a daily window)
  ending login_or_quota no raise until the account check passes FOR THAT MODEL, backing off 5, 15, 30, 60 min
  reset                 6 h of healthy running clears the 24 h count (and a stop), never the 7-day count; a named fix
                        (`raise_ladder.py reset --seat S --fix ITEM`) clears both. Time alone clears nothing: a stop
                        stays a stop when its deaths roll out of the window.
Single flight: no raise while the dead window's own process is still alive, or while memory is short; one raise in
flight per seat (the Dispatcher's `recover` record), and its id is on the register.

Pure: decide() reads the register and observations and returns a verdict; the Dispatcher acts and persists.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

DAY = 86400
RULE = {"backoff_s": [120, 480], "stop_at_life": 4, "window_s": DAY, "week_n": 7, "week_s": 7 * DAY,
        "healthy_reset_s": 6 * 3600, "raise_blame_s": 900, "gate_backoff_s": [300, 900, 1800, 3600],
        "min_mem_gb": 2.0, "keep_s": 8 * DAY}
ENDINGS = ("login_or_quota", "out_of_memory", "server_error", "raise_failed", "window_gone")
# A fixed advice line per ending, never invented (§4). None: no advice for that ending.
ADVICE = {
    "login_or_quota": "The account check for your model passed before this raise; if the limit hits again, stop and "
                      "write your progress file.",
    "out_of_memory": "It was killed for memory: stream big files, keep long output in files, one heavy job at a time.",
    "server_error": "It ended on an API server error; the raise is the retry, so pick up where the progress file says.",
    "raise_failed": "The last raise never brought the window back; read your progress file before acting.",
    "window_gone": None,
}
LIMIT_RX = re.compile(r"rate.?limit|usage limit|quota|limit reached|overloaded|not logged in|log ?in expired|"
                      r"authenticat", re.I)


def rule(sch):
    r = dict(RULE)
    r.update({k: v for k, v in (sch.get("raise_ladder") or {}).items() if not k.startswith("_")})
    return r


def iso(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


def register(st, seat):
    rec = st.setdefault("lives", {}).setdefault(seat, {})
    rec.setdefault("deaths", [])
    rec.setdefault("raises", [])
    return rec


def record_death(rec, at, ending, cause="unknown", model=None, r=None):
    """One line per death. -> the line. A death within raise_blame_s of the last raise is charged to that raise."""
    r = r or RULE
    ending = ending if ending in ENDINGS else "window_gone"
    last = rec["raises"][-1] if rec.get("raises") else None
    line = {"at": at, "ending": ending, "cause": cause or "unknown", "model": model,
            "raise_id": last["id"] if last and 0 <= at - last["at"] <= r["raise_blame_s"] else None}
    rec["deaths"].append(line)
    return line


def record_raise(rec, seat, now, life):
    rid = "%s-life%d-%d" % (seat, life, int(now))
    rec["raises"].append({"id": rid, "at": now, "life": life})
    return rid


def unraise(rec, now):
    """Give back a raise decided but never started."""
    rec["raises"] = [x for x in rec.get("raises") or [] if x.get("at") != now]


def healthy(rec, alive_since, now, r=None):
    """Called while the window is alive. 6 h of healthy running clears the 24 h count and a stop. -> True if it reset."""
    r = r or RULE
    if alive_since is None or now - alive_since < r["healthy_reset_s"]:
        return False
    if not any(d["at"] > rec.get("day_reset_at", 0) for d in rec["deaths"]) and not rec.get("stopped"):
        return False
    rec["day_reset_at"] = now
    rec["day_reset_why"] = "%d h of healthy running since %s" % (r["healthy_reset_s"] // 3600, iso(alive_since))
    rec.pop("stopped", None)
    rec.pop("gate", None)
    return True


def apply_fix(rec, fix):
    """A named fix (`reset` request {fix, at}) newer than the last one clears both counts and a stop. -> True if new."""
    if not isinstance(fix, dict) or not fix.get("fix") or not isinstance(fix.get("at"), (int, float)):
        return False
    if fix["at"] <= rec.get("fix_at", 0):
        return False
    rec["fix_at"] = rec["day_reset_at"] = fix["at"]
    rec["fix"] = str(fix["fix"])
    rec["day_reset_why"] = "named fix " + rec["fix"]
    rec.pop("stopped", None)
    rec.pop("gate", None)
    return True


def counts(rec, now, r=None):
    """-> (deaths in the 24 h window since the last reset, deaths in the 7-day window since the last named fix)."""
    r = r or RULE
    day = [d for d in rec["deaths"] if d["at"] > max(now - r["window_s"], rec.get("day_reset_at", 0))]
    week = [d for d in rec["deaths"] if d["at"] > max(now - r["week_s"], rec.get("fix_at", 0))]
    return day, week


def quote(deaths):
    return "; ".join("%s %s (cause %s%s)" % (iso(d["at"]), d["ending"], d["cause"],
                                             ", raise " + d["raise_id"] if d.get("raise_id") else "") for d in deaths)


def decide(rec, now, r=None, model_ok=None, old_alive=False, mem=(True, "")):
    """-> {verdict: raise|wait|stop|gated, why, life, until?, last?}. Mutates only rec["stopped"] and rec["gate"].
    model_ok(model) -> (True | False | None, why), called only when a login/quota gate is due."""
    r = r or RULE
    day, week = counts(rec, now, r)
    life = len(day) + 1
    if rec.get("stopped"):
        return {"verdict": "stop", "life": life, "new": False, "why": rec["stopped"]["why"]}
    why = None
    if len(week) >= r["week_n"]:
        why = "%d deaths in %d days (breaker): %s" % (len(week), r["week_s"] // DAY, quote(week))
    elif life >= r["stop_at_life"]:
        why = "life %d in 24 h, any causes: %s" % (life, quote(day))
    if why:
        rec["stopped"] = {"at": now, "why": why}
        return {"verdict": "stop", "life": life, "new": True, "why": why}
    if not day:
        return {"verdict": "wait", "life": life, "why": "no death on the register since the last reset"}
    last = day[-1]
    until = last["at"] + r["backoff_s"][min(life - 2, len(r["backoff_s"]) - 1)]
    if now < until:
        return {"verdict": "wait", "life": life, "until": until, "last": last,
                "why": "life %d waits until %s (%d s after the death)" % (life, iso(until), until - last["at"])}
    if last["ending"] == "login_or_quota":
        g = rec.get("gate")
        if not g or g.get("death_at") != last["at"]:
            g = rec["gate"] = {"death_at": last["at"], "model": last.get("model"), "tries": 0, "next_at": now}
        if not g.get("passed_at"):
            if now < g["next_at"]:
                return {"verdict": "gated", "life": life, "until": g["next_at"], "last": last, "new": False,
                        "why": "login/quota: account check for model %s next at %s" % (g["model"], iso(g["next_at"]))}
            ok, said = model_ok(g["model"]) if model_ok else (None, "no account check available")
            if ok is not True:
                g["tries"] += 1
                b = r["gate_backoff_s"]
                g["next_at"] = now + b[min(g["tries"] - 1, len(b) - 1)]
                return {"verdict": "gated", "life": life, "until": g["next_at"], "last": last, "new": g["tries"] == 1,
                        "why": "login/quota: account check for model %s did not pass (%s); try %d, next at %s"
                               % (g["model"], said or ok, g["tries"], iso(g["next_at"]))}
            g["passed_at"] = now
    if old_alive:
        return {"verdict": "wait", "life": life, "last": last, "why": "the dead window's process is still running"}
    if mem[0] is False:
        return {"verdict": "wait", "life": life, "last": last, "why": "memory short before a raise: %s" % mem[1]}
    return {"verdict": "raise", "life": life, "last": last, "why": "life %d in 24 h" % life}


def life_note(seat, life, last, progress):
    """The raise message's memory: life number, how the last life ended, its progress file, a fixed advice line."""
    s = "Life %d today. Life %d ended %s at %s (cause %s)" % (life, life - 1, last["ending"], iso(last["at"]),
                                                              last["cause"])
    if last.get("raise_id"):
        s += ", within minutes of raise %s" % last["raise_id"]
    s += ". Its progress file: %s." % (progress or "none written")
    if ADVICE.get(last["ending"]):
        s += " " + ADVICE[last["ending"]]
    return s


# ---------------------------------------------------------------- observations (the Dispatcher's default)

def ending_of(seat, sess, cfg):
    """-> (ending, cause) from what the dead window left: its transcript's last turn and memwatch's oom kills."""
    try:
        import seat_restart as SR
        path = SR.transcript_for(sess or {}, cfg)
        recs = SR._tail_records(path, 1 << 17) if path else []
    except Exception:  # noqa: BLE001 - an unreadable transcript is no ending, not a crash
        recs = []
    last = None
    for x in recs:
        if x.get("type") in ("user", "assistant") and not x.get("isSidechain"):
            last = x
    err = None
    if last and last.get("type") == "assistant" and last.get("isApiErrorMessage"):
        err = last.get("error")
    if err in ("authentication_failed", "rate_limit"):
        return "login_or_quota", err
    if err == "server_error":
        return "server_error", "unknown"
    if oom_killed(seat):
        return "out_of_memory", "unknown"
    return "window_gone", "unknown"


def oom_killed(seat, now=None, path=None):
    """memwatch's events.jsonl holds an oom kill for this seat in the last hour."""
    import datetime
    try:
        if path is None:
            sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Utils"))
            import memwatch
            path = memwatch.state_dir() / "events.jsonl"
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()[-200:]  # cut-ok: the last 200 lines read, not stored text
    except Exception:  # noqa: BLE001 - no memwatch reading: not an oom ending
        return False
    now = now or time.time()
    for ln in reversed(lines):
        try:
            e = json.loads(ln)
            at = datetime.datetime.strptime(e["ts"], "%Y-%m-%dT%H:%M:%S%z").timestamp()
        except (ValueError, KeyError, TypeError):
            continue
        if now - at > 3600:
            break
        if e.get("kind") in ("oom_kill", "oom_group_kill") and str(e.get("seat") or "").upper() == seat.upper():
            return True
    return False


def progress_of(seat, cfg, now=None):
    """The newest handoff the seat wrote in its clone in the last day, else None."""
    d = os.path.join(cfg.get("clone") or "", "infrastructure", "state", "handoffs")
    try:
        names = [n for n in os.listdir(d) if n.upper().startswith(seat.upper() + "_") and n.endswith(".md")]
    except OSError:
        return None
    best = max(names, key=lambda n: os.path.getmtime(os.path.join(d, n)), default=None)
    if best and (now or time.time()) - os.path.getmtime(os.path.join(d, best)) < DAY:
        return os.path.join(d, best)
    return None


def mem_ok(r=None):
    r = r or RULE
    try:
        with open("/proc/meminfo", encoding="utf-8") as f:
            kv = {ln.split(":")[0]: ln.split(":")[1] for ln in f if ":" in ln}
        gb = int(kv["MemAvailable"].split()[0]) / 1048576
    except (OSError, KeyError, ValueError, IndexError) as e:
        return None, "meminfo unreadable: %s" % type(e).__name__
    return (gb >= r["min_mem_gb"]), "%.1f GB available, %.1f wanted" % (gb, r["min_mem_gb"])


def model_ok(model, claude=None, timeout=90):
    """The account check for ONE model: a one-turn `claude -p --model <m>` answers. -> (True|False|None, why)."""
    exe = claude or shutil.which("claude")
    if not exe or not model:
        return None, "no claude binary or no model"
    cwd = tempfile.mkdtemp(prefix="raise-gate-")
    try:
        p = subprocess.run([exe, "-p", "--model", model, "Reply with the single word OK."], cwd=cwd,
                           capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as e:
        return None, "check gave no reading: %s" % type(e).__name__
    finally:
        shutil.rmtree(cwd, ignore_errors=True)
    said = ("%s %s" % (p.stdout, p.stderr)).strip()
    if p.returncode == 0 and said and not LIMIT_RX.search(said):
        return True, ""
    if LIMIT_RX.search(said):
        return False, said
    return None, "exit %d: %s" % (p.returncode, said)


def resets_dir(root):
    return os.path.join(root, "raise_resets")


def read_resets(root):
    out = {}
    d = resets_dir(root)
    for n in (os.listdir(d) if os.path.isdir(d) else []):
        try:
            with open(os.path.join(d, n), encoding="utf-8") as f:
                out[n[:-5]] = json.load(f)
        except (OSError, ValueError):
            continue
    return out


def default_obs(sch, root):
    r = rule(sch)
    return {"ending": ending_of, "progress": progress_of, "mem": lambda: mem_ok(r), "model_ok": model_ok,
            "resets": lambda: read_resets(root)}


def prune(rec, now, r=None):
    r = r or RULE
    rec["deaths"] = [d for d in rec["deaths"] if now - d["at"] < r["keep_s"]]
    rec["raises"] = [x for x in rec["raises"] if now - x["at"] < r["keep_s"]]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    rs = sub.add_parser("reset", help="clear a seat's ladder by a named fix (read by the next Dispatcher tick)")
    rs.add_argument("--seat", required=True)
    rs.add_argument("--fix", required=True, help="the item or sha that fixed the cause")
    rs.add_argument("--root", default=os.environ.get("RIMFLOW_DISPATCHER_ROOT") or "/mnt/d/ClaudeWork/rimmandrake/dispatcher")
    sh = sub.add_parser("show", help="print a seat's register from the Dispatcher state")
    sh.add_argument("--seat", required=True)
    sh.add_argument("--root", default=os.environ.get("RIMFLOW_DISPATCHER_ROOT") or "/mnt/d/ClaudeWork/rimmandrake/dispatcher")
    a = ap.parse_args(argv)
    if a.cmd == "reset":
        os.makedirs(resets_dir(a.root), exist_ok=True)
        p = os.path.join(resets_dir(a.root), a.seat.upper() + ".json")
        with open(p + ".tmp", "w", encoding="utf-8") as f:
            json.dump({"fix": a.fix, "at": time.time()}, f)
        os.replace(p + ".tmp", p)
        print("RESET requested for %s by fix %s: %s" % (a.seat.upper(), a.fix, p))
        return 0
    try:
        with open(os.path.join(a.root, "state.json"), encoding="utf-8") as f:
            st = json.load(f)
    except (OSError, ValueError) as e:
        print("UNMEASURED: state unreadable: %s" % e)
        return 2
    rec = (st.get("lives") or {}).get(a.seat.upper())
    print(json.dumps(rec, indent=1) if rec else "no register for %s" % a.seat.upper())
    return 0


if __name__ == "__main__":
    sys.exit(main())
