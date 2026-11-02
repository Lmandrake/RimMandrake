#!/usr/bin/env python3
"""helper_checkpoint.py — a draining window tells its in-process helpers to checkpoint, waits a bounded time, and
names every helper still alive at the deadline as LOST with its item (CONDUCTOR_RESTART_REDESIGN_NEVER_FREEZE_HIM).

Owner, 2026-11-02: "It seems like there's a need to have a context-draining agent be able to redirect long-running
subagents to just write out their results to their tickets and send them elsewhere, so the agent can restart or
something. This is really a problem."

Claude Code cannot re-parent an in-process (Agent tool) helper: it dies with its window. So a window that must restart
while helpers run does this, through `seat_restart.py checkpoint` (this file is its body):

    seat_restart.py checkpoint --seat BENCH          # lists live helpers, records a deadline, prints ORDER per helper
    (SendMessage each helper: to=<agentId>, message=ORDER)
    seat_restart.py checkpoint --seat BENCH --wait   # bounded poll; re-run until DONE or LOST (deadline is recorded)
    commit + ./publish your shard, then `seat_restart.py request` as usual

At the deadline every helper still alive is LOST: the record names it and its item, a `rimflow note` goes on the item
(so `next` / a fresh run picks it up), and seat_restart.helpers_of reads it as retired, so the Dispatcher's kill no
longer waits on it. The wake digest prints the lost list. Long work should not be in-process at all: detached_helper.py.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

ORDER = ("Checkpoint now: write your state, evidence paths and one imperative NEXT as a note on your item, "
         "commit and publish what is done, then stop.")
DEFAULT_WAIT_S = 600        # the bounded wait the owner's order allows a helper to checkpoint
POLL_CAP_S = 500            # one --wait call stays under a window's 600 s tool ceiling
POLL_S = 15
LOST_WORD = "LOST at checkpoint (deadline passed alive)"   # seat_restart.helpers_of's retired reason
ITEM_RE = re.compile(r"\b[A-Z][A-Z0-9]+(?:_[A-Z0-9]+){2,}\b")
LEAD_RE = re.compile(r"\b(?:[Ii]tem|ITEM|claim|ticket)[:\s`]+([A-Z][A-Z0-9]+(?:_[A-Z0-9]+){2,})")


def record_path(session_id, root=None):
    import seat_restart as SR
    return os.path.join(SR.restart_dir(root), "checkpoint-%s.json" % session_id)


def read_record(session_id, root=None):
    try:
        with open(record_path(session_id, root), encoding="utf-8") as f:
            d = json.load(f)
        return d if isinstance(d, dict) else None
    except (OSError, ValueError):
        return None


def write_record(rec, root=None):
    p = record_path(rec["session_id"], root)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=1, sort_keys=True)
    os.replace(tmp, p)
    return p


def lost_ids(tx_path, now, root=None):
    """The helper ids of this window whose checkpoint deadline has passed: helpers_of retires them. Empty when no
    checkpoint was recorded for the window (the default: nothing changes without the order having been given)."""
    if not tx_path:
        return {}
    rec = read_record(os.path.basename(tx_path)[:-len(".jsonl")], root)
    if not rec or now < float(rec.get("deadline") or 0):
        return {}
    return {h["id"]: h.get("items") or [] for h in rec.get("helpers") or [] if h.get("id")}


def known_items(repo=REPO):
    """Every id the ledger has a `file` event for, read from the shards (the instrument; a set of 0 means blind)."""
    ids = set()
    d = os.path.join(repo, "infrastructure", "state", "ledger", "events")
    try:
        names = os.listdir(d)
    except OSError:
        return ids
    for n in names:
        if not n.endswith(".jsonl"):
            continue
        try:
            with open(os.path.join(d, n), encoding="utf-8", errors="replace") as f:
                for line in f:
                    if '"event":"file"' not in line.replace(" ", ""):
                        continue
                    try:
                        ev = json.loads(line)
                    except ValueError:
                        continue
                    if ev.get("event") == "file" and ev.get("id"):
                        ids.add(ev["id"])
        except OSError:
            continue
    return ids


def first_prompt(helper_file):
    """The text the helper was spawned with: its first user record."""
    try:
        with open(helper_file, encoding="utf-8", errors="replace") as f:
            for line in f:
                try:
                    r = json.loads(line)
                except ValueError:
                    continue
                if r.get("type") != "user":
                    continue
                c = (r.get("message") or {}).get("content")
                if isinstance(c, list):
                    c = " ".join(x.get("text", "") for x in c if isinstance(x, dict))
                return c if isinstance(c, str) else ""
    except OSError:
        pass
    return ""


def items_of(prompt, known):
    """The helper's item(s): the ids written after `Item`/`claim`/`ticket`; only when there is none, every ledger id the
    brief names (a ruling cited in a brief is a ledger item too, so it must not outrank the item named as such)."""
    lead = [m for m in LEAD_RE.findall(prompt or "") if not known or m in known]
    rest = [] if lead else [m for m in ITEM_RE.findall(prompt or "") if m in known]
    out = []
    for m in lead + rest:
        if m not in out:
            out.append(m)
    return out[:3]


def window(seat, pid=None, tx=None):
    """-> (session_id, transcript path) of the calling window (or --tx for tests), or (None, why)."""
    import seat_restart as SR
    if tx:
        return os.path.basename(tx)[:-len(".jsonl")], tx
    import doorbell
    pid = pid or doorbell.claude_ancestor()
    sf = SR.session_file(pid) if pid else None
    if not (sf and sf.get("cwd") and sf.get("sessionId")):
        return None, "no session file for pid %s (run this from the window itself)" % pid
    return sf["sessionId"], SR.transcript_path(sf["cwd"], sf["sessionId"])


def live_helpers(tx_path, now, stale_s=None):
    import seat_restart as SR
    hs = SR.helpers_of(tx_path, now, stale_s)
    # a helper helpers_of retired only because the deadline passed is still running: here it counts as live
    return None if hs is None else [h for h in hs if h.get("alive") or h.get("retired") == LOST_WORD]


def agent_id(hid):
    return hid[len("agent-"):] if hid.startswith("agent-") else hid


def start(seat, tx_path, session_id, wait_s=DEFAULT_WAIT_S, now=None, root=None, known=None):
    """Record the checkpoint (deadline = now + wait_s) and return (record, text to print)."""
    now = now or time.time()
    live = live_helpers(tx_path, now)
    if live is None:
        return None, "CHECKPOINT UNMEASURED: helper inventory of %s unreadable; nothing recorded." % tx_path
    old = read_record(session_id, root)
    if old and now < float(old.get("deadline") or 0):     # one deadline per window: re-running never extends it
        rec = old
    else:
        known = known_items() if known is None else known
        base = tx_path[:-len(".jsonl")]
        hs = []
        for h in live:
            items = items_of(first_prompt(os.path.join(base, "subagents", h["id"] + ".jsonl")), known)
            hs.append({"id": h["id"], "agent_id": agent_id(h["id"]), "desc": h.get("desc") or "", "items": items})
        rec = {"seat": seat, "session_id": session_id, "tx_path": tx_path, "at": now, "deadline": now + wait_s,
               "order": ORDER, "helpers": hs, "lost": None}
        write_record(rec, root)
    lines = ["CHECKPOINT %s: %d live helper(s); deadline %s (%d s). Send each the order below with SendMessage "
             "(to = its agentId), then run `seat_restart.py checkpoint --seat %s --wait`."
             % (seat, len(rec["helpers"]), time.strftime("%H:%M:%SZ", time.gmtime(rec["deadline"])),
                rec["deadline"] - now, seat)]
    for h in rec["helpers"]:
        lines.append("- to=%s  (%s)  item: %s" % (h["agent_id"], h["desc"] or "-", ", ".join(h["items"]) or "UNKNOWN"))
    lines.append("ORDER: " + ORDER)
    if not rec["helpers"]:
        lines.append("No live helper: nothing to checkpoint. Publish your shard and request the restart.")
    return rec, "\n".join(lines)


def note_lost(seat, h, rec, runner=subprocess.run):
    """A `rimflow note` on each item of a lost helper, under the seat (the window publishes its shard next)."""
    done = []
    for it in h.get("items") or []:
        text = ("LOST at checkpoint: helper %s (%s) of the %s window was still running at the %s deadline and died with "
                "the restart. Its transcript is %s. NEXT: re-run this item from its last note and its committed work."
                % (h["agent_id"], h.get("desc") or "-", seat, time.strftime("%H:%M:%SZ", time.gmtime(rec["deadline"])),
                   os.path.join(rec["tx_path"][:-len(".jsonl")], "subagents", h["id"] + ".jsonl")))
        r = runner(["python3", os.path.join(REPO, "src", "RimMandrake", "rimflow", "cli.py"), "note", it, "--text", text,
                    "--seat", seat, "--why", "checkpoint deadline passed with the helper alive"],
                   capture_output=True, text=True, timeout=120, stdin=subprocess.DEVNULL)
        done.append((it, r.returncode))
    return done


def wait(seat, tx_path, session_id, cap_s=POLL_CAP_S, now_fn=time.time, sleep=time.sleep, root=None,
         runner=subprocess.run):
    """Poll until every checkpointed helper has stopped, or the deadline passes (-> LOST, notes written), or cap_s
    elapses (-> WAITING: run again). Returns (exit code, text)."""
    rec = read_record(session_id, root)
    if not rec:
        return 2, "No checkpoint recorded for this window: run `seat_restart.py checkpoint --seat %s` first." % seat
    t0 = now_fn()
    ids = {h["id"] for h in rec["helpers"]}
    while True:
        now = now_fn()
        live = live_helpers(tx_path, now)
        still = None if live is None else [h for h in rec["helpers"] if h["id"] in {x["id"] for x in live}]
        if still == []:
            return 0, "CHECKPOINT DONE: all %d helper(s) stopped. Publish your shard, then request the restart." % len(ids)
        if now >= rec["deadline"]:
            # live None: blind at the deadline. Every recorded helper not known to have stopped is lost: the restart
            # proceeds anyway (that is the bound), and over-reporting a loss costs one re-run, never work.
            lost = still if still is not None else rec["helpers"]
            if rec.get("lost") is None:
                rec["lost"] = [dict(h, notes=note_lost(seat, h, rec, runner)) for h in lost]
                rec["lost_at"] = now
                write_record(rec, root)
            names = "; ".join("%s (item %s)" % (h["agent_id"], ", ".join(h["items"]) or "UNKNOWN") for h in rec["lost"])
            return 1, ("CHECKPOINT DEADLINE: %d helper(s) LOST: %s. Each item got a note; the kill no longer waits on "
                       "them. Commit + ./publish your shard, then request the restart." % (len(rec["lost"]), names))
        if now - t0 >= cap_s:
            return 3, "CHECKPOINT WAITING: %d helper(s) still running, %d s to the deadline. Run --wait again." % (
                len(still or ids), rec["deadline"] - now)
        sleep(min(POLL_S, max(1, rec["deadline"] - now)))


def wake_lines(session_id, root=None):
    """For the fresh window's wake: the helpers the old window lost at its checkpoint."""
    rec = read_record(session_id, root) if session_id else None
    if not rec or not rec.get("lost"):
        return []
    return ["- LOST at checkpoint: %s (%s) item %s: re-run it from the item's last note"
            % (h["agent_id"], h.get("desc") or "-", ", ".join(h.get("items") or []) or "UNKNOWN") for h in rec["lost"]]


