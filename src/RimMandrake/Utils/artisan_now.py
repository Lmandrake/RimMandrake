#!/usr/bin/env python3
"""artisan_now.py: the Artisan loops' ops console, written once a minute with no model call.

The owner, 2026-11-07: "Please design a rich, robust ARTISAN_NOW.md file similar to RUNNING_NOW.md that
lets me know with zero token spend what all the Artisan agents are currently working on and any other
relevant information we can glean with determinstic python from their logs, activity, etc. It should not
take an LLM to regenerate the sheet, and the sheet should update every minute."

Writes D:\\ClaudeWork\\rimmandrake\\conductor\\ARTISAN_NOW.md and ARTISAN_NOW_PHONE.md beside the Relentless
sheet. Run by rm-artisan-now.timer (src/RimMandrake/Utils/systemd/).

    python3 artisan_now.py            build and write both sheets
    python3 artisan_now.py --print    build the page to stdout, write nothing
    python3 artisan_now.py --phone    build the phone copy to stdout, write nothing
    python3 artisan_now.py --check    print the page's age; exit 1 when older than 3 minutes

Read-only by rule: it never writes in a loop's clone, never calls the game's bridge, and calls no model.
Anything it cannot read says UNMEASURED with the reason; a figure from an earlier run says how old it is.
Stdlib only. Every subprocess has a timeout, and the machine reads share one deadline, so a dead ssh
cannot hold the page. Loops are discovered from systemd, the scratch clones and the log folders, so a new
loop shows up with no edit here.

The picture at the top (owner, 2026-11-07: "something graphical in HTML at its top so I can very quickly understand what's
happening") draws every pass on one clock, split by where its time went, read from the transcript the pass log names. A finished
pass is read once and kept in the state file; a live one is read from where it stopped. What it can't read, it hatches and names.

Tokens are the loops' own weighted count (ralph/tally.py): input + output + cache writes + cache reads / 10.
The running total is the last figure the loop's shell logged plus a tally of the live pass's log, read
incrementally: the pass logs run to hundreds of MB on a slow drive, and only the live one can have moved.
"""

import ast
import datetime as dt
import glob
import json
import os
import re
import statistics
import subprocess
import sys
import textwrap
import threading
import time
from collections import Counter
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.environ.get("ARTISAN_NOW_OUT", "/mnt/d/ClaudeWork/rimmandrake/conductor")
NATIVE_OUT = r"D:\ClaudeWork\rimmandrake\conductor"
LOG_ROOT = os.environ.get("ARTISAN_LOG_ROOT", "/mnt/d/ClaudeWork/rimmandrake")
CLONE_GLOB = os.environ.get("ARTISAN_CLONE_GLOB", "/home/mandrake/rm/scratch/*/ralph_*")
PROJECTS = os.environ.get("ARTISAN_PROJECTS", os.path.expanduser("~/.claude/projects"))
QHOME = os.environ.get("TESTQ_QUEUE", "/mnt/d/ClaudeWork/rimmandrake/testq")
ACCOUNTS = os.environ.get("ARTISAN_ACCOUNTS", "/mnt/d/ClaudeWork/rimmandrake/account_usage")
STEVE_SSH = os.environ.get("ARTISAN_STEVE_SSH", "mandrake@stevedesktop-wsl")
BRIDGE_FILES = ["/home/mandrake/rm/dispatch/infrastructure/state/BRIDGE",
                "/home/mandrake/rm/bench/infrastructure/state/BRIDGE"]
LEARNED = os.path.expanduser("~/.claude/skills/artisan/references/learned.md")

STALE_PAGE_S = 180
QUIET_STUCK_S = 45 * 60         # model running and nothing written for this long: stuck
NO_MODEL_STUCK_S = 5 * 60       # unit up, no model, not waiting for a game, for this long: stuck
TRANSCRIPT_TAIL = 1_500_000
MACHINE_DEADLINE_S = 18
SOFT_CONTEXT, FIRM_CONTEXT = 250_000, 350_000   # defaults; read from the loop's game_gate.py when it says
PASS_LIMIT_S = 6 * 3600                         # loop.sh wraps each pass in `timeout 6h`


# ---- small helpers ---------------------------------------------------------------------------------

class Unmeasured(Exception):
    """A value could not be read. The text is the reason, shown to the owner."""


def now_s():
    return time.time()


def clock(t):
    """A time on the owner's clock: 11:34 PST, with the date when it is not today."""
    if t is None:
        return "UNMEASURED"
    d = dt.datetime.fromtimestamp(t).astimezone()
    today = dt.datetime.fromtimestamp(now_s()).date()
    stamp = d.strftime("%H:%M")
    if d.date() != today:
        stamp = d.strftime("%b %-d ") + stamp
    return stamp + " " + (d.tzname() or "")


def ago(seconds):
    """A duration in the shortest plain form."""
    if seconds is None:
        return "UNMEASURED"
    s = max(0, int(seconds))
    if s < 90:
        return "%d s" % s
    if s < 90 * 60:
        return "%d min" % round(s / 60)
    if s < 48 * 3600:
        return "%.1f h" % (s / 3600)
    return "%.1f days" % (s / 86400)


def toks(n):
    if n is None:
        return "UNMEASURED"
    if n >= 1_000_000:
        return "%.2fM" % (n / 1_000_000)
    if n >= 1000:
        return "%dk" % round(n / 1000)
    return str(int(n))


def short(text, n=120):
    text = re.sub(r"\s+", " ", str(text or "")).strip()
    return text if len(text) <= n else text[: n - 1].rstrip() + "…"


def cell(text):
    """Text safe inside a Markdown table cell."""
    return str(text).replace("|", "\\|").replace("\n", " ")


def run(cmd, timeout=6, input_text=None, env=None):
    """(rc, stdout, stderr); raises Unmeasured on a timeout or a missing program."""
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, errors="replace", timeout=timeout,
                           input=input_text, env=env, stdin=None if input_text is not None else subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        raise Unmeasured("%s took over %d s" % (os.path.basename(cmd[0]), timeout))
    except OSError as e:
        raise Unmeasured("%s: %s" % (os.path.basename(cmd[0]), e.strerror or e))
    return p.returncode, p.stdout, p.stderr


def git(clone, *args, timeout=8):
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
    rc, out, err = run(["git", "-C", clone] + list(args), timeout=timeout, env=env)
    if rc:
        raise Unmeasured("git %s: %s" % (args[0], short(err, 100)))
    return out


def read_text(path, limit=200_000):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read(limit)


def read_tail(path, size):
    """The last `size` bytes, with the torn first line dropped when the read started mid-file."""
    with open(path, "rb") as f:
        f.seek(0, os.SEEK_END)
        end = f.tell()
        f.seek(max(0, end - size))
        raw = f.read()
    if end > size:
        cut = raw.find(b"\n")
        raw = raw[cut + 1:] if cut >= 0 else b""
    return raw.decode("utf-8", errors="replace")


def mtime(path):
    try:
        return os.path.getmtime(path)
    except OSError:
        return None


def write_atomic(path, text):
    tmp = "%s.tmp.%d" % (path, os.getpid())
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    # A Windows reader (Typora, a phone sync) can hold the target open for a moment.
    for attempt in range(4):
        try:
            os.replace(tmp, path)
            return
        except PermissionError:
            if attempt == 3:
                os.unlink(tmp)
                raise
            time.sleep(0.5)


