"""One evidence record per (item, sha): immutable receipts, appended, never rewritten (RIMFLOW_BUILD_EVIDENCE_RECEIPTS_FIRST,
redesign_final.md WP-09a; redesign.md section 2).

Owner 2026-11-06: "I like replacing the guards with the evidence already gathered very much". This step only WRITES the
record; no guard reads it yet (09b adds a shadow predicate in cli.py, 09c deletes guards one at a time).

Layout, under the Relentless store dir (<root>/store):
    evidence/<ID>/<sha>.jsonl   the record: one JSON entry per line, each a step (a box run, a Marker verdict, ...)
    evidence/index.jsonl        every append, store-wide: (item, sha, n, hash) - the anchor that makes a cut tail visible
    evidence/HEAD.json          the seal: index length and last hash after the last whole append (a cut tail shows)
    evidence/.pending.json      the append in flight: written before either file, removed after HEAD; a crash leaves it
                                and the next locked reader or writer rolls that one append forward (nothing stranded)
    evidence/.lock              flock held across one append, and by readers (no half-written append is ever seen)

Every entry carries `prev` (the hash of the entry before it in the same record, ZERO for the first) and `hash` (sha256 of
the entry's canonical JSON without `hash`). The index is chained the same way. So an edited line breaks its own hash and
the next line's prev; a deleted or cut line disagrees with the index; a rewritten index breaks its own chain; a tail cut
from both the record and the index (two valid prefixes) disagrees with HEAD, which is required once any index row is
`sealed` (a store from before HEAD gains it on its next append). verify() and read() check the index and HEAD too. Appending to a record that does not verify is refused (TamperError): new evidence is never laid on top of
changed evidence. Files are left read-only (0444) between appends, so a careless editor fails loudly first.

Kinds (one schema version, V):
    run     a box run of the item's proof at sha (relentless_boxrun.check, finish or the builder's verb): gen, kind_of_run,
            mode, exam_hash (today the contract hash; WP-03 makes it the exam's), argv, exit, out_sha256, secs, verdict,
            why, box {config_hash, tools}
    marker  a Marker's verdict at sha: verdict (PASS/WEAK/FAIL/UNMEASURED), classes (cause classes), defects (its
            structured defect lines), session, nonce, reasons_sha256

Only the supervisor writes here (finish's box run, the Marker's verdict, later the live broker). Read with read() /
verify(); `python3 evidence.py verify|show|marker|harvest`.
"""
import argparse
import contextlib
import fcntl
import hashlib
import io
import json
import os
import re
import stat
import subprocess
import sys
import time

V = 1
ZERO = "0" * 64
KINDS = ("run", "marker")
MARKER_WORDS = ("PASS", "WEAK", "FAIL", "UNMEASURED")
INDEX = "index.jsonl"
HEAD = "HEAD.json"          # the seal: the index length and last hash after the last whole append
PENDING = ".pending.json"    # the one append in flight: written first, removed last, rolled forward after a crash
_ID = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_.-]{0,159}$")     # never "." / ".." / a dotfile: no way out of evidence/
_SHA = re.compile(r"^[0-9a-f]{40}([0-9a-f]{24})?$")


class TamperError(ValueError):
    """The record (or the index) does not verify: nothing is appended on top of it."""


# ---------------------------------------------------------------- where

def base(store_dir):
    return os.path.join(store_dir, "evidence")


def record_path(store_dir, item, sha):
    if not _ID.match(str(item or "")):
        raise ValueError("evidence: not an item id: %r" % (item,))
    if not _SHA.match(str(sha or "")):
        raise ValueError("evidence: sha must be one full commit id, not %r" % (sha,))
    return os.path.join(base(store_dir), item, "%s.jsonl" % sha)


def entry_hash(entry):
    body = {k: v for k, v in entry.items() if k != "hash"}
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def sha256_text(text):
    return hashlib.sha256((text or "").encode("utf-8", "replace")).hexdigest()


# ---------------------------------------------------------------- reading and verifying

def _lines(path):
    """-> [(lineno, entry or None for an unparseable line)]; [] when the file is not there."""
    try:
        with open(path, encoding="utf-8") as f:
            raw = f.read()
    except FileNotFoundError:
        return []
    out = []
    for n, line in enumerate(raw.split("\n")):
        if not line.strip():
            continue
        try:
            e = json.loads(line)
        except ValueError:
            e = None
        out.append((n + 1, e if isinstance(e, dict) else None))
    if raw and not raw.endswith("\n"):
        out.append((raw.count("\n") + 1, None))     # a torn last line: an append that did not finish, or a cut
    return out


