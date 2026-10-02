#!/usr/bin/env python3
"""ledger_lint.py — the second permanent invariant of the union-merged ledger.

Git plan §2.5 (`design/RimMandrake/git_workflow_plan_2026-10-01.md`): the per-seat shards
`infrastructure/state/ledger/events/<SEAT>.jsonl` (and, since Phase 5, the code-review records
`infrastructure/state/code_review/<SEAT>.jsonl`) merge with `merge=union`. Union never
conflicts, which is the point, and also means git will never stop a bad shard from
landing. So this lint does, refusing:

  MALFORMED      a line that is not a JSON object (a torn write; repair with
                 repair_torn_ledger.py, never by hand)
  NO_NEWLINE     a non-empty shard whose last byte is not "\\n" — the next union or
                 append would glue two events into one unparsable line
  NOT_APPEND     a line present on the base (origin/main) that is gone from the
                 checked revision: an edit or deletion in place. Union would keep BOTH
                 the old and the new line on the next merge, so an edit never sticks
  DUP_DIFFERENT  a NEW line (not on the base) with the same event identity —
                 (seat, verb, subject, ts) — as a line ALREADY ON THE BASE but different
                 content. That is the shape an edit-in-place leaves after a union: the
                 landed original plus its altered twin. Two new same-second events are
                 NOT flagged — the owner writes same-second note pairs legitimately
                 (OWNER.jsonl, 2026-10-01/02), and `event` carries no unique id.
  FROZEN         any change at all to the frozen pre-shard `events.jsonl`

Identical duplicate lines are NOT an error: union produces them and the reader
(`rimflow.model.canonical_order`) collapses them.

    python3 src/RimMandrake/Utils/ledger_lint.py               # worktree vs origin/main
    python3 src/RimMandrake/Utils/ledger_lint.py --rev HEAD    # a commit (the push guard)
    python3 src/RimMandrake/Utils/ledger_lint.py --base <ref>  # another base

Exit 0 clean, 1 findings, 2 could not run. With no base ref (no origin/main) the
append/frozen checks are skipped and SAID so — never reported as passed.
"""
import argparse
import collections
import json
import os
import subprocess
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SHARD_DIR = "infrastructure/state/ledger/events"
# Every append-only, union-merged shard directory. Phase 5 (2026-10-02) added the
# code-review records (`code_review_status.py`), which carry the same invariants.
SHARD_DIRS = (SHARD_DIR, "infrastructure/state/code_review")
FROZEN = "infrastructure/state/ledger/events.jsonl"


def _git(root, *args):
    return subprocess.run(["git", "-C", root, *args], capture_output=True)


def ref_exists(root, ref):
    return _git(root, "rev-parse", "--verify", "-q", ref + "^{commit}").returncode == 0


def blob_at(root, rev, path):
    """-> bytes of `path` at `rev`, or None if absent there."""
    r = _git(root, "show", "%s:%s" % (rev, path))
    return r.stdout if r.returncode == 0 else None


def shards_at(root, rev):
    """-> sorted shard paths at `rev` (None = worktree)."""
    out = []
    for sd in SHARD_DIRS:
        if rev is None:
            try:
                names = os.listdir(os.path.join(root, sd))
            except OSError:
                continue
            out += ["%s/%s" % (sd, n) for n in names if n.endswith(".jsonl")]
        else:
            r = _git(root, "ls-tree", "--name-only", rev, sd + "/")
            out += [p for p in r.stdout.decode().splitlines() if p.endswith(".jsonl")]
    return sorted(out)


def content(root, rev, path):
    if rev is None:
        try:
            with open(os.path.join(root, path), "rb") as fh:
                return fh.read()
        except OSError:
            return None
    return blob_at(root, rev, path)


def identity(ev):
    subj = ev.get("id") or ev.get("name") or ev.get("system") or ev.get("path") or ""
    return (ev.get("seat"), ev.get("event"), subj, ev.get("ts"))


