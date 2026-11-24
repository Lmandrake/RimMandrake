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
  YOURS BY A WAIT (<k>):                                 not owed items: a dated wait that names the Conductor
    until|PASSED <date>  <ID>  <title>: <reason>
  WAITING (<w>):
    <age>  <ID>  <title>  until <date>: <reason>         under a running `rimflow wait`
  … <k> more: rimflow queue CONDUCTOR --owed --all        at most 40 lines in all

An item's age is from its `file`, never from a later event: nothing resets it. Closing its parent discharges nothing.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

try:                                                 # imported by cli.py as rimflow.owed: share its rebound model
    from . import model, priority
except ImportError:                                  # a hook or script: priority imports only as rimflow.priority
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from rimflow import model, priority

KIND = "owed"
NAMES_CONDUCTOR = re.compile(r"\bConductor\b", re.I)     # the launcher's wait line says "who acts next and on what"
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
    e = model.iso_epoch(created) if created else None
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


def named_waits(world, seat="BENCH", now=None):
    """-> [item], the soonest date first: the seat's open items that are not owed items and whose dated wait names the
    Conductor. Nothing else starts such an item: the List Pipeline reads a wait as Waiting, and no owed item exists. Pure."""
    seat = model.canonical(seat)
    return sorted((i for i in world.items.values()
                   if i.owner == seat and i.open and i.kind not in (KIND, "standing") and i.wait_until
                   and NAMES_CONDUCTOR.search(i.wait_reason or "")), key=lambda i: (str(i.wait_until), i.id))


def banner(world, seat="BENCH", now=None):
    """-> the view's first line: `OWED n (actionable a, waiting w), oldest <age> <ID>[ · k waits name you]`."""
    k = len(named_waits(world, seat, now))
    return _banner(world, seat, now) + ("" if not k else " · 1 wait names you" if k == 1 else " · %d waits name you" % k)


def _banner(world, seat, now):
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
    named = named_waits(world, seat, now)
    if named:
        body.append((None, "YOURS BY A WAIT (%d): a ticket whose dated wait names the Conductor; nothing else starts it" % len(named)))
        for i in named:
            e = model.iso_epoch(str(i.wait_until))
            body.append((i, "  %s%s  %s  %s: %s" % ("PASSED " if e is not None and e <= now else "until ", str(i.wait_until)[:10],
                                                   i.id, _title(i), i.wait_reason)))
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
    return safe_banner_and_ids(seat)[0]


def safe_banner_and_ids(seat="BENCH"):
    """-> (first line, the seat's open owed ids or None when the ledger could not be read), from one replay: the
    per-prompt hook needs both (the banner, and what tracks a promise in promise_scan)."""
    try:
        led = os.path.dirname(model.EVENTS)
        if not (os.path.exists(model.EVENTS) or os.path.isdir(os.path.join(led, model.SHARD_DIR))):
            # no ledger at all is could-not-look, never "OWED 0" (a hook run with CLAUDE_PROJECT_DIR elsewhere replayed
            # an empty world and said 0; found by RIMMANDRAKE_SLIM_OPERATIONS_START_PACKAGE_HALF_IS_UNRELATED)
            raise FileNotFoundError("no ledger at %s" % led)
        w = model.replay()
        act, wait = split(w, seat)
        return banner(w, seat), [i.id for i in act + wait]
    except Exception as e:                      # noqa: BLE001 - said, never silent
        return "OWED view did not run (%s: %s): run `rimflow queue CONDUCTOR --owed`" % (type(e).__name__, e), None


def safe_banner_and_items(seat="BENCH"):
    """-> (first line, {open owed id: (title, caused_by)} or None when the ledger could not be read): what
    promise_scan.covered reads, so a promise an open owed item already tracks is not said again."""
    try:
        led = os.path.dirname(model.EVENTS)
        if not (os.path.exists(model.EVENTS) or os.path.isdir(os.path.join(led, model.SHARD_DIR))):
            raise FileNotFoundError("no ledger at %s" % led)
        w = model.replay()
        act, wait = split(w, seat)
        return banner(w, seat), {i.id: (i.title or "", i.caused_by or "") for i in act + wait}
    except Exception as e:                      # noqa: BLE001 - said, never silent
        return "OWED view did not run (%s: %s): run `rimflow queue CONDUCTOR --owed`" % (type(e).__name__, e), None


WAKE_HEAD = "== what the Conductor OWES (rimflow queue CONDUCTOR --owed): act on these before anything else"


def wake_lines(repo, seat="CONDUCTOR", timeout=300):  # budget: class=rimflow
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
        print("%s:%d: %s\n    %s" % (path, n, why, lines[n - 1].strip()[:160]))  # cut-ok: terminal display
    n_ptr = len(pointer_bullets(text))
    print("check-pointers: %d pointer(s), %d refused" % (n_ptr, len(bad)) if bad or n_ptr else
          "check-pointers: no pointers in %s" % path)
    return 1 if bad else 0


if __name__ == "__main__":
    if sys.argv[1:2] == ["check-pointers"]:
        if len(sys.argv) != 3:
            print("usage: owed.py check-pointers <handoff.md>")
            sys.exit(2)
        sys.exit(check_pointers_main(sys.argv[2]))
    if sys.argv[1:] not in ([], ["--all"]):     # an unknown verb (the retired sync-sources too) never reads as a view
        print("owed.py: unknown command %r. Commands: owed.py [--all] | owed.py check-pointers <handoff.md>. The Dispatcher "
              "files no owed item (design/specs/2026-11-23-owed-sources-retired/boundary.md)" % " ".join(sys.argv[1:]))
        sys.exit(2)
    w = model.replay()
    print("\n".join(view(w, show_all="--all" in sys.argv)))
