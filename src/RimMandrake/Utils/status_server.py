#!/usr/bin/env python3
"""status_server.py — serve the v1 obeya board to a Windows browser.

    python3 src/RimMandrake/Utils/status_server.py        # http://localhost:8787
    ... --port N   --once (print the JSON and exit)

The browser renders it, not WSLg, so text is crisp at any DPI. That is the whole
reason this is a page and not a Tk window.

Data:
    infrastructure/state/status_matrix.json   rows, per-cell state mix,
                                              blocker classes, velocity
    infrastructure/state/status/game.json     is the game up, and in what state
    live                                       host memory, agent liveness
"""
import argparse
import json
import os
import sys
import re
import subprocess
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from game_paths import PLAYER_LOG as _PLAYER_LOG  # noqa: E402

ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
STATE = os.path.join(ROOT, "infrastructure/state")
PAGE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "status_board.html")
SEATS = ["DECIDE", "BUILD", "CHECK", "REP"]


def jload(name, default):
    try:
        with open(os.path.join(STATE, name)) as fh:
            return json.load(fh)
    except Exception:
        return default


def host():
    """Real numbers, re-read every poll. A bar that never moves is worse than none."""
    out = {}
    try:
        mi = {}
        with open("/proc/meminfo") as fh:
            for ln in fh:
                k, _, v = ln.partition(":")
                mi[k] = int(v.strip().split()[0])          # kB
        total = mi.get("MemTotal", 0) / 1048576.0
        avail = mi.get("MemAvailable", 0) / 1048576.0
        out["wsl"] = {"used_gb": round(total - avail, 1), "total_gb": round(total, 1)}
        out["swap"] = {"used_gb": round((mi.get("SwapTotal", 0) - mi.get("SwapFree", 0)) / 1048576.0, 1),
                       "total_gb": round(mi.get("SwapTotal", 0) / 1048576.0, 1)}
    except Exception:
        pass
    try:
        # Count THIS project's agents only. A bare `ps | grep claude` also
        # catches the owner's sessions in other repos, which is how the panel
        # read 5 processes beside a SEATS UP of 4/4 — the fifth was a Hestia
        # session. The working directory is what distinguishes them.
        ps = subprocess.run(["ps", "-eo", "pid,rss,comm"], capture_output=True,
                            text=True, timeout=10).stdout.splitlines()[1:]
        rss = n = other = 0
        here = os.path.realpath(ROOT)
        for line in ps:
            parts = line.split(None, 2)
            if len(parts) < 3 or "claude" not in parts[2].lower():
                continue
            try:
                cwd = os.path.realpath("/proc/%s/cwd" % parts[0])
            except OSError:
                continue
            if cwd == here or cwd.startswith(here + os.sep):
                rss += int(parts[1])
                n += 1
            else:
                other += 1
        out["agents"] = {"count": n, "rss_gb": round(rss / 1048576.0, 2),
                         "elsewhere": other}
    except Exception:
        pass
    # WSL CPU. This is the number that actually tracks how hard the seats are
    # working — WSL *memory* barely moves, because four agents are ~0.4 GB each
    # against a 35 GB ceiling, and RimWorld is not in WSL at all.
    try:
        one, five, fifteen = open("/proc/loadavg").read().split()[:3]
        cores = os.cpu_count() or 1
        out["wsl_cpu"] = {"load1": float(one), "load5": float(five),
                          "load15": float(fifteen), "cores": cores,
                          "pct": round(100.0 * float(one) / cores)}
    except Exception:
        pass
    out.update(windows())
    return out


_WIN = {"at": 0, "v": {}}
WIN_TTL = 6          # seconds; one PowerShell call is ~1s and the poll is 3s


