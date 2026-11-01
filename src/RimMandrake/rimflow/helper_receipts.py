#!/usr/bin/env python3
"""helper_receipts.py — what a dead window left unfinished reaches the next one (HELPER_REGISTRY_BUILD_DURABLE_RECEIPTS).

Why it is shaped this way: a parent that dies by SIGKILL, a crash or a reboot writes nothing, so a registry the parent
keeps is empty exactly when it is needed. The harness already keeps one that outlives every parent: the window's
transcript, its subagents/ directory and its tasks/ output files. So the registry is read, not written, and by a
program: `collect` reads each dead window of a seat's project once and leaves one receipt.

MEASURED 2026-11-01, real claude_bounded runs (D:\\ClaudeWork\\rimmandrake\\helpers_dead_parent\\probe):
  SIGTERM (restart_kill: goodbye, ticket restart, backstop)  claude gone inside 3 s; a background Bash and a subagent's
    running Bash are killed (exit 137 is the last record); no final report; a setsid process runs on.
  SIGKILL (crash, restart_kill's fallback)  the same LLM loops die, but both Bash commands run on as orphans and
    finish, unread; a setsid process runs on.
  /clear  the only route that lost a helper in 7 days: 4 of 1244, and it has no restart, so no wake reads anything.
  reboot, WSL restart  everything on the machine dies with it; a process on another machine runs on with nobody watching.

A receipt has three lists:
  died    a helper that had not finished and whose notice never came: its work stopped mid-way, nobody was told
  unread  a helper that reported, but no turn of the parent came after the report
  bash    a background command whose notice no turn saw: it ended with the window, or is running with no reader
A helper whose notice came before the parent's last turn is the normal case and is no finding.

Readers: `seat_restart.py wake` prints a seat's open receipts in the next window, and the Dispatcher raises one
`helper_lost:<session>` alarm per receipt, the route for the deaths that have no wake (/clear, a quit, a crash).
A receipt stays open until `helper_receipts.py ack`. Relentless workers are outside this by construction: they run in
their own clones' projects, hold no helpers, and their state is on disk. A run that must outlive its window belongs in
`systemd-run --user`; the receipt only says that it needs a new watcher.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import doorbell  # noqa: E402
import seat_restart as SR  # noqa: E402

SETTLE_S = 300            # a window with no live process, silent this long, is dead (a named predecessor needs no wait)
MAX_AGE_S = 3 * 86400     # older transcripts are not read; `collect --since-days` reaches further back by hand
MAX_READS = 6             # transcripts parsed in one call, so one tick stays cheap; the rest come next tick
REPORT_CHARS = 1500

NOTICE = re.compile(r"<task-id>([^<\\]+)</task-id>.{0,700}?<status>(\w+)</status>", re.S)
BG_ID = re.compile(r"running in background with ID: (\w+)")
BG_OUT = re.compile(r"written to: (\S+?\.output)")


def receipts_dir(seat, root=None):
    return os.path.join(root or doorbell.state_dir(), "receipts", seat)


def receipt_path(seat, session, root=None):
    return os.path.join(receipts_dir(seat, root), "%s.json" % session)


def live_sessions():
    """-> the session ids of processes alive now. A session file names the current session of its pid. An unreadable
    directory raises: read as "nobody is alive" it would receipt every live window."""
    out = set()
    for n in os.listdir(os.path.join(SR.claude_home(), "sessions")):
        if not n.endswith(".json"):
            continue
        d = SR._read_json(os.path.join(SR.claude_home(), "sessions", n)) or {}
        try:
            os.kill(int(d.get("pid")), 0)
        except PermissionError:
            pass
        except (OSError, TypeError, ValueError):
            continue
        if d.get("sessionId"):
            out.add(d["sessionId"])
    return out


def _ts(s):
    return (SR._ts(s) if s else None) or None


def _text_of(rec):
    c = (rec.get("message") or {}).get("content")
    if isinstance(c, str):
        return c
    return "\n".join(b.get("text") or "" for b in c or [] if isinstance(b, dict) and b.get("type") == "text").strip()


def _read_main(path):
    """One pass over a parent transcript -> what it knows of its helpers, by line position. A /clear queued after the
    last assistant record is how that window ended: /clear starts a new session, so the old file just stops."""
    rows = {"last_assistant": -1, "last_at": None, "cleared": False, "notes": {}, "pending": [], "bg": {}, "done": set()}
    with open(path, errors="replace") as f:
        for pos, line in enumerate(f):
            if line.startswith('{"type":"api-request'):
                continue
            try:
                r = json.loads(line)
            except ValueError:
                continue                 # the last line of a killed writer may be torn: the rest still counts
            t = r.get("type")
            rows["last_at"] = _ts(r.get("timestamp")) or rows["last_at"]
            if t == "assistant":
                rows["last_assistant"], rows["cleared"] = pos, False
            if t == "queue-operation":
                op, body = r.get("operation"), str(r.get("content") or "")
                if "/clear" in body[:20]:
                    rows["cleared"] = True
                if op == "enqueue" and body.lstrip().startswith("<task-notification>"):
                    rows["pending"] += NOTICE.findall(body)
                elif op in ("remove", "dequeue"):
                    for tid, status in rows["pending"]:   # taken off the queue: the turn after it saw them
                        rows["notes"].setdefault(tid, (status, pos))
                    rows["pending"] = []
            elif t in ("user", "attachment") and SR._is_helper_notice(r):
                for tid, status in NOTICE.findall(line):
                    rows["notes"].setdefault(tid, (status, pos))
            content = (r.get("message") or {}).get("content")
            for c in content if isinstance(content, list) else []:
                if not isinstance(c, dict):
                    continue
                if c.get("type") == "tool_use" and c.get("name") == "Bash" and (c.get("input") or {}).get("run_in_background"):
                    rows["bg"][c["id"]] = {"cmd": (c.get("input") or {}).get("command", "")[:300]}
                elif c.get("type") == "tool_result":
                    body = json.dumps(c.get("content"))[:2000]
                    tu = c.get("tool_use_id")
                    if tu in rows["bg"]:
                        got, out = BG_ID.search(body), BG_OUT.search(body)
                        rows["bg"][tu].update(id=got.group(1) if got else None, output=out.group(1) if out else None)
                    if "Async agent launched" not in body:
                        rows["done"].add(tu)     # a foreground Agent's result is its report
    return rows


def _helper_detail(path):
    """-> {cwd, last_cmd, last_at, final}: the tail of one helper's transcript, whole file read (a helper's is small)."""
    d = {"cwd": None, "last_cmd": None, "last_at": None, "final": ""}
    with open(path, errors="replace") as f:
        for line in f:
            if line.startswith('{"type":"api-request'):
                continue
            try:
                r = json.loads(line)
            except ValueError:
                continue
            d["cwd"] = r.get("cwd") or d["cwd"]
            d["last_at"] = _ts(r.get("timestamp")) or d["last_at"]
            if r.get("type") != "assistant":
                continue
            d["final"] = _text_of(r) or d["final"]
            for c in (r.get("message") or {}).get("content") or []:
                if isinstance(c, dict) and c.get("type") == "tool_use":
                    d["last_cmd"] = str((c.get("input") or {}).get("command") or c.get("name"))[:300]
    return d


def tree_of(cwd):
    """-> {clone, dirty, unlanded} or None (UNMEASURED: gone, not a clone, or git refused): what the dead helper left."""
    if not cwd or not os.path.isdir(cwd):
        return None
    try:
        top = subprocess.run(["git", "-C", cwd, "rev-parse", "--show-toplevel"], capture_output=True, text=True, timeout=20)
        if top.returncode:
            return None
        dirty = subprocess.run(["git", "-C", cwd, "status", "--porcelain"], capture_output=True, text=True, timeout=60)
        ahead = subprocess.run(["git", "-C", cwd, "rev-list", "--count", "@{u}..HEAD"], capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.SubprocessError):
        return None
    return {"clone": top.stdout.strip(), "dirty": len(dirty.stdout.splitlines()) if dirty.returncode == 0 else None,
            "unlanded": int(ahead.stdout) if ahead.returncode == 0 and ahead.stdout.strip().isdigit() else None}


def how_it_ended(session, last_at, cleared, seat, root=None, btime=None):
    killed = SR._read_json(SR.killed_path(seat, root)) or {}
    if killed.get("session_id") == session:
        return "restart kill (%s)" % (killed.get("source") or "?")
    if cleared:
        return "/clear"
    if last_at and btime and last_at < btime:
        return "before the last boot: the restart, or a quit or crash earlier"
    return "the transcript just stops: a quit or a crash"


def boot_time():
    try:
        with open("/proc/stat") as f:
            return next((float(x.split()[1]) for x in f if x.startswith("btime ")), None)
    except OSError:
        return None


def harvest(path, seat, now=None, root=None):
    """The receipt of one dead window. The parent is dead by the caller's word; nothing here decides that."""
    now = now or time.time()
    session = os.path.basename(path)[:-len(".jsonl")]
    rows = _read_main(path)
    acted = lambda tid: tid in rows["notes"] and rows["notes"][tid][1] < rows["last_assistant"]   # noqa: E731
    rec = {"session": session, "seat": seat, "transcript": path, "read_at": now, "last_at": rows["last_at"],
           "ended": how_it_ended(session, rows["last_at"], rows["cleared"], seat, root, boot_time()),
           "died": [], "unread": [], "bash": []}
    hs = SR.helpers_of(path)
    if hs is None:
        rec["unmeasured"] = "its subagents directory or a helper transcript cannot be read"
        hs = []
    for h in hs:
        aid = h["id"][len("agent-"):]
        f = os.path.join(path[:-len(".jsonl")], "subagents", h["id"] + ".jsonl")
        meta = SR._read_json(f[:-len(".jsonl")] + ".meta.json") or {}
        if acted(aid) or meta.get("toolUseId") in rows["done"]:
            continue
        d = _helper_detail(f)
        one = {"id": aid, "desc": h.get("desc"), "last_at": d["last_at"], "transcript": f, "cwd": d["cwd"]}
        if not h["alive"] or aid in rows["notes"]:
            rec["unread"].append(dict(one, status=(rows["notes"].get(aid) or ("no notice",))[0],
                                      report=d["final"][-REPORT_CHARS:]))
        else:
            rec["died"].append(dict(one, last_cmd=d["last_cmd"], tree=tree_of(d["cwd"])))
    for b in rows["bg"].values():
        if b.get("id") and not acted(b["id"]):
            rec["bash"].append(b)
    return rec


