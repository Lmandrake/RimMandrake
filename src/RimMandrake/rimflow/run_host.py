#!/usr/bin/env python3
"""run_host.py - where a detached list run starts: this machine, or SteveDesktop over ssh.

Boundary page: design/specs/2026-11-24-run-on-steve/boundary.md. Pure: plan(), stop_argv(), record() and parse_unit()
read only their arguments; read_facts() and remote_status() are the functions that touch the network.

The route (measured 2026-11-24): the host's OWN detached_helper.py in ~/rm/bench, reached through the WSL door with
~/.local/bin on PATH. It makes the clone, the footer, the run record, the finish note and the publish there. This side
copies the brief over (stdin), runs that launch, and keeps a record that names host, unit and item.
plan(host, item, brief_path, facts, model, budget, ...) -> {"verdict": LOCAL|REMOTE|REFUSED|COULD NOT LOOK, "why", "argv"}
"""
import json
import os
import re
import shlex
import subprocess
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Utils"))

LOCAL_NAMES = ("archmagi", "local", "")
# lower-case name -> ssh target. The bare alias `stevedesktop` lands in Windows PowerShell; WSL is this door.
HOSTS = {"stevedesktop": "mandrake@stevedesktop-wsl"}
NAMES = {"stevedesktop": "SteveDesktop"}               # the machine's name, as a line names it
LOGIN = "export PATH=$HOME/.local/bin:$PATH; "     # claude and claude-account are on PATH only in a login shell
BENCH = "~/rm/bench"                               # the host's own seat clone: its launcher makes the run's clone
BRIEFS = "~/rm/list_briefs"
SYNC_RC = 75                                       # the exit code of a remote command whose `./sync` failed (EX_TEMPFAIL)
SYNC_FAILED = "COULD NOT LAUNCH: the host's seat clone could not sync"
LAUNCHER = "src/RimMandrake/rimflow/detached_helper.py"
LANE_CLONES = ("rm/runner", "rm/runner_b")         # the test lane's own clones: a session writing there pauses the lane
FACTS = ("reachable", "claude", "account", "picked_account", "push", "launcher", "clone", "free_gb")
LIVE_UNIT = ("active", "activating", "reloading", "deactivating")


def _norm(host):
    return (host or "").strip().lower()


def door(host):
    return HOSTS.get(_norm(host))


def clone_of(item):
    """The clone the host's launcher makes for a run of `item` (detached_helper's pool clone)."""
    return "~/rm/relentless/clones/%s.det" % item


def _lane_clone(path):
    p = str(path).replace("\\", "/").rstrip("/")
    return any(p.endswith("/" + c) or p.endswith(c) and p.startswith("~") for c in LANE_CLONES)


def _ssh(target, cmd):
    return ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", target, LOGIN + cmd]


def in_bench(cmd):
    """`cmd` run in the host's seat clone after `./sync` has made it level with origin/main; when the sync fails, `cmd`
    does not run: the command prints SYNC_FAILED and exits SYNC_RC. The one text for every remote launch (a detached
    run here, a lane bundle in work_bundle.remote_argv)."""
    return "cd %s && { ./sync || { echo %s; exit %d; }; } && %s" % (BENCH, shlex.quote(SYNC_FAILED), SYNC_RC, cmd)


