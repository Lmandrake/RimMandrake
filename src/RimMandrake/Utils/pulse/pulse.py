#!/usr/bin/env python3
"""rimflow pulse — the away-dashboard spine (AWAY_DASHBOARD_BUILD_1).

  pulse.py daemon              collector loop (5 s) + HTTP/SSE on 127.0.0.1:8765. Run by
                               rm-pulse.service (systemd --user, Restart=always). Nothing
                               else needs to keep it fresh.
  pulse.py collect             one collection, prints the rows (debug)
  pulse.py since [--back | --scheduled | --since ISO] [--quiet]
                               the "since you left" digest: printed with native paths,
                               saved dated under D:\\Luke\\dev\\_rmdashboard\\digests\\ and
                               shown in the widget. `./pulse back` is the "I'm back" form.
  pulse.py ack <incident> [--noise]
  pulse.py hand <path-or-url> [--title "what it is"] [--seat BENCH|FOUNDRY]
                               HAND THE OWNER SOMETHING TO LOOK AT. It appears in the widget's
                               "to look at" list (one line, tiny preview for images, an open link,
                               coloured by --seat) until he opens it, which marks it seen. Use it
                               for a thing you deliberately made for his eyes: a contact sheet,
                               a review page, a keeper save, a folder of shots. Relative paths
                               resolve against the cwd; handing the same target again re-raises it.
                               Review-sheet servers (Transient/biome_ffar/*.serve.log) need no hand:
                               pulse lists every live one with its unseen count by itself.
  pulse.py seen <id>           mark a look item seen without opening it (ids print from `hand`)
  pulse.py metrics             time-to-notice red, question age, alert precision

State: ~/.local/state/rm-dashboard/ (state.json, pulse_now.json, pulse.jsonl, metrics.jsonl).
The widget is src/RimMandrake/Utils/pulse/widget/ (Windows, pywebview).
"""
from __future__ import annotations

import argparse
import hashlib
import re
import json
import os
import sys
import threading
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pulse_core as pc  # noqa: E402

HERE = Path(__file__).resolve().parent
WIDGET_HTML = HERE / "widget" / "index.html"
PORT = int(os.environ.get("RM_PULSE_PORT", "8765"))
DIGEST_DIR = Path(os.environ.get("RM_PULSE_DIGESTS", "/mnt/d/Luke/dev/_rmdashboard/digests"))
INTERVAL = 5.0

# Phone push: NOT decided by the owner yet (2026-10-08). Hook point only; stays off until
# he rules. Wire ntfy (or anything) here, never in the widget.
PHONE_PUSH_ENABLED = False


def notify_phone(row: dict) -> None:
    if not PHONE_PUSH_ENABLED:
        return


# ---------------------------------------------------------------- state io

def _p(name: str) -> Path:
    pc.STATE_DIR.mkdir(parents=True, exist_ok=True)
    return pc.STATE_DIR / name


def load_state() -> dict:
    try:
        return json.loads(_p("state.json").read_text())
    except (OSError, ValueError):
        return {}


def save_json(name: str, obj) -> None:
    p = _p(name)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False))
    os.replace(tmp, p)


def append(name: str, rec: dict) -> None:
    rec.setdefault("ts", time.time())
    with open(_p(name), "a") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


_lock = threading.RLock()

# ---------------------------------------------------------------- collection


