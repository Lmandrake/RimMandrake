#!/usr/bin/env python3
"""The owed view: what the Conductor owes, first at every wake (RIMMANDRAKE_LIST_CONDUCTOR_OWES_FIRST_AT_EVERY_WAKE,
design/specs/2026-11-15-conductor-restart-loses-nothing.md §3 E1).

WHY. Every measured wake read `queue CONDUCTOR | tail -40` of a 23,872-line view, so it saw the newest four items and
nothing a dying window had filed before them; 8 of 9 lost or late debts had no item saying the Conductor owed the act.
An owed act is an ordinary item, `rimflow file <ID> --for BENCH --kind owed --title "<the act>"` (`--caused-by` the
item it acts on). This module only reads: `view()` is `rimflow queue CONDUCTOR --owed`, `banner()` its first line (the
per-prompt notice, .claude/hooks/conductor_goodbye.py), `evidence_ok()` the discharge rule `rimflow close` applies,
`check_pointers()` the handoff gate (`owed.py check-pointers <handoff.md>`, run by `handoff.py --check`).

  OWED <n> (actionable <a>, waiting <w>), oldest <age> <ID>
    <age>  [LATE]  <ID>  <title>  [for <caused_by>]       actionable, oldest first; LATE past 2 h
  WAITING (<w>):
    <age>  <ID>  <title>  until <date>: <reason>         under a running `rimflow wait`
  … <k> more: rimflow queue CONDUCTOR --owed --all        at most 40 lines in all

An item's age is from its `file`, never from a later event: nothing resets it. Closing its parent discharges nothing.
"""
import datetime
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))

try:                                                 # imported by cli.py as rimflow.owed: share its rebound model
    from . import model, priority, priority_list
except ImportError:                                  # a hook or script: priority imports only as rimflow.priority
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from rimflow import model, priority, priority_list

KIND = "owed"
LATE_S = 2 * 3600
MAX_LINES = 40
TITLE_MAX = 110
ALL_CMD = "rimflow queue CONDUCTOR --owed --all"

# A discharge names its evidence: a commit sha, a detached run id, a path, or when he was told.
EVIDENCE = (("a commit sha (7+ hex)", re.compile(r"(?<![0-9A-Za-z])[0-9a-f]{7,40}(?![0-9A-Za-z])")),
            ("a run id (rm-detached-…)", re.compile(r"\brm-detached-[\w.-]+")),
            ("a path (contains / or \\)", re.compile(r"[/\\]")),
            ("`told him at <time>`", re.compile(r"\btold him at \S", re.I)))
SHAPES = "; ".join(n for n, _ in EVIDENCE)


def is_owed(it):
    return getattr(it, "kind", None) == KIND


def evidence_ok(text):
    """-> True when a `--no-code` text holds one of the four evidence shapes."""
    return any(rx.search(text or "") for _, rx in EVIDENCE)


def refusal(iid, text):
    """The refusal record for an owed close without evidence: evidence, would_pass, smallest_fix."""
    return ("close refused: %s is an owed act, and closing one needs evidence that it was done.\n"
            "  evidence:     --no-code %r holds none of the four shapes: %s.\n"
            "  would_pass:   `close %s --sha <sha>` or `--no-code` text naming one of those, e.g. "
            "\"told him at 4:56 PM PST\" or \"launched rm-detached-<id>\".\n"
            "  smallest_fix: add the sha, run id, path or time you told him to the --no-code text. If the act was not "
            "done, it is still owed: leave it open, or `drop` it with why.\nNothing changed: the item is as it was."
            % (iid, text, SHAPES, iid))