def _chain(rows, what):
    """-> [problem] for one hash chain."""
    bad, prev = [], ZERO
    for i, (ln, e) in enumerate(rows):
        if e is None:
            bad.append("%s line %d: not a JSON object (edited or torn)" % (what, ln))
            prev = None
            continue
        if e.get("hash") != entry_hash(e):
            bad.append("%s line %d: its hash does not match its content (edited)" % (what, ln))
        if prev is not None and e.get("prev") != prev:
            bad.append("%s line %d: prev does not link to the line before (a line removed, inserted or reordered)" % (what, ln))
        if e.get("n") != i:
            bad.append("%s line %d: n=%r, expected %d" % (what, ln, e.get("n"), i))
        prev = e.get("hash")
    return bad


def _index(store_dir):
    return _lines(os.path.join(base(store_dir), INDEX))


def _head(store_dir):
    """-> (HEAD dict, None) or (None, problem); (None, None) when there is no HEAD file."""
    try:
        with open(os.path.join(base(store_dir), HEAD), encoding="utf-8") as f:
            h = json.loads(f.read())
    except FileNotFoundError:
        return None, None
    except (OSError, ValueError) as e:
        return None, "HEAD is not readable JSON (%s)" % type(e).__name__
    return (h, None) if isinstance(h, dict) else (None, "HEAD is not a JSON object")


def _index_problems(store_dir, rows):
    """The index's own chain plus the HEAD seal: a tail cut from the index (with or without its record lines) leaves a
    valid prefix chain, and only HEAD, written after every append, still names the true length and last hash."""
    bad = _chain(rows, INDEX)
    ents = [e for _, e in rows if e]
    h, why = _head(store_dir)
    if why:
        bad.append(why)
    elif h is None:
        if any(e.get("sealed") for e in ents):
            bad.append("HEAD is missing but the index was sealed (HEAD deleted)")
    elif h.get("n") != len(ents) or h.get("hash") != (ents[-1]["hash"] if ents else ZERO):
        bad.append("HEAD names %s index rows ending %s, the index has %d ending %s (a tail cut, or HEAD rewritten)" % (
            h.get("n"), str(h.get("hash"))[:10], len(ents), (ents[-1].get("hash") if ents else ZERO)[:10]))
    return bad


def verify_index(store_dir):
    with _consistent(store_dir) as rbad:
        return rbad + _index_problems(store_dir, _index(store_dir))


def _verify_record(store_dir, item, sha, rows, index_rows):
    """-> [problem] for one record against one snapshot of the index (the record's chain, its envelope, and that the
    index names every one of its lines with the same hash)."""
    path = record_path(store_dir, item, sha)
    bad = _chain(rows, os.path.relpath(path, base(store_dir)))
    for ln, e in rows:
        if e and (e.get("item"), e.get("sha"), e.get("v")) != (item, sha, V):
            bad.append("line %d: names %s@%s v%s, not this record" % (ln, e.get("item"), str(e.get("sha"))[:10], e.get("v")))
    idx = [e for _, e in index_rows if e and e.get("item") == item and e.get("sha") == sha]
    have = {e.get("n"): e.get("hash") for _, e in rows if e}
    for e in idx:       # an index row names the record's line by entry_n (its own n is its place in the index)
        if e.get("entry_n") not in have:
            bad.append("entry %s is in the index but not in the record (cut or deleted)" % e.get("entry_n"))
        elif have[e["entry_n"]] != e.get("entry"):
            bad.append("entry %s differs from the hash the index took when it was appended" % e["entry_n"])
    named = {e.get("entry_n") for e in idx}
    for n in sorted(k for k in have if k not in named):
        bad.append("entry %s is not in the index (written around evidence.append)" % n)
    return bad


def verify(store_dir, item, sha):
    """-> [problem]; [] = the record is exactly what was appended AND the index it is checked against verifies (its
    chain and its HEAD seal) - a record is never vouched for by an index nobody checked."""
    path = record_path(store_dir, item, sha)
    with _consistent(store_dir) as rbad:
        idx = _index(store_dir)
        return rbad + _index_problems(store_dir, idx) + _verify_record(store_dir, item, sha, _lines(path), idx)


