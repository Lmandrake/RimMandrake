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
    python3 running_now.py --phone    the phone-sized plain copy to stdout, write nothing, no ssh

The owner retired Fleet Watch for this page (2026-11-03: "Let's put as much into a static, zero token page as we can."):
progress by mod, receipts and Needs you come from fleet_mods.py and owner_queue.py every FLEET_EVERY seconds, cached in
running_fleet.json and refreshed after the page is written. Every number carries a verdict with a rough normal range, and
every panel a how-to-read line (owner 2026-11-04: "The Markdown should do both", a status and a working model of the system).

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
import shutil
import socket
import statistics
import subprocess
import sys
import time
from html import escape as hesc
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
RULES_FILE = os.path.join(HERE, "..", "rimflow", "relentless_rules.json")     # committed: this tree's copy, level with main
PAUSE_WORDS = "Relentless starts no new content work. System items, expedited items, live-failure fixes, checks of finished builds and the game phase go on."
AGENT = "/mnt/d/ClaudeWork/rimmandrake"
OUT_DIR = AGENT + "/conductor"
OUT = OUT_DIR + "/RUNNING_NOW.md"
PHONE_OUT = OUT_DIR + "/RUNNING_NOW_PHONE.md"
HIST = OUT_DIR + "/running_history.jsonl"
STATE = OUT_DIR + "/running_state.json"
STEVE_CACHE = OUT_DIR + "/running_steve.json"
FLEET_CACHE = OUT_DIR + "/running_fleet.json"
FLEET_STALE = 1800          # past this a last good reading stops being shown
FLEET_EVERY = 300           # mods, receipts and the Needs you list cost about 5 s: refreshed after the page is on disk
HOLD_CAP = 2700             # a bridge hold silent for 45 minutes is stale by the bridge's own rule: it stops counting as busy
TREND_BUCKET = 7200         # the trend lines: two-hour points
TREND_POINTS = 24           # over 48 hours
USUAL_DAYS = 6              # "usual" for a 24 h count: the six 24 h windows before this one
TESTQ = AGENT + "/testq"
HIST_CAP = 10200            # one sample a minute: about 7 days and a bit
TASKLIST_EVERY = 180        # a tasklist.exe call is ~0.6 s wall: cache it
PROBE_EVERY = 180           # ssh to SteveDesktop at most this often
STALE_AFTER = 180           # a page older than this is stale
FENCE_WIDTH = 84            # Typora wraps a code fence at about 87 columns in a 1600 px window
BRIDGE_FILES = ["/home/mandrake/rm/dispatch/infrastructure/state/BRIDGE", "/home/mandrake/rm/bench/infrastructure/state/BRIDGE"]
LEDGER_EVENTS = "/home/mandrake/rm/dispatch/infrastructure/state/ledger/events"
RELENTLESS_STORE = "/home/mandrake/rm/relentless/store"
LIVE_RUNS = "/home/mandrake/rm/relentless/live/runs.jsonl"
RUNS_TAIL = 2 * 1024 * 1024
IDLE_WINDOW_MIN = 180
FUEL_TAIL = 512 * 1024      # series.jsonl gains about 470 bytes per account per 15-minute poll: this holds days
FUEL_NEAR = 3 * 3600        # "current" burn is the last 3 h ...
FUEL_FAR = 6 * 3600         # ... widened to 6 h when under FUEL_NEAR_RISE points rose, since /usage reports whole percents
FUEL_NEAR_RISE = 3
FUEL_MIN_SPAN = 3600        # under an hour of readings is no rate
FUEL_EQUAL = 0.15           # EQUAL: within this share of the pace, or one point over the span, whichever is wider
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
BELT_WORD = {"queued": "waits for a place", "running": "Builder at work", "candidate": "waits for a Judge",
             "checking": "Judge at work", "closing": "being landed", "done": "closed"}
SIDE_WORD = {"game": "needs the live game", "held": "held for the seat or the owner", "blocked": "waits on another item",
             "stopping": "being stopped", "retiring": "being retired", "retired": "dropped for good"}
# A rough normal for how many items sit in each stage: (top of normal, words). Read off the stages on 2026-11-03; only a
# count above the top is called out. Done and retired only grow, so no count of theirs is ever high.
STAGE_NORMAL = {"queued": (400, "100-400"), "running": (9, "3-9"), "candidate": (6, "0-6"), "checking": (9, "0-9"), "closing": (40, "0-40"),
                "done": (None, "only grows"), "game": (40, "0-40"), "held": (40, "0-40"), "blocked": (70, "0-70"), "stopping": (3, "0-3"),
                "retiring": (3, "0-3"), "retired": (None, "only grows")}
# How old the oldest item of a stage normally is: (seconds, words). An old one is the thing to look at, so the top is short.
STAGE_OLD = {"queued": (2 * 86400, "<2d"), "running": (3 * 3600, "<3h"), "candidate": (3600, "<1h"), "checking": (3600, "<1h"), "closing": (86400, "<1d"),
             "game": (2 * 86400, "<2d"), "held": (7 * 86400, "<7d"), "blocked": (7 * 86400, "<7d"), "stopping": (900, "<15m"), "retiring": (900, "<15m")}
LAST_CLOSE = (3 * 3600, "<3h")
# The belt's name lists. Running and checking top out at 9 (STAGE_NORMAL): more than that in a card would push the panel
# down by a screen, so that stage (closing, most days) lists its names whole in a band of its own under the set-aside row.
NAMES_IN_CARD = 9
NEXT_SHOWN, LATEST_SHOWN = 4, 3     # queued and done are too long to list whole: the next few, the latest few, a count of the rest
QUEUE_NEXT_MAX_AGE = 1800           # the tick runs every 2 min and is allowed 20: older than this and the order is old news
NAME_LINE, NAME_GAP = 13, 3         # a name's lines sit close, with a gap before the next name
CARD_CHARS, BAND_CHARS, BAND_COLS, MONO_CHAR = 21, 51, 3, 6.3     # MONO_CHAR: px per character of the mono face at 10.5
# A rough normal for a number with no measured baseline yet, read off the records on 2026-11-03. A measured range replaces it as the record grows.
ROUGH = {"pass": (100, 300), "weak": (50, 200), "fail": (30, 120), "unmeasured": (0, 20), "refused": (10, 60), "closed": (50, 100), "blind_fail": (20, 80), "put_back": (100, 400),
         "tokens_day": (100e6, 400e6), "tokens_per": (1e6, 6e6), "steve_done": (5, 150), "steve_failed": (0, 15), "steve_rows_h": (1, 130),
         "closed_here": (5, 30), "closed_steve": (0, 10), "trend_closed": (0, 18), "trend_blind_fail": (0, 9), "trend_proofs": (0, 63)}
FEED_WORD = {"done": "closed", "blind_fail": "a Judge failed it", "game_fail": "live proof failed", "held_delivered": "held for the seat or the owner",
             "retired": "dropped", "jam_alarm": "jam alarm", "game_staged": "game staged for it"}

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

    def relentless_rules(self):
        return self.read_json(RULES_FILE)

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

    def account_names(self):
        return list(account_usage_module().registry())

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

    def local_stats(self):
        """This machine, read the way the Steve probe reads that one: uptime s, load, cores, RAM used/total MB, free GB."""
        with open("/proc/uptime") as f:
            up = float(f.read().split()[0])
        with open("/proc/loadavg") as f:
            load = float(f.read().split()[0])
        mem = {}
        with open("/proc/meminfo") as f:
            for line in f:
                k, v = line.split(":", 1)
                mem[k] = int(v.split()[0]) // 1024
        free = lambda path: shutil.disk_usage(path).free // 2**30  # noqa: E731
        return {"up": up, "load": load, "cores": os.cpu_count(), "ram": (mem["MemTotal"] - mem["MemAvailable"], mem["MemTotal"]),
                "disk": free("/"), "disk_d": free("/mnt/d")}

    def bridge_events(self):
        """(epoch, state) of this machine's bridge events, oldest first, from every ledger shard."""
        out = []
        for p in glob.glob(LEDGER_EVENTS + "/*.jsonl"):
            with open(p, errors="replace") as f:
                for line in f:
                    if '"bridge"' not in line:
                        continue
                    try:
                        d = json.loads(line)
                        if d.get("event") == "bridge" and d.get("host") in (None, "archmagi"):
                            out.append((iso_epoch(d["ts"]), d.get("tsn") or 0, d.get("state")))
                    except (ValueError, KeyError, TypeError):
                        if line.endswith("\n"):      # only a last line still being written may be broken
                            raise Unmeasured("a bridge record in %s is broken" % os.path.basename(p))
        if not out:
            raise Unmeasured("no bridge event in the ledger")
        # two events in one second keep their real order by the ledger's tsn, never alphabetically by state
        return [(at, state) for at, _, state in sorted(out, key=lambda e: e[:2])]

    def conductor_helpers(self, pid):
        """How many in-process helpers the Conductor window has alive, by the reader the restart path trusts."""
        rf = os.path.join(HERE, "..", "rimflow")
        sys.path[:0] = [rf, HERE]
        import seat_restart     # late: only this line of the page needs it
        sf = seat_restart.session_file(pid) or {}
        if not sf.get("cwd") or not sf.get("sessionId"):
            raise Unmeasured("no session file for pid %s" % pid)
        hs = seat_restart.helpers_of(seat_restart.transcript_path(sf["cwd"], sf["sessionId"]), time.time())
        if hs is None:
            raise Unmeasured("helpers_of could not read the transcript")
        return sum(1 for h in hs if h.get("alive"))

    def fleet_gather(self, now):
        """The slow half: progress by mod, today's receipts, Needs you. Lives in fleet_mods.py and owner_queue.py."""
        sys.path.insert(0, HERE)
        import fleet_mods
        import fleet_watch
        hours = int((now - fleet_mods.local_midnight(now)) / 3600) + 1     # back to local midnight: "finished today"
        d = fleet_mods.gather(int(now), detached_done=[r for r in fleet_watch.rows(hours) if r["status"] != "Building"])
        d["total_mods"] = len(fleet_mods.mod_folders())
        return d

    def status_board(self):
        """STATUS_BOARD.html from the fleet cache just written: STATUS_PAGES_BUILD_REPLACE_RIMPULSE."""
        sys.path.insert(0, HERE)
        import status_board
        return status_board.write(out=os.path.join(OUT_DIR, "STATUS_BOARD.html"), cache=FLEET_CACHE)

    def mods_status(self):
        """`modcheck status`, which re-derives each mod against its code as it stands (the stored word goes stale)."""
        rc, out = self.run(["python3", os.path.join(HERE, "modcheck", "cli.py"), "status"], timeout=45)
        if rc != 0:
            raise Unmeasured("modcheck status exited %d" % rc)
        return out

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


def run_at(t):
    """A live/runs.jsonl `at`: void rows before 2026-11-04 carried epoch seconds."""
    return t if isinstance(t, (int, float)) else iso_epoch(t)


def tokens(n):
    if not n:
        return "0"
    return "%.1fM" % (n / 1e6) if n >= 1e6 else "%dk" % round(n / 1e3)


def clip(s, n):
    s = re.sub(r"\s+", " ", str(s)).strip()
    return s if len(s) <= n else s[:max(n - 1, 1)].rstrip() + "…"


def wrap_name(s, width, hang=0):
    """Lines of at most `width` holding ALL of s, breaking after a _ - / or space so a name stays readable; only a run
    longer than a line is cut. Lines after the first get `width - hang`: the caller indents them by `hang`."""
    s = re.sub(r"\s+", " ", str(s)).strip()
    lines, cur = [], ""
    for tok in re.findall(r"[^_\-/ ]*[_\-/ ]+|[^_\-/ ]+$", s):
        while True:
            room = width if not lines else max(width - hang, 1)
            if len((cur + tok).rstrip()) <= room:
                cur += tok
                break
            if cur:
                lines.append(cur.rstrip())
                cur = ""
                continue
            lines.append(tok[:room])    # one run wider than the line: the only place a word is cut
            tok = tok[room:]
    if cur.strip():
        lines.append(cur.rstrip())
    return lines or [""]


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
        if hit and hit[3].group(0) and hit[2] not in ("selftest", "window"):
            res = hit
        else:
            parent = r["ppid"]
            if parent in by_pid and parent > 1 and parent not in seen:
                res = owner(parent, seen + (pid,))
            # a claude-seat-<name>-<number> scope is a window of its own unless a run that owns its agents started it
            if hit and hit[2] == "window" and (res is None or res[2] not in ("worker", "role", "helper")):
                res = hit
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
        g["main_pid"] = main["pid"] if main else None
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


def silent_hold(b, now):
    """Past HOLD_CAP with no write the bridge's own rule calls a hold stale and anyone may take it: say so, it may be nobody's."""
    return ", silent %s" % ago(now - b["mt"]) if now - b["mt"] > HOLD_CAP else ""


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


def collect_queue_next(env, now):
    """The order the tick computed (relentless.write_queue_next): the page cannot recompute it, it needs the ledger's plan."""
    q = env.read_json(RELENTLESS_STORE + "/queue_next.json")
    if not isinstance(q.get("t"), (int, float)) or not isinstance(q.get("free"), list) or not isinstance(q.get("waiting"), list):
        raise Unmeasured("queue_next.json is not the tick's shape")
    if now - q["t"] > QUEUE_NEXT_MAX_AGE:
        raise Unmeasured("queue_next.json is %s old" % ago(now - q["t"]))
    return q


def collect_staffing(env):
    s = env.read_json(RELENTLESS_STORE + "/staffing.json")
    if not isinstance(s.get("t"), (int, float)):
        raise Unmeasured("staffing.json has no timestamp")
    return s