def lint_blob(path, data, base_data=None):
    """-> [(code, path, line_no, detail)] for one shard. Pure; the selftest drives it."""
    out = []
    if not data:
        return out
    if not data.endswith(b"\n"):
        out.append(("NO_NEWLINE", path, data.count(b"\n") + 1,
                    "last line has no trailing newline"))
    lines = data.decode("utf-8", errors="replace").split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    base_lines = []
    if base_data:
        base_lines = base_data.decode("utf-8", errors="replace").split("\n")
        if base_lines and base_lines[-1] == "":
            base_lines.pop()
    base_ct = collections.Counter(l for l in base_lines if l.strip())
    have_ct = collections.Counter(l for l in lines if l.strip())
    for l, n in base_ct.items():
        if have_ct[l] < n:
            out.append(("NOT_APPEND", path, 0,
                        "line on the base is gone (edited or removed in place): %s"
                        % l[:160]))
    by_ident = collections.defaultdict(set)
    parsed = []
    for i, raw in enumerate(lines, 1):
        if not raw.strip():
            continue
        try:
            ev = json.loads(raw)
            if not isinstance(ev, dict):
                raise ValueError("not an object")
        except ValueError as e:
            out.append(("MALFORMED", path, i, "%s: %s" % (e, raw[:120])))
            continue
        canon = json.dumps(ev, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        by_ident[identity(ev)].add(canon)
        parsed.append((i, raw, ev, canon))
    remaining_base = collections.Counter(base_ct)
    base_idents = collections.defaultdict(set)
    for l in base_ct:
        try:
            bev = json.loads(l)
        except ValueError:
            continue
        if isinstance(bev, dict):
            base_idents[identity(bev)].add(
                json.dumps(bev, sort_keys=True, separators=(",", ":"), ensure_ascii=False))
    for i, raw, ev, canon in parsed:
        if remaining_base[raw] > 0:          # already on the base: not re-judged
            remaining_base[raw] -= 1
            continue
        if base_idents.get(identity(ev)) and canon not in base_idents[identity(ev)]:
            out.append(("DUP_DIFFERENT", path, i,
                        "same (seat, event, subject, ts) %r as another line with "
                        "different content — an in-place edit after a union merge? "
                        "Re-append a corrected event with a fresh ts instead"
                        % (identity(ev),)))
    return out


def lint(root=REPO_ROOT, rev=None, base="origin/main"):
    """-> (findings, notes). rev None = worktree."""
    notes = []
    have_base = bool(base) and ref_exists(root, base)
    if not have_base:
        notes.append("no base ref %r — NOT_APPEND/FROZEN checks UNMEASURED, structure only"
                     % base)
    findings = []
    for p in shards_at(root, rev):
        data = content(root, rev, p)
        base_data = blob_at(root, base, p) if have_base else None
        findings.extend(lint_blob(p, data, base_data))
    if have_base:
        a, b = content(root, rev, FROZEN), blob_at(root, base, FROZEN)
        if a != b:
            findings.append(("FROZEN", FROZEN, 0,
                             "the frozen pre-shard ledger changed; nothing may write it"))
    return findings, notes


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--rev", default=None, help="lint this commit instead of the worktree")
    ap.add_argument("--base", default="origin/main")
    ap.add_argument("--root", default=REPO_ROOT)
    a = ap.parse_args(argv)
    try:
        findings, notes = lint(a.root, a.rev, a.base)
    except Exception as e:                       # noqa: BLE001 — say so, exit 2
        print("ledger_lint: could not run: %s" % e)
        return 2
    for n in notes:
        print("note: " + n)
    for code, path, ln, detail in findings:
        print("%s %s:%s %s" % (code, path, ln, detail))
    print("ledger_lint: %d finding%s over %s vs %s"
          % (len(findings), "" if len(findings) == 1 else "s",
             a.rev or "worktree", a.base))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
