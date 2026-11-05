#!/usr/bin/env python3
"""pipeline_watch.py -- the Pipeline window's renderer: one station's live worker, readable, at zero tokens.

PIPELINE_WINDOW_BUILD_TABS_NOT_TERMINALS, report step 2 (design/RimMandrake/agent_visibility_2026-11-04/report.md;
owner: "1 yes ... 3 no" -- built now, no phone access). The Pipeline window sits in FOUNDRY's old tile
(launch_fleet.ps1 seat PIPELINE); each of its tabs runs pipeline_watch.sh <station>, which loops this script.

WHAT IT IS NOT. The workers stay supervised systemd units (relentless.py launches them `claude -p`); this file only
READS: the live unit list (`systemctl --user list-units`), the run's clone sidecar (relentless_usage.note_clone) and
the run's own Claude transcript JSONL under ~/.claude/projects/<clone>/. It never runs claude, never calls the
API, and never writes the relentless store, so watching costs zero tokens, closing the window stops nothing and
opening it starts nothing. Its one write is its station map in $XDG_RUNTIME_DIR (tmpfs, gone at reboot).

STATIONS. A tab is a fixed station: B1..B8 (builders, `work` units; relentless_rules max_workers), J1..J4 (judges,
`check` units; check_backlog_max), C1 (the consult, `help` units), and `overview` (every live run, overflow
included). A run keeps the station it first got until its unit ends, so a tab never jumps to another worker
mid-run; a new run takes the lowest free station of its kind (assign()).

    python3 src/RimMandrake/rimflow/pipeline_watch.py B3            # follow station B3 until killed
    python3 src/RimMandrake/rimflow/pipeline_watch.py overview      # the station table, redrawn
    python3 src/RimMandrake/rimflow/pipeline_watch.py B3 --once     # one frame, then exit (tests)
"""
import argparse
import contextlib
import datetime
import fcntl
import hashlib
import json
import os
import re
import subprocess
import sys
import textwrap
import time

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ROOT = "/home/mandrake/rm/relentless"      # relentless.DEFAULT_ROOT; not imported, so a broken relentless.py
                                                   # never blinds the window

# kind -> (station prefix, count, label). Counts mirror relentless_rules.json max_workers / check_backlog_max / one
# consult; a run past the last station of its kind shows in the overview only.
KINDS = {"work": ("B", 8, "Builder"), "check": ("J", 4, "Judge"), "help": ("C", 1, "Consult")}
STATIONS = [p + str(i) for k, (p, n, _) in KINDS.items() for i in range(1, n + 1)]
UNIT_RE = re.compile(r"^claude-seat-.+?-(rm-relentless-(work|check|help)-([0-9a-f]{10})-g(\d+)(?:-[ch]\d+)?)\.scope$")
TAIL_EVENTS = 40          # how much of a run's past a tab shows when the run first lands on it
TEXT_MAX = 600            # assistant prose shown per message
POLL_S = 1.0              # a worker's act reaches its tab within ~1 s (report target: 2 s)
OVERVIEW_S = 5.0


def root():
    return os.environ.get("RELENTLESS_ROOT") or DEFAULT_ROOT


# A WT tab's `wsl.exe -- <script>` may start without XDG_RUNTIME_DIR, and `systemctl --user` cannot find the user
# manager without it: the tab would read "cannot read the unit list" forever.
os.environ.setdefault("XDG_RUNTIME_DIR", "/run/user/%d" % os.getuid())


def runtime_dir():
    base = os.environ.get("XDG_RUNTIME_DIR") or "/tmp"
    d = os.path.join(base, "rm-pipeline-window")
    os.makedirs(d, exist_ok=True)
    return d


def short(item):
    return hashlib.sha1(item.encode()).hexdigest()[:10]      # relentless.short


# ---------------------------------------------------------------- what is running

def list_scopes():
    """-> the active claude-seat scope names. The only command this file runs; 2 s at most, as it runs under the
    station lock every tab shares."""
    try:
        r = subprocess.run(["systemctl", "--user", "list-units", "--state=active", "--plain", "--no-legend",
                            "claude-seat-*-rm-relentless-*"], capture_output=True, text=True, timeout=2,
                           stdin=subprocess.DEVNULL)
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode != 0:
        return None
    return [ln.split()[0] for ln in r.stdout.splitlines() if ln.strip()]


def parse_scope(scope):
    """claude-seat-BENCH-rm-relentless-work-91c4156a1a-g1.scope -> {unit, kind, hash, gen} or None."""
    m = UNIT_RE.match(scope)
    if not m:
        return None
    return {"unit": m.group(1), "kind": m.group(2), "hash": m.group(3), "gen": int(m.group(4))}


