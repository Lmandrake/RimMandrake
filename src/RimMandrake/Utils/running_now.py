#!/usr/bin/env python3
"""running_now.py - the always-current page of what runs on this machine, for zero tokens.

Owner, 2026-11-03: "I definitely need some kind of markdown that gets regularly updated ... for zero tokens that just
tells me how many system elements are running in the background that I can't see ... it should just have a markdown up
at all times that constantly refreshes so I know what's running on the machine and how they relate in our system."
(ledger item RUNNING_PAGE_BUILD_WHO_IS_AWAKE.)

One plain Python script, no AI. Run by rm-running.timer every minute, on purpose NOT through the Dispatcher, so the page
still says so when the Dispatcher is dead. It reads processes, systemd, and state files other programs already write;
it never calls the game bridge and never uses ssh. A source it cannot read prints UNMEASURED, never 0.

    python3 running_now.py            write the page (atomic) and append one history sample
    python3 running_now.py --check    print the page's age; exit 1 when older than 3 minutes
    python3 running_now.py --print    build the page to stdout, write nothing

Related, not duplicated: STATUS_PAGES_BUILD_REPLACE_RIMPULSE builds the Relentless status HTML and RimPulse's successor
(brown HTML, ops trends). This page is the plain-markdown inventory of what is alive; that one is the work-progress view.
Family rules live in running_now_families.json beside this file.
"""
import csv
import io
import json
import os
import re
import statistics
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
AGENT = "/mnt/d/ClaudeWork/rimmandrake"
OUT_DIR = AGENT + "/conductor"
OUT = OUT_DIR + "/RUNNING_NOW.md"
HIST = OUT_DIR + "/running_history.jsonl"
STATE = OUT_DIR + "/running_state.json"
HIST_CAP = 10200            # one sample a minute: about 7 days and a bit
TASKLIST_EVERY = 180        # a tasklist.exe call is ~0.6 s wall: cache it
STALE_AFTER = 180           # a page older than this is stale
BRIDGE_FILES = ["/home/mandrake/rm/dispatch/infrastructure/state/BRIDGE", "/home/mandrake/rm/bench/infrastructure/state/BRIDGE"]
RELENTLESS_STORE = "/home/mandrake/rm/relentless/store"
PLAYER_LOG = "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Player.log"


class Unmeasured(Exception):
    """A source could not be read: the page says UNMEASURED and why, never a 0."""


# --------------------------------------------------------------------------- the real world (a selftest swaps this)
class Env:
    def now(self):
        return time.time()

    def run(self, argv, timeout=20):
        r = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout

    def ps(self):
        rc, out = self.run(["ps", "-eo", "pid,ppid,etimes,pcpu,comm,args", "-ww", "--no-headers"])
        if rc != 0:
            raise Unmeasured("ps exited %d" % rc)
        return out

    def cgroup(self, pid):
        try:
            return open("/proc/%d/cgroup" % pid).read()
        except OSError:
            return ""

    def cwd(self, pid):
        try:
            return os.readlink("/proc/%d/cwd" % pid)
        except OSError:
            return ""

    def units_json(self):
        pats = ["rm-*", "claude-*", "testq-*", "steve-*", "lodestar-*", "account-plan*", "hestia*"]
        rc, out = self.run(["systemctl", "--user", "list-units", "--all", "--output=json", "--no-pager"] + pats)
        if rc != 0:
            raise Unmeasured("systemctl list-units exited %d" % rc)
        return json.loads(out)

    def timers_json(self):
        rc, out = self.run(["systemctl", "--user", "list-timers", "--all", "--output=json", "--no-pager"])
        if rc != 0:
            raise Unmeasured("systemctl list-timers exited %d" % rc)
        return json.loads(out)

    def tick_limit_text(self):
        return self.run(["systemctl", "--user", "show", "rm-relentless.service", "-p", "TimeoutStartUSec"])[1]

    def last_failure(self, unit):
        rc, out = self.run(["journalctl", "--user", "-u", unit, "-g", "Failed with result", "-n", "1", "--no-pager",
                            "-o", "short-iso"])
        return out.strip()

    def tasklist(self):
        rc, out = self.run(["/mnt/c/Windows/System32/tasklist.exe", "/FO", "CSV", "/NH"], timeout=30)
        if rc != 0:
            raise Unmeasured("tasklist.exe exited %d" % rc)
        return out

    def read_json(self, path):
        with open(path) as f:
            return json.load(f)

    def read_text(self, path):
        with open(path, errors="replace") as f:
            return f.read()

    def mtime(self, path):
        return os.stat(path).st_mtime

    def count_dir(self, path):
        return len(os.listdir(path))

    def families(self):
        return self.read_json(os.path.join(HERE, "running_now_families.json"))

    def write_atomic(self, path, text):
        tmp = "%s.tmp.%d" % (path, os.getpid())
        with open(tmp, "w") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)