def has_findings(rec):
    return bool(rec.get("died") or rec.get("unread") or rec.get("bash") or rec.get("unmeasured"))


def _worth_parsing(path):
    """Cheap first look: a window with no helper directory and no background Bash has nothing to find."""
    if os.path.isdir(path[:-len(".jsonl")] + "/subagents"):
        return True
    with open(path, "rb") as f:
        return b'"run_in_background":true' in f.read()


def collect(seat, clone, root=None, now=None, force=(), since_s=MAX_AGE_S, max_reads=MAX_READS, live=None):
    """Read the dead windows of this seat's project not yet receipted -> [new receipts with findings]. A live session is
    never read; one with no live process must also be silent SETTLE_S, unless the caller names it in force (the wake
    knows its predecessor is dead). Every window gets a file, an empty one too, so it is read once."""
    now = now or time.time()
    live = live_sessions() if live is None else live
    project = os.path.dirname(SR.transcript_path(clone, "x"))
    try:
        names = [n for n in os.listdir(project) if n.endswith(".jsonl")]
    except OSError:
        return []
    os.makedirs(receipts_dir(seat, root), exist_ok=True)
    seen = set(os.listdir(receipts_dir(seat, root)))
    new, todo = [], []
    for n in names:
        sid = n[:-len(".jsonl")]
        if sid + ".json" in seen or sid in live:
            continue
        p = os.path.join(project, n)
        try:
            age = now - os.path.getmtime(p)
        except OSError:
            continue
        if sid in force or (SETTLE_S <= age <= since_s):
            todo.append((sid not in force, age, sid, p))
    reads = 0
    for _, _, sid, p in sorted(todo):         # the named predecessor first, then the newest
        if not _worth_parsing(p):
            SR._write_json(receipt_path(seat, sid, root), {"session": sid, "empty": True})
            continue
        if reads >= max_reads:
            continue
        reads += 1
        rec = harvest(p, seat, now, root)
        if os.path.exists(receipt_path(seat, sid, root)):
            continue                    # a concurrent collector published (maybe acked) it while we parsed: never overwrite
        SR._write_json(receipt_path(seat, sid, root), rec if has_findings(rec) else {"session": sid, "empty": True})
        if has_findings(rec):
            new.append(rec)
    return new