def windows():
    """The Windows side, in one call: RimWorld's memory, host RAM, host CPU.

    RimWorld runs on Windows, not in WSL, so the machine that matters for the
    game is invisible to /proc. Cached briefly because PowerShell start-up costs
    about a second and the board polls every three.
    """
    if _WIN["v"] and time.time() - _WIN["at"] < WIN_TTL:
        return _WIN["v"]
    ps = (r"$p=Get-Process RimWorldWin64 -ErrorAction SilentlyContinue;"
          r"$o=Get-CimInstance Win32_OperatingSystem;"
          r"$s=Get-CimInstance Win32_ComputerSystem;"
          r"$c=(Get-CimInstance Win32_Processor|Measure-Object -Property LoadPercentage"
          r" -Average).Average;"
          r"'{0}|{1}|{2}|{3}|{4}|{5}|{6}' -f "
          r"$(if($p){[math]::Round($p.WorkingSet64/1GB,1)}else{'na'}),"
          r"[math]::Round(($o.TotalVisibleMemorySize-$o.FreePhysicalMemory)/1MB,1),"
          r"[math]::Round($o.TotalVisibleMemorySize/1MB,1),[int]$c,"
          r"$(if($p){[math]::Round($p.CPU,2)}else{'na'}),"
          r"$s.NumberOfLogicalProcessors,"
          r"$(if($p){$p.Threads.Count}else{'na'})")
    v = {"rimworld_gb": None}
    try:
        raw = subprocess.run(["powershell.exe", "-NoProfile", "-Command", ps],
                             capture_output=True, text=True, timeout=20).stdout
        # PowerShell formats with the locale's thousands separator, so 1,009.8
        # arrives for a process that has run 17 minutes. Strip before float().
        rw, used, total, cpu, cpu_s, cores, threads = [
            f.strip().replace(",", "") for f in raw.strip().split("|")]
        v = {"rimworld_gb": None if rw == "na" else float(rw),
             "win": {"used_gb": float(used), "total_gb": float(total),
                     "cpu_pct": int(cpu), "cores": int(cores)}}
        if cpu_s != "na":
            v["win"]["threads"] = int(threads)
            v["win"]["rimworld_cores"] = _cores_used(float(cpu_s))
    except Exception:
        pass
    _WIN.update(at=time.time(), v=v)
    return v


_RWCPU = {"cpu_s": None, "at": None}


def _cores_used(cpu_s):
    """Cores RimWorld is actually burning, from the change in its CPU time.

    `.CPU` is cumulative processor-seconds, so it only answers "how busy is it
    NOW" as a rate: seconds of CPU consumed per second of wall clock IS the
    number of cores in use. One sample tells you nothing, so the first poll
    returns None and every later one measures against the previous.
    """
    now = time.time()
    prev_s, prev_at = _RWCPU["cpu_s"], _RWCPU["at"]
    _RWCPU.update(cpu_s=cpu_s, at=now)
    if prev_s is None or prev_at is None:
        return None
    dt, dc = now - prev_at, cpu_s - prev_s
    if dt <= 0 or dc < 0:            # relaunched: counter reset, not negative work
        return None
    return round(dc / dt, 2)


PLAYER_LOG = _PLAYER_LOG
LOAD_DONE_CUE = "Startup conditions satisfied"
_LOG = {"key": None, "done": None}


def load_finished():
    """Has THIS launch got past loading? Read from the game's own log.

    A seat has to remember to restamp `game.json`; the log does not. One stamp
    sat at LOADING for 77 minutes after the game had reached the menu, so the
    board now checks rather than trusts. RimWorld truncates Player.log at each
    launch (the previous one moves to Player-prev.log), so a marker in the
    current file belongs to the current process.

    Cached on (size, mtime): an idle game writes nothing, so this is one stat
    per poll and a scan only when the log actually moves.
    """
    try:
        stt = os.stat(PLAYER_LOG)
    except OSError:
        return None                       # no log readable — say nothing
    key = (stt.st_size, int(stt.st_mtime))
    if _LOG["key"] == key:
        return _LOG["done"]
    done = None
    try:
        with open(PLAYER_LOG, "r", errors="ignore") as fh:
            done = any(LOAD_DONE_CUE in ln for ln in fh)
    except OSError:
        return None
    _LOG.update(key=key, done=done)
    return done


def agents():
    """Liveness from Claude Code's own session list — the supported surface."""
    st = {s: {"state": "offline", "item": ""} for s in SEATS}
    try:
        rows = json.loads(subprocess.run(["claude", "agents", "--json"],
                                         capture_output=True, text=True,
                                         timeout=15).stdout)
        rank = {"idle": 1, "busy": 2, "waiting": 3, "blocked": 3}
        for r in rows:
            name = (r.get("name") or "").upper()
            if not name.startswith("AGENT "):
                continue
            # Other repos' sessions show up in this list too. A seat is only
            # this project's seat if its cwd is this project.
            if r.get("cwd") and os.path.realpath(r["cwd"]) != os.path.realpath(ROOT):
                continue
            seat = name[6:].strip()
            if seat not in st:
                continue
            s = r.get("status") or r.get("state") or "offline"
            if rank.get(s, 0) >= rank.get(st[seat]["state"], 0):
                st[seat]["state"] = s
    except Exception:
        pass
    for s in SEATS:
        try:
            with open(os.path.join(STATE, "status", "%s.json" % s)) as fh:
                d = json.load(fh)
            st[s]["item"] = d.get("item", "")
            st[s]["why"] = d.get("why", "")
            # How old the seat's own line is. Without it a ten-hour-old CURRENTLY
            # entry reads exactly like one written a minute ago.
            st[s]["said_at"] = d.get("updated")
        except Exception:
            pass
    return st


