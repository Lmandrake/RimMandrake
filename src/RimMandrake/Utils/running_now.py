#!/usr/bin/env python3
"""running_now.py - a one-minute snapshot of what runs: numbers, trees and diagrams from programs only, for zero tokens.

Owner, 2026-11-03 (RUNNING_PAGE_BUILD_WHO_IS_AWAKE, then RUNNING_PAGE_BUILD_SNAPSHOT_NOT_NARRATIVE): "much more
streamlined ... how many Relentless Agents are running, and how many background processes do each of them use? They
should be shown as a branching tree down from Dispatch. Much less Prose ... a snapshot of what's running ... SteveDesktop
needs a lot more basic stats ... way more SVG or asciiart diagrams ... no AI, just templated info ... The Relentless
pipelines is especially important to make beautiful."

Run by rm-running.timer every minute, on purpose NOT through the Dispatcher, so the page still says so when the
Dispatcher is dead. It reads processes, systemd and state files other programs already write. It never calls the game
bridge. A source it cannot read prints UNMEASURED, never 0. The page is written BEFORE the one ssh probe of SteveDesktop
(at most every PROBE_EVERY seconds, short timeouts, result cached in running_steve.json), so ssh can never block the page.

    python3 running_now.py            write the page (atomic), append a history sample, refresh the Steve cache if old
    python3 running_now.py --check    print the page's age; exit 1 when older than 3 minutes
    python3 running_now.py --print    build the page to stdout, write nothing, no ssh

Family rules live in running_now_families.json beside this file. The page is viewed in Typora, which renders inline SVG
(screenshot proof in the item's note); every SVG panel has a plain text twin in the collapsed section at the bottom.
"""
import calendar
import collections
import csv
import glob
import hashlib
import io
import json
import os
import re
import socket
import statistics
import subprocess
import sys
import time
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
AGENT = "/mnt/d/ClaudeWork/rimmandrake"
OUT_DIR = AGENT + "/conductor"
OUT = OUT_DIR + "/RUNNING_NOW.md"
HIST = OUT_DIR + "/running_history.jsonl"
STATE = OUT_DIR + "/running_state.json"
STEVE_CACHE = OUT_DIR + "/running_steve.json"
TESTQ = AGENT + "/testq"
HIST_CAP = 10200            # one sample a minute: about 7 days and a bit
TASKLIST_EVERY = 180        # a tasklist.exe call is ~0.6 s wall: cache it
PROBE_EVERY = 180           # ssh to SteveDesktop at most this often
STALE_AFTER = 180           # a page older than this is stale
FENCE_WIDTH = 84            # Typora wraps a code fence at about 87 columns in a 1600 px window
BRIDGE_FILES = ["/home/mandrake/rm/dispatch/infrastructure/state/BRIDGE", "/home/mandrake/rm/bench/infrastructure/state/BRIDGE"]
LEDGER_EVENTS = "/home/mandrake/rm/dispatch/infrastructure/state/ledger/events"
RELENTLESS_STORE = "/home/mandrake/rm/relentless/store"
JOURNAL_TAIL = 6 * 1024 * 1024      # the journal grew 2.6 MB in 3 days: this tail holds far more than 24 h
STEVE_SSH = "stevedesktop-wsl"
STEVE_TS_PEER = "stevedesktop"
STEVE_LAN = "192.168.86.62"
STEVE_SCRIPT = r"""
echo up=$(cut -d" " -f1 /proc/uptime)
echo load=$(cut -d" " -f1 /proc/loadavg)
echo cores=$(nproc)
echo stat=$(grep "^cpu " /proc/stat)
free -m | awk '/^Mem:/{print "ram="$3" "$2}'
df -BG / | awk 'NR==2{gsub("G","",$2);gsub("G","",$4);print "disk="$4" "$2}'
echo claude=$(pgrep -c -x claude)
if t=$(timeout 5 /mnt/c/Windows/System32/tasklist.exe /FO CSV /NH /FI "IMAGENAME eq RimWorldWin64.exe" </dev/null 2>/dev/null); then echo "game=$(printf "%s\n" "$t" | grep -c RimWorldWin64)"; fi
timeout 5 /usr/lib/wsl/lib/nvidia-smi --query-gpu=name,utilization.gpu,memory.used,memory.total --format=csv,noheader,nounits </dev/null 2>/dev/null | head -1 | tr -d "\r" | sed s/^/gpu=/
"""

# Real Relentless status names (relentless.py: HOLDS_A_PLACE, RUNS_A_PLACE, PUT_DOWN, ENDED).
RUNS_A_PLACE = ("running", "checking", "stopping", "retiring")
BELT = ("queued", "running", "candidate", "checking", "closing", "done")
SIDE = ("game", "held", "blocked", "stopping", "retiring", "retired")
BELT_WORD = {"queued": "waits for a place", "running": "worker builds", "candidate": "waits for a check",
             "checking": "blind checker", "closing": "being landed", "done": "closed"}
SIDE_WORD = {"game": "needs the live game", "held": "held for a person", "blocked": "waits on another item",
             "stopping": "being stopped", "retiring": "being retired", "retired": "dropped for good"}

BG, CARD, EDGE, TEXT, DIM, FAINT = "#14171c", "#1f242c", "#3a4250", "#e8eaee", "#98a1af", "#5d6675"
GOOD, WARN, BAD, LIVE, BAR = "#4cc38a", "#f0b429", "#ef5350", "#5aa9e6", "#7d8796"
MONO = "Consolas,'JetBrains Mono',monospace"
SANS = "'Segoe UI',Helvetica,Arial,sans-serif"


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

    def self_pid(self):
        return os.getpid()

    def cgroup(self, pid):
        try:
            with open("/proc/%d/cgroup" % pid) as f:
                return f.read()
        except (FileNotFoundError, ProcessLookupError):
            return ""       # it ended after ps listed it

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

    def tick_show(self):
        """The Relentless tick unit's timing, with the monotonic clock those timestamps are on."""
        rc, out = self.run(["systemctl", "--user", "show", "rm-relentless.service", "-p", "ActiveState", "-p", "Result",
                            "-p", "TimeoutStartUSec", "-p", "ExecMainStartTimestampMonotonic",
                            "-p", "InactiveEnterTimestampMonotonic", "-p", "InactiveExitTimestampMonotonic"])
        if rc != 0:
            raise Unmeasured("systemctl show exited %d" % rc)
        d = dict(l.split("=", 1) for l in out.splitlines() if "=" in l)
        with open("/proc/uptime") as f:
            d["mono"] = float(f.read().split()[0])
        return d

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

    def read_tail(self, path, n):
        with open(path, "rb") as f:
            size = f.seek(0, 2)
            f.seek(max(0, size - n))
            return f.read().decode("utf-8", "replace"), size > n

    def mtime(self, path):
        return os.stat(path).st_mtime

    def listdir(self, path):
        return os.listdir(path)

    def item_states(self):
        """Every Relentless item's state.json, read this tick (a 588-file read costs about 20 ms)."""
        out, unread = [], 0
        root = RELENTLESS_STORE + "/items"
        for name in os.listdir(root):       # not glob: glob hides a directory it cannot read
            try:
                with open("%s/%s/state.json" % (root, name)) as f:
                    out.append(json.load(f))
            except FileNotFoundError:
                if os.path.isdir("%s/%s" % (root, name)):
                    unread += 1     # the item is still there and its state is not
            except (OSError, ValueError):
                unread += 1
        if unread:          # a count short by an unread file would read as true: say so instead
            raise Unmeasured("%d item state files unreadable" % unread)
        if not out:
            raise Unmeasured("no item state files readable in the Relentless store")
        return out

    def ledger_titles(self, wanted):
        """Item -> title from the ledger's file events. Only called for names not cached yet."""
        got = {}
        for p in glob.glob(LEDGER_EVENTS + "/*.jsonl"):
            with open(p, errors="replace") as f:
                for line in f:
                    if '"file"' not in line or '"title"' not in line:
                        continue
                    try:
                        d = json.loads(line)
                    except ValueError:
                        continue
                    if d.get("event") == "file" and d.get("id") in wanted and isinstance(d.get("title"), str):
                        got[d["id"]] = d["title"]
        return got

    def steve_probe(self):
        r = subprocess.run(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=6", STEVE_SSH, "bash -s"], input=STEVE_SCRIPT,
                           capture_output=True, text=True, timeout=20)
        if r.returncode != 0:
            raise Unmeasured("ssh exited %d: %s" % (r.returncode, r.stderr.strip()[:80]))
        return r.stdout

    def tailscale_status(self):
        rc, out = self.run(["tailscale", "status", "--json"], timeout=5)
        if rc != 0:
            raise Unmeasured("tailscale status exited %d" % rc)
        return json.loads(out)

    def port_open(self, host, port=22):
        with socket.create_connection((host, port), timeout=1.5):
            return True

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


