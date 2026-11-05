#!/usr/bin/env python3
"""The station note box (STATION_NOTEBOX_BUILD_WHISPER_AT_NEXT_TURN; report steps 3-4 of
design/RimMandrake/agent_visibility_2026-11-04/report.md). The owner (or the Conductor, with his authority) sends a note
to the worker that is running an item; it reaches that worker's conversation at its next turn and is kept in the record.

Delivery way (chosen by the probe, design/RimMandrake/agent_visibility_2026-11-04/notebox_probe.md): a mailbox read by
two Claude Code hooks in the worker's own session, so the launch shape (`claude -p ... --output-format json` in a
systemd unit) is untouched:
  PostToolUse  a pending note rides back with the next tool result (additionalContext), mid-run;
  Stop         a note still pending when the worker tries to end blocks that stop once, with the note as the reason.

Binding: a note is bound at send time to (item, gen), the execution running then. Only a session whose project clone's
marker (.git/relentless.json under CLAUDE_PROJECT_DIR) names that item, and whose RELENTLESS_GEN (set only at a worker's
launch) is that gen, receives it: any other session in the clone (a helper, the owner's own `claude`) has no
RELENTLESS_GEN and receives nothing. A note
never follows a station to other work, nor to a later gen of the same item: one left pending when its run ends stays
pending in the record (`show`) and is sent again on purpose (`send --gen`). Delivery is at most once: the note is
marked before the hook prints it, so a hook killed in between loses that one delivery (never doubles it); the record and
learned.md still carry the text to the item's next worker. A subagent's tool call (event carries
agent_id) delivers nothing, so the note lands in the worker's main thread. Take-over is not built (owner, 2026-11-05:
"3 no").

Record: <relentless root>/store/items/<ITEM>/notes.jsonl, append-only: {"kind": "sent"|"delivered", ...}. Each event
is also a line in the store journal, and a delivered note is appended to the item's learned.md, so the next worker's
brief carries it.

  notebox.py send ITEM "text" [--gen G] [--by NAME]   bind to the running gen (or G); prints the note id
  notebox.py show ITEM [--json]                       every note with its state
  notebox.py deliver --event PostToolUse|Stop         the hook entry (reads the hook event on stdin)
"""
import argparse
import contextlib
import fcntl
import json
import os
import sys
import time
import uuid

DEFAULT_ROOT = "/home/mandrake/rm/relentless"   # relentless.py's DEFAULT_ROOT; RELENTLESS_ROOT overrides both
MAX_TEXT = 4000


def root():
    return os.environ.get("RELENTLESS_ROOT") or DEFAULT_ROOT


def item_dir(item, base=None):
    return os.path.join(base or root(), "store", "items", item)


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _append(path, rec):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    line = json.dumps(rec, sort_keys=True)
    with open(path, "a+b") as f:
        f.seek(0, os.SEEK_END)
        head = b""
        if f.tell():        # a torn last line would glue this record onto it
            f.seek(-1, os.SEEK_END)
            head = b"" if f.read(1) == b"\n" else b"\n"
        f.write(head + (line + "\n").encode("utf-8"))
        f.flush()
        os.fsync(f.fileno())


class Busy(Exception):
    """The note lock stayed held past the wait: the hook delivers nothing this time, the note stays pending."""


@contextlib.contextmanager
def _locked(item, base=None, wait_s=None):
    """wait_s None: block (send, show). A number: give up after it (the hook must never stall a session)."""
    d = item_dir(item, base)
    os.makedirs(d, exist_ok=True)
    fd = os.open(os.path.join(d, "notes.lock"), os.O_CREAT | os.O_RDWR, 0o644)
    try:
        if wait_s is None:
            fcntl.flock(fd, fcntl.LOCK_EX)
        else:
            end = time.monotonic() + wait_s
            while True:
                try:
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except BlockingIOError:
                    if time.monotonic() >= end:
                        raise Busy("notes lock held over %.1f s" % wait_s)
                    time.sleep(0.05)
        yield
    finally:
        os.close(fd)


def records(item, base=None):
    try:
        with open(os.path.join(item_dir(item, base), "notes.jsonl"), encoding="utf-8") as f:
            lines = f.readlines()
    except OSError:
        return []
    out = []
    for ln in lines:
        try:
            out.append(json.loads(ln))
        except ValueError:      # one torn line loses that line, never the record around it
            pass
    return out


def notes(item, base=None):
    """-> [note dict with "state": pending|delivered], in send order."""
    got, order = {}, []
    for r in records(item, base):
        if r.get("kind") == "sent" and r.get("id") not in got:
            got[r["id"]] = dict(r, state="pending")
            order.append(r["id"])
        elif r.get("kind") == "delivered" and r.get("id") in got:
            got[r["id"]].update(state="delivered", delivered_at=r.get("at"), event=r.get("event"),
                                session=r.get("session"))
    return [got[i] for i in order]


def _journal(base, rec):
    try:
        _append(os.path.join(base or root(), "store", "journal.jsonl"), rec)
    except OSError:
        pass        # the note record is the authority; the journal line is a convenience


def running_gen(item, base=None):
    """-> (gen, status) from the item's state.json, or (None, why)."""
    try:
        with open(os.path.join(item_dir(item, base), "state.json"), encoding="utf-8") as f:
            st = json.load(f)
    except (OSError, ValueError) as e:
        return None, "no readable state for %s (%s)" % (item, type(e).__name__)
    return int(st.get("gen") or 0), st.get("status")