# The census walks ~3k files. It changes on the scale of a work session, not a
# poll, so it is cached for an hour and the page shows how old it is.
INV_TTL = 3600

# Counted: what we authored. Excluded: everything we merely downloaded, harvested
# or generated. `research/` holds other people's hand-authored maps and `observed/`
# holds harvested savegames — 400+ MB between them, none of it ours.
EXCLUDE = (".git", "vendor", "research", "observed", "deployed", "disposing",
           "obj", "bin", "__pycache__", "node_modules", "artifacts")
_INV = {"at": 0, "v": None}


def inventory():
    """Repo census, cached — it moves slowly and a full scan is ~0.4s.

    Two axes because they answer different questions: bytes says where the
    weight is, count says where the work is. A 46 MB DLL and 230 patch files
    are both 'a lot' and neither number substitutes for the other.
    """
    if _INV["v"] and time.time() - _INV["at"] < INV_TTL:
        return _INV["v"]
    vol = {}
    cnt = {}

    def add(k, n):
        vol[k] = vol.get(k, 0) + n
        cnt[k] = cnt.get(k, 0) + 1

    mods = defs = patches = about = tex = 0
    for dirpath, dirnames, files in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE]
        rel = os.path.relpath(dirpath, ROOT)
        for f in files:
            fp = os.path.join(dirpath, f)
            try:
                n = os.path.getsize(fp)
            except OSError:
                continue
            e = f.rsplit(".", 1)[-1].lower() if "." in f else ""
            if e in ("png", "jpg", "jpeg", "dds", "bmp", "psd"):
                # Shipping art and reference art are not the same asset. A
                # 3 MB biome screenshot for review is not a texture the game
                # loads, and summing them hides how much art actually ships.
                if rel.startswith("src"):
                    add("game textures", n); tex += 1
                else:
                    add("reference art", n)
            elif e == "dll":
                add("assemblies", n)
            elif e == "cs":
                add("C# source", n)
            elif e in ("py", "ps1", "sh"):
                add("tools/scripts", n)
            elif e == "xml":
                add("game XML", n)
                if "/Patches" in rel or rel.endswith("Patches"):
                    patches += 1
                if "/Defs" in rel or rel.endswith("Defs"):
                    defs += 1
                if f.lower() == "about.xml":
                    about += 1
            elif e == "md":
                add("skills" if rel.startswith("skills") else "design + docs", n)
            elif e in ("json", "cfg", "ini", "rws"):
                add("data/config", n)
    things = [
        ("mods", about),
        ("def files", defs),
        ("patch files", patches),
        ("game textures", tex),
        ("reference images", cnt.get("reference art", 0)),
        ("C# files", cnt.get("C# source", 0)),
        ("tools/scripts", cnt.get("tools/scripts", 0)),
        ("skill docs", cnt.get("skills", 0)),
        ("design docs", cnt.get("design + docs", 0)),
    ]
    v = {"volume": sorted(({"label": k, "mb": round(b / 1048576.0, 1)}
                           for k, b in vol.items()),
                          key=lambda d: -d["mb"]),
         "counts": sorted(({"label": k, "n": n} for k, n in things),
                          key=lambda d: -d["n"])}
    v["scanned_at"] = int(time.time())
    v["excluded"] = [d for d in EXCLUDE if d not in
                     (".git", "obj", "bin", "__pycache__", "node_modules")]
    _INV.update(at=time.time(), v=v)
    return v