_item_names = {}
_listed_at = {}         # base -> (when store/items was last listed, its mtime then)
RELIST_S = 60             # a hash no item matches (an orphan) re-lists store/items at most this often, not every poll


def item_for(hsh, base):
    """The item a unit's hash names (relentless.unit_name hashes the item id). Re-listed only on a miss."""
    items = os.path.join(base, "store", "items")
    try:
        mt = os.path.getmtime(items)
    except OSError:
        mt = None
    seen = _listed_at.get(base, (0, None))
    if hsh not in _item_names and (mt != seen[1] or time.time() - seen[0] >= RELIST_S):
        _listed_at[base] = (time.time(), mt)     # a new item changes the dir's mtime: listed at once
        try:
            for name in os.listdir(os.path.join(base, "store", "items")):
                _item_names.setdefault(short(name), name)
        except OSError:
            pass
    return _item_names.get(hsh)


def run_start(unit, base):
    """When the run was launched: the clone sidecar is written just before its unit starts."""
    p = os.path.join(base, "store", "runs", "roles", unit + ".json.clone")
    try:
        return os.path.getmtime(p)
    except OSError:
        return None


def clone_of(unit, base):
    p = os.path.join(base, "store", "runs", "roles", unit + ".json.clone")
    try:
        with open(p, encoding="utf-8") as f:
            return f.read().strip() or None
    except OSError:
        return None


def live_runs(base, scopes):
    out = []
    for s in scopes or ():
        u = parse_scope(s)
        if not u:
            continue
        u["item"] = item_for(u["hash"], base)
        u["start"] = run_start(u["unit"], base)
        u["clone"] = clone_of(u["unit"], base)
        out.append(u)
    return out


# ---------------------------------------------------------------- stations

def assign(prev, runs):
    """prev {unit: station}, runs [{unit, kind, start}] -> {unit: station}. A run keeps the station it holds; runs that
    have ended give theirs up; a new run takes the lowest free station of its kind, oldest run first. A run with no
    free station gets none (the overview lists it)."""
    live = {r["unit"]: r for r in runs}
    got = {u: s for u, s in prev.items() if u in live and s in STATIONS
           and s[0] == KINDS[live[u]["kind"]][0]}
    taken = set(got.values())
    for r in sorted((r for r in runs if r["unit"] not in got), key=lambda r: (r.get("start") or 0, r["unit"])):
        p, n, _ = KINDS[r["kind"]]
        free = [p + str(i) for i in range(1, n + 1) if p + str(i) not in taken]
        if free:
            got[r["unit"]] = free[0]
            taken.add(free[0])
    return got


