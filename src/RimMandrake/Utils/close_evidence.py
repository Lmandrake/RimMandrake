#!/usr/bin/env python3
"""close_evidence.py -- machine evidence per commit sha, so the Arbiter's no-AI gates can decide a close.

CLOSE_EVIDENCE_BUILD_GATES_CAN_DECIDE (design/RimMandrake/rimflow_v3_arbiter_tiers_2026-10-27.md, "Missing gates"):
94% of closes recorded no machine evidence, although selftests, C# builds, patch validation and modcheck all ran.
Each of those tools now appends ONE line here when it finishes; a gate looks the sha up at claim time with no AI and
no re-run.

Where: one JSONL per UTC day, `<agent storage>/rimmandrake/evidence/YYYY-MM-DD.jsonl`. The root comes from
`python3 ~/dev/Lodestar/bin/lib/agent_storage.py rimmandrake` (never hard-wired); `RM_CLOSE_EVIDENCE_DIR` overrides it
(selftests). Append-only: a line is never rewritten.

A line: {v, ts, tool, clone, sha, dirty, dirty_n, dirty_paths, paths, result, item, seat, detail}
  * sha    -- HEAD of the clone the covered paths live in; None when they live in no git clone (a game Mods folder).
  * dirty  -- the clone had uncommitted changes (tracked or untracked) outside DIRTY_IGNORE; None when git could
              not say. A dirty or unknown run is RECORDED (so its existence is auditable) but `lookup` never returns
              it as evidence for a sha: the result describes the working tree, not the commit.
  * result -- PASS / FAIL / UNMEASURED, nothing else.
  * item   -- `$RIMFLOW_ITEM` when the caller set it, else None.

Writing evidence never fails the tool: every error is printed loudly to stderr and swallowed.
Under the selftest runner (`RM_SELFTEST_NESTED`) a tool run by a test writes nothing unless the test pointed
`RM_CLOSE_EVIDENCE_DIR` somewhere, so fixtures never pose as evidence; the runner itself records with force=True.

    python3 src/RimMandrake/Utils/close_evidence.py lookup --sha <sha> [--item ID] [--tool T] [--all]
    python3 src/RimMandrake/Utils/close_evidence.py where
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import subprocess
import sys
from pathlib import Path

V = 1
RESULTS = ("PASS", "FAIL", "UNMEASURED")
ENV_DIR = "RM_CLOSE_EVIDENCE_DIR"
AGENT_STORAGE = Path.home() / "dev/Lodestar/bin/lib/agent_storage.py"
#: Paths whose uncommitted state never feeds a tool's result: session transcripts are written continuously
#: into the bench clone, so counting them would make every run "dirty" and the record worthless.
DIRTY_IGNORE = ("conversations/",)
DIRTY_KEEP = 20
_ROOT_CACHE: list = []


def evidence_dir() -> Path:
    """The evidence folder (created). Raises when the storage root cannot be found."""
    env = os.environ.get(ENV_DIR, "").strip()
    if env:
        p = Path(env)
    else:
        if not _ROOT_CACHE:
            r = subprocess.run([sys.executable or "python3", str(AGENT_STORAGE), "rimmandrake"],
                               capture_output=True, text=True, timeout=30)
            out = r.stdout.strip()
            if r.returncode != 0 or not out:
                raise RuntimeError("agent_storage.py rimmandrake failed: %s" % (r.stderr.strip() or "no output"))
            _ROOT_CACHE.append(out)
        p = Path(_ROOT_CACHE[0]) / "evidence"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _git(clone, *args, timeout=60):
    r = subprocess.run(["git", "-C", str(clone), *args], capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout


def clone_of(path) -> str | None:
    """The git toplevel holding `path` (a file or dir), or None."""
    p = Path(path).resolve()
    d = p if p.is_dir() else p.parent
    while not d.exists() and d != d.parent:
        d = d.parent
    try:
        rc, out = _git(d, "rev-parse", "--show-toplevel", timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.strip() if rc == 0 and out.strip() else None


def tree_state(clone) -> dict:
    """{sha, dirty, dirty_n, dirty_paths} for a clone. dirty None when git status could not run."""
    st = {"sha": None, "dirty": None, "dirty_n": None, "dirty_paths": []}
    try:
        rc, out = _git(clone, "rev-parse", "HEAD", timeout=30)
        if rc == 0 and out.strip():
            st["sha"] = out.strip()
        rc, out = _git(clone, "status", "--porcelain=v1", "-z", "--untracked-files=normal")
    except (OSError, subprocess.SubprocessError):
        return st
    if rc != 0:
        return st
    paths, recs, i = [], out.split("\0"), 0
    while i < len(recs):
        e = recs[i]
        i += 1
        if len(e) < 4:
            continue
        code, path = e[:2], e[3:]
        if code[0] in "RC":          # rename/copy: the next NUL field is the source path
            i += 1
        if not path.startswith(DIRTY_IGNORE):
            paths.append(path)
    st.update(dirty=bool(paths), dirty_n=len(paths), dirty_paths=sorted(paths)[:DIRTY_KEEP])
    return st


def _rel(path, clone) -> str:
    p = os.path.abspath(str(path))
    if clone:
        try:
            r = os.path.relpath(p, os.path.realpath(clone))
            if not r.startswith(".."):
                return r.replace(os.sep, "/")
        except ValueError:
            pass
    return p


def build_record(tool, result, paths, clone=None, detail=None, item=None, now=None) -> dict:
    if result not in RESULTS:
        raise ValueError("result must be one of %s, got %r" % (RESULTS, result))
    paths = [str(p) for p in (paths or [])]
    if clone is None and paths:
        clone = clone_of(paths[0])
    clone = os.path.realpath(str(clone)) if clone else None
    st = tree_state(clone) if clone else {"sha": None, "dirty": None, "dirty_n": None, "dirty_paths": []}
    now = now or datetime.datetime.now(datetime.timezone.utc)
    return {"v": V, "ts": now.isoformat(timespec="seconds"), "tool": tool, "clone": clone, **st,
            "paths": [_rel(p, clone) for p in paths], "result": result,
            "item": item if item is not None else (os.environ.get("RIMFLOW_ITEM") or None),
            "seat": os.environ.get("RIMFLOW_SEAT") or None, "detail": detail or {}}


def record(tool, result, paths, clone=None, detail=None, item=None, force=False) -> dict | None:
    """Append one evidence line. NEVER raises: a failure is printed loudly and None returned."""
    try:
        if os.environ.get("RM_SELFTEST_NESTED") and not force and not os.environ.get(ENV_DIR):
            return None                       # a tool run by a selftest: fixture, not evidence
        rec = build_record(tool, result, paths, clone, detail, item)
        day = rec["ts"][:10]
        line = (json.dumps(rec, sort_keys=True, default=str) + "\n").encode("utf-8")
        fd = os.open(str(evidence_dir() / ("%s.jsonl" % day)), os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
        try:
            os.write(fd, line)                # one write per line: concurrent appenders do not interleave
        finally:
            os.close(fd)
        return rec
    except Exception as exc:  # noqa: BLE001 -- evidence is a side channel; the tool's own verdict stands
        print("!!! CLOSE-EVIDENCE WRITE FAILED (%s, tool=%s): %s: %s -- the tool's result is unaffected, but no "
              "gate will see this run" % (__file__, tool, type(exc).__name__, exc), file=sys.stderr, flush=True)
        return None


def _days(n, today=None):
    today = today or datetime.datetime.now(datetime.timezone.utc).date()
    return [(today - datetime.timedelta(days=k)).isoformat() for k in range(n)]


def read_all(days=30, folder=None):
    """Every record in the last `days` day files, oldest first. Bad lines are skipped and counted."""
    folder = Path(folder) if folder else evidence_dir()
    out, bad = [], 0
    for day in sorted(_days(days)):
        f = folder / ("%s.jsonl" % day)
        if not f.is_file():
            continue
        with f.open(encoding="utf-8") as fh:
            for ln in fh:
                try:
                    out.append(json.loads(ln))
                except ValueError:
                    bad += 1
    if bad:
        print("close_evidence: %d unreadable line(s) skipped" % bad, file=sys.stderr)
    return out


def _sha_match(a, b) -> bool:
    if not a or not b:
        return False
    n = min(len(a), len(b))
    return n >= 7 and a[:n].lower() == b[:n].lower()


def counts_as_evidence(rec) -> bool:
    """A record speaks for its sha only from a clean tree at a known sha."""
    return bool(rec.get("sha")) and rec.get("dirty") is False and rec.get("result") in RESULTS


def lookup(sha=None, item=None, tool=None, days=30, folder=None, include_dirty=False):
    """Evidence for sha S and/or item X, oldest first.

    sha given: records at that commit (prefix match, >=7 chars), whatever item they name.
    item given: records tagged with that item; with sha too, both must match.
    Dirty-tree and unknown-tree records are excluded unless include_dirty (audit only)."""
    if not sha and not item:
        raise ValueError("lookup needs a sha or an item")
    hits = []
    for r in read_all(days, folder):
        if sha and not _sha_match(r.get("sha"), sha):
            continue
        if item and r.get("item") != item:
            continue
        if tool and r.get("tool") != tool:
            continue
        if not include_dirty and not counts_as_evidence(r):
            continue
        hits.append(r)
    return hits


def summarize(records) -> dict:
    """{tool: PASS|FAIL|UNMEASURED}: per tool, the latest record per covered-path set; FAIL beats UNMEASURED
    beats PASS across sets. A gate reads PASS only when every latest run of that tool passed."""
    latest = {}
    for r in sorted(records, key=lambda r: r.get("ts") or ""):
        latest[(r["tool"], tuple(r.get("paths") or ()))] = r["result"]
    out = {}
    for (tool, _), res in latest.items():
        prev = out.get(tool)
        out[tool] = res if prev is None else min(prev, res, key=("FAIL", "UNMEASURED", "PASS").index)
    return out


def _main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    lk = sub.add_parser("lookup", help="evidence for a sha and/or item")
    lk.add_argument("--sha")
    lk.add_argument("--item")
    lk.add_argument("--tool")
    lk.add_argument("--days", type=int, default=30)
    lk.add_argument("--all", action="store_true", help="include dirty-tree records (audit; never evidence)")
    sub.add_parser("where", help="print the evidence folder")
    a = ap.parse_args(argv)
    if a.cmd == "where":
        print(evidence_dir())
        return 0
    if not (a.sha or a.item):
        ap.error("lookup needs --sha or --item")
    hits = lookup(a.sha, a.item, a.tool, a.days, include_dirty=a.all)
    for r in hits:
        print("%s %-12s %-10s %s%s %s%s" % (r["ts"], r["tool"], r["result"], (r.get("sha") or "-")[:12],
                                            "" if r.get("dirty") is False else " DIRTY", ",".join(r["paths"][:4]),
                                            " (+%d)" % (len(r["paths"]) - 4) if len(r["paths"]) > 4 else ""))
    print("%d record(s); summary %s" % (len(hits), json.dumps(summarize(hits), sort_keys=True)))
    return 0


if __name__ == "__main__":
    sys.exit(_main())