def plan(host, item, brief_path, facts, model="sonnet", budget=None, seat="BENCH", next_act_owner=None, env=(), effort=None):
    h = _norm(host)
    if h in LOCAL_NAMES:
        return {"verdict": "LOCAL", "why": "this machine", "argv": []}
    if h not in HOSTS:
        return {"verdict": "REFUSED", "why": "unknown host %r (known: archmagi, %s)" % (host, ", ".join(HOSTS)), "argv": []}
    if budget is None:
        return {"verdict": "REFUSED", "why": "a spend cap is required: --budget-usd <USD>, or 0 for none", "argv": []}
    facts = facts or {}
    unread = [k for k in FACTS if facts.get(k) is None]
    if unread:
        return {"verdict": "COULD NOT LOOK", "why": "could not read: " + ", ".join(unread), "argv": []}
    if facts["reachable"] is False:
        return {"verdict": "COULD NOT LOOK", "why": "%s is not reachable" % host, "argv": []}
    if facts["account"] != facts["picked_account"]:
        return {"verdict": "REFUSED", "why": "login %s is not the pick %s" % (facts["account"], facts["picked_account"]),
                "argv": []}
    if not facts["push"]:
        return {"verdict": "REFUSED", "why": "no push route (github-rimmandrake-write) on %s" % host, "argv": []}
    if not facts["launcher"]:
        return {"verdict": "REFUSED", "why": "%s has no %s/%s" % (host, BENCH, LAUNCHER), "argv": []}
    if _lane_clone(facts["clone"]):
        return {"verdict": "REFUSED", "why": "clone %s is the test lane's own" % facts["clone"], "argv": []}
    q = shlex.quote
    brief = "%s/%s.md" % (BRIEFS, re.sub(r"[^A-Za-z0-9_.-]", "-", item))
    launch = ["python3", LAUNCHER, "launch", "--seat", seat, "--item", item, "--brief-file", brief, "--model", model,
              "--budget-usd", "%g" % budget]
    if next_act_owner:
        launch += ["--next-act-owner", next_act_owner]
    if effort:          # else the host's own launcher states its table's level (rimflow/effort.py)
        launch += ["--effort", effort]
    for kv in env or ():
        launch += ["--env", kv]
    # ~ stays unquoted so the host's shell expands it; every other word is quoted
    cmd = "mkdir -p %s && cat > %s && %s" % (BRIEFS, brief, in_bench(" ".join(
        w if w.startswith("~/") else q(w) for w in launch)))
    return {"verdict": "REMOTE", "why": "launch on %s in %s" % (host, facts["clone"]), "argv": _ssh(HOSTS[h], cmd),
            "stdin_path": brief_path}


def parse_unit(text):
    m = re.search(r"^DETACHED (\S+)", text or "", re.M)
    return m.group(1) if m else None


def record(host, item, unit, model, budget, now=None, seat="BENCH", next_act_owner=None):
    """The run record on this machine for a run that lives on `host`: the host's own record holds its end state."""
    rec = {"unit": unit, "item": item, "host": host, "status": "running", "at": time.time() if now is None else now,
           "model": model, "budget_usd": budget, "seat": seat, "remote": True}
    if next_act_owner:
        rec["next_act_owner"] = next_act_owner
    return rec


def _state_cmd(unit):
    py = ("import json,subprocess,sys; sys.path.insert(0,'src/RimMandrake/rimflow'); import detached_helper as D; "
          "a=subprocess.run(['systemctl','--user','show','-p','ActiveState','--value',%r],capture_output=True,text=True)"
          ".stdout.strip(); print(json.dumps({'active':a or 'unknown','record':D.read_record(%r)}))" % (unit, unit))
    return "cd %s && python3 -c %s" % (BENCH, shlex.quote(py))


def remote_status(rec, runner=subprocess.run):
    """-> (status, host record or None). Live while the host's unit is live or the host cannot be read (could not
    look is live, never ended); ended: the host record's own status; a dead unit with no record there is "dead"."""
    target = door(rec.get("host"))
    if not target:
        return rec.get("status"), None
    try:
        r = runner(_ssh(target, _state_cmd(rec["unit"])), capture_output=True, text=True, timeout=60,
                   stdin=subprocess.DEVNULL)
        d = json.loads((r.stdout or "").strip().splitlines()[-1]) if r.returncode == 0 else None
    except Exception:  # noqa: BLE001
        d = None
    if not isinstance(d, dict):
        return "running", None
    host_rec = d.get("record") if isinstance(d.get("record"), dict) else None
    if d.get("active") in LIVE_UNIT or d.get("active") == "unknown":
        return "running", host_rec
    if host_rec and host_rec.get("status") not in ("launching", "running"):
        return host_rec.get("status"), host_rec
    return "dead", host_rec