def main(argv=None, seat=None):
    ap = argparse.ArgumentParser(prog="seat_restart.py checkpoint", description=__doc__.split("\n\n")[0])
    ap.add_argument("--seat")
    ap.add_argument("--wait", action="store_true", help="poll (<=%d s per call) until done or the deadline" % POLL_CAP_S)
    ap.add_argument("--wait-s", type=int, default=DEFAULT_WAIT_S, help="the bounded wait (recorded once per window)")
    ap.add_argument("--cap-s", type=int, default=POLL_CAP_S)
    ap.add_argument("--pid", type=int)
    ap.add_argument("--tx", help="a transcript path (tests): the window whose helpers are checkpointed")
    a = ap.parse_args(argv)
    import doorbell
    seat = (a.seat or seat or doorbell.seat_name() or "").upper()
    if not seat:
        print("checkpoint: no seat (--seat or AGENT_SEAT)")
        return 2
    sid, tx = window(seat, a.pid, a.tx)
    if not sid:
        print("checkpoint: %s" % tx)
        return 2
    if a.wait:
        rc, text = wait(seat, tx, sid, cap_s=min(a.cap_s, POLL_CAP_S))
        print(text)
        return rc
    rec, text = start(seat, tx, sid, wait_s=a.wait_s)
    print(text)
    return 0 if rec else 2


if __name__ == "__main__":
    sys.exit(main())
