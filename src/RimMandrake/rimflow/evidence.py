"""One evidence record per (item, sha): immutable receipts, appended, never rewritten (RIMFLOW_BUILD_EVIDENCE_RECEIPTS_FIRST,
redesign_final.md WP-09a; redesign.md section 2).

Owner 2026-11-06: "I like replacing the guards with the evidence already gathered very much". This step only WRITES the
record; no guard reads it yet (09b adds a shadow predicate in cli.py, 09c deletes guards one at a time).

Layout, under the Relentless store dir (<root>/store):
    evidence/<ID>/<sha>.jsonl   the record: one JSON entry per line, each a step (a box run, a Marker verdict, ...)
    evidence/index.jsonl        every append, store-wide: (item, sha, n, hash) - the anchor that makes a cut tail visible
    evidence/.lock              flock held across one append (record line + index line)

Every entry carries `prev` (the hash of the entry before it in the same record, ZERO for the first) and `hash` (sha256 of
the entry's canonical JSON without `hash`). The index is chained the same way. So an edited line breaks its own hash and
the next line's prev; a deleted or cut line disagrees with the index; a rewritten index breaks its own chain. verify()
says which. Appending to a record that does not verify is refused (TamperError): new evidence is never laid on top of
changed evidence. Files are left read-only (0444) between appends, so a careless editor fails loudly first.

Kinds (one schema version, V):
    run     a box run of the item's proof at sha (relentless_boxrun.check, finish or the builder's verb): gen, kind_of_run,
            mode, exam_hash (today the contract hash; WP-03 makes it the exam's), argv, exit, out_sha256, secs, verdict,
            why, box {config_hash, tools}
    marker  a Marker's verdict at sha: verdict (PASS/WEAK/FAIL/UNMEASURED), classes, session, nonce, reasons_sha256

Only the supervisor writes here (finish's box run, the Marker's verdict, later the live broker). Read with read() /
verify(); `python3 evidence.py verify|show|marker|harvest`.
"""
import argparse
import contextlib
import fcntl
import hashlib
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
_ID = re.compile(r"^[A-Za-z0-9_.-]{1,160}$")
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
        out.append((len(out) + 1, None))     # a torn last line: an append that did not finish, or a cut
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


def verify_index(store_dir):
    return _chain(_index(store_dir), INDEX)


def verify(store_dir, item, sha, index_rows=None):
    """-> [problem]; [] = the record is exactly what was appended. Checks the record's chain and that the store-wide
    index names every one of its lines with the same hash (a cut tail or a removed record shows here)."""
    path = record_path(store_dir, item, sha)
    rows = _lines(path)
    bad = _chain(rows, os.path.relpath(path, base(store_dir)))
    for ln, e in rows:
        if e and (e.get("item"), e.get("sha"), e.get("v")) != (item, sha, V):
            bad.append("line %d: names %s@%s v%s, not this record" % (ln, e.get("item"), str(e.get("sha"))[:10], e.get("v")))
    idx = [e for _, e in (_index(store_dir) if index_rows is None else index_rows)
           if e and e.get("item") == item and e.get("sha") == sha]
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


def read(store_dir, item, sha, strict=True):
    """-> [entry] in order. strict: raises TamperError when the record does not verify."""
    bad = verify(store_dir, item, sha)
    if bad and strict:
        raise TamperError("; ".join(bad[:5]))
    return [e for _, e in _lines(record_path(store_dir, item, sha)) if e]


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
    rows = _index(store_dir)
    out = {"index": _chain(rows, INDEX)}
    seen = set()
    for item, sha in records(store_dir):
        seen.add((item, sha))
        bad = verify(store_dir, item, sha, rows)
        if bad:
            out["%s@%s" % (item, sha)] = bad
    for _, e in rows:       # a whole record deleted: its index lines stay
        k = (e or {}).get("item"), (e or {}).get("sha")
        if e and k not in seen:
            seen.add(k)
            out["%s@%s" % k] = ["the index names this record but it is not on disk (deleted)"]
    return out


# ---------------------------------------------------------------- appending