def parse_iso(text):
    """Epoch seconds from an ISO stamp, or None."""
    if not text:
        return None
    try:
        return dt.datetime.fromisoformat(str(text).replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


class Sources:
    """Every source the page leaned on, with its age, for the table at the foot."""

    def __init__(self):
        self.rows = []

    def add(self, name, age=None, why=None):
        self.rows.append((name, age, why))

    def file(self, name, path):
        m = mtime(path)
        if m is None:
            self.rows.append((name, None, "missing: %s" % path))
        else:
            self.rows.append((name, now_s() - m, None))
        return m


# ---- saved state (a program's scratch, beside the sheet) ---------------------------------------------

def state_path():
    return os.path.join(OUT_DIR, "artisan_now_state.json")


def load_state():
    try:
        with open(state_path(), encoding="utf-8") as f:
            d = json.load(f)
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


# ---- token tally, same arithmetic as ralph/tally.py, read incrementally ---------------------------------

def weight(u):
    return (u.get("input_tokens", 0) + u.get("output_tokens", 0) + u.get("cache_creation_input_tokens", 0)
            + u.get("cache_read_input_tokens", 0) // 10)


def tally_file(path, cache):
    """Weighted tokens in one pass log; `cache` holds where the last read stopped, keyed by path."""
    size = os.path.getsize(path)
    c = cache.get(path)
    if not c or c.get("offset", 0) > size:
        c = {"offset": 0, "msgs": {}, "result": None}
    if c["offset"] < size:
        with open(path, "rb") as f:
            f.seek(c["offset"])
            raw = f.read()
        end = raw.rfind(b"\n")
        if end >= 0:
            for line in raw[:end].split(b"\n"):
                if b'"usage"' not in line:
                    continue
                try:
                    d = json.loads(line)
                except ValueError:
                    continue
                if d.get("type") == "result" and d.get("usage"):
                    c["result"] = weight(d["usage"])
                elif d.get("type") == "assistant":
                    m = d.get("message") or {}
                    if m.get("id") and m.get("usage"):
                        c["msgs"][m["id"]] = weight(m["usage"])
            c["offset"] += end + 1
    cache[path] = c
    return max(c["result"] or 0, sum(c["msgs"].values()))


# ---- events.log -----------------------------------------------------------------------------------

EVENT = re.compile(r"^(\d\d):(\d\d):(\d\d)(?: \S+)? (.*)$")
PASS_START = re.compile(r"^PASS (\d+) start, (\d+) tokens so far")
PASS_END = re.compile(r"^PASS (\d+) end, rc (-?\d+), (\d+) tokens, head (\S+)")
LOOP_START = re.compile(r"^LOOP start, (\d+) passes on record, (\d+) tokens")
ANY_TOKENS = re.compile(r"(\d{3,}) tokens")


def read_events(path):
    """[(epoch, text)] oldest first. The log has times and no dates, so the date is walked back from the
    file's own modified time, a day at each midnight crossed."""
    m = os.path.getmtime(path)
    rows = []
    for line in read_text(path, 2_000_000).splitlines():
        hit = EVENT.match(line.strip())
        if hit:
            rows.append((int(hit[1]), int(hit[2]), int(hit[3]), hit[4]))
    out = []
    day = dt.datetime.fromtimestamp(m).date()
    later = dt.datetime.fromtimestamp(m) + dt.timedelta(seconds=5)
    for h, mi, s, text in reversed(rows):
        when = dt.datetime.combine(day, dt.time(h, mi, s))
        while when > later:
            day -= dt.timedelta(days=1)
            when = dt.datetime.combine(day, dt.time(h, mi, s))
        out.append((when.timestamp(), text))
        later = when
    out.reverse()
    return out


def passes_from_events(events):
    """Pass rows from the shell's own lines. A pass with a start and no end, followed by a fresh LOOP start,
    is marked `lost`: its shell died under it."""
    rows, cur, total = [], None, None
    for t, text in events:
        hit = PASS_START.match(text)
        if hit:
            if cur:
                cur.update(lost=True, end=t, t_end=int(hit[2]))
            cur = {"n": int(hit[1]), "start": t, "t_start": int(hit[2]), "end": None, "rc": None,
                   "t_end": None, "head": None, "lost": False}
            rows.append(cur)
            total = int(hit[2])
            continue
        hit = PASS_END.match(text)
        if hit:
            if cur and cur["n"] == int(hit[1]):
                cur.update(end=t, rc=int(hit[2]), t_end=int(hit[3]), head=hit[4])
                cur = None
            total = int(hit[3])
            continue
        hit = LOOP_START.match(text)
        if hit:
            if cur:
                cur.update(lost=True, end=t, t_end=int(hit[2]))
                cur = None
            total = int(hit[2])
            continue
        hit = ANY_TOKENS.search(text)
        if hit:
            total = int(hit[1])
    return rows, cur, total


# ---- discovery ------------------------------------------------------------------------------------

UNIT_PROPS = ["Id", "LoadState", "WorkingDirectory", "ActiveState", "SubState", "ActiveEnterTimestampMonotonic",
              "InactiveEnterTimestampMonotonic", "MainPID", "Result", "ControlGroup", "ExecStart", "Environment"]


def boot_epoch():
    with open("/proc/stat") as f:
        for line in f:
            if line.startswith("btime"):
                return int(line.split()[1])
    raise Unmeasured("no btime in /proc/stat")


def uptime_now():
    with open("/proc/uptime") as f:
        return float(f.read().split()[0])


def list_units(sources):
    """The rm-* units that run a loop. Returns {unit name: properties}."""
    try:
        rc, out, err = run(["systemctl", "--user", "list-units", "--all", "--plain", "--no-legend",
                            "--type=service", "rm-*"], timeout=8)
        if rc:
            raise Unmeasured(short(err, 100))
        names = [ln.split()[0] for ln in out.splitlines() if ln.strip()]
        if not names:
            sources.add("systemd units", 0, None)
            return {}
        rc, out, err = run(["systemctl", "--user", "show", "-p", ",".join(UNIT_PROPS)] + names, timeout=8)
        if rc:
            raise Unmeasured(short(err, 100))
    except Unmeasured as e:
        sources.add("systemd units", None, str(e))
        raise
    sources.add("systemd units", 0, None)
    units = {}
    for block in out.split("\n\n"):
        props = {}
        for line in block.splitlines():
            k, _, v = line.partition("=")
            props[k] = v
        name = props.get("Id", "")
        if name.endswith(".service") and (name.startswith("rm-ralph-") or "ralph/loop.sh" in props.get("ExecStart", "")):
            units[name[: -len(".service")]] = props
    return units


def env_from_unit(props):
    out = {}
    for m in re.finditer(r"(\w+)=(\"[^\"]*\"|\S+)", props.get("Environment", "") or ""):
        out[m[1]] = m[2].strip('"')
    return out


def saved_unit_name(logs):
    """A loop's log folder keeps <unit>.service.saved so the unit can be restarted. Newest wins."""
    best = None
    for p in glob.glob(os.path.join(logs, "*.service.saved")):
        m = mtime(p)
        if m is not None and (best is None or m > best[0]):
            best = (m, os.path.basename(p)[: -len(".service.saved")])
    return best[1] if best else None


def discover(sources):
    """Every loop the machine knows of: from units, clones and log folders. Unit name and clone name differ
    (rm-ralph-gss-steve runs ralph_gss), so identity is the clone a unit runs in."""
    units_error = None
    try:
        units = list_units(sources)
    except Unmeasured as e:
        units, units_error = {}, str(e)
    loops, by_clone = {}, {}
    for clone in sorted(glob.glob(CLONE_GLOB)):
        if os.path.isfile(os.path.join(clone, "ralph", "loop.sh")):
            name = os.path.basename(clone).replace("ralph_", "", 1)
            base, n = name, 2
            while name in loops:        # two seats could each hold a ralph_x
                name, n = "%s-%d" % (base, n), n + 1
            loops[name] = {"name": name, "clone": clone, "logs": None, "unit": None, "props": None}
            by_clone[clone] = name
    for unit, props in sorted(units.items()):
        wd = props.get("WorkingDirectory", "")
        name = by_clone.get(wd)
        if name is None:
            if not unit.startswith("rm-ralph-"):
                continue    # a watcher that restarts a loop runs loop.sh in its command line; it is not a loop
            name = unit.replace("rm-ralph-", "", 1)
            loops.setdefault(name, {"name": name, "clone": wd or None, "logs": None, "unit": None, "props": None})
        rec = loops[name]
        # The live unit beats an ended one of the same clone.
        if rec["props"] is None or props.get("ActiveState") == "active":
            rec.update(unit=unit, props=props)
    for rec in loops.values():
        env = env_from_unit(rec["props"]) if rec["props"] else {}
        rec["env"] = env
        rec["logs"] = env.get("LOGS") or logs_from_loop_sh(rec) or os.path.join(LOG_ROOT, "ralph_" + rec["name"])
        if not rec["unit"]:
            rec["unit_saved"] = saved_unit_name(rec["logs"])
    seen_logs = {os.path.realpath(r["logs"]) for r in loops.values()}
    old = []
    for d in sorted(glob.glob(os.path.join(LOG_ROOT, "ralph*"))):
        if os.path.isdir(d) and os.path.realpath(d) not in seen_logs and os.path.exists(os.path.join(d, "events.log")):
            old.append(d)
    return list(loops.values()), old, units_error


def logs_from_loop_sh(rec):
    if not rec.get("clone"):
        return None
    try:
        m = re.search(r"^LOGS=\$?\{?(?:LOGS:-)?[\"']?([^\"'}\s]+)", read_text(os.path.join(rec["clone"], "ralph", "loop.sh")),
                      re.M)
    except OSError:
        return None
    return m[1] if m and m[1].startswith("/") else None


# ---- what a loop is doing: its transcript and its processes -------------------------------------------

def project_dir(clone):
    return os.path.join(PROJECTS, re.sub(r"[^A-Za-z0-9-]", "-", clone))


SHELL_WRAP = re.compile(r"&& eval (?:'(.*?)'|\"(.*?)\"|(.*?))(?: < /dev/null)? && pwd -P", re.S)


def clean_command(cmd):
    """The command a person typed, out of the tool's shell wrapper."""
    m = SHELL_WRAP.search(cmd)
    if m:
        cmd = m[1] or m[2] or m[3] or cmd
    return re.sub(r"\s+", " ", cmd).strip()


def plain_tool(name, inp):
    """One short line in plain words for a tool call."""
    inp = inp or {}
    fname = os.path.basename(str(inp.get("file_path") or inp.get("path") or ""))
    if name == "Bash":
        return "ran: " + short(inp.get("description") or clean_command(str(inp.get("command", ""))), 100)
    if name == "Read":
        return "read " + (fname or "a file")
    if name in ("Edit", "Write", "NotebookEdit"):
        return "%s %s" % ("edited" if name != "Write" else "wrote", fname or "a file")
    if name == "Grep":
        return "searched for: " + short(inp.get("pattern"), 60)
    if name == "Glob":
        return "listed files: " + short(inp.get("pattern"), 60)
    if name in ("Agent", "Task"):
        return "started a helper: " + short(inp.get("description") or inp.get("prompt"), 80)
    if name == "Skill":
        return "loaded skill " + short(inp.get("skill"), 40)
    if name == "ToolSearch":
        return "looked up a tool"
    if name == "TodoWrite":
        return "updated its to-do list"
    return "used " + name


def read_transcript(clone, sources, label, cache):
    """What the newest session of this clone shows: last tools, last words, files, context, errors, helpers."""
    pdir = project_dir(clone)
    if not os.path.isdir(pdir):
        raise Unmeasured("no transcript folder %s" % pdir)
    files = [(mtime(p) or 0, p) for p in glob.glob(os.path.join(pdir, "*.jsonl"))]
    if not files:
        raise Unmeasured("no transcript in %s" % pdir)
    last_m, path = max(files)
    sources.add("transcript, %s" % label, now_s() - last_m, None)
    out = {"path": path, "mtime": last_m, "tools": [], "said": None, "said_t": None, "files": Counter(),
           "context": None, "errors": [], "bash": [], "helpers": [], "helper_tokens": 0, "helper_count": 0}
    pending = {}
    for line in read_tail(path, TRANSCRIPT_TAIL).splitlines():
        try:
            d = json.loads(line)
        except ValueError:
            continue
        kind = d.get("type")
        if kind not in ("assistant", "user") or d.get("isSidechain"):
            continue
        t = parse_iso(d.get("timestamp"))
        msg = d.get("message") or {}
        usage = msg.get("usage")
        if kind == "assistant" and usage:
            out["context"] = (usage.get("input_tokens", 0) + usage.get("cache_creation_input_tokens", 0)
                              + usage.get("cache_read_input_tokens", 0))
        content = msg.get("content")
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict):
                continue
            b = block.get("type")
            if b == "tool_use":
                name, inp = block.get("name"), block.get("input") or {}
                row = {"t": t, "line": plain_tool(name, inp), "name": name,
                       "cmd": clean_command(str(inp.get("command", ""))) if name == "Bash" else ""}
                out["tools"].append(row)
                pending[block.get("id")] = row
                if name in ("Edit", "Write", "NotebookEdit") and inp.get("file_path"):
                    out["files"][str(inp["file_path"])] += 1
                if name == "Bash":
                    out["bash"].append(clean_command(str(inp.get("command", ""))))
            elif b == "text" and kind == "assistant" and (block.get("text") or "").strip():
                out["said"], out["said_t"] = block["text"].strip(), t
            elif b == "tool_result" and block.get("is_error"):
                body = block.get("content")
                if isinstance(body, list):
                    body = " ".join(x.get("text", "") for x in body if isinstance(x, dict))
                out["errors"].append(short(body, 140))
                row = pending.get(block.get("tool_use_id"))
                if row:
                    row["failed"] = True
    sub = os.path.join(path[: -len(".jsonl")], "subagents")
    for p in glob.glob(os.path.join(sub, "agent-*.jsonl")):
        out["helper_count"] += 1
        try:
            out["helper_tokens"] += tally_file(p, cache)
        except OSError:
            continue
        m = mtime(p) or 0
        if now_s() - m < 600:
            meta = {}
            try:
                meta = json.loads(read_text(p[: -len(".jsonl")] + ".meta.json"))
            except (OSError, ValueError):
                pass
            if not meta.get("finished"):
                out["helpers"].append({"what": short(meta.get("description") or meta.get("agentType") or "helper", 80),
                                       "quiet": now_s() - m})
        out["helper_last"] = max(out.get("helper_last", 0), m)
    return out


NOISE_CMD = re.compile(r"^(\S*/)?(claude|node|timeout|sleep|tail|head|cat|tee|cut|grep|sed|awk|wc|sort|uniq|tr|xargs)(\s|$)"
                       r"|ralph/loop\.sh|shell-snapshots/[^ ]*\s*$|game_gate\.py|\bmcp\b|^-?z?sh$|^/bin/(ba|z)?sh$")


def cgroup_processes(props):
    """(model_alive, [{cmd, age}]) for the unit's live processes, oldest command first."""
    cg = (props or {}).get("ControlGroup") or ""
    if not cg:
        return False, []
    root = "/sys/fs/cgroup" + cg
    if not os.path.isdir(root):
        return False, []
    pids = []
    for d, _, names in os.walk(root):
        if "cgroup.procs" in names:
            try:
                pids += [int(x) for x in read_text(os.path.join(d, "cgroup.procs")).split()]
            except OSError:
                pass
    hz = os.sysconf("SC_CLK_TCK")
    up = uptime_now()
    model, rows, seen = False, [], set()
    for pid in pids:
        try:
            raw = open("/proc/%d/cmdline" % pid, "rb").read(4000)
            stat = read_text("/proc/%d/stat" % pid)
        except OSError:
            continue
        parts = [x.decode("utf-8", "replace") for x in raw.split(b"\0") if x]
        if not parts:
            continue
        if os.path.basename(parts[0]) == "claude" or (len(parts) > 1 and os.path.basename(parts[1]) == "claude"):
            model = True
            continue
        cmd = re.sub(r"^cd \S+\s*(;|&&)\s*", "", clean_command(" ".join(parts)))
        if NOISE_CMD.search(cmd):
            continue
        start = int(stat.rsplit(")", 1)[1].split()[19]) / hz
        key = cmd[:80]
        if key not in seen:
            seen.add(key)
            rows.append({"cmd": cmd, "age": max(0, up - start)})
    rows.sort(key=lambda r: -r["age"])
    return model, rows


# ---- the loop's files -----------------------------------------------------------------------------

COUNT_LINE = re.compile(r"^\s*[-*]\s+(.+?)\s*[:=—-]+\s*\**(true|false|unseen)\b\**(.*)$", re.I)


def parse_progress(text):
    """The opening state of PROGRESS.md and its running count: `- bar: true|false|unseen` lines."""
    counts, rows = Counter(), []
    for line in text.splitlines():
        m = COUNT_LINE.match(line)
        if m:
            counts[m[2].lower()] += 1
            rows.append((short(m[1].strip("`* "), 70), m[2].lower(), short(m[3].strip(" .,:;—-()"), 90)))
    head = []
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#") or COUNT_LINE.match(line):
            if head and not s:
                break
            continue
        head.append(s)
        if sum(len(x) for x in head) > 500:
            break
    return {"state": short(" ".join(head), 520), "counts": counts, "rows": rows}


def parse_north_star(clone):
    """state, must-show and cannot-show counts from the mod's validation walk, named in PROMPT.md."""
    prompt = read_text(os.path.join(clone, "ralph", "PROMPT.md"))
    m = re.search(r"design/validation_walks/RimMandrake/([A-Za-z0-9_]+)", prompt)
    if not m:
        raise Unmeasured("PROMPT.md names no validation walk")
    rel = "design/validation_walks/RimMandrake/%s.md" % m[1]
    path = os.path.join(clone, rel)
    if not os.path.exists(path):
        raise Unmeasured("%s is not in this clone" % rel)
    text = read_text(path, 1_000_000)
    i = text.find("## north star")
    if i < 0:
        raise Unmeasured("%s has no north star section" % rel)
    sec = text[i:]
    st = re.search(r"^state:\s*(\S+)", sec, re.M)
    must = sec.find("### must show")
    cannot = sec.find("### cannot show")
    box = re.compile(r"^\s*- \[[ xX]\]", re.M)
    return {"mod": m[1], "state": st[1] if st else "no state line",
            "must": len(box.findall(sec[must:cannot if cannot > must else None])) if must >= 0 else 0,
            "cannot": len(box.findall(sec[cannot:])) if cannot >= 0 else 0}


def parse_questions(text):
    """Sections of QUESTIONS.md. Those that say no answer is needed are marked as notes."""
    body = re.sub(r"^#\s.*$", "", text, count=1, flags=re.M).strip()
    if not body:
        return []
    parts = re.split(r"(?m)^(?=##\s)", body)
    if len(parts) == 1:
        parts = re.split(r"\n\s*\n(?=\*\*)", body)
    out = []
    for p in parts:
        p = p.strip()
        if p:
            fyi = bool(re.search(r"no answer (is )?needed|needs an answer from you unless|nothing (is )?needed from you|for your information", p, re.I))
            title = re.sub(r"^#+\s*", "", p.splitlines()[0]).strip("* ")
            out.append({"title": short(title, 110), "text": p, "fyi": fyi})
    return out


VERDICT_ROW = re.compile(r"(?m)^\|\s*`([\w-]+)`\s*\|\s*\**(TRUE|FALSE|CANNOT TELL)[^|]*\|", re.I)


def parse_verdict(path):
    """A blind judge's counts, the lines it would not pass, and its overall yes or no."""
    text = read_text(path, 400_000)
    counts = re.search(r"(?:Counts?|Tally):?\**:?\s*([^\n*]{5,90})", text)
    call = re.search(r"(?im)^#+\s*\d*\.?\s*overall(?: call)?\s*\n+(.+)", text) or re.search(r"(?i)\*\*overall call:\s*(.+?)\*\*", text)
    rows = {m[1]: m[2].upper() for m in VERDICT_ROW.finditer(text)}
    answer = re.match(r"\W*(no|yes)\b", call[1], re.I) if call else None
    return {"counts": short(counts[1], 90) if counts else None, "call": short(call[1], 220) if call else None,
            "lines": len(rows), "passed": sum(1 for v in rows.values() if v == "TRUE"),
            "short": sorted(k for k, v in rows.items() if v != "TRUE"), "answer": answer[1].lower() if answer else None}


def gate_info(clone):
    """The game regex, the queue list and the context ceilings out of ralph/game_gate.py, without running it."""
    out = {"ahead": [], "game": None, "soft": SOFT_CONTEXT, "firm": FIRM_CONTEXT}
    try:
        tree = ast.parse(read_text(os.path.join(clone, "ralph", "game_gate.py")))
    except (OSError, SyntaxError):
        return out
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
            nm = node.targets[0].id
            try:
                if nm == "AHEAD":
                    out["ahead"] = list(ast.literal_eval(node.value))
                elif nm == "GAME" and isinstance(node.value, ast.Call) and node.value.args:
                    out["game"] = re.compile(ast.literal_eval(node.value.args[0]))
                elif nm in ("SOFT", "HARD", "FIRM") and isinstance(ast.literal_eval(node.value), int):
                    out["soft" if nm == "SOFT" else "firm"] = ast.literal_eval(node.value)
            except (ValueError, re.error, SyntaxError):
                pass
    return out


def loop_sh_info(clone):
    text = read_text(os.path.join(clone, "ralph", "loop.sh"))
    out = {"review_at": None, "offline_at": None, "busy_units": [], "stop_no_commit": "no commit" in text.lower()}
    m = re.search(r"REVIEW_AT=\$\{REVIEW_AT:-(\d+)\}", text)
    out["review_at"] = int(m[1]) if m else None
    m = re.search(r"OFFLINE_AT=\$\{OFFLINE_AT:-(\d+)\}", text)
    out["offline_at"] = int(m[1]) if m else None
    m = re.search(r"game_busy\s*\(\)\s*\{(.*?)^\}", text, re.S | re.M)
    if m:
        out["busy_units"] = sorted(set(re.findall(r"rm-[\w-]+", m[1])))
        out["busy_steve"] = "steve.sh" in m[1]
    return out


def commits_of(clone):
    rows = []
    for line in git(clone, "log", "-n", "200", "--format=%h %ct %s").splitlines():
        p = line.split(" ", 2)
        if len(p) == 3 and p[1].isdigit():
            rows.append({"sha": p[0], "t": int(p[1]), "subject": p[2]})
    return rows


def pushed_state(clone):
    branch = git(clone, "rev-parse", "--abbrev-ref", "HEAD").strip()
    ref = "refs/remotes/origin/" + branch
    if git(clone, "for-each-ref", "--count=1", "--format=%(refname)", ref).strip() != ref:
        return branch, None
    return branch, int(git(clone, "rev-list", "--count", "%s..HEAD" % ref).strip())


def read_note(path):
    m = mtime(path)
    if m is None:
        return None
    try:
        return {"t": m, "first": short(read_text(path, 2000), 140)}
    except OSError as e:
        return {"t": m, "first": "UNMEASURED: %s" % e}


def read_stop_reason(path):
    """A STOP file's first line says why it was set. Empty means nobody said."""
    try:
        for line in read_text(path, 2000).splitlines():
            if line.strip():
                return short(line, 140)
    except OSError:
        pass
    return None


def collect_loop(rec, sources, cache):
    """Everything measurable about one loop. A part that fails records its reason in rec['unmeasured']."""
    name, clone, logs = rec["name"], rec.get("clone"), rec["logs"]
    un = rec["unmeasured"] = {}
    rec["warnings"] = []
    ev_path = os.path.join(logs, "events.log")
    rec["events"], rec["passes"], rec["open_pass"], rec["total_logged"] = [], [], None, None
    try:
        sources.file("events log, %s" % name, ev_path)
        rec["events"] = read_events(ev_path)
        rec["events_mtime"] = mtime(ev_path)
        rec["passes"], rec["open_pass"], rec["total_logged"] = passes_from_events(rec["events"])
    except OSError as e:
        un["events"] = "cannot read %s: %s" % (ev_path, e.strerror or e)
    has_ralph = bool(clone) and os.path.isdir(os.path.join(clone, "ralph"))
    rdir = os.path.join(clone, "ralph") if has_ralph else None
    if not has_ralph:
        un["clone"] = "no clone with ralph/ at %s" % clone

    rec["model"], rec["procs"] = cgroup_processes(rec.get("props"))
    rec["stop_file"] = mtime(os.path.join(logs, "STOP"))
    rec["stop_reason"] = read_stop_reason(os.path.join(logs, "STOP"))
    rec["done"] = read_note(os.path.join(rdir, "DONE.md")) if rdir else None
    rec["need_game"] = mtime(os.path.join(rdir, "NEED_GAME")) if rdir else None
    rec["note_pending"] = read_note(os.path.join(rdir, "OWNER_NOTE")) if rdir else None
    rec["note_delivered"] = read_note(os.path.join(rdir, "OWNER_NOTE.delivered")) if rdir else None

    rec["loopsh"], rec["gate"] = {"review_at": None, "offline_at": None, "busy_units": []}, {"ahead": [], "game": None,
                                                                                            "soft": SOFT_CONTEXT, "firm": FIRM_CONTEXT}
    if rdir:
        try:
            rec["loopsh"] = loop_sh_info(clone)
        except OSError as e:
            un["loop.sh"] = str(e)
        rec["gate"] = gate_info(clone)
    env = rec.get("env") or {}
    rec["limit"] = int(env["REVIEW_AT"]) if env.get("REVIEW_AT", "").isdigit() else rec["loopsh"].get("review_at")
    rec["offline"] = int(env["OFFLINE_AT"]) if env.get("OFFLINE_AT", "").isdigit() else rec["loopsh"].get("offline_at")
    rec["machine"] = "SteveDesktop" if rdir and os.path.exists(os.path.join(rdir, "steve.sh")) else "Archmagi"

    # mod and goal: PROMPT.md's first plain paragraph is the frozen statement's lead.
    rec["goal"], rec["mod"] = None, None
    if rdir:
        try:
            text = read_text(os.path.join(rdir, "PROMPT.md"))
            sources.file("prompt, %s" % name, os.path.join(rdir, "PROMPT.md"))
            for para in re.split(r"\n\s*\n", text):
                p = para.strip()
                if p and not p.startswith("#"):
                    rec["goal"] = short(p, 320)
                    break
        except OSError as e:
            un["goal"] = "PROMPT.md: %s" % (e.strerror or e)

    # tokens: the shell's last logged figure, plus the live pass's log when one is open.
    rec["total"], rec["live_tokens"] = rec["total_logged"], None
    op = rec["open_pass"]
    if op:
        path = os.path.join(logs, "pass_%03d.jsonl" % op["n"])
        try:
            rec["live_tokens"] = tally_file(path, cache)
            rec["total"] = op["t_start"] + rec["live_tokens"]
            sources.file("live pass log, %s" % name, path)
            rec["pass_log_mtime"] = mtime(path)
        except OSError as e:
            un["live tokens"] = "pass %d log: %s" % (op["n"], e.strerror or e)
            sources.add("live pass log, %s" % name, None, "missing: %s" % path)
            rec["total"] = None
    err = os.path.join(logs, "pass_%03d.jsonl.err" % (op["n"] if op else (rec["passes"][-1]["n"] if rec["passes"] else 0)))
    try:
        rec["err_size"] = os.path.getsize(err)
    except OSError:
        rec["err_size"] = None

    # git
    rec["commits"], rec["branch"], rec["unpushed"], rec["dirty"] = [], None, None, None
    if rdir:
        try:
            rec["commits"] = commits_of(clone)
            rec["branch"], rec["unpushed"] = pushed_state(clone)
            rec["dirty"] = len(git(clone, "status", "--porcelain", "--untracked-files=no").splitlines())
            sources.add("git, %s" % name, 0, None)
        except Unmeasured as e:
            un["git"] = str(e)
            sources.add("git, %s" % name, None, str(e))
    for p in rec["passes"]:
        end = p["end"] or now_s()
        p["commits"] = sum(1 for c in rec["commits"] if p["start"] <= c["t"] <= end) if not un.get("git") else None

    # transcript
    rec["tx"] = None
    if clone:
        try:
            rec["tx"] = read_transcript(clone, sources, name, cache)
        except (Unmeasured, OSError) as e:
            un["transcript"] = str(e)
            sources.add("transcript, %s" % name, None, str(e))

    # the loop's notes
    for key, fname in (("progress", "PROGRESS.md"), ("questions", "QUESTIONS.md"), ("look", "LOOK.md")):
        rec[key] = None
        rec[key + "_t"] = None
        if rdir:
            path = os.path.join(rdir, fname)
            m = mtime(path)
            if m is None:
                # A loop with no questions or look yet is ordinary; a loop with no progress file is not.
                if key == "progress":
                    un["progress"] = "no %s" % path
                    sources.add("progress, %s" % name, None, "missing: %s" % path)
                continue
            rec[key + "_t"] = m
            if key == "progress":
                sources.add("progress, %s" % name, now_s() - m, None)
            try:
                rec[key] = read_text(path)
            except OSError as e:
                un[key] = str(e)
    rec["prog"] = parse_progress(rec["progress"]) if rec["progress"] else None
    rec["qs"] = parse_questions(rec["questions"]) if rec["questions"] else []
    rec["ns"] = None
    if rdir:
        try:
            rec["ns"] = parse_north_star(clone)
        except (Unmeasured, OSError) as e:
            un["north star"] = str(e)

    # judge verdicts and past claims
    rec["verdicts"] = []
    for p in sorted(glob.glob(os.path.join(logs, "blind_judge_verdict*.md")), key=lambda x: mtime(x) or 0):
        try:
            rec["verdicts"].append(dict(parse_verdict(p), file=os.path.basename(p), t=mtime(p)))
        except OSError as e:
            un["verdict"] = str(e)
    rec["claims"] = sorted(glob.glob(os.path.join(rdir, "history", "DONE_pass*.md"))) if rdir else []
    rec["shots"] = None
    sdir = os.path.join(logs, "shots")
    if os.path.isdir(sdir):
        try:
            with os.scandir(sdir) as it:
                ms = [e.stat().st_mtime for e in it if e.is_file()]
            rec["shots"] = {"n": len(ms), "t": max(ms) if ms else None}
        except OSError:
            pass

    rec["last_active"] = max([x for x in (rec.get("pass_log_mtime"), rec["tx"]["mtime"] if rec["tx"] else None,
                                          rec["tx"].get("helper_last") if rec["tx"] else None,
                                          rec.get("events_mtime")) if x] or [0]) or None
    rec["state"], rec["state_why"] = classify(rec)
    warn_about(rec)
    return rec


def classify(rec):
    """One word, and why. Order: what the shell last said, then what the unit and processes say now."""
    props = rec.get("props") or {}
    active = props.get("ActiveState") == "active"
    failed = props.get("ActiveState") == "failed" or props.get("Result", "success") not in ("success", "")
    last = rec["events"][-1] if rec["events"] else None
    text = last[1] if last else ""
    t = last[0] if last else None
    if not active:
        if failed:
            return "dead", "its unit %s failed (%s)" % (rec.get("unit"), props.get("Result") or "unknown")
        if text.startswith("LOOP DONE_CLAIMED") or rec.get("done"):
            return "done claimed", "it wrote DONE.md %s ago" % ago(now_s() - (rec["done"]["t"] if rec.get("done") else t))
        if text.startswith("LOOP PAUSED_FOR_REVIEW"):
            return "paused for review", "it reached its token limit and waits for your word"
        if text.startswith("LOOP stopped") or text.startswith("LOOP STOPPED"):
            if "STOP file" in text:
                how = "on its STOP file (%s)" % rec["stop_reason"] if rec.get("stop_reason") else "on its STOP file"
            else:
                how = "by its own stop rule: " + short(text.split(":", 1)[-1], 90)
            return "stopped", "it ended %s, %s ago, and nothing will run it until someone restarts it" % (how, ago(now_s() - t))
        if not rec["events"]:
            return "not started", "no events log yet"
        return "dead", "no unit is running it and its log ends without a clean finish: %s" % short(text, 80)
    if text.startswith("LOOP PAUSED_FOR_REVIEW"):
        return "paused for review", "it reached its token limit and waits for your word"
    if rec["unmeasured"].get("events"):
        return "unmeasured", "its unit is up but its log can't be read: %s" % rec["unmeasured"]["events"]
    if text.startswith("GAME_WAIT"):
        return "waiting for game", "a loop ahead has the game; no model running, for %s" % ago(now_s() - t)
    if rec["open_pass"]:
        quiet = now_s() - rec["last_active"] if rec.get("last_active") else None
        if not rec["model"] and not rec["procs"] and (quiet is None or quiet > 120):
            return "stuck", "pass %d is open but no model process is alive, and nothing written for %s" % (rec["open_pass"]["n"], ago(quiet))
        if quiet is not None and quiet > QUIET_STUCK_S and not rec["procs"]:
            return "stuck", "nothing written for %s, and no command is running" % ago(quiet)
        return "working", "pass %d, running %s" % (rec["open_pass"]["n"], ago(now_s() - rec["open_pass"]["start"]))
    if t is not None and now_s() - t > NO_MODEL_STUCK_S and not rec["model"]:
        return "stuck", "unit is up, no pass is open, and nothing logged for %s" % ago(now_s() - t)
    return "working", "between passes"


def warn_about(rec):
    w = rec["warnings"]
    active = (rec.get("props") or {}).get("ActiveState") == "active"
    if rec["stop_file"] is not None:
        why = " Reason: %s." % rec["stop_reason"] if rec.get("stop_reason") else ""
        if active:
            w.append("STOP is set (%s ago) and the unit still runs: it ends after this pass.%s" % (ago(now_s() - rec["stop_file"]), why))
        else:
            w.append("STOP is still set from %s ago: a restart would end at once. Clear it first.%s" % (ago(now_s() - rec["stop_file"]), why))
    if rec.get("done") and rec["state"] == "working":
        w.append("DONE.md exists while a pass runs: the loop ends when the pass does.")
    done_passes = [p for p in rec["passes"] if p["end"]]
    tail_nc = 0
    for p in reversed(done_passes):
        if p.get("commits") == 0:
            tail_nc += 1
        else:
            break
    if tail_nc:
        w.append("%d pass%s in a row with no commit%s." % (
            tail_nc, "" if tail_nc == 1 else "es", " (the shell stops at 2 if this loop has that rule)" if tail_nc == 1 else ""))
    tail_bad = 0
    for p in reversed(done_passes):
        if p["rc"] not in (0, None) or p["lost"]:
            tail_bad += 1
        else:
            break
    if tail_bad:
        w.append("%d failed pass%s in a row, latest %s (the shell stops at 3)." % (
            tail_bad, "" if tail_bad == 1 else "es",
            "with no end line" if done_passes[-1]["lost"] else "rc %s" % done_passes[-1]["rc"]))
    bad = [p for p in rec["passes"] if p["rc"] not in (0, None) or p["lost"]]
    if bad and not tail_bad:
        w.append("Earlier failed passes: %s." % ", ".join(str(p["n"]) for p in bad[-5:]))
    op = rec["open_pass"]
    if op and now_s() - op["start"] > PASS_LIMIT_S - 1800:
        w.append("Pass %d has run %s; each pass is killed at 6 h." % (op["n"], ago(now_s() - op["start"])))
    if rec.get("err_size"):
        w.append("The latest pass wrote %d bytes to its error file." % rec["err_size"])
    tx = rec.get("tx")
    if tx:
        norm = Counter(re.sub(r"\d+", "#", c)[:120] for c in tx["bash"] if c)
        rep = [(c, n) for c, n in norm.most_common(2) if n >= 5]
        for c, n in rep:
            w.append("Same command %d times lately: `%s`." % (n, short(c, 90)))
        errs = Counter(re.sub(r"\d+", "#", e)[:100] for e in tx["errors"] if e)
        for e, n in errs.most_common(2):
            if n >= 3:
                w.append("Same error %d times lately: %s" % (n, short(e, 110)))
        if tx["context"] and tx["context"] > rec["gate"]["firm"]:
            w.append("Context %s is over the firm ceiling %s." % (toks(tx["context"]), toks(rec["gate"]["firm"])))


# ---- games and machines ---------------------------------------------------------------------------

READER = r'''
import glob, json, os, re, subprocess, time, datetime as dt
from collections import Counter
out = {"read_at": time.time()}
def run(cmd, t):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, errors="replace", timeout=t, stdin=subprocess.DEVNULL).stdout
    except Exception as e:
        out.setdefault("errors", []).append("%s: %s" % (os.path.basename(cmd[0]), str(e)[:80]))
        return None
def iso(s):
    try:
        return dt.datetime.fromisoformat(str(s).replace("Z", "+00:00")).timestamp()
    except Exception:
        return None
W = "/mnt/c/Windows/System32/"
s = run([W + "tasklist.exe", "/FO", "CSV", "/NH", "/FI", "IMAGENAME eq RimWorldWin64.exe"], 5)
pid = None
if s is None:
    out["game"] = None
else:
    pids = re.findall(r'"RimWorldWin64\.exe","(\d+)"', s)
    out["game"] = bool(pids)
    pid = pids[0] if pids else None
    out["games"] = [{"pid": x} for x in pids]
if pid:
    s = run([W + "NETSTAT.EXE", "-ano", "-p", "TCP"], 5)
    if s is not None:
        for g in out["games"]:
            g["ports"] = sorted({l.split()[1].rsplit(":", 1)[1] for l in s.splitlines() if "LISTENING" in l and l.split()[-1] == g["pid"]})
        out["ports"] = out["games"][0]["ports"]
s = run([W + "typeperf.exe", r"\Memory\Available MBytes", "-sc", "1"], 6)
if s:
    m = re.search(r'",\s*"([\d.]+)"', s)
    if m:
        out["win_free_mb"] = float(m[1])
try:
    mem = dict(l.split(":", 1) for l in open("/proc/meminfo"))
    out["wsl_free_mb"] = int(mem["MemAvailable"].split()[0]) // 1024
except Exception as e:
    out.setdefault("errors", []).append("meminfo: %s" % e)
def newest(d, pat):
    best = None
    with os.scandir(d) as it:
        for e in it:
            if pat.match(e.name):
                m = e.stat().st_mtime
                if best is None or m > best[0]:
                    best = (m, e.path)
    return best
roots = glob.glob(os.environ.get("ARTISAN_TPS_ROOT") or "/mnt/c/Users/*/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/JawaBench/tps")
out["tps_roots"] = len(roots)
sessions = []
for r in roots:
    with os.scandir(r) as it:
        for e in it:
            m = re.match(r"tps_(\d{8}T\d{6})Z_\w+?_(\d+)_\d+\.jsonl$", e.name)
            if not m:
                continue
            st = e.stat()
            if time.time() - st.st_mtime > 26 * 3600:
                continue
            row = {"start": dt.datetime.strptime(m[1], "%Y%m%dT%H%M%S").replace(tzinfo=dt.timezone.utc).timestamp(), "end": st.st_mtime, "pid": m[2], "stalls": []}
            with open(e.path, "rb") as f:
                for line in f:
                    if b'"type":"stall"' in line:
                        try:
                            i = json.loads(line)
                        except ValueError:
                            continue
                        if (i.get("unexplainedS") or 0) >= 1 and iso(i.get("utc")):
                            row["stalls"].append([round(iso(i["utc"])), round(i["unexplainedS"], 1)])
            row["stalls"] = row["stalls"][-60:]
            sessions.append(row)
out["sessions"] = sorted(sessions, key=lambda x: x["start"])
best = None
for r in roots:
    n = newest(r, re.compile(r"tps_.*\.jsonl$"))
    if n and (best is None or n[0] > best[0]):
        best, root = n, r
if best:
    out["tps_file"] = os.path.basename(best[1])
    out["tps_mtime"] = best[0]
    h = newest(root, re.compile(r"hb_.*\.json$"))
    if h:
        try:
            d = json.load(open(h[1], encoding="utf-8", errors="replace"))
            out["hb"] = {"mtime": h[0], "silent": d.get("silentS"), "phase": d.get("phase"), "pid": d.get("pid"),
                         "beat": iso(d.get("mainBeatUtc")), "start": iso(d.get("procStartUtc"))}
        except Exception as e:
            out["hb_error"] = str(e)[:80]
    with open(best[1], "rb") as f:
        f.seek(0, 2); end = f.tell(); f.seek(max(0, end - 400000)); raw = f.read()
    if end > 400000:
        raw = raw[raw.find(b"\n") + 1:]
    samples, worst, ctx, incidents, shut = [], {}, None, [], None
    for line in raw.decode("utf-8", "replace").splitlines():
        try:
            d = json.loads(line)
        except ValueError:
            continue
        k = d.get("kind")
        if k == "sample":
            samples.append(d)
            for w in d.get("worst") or []:
                if isinstance(w, dict) and w.get("tg") is not None:
                    worst[w["tg"]] = {"ms": w.get("ms") or 0, "top": w.get("top"), "t": iso(d.get("utc"))}
        elif k == "context":
            ctx = d
        elif k == "incident":
            incidents.append(d)
        elif k in ("shutdown", "shutdown-complete"):
            shut = iso(d.get("utc"))
    out["samples_read"] = len(samples)
    out["shutdown"] = shut
    if samples:
        last = samples[-1]
        tl = iso(last.get("utc")) or best[0]
        out["last"] = {"t": tl, "state": last.get("state"), "speed": last.get("speed"), "mult": last.get("mult"),
                       "tps": last.get("tps"), "ratio": last.get("ratio"), "target": last.get("target"), "heap": last.get("heapMB")}
        recent = [s for s in samples if (iso(s.get("utc")) or 0) >= tl - 600]
        run_s = [s for s in recent if s.get("ratio") is not None and s.get("state") == "run"]
        out["window_s"] = int(tl - (iso(recent[0].get("utc")) or tl))
        out["paused_frac"] = round(sum(1 for s in recent if s.get("state") == "paused") / len(recent), 2)
        if run_s:
            r = sorted(s["ratio"] for s in run_s)
            t = sorted(s.get("tps") or 0 for s in run_s)
            out["ratio_med"], out["tps_med"] = r[len(r) // 2], t[len(t) // 2]
            out["ratio_low"] = r[len(r) // 10]
        wr = {k: v for k, v in worst.items() if (v["t"] or 0) >= tl - 600}
        if wr:
            tg, v = max(wr.items(), key=lambda kv: kv[1]["ms"])
            out["worst"] = {"ms": v["ms"], "top": v["top"], "tg": tg, "t": v["t"]}
            big = sorted(k for k, x in wr.items() if x["ms"] >= 150)
            out["big_ticks"] = len(big)
            diffs = [b - a for a, b in zip(big, big[1:]) if b > a]
            if len(diffs) >= 3:
                p, _ = Counter(diffs).most_common(1)[0]
                fit = sum(1 for d in diffs if p and (d % p <= 2 or p - d % p <= 2))
                if p >= 2 and fit >= max(3, 0.6 * len(diffs)):
                    ms = sorted(wr[k]["ms"] for k in big)
                    tops = Counter(str(wr[k]["top"]) for k in big).most_common(1)[0][0]
                    out["period"] = {"ticks": p, "ms": ms[len(ms) // 2], "top": tops, "seen": len(big)}
        out["stalls_10m"] = sum(1 for i in incidents if (iso(i.get("utc")) or 0) >= tl - 600)
    if ctx:
        maps = ctx.get("maps") or []
        cur = next((m for m in maps if m.get("current")), maps[0] if maps else None)
        out["ctx"] = {"t": iso(ctx.get("utc")), "biome": cur and cur.get("biome"), "pawns": cur and cur.get("pawns"), "things": cur and cur.get("things"),
                      "ws": ctx.get("workingSetMB"), "logErr": ctx.get("logErr"), "logWarn": ctx.get("logWarn"), "up": ctx.get("upS")}
print(json.dumps(out))
'''


def read_machine(name):
    if name == "Archmagi":
        cmd = ["python3", "-"]
    else:
        cmd = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=6", "-o", "LogLevel=ERROR", STEVE_SSH, "python3", "-"]
    rc, out, err = run(cmd, timeout=MACHINE_DEADLINE_S - 1, input_text=READER)
    if rc:
        raise Unmeasured("%s: %s" % ("reader" if name == "Archmagi" else "ssh", short(err or "exit %d" % rc, 110)))
    try:
        return json.loads(out)
    except ValueError:
        raise Unmeasured("reader said no JSON: %s" % short(out or err, 100))


def read_machines(state, sources):
    """Both machines at once under one deadline. A miss keeps the last good reading, labelled with its age."""
    results = {}

    def work(name):
        try:
            results[name] = {"data": read_machine(name)}
        except Unmeasured as e:
            results[name] = {"why": str(e)}

    threads = {n: threading.Thread(target=work, args=(n,), daemon=True) for n in ("Archmagi", "SteveDesktop")}
    for th in threads.values():
        th.start()
    deadline = time.time() + MACHINE_DEADLINE_S
    for th in threads.values():
        th.join(max(0.1, deadline - time.time()))
    saved = state.setdefault("machines", {})
    out = {}
    for name in threads:
        r = results.get(name) or {"why": "no answer within %d s" % MACHINE_DEADLINE_S}
        if "data" in r:
            saved[name] = r["data"]
            out[name] = {"data": r["data"], "fresh": True}
            sources.add("machine read, %s" % name, 0, None)
        else:
            out[name] = {"why": r["why"], "fresh": False, "data": saved.get(name)}
            sources.add("machine read, %s" % name, None, r["why"])
    return out


def game_ports(games):
    """One entry per running game: its port, or a word when it has none yet."""
    return [", ".join(g.get("ports") or []) or "none yet" for g in games]


def machine_lines(name, m):
    """Plain lines about a machine. Old figures are said to be old."""
    lines = []
    d = m.get("data")
    if not m["fresh"]:
        lines.append("**UNMEASURED now:** %s." % m["why"])
        if not d:
            return lines
        lines.append("Figures below are from the last good read, %s ago, not now." % ago(now_s() - d.get("read_at", 0)))
    if d.get("game") is None:
        lines.append("Game: UNMEASURED (tasklist did not answer: %s)." % "; ".join(d.get("errors", []))[:120])
    elif not d["game"]:
        lines.append("Game: **not running**.")
    else:
        ports = d.get("ports")
        games = d.get("games") or []
        if len(games) > 1:
            lines.append("**%d games running**, ports %s." % (len(games), " and ".join(game_ports(games))))
        else:
            lines.append("Game: **running**%s." % (
                "" if ports is None else ", listening on port %s" % ", ".join(ports) if ports else ", no listening port yet (bridge not up)"))
    hb = d.get("hb")
    if d.get("game") and hb and now_s() - hb["mtime"] < 300:
        silent = hb.get("silent")
        beat = "Main thread answering" if not silent or silent < 5 else "**Main thread silent %d s**" % silent
        lines.append("%s (heartbeat %s old%s)." % (beat, ago(now_s() - hb["mtime"]), ", " + str(hb["phase"]) if hb.get("phase") else ""))
    last = d.get("last")
    if not d.get("tps_roots"):
        lines.append("TPS: UNMEASURED (no JawaBench tps folder found on this machine).")
    elif not d.get("tps_file"):
        lines.append("TPS: UNMEASURED (the tps folder holds no record).")
    elif not last:
        lines.append("TPS: UNMEASURED (%s holds no sample in its last 400 KB)." % d["tps_file"])
    else:
        age = now_s() - d.get("tps_mtime", 0)
        running_now = d.get("game") and age < 120
        lead = "" if running_now else "Not now: from its last record, %s ago%s. " % (ago(age), ", game closed %s" % clock(d["shutdown"]) if d.get("shutdown") else "")
        state = {"run": "running", "paused": "**paused**", "stall": "**stalling**", "longevent": "loading", "mixed": "running, partly paused"}.get(last.get("state"), last.get("state"))
        speed = ""
        if last.get("speed") and last.get("state") != "paused":
            speed = " on its %s button" % last["speed"]
            if last.get("target"):  # a dev multiplier can make Ultrafast ask for 60, so the button alone misleads
                speed += ", asking %d ticks a second" % round(last["target"])
        bits = ["Game clock: %s%s." % (state, speed)]
        if d.get("ratio_med") is not None:
            pf = d.get("paused_frac") or 0
            bits.append("While running, over %s%s: %s ticks a second, %d%% of what the speed asks (slowest tenth %d%%)." % (
                ago(d.get("window_s")), ", %d%% of it paused" % round(pf * 100) if pf else "", round(d.get("tps_med") or 0),
                round(d["ratio_med"] * 100), round(d.get("ratio_low", 0) * 100)))
        elif d.get("paused_frac") == 1:
            bits.append("It did not tick in the last %s, so no speed reading." % ago(d.get("window_s")))
        lines.append(lead + " ".join(bits))
        if d.get("worst"):
            w = d["worst"]
            lines.append("Worst tick%s: %d ms, biggest part %s." % (" then" if lead else "", round(w["ms"]), short(w.get("top") or "unnamed", 50)))
        if d.get("period"):
            p = d["period"]
            lines.append("**Repeating freeze: about %d ms every %d ticks** (%d seen, mostly %s)." % (
                round(p["ms"]), p["ticks"], p["seen"], short(p["top"], 40)))
        if d.get("stalls_10m"):
            lines.append("Stall incidents in the last 10 minutes of record: %d." % d["stalls_10m"])
    c = d.get("ctx")
    if c and d.get("game") and c.get("biome"):
        lines.append("On map: %s, %s pawns, %s things; game memory %s MB; log errors %s, warnings %s." % (
            c["biome"], c.get("pawns"), c.get("things"), round(c["ws"]) if c.get("ws") else "UNMEASURED", c.get("logErr"), c.get("logWarn")))
    win = d.get("win_free_mb")
    lines.append("Memory free: Windows %s, WSL %s." % (
        "%.1f GB" % (win / 1024) if win is not None else "UNMEASURED",
        "%.1f GB" % (d["wsl_free_mb"] / 1024) if d.get("wsl_free_mb") is not None else "UNMEASURED"))
    return lines


def read_tailscale():
    rc, out, err = run(["tailscale", "status", "--json"], timeout=5)
    if rc:
        raise Unmeasured(short(err, 100))
    data = json.loads(out)
    return [p for p in (data.get("Peer") or {}).values() if "stevedesktop" in str(p.get("HostName", "")).lower()]


def read_fault(sources):
    path = os.path.join(QHOME, "fault_state.json")
    if sources.file("SteveDesktop fault monitor", path) is None:
        raise Unmeasured("no %s" % path)
    st = json.loads(read_text(path, 2_000_000))
    win = json.loads(read_text(os.path.join(QHOME, "fault_windows.json"), 4_000_000))
    return st, win if isinstance(win, list) else []


def fault_lines(st, windows, loops):
    lines = []
    day = now_s() - 86400
    today = [w for w in windows if (parse_iso(w.get("first_bad") or w.get("start")) or 0) >= day]
    op = st.get("open_window")
    last = parse_iso(st.get("last_cycle"))
    head = "CPU fault monitor: "
    if st.get("alarm"):
        head += "**ALARM**, "
    if op:
        head += "**a fault window is open now** (%s), " % short(op if isinstance(op, str) else op.get("id", op), 40)
    else:
        head += "no window open, "
    head += "clean since %s, last check %s ago, %s." % (clock(parse_iso(st.get("clean_through"))), ago(now_s() - last) if last else "UNMEASURED",
                                                       "machine answering" if st.get("reachable") else "**machine not answering**")
    lines.append(head)
    if today:
        cpus = Counter()
        for w in today:
            for c, n in (w.get("cpus") or {}).items():
                cpus[c] += n
        names = sorted(cpus, key=int)
        lines.append("Fault windows in 24 h: %d, on CPU%s %s; last began %s." % (
            len(today), "" if len(names) == 1 else "s", ", ".join(names[:8]) + (" and %d more" % (len(names) - 8) if len(names) > 8 else ""),
            clock(parse_iso(today[-1].get("first_bad")))))
    else:
        lines.append("Fault windows in 24 h: none.")
    for rec in loops:
        if rec.get("machine") != "SteveDesktop":
            continue
        hit = set()
        for w in today:
            a, b = parse_iso(w.get("first_bad") or w.get("start")), parse_iso(w.get("end")) or now_s()
            for p in rec["passes"]:
                if a is not None and p["start"] <= b and (p["end"] or now_s()) >= a:
                    hit.add(p["n"])
        if hit:
            lines.append("%s's passes that overlap a window: %s." % (rec["name"], ", ".join(map(str, sorted(hit)))))
    return lines


def read_accounts(sources):
    path = os.path.join(ACCOUNTS, "latest.json")
    if sources.file("account readings", path) is None:
        raise Unmeasured("no %s" % path)
    data = json.loads(read_text(path, 500_000))
    rows = []
    series = {}
    try:
        for line in read_tail(os.path.join(ACCOUNTS, "series.jsonl"), 300_000).splitlines():
            d = json.loads(line)
            series.setdefault(d.get("account"), []).append((parse_iso(d.get("measured_at")), d.get("week_pct_used")))
    except (OSError, ValueError):
        pass
    for name, a in sorted((data.get("accounts") or {}).items()):
        used = a.get("week_pct_used")
        slope = None
        pts = [p for p in series.get(name, []) if p[0] and p[1] is not None and p[0] >= now_s() - 6 * 3600]
        if len(pts) >= 2 and pts[-1][0] - pts[0][0] > 1800:
            slope = (pts[-1][1] - pts[0][1]) / ((pts[-1][0] - pts[0][0]) / 3600)
        rows.append({"name": short(name.split("@")[0], 24), "used": used, "resets": parse_iso(a.get("week_resets_at")),
                     "t": parse_iso(a.get("measured_at")), "why": a.get("why"), "slope": slope})
    return rows


def read_bridge():
    best = None
    for p in BRIDGE_FILES:
        m = mtime(p)
        if m and (not best or m > best[0]):
            best = (m, p)
    if not best:
        raise Unmeasured("no BRIDGE file")
    text = read_text(best[1])
    m = re.search(r"^(HELD|FREE)\b[ \t]*(?!since\b)(\S*)[ \t]*(?:since\s+(\S+))?", text, re.M)
    if not m:
        raise Unmeasured("BRIDGE file has no HELD or FREE line")
    why = re.search(r"^for\s+(.*)$", text, re.M)
    return {"state": m[1], "who": m[2], "since": parse_iso(m[3]), "why": why[1] if why else None, "t": best[0]}


def read_background(sources):
    """Live helpers, detached runs, armed watches and failed rm-* units, each cheap and each may fail alone."""
    out = {"detached": None, "failed": None, "watchers": None, "claude": None}
    try:
        rc, s, err = run([sys.executable, os.path.join(HERE, "..", "rimflow", "detached_helper.py"), "status"], timeout=8)
        if rc:
            raise Unmeasured(short((err.strip().splitlines() or ["exit %d" % rc])[-1], 110))
        out["detached"] = [ln.strip() for ln in s.splitlines() if " running " in ln or ln.strip().endswith("running")]
        sources.add("detached runs", 0, None)
    except Unmeasured as e:
        out["detached_why"] = str(e)
        sources.add("detached runs", None, str(e))
    try:
        rc, s, err = run(["systemctl", "--user", "list-units", "--state=failed", "--plain", "--no-legend", "rm-*"], timeout=6)
        out["failed"] = [ln.split()[0].replace(".service", "") for ln in s.splitlines() if ln.strip()]
    except Unmeasured as e:
        out["failed_why"] = str(e)
    watchers, seats = 0, Counter()
    try:
        for pid in os.listdir("/proc"):
            if not pid.isdigit():
                continue
            try:
                raw = open("/proc/%s/cmdline" % pid, "rb").read(600)
            except OSError:
                continue
            parts = raw.split(b"\0")
            if b"waitfor.py" in raw and b"events.log" in raw:
                watchers += 1
            if parts and os.path.basename(parts[0]) == b"claude":
                try:
                    cwd = os.readlink("/proc/%s/cwd" % pid)
                except OSError:
                    continue
                seats[os.path.basename(cwd)] += 1
        out["watchers"], out["claude"] = watchers, seats
    except OSError as e:
        out["proc_why"] = str(e)
    return out


def read_scoreboard():
    m = re.search(r"Acceptances?:?\**\s*(\d+)[^\n]*", read_text(LEARNED))
    if not m:
        raise Unmeasured("no Acceptances line in learned.md")
    return m[0].replace("*", "").split(". ")[0].rstrip(".")


def holder_of_game(loops):
    """Who is driving each game, from live processes that match the loop's own gate pattern, then recent commands."""
    out = {}
    for rec in loops:
        rx = rec["gate"].get("game")
        if not rx:
            continue
        for p in rec["procs"]:
            if rx.search(p["cmd"]):
                out.setdefault(rec["machine"], []).append({"loop": rec["name"], "cmd": p["cmd"], "age": p["age"]})
    return out


def last_game_use(rec):
    rx = rec["gate"].get("game")
    if not rx or not rec.get("tx"):
        return None
    for row in reversed(rec["tx"]["tools"]):
        if row["name"] == "Bash" and rx.search(row["cmd"]):
            return row
    return None


def queue_lines(loops):
    """The game queue is the order of each loop's own lists; there is no scheduler."""
    known = set()
    for r in loops:
        if r.get("unit"):
            known.add(r["unit"])
        if r.get("unit_saved"):
            known.add(r["unit_saved"])
    lines, drift = [], []
    for r in loops:
        if not r["loopsh"].get("busy_units") and not r["gate"]["ahead"] and not r["loopsh"].get("busy_steve"):
            continue
        names = sorted(set(r["loopsh"].get("busy_units", [])) | set(r["gate"]["ahead"]))
        names = [n for n in names if n != r.get("unit")]
        missing = [n for n in names if n not in known]
        real = [n for n in names if n in known]
        if r["loopsh"].get("busy_steve") and not names:
            who = "gives way only if SteveDesktop stops answering"
        elif real:
            who = "gives way to " + ", ".join(real)
        else:
            who = "gives way to no unit that exists"
        need = ", has asked for the game (NEED_GAME, %s ago)" % ago(now_s() - r["need_game"]) if r.get("need_game") else ""
        lines.append("%s, on %s: %s%s." % (r["name"], r["machine"], who, need))
        if missing:
            drift.append("%s's gate names %s, which match no unit on record, so it would not wait for them. "
                         "Deliberate or drift: the file can't say." % (r["name"], ", ".join(missing)))
    return lines, drift


# ---- spend today ----------------------------------------------------------------------------------

def check_waits(loops):
    """A waiting loop names who it waits on. A wait with nobody ahead has outlasted its cause."""
    active = {r["unit"] for r in loops if r.get("unit") and (r.get("props") or {}).get("ActiveState") == "active"}
    for r in loops:
        if r["state"] != "waiting for game":
            continue
        ahead = set(r["loopsh"].get("busy_units", [])) | set(r["gate"]["ahead"])
        on = sorted((ahead & active) - {r.get("unit")})
        since = ago(now_s() - r["events"][-1][0])
        if on:
            r["state_why"] = "it gives way to %s, which is active; no model running, so it spends nothing, for %s" % (", ".join(on), since)
            r["wait_on"] = [next((x["name"] for x in loops if x.get("unit") == u), u) for u in on]
        elif r["loopsh"].get("busy_steve"):
            r["state_why"] = "SteveDesktop isn't answering; no model running, for %s" % since
        else:
            r["state_why"] = "no unit it gives way to is active now, so it should start within a minute; waiting %s" % since
            r["wait_orphan"] = True


def spend_today(rec):
    """Weighted tokens in today's local date, each pass spread evenly over its own run: an estimate."""
    start = dt.datetime.combine(dt.datetime.fromtimestamp(now_s()).date(), dt.time()).timestamp()
    total = 0.0
    for p in rec["passes"]:
        end = p["end"] or now_s()
        spent = (p["t_end"] - p["t_start"]) if p["t_end"] is not None else rec.get("live_tokens")
        if not spent or end <= start or end <= p["start"]:
            continue
        total += spent * (end - max(start, p["start"])) / (end - p["start"])
    return int(total)


# ---- the arc: where each pass's time went, read from its transcript ------------------------------------

ARC_KINDS = ("think", "code", "build", "game", "wait", "idle")
ARC_PRIO = ("game", "wait", "build", "code", "think", "idle")   # two tools open at once: the time goes to the first of these
ARC_LETTER = {"think": "T", "code": "C", "build": "B", "game": "G", "wait": "W", "idle": "I"}
ARC_OF_LETTER = {v: k for k, v in ARC_LETTER.items()}
ARC_VERSION = 1             # bump when the classifier changes: every finished pass is read again
STALL_S = 300               # the model silent this long with no tool open and no job running is a stall
BIN_S = 60                  # the picture draws about a pixel a minute, so a finished pass keeps one letter a minute
ARC_BUDGET_S = 8            # a fresh cache is many hundreds of MB: read for this long, finish over the next minutes
GAME_MERGE_S = 600          # game use with a gap under this is one hold of the game
HOLD_MERGE_S = 1200         # on the picture, holds by one loop this close read as one

HEREDOC = re.compile(r"<<-?\s*['\"]?(\w+)['\"]?[^\n]*\n(.*?)\n\s*\1\b", re.S)
ARC_TESTS = re.compile(r"selftest|\bfuzz|pytest|proof_all\.py[^|;&]*--offline")
ARC_BUILD = re.compile(r"winbuild|msbuild|\bdotnet\b|\bcsc\b|deploy_custom_mods[^|;&]*|modset_builder[^|;&]*|modlist_swap[^|;&]*|\./publish|land\.sh|\./sync\b"
                       r"|git\s+(?:commit|push|pull|fetch|rebase|merge|add)\b|bake\.py|build\.py")
ARC_GAME = re.compile(r"steve\.sh|python\.exe|\bbridge\b|rimbridge|live_session|logwait|modcheck\s+run|\./game\b|proof_all\.py|\bplay\.py|stage_colony|\bcolony\.py"
                      r"|northstar/|Player\.log|RimWorldWin64|steam://|Start-Process|taskkill|system_click|system_screenshot|--live\b|jawa/")
ARC_WAIT = re.compile(r"\blogwait\b|waitlog|\bwait_?for\b|tail\s+--pid|\bsleep\s+[1-9]\d|\b(?:until|while)\b.*\bsleep\b|time\.sleep\(|while time\.time", re.S)
ARC_WRITES = re.compile(r"\bcat\s*>|\btee\s+\S|>>?\s*[\w./$-]+\.(?:py|cs|xml|sh|md|json|csproj)\b|\bsed\s+-i|\bgit\s+apply|\bperl\s+-pi")
BODY_WRITES = re.compile(r"\.write(?:_text)?\(|open\([^)]*['\"][wa]b?['\"]")
EFFORT = re.compile(rb'"effort":"(\w+)"')


def bash_kind(command, gate=None):
    """What a shell command's time went to. A heredoc's body is the code being written, not what the command does."""
    outer = HEREDOC.sub(" ", command)
    # a heredoc fed to a file is only written; one fed to an interpreter runs
    bodies = [] if re.search(r"\bcat\s*>|\btee\s", outer) else [m[2] for m in HEREDOC.finditer(command)]
    if ARC_TESTS.search(outer):
        return "build"
    rest = ARC_BUILD.sub(" ", outer)
    if ARC_WAIT.search(outer) or any(ARC_WAIT.search(b) for b in bodies):
        return "wait"
    if ARC_GAME.search(rest) or (gate is not None and gate.search(rest)):
        return "game"
    if rest != outer:
        return "build"
    if ARC_WRITES.search(outer) or any(BODY_WRITES.search(b) for b in bodies):
        return "code"
    return "think"


def tool_kind(name, inp, gate=None):
    if name == "Bash":
        return bash_kind(str(inp.get("command", "")), gate)
    if name in ("Edit", "Write", "NotebookEdit"):
        return "code"
    if name == "Read" and re.search(r"\.(png|jpe?g|bmp|gif)$", str(inp.get("file_path", "")), re.I):
        return "game"       # a screenshot it took: looking at the game
    if name == "Monitor":
        return "watch"      # watching a job it started: the time belongs to that job
    return "think"


def arc_new():
    return {"offset": 0, "spans": [], "open": {}, "bg": [], "bg_last": None, "last": None, "first": None, "ended": False, "effort": None,
            "notes": [], "game": [], "where": "A", "lines": 0, "stamped": 0}


def arc_span(c, a, b, kind):
    spans = c["spans"]
    if spans and spans[-1][2] == kind and a - spans[-1][1] < 1:
        spans[-1][1] = b
    else:
        spans.append([a, b, kind])
    if kind == "game":
        g = c["game"]
        if g and g[-1][2] == c["where"] and a - g[-1][1] < GAME_MERGE_S:
            g[-1][1] = b
            g[-1][3] += b - a
        else:
            g.append([a, b, c["where"], b - a])


def job_kind(c):
    """A job running in the background that the model is waiting on."""
    if c["bg"]:
        return min(c["bg"], key=ARC_PRIO.index)
    return c["bg_last"] or "wait"


def gap_kind(c, rec_kind, uses, notified, gap, gate):
    """What the time up to this line went to, by what was open when it began."""
    if c["open"]:
        best = min((k for k in c["open"].values() if k != "watch"), key=ARC_PRIO.index, default="watch")
        return job_kind(c) if best in ("watch", "think") and "watch" in c["open"].values() else best
    if rec_kind == "assistant" and not c["ended"]:
        if gap > STALL_S:
            return "idle"
        return "code" if any(tool_kind(u.get("name"), u.get("input") or {}, gate) == "code" for u in uses) else "think"
    if notified or c["bg"]:
        return job_kind(c)
    return "idle" if gap > 60 else "think"


def arc_step(c, d, gate):
    """One transcript line through the walker."""
    kind = d.get("type")
    c["lines"] += 1
    t = parse_iso(d.get("timestamp"))
    if t is None:
        return
    c["stamped"] += 1
    msg = d.get("message") or {}
    content = msg.get("content")
    blocks = [b for b in content if isinstance(b, dict)] if isinstance(content, list) else []
    uses = [b for b in blocks if b.get("type") == "tool_use"] if kind == "assistant" else []
    words = content if isinstance(content, str) else " ".join(str(b.get("text", "")) for b in blocks if b.get("type") == "text")
    notified = kind == "user" and "<task-notification>" in words
    if c["last"] is not None and t > c["last"]:
        arc_span(c, c["last"], t, gap_kind(c, kind, uses, notified, t - c["last"], gate))
    if c["first"] is None:
        c["first"] = t
    c["last"] = max(t, c["last"] or t)
    for u in uses:
        inp = u.get("input") or {}
        k = tool_kind(u.get("name"), inp, gate)
        if k == "game" and u.get("name") == "Bash":
            c["where"] = "S" if "steve.sh" in str(inp.get("command", "")) else "A"
        if inp.get("run_in_background") and u.get("name") in ("Bash", "Agent", "Task"):
            c["bg"].append("wait" if k == "watch" else k)
            c["bg_last"] = c["bg"][-1]
            c["open"][u.get("id")] = "think"
        else:
            c["open"][u.get("id")] = k
    for b in blocks:
        if b.get("type") == "tool_result":
            c["open"].pop(b.get("tool_use_id"), None)
            if b.get("is_error") and "owner sent you a note" in json.dumps(b.get("content"))[:4000]:
                if not c["notes"] or t - c["notes"][-1] > GAME_MERGE_S:     # the gate repeats one note until it is read
                    c["notes"].append(t)
    if notified and c["bg"]:
        c["bg"].pop(0)
    c["ended"] = kind == "assistant" and msg.get("stop_reason") == "end_turn"


def arc_feed(path, c, gate):
    """Read what was added since the last read, whole lines only. A half-written last line waits for the next."""
    size = os.path.getsize(path)
    if c["offset"] > size:
        c.clear()
        c.update(arc_new())
    if c["offset"] >= size:
        return
    with open(path, "rb") as f:
        f.seek(c["offset"])
        raw = f.read()
    end = raw.rfind(b"\n")
    if end < 0:
        return
    for line in raw[:end].split(b"\n"):
        if b'"isSidechain":true' in line[:300] or not (b'"type":"assistant"' in line or b'"type":"user"' in line):
            continue
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if d.get("isSidechain") or d.get("type") not in ("assistant", "user"):
            continue
        if d["type"] == "assistant":
            hit = EFFORT.search(line)
            if hit:
                c["effort"] = hit[1].decode()
        arc_step(c, d, gate)
    c["offset"] += end + 1


def arc_result(c, start, end, live):
    """Seconds by kind and a letter a minute over the pass, from the walker's spans. The head before its first line is the
    model starting up; the tail of a live pass goes to what is open now, or a stall once it has been quiet long enough."""
    spans = [list(x) for x in c["spans"]]
    if c["first"] is not None and c["first"] > start:
        spans.insert(0, [start, c["first"], "think"])
    if c["last"] is not None and end > c["last"]:
        if live:
            quiet = end - c["last"]
            kinds = [k for k in c["open"].values() if k != "watch"]
            tail = "idle" if not c["open"] and not c["bg"] and quiet > STALL_S else (min(kinds, key=ARC_PRIO.index) if kinds else job_kind(c) if c["open"] or c["bg"] else "think")
        else:
            tail = "think"
        spans.append([c["last"], end, tail])
    sec = Counter()
    n = max(1, int((end - start) // BIN_S) + 1)
    bins = [Counter() for _ in range(n)]
    for a, b, k in spans:
        a, b = max(a, start), min(b, end)
        if b <= a:
            continue
        sec[k] += b - a
        i = int((a - start) // BIN_S)
        while a < b and i < n:
            edge = start + (i + 1) * BIN_S
            bins[i][k] += min(b, edge) - a
            a, i = edge, i + 1
    letters = "".join(ARC_LETTER[b.most_common(1)[0][0]] if b else "." for b in bins)
    return {"sec": {k: int(v) for k, v in sec.items()}, "bins": letters}


def session_of(pass_log):
    """The transcript's id, from the pass log's first line. Raises Unmeasured when that line can't say."""
    try:
        with open(pass_log, "rb") as f:
            first = f.readline(400_000)
    except OSError:
        raise Unmeasured("no log")
    try:
        sid = json.loads(first).get("session_id")
    except ValueError:
        raise Unmeasured("its log can't be read")
    if not sid:
        raise Unmeasured("its log can't be read")
    return sid


def bars_at(clone, sha):
    """The loop's own count and open questions as they stood at a commit, or None when that commit has no count."""
    out = {"bars": None, "q": None}
    try:
        counts = parse_progress(git(clone, "show", "%s:ralph/PROGRESS.md" % sha))["counts"]
        if sum(counts.values()):
            out["bars"] = {k: counts[k] for k in ("true", "false", "unseen")}
    except Unmeasured:
        pass
    try:
        out["q"] = sum(1 for q in parse_questions(git(clone, "show", "%s:ralph/QUESTIONS.md" % sha)) if not q["fyi"])
    except Unmeasured:
        out["q"] = 0
    return out


def read_arc(rec, cache, deadline):
    """One row per pass of this loop. A finished pass is read once and kept; a live one is read from where it stopped."""
    clone, logs = rec.get("clone"), rec["logs"]
    gate = (rec.get("gate") or {}).get("game")
    pdir = project_dir(clone) if clone else None
    now = now_s()
    rows = []
    for p in rec["passes"]:
        key = "%s#%d" % (logs, p["n"])
        live = p["end"] is None
        kept = cache.get(key)
        if kept and kept.get("done") and kept.get("v") == ARC_VERSION:
            rows.append(dict(kept, n=p["n"], start=p["start"], end=p["end"], live=False))
            continue
        row = {"n": p["n"], "start": p["start"], "end": p["end"] or now, "live": live, "v": ARC_VERSION}
        walker = (kept or {}).get("walker") if (kept or {}).get("v") == ARC_VERSION else None
        try:
            sid = (kept or {}).get("session") or session_of(os.path.join(logs, "pass_%03d.jsonl" % p["n"]))
            row["session"] = sid
            path = os.path.join(pdir or "", sid + ".jsonl")
            if not os.path.exists(path):
                raise Unmeasured("no transcript")
            if time.time() > deadline:
                row["broken"] = "still being read"
                rows.append(row)
                continue
            walker = walker or arc_new()
            arc_feed(path, walker, gate)
            if walker["lines"] and not walker["stamped"]:
                raise Unmeasured("no times in its log")
            if not walker["lines"]:
                raise Unmeasured("nothing in its log yet" if live else "its log is empty")
            row.update(arc_result(walker, p["start"], row["end"], live))
            row.update(effort=walker["effort"], notes=walker["notes"], game=[g for g in walker["game"] if g[3] >= 60])
        except Unmeasured as e:
            row["broken"] = str(e)
            if not live:
                row["done"] = True
                cache[key] = {k: v for k, v in row.items() if k not in ("start", "end", "live", "n")}
            rows.append(row)
            continue
        if not live:
            row["done"] = True
            if p.get("head") and clone:
                row.update(bars_at(clone, p["head"]))
            cache[key] = {k: v for k, v in row.items() if k not in ("start", "end", "live", "n")}
        else:
            cache[key] = {"v": ARC_VERSION, "session": sid, "walker": walker}
        rows.append(row)
    return rows


# ---- rendering ------------------------------------------------------------------------------------

STATE_WORD = {"working": "working", "waiting for game": "waiting for game", "paused for review": "PAUSED FOR REVIEW",
              "stopped": "STOPPED", "done claimed": "DONE CLAIMED", "dead": "DEAD", "stuck": "STUCK", "not started": "not started", "unmeasured": "UNMEASURED"}


def at_limit(r):
    """Its tokens have reached the limit, whatever the last line of its log calls the stop."""
    return bool(r.get("limit") and r.get("total") is not None and r["total"] >= r["limit"])


def needs_you(loops, fault, world):
    """(rank, text) for what wants the owner, most urgent first."""
    out = []
    for r in loops:
        nm = r["name"]
        if r["state"] == "dead":
            out.append((1, "**%s is dead:** %s. Read its last pass, then restart or retire." % (nm, r["state_why"])))
        elif r["state"] == "stuck":
            out.append((1, "**%s looks stuck:** %s." % (nm, r["state_why"])))
        elif r["state"] == "unmeasured":
            out.append((1, "**%s can't be read:** %s." % (nm, r["state_why"])))
        elif r["state"] == "done claimed":
            if r["done"] and any(v["t"] and v["t"] >= r["done"]["t"] for v in r["verdicts"]):
                out.append((2, "**%s claims done** and its blind judge has read it. Your look decides." % nm))
            else:
                out.append((2, "**%s claims done:** blind judge owed, then your look." % nm))
        elif r["state"] == "paused for review":
            out.append((2, "**%s reached its limit of %s tokens** and waits for your word on more." % (nm, toks(r["limit"]))))
        elif r["state"] == "stopped" and at_limit(r):
            out.append((2, "**%s reached its limit of %s tokens** and has stopped: %s." % (nm, toks(r["limit"]), r["state_why"])))
        elif r["state"] == "stopped" and not r.get("stop_reason"):
            out.append((3, "**%s has stopped:** %s." % (nm, r["state_why"])))
        real_qs = [q for q in r["qs"] if not q["fyi"]]
        if real_qs:
            out.append((2, "**%s asks you %d question%s**, written %s ago: %s. In full under its section." % (
                nm, len(real_qs), "" if len(real_qs) == 1 else "s", ago(now_s() - r["questions_t"]), short(real_qs[0]["title"], 70))))
        if r.get("wait_orphan"):
            out.append((3, "%s still waits for the game with nobody ahead of it." % nm))
        if r.get("look_t"):
            out.append((4, "%s has an early look for you, %s old (LOOK.md)." % (nm, ago(now_s() - r["look_t"]))))
        if r["state"] == "working" and r.get("eta_s") is not None and r["eta_s"] < 2 * 3600:
            out.append((3, "%s will reach its token limit in about %s." % (nm, ago(r["eta_s"]))))
        if r["state"] == "working" and r.get("stop_file") is not None and not r.get("stop_reason"):
            out.append((4, "%s has STOP set: it ends after this pass. Clear it if that is no longer wanted." % nm))
        elif r["state"] in ("waiting for game",) and r.get("stop_file") is not None and not r.get("stop_reason"):
            out.append((4, "%s has STOP set while it waits." % nm))
    if fault and fault.get("state"):
        st = fault["state"]
        if st.get("alarm") or st.get("open_window"):
            out.append((2, "**SteveDesktop's CPU fault monitor:** %s." % ("alarm raised" if st.get("alarm") else "a fault window is open")))
    for name, m in (world.get("machines") or {}).items():
        d = m.get("data") or {}
        if m.get("fresh") and d.get("period") and d.get("game") and now_s() - d.get("tps_mtime", 0) < 300:
            out.append((3, "**%s's game freezes about %d ms every %d ticks**, playing right now." % (name, round(d["period"]["ms"]), d["period"]["ticks"])))
    out.sort(key=lambda x: x[0])
    return out


def one_line(loops, needs, spend):
    words = Counter(r["state"] for r in loops)
    order = ["dead", "stuck", "unmeasured", "done claimed", "paused for review", "stopped", "waiting for game", "working", "not started"]
    part = ", ".join("%d %s" % (words[w], w) for w in order if words[w])
    return "%d loop%s: %s. Needs you: %d. Tokens today: ~%s." % (
        len(loops), "" if len(loops) == 1 else "s", part or "none", len(needs), toks(spend))


def rate_for(rec):
    """Tokens per hour, from the live pass once it has run 10 minutes, else the last finished passes."""
    op = rec["open_pass"]
    if op and rec.get("live_tokens") is not None and now_s() - op["start"] > 600:
        return rec["live_tokens"] / ((now_s() - op["start"]) / 3600), "this pass"
    done = [p for p in rec["passes"] if p["end"] and p["t_end"] is not None][-3:]
    secs = sum(p["end"] - p["start"] for p in done)
    if secs > 600:
        return sum(p["t_end"] - p["t_start"] for p in done) / (secs / 3600), "its last %d passes" % len(done)
    return None, None


def prepare(rec):
    """Figures the summaries and the section share."""
    rate, basis = rate_for(rec)
    rec["rate"], rec["rate_basis"] = rate, basis
    rec["eta_s"] = None
    if rate and rec["total"] is not None and rec["limit"] and rec["state"] == "working" and rec["limit"] > rec["total"]:
        rec["eta_s"] = (rec["limit"] - rec["total"]) / rate * 3600
    rec["spend_today"] = spend_today(rec)


def unit_line(r):
    p = r.get("props")
    if not p:
        saved = r.get("unit_saved")
        return "No unit now%s." % (" (saved definition: %s)" % saved if saved else "")
    state = p.get("ActiveState")
    if state == "active":
        try:
            up = uptime_now() - int(p.get("ActiveEnterTimestampMonotonic") or 0) / 1e6
            return "%s, up %s." % (r["unit"], ago(up))
        except (ValueError, OSError) as e:
            return "%s, active, uptime UNMEASURED (%s)." % (r["unit"], e)
    return "%s is %s (%s)." % (r["unit"], state, p.get("Result") or p.get("SubState"))


def loop_section(r, machines):
    nm = r["name"]
    un = r["unmeasured"]
    L = ["## %s: %s" % (nm, STATE_WORD.get(r["state"], r["state"])), ""]
    L.append("%s" % r["state_why"][0].upper() + r["state_why"][1:] + ".")
    L.append("")
    if r.get("goal"):
        L.append("**Goal:** %s" % r["goal"])
        L.append("")
    elif un.get("goal"):
        L.append("**Goal:** UNMEASURED (%s)" % un["goal"])
        L.append("")
    L.append("- **Machine and game:** %s." % r["machine"])
    L.append("- **Unit:** %s" % unit_line(r))
    L.append("- **Clone:** `%s`, branch %s. **Logs:** `%s`" % (r.get("clone"), r.get("branch") or "UNMEASURED", r["logs"]))
    for key, why in sorted(un.items()):
        if key not in ("goal", "git", "transcript", "progress", "north star", "live tokens"):
            L.append("- **%s:** UNMEASURED (%s)" % (key, why))
    op = r["open_pass"]
    if op:
        L.append("- **Pass %d:** running for %s, started %s." % (op["n"], ago(now_s() - op["start"]), clock(op["start"])))
    elif r["passes"]:
        last = r["passes"][-1]
        L.append("- **Last pass, %d:** ended %s, %s ago, after %s." % (
            last["n"], clock(last["end"]), ago(now_s() - last["end"]), ago(last["end"] - last["start"])))
    if un.get("live tokens"):
        L.append("- **Tokens:** UNMEASURED (%s)." % un["live tokens"])
    elif r["total"] is None:
        L.append("- **Tokens:** UNMEASURED (no figure in the events log).")
    else:
        lim = r["limit"]
        txt = "- **Tokens:** %s" % toks(r["total"])
        txt += " of %s (%d%%)" % (toks(lim), round(100 * r["total"] / lim)) if lim else ", limit UNMEASURED"
        if op and r.get("live_tokens") is not None:
            txt += "; this pass %s" % toks(r["live_tokens"])
        if r["rate"] and r["state"] == "working":
            txt += "; %s an hour (%s)" % (toks(r["rate"]), r["rate_basis"])
            if r.get("eta_s") is not None:
                txt += "; limit in about %s" % ago(r["eta_s"])
        tx = r.get("tx")
        if tx and tx.get("helper_count"):
            txt += ". Helpers this session: %d, %s more, outside the loop's count" % (tx["helper_count"], toks(tx["helper_tokens"]))
        L.append(txt + ".")
    if r.get("offline"):
        L.append("- **Offline budget:** after %s tokens without the game it must wait for one." % toks(r["offline"]))
    tx = r.get("tx")
    if un.get("transcript"):
        L.append("- **Context:** UNMEASURED (%s)." % un["transcript"])
    elif tx and tx.get("context") and (r["model"] or r["state"] == "working"):
        L.append("- **Context:** %s; warned at %s, must wrap up at %s." % (toks(tx["context"]), toks(r["gate"]["soft"]), toks(r["gate"]["firm"])))
    L.append("")

    # Now
    live = r["model"] or r["procs"]
    L.append("### %s" % ("Doing now" if live else "Last seen doing"))
    L.append("")
    quiet = now_s() - r["last_active"] if r.get("last_active") else None
    L.append("Last activity %s ago." % ago(quiet))
    if r["procs"]:
        L.append("")
        L.append("Running now:")
        L.append("")
        for p in r["procs"][:5]:
            L.append("- for %s: `%s`" % (ago(p["age"]), short(p["cmd"], 130).replace("`", "'")))
    if tx:
        if tx["helpers"]:
            L.append("")
            L.append("Helpers working:")
            L.append("")
            for h in tx["helpers"][:6]:
                L.append("- %s (last wrote %s ago)" % (h["what"], ago(h["quiet"])))
        if tx["said"]:
            L.append("")
            L.append("Last said, %s ago: *%s*" % (ago(now_s() - (tx["said_t"] or tx["mtime"])), short(tx["said"], 340).replace("*", "")))
        if tx["tools"]:
            L.append("")
            L.append("Last steps:")
            L.append("")
            for row in tx["tools"][-8:]:
                L.append("- %s ago: %s%s" % (ago(now_s() - row["t"]) if row["t"] else "?", row["line"].replace("`", "'"), " (**failed**)" if row.get("failed") else ""))
        if tx["files"]:
            L.append("")
            L.append("Files it has been editing: " + ", ".join(
                "`%s`" % os.path.basename(p) + (" (%d)" % n if n > 1 else "") for p, n in tx["files"].most_common(8)) + ".")
    L.append("")

    # Warnings
    if r["warnings"]:
        L.append("### Warning signs")
        L.append("")
        for w in r["warnings"]:
            L.append("- %s" % w)
        L.append("")

    # Questions in full
    if r["qs"]:
        L.append("### Written for you, QUESTIONS.md, %s old" % ago(now_s() - r["questions_t"]))
        L.append("")
        for q in r["qs"]:
            body = re.sub(r"(?m)^#+\s*", "**", q["text"].split("\n", 1)[0]) + ("**" if q["text"].startswith("#") else "")
            rest = q["text"].split("\n", 1)[1].strip() if "\n" in q["text"] else ""
            L.append(body + (" (*for your information*)" if q["fyi"] else ""))
            if rest:
                L.append("")
                L.append(rest)
            L.append("")

    # North star and count
    L.append("### Bars")
    L.append("")
    ns = r.get("ns")
    if un.get("north star"):
        L.append("North star: UNMEASURED (%s)." % un["north star"])
    elif ns:
        L.append("North star for %s: **%s**, %d must-show and %d cannot-show lines." % (ns["mod"], ns["state"], ns["must"], ns["cannot"]))
    prog = r.get("prog")
    if un.get("progress"):
        L.append("")
        L.append("Progress: UNMEASURED (%s)." % un["progress"])
    elif prog:
        c = prog["counts"]
        L.append("")
        if sum(c.values()):
            L.append("Its own running count, which runs optimistic: **%d true, %d false, %d unseen**, of %d lines (PROGRESS.md, %s old)." % (
                c["true"], c["false"], c["unseen"], sum(c.values()), ago(now_s() - r["progress_t"])))
            shown = [x for x in prog["rows"] if x[1] != "true"][:12]
            if shown:
                L.append("")
                L.append("Not yet true by its own count:")
                L.append("")
                for bar, val, note in shown:
                    L.append("- %s: %s%s" % (bar, val, ", " + note if note else ""))
        else:
            L.append("No running count in PROGRESS.md yet (%s old)." % ago(now_s() - r["progress_t"]))
        if prog["state"]:
            L.append("")
            L.append("Its notes open with: *%s*" % prog["state"].replace("*", ""))
    L.append("")

    # Claims and verdicts
    if r.get("done") or r["verdicts"] or r["claims"] or r.get("look_t") or r.get("note_pending") or r.get("note_delivered"):
        L.append("### Claims, judges and notes")
        L.append("")
        if r.get("done"):
            L.append("- **DONE.md**, %s old: %s" % (ago(now_s() - r["done"]["t"]), r["done"]["first"]))
        if r["claims"]:
            L.append("- Earlier claims set aside: %d." % len(r["claims"]))
        for v in r["verdicts"][-3:]:
            what = v["counts"] or v["call"] or "no count line found; read it"
            L.append("- Blind judge `%s`, %s old: %s" % (v["file"], ago(now_s() - v["t"]), what))
        if r.get("look_t"):
            title = (r["look"] or "").strip().splitlines()[0].lstrip("# ") if (r["look"] or "").strip() else "empty"
            L.append("- **LOOK.md**, %s old: %s" % (ago(now_s() - r["look_t"]), short(title, 100)))
        if r.get("note_pending"):
            L.append("- **Your note is waiting**, %s old; the loop gets it on its next command%s: %s" % (
                ago(now_s() - r["note_pending"]["t"]), "" if r["model"] else ", and none is running", r["note_pending"]["first"]))
        if r.get("note_delivered"):
            L.append("- Your last note reached it %s ago: %s" % (ago(now_s() - r["note_delivered"]["t"]), r["note_delivered"]["first"]))
        L.append("")

    # Commits
    L.append("### Commits")
    L.append("")
    if un.get("git"):
        L.append("UNMEASURED (%s)." % un["git"])
    else:
        rows = r["commits"]
        if r["unpushed"] is None:
            pushed = "this clone has no origin copy of the branch, so pushed state is UNMEASURED"
        elif r["unpushed"] == 0:
            pushed = "all pushed, by this clone's last push"
        else:
            pushed = "**%d not pushed**" % r["unpushed"]
        L.append("%s; %d files edited and uncommitted." % (pushed[0].upper() + pushed[1:], r["dirty"] or 0))
        L.append("")
        for c in rows[:5]:
            L.append("- `%s`, %s ago: %s" % (c["sha"], ago(now_s() - c["t"]), short(c["subject"], 100)))
    L.append("")

    # Pass table
    if r["passes"]:
        L.append("### Passes")
        L.append("")
        L.append("| Pass | Started | Ran | Tokens | Commits | Ended |")
        L.append("|---|---|---|---|---|---|")
        for p in r["passes"][-10:]:
            spent = (p["t_end"] - p["t_start"]) if p["t_end"] is not None else r.get("live_tokens")
            if p["end"] is None:
                end = "running"
            elif p["lost"]:
                end = "**no end line**"
            else:
                end = "clean" if p["rc"] == 0 else "**rc %s**" % p["rc"]
            L.append("| %d | %s | %s | %s | %s | %s |" % (
                p["n"], clock(p["start"]), ago((p["end"] or now_s()) - p["start"]), toks(spent),
                "UNMEASURED" if p.get("commits") is None else p["commits"], end))
        L.append("")
    if r["events"]:
        L.append("Last line of its log, %s: `%s`" % (clock(r["events"][-1][0]), short(r["events"][-1][1], 110).replace("`", "'")))
        L.append("")
    return L


# ---- the picture at the top of the page -------------------------------------------------------------
# Inline SVG, viewed in Typora: one line with no blank line in it (a blank line ends Typora's HTML block and spills the rest
# as text), no <details> (a click marks the page edited). It paints its own dark card, so it reads the same in a light or dark
# theme. His window's column is about 765 px, so 1040 units draw at 0.73 scale: no text under 10.5 units.

PIC_W = 1040
BG, CARD, EDGE, TEXT, DIM, FAINT = "#14171c", "#1f242c", "#3a4250", "#e8eaee", "#a2abb8", "#5d6675"
ALERT = "#ff8a7a"           # text and marks that want him; always beside a word, never colour alone
BARE, FALSE_BAR, OPEN_BAR = "#dfe3ea", "#ff5a4d", "#3a4250"
INK = "#0b0f14"             # labels on a coloured layer
ARC_COLOUR = {"wait": "#b28a00", "game": "#2aa98a", "build": "#b277d6", "code": "#e0713f", "think": "#4f97d6", "idle": "#6b7380"}
ARC_WORD = {"wait": "waiting", "game": "game", "build": "building", "code": "writing code", "think": "thinking", "idle": "idle"}
ARC_LONG = {"wait": "waiting for the game or a long run", "game": "driving the game and looking at it", "build": "building, testing, deploying",
            "code": "writing code", "think": "reading and thinking", "idle": "idle or stalled"}
ARC_STACK = ("wait", "game", "build", "code", "think", "idle")  # waiting on the baseline: it is the one to compare pass to pass
GAP_WORD = {"queue": "queued for the game", "claimed": "said done, waiting on review", "stopped": "stopped", "limit": "at its token limit"}
WINDOW_S = 24 * 3600
LANE_L, LANE_R, SIDE_X = 12, 836, 850
SIDE_CHARS = 33


class Pic:
    def __init__(self):
        self.parts = []

    def rect(self, x, y, w, h, fill, rx=0, title=None):
        body = "<title>%s</title>" % escape(title) if title else ""
        self.parts.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s"%s>%s</rect>' % (x, y, max(w, 0), h, fill, ' rx="%s"' % rx if rx else "", body))

    def line(self, x1, y1, x2, y2, colour=EDGE, width=1, dash=None):
        self.parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="%s"%s/>' % (x1, y1, x2, y2, colour, width, ' stroke-dasharray="%s"' % dash if dash else ""))

    def text(self, x, y, words, size=11, colour=TEXT, weight=None, anchor=None):
        self.parts.append('<text x="%.1f" y="%.1f" font-size="%s" fill="%s"%s%s>%s</text>' % (
            x, y, size, colour, ' font-weight="%s"' % weight if weight else "", ' text-anchor="%s"' % anchor if anchor else "", escape(str(words))))

    def diamond(self, x, y, fill, title=None):
        body = "<title>%s</title>" % escape(title) if title else ""
        self.parts.append('<path d="M%.1f %.1f l6 6 l-6 6 l-6 -6 z" fill="%s" stroke="%s">%s</path>' % (x, y, fill, BG, body))

    def out(self, h, label):
        hatch = ('<defs><pattern id="arcHatch" patternUnits="userSpaceOnUse" width="7" height="7" patternTransform="rotate(45)"><rect width="7" height="7" fill="#2a2f38"/>'
                 '<rect width="2.5" height="7" fill="#7d8796"/></pattern></defs>')
        return ('<div><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="100%%" role="img" aria-label="%s" style="max-width:%dpx;font-family:\'Segoe UI\',Helvetica,Arial,sans-serif">%s'
                '<rect width="%d" height="%d" rx="10" fill="%s"/>%s</svg></div>' % (PIC_W, h, escape(label, {'"': "&quot;"}), PIC_W, hatch, PIC_W, h, BG, "".join(self.parts)))


def text_w(words, size):
    return len(str(words)) * size * 0.53


def gaps_of(rec):
    """The stretches between passes, from the shell's own lines: (from, to, kind)."""
    out, ev = [], rec["events"]
    for i, (t, text) in enumerate(ev):
        to = ev[i + 1][0] if i + 1 < len(ev) else now_s()
        low = text.lower()
        if text.startswith("GAME_WAIT"):
            out.append((t, to, "queue"))
        elif text.startswith("LOOP DONE_CLAIMED"):
            out.append((t, to, "claimed"))
        elif low.startswith("loop paused_for_review"):
            out.append((t, to, "limit"))
        elif low.startswith("loop stopped"):
            out.append((t, to, "stopped"))
    return out


def own_counts(rec):
    """The loop's own count at the end of each pass, with today's file standing in for the live pass."""
    pts = [(a["n"], a["bars"]) for a in rec["arc"] or [] if a.get("bars")]
    counts = rec["prog"]["counts"] if rec.get("prog") else None
    if rec.get("open_pass") and counts and sum(counts.values()):
        pts.append((rec["open_pass"]["n"], {k: counts[k] for k in ("true", "false", "unseen")}))
    return pts


def judged(rec):
    """Each judge's answer in order, with what repeats from the one before."""
    out, prev = [], None
    for v in rec["verdicts"]:
        v = dict(v)
        v["repeat"] = sorted(set(v.get("short") or []) & set(prev)) if prev is not None else []
        out.append(v)
        prev = v.get("short") or []
    return out


def better_words(rec):
    """(word, lines) for "is it getting better". A word only when there is enough history to earn it."""
    pts = own_counts(rec)
    js = judged(rec)
    lines = []
    if len(pts) >= 3:
        recent = [b["true"] for _, b in pts[-4:]]
        lines.append("Bars met, by its own count: %s of %d." % (", ".join(map(str, recent)), sum(pts[-1][1].values())))
        agreed = js and js[-1].get("answer") == "yes" and rec.get("arc") and (js[-1].get("t") or 0) >= rec["arc"][-1]["end"]
        word = "not by its own count" if recent[-1] <= recent[0] else "yes, and the judge agrees" if agreed else "only by its own count"
    elif pts:
        lines.append("Bars met, by its own count: %d of %d." % (pts[-1][1]["true"], sum(pts[-1][1].values())))
        word = "too few to say"
    else:
        word = "too few to say" if js else "nothing to judge by yet"
        if not js:
            lines.append("It keeps no count of its own.")
    if not js:
        lines.append("No judge yet.")
    else:
        said = {"no": "no", "yes": "yes"}.get(js[-1].get("answer"), "unclear")
        seq = ", then ".join("%s of %s" % (v["passed"], v["lines"]) if v.get("lines") else "unread" for v in js)
        at = [a["n"] for a in rec.get("arc") or [] if js[-1].get("t") and a["end"] <= js[-1]["t"]]
        where = " after pass %d" % at[-1] if at and len(js) == 1 else ""
        lines.append("Judge said %s%s: %s lines passed." % (said, where, seq))
        rep = js[-1]["repeat"]
        if rep:
            lines.append("%d line%s refused both times." % (len(rep), "" if len(rep) == 1 else "s"))
        if len(js) < 3:
            lines.append("One judgement is no trend." if len(js) == 1 else "Two judgements are no trend.")
        else:
            a, b = len(js[-3].get("short") or []), len(js[-1].get("short") or [])
            lines.append("Refusals %s over 3 judgements." % ("shrinking" if b < a else "growing" if b > a else "not shrinking"))
    return word, lines


def wants(rec):
    """What this loop wants from him, in the fewest words."""
    out = []
    state = rec["state"]
    if state in ("dead", "stuck", "unmeasured"):
        out.append({"dead": "dead: restart or retire", "stuck": "looks stuck", "unmeasured": "can't be read"}[state])
    if state == "done claimed":
        out.append("says done: your look")
    if state == "paused for review" or (state == "stopped" and at_limit(rec)):
        out.append("at its token limit: your word")
    if state == "stopped" and not rec.get("stop_reason") and not at_limit(rec):
        out.append("stopped, nobody said why")
    real = [q for q in rec.get("qs") or [] if not q["fyi"]]
    if real:
        out.append("%d question%s for you" % (len(real), "" if len(real) == 1 else "s"))
    if rec.get("look_t"):
        out.append("an early look for you")
    if state == "working" and rec.get("eta_s") is not None and rec["eta_s"] < 2 * 3600:
        out.append("token limit in about %s" % ago(rec["eta_s"]))
    return out


def now_words(rec):
    """(colour of what it is doing, the state, what it is doing)."""
    state = rec["state"]
    arc = rec.get("arc") or []
    live = arc[-1] if arc and arc[-1].get("live") else None
    kind = ARC_OF_LETTER.get(live["bins"][-1]) if live and live.get("bins") else None
    word = {"waiting for game": "queued for the game", "done claimed": "said done", "paused for review": "at its token limit"}.get(state, state)
    if state == "waiting for game" and rec.get("wait_on"):
        word = "queued behind %s" % ", ".join(rec["wait_on"])
    quiet = now_s() - rec["last_active"] if rec.get("last_active") else None
    tx = rec.get("tx")
    if state == "working" and rec.get("open_pass"):
        what = "pass %d, %s in" % (rec["open_pass"]["n"], ago(now_s() - rec["open_pass"]["start"]))
        if tx and tx["tools"]:
            what += ": " + tx["tools"][-1]["line"].replace("ran: ", "", 1)
        return ARC_COLOUR.get(kind or "think"), word, what
    if state == "waiting for game":
        return ARC_COLOUR["wait"], word, "for %s, spending nothing" % ago(now_s() - rec["events"][-1][0])
    if state == "stopped":
        return ARC_COLOUR["idle"], word, rec.get("stop_reason") or ("for %s" % ago(quiet) if quiet is not None else "")
    return ARC_COLOUR["idle"], word, "for %s" % ago(quiet) if quiet is not None else ""


def draw_axis(p, tmin, tmax, sx, y0, y1, now):
    """Hour marks in real time. Labels every 2 hours, or every 4 when the window is long."""
    step = 4 if tmax - tmin > 18 * 3600 else 2
    d = dt.datetime.fromtimestamp(tmin).replace(minute=0, second=0, microsecond=0)
    while d.timestamp() < tmax:
        t = d.timestamp()
        if t >= tmin and d.hour % step == 0:
            p.line(sx(t), y0, sx(t), y1, "#262b34")
            if sx(now) - sx(t) > 34:
                p.text(sx(t), y0 - 4, d.strftime("%b %-d") if d.hour == 0 else d.strftime("%H:%M"), 10.5, TEXT if d.hour == 0 else DIM, "600" if d.hour == 0 else None, "middle")
        d += dt.timedelta(hours=1)


def draw_pass(p, a, sx, tmin, y, height, rec):
    """One pass: width is its real time, layers its split, waiting on the baseline. Broken data is hatched and says so."""
    x0, x1 = sx(max(a["start"], tmin)), sx(a["end"])
    w = max(x1 - x0 - 1.5, 2)
    tokens = a.get("tokens")
    head = str(a["n"])
    p.text(x0, y - 3, head, 10.5, TEXT, "700")
    if tokens and w > 40:
        p.text(x0 + text_w(head, 10.5) + 5, y - 3, toks(tokens), 10.5, DIM)
    if a.get("broken") or not a.get("sec"):
        why = a.get("broken") or "no time read"
        p.rect(x0, y, w, height, "url(#arcHatch)", 0, "pass %d: %s" % (a["n"], why))
        return
    total = max(1, sum(a["sec"].values()))
    title = "pass %d, %s to %s: %s" % (a["n"], clock(a["start"]), clock(a["end"]), ", ".join(
        "%s %d min" % (ARC_WORD[k], round(a["sec"][k] / 60)) for k in ARC_STACK if a["sec"].get(k, 0) >= 30))
    title += "; %s tokens; %d commits" % (toks(tokens), len(a.get("commits") or []))
    bottom = y + height
    for k in ARC_STACK:
        h = height * a["sec"].get(k, 0) / total
        if h <= 0:
            continue
        p.rect(x0, bottom - h, w, h, ARC_COLOUR[k], 0, title)
        minutes = round(a["sec"][k] / 60)
        word = "%s %d min" % (ARC_WORD[k], minutes)
        if h >= 13 and w >= text_w(word, 10.5) + 6:
            p.text(x0 + 3, bottom - h / 2 + 3.7, word, 10.5, INK, "600")
        elif h >= 13 and w >= text_w("%d min" % minutes, 10.5) + 6:
            p.text(x0 + 3, bottom - h / 2 + 3.7, "%d min" % minutes, 10.5, INK, "600")
        bottom -= h
    for c in a.get("commits") or []:
        p.line(sx(c), y + height, sx(c), y + height + 4, TEXT)
    for t in a.get("notes") or []:
        p.parts.append('<path d="M%.1f %.1f l4 6 h-8 z" fill="%s"><title>your note reached it, %s</title></path>' % (sx(t), y + height, ALERT, clock(t)))


def draw_count(p, x, y, w, b, q):
    """The loop's own count at the end of a pass: filled true, red false, dark unseen, with the numbers when they fit."""
    total = max(1, sum(b.values()))
    at = x
    for k, colour in (("true", BARE), ("false", FALSE_BAR), ("unseen", OPEN_BAR)):
        part = w * b[k] / total
        if part > 0:
            p.rect(at, y, max(part - 0.8, 0.5), 9, colour)
        at += part
    words = "%d of %d" % (b["true"], total)
    if w < text_w(words, 10.5) + 2:
        words = "%d/%d" % (b["true"], total)
    if w >= text_w(words, 10.5):
        p.text(x, y + 20, words, 10.5, TEXT)
        if b["false"] and w >= text_w(words + " %d failed" % b["false"], 10.5) + 6:
            p.text(x + text_w(words, 10.5) + 5, y + 20, "%d failed" % b["false"], 10.5, ALERT)


def draw_loop(p, rec, y, tmin, sx):
    """One loop's row. Returns its height."""
    colour, word, what = now_words(rec)
    p.parts.append('<circle cx="%d" cy="%.1f" r="5" fill="%s"/>' % (LANE_L + 5, y + 8, colour))
    p.text(LANE_L + 15, y + 13, rec["name"], 15, TEXT, "700")
    x = LANE_L + 15 + text_w(rec["name"], 15) + 8
    p.text(x, y + 13, word, 12, TEXT, "600")
    x += text_w(word, 12) + 8
    room = int((SIDE_X - x) / (10.5 * 0.53))
    p.text(x, y + 13, short(what, room), 10.5, DIM)
    blocks_y = y + 34
    height = 52
    if rec.get("arc_why"):
        p.text(LANE_L, blocks_y + 18, "Passes could not be read: %s" % short(rec["arc_why"], 90), 11, ALERT)
    arc = rec.get("arc") or []
    if not arc and not rec.get("arc_why"):
        p.text(LANE_L, blocks_y + 18, "No passes on record yet.", 11, DIM)
    gaps = [g for g in gaps_of(rec) if g[1] > tmin]
    for a, b, kind in gaps:
        a = max(a, tmin)
        mid = blocks_y + height / 2
        p.line(sx(a), mid, sx(b), mid, ARC_COLOUR["wait"] if kind == "queue" else "#7d8796", 2, "2 4")
        label = GAP_WORD[kind]
        if sx(b) - sx(a) > text_w(label, 10.5) + 8:
            p.text((sx(a) + sx(b)) / 2, mid - 5, label, 10.5, ARC_COLOUR["wait"] if kind == "queue" else DIM, None, "middle")
    earlier = sum(1 for a in arc if a["end"] <= tmin)
    if earlier:
        p.text(LANE_L, blocks_y - 3, "+%d earlier" % earlier, 10.5, FAINT)
    broken = []
    prev_effort = None
    for a in arc:
        tokens_known = next((q for q in rec["passes"] if q["n"] == a["n"]), None)
        if tokens_known:
            spent = tokens_known["t_end"] - tokens_known["t_start"] if tokens_known["t_end"] is not None else rec.get("live_tokens")
            a["tokens"] = spent
            a["commits"] = [c["t"] for c in rec["commits"] if tokens_known["start"] <= c["t"] <= (tokens_known["end"] or now_s())]
        if a["end"] > tmin:
            draw_pass(p, a, sx, tmin, blocks_y, height, rec)
            b = a.get("bars")
            if a.get("live") and not b:
                pts = own_counts(rec)
                b = pts[-1][1] if pts and pts[-1][0] == a["n"] else None
            if b:
                x0 = sx(max(a["start"], tmin))
                draw_count(p, x0, blocks_y + height + 7, max(sx(a["end"]) - x0 - 1.5, 2), b, a.get("q"))
            effort = a.get("effort")
            if effort and prev_effort and effort != prev_effort:
                x0 = sx(a["start"])
                p.line(x0, blocks_y - 16, x0, blocks_y + height, ALERT, 1.5)
                p.text(x0 - 3, blocks_y - 16, "%s effort from here" % effort, 10.5, ALERT, "600", "end")
        if a.get("broken") and a["end"] > tmin and a["broken"] != "still being read":
            broken.append("pass %d: %s" % (a["n"], a["broken"]))
        elif a.get("broken") == "still being read":
            broken.append("pass %d: still being read" % a["n"])
        if a.get("effort"):
            prev_effort = a["effort"]
    last_x = None
    counted = bool(own_counts(rec))
    judge_y = blocks_y + height + (26 if counted else 8)
    for v in judged(rec):
        if v.get("t") is None or v["t"] < tmin:
            continue
        vx = sx(v["t"])
        said = {"no": "judge said no", "yes": "judge said yes"}.get(v.get("answer"), "judge: answer unclear")
        words = "%s, %s of %s" % (said, v["passed"], v["lines"]) if v.get("lines") else said
        p.diamond(vx, judge_y, FALSE_BAR if v.get("answer") == "no" else BARE, short(v.get("call") or v.get("counts") or "", 200))
        anchor = "end" if vx + 10 + text_w(words, 10.5) > LANE_R else None
        p.text(vx + (-9 if anchor else 9), judge_y + 10, words, 10.5, TEXT, "600", anchor)
        last_x = vx
    # the side column: tokens, then is it getting better, then what it wants
    sy = y + 13
    if rec.get("total") is not None and rec.get("limit"):
        frac = rec["total"] / rec["limit"]
        p.text(SIDE_X, sy, "%s of %s tokens" % (toks(rec["total"]), toks(rec["limit"])), 10.5, DIM)
        p.rect(SIDE_X, sy + 4, 178, 4, EDGE, 2)
        p.rect(SIDE_X, sy + 4, 178 * min(1, frac), 4, FALSE_BAR if frac >= 0.9 else BARE, 2)
    elif rec.get("total") is None:
        p.text(SIDE_X, sy, "tokens: no reading", 10.5, ALERT)
    sy += 24
    word, lines = better_words(rec)
    p.text(SIDE_X, sy, "Better? " + word, 12, TEXT, "700")
    sy += 14
    for ln in lines:
        for piece in textwrap.wrap(ln, SIDE_CHARS):
            p.text(SIDE_X, sy, piece, 10.5, DIM)
            sy += 13
    for line in broken[:3]:
        for piece in textwrap.wrap("Can't draw " + line, SIDE_CHARS):
            p.text(SIDE_X, sy, piece, 10.5, ALERT, "600")
            sy += 13
    for want in wants(rec):
        p.parts.append('<circle cx="%d" cy="%.1f" r="3" fill="%s"/>' % (SIDE_X + 3, sy - 4, ALERT))
        for i, piece in enumerate(textwrap.wrap(want, SIDE_CHARS - 2)):
            p.text(SIDE_X + 10, sy, piece, 10.5, ALERT, "600")
            sy += 13
    below = judge_y - blocks_y - height + 18 if last_x is not None else (24 if counted else 10)
    return max(blocks_y + height + below - y, sy - y + 4)


def draw_games(p, loops, world, y, tmin, sx):
    """Who drove each game when. Above: holds, labelled by loop. Under: each running game, a row per game when they overlap, red ticks for freezes."""
    for name, letter in (("Archmagi", "A"), ("SteveDesktop", "S")):
        m = (world.get("machines") or {}).get(name) or {}
        d = m.get("data") or {}
        for r in loops:
            held = []
            for a in r.get("arc") or []:
                for g in a.get("game") or []:
                    if g[2] != letter or g[1] <= tmin:
                        continue
                    if held and g[0] - held[-1][1] < HOLD_MERGE_S:
                        held[-1][1] = g[1]
                    else:
                        held.append([g[0], g[1]])
            for a, b in held:
                x0, x1 = sx(max(a, tmin)), sx(b)
                p.rect(x0, y, max(x1 - x0, 2), 17, ARC_COLOUR["game"], 2, "%s drove this game, %s to %s" % (r["name"], clock(a), clock(b)))
                label = next((w for w in (r["name"], r["name"][:3]) if x1 - x0 > text_w(w, 10.5) + 5), None)
                if label:
                    p.text(x0 + 3, y + 12.5, label, 10.5, INK, "600")
        rows = []
        stalls = 0
        for g in d.get("sessions") or []:
            if g["end"] <= tmin:
                continue
            row = next((i for i, last in enumerate(rows) if g["start"] > last), None)
            if row is None:
                rows.append(0)
                row = len(rows) - 1
            rows[row] = g["end"]
            yy = y + 20 + min(row, 2) * 4
            p.rect(sx(max(g["start"], tmin)), yy, max(sx(g["end"]) - sx(max(g["start"], tmin)), 1), 3, "#5f6878")
            for t, _gap in g.get("stalls") or []:
                if t > tmin:
                    stalls += 1
        tick_y = y + 20 + min(max(len(rows), 1), 3) * 4
        for g in d.get("sessions") or []:
            for t, gap in g.get("stalls") or []:
                if t > tmin:
                    p.line(sx(t), tick_y, sx(t), tick_y + 5, FALSE_BAR)
        sy = y + 11
        p.text(SIDE_X, sy, "%s game" % name, 12, TEXT, "700")
        sy += 14
        if not m.get("fresh") and not d:
            p.text(SIDE_X, sy, "no reading: %s" % short(m.get("why"), SIDE_CHARS - 12), 10.5, ALERT)
        else:
            games = d.get("games") or []
            old = "" if m.get("fresh") else ", from an old reading"
            if len(games) > 1:
                words = "%d games running, ports %s%s" % (len(games), " and ".join(game_ports(games)), old)
                colour, weight = ALERT, "600"
            elif d.get("game"):
                ports = d.get("ports") or []
                words = "running, port %s%s" % (", ".join(ports) or "not up yet", old)
                colour, weight = DIM, None
            elif d.get("game") is False:
                words, colour, weight = "not running" + old, DIM, None
            else:
                words, colour, weight = "state unknown", ALERT, None
            p.text(SIDE_X, sy, short(words, SIDE_CHARS + 6), 10.5, colour, weight)
            sy += 13
            if d.get("sessions"):
                for piece in textwrap.wrap("Grey: game open. %s" % ("Red: %d freeze%s of 1 s or more." % (stalls, "" if stalls == 1 else "s") if stalls else "No freezes of 1 s or more."), SIDE_CHARS):
                    p.text(SIDE_X, sy, piece, 10.5, DIM)
                    sy += 13
        y += 58 + max(0, len(rows) - 1) * 4
    return y


def arc_picture(loops, world):
    """The picture at the top of the page: one glance at what each loop does, where its time went, whether it is winning, what it wants."""
    now = now_s()
    starts = [a["start"] for r in loops for a in r.get("arc") or [] if a["end"] > now - WINDOW_S]
    tmin = min(starts) if starts else now - 6 * 3600
    tmin = max(tmin, now - WINDOW_S) - 300
    tmax = now + 300
    span = max(1, tmax - tmin)
    sx = lambda t: LANE_L + (t - tmin) / span * (LANE_R - LANE_L)  # noqa: E731
    p = Pic()
    x = LANE_L
    for k in ARC_STACK:
        word = "waiting, for the game or a long run" if k == "wait" else ARC_WORD[k]
        p.rect(x, 12, 11, 11, ARC_COLOUR[k], 2)
        p.text(x + 15, 22, word, 11, TEXT)
        x += 15 + text_w(word, 11) * 0.88 + 11
    p.line(x + 3, 13, x + 3, 22, TEXT)
    p.text(x + 8, 22, "commit", 11, DIM)
    x += 8 + text_w("commit", 11) + 12
    p.parts.append('<path d="M%.1f 15 l4 6 h-8 z" fill="%s"/>' % (x, ALERT))
    p.text(x + 8, 22, "your note", 11, DIM)
    p.text(PIC_W - 12, 22, "as of %s" % clock(now), 11, TEXT, "600", "end")
    p.text(LANE_L, 39, "Each block is one numbered pass, tokens above it, its width its real time.", 11, DIM)
    x = LANE_L + text_w("Each block is one numbered pass, tokens above it, its width its real time.", 11) * 0.9
    p.text(x, 39, "Under it, bars met by its own count:", 11, DIM)
    x += text_w("Under it, bars met by its own count:", 11) * 0.9 + 4
    for word, colour in (("met", BARE), ("failed", FALSE_BAR), ("unseen", OPEN_BAR)):
        p.rect(x, 30, 11, 10, colour)
        p.text(x + 14, 39, word, 11, TEXT)
        x += 14 + text_w(word, 11) + 9
    body = Pic()
    y = 70
    for rec in loops:
        y += draw_loop(body, rec, y, tmin, sx) + 8
    y = draw_games(body, loops, world, y + 4, tmin, sx)
    draw_axis(p, tmin, tmax, sx, 62, y - 6, now)
    p.line(sx(now), 62, sx(now), y - 6, TEXT, 1)
    p.text(sx(now), 58, "now", 10.5, TEXT, "700", "middle")
    p.parts += body.parts
    words = "; ".join("%s %s" % (r["name"], now_words(r)[1]) for r in loops) or "no loops"
    return p.out(y + 2, "Artisan loops, on one clock: " + words)


def glance_table(loops):
    L = ["| Loop | State | Game on | Pass | Tokens | Rate | Last active | Bars true / false / unseen |", "|---|---|---|---|---|---|---|---|"]
    for r in loops:
        op = r["open_pass"]
        pc = "%s %s%s" % (op["n"] if op else (r["passes"][-1]["n"] if r["passes"] else "none"),
                          "for " if op else "", ago(now_s() - op["start"]) if op else "ended")
        tok = "UNMEASURED" if r["total"] is None else toks(r["total"])
        if r["total"] is not None and r["limit"]:
            tok += " of %s, %d%%" % (toks(r["limit"]), round(100 * r["total"] / r["limit"]))
        rate = "%s/h" % toks(r["rate"]) if r.get("rate") and r["state"] == "working" else "none"
        c = r["prog"]["counts"] if r.get("prog") else None
        bars = "UNMEASURED" if not c and r["unmeasured"].get("progress") else ("%d / %d / %d" % (c["true"], c["false"], c["unseen"]) if c and sum(c.values()) else "no count")
        quiet = ago(now_s() - r["last_active"]) + " ago" if r.get("last_active") else "UNMEASURED"
        L.append("| **%s** | %s | %s | %s | %s | %s | %s | %s |" % (
            cell(r["name"]), cell(STATE_WORD.get(r["state"], r["state"])), r["machine"], pc, tok, rate, quiet, bars))
    return L


def guarded(fn, *args):
    """(value, None), or (None, reason) when it could not be read."""
    try:
        return fn(*args), None
    except Unmeasured as e:
        return None, str(e)
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as e:
        return None, "%s: %s" % (type(e).__name__, short(e, 110))


def build():
    t0 = time.time()
    sources = Sources()
    state = load_state()
    tally_cache = state.get("tally") or {}
    loops, old_logs, units_error = discover(sources)
    for rec in loops:
        try:
            collect_loop(rec, sources, tally_cache)
        except Exception as e:      # one broken loop must not blank the page
            rec.setdefault("unmeasured", {})["loop"] = "%s: %s" % (type(e).__name__, short(e, 140))
            for k, v in (("events", []), ("passes", []), ("open_pass", None), ("total", None), ("warnings", []), ("qs", []),
                         ("verdicts", []), ("claims", []), ("procs", []), ("model", False), ("limit", None), ("machine", "Archmagi"),
                         ("gate", {"ahead": [], "game": None, "soft": SOFT_CONTEXT, "firm": FIRM_CONTEXT}),
                         ("loopsh", {"busy_units": []}), ("commits", []), ("state", "dead"), ("state_why", "the sheet could not read it: %s" % e)):
                rec.setdefault(k, v)
            sources.add("loop %s" % rec["name"], None, rec["unmeasured"]["loop"])
        prepare_safe(rec)
    state["tally"] = {p: c for p, c in tally_cache.items() if now_s() - (mtime(p) or 0) < 86400}
    arc_cache = state.get("arc") or {}
    arc_deadline = time.time() + ARC_BUDGET_S
    for rec in loops:
        rec["arc"], rec["arc_why"] = guarded(read_arc, rec, arc_cache, arc_deadline)
    state["arc"] = arc_cache

    world = {"machines": read_machines(state, sources)}
    fault_data, fault_why = guarded(read_fault, sources)
    tailscale, ts_why = guarded(read_tailscale)
    accounts, acct_why = guarded(read_accounts, sources)
    bridge, bridge_why = guarded(read_bridge)
    bg, bg_why = guarded(read_background, sources)
    score, score_why = guarded(read_scoreboard)
    fault = {"state": fault_data[0], "windows": fault_data[1]} if fault_data else None

    check_waits(loops)
    needs = needs_you(loops, fault, world)
    spend = sum(r.get("spend_today") or 0 for r in loops)
    head = one_line(loops, needs, spend)
    stamp = "Generated %s, by `artisan_now.py`, no model called." % dt.datetime.fromtimestamp(now_s()).astimezone().strftime("%b %-d, %H:%M:%S %Z")

    try:
        picture, picture_why = arc_picture(loops, world), None
    except Exception as e:      # a page without its picture still says everything else
        picture, picture_why = None, "%s: %s" % (type(e).__name__, short(e, 110))
    L = ["# Artisan now", "", picture if picture else "*The picture could not be drawn: %s*" % picture_why, "", "**%s**" % head, "", "%s Written every minute: over 3 minutes old means the timer is dead." % stamp, ""]
    if units_error:
        L += ["**Unit states are UNMEASURED: %s.** States below come from logs alone." % units_error, ""]
    L += ["## Needs you", ""]
    if needs:
        L += ["%d. %s" % (i + 1, t) for i, (_, t) in enumerate(needs)]
    else:
        L.append("Nothing right now.")
    L.append("")
    L += ["## Loops at a glance", ""] + glance_table(loops) + [""]
    L.append("Bars are each loop's own count, which runs optimistic. Commits and tokens show a loop is alive, not that it is winning.")
    if score:
        L.append("Scoreboard: %s." % score)
    L.append("")

    L += games_section(loops, world, bridge, bridge_why, fault, fault_why, tailscale, ts_why)
    L += tokens_section(loops, spend, accounts, acct_why)
    L += background_section(bg, bg_why, old_logs)
    for r in loops:
        L += loop_section(r, world["machines"])
    L += ["## Sources and how old each is", "", "| Source | Age | Note |", "|---|---|---|"]
    for name, age, why in sources.rows:
        if why:
            L.append("| %s | **UNMEASURED** | %s |" % (cell(name), cell(short(why, 130))))
        else:
            L.append("| %s | %s | |" % (cell(name), "read now" if age == 0 else ago(age)))
    took = time.time() - t0
    L += ["", "Built in %.1f s." % took, "",
          "## How to read this", "",
          "- **working** a pass is running. **waiting for game** the shell holds it with no model running, spending nothing. "
          "**paused for review** it reached its token limit. **stopped** it ended on STOP or its own stop rule. **done claimed** it wrote DONE.md, "
          "which starts a review and is not acceptance. **dead** no unit runs it and its log has no clean finish. **stuck** the unit is up and nothing is happening.",
          "- **Tokens** are weighted: input + output + cache writes + cache reads ÷ 10, as the loop's own `tally.py` counts them. Today's figures spread each pass evenly over its hours, so they carry a ~.",
          "- **The picture's split** comes from each pass's transcript: a shell command counts as game, waiting, building, code or thinking by what it runs, and model time counts as thinking, or code when it ends in an edit. A sleep or a poll can't say what it waits on, so waiting means the game or a long run; a queue for the game is drawn between passes. The model silent 5 minutes with nothing running is idle. The white strips under a pass are the loop's own count at the end of that pass; a diamond is a blind judge's answer.",
          "- **UNMEASURED** means the sheet could not read it, with the reason beside it. It never means zero.",
          "- Relentless lives on its own sheet: `%s\\RELENTLESS_NOW.md`." % NATIVE_OUT, ""]
    page = "\n".join(L)
    phone = phone_page(head, loops, needs, world, spend)
    return page, phone, state


def prepare_safe(rec):
    try:
        prepare(rec)
    except (KeyError, TypeError, ValueError):
        rec.setdefault("rate", None)
        rec.setdefault("rate_basis", None)
        rec.setdefault("eta_s", None)
        rec.setdefault("spend_today", 0)


def games_section(loops, world, bridge, bridge_why, fault, fault_why, tailscale, ts_why):
    L = ["## Games and machines", ""]
    holders = holder_of_game(loops)
    for machine in ("Archmagi", "SteveDesktop"):
        L.append("### %s" % machine)
        L.append("")
        if holders.get(machine):
            h = holders[machine][0]
            L.append("- **Held by %s**, command running %s: `%s`" % (h["loop"], ago(h["age"]), short(h["cmd"], 100).replace("`", "'")))
        else:
            recent = [(last_game_use(r), r) for r in loops if r["machine"] == machine]
            recent = [(u, r) for u, r in recent if u and u["t"]]
            if recent:
                u, r = max(recent, key=lambda x: x[0]["t"])
                L.append("- No loop is running a game command now. Last game command: %s, %s ago." % (r["name"], ago(now_s() - u["t"])))
            else:
                L.append("- No loop is running a game command now.")
        for ln in machine_lines(machine, world["machines"][machine]):
            L.append("- %s" % ln)
        if machine == "Archmagi":
            if bridge:
                who = "held by %s%s" % (bridge["who"] or "someone", ", for: %s" % short(bridge["why"], 70) if bridge["why"] else "") if bridge["state"] == "HELD" else "free"
                L.append("- Bridge lock (the lock file, not the bridge): %s, file %s old." % (who, ago(now_s() - bridge["t"])))
            else:
                L.append("- Bridge lock: UNMEASURED (%s)." % bridge_why)
        else:
            if tailscale:
                on = [p for p in tailscale if p.get("Online")]
                L.append("- Tailscale: %s." % ("online" if on else "**offline**, last seen %s" % clock(max((parse_iso(p.get("LastSeen")) or 0) for p in tailscale))))
            else:
                L.append("- Tailscale: UNMEASURED (%s)." % (ts_why or "no such peer in tailscale status"))
            if fault:
                for ln in fault_lines(fault["state"], fault["windows"], loops):
                    L.append("- %s" % ln)
            else:
                L.append("- CPU fault monitor: UNMEASURED (%s)." % fault_why)
        L.append("")
    q, drift = queue_lines(loops)
    L += ["### Queue for the game", ""]
    L.append("There is no scheduler: each loop's own gate says who it gives way to.")
    L.append("")
    L += ["- %s" % x for x in q] or ["- No loop has a queue list."]
    L += ["- **Check:** %s" % x for x in drift]
    L.append("")
    return L


def tokens_section(loops, spend, accounts, why):
    L = ["## Tokens", ""]
    L.append("Across all loops today: **~%s** weighted (%s)." % (toks(spend), ", ".join("%s ~%s" % (r["name"], toks(r.get("spend_today"))) for r in loops) or "no loops"))
    L.append("")
    if accounts:
        L += ["| Account | Used this week | Resets in | Moving | Read |", "|---|---|---|---|---|"]
        for a in accounts:
            used = ("**%d%%**" if a["used"] >= 90 else "%d%%") % a["used"] if a["used"] is not None else "UNMEASURED (%s)" % short(a.get("why") or "no reading", 50)
            moving = "%+.1f%% an hour" % a["slope"] if a["slope"] is not None else "not enough readings"
            L.append("| %s | %s | %s | %s | %s ago |" % (
                cell(a["name"]), cell(used), ago(a["resets"] - now_s()) if a["resets"] else "UNMEASURED", moving, ago(now_s() - a["t"]) if a["t"] else "UNMEASURED"))
    else:
        L.append("Account readings: UNMEASURED (%s)." % why)
    L.append("")
    return L


def background_section(bg, why, old_logs):
    L = ["## Other background", ""]
    if not bg:
        return L + ["UNMEASURED (%s)." % why, ""]
    if bg.get("detached") is None:
        L.append("- Detached runs: UNMEASURED (%s)." % bg.get("detached_why"))
    else:
        L.append("- Detached runs: %d running%s" % (len(bg["detached"]), "." if not bg["detached"] else ":"))
        for d in bg["detached"][:6]:
            m = re.search(r"item (\S+)", d)
            L.append("  - %s" % short(m[1] if m else d, 90))
    if bg.get("claude") is None:
        L.append("- Live model sessions: UNMEASURED (%s)." % bg.get("proc_why"))
    else:
        L.append("- Live model sessions on Archmagi, by folder: %s." % (", ".join("%s %d" % (k, v) for k, v in bg["claude"].most_common(10)) or "none"))
        L.append("- Watches armed on a loop's events log: **%d**.%s" % (bg["watchers"], " No agent will be woken by a DONE claim or a stop; only this sheet shows them." if not bg["watchers"] else ""))
    if bg.get("failed") is None:
        L.append("- Failed rm-* units: UNMEASURED (%s)." % bg.get("failed_why"))
    else:
        L.append("- Failed rm-* units: %s." % (", ".join(bg["failed"][:10]) if bg["failed"] else "none"))
    if old_logs:
        L.append("- Old loop logs with no clone or unit, not watched here: %s." % ", ".join(os.path.basename(d) for d in old_logs))
    L.append("")
    return L


def better_line(r):
    """The picture's one word for the phone, which stays text: at phone width the picture's labels would be about 4 px."""
    try:
        return better_words(r)[0]
    except Exception:       # the phone is the last thing that should go blank
        return "UNMEASURED"


def phone_page(head, loops, needs, world, spend):
    t = dt.datetime.fromtimestamp(now_s()).astimezone().strftime("%H:%M %Z")
    L = ["Artisan %s" % t, head, ""]
    if needs:
        L.append("NEEDS YOU %d" % len(needs))
        for _, text in needs[:8]:
            L.append("- " + short(text.replace("*", "").replace(" In full under its section.", ""), 150))
        L.append("")
    L.append("LOOPS")
    for r in loops:
        tok = "tokens UNMEASURED" if r["total"] is None else toks(r["total"]) + ("/" + toks(r["limit"]) if r["limit"] else "")
        L.append("%s: %s, %s, %s" % (r["name"], r["state"], r["machine"], tok))
        L.append("  better? %s" % better_line(r))
        tx = r.get("tx")
        if tx and tx["tools"] and r["state"] == "working":
            row = tx["tools"][-1]
            L.append("  %s ago: %s" % (ago(now_s() - row["t"]) if row["t"] else "?", short(row["line"], 80)))
    L += ["", "GAMES"]
    for name, m in world["machines"].items():
        d = m.get("data") or {}
        if not m["fresh"]:
            L.append("%s: UNMEASURED, %s" % (name, short(m["why"], 80)))
            continue
        bits = ["game " + ("up" if d.get("game") else "down" if d.get("game") is False else "UNMEASURED")]
        if len(d.get("games") or []) > 1:
            bits[0] = "%d games up, ports %s" % (len(d["games"]), " and ".join(game_ports(d["games"])))
        if d.get("game") and d.get("ratio_med") is not None and now_s() - d.get("tps_mtime", 0) < 180:
            bits.append("%d%% speed" % round(d["ratio_med"] * 100))
        if d.get("game") and d.get("period"):
            bits.append("freeze %d ms every %d ticks" % (round(d["period"]["ms"]), d["period"]["ticks"]))
        L.append("%s: %s" % (name, ", ".join(bits)))
    return "\n".join(L) + "\n"


def check():
    path = os.path.join(OUT_DIR, "ARTISAN_NOW.md")
    m = mtime(path)
    if m is None:
        print("ARTISAN_NOW.md: missing")
        return 1
    age = now_s() - m
    print("ARTISAN_NOW.md: %s old" % ago(age))
    return 1 if age > STALE_PAGE_S else 0


def main():
    if "--check" in sys.argv:
        return check()
    page, phone, state = build()
    if "--print" in sys.argv:
        print(page)
        return 0
    if "--phone" in sys.argv:
        print(phone)
        return 0
    write_atomic(state_path(), json.dumps(state))
    write_atomic(os.path.join(OUT_DIR, "ARTISAN_NOW.md"), page)
    write_atomic(os.path.join(OUT_DIR, "ARTISAN_NOW_PHONE.md"), phone)
    return 0


if __name__ == "__main__":
    sys.exit(main())
