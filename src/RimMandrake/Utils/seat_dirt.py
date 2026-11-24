#!/usr/bin/env python3
"""seat_dirt.py — keep the Conductor's seat clone clean: land what is safe to land, alarm on the rest.

RIMMANDRAKE_ALARM_SEAT_CLONE_DIRT_OLDER_THAN_AN_HOUR (2026-11-16): the seat clone /home/mandrake/rm/bench held 150
dirty paths (92 conversation records, 14 items whose ledger `file` event was on origin but whose prose never landed,
5 Designer edits, 15 queue views, ...) and nothing noticed. Three classes are always safe to land and are landed here:

    conversations/*.md           written by ~/dev/Lodestar/bin/conversations.py, landed before only at a handoff
    infrastructure/state/items/<ID>.md, untracked, when origin's ledger has a `file` event for <ID> and origin has
                                 no such file: the item exists, its prose is simply missing from origin
    design/concepts/<Mod>/...    a concept folder whose stage.json names no open run and whose dirty files have not
                                 changed for CONCEPT_SETTLE_MIN: a finished Designer run whose harvest never landed
                                 its state (RIMMANDRAKE_LAND_DESIGNER_RUN_DONE_BUT_NEVER_HARVESTED: Cauldron's 12
                                 files sat here after a done run left the Dispatcher's tracking without role_done)

Everything else older than STALE_MIN is counted as `disk.seat_dirt` by ops_watch (alarm OPS_SEAT_CLONE_DIRT_RESTORE):
a writer is dirtying the seat clone instead of its own clone. A path outside the safe classes written in the last
STALE_MIN minutes is taken to be held by a live run and is never counted; a safe-class path lands once it has
settled (SETTLE_MIN, or CONCEPT_SETTLE_MIN for a concept folder).

Every role clone (ROLE_CLONE_ROOT/<name>, rimflow/role_clones.py: the Dispatcher's role runs and the art daemon work
there since RIMMANDRAKE_MOVE_SEAT_CLONE_WRITERS_INTO_OWN_POOL_CLONES) is read and tidied the same way (clones()).

A safe-class path that is still dirty TIDY_LATE_MIN after its last change is counted as dirt too: the tidy did not
land it (its unit is dead, or land.sh refused), and nothing else would say so.

The tidy fetches and lands, so it runs in its own unit (rm-seat-tidy.timer: `tidy --all --apply`), never inside
ops_watch's disk sense: there a land under the metronome's 15 s kill was killed on every beat and blinded every disk.*
reading (RIMMANDRAKE_UNBLIND_OPS_DISK_FAMILY_TWENTY_OVERRUNS_STRAIGHT, 11:02-16:20 PST 2026-11-22).

    seat_dirt.py report [--clone DIR]        one JSON reading
    seat_dirt.py tidy [--clone DIR] --apply  land the safe classes, then print the reading
    seat_dirt.py tidy --all --apply          the same for every clone (clones()); exit 1 when any clone's tidy failed
"""
import argparse
import contextlib
import io
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SEAT_CLONE = os.environ.get("RM_SEAT_CLONE", "/home/mandrake/rm/bench")
ROLE_CLONE_ROOT = os.environ.get("RM_ROLE_CLONE_ROOT", "/home/mandrake/rm/roles")     # = role_clones.ROOT
STALE_MIN = 60           # older than this and not landable -> dirt (the alarm)
SETTLE_MIN = 10          # a safe-class file is landed only once it has not changed for this long
# A settled safe-class path still dirty this long after its last change is dirt: the tidy left it. The tidy unit runs
# every 15 min (rm-seat-tidy.timer), so a live tidy has had several passes by then.
TIDY_LATE_MIN = STALE_MIN + 30
ITEMS = "infrastructure/state/items/"
LEDGER = "infrastructure/state/ledger/"
LAND = os.path.join(HERE, "land.sh")
ITEM_RE = re.compile(r"^infrastructure/state/items/([A-Z0-9_]+)\.md$")
CONCEPT_RE = re.compile(r"^design/concepts/([^/]+)/")
LEDGER_SHARD_RE = re.compile(r"^infrastructure/state/ledger/events/[A-Za-z0-9_.-]+\.jsonl$")
CONCEPT_SETTLE_MIN = 30  # a concept folder lands only this long after its last change, and only with no run open


def git(clone, *a, check=True, timeout=120):
    r = subprocess.run(["git", "-C", clone] + list(a), capture_output=True, text=True, timeout=timeout)
    if check and r.returncode != 0:
        raise RuntimeError("git %s: %s" % (" ".join(a[:2]), r.stderr.strip()))
    return r.stdout