def guarded(fn, *a):
    """-> (value, None) or (None, why). Every source goes through here so one dead source never kills the page."""
    try:
        return fn(*a), None
    except Unmeasured as e:
        return None, str(e)
    except Exception as e:      # noqa: BLE001 - any failure is "could not read", with its reason
        return None, "%s: %s" % (type(e).__name__, str(e)[:120])


# --------------------------------------------------------------------------- small formatting helpers
def ago(sec):
    sec = int(max(sec, 0))
    if sec < 90:
        return "%d s" % sec
    if sec < 5400:
        return "%d min" % round(sec / 60)
    if sec < 172800:
        return "%.1f h" % (sec / 3600)
    return "%.1f d" % (sec / 86400)


def stamp(t, utc=False):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(t) if utc else time.localtime(t)) + ("Z" if utc else " " + time.strftime("%Z", time.localtime(t)))


def unm(why):
    return "**UNMEASURED** (%s)" % why


def plural(n, one, many=None):
    return "%d %s" % (n, one if n == 1 else (many or one + "s"))


# --------------------------------------------------------------------------- classification
class Table:
    def __init__(self, raw):
        self.raw = raw
        self.units = [(re.compile(p), fam, lab) for p, fam, lab in raw["units"]]
        self.procs = [(re.compile(p), fam, lab) for p, fam, lab in raw["procs"]]

    def unit(self, name):
        for rx, fam, lab in self.units:
            m = rx.search(name)
            if m:
                return fam, lab, m
        return None

    def cgroup_unit(self, cg):
        """The first path component of a cgroup that the table knows -> (component, family, label, match)."""
        for line in cg.splitlines():
            for comp in line.split("/"):
                if comp.endswith((".service", ".scope")) and not comp.startswith(("user@", "init.")):
                    hit = self.unit(comp)
                    if hit:
                        return (comp,) + hit
        return None

    def proc(self, args):
        for rx, fam, lab in self.procs:
            if rx.search(args):
                return fam, lab
        return None


def parse_ps(text):
    rows = []
    for line in text.splitlines():
        p = line.split(None, 5)
        if len(p) < 6:
            continue
        try:
            rows.append({"pid": int(p[0]), "ppid": int(p[1]), "age": int(p[2]), "cpu": float(p[3]), "comm": p[4], "args": p[5]})
        except ValueError:
            continue
    return rows


def is_agent_proc(r):
    return r["comm"] == "claude" or "/claude/versions/" in r["args"].split(" ", 1)[0]


def is_watched(r):
    """Processes the 'Not recognised' rule applies to: claude, python, node, codex."""
    c = r["comm"].lower()
    return is_agent_proc(r) or c.startswith(("python", "node", "codex")) or r["args"].split(" ", 1)[0].endswith(("python3", "python"))


def short_args(r):
    """A safe one-line description: never a prompt (claude -p text can be a page long)."""
    a = r["args"]
    if is_agent_proc(r):
        m = re.search(r"--name\s+(\S+(?: \S+)?)", a)
        return "claude %s" % (("window " + m.group(1).split(" --")[0]) if m else ("-p run" if " -p " in a or " --print" in a else "session"))
    a = re.sub(r"\s+", " ", a)
    return a if len(a) <= 110 else a[:109] + "..."


def classify_processes(env, table, rows):
    """-> things {(family, key): info}, unrecognised [rows], busiest [rows]. Counts units, not processes."""
    things, unrecog = {}, []
    for r in rows:
        if not is_watched(r):
            continue
        cg = env.cgroup(r["pid"])
        hit = table.cgroup_unit(cg)
        r["unit"] = hit[0] if hit else ""
        r["cwd"] = env.cwd(r["pid"]) if is_agent_proc(r) or r["comm"].startswith("python") else ""
        r["family"], r["label"] = None, ""
        if hit:
            comp, fam, lab, m = hit
            r["family"], r["label"] = fam, lab
            gd = m.groupdict()
            # a role run is both claude-seat-X-rm-role-... (scope) and rm-role-... (service): the id dedupes them
            key = (fam, gd.get("id") or comp)
            th = things.setdefault(key, {"family": fam, "label": lab, "unit": comp, "who": gd.get("who", ""), "kind": gd.get("kind", ""),
                                         "age": r["age"], "claude": False, "cwd": "", "name": "", "procs": 0, "cpu": 0.0})
            th["age"] = max(th["age"], r["age"])
            th["procs"] += 1
            th["cpu"] += r["cpu"]
            if is_agent_proc(r):
                th["claude"] = True
                th["cwd"] = th["cwd"] or r["cwd"]
                nm = re.search(r"--name\s+(\S+)", r["args"])
                th["name"] = th["name"] or (nm.group(1) if nm else "")
            continue
        pr = table.proc(r["args"])
        if pr:
            r["family"], r["label"] = pr
            continue
        unrecog.append(r)
    return things, unrecog