@contextlib.contextmanager
def _locked(path):
    fd = os.open(path + ".lock", os.O_CREAT | os.O_RDWR, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        os.close(fd)


def poll(base, scopes_fn, state_dir=None):
    """-> (scopes, runs, {unit: station}), the station map persisted so every tab (its own process) agrees. The unit
    list is read INSIDE the lock: a tab holding an older list would otherwise drop a station another tab just gave a
    new run. An unreadable list (None) changes nothing: the map stays as it is and no run is called ended."""
    p = os.path.join(state_dir or runtime_dir(), "stations.json")
    with _locked(p):
        scopes = scopes_fn()
        try:
            with open(p, encoding="utf-8") as f:
                prev = json.load(f)
        except (OSError, ValueError):
            prev = {}
        prev = prev if isinstance(prev, dict) else {}
        if scopes is None:
            return None, [], prev
        runs = live_runs(base, scopes)
        got = assign(prev, runs)
        if got != prev:
            tmp = "%s.tmp.%d" % (p, os.getpid())
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(got, f, sort_keys=True)
            os.replace(tmp, p)
    return scopes, runs, got


# ---------------------------------------------------------------- the transcript

def project_dirs(clone):
    """Where a run's transcripts land: ~/.claude/projects/<clone> (relentless_usage.project_dir), or, for a walled
    judge whose clone is <box>/tree, the box's own <box>/projects/<clone> (its config dir lives inside the wall)."""
    m = re.sub(r"[^A-Za-z0-9]", "-", clone or "")
    return [os.path.expanduser("~/.claude/projects/" + m), os.path.join(os.path.dirname(clone or "/"), "projects", m)]


def project_dir(clone):
    return project_dirs(clone)[0]


def transcript_for(run):
    """The run's own session file: the newest top-level JSONL of its clone touched since the run started (a resumed
    run appends to its older session file, so the file's mtime is what counts, not its birth)."""
    if not run.get("clone"):
        return None
    names = []
    for d in project_dirs(run["clone"]):
        try:
            names += [os.path.join(d, n) for n in os.listdir(d) if n.endswith(".jsonl")]
        except OSError:
            pass
    since = (run.get("start") or 0) - 5
    best = None
    for p in names:
        try:
            m = os.path.getmtime(p)
        except OSError:
            continue
        if m >= since and (best is None or m > best[0]):
            best = (m, p)
    return best[1] if best else None


def _clock(ts):
    try:
        t = datetime.datetime.strptime(ts[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=datetime.timezone.utc)
        return t.astimezone().strftime("%H:%M:%S")
    except (TypeError, ValueError):
        return "--:--:--"


# A worker's own text may hold ESC and other controls (a pasted log, `\033[2J`): printed raw they would clear,
# move or retitle the tab. Every worker-sourced string loses them; newline and tab survive for wrapping.
_CTRL = re.compile(r"[\x00-\x08\x0b-\x1f\x7f-\x9f]")


def _clean(s):
    return _CTRL.sub("", str(s))


def _one_line(s, n):
    s = " ".join(_clean(s).split())
    return s if len(s) <= n else s[:n - 1] + "…"


def _tool_summary(b):
    inp = b.get("input") or {}
    name = b.get("name") or "?"
    for k in ("description", "command", "file_path", "pattern", "prompt", "query", "skill", "url"):
        if inp.get(k):
            return "%s: %s" % (name, _one_line(inp[k], 140))
    return name


def render_event(d, width=110):
    """One transcript record -> printable lines ([] for the bookkeeping kinds: attachments, titles, api requests)."""
    t = d.get("type")
    if t not in ("assistant", "user") or d.get("isSidechain"):
        return []
    clock = _clock(d.get("timestamp"))
    m = d.get("message") or {}
    content = m.get("content")
    out = []
    if isinstance(content, str):
        content = [{"type": "text", "text": content}]
    for b in content if isinstance(content, list) else ():
        k = b.get("type")
        if t == "assistant" and k == "text" and b.get("text", "").strip():
            txt = _clean(b["text"]).strip()
            txt = txt if len(txt) <= TEXT_MAX else txt[:TEXT_MAX - 1] + "…"
            wrapped = []
            for para in txt.splitlines():
                wrapped += textwrap.wrap(para, width - 11) or [""]
            out.append("%s  \033[1m%s\033[0m" % (clock, wrapped[0]))
            out += ["          \033[1m%s\033[0m" % w for w in wrapped[1:]]
        elif t == "assistant" and k == "tool_use":
            out.append("%s  \033[36m▶ %s\033[0m" % (clock, _tool_summary(b)))
        elif t == "user" and k == "tool_result":
            c = b.get("content")
            if isinstance(c, list):
                c = " ".join(x.get("text", "") for x in c if isinstance(x, dict))
            lines = [x for x in _clean(c or "").splitlines() if x.strip()]
            mark = "\033[31m✗" if b.get("is_error") else "\033[2m←"
            first = _one_line(lines[0], width - 24) if lines else "(no output)"
            more = " (+%d lines)" % (len(lines) - 1) if len(lines) > 1 else ""
            out.append("%s  %s %s%s\033[0m" % (clock, mark, first, more))
        elif t == "user" and k == "text" and b.get("text", "").strip():
            out.append("%s  \033[33m» %s\033[0m" % (clock, _one_line(b["text"], width - 14)))
    return out


def read_from(path, offset):
    """-> (records, new offset). Only whole lines: a line the writer is mid-way through waits for the next poll."""
    try:
        with open(path, "rb") as f:
            f.seek(offset)
            data = f.read()
    except OSError:
        return [], offset
    end = data.rfind(b"\n")
    if end < 0:
        return [], offset
    recs = []
    for ln in data[:end].splitlines():
        try:
            recs.append(json.loads(ln))
        except ValueError:
            pass
    return recs, offset + end + 1


# ---------------------------------------------------------------- the tabs

def label(station):
    for k, (p, n, name) in KINDS.items():
        if station.startswith(p):
            return "%s %s" % (name, station[1:])
    return station


def header(station, run):
    age = int(time.time() - run["start"]) // 60 if run.get("start") else None
    return ["", "\033[7m %s · %s · gen %d · %s%s \033[0m" % (
        label(station), run.get("item") or run["hash"], run["gen"], run["kind"],
        " · %d min" % age if age is not None else ""), ""]


def follow_station(station, base, rounds=None, out=sys.stdout, state_dir=None, scopes_fn=list_scopes):
    """Follow one station: rounds=None runs until killed; a number stops after that many polls (tests, --once)."""
    cur, path, off, idle_said, blind_said = None, None, 0, False, False
    n = 0
    while True:
        scopes, runs, st = poll(base, scopes_fn, state_dir)
        mine = next((r for r in runs if st.get(r["unit"]) == station), None)
        if scopes is not None:
            blind_said = False
        if scopes is None:
            if not blind_said:
                print("%s  cannot read the unit list (systemctl --user); retrying" % time.strftime("%H:%M:%S"),
                      file=out)
                blind_said = True
            mine = cur          # blind is not ended: keep following what we follow
        elif mine is None and cur is not None:
            print("\n%s  \033[2m— %s ended; station idle —\033[0m" % (time.strftime("%H:%M:%S"), cur["unit"]),
                  file=out)
            cur, path, off, idle_said = None, None, 0, True
        elif mine is None and not idle_said:
            print("%s  \033[2m%s: no run here yet; the next %s takes the lowest free station\033[0m" % (
                time.strftime("%H:%M:%S"), label(station), label(station).split()[0].lower()), file=out)
            idle_said = True
        elif mine is not None and (cur is None or mine["unit"] != cur["unit"]):
            cur, path, off, idle_said = mine, None, 0, False
            print("\n".join(header(station, mine)), file=out)
        if cur is not None:
            p = transcript_for(cur)
            if p and p != path:
                path, off = p, 0
                recs, off = read_from(path, 0)
                lines = [ln for r in recs for ln in render_event(r)]
                if len(lines) > TAIL_EVENTS:
                    print("\033[2m… %d earlier lines\033[0m" % (len(lines) - TAIL_EVENTS), file=out)
                    lines = lines[-TAIL_EVENTS:]
                for ln in lines:
                    print(ln, file=out)
            elif path:
                recs, off = read_from(path, off)
                for r in recs:
                    for ln in render_event(r):
                        print(ln, file=out)
            elif not p and not idle_said:
                print("\033[2m(no transcript yet under %s)\033[0m" % project_dir(cur.get("clone")), file=out)
                idle_said = True
        out.flush()
        n += 1
        if rounds is not None and n >= rounds:
            return
        time.sleep(POLL_S)


def overview(base, rounds=None, out=sys.stdout, state_dir=None, scopes_fn=list_scopes):
    n = 0
    while True:
        scopes, runs, st = poll(base, scopes_fn, state_dir)
        by = {s: r for r in runs for s in [st.get(r["unit"])] if s}
        rows = ["\033[H\033[2J\033[7m Pipeline · %s · %d live run(s) \033[0m" % (time.strftime("%H:%M:%S"),
                                                                                  len(runs)), ""]
        if scopes is None:
            rows.append("cannot read the unit list (systemctl --user)")
        for s in STATIONS:
            r = by.get(s)
            if r is None:
                rows.append("  %-10s \033[2midle\033[0m" % label(s))
                continue
            p = transcript_for(r)
            last = "—"
            if p:
                try:
                    last = "%ds ago" % int(time.time() - os.path.getmtime(p))
                except OSError:
                    pass
            age = "%dm" % (int(time.time() - r["start"]) // 60) if r.get("start") else "?"
            rows.append("  %-10s %-48s g%-2d %5s  last write %s" % (label(s), _one_line(r.get("item") or r["hash"], 48),
                                                                   r["gen"], age, last))
        extra = [r for r in runs if r["unit"] not in st]
        if extra:
            rows += ["", "  no free station:"] + ["    %s %s" % (r["kind"], r.get("item") or r["hash"]) for r in extra]
        rows += ["", "\033[2m  read-only: closing this window stops nothing; watching spends no tokens.\033[0m"]
        print("\n".join(rows), file=out)
        out.flush()
        n += 1
        if rounds is not None and n >= rounds:
            return
        time.sleep(OVERVIEW_S)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("station", help="B1..B8, J1..J4, C1 or overview")
    ap.add_argument("--once", action="store_true", help="one frame, then exit")
    a = ap.parse_args(argv)
    if a.station != "overview" and a.station not in STATIONS:
        ap.error("station %r: one of overview, %s" % (a.station, ", ".join(STATIONS)))
    try:
        if a.station == "overview":
            overview(root(), rounds=1 if a.once else None)
        else:
            follow_station(a.station, root(), rounds=1 if a.once else None)
    except KeyboardInterrupt:
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