class Collector:
    def __init__(self):
        self.state = load_state()
        self.snapshot: dict = {}
        self.version = 0
        self.cond = threading.Condition()
        self.probe: dict | None = None
        self.artpipe: dict = {}
        self.ledger_cache: dict = {}
        self.prev_kinds: dict = {}
        self.kernel: dict = {}
        self.sheets: dict = {"at": 0, "rows": []}

    def _ledger(self) -> list[dict]:
        sig = []
        for c in pc.CLONES:
            for f in sorted((c / "infrastructure/state/ledger/events").glob("*.jsonl")):
                try:
                    st = f.stat()
                    sig.append((str(f), st.st_mtime, st.st_size))
                except OSError:
                    pass
        if self.ledger_cache.get("sig") != sig:
            self.ledger_cache = {"sig": sig, "events": pc.read_ledger()}
        return self.ledger_cache["events"]

    def gather(self, now: float) -> dict:
        status, raw = {}, {"at": {}}

        def src(name, fn):
            t0 = time.time()
            try:
                v = fn()
                status[name] = {"ok": True, "at": now, "ms": round((time.time() - t0) * 1000)}
                return v
            except Exception as e:  # a broken source degrades coverage; it never guesses
                status[name] = {"ok": False, "at": self.snapshot.get("sources", {}).get(name, {}).get("at"),
                                "error": f"{type(e).__name__}: {e}"[:160]}
                return None

        sessions = src("sessions", pc.read_sessions) or []
        raw["sessions"] = sessions
        raw["extras"] = src("subagents", lambda: {s.get("sessionId"): pc.session_extras(s.get("sessionId"), now)
                                                  for s in sessions if s.get("alive")}) or {}
        if now - self.kernel.get("at", 0) > 20:
            k = src("kernel", pc.read_kernel_oom)
            self.kernel = {"at": now, "kills": k}
        else:
            status["kernel"] = self.snapshot.get("sources", {}).get("kernel", {"ok": True, "at": now})
        raw["kernel_oom"] = self.kernel.get("kills")
        raw["memwatch"] = src("memwatch", lambda: pc.read_jsonl_tail(pc.MEMWATCH_EVENTS, 2 << 20)) or []
        raw["ledger"] = src("ledger", self._ledger) or []
        a = src("artpipe", lambda: pc.read_artpipe(pc.ARTPIPE_DIR, self.artpipe, now))
        if a:
            self.artpipe = a
        raw["artpipe"] = self.artpipe
        raw["hands"] = src("hands", pc.read_hands) or []
        if now - self.sheets["at"] > 45:
            r = src("sheets", pc.read_sheets)
            if r is not None:
                self.sheets = {"at": now, "rows": r}
        else:
            status["sheets"] = self.snapshot.get("sources", {}).get("sheets", {"ok": True, "at": now})
        raw["sheets"] = self.sheets["rows"]
        raw["bridge"] = src("bridge", pc.read_bridge)
        raw["probe"] = self.probe
        status["probe"] = {"ok": self.probe is not None, "at": (self.probe or {}).get("at")}
        raw["source_status"] = status
        return raw

    def tick(self) -> dict:
        now = time.time()
        raw = self.gather(now)
        with _lock:
            disk = load_state()   # `pulse.py since` writes the digest fields from another process
            if ((disk.get("last_digest") or {}).get("at") or 0) > ((self.state.get("last_digest") or {}).get("at") or 0):
                self.state["last_digest"] = disk["last_digest"]
                self.state["done_since"] = disk.get("done_since")
            snap, new_state, events = pc.collect_snapshot(raw, self.state, now)
            self._notice_metrics(snap, new_state, now)
            snap["digest"] = new_state.get("last_digest")
            snap["widget_version"] = widget_version()
            self.state = new_state
            save_json("state.json", self.state)
            save_json("pulse_now.json", snap)
        for ev in events:
            append("metrics.jsonl", ev)
        kinds = {r["key"]: r["kind"] for r in snap["rows"]}
        for k, kind in kinds.items():
            if self.prev_kinds.get(k) != kind:
                append("pulse.jsonl", {"key": k, "kind": kind, "was": self.prev_kinds.get(k)})
                if kind in ("red", "amber"):
                    notify_phone(next(r for r in snap["rows"] if r["key"] == k))
        self.prev_kinds = kinds
        with self.cond:
            self.snapshot = snap
            self.version += 1
            self.cond.notify_all()
        return snap

    def _notice_metrics(self, snap: dict, state: dict, now: float) -> None:
        """time-to-notice red: first owner prompt (any window) after the incident opened."""
        noticed = state.setdefault("noticed", {})
        reds = [r for r in snap["rows"] if r["kind"] == "red" and r["incident"] not in noticed]
        if not reds:
            return
        oldest = min(r["since"] for r in reds)
        prompts = sorted((h.get("timestamp") or 0) / 1000 for h in pc.owner_prompts(oldest))
        for r in reds:
            after = [t for t in prompts if t > r["since"]]
            if after:
                noticed[r["incident"]] = after[0]
                append("metrics.jsonl", {"m": "red_noticed", "id": r["incident"], "via": "next_prompt",
                                         "latency_s": round(after[0] - r["since"])})
        for k in list(noticed):
            if now - noticed[k] > 3 * 86400:
                noticed.pop(k)

    def ack(self, inc: str, label: str = "actionable") -> bool:
        with _lock:
            row = next((r for r in self.snapshot.get("rows", []) if r.get("incident") == inc), None)
            acks = self.state.setdefault("acks", {})
            acks[inc] = {"at": time.time(), "count": (row or {}).get("count", 1), "label": label}
            # keep the ack table small: drop acks older than 3 days
            for k in [k for k, v in acks.items() if time.time() - v.get("at", 0) > 3 * 86400]:
                acks.pop(k)
            save_json("state.json", self.state)
        append("metrics.jsonl", {"m": "alarm_ack", "id": inc, "label": label,
                                 "kind": (row or {}).get("kind"),
                                 "latency_s": round(time.time() - (row or {}).get("since", time.time()))})
        threading.Thread(target=self.tick, daemon=True).start()
        return True


    def seen(self, sid: str) -> bool:
        with _lock:
            self.state.setdefault("seen_look", {})[sid] = time.time()
            save_json("state.json", self.state)
        threading.Thread(target=self.tick, daemon=True).start()
        return True

    def hand_row(self, sid: str) -> dict | None:
        return next((h for h in pc.read_hands() if h["id"] == sid), None)