# ---------------------------------------------------------------------------
# THE LEDGER IS THE SOURCE NOW — 2026-08-20
#
# `status_matrix.json` came from parsing six hand-written queue files whose `state:`
# was free text. 58 of 142 items led with an emoji, so it reported 0 done and 0 blocked
# against a real 53 and 2. There was nothing wrong with the parsing; there was no enum
# to parse. `derive_matrix.py` now REFUSES to run against the rendered queues rather
# than reporting zero, which means this file must get its numbers elsewhere.
#
# `infrastructure/state/derived/board.json` is that elsewhere: a projection of
# `ledger/events.jsonl`, regenerated by `rimflow render`. It keeps status_matrix's
# `rows[].cells{}` shape deliberately, so everything below kept working unchanged.
#
# ⚠️ `derived/` is gitignored, so board.json can be ABSENT on a fresh checkout. That is
# not an error and must not render as zeros — zeros look like an answer. `_board()`
# regenerates it, and if that fails the page is told the board is UNAVAILABLE.
# ---------------------------------------------------------------------------
BOARD = os.path.join(STATE, "derived", "board.json")
_RENDER = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "rimflow", "render.py")
# ⏱️ 30 s, halved from 60 on the owner's ask 2026-08-21. `render.py` self-reports
# ~400 ms, so this is ~1.3% of one core — the page's cheap half (/data: game state,
# agent liveness, host memory) already ticks at 3 s and is unaffected. ⛔ Do not push
# this below ~10 s: `stat`-ing the item files alone costs 130 ms on this 9p mount, so a
# faster cadence buys nothing and starts competing with the seats for the disk.
_BOARD_TTL = 30
_BOARD = {"at": 0.0, "v": None, "err": None}


def _regenerate():
    """Run `rimflow render`. -> None on success, or an error string.

    ⚠️ Never raises. A board that 500s is a board nobody leaves open, and this page is
    meant to sit on a second monitor all day.
    """
    try:
        r = subprocess.run([sys.executable, os.path.abspath(_RENDER)],
                           capture_output=True, text=True, cwd=ROOT, timeout=120)
        return None if r.returncode == 0 else (r.stderr or r.stdout or "")[-400:]
    except Exception as e:
        return "%s: %s" % (type(e).__name__, e)


def _board(force=False):
    """The ledger projection, regenerated at most every _BOARD_TTL seconds."""
    now_ = time.time()
    if not force and _BOARD["v"] is not None and now_ - _BOARD["at"] < _BOARD_TTL:
        return _BOARD["v"]
    err = None
    if force or not os.path.exists(BOARD) or \
            now_ - os.path.getmtime(BOARD) > _BOARD_TTL:
        err = _regenerate()
    try:
        with open(BOARD, encoding="utf-8") as fh:
            v = json.load(fh)
    except Exception as e:
        v, err = None, err or "%s: %s" % (type(e).__name__, e)
    _BOARD.update(at=now_, v=v, err=err)
    return v


# ---------------------------------------------------------------------------
# WHAT IS LEFT, AND WHAT IT IS WAITING FOR
# ---------------------------------------------------------------------------
# 🔴 OWNER, 2026-08-21: the board showed per-row done/total and per-seat state mixes,
# and never once showed the number he actually wanted — HOW MANY THINGS ARE NOT DONE.
# It also scattered "needs live game" across dozens of small cells instead of counting
# them once at the top. Both are computed here, from `catalog`, which already carries
# `needs` and `blocked` per item. ⛔ Nothing new is derived in render.py: this file
# DISPLAYS, the ledger projection DECIDES.
#
# 🔑 `needs` and `blocked` are ORTHOGONAL and the page must not add them up.
# `needs` is a window that will open by itself — nothing is wrong. `blocked` is
# something being wrong that a person must act on. Conflating them is what made
# "waiting on the owner" the only trustworthy number on the old board.
OPEN_STATES = ("proposed", "ready", "doing")

# label, needs-key, and what the owner does about it. Order is the order shown.
WAITING_ON = [
    ("GAME UP",     "game-up", "start the game"),
    ("LIVE BRIDGE", "bridge",  "game up, bridge free"),
    ("GAME DOWN",   "deploy",  "close the game — assemblies are locked while it runs"),
    ("FRESH DUMP",  "harvest", "arm DefDump/dump_request.txt and load"),
    ("YOU",         "owner",   "a ruling only you can give"),
    ("NOTHING",     "offline", "runnable right now"),
]


