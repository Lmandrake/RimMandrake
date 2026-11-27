#!/usr/bin/env python3
"""check_once.py: run the outcome checks of one beat once, in parallel under a bound, and keep each result until a file
that the check read has changed. Both ticket-lane timers (rm-list-effect and rm-list-dispatch) share the kept results.

Item RIMMANDRAKE_RUN_LANE_CHECKS_ONCE_193_OF_218_SECONDS (rows 2, 7 and 8 of design/specs/2026-11-26-slow-actions/
one_page.md: one lane tick 218 s, 193 s of it 48 checks one after the other, the same checks again by the second timer).
Page: design/specs/2026-11-27-check-once/boundary.md; selftest: selftest_check_once.py.

How a check's reads are named. A `cmd:` check is named only when its command is a chain of simple clauses joined by
`&&`, each `test [!] -f|-s|-d|-e|-x|-r <path>` or `python3 <script or -c or -m> <args>`, with no expansion, pipe,
redirection or assignment. Each python process then runs with check_reads_hook/sitecustomize.py, which records every
path it opens, lists or stats, the python children it starts, and each reason its reads cannot be named (another
program, a socket, /proc). A check whose reads cannot be named runs every time. A path check (`path-has`,
`path-lacks`) reads one file and runs every time: it is cheap.

A kept result is used again only when the check text and root are the same, every read file has the stat that it had
when the check first read it, and the result is younger than KEEP_S. Only holds and fails are kept; an unmeasured
result is never kept and never becomes holds or fails.

`python3 src/RimMandrake/rimflow/list_shape.py holds <ID>` is answered in this process when the caller passes its
ledger world: the same function (list_shape.holds_text) on the world the beat already read, and its parts' checks go
through the same batch, so the ledger is not read again once per such check (30 of 81 checks, about 5 s each).
"""
import concurrent.futures as cf
import fcntl
import hashlib
import json
import os
import shlex
import shutil
import stat
import sys
import tempfile
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for _p in (HERE, os.path.join(REPO, "src", "RimMandrake", "Utils")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

ITEM = "RIMMANDRAKE_RUN_LANE_CHECKS_ONCE_193_OF_218_SECONDS"
HOOK = os.path.join(HERE, "check_reads_hook")
# Bound on checks run at the same time. danger: the beat runs on a machine at load 22 to 52 on 14 cores (slow-actions
# page, 2026-11-26), and each check is a python process (a list_shape check replays the whole ledger, about 0.5 GB);
# 81 at once would add 81 runnable processes and their memory to that load. 4 took 166 s for 81 checks (2026-11-27).
WORKERS = 4
# Refresh of a kept result (it ends no work: the check runs again). danger: a verdict that turns on the clock alone,
# which no recorded read shows (time.time and datetime.now leave no audit event): such a check would be kept for ever.
# None is known today; one hour still cuts the 12 runs an hour of the two timers to one.
KEEP_S = 3600
SHAPE_CMD = ["python3", "src/RimMandrake/rimflow/list_shape.py", "holds"]
TEST_FLAGS = "fsdexr"
PY_NAMES = ("python3", "python")


_STATS_LOCK = threading.Lock()


def _count(stats, k, text=None, why=None):
    with _STATS_LOCK:
        stats[k] = stats.get(k, 0) + 1
        if why:             # which checks run every time, and why: the reading shows what to name next
            stats.setdefault("unnamed_why", {})[" ".join(str(text).split())[:160]] = why  # cut-ok: a reading's label


def _le():
    import list_effect
    return list_effect


# ---- naming a check's reads -----------------------------------------------------------------------------------------

def split_chain(cmd):
    """-> (clause strings split at each unquoted `&&`, None) or (None, why) when bash would expand, redirect, pipe or
    group anything: a `$` or backtick outside single quotes, or an unquoted glob, brace, tilde, `;`, `|`, `<`, `>`, `(`,
    `)`, `#`, a lone `&` or a newline."""
    out, cur, i, q = [], [], 0, None
    while i < len(cmd):
        ch = cmd[i]
        if q == "'":
            q = None if ch == "'" else q
        elif q == '"':
            if ch in "$`":
                return None, "an expansion inside double quotes (%s)" % ch
            if ch == "\\" and i + 1 < len(cmd):
                cur.append(ch)
                i += 1
                ch = cmd[i]
            elif ch == '"':
                q = None
        elif ch in "'\"":
            q = ch
        elif ch == "\\":
            if i + 1 >= len(cmd) or cmd[i + 1] == "\n":
                return None, "a line continuation"
            cur.append(ch)
            i += 1
            ch = cmd[i]
        elif cmd.startswith("&&", i):
            out.append("".join(cur))
            cur, i = [], i + 2
            continue
        elif ch in "$`*?[]{}~;|&<>()#\n":
            return None, "a shell operator or expansion (%s)" % ch
        cur.append(ch)
        i += 1
    if q:
        return None, "an unclosed quote"
    out.append("".join(cur))
    return out, None


def plan(cmd):
    """-> (clauses, None) or (None, why). A clause is ("test", tokens, negate, flag, path) or ("python", tokens)."""
    parts, why = split_chain(cmd)
    if parts is None:
        return None, why
    clauses = []
    for part in parts:
        try:
            c = shlex.split(part)
        except ValueError as e:
            return None, "the command does not parse (%s)" % e
        if not c:
            return None, "an empty clause"
        if "=" in c[0]:
            return None, "an assignment (%s)" % c[0][:40]
        clauses.append(c)
    out = []
    for c in clauses:
        if c[0] == "test":
            a = c[1:]
            neg = bool(a) and a[0] == "!"
            a = a[1:] if neg else a
            if len(a) != 2 or len(a[0]) != 2 or a[0][0] != "-" or a[0][1] not in TEST_FLAGS:
                return None, "a test clause of another form (%s)" % " ".join(c)[:60]
            out.append(("test", c, neg, a[0][1], a[1]))
        elif c[0] in PY_NAMES and len(c) >= 2 and (not c[1].startswith("-") or (c[1] in ("-c", "-m") and len(c) >= 3)):
            out.append(("python", c))
        else:
            return None, "a program whose reads are not recorded (%s)" % c[0][:40]
    return out, None


def rewrite(clauses):
    """-> the same command, each python clause marked with its index (an env assignment: no other change)."""
    parts = []
    for i, c in enumerate(clauses):
        parts.append(("RM_CHECK_CLAUSE=%d " % i if c[0] == "python" else "") + shlex.join(c[1]))
    return " && ".join(parts)


def sig(p):
    """-> a path as kept: a file's [mtime_ns, size, inode, mode]; a folder's ["dir", sha1 of its sorted names] (what a
    listing shows: an atomic replace inside it changes the folder's time, not its names); ["missing"]; ["error", errno].
    check_reads_hook/sitecustomize.py computes the same (selftest t_the_hook_and_the_beat_key_a_path_alike)."""
    try:
        s = os.stat(p)
        if stat.S_ISDIR(s.st_mode):
            return ["dir", hashlib.sha1("\0".join(sorted(os.listdir(p))).encode("utf-8", "surrogateescape")).hexdigest()]
        return [s.st_mtime_ns, s.st_size, s.st_ino, s.st_mode]
    except (FileNotFoundError, NotADirectoryError):
        return ["missing"]
    except OSError as e:
        return ["error", e.errno]


def test_now(c, root):
    """-> True when a test clause holds now (the same answer bash's test gives on a file of this machine)."""
    _, _, neg, flag, path = c
    p = os.path.join(root, path)
    if flag == "f":
        v = os.path.isfile(p)
    elif flag == "d":
        v = os.path.isdir(p)
    elif flag == "e":
        v = os.path.exists(p)
    elif flag == "s":
        v = os.path.exists(p) and os.stat(p).st_size > 0
    elif flag == "x":
        v = os.access(p, os.X_OK)
    else:
        v = os.access(p, os.R_OK)
    return v != neg


def collect(recdir, clauses, verdict, root, pre):
    """-> (reads, None) when every read of the run is named, else (None, why). pre: the test clauses' reads."""
    try:
        names = os.listdir(recdir)
    except OSError as e:
        return None, "the read records could not be listed (%s)" % e
    starts = set(int(n.split(".")[0]) for n in names if n.endswith(".start"))
    recs = {}
    for n in names:
        if n.endswith(".json"):
            try:
                with open(os.path.join(recdir, n), encoding="utf-8") as f:
                    r = json.load(f)
                recs[int(r["pid"])] = r
            except (OSError, ValueError, KeyError, TypeError):
                return None, "a read record could not be read (%s)" % n
    if starts - set(recs):
        return None, "a python process ended without its read record (os._exit, a signal or a deadline)"
    for r in recs.values():
        if r.get("why"):
            return None, "a python process %s" % r["why"][0]
        kids = sum(1 for k in recs.values() if k.get("ppid") == r["pid"])
        if kids < int(r.get("kids") or 0):
            return None, "a python child did not record its reads"
    ran = set()
    for r in recs.values():
        if r.get("ppid") not in recs:
            try:
                ran.add(int(r.get("clause")))
            except (TypeError, ValueError):
                return None, "a python process outside the check's clauses"
    stopped = False         # a clause before this one could have ended the chain
    for i, c in enumerate(clauses):
        if c[0] == "test":
            stopped = stopped or not test_now(c, root)
            continue
        if i in ran:
            stopped = True  # it ran; its exit may end the chain
            continue
        if verdict == "holds" or not stopped:
            return None, "python clause %d left no record" % i
    reads = dict(pre)
    for r in recs.values():
        for p, s in (r.get("reads") or {}).items():
            reads.setdefault(p, s)
    return reads, None


# ---- the kept results -----------------------------------------------------------------------------------------------

def store_dir(create=True):
    d = os.path.join(_le().sdir(create=create), "check_kept")
    if create:
        os.makedirs(d, exist_ok=True)
    return d


def _key(text, root):
    return hashlib.sha1(("%s\0%s" % (root, text)).encode("utf-8", "replace")).hexdigest()


def kept(store, text, root, now):
    """-> the kept entry when it may be used now, else None."""
    try:
        with open(os.path.join(store, _key(text, root) + ".json"), encoding="utf-8") as f:
            e = json.load(f)
    except (OSError, ValueError):
        return None
    if e.get("text") != text or e.get("root") != root or e.get("verdict") not in ("holds", "fails"):
        return None
    if not (0 <= now - float(e.get("at") or 0) < KEEP_S):
        return None
    for p, s in (e.get("reads") or {}).items():
        if sig(p) != s:
            return None
    return e


def keep(store, text, root, now, verdict, out, reads):
    p = os.path.join(store, _key(text, root) + ".json")
    with open(p + ".tmp", "w", encoding="utf-8") as f:
        json.dump({"text": text, "root": root, "at": now, "verdict": verdict, "out": out, "reads": reads}, f)
    os.replace(p + ".tmp", p)


class _Lock:
    """One check at a time across both timers: the second waits, then finds the first's result kept."""

    def __init__(self, store, text, root):
        self.f = None
        if store:
            try:
                self.f = open(os.path.join(store, _key(text, root) + ".lock"), "w")
                fcntl.flock(self.f, fcntl.LOCK_EX)
            except OSError:
                self.f = None

    def __enter__(self):
        return self

    def __exit__(self, *a):
        if self.f:
            self.f.close()


def run_one(text, root, store=None, write=True, now=None, stats=None):
    """-> (verdict, output), the same answer list_effect.run gives. Never raises. stats (dict) counts what happened."""
    LE = _le()
    stats = stats if stats is not None else {}
    p = LE.parse(text)
    if p["kind"] != "cmd":
        _count(stats, "path")
        return LE.run(text, root)
    clauses, why = plan(p["cmd"])
    if clauses is None:
        _count(stats, "unnamed", text, why)
        return LE.run(text, root)
    now = time.time() if now is None else now
    with _Lock(store, text, root):
        if store:
            e = kept(store, text, root, time.time())
            if e:
                _count(stats, "kept")
                return e["verdict"], e.get("out") or ""
        pre = {os.path.normpath(os.path.join(root, c[4])): sig(os.path.join(root, c[4]))
               for c in clauses if c[0] == "test"}
        recdir = tempfile.mkdtemp(prefix="rm-check-reads-")
        try:
            pp = os.environ.get("PYTHONPATH")
            env = {"RM_CHECK_READS": recdir, "PYTHONPATH": HOOK + (os.pathsep + pp if pp else "")}
            verdict, out = LE.run("cmd:" + rewrite(clauses), root, env_extra=env)
            reads, why = collect(recdir, clauses, verdict, root, pre)
        finally:
            shutil.rmtree(recdir, ignore_errors=True)
        _count(stats, "ran")
        if reads is None:
            _count(stats, "unnamed", text, why)
        elif store and write and verdict in ("holds", "fails"):
            try:
                keep(store, text, root, now, verdict, out, reads)
            except OSError:
                _count(stats, "keep_failed")
        return verdict, out


def shape_id(text):
    """-> the item id when the check is exactly `cmd:python3 src/RimMandrake/rimflow/list_shape.py holds <ID>`."""
    LE = _le()
    p = LE.parse(text)
    if p["kind"] != "cmd":
        return None
    try:
        t = shlex.split(p["cmd"])
    except ValueError:
        return None
    return t[3] if len(t) == 4 and t[:3] == SHAPE_CMD else None


def run_many(texts, root, world=None, write=True, workers=WORKERS, store=None):
    """-> ({text: (verdict, output)}, stats). Each distinct check runs at most once, `workers` at a time, and a kept
    result is used where its reads are unchanged. write=False (a dry beat) keeps nothing new."""
    t0 = time.time()
    stats = {}
    if store is None:
        try:
            store = store_dir(create=write)
            if not os.path.isdir(store):
                store = None
        except OSError:
            store = None
    texts = list(dict.fromkeys(t for t in texts if t))
    shaped = {}
    if world is not None:
        import list_shape as LS
        for t in texts:
            iid = shape_id(t)
            if iid and iid in world.items:
                parts = (world.items[iid].shape or {}).get("parts") or []
                shaped[t] = iid
                texts += [q["effect"] for q in parts if isinstance(q, dict) and LS._check_ok(q.get("effect"))]
    first = list(dict.fromkeys(t for t in texts if t not in shaped))
    res = {}
    if first:
        with cf.ThreadPoolExecutor(max(1, min(workers, len(first)))) as ex:
            futs = {ex.submit(run_one, t, root, store, write, None, stats): t for t in first}
            for f in cf.as_completed(futs):
                try:
                    res[futs[f]] = f.result()
                except Exception as e:  # noqa: BLE001 - one check's fault is that check's unmeasured, never the beat's
                    res[futs[f]] = ("unmeasured", "the check could not be run (%s: %s)" % (type(e).__name__, e))
    for t, iid in shaped.items():
        try:
            import list_shape as LS
            code, out = LS.holds_text(iid, world, root, run=lambda q, r: res.get(q) or run_one(q, r, store, write))
            _count(stats, "in_process")
            res[t] = {0: ("holds", out), 1: ("fails", out)}.get(
                code, ("unmeasured", "exit %d (only 0 holds and 1 fails)" % code + ("\n" + out if out else "")))
        except Exception as e:  # noqa: BLE001
            res[t] = ("unmeasured", "the shape check could not be answered (%s: %s)" % (type(e).__name__, e))
    stats["checks"] = len(res)
    stats["seconds"] = round(time.time() - t0, 1)
    return res, stats


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("check", nargs="+", help="one or more check texts")
    ap.add_argument("--root", default=None)
    ap.add_argument("--no-keep", action="store_true", help="read kept results, keep nothing new")
    a = ap.parse_args(argv)
    res, st = run_many(a.check, a.root or _le().check_root(), write=not a.no_keep)
    for t, (v, o) in res.items():
        print("%-10s %s\n           %s" % (v, t, " ".join(str(o or "").split())[:300]))  # cut-ok: terminal display
    print("stats: %s" % json.dumps(st, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