def thumb_bytes(path: str, w: int = 78, h: int = 54) -> bytes | None:
    """Cached small JPEG of a handed image (3x the 26x18 chip, so it stays sharp)."""
    import io
    from PIL import Image
    src = Path(path)
    try:
        key = hashlib.sha1(f"{src}|{src.stat().st_mtime_ns}".encode()).hexdigest()[:16]
        cache = pc.STATE_DIR / "thumbs"
        cache.mkdir(parents=True, exist_ok=True)
        c = cache / f"{key}.jpg"
        if c.exists():
            return c.read_bytes()
        from PIL import ImageOps
        with Image.open(src) as im:
            im = ImageOps.fit(im.convert("RGB"), (w, h))
            buf = io.BytesIO()
            im.save(buf, "JPEG", quality=80)
        c.write_bytes(buf.getvalue())
        return buf.getvalue()
    except Exception:
        return None


def hand(target: str, title: str | None, seat: str | None) -> dict:
    """Write one hand-off record (pure file append; the daemon picks it up within 5 s)."""
    if re.match(r"^https?://", target):
        tgt, win = target, None
    else:
        p = Path(target).expanduser()
        p = p if p.is_absolute() else Path.cwd() / p
        tgt = os.path.normpath(str(p))
        win = pc.win_path(tgt)
    rec = {"id": "hand:" + hashlib.sha1(tgt.encode()).hexdigest()[:10], "target": tgt, "win": win,
           "title": title or Path(tgt).name or tgt, "seat": (seat or "").upper() or None, "ts": time.time()}
    append("hands.jsonl", rec)
    return rec


def widget_version() -> str:
    try:
        return hashlib.sha1(WIDGET_HTML.read_bytes()).hexdigest()[:10]
    except OSError:
        return "missing"

# ---------------------------------------------------------------- digest