# --------------------------------------------------------------------------- collectors (each raises Unmeasured)
def collect_tasklist(env, state):
    """Windows process counts, cached TASKLIST_EVERY seconds. powershell is avoided (slow, steals focus)."""
    now = env.now()
    c = state.get("win")
    if c and now - c.get("t", 0) < TASKLIST_EVERY and c.get("ok"):
        return dict(c, cached_age=now - c["t"])
    raw = env.tasklist()
    counts, mem = {}, {}
    for row in csv.reader(io.StringIO(raw)):
        if len(row) < 5:
            continue
        n = row[0].lower()
        counts[n] = counts.get(n, 0) + 1
        mem[n] = row[4]
    out = {"t": now, "ok": True, "game": counts.get("rimworldwin64.exe", 0), "codex": counts.get("codex.exe", 0),
           "python_exe": counts.get("python.exe", 0), "game_mem": mem.get("rimworldwin64.exe", ""), "cached_age": 0}
    state["win"] = out
    return out


def collect_dispatcher(env):
    s = env.read_json(AGENT + "/dispatcher/state.json")
    t = s.get("last_tick") or s.get("last_ok_tick")
    if not t:
        raise Unmeasured("dispatcher state.json has no last_tick")
    epoch = time.mktime(time.strptime(t, "%Y-%m-%dT%H:%M:%SZ")) - time.timezone
    ok = s.get("last_ok_tick")
    ok_epoch = time.mktime(time.strptime(ok, "%Y-%m-%dT%H:%M:%SZ")) - time.timezone if ok else None
    return {"tick": epoch, "ok_tick": ok_epoch, "roles_today": None}


def collect_relentless(env):
    s = env.read_json(RELENTLESS_STORE + "/staffing.json")
    t = s.get("t")
    if not isinstance(t, (int, float)):
        raise Unmeasured("staffing.json has no timestamp")
    return {"t": t, "places": s.get("places"), "target": s.get("target"), "running": s.get("running"), "ready": s.get("ready"),
            "why": s.get("why"), "checks": s.get("checks") or {}}


def relentless_item(env, unit):
    """The ledger item a worker unit belongs to: the unit name is recorded in the item's state.json."""
    base = RELENTLESS_STORE + "/items"
    m = re.search(r"rm-relentless-\w+-([0-9a-f]{10})-g", unit)
    if not m:
        return ""
    try:
        for d in os.listdir(base):
            p = "%s/%s/state.json" % (base, d)
            try:
                if unit.replace(".service", "") in env.read_text(p):
                    return d
            except OSError:
                continue
    except OSError:
        pass
    return ""


def collect_steve(env):
    sj = env.read_json(AGENT + "/testq/steward.json")
    ss = None
    try:
        ss = env.read_json(AGENT + "/testq/ssh_state.json")
    except Exception:       # noqa: BLE001 - ssh state is an extra, the steward record decides
        pass
    ep = sj.get("epoch")
    if not isinstance(ep, (int, float)):
        raise Unmeasured("steward.json has no epoch")
    return {"state": sj.get("state"), "fault": sj.get("fault"), "reason": sj.get("reason") or "", "epoch": ep, "since": sj.get("since"),
            "down_since": (ss or {}).get("down_since"), "last_probe": (ss or {}).get("last_probe")}


def collect_bridge(env):
    last = None
    for p in BRIDGE_FILES:
        try:
            txt = env.read_text(p)
        except OSError:
            continue
        m = re.search(r"^(HELD|FREE)\s*(\S*)\s*(?:since\s+(\S+))?", "\n".join(l for l in txt.splitlines() if not l.startswith("#")), re.M)
        why = re.search(r"^for\s+(.*)$", txt, re.M)
        if m:
            mt = env.mtime(p)
            if last is None or mt > last["mt"]:
                last = {"state": m.group(1), "who": m.group(2), "since": m.group(3), "for": why.group(1) if why else "", "mt": mt, "path": p}
    if not last:
        raise Unmeasured("no BRIDGE mirror file readable")
    return last


def collect_art(env):
    out = {}
    for d in ("active", "pending"):
        out[d] = env.count_dir(AGENT + "/artpipe/" + d)
    return out


# --------------------------------------------------------------------------- history
def read_history(env):
    try:
        text = env.read_text(HIST)
    except OSError:
        return []
    out = []
    for line in text.splitlines():
        try:
            r = json.loads(line)
            if isinstance(r.get("t"), (int, float)) and isinstance(r.get("n"), int):
                out.append(r)
        except ValueError:
            continue
    return out