def _age(created, now):
    e = priority_list.epoch(created) if created else None
    if e is None:
        return None, "age?"
    s = max(0, now - e)
    if s < 3600:
        return s, "%dm" % (s // 60)
    if s < 86400 * 2:
        return s, "%dh%02d" % (s // 3600, (s % 3600) // 60)
    return s, "%dd" % (s // 86400)


def _title(it):
    t = " ".join((it.title or "(no title)").split())
    return t if len(t) <= TITLE_MAX else t[:TITLE_MAX - 1] + "…"


def split(world, seat="BENCH", now=None):
    """-> (actionable, waiting): the seat's open owed items, each oldest first. Pure."""
    now = model.epoch_now() if now is None else now
    seat = model.canonical(seat)
    mine = sorted((i for i in world.items.values() if i.owner == seat and i.open and is_owed(i)),
                  key=lambda i: (i.created_at or "", i.id))
    waiting = [i for i in mine if priority.wait_running(i, now)]
    wids = {i.id for i in waiting}
    return [i for i in mine if i.id not in wids], waiting


def banner(world, seat="BENCH", now=None):
    """-> the view's first line: `OWED n (actionable a, waiting w), oldest <age> <ID>`."""
    now = model.epoch_now() if now is None else now
    act, wait = split(world, seat, now)
    n = len(act) + len(wait)
    if not n:
        return "OWED 0 (actionable 0, waiting 0)"
    old = min(act + wait, key=lambda i: (i.created_at or "", i.id))
    return "OWED %d (actionable %d, waiting %d), oldest %s %s" % (n, len(act), len(wait), _age(old.created_at, now)[1],
                                                                  old.id)


def view(world, seat="BENCH", now=None, show_all=False):
    """-> [line]: the owed view, at most MAX_LINES unless `show_all`. Pure."""
    now = model.epoch_now() if now is None else now
    act, wait = split(world, seat, now)
    body = []
    for i in act:
        s, age = _age(i.created_at, now)
        late = "LATE" if s is not None and s > LATE_S else "    "
        extra = ("  for %s" % i.caused_by if i.caused_by else "") + \
                ("  (blocked: %s)" % (i.blocked_reason or "unexplained") if i.blocked else "")
        body.append((i, "  %-6s %s  %s  %s%s" % (age, late, i.id, _title(i), extra)))
    if wait:
        body.append((None, "WAITING (%d):" % len(wait)))
        for i in wait:
            body.append((i, "  %-6s %s  %s  until %s: %s" % (_age(i.created_at, now)[1], i.id, _title(i),
                                                             (i.wait_until or "?")[:10], i.wait_reason or "?")))
    head = banner(world, seat, now)
    if show_all or 1 + len(body) <= MAX_LINES:
        return [head] + [ln for _, ln in body]
    keep = body[:MAX_LINES - 2]
    if keep and keep[-1][0] is None:            # never end on a bare WAITING header
        keep = keep[:-1]
    more = sum(1 for i, _ in body if i is not None) - sum(1 for i, _ in keep if i is not None)
    return [head] + [ln for _, ln in keep] + ["… %d more: %s" % (more, ALL_CMD)]


def safe_banner(seat="BENCH"):
    """-> the first line from the live ledger, or a `did not run` line: a per-prompt caller must never fail."""
    try:
        return banner(model.replay(), seat)
    except Exception as e:                      # noqa: BLE001 - said, never silent
        return "OWED view did not run (%s: %s): run `rimflow queue CONDUCTOR --owed`" % (type(e).__name__, e)


WAKE_HEAD = "== what the Conductor OWES (rimflow queue CONDUCTOR --owed): act on these before anything else"


def wake_lines(repo, seat="CONDUCTOR", timeout=120):
    """-> [line] for a wake (seat_restart.py wake, handoff.py --wake), printed right after the old window's last reply.
    Runs `cli.py queue <seat> --owed`; a view that cannot run says `did not run` and the wake goes on."""
    import subprocess
    cmd = [sys.executable, os.path.join(repo, "src", "RimMandrake", "rimflow", "cli.py"), "queue", seat, "--owed"]
    try:
        r = subprocess.run(cmd, cwd=repo, capture_output=True, text=True, timeout=timeout)
        out = (r.stdout or "").rstrip()
        if r.returncode or not out:
            raise RuntimeError("exit %d: %s" % (r.returncode, (r.stderr or "").strip()))
    except Exception as e:                      # noqa: BLE001 - said, never silent
        return ["", WAKE_HEAD, "OWED view did not run (%s: %s). Run `rimflow queue CONDUCTOR --owed` yourself and say "
                "so to him in one line." % (type(e).__name__, e)]
    return ["", WAKE_HEAD] + out.splitlines()


# A handoff pointer (RIMMANDRAKE_REFUSE_HANDOFF_POINTER_WITHOUT_OWED_ID, spec §3 E4): `- `ID`` or the template's
# `- ID -- state` / `- ID — state`, on a line holding `NEXT:` (handoff.pointer_ids reads the same two shapes).
POINTER = re.compile(r"^- (?:`[A-Z][A-Z0-9_]+`|[A-Z][A-Z0-9_]+ (?:--|\u2014|\u2013) )")
LIST_OR_HEAD = re.compile(r"^\s*(?:[-*+]\s|\d+[.)]\s|#|<!--)")    # a new bullet (any marker, any depth), heading or comment
CITED = re.compile(r"(?<![A-Za-z0-9_])[A-Z][A-Z0-9_]{2,}(?![A-Za-z0-9_])")


def pointer_bullets(text):
    """-> [(first line number, bullet text)] for each pointer, its continuation lines folded in: in the 17:27 Conductor
    handoff of 2026-11-18, 5 of 6 pointers wrapped their `NEXT:` onto a later line (handoff._bullets folds the same
    way). A blank line, a heading or a new bullet ends one."""
    out, cur = [], None
    for n, line in enumerate((text or "").splitlines(), 1):
        if cur is not None and line.strip() and not LIST_OR_HEAD.match(line):
            cur[1] += " " + line.strip()
            continue
        if cur is not None:
            out.append(tuple(cur))
            cur = None
        if POINTER.match(line):
            cur = [n, line]
    if cur is not None:
        out.append(tuple(cur))
    return [(n, b) for n, b in out if "NEXT:" in b]


def check_pointers(text, world):
    """-> [(line number, reason)] for each pointer that cites no open owed id, or cites a closed one. Pure: a validator
    that writes nothing. Any id in the pointer's bullet counts, its own included; a cited owed id that is no longer open
    refuses the pointer even beside an open one (the act it named is done: drop the pointer, or file the new act)."""
    bad = []
    for n, line in pointer_bullets(text):
        owed = [world.items[i] for i in dict.fromkeys(CITED.findall(line)) if i in world.items
                and is_owed(world.items[i])]
        closed = [i for i in owed if not i.open]
        if closed:
            bad.append((n, "; ".join("owed %s is closed (%s): drop the pointer, or file the new act and cite it"
                                     % (i.id, i.state) for i in closed)))
        elif not owed:
            bad.append((n, "no owed id: file the act (`rimflow file <ID> --for BENCH --kind owed --title \"<the act>\" "
                           "--caused-by <item>`), then cite it on this line (no act owed? write it as prose, not a `- `ID` … NEXT:` pointer)"))
    return bad


def check_pointers_main(path):
    """`owed.py check-pointers <handoff.md>`: 0 every pointer cites an open owed id (or there are none), 1 one or more
    do not (one line each), 2 could not look (the file or the ledger unreadable; nothing was judged)."""
    try:
        text = open(path, encoding="utf-8").read()
    except (OSError, UnicodeDecodeError) as e:
        print("check-pointers could not look: %s unreadable (%s)" % (path, e))
        return 2
    if os.environ.get("RIMFLOW_LEDGER"):        # a throwaway ledger, as cli._bind_paths reads it (shards beside it)
        model.EVENTS = os.environ["RIMFLOW_LEDGER"]
    try:
        world = model.replay()
    except Exception as e:                      # noqa: BLE001 - said, never silent
        print("check-pointers could not look: the ledger did not replay (%s: %s)" % (type(e).__name__, e))
        return 2
    bad = check_pointers(text, world)
    lines = text.splitlines()
    for n, why in bad:
        print("%s:%d: %s\n    %s" % (path, n, why, lines[n - 1].strip()[:160]))
    n_ptr = len(pointer_bullets(text))
    print("check-pointers: %d pointer(s), %d refused" % (n_ptr, len(bad)) if bad or n_ptr else
          "check-pointers: no pointers in %s" % path)
    return 1 if bad else 0


# ---- E3: the explicit Conductor hand steps become owed items at their source -----------------------------------------
# RIMMANDRAKE_FILE_OWED_WHERE_RUNS_PARK_FOR_THE_CONDUCTOR (spec §3 E3 as narrowed by §4). Measured why: "Gimme Some Slack
# is paused for the Conductor's call" reached the Conductor only as a run result, after the window that launched it was
# gone. Only the hand steps the programs already name are sources; a plain failed run is not one (noise, §4).
SOURCE_TAG = "owed-source"
SOURCE_RX = re.compile(r"\b%s ([a-z]+:[\w@.:+~-]*[\w.+~-])" % SOURCE_TAG)     # the key, never a trailing `]` or `:`


def _part(x):
    """A key part SOURCE_RX reads back whole, one-to-one: A-Z a-z 0-9 _ . + - kept, any other character `~XX` (its
    code point in hex), nothing `~none`. Two different values never share a key (Codex's second look, 2026-11-18)."""
    if x is None or x == "":
        return "~none"
    return "".join(c if re.match(r"[A-Za-z0-9_.+-]", c) else "~%02X" % ord(c) for c in str(x))


def _token(key):
    """-> a 5-letter word unique to the source (sha1, A-Z only): the name's last resort, so names never run out."""
    import hashlib
    h = int(hashlib.sha1(key.encode()).hexdigest(), 16)
    return "".join("ABCDEFGHIJKLMNOPQRSTUVWXYZ"[(h >> (5 * i)) % 26] for i in range(5))
DECIDES = "the Conductor decides"               # maturation.next_step: "PAUSED: three cycles, the Conductor decides"
CARD = "a card in the Conductor log"            # maturation.next_step: "OWNER, a card in the Conductor log"
# A program seat may not `file` (model: "`file` is a window's verb"); RUNNER spawns instead, from the run's item or, for a
# maturation row, from the Maturation Dispatch's own item (the cause maturation_dispatch.file_and_publish names).
MATURATION_PARENT = "RIMMANDRAKE_WIRE_DISPATCH_TO_LAUNCH_BUILDERS_MODS_SAT_IDLE"
PUBLISH_RESERVE_S = 15                           # a push (fetch, replay, lint, push) is not started with less left


def _cut(text, n=150):
    t = " ".join(str(text or "").split())
    return t if len(t) <= n else t[:n - 1] + "…"


def maturation_sources(rows):
    """-> [(key, name bases, title, caused_by)] for each status row whose NEXT names a Conductor hand step. Pure."""
    out = []
    for r in rows or []:
        nxt, mod = str(r.get("next") or ""), str(r.get("mod") or "")
        head = nxt.split("):", 1)[0]                # the NEXT's tag, never a later sentence quoting the words
        if not mod or (DECIDES not in head and CARD not in head):
            continue
        b = r.get("blind") if isinstance(r.get("blind"), dict) else {}
        visit = b.get("visit") or 0
        key = "maturation:%s@%s:%s:visit%s" % (_part(mod), _part(r.get("version")), _part(r.get("stage")),
                                                _part(visit))
        m, stage = mod.upper(), [w for w in re.split(r"[^A-Z0-9]+", str(r.get("stage") or "").upper()) if w]
        if DECIDES in head:
            bases = ["RIMMANDRAKE_DECIDE_%s_AFTER_THREE_BLIND_CYCLES" % m, "RIMMANDRAKE_DECIDE_%s_AFTER_THREE_CYCLES" % m,
                     "RIMMANDRAKE_DECIDE_%s_%s_AFTER_THREE_CYCLES" % (m, _token(key))]
            act = "Decide %s %s after three blind cycles" % (mod, r.get("version") or "")
        else:
            bases = ["_".join(["RIMMANDRAKE", "CARD", m] + stage + ["TO_THE_OWNER"]), "RIMMANDRAKE_CARD_%s_TO_HIM" % m,
                     "RIMMANDRAKE_CARD_%s_%s_TO_HIM" % (m, _token(key))]
            act = "Put the card to him for %s %s at %s" % (mod, r.get("version") or "", r.get("stage") or "?")
        out.append((key, bases, "%s: %s" % (act, _cut(nxt)), None))
    return out


def detached_sources(recs, items):
    """-> [(key, name bases, title, caused_by)] for each run record carrying `owed_close` whose item is still open on
    `items` (an item the ledger does not hold yet is not known open: a later pass files it). Pure."""
    out = []
    for rec in recs or []:
        unit, iid = rec.get("unit"), rec.get("item")
        it = items.get(iid) if iid else None
        if not unit or not rec.get("owed_close") or it is None or not it.open:
            continue
        words = [w for w in str(iid).split("_")[1:4] if w]
        bases = ["_".join(["RIMMANDRAKE", "SETTLE"] + words + ["LEFT_OPEN"]),
                 "_".join(["RIMMANDRAKE", "SETTLE"] + words[:2] + ["AFTER_ITS_RUN"])]
        key = "detached:%s" % _part(unit)
        bases.append("_".join(["RIMMANDRAKE", "SETTLE"] + words[:2] + [_token(key), "LEFT_OPEN"]))
        out.append((key, bases, "Close or carry %s: run %s ended with it open (%s)" % (
            iid, unit, _cut(rec.get("owed_close"), 110)), iid))
    return out


def _free_name(bases, known):
    """-> the first base (then base_AGAIN_<N as a word>) that `rimflow file` takes, or None (model.mint_problems)."""
    ones = "TWO THREE FOUR FIVE SIX SEVEN EIGHT NINE TEN ELEVEN TWELVE".split()
    for c in list(bases) + ["%s_AGAIN_%s" % (b, w) for b in bases for w in ones]:
        if not model.mint_problems(c, known):
            return c
    return None


def _lock_path():
    """One exclusive lock per ledger: two passes at once each re-read the ledger under it, so a key is filed once."""
    import hashlib
    import tempfile
    tag = hashlib.sha1(os.path.abspath(model.EVENTS).encode()).hexdigest()[:12]
    return os.path.join(tempfile.gettempdir(), "rimflow_owed_sources.%s.lock" % tag)


def filed_keys(events):
    """-> {source key}: every key already written into an owed filing, open or closed (never filed twice)."""
    keys = set()
    for ev in events:
        if ev.get("event") not in ("file", "spawn"):
            continue
        for v in ev.values():
            if isinstance(v, str) and SOURCE_TAG in v:
                keys.update(SOURCE_RX.findall(v))
    return keys


def sync_sources(rows, recs, seat="BENCH", repo=None, timeout=120, sources_err=None, spawn=False):
    """File one owed item for each new source. -> (filed [(id, key)], problems [str]). rows/recs None = that source
    could not be read (named in sources_err); the other source is still filed. spawn: write `spawn --from <cause>`
    (RUNNER, the Dispatcher tick), else `file`."""
    import fcntl
    import subprocess
    repo = repo or os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
    cli = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cli.py")
    filed, problems = [], list(sources_err or [])
    with open(_lock_path(), "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        evs = model.read()
        world = model.replay(evs)
        done = filed_keys(evs)
        known = set(world.items)
        for key, bases, title, cause in maturation_sources(rows) + detached_sources(recs, world.items):
            if key in done:
                continue
            iid = _free_name(bases, known)
            if iid is None:
                problems.append("%s: no free item name from %s" % (key, bases[0]))
                continue
            tagged = "%s [%s %s]" % (title, SOURCE_TAG, key)
            if spawn:
                argv = [sys.executable, cli, "spawn", "--from", cause or MATURATION_PARENT, "--for", seat, "--name", iid,
                        "--kind", KIND, "--title", tagged]
            else:
                argv = [sys.executable, cli, "file", iid, "--for", seat, "--kind", KIND, "--title", tagged]
                argv += ["--caused-by", cause] if cause else []
            argv += ["--why", "%s %s: an explicit Conductor hand step, filed where it parked (owed.py sync-sources)"
                     % (SOURCE_TAG, key)]
            try:
                r = subprocess.run(argv, cwd=repo, capture_output=True, text=True, timeout=timeout,
                                   stdin=subprocess.DEVNULL)
                ok, out = r.returncode == 0, (r.stdout + r.stderr).strip()
            except Exception as e:              # noqa: BLE001 - said, never silent
                ok, out = False, "%s: %s" % (type(e).__name__, e)
            if ok:
                filed.append((iid, key))
                known.add(iid)
                done.add(key)
            else:
                problems.append("%s: file %s refused: %s" % (key, iid, _cut(out, 300)))
    return filed, problems


def live_rows(root=None):
    """-> [next_step row] for every versioned mod not held by the owner (mod_owner_hold.json: nothing alarms on one)."""
    import maturation as M
    root = root or M.REPO
    return [M.next_step(root, m) for m in M.versioned(root)]


def held_names():
    """-> {MODNAME}: every owner-held mod, upper-cased as item ids spell it (mod_owner_hold.json)."""
    import mod_owner_hold as H
    return {re.sub(r"[^A-Z0-9]", "", str(k).upper()) for k in H.load()} - {""}


def not_held(rows, recs, names):
    """-> (rows, recs) without an owner-held mod: a row by its mod, a run by a word of its item id (the pipeline's names
    spell the mod as one word, RIMMANDRAKE_AUTOBUILD_GRAFFITI_…). Nothing alarms on a held mod."""
    rows = [r for r in rows if re.sub(r"[^A-Z0-9]", "", str(r.get("mod") or "").upper()) not in names]
    recs = [r for r in recs if not names & set(str(r.get("item") or "").split("_"))]
    return rows, recs


def live_records(d=None):
    """-> (records, [unreadable file]): a record mid-write is read on the next pass, but this pass says it missed it."""
    import detached_helper as DH
    d = d or DH.runs_dir()
    out, bad = [], []
    for n in sorted(os.listdir(d)):
        if n.endswith(".json") and not n.endswith(".out.json"):
            try:
                with open(os.path.join(d, n), encoding="utf-8") as f:
                    rec = json.load(f)
            except (OSError, ValueError) as e:
                bad.append("%s (%s)" % (n, type(e).__name__))
                continue
            if isinstance(rec, dict) and rec.get("unit"):
                out.append(rec)
            else:
                bad.append("%s (no unit)" % n)
    return out, bad


def sync_sources_main(argv):
    """`owed.py sync-sources [--maturation-json F] [--detached-dir D] [--for SEAT] [--publish]`: prints FILED <ID> <key>
    per new item. Exit 0 every source read and every filing taken (nothing new is 0 too), 1 a filing refused, 2 a source
    could not be read (the other is still filed). Run as RIMFLOW_SEAT=RUNNER (dispatcher.py's tick) it spawns, and
    --publish then lands the RUNNER shard (testq ingest.publish; the caller holds testq's ingest.lock)."""
    import argparse
    ap = argparse.ArgumentParser(prog="owed.py sync-sources")
    ap.add_argument("--maturation-json")
    ap.add_argument("--detached-dir")
    ap.add_argument("--for", dest="seat", default="BENCH")
    ap.add_argument("--publish", action="store_true")
    ap.add_argument("--deadline", type=float, help="epoch: past it minus PUBLISH_RESERVE_S the push is deferred")
    a = ap.parse_args(argv)
    if os.environ.get("RIMFLOW_LEDGER"):        # a throwaway ledger, as cli._bind_paths reads it
        model.EVENTS = os.environ["RIMFLOW_LEDGER"]
    if HERE not in sys.path:
        sys.path.insert(0, HERE)
    errs, rows, recs = [], None, None
    try:
        rows = json.load(open(a.maturation_json, encoding="utf-8")) if a.maturation_json else live_rows()
    except Exception as e:                      # noqa: BLE001 - said, never silent
        errs.append("could not look at the maturation rows (%s: %s)" % (type(e).__name__, e))
    try:
        recs, unread = live_records(a.detached_dir)
        if unread:
            errs.append("could not read %d detached record(s): %s" % (len(unread), ", ".join(unread[:5])))
    except Exception as e:                      # noqa: BLE001
        errs.append("could not look at the detached records (%s: %s)" % (type(e).__name__, e))
    try:
        names = held_names()
        kept_rows, kept_recs = not_held(rows or [], recs or [], names)
        rows, recs = (None if rows is None else kept_rows), (None if recs is None else kept_recs)   # unread stays unread
    except Exception as e:                      # noqa: BLE001 - a hold unread is never "nothing held"
        errs.append("could not read the owner holds (%s: %s): nothing filed" % (type(e).__name__, e))
        rows, recs = None, None
    runner = os.environ.get("RIMFLOW_SEAT") == "RUNNER"
    filed, problems = sync_sources(rows, recs, seat=a.seat, sources_err=errs, spawn=runner)
    for iid, key in filed:
        print("FILED %s %s" % (iid, key))
    if a.publish and runner:
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("owed_ingest", os.path.join(
                os.path.dirname(HERE), "Utils", "testq", "ingest.py"))
            ing = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(ing)
            if not (filed or ing.unpublished()):
                pass
            elif a.deadline is not None and time.time() + PUBLISH_RESERVE_S > a.deadline:
                # no room to push before the kill: the lines stay in the RUNNER shard, the next testq publish carries
                # them (ops_watch's own rule)
                print("publish: deferred: no time left in this beat; the next testq publish carries it")
            else:
                out = ing.publish(len(filed), message="ledger: owed sync-sources filed %d" % len(filed))
                print("publish: %s" % out)
                if not (out == "pushed" or str(out).endswith("; pushed")):
                    problems.append("publish did not push (%s); the RUNNER shard keeps the lines" % _cut(out, 200))
        except Exception as e:                  # noqa: BLE001 - the shard stays; the RUNNER ingest publishes it
            problems.append("publish failed (%s: %s); the RUNNER shard keeps the lines" % (type(e).__name__, e))
    elif a.publish:
        problems.append("--publish lands only the RUNNER shard; seat %s publishes its own" % (
            os.environ.get("RIMFLOW_SEAT") or "unset"))
    for p in problems:
        print("PROBLEM %s" % p)
    print("sync-sources: %d filed, %d problem(s); rows %s, records %s" % (
        len(filed), len(problems), "UNMEASURED" if rows is None else len(rows),
        "UNMEASURED" if recs is None else len(recs)))
    return 2 if errs else (1 if problems else 0)


if __name__ == "__main__":
    if sys.argv[1:2] == ["sync-sources"]:
        sys.exit(sync_sources_main(sys.argv[2:]))
    if sys.argv[1:2] == ["check-pointers"]:
        if len(sys.argv) != 3:
            print("usage: owed.py check-pointers <handoff.md>")
            sys.exit(2)
        sys.exit(check_pointers_main(sys.argv[2]))
    w = model.replay()
    print("\n".join(view(w, show_all="--all" in sys.argv)))