def back_since(now: float) -> float:
    """Owner's last prompt before the most recent >=30 min gap in his prompt stream."""
    ts = sorted((h.get("timestamp") or 0) / 1000 for h in pc.owner_prompts(now - 36 * 3600))
    ts = [t for t in ts if t < now - 120]
    gaps = [(ts[i], ts[i + 1]) for i in range(len(ts) - 1) if ts[i + 1] - ts[i] >= 1800]
    if ts and now - 120 - ts[-1] >= 1800:
        return ts[-1]
    if gaps:
        return gaps[-1][0]
    return now - 12 * 3600


def parse_since(v: str) -> float:
    """How far back: a duration ("3h", "90m", "2d", "1h30m"), a clock time today ("17:30"), or ISO."""
    import re as _re
    v = v.strip().lower()
    m = _re.fullmatch(r"(?:(\d+)d)?\s*(?:(\d+)h)?\s*(?:(\d+)m)?", v)
    if m and any(m.groups()):
        d, h, mi = (int(x or 0) for x in m.groups())
        return time.time() - (d * 86400 + h * 3600 + mi * 60)
    m = _re.fullmatch(r"(\d{1,2}):(\d{2})", v)
    if m:
        lt = time.localtime()
        t = time.mktime((lt.tm_year, lt.tm_mon, lt.tm_mday, int(m[1]), int(m[2]), 0, 0, 0, -1))
        return t if t <= time.time() else t - 86400
    return pc.iso_to_epoch(v)


def make_digest(mode: str, since: float | None = None) -> dict:
    now = time.time()
    state = load_state()
    if since is None:
        if mode == "back":
            since = back_since(now)
        else:
            last = (state.get("last_digest") or {}).get("at") or 0
            since = max(last, now - 16 * 3600)
    col = Collector()
    raw = col.gather(now)
    snap, _, _ = pc.collect_snapshot(raw, {**state, "done_since": since}, now)
    lines = []
    for r in snap["rows"]:
        if r["kind"] == "red" and r["since"] >= since - 3600:
            lines.append({"g": "✖", "kind": "red", "t": r["since"], "text": r["text"], "link": r.get("link")})
    for r in snap["rows"]:
        if r["kind"] in ("amber", "amber_soft", "review", "warn"):
            lines.append({"g": "◐" if r["kind"] != "review" else "◇", "kind": r["kind"], "t": r["since"],
                          "text": r["text"], "link": r.get("link")})
    for r in sorted((r for r in snap["rows"] if r["kind"] == "done"), key=lambda r: r["since"]):
        lines.append({"g": "✓", "kind": "done", "t": r["since"], "text": f"{r['who']:<8} {r['text']}",
                      "link": r.get("link")})
    for r in snap["rows"]:
        if r["kind"] in ("run", "stuck"):
            lines.append({"g": "▶", "kind": r["kind"], "t": r["since"], "text": r["text"], "link": None})
    c = snap["counts"]
    tail = f"{c['filed']} filed · {c['implemented']} implemented · {c['closed']} closed · {c['verifies']} verifies · {c['drops']} drops"
    span = now - since
    head = (f"rimflow since {time.strftime('%a %H:%M', time.localtime(since))}  "
            f"({int(span // 3600)}h {int(span % 3600 // 60)}m · {mode} · ledger · sessions · memwatch · artpipe)")
    stamp = datetime.fromtimestamp(now).strftime("%Y-%m-%d_%H%M")
    DIGEST_DIR.mkdir(parents=True, exist_ok=True)
    path = DIGEST_DIR / f"digest_{stamp}_{mode}.md"

    def fmt(ln, md=False):
        if not ln["t"]:
            when = "     "
        elif ln["kind"] in ("amber", "amber_soft", "review"):
            a = time.time() - ln["t"]
            when = (f"{int(a // 60)}m" if a < 3600 else f"{int(a // 3600)}h" if a < 86400 else f"{int(a // 86400)}d").rjust(5)
        else:
            when = time.strftime("%H:%M", time.localtime(ln["t"]))
        link = ln.get("link") or {}
        lv = f"   {link['value']}" if link else ""
        return f"{ln['g']} {when}  {ln['text']}{('  `' + link['value'] + '`') if (md and link) else lv}"
    text = "\n".join([head] + ["  " + fmt(ln) for ln in lines] + ["  · " + tail])
    md = "\n".join([f"# {head}", ""] + [f"- {fmt(ln, True)}" for ln in lines] + ["", f"_{tail}_", ""])
    path.write_text(md)
    rec = {"at": now, "mode": mode, "since": since, "path": pc.win_path(str(path)), "head": head,
           "tail": tail, "lines": lines}
    with _lock:
        st = load_state()
        st["last_digest"] = rec
        st["done_since"] = since
        save_json("state.json", st)
    append("metrics.jsonl", {"m": "digest", "mode": mode, "since": since, "lines": len(lines)})
    return {"text": text, "path": rec["path"], "rec": rec}