def dirty(clone):
    """-> [(status, path)] for every modified, deleted or untracked path (ignored files never count)."""
    out = []
    recs = iter(git(clone, "status", "--porcelain=v1", "-z", "--untracked-files=all").split("\0"))
    for rec in recs:
        if len(rec) > 3:
            out.append((rec[:2], rec[3:]))
            if "R" in rec[:2] or "C" in rec[:2]:
                next(recs, None)    # a rename or copy carries its source path as the next record, not an entry
    return out


def age_min(clone, path, now):
    """Minutes since the path last changed; a deleted path takes its directory's time (when it was removed)."""
    p = os.path.join(clone, path)
    while not os.path.lexists(p) and p != clone:
        p = os.path.dirname(p)
    try:
        return (now - os.lstat(p).st_mtime) / 60.0
    except OSError:
        return float("inf")     # unmeasured age is never "fresh": it is counted (stale), not hidden


def filed_on_origin(clone, ids, ref="origin/main"):
    """-> the subset of ids that origin's ledger holds a `file` event for."""
    if not ids:
        return set()
    pats = []
    for i in sorted(ids):
        pats += ["-e", '"%s"' % i]        # the quoted id alone: a filing written with spaces matches; parsed below
    out = git(clone, "grep", "-h", "-F", *pats, ref, "--", LEDGER, check=False)
    found = set()
    for line in out.splitlines():
        try:
            e = json.loads(line)
        except ValueError:
            continue
        if isinstance(e, dict) and e.get("event") == "file" and isinstance(e.get("id"), str) and e["id"] in ids:
            found.add(e["id"])
    return found


def on_origin(clone, path, ref="origin/main"):
    return subprocess.run(["git", "-C", clone, "cat-file", "-e", "%s:%s" % (ref, path)],
                          capture_output=True, timeout=60).returncode == 0


def replaces_nothing_newer(clone, st, path, ref="origin/main"):
    """True when landing the clone's copy of path whole over origin's copy loses nothing that origin holds and the clone
    does not (RIMMANDRAKE_STOP_SEAT_DIRT_LANDING_STALE_COPY_OVER_NEWER_ORIGIN: a clone 42 commits behind landed its stale
    FlowWorks DISPATCH.jsonl over origin's newer one and deleted 4 ledger lines). True when origin has no such path;
    origin's copy is the clone's HEAD copy (the clone's edit is on the current base); origin's copy is a byte prefix of
    the clone's (an append-only file origin has not passed); or, for a conversation record (rewritten whole from its
    transcript), the clone's copy changed after origin's last commit of the path. Anything unreadable is False."""
    o = git(clone, "rev-parse", "-q", "--verify", "%s:%s" % (ref, path), check=False).strip()
    if not o:
        return True
    if st != "??" and git(clone, "rev-parse", "-q", "--verify", "HEAD:%s" % path, check=False).strip() == o:
        return True
    try:
        with open(os.path.join(clone, path), "rb") as f:
            mine = f.read()
        r = subprocess.run(["git", "-C", clone, "cat-file", "blob", o], capture_output=True, timeout=60)
        if r.returncode == 0 and mine.startswith(r.stdout):
            return True
        if path.startswith("conversations/"):
            ct = git(clone, "log", "-1", "--format=%ct", ref, "--", path, check=False).strip()
            return bool(ct) and os.stat(os.path.join(clone, path)).st_mtime > int(ct)
    except (OSError, ValueError):
        pass
    return False


def ledger_tail(clone, st, path):
    """-> the bytes a ledger events shard appended over the clone's HEAD copy, or None when the path is not a shard that
    only gained lines (RIMMANDRAKE_LAND_APPENDED_LEDGER_LINES_IN_TIDY_FIFTH_RING: a window's unlanded rimflow append rang
    disk.seat_dirt five times). None for a shard that lost or changed a byte, is untracked, deleted or unmerged, whose HEAD
    copy lacks a final newline, or whose new bytes are not whole lines. An unchanged shard gives b''."""
    if not LEDGER_SHARD_RE.match(path) or "?" in st or "D" in st or "U" in st:
        return None
    r = subprocess.run(["git", "-C", clone, "cat-file", "blob", "HEAD:" + path], capture_output=True, timeout=60)
    if r.returncode != 0:
        return None
    try:
        with open(os.path.join(clone, path), "rb") as f:
            mine = f.read()
    except OSError:
        return None
    head = r.stdout
    if not mine.startswith(head) or (head and not head.endswith(b"\n")):
        return None
    tail = mine[len(head):]
    return tail if (not tail or tail.endswith(b"\n")) else None