def read(store_dir, item, sha, strict=True):
    """-> [entry] in order, from the one snapshot that was verified. strict: raises TamperError when the record or the
    index does not verify."""
    path = record_path(store_dir, item, sha)
    with _consistent(store_dir) as rbad:
        idx, rows = _index(store_dir), _lines(path)
        bad = rbad + _index_problems(store_dir, idx) + _verify_record(store_dir, item, sha, rows, idx)
    if bad and strict:
        raise TamperError("; ".join(bad[:5]))
    return [e for _, e in rows if e]


def records(store_dir):
    """-> [(item, sha)] for every record on disk."""
    out, b = [], base(store_dir)
    try:
        items = sorted(os.listdir(b))
    except FileNotFoundError:
        return []
    for item in items:
        d = os.path.join(b, item)
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            if f.endswith(".jsonl"):
                out.append((item, f[:-6]))
    return out


def verify_all(store_dir):
    """-> {"index": [problem], "<item>@<sha>": [problem], ...} - only the ones with problems, plus index."""
    with _consistent(store_dir) as rbad:
        rows = _index(store_dir)
        out = {"index": rbad + _index_problems(store_dir, rows)}
        seen = set()
        for item, sha in records(store_dir):
            seen.add((item, sha))
            try:
                path = record_path(store_dir, item, sha)
            except ValueError as e:
                out["%s@%s" % (item, sha)] = ["not a record a writer could have made (%s)" % e]
                continue
            bad = _verify_record(store_dir, item, sha, _lines(path), rows)
            if bad:
                out["%s@%s" % (item, sha)] = bad
    for _, e in rows:       # a whole record deleted: its index lines stay
        k = (e or {}).get("item"), (e or {}).get("sha")
        if e and k not in seen:
            seen.add(k)
            out["%s@%s" % k] = ["the index names this record but it is not on disk (deleted)"]
    return out


# ---------------------------------------------------------------- durability and the one transaction

def _fsync_dir(path):
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _makedirs(path):
    """os.makedirs, with every directory it creates made durable in its parent."""
    path = os.path.abspath(path)
    missing = []
    while not os.path.isdir(path):
        missing.append(path)
        path = os.path.dirname(path)
    for d in reversed(missing):
        try:
            os.mkdir(d)
        except FileExistsError:
            pass
        _fsync_dir(os.path.dirname(d))


def _write_all(fd, data):
    """os.write until every byte is down: a short write (a full disk) is an OSError, never a silent truncation."""
    view = memoryview(data)
    while view:
        n = os.write(fd, view)
        if n <= 0:
            raise OSError("evidence: write wrote %r bytes" % (n,))
        view = view[n:]