def send(item, text, gen=None, by="owner", base=None):
    """-> (note id, None) or (None, why refused)."""
    text = (text or "").strip()
    if not text:
        return None, "empty note"
    if len(text) > MAX_TEXT:
        return None, "note over %d characters" % MAX_TEXT
    if gen is None:
        g, status = running_gen(item, base)
        if g is None:
            return None, status
        if status != "running":
            return None, ("%s is %s, not running: no worker would read it (pass --gen to bind to a later one)"
                          % (item, status))
        gen = g
    nid = "note-" + uuid.uuid4().hex[:12]
    rec = {"kind": "sent", "id": nid, "item": item, "gen": int(gen), "text": text, "by": by, "at": now()}
    with _locked(item, base):
        _append(os.path.join(item_dir(item, base), "notes.jsonl"), rec)
    _journal(base, {"do": "note_sent", "item": item, "gen": int(gen), "id": nid, "by": by, "at": rec["at"]})
    return nid, None


def _marker(proj):
    """-> (item, gen) for a worker session of the Relentless clone at proj, else None. Never raises. The gen is
    RELENTLESS_GEN alone (set at a worker's launch, so a resumed old session cannot read a new marker); a session
    without it is not a worker and gets nothing. The item is the marker's in proj itself, the directory the hook gate
    read, never wherever the tool call's cwd wandered."""
    env_gen = os.environ.get("RELENTLESS_GEN")
    if not env_gen:
        return None
    try:
        with open(os.path.join(proj, ".git", "relentless.json"), encoding="utf-8") as f:
            m = json.load(f)
        return m["item"], int(env_gen)
    except (OSError, ValueError, KeyError, TypeError):
        return None


def _append_text(path, text):
    """learned.md's own shape (relentless.py Store.learn): plain text, one line per record."""
    with open(path, "a+b") as f:
        f.seek(0, os.SEEK_END)
        head = b""
        if f.tell():
            f.seek(-1, os.SEEK_END)
            head = b"" if f.read(1) == b"\n" else b"\n"
        f.write(head + (text.rstrip("\n") + "\n").encode("utf-8"))
        f.flush()
        os.fsync(f.fileno())


def take(item, gen, event, session=None, base=None, wait_s=2.0):
    """Mark every pending note bound to (item, gen) delivered, at most once, and return them. Raises Busy."""
    with _locked(item, base, wait_s):
        due = [n for n in notes(item, base) if n["state"] == "pending" and n.get("gen") == gen]
        at = now()
        for n in due:
            _append(os.path.join(item_dir(item, base), "notes.jsonl"),
                    {"kind": "delivered", "id": n["id"], "item": item, "gen": gen, "event": event,
                     "session": session, "at": at})
            try:
                _append_text(os.path.join(item_dir(item, base), "learned.md"),
                             "%s owner note %s (by %s, delivered to gen %d at %s): %s"
                             % (at, n["id"], n.get("by"), gen, event, " ".join(n["text"].split())))
            except OSError:
                pass
    for n in due:
        _journal(base, {"do": "note_delivered", "item": item, "gen": gen, "id": n["id"], "event": event, "at": at})
    return due


def message(due):
    lines = ["NOTE FROM THE OWNER via the station note box (the supervisor's record, notebox.py; it carries his "
             "authority as a Conductor instruction does, per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM). "
             "Act on it now, then carry on with your item:"]
    for n in due:
        lines.append("- [%s, sent %s by %s] %s" % (n["id"], n.get("at"), n.get("by"), n["text"]))
    return "\n".join(lines)


def deliver(event_name, ev, base=None):
    """The hook body. -> the JSON the hook prints, or None to print nothing."""
    if ev.get("agent_id"):          # a subagent's tool call: the note belongs to the worker's main thread
        return None
    m = _marker(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    if not m:
        return None
    item, gen = m
    due = take(item, gen, event_name, ev.get("session_id"), base)
    if not due:
        return None
    if event_name == "Stop":
        return {"decision": "block", "reason": message(due)}
    return {"hookSpecificOutput": {"hookEventName": event_name, "additionalContext": message(due)}}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("send")
    s.add_argument("item")
    s.add_argument("text")
    s.add_argument("--gen", type=int)
    s.add_argument("--by", default="owner")
    w = sub.add_parser("show")
    w.add_argument("item")
    w.add_argument("--json", action="store_true")
    d = sub.add_parser("deliver")
    d.add_argument("--event", required=True, choices=("PostToolUse", "Stop"))
    a = ap.parse_args(argv)
    if a.cmd == "send":
        nid, why = send(a.item, a.text, a.gen, a.by)
        if why:
            print("REFUSED: " + why, file=sys.stderr)
            return 2
        print(nid)
        return 0
    if a.cmd == "show":
        ns = notes(a.item)
        if a.json:
            print(json.dumps(ns, indent=1))
        else:
            for n in ns:
                print("%s  gen %s  %-9s  sent %s by %s%s\n    %s" % (
                    n["id"], n.get("gen"), n["state"], n.get("at"), n.get("by"),
                    ("  delivered %s at %s" % (n.get("delivered_at"), n.get("event"))) if n["state"] == "delivered"
                    else "", n["text"][:300]))
            if not ns:
                print("no notes for %s" % a.item)
        return 0
    # deliver: a hook must never break the session it runs in
    try:
        ev = json.load(sys.stdin)
        out = deliver(a.event, ev if isinstance(ev, dict) else {})
    except Exception as e:      # noqa: BLE001 -- report on stderr, never fail the tool call
        print("notebox deliver: %s: %s" % (type(e).__name__, e), file=sys.stderr)
        return 0
    if out:
        print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