# ---------------------------------------------------------------- http


def make_handler(col: Collector):
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def _hdr(self, code=200, ctype="application/json"):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()

        def do_OPTIONS(self):
            self._hdr(204)

        def do_GET(self):
            if self.path in ("/", "/index.html"):
                self._hdr(200, "text/html; charset=utf-8")
                self.wfile.write(WIDGET_HTML.read_bytes())
            elif self.path.startswith("/api/now"):
                self._hdr()
                self.wfile.write(json.dumps(col.snapshot).encode())
            elif self.path.startswith("/api/thumb"):
                from urllib.parse import parse_qs, urlparse
                h = col.hand_row((parse_qs(urlparse(self.path).query).get("id") or [""])[0])
                data = thumb_bytes(h["target"]) if h and not h["target"].startswith("http") else None
                if data:
                    self._hdr(200, "image/jpeg")
                    self.wfile.write(data)
                else:
                    self._hdr(404)
            elif self.path.startswith("/api/stream"):
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Cache-Control", "no-store")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                seen = -1
                try:
                    while True:
                        with col.cond:
                            if col.version == seen:
                                col.cond.wait(timeout=15)
                            v, snap = col.version, col.snapshot
                        if v != seen:
                            self.wfile.write(b"data: " + json.dumps(snap).encode() + b"\n\n")
                            seen = v
                        else:
                            self.wfile.write(b": hb\n\n")
                        self.wfile.flush()
                except (BrokenPipeError, ConnectionResetError, OSError):
                    return
            else:
                self._hdr(404)

        def do_POST(self):
            n = int(self.headers.get("Content-Length") or 0)
            try:
                body = json.loads(self.rfile.read(n) or b"{}")
            except ValueError:
                body = {}
            if self.path == "/api/ack" and body.get("id"):
                col.ack(str(body["id"]), "noise" if body.get("noise") else "actionable")
                self._hdr()
                self.wfile.write(b'{"ok":true}')
            elif self.path == "/api/seen" and body.get("id"):
                col.seen(str(body["id"]))
                self._hdr()
                self.wfile.write(b'{"ok":true}')
            elif self.path == "/api/probe":
                col.probe = {"rimworld_running": bool(body.get("rimworld_running")), "at": time.time(),
                             "host": str(body.get("host", ""))[:40]}
                self._hdr()
                self.wfile.write(b'{"ok":true}')
            elif self.path == "/api/metric" and body.get("m"):
                append("metrics.jsonl", {k: v for k, v in body.items() if isinstance(v, (str, int, float))})
                self._hdr()
                self.wfile.write(b'{"ok":true}')
            else:
                self._hdr(404)
    return H


def daemon() -> None:
    col = Collector()
    col.tick()
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), make_handler(col))
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    print(f"pulse: serving http://127.0.0.1:{PORT}/  state {pc.STATE_DIR}", flush=True)
    while True:
        time.sleep(INTERVAL)
        try:
            col.tick()
        except Exception as e:  # never die on one bad tick; the snapshot just ages and goes STALE
            print(f"pulse: tick failed: {type(e).__name__}: {e}", flush=True)