def waiting(m):
    """-> {'lanes': [...], 'open_total': N, 'blocked_total': N, 'per_seat': {...}}

    Counts OPEN items only. A done item waiting for nothing is not news.
    """
    cat = m.get("catalog") or []
    lanes = {k: 0 for _, k, _ in WAITING_ON}
    # 🔴 OWNER, 2026-08-21: "only the agents actively waiting should be in those
    # messages". A lane reading 4 tells him something is stuck; a lane reading
    # "BUILD (3), DECIDE (1)" tells him WHO to go and unstick, which is the whole
    # difference between a dashboard and a to-do list.
    by_seat = {k: {} for _, k, _ in WAITING_ON}
    blocked_by_seat, unset_by_seat = {}, {}
    per_seat, blocked_total, open_total, unknown = {}, 0, 0, 0
    for it in cat:
        if it.get("state") not in OPEN_STATES:
            continue
        open_total += 1
        seat = it.get("owner") or "?"
        d = per_seat.setdefault(seat, {"open": 0, "blocked": 0, "doing": 0})
        d["open"] += 1
        if it.get("state") == "doing":
            d["doing"] += 1
        if it.get("blocked"):
            blocked_total += 1
            d["blocked"] += 1
            blocked_by_seat[seat] = blocked_by_seat.get(seat, 0) + 1
            continue                 # blocked is not a window; do not double-count
        k = it.get("needs")
        if k in lanes:
            lanes[k] += 1
            by_seat[k][seat] = by_seat[k].get(seat, 0) + 1
        else:
            unknown += 1
            unset_by_seat[seat] = unset_by_seat.get(seat, 0) + 1

    def seats_of(d):
        """Busiest first, then alphabetical — the seat to chase is named first."""
        return [{"seat": k, "n": v}
                for k, v in sorted(d.items(), key=lambda kv: (-kv[1], kv[0]))]

    out = [{"label": lab, "key": k, "hint": hint, "n": lanes[k],
            "seats": seats_of(by_seat[k])}
           for lab, k, hint in WAITING_ON]
    if unknown:
        out.append({"label": "UNSET", "key": None,
                    "hint": "no `needs` recorded — the filer left the default",
                    "n": unknown, "seats": seats_of(unset_by_seat)})
    return {"lanes": out, "open_total": open_total,
            "blocked_total": blocked_total, "per_seat": per_seat,
            "blocked_seats": seats_of(blocked_by_seat)}