def append_history(env, hist, sample):
    hist.append(sample)
    if len(hist) > HIST_CAP + 300:
        hist[:] = hist[-HIST_CAP:]
        env.write_atomic(HIST, "".join(json.dumps(r, separators=(",", ":")) + "\n" for r in hist))
    else:
        with open(HIST, "a") as f:
            f.write(json.dumps(sample, separators=(",", ":")) + "\n")


def window_stats(hist, now, secs, label):
    rows = [r for r in hist if now - r["t"] <= secs]
    if not rows:
        return "last %s: no history yet" % label, None
    span = now - min(r["t"] for r in rows)
    ns = [r["n"] for r in rows]
    note = "" if span >= secs * 0.95 else " (history only covers %s so far, so this is not yet a full %s)" % (ago(span), label)
    return ("last %s: min %d / median %d / max %d things, from %d readings%s" % (label, min(ns), int(statistics.median(ns)), max(ns), len(ns), note)), rows


# --------------------------------------------------------------------------- the page
def build(env, state, hist):
    now = env.now()
    fam = env.families()
    table = Table(fam)
    F = fam["families"]
    notes = []          # (family, text)  UNMEASURED lines roll up here as well
    unmeasured = []

    ps_text, why = guarded(env.ps)
    rows = parse_ps(ps_text) if ps_text else []
    if why:
        unmeasured.append("processes (%s)" % why)
    things, unrecog = ({}, [])
    if ps_text:
        things, unrecog = classify_processes(env, table, rows)

    units, why_u = guarded(env.units_json)
    if why_u:
        unmeasured.append("systemd units (%s)" % why_u)
    timers, why_t = guarded(env.timers_json)
    if why_t:
        unmeasured.append("systemd timers (%s)" % why_t)
    win, why_w = guarded(collect_tasklist, env, state)
    if why_w:
        unmeasured.append("Windows processes (%s)" % why_w)

    # fold systemd units into the same things map so a role (service + scope) or a worker counts once
    for u in units or []:
        n, act = u["unit"], u["active"]
        if act not in ("active", "activating", "deactivating") or n.endswith((".timer", ".slice", ".path", ".socket")):
            continue
        hit = table.unit(n)
        if not hit:
            continue
        f, lab, m = hit
        if n in ("dbus.service", "ssh-agent.service"):
            continue
        gd = m.groupdict()
        key = (f, gd.get("id") or n)
        th = things.setdefault(key, {"family": f, "label": lab, "unit": n, "who": gd.get("who", ""), "kind": gd.get("kind", ""),
                                     "age": None, "claude": False, "cwd": "", "name": "", "procs": 0, "cpu": 0.0})
        th["state"] = u["sub"]
        th["desc"] = u.get("description", "")
        th["svc"] = True
        if act == "activating" or u["sub"] in ("start", "start-pre"):
            th["midrun"] = True

    # ours / other project for seats, by working directory
    for th in things.values():
        if th["family"] == "seats":
            if th["cwd"] and not th["cwd"].startswith("/home/mandrake/rm/"):
                th["family"] = "other"
                th["label"] = "window of another project"
        if th["family"] == "tests" and th["unit"].endswith(".scope") is False and th.get("midrun"):
            th["label"] = "Steve-lane job"

    by = {f: [] for f in fam["order"]}
    for th in things.values():
        by.setdefault(th["family"], []).append(th)

    def cnt(f, pred=lambda t: True):
        return sum(1 for t in by.get(f, []) if pred(t))

    # ---- totals line
    counts = {}
    counts["game"] = win["game"] if win else None
    seats_ours = cnt("seats")
    agents = seats_ours + cnt("roles") + cnt("helpers") + cnt("relentless", lambda t: t["label"] == "worker")
    counts["agents"] = agents if ps_text else None
    counts["codex"] = win["codex"] if win else None
    counts["tests"] = cnt("tests") if (ps_text or units) else None
    svc = lambda t: t.get("svc") and t.get("state") == "running" and not t.get("claude")   # noqa: E731
    daemons = sum(cnt(f, svc) for f in ("art", "monitors", "upkeep", "dispatcher", "relentless")) if units else None
    counts["services"] = daemons
    mid = sum(cnt(f, lambda t: t.get("midrun") and f != "tests") for f in fam["order"]) if units else None
    counts["midrun"] = mid
    counts["other"] = cnt("other") if (ps_text or units) else None
    counts["unrecognised"] = len(unrecog) + (win["python_exe"] if win else 0) if (ps_text and win) else (len(unrecog) if ps_text else None)

    def show(label, n, one, many=None):
        return unm("%s" % label) if n is None else plural(n, one, many)

    total_known = sum(v for v in counts.values() if v is not None)
    parts = [
        show("game", counts["game"], "game"),
        show("agents", counts["agents"], "AI agent"),
        show("codex", counts["codex"], "Codex image job"),
        show("tests", counts["tests"], "test run"),
        show("services", counts["services"], "standing service"),
        show("jobs", counts["midrun"], "timer job running right now", "timer jobs running right now"),
        show("other", counts["other"], "thing from other projects", "things from other projects"),
        show("unrecognised", counts["unrecognised"], "not recognised", "not recognised"),
    ]
    n_timers = len(timers) if timers is not None else None
    sample_n = total_known

    # ---- dispatcher
    disp, why_d = guarded(collect_dispatcher, env)
    if why_d:
        unmeasured.append("Dispatcher state (%s)" % why_d)
    dline_head = ""
    banners = []
    if disp:
        age = now - disp["tick"]
        if age > 360:
            banners.append("**DISPATCHER NOT TICKING: its last tick was %s ago (it should tick every 2 minutes).** Nothing is launching roles or restarting seats." % ago(age))
        dline_head = "Dispatcher last ticked **%s ago** (%s)" % (ago(age), "healthy" if age <= 360 else "LATE")
    else:
        dline_head = "Dispatcher last tick: " + unm(why_d)

    # ---- stale banner from the previous state
    prev_ok = state.get("ok_t")
    gap = (now - prev_ok) if prev_ok else None
    if gap is not None and gap > STALE_AFTER + 30:
        state["stale"] = {"from": prev_ok, "to": now, "why": state.get("last_error", "") or "no reading was written (timer missed or machine was off)"}
    sb = state.get("stale")
    if sb and now - sb["to"] < 600:
        banners.insert(0, "**STALE since %s:** this page was not refreshed for %s (until %s). Reason: %s. Numbers below are fresh again." % (
            stamp(sb["from"]), ago(sb["to"] - sb["from"]), stamp(sb["to"]), sb["why"]))
    elif sb:
        state.pop("stale", None)

    # ---- sections
    S = []

    def sec(f, body_lines):
        S.append("## %s\n_%s_\n\n%s\n" % (F[f]["title"], F[f]["plain"], "\n".join(body_lines) if body_lines else "Nothing running."))

    # seats
    L = []
    for t in sorted(by.get("seats", []), key=lambda t: t["who"] + t["unit"]):
        L.append("- %s window, clone `%s`, up %s%s" % ((t["name"] or t["who"]).title() if (t["name"] or t["who"]).isupper() else (t["name"] or t["who"]),
                 t["cwd"].replace("/home/mandrake/rm/", "") or "?", ago(t["age"] or 0), " (seat scope for %s)" % t["who"] if t["who"] != "unknown" else ""))
    if not ps_text:
        L = [unm("process list unreadable")]
    sec("seats", L)

    # dispatcher
    L = ["- " + dline_head]
    if timers:
        for tm in timers:
            if tm["unit"] == "rm-dispatcher.timer":
                L.append("- Its timer fired %s ago; next in %s." % (ago(now - tm["last"] / 1e6) if tm["last"] else "never", ago(tm["next"] / 1e6 - now) if tm["next"] else "UNKNOWN"))
    if disp and disp.get("ok_tick") and disp["ok_tick"] != disp["tick"]:
        L.append("- Last fully clean tick: %s ago." % ago(now - disp["ok_tick"]))
    sec("dispatcher", L)

    # relentless
    rel, why_r = guarded(collect_relentless, env)
    L = []
    if rel:
        a = now - rel["t"]
        L.append("- Places staffed **%s of target %s** (%s workers running, %s items ready); this reading was written %s ago%s. Reason it gives: %s." % (
            rel["places"], rel["target"], rel["running"], rel["ready"], ago(a), " - STALE, the tick has not finished since" if a > 600 else "", rel["why"]))
    else:
        unmeasured.append("Relentless staffing (%s)" % why_r)
        L.append("- Staffing record: " + unm(why_r))
    tick = [t for t in by.get("relentless", []) if t["label"] == "tick"]
    limit = re.search(r"=(\d+)(min|s)", env.tick_limit_text() if units else "")
    lim_min = int(limit.group(1)) * (1 if limit.group(2) == "min" else 1 / 60) if limit else None
    if tick and tick[0].get("midrun"):
        age_t = tick[0]["age"]
        L.append("- The Relentless tick is **running now**%s (limit %s)." % (" for %s" % ago(age_t) if age_t is not None else "", ("%d min" % lim_min) if lim_min else UNMEASURED_WORD))
    elif units is not None:
        L.append("- The Relentless tick is not running at this moment.")
    fail = env.last_failure("rm-relentless.service") if units else ""
    mf = re.match(r"(\S+)\s.*Failed with result '(\w+)'", fail)
    L.append("- Last tick that ended badly: %s." % ("%s (%s)" % (mf.group(1)[:16].replace("T", " "), "ran past its time limit and was killed" if mf.group(2) == "timeout" else mf.group(2)) if mf else "none found in the journal"))
    workers = [t for t in by.get("relentless", []) if t["label"] == "worker"]
    L.append("- Workers right now: **%d**%s" % (len(workers), ":" if workers else "."))
    for t in sorted(workers, key=lambda t: t["unit"]):
        item = relentless_item(env, t["unit"]) or "item not found"
        L.append("  - %s for `%s`, up %s" % ("blind checker" if t["kind"] == "check" else t["kind"] + " worker", item, ago(t["age"]) if t["age"] is not None else "?"))
    sec("relentless", L)

    # helpers
    L = []
    for t in sorted(by.get("helpers", []), key=lambda t: t["unit"]):
        slug = t["unit"]
        slug = re.sub(r"^claude-seat-[A-Za-z]+-", "", slug)
        slug = re.sub(r"^rm-detached-", "", slug)
        slug = re.sub(r"-\d{9,}.*$", "", slug)
        L.append("- `%s`, up %s" % (slug, ago(t["age"]) if t["age"] is not None else "?"))
    sec("helpers", L if ps_text else [unm("process list unreadable")])

    # roles
    L = []
    for t in sorted(by.get("roles", []), key=lambda t: t["unit"]):
        role = re.search(r"rm-role-([a-z]+)-", t["unit"])
        L.append("- %s role run, up %s" % ((role.group(1).title() if role else t["unit"]), ago(t["age"]) if t["age"] is not None else "?"))
    sec("roles", L if ps_text else [unm("process list unreadable")])

    # art
    L = []
    art_up = [t for t in by.get("art", []) if "artpiped" in t["unit"]]
    L.append("- artpiped daemon: %s" % ("**running**, up %s" % ago(art_up[0]["age"]) if art_up and art_up[0]["age"] is not None else ("**running**" if art_up else "**NOT RUNNING**" if units is not None else unm("systemd unreadable"))))
    L.append("- codex.exe renders on Windows right now: %s" % (("**%d**" % win["codex"] + (" (reading %s old)" % ago(win["cached_age"]) if win["cached_age"] > 1 else "")) if win else unm(why_w)))
    art, why_a = guarded(collect_art, env)
    L.append("- Art queue: %s" % ("%d being worked, %d waiting" % (art["active"], art["pending"]) if art else unm(why_a)))
    sec("art", L)

    # monitors
    L = []
    mon_t = [tm for tm in (timers or []) if (table.unit(tm["unit"]) or ("",))[0] == "monitors"]
    if timers is not None:
        late = [tm["unit"] for tm in mon_t if tm["next"] and tm["next"] / 1e6 < now - 300]
        L.append("- %d monitor timers installed%s." % (len(mon_t), "; **late: %s**" % ", ".join(late) if late else ", none late"))
        failed = [u["unit"] for u in (units or []) if u["active"] == "failed" and (table.unit(u["unit"]) or ("",))[0] == "monitors"]
        L.append("- Monitor jobs in a failed state: %s" % (", ".join(failed) if failed else "none"))
    else:
        L.append("- Monitor timers: " + unm(why_t))
    pulse = [t for t in by.get("monitors", []) if "pulse" in t["unit"] and t.get("state") == "running"]
    L.append("- RimPulse server (being retired, see STATUS_PAGES_BUILD_REPLACE_RIMPULSE): %s" % ("running" if pulse else "not running" if units is not None else unm("systemd unreadable")))
    sec("monitors", L)

    # tests
    L = []
    harness = [t for t in by.get("tests", []) if "harness" in t["unit"]]
    L.append("- Selftest files running now on this machine: **%d**" % len(harness) if (ps_text or units) else "- Selftests: " + unm("neither process list nor systemd readable"))
    sv, why_s = guarded(collect_steve, env)
    if sv:
        hb = now - sv["epoch"]
        L.append("- Steve lane (SteveDesktop): **%s**%s. Steward last wrote %s ago%s." % (
            sv["state"], " (fault)" if sv["fault"] else "", ago(hb), "; STALE, treat as its last word" if hb > 1800 else ""))
        if sv["reason"]:
            L.append("  - Why: %s" % sv["reason"][:220])
        if sv["down_since"]:
            L.append("  - SSH to the Steve PC has been down since %s." % sv["down_since"])
        elif sv["last_probe"]:
            L.append("  - SSH probe last succeeded %s ago (read from the file; this page makes no ssh call)." % ago(now - sv["last_probe"]))
    else:
        unmeasured.append("Steve lane (%s)" % why_s)
        L.append("- Steve lane: " + unm(why_s))
    sec("tests", L)

    # game
    L = []
    if win:
        L.append("- RimWorld: **%s**%s" % ("running" if win["game"] else "not running", " (memory %s, reading %s old)" % (win["game_mem"], ago(win["cached_age"])) if win["game"] else ""))
    else:
        L.append("- RimWorld: " + unm(why_w))
    br, why_b = guarded(collect_bridge, env)
    if br:
        L.append("- Bridge: **%s** by %s since %s%s" % (br["state"].lower(), br["who"] or "nobody", br["since"] or "?", (' - "%s"' % br["for"][:140]) if br["for"] else ""))
    else:
        L.append("- Bridge holder: " + unm(why_b))
    pl, why_l = guarded(env.mtime, PLAYER_LOG)
    L.append("- Game log last written %s ago." % ago(now - pl) if pl else "- Game log: " + unm(why_l))
    L.append("- Game tick: " + unm("only the bridge knows it, and this page never calls the bridge"))
    sec("game", L)

    # other projects
    L = []
    for t in sorted(by.get("other", []), key=lambda t: t["unit"]):
        L.append("- %s (%s)" % ((t["name"] or t.get("desc") or t["unit"]), t["label"]))
    sec("other", L)

    # upkeep
    L = []
    ups = [t for t in by.get("upkeep", []) if t.get("svc")]
    for t in sorted(ups, key=lambda t: t["unit"]):
        L.append("- %s: %s" % (t["unit"], t.get("desc", "")[:80]))
    sec("upkeep", L)

    # not recognised
    if ps_text:
        if unrecog:
            R = ["- pid %d, %s, up %s, CPU %.0f%% (average since start), cwd `%s`: `%s`" % (r["pid"], r["comm"], ago(r["age"]), r["cpu"], r["cwd"] or "?", short_args(r)) for r in unrecog[:15]]
        else:
            R = ["Every claude, python, node and codex process on the Linux side is matched by the family table."]
        if win and win["python_exe"]:
            R.append("- %s python.exe on Windows: the command line is not read (a cheap read would need powershell); mostly test scripts started from a window." % win["python_exe"])
    else:
        R = [unm("process list unreadable")]
    S.append("## Not recognised\n_Running python, claude, node or codex but matched by no rule in `running_now_families.json`. Nothing is hidden: if a line is here, someone should say what it is and add a rule._\n\n%s\n" % "\n".join(R))

    # busiest
    busy = sorted([r for r in rows if r["cpu"] >= 50 and r["age"] >= 20], key=lambda r: -r["cpu"])[:5]
    B = ["- pid %d, %.0f%% CPU (average since it started), up %s, belongs to %s: `%s`" % (
        r["pid"], r["cpu"], ago(r["age"]), (table.cgroup_unit(env.cgroup(r["pid"])) or ["outside the family table"])[0], short_args(r)) for r in busy] or ["No process older than 20 s averages above 50% CPU."]
    S.append("## Busiest processes right now\n%s\n" % "\n".join(B))

    # timers
    T = []
    if timers is not None:
        info = {u["unit"]: u for u in (units or [])}
        mine = sorted(timers, key=lambda tm: tm["unit"])
        T.append("| timer | what it does | last ran | next run |\n|---|---|---|---|")
        for tm in mine:
            last = "%s ago" % ago(now - tm["last"] / 1e6) if tm["last"] else "never"
            nxt = "in %s" % ago(tm["next"] / 1e6 - now) if tm["next"] and tm["next"] / 1e6 >= now else ("**OVERDUE %s**" % ago(now - tm["next"] / 1e6) if tm["next"] else "none scheduled")
            if info.get(tm["unit"], {}).get("sub") == "running":
                nxt = "running now"
            d = info.get(tm["unit"], {}).get("description", "")
            T.append("| %s | %s | %s | %s |" % (tm["unit"].replace(".timer", ""), d[:70], last, nxt))
        n_rm = sum(1 for tm in timers if tm["unit"].startswith("rm-"))
        T.insert(0, "%d timers installed (%d named rm-*), plus 1 path watcher (rm-restart-now) that reacts when a window says it is ready to restart.\n" % (len(timers), n_rm))
    else:
        T.append(unm(why_t))
    S.append("## Timers (all installed, last and next run)\n%s\n" % "\n".join(T))

    # typical
    tp = []
    w24, r24 = window_stats(hist, now, 86400, "24 h")
    w7, r7 = window_stats(hist, now, 7 * 86400, "7 d")
    tp.append("- %s" % w24)
    tp.append("- %s" % w7)
    if hist:
        tp.append("- History file holds %d readings covering %s (one per minute, capped at about 7 days)." % (len(hist), ago(now - min(r["t"] for r in hist))))
    if r24:
        tp.append("\n| family | now | median 24 h | max 24 h |\n|---|---|---|---|")
        for k, label in (("game", "game"), ("agents", "AI agents"), ("codex", "Codex jobs"), ("tests", "test runs"), ("services", "standing services"), ("midrun", "timer jobs mid-run"), ("unrecognised", "not recognised")):
            vals = [r["f"].get(k) for r in r24 if isinstance(r.get("f"), dict) and r["f"].get(k) is not None]
            if vals:
                tp.append("| %s | %s | %d | %d |" % (label, counts[k] if counts.get(k) is not None else "UNMEASURED", statistics.median(vals), max(vals)))
    S.append("## How many run, typically\n_\"Things\" is the number in the headline. It counts running units, not every helper process, and leaves the waiting timers out._\n\n%s\n" % "\n".join(tp))

    relate = """```
 You (owner) --> Conductor window --> detached helpers   one task each, own unit, end with a ledger note
                    |
 Dispatcher  (program, every 2 min, no AI) --> launches role runs (Operations, Arbiter...) and restarts seats
     ^  runs ops-watch every 15 min --> alarms --> Dispatcher wakes an Operations run to fix them
 Relentless  (own timer, every 2 min) --> a worker per item in a private clone, then a blind checker; target 8
 deadman     (every 15 min) rechecks each "done means running" promise and reopens an item whose thing died
 Art pipe    artpiped --> codex.exe renders --> auto-judge --> review sheets for you
 Test lanes  selftests here; the Steve lane on SteveDesktop over ssh (testq timers), braked when fillers fail
 Game        one live user at a time (the bridge holder); Relentless items that need it wait their turn
 This page   its own 1-minute timer, outside the Dispatcher on purpose
```"""
    S.append("## How these relate\n%s\n\n_Related page: STATUS_PAGES_BUILD_REPLACE_RIMPULSE builds the Relentless progress pages and RimPulse's replacement; this page only says what is alive._\n" % relate)

    head = ["# What is running on this machine",
            "**Updated %s (%s).** Refreshed every minute with no AI. If this time is more than 3 minutes old, the refresher itself has stopped." % (stamp(now), stamp(now, True)),
            ""]
    for b in banners:
        head.append("> " + b)
        head.append("")
    head.append("**%d things running:** %s%s" % (total_known, ", ".join(parts), ("; plus **%d** timers waiting their turn" % n_timers) if n_timers is not None else "; timers: " + unm(why_t)))
    head.append("")
    head.append("- " + dline_head)
    if unmeasured:
        head.append("- **UNMEASURED this minute:** " + "; ".join(unmeasured) + ". The total above counts only what could be read.")
    head.append("")
    head.append("<!-- running_now updated_epoch=%d -->" % int(now))
    page = "\n".join(head) + "\n" + "\n".join(S)
    fcounts = {k: v for k, v in counts.items() if v is not None}
    return page, {"t": int(now), "n": sample_n, "f": fcounts}