def metrics() -> None:
    recs = pc.read_jsonl_tail(_p("metrics.jsonl"), 8 << 20)
    def med(xs):
        xs = sorted(xs)
        return xs[len(xs) // 2] if xs else None
    notice = [r["latency_s"] for r in recs if r.get("m") == "red_noticed"]
    qage = [r["age_s"] for r in recs if r.get("m") == "alarm_close" and r.get("kind") == "amber"]
    acks = [r for r in recs if r.get("m") == "alarm_ack"]
    good = sum(1 for r in acks if r.get("label") == "actionable")
    print(f"red time-to-notice : n={len(notice)} median={med(notice)} s")
    print(f"question age       : n={len(qage)} median={med(qage)} s  p90={sorted(qage)[int(len(qage)*.9)] if qage else None} s")
    print(f"alert precision    : {good}/{len(acks)} acks labelled actionable" if acks else "alert precision    : no acks yet")
    print(f"log                : {_p('metrics.jsonl')}")


def health(restart: bool) -> int:
    import subprocess
    import urllib.request
    try:
        snap = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/api/now", timeout=10).read())
        age = time.time() - snap.get("collected_at", 0)
    except Exception as e:
        age, snap = None, {"error": str(e)}
    ok = age is not None and age < 60
    print(f"pulse health: {'ok' if ok else 'BAD'} age={None if age is None else round(age)}s")
    if not ok and restart:
        append("metrics.jsonl", {"m": "spine_restart", "age_s": age})
        subprocess.run(["systemctl", "--user", "restart", "rm-pulse.service"], timeout=20)
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("daemon")
    sub.add_parser("collect")
    s = sub.add_parser("since")
    g = s.add_mutually_exclusive_group()
    g.add_argument("--back", action="store_true")
    g.add_argument("--scheduled", action="store_true")
    g.add_argument("--since")
    s.add_argument("--quiet", action="store_true")
    a = sub.add_parser("ack")
    a.add_argument("incident")
    a.add_argument("--noise", action="store_true")
    hd = sub.add_parser("hand")
    hd.add_argument("target")
    hd.add_argument("--title")
    hd.add_argument("--seat")
    sn = sub.add_parser("seen")
    sn.add_argument("id")
    sub.add_parser("metrics")
    h = sub.add_parser("health")
    h.add_argument("--restart", action="store_true")
    args = ap.parse_args(argv)
    if args.cmd == "daemon":
        daemon()
    elif args.cmd == "collect":
        snap = Collector().tick()
        for r in snap["rows"]:
            print(f"{r['kind']:<10} {r['who']:<9} {r['text']}")
        print(" | ".join(p["text"] for p in snap["strip"]))
    elif args.cmd == "since":
        mode = "back" if args.back else "scheduled" if args.scheduled else "manual"
        since = parse_since(args.since) if args.since else None
        d = make_digest(mode, since)
        if not args.quiet:
            print(d["text"])
        print(f"saved: {d['path']}")
    elif args.cmd == "ack":
        import urllib.request
        req = urllib.request.Request(f"http://127.0.0.1:{PORT}/api/ack", method="POST",
                                     data=json.dumps({"id": args.incident, "noise": args.noise}).encode(),
                                     headers={"Content-Type": "application/json"})
        print(urllib.request.urlopen(req, timeout=5).read().decode())
    elif args.cmd == "hand":
        r = hand(args.target, args.title, args.seat)
        print(f"handed: {r['id']}  {r['title']}  ->  {r['win'] or r['target']}")
    elif args.cmd == "seen":
        import urllib.request
        req = urllib.request.Request(f"http://127.0.0.1:{PORT}/api/seen", method="POST",
                                     data=json.dumps({"id": args.id}).encode(),
                                     headers={"Content-Type": "application/json"})
        print(urllib.request.urlopen(req, timeout=5).read().decode())
    elif args.cmd == "metrics":
        metrics()
    elif args.cmd == "health":
        return health(args.restart)
    return 0


if __name__ == "__main__":
    sys.exit(main())