@contextlib.contextmanager
def _locked(store_dir):
    os.makedirs(base(store_dir), exist_ok=True)
    fd = os.open(os.path.join(base(store_dir), ".lock"), os.O_CREAT | os.O_RDWR, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        os.close(fd)


def _append_line(path, entry):
    """One line on the end of path, fsynced, the file left 0444."""
    line = json.dumps(entry, sort_keys=True, separators=(",", ":")) + "\n"
    if os.path.exists(path):
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
    fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
    try:
        os.write(fd, line.encode("utf-8"))
        os.fsync(fd)
    finally:
        os.close(fd)
        os.chmod(path, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)


def append(store_dir, item, sha, kind, body, at=None):
    """-> the entry written (with n, prev, hash). Refuses (TamperError) when the record or the index does not verify;
    ValueError on a bad id, sha or kind. body keys never override the envelope."""
    if kind not in KINDS:
        raise ValueError("evidence: kind is one of %s, not %r" % ("/".join(KINDS), kind))
    path = record_path(store_dir, item, sha)
    with _locked(store_dir):
        idx_rows = _index(store_dir)
        bad = _chain(idx_rows, INDEX) + verify(store_dir, item, sha, idx_rows)
        if bad:
            raise TamperError("evidence for %s@%s does not verify, nothing appended: %s" % (item, sha[:10], "; ".join(bad[:5])))
        rows = [e for _, e in _lines(path) if e]
        entry = dict(body or {})
        entry.update(v=V, kind=kind, item=item, sha=sha, n=len(rows), prev=rows[-1]["hash"] if rows else ZERO,
                     at=at or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
        entry.pop("hash", None)
        entry["hash"] = entry_hash(entry)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        _append_line(path, entry)
        last = [e for _, e in idx_rows if e]
        ix = {"v": V, "n": len(last), "prev": last[-1]["hash"] if last else ZERO, "item": item, "sha": sha,
              "entry_n": entry["n"], "entry": entry["hash"], "kind": kind, "at": entry["at"]}
        for k in ("kind_of_run", "mode", "verdict"):     # what an SLI counts without opening every record
            if k in entry:
                ix[k] = entry[k]
        ix["hash"] = entry_hash(ix)
        _append_line(os.path.join(base(store_dir), INDEX), ix)
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


def append_marker(store_dir, item, sha, verdict, classes=None, session=None, nonce=None, reasons=""):
    """The Marker's verdict on sha, appended (never a rewrite of an earlier verdict). Idempotent on nonce: the same
    check's verdict seen twice is one entry. -> the entry, or None when this nonce is already there."""
    word = str(verdict or "").upper()
    if word not in MARKER_WORDS:
        raise ValueError("evidence: a Marker verdict is one of %s, not %r" % ("/".join(MARKER_WORDS), verdict))
    if nonce and os.path.exists(record_path(store_dir, item, sha)):
        if any(e.get("kind") == "marker" and e.get("nonce") == nonce for e in read(store_dir, item, sha)):
            return None
    return append(store_dir, item, sha, "marker", {"verdict": word, "classes": list(classes or []), "session": session,
                                                    "nonce": nonce, "reasons_sha256": sha256_text(reasons)})


def harvest(store):
    """Append every Marker verdict a store item holds now (check.verdict on its candidate's sha) that its record does
    not have yet. -> [(item, sha, verdict)] appended. The tick's call site is not wired yet (WP-09a edits no relentless.py):
    run `evidence.py harvest` until it is."""
    got = []
    for st in store.states():
        chk, cand = st.get("check") or {}, st.get("candidate") or {}
        if not chk.get("verdict") or not _SHA.match(str(cand.get("sha") or "")):
            continue
        try:
            e = append_marker(store.dir, st["item"], cand["sha"], chk["verdict"], classes=chk.get("defects") or [],
                              session=chk.get("session"), nonce=chk.get("nonce"), reasons=chk.get("reasons") or "")
        except (ValueError, OSError) as ex:
            print("evidence: harvest %s: %s" % (st.get("item"), ex), file=sys.stderr)
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
        got = harvest(relentless.Store(os.path.dirname(d)))
        print("evidence: harvested %d Marker verdict(s)" % len(got))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