def collect_game_idle(env, now, waiting):
    """The Conductor's reading (RELENTLESS_TICK_TUNE_FIFTEEN_MINUTE_NAPS): the share of the last IDLE_WINDOW_MIN minutes in
    which no proof held the live game, from live/runs.jsonl. A row with a log held the game. Deploy and load time write no
    rows, so the share is a ceiling on idle. A tail that does not reach back the whole window shortens it, and says so."""
    text, cut_off = env.read_tail(LIVE_RUNS, RUNS_TAIL)
    lines = text.splitlines()
    cut = now - IDLE_WINDOW_MIN * 60
    used, oldest = set(), None
    for i, line in enumerate(lines):
        try:
            d = json.loads(line)
            at = run_at(d["at"])
        except (ValueError, KeyError, TypeError):
            if (i == 0 and cut_off) or (i == len(lines) - 1 and not text.endswith("\n")):
                continue
            raise Unmeasured("runs.jsonl tail line %d is broken" % (i + 1))
        oldest = at if oldest is None else min(oldest, at)
        if cut <= at <= now and d.get("log"):
            used.add(int(at // 60))
    if oldest is None:
        raise Unmeasured("runs.jsonl has no rows")
    window = IDLE_WINDOW_MIN if not cut_off or oldest <= cut else max(1, int((now - oldest) // 60))
    busy = min(len(used), window)       # the span can touch one more epoch minute than it is long
    return {"window_min": window, "used_min": busy, "idle_pct": round(100 * (window - busy) / window),
            "waiting": waiting}


def it_waiting(it):
    """None when the item states were not read: an unread stage is not an empty one."""
    return it["counts"]["game"] if it else None


def game_idle_text(g):
    return ("GAME idle %d%% of the last %d min: a proof held it in %d, %s items wait (ceiling: deploy and load write no rows)"
            % (g["idle_pct"], g["window_min"], g["used_min"], "UNMEASURED" if g["waiting"] is None else g["waiting"]))


def systemd_seconds(words):
    """systemd's "20min", "1min 30s", "1h 5min" -> seconds; anything else (infinity, nothing) -> None."""
    parts = re.findall(r"(\d+)(h|min|s)\b", words)
    if not parts or re.sub(r"\s+", "", words) != "".join(n + u for n, u in parts):
        return None
    return sum(int(n) * {"h": 3600, "min": 60, "s": 1}[u] for n, u in parts)


def collect_tick(env, state):
    d = env.tick_show()
    out = {"limit_s": systemd_seconds(d.get("TimeoutStartUSec", "")), "result": d.get("Result", "")}
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
    days = [collections.Counter() for _ in range(USUAL_DAYS + 1)]     # days[0] is the 24 h on the page, the rest its baseline
    t = days[0]
    start = now - TREND_POINTS * TREND_BUCKET
    trend = {"closed": [0] * TREND_POINTS, "blind_fail": [0] * TREND_POINTS}
    closed_day = collections.Counter()
    recent_done, feed = [], []
    seen = set()
    first_verdict = None
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
        if isinstance(d.get("at"), (int, float)) and d.get("nonce") not in seen:
            first_verdict = d["at"] if first_verdict is None else min(first_verdict, d["at"])
            k = int((now - d["at"]) // 86400)
            if 0 <= k <= USUAL_DAYS:
                seen.add(d.get("nonce"))
                days[k][d.get("word")] += 1
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
        k = int((now - at) // 86400)
        b = int((at - start) // TREND_BUCKET)
        for x in d.get("acts") or []:
            w = x.get("do")
            if 0 <= k <= USUAL_DAYS:
                days[k][w] += 1
            if w == "done":
                closed_day[time.strftime("%Y%m%d", time.gmtime(at))] += 1
            if 0 <= b < TREND_POINTS and w in ("done", "blind_fail"):
                trend["closed" if w == "done" else "blind_fail"][b] += 1
            if at >= cut and w == "done":
                recent_done.append((at, x.get("item") or ""))
            if at >= start and w in FEED_WORD:
                feed.append((at, FEED_WORD[w], x.get("item") or ""))
    if cut_off and first is not None:
        # tokens per item divides a whole day's spend by that day's closes: the day the journal tail starts in is not whole
        if first > cut:
            raise Unmeasured("journal.jsonl tail reaches back less than 24 h")
        closed_day.pop(time.strftime("%Y%m%d", time.gmtime(first)), None)
    recent_done.sort(reverse=True)
    feed.sort(reverse=True)

    def fold(c):
        return {"closed": c["done"], "pass": c["PASS"], "weak": c["WEAK"], "fail": c["FAIL"] + c["game_fail"],
                "unmeasured": c["game_unmeasured"] + c["game_proof_unmeasured"], "refused": c["game_refused"] + c["start_refused"] + c["close_refused"],
                "blind_fail": c["FAIL"], "put_back": c["returned"]}

    # a window counts toward "usual" only when the record behind that count reaches back past its start
    out = fold(t)
    from_journal = first if first is not None else now
    from_verdicts = first_verdict if first_verdict is not None else now
    reach = {"closed": from_journal, "unmeasured": from_journal, "refused": from_journal, "pass": from_verdicts, "weak": from_verdicts,
             "fail": max(from_journal, from_verdicts), "blind_fail": from_verdicts, "put_back": from_journal}
    usual = {}
    for key, since in reach.items():
        vals = [fold(days[k])[key] for k in range(1, USUAL_DAYS + 1) if now - (k + 1) * 86400 >= since]
        if vals:
            usual[key] = (min(vals), max(vals))
    out.update({"recent": recent_done[:3], "trend": trend, "feed": feed[:30], "closed_day": closed_day,
                "usual": usual,
                "short": bool(cut_off and first is not None and first > start)})
    return out


def merged(rows):
    """Sorted (start, end) intervals -> the same with overlaps joined."""
    out = []
    for a, b in sorted(rows):
        if out and a <= out[-1][1]:
            out[-1] = (out[-1][0], max(out[-1][1], b))
        else:
            out.append((a, b))
    return out


def share_of(intervals, t0, t1):
    """The fraction of [t0, t1] the merged intervals cover."""
    return sum(max(0, min(b, t1) - max(a, t0)) for a, b in intervals) / max(t1 - t0, 1)


def bridge_intervals(events, now):
    """Ledger (epoch, state) -> merged spans somebody held the bridge. Each event only speaks for HOLD_CAP after it."""
    out, held, last = [], False, None
    for at, state in events:
        if held:
            out.append((last, min(at, last + HOLD_CAP)))
        held, last = state != "released", at
    if held:
        out.append((last, min(now, last + HOLD_CAP)))
    return merged(out)


def collect_archmagi_live(env, now, items, hist):
    """Last 24 h of live testing here: proof rows by result, what they closed and found, and how busy the game was."""
    text = env.read_text(LIVE_RUNS)
    lines = text.splitlines()
    days = [collections.Counter() for _ in range(USUAL_DAYS + 1)]
    start = now - TREND_POINTS * TREND_BUCKET
    proofs = [0] * TREND_POINTS
    bugs, passed = set(), set()
    first = None
    for i, line in enumerate(lines):
        try:
            d = json.loads(line)
            at = run_at(d["at"])
        except (ValueError, KeyError, TypeError):
            if i == len(lines) - 1 and not text.endswith("\n"):
                continue
            raise Unmeasured("runs.jsonl line %d is broken" % (i + 1))
        if d.get("void"):     # a void row ends earlier rows (relentless_game.void_rows); it is not a run
            continue
        first = at if first is None else min(first, at)
        k = int((now - at) // 86400)
        if 0 <= k <= USUAL_DAYS:
            days[k][d.get("outcome")] += 1
        if d.get("outcome") == "PASS":
            passed.add(d.get("item"))
        if k == 0 and d.get("outcome") == "FAIL":
            bugs.add((d.get("item"), d.get("criterion")))
        b = int((at - start) // TREND_BUCKET)
        if 0 <= b < TREND_POINTS:
            proofs[b] += 1
    if first is None:
        raise Unmeasured("runs.jsonl holds no rows")
    whole = [sum(days[k].values()) for k in range(1, USUAL_DAYS + 1) if now - (k + 1) * 86400 >= first]
    out = {"rows": days[0], "bugs": len(bugs), "usual_rows": (min(whole), max(whole)) if whole else None, "proofs": proofs, "closed": None}
    if items:
        out["closed"] = sum(1 for s in items["by_status"]["done"] if now - (s.get("done_at") or 0) <= 86400 and s.get("item") in passed)
    spans, why = guarded(lambda: bridge_intervals(env.bridge_events(), now))
    out["busy"] = share_of(spans, now - 86400, now) if spans is not None else None
    out["idle_trend"] = None if spans is None else [1 - share_of(spans, start + j * TREND_BUCKET, start + (j + 1) * TREND_BUCKET) for j in range(TREND_POINTS)]
    out["busy_why"] = why
    day = [r for r in hist if now - r["t"] <= 86400 and "game" in (r.get("f") or {})]
    out["game_up"] = sum(1 for r in day if r["f"]["game"]) / len(day) if day else None
    return out


def full_days(rows, now):
    """collect_tokens rows without today: a day still running would flatter the number."""
    today = time.strftime("%Y%m%d", time.gmtime(now))
    return [r for r in rows if r["day"] != today]


def collect_tokens(env, now, thr):
    """Tokens per item closed (a trial): Relentless's own spend files over its own closes, per UTC day."""
    rows = []
    for k in range(0, 8):
        day = time.strftime("%Y%m%d", time.gmtime(now - k * 86400))
        if not thr["closed_day"][day]:
            continue
        try:
            got = env.read_json("%s/spend-%s.json" % (RELENTLESS_STORE, day))
        except FileNotFoundError:       # before the spend files began; an unreadable one fails the reading instead
            continue
        if isinstance(got.get("spent"), (int, float)):
            rows.append({"day": day, "spent": got["spent"], "closed": thr["closed_day"][day], "per": got["spent"] / thr["closed_day"][day]})
    if not rows:
        raise Unmeasured("no spend file with a closed item beside it")
    return rows


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
        if st and prev and len(st) >= 8 and len(prev) >= 8 and sum(st[:8]) > sum(prev[:8]):     # guest time is inside user time; I/O wait is not busy
            d["cpu_pct"] = round(100 * (1 - (st[3] + st[4] - prev[3] - prev[4]) / (sum(st[:8]) - sum(prev[:8]))))
        cache["stat"] = st
        cache["good"] = d
        cache["good_t"] = now
    env.write_atomic(STEVE_CACHE, json.dumps(cache))
    return cache


def collect_steve(env, state, items=None):
    now = env.now()
    sj, why = guarded(env.read_json, TESTQ + "/steward.json")
    if sj is not None and not isinstance(sj.get("epoch"), (int, float)):
        sj, why = None, "steward.json has no epoch"
    # a dead steward costs its own words: the queue, the results and the machine reading are other sources
    out = {"state": None, "reason": "steward UNMEASURED: %s" % why, "age": None, "incident": None} if sj is None else {
        "state": sj.get("state"), "fault": sj.get("fault"), "reason": sj.get("reason") or "", "age": now - sj["epoch"], "incident": sj.get("incident") or None}
    sj = sj or {}
    if sj.get("since"):
        out["since"] = iso_epoch(sj["since"])
    for d in ("running", "pending"):
        v, why = guarded(lambda p: len(env.listdir(p)), TESTQ + "/" + d)
        out[d] = v
    out["jobs_known"] = False
    names, why = guarded(env.listdir, TESTQ + "/done")
    if names is not None:
        # every result, read once: a job's name dates its birth, and one born a fortnight ago may finish this minute.
        # A job finished over 8 days ago keeps only its finish time, so a later minute need not read it again.
        keep = {n for n in names if n.endswith(".json")}
        memo = state.setdefault("steve_jobs", {})
        for n in list(memo):
            if n not in keep or memo[n].get("v") != 2:
                del memo[n]
        unread = 0
        for n in keep - set(memo):
            try:
                j = env.read_json(TESTQ + "/done/" + n)
            except Exception:       # noqa: BLE001 - being written or bad: the day's counts are unknown, not short
                unread += 1
                continue
            r = j.get("result") or {}
            job = j.get("job") or {}
            fin, begun = r.get("finished") or j.get("finished"), r.get("started")
            cnt = r.get("counts") if isinstance(r.get("counts"), dict) else {}
            memo[n] = {"v": 2, "f": iso_epoch(fin) if fin else 0, "s": iso_epoch(begun) if begun else 0, "o": r.get("outcome") or "?", "c": r.get("cause") or "",
                       "r": len(r.get("rows") or []), "p": job.get("purpose") or "", "m": job.get("mod") or "", "i": job.get("item") or "",
                       "k": {k: v for k, v in cnt.items() if isinstance(v, int)},
                       "b": sorted({"%s/%s" % (x.get("chain"), x.get("row")) for x in (r.get("rows") or []) if isinstance(x, dict) and x.get("verdict") == "FAIL"})}
        for n, v in memo.items():
            if v["f"] and now - v["f"] > 8 * 86400:
                memo[n] = {"v": 2, "f": v["f"]}
        jobs = [v for v in memo.values() if "o" in v]
        day = [v for v in jobs if now - v["f"] <= 86400]
        out["jobs_known"] = not unread
        out["done"] = sum(1 for v in day if v["o"] == "DONE")
        out["failed"] = sum(1 for v in day if v["o"] != "DONE")
        out["rows_h"] = sum(v["r"] for v in day) / 24.0
        out["last"] = max(jobs, key=lambda v: v["f"]) if jobs else None
        earliest = min((v["f"] for v in memo.values() if v["f"]), default=now)
        win = [[v for v in jobs if k <= (now - v["f"]) / 86400 < k + 1] for k in range(1, USUAL_DAYS + 1) if now - (k + 1) * 86400 >= earliest]

        def span(fn):
            vals = [fn(w) for w in win]
            return (min(vals), max(vals)) if vals else None

        out["usual_done"] = span(lambda w: sum(1 for v in w if v["o"] == "DONE"))
        out["usual_failed"] = span(lambda w: sum(1 for v in w if v["o"] != "DONE"))
        out["usual_rows_h"] = span(lambda w: sum(v["r"] for v in w) / 24.0)
        spans = merged([(v["s"], v["f"]) for v in jobs if v["s"] and v["f"] > v["s"]])
        rows = collections.Counter()
        for v in day:
            rows.update(v["k"])
        done_items = {s.get("item") for s in (items["by_status"]["done"] if items else []) if now - (s.get("done_at") or 0) <= 86400}
        # an unreadable result would make these short: the panel says UNMEASURED instead
        out["live"] = None if unread else {"busy": share_of(spans, now - 86400, now), "rows": rows, "closed": len({v["i"] for v in day if v["i"] and v["i"] in done_items and v["k"].get("PASS")}) if items else None,
                       "bugs": len({"%s %s" % (v["m"], b) for v in day for b in v["b"]}), "jobs": [(v["f"], v["o"], v["p"], v["m"]) for v in sorted(day, key=lambda v: -v["f"])[:6]]}
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

    def polyline(self, pts, stroke=LIVE, sw=1.6):
        self.parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (" ".join("%.1f,%.1f" % q for q in pts), stroke, sw))

    def reading_open(self, label, hover=None):
        """One reading: a named group, so a panel's readings can be told apart. A hover line is free, it adds the why where the viewer shows it."""
        self.parts.append('<g data-reading="%s">' % escape(str(label), {'"': "&quot;"}) + ("<title>%s</title>" % escape(hover) if hover else ""))

    def hover_open(self, hover):
        """A hover line over a few text lines, with no reading of its own: the name's plain words stay a mouse-over away."""
        self.parts.append("<g><title>%s</title>" % escape(str(hover)))

    def reading_close(self):
        self.parts.append("</g>")

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


# --------------------------------------------------------------------------- what a number means
def versus(n, usual, high_is_bad=True, rough=None, show=None):
    """A count against the same count in the windows before it -> (note, colour). With no such windows yet, against a rough
    range read off the records, and the note says "rough"; with neither, it says so and never guesses."""
    word = "usual"
    if usual is None:
        usual, word = rough, "rough"
    if usual is None:
        return "no baseline yet", DIM
    fmt = "%d-%d" if all(float(x).is_integer() for x in usual) else "%.0f-%.0f"
    rng = "%s-%s" % (show(usual[0]), show(usual[1])) if show else fmt % tuple(usual)
    if n > usual[1]:
        return "high, %s %s" % (word, rng), WARN if high_is_bad else GOOD
    if n < usual[0]:
        return "low, %s %s" % (word, rng), GOOD if high_is_bad else WARN
    return "normal, %s %s" % (word, rng), DIM


def against(n, top, words):
    """A reading against a rough fixed top -> (note, colour)."""
    return ("high, normal %s" % words, WARN) if n > top else ("ok, normal %s" % words, DIM)


def uptime_note(up):
    return ("low, normal 1 h+", WARN) if up < 3600 else ("ok, normal 1 h+", DIM)


def stage_note(name, n):
    """A stage's count -> (verdict and normal, colour). Done and retired only grow, so no count of theirs is off."""
    top, words = STAGE_NORMAL[name]
    bottom = re.match(r"(\d+)-", words)
    if n is not None and top and n > top:
        return "high, normal " + words, WARN
    if n is not None and bottom and n < int(bottom.group(1)):
        return "low, normal " + words, WARN
    return "ok, normal " + words, DIM


def age_note(head, age, limit):
    """An age -> "oldest 3 h: ok, normal <1 d" and its colour."""
    return "%s %s: %s, normal %s" % (head, ago(age).replace(" ", ""), "high" if age > limit[0] else "ok", limit[1]), WARN if age > limit[0] else DIM


def tile(s, x, y, w, label, val, colour=TEXT, bar=None, note=None, note_colour=DIM, hover=None):
    """One number with its verdict under it."""
    s.reading_open(label, hover)
    s.rect(x, y, w, 62, CARD, None, 5)
    s.text(x + 8, y + 14, label, 9.5, DIM, "700")
    missing = val == "?"
    # the mono face is 0.6 em wide: a long value shrinks to stay inside its tile
    s.text(x + 8, y + 33, "UNMEASURED" if missing else val, 11 if missing else min(15, round((w - 16) / (len(str(val)) * 0.6), 1)), colour, "700", font=MONO)
    if bar is not None:
        s.rect(x + 8, y + 38, w - 16, 3, EDGE, None, 1)
        s.rect(x + 8, y + 38, (w - 16) * min(bar, 1), 3, WARN if bar >= 0.9 else LIVE, None, 1)
    if note:
        s.text(x + 8, y + 53, clip(note, int((w - 12) / 4.7)), 9, note_colour)
    s.reading_close()


def live_row(s, y, d, busy_means, closed_means, closed_rough):
    """The Live Testing tiles, the same five on each machine, so the two read side by side."""
    s.text(18, y - 6, "LIVE TESTING, LAST 24 H", 10.5, DIM, "700")
    if d is None:
        s.text(190, y - 6, "UNMEASURED", 10.5, WARN, "700")
        return
    busy = d.get("busy")
    if busy is None:
        tile(s, 14, y, 200, "BUSY / IDLE", "?", WARN)
    else:
        note, col = ("low, normal busy 20-90%", WARN) if busy < 0.2 else (("high, normal busy 20-90%", WARN) if busy > 0.9 else ("ok, normal busy 20-90%", DIM))
        tile(s, 14, y, 200, "BUSY / IDLE", "%d%% / %d%%" % (round(busy * 100), 100 - round(busy * 100)), TEXT, busy, note, col, busy_means)
    r = d.get("rows") or {}
    total = sum(r.values())
    measured = r.get("PASS", 0) + r.get("FAIL", 0)
    words = " ".join("%s %d" % (k, r.get(k, 0)) for k in ("PASS", "FAIL", "UNMEASURED", "REFUSED") if r.get(k) or k in ("PASS", "FAIL"))
    if total:
        low = measured / total < 0.3
        note = "%s, %d of %d measured%s; normal over 30%%" % ("low" if low else "ok", measured, total, ", most said nothing" if low else "")
        tile(s, 222, y, 338, "PROOF ROWS BY RESULT", words, TEXT, measured / total, note, WARN if low else DIM, "PASS and FAIL measured something; UNMEASURED and REFUSED ran or were turned away without an answer")
    else:
        tile(s, 222, y, 338, "PROOF ROWS BY RESULT", "none", DIM, None, "low, no live proof ran in 24 h; normal: some every day", WARN)
    c = d.get("closed")
    cn = versus(c, None, False, closed_rough) if c is not None else (None, DIM)
    tile(s, 568, y, 150, "CLOSED BY LIVE PROOF", "?" if c is None else "%d items" % c, TEXT if c is not None else WARN, None, cn[0], cn[1], closed_means)
    b = d.get("bugs")
    tile(s, 726, y, 130, "BUGS FOUND", "%d" % b, BAD if b else TEXT, None, *against(b, 20, "0-20"), "Distinct clauses with a FAIL in 24 h. Some will turn out to be the harness, not the mod.")
    tile(s, 864, y, 162, "FALSIFIED EXPECTATIONS", "not recorded", DIM, None, "nothing records these yet", DIM, "A player expectation a live test proved false. No program writes this down yet.")


# --------------------------------------------------------------------------- the Relentless panel
def stage_since(st):
    """When an item entered the stage it is in, by the field each stage writes; None when the stage has no clock."""
    def field(d, k):
        v = d.get(k) if isinstance(d, dict) else None
        return float(v) if isinstance(v, (int, float)) else None
    status = st.get("status")
    chk, cand = st.get("check"), st.get("candidate")
    return {"queued": field(st, "returned_at") or field(st, "enrolled_at"), "running": field(st, "started_at"), "candidate": field(cand, "at"),
            "checking": field(chk, "at"), "closing": field(st, "tomb_since") or field(chk, "verdict_at") or field(cand, "at"),
            "game": field(st.get("game"), "entered_at"), "held": field(st.get("hold"), "at"), "blocked": field(st, "blocked_at"),
            "stopping": field(st, "stopping_since"), "retiring": field(st, "stopping_since")}.get(status)


def oldest_in(it, name, now):
    """-> (age seconds, item) of the stage's oldest item, or None."""
    rows = [(now - t, x.get("item") or "") for x in it["by_status"][name] for t in [stage_since(x)] if t]
    return max(rows) if rows else None


def age_head(t, now):
    return ago(now - t).replace(" ", "") + " " if t else ""


def stage_lists(p):
    """What each belt card lists: {stage: [("note", words) | ("name", age, item), ...]}. A name is never shortened here or later."""
    now, it, thr = p["now"], p["items"], p["throughput"]
    out = {k: [] for k in BELT}
    if it:
        for k in ("running", "candidate", "checking", "closing"):
            rows = sorted(it["by_status"][k], key=lambda v: (stage_since(v) or now, v.get("item") or ""))
            out[k] = [("name", age_head(stage_since(r), now), r.get("item") or "") for r in rows]
        waiting = it["by_status"]["queued"]
        exp = sum(1 for v in waiting if v.get("expedite"))
        ret = sum(1 for v in waiting if v.get("returns"))
        out["queued"] = [("note", "%d failed a check before" % ret)] + ([("note", "%d expedited" % exp)] if exp else [])
        qn = p.get("queue_next")
        if qn is None:
            out["queued"].append(("note", "next in line UNMEASURED"))
        elif waiting:
            here = {v.get("item") for v in waiting}
            free = [i for i in qn["free"] if i in here][:NEXT_SHOWN]
            held = [i for i in qn["waiting"] if i in here][:NEXT_SHOWN - len(free)]
            if free:
                out["queued"] += [("note", "next in line:")] + [("name", "", i) for i in free]
            if held:
                out["queued"] += [("note", "not free to start:")] + [("name", "", i) for i in held]
            if len(waiting) > len(free) + len(held):
                out["queued"].append(("note", "+ %d more" % (len(waiting) - len(free) - len(held))))
    if thr:
        recent = thr["recent"][:LATEST_SHOWN]
        out["done"] = [("name", age_head(at, now), i) for at, i in recent]
        rest = it["counts"]["done"] - len(recent) if it else 0
        if rest > 0:
            out["done"].append(("note", "+ %d earlier" % rest))
    elif it and it["counts"]["done"]:
        out["done"] = [("note", "latest UNMEASURED")]
    return out


def banded(lists):
    """The stages whose names are too many for a card; they get a band of their own, in belt order."""
    return [k for k in BELT if sum(1 for e in lists[k] if e[0] == "name") > NAMES_IN_CARD]


def card_entries(lists, name):
    if name in banded(lists):
        return [("note", "all %d named below" % len(lists[name]))]
    return lists[name]


def entries_height(entries):
    """Pixels the card needs for its list, the same sums the drawing does."""
    h = 0
    for e in entries:
        h += NAME_LINE * len(wrap_name(e[1] if e[0] == "note" else e[1] + e[2], CARD_CHARS, 2)) + NAME_GAP
    return h


def band_columns(rows):
    """-> (columns of rows, height). Rows run down the columns, oldest first, the columns as level as whole names allow."""
    total = sum(len(wrap_name(e[1] + e[2], BAND_CHARS, 2)) for e in rows)
    each, cols, cur, used = -(-total // BAND_COLS), [], [], 0
    for e in rows:
        n = len(wrap_name(e[1] + e[2], BAND_CHARS, 2))
        if cur and used + n > each and len(cols) < BAND_COLS - 1:
            cols.append(cur)
            cur, used = [], 0
        cur.append(e)
        used += n
    cols.append(cur)
    tallest = max(sum(len(wrap_name(e[1] + e[2], BAND_CHARS, 2)) for e in c) for c in cols)
    return cols, 24 + tallest * NAME_LINE


def trend_rows(p):
    """The four lines the owner chose: label, two-hour points, colour, how to print a point. A line it cannot read is None."""
    thr, live = p["throughput"], p["live_here"]
    tr = thr["trend"] if thr else {}
    count = lambda v: "%d" % v  # noqa: E731
    return [("closed", tr.get("closed"), GOOD, count, lambda v: versus(v, None, False, ROUGH["trend_closed"])),
            ("Judge fails", tr.get("blind_fail"), BAD, count, lambda v: versus(v, None, True, ROUGH["trend_blind_fail"])),
            ("live proofs", live["proofs"] if live else None, LIVE, count, lambda v: versus(v, None, False, ROUGH["trend_proofs"])),
            ("game idle", live.get("idle_trend") if live else None, WARN, lambda v: "%d%%" % round(v * 100), lambda v: against(v * 100, 50, "under 50%"))]


def pipeline_svg(p):
    """The instrument panel. Numbers are the primary layer; items secondary; arrows context."""
    now, it, thr, title = p["now"], p["items"], p["throughput"], p["title"]
    lists = stage_lists(p)
    # the cards grow to the longest list, and every band adds its own height: all the layout below hangs off these two
    ch = max([170] + [112 + entries_height(card_entries(lists, k)) + 6 for k in BELT])
    bands = [(k, *band_columns(lists[k])) for k in banded(lists)]
    W, H = 1040, 610 + (ch - 170) + sum(b[2] + 8 for b in bands)
    s = Svg(W, H, "Relentless Pipeline: stage counts, places, tick, breaker, trends, last 24 hours")
    # ---- header gauges
    s.text(18, 34, "RELENTLESS", 20, TEXT, "700")
    s.text(18, 58, "PIPELINE", 20, TEXT, "700")
    places, live = p["places"], it["live"] if it else None
    x = 172
    s.reading_open("PLACES")
    s.text(x, 20, "PLACES", 10, DIM, "600")
    if places and live is not None:
        shown = min(max(places, live), 9)     # the number says how many; past nine the row would run under TICK
        for i in range(shown):
            s.rect(x + i * 17, 26, 14, 12, LIVE if i < live else "none", LIVE if i < live else FAINT, 2)
        x2 = x + shown * 17 + 4
        s.text(x2, 37, "%d / %d" % (live, places), 15, TEXT, "700", font=MONO)
        word = "low" if live < places - 2 else ("high" if live > places + 1 else "ok")
        s.text(x, 50, "%s, normal %d-%d" % (word, places - 2, places + 1), 9, DIM if word == "ok" else WARN)
    else:
        s.text(x, 37, "UNMEASURED", 13, WARN, "700")
    s.reading_close()
    tick, gx = p["tick"], 390

    def gauge(xx, label, value, colour=TEXT, note=None, note_colour=DIM, yy=0):
        s.reading_open(label)
        s.text(xx, 20 + yy, label, 10, DIM, "600")
        s.text(xx, 37 + yy, value, 13, colour, "700", font=MONO)
        if note:
            s.text(xx, 50 + yy, note, 9, note_colour)
        s.reading_close()

    if tick:
        limit = tick["limit_s"]
        note = "normal under %s" % ago(limit * 0.8) if limit else "no limit read"
        if tick["running"]:
            over = limit and tick["for_s"] > limit * 0.8
            val = "running %s" % ago(tick["for_s"]) + (" of %s" % ago(limit) if limit else "")
            gauge(gx, "TICK", val, WARN if over else TEXT, ("high, near the limit, " if over else "ok, ") + note, WARN if over else DIM)
        else:
            gauge(gx, "TICK", "%s ago, took %s" % (ago(tick["ended_s"]), ago(tick["last_s"]) if tick["last_s"] else "UNMEASURED"), BAD if tick["result"] not in ("success", "") else TEXT,
                  ("bad, last run failed; " if tick["result"] not in ("success", "") else ("high, " if limit and tick["last_s"] and tick["last_s"] > limit * 0.8 else "ok, ")) + note)
    else:
        gauge(gx, "TICK", "UNMEASURED", WARN)
    br = breaker_word(p)
    gauge(600, "BREAKER", br, WARN if br == "UNMEASURED" else (GOOD if br == "clear" else BAD), "ok, normal clear" if br == "clear" else ("bad, normal clear" if br != "UNMEASURED" else None))
    gi = p.get("game_idle")
    idle_note = "idle %d%% of %d min, %s wait; %s, normal under 50%%" % (gi["idle_pct"], gi["window_min"], "UNMEASURED" if gi["waiting"] is None else gi["waiting"],
                                                                        "ok" if gi["idle_pct"] < 50 else ("high" if gi["waiting"] else ("ok, nothing waits" if gi["waiting"] == 0 else "verdict UNMEASURED"))) if gi else "idle UNMEASURED"
    gauge(700, "LIVE GAME", p["game_text"], p["game_colour"], idle_note, WARN if not gi or (gi["idle_pct"] >= 50 and gi["waiting"]) else DIM)
    # second row: what the pipeline costs and what it is for
    yy = 52
    tk = p["tokens"]
    full = full_days(tk, now) if tk else []
    if p.get("spent_n") is not None:
        days_seen = [r["spent"] for r in full]
        verdict = versus(p["spent_n"], (min(days_seen), max(days_seen)) if len(days_seen) > 1 else None, True, ROUGH["tokens_day"], tokens)[0]
        high = verdict.startswith("high")
        # the day is still running: under the range says nothing yet, so it is only ever ok or high
        gauge(172, "TOKENS TODAY", p["spent"], WARN if high else TEXT,
              ("high," if high else "ok,") + verdict.split(",", 1)[1] + " a day" + ("; %s/%s: %s" % (full[0]["day"][4:6], full[0]["day"][6:], tokens(full[0]["spent"])) if full else ""), WARN if high else DIM, yy=yy)
    else:
        gauge(172, "TOKENS TODAY", "UNMEASURED", WARN, yy=yy)
    if full:
        earlier = [r["per"] for r in full[1:]]
        verdict, col = versus(full[0]["per"], (min(earlier), max(earlier)) if len(earlier) > 1 else None, True, ROUGH["tokens_per"], tokens)
        gauge(390, "TOKENS PER ITEM CLOSED (TRIAL)", "%s" % tokens(full[0]["per"]), TEXT, "%s; %s/%s: %d closed" % (verdict, full[0]["day"][4:6], full[0]["day"][6:], full[0]["closed"]), col, yy=yy)
    else:
        gauge(390, "TOKENS PER ITEM CLOSED (TRIAL)", "UNMEASURED", WARN, yy=yy)
    ac = p["accepted"]
    if ac:
        low = ac["green"] * 2 < ac["total"]
        gauge(600, "MODS ACCEPTED, GOAL IS ALL", "%d of %d" % (ac["green"], ac["total"]), WARN if low else TEXT,
              "%s, normal over half; GREEN at today's code; %d at older code, %d red, %d draft, %d never run" % ("low" if low else "ok", ac["stale"], ac["red"], ac["draft"], ac["never"]), WARN if low else DIM, yy=yy)
    else:
        gauge(600, "MODS ACCEPTED, GOAL IS ALL", "UNMEASURED", WARN, yy=yy)
    # ---- the belt
    cw, gap, x0, y0 = 152, 20, 16, 138
    cx = {}
    for i, name in enumerate(BELT):
        x = x0 + i * (cw + gap)
        cx[name] = x
        n = it["counts"][name] if it else None
        hot = name in ("running", "checking") and n
        s.rect(x, y0, cw, ch, CARD, LIVE if hot else (GOOD if name == "done" else EDGE), 7, 2 if hot else 1)
        s.reading_open(name.upper())
        s.text(x + 10, y0 + 19, name.upper(), 11, DIM, "700")
        s.text(x + 10, y0 + 54, "UNMEASURED" if n is None else n, 13 if n is None else 34, WARN if n is None or stage_note(name, n)[0].startswith("high") else (TEXT if n else FAINT), "700", font=MONO)
        s.text(x + 10, y0 + 70, BELT_WORD[name], 10.5, DIM)
        verdict, col = stage_note(name, n)
        if n is not None:
            s.text(x + 10, y0 + 83, verdict, 9, col)
        old = oldest_in(it, name, now) if it else None
        if old:
            note_, col_ = age_note("oldest", old[0], STAGE_OLD[name])
            s.text(x + 10, y0 + 96, note_, 9, col_)
        elif name == "done" and thr and thr["recent"]:
            note_, col_ = age_note("last", now - thr["recent"][0][0], LAST_CLOSE)
            s.text(x + 10, y0 + 96, note_, 9, col_)
        yy = y0 + 112
        for e in card_entries(lists, name):
            if e[0] == "note":
                for ln in wrap_name(e[1], CARD_CHARS, 2):
                    s.text(x + 10, yy, ln, 10.5, DIM, font=MONO)
                    yy += NAME_LINE
            else:
                s.hover_open(title(e[2]))
                for j, ln in enumerate(wrap_name(e[1] + e[2], CARD_CHARS, 2)):
                    s.text(x + 10 + (2 * MONO_CHAR if j else 0), yy, ln, 10.5, TEXT, font=MONO)
                    yy += NAME_LINE
                s.reading_close()
            yy += NAME_GAP
        s.reading_close()
        if i < len(BELT) - 1:
            s.arrow_r(x + cw + 1, x + cw + gap - 1, y0 + 40, BAR)
    # FAIL loop: checking back to queued, along the top of the belt
    ly = 120
    qx, kx = cx["queued"] + cw / 2, cx["checking"] + cw / 2
    s.line(kx, y0, kx, ly, BAD, 1.5)
    s.line(kx, ly, qx, ly, BAD, 1.5)
    s.arrow_d(qx, ly, y0, BAD)
    label = "a Judge's FAIL goes back to the queue: %s in 24 h%s" % (thr["blind_fail"] if thr else "UNMEASURED", "; " + versus(thr["blind_fail"], thr["usual"].get("blind_fail"), True, ROUGH["blind_fail"])[0] if thr else "")
    s.rect(qx + 96, ly - 9, len(label) * 5.9 + 16, 18, BG, None, 0)
    s.reading_open("FAIL LOOP")
    s.text(qx + 104, ly + 4, label, 11, BAD, "600")
    s.reading_close()
    # ---- side branches off RUNNING
    ry, sy, sh = y0 + ch + 18, y0 + ch + 34, 84
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
        s.reading_open(name.upper())
        s.text(x + 10, sy + 16, name.upper(), 10.5, DIM, "700")
        s.text(x + cw - 10, sy + 26, "UNMEASURED" if n is None else n, 11 if n is None else 24, WARN if n is None else (TEXT if n else FAINT), "700", "end", MONO)
        s.text(x + 10, sy + 42, SIDE_WORD[name], 10, DIM)
        verdict, col = stage_note(name, n)
        if n is not None:
            s.text(x + 10, sy + 58, verdict, 9, col)
        old = oldest_in(it, name, now) if it else None
        if old:
            note_, col_ = age_note("oldest", old[0], STAGE_OLD[name])
            s.text(x + 10, sy + 72, note_, 9, col_)
        s.reading_close()
    # ---- a stage too long for its card names everything here, whole, on a single line where it fits
    by = sy + sh + 12
    for name, cols, band_h in bands:
        s.rect(x0, by, W - 2 * x0, band_h, CARD, EDGE, 6)
        s.reading_open("NAMES " + name.upper())
        s.text(x0 + 10, by + 15, "%s: ALL %d, LONGEST THERE FIRST" % (name.upper(), len(lists[name])), 10.5, DIM, "700")
        for c, col in enumerate(cols):
            cx_, yy = x0 + 10 + c * (W - 2 * x0 - 20) / BAND_COLS, by + 30
            for e in col:
                s.hover_open(title(e[2]))
                for j, ln in enumerate(wrap_name(e[1] + e[2], BAND_CHARS, 2)):
                    s.text(cx_ + (2 * MONO_CHAR if j else 0), yy, ln, 10.5, TEXT, font=MONO)
                    yy += NAME_LINE
                s.reading_close()
        s.reading_close()
        by += band_h + 8
    # ---- throughput: common zero baseline, direct labels
    ty = by + 6 if bands else sy + sh + 18
    s.line(16, ty - 8, W - 16, ty - 8, EDGE, 1)
    s.text(18, ty + 8, "LAST 24 H, EVENTS (SEVERAL PER ITEM)", 10.5, DIM, "700")
    if thr:
        rows = [("CLOSED", "closed", GOOD, False), ("PASS", "pass", GOOD, False), ("WEAK", "weak", WARN, True), ("FAIL", "fail", BAD, True),
                ("GAME UNMEASURED", "unmeasured", WARN, True), ("REFUSED", "refused", BAR, True), ("PUT BACK", "put_back", BAR, True)]
        top = max(max(thr[r[1]] for r in rows), 1)
        for j, (lab, key, col, bad) in enumerate(rows):
            yy = ty + 18 + j * 19
            n = thr[key]
            note, ncol = versus(n, thr["usual"].get(key), bad, ROUGH.get(key))
            s.reading_open("BAR " + lab)
            s.text(112, yy + 11, lab, 10.5, DIM, anchor="end", weight="600")
            s.rect(118, yy + 1, 190, 13, CARD, None, 2)
            s.rect(118, yy + 1, max(190 * n / top, 2 if n else 0), 13, col, None, 2)
            s.text(314, yy + 12, n, 12, TEXT, "700", font=MONO)
            s.text(350, yy + 11, note, 9, ncol)
            s.reading_close()
    else:
        s.text(120, ty + 40, "UNMEASURED: %s" % clip(p["throughput_why"], 100), 13, WARN, "700")
    # trends: each line on its own zero baseline, since a count and a share cannot share an axis
    bx, lx, rx, rh = 486, 556, 900, 30
    s.text(bx, ty + 8, "TRENDS, 48 H, TWO-HOUR POINTS", 10.5, DIM, "700")
    for j, (lab, vals, col, show, judge) in enumerate(trend_rows(p)):
        yy = ty + 18 + j * rh
        s.reading_open("TREND " + lab)
        s.text(bx, yy + 17, lab, 10.5, DIM, weight="600")
        s.line(lx, yy + rh - 4, rx, yy + rh - 4, EDGE, 1)
        if vals is None:
            s.text(lx + 4, yy + 17, "UNMEASURED", 10, WARN, "700")
            s.reading_close()
            continue
        top = max(max(vals), 1 if lab != "game idle" else 1.0)
        n = len(vals) - 1
        s.polyline([(lx + (rx - lx) * i / n, yy + rh - 4 - (rh - 8) * v / top) for i, v in enumerate(vals)], col)
        s.text(rx + 8, yy + 17, "now " + show(vals[-1]), 10.5, TEXT, "700", font=MONO)
        s.text(1024, yy + 17, "top " + show(top if lab != "game idle" else max(vals)), 9, DIM, anchor="end")
        verdict, ncol = judge(vals[-1])
        s.text(rx + 8, yy + 27, verdict, 9, ncol)
        s.reading_close()
    yy = ty + 18 + 4 * rh
    s.text(lx, yy + 9, "48 h ago", 9, DIM)
    s.text(rx, yy + 9, "now", 9, DIM, anchor="end")
    if thr and thr["short"]:
        s.text((lx + rx) / 2, yy + 9, "journal tail covers less than 48 h", 9, WARN, anchor="middle")
    return s.out()


def fence_wrap(words, first, rest):
    """Whole words at the fence's width: the first line starts `first`, the others `rest`."""
    hang = len(rest) - len(first)
    lines = wrap_name(words, FENCE_WIDTH - len(first), hang)
    return [(rest if j else first) + ln for j, ln in enumerate(lines)]


def pipeline_text(p):
    """The same panel as a monospace rail: the fallback twin, and what a raw text reader sees."""
    it, thr = p["items"], p["throughput"]
    if not it:
        return "RELENTLESS PIPELINE  stages UNMEASURED"
    c = it["counts"]
    top = max([c[k] for k in BELT + SIDE] + [1])

    def rail(name):
        n = c[name]
        return "%-10s %4d %s" % (name.upper(), n, "█" * (round(24 * n / top) or (1 if n else 0)))

    side = {"running": "──▶ game %d, held %d, blocked %d" % (c["game"], c["held"], c["blocked"]),
            "closing": "    stopping %d, retiring %d ──▶ retired %d" % (c["stopping"], c["retiring"], c["retired"])}
    out = ["RELENTLESS PIPELINE  places %d/%s  breaker %s" % (it["live"], p["places"] if p["places"] else "UNMEASURED",
                                                     breaker_word(p))]
    lists = stage_lists(p)
    for i, name in enumerate(BELT):
        ln = rail(name)
        if name in side:
            ln = "%-44s%s" % (ln, side[name])
        out.append(ln)
        for e in lists[name]:   # whole names, as on the cards
            out += fence_wrap(e[1] if e[0] == "note" else e[1] + e[2], "  │   ", "  │     ")
        if i < len(BELT) - 1:
            out.append("  │" + ("  a Judge's FAIL returns to queued: %s in 24 h" % thr["blind_fail"] if name == "checking" and thr else ""))
    gi = p.get("game_idle")
    out.append(game_idle_text(gi) if gi else "GAME idle UNMEASURED (%s)" % p.get("game_idle_why"))
    if thr:
        out.append("24 h: closed %d, PASS %d, WEAK %d, FAIL %d, game-phase UNMEASURED %d, REFUSED %d" % (thr["closed"], thr["pass"], thr["weak"], thr["fail"], thr["unmeasured"], thr["refused"]))
    title = p["title"]
    olds = [(k, oldest_in(it, k, p["now"])) for k in BELT + SIDE]
    out.append("oldest:")
    for k, o in olds:
        if o:
            out += fence_wrap("%s %s: %s" % (k, ago(o[0]), title(o[1])), "  ", "      ")
    for lab, vals, _, show, _ in trend_rows(p):
        out.append("trend %-12s %s" % (lab, " ".join(show(v) for v in vals) if vals else "UNMEASURED"))
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

    def leaf(prefix, name, right, procs, cont=None):
        # name stretches: the counts column stays whole; with `cont` the name wraps under itself in full, without it takes the clip
        counts = kinds_text(procs, by_pid) + " = %d" % len(procs)
        room = max(W - len(prefix) - len(counts) - len(right) - 3, 12)
        if cont is None:
            L.append("%s%-*s %s  %s" % (prefix, room, clip(name, room), right, counts))
            return
        first = wrap_name(name, room)[0]
        L.append("%s%-*s %s  %s" % (prefix, room, first, right, counts))
        left = re.sub(r"\s+", " ", str(name)).strip()[len(first):].strip()
        if left:
            L.extend(cont + ln for ln in wrap_name(left, W - len(cont)))

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
    held = "%d/%d" % (it["live"], p["places"]) if it and p["places"] else "UNMEASURED"
    L.append("├┄ RELENTLESS PIPELINE  Builders %d, Judges %d%s, places %s  [%d proc]" % (n_work, n_chk, ", other %d" % n_other if n_other else "", held, n_procs(rel_all)))
    L.append("│  ├─ supervisor tick: " + (kinds_text(sum((x["procs"] for x in sup), []), by_pid) or "not mid-run") + "  [%d proc]" % n_procs(sup))
    for i, w in enumerate(workers):
        branch = "└─" if i == len(workers) - 1 else "├─"
        st = it["by_short"].get(w["id"].split("-")[0]) if it else None
        name = title(st["item"]) if st else "item UNMEASURED"
        right = "%6s %-4s %5s" % (ago(w["age"]), w["model"][:4], tokens(st.get("spent")) if st else "UNMEASURED")
        leaf("│  %s %-5s " % (branch, {"work": "build", "check": "judge"}.get(w["kind"], w["kind"] or "?")), name, right, w["procs"],
             cont="│  %s" % (" " if branch == "└─" else "│") + " " * 8)
    if not workers:
        L.append("│  └─ no Builder or Judge process running")
    ghosts = ghost_places(p)
    if ghosts:
        L.extend(fence_wrap("! %d items hold a place with no process: %s" % (len(ghosts), title(ghosts[0])), "│  ", "│    "))
    L.append("├─ ROLE RUNS  %d running  [%d proc]" % (len(roles), n_procs(roles)))
    for i, x in enumerate(roles):
        name = x["id"].rsplit("-", 1)[0].capitalize() if x["id"] else x["unit"]
        leaf("│  %s " % ("└─" if i == len(roles) - 1 else "├─"), name, "%6s %-4s" % (ago(x["age"]), x["model"][:4]), x["procs"])
    inproc = p.get("cond_helpers")
    inside = ", %s in-process" % ("UNMEASURED" if inproc is None else inproc) if cond else ""
    L.append("└─ CONDUCTOR WINDOW  %s, helpers %d detached%s  [%d proc]" % (ago(cond[0]["age"]) if cond else "not running", len(helpers), inside, n_procs(cond) + n_procs(helpers)))
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
    W, H = 1040, 332
    s = Svg(W, H, "SteveDesktop: state, machine stats, test jobs and live testing")
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
    extra = ("  incident level %s, normal none" % inc.get("level")) if inc.get("level") is not None else ""
    if since:
        since += ": " + ("high, normal not at all" if tone == BAD else (("high" if now - sv["since"] > 3600 else "ok") + ", normal under 1 h" if tone == WARN else "ok, normal any length"))
    s.reading_open("STATE")
    s.text(W - 28, 40, "%s%s" % (since, extra), 12, fg, "600", "end", MONO)
    s.reading_close()
    s.text(18, 73, clip(sv["reason"], 150) or "no reason recorded", 11.5, TEXT if tone != BAD else "#ffb4b0")

    good = cache.get("good") or {}
    good_age = now - cache["good_t"] if cache.get("good_t") else None

    def tile_(x, y, w, label, val, colour=TEXT, bar=None, note=None, note_colour=DIM, hover=None):
        tile(s, x, y, w, label, val, colour, bar, note, note_colour, hover)

    # ---- machine row
    y = 84
    routes = cache.get("routes") or {}
    s.reading_open("ROUTES")
    s.rect(14, y, 148, 62, CARD, None, 5)
    s.text(22, y + 53, "ok, normal all green" if all((cache.get("routes") or {}).get(k) for k in ("tailscale", "lan", "wsl")) else "low, normal all green", 9, DIM)
    s.text(22, y + 14, "ROUTES", 9.5, DIM, "700")
    for i, (k, lab) in enumerate((("tailscale", "tail"), ("lan", "LAN"), ("wsl", "wsl"))):
        v = routes.get(k)
        s.parts.append('<circle cx="%d" cy="%d" r="5" fill="%s"/>' % (28 + i * 46, y + 31, FAINT if v is None else (GOOD if v else BAD)))
        s.text(36 + i * 46, y + 35, lab, 10.5, TEXT if v else DIM)
    s.reading_close()
    cols = [(170, 92), (270, 96), (374, 132), (514, 100), (622, 124), (754, 180), (942, 84)]

    def num(k):
        return good.get(k) or ""

    up = num("up")
    up = up if re.fullmatch(r"\d+(\.\d+)?", up) else ""
    upv = float(up) if up else None
    tile_(cols[0][0], y, cols[0][1], "UPTIME", ago(upv).replace(" ", "") if up else "?", TEXT if up else WARN, None, *(uptime_note(upv) if upv is not None else (None, DIM)))
    load, cores = num("load"), num("cores")
    lnote = against(float(load), float(cores), "0-%s" % cores) if load and cores else (None, DIM)
    tile_(cols[1][0], y, cols[1][1], "LOAD/%s" % (cores or "CORES?"), load or "?", TEXT if load else WARN, None, lnote[0], lnote[1], "Processes wanting a CPU core. Below the core count means nothing is waiting.")
    ram = num("ram").split()
    if len(ram) == 2 and all(x.isdigit() for x in ram):
        frac = int(ram[0]) / max(int(ram[1]), 1)
        tile_(cols[2][0], y, cols[2][1], "WSL RAM USED", "%.1f/%.0f GB" % (int(ram[0]) / 1024, int(ram[1]) / 1024), TEXT, frac, *against(frac * 100, 85, "under 85%"))
    else:
        tile_(cols[2][0], y, cols[2][1], "WSL RAM USED", "?", WARN)
    cpu = good.get("cpu_pct")
    tile_(cols[3][0], y, cols[3][1], "CPU", "%d%%" % cpu if cpu is not None else "?", TEXT if cpu is not None else WARN, cpu / 100 if cpu is not None else None, *(against(cpu, 90, "0-90%") if cpu is not None else (None, DIM)))
    disk = num("disk").split()
    if disk:
        tile_(cols[4][0], y, cols[4][1], "DISK FREE", "%s GB" % disk[0], TEXT, None, *(("low, normal over 100 GB", WARN) if int(disk[0]) < 100 else ("ok, normal over 100 GB", DIM)))
    else:
        tile_(cols[4][0], y, cols[4][1], "DISK FREE", "?", WARN)
    gpu = [x.strip() for x in num("gpu").split(",")]
    if len(gpu) == 4 and all(x.isdigit() for x in gpu[1:]):     # "[N/A]" on some cards
        tile_(cols[5][0], y, cols[5][1], "GPU " + re.sub(r"NVIDIA |GeForce ", "", gpu[0]), "%s%%  %.1f/%.0f GB" % (gpu[1], int(gpu[2]) / 1024, int(gpu[3]) / 1024), TEXT, int(gpu[1]) / 100, *against(int(gpu[1]), 60, "0-60% with the game up"))
    else:
        tile_(cols[5][0], y, cols[5][1], "GPU", "?", WARN)
    gm = num("game")
    run_v, q_v = sv.get("running"), sv.get("pending")
    wasted = gm == "0" and bool(q_v or run_v)
    tile_(cols[6][0], y, cols[6][1], "GAME", ("up" if gm != "0" else "down") if gm else "?", (LIVE if gm != "0" else DIM) if gm else WARN, None, "bad, normal up" if wasted else ("ok, normal up" if gm else None), WARN if wasted else DIM, "Up is normal. Down is fine while no job waits; jobs waiting with the game down cannot run.")

    # ---- jobs row
    y = 154
    known = sv.get("jobs_known")
    n = lambda v: "?" if v is None else str(v)  # noqa: E731
    rv = (("low, normal 1", WARN) if run_v == 0 else (("high, normal 1", WARN) if run_v > 1 else ("ok, normal 1", DIM))) if run_v is not None else (None, DIM)
    tile_(14, y, 80, "RUNNING", n(run_v), BAD if idle else (LIVE if run_v else DIM), None, rv[0], rv[1])
    qn = against(q_v, 20, "0-20") if q_v is not None else (None, DIM)
    tile_(102, y, 96, "QUEUED", n(q_v), WARN if q_v and not run_v else TEXT, None, qn[0], qn[1])
    dn = versus(sv.get("done") or 0, sv.get("usual_done"), False, ROUGH["steve_done"]) if known else (None, DIM)
    tile_(206, y, 112, "DONE 24 H", n(sv.get("done")) if known else "?", TEXT if known else WARN, None, dn[0], dn[1])
    fl = sv.get("failed")
    fn = versus(fl or 0, sv.get("usual_failed"), True, ROUGH["steve_failed"]) if known else (None, DIM)
    tile_(326, y, 112, "FAILED 24 H", n(fl) if known else "?", (BAD if fl else DIM) if known else WARN, None, fn[0], fn[1])
    last = sv.get("last")
    if last and known:     # an unread result could be the newest job
        word = last["o"] + ("/" + last["c"] if last["c"] else "")
        tile_(446, y, 232, "LAST JOB, %s AGO" % ago(now - last["f"]).upper(), clip("%s %s" % (last["p"], word), 26), GOOD if last["o"] == "DONE" else BAD, None, *against(now - last["f"], 3600, "under 1 h while the lane runs"))
    else:
        tile_(446, y, 232, "LAST JOB", "none in 8 days" if known else "?", WARN, None, "low, normal under 1 h while the lane runs" if known else None, WARN)
    rn = versus(sv.get("rows_h") or 0, sv.get("usual_rows_h"), False, ROUGH["steve_rows_h"]) if known else (None, DIM)
    tile_(686, y, 110, "ROWS/HOUR 24 H", "%.0f" % sv["rows_h"] if known else "?", TEXT if known else WARN, None, rn[0], rn[1])
    age = sv["age"]
    if age is None:
        tile_(804, y, 102, "STEWARD WROTE", "?", WARN)
    else:
        tile_(804, y, 102, "STEWARD WROTE", ago(age) + " ago", BAD if age > 300 else TEXT, None, "high, normal <5 min" if age > 300 else "ok, normal <5 min", BAD if age > 300 else DIM)
    pa = "%s old" % ago(good_age) if good_age is not None else "never"
    stale = good_age is None or good_age > 900
    tile_(914, y, 112, "MACHINE READING", pa, WARN if cache.get("why") or stale else DIM, None, "high, normal <15 min" if stale else "ok, normal <15 min", WARN if stale else DIM)
    live_row(s, 248, sv.get("live"), "Busy: share of 24 h with a finished job running. A job still running counts once it ends.", "Jobs here that named an item, had PASS rows, and that item closed in 24 h", ROUGH["closed_steve"])
    return s.out()


def game_gb(mem):
    """tasklist's "1,291,932 K" -> "1.2 GB"; anything else as it came."""
    digits = re.sub(r"\D", "", mem or "")
    return "%.1f GB" % (int(digits) / 1048576) if digits else "memory not read"


def archmagi_svg(p):
    """This machine, drawn as SteveDesktop is, so the two panels read alike."""
    W, H = 1040, 202
    s = Svg(W, H, "Archmagi: game, machine stats and live testing")
    s.text(18, 28, "ARCHMAGI", 18, TEXT, "700")
    s.text(130, 28, p["game_text"], 14, p["game_colour"], "700", font=MONO)
    d = p["local"]
    y = 44
    if d:
        tile(s, 14, y, 110, "UPTIME", ago(d["up"]).replace(" ", ""), TEXT, None, *uptime_note(d["up"]))
        tile(s, 132, y, 110, "LOAD/%d" % d["cores"], "%.1f" % d["load"], TEXT, None, *against(d["load"], d["cores"] * 1.5, "0-%d" % (d["cores"] * 1.5)), "Processes wanting a CPU core. This machine runs fine a little above its core count.")
        frac = d["ram"][0] / max(d["ram"][1], 1)
        tile(s, 250, y, 170, "WSL RAM USED", "%.1f/%.0f GB" % (d["ram"][0] / 1024, d["ram"][1] / 1024), TEXT, frac, *against(frac * 100, 85, "under 85%"))
        tile(s, 428, y, 130, "EXT4 FREE", "%d GB" % d["disk"], TEXT, None, *(("low, normal over 100 GB", WARN) if d["disk"] < 100 else ("ok, normal over 100 GB", DIM)))
        tile(s, 566, y, 130, "D: FREE", "%d GB" % d["disk_d"], TEXT, None, *(("low, normal over 100 GB", WARN) if d["disk_d"] < 100 else ("ok, normal over 100 GB", DIM)))
    else:
        s.text(18, y + 30, "machine stats UNMEASURED: %s" % clip(p["local_why"], 90), 12, WARN, "700")
    w, live = p["win"], p["live_here"]
    gu = live.get("game_up") if live else None
    tile(s, 704, y, 322, "GAME THIS 24 H", "?" if not w else ("up, %s" % game_gb(w["game_mem"]) if w["game"] else "down"), TEXT if w else WARN, gu,
         None if gu is None else "%s, up %d%% of the minutes sampled; normal 60-100%%" % ("low" if gu < 0.6 else "ok", round(gu * 100)), DIM if gu is None or gu >= 0.6 else WARN)
    live_row(s, 130, live, "Busy: share of 24 h somebody held the bridge, from the ledger's bridge events (a hold silent for 45 min stops counting).", "Items closed in 24 h with a PASS proof row here", ROUGH["closed_here"])
    return s.out()


def steve_text(p):
    sv, cache = p["steve"], p["steve_cache"] or {}
    if not sv:
        return "STEVEDESKTOP  UNMEASURED (%s)" % p["steve_why"]
    g = cache.get("good") or {}
    said = lambda v: "UNMEASURED" if v is None else v  # noqa: E731
    return "\n".join([
        "STEVEDESKTOP  %s  jobs running %s, queued %s, done 24 h %s, failed 24 h %s" % (said(sv.get("state")), said(sv.get("running")), said(sv.get("pending")), sv.get("done") if sv.get("jobs_known") else "UNMEASURED", sv.get("failed") if sv.get("jobs_known") else "UNMEASURED"),
        "routes %s" % " ".join("%s:%s" % (k, "up" if v else "DOWN") for k, v in (cache.get("routes") or {}).items()),
        "load %s  ram %s  disk %s  gpu %s  game %s" % tuple(g.get(k, "UNMEASURED") for k in ("load", "ram", "disk", "gpu", "game")),
        live_text("live testing", sv.get("live")),
    ])


def live_text(name, d):
    if not d:
        return "%s UNMEASURED" % name
    busy = "UNMEASURED" if d.get("busy") is None else "%d%%" % round(d["busy"] * 100)
    r = d.get("rows") or {}
    return "%s 24 h: busy %s; proof rows %s; closed by a live proof %s; bugs found %s; falsified expectations not recorded" % (
        name, busy, " ".join("%s %d" % kv for kv in sorted(r.items())) or "none", "UNMEASURED" if d.get("closed") is None else d["closed"], d.get("bugs"))


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
            [("rm-relentless.timer", "every 2 min, own timer"), ("Supervisor", "no AI"), ("Builders", c("work") + ", private clones"), ("Judges", c("check") + ", never saw the work")],
            [("rm-artpiped", "art daemon"), ("codex_image.py", "one per render"), ("codex.exe", ("%d now on Windows" % p["win"]["codex"]) if p["win"] else "UNMEASURED")],
        ]),
        ("AN ALARM'S ROUTE", [
            [("Monitors, ops_watch", "ops_watch every 15 min"), ("Alarm or signal", "alarm files"), ("Dispatcher tick", "incident step"), ("Reader role", "named by its route"),
             ("Conductor", "next rung"), ("Fresh Operations", "next rung"), ("You", "last rung")],
        ]),
        ("AN ITEM'S LIFE", [
            [("Ledger item", "filed"), ("Queued", "enrolled"), ("Builder", "own clone"), ("Candidate", "a commit"), ("Judge", "PASS or FAIL"), ("Closing", "landed"), ("Done", "deadman rechecks")],
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
    chips.append(("bridge UNMEASURED", 1) if not b else (("bridge FREE", 0) if b["state"] == "FREE" else ("bridge HELD by %s%s" % (b["who"] or "?", silent_hold(b, p["now"])), -1)))
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


# --------------------------------------------------------------------------- the zero-token sections that replaced Fleet Watch
BOX = '<div style="background:%s;color:%s;border-radius:10px;padding:10px 16px;max-width:1040px;box-sizing:border-box;font-family:%s;font-size:13px;line-height:1.5">' % (BG, TEXT, SANS.replace("'", ""))
HEAD = '<div style="color:%s;font-size:11px;font-weight:700;letter-spacing:.04em;margin-bottom:4px">%%s</div>' % DIM
SMALL = '<span style="color:%s;font-size:11px">%%s</span>' % DIM
MARK_COLOUR = {"pass": GOOD, "fail": BAD, "done": WARN, "park": DIM, "open": LIVE}
# No <details> in these sections: in Typora a click on one marks the document modified (measured 2026-11-03), and a page
# with unsaved edits asks to save on close and is no longer simply replaced by the next minute's write.


def how_to_read(text):
    """One line under a panel. Plain words, on one line, because the page is read by a person learning the system."""
    return '<div style="max-width:1040px;color:%s;font-size:12px;margin:3px 2px 12px 2px"><b>How to read:</b> %s</div>' % (DIM, hesc(text))


def box(*parts):
    return BOX + "".join(parts) + "</div>"


def fleet_of(p):
    """The cached slow half, or None. A failed refresh keeps the last reading for FLEET_STALE, then it reads UNMEASURED:
    today's receipts and his Needs you list must not pass on yesterday's numbers."""
    f = p.get("fleet")
    if not isinstance(f, dict) or f.get("mods") is None or p["now"] - f.get("good_t", 0) > FLEET_STALE:
        return None
    return f


def needs_html(p):
    f = fleet_of(p)
    if not f:
        return box(HEAD % "NEEDS YOU", '<b style="color:%s">UNMEASURED</b> ' % WARN, hesc(clip(p.get("fleet_why") or "not read yet", 120)))
    n = f["needs"]
    rows = []
    for t in n.get("topics") or []:
        more = "".join("<div style='margin-left:18px;color:%s;font-size:12px'>also: %s</div>" % (DIM, hesc(clip(o, 120))) for o in t["others"])
        rows.append("<div>• %s %s%s</div>" % (hesc(clip(t["q"], 130)), SMALL % hesc(t["items"][0] if len(t["items"]) == 1 else "%s, %d items" % (t["topic"], len(t["items"]))), more))
    ans = n.get("answered") or []
    tail = ""
    if ans:
        tail = '<div style="color:%s;font-size:12px;margin-top:6px">%d more you already answered; the next move is ours: %s</div>' % (DIM, len(ans), hesc(", ".join(a["item"] for a in ans)))
    return box(HEAD % ("NEEDS YOU, %d" % n["count"]), "".join(rows) or "Nothing waits on you.", tail)


def events_html(p):
    """A static feed as of this refresh: the pipeline's acts, the Steve lane's finished jobs and the owner's notes."""
    now = p["now"]
    rows = event_rows(p)
    if not rows:
        return box(HEAD % "RECENT EVENTS", '<b style="color:%s">UNMEASURED</b>' % WARN)
    body = "".join('<div><span style="color:%s;font-family:%s">%s</span> <b>%s</b> %s</div>' % (DIM, MONO.replace("'", ""), time.strftime("%H:%M", time.localtime(at)), hesc(word), hesc(clip(txt, 110)))
                   for at, word, txt in rows[:18])
    return box(HEAD % ("RECENT EVENTS, AS OF THIS REFRESH, THE LAST %s" % ago(now - rows[min(17, len(rows) - 1)][0]).upper()), body)


def event_rows(p):
    """(epoch, what, about), newest first."""
    title = p["title"]
    thr, sv = p["throughput"], p["steve"]
    rows = []
    if thr:
        rows += [(at, word, title(item)) for at, word, item in thr["feed"]]
    if sv and sv.get("live"):
        rows += [(at, "Steve job %s" % o.lower(), " ".join(x for x in (m, pur) if x)) for at, o, pur, m in sv["live"]["jobs"]]
    rows += [(at, "your note", txt) for at, txt in p.get("owner_notes") or []]
    rows.sort(key=lambda r: -r[0])
    return rows


def receipts_html(p):
    f = fleet_of(p)
    # a reading from before midnight is not today's, however young
    if not f or time.localtime(f.get("good_t", 0))[:3] != time.localtime(p["now"])[:3]:
        return box(HEAD % "FINISHED TODAY", '<b style="color:%s">UNMEASURED</b>' % WARN)
    rows = f.get("receipts") or []

    def row(r):
        rc = r.get("receipt") or {}
        words = rc.get("outcome") or clip(r.get("title") or r["item"], 100)
        bits = [x for x in (r.get("where"), "check " + rc["check"] if rc.get("check") else "unchecked", "%d commits this week" % rc["commits"] if rc.get("commits") else "",
                            tokens(rc["tokens"]) if rc.get("tokens") else "") if x]
        return "<div>%s %s %s</div>" % (r.get("glyph") or "●", hesc(clip(words, 120)), SMALL % hesc(" · ".join(bits)))

    return box(HEAD % ("FINISHED TODAY, %d ITEMS" % len(rows)), "".join(row(r) for r in rows) or "Nothing yet today.")


def mods_html(p):
    f = fleet_of(p)
    if not f:
        return box(HEAD % "PROGRESS BY MOD", '<b style="color:%s">UNMEASURED</b>' % WARN)

    def task(t):
        note = " · ".join(x for x in (t.get("date"), t.get("note")) if x)
        return '<div><span style="color:%s">%s</span> %s %s</div>' % (MARK_COLOUR.get(t.get("kind"), DIM), t.get("mark") or "", hesc(clip(t.get("title") or "", 120)), SMALL % hesc(note) if note else "")

    out = []
    for m in f["mods"]:
        line = ["<b>%s</b>" % hesc(m["name"]), SMALL % hesc(" · ".join(x for x in (m.get("meta"), m.get("backlog")) if x))]
        inner = []
        for k in ("proof", "next"):
            if m.get(k):
                inner.append('<div style="color:%s;font-size:12px">%s%s</div>' % (DIM, "Next: " if k == "next" else "", hesc(clip(m[k], 130))))
        inner += ['<div style="color:%s;font-size:12px">%s</div>' % (WARN, hesc(clip(w, 130))) for w in m.get("waits") or []]
        inner += [task(t) for t in m.get("tasks") or []]
        if m.get("more"):
            inner.append(SMALL % ("and %d more" % m["more"]))
        out.append("<div style='margin-top:10px'>%s</div><div style='margin:2px 0 0 16px'>%s</div>" % (" ".join(line), "".join(inner)))
    return box(HEAD % ("PROGRESS BY MOD, %d MODS TOUCHED IN 7 DAYS, ✓ JUDGE PASSED · ✗ FAILED · ● UNCHECKED · ○ OPEN · ⏸ PARKED" % sum(1 for m in f["mods"] if not m.get("infra") and not m.get("cross"))), "".join(out))


# --------------------------------------------------------------------------- the three accounts' weekly fuel
def account_usage_module():
    """Imported late so that a broken account_usage.py costs this panel, not the page."""
    if HERE not in sys.path:
        sys.path.insert(0, HERE)
    import account_usage
    return account_usage


def fuel_series(text, truncated, au):
    """account -> [(epoch, pct used, reset epoch)], oldest first, MEASURED points only: an ESTIMATE only repeats an old figure."""
    lines = text.splitlines()
    out = {}
    for line in lines[1:] if truncated else lines:
        try:
            r = json.loads(line)
            t, pct = au.epoch(r["measured_at"]), r["week_pct_used"]
            if r["source"] == "MEASURED" and t is not None and isinstance(pct, (int, float)) and not isinstance(pct, bool):
                out.setdefault(r["account"], []).append((t, pct, au.epoch(r.get("week_resets_at"))))
        except (ValueError, KeyError, TypeError, AttributeError):
            continue        # a torn or foreign line says nothing about the rate
    for rows in out.values():
        rows.sort(key=lambda x: x[0])
    return out


def fuel_burn(samples, left, hours, measured, reset):
    """The burn rate against the spend left -> {burn, pace, span, verdict, ...}, or raises Unmeasured with the reason.

    burn: points per hour across the current window. pace: the points per hour that would use exactly what is left by the
    reset. AHEAD = burning faster than what is left can last; BEHIND = slower, so some goes unused; EQUAL = inside
    FUEL_EQUAL of the pace or inside the error of two whole-percent readings, which cannot be told apart."""
    if not samples:
        raise Unmeasured("no measured readings in the series")
    last = samples[-1]
    if measured is not None and measured - last[0] > account_usage_module().STALE_AFTER:
        raise Unmeasured("the series stopped %s before the reading" % ago(measured - last[0]))
    if last[2] is not None and reset is not None and abs(last[2] - reset) > 3600:
        raise Unmeasured("the series' newest reading is from another week")
    chain = [last]
    for s in reversed(samples[:-1]):
        if last[0] - s[0] > FUEL_FAR or s[1] > chain[-1][1] or (s[2] is not None and last[2] is not None and abs(s[2] - last[2]) > 3600):
            break       # too old, or a reset lies between them: usage only rises inside one week
        chain.append(s)
    near = [s for s in chain if last[0] - s[0] <= FUEL_NEAR][-1]
    start = near if last[1] - near[1] >= FUEL_NEAR_RISE and last[0] - near[0] >= FUEL_MIN_SPAN else chain[-1]
    span = last[0] - start[0]
    if span < FUEL_MIN_SPAN:
        raise Unmeasured("only %s of readings this week" % ago(span))
    hrs = span / 3600
    burn, pace = (last[1] - start[1]) / hrs, left / hours
    gap = burn - pace
    verdict = "EQUAL" if abs(gap) <= max(FUEL_EQUAL * pace, 1 / hrs) else ("AHEAD" if gap > 0 else "BEHIND")
    out = {"burn": burn, "pace": pace, "span": span, "verdict": verdict}
    if verdict == "AHEAD":
        out["out_in"] = left / burn
        out["early"] = hours - left / burn
    elif verdict == "BEHIND":
        out["unused"] = left - burn * hours
    return out


def fuel_row(name, d, series, series_why, now, au):
    """One account's reading. why set = UNMEASURED, every figure withheld; burn_why set = the week figures stand, the rate does not."""
    row = {"name": name, "why": None, "burn_why": None}
    if d is None:
        row["why"] = "no reading on file"
        return row
    left, hours, reset = d.get("week_pct_left"), d.get("hours_to_week_reset"), au.epoch(d.get("week_resets_at"))
    age = d.get("age_min")
    if d.get("source") not in ("MEASURED", "ESTIMATE"):
        row["why"] = clip(str(d.get("why") or "no measurement"), 80)
    elif d.get("stale"):
        row["why"] = "last poll %s ago" % ago(d["poll_age_min"] * 60)
    elif age is None or age * 60 > au.STALE_AFTER or age < -5:
        row["why"] = "no measurement time" if age is None else ("last measured %s ago" % ago(age * 60) if age > 0 else "measured in the future")
    elif not isinstance(left, (int, float)) or not 0 <= left <= 100:
        row["why"] = "no week figure in the reading" if left is None else "week figure out of range"
    elif reset is None or hours is None or reset <= now:
        row["why"] = "no week reset time, or the reset has passed"
    if row["why"]:
        return row
    exact = (reset - now) / 3600        # the 2-decimal hours_to_week_reset rounds to 0 in the last minute
    row.update(left=left, hours=exact, reset=reset, estimate=d["source"] == "ESTIMATE", age=age)
    if series_why:
        row["burn_why"] = "the series is unreadable (%s)" % clip(series_why, 60)
        return row
    got, why = guarded(fuel_burn, series.get(name) or [], left, exact, au.epoch(d.get("measured_at")), reset)
    if why:
        row["burn_why"] = why
    else:
        row.update(got)
    return row


def collect_fuel(env, now):
    """Every account's week from account_usage.py's own files. The registry says who should be here, so a missing account shows."""
    au = account_usage_module()
    lat = env.read_json(str(au.DATA_DIR / "latest.json"))
    recs = lat.get("accounts") if isinstance(lat, dict) else None
    if not isinstance(recs, dict):
        raise Unmeasured("latest.json holds no accounts")
    names, _ = guarded(env.account_names)
    names = list(names or []) + sorted(n for n in recs if n not in (names or []))
    if not names:
        raise Unmeasured("no account in the registry or latest.json")
    tail, series_why = guarded(env.read_tail, str(au.DATA_DIR / "series.jsonl"), FUEL_TAIL)
    series = fuel_series(tail[0], tail[1], au) if tail else {}
    rows = []
    for name in names:
        d, why = (None, None) if name not in recs else guarded(au.derive_record, recs[name], now)
        row, row_why = guarded(fuel_row, name, d, series, series_why, now, au) if not why else (None, why)
        rows.append(row or {"name": name, "why": "unreadable reading (%s)" % clip(row_why, 60), "burn_why": None})
    return rows


CLAUDE_ACCOUNT = "/home/mandrake/.local/bin/claude-account"


def collect_inuse(env):
    """Which account this machine uses RIGHT NOW, from `claude-account --json status` only (never from the fuel readings).
    -> {"live": name, "interrupted": bool}; raises Unmeasured with the reason. The email is dropped here, it never reaches the page."""
    try:
        rc, out = env.run([CLAUDE_ACCOUNT, "--json", "status"], timeout=10)
    except subprocess.TimeoutExpired:
        raise Unmeasured("claude-account timed out after 10 s")
    except FileNotFoundError:
        raise Unmeasured("claude-account not found")
    try:
        d = json.loads(out)
    except ValueError:
        raise Unmeasured("claude-account exited %s with no JSON" % rc)
    if rc != 0 or not isinstance(d, dict) or not d.get("ok"):
        raise Unmeasured("claude-account reports not ok")
    if not d.get("live"):
        raise Unmeasured("claude-account names no live account")
    return {"live": str(d["live"]), "interrupted": bool(d.get("interrupted_switch"))}


def inuse_text(p):
    """The one headline line, same words on the page and the phone."""
    lv = p.get("live")
    if not lv:
        return "IN USE NOW: UNMEASURED (%s)" % clip(p.get("live_why") or "not read", 90)
    return "IN USE NOW: %s%s" % (lv["live"], "  (ACCOUNT SWITCH INTERRUPTED)" if lv["interrupted"] else "")


def inuse_html(p):
    bad = not p.get("live") or p["live"]["interrupted"]
    return '<div style="font-size:20px;font-weight:800;color:%s;margin-bottom:6px">%s</div>' % (WARN if bad else GOOD, hesc(inuse_text(p)))


def is_inuse(p, name):
    return bool(p.get("live")) and p["live"]["live"] == name


FUEL_COLOUR = {"AHEAD": BAD, "EQUAL": GOOD, "BEHIND": LIVE}


def rate(x):
    return "%.2f points/h" % x


def fuel_left(r):
    """What is left, in the same words on the page and the phone."""
    return "%s%g%% left" % ("at most " if r["estimate"] else "", r["left"])


def fuel_verdict_words(r):
    """(verdict word, the rest of the sentence); the verdict is the word he reads, the rest is why."""
    head = "burning %s over %s; %s would last to the reset" % (rate(r["burn"]), ago(r["span"]), rate(r["pace"]))
    if r["verdict"] == "AHEAD":
        return "AHEAD", "%s: runs out in %s, %s before the reset" % (head, ago(r["out_in"] * 3600), ago(r["early"] * 3600))
    if r["verdict"] == "BEHIND":
        return "BEHIND", "%s: about %.0f%% unused at the reset" % (head, r["unused"])
    return "EQUAL", "%s: lasts to about the reset" % head


def fuel_html(p):
    rows = p["fuel"]
    if not rows:
        return box(HEAD % "ACCOUNTS, THIS WEEK", inuse_html(p) + '<b style="color:%s">UNMEASURED</b> ' % WARN, hesc(clip(p.get("fuel_why") or "not read", 120)))
    out = [inuse_html(p)]
    for r in rows:
        name = '<span style="display:inline-block;width:64px;font-weight:700">%s</span>' % hesc(r["name"])
        if is_inuse(p, r["name"]):
            name = '<span style="color:%s">&#9654; </span>' % GOOD + name + '<span style="background:%s;color:#fff;font-size:11px;font-weight:700;padding:1px 5px;border-radius:3px;margin-right:6px">IN USE</span>' % GOOD
        if r["why"]:
            out.append('<div>%s<b style="color:%s">UNMEASURED</b> %s</div>' % (name, WARN, SMALL % hesc(r["why"])))
            continue
        share = max(0.0, min(100.0, float(r["left"])))
        bar = '<span style="display:inline-block;width:100px;height:8px;background:%s;border-radius:2px;margin-right:8px"><span style="display:block;width:%dpx;height:8px;background:%s;border-radius:2px"></span></span>' % (EDGE, round(share), TEXT)
        figures = '<b style="font-size:15px">%s</b>, resets in <b>%s</b>' % (hesc(fuel_left(r)), ago(r["hours"] * 3600))
        if r["estimate"]:
            figures += " " + SMALL % ("estimate, measured %s ago" % ago(r["age"] * 60))
        if r["burn_why"]:
            burn = '<b style="color:%s">burn UNMEASURED</b> %s' % (WARN, SMALL % hesc(r["burn_why"]))
        else:
            word, rest = fuel_verdict_words(r)
            burn = '<b style="color:%s;font-size:15px">%s</b> %s' % (FUEL_COLOUR[word], word, SMALL % hesc(rest))
        out.append('<div style="margin-top:4px">%s%s%s</div><div style="margin-left:64px">%s</div>' % (name, bar, figures, burn))
    return box(HEAD % "ACCOUNTS, THIS WEEK", "".join(out))


def fuel_phone(p):
    rows = p["fuel"]
    if not rows:
        return [inuse_text(p), "ACCOUNTS UNMEASURED: %s" % clip(p.get("fuel_why") or "not read", 70)]
    out = [inuse_text(p), "ACCOUNTS, THIS WEEK"]
    for r in rows:
        mark = "> " if is_inuse(p, r["name"]) else ""
        if r["why"]:
            out.append("%s%s UNMEASURED: %s" % (mark, r["name"], clip(r["why"], 60)))
            continue
        line = "%s%s %s, resets in %s: " % (mark, r["name"], fuel_left(r), ago(r["hours"] * 3600))
        if r["burn_why"]:
            out.append(line + "burn UNMEASURED")
        elif r["verdict"] == "AHEAD":
            out.append(line + "AHEAD, out %s before reset" % ago(r["early"] * 3600))
        elif r["verdict"] == "BEHIND":
            out.append(line + "BEHIND, %.0f%% unused at reset" % r["unused"])
        else:
            out.append(line + "EQUAL")
    return out


def phone_copy(p, chips):
    """The same reading in a few plain lines (owner 2026-11-04): no model, no SVG; the Conductor sends it when he asks for status."""
    now, it, thr, f = p["now"], p["items"], p["throughput"], fleet_of(p)
    out = ["RimMandrake %s" % time.strftime("%H:%M %Z", time.localtime(now))]
    if p["pause"]:
        out.append("TOKEN PAUSE ON: " + PAUSE_WORDS)
    elif p["pause"] is None:
        out.append("TOKEN PAUSE UNMEASURED")
    out += [" · ".join(t for t, _ in chips), ""] + fuel_phone(p) + [""]
    if f:
        n = f["needs"]
        out.append("NEEDS YOU %d" % n["count"])
        out += ["- " + clip(t["q"], 70) for t in (n.get("topics") or [])[:5]]
        if len(n.get("topics") or []) > 5:
            out.append("- and %d more" % (len(n["topics"]) - 5))
    else:
        out.append("NEEDS YOU UNMEASURED")
    out += ["", "RELENTLESS PIPELINE"]
    if it:
        c = it["counts"]
        out.append("places %d of %s; breaker %s" % (it["live"], p["places"] or "UNMEASURED", breaker_word(p)))
        out.append("queued %d, building %d, waiting a Judge %d, judging %d, landing %d" % (c["queued"], c["running"], c["candidate"], c["checking"], c["closing"]))
        out.append("set aside: game %d, held %d, blocked %d" % (c["game"], c["held"], c["blocked"]))
    else:
        out.append("stages UNMEASURED")
    if thr:
        out.append("24 h: closed %d (%s), Judge fails %d" % (thr["closed"], versus(thr["closed"], thr["usual"].get("closed"), False)[0], thr["blind_fail"]))
    done_days = full_days(p["tokens"], now) if p["tokens"] else []
    if done_days:
        out.append("tokens per item closed (trial): %s" % tokens(done_days[0]["per"]))
    if p["accepted"]:
        out.append("mods accepted: %d of %d" % (p["accepted"]["green"], p["accepted"]["total"]))
    out += ["", "LIVE TESTING, 24 H"]

    def machine(name, d):
        if not d:
            return "%s UNMEASURED" % name
        busy = "UNMEASURED" if d.get("busy") is None else "%d%%" % round(d["busy"] * 100)
        r = d.get("rows") or {}
        return "%s: busy %s; PASS %d, FAIL %d, no answer %d; bugs %s" % (name, busy, r.get("PASS", 0), r.get("FAIL", 0), r.get("UNMEASURED", 0) + r.get("REFUSED", 0), d.get("bugs"))

    sv = p["steve"]
    out += [machine("Archmagi", p["live_here"]), machine("SteveDesktop", sv.get("live") if sv else None)]
    if sv:
        out.append("SteveDesktop %s" % (sv.get("state") or "UNMEASURED"))
    rows = event_rows(p)
    if rows:
        out += ["", "LATEST"] + ["%s %s: %s" % (time.strftime("%H:%M", time.localtime(at)), word, clip(txt, 60)) for at, word, txt in rows[:6]]
    return "\n".join(out) + "\n"


def mods_status_counts(text):
    """`modcheck status` lines -> counts by state. Its first word after the name is the state (a word stored in the file goes stale)."""
    c = collections.Counter()
    for line in text.splitlines():
        m = re.match(r"\S+\s+(GREEN|STALE|RED|DRAFT-CHECKLIST|NEVER)\b", line)
        if m:
            c[m.group(1)] += 1
    if not c:
        raise Unmeasured("modcheck status printed no mod line")
    return c


def refresh_fleet(env, save=True):
    """The slow half of the page, cached in FLEET_CACHE. A failed read keeps the last good one with its reason."""
    now = env.now()
    got, why = guarded(env.fleet_gather, now)
    try:
        old = env.read_json(FLEET_CACHE)
    except Exception:       # noqa: BLE001 - first run or torn cache
        old = {}
    if got is None:
        old.update({"t": now, "why": why})
        out = old
    else:
        out = dict(got, t=now, good_t=now, why=None)
    out.pop("accepted", None)       # an old count must not pass as "at today's code"
    raw, why_m = guarded(env.mods_status)
    if raw is not None:
        c, why_m = guarded(mods_status_counts, raw)
        if c is not None:
            total = out.get("total_mods") or sum(c.values())
            out["accepted"] = {"green": c["GREEN"], "stale": c["STALE"], "red": c["RED"], "draft": c["DRAFT-CHECKLIST"], "never": max(total - sum(c.values()) + c["NEVER"], 0), "total": total}
    out["accepted_why"] = why_m
    if save:
        env.write_atomic(FLEET_CACHE, json.dumps(out, ensure_ascii=False))
    return out


def collect_owner_notes(env, now):
    """His own recent words, from the tail of the ledger's OWNER shard (its older half is not this page's business)."""
    text, cut = env.read_tail(LEDGER_EVENTS + "/OWNER.jsonl", 512 * 1024)
    out = []
    for line in text.splitlines():
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if d.get("event") == "note" and d.get("text"):
            at = iso_epoch(d["ts"]) if isinstance(d.get("ts"), str) else None
            if at and now - at <= 172800:
                out.append((at, "%s: %s" % (d.get("id") or "", d["text"])))
    return out[-12:]


# --------------------------------------------------------------------------- timers and history (last, collapsed)
def timers_rows(timers, units, now):
    desc = {u["unit"]: u.get("description", "") for u in units or []}
    rows = []
    for t in sorted(timers or [], key=lambda x: x.get("unit", "")):
        name = t.get("unit", "").replace(".timer", "")
        last, nxt = t.get("last") or 0, t.get("next") or 0
        last_s = ago(now - last / 1e6) + " ago" if last else "never"
        nxt_s = "in " + ago(nxt / 1e6 - now) if nxt else "no next run"
        rows.append("%-24s %10s %12s  %s" % (clip(name, 24), last_s, nxt_s, clip(desc.get(t.get("unit"), ""), 34)))
    return rows


class UnreadHistory(list):
    """History that exists and could not be read: empty to the code that appends to it, UNMEASURED to the reader."""


def read_history(env):
    try:
        text = env.read_text(HIST)
    except FileNotFoundError:
        return []
    except OSError:
        return UnreadHistory()
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
    if isinstance(hist, UnreadHistory):
        return "last %s: UNMEASURED (the history file could not be read)" % label, None
    rows = [r for r in hist if now - r["t"] <= secs]
    if not rows:
        return "last %s: no history yet" % label, None
    span = now - min(r["t"] for r in rows)
    ns = [r["n"] for r in rows]
    note = "" if span >= secs * 0.95 else " (covers only %s, not yet a full %s)" % (ago(span), label)
    return ("last %s: processes min %d / median %d / max %d%s" % (label, min(ns), int(statistics.median(ns)), max(ns), note)), rows


# --------------------------------------------------------------------------- the page
def collect_pause(env):
    """The owner's token pause: True, False, or Unmeasured. Truth as relentless.owner_hold reads it: a missing key is off."""
    rules = env.relentless_rules()
    if not isinstance(rules, dict):
        raise Unmeasured("relentless rules are not an object")
    return bool(rules.get("only_system_and_live"))


def pause_banner(p):
    """Top of the page while the pause is on; one line saying so when it cannot be read; nothing while it is off."""
    if p["pause"]:
        return ['<div style="max-width:1040px;background:%s;color:#14171c;border-radius:6px;padding:6px 12px;font-weight:600"><b>TOKEN PAUSE ON</b>, by the owner: %s</div>' % (WARN, hesc(PAUSE_WORDS)), ""]
    if p["pause"] is None:
        return ["**Token pause UNMEASURED**: the Relentless rules file could not be read, so this page cannot say whether it is on.", ""]
    return []


def gather(env, state, hist=(), write=True):
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
    p["queue_next"], why = guarded(collect_queue_next, env, now)
    if why:
        p["unmeasured"].append("Relentless next in line (%s)" % why)
    staffing, why = guarded(collect_staffing, env)
    if why:
        p["unmeasured"].append("Relentless staffing (%s)" % why)
    p["pause"], why = guarded(collect_pause, env)
    if why:
        p["unmeasured"].append("token pause (%s)" % why)
    p["places"] = (staffing or {}).get("target")   # "places" in that file is what this tick allowed; target is the 8 he asks about
    p["checks"] = (staffing or {}).get("checks")
    sp = (staffing or {}).get("spent_today")
    # a staffing file from another UTC day holds that day's spend, not today's
    same_day = staffing and time.strftime("%Y%m%d", time.gmtime(staffing["t"])) == time.strftime("%Y%m%d", time.gmtime(now))
    p["spent_n"] = sp if same_day and isinstance(sp, (int, float)) else None
    p["spent"] = tokens(p["spent_n"]) if p["spent_n"] is not None else None
    p["tick"], why = guarded(collect_tick, env, state)
    if why:
        p["unmeasured"].append("Relentless tick (%s)" % why)
    p["breaker"], why = guarded(env.read_json, RELENTLESS_STORE + "/breaker.json")
    if why:
        p["unmeasured"].append("breaker (%s)" % why)
    p["throughput"], p["throughput_why"] = guarded(collect_throughput, env, now)
    if p["throughput_why"]:
        p["unmeasured"].append("24 h throughput (%s)" % p["throughput_why"])
    p["steve"], p["steve_why"] = guarded(collect_steve, env, state, p["items"])
    p["local"], p["local_why"] = guarded(env.local_stats)
    p["live_here"], why = guarded(collect_archmagi_live, env, now, p["items"], hist)
    if why:
        p["unmeasured"].append("live proof rows (%s)" % why)
    elif p["live_here"]["busy_why"]:
        p["unmeasured"].append("bridge history (%s)" % p["live_here"]["busy_why"])
    p["tokens"], why = (None, "no throughput") if not p["throughput"] else guarded(collect_tokens, env, now, p["throughput"])
    if why:
        p["unmeasured"].append("tokens per item (%s)" % why)
    p["live"], p["live_why"] = guarded(collect_inuse, env)
    if p["live_why"]:
        p["unmeasured"].append("account in use (%s)" % p["live_why"])
    p["fuel"], p["fuel_why"] = guarded(collect_fuel, env, now)
    if p["fuel_why"]:
        p["unmeasured"].append("account fuel (%s)" % p["fuel_why"])
    for r in p["fuel"] or []:
        if r["why"] or r["burn_why"]:
            p["unmeasured"].append("account %s %s(%s)" % (r["name"], "burn " if not r["why"] else "", r["why"] or r["burn_why"]))
    p["owner_notes"], _ = guarded(collect_owner_notes, env, now)
    p["fleet"], p["fleet_why"] = guarded(env.read_json, FLEET_CACHE)
    if not write and not fleet_of(p):       # --print on a machine with no fresh cache still draws the whole page
        p["fleet"], p["fleet_why"] = guarded(refresh_fleet, env, False)
    fl = fleet_of(p)
    if not fl:
        p["unmeasured"].append("mods, receipts and Needs you (%s)" % (p["fleet_why"] or "not read yet"))
    elif fl.get("why"):
        p["unmeasured"].append("mods, receipts and Needs you are %s old (%s)" % (ago(now - fl.get("good_t", 0)), clip(fl["why"], 80)))
    p["accepted"] = (p["fleet"] or {}).get("accepted")
    if p["accepted"] and now - (p["fleet"].get("t") or 0) > FLEET_STALE:      # refreshes stopped: no longer "at today's code"
        p["accepted"] = None
    if not p["accepted"]:
        p["unmeasured"].append("mods accepted (%s)" % ((p["fleet"] or {}).get("accepted_why") or "not read yet"))
    conductors = [x for x in p["tree"]["groups"].values() if is_conductor(x)] if p["tree"] else []
    p["cond_helpers"] = None
    if conductors and conductors[0].get("main_pid"):
        p["cond_helpers"], why = guarded(env.conductor_helpers, conductors[0]["main_pid"])
        if why:
            p["unmeasured"].append("Conductor's in-process helpers (%s)" % why)
    p["steve_cache"], _ = guarded(env.read_json, STEVE_CACHE)

    # who holds the live game: the bridge file first, then the game process
    b, w = p["bridge"], p["win"]
    if b and b["state"] == "HELD":
        silent = silent_hold(b, now)
        p["game_text"], p["game_colour"] = "held by %s%s" % (clip(b["who"] or "?", 16), silent), WARN if silent else LIVE
    elif b:
        p["game_text"], p["game_colour"] = ("free, game up" if w and w["game"] else ("free, game down" if w else "free")), GOOD
    else:
        p["game_text"], p["game_colour"] = "UNMEASURED", WARN

    p["game_idle"], p["game_idle_why"] = guarded(collect_game_idle, env, now, it_waiting(p["items"]))
    if p["game_idle_why"]:
        p["unmeasured"].append("game idle share (%s)" % p["game_idle_why"])

    # plain words: only for names the page shows
    want = set()
    it = p["items"]
    if it:
        for k in ("running", "checking", "candidate", "closing"):
            want.update(s.get("item") for s in it["by_status"][k])
    if p["queue_next"]:
        want.update(p["queue_next"]["free"][:NEXT_SHOWN] + p["queue_next"]["waiting"][:NEXT_SHOWN])
    if p["throughput"]:
        want.update(i for _, i in p["throughput"]["recent"])
        want.update(i for _, _, i in p["throughput"]["feed"])
    if it:
        for k in BELT + SIDE:
            old = oldest_in(it, k, now)
            if old:
                want.add(old[1])
    p["title"] = titles_for(env, state, want)
    return p


def build(env, state, hist, write=True):
    p = gather(env, state, hist, write)
    now = p["now"]
    strip, chips = status_strip(p)
    tree, roots = tree_lines(p)
    p["roots"] = roots

    head = [strip + ' <span style="color:#98a1af;font-size:85%%;white-space:nowrap">at %s, new every minute</span>' % time.strftime("%H:%M:%S %Z", time.localtime(now)), ""]
    head += pause_banner(p)
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

    # how many Judges may run above the ceiling comes from relentless.py admission(): a check takes extra=1
    S = [panel("Accounts", fuel_html),
         how_to_read("Each account's week: % left and time to its reset, from account_usage.py. The word compares the burn rate of the last 3 to 6 hours with the rate that would use exactly what is left by the reset. "
                     "AHEAD: burning faster than what is left can last, so it runs out early. EQUAL: about right, within 15% or within what whole-percent readings can tell apart. BEHIND: burning slower, so some goes unused. "
                     "A reading older than 45 minutes, or one that cannot be read, says UNMEASURED."), "",
         panel("Relentless Pipeline", pipeline_svg),
         how_to_read("Items move left to right; a card names its items whole, longest there first (hover a name for its plain words), and a stage too long for its card names them in a band below; queued shows the next few in the tick's order, done the latest few, each with a count of the rest. each worker is a Relentless-style Builder or Judge (MandrakeWorkflows), so workers can be swapped while the pipeline stays. "
                     "A place is one running Builder or Judge, or one being stopped; 8 is the ceiling for starting a Builder. A Judge may start one place above it, because "
                     "a cap never stops finishing work, and stopping runs still count, so 9 of 8 is normal and brief. The left bars count events, not items, and each says if it is usual for 24 h. "
                     "GAME UNMEASURED is game-phase events only; every proof row, measured or not, is in Live Testing below. Trends each have their own zero line. "
                     "Idle under LIVE GAME is minutes no proof ran in the last 3 h; the game idle trend is time nobody held the bridge, so a load counts as busy in the trend only."), "",
         # below the pipeline (owner 2026-11-04: the pipeline sat "after all those waiting for me notifications. That's dumb.")
         panel("Needs you", needs_html), "",
         panel("Archmagi", archmagi_svg),
         how_to_read("This machine and its live game. Each number has its verdict underneath; Busy means somebody held the bridge. A proof row that says UNMEASURED or REFUSED ran or was turned away and learned nothing."), "",
         panel("SteveDesktop", steve_svg),
         how_to_read("The second machine, which only runs test jobs from its queue. The bar under a number shows how full it is; Busy means a job was running. Two jobs in a row not DONE brake the lane, which then reads red here."), "",
         "```", "\n".join(tree), "```",
         how_to_read("Every process has one owner, read down from Dispatch: [n proc] counts a branch, and each line ends with what the processes are. "
                     "Under the Conductor, detached helpers are services and in-process helpers run inside the window with no process of their own."), "",
         panel("chains", chains_svg),
         how_to_read("Fixed routes, read from the code; only the live counts change. Follow an arrow to see who starts what, and where an item or alarm goes next."), "",
         panel("Recent events", events_html), "", panel("Finished today", receipts_html), "", panel("Progress by mod", mods_html),
         how_to_read("One block per mod worked on in the last week: what is next, what waits on you or the game, and one line per task that touched it. Refreshed every 5 minutes. Leave the page unclicked: a click inside a block marks it edited in Typora, and it may then stop refreshing."), ""]
    if p["unmeasured"]:
        head += ["**UNMEASURED this minute:** " + "; ".join(p["unmeasured"]), ""]

    n = p["tree"]["total"] if p["tree"] else None
    hist_lines = [window_stats(hist, now, secs, label)[0] for secs, label in ((86400, "24 h"), (604800, "7 d"))]
    if p["timers"] is None:
        tim = "timers UNMEASURED (%s)" % p["timers_why"]
    else:
        tim = "\n".join(["%d timers loaded" % len(p["timers"]), "%-24s %10s %12s  %s" % ("timer", "last ran", "next run", "what")] + timers_rows(p["timers"], p["units"], now))
    text = "\n".join(["-- the panels as plain text --", pipeline_text(p), "-- Archmagi --", live_text("live testing", p["live_here"]), "-- SteveDesktop --", steve_text(p), "-- chains --", chains_text(p),
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
    phone, why = guarded(phone_copy, p, chips)
    return page, sample, phone if phone is not None else "phone copy UNMEASURED: %s\n" % why


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
        page, sample, phone = build(env, state, hist, write)
    except Exception as e:      # noqa: BLE001 - leave the old page, remember why, fail loudly
        state["last_error"] = "%s: %s" % (type(e).__name__, str(e)[:160])
        state["fail_since"] = state.get("fail_since") or env.now()
        if write:
            env.write_atomic(STATE, json.dumps(state))
        print("running_now FAILED: %s" % state["last_error"], file=sys.stderr)
        return 1, ""
    if write:
        env.write_atomic(OUT, page)
        env.write_atomic(PHONE_OUT, phone)
        if isinstance(sample["n"], int):
            append_history(env, hist, sample)
        state["ok_t"] = env.now()
        state.pop("fail_since", None)
        state.pop("last_error", None)
        env.write_atomic(STATE, json.dumps(state))
        # last on purpose: the page is already on disk, so neither ssh nor a ledger replay can ever hold it back
        fleet, _ = guarded(env.read_json, FLEET_CACHE)
        if env.now() - ((fleet or {}).get("t") or 0) >= FLEET_EVERY:
            guarded(refresh_fleet, env)
            guarded(lambda: env.status_board())     # the owner's board (status_board.py) follows each fleet refresh
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
    if "--phone" in sys.argv:
        env_ = Env()
        try:
            state_ = env_.read_json(STATE)
        except Exception:       # noqa: BLE001 - first run or torn state
            state_ = {}
        print(build(env_, state_, read_history(env_), False)[2], end="")
        sys.exit(0)
    rc, page = run(write="--print" not in sys.argv)
    if "--print" in sys.argv:
        print(page)
    sys.exit(rc)