def closed_copy(clone, path, ref="origin/main"):
    """For an items/<ID>.md path: "same" when origin holds items/closed/<ID>.md with these exact bytes, "differs" when it
    holds that file with other bytes, None when origin has no closed prose for the item. A closed item's prose never
    lands in items/ (origin's check refuses the push, and the refusal sank the whole tidy on 2026-11-22)."""
    m = ITEM_RE.match(path)
    if not m:
        return None
    r = subprocess.run(["git", "-C", clone, "cat-file", "blob", "%s:%sclosed/%s.md" % (ref, ITEMS, m.group(1))],
                       capture_output=True, timeout=60)
    if r.returncode != 0:
        return None
    try:
        with open(os.path.join(clone, path), "rb") as f:
            return "same" if f.read() == r.stdout else "differs"
    except OSError:
        return "differs"


def clones(seat=None, role_root=None):
    """The seat clone, then every role clone on disk (<role_root>/<name> holding a .git), sorted."""
    seat = seat or SEAT_CLONE
    role_root = role_root or ROLE_CLONE_ROOT
    try:
        names = sorted(os.listdir(role_root))
    except FileNotFoundError:
        names = []
    return [seat] + [os.path.join(role_root, n) for n in names if os.path.isdir(os.path.join(role_root, n, ".git"))]


def classify(clone, now=None, settle_min=SETTLE_MIN):
    """-> {"landable": [paths], "fresh": [paths], "stale": [paths], "closed_copies": [paths]} over the clone's dirt.
    settle_min 0: the writer is known to have stopped (role_clones.land at the end of a role run's unit). A closed_copies
    path is an untracked items/<ID>.md that origin already holds byte for byte in items/closed/: nothing is at risk, and
    tidy removes it."""
    now = time.time() if now is None else now
    rows = [(st, p, age_min(clone, p, now)) for st, p in dirty(clone)]
    item_ids = {ITEM_RE.match(p).group(1) for st, p, _ in rows if st == "??" and ITEM_RE.match(p)}
    filed = filed_on_origin(clone, item_ids)
    settled = settled_concepts(clone, rows)
    # a settled concept lands whole or not at all: one path that would overwrite a newer origin copy holds the folder
    settled -= {CONCEPT_RE.match(p).group(1) for st, p, _ in rows
                if CONCEPT_RE.match(p) and CONCEPT_RE.match(p).group(1) in settled
                and not replaces_nothing_newer(clone, st, p)}
    out = {"landable": [], "fresh": [], "stale": [], "closed_copies": []}
    for st, p, age in rows:
        m = ITEM_RE.match(p)
        c = CONCEPT_RE.match(p)
        closed = closed_copy(clone, p) if st == "??" and m and m.group(1) in filed else None
        if closed == "same":
            out["closed_copies"].append(p)
            continue
        # a deletion (staged or not) or an unmerged path is never a safe class
        safe = (ledger_tail(clone, st, p) is not None) or \
               (p.startswith("conversations/") and p.endswith(".md") and "D" not in st and "U" not in st
                and replaces_nothing_newer(clone, st, p)) or \
               (st == "??" and m and m.group(1) in filed and closed is None and not on_origin(clone, p)) or \
               bool(c and c.group(1) in settled)
        if safe and (age >= settle_min or (c and c.group(1) in settled)):
            out["landable"].append(p)
        elif age < STALE_MIN:
            out["fresh"].append(p)
        else:
            out["stale"].append(p)
    return out


def settled_concepts(clone, rows):
    """-> the concept folders whose every dirty path is CONCEPT_SETTLE_MIN old and unstaged, and whose stage.json parses
    and names no open run (`running` empty). A concept with a run open, or a stage.json that is missing or does not parse, is
    never landed here: its files are a live run's, or nobody can tell."""
    newest, staged = {}, set()
    for st_, p, age in rows:
        c = CONCEPT_RE.match(p)
        if c:
            newest[c.group(1)] = min(age, newest.get(c.group(1), age))
            if st_[0] not in " ?":
                # anything staged is a hand edit under way: a run's close renames with os.replace and stages nothing,
                # and a staged rename's source never reaches the landing list (Codex review 2026-11-18)
                staged.add(c.group(1))
    out = set()
    for mod, age in newest.items():
        if age < CONCEPT_SETTLE_MIN or mod in staged:
            continue
        try:
            with open(os.path.join(clone, "design", "concepts", mod, "stage.json"), encoding="utf-8") as f:
                st = json.load(f)
        except (OSError, ValueError):
            continue
        if isinstance(st, dict) and not st.get("running"):
            out.add(mod)
    return out