def iso_epoch(t):
    return calendar.timegm(time.strptime(t, "%Y-%m-%dT%H:%M:%SZ"))


def tokens(n):
    if not n:
        return "0"
    return "%.1fM" % (n / 1e6) if n >= 1e6 else "%dk" % round(n / 1e3)


def clip(s, n):
    s = re.sub(r"\s+", " ", str(s)).strip()
    return s if len(s) <= n else s[:max(n - 1, 1)].rstrip() + "…"


def humanise(item):
    return re.sub(r"_+", " ", item).strip().capitalize()


def tidy_title(t):
    """A ledger title without its leading [MAJOR] style tag."""
    return re.sub(r"^(\[[^\]]*\]\s*)+", "", t).strip()


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
    """Processes the NOT RECOGNISED rule applies to: claude, python, node, codex."""
    c = r["comm"].lower()
    return is_agent_proc(r) or c.startswith(("python", "node", "codex")) or r["args"].split(" ", 1)[0].endswith(("python3", "python"))


def proc_kind(r, by_pid):
    """One word for what a process is. A claude spawned by a claude is its bundled search tool, not a second agent."""
    a, c = r["args"], r["comm"].lower()
    if is_agent_proc(r):
        par = by_pid.get(r["ppid"])
        return "tool" if par and is_agent_proc(par) else "claude"
    if "codex" in c or "codex" in a.split(" ", 1)[0].lower() or "codex.exe" in a[:120].lower():
        return "codex"
    if c.startswith("python") or a.split(" ", 1)[0].rsplit("/", 1)[-1].startswith("python") or ".exe" in a[:80] and "python" in a[:80].lower():
        if re.search(r"selftest|run_selftests", a):
            return "test"
        if re.search(r"prove_|proof_|validation|northstar", a):
            return "proof"
        return "py"
    if c in ("bash", "sh", "zsh", "dash", "timeout", "head", "tail", "tee", "sleep", "sed", "awk", "grep", "cat", "find", "xargs"):
        return "sh"
    if c.startswith("git") or c in ("rsync", "ssh", "cp"):
        return "git"
    return "other"


KIND_ORDER = ("claude", "codex", "proof", "test", "py", "sh", "git", "tool", "other")


def kinds_text(procs, by_pid):
    c = collections.Counter(proc_kind(r, by_pid) for r in procs)
    return " ".join("%s %d" % (k, c[k]) for k in KIND_ORDER if c[k])


def own_pids(rows, self_pid):
    """This page's own ps child is not part of the machine it reports on."""
    return {r["pid"] for r in rows if r["ppid"] == self_pid and r["comm"] == "ps"}


def build_tree(env, table, rows):
    """Give every process exactly one owner, by its own cgroup or else its nearest ancestor's. A selftest scope is not
    an owner while a live parent can be found (a worker's selftest belongs to the worker)."""
    by_pid = {r["pid"]: r for r in rows}
    memo = {}

    def own_hit(pid):
        hit = table.cgroup_unit(env.cgroup(pid))
        return hit

    def owner(pid, seen=()):
        if pid in memo:
            return memo[pid]
        r = by_pid[pid]
        hit = own_hit(pid)
        res = None
        if hit and hit[3].group(0) and hit[2] != "selftest":
            res = hit
        else:
            parent = r["ppid"]
            if parent in by_pid and parent > 1 and parent not in seen:
                res = owner(parent, seen + (pid,))
            if res is None and hit:
                res = hit
        memo[pid] = res
        return res

    groups = {}     # key -> {"family","label","unit","kind","id","who","procs":[]}
    machine, unknown = [], []
    for r in rows:
        hit = owner(r["pid"])
        if hit is None:
            pr = table.proc(r["args"])
            if pr:
                key = (pr[0], pr[1])
                groups.setdefault(key, {"family": pr[0], "label": pr[1], "unit": pr[1], "kind": "", "id": "", "who": "", "procs": []})["procs"].append(r)
            elif is_watched(r):
                unknown.append(r)
            else:
                machine.append(r)
            continue
        comp, fam, lab, m = hit
        gd = m.groupdict()
        # a role or worker is both a service and a claude-seat-...scope: the id folds them into one
        key = (fam, gd.get("id") or comp if fam != "other" else comp)
        g = groups.setdefault(key, {"family": fam, "label": lab, "unit": comp, "kind": gd.get("kind", ""), "id": gd.get("id", ""),
                                    "who": gd.get("who", ""), "procs": []})
        g["procs"].append(r)
    for g in groups.values():
        agents = [r for r in g["procs"] if proc_kind(r, by_pid) == "claude"]
        g["age"] = max(r["age"] for r in g["procs"])
        main = min(agents, key=lambda r: r["pid"]) if agents else None
        g["model"] = g["name"] = g["cwd"] = ""
        if main:
            mm = re.search(r"--model\s+(\S+)", main["args"])
            g["model"] = mm.group(1) if mm else ""
            nm = re.search(r"--name\s+(\S+)", main["args"])
            g["name"] = nm.group(1) if nm else ""
            g["cwd"] = env.cwd(main["pid"])
    return {"groups": groups, "machine": machine, "unknown": unknown, "by_pid": by_pid, "total": len(rows)}


def is_conductor(g):
    return g["family"] == "seats" and (g["name"].upper() == "CONDUCTOR")


def is_other_project(g):
    return g["family"] == "other" or (g["family"] == "seats" and g["cwd"] and not g["cwd"].startswith("/home/mandrake/rm/"))


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
    return {"tick": iso_epoch(t)}


def collect_bridge(env):
    last = None
    for p in BRIDGE_FILES:
        try:
            txt = env.read_text(p)
        except OSError:
            continue
        body = "\n".join(l for l in txt.splitlines() if not l.startswith("#"))
        m = re.search(r"^(HELD|FREE)\b[ \t]*(?!since\b)(\S*)[ \t]*(?:since\s+(\S+))?", body, re.M)
        why = re.search(r"^for\s+(.*)$", body, re.M)
        if m:
            mt = env.mtime(p)
            if last is None or mt > last["mt"]:
                last = {"state": m.group(1), "who": m.group(2), "since": m.group(3), "for": why.group(1) if why else "", "mt": mt}
    if not last:
        raise Unmeasured("no BRIDGE mirror file readable")
    return last


def short(item):
    """relentless.py names an item's units rm-relentless-<kind>-<short(item)>-g<gen>: same hash, so a unit finds its item."""
    return hashlib.sha1(item.encode()).hexdigest()[:10]


def collect_items(env):
    states = env.item_states()
    counts = collections.Counter(s.get("status") for s in states)
    by_status = collections.defaultdict(list)
    for s in states:
        by_status[s.get("status")].append(s)
    return {"counts": counts, "by_status": by_status, "by_short": {short(s["item"]): s for s in states if s.get("item")},
            "live": sum(counts[k] for k in RUNS_A_PLACE)}


def collect_staffing(env):
    s = env.read_json(RELENTLESS_STORE + "/staffing.json")
    if not isinstance(s.get("t"), (int, float)):
        raise Unmeasured("staffing.json has no timestamp")
    return s


def collect_tick(env, state):
    d = env.tick_show()
    limit = re.match(r"(\d+)min", d.get("TimeoutStartUSec", ""))
    out = {"limit_s": int(limit.group(1)) * 60 if limit else None, "result": d.get("Result", "")}
    running = d.get("ActiveState") == "activating"
    out["running"] = running
    if running:
        out["for_s"] = d["mono"] - int(d["ExecMainStartTimestampMonotonic"]) / 1e6
    else:
        start, end = int(d["InactiveExitTimestampMonotonic"]), int(d["InactiveEnterTimestampMonotonic"])
        out["ended_s"] = d["mono"] - end / 1e6
        if end > start:
            state["tick_last_s"] = (end - start) / 1e6
    out["last_s"] = state.get("tick_last_s")
    return out