def snapshot():
    m = _board() or {"rows": [], "unavailable": True,
                     "why": _BOARD.get("err") or "board.json could not be built"}
    rows = m.get("rows", [])
    tot = don = 0
    for r in rows:
        for c in r.get("cells", {}).values():
            tot += c.get("total", 0)
            don += c.get("done", 0)
    return {
        "rows": rows,
        "overall": {"done": don, "total": tot,
                    "pct": round(100.0 * don / tot) if tot else 0},
        # Blockers and velocity ride in the matrix now — derive_matrix.py counts
        # them off the items themselves. The hand-kept blockers.json that used to
        # sit here had drifted to 12 against 7 real blocked items.
        "blockers": m.get("blockers", {"classes": [], "on_human": 0}),
        # ⭐ The number the owner asked for first: how many things are NOT done.
        "waiting": waiting(m),
        "velocity": m.get("velocity", {}),
        # Declared game state, which is NOT the same fact as host()'s RSS reading:
        # one is what a seat claims, the other is whether the process exists. The
        # page reconciles them, because the disagreement is the interesting case.
        # 🔑 THREE SOURCES FOR ONE FACT, AND THE DISAGREEMENT IS THE POINT.
        # `status/game.json` is what a seat wrote down; the ledger's `game` is what the
        # OWNER last announced; host() reads whether the process actually exists. They
        # can differ — a load can abort while `game_loaded` still says UP — so all three
        # travel to the page rather than one being picked here.
        "game": dict(jload("status/game.json", {}),
                     load_done=load_finished(),
                     ledger=m.get("game"),
                     bridge=m.get("bridge_holder")),
        # From the ledger: per-seat counts, findings, and the replay refusals already
        # sitting in an append-only file that nobody can remove.
        "seats": m.get("seats", {}),
        "findings": m.get("findings", {}),
        "ledger_errors": m.get("errors", []),
        "board_unavailable": bool(m.get("unavailable")),
        "board_why": m.get("why"),
        "host": host(),
        "agents": agents(),
        "inventory": inventory(),
        "ts": int(time.time()),
        # See the note above main(): a five-day-old process served a page whose code
        # had moved on, and nothing on screen said so.
        "server_started": int(_STARTED),
        "server_pid": os.getpid(),
    }


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        # ⚠️ EXACT match, and the order below is load-bearing. `startswith("/board")`
        # swallowed `/board/deck.js` too, so every module request returned the 81 KB
        # board JSON with a JSON content-type and the page silently loaded nothing.
        # Found 2026-08-20 by the view that could not load itself.
        if self.path.split("?")[0].rstrip("/") == "/board":
            # The raw ledger projection, for the view modules. Kept separate from
            # /data so a view can poll the ledger without paying for host(),
            # inventory() and the process census on every tick.
            body = json.dumps(_board() or {"unavailable": True,
                                           "why": _BOARD.get("err")}).encode()
            ctype = "application/json"
        elif self.path.startswith("/items/"):
            # One item's PROSE. The ledger holds every scalar and `items/<ID>.md` holds
            # the spec/verify/criteria — deliberately, so no field exists twice — which
            # left the Flow inspector with a native path to print and nothing to show.
            # ⚠️ basename() is the path-traversal guard; do not "simplify" it away.
            name = os.path.basename(self.path.split("?")[0])
            if not name.endswith(".md"):
                name += ".md"
            try:
                body = open(os.path.join(STATE, "items", name), "rb").read()
            except Exception:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"no such item")
                return
            ctype = "text/markdown; charset=utf-8"
        elif self.path.split("?")[0].rstrip("/") == "/ledger/events.jsonl":
            # The raw ledger, verbatim. The Timeline view needs the EVENT STREAM and
            # /board carries only `events` as an integer count, so there was no served
            # route to it at all — the view could render nothing but its own error
            # panel. Reported by the view that could not read its own source.
            # ⚠️ Served as text/plain, not JSON: it is JSON *Lines*, and a torn line is
            # something the Timeline renders in place rather than something a parser
            # here should reject on the reader's behalf.
            try:
                body = open(os.path.join(STATE, "ledger", "events.jsonl"), "rb").read()
            except Exception as e:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(("ledger unreadable: %s" % e).encode())
                return
            ctype = "text/plain; charset=utf-8"
        elif self.path.startswith("/board/"):
            # The view modules, served from src/RimMandrake/Utils/board/.
            name = os.path.basename(self.path.split("?")[0])
            f = os.path.join(os.path.dirname(os.path.abspath(__file__)), "board", name)
            # ⚠️ basename() above is the path-traversal guard; do not "simplify" it.
            try:
                body = open(f, "rb").read()
            except Exception:
                self.send_response(404)
                self.end_headers()
                return
            ctype = ("text/javascript" if name.endswith(".js")
                     else "text/css" if name.endswith(".css") else "text/plain")
            ctype += "; charset=utf-8"
        elif self.path.startswith("/data"):
            body = json.dumps(snapshot()).encode()
            ctype = "application/json"
        else:
            try:
                body = open(PAGE, "rb").read()
            except Exception as e:
                body = ("<pre>missing %s: %s</pre>" % (PAGE, e)).encode()
            ctype = "text/html; charset=utf-8"
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


# 🔴 THE SERVER IS LONG-LIVED, AND THAT IS A TRAP THIS PAGE HAS ALREADY SPRUNG.
# On 2026-08-20 the board reported "deck failed to render: Failed to fetch dynamically
# imported module .../board/deck.js". Nothing was wrong with the code: the process
# answering :8787 had been up since 2026-08-15 and predated the `/board` route entirely,
# so every module request fell through to the HTML page and the browser tried to import
# markup as JavaScript.
#
# ⚠️ Every verification that day had spun up a FRESH server on a spare port and passed.
# A long-running process is a cached copy of the code, and testing a copy you just
# started is testing the wrong thing — the same shape as the concurrency test that
# passed on the wrong filesystem.
#
# ⇒ The page reports the server's start time, so a stale process is visible rather than
# mysterious. `/data` carries `server_started` and `server_pid`.
_STARTED = time.time()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8787)
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--inv-ttl", type=int, default=INV_TTL,
                    help="seconds between repo censuses (default 3600)")
    a = ap.parse_args()
    globals()["INV_TTL"] = a.inv_ttl
    if a.once:
        print(json.dumps(snapshot(), indent=1))
        return 0
    print("http://localhost:%d" % a.port)
    HTTPServer(("0.0.0.0", a.port), H).serve_forever()


if __name__ == "__main__":
    raise SystemExit(main())
