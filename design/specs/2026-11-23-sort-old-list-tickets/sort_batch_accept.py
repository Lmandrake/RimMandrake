#!/usr/bin/env python3
"""sort_batch_accept.py: the reader's packet, the ledger writes and the outcome check of the old-ticket sort.

Item RIMMANDRAKE_SORT_OLD_TICKETS_BEFORE_SHAPE_971_WAIT_UNNAMED. Plan: plan.md beside this file. The name ends in
`_accept.py` so that list_dispatch.pick_model gives a batch item a Sonnet run.

    T=design/specs/2026-11-23-sort-old-list-tickets/sort_batch_accept.py      (run from the clone root)
    python3 $T packet BATCH [--ids ID...]   what a reader reads: one block for each ticket
    python3 $T validate BATCH               each row of results/<BATCH>.tsv is well formed; exit 1 lists each fault
    python3 $T apply BATCH                  write each row to the ledger (close, supersede, drop, name for Shape), then
                                            say which rows the ledger refused. It may run again: a row already done is
                                            skipped. It publishes nothing; it prints the ./publish command.
    python3 $T check BATCH                  the batch item's outcome check: exit 0 each ticket has a row and the ledger
                                            agrees with the row; exit 1 one does not; exit 2 could not look
    python3 $T sample BATCH                 the second reader's sample of the removed tickets (the same draw each time)
    python3 $T restore ID --why "..."       a wrong removal: file a successor with the ticket's title and prose, and
                                            name it for Shape (the ledger reopens no dropped ticket)
    python3 $T check_second NAME            a second-read item's outcome check (second_read_check.py calls it)
    python3 $T counts [BATCH...]            the class counts of the results files
    python3 $T selftest

results/<BATCH>.tsv, one line for each ticket, tab between fields:  ID  CLASS  EVIDENCE  TARGET
  CLASS is DONE | REPLACED | DEAD | NOT_WORTH | REAL_WORK. TARGET is a commit on origin/main (DONE; `cleared` for an
  OPS_ alarm ticket whose alarm is not open), the successor's item id (REPLACED), or `-`. A line that starts with `#`
  is a comment.
"""
import collections
import hashlib
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for _p in (os.path.join(REPO, "src", "RimMandrake", "rimflow"), os.path.join(REPO, "src", "RimMandrake", "Utils")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

CLASSES = ("DONE", "REPLACED", "DEAD", "NOT_WORTH", "REAL_WORK")
REMOVED = CLASSES[:4]
STATE_OF = {"DONE": ("done",), "REPLACED": ("superseded", "dropped"), "DEAD": ("dropped",), "NOT_WORTH": ("dropped",)}
CLOSED = ("done", "dropped", "superseded")
CLI = os.path.join("src", "RimMandrake", "rimflow", "cli.py")
# Verbs that move a ticket between queues or take it: his words on them are about the queue, not about the ticket.
ADMIN = ("reassign", "reclaim", "lease", "claim", "start", "live", "raise", "seat", "bridge")
# One text on more tickets than this is an order about the queue (measured 2026-11-23: "Please have those Frozen
# Relentless items shut down their work" is on 15 of the 936; his words about one mechanic are on 1 to 3).
MASS = 6
SHA_RX = re.compile(r"^[0-9a-f]{7,40}$")
ID_RX = re.compile(r"^[A-Z0-9]+(?:_[A-Z0-9]+)+$")
CLI_TIMEOUT_S = 600     # hang guard on one rimflow call (a ledger replay takes about 1 s)
# The second reader's sample of each batch: at least this many, and this share, of the removed tickets, with at least
# SAMPLE_CLASS of each class. The danger is a wrong class that drops true work and that nobody sees.
SAMPLE_MIN, SAMPLE_SHARE, SAMPLE_CLASS = 10, 0.25, 3


class Blind(Exception):
    """The tool could not look."""


# ---- inputs ---------------------------------------------------------------------------------------------------------

def batches(path=None):
    try:
        with open(path or os.path.join(HERE, "batches.json"), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError) as e:
        raise Blind("batches.json could not be read (%s)" % e)


def batch(name, d=None):
    b = (d or batches())["batches"].get(name)
    if b is None:
        raise Blind("batches.json has no batch %s" % name)
    return b


def ledger():
    """-> (world, {id: [events]})."""
    try:
        import model as M
        evs = M.read()
        world = M.replay(evs)
    except Exception as e:  # noqa: BLE001 - could not look is never a verdict
        raise Blind("the ledger could not be read (%s: %s)" % (type(e).__name__, e))
    by = collections.defaultdict(list)
    texts = collections.defaultdict(set)
    for e in evs:
        i = e.get("id") or (e.get("name") if e.get("event") == "spawn" else None)
        if not i:
            continue
        by[i].append(e)
        for k in ("ownerSaid", "byCard"):
            if e.get(k):
                texts[str(e[k])].add(i)
    by["__mass__"] = set(t for t, s in texts.items() if len(s) > MASS)
    return world, by


def owner_mark(iid, world, by):
    """-> why this ticket carries his words or waits on him, or None. (A program's floor; the reader reads the rest.)"""
    it = world.items[iid]
    if it.needs == "owner" or (it.blocked and it.blocked_kind == "owner"):
        return "it waits on the owner"
    for e in by.get(iid, ()):
        if e.get("event") in ADMIN:
            continue
        for k in ("ownerSaid", "byCard"):
            v = e.get(k)
            if v and str(v) not in by.get("__mass__", ()):
                return "%s on its %s event: %s" % (k, e.get("event"), clip(v, 160))
    return None


def clip(s, n):
    s = " ".join(str(s or "").split())
    return s if len(s) <= n else s[:n - 1] + "…"


def git(*args):
    try:
        r = subprocess.run(["git", "-C", REPO] + list(args), capture_output=True, text=True, errors="replace",
                           timeout=300, stdin=subprocess.DEVNULL)
    except (OSError, subprocess.TimeoutExpired) as e:
        raise Blind("git %s did not run: %s" % (args[0], e))
    return r


def commits_naming(ids):
    """-> {id: ["<sha10> <date> <subject>"]}: the commits on origin/main whose message names the id (no ledger commit)."""
    want, out = set(ids), collections.defaultdict(list)
    r = git("log", "origin/main", "--format=%h%x1f%ad%x1f%s%x1f%b%x1e", "--date=short", "--abbrev=10")
    if r.returncode:
        raise Blind("git log origin/main failed: %s" % clip(r.stderr, 200))
    for rec in r.stdout.split("\x1e"):
        f = rec.strip("\n").split("\x1f")
        if len(f) < 4 or re.match(r"(ledger|conversations|handoff|chore\(sync\))\b", f[2]):
            continue
        for tok in set(re.findall(r"[A-Z0-9]+(?:_[A-Z0-9]+)+", f[2] + " " + f[3])) & want:
            out[tok].append("%s %s %s" % (f[0], f[1], clip(f[2], 130)))
    return out


def tree():
    r = git("ls-tree", "-r", "-t", "--name-only", "origin/main")
    if r.returncode:
        raise Blind("git ls-tree origin/main failed: %s" % clip(r.stderr, 200))
    return set(r.stdout.splitlines())


def prose(iid):
    for d in ("items", os.path.join("items", "closed")):
        p = os.path.join(REPO, "infrastructure", "state", d, iid + ".md")
        if os.path.isfile(p):
            with open(p, encoding="utf-8", errors="replace") as f:
                return os.path.relpath(p, REPO), f.read()
    return None, ""


def alarm_state(iid):
    try:
        import ops_watch as OW
        with open(os.path.join(str(OW.ops_dir()), "alarms.json"), encoding="utf-8") as f:
            d = json.load(f)
    except Exception as e:  # noqa: BLE001 - could not look is not "clear"
        return "UNMEASURED (%s: %s)" % (type(e).__name__, e)
    st = sorted(set(str(v.get("state")) for v in d.values() if isinstance(v, dict) and v.get("item") == iid))
    return ", ".join(st) or "not in the file (no open alarm)"


# ---- the packet -----------------------------------------------------------------------------------------------------

def ticket_text(iid, world, by, commits, children, paths=None):
    """One ticket's block. `paths`: the set of paths on origin/main, or None (then no path line)."""
    it = world.items[iid]
    evs = by.get(iid, [])
    L = ["=== %s" % iid, "title: %s" % clip(it.title, 400),
         "kind %s | state %s | needs %s | filed %s | owner %s" % (it.kind, it.state, it.needs, str(it.created_at)[:10], it.owner)]
    mark = owner_mark(iid, world, by)
    if mark:
        L.append("OWNER MARK (class REAL_WORK): %s" % mark)
    if it.blocked:
        L.append("blocked: %s %s (%s)" % (it.blocked_kind or "", it.blocked_on or "", clip(it.blocked_reason, 200)))
    if it.outstanding:
        L.append("criteria outstanding (a close is refused while one stands): %s" % "; ".join(
            "%s %s" % (c.get("id"), clip(c.get("text"), 130)) for c in (it.criteria or []) if c.get("id") in it.outstanding)[:900])
    if it.live:
        L.append("live promise (rechecked by rm-deadman, %s): %s" % ("DEAD" if it.live_broken else "kept", clip(it.live, 160)))
    if iid.startswith("OPS_"):
        a = alarm_state(iid)
        L.append("alarm state now (ops_watch alarms.json): %s" % a)
    body = []
    for e in evs:
        if e.get("event") in ("file", "spawn"):
            for k in ("spec", "why", "ownerSaid"):
                if e.get(k):
                    body.append("%s: %s" % (k, clip(e[k], 700)))
    L += body
    path, text = prose(iid)
    if path:
        L.append("prose (%s, %d characters): %s" % (path, len(text), clip(text, 3000)))
    notes = [e for e in evs if e.get("event") in ("note", "implemented", "verify", "reconcile", "needs", "block", "wait",
                                                 "unblock", "retarget", "close")
             and not str(e.get("text") or "").startswith("DETACHED run")]
    keep = notes[-6:]
    if len(notes) > len(keep):
        L.append("(%d earlier notes and acts: python3 %s show %s)" % (len(notes) - len(keep), CLI, iid))
    for e in keep:
        said = e.get("text") or e.get("reason") or e.get("evidence") or e.get("why") or ""
        extra = " ".join("%s=%s" % (k, clip(e[k], 60)) for k in ("sha", "result", "to", "remaining") if e.get(k))
        L.append("%s %s%s: %s" % (str(e.get("ts"))[:10], e.get("event"), " " + extra if extra else "", clip(said, 450)))
    if commits.get(iid):
        L.append("commits on origin/main that name it: " + " | ".join(commits[iid][:5])
                 + (" | (%d more)" % (len(commits[iid]) - 5) if len(commits[iid]) > 5 else ""))
    if children.get(iid):
        L.append("filed from it: " + " | ".join("%s [%s]" % (c, world.items[c].state) for c in children[iid][:6]))
    if paths is not None:
        cited = sorted(set(p.rstrip(".") for p in re.findall(r"\b(?:src|design|infrastructure|skills)/[\w./-]+\w",
                                                             "%s %s %s" % (it.title, " ".join(body), text))))
        gone = [p for p in cited if p not in paths and p.rstrip("/") not in paths]
        if cited:
            L.append("cited paths: %d, not on origin/main: %s" % (len(cited), ", ".join(gone[:8]) or "none"))
    return "\n".join(L) + "\n"


def packet(name, only=None):
    ids = only or batch(name)["tickets"]
    world, by = ledger()
    com, paths = commits_naming(ids), tree()
    kids = collections.defaultdict(list)
    for i, x in world.items.items():
        if x.caused_by:
            kids[x.caused_by].append(i)
    out = []
    for i in ids:
        if i not in world.items:
            out.append("=== %s\nnever filed on this clone's ledger\n" % i)
        elif world.items[i].state in CLOSED:
            out.append("=== %s\nalready %s; write no row for it\n" % (i, world.items[i].state) if not only else
                       ticket_text(i, world, by, com, kids, paths))
        else:
            out.append(ticket_text(i, world, by, com, kids, paths))
    return "\n".join(out)


# ---- the rows -------------------------------------------------------------------------------------------------------

def rows_path(name):
    return os.path.join(HERE, "results", name + ".tsv")


def read_rows(name, path=None):
    """-> ([(id, class, evidence, target)], [faults]) or (None, why) when there is no file."""
    p = path or rows_path(name)
    if not os.path.isfile(p):
        return None, ["no results file %s" % os.path.relpath(p, REPO)]
    rows, bad, seen = [], [], set()
    with open(p, encoding="utf-8") as f:
        for n, ln in enumerate(f, 1):
            ln = ln.rstrip("\n")
            if not ln.strip() or ln.startswith("#"):
                continue
            f4 = [x.strip() for x in ln.split("\t")]
            if len(f4) == 3:
                f4.append("-")
            if len(f4) != 4:
                bad.append("line %d: %d fields, 4 wanted (ID, CLASS, EVIDENCE, TARGET, a tab between)" % (n, len(f4)))
                continue
            if f4[0] in seen:
                bad.append("line %d: %s has two rows" % (n, f4[0]))
                continue
            seen.add(f4[0])
            rows.append(tuple(f4))
    return rows, bad


def faults(rows, bad, b, items, sha_ok):
    """-> each fault of the rows against the batch, the ledger items {id: item} and sha_ok(sha)."""
    out = list(bad)
    have = {r[0] for r in rows}
    for i in b["tickets"]:
        if i not in have and not (i in items and items[i].state in CLOSED):
            out.append("%s has no row" % i)
    for i, c, ev, t in rows:
        if i not in b["tickets"]:
            out.append("%s is not a ticket of this batch" % i)
        if c not in CLASSES:
            out.append("%s: class %r is not one of %s" % (i, c, ", ".join(CLASSES)))
            continue
        if len(ev) < 12:
            out.append("%s: no evidence line" % i)
        if c in REMOVED and i in b.get("owner_words", ()):
            out.append("%s carries an OWNER MARK, so its class is REAL_WORK" % i)
        if c == "DONE" and t == "cleared" and i.startswith("OPS_"):
            continue
        if c == "DONE" and not (SHA_RX.match(t) and sha_ok(t)):
            out.append("%s: DONE needs TARGET to be a commit on origin/main; got %r" % (i, t))
        if c == "REPLACED" and (not ID_RX.match(t) or t == i or t not in items):
            out.append("%s: REPLACED needs TARGET to be the successor's item id; got %r" % (i, t))
    return out


def sha_on_main(sha):
    return git("merge-base", "--is-ancestor", sha, "origin/main").returncode == 0


def agrees(row, it):
    """-> None when the ledger agrees with the row, else what is missing."""
    i, c, _ev, _t = row
    if c == "REAL_WORK":
        if it.state in CLOSED:
            return None         # somebody closed it after the read; nothing waits on this sort
        import list_shape as LS
        f = LS.facts(it)
        if f["named"] or not LS.needs_shape_run(f):
            return None
        return "%s is REAL_WORK and is not named for Shape" % i
    if it.state in CLOSED:
        return None
    return "%s is %s and is still open (%s)" % (i, c, it.state)


def check(name, d=None, rows=None, items=None):
    """-> (code, lines)."""
    b = batch(name, d)
    bad = []
    if rows is None:
        rows, bad = read_rows(name)
    if rows is None:
        return 1, bad           # decided with no ledger read: most batches stand here on most beats
    if items is None:
        items = ledger()[0].items
    have = {r[0] for r in rows}
    for i in b["tickets"]:
        it = items.get(i)
        if it is None:
            raise Blind("%s has never been filed on this clone's ledger" % i)
        if i not in have and it.state not in CLOSED:
            bad.append("%s has no row" % i)
    for r in rows:
        if r[0] not in b["tickets"]:
            bad.append("%s is not a ticket of this batch" % r[0])
            continue
        if r[1] not in CLASSES:
            bad.append("%s: class %r" % (r[0], r[1]))
            continue
        w = agrees(r, items[r[0]])
        if w:
            bad.append(w)
    return (1 if bad else 0), bad


# ---- the writes -----------------------------------------------------------------------------------------------------

def command(row, name):
    i, c, ev, t = row
    why = "old-ticket sort (%s): %s: %s" % (name, c, ev)
    tail = ["--seat", "BENCH", "--why", why]
    if c == "DONE" and t == "cleared":
        return ["close", i, "--no-code", "the alarm is not open: %s" % ev, "--reason", why, "--live",
                "once: the alarm's own watch (ops_watch) reopens this fixed id when it rings"] + tail
    if c == "DONE":
        return ["close", i, "--sha", t, "--reason", why] + tail
    if c == "REPLACED":
        return ["supersede", i, "--by", t, "--reason", why] + tail
    if c == "DEAD":
        return ["drop", i, "--reason", "dead: %s" % ev] + tail
    if c == "NOT_WORTH":
        return ["drop", i, "--reason", "not worth the touch: %s" % ev] + tail
    return ["shape", i, "--enter"] + tail


def cli(args):
    env = dict(os.environ, RIMFLOW_SEAT="BENCH")
    r = subprocess.run([sys.executable, CLI] + args, cwd=REPO, env=env, capture_output=True, text=True, errors="replace",
                       timeout=CLI_TIMEOUT_S, stdin=subprocess.DEVNULL)
    return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()


def apply(name, run=cli):
    rows, bad = read_rows(name)
    if rows is None:
        print("\n".join(bad))
        return 1
    items = ledger()[0].items
    f = faults(rows, bad, batch(name), items, sha_on_main)
    if f:
        print("NOTHING WRITTEN, %d fault(s):\n%s" % (len(f), "\n".join(f)))
        return 1
    n, refused = 0, []
    for r in rows:
        if agrees(r, items[r[0]]) is None:
            continue
        rc, out = run(command(r, name))
        if rc:
            refused.append("%s (%s): %s" % (r[0], r[1], clip(out, 500)))
        else:
            n += 1
        print("%d of %d" % (n + len(refused), len(rows)), flush=True)
    print("%d row(s) written, %d refused, %d already so" % (n, len(refused), len(rows) - n - len(refused)))
    for x in refused:
        print("REFUSED %s" % x)
    r = git("status", "--porcelain", "-uall", "--", "infrastructure/state", os.path.relpath(HERE, REPO))
    paths = [ln[3:] for ln in r.stdout.splitlines() if ln[3:]]
    print("land it:\n./publish -m \"ledger: %s sorted\" %s" % (name, " ".join(paths)))
    return 1 if refused else 0


def restore(iid, why, run=cli):
    """A wrong removal: a successor with the same title and prose, named for Shape. -> (code, text)."""
    world, _by = ledger()
    it = world.items.get(iid)
    if it is None or it.state not in CLOSED:
        return 1, "%s is not closed; nothing to restore" % iid
    words = iid.split("_")
    while len("_".join(words)) > 44 or len(words) > 6:
        words.pop()
    if words[0] not in ("RIMMANDRAKE", "RIMMASTER"):
        words = ["RIMMANDRAKE"] + words
    new = "_".join(words) + "_RESTORED_AFTER_SORT"
    if new in world.items:
        return 1, "%s exists already (restored before, or the name is taken)" % new
    rc, out = run(["file", new, "--for", "BENCH", "--title", it.title, "--kind", it.kind or "task", "--caused-by", iid,
                   "--seat", "BENCH", "--why", "restored: the old-ticket sort removed %s wrongly: %s" % (iid, why)])
    if rc:
        return rc, out
    path, text = prose(iid)
    if path:
        with open(os.path.join(REPO, "infrastructure", "state", "items", new + ".md"), "w", encoding="utf-8") as f:
            f.write("Restored from `%s` (its whole record: `rimflow show %s`).\n\n%s" % (iid, iid, text))
    rc, out2 = run(["shape", new, "--enter", "--seat", "BENCH", "--why", "restored by the second reader: " + why])
    return rc, "%s restored as %s\n%s" % (iid, new, out2)


# ---- the second reader ----------------------------------------------------------------------------------------------

def sample(name, rows):
    """-> the sampled removed rows, the same draw each time: at least SAMPLE_MIN and SAMPLE_SHARE of the batch's removed
    tickets, with at least SAMPLE_CLASS of each class (all of them when there are fewer)."""
    gone = sorted((r for r in rows if r[1] in REMOVED),
                  key=lambda r: hashlib.sha256((name + r[0]).encode()).hexdigest())
    pick = []
    for c in REMOVED:
        pick += [r for r in gone if r[1] == c][:SAMPLE_CLASS]
    want = max(SAMPLE_MIN, int(len(gone) * SAMPLE_SHARE + 0.999))
    pick += [r for r in gone if r not in pick][:max(0, want - len(pick))]
    return pick


def check_second(name, d=None, rows_of=None, second_of=None, items=None):
    """second/<BATCH>.tsv rows: ID <tab> RIGHT|WRONG <tab> evidence. -> (code, lines)."""
    d = d or batches()
    sr = d.get("second_reads", {}).get(name)
    if sr is None:
        raise Blind("batches.json has no second read %s" % name)
    rows_of = rows_of or (lambda b: read_rows(b)[0])
    second_of = second_of or (lambda b: read_second(b))
    bad = []
    for b in sr:
        rows = rows_of(b)
        if rows is None:
            bad.append("%s is not sorted yet" % b)
            continue
        got = second_of(b)
        if got is None:
            bad.append("%s: no second/%s.tsv" % (b, b))
            continue
        pick = sample(b, rows)
        miss = [r[0] for r in pick if r[0] not in got]
        wrong = [r[0] for r in pick if got.get(r[0]) == "WRONG"]
        if pick and len(wrong) * 10 > len(pick):
            miss = [r[0] for r in rows if r[1] in REMOVED and r[0] not in got]
        if miss:
            bad.append("%s: not read yet: %s" % (b, ", ".join(miss)))
        allwrong = [i for i, v in got.items() if v == "WRONG"]
        if allwrong:
            if items is None:
                items = ledger()[0].items
            for i in allwrong:
                if not any(x.caused_by == i and x.id.endswith("_RESTORED_AFTER_SORT") for x in items.values()):
                    bad.append("%s is WRONG and is not restored" % i)
    return (1 if bad else 0), bad


def read_second(b):
    p = os.path.join(HERE, "second", b + ".tsv")
    if not os.path.isfile(p):
        return None
    out = {}
    with open(p, encoding="utf-8") as f:
        for ln in f:
            x = [y.strip() for y in ln.rstrip("\n").split("\t")]
            if len(x) >= 3 and x[1] in ("RIGHT", "WRONG") and len(x[2]) >= 12:
                out[x[0]] = x[1]
    return out


# ---- selftest -------------------------------------------------------------------------------------------------------

class _It:
    def __init__(self, i="A_B", state="ready", **k):
        self.id, self.state, self.needs, self.blocked, self.blocked_kind = i, state, "offline", False, None
        self.effect = self.shape = self.shape_named = self.created_at = self.caused_by = None
        self.__dict__.update(k)


def selftest():
    n = [0]

    def eq(got, want, what):
        n[0] += 1
        assert got == want, "%s: got %r, wanted %r" % (what, got, want)

    d = {"batches": {"B": {"tickets": ["A_A", "A_B", "A_C", "A_D"], "owner_words": ["A_B"]}}, "second_reads": {"S": ["B"]}}
    live = {i: _It(i) for i in d["batches"]["B"]["tickets"]}
    live["X_Y"] = _It("X_Y")
    rows = [("A_A", "DONE", "origin does it already", "abcdef1234"), ("A_B", "REAL_WORK", "still true work here", "-"),
            ("A_C", "REPLACED", "X_Y took the work over", "X_Y"), ("A_D", "NOT_WORTH", "nobody would ever notice", "-")]
    good = {"A_A": _It("A_A", "done"), "A_B": _It("A_B", shape_named="2026-11-24T01:00:00Z"),
            "A_C": _It("A_C", "superseded"), "A_D": _It("A_D", "dropped"), "X_Y": _It("X_Y")}
    F = lambda r, it=live: faults(r, [], d["batches"]["B"], it, lambda s: s == "abcdef1234")  # noqa: E731
    eq(F(rows), [], "good rows have no fault")
    eq(len(F(rows[1:])), 1, "a ticket with no row is a fault")
    eq(len(F([("A_A", "DONE", "origin does it already", "0000000000")] + rows[1:])), 1, "a commit not on main")
    eq(len(F([("A_A", "DONE", "origin does it already", "-")] + rows[1:])), 1, "DONE with no commit")
    eq(len(F(rows[:2] + [("A_C", "REPLACED", "took the work over", "NO_SUCH")] + rows[3:])), 1, "an unfiled successor")
    eq(len(F(rows[:2] + [("A_C", "REPLACED", "took the work over", "A_C")] + rows[3:])), 1, "its own successor")
    eq(len(F([rows[0], ("A_B", "DEAD", "the file is gone now", "-")] + rows[2:])), 1, "an OWNER MARK is not dropped")
    eq(len(F(rows[:3] + [("A_D", "NOT_WORTH", "", "-")])), 1, "no evidence")
    eq(len(F(rows[:3] + [("A_D", "MAYBE", "nobody would ever notice", "-")])), 1, "an unknown class")
    eq(len(F([("A_A", "DONE", "the alarm is clear now", "cleared")] + rows[1:])), 1, "cleared is for OPS_ tickets only")
    ops = {"tickets": ["OPS_A"], "owner_words": []}
    eq(faults([("OPS_A", "DONE", "the alarm is clear now", "cleared")], [], ops, {"OPS_A": _It("OPS_A")}, lambda s: False),
       [], "a cleared alarm")
    eq(len(F(rows + [("Z_Z", "DEAD", "the file is gone now", "-")])), 1, "a ticket of another batch")
    eq(F(rows[1:], dict(live, A_A=_It("A_A", "done"))), [], "a ticket closed before the read needs no row")
    eq(check("B", d, rows, good)[0], 0, "the ledger agrees with each row")
    eq(check("B", d, rows, dict(good, A_B=_It("A_B")))[0], 1, "REAL_WORK that nobody named")
    eq(check("B", d, rows, dict(good, A_B=_It("A_B", effect="cmd:x")))[0], 0, "REAL_WORK that has its check")
    eq(check("B", d, rows, dict(good, A_D=_It("A_D")))[0], 1, "a drop the ledger does not hold")
    eq(check("B", d, rows[:3], dict(good, A_D=_It("A_D")))[0], 1, "an open ticket with no row")
    try:
        check("B", d, rows, {"A_A": _It("A_A")})
        raise AssertionError("an unfiled ticket must be could-not-look")
    except Blind:
        n[0] += 1
    eq(read_rows("B", os.path.join(HERE, "no-such.tsv"))[0], None, "no results file")
    by = {"A_A": [{"event": "reassign", "ownerSaid": "move it"}], "A_B": [{"event": "file", "ownerSaid": "build it"}],
          "A_C": [{"event": "note", "byCard": "mass"}], "__mass__": {"mass"}}
    w = type("W", (), {"items": dict(live, A_D=_It("A_D", needs="owner"))})()
    eq([bool(owner_mark(i, w, by)) for i in ("A_A", "A_B", "A_C", "A_D")], [False, True, False, True], "owner marks")
    many = [("T_%d" % k, "DEAD", "the file is gone", "-") for k in range(60)] + [("U_%d" % k, "DONE", "done at sha", "a") for k in range(4)]
    s = sample("B", many)
    eq(len(s), 16, "a quarter of 64 removed tickets")
    eq(sum(r[1] == "DONE" for r in s) >= 3, True, "three of each class")
    eq(sample("B", many) == s and sample("B", many[:4]) != [], True, "the same draw each time")
    eq(len(sample("B", many[:4])), 4, "all of a small batch")
    S = lambda got, it=None: check_second("S", d, lambda b: rows, lambda b: got, it or good)[0]  # noqa: E731
    eq(S({"A_A": "RIGHT", "A_C": "RIGHT", "A_D": "RIGHT"}), 0, "the sample is read and right")
    eq(S({"A_A": "RIGHT", "A_C": "RIGHT"}), 1, "one of the sample is not read")
    eq(S({"A_A": "RIGHT", "A_C": "RIGHT", "A_D": "WRONG"}), 1, "a wrong drop is not restored")
    eq(S({"A_A": "RIGHT", "A_C": "RIGHT", "A_D": "WRONG"},
         dict(good, N=_It("RIMMANDRAKE_A_D_RESTORED_AFTER_SORT", caused_by="A_D"))), 0, "a wrong drop is restored")
    m2 = {"batches": d["batches"], "second_reads": {"S": ["B"]}}
    two = {r[0]: "RIGHT" for r in sample("B", many)}
    for i in list(two)[:2]:
        two[i] = "WRONG"
    back = {"N%d" % k: _It("R_RESTORED_AFTER_SORT", caused_by=i) for k, i in enumerate(list(two)[:2])}
    eq(check_second("S", m2, lambda b: many, lambda b: two, back)[0], 1, "2 of 16 wrong: all of the batch must be read")
    full = {r[0]: two.get(r[0], "RIGHT") for r in many}
    eq(check_second("S", m2, lambda b: many, lambda b: full, back)[0], 0, "all read")
    print("selftest: %d cases pass" % n[0])
    return 0


def counts(names):
    d = batches()
    tot = collections.Counter()
    for b in names or d["batches"]:
        rows, _bad = read_rows(b)
        if rows is None:
            print("%-62s not sorted" % b)
            continue
        c = collections.Counter(r[1] for r in rows)
        tot.update(c)
        print("%-62s %s" % (b, " ".join("%s %d" % (k, c[k]) for k in CLASSES)))
    print("all: %s" % " ".join("%s %d" % (k, tot[k]) for k in CLASSES))
    return 0


def report(code, lines, name):
    for ln in lines:
        print(ln)
    print("%s: %s" % ({0: "HOLDS", 1: "FAILS"}[code], name))
    return code


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    cmd, rest = argv[0], argv[1:]
    try:
        if cmd == "selftest":
            return selftest()
        if cmd == "counts":
            return counts(rest)
        if cmd == "packet":
            print(packet(rest[0], rest[rest.index("--ids") + 1:] if "--ids" in rest else None))
            return 0
        if cmd == "validate":
            rows, bad = read_rows(rest[0])
            f = bad if rows is None else faults(rows, bad, batch(rest[0]), ledger()[0].items, sha_on_main)
            print("\n".join(f) or "each row is well formed")
            return 1 if f else 0
        if cmd == "apply":
            return apply(rest[0])
        if cmd == "check":
            return report(*check(rest[0]), name=rest[0])
        if cmd == "check_second":
            return report(*check_second(rest[0]), name=rest[0])
        if cmd == "sample":
            rows, _bad = read_rows(rest[0])
            if rows is None:
                raise Blind("%s is not sorted yet" % rest[0])
            for r in sample(rest[0], rows):
                print("\t".join(r))
            return 0
        if cmd == "restore":
            rc, out = restore(rest[0], rest[rest.index("--why") + 1])
            print(out)
            return rc
    except Blind as e:
        print("UNMEASURED: %s" % e)
        return 2
    except (IndexError, ValueError) as e:
        print("bad arguments (%s)\n%s" % (e, __doc__))
        return 2
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