def collect_throughput(env, now):
    """Last 24 h, from Relentless's own records: the blind-check verdict file and the tick journal's acts."""
    cut = now - 86400
    t = collections.Counter()
    closed_by_hour = [0] * 24
    recent_done = []
    seen = set()
    text = env.read_text(RELENTLESS_STORE + "/shadow.jsonl")
    lines = text.splitlines()
    for i, line in enumerate(lines):
        try:
            d = json.loads(line)
            if not isinstance(d, dict):
                raise ValueError("not a record")
        except ValueError:
            # only a last line still being written may be broken; dropping any other makes a count look true
            if i == len(lines) - 1 and not text.endswith("\n"):
                continue
            raise Unmeasured("shadow.jsonl line %d is broken" % (i + 1))
        # one row per shadow rule, so a verdict can have several: its nonce makes it one verdict
        if isinstance(d.get("at"), (int, float)) and d["at"] >= cut and d.get("nonce") not in seen:
            seen.add(d.get("nonce"))
            t[d.get("word")] += 1
    text, cut_off = env.read_tail(RELENTLESS_STORE + "/journal.jsonl", JOURNAL_TAIL)
    lines = text.splitlines()
    first = None
    for i, line in enumerate(lines):
        try:
            d = json.loads(line)
            if not isinstance(d, dict):
                raise ValueError("not a record")
            if "acts" not in d:
                continue
            at = iso_epoch(d["at"])
        except (ValueError, KeyError, TypeError):
            # the tail read can start mid-line and the last line can be mid-write; any other is damage
            if (i == 0 and cut_off) or (i == len(lines) - 1 and not text.endswith("\n")):
                continue
            raise Unmeasured("journal.jsonl tail line %d is broken" % (i + 1))
        first = at if first is None else min(first, at)
        if at < cut:
            continue
        for x in d.get("acts") or []:
            w = x.get("do")
            t[w] += 1
            if w == "done":
                closed_by_hour[min(23, int((at - cut) // 3600))] += 1
                recent_done.append((at, x.get("item") or ""))
    recent_done.sort(reverse=True)
    return {"pass": t["PASS"], "weak": t["WEAK"], "fail": t["FAIL"] + t["game_fail"],
            "unmeasured": t["game_unmeasured"] + t["game_proof_unmeasured"], "refused": t["game_refused"] + t["start_refused"] + t["close_refused"],
            "closed": t["done"], "blind_fail": t["FAIL"], "put_back": t["returned"], "by_hour": closed_by_hour, "recent": recent_done[:3],
            "short": bool(cut_off and first is not None and first > cut)}


def titles_for(env, state, items):
    """Plain words for item names, cached forever: a ledger scan only runs for names not seen before."""
    cache = state.setdefault("titles", {})
    miss = {i for i in items if i and i not in cache}
    if miss:
        got, why = guarded(env.ledger_titles, miss)
        if why:
            return lambda i: tidy_title(cache.get(i) or "") or humanise(i)
        for i in miss:
            cache[i] = got.get(i) or ""
    return lambda i: tidy_title(cache.get(i) or "") or humanise(i)


def parse_probe(text):
    out = {}
    for line in text.splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def probe_steve(env):
    """Called after the page is on disk. Refreshes the cache file; a failed ssh keeps the last good numbers with their age."""
    now = env.now()
    try:
        cache = env.read_json(STEVE_CACHE)
    except Exception:       # noqa: BLE001 - first run or torn cache
        cache = {}
    if now - cache.get("t", 0) < PROBE_EVERY:
        return cache
    cache["t"] = now
    routes = {}
    ts, why = guarded(env.tailscale_status)
    if ts is not None:
        peers = [p for p in (ts.get("Peer") or {}).values() if str(p.get("HostName", "")).lower() == STEVE_TS_PEER]
        routes["tailscale"] = bool(peers and peers[0].get("Online"))
    lan, why = guarded(env.port_open, STEVE_LAN)
    routes["lan"] = bool(lan)
    raw, why = guarded(env.steve_probe)
    routes["wsl"] = raw is not None
    cache["routes"] = routes
    if raw is None:
        cache["why"] = why
    else:
        cache.pop("why", None)
        d = parse_probe(raw)
        d["cpu_pct"] = None
        st = [int(x) for x in d.get("stat", "").split()[1:] if x.isdigit()]
        prev = cache.get("stat")
        if st and prev and sum(st) > sum(prev):
            d["cpu_pct"] = round(100 * (1 - (st[3] - prev[3]) / (sum(st) - sum(prev))))
        cache["stat"] = st
        cache["good"] = d
        cache["good_t"] = now
    env.write_atomic(STEVE_CACHE, json.dumps(cache))
    return cache


def collect_steve(env, state):
    now = env.now()
    sj = env.read_json(TESTQ + "/steward.json")
    if not isinstance(sj.get("epoch"), (int, float)):
        raise Unmeasured("steward.json has no epoch")
    out = {"state": sj.get("state"), "fault": sj.get("fault"), "reason": sj.get("reason") or "", "age": now - sj["epoch"],
           "incident": sj.get("incident") or None}
    if sj.get("since"):
        out["since"] = iso_epoch(sj["since"])
    for d in ("running", "pending"):
        v, why = guarded(lambda p: len(env.listdir(p)), TESTQ + "/" + d)
        out[d] = v
    out["jobs_known"] = False
    names, why = guarded(env.listdir, TESTQ + "/done")
    if names is not None:
        # the name dates the job's birth, not its finish: a week back catches one that sat queued (results are memoised)
        days = {time.strftime("J%Y%m%d", time.gmtime(now - k * 86400)) for k in range(8)}
        keep = {n for n in names if n[:9] in days and n.endswith(".json")}
        memo = state.setdefault("steve_jobs", {})
        for n in list(memo):
            if n not in keep:
                del memo[n]
        unread = 0
        for n in keep - set(memo):
            try:
                j = env.read_json(TESTQ + "/done/" + n)
            except Exception:       # noqa: BLE001 - being written or bad: the day's counts are unknown, not short
                unread += 1
                continue
            r = j.get("result") or {}
            fin = r.get("finished") or j.get("finished")
            memo[n] = {"f": iso_epoch(fin) if fin else 0, "o": r.get("outcome") or "?", "c": r.get("cause") or "",
                       "r": len(r.get("rows") or []), "p": (j.get("job") or {}).get("purpose") or ""}
        day = [v for v in memo.values() if now - v["f"] <= 86400]
        out["jobs_known"] = not unread
        out["done"] = sum(1 for v in day if v["o"] == "DONE")
        out["failed"] = sum(1 for v in day if v["o"] != "DONE")
        out["rows_h"] = sum(v["r"] for v in day) / 24.0
        last = max(memo.values(), key=lambda v: v["f"]) if memo else None
        out["last"] = last
    return out


# --------------------------------------------------------------------------- SVG primitives
class Svg:
    def __init__(self, w, h, label):
        self.w, self.h, self.label, self.parts = w, h, label, []

    def rect(self, x, y, w, h, fill=CARD, stroke=None, rx=6, sw=1):
        s = ' stroke="%s" stroke-width="%s"' % (stroke, sw) if stroke else ""
        self.parts.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%s" fill="%s"%s/>' % (x, y, w, h, rx, fill, s))

    def text(self, x, y, s, size=12, fill=TEXT, weight=None, anchor=None, font=SANS):
        a = ' text-anchor="%s"' % anchor if anchor else ""
        b = ' font-weight="%s"' % weight if weight else ""
        self.parts.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="%s" fill="%s"%s%s>%s</text>' % (x, y, font, size, fill, a, b, escape(str(s))))

    def line(self, x1, y1, x2, y2, stroke=EDGE, sw=2, dash=None):
        d = ' stroke-dasharray="%s"' % dash if dash else ""
        self.parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="%s"%s/>' % (x1, y1, x2, y2, stroke, sw, d))

    def poly(self, pts, fill=EDGE):
        self.parts.append('<polygon points="%s" fill="%s"/>' % (" ".join("%.1f,%.1f" % p for p in pts), fill))

    def arrow_r(self, x1, x2, y, stroke=EDGE):
        self.line(x1, y, x2 - 6, y, stroke)
        self.poly([(x2, y), (x2 - 8, y - 5), (x2 - 8, y + 5)], stroke)

    def arrow_d(self, x, y1, y2, stroke=EDGE):
        self.line(x, y1, x, y2 - 6, stroke)
        self.poly([(x, y2), (x - 5, y2 - 8), (x + 5, y2 - 8)], stroke)

    def out(self):
        # one line and no blank line: Typora keeps an HTML block together only up to a blank line
        return ('<div><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="100%%" role="img" aria-label="%s" style="max-width:%dpx">'
                '<rect width="%d" height="%d" rx="10" fill="%s"/>%s</svg></div>'
                % (self.w, self.h, escape(self.label, {'"': "&quot;"}), self.w, self.w, self.h, BG, "".join(self.parts)))


# --------------------------------------------------------------------------- the Relentless panel
def item_line(st, now, title, n):
    since = st.get("started_at")
    chk = st.get("check") if isinstance(st.get("check"), dict) else {}
    if st.get("status") == "checking" and isinstance(chk.get("at"), (int, float)):
        since = chk["at"]
    head = ago(now - since).replace(" ", "") + " " if isinstance(since, (int, float)) else ""
    return head + clip(title(st.get("item") or ""), n - len(head))


def pipeline_svg(p):
    """The instrument panel. Numbers are the primary layer; items secondary; arrows context."""
    now, it, thr, title = p["now"], p["items"], p["throughput"], p["title"]
    W, H = 1040, 512
    s = Svg(W, H, "Relentless pipeline: stage counts, places, tick, breaker, last 24 hours")
    # ---- header gauges
    s.text(18, 34, "RELENTLESS", 22, TEXT, "700")
    places, live = p["places"], it["live"] if it else None
    x = 172
    s.text(x, 20, "PLACES", 10, DIM, "600")
    if places and live is not None:
        for i in range(max(places, live)):
            s.rect(x + i * 17, 26, 14, 12, LIVE if i < live else "none", LIVE if i < live else FAINT, 2)
        x2 = x + max(places, live) * 17 + 4
        s.text(x2, 37, "%d / %d" % (live, places), 15, TEXT, "700", font=MONO)
    else:
        x2 = x
        s.text(x, 37, "UNMEASURED", 13, WARN, "700")
    tick, gx = p["tick"], 390

    def gauge(xx, label, value, colour=TEXT):
        s.text(xx, 20, label, 10, DIM, "600")
        s.text(xx, 37, value, 13, colour, "700", font=MONO)

    if tick:
        if tick["running"]:
            over = tick["limit_s"] and tick["for_s"] > tick["limit_s"] * 0.8
            val = "running %s" % ago(tick["for_s"]) + (" of %s" % ago(tick["limit_s"]) if tick["limit_s"] else "")
            gauge(gx, "TICK", val, WARN if over else TEXT)
        else:
            gauge(gx, "TICK", "%s ago, took %s" % (ago(tick["ended_s"]), ago(tick["last_s"]) if tick["last_s"] else "UNMEASURED"), BAD if tick["result"] not in ("success", "") else TEXT)
    else:
        gauge(gx, "TICK", "UNMEASURED", WARN)
    br = breaker_word(p)
    gauge(600, "BREAKER", br, WARN if br == "UNMEASURED" else (GOOD if br == "clear" else BAD))
    gauge(700, "LIVE GAME", p["game_text"], p["game_colour"])
    gauge(900, "TOKENS TODAY", p["spent"] or "UNMEASURED", TEXT if p["spent"] else WARN)
    # ---- the belt
    cw, gap, x0, y0, ch = 152, 20, 16, 86, 150
    cx = {}
    for i, name in enumerate(BELT):
        x = x0 + i * (cw + gap)
        cx[name] = x
        n = it["counts"][name] if it else None
        hot = name in ("running", "checking") and n
        s.rect(x, y0, cw, ch, CARD, LIVE if hot else (GOOD if name == "done" else EDGE), 7, 2 if hot else 1)
        s.text(x + 10, y0 + 19, name.upper(), 11, DIM, "700")
        s.text(x + 10, y0 + 54, "UNMEASURED" if n is None else n, 13 if n is None else 34, WARN if n is None else (TEXT if n else FAINT), "700", font=MONO)
        word = BELT_WORD[name]
        if name == "done" and thr and thr["recent"]:
            word = "closed, last %s ago" % ago(now - thr["recent"][0][0])
        s.text(x + 10, y0 + 70, word, 10.5, DIM)
        lines = []
        if it and name in ("running", "checking", "candidate", "closing"):
            rows = sorted(it["by_status"][name], key=lambda v: v.get("started_at") or 0)
            lines = [item_line(r, now, title, 25) for r in rows[:4]]
            if len(rows) > 4:
                lines[-1] = "+ %d more" % (len(rows) - 3)
        elif name == "done" and thr:
            lines = [clip(title(i), 25) for _, i in thr["recent"]]
        elif name == "queued" and it:
            exp = sum(1 for v in it["by_status"]["queued"] if v.get("expedite"))
            ret = sum(1 for v in it["by_status"]["queued"] if v.get("returns"))
            lines = ["%d failed a check before" % ret] + (["%d expedited" % exp] if exp else [])
            if thr:
                lines.append("%d stopped, put back 24 h" % thr["put_back"])
        for j, ln in enumerate(lines):
            s.text(x + 10, y0 + 88 + j * 15, ln, 10.5, TEXT if name != "queued" else DIM, font=MONO)
        if i < len(BELT) - 1:
            s.arrow_r(x + cw + 1, x + cw + gap - 1, y0 + 40, BAR)
    # FAIL loop: checking back to queued, along the top of the belt
    ly = 66
    qx, kx = cx["queued"] + cw / 2, cx["checking"] + cw / 2
    s.line(kx, y0, kx, ly, BAD, 1.5)
    s.line(kx, ly, qx, ly, BAD, 1.5)
    s.arrow_d(qx, ly, y0, BAD)
    label = "blind check FAIL goes back to the queue: %s in 24 h" % (thr["blind_fail"] if thr else "UNMEASURED")
    s.rect(qx + 96, ly - 9, len(label) * 5.9 + 16, 18, BG, None, 0)
    s.text(qx + 104, ly + 4, label, 11, BAD, "600")
    # ---- side branches off RUNNING
    ry, sy, sh = y0 + ch + 18, y0 + ch + 34, 58
    runx = cx["running"] + cw / 2
    s.line(runx, y0 + ch, runx, ry, FAINT, 1.5, "4 3")
    s.line(cx["queued"] + cw / 2, ry, cx["closing"] + cw + 20 + cw / 2, ry, FAINT, 1.5, "4 3")
    s.rect(runx + 8, ry - 8, 118, 16, BG, None, 0)
    s.text(runx + 14, ry + 4, "set aside from the belt", 10, DIM)
    for i, name in enumerate(SIDE):
        x = x0 + i * (cw + gap)
        n = it["counts"][name] if it else None
        s.arrow_d(x + cw / 2, ry, sy, FAINT)
        s.rect(x, sy, cw, sh, CARD, EDGE, 6)
        s.text(x + 10, sy + 16, name.upper(), 10.5, DIM, "700")
        s.text(x + cw - 10, sy + 26, "UNMEASURED" if n is None else n, 11 if n is None else 24, WARN if n is None else (TEXT if n else FAINT), "700", "end", MONO)
        s.text(x + 10, sy + 46, SIDE_WORD[name], 10, DIM)
    # ---- throughput: common zero baseline, direct labels
    ty = sy + sh + 18
    s.line(16, ty - 8, W - 16, ty - 8, EDGE, 1)
    s.text(18, ty + 8, "LAST 24 H, EVENTS", 10.5, DIM, "700")
    if thr:
        rows = [("CLOSED", thr["closed"], GOOD), ("PASS", thr["pass"], GOOD), ("WEAK", thr["weak"], WARN), ("FAIL", thr["fail"], BAD),
                ("UNMEASURED", thr["unmeasured"], WARN), ("REFUSED", thr["refused"], BAR)]
        top = max(max(r[1] for r in rows), 1)
        for j, (lab, n, col) in enumerate(rows):
            yy = ty + 18 + j * 19
            s.text(100, yy + 11, lab, 11, DIM, anchor="end", weight="600")
            s.rect(108, yy + 1, 12 + 340, 13, CARD, None, 2)
            s.rect(108, yy + 1, max(340 * n / top, 2 if n else 0), 13, col, None, 2)
            s.text(460, yy + 12, n, 12, TEXT, "700", font=MONO)
        # closures per hour, zero-based columns
        bx, bw, by, bh = 540, 480, ty + 22, 92
        top_h = max(max(thr["by_hour"]), 1)
        s.text(bx, ty + 8, "CLOSED PER HOUR", 10.5, DIM, "700")
        s.text(bx + bw, ty + 8, "tallest hour %d" % top_h, 10.5, DIM, anchor="end")
        for j, n in enumerate(thr["by_hour"]):
            hh = bh * n / top_h
            s.rect(bx + j * 20, by + bh - hh, 16, max(hh, 1), GOOD if n else EDGE, None, 1)
        s.line(bx, by + bh + 1, bx + bw, by + bh + 1, EDGE, 1)
        s.text(bx, by + bh + 14, "24 h ago", 10, DIM)
        s.text(bx + bw, by + bh + 14, "now", 10, DIM, anchor="end")
        if thr["short"]:
            s.text(bx + bw / 2, by + bh + 14, "journal tail covers less than 24 h", 10, WARN, anchor="middle")
    else:
        s.text(120, ty + 40, "UNMEASURED: %s" % clip(p["throughput_why"], 100), 13, WARN, "700")
    return s.out()


def pipeline_text(p):
    """The same panel as a monospace rail: the fallback twin, and what a raw text reader sees."""
    it, thr = p["items"], p["throughput"]
    if not it:
        return "RELENTLESS  stages UNMEASURED"
    c = it["counts"]
    top = max([c[k] for k in BELT + SIDE] + [1])

    def rail(name):
        n = c[name]
        return "%-10s %4d %s" % (name.upper(), n, "█" * (round(24 * n / top) or (1 if n else 0)))

    side = {"running": "──▶ game %d, held %d, blocked %d" % (c["game"], c["held"], c["blocked"]),
            "closing": "    stopping %d, retiring %d ──▶ retired %d" % (c["stopping"], c["retiring"], c["retired"])}
    out = ["RELENTLESS  places %d/%s  breaker %s" % (it["live"], p["places"] if p["places"] else "UNMEASURED",
                                                     breaker_word(p))]
    for i, name in enumerate(BELT):
        ln = rail(name)
        if name in side:
            ln = "%-44s%s" % (ln, side[name])
        out.append(ln)
        if i < len(BELT) - 1:
            out.append("  │" + ("  FAIL returns to queued: %s in 24 h" % thr["blind_fail"] if name == "checking" and thr else ""))
    if thr:
        out.append("24 h: closed %d, PASS %d, WEAK %d, FAIL %d, UNMEASURED %d, REFUSED %d" % (thr["closed"], thr["pass"], thr["weak"], thr["fail"], thr["unmeasured"], thr["refused"]))
    return "\n".join(out)


# --------------------------------------------------------------------------- the process tree
def breaker_word(p):
    """Open only while `until` is ahead (relentless.py admission): its file keeps old `opens` counts long after it closes."""
    br = p["breaker"]
    if br is None:
        return "UNMEASURED"
    return "OPEN" if br.get("until", 0) > p["now"] else "clear"


def ghost_places(p):
    """Items whose status says a process is at work while no unit of theirs has one. None when either side is unread."""
    it, tree = p["items"], p["tree"]
    if not it or not tree:
        return None
    alive = {x["id"].split("-")[0] for x in tree["groups"].values() if x["label"] == "worker"}
    return [s["item"] for k in ("running", "checking") for s in it["by_status"][k] if short(s["item"]) not in alive]


def tree_lines(p):
    tree, now, it, title = p["tree"], p["now"], p["items"], p["title"]
    if tree is None:
        return ["PROCESS TREE: UNMEASURED (%s)" % p["ps_why"]], None
    by_pid = tree["by_pid"]
    g = list(tree["groups"].values())
    fam = lambda f: [x for x in g if x["family"] == f]  # noqa: E731
    W = FENCE_WIDTH
    L = []

    def n_procs(gs):
        return sum(len(x["procs"]) for x in gs)

    def head(text, count):
        tail = "[%d proc]" % count
        L.append("%s %s %s" % (text, "·" * max(1, W - len(text) - len(tail) - 2), tail))

    def leaf(prefix, name, right, procs):
        # name stretches: the counts column stays whole, the name takes the clip
        counts = kinds_text(procs, by_pid) + " = %d" % len(procs)
        room = W - len(prefix) - len(counts) - len(right) - 3
        L.append("%s%-*s %s  %s" % (prefix, max(room, 12), clip(name, max(room, 12)), right, counts))

    # ---- Dispatch and what hangs off it
    disp = [x for x in fam("dispatcher")]
    roles = sorted(fam("roles"), key=lambda x: -x["age"])
    rel_all = fam("relentless")
    workers = sorted([x for x in rel_all if x["label"] == "worker"], key=lambda x: (x["kind"] != "work", -x["age"]))
    sup = [x for x in rel_all if x["label"] != "worker"]
    cond = [x for x in fam("seats") if is_conductor(x)]
    helpers = sorted(fam("helpers"), key=lambda x: -x["age"])
    under = n_procs(disp) + n_procs(roles) + n_procs(rel_all) + n_procs(cond) + n_procs(helpers)
    dt = p["dispatcher"]
    head("DISPATCH  " + ("last tick %s ago" % ago(now - dt["tick"]) if dt else "last tick UNMEASURED"), under)
    L.append("│  ── it starts or restarts this    ┄┄ own timer, same chain")
    L.append("├─ tick right now: " + (kinds_text(sum((x["procs"] for x in disp), []), by_pid) or "not mid-run") + "  [%d proc]" % n_procs(disp))
    n_work = sum(1 for x in workers if x["kind"] == "work")
    n_chk = sum(1 for x in workers if x["kind"] == "check")
    n_other = len(workers) - n_work - n_chk      # the game stage and help runs are neither
    L.append("├┄ RELENTLESS  workers %d, checkers %d%s, places %s of %s  [%d proc]" % (n_work, n_chk, ", other %d" % n_other if n_other else "", it["live"] if it else "UNMEASURED", p["places"] or "UNMEASURED", n_procs(rel_all)))
    L.append("│  ├─ supervisor tick: " + (kinds_text(sum((x["procs"] for x in sup), []), by_pid) or "not mid-run") + "  [%d proc]" % n_procs(sup))
    for i, w in enumerate(workers):
        branch = "└─" if i == len(workers) - 1 else "├─"
        st = it["by_short"].get(w["id"].split("-")[0]) if it else None
        name = title(st["item"]) if st else "item UNMEASURED"
        right = "%6s %-4s %5s" % (ago(w["age"]), w["model"][:4], tokens(st.get("spent")) if st else "UNMEASURED")
        leaf("│  %s %-5s " % (branch, w["kind"] or "?"), name, right, w["procs"])
    if not workers:
        L.append("│  └─ no worker or checker process running")
    ghosts = ghost_places(p)
    if ghosts:
        L.append("│  ! %d items hold a place with no process: %s" % (len(ghosts), clip(title(ghosts[0]), W - 45)))
    L.append("├─ ROLE RUNS  %d running  [%d proc]" % (len(roles), n_procs(roles)))
    for i, x in enumerate(roles):
        name = x["id"].rsplit("-", 1)[0].capitalize() if x["id"] else x["unit"]
        leaf("│  %s " % ("└─" if i == len(roles) - 1 else "├─"), name, "%6s %-4s" % (ago(x["age"]), x["model"][:4]), x["procs"])
    L.append("└─ CONDUCTOR WINDOW  %s, %d helpers  [%d proc]" % (ago(cond[0]["age"]) if cond else "not running", len(helpers), n_procs(cond) + n_procs(helpers)))
    if cond:
        leaf("   ├─ " if helpers else "   └─ ", "the window", "", sum((x["procs"] for x in cond), []))
    for i, x in enumerate(helpers):
        name = re.sub(r"-\d{9,}$", "", x["id"]).replace("bench-", "").replace("-", " ")
        leaf("   %s helper " % ("└─" if i == len(helpers) - 1 else "├─"), name, "%6s %-4s" % (ago(x["age"]), x["model"][:4]), x["procs"])
    L.append("")

    # ---- every other root
    windows = [x for x in fam("seats") if not is_conductor(x) and not is_other_project(x)]
    other = [x for x in g if is_other_project(x) and not is_conductor(x)]    # Conductor counts under Dispatch, wherever it sits
    roots = under
    head("OTHER WINDOWS OF OURS  %d" % len(windows), n_procs(windows))
    roots += n_procs(windows)
    for x in sorted(windows, key=lambda y: -y["age"]):
        leaf("   ", x["name"] or x["who"] or x["unit"], "%6s" % ago(x["age"]), x["procs"])
    timer_fams = ("art", "monitors", "tests", "upkeep", "game")
    tf = [x for x in g if x["family"] in timer_fams]
    head("TIMERS AND SERVICES, NOT UNDER DISPATCH  %d mid-run" % len(tf), n_procs(tf))
    roots += n_procs(tf)
    for f in timer_fams:
        xs = fam(f)
        if xs:
            title_f = p["fam"]["families"].get(f, {}).get("title", f)
            names = sorted({re.sub(r"\.(service|scope)$", "", x["unit"]) for x in xs if x["label"] != "selftest"})
            n_self = sum(1 for x in xs if x["label"] == "selftest")
            desc = ", ".join(names) + (("; " if names else "") + "%d selftest scopes" % n_self if n_self else "")
            pre = "   %-20s %3d proc  " % (title_f, n_procs(xs))
            L.append(pre + clip(desc, W - len(pre)))
    head("OTHER PROJECTS  %d" % len(other), n_procs(other))
    roots += n_procs(other)
    for x in other:
        leaf("   ", x["name"] or x["label"], "%6s" % ago(x["age"]), x["procs"])
    head("OPERATING SYSTEM AND TERMINALS", len(tree["machine"]))
    roots += len(tree["machine"])
    unknown = tree["unknown"]
    head("NOT RECOGNISED  %d" % len(unknown), len(unknown))
    roots += len(unknown)
    for r in unknown:
        L.append("   pid %d  %s" % (r["pid"], clip(r["args"], W - 14)))
    win = p["win"]
    L.append("")
    if win:
        L.append("WINDOWS SIDE (separate count, %s old)  game %d, codex %d, python %d" % (ago(win.get("cached_age", 0)), win["game"], win["codex"], win["python_exe"]))
    else:
        L.append("WINDOWS SIDE  UNMEASURED (%s)" % clip(p["win_why"], 60))
    L.append("TOTAL %d Linux processes = %d under Dispatch + %d in the other roots" % (tree["total"], under, roots - under))
    return L, roots


# --------------------------------------------------------------------------- SteveDesktop
def steve_tone(st):
    if st in ("BRAKED", "UNREACHABLE", "QUARANTINE"):
        return BAD
    if st in ("READY", "STALLED", "PAUSED"):
        return WARN
    if st in ("RUNNING", "IDLE"):
        return GOOD
    return WARN


def steve_headline(sv):
    """-> (state word, idle-under-brake flag)."""
    state = sv.get("state") or "UNMEASURED"
    return state, bool(sv.get("running") == 0 and state in ("BRAKED", "QUARANTINE", "STALLED", "UNREACHABLE"))


def steve_svg(p):
    sv, cache, now = p["steve"], p["steve_cache"] or {}, p["now"]
    W, H = 1040, 212
    s = Svg(W, H, "SteveDesktop: state, machine stats and test jobs")
    if not sv:
        s.text(18, 40, "STEVEDESKTOP  UNMEASURED: %s" % clip(p["steve_why"], 90), 16, WARN, "700")
        return s.out()
    state, idle = steve_headline(sv)
    tone = steve_tone(state)
    s.rect(1, 1, W - 2, H - 2, "none", tone, 10, 3 if tone == BAD else 1)
    s.rect(14, 12, W - 28, 44, tone if tone == BAD else CARD, None, 6)
    fg = "#ffffff" if tone == BAD else tone
    s.text(26, 41, "STEVEDESKTOP", 18, fg, "700")
    s.text(190, 41, state + (" AND IDLE" if idle else ""), 20, fg, "800", font=MONO)
    since = "for %s" % ago(now - sv["since"]) if sv.get("since") else ""
    inc = sv.get("incident") or {}
    extra = ("  incident level %s" % inc.get("level")) if inc.get("level") is not None else ""
    s.text(W - 28, 40, "%s%s" % (since, extra), 12, fg, "600", "end", MONO)
    s.text(18, 73, clip(sv["reason"], 150) or "no reason recorded", 11.5, TEXT if tone != BAD else "#ffb4b0")

    good = cache.get("good") or {}
    good_age = now - cache["good_t"] if cache.get("good_t") else None

    def tile(x, y, w, label, val, colour=TEXT, bar=None):
        s.rect(x, y, w, 50, CARD, None, 5)
        s.text(x + 8, y + 14, label, 9.5, DIM, "700")
        missing = val == "?"
        s.text(x + 8, y + 36, "UNMEASURED" if missing else val, 11 if missing else 15, colour, "700", font=MONO)
        if bar is not None:
            s.rect(x + 8, y + 42, w - 16, 3, EDGE, None, 1)
            s.rect(x + 8, y + 42, (w - 16) * min(bar, 1), 3, WARN if bar >= 0.9 else LIVE, None, 1)

    # ---- machine row
    y = 84
    routes = cache.get("routes") or {}
    s.rect(14, y, 148, 50, CARD, None, 5)
    s.text(22, y + 14, "ROUTES", 9.5, DIM, "700")
    for i, (k, lab) in enumerate((("tailscale", "tail"), ("lan", "LAN"), ("wsl", "wsl"))):
        v = routes.get(k)
        s.parts.append('<circle cx="%d" cy="%d" r="5" fill="%s"/>' % (28 + i * 46, y + 31, FAINT if v is None else (GOOD if v else BAD)))
        s.text(36 + i * 46, y + 35, lab, 10.5, TEXT if v else DIM)
    cols = [(170, 92), (270, 88), (366, 148), (522, 88), (618, 128), (754, 180), (942, 84)]

    def num(k):
        return good.get(k) or ""

    up = num("up")
    up = up if re.fullmatch(r"\d+(\.\d+)?", up) else ""
    tile(cols[0][0], y, cols[0][1], "UPTIME", ago(float(up)).replace(" ", "") if up else "?", TEXT if up else WARN)
    load, cores = num("load"), num("cores")
    tile(cols[1][0], y, cols[1][1], "LOAD/%s" % (cores or "CORES?"), load or "?", TEXT if load else WARN)
    ram = num("ram").split()
    if len(ram) == 2 and all(x.isdigit() for x in ram):
        tile(cols[2][0], y, cols[2][1], "WSL RAM USED", "%.1f/%.0f GB" % (int(ram[0]) / 1024, int(ram[1]) / 1024), TEXT, int(ram[0]) / max(int(ram[1]), 1))
    else:
        tile(cols[2][0], y, cols[2][1], "WSL RAM USED", "?", WARN)
    cpu = good.get("cpu_pct")
    tile(cols[3][0], y, cols[3][1], "CPU", "%d%%" % cpu if cpu is not None else "?", TEXT if cpu is not None else WARN, cpu / 100 if cpu is not None else None)
    disk = num("disk").split()
    tile(cols[4][0], y, cols[4][1], "DISK FREE", "%s GB" % disk[0] if disk else "?", TEXT if disk else WARN)
    gpu = [x.strip() for x in num("gpu").split(",")]
    if len(gpu) == 4 and all(x.isdigit() for x in gpu[1:]):     # "[N/A]" on some cards
        tile(cols[5][0], y, cols[5][1], "GPU " + re.sub(r"NVIDIA |GeForce ", "", gpu[0]), "%s%%  %.1f/%.0f GB" % (gpu[1], int(gpu[2]) / 1024, int(gpu[3]) / 1024), TEXT, int(gpu[1]) / 100)
    else:
        tile(cols[5][0], y, cols[5][1], "GPU", "?", WARN)
    gm = num("game")
    tile(cols[6][0], y, cols[6][1], "GAME", ("up" if gm != "0" else "down") if gm else "?", (LIVE if gm != "0" else DIM) if gm else WARN)

    # ---- jobs row
    y = 142
    known = sv.get("jobs_known")
    n = lambda v: "?" if v is None else str(v)  # noqa: E731
    run_v, q_v = sv.get("running"), sv.get("pending")
    tile(14, y, 84, "RUNNING", n(run_v), BAD if idle else (LIVE if run_v else DIM))
    tile(106, y, 84, "QUEUED", n(q_v), WARN if q_v and not run_v else TEXT)
    tile(198, y, 92, "DONE 24 H", n(sv.get("done")) if known else "?", TEXT if known else WARN)
    fl = sv.get("failed")
    tile(298, y, 92, "FAILED 24 H", n(fl) if known else "?", (BAD if fl else DIM) if known else WARN)
    last = sv.get("last")
    if last:
        word = last["o"] + ("/" + last["c"] if last["c"] else "")
        tile(398, y, 268, "LAST JOB, %s AGO" % ago(now - last["f"]).upper(), clip("%s %s" % (last["p"], word), 30), GOOD if last["o"] == "DONE" else BAD)
    else:
        tile(398, y, 268, "LAST JOB", "none in 2 days" if known else "?", WARN)
    tile(674, y, 110, "ROWS/HOUR 24 H", "%.0f" % sv["rows_h"] if known else "?", TEXT if known else WARN)
    age = sv["age"]
    tile(792, y, 102, "STEWARD WROTE", ago(age) + " ago", BAD if age > 300 else TEXT)
    pa = "%s old" % ago(good_age) if good_age is not None else "never"
    tile(902, y, 124, "MACHINE READING", pa, WARN if cache.get("why") or good_age is None or good_age > 900 else DIM)
    return s.out()


def steve_text(p):
    sv, cache = p["steve"], p["steve_cache"] or {}
    if not sv:
        return "STEVEDESKTOP  UNMEASURED (%s)" % p["steve_why"]
    g = cache.get("good") or {}
    return "\n".join([
        "STEVEDESKTOP  %s  jobs running %s, queued %s, done 24 h %s, failed 24 h %s" % (sv.get("state"), sv.get("running"), sv.get("pending"), sv.get("done") if sv.get("jobs_known") else "UNMEASURED", sv.get("failed") if sv.get("jobs_known") else "UNMEASURED"),
        "routes %s" % " ".join("%s:%s" % (k, "up" if v else "DOWN") for k, v in (cache.get("routes") or {}).items()),
        "load %s  ram %s  disk %s  gpu %s  game %s" % tuple(g.get(k, "UNMEASURED") for k in ("load", "ram", "disk", "gpu", "game")),
    ])


# --------------------------------------------------------------------------- chains: fixed text, checked against code
def chains(p):
    """Each row is one true route, read from dispatcher.py, detached_helper.py, relentless.py, alarm_routes.json,
    incident.py and Utils/testq; only the counts are live."""
    tree = p["tree"]
    n_of = None
    if tree:
        vals = list(tree["groups"].values())
        n_of = {"role": sum(1 for x in vals if x["family"] == "roles"), "helper": sum(1 for x in vals if x["family"] == "helpers"),
                "work": sum(1 for x in vals if x["kind"] == "work"), "check": sum(1 for x in vals if x["kind"] == "check")}
    c = lambda k: ("%d now" % n_of[k]) if n_of else "UNMEASURED"  # noqa: E731
    return [
        ("WHO STARTS WHAT", [
            [("You", "the owner"), ("Conductor window", "a person's window"), ("Helpers", c("helper") + ", one task each")],
            [("rm-dispatcher.timer", "every 2 min, no AI"), ("Dispatcher", "caps, tickets, restarts seats"), ("Role runs", c("role") + ", read a role, stop")],
            [("rm-relentless.timer", "every 2 min, own timer"), ("Supervisor", "no AI"), ("Workers", c("work") + ", private clones"), ("Blind checkers", c("check") + ", never saw the work")],
            [("rm-artpiped", "art daemon"), ("codex_image.py", "one per render"), ("codex.exe", ("%d now on Windows" % p["win"]["codex"]) if p["win"] else "UNMEASURED")],
        ]),
        ("AN ALARM'S ROUTE", [
            [("Monitors, ops_watch", "ops_watch every 15 min"), ("Alarm or signal", "alarm files"), ("Dispatcher tick", "incident step"), ("Reader role", "named by its route"),
             ("Conductor", "next rung"), ("Fresh Operations", "next rung"), ("You", "last rung")],
        ]),
        ("AN ITEM'S LIFE", [
            [("Ledger item", "filed"), ("Queued", "enrolled"), ("Worker", "own clone"), ("Candidate", "a commit"), ("Blind check", "PASS or FAIL"), ("Closing", "landed"), ("Done", "deadman rechecks")],
        ]),
        ("STEVE LANE", [
            [("testq-tick.timer", "every 60 s"), ("pending/", "job file, fill plan"), ("SteveDesktop", "over ssh, running/"), ("done/", "result file"), ("Steward", "2 not DONE = brake"), ("ingest", "rimflow verify")],
        ]),
    ]


def chains_svg(p):
    groups = chains(p)
    bw_gap = 18
    rows = sum(len(r) for _, r in groups)
    H = 16 + len(groups) * 22 + rows * 52 + 8
    W = 1040
    s = Svg(W, H, "Chain diagrams: who starts what, an alarm's route, an item's life, the Steve lane")
    y = 8
    for name, rs in groups:
        s.text(16, y + 16, name, 11, DIM, "700")
        y += 24
        for r in rs:
            bw = min(230, (W - 32 - bw_gap * (len(r) - 1)) / len(r))
            for i, (a, b) in enumerate(r):
                x = 16 + i * (bw + bw_gap)
                s.rect(x, y, bw, 42, CARD, EDGE, 5)
                s.text(x + 8, y + 17, a, 11.5, TEXT, "700")
                s.text(x + 8, y + 33, clip(b, int(bw / 5.6)), 10, LIVE if " now" in b else DIM)
                if i < len(r) - 1:
                    s.arrow_r(x + bw + 1, x + bw + bw_gap - 1, y + 21, BAR)
            y += 50
    return s.out()


def chains_text(p):
    out = []
    for name, rs in chains(p):
        out.append(name)
        for r in rs:
            out.append("  " + " -> ".join(a for a, _ in r))
    return "\n".join(out)


# --------------------------------------------------------------------------- the top strip
def chip(text, sev):
    col = {2: "#c0392b", 1: "#a86e00", 0: "#256b4c", -1: "#3a4250"}[sev]
    return '<span style="background:%s;color:#fff;padding:2px 9px;border-radius:4px;font-weight:600;white-space:nowrap">%s</span>' % (col, escape(text))


def status_strip(p):
    now, chips = p["now"], []
    w = p["win"]
    chips.append(("game UNMEASURED", 1) if not w else (("game UP", 0) if w["game"] else ("game DOWN", -1)))
    b = p["bridge"]
    chips.append(("bridge UNMEASURED", 1) if not b else (("bridge FREE", 0) if b["state"] == "FREE" else ("bridge HELD by %s" % (b["who"] or "?"), -1)))
    it = p["items"]
    if not it or not p["places"]:
        chips.append(("Relentless UNMEASURED", 1))
    else:
        chips.append(("Relentless %d/%d" % (it["live"], p["places"]), 0 if it["live"] >= p["places"] else 1))
    if breaker_word(p) == "OPEN":
        chips.append(("Relentless breaker OPEN", 2))
    sv = p["steve"]
    if sv:
        state, idle = steve_headline(sv)
        tone = steve_tone(state)
        chips.append(("Steve %s%s" % (state, " + IDLE" if idle else ""), 2 if tone == BAD else (1 if tone == WARN else 0)))
    else:
        chips.append(("Steve UNMEASURED", 1))
    d = p["dispatcher"]
    if not d:
        chips.append(("Dispatcher UNMEASURED", 1))
    else:
        age = now - d["tick"]
        chips.append((("DISPATCHER NOT TICKING, last %s ago" % ago(age)) if age > 360 else "Dispatcher %s ago" % ago(age), 2 if age > 360 else 0))
    tree = p["tree"]
    if not tree:
        chips.append(("processes UNMEASURED", 1))
    elif tree["unknown"]:
        chips.append(("%d NOT RECOGNISED" % len(tree["unknown"]), 1))
    ghosts = ghost_places(p)
    if ghosts:
        chips.append(("%d place%s with no process" % (len(ghosts), "" if len(ghosts) == 1 else "s"), 1))
    if p["failed_units"]:
        chips.append(("%d failed jobs" % len(p["failed_units"]), 2))
    chips.sort(key=lambda c: -c[1])
    return " ".join(chip(t, sv_) for t, sv_ in chips), chips


# --------------------------------------------------------------------------- timers and history (last, collapsed)
def timers_rows(timers, units, now):
    desc = {u["unit"]: u.get("description", "") for u in units or []}
    rows = []
    for t in sorted(timers or [], key=lambda x: x.get("unit", "")):
        name = t.get("unit", "").replace(".timer", "")
        last, nxt = t.get("last") or 0, t.get("next") or 0
        last_s = ago(now - last / 1e6) + " ago" if last else "never"
        nxt_s = "in " + ago(nxt / 1e6 - now) if nxt else "running now"
        rows.append("%-24s %10s %12s  %s" % (clip(name, 24), last_s, nxt_s, clip(desc.get(t.get("unit"), ""), 34)))
    return rows


def read_history(env):
    try:
        text = env.read_text(HIST)
    except OSError:
        return []
    out = []
    for line in text.splitlines():
        try:
            r = json.loads(line)
            # v2 counts processes; v1 samples counted "things" and would not compare
            if isinstance(r, dict) and r.get("v") == 2 and isinstance(r.get("t"), (int, float)) and isinstance(r.get("n"), int):
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
    note = "" if span >= secs * 0.95 else " (covers only %s, not yet a full %s)" % (ago(span), label)
    return ("last %s: processes min %d / median %d / max %d%s" % (label, min(ns), int(statistics.median(ns)), max(ns), note)), rows


# --------------------------------------------------------------------------- the page
def gather(env, state):
    now = env.now()
    fam = env.families()
    table = Table(fam)
    p = {"now": now, "fam": fam, "unmeasured": []}

    ps_text, p["ps_why"] = guarded(env.ps)
    p["tree"] = None
    if ps_text is not None:
        rows = parse_ps(ps_text)
        mine = own_pids(rows, env.self_pid())
        rows = [r for r in rows if r["pid"] not in mine]
        p["tree"], p["ps_why"] = guarded(build_tree, env, table, rows)
    if p["ps_why"]:
        p["unmeasured"].append("processes (%s)" % p["ps_why"])

    p["units"], why_u = guarded(env.units_json)
    if why_u:
        p["unmeasured"].append("systemd units (%s)" % why_u)
    p["timers"], p["timers_why"] = guarded(env.timers_json)
    if p["timers_why"]:
        p["unmeasured"].append("systemd timers (%s)" % p["timers_why"])
    p["failed_units"] = [u["unit"] for u in (p["units"] or []) if u.get("active") == "failed"]
    p["win"], p["win_why"] = guarded(collect_tasklist, env, state)
    if p["win_why"]:
        p["unmeasured"].append("Windows processes (%s)" % p["win_why"])
    p["dispatcher"], why = guarded(collect_dispatcher, env)
    if why:
        p["unmeasured"].append("Dispatcher state (%s)" % why)
    p["bridge"], why = guarded(collect_bridge, env)
    if why:
        p["unmeasured"].append("bridge file (%s)" % why)
    p["items"], why = guarded(collect_items, env)
    if why:
        p["unmeasured"].append("Relentless items (%s)" % why)
    staffing, why = guarded(collect_staffing, env)
    if why:
        p["unmeasured"].append("Relentless staffing (%s)" % why)
    p["places"] = (staffing or {}).get("target")   # "places" in that file is what this tick allowed; target is the 8 he asks about
    p["checks"] = (staffing or {}).get("checks")
    sp = (staffing or {}).get("spent_today")
    p["spent"] = tokens(sp) if isinstance(sp, (int, float)) else None
    p["tick"], why = guarded(collect_tick, env, state)
    if why:
        p["unmeasured"].append("Relentless tick (%s)" % why)
    p["breaker"], why = guarded(env.read_json, RELENTLESS_STORE + "/breaker.json")
    if why:
        p["unmeasured"].append("breaker (%s)" % why)
    p["throughput"], p["throughput_why"] = guarded(collect_throughput, env, now)
    if p["throughput_why"]:
        p["unmeasured"].append("24 h throughput (%s)" % p["throughput_why"])
    p["steve"], p["steve_why"] = guarded(collect_steve, env, state)
    p["steve_cache"], _ = guarded(env.read_json, STEVE_CACHE)

    # who holds the live game: the bridge file first, then the game process
    b, w = p["bridge"], p["win"]
    if b and b["state"] == "HELD":
        p["game_text"], p["game_colour"] = "held by %s" % clip(b["who"] or "?", 16), LIVE
    elif b:
        p["game_text"], p["game_colour"] = ("free, game up" if w and w["game"] else ("free, game down" if w else "free")), GOOD
    else:
        p["game_text"], p["game_colour"] = "UNMEASURED", WARN

    # plain words: only for names the page shows
    want = set()
    it = p["items"]
    if it:
        for k in ("running", "checking", "candidate", "closing"):
            want.update(s.get("item") for s in it["by_status"][k])
    if p["throughput"]:
        want.update(i for _, i in p["throughput"]["recent"])
    p["title"] = titles_for(env, state, want)
    return p


def build(env, state, hist):
    p = gather(env, state)
    now = p["now"]
    strip, chips = status_strip(p)
    tree, roots = tree_lines(p)
    p["roots"] = roots

    head = [strip + ' <span style="color:#98a1af;font-size:85%%;white-space:nowrap">at %s, new every minute</span>' % time.strftime("%H:%M:%S %Z", time.localtime(now)), ""]
    ok_t, fail = state.get("ok_t"), state.get("fail_since")
    if fail or (ok_t and now - ok_t > STALE_AFTER):
        head += ["> **STALE since %s**%s" % (stamp(ok_t or fail), (": last failed refresh said " + state["last_error"]) if state.get("last_error") else ""), ""]

    def panel(name, fn):
        """A panel that cannot draw costs that panel, not the page."""
        out, why = guarded(fn, p)
        if why:
            p["unmeasured"].append("%s panel (%s)" % (name, why))
            return "**%s: UNMEASURED**" % name
        return out

    S = [panel("Relentless", pipeline_svg), "", panel("SteveDesktop", steve_svg), "", "```", "\n".join(tree), "```", "", panel("chains", chains_svg), ""]
    if p["unmeasured"]:
        head += ["**UNMEASURED this minute:** " + "; ".join(p["unmeasured"]), ""]

    n = p["tree"]["total"] if p["tree"] else None
    hist_lines = [window_stats(hist, now, secs, label)[0] for secs, label in ((86400, "24 h"), (604800, "7 d"))]
    if p["timers"] is None:
        tim = "timers UNMEASURED (%s)" % p["timers_why"]
    else:
        tim = "\n".join(["%d timers installed" % len(p["timers"]), "%-24s %10s %12s  %s" % ("timer", "last ran", "next run", "what")] + timers_rows(p["timers"], p["units"], now))
    text = "\n".join(["-- the panels as plain text --", pipeline_text(p), "-- SteveDesktop --", steve_text(p), "-- chains --", chains_text(p),
                      "-- history --"] + hist_lines + ["-- timers --", tim])
    # no blank line anywhere inside: a blank line would end Typora's HTML block and spill the rest as text
    S += ["<details><summary>Plain text panels, timers, history</summary>",
          "<pre style='font-size:12px;line-height:1.3;white-space:pre;overflow-x:auto'>" + escape(re.sub(r"\n\s*\n", "\n", text)) + "</pre>",
          "</details>", "", "<!-- running_now updated_epoch=%d -->" % int(now), ""]
    page = "\n".join(head + S)

    f = {}
    if p["tree"]:
        vals = list(p["tree"]["groups"].values())
        f["workers"] = sum(1 for x in vals if x["label"] == "worker")
        f["roles"] = sum(1 for x in vals if x["family"] == "roles")
        f["helpers"] = sum(1 for x in vals if x["family"] == "helpers")
        f["unknown"] = len(p["tree"]["unknown"])
    if p["win"]:
        f["game"], f["codex"] = p["win"]["game"], p["win"]["codex"]
    sample = {"v": 2, "t": int(now), "n": n, "f": f}
    return page, sample


def run(env=None, write=True):
    env = env or Env()
    if write:
        os.makedirs(OUT_DIR, exist_ok=True)
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
        if isinstance(sample["n"], int):
            append_history(env, hist, sample)
        state["ok_t"] = env.now()
        state.pop("fail_since", None)
        state.pop("last_error", None)
        env.write_atomic(STATE, json.dumps(state))
        # last on purpose: the page is already on disk, so ssh can never hold it back
        guarded(probe_steve, env)
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