UNMEASURED_WORD = "UNMEASURED"


def run(env=None, write=True):
    env = env or Env()
    os.makedirs(OUT_DIR, exist_ok=True) if write else None
    try:
        state = env.read_json(STATE)
    except Exception:       # noqa: BLE001 - first run or torn state: start fresh
        state = {}
    hist = read_history(env)
    try:
        page, sample = build(env, state, hist)
    except Exception as e:      # noqa: BLE001 - leave the old page, remember why, fail loudly
        state["last_error"] = "%s: %s" % (type(e).__name__, str(e)[:160])
        state["fail_since"] = state.get("fail_since") or env.now()
        if write:
            env.write_atomic(STATE, json.dumps(state))
        print("running_now FAILED: %s" % state["last_error"], file=sys.stderr)
        return 1, ""
    if write:
        env.write_atomic(OUT, page)
        append_history(env, hist, sample)
        state["ok_t"] = env.now()
        state.pop("fail_since", None)
        state.pop("last_error", None)
        env.write_atomic(STATE, json.dumps(state))
    return 0, page


def check():
    try:
        age = time.time() - os.stat(OUT).st_mtime
    except OSError as e:
        print("RUNNING_NOW.md: UNMEASURED (%s)" % e)
        return 1
    print("RUNNING_NOW.md is %s old%s" % (ago(age), "" if age <= STALE_AFTER else " - STALE (limit 3 min)"))
    return 0 if age <= STALE_AFTER else 1


if __name__ == "__main__":
    if "--check" in sys.argv:
        sys.exit(check())
    rc, page = run(write="--print" not in sys.argv)
    if "--print" in sys.argv:
        print(page)
    sys.exit(rc)