def stamp(seats, root=None, now=None):
    """The reading a `rimflow close --live` promise watches: a tick read every seat's dead windows, whether or not any
    died. A dead reader goes stale here long before anyone misses a receipt."""
    path = os.path.join(root or doorbell.state_dir(), "receipts", "last_read.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    SR._write_json(path, {"read_at": now or time.time(), "seats": sorted(seats)})
    return path


def open_receipts(seat, root=None):
    out = []
    try:
        names = os.listdir(receipts_dir(seat, root))
    except OSError:
        return out
    for n in sorted(names):
        rec = SR._read_json(os.path.join(receipts_dir(seat, root), n))
        if rec and has_findings(rec) and not rec.get("acked_at"):
            out.append(rec)
    return sorted(out, key=lambda r: r.get("last_at") or 0)


def ack(seat, session, root=None, now=None):
    """Mark one receipt taken. session may be a unique prefix. -> the sessions acked."""
    done = []
    hits = [r for r in open_receipts(seat, root) if session == "all" or r["session"].startswith(session)]
    if session != "all" and len(hits) > 1:
        return []                       # an ambiguous prefix acks nothing: an unread receipt must not be hidden by a typo
    for rec in hits:
        rec["acked_at"] = now or time.time()
        SR._write_json(receipt_path(seat, rec["session"], root), rec)
        done.append(rec["session"])
    return done


def one_line(rec):
    return "window %s of %s ended %s (%s): %d helper(s) died mid-work, %d report(s) unread, %d background command(s) " \
           "with no reader" % (rec["session"][:8], rec["seat"], SR._iso(rec.get("last_at") or 0), rec.get("ended"),
                               len(rec["died"]), len(rec["unread"]), len(rec["bash"]))


def render(rec):
    """-> lines a fresh window can act on: every finding names its file."""
    out = ["- " + one_line(rec) + ". Transcript: %s" % rec["transcript"]]
    if rec.get("unmeasured"):
        out.append("  UNMEASURED: %s" % rec["unmeasured"])
    for h in rec["died"]:
        t = h.get("tree")
        tree = "clone %s: %s dirty, %s unlanded" % (t["clone"], t["dirty"], t["unlanded"]) if t else \
            "clone UNMEASURED (cwd %s)" % h.get("cwd")
        out.append("  DIED MID-WORK %s (%s), last at %s; %s. Last command: %s. Its transcript: %s" % (
            h["id"], h.get("desc") or "?", SR._iso(h.get("last_at") or 0), tree, (h.get("last_cmd") or "?")[:200],
            h["transcript"]))
    for h in rec["unread"]:
        out.append("  REPORT NOBODY READ %s (%s, %s). Its transcript: %s\n  | %s" % (
            h["id"], h.get("desc") or "?", h.get("status"), h["transcript"],
            (h.get("report") or "(no final text)").replace("\n", "\n  | ")))
    for b in rec["bash"]:
        out.append("  BACKGROUND COMMAND WITH NO READER %s: %s. Output: %s. It ended with the window or runs unwatched; "
                   "if what it watched still matters, start it again." % (b["id"], b["cmd"][:200], b.get("output")))
    return out


def wake_lines(seat, clone, force=(), root=None):
    """-> lines for `seat_restart.py wake`: this seat's open receipts, the predecessor's read now."""
    collect(seat, clone, root=root, force=force)
    recs = open_receipts(seat, root)
    if not recs:
        return []
    out = ["\n== RECEIPTS from dead windows of this seat: work nobody finished or read. Judge each, then "
           "`python3 src/RimMandrake/rimflow/helper_receipts.py ack --seat %s <session|all>`:" % seat]
    for r in recs:
        out += render(r)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("list", "collect", "ack"):
        p = sub.add_parser(name)
        p.add_argument("--seat", required=True)
    sub.choices["ack"].add_argument("session")
    sub.choices["collect"].add_argument("--clone", required=True)
    sub.choices["collect"].add_argument("--since-days", type=float, default=MAX_AGE_S / 86400)
    sub.choices["collect"].add_argument("--max-reads", type=int, default=MAX_READS)
    args = ap.parse_args(argv)
    seat = args.seat.upper()
    if args.cmd == "ack":
        print("acked: %s" % (", ".join(ack(seat, args.session)) or "nothing"))
    elif args.cmd == "collect":
        new = collect(seat, args.clone, since_s=args.since_days * 86400, max_reads=args.max_reads)
        print("%d new receipt(s) with findings" % len(new))
        for r in new:
            print("\n".join(render(r)))
    else:
        for r in open_receipts(seat):
            print("\n".join(render(r)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