def live_units(host, runner=subprocess.run):
    """-> the host's count of live rm-detached-* Claude units (its -return bookkeeping units left out), every run there
    whoever launched it, or None when the host cannot be read (could not look is no room, never zero)."""
    target = door(host)
    if not target:
        return None
    try:
        r = runner(_ssh(target, "systemctl --user list-units 'rm-detached-*' --state=active --no-legend --plain"),
                   capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
    except Exception:  # noqa: BLE001
        return None
    if r.returncode:
        return None
    return sum(1 for ln in (r.stdout or "").splitlines()
               if ln.split() and ln.split()[0].startswith("rm-detached-") and not ln.split()[0].endswith("-return.service"))


# budget: danger=a Conductor log that is trimmed or rotated would have every old host run announced again as new, since
# budget: the host's record folder only grows (35 records in 2 days on SteveDesktop, 2026-11-25); ends no work: a run
# budget: older than this is still in the host's record and `rimflow show`
RELAY_WINDOW_S = 7 * 86400
RELAY_HEAD = "DETACHED RUN ENDED"
# The host's finished records since a time, with the run's report tail for a record that holds no line text (records
# from before conductor_text). The host's own code reads them: one ssh, no model.
_ENDS_PY = (
    "import json,sys; sys.path.insert(0,'src/RimMandrake/rimflow'); import detached_helper as D, role_launch as RL\n"
    "out=[]\n"
    "for r in D.all_records():\n"
    "    if r.get('status')!='finished' or not isinstance(r.get('ended'),(int,float)) or r['ended']<%r: continue\n"
    "    x={k:r.get(k) for k in ('unit','item','seat','status','at','ended','result','tokens','out','owed_close',"
    "'filing_refusals','conductor_text')}\n"
    "    if not x['conductor_text']:\n"
    "        try: x['tail']=' '.join(D.run_report(r, RL.read_result({'out':r.get('out') or '','err':r.get('err') or ''})).split())\n"
    "        except Exception as e: x['tail']='report UNMEASURED (%%s: %%s)'%%(type(e).__name__,e)\n"
    "    out.append(x)\n"
    "print(json.dumps(out))\n")


def host_ends(host, since, runner=subprocess.run):
    """-> the host's finished run records that ended at `since` or later (a list, [] when none), or None when the host
    cannot be read (could not look is never "no ends")."""
    target = door(host)
    if not target:
        return None
    try:
        r = runner(_ssh(target, "cd %s && python3 -c %s" % (BENCH, shlex.quote(_ENDS_PY % float(since)))),
                   capture_output=True, text=True, timeout=120, stdin=subprocess.DEVNULL)  # budget: class=ssh (hang guard)
        d = json.loads((r.stdout or "").strip().splitlines()[-1]) if r.returncode == 0 else None
    except Exception:  # noqa: BLE001
        return None
    return d if isinstance(d, list) else None


def end_line(host, x):
    """The Conductor log text for a host run's end: the host's own line text (its finish keeps it in conductor_text),
    else one made from its record, in the shape detached_helper.finish writes."""
    if x.get("conductor_text"):
        return "%s [on %s]" % (x["conductor_text"], host)
    import fulltext
    tok = x.get("tokens")
    took = int(x["ended"] - x["at"]) if isinstance(x.get("at"), (int, float)) else "UNMEASURED"
    owed = (" OWED: %s." % x["owed_close"]) if x.get("owed_close") else ""
    refused = "".join(" %s." % y for y in (x.get("filing_refusals") or []))
    return ("%s on %s (%s seat) on %s: %s, %s s, %s weighted tokens. %s. Output %s:%s. READ: rimflow show %s.%s%s"
            % (x.get("unit"), x.get("item"), x.get("seat"), host, x.get("result") or "UNMEASURED", took,
               "{:,}".format(tok) if isinstance(tok, (int, float)) else "UNMEASURED",
               fulltext.clip(x.get("tail"), 200, "%s:%s" % (host, x.get("out"))) or "-", host, x.get("out"),
               x.get("item"), owed, refused))


def relay_ends(host, now=None, runner=subprocess.run, log_path=None):
    """Each run that ended on `host` in the last RELAY_WINDOW_S and has no DETACHED RUN ENDED line in this machine's
    Conductor log gets one (the host's own finish cannot write it: the log is on this machine). -> (rc, text): 0 looked
    (n written, maybe none), 2 unknown host, 5 could not look (nothing written)."""
    import detached_helper as D
    now = time.time() if now is None else now
    if not door(host):
        return 2, "relay ends: unknown host %r" % host
    host = NAMES.get(_norm(host), host)     # its name in every line, whatever case the caller used
    path = log_path or D.conductor_log_path()
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            seen = [ln for ln in f.read().splitlines() if RELAY_HEAD in ln]
    except FileNotFoundError:
        seen = []
    except OSError as e:
        return 5, "relay ends: COULD NOT LOOK at the Conductor log %s: %s" % (path, e)
    ends = host_ends(host, now - RELAY_WINDOW_S, runner)
    if ends is None:
        return 5, "relay ends: COULD NOT LOOK at %s's run records (ssh)" % host
    wrote = []
    for x in sorted(ends, key=lambda y: y.get("ended") or 0):
        u = x.get("unit")
        if not u or any(u in ln for ln in seen):
            continue
        D.conductor_line(end_line(host, x), now, path, head=RELAY_HEAD)
        seen.append(u)
        wrote.append(u)
    return 0, "relay ends: %s: %d ended in %d days, %d new line(s) in %s%s" % (
        host, len(ends), RELAY_WINDOW_S // 86400, len(wrote), path, "".join("\n  " + u for u in wrote))


def stop_argv(rec, mode="at_easy_spot", why="stopped from Archmagi", end=False):
    """The host's own `./pipe stop <unit>` for a remote run (control.remote_stop runs it). end: the stop ends the work
    (`--end`; named only when set, so a host on older code still takes the default stop)."""
    target = door(rec.get("host"))
    if not target:
        raise ValueError("record names no known host: %r" % rec.get("host"))
    flag = "--" + mode.replace("_", "-") + (" --end" if end else "")
    return _ssh(target, "cd %s && ./pipe stop %s %s --why %s" % (BENCH, shlex.quote(rec["unit"]), flag,
                                                                  shlex.quote(why)))


def read_facts(host, item, picked_account=None, runner=subprocess.run):
    """Facts over ssh; a fact that could not be read stays None. picked_account None: the host's own live login."""
    h = door(host)
    f = {k: None for k in FACTS}
    f["clone"] = clone_of(item)
    if not h:
        return f

    def sh(cmd):
        try:
            r = runner(_ssh(h, cmd), capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
        except Exception:  # noqa: BLE001
            return None
        return r.stdout.strip() if r.returncode == 0 else None

    up = sh("echo up")
    f["reachable"] = up == "up"
    if up != "up":
        return f
    f["claude"] = sh("$HOME/.local/bin/claude --version") or None     # its full path: a systemd PATH lacks ~/.local/bin
    import account_live as AL       # the one reader of `live` in `claude-account --json status`

    def run_status(argv, timeout):  # its ssh argv, through this door with the login PATH
        r = runner(_ssh(h, argv[-1]), capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)
        return r.returncode, r.stdout
    f["account"] = AL.name_of(AL.read(target=h, run=run_status)) or None
    f["picked_account"] = picked_account or f["account"]
    f["push"] = (sh("ssh -T -o BatchMode=yes git@github-rimmandrake-write 2>&1; true") or "").lower().count(
        "successfully") > 0 or None
    f["launcher"] = {"yes": True, "no": False}.get(sh("test -f %s/%s && echo yes || echo no" % (BENCH, LAUNCHER)))
    free = sh("df -BG --output=avail / | tail -1 | tr -dc 0-9")
    f["free_gb"] = int(free) if free else None
    return f