def _append_bytes(path, data):
    """data on the end of path, fsynced (and its directory entry, when the file is new); the file left 0444."""
    new = not os.path.exists(path)
    if not new:
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
    fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
    try:
        _write_all(fd, data)
        os.fsync(fd)
    finally:
        os.close(fd)
        os.chmod(path, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
    if new:
        _fsync_dir(os.path.dirname(path))


def _replace(path, text):
    """path replaced whole by text, atomically and durably (tmp, fsync, rename, fsync the directory)."""
    tmp = path + ".tmp"
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
    try:
        _write_all(fd, text.encode("utf-8"))
        os.fsync(fd)
    finally:
        os.close(fd)
    os.replace(tmp, path)
    _fsync_dir(os.path.dirname(path))


def _line(entry):
    return json.dumps(entry, sort_keys=True, separators=(",", ":")) + "\n"


def _size(path):
    try:
        return os.path.getsize(path)
    except FileNotFoundError:
        return 0


def _finish_tail(path, pre_len, line, what):
    """Bring path to exactly its pre_len bytes + line: nothing past pre_len (the crash came first), a prefix of line (a
    torn write), line itself, or - a power loss before the fsync - a tail whose every byte is line's or NUL (cut back
    to pre_len and written again). Anything else past pre_len is not this transaction: TamperError."""
    data = line.encode("utf-8")
    size = _size(path)
    if size < pre_len:
        raise TamperError("%s is shorter (%d bytes) than before the pending append (%d): cut" % (what, size, pre_len))
    with open(path, "rb") if os.path.exists(path) else io.BytesIO() as f:
        f.seek(pre_len)
        tail = f.read()
    if not data.startswith(tail):
        if len(tail) > len(data) or any(b != 0 and b != data[i] for i, b in enumerate(tail)):
            raise TamperError("%s holds %d bytes past the pending append that are not its line" % (what, len(tail)))
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
        os.truncate(path, pre_len)
        tail = b""
    if len(tail) < len(data):
        if not os.path.exists(os.path.dirname(path)):
            _makedirs(os.path.dirname(path))
        _append_bytes(path, data[len(tail):])


def _recover(store_dir):
    """Complete the append a crash interrupted (the caller holds the lock). append() writes PENDING (the record line,
    the index line, HEAD and both files' lengths before) BEFORE it touches either file, and removes it last; a PENDING
    left on disk is rolled FORWARD to exactly that transaction, so a crash between the record line and the index line
    strands nothing. A PENDING that does not fit the files is tampering, refused and left in place."""
    p = os.path.join(base(store_dir), PENDING)
    try:
        with open(p, encoding="utf-8") as f:
            t = json.loads(f.read())
    except FileNotFoundError:
        return
    except (OSError, ValueError) as e:
        raise TamperError("%s is not readable JSON (%s)" % (PENDING, type(e).__name__))
    try:
        path = record_path(store_dir, t["item"], t["sha"])
        _finish_tail(path, int(t["rec_len"]), t["line"], os.path.relpath(path, base(store_dir)))
        _finish_tail(os.path.join(base(store_dir), INDEX), int(t["idx_len"]), t["ix_line"], INDEX)
        head = t["head"]
        _fsync_dir(os.path.dirname(path))      # the crash may have come between creating an entry and syncing it
        _fsync_dir(os.path.dirname(os.path.dirname(path)))
    except (KeyError, TypeError, ValueError, AttributeError) as e:
        raise TamperError("%s is malformed (%s: %s)" % (PENDING, type(e).__name__, e))
    _replace(os.path.join(base(store_dir), HEAD), json.dumps(head, sort_keys=True))
    os.remove(p)
    _fsync_dir(base(store_dir))


@contextlib.contextmanager
def _locked(store_dir):
    _makedirs(base(store_dir))
    fd = os.open(os.path.join(base(store_dir), ".lock"), os.O_CREAT | os.O_RDWR, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        os.close(fd)


@contextlib.contextmanager
def _consistent(store_dir):
    """A reader's view: the append lock held (so no half-written append is seen) and an interrupted append completed.
    Yields [problem] - a recovery that could not complete - for the reader to report; a store with no evidence/ dir is
    read as it is (no lock, nothing created)."""
    if not os.path.isdir(base(store_dir)):
        yield []
        return
    with _locked(store_dir):
        try:
            _recover(store_dir)
            bad = []
        except (TamperError, OSError) as e:
            bad = ["an interrupted append could not be completed: %s" % e]
        yield bad


# ---------------------------------------------------------------- appending

def append(store_dir, item, sha, kind, body, at=None, nonce=None):
    """-> the entry written (with n, prev, hash), or None when nonce is given and the record already holds a marker
    entry with it (checked under the same lock as the write, so two writers cannot both pass). Refuses (TamperError)
    when the record or the index does not verify; ValueError on a bad id, sha or kind. body keys never override the
    envelope."""
    if kind not in KINDS:
        raise ValueError("evidence: kind is one of %s, not %r" % ("/".join(KINDS), kind))
    path = record_path(store_dir, item, sha)
    with _locked(store_dir):
        _recover(store_dir)
        idx_rows, rec_rows = _index(store_dir), _lines(path)
        bad = _index_problems(store_dir, idx_rows) + _verify_record(store_dir, item, sha, rec_rows, idx_rows)
        if bad:
            raise TamperError("evidence for %s@%s does not verify, nothing appended: %s" % (item, sha[:10], "; ".join(bad[:5])))
        rows = [e for _, e in rec_rows if e]
        if nonce and any(e.get("nonce") == nonce for e in rows):
            return None
        entry = dict(body or {})
        if nonce:
            entry["nonce"] = nonce
        entry.update(v=V, kind=kind, item=item, sha=sha, n=len(rows), prev=rows[-1]["hash"] if rows else ZERO,
                     at=at or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
        entry.pop("hash", None)
        entry["hash"] = entry_hash(entry)
        last = [e for _, e in idx_rows if e]
        ix = {"v": V, "n": len(last), "prev": last[-1]["hash"] if last else ZERO, "item": item, "sha": sha,
              "entry_n": entry["n"], "entry": entry["hash"], "kind": kind, "at": entry["at"], "sealed": 1}
        for k in ("kind_of_run", "mode", "verdict"):     # what an SLI counts without opening every record
            if k in entry:
                ix[k] = entry[k]
        ix["hash"] = entry_hash(ix)
        ipath = os.path.join(base(store_dir), INDEX)
        txn = {"item": item, "sha": sha, "rec_len": _size(path), "line": _line(entry), "idx_len": _size(ipath),
               "ix_line": _line(ix), "head": {"v": V, "n": len(last) + 1, "hash": ix["hash"]}}
        _replace(os.path.join(base(store_dir), PENDING), json.dumps(txn, sort_keys=True))
        _makedirs(os.path.dirname(path))
        _append_bytes(path, txn["line"].encode("utf-8"))
        _append_bytes(ipath, txn["ix_line"].encode("utf-8"))
        _replace(os.path.join(base(store_dir), HEAD), json.dumps(txn["head"], sort_keys=True))
        os.remove(os.path.join(base(store_dir), PENDING))
        _fsync_dir(base(store_dir))
        return entry


# ---------------------------------------------------------------- box tools

_TOOLS = {}


def box_tools(box_cfg=None):
    """-> {config_hash, tools{name: version}}: what the box carried. config_hash is relentless_box.json's toolchain,
    path_prepend and grants (what make_box builds from); tools are probed once per process on the host binaries the box
    binds (the same git and the same checkbox venv python), `probed: host`."""
    if box_cfg is None:
        try:
            import relentless_wall
            box_cfg = relentless_wall.box_config()
        except ImportError:
            box_cfg = {}
    shape = {k: box_cfg.get(k) for k in ("toolchain", "path_prepend", "default_grants", "reach_served")}
    key = json.dumps(shape, sort_keys=True)
    if key not in _TOOLS:
        tools = {}
        py = "/usr/bin/python3"
        for p in box_cfg.get("path_prepend") or []:
            cand = os.path.join(os.path.expanduser(str(p)), "python3")
            if os.access(cand, os.X_OK):
                py = cand
                break
        probes = {"git": ["git", "--version"],
                  "python3": [py, "-c", "import sys; print(sys.version.split()[0])"],
                  "cv2": [py, "-c", "import cv2, numpy; print(cv2.__version__, numpy.__version__)"]}
        for name, argv in probes.items():
            try:
                r = subprocess.run(argv, capture_output=True, text=True, timeout=30, stdin=subprocess.DEVNULL)
                tools[name] = (r.stdout.strip() or r.stderr.strip()[-120:]) if r.returncode == 0 else "absent (exit %d)" % r.returncode
            except (OSError, subprocess.SubprocessError) as e:
                tools[name] = "absent (%s)" % type(e).__name__
        tools["toolchain"] = [str(t.get("name")) for t in box_cfg.get("toolchain") or [] if isinstance(t, dict)]
        _TOOLS[key] = {"config_hash": hashlib.sha256(key.encode()).hexdigest(), "tools": tools, "probed": "host"}
    return json.loads(json.dumps(_TOOLS[key]))


BOX_TOOLS = box_tools    # the seam selftests replace


# ---------------------------------------------------------------- the two writers

def run_receipt(store_dir, item, sha, rec, exam_hash, argv):
    """relentless_boxrun.check's receipt: one `run` entry from its run record. -> the entry."""
    body = {"gen": rec.get("gen"), "kind_of_run": rec.get("kind"), "mode": rec.get("mode"), "verdict": rec.get("verdict"),
            "exam_hash": exam_hash, "exam_kind": "contract", "argv": argv, "exit": rec.get("exit"),
            "out_sha256": rec.get("out_sha256"), "out_tail": rec.get("out_tail"), "secs": rec.get("secs"),
            "why": rec.get("why"), "box": BOX_TOOLS() if argv else None}
    return append(store_dir, item, sha, "run", body, at=rec.get("at"))


def append_marker(store_dir, item, sha, verdict, classes=None, session=None, nonce=None, reasons="", defects=None):
    """The Marker's verdict on sha, appended (never a rewrite of an earlier verdict). Idempotent on nonce: the same
    check's verdict seen twice is one entry. -> the entry, or None when this nonce is already there."""
    word = str(verdict or "").upper()
    if word not in MARKER_WORDS:
        raise ValueError("evidence: a Marker verdict is one of %s, not %r" % ("/".join(MARKER_WORDS), verdict))
    return append(store_dir, item, sha, "marker", {"verdict": word, "classes": list(classes or []), "session": session,
                                                    "defects": list(defects or []), "nonce": nonce,
                                                    "reasons_sha256": sha256_text(reasons)}, nonce=nonce)


def _harvest_nonce(chk):
    """A verdict held without a nonce still dedupes: the same held check (verdict, session, reasons) is one entry."""
    raw = json.dumps([str(chk.get("verdict")), chk.get("session"), chk.get("reasons") or "", chk.get("defects") or []],
                     sort_keys=True, default=str)
    return "harvest-" + sha256_text(raw)[:24]


def harvest(store, failures=None):
    """Append every Marker verdict a store item holds now (check.verdict on its candidate's sha) that its record does
    not have yet. -> [(item, sha, verdict)] appended; each one that failed is added to `failures` as (item, reason)
    (the CLI exits 1 when any did: "nothing new" and "every receipt failed" must not look alike). The tick's call site is not wired yet (WP-09a edits no relentless.py):
    run `evidence.py harvest` until it is."""
    got = []
    for st in store.states():
        chk, cand = st.get("check") or {}, st.get("candidate") or {}
        if not chk.get("verdict") or not _SHA.match(str(cand.get("sha") or "")):
            continue
        try:
            e = append_marker(store.dir, st["item"], cand["sha"], chk["verdict"], defects=chk.get("defects") or [],
                              session=chk.get("session"), reasons=chk.get("reasons") or "",
                              nonce=chk.get("nonce") or _harvest_nonce(chk))
        except (ValueError, OSError) as ex:
            print("evidence: harvest %s: %s" % (st.get("item"), ex), file=sys.stderr)
            if failures is not None:
                failures.append((st.get("item"), str(ex)))
            continue
        if e:
            got.append((st["item"], cand["sha"], e["verdict"]))
    return got


def index_rows(store_dir, since=None):
    """-> [index entry] (for SLIs), at or after `since` (ISO)."""
    return [e for _, e in _index(store_dir) if e and (not since or e.get("at", "") >= since)]


# ---------------------------------------------------------------- CLI

def _store_dir(a):
    if a.store_dir:
        return a.store_dir
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import relentless
    return relentless.Store().dir


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--store-dir", help="the Relentless store dir (default: relentless.Store().dir)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("verify", help="verify one record, or every record and the index")
    v.add_argument("--item")
    v.add_argument("--sha")
    s = sub.add_parser("show", help="print one record's entries")
    s.add_argument("--item", required=True)
    s.add_argument("--sha", required=True)
    m = sub.add_parser("marker", help="append a Marker verdict")
    for k in ("--item", "--sha", "--verdict"):
        m.add_argument(k, required=True)
    m.add_argument("--class", dest="classes", action="append", default=[])
    m.add_argument("--session")
    m.add_argument("--nonce")
    m.add_argument("--reasons", default="")
    sub.add_parser("harvest", help="append the Marker verdicts store items hold now")
    a = ap.parse_args(argv)
    d = _store_dir(a)
    if a.cmd == "verify":
        bad = {"%s@%s" % (a.item, a.sha): verify(d, a.item, a.sha)} if a.item and a.sha else verify_all(d)
        bad = {k: x for k, x in bad.items() if x}
        for k, x in bad.items():
            for p in x:
                print("TAMPERED %s: %s" % (k, p))
        print("evidence: %s" % ("TAMPERED (%d)" % len(bad) if bad else "OK (%d records)" % len(records(d))))
        return 1 if bad else 0
    if a.cmd == "show":
        for e in read(d, a.item, a.sha, strict=False):
            print(json.dumps(e, sort_keys=True))
        bad = verify(d, a.item, a.sha)
        print("evidence: %s" % ("TAMPERED: " + "; ".join(bad) if bad else "OK"))
        return 1 if bad else 0
    if a.cmd == "marker":
        e = append_marker(d, a.item, a.sha, a.verdict, a.classes, a.session, a.nonce, a.reasons)
        print("evidence: %s" % ("appended n=%d" % e["n"] if e else "already there (same nonce)"))
        return 0
    if a.cmd == "harvest":
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import relentless
        failed = []
        got = harvest(relentless.Store(os.path.dirname(d)), failed)
        print("evidence: harvested %d Marker verdict(s)%s" % (len(got), ", %d FAILED" % len(failed) if failed else ""))
        return 1 if failed else 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
