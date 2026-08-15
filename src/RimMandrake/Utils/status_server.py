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
import re
import subprocess
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

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
        ps = subprocess.run(["ps", "-eo", "rss,comm"], capture_output=True,
                            text=True, timeout=10).stdout.splitlines()[1:]
        rss = sum(int(l.split()[0]) for l in ps if "claude" in l.lower())
        n = sum(1 for l in ps if "claude" in l.lower())
        out["agents"] = {"count": n, "rss_gb": round(rss / 1048576.0, 2)}
    except Exception:
        pass
    try:
        tl = subprocess.run(["tasklist.exe"], capture_output=True, text=True,
                            timeout=20).stdout
        m = re.search(r"RimWorldWin64\.exe\s+\d+\s+\S+\s+\d+\s+([\d,]+) K", tl)
        out["rimworld_gb"] = round(int(m.group(1).replace(",", "")) / 1048576.0, 1) if m else None
    except Exception:
        out["rimworld_gb"] = None
    return out


PLAYER_LOG = ("/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/"
              "RimWorld by Ludeon Studios/Player.log")
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


def snapshot():
    m = jload("status_matrix.json", {"rows": []})
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
        "velocity": m.get("velocity", {}),
        # Declared game state, which is NOT the same fact as host()'s RSS reading:
        # one is what a seat claims, the other is whether the process exists. The
        # page reconciles them, because the disagreement is the interesting case.
        "game": dict(jload("status/game.json", {}), load_done=load_finished()),
        "host": host(),
        "agents": agents(),
        "inventory": inventory(),
        "ts": int(time.time()),
    }


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        if self.path.startswith("/data"):
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