def reading(clone=SEAT_CLONE, now=None):
    """Reads git status and file times only: no fetch, no land (ops_watch's disk sense calls it under a 15 s kill)."""
    now = time.time() if now is None else now
    c = classify(clone, now)
    late = [p for p in c["landable"] if age_min(clone, p, now) >= TIDY_LATE_MIN]
    stale = c["stale"] + late
    return {"clone": clone, "stale": len(stale), "landable": len(c["landable"]), "fresh": len(c["fresh"]),
            "stale_paths": stale[:12], "tidy_late": len(late)}


def tidy(clone=SEAT_CLONE, now=None, land=LAND, settle_min=SETTLE_MIN, fetch_timeout=120):
    """Land the safe classes: a ledger shard's appended lines with publish.land_ledger, the rest in one land.sh -m commit
    (a temp index from origin/main: the clone's index, HEAD and a peer's edits are never touched). -> "PUBLISHED <sha>" | "nothing to land" | "not landed: fetch past ..." | raises RuntimeError on a refusal."""
    if not dirty(clone):   # a clean clone has nothing to classify, so it costs no network
        return "nothing to land"
    try:   # classify against the origin land.sh will build on
        git(clone, "fetch", "-q", "origin", check=False, timeout=fetch_timeout)
    except subprocess.TimeoutExpired:
        return "not landed: fetch past %d s (the reading still counts the dirt)" % fetch_timeout
    c = classify(clone, now, settle_min)
    removed = []
    for p in c["closed_copies"]:       # origin holds these exact bytes in items/closed/: removing loses nothing
        try:
            os.remove(os.path.join(clone, p))
            removed.append(p)
        except OSError:
            pass
    said = "removed %d closed item copies; " % len(removed) if removed else ""
    paths = c["landable"]
    if not paths:
        return said + "nothing to land"
    where = "seat clone" if clone == SEAT_CLONE else "role clone " + os.path.basename(os.path.normpath(clone))
    msg = ("seat_dirt: land %d safe path(s) left in the %s (conversation records, appended ledger lines, filed item prose, "
           "settled concept folders)\n\n"
           "RIMMANDRAKE_ALARM_SEAT_CLONE_DIRT_OLDER_THAN_AN_HOUR (seat_dirt.py tidy)." % (len(paths), where))
    said_paths = []
    shards = [q for q in paths if LEDGER_SHARD_RE.match(q)]
    rest = [q for q in paths if q not in shards]
    if shards:
        # Lines, rebuilt on the newest origin at each try. A shard landed as a whole file dropped every line that origin
        # gained between this tidy's fetch and land.sh's own (RELAPSE_WORK_BELT_FIX_DIED_TWICE).
        if HERE not in sys.path:
            sys.path.insert(0, HERE)
        import publish
        with contextlib.redirect_stdout(io.StringIO()):
            sha = publish.land_ledger(clone, shards, msg + "\n")
        if not sha:
            raise RuntimeError("the ledger lines did not land (publish.land_ledger gave no sha): %s" % " ".join(shards))
        said_paths.append("PUBLISHED %s" % sha)
    if rest:
        p = subprocess.run(["sh", land, "-m", msg] + rest, cwd=clone, capture_output=True, text=True, timeout=600,
                           env=dict(os.environ, LAND_REPO=clone))
        if p.returncode == 0:
            said_paths.append((p.stdout.strip().splitlines() or ["PUBLISHED ?"])[-1])
        elif "nothing to land" not in p.stderr:
            raise RuntimeError("land.sh exited %d: %s" % (p.returncode, p.stderr.strip()))
    return said + ("; ".join(said_paths) or "nothing to land")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cmd", choices=("report", "tidy"))
    ap.add_argument("--clone", default=SEAT_CLONE)
    ap.add_argument("--all", action="store_true", help="tidy: every clone (clones()), one failure costs only its clone")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args(argv)
    if a.cmd == "tidy" and a.all:
        failed = 0
        for clone in clones():
            if not a.apply:
                print("%s: %s" % (clone, " ".join(classify(clone)["landable"]) or "nothing to land"))
                continue
            try:
                print("%s: %s" % (clone, tidy(clone)))
            except Exception as e:  # noqa: BLE001 - named, counted in the exit; the next clone still lands
                failed += 1
                print("%s: FAILED %s: %s" % (clone, type(e).__name__, str(e)[:400]))  # cut-ok: terminal display
        return 1 if failed else 0
    if a.cmd == "tidy":
        if a.apply:
            print(tidy(a.clone))
        else:
            print("\n".join(classify(a.clone)["landable"]) or "nothing to land")
    print(json.dumps(reading(a.clone)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
