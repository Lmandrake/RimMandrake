#!/usr/bin/env python3
"""selftest_rotate.py — art-ledger rotation is a pure move and the fold cannot tell.

On a COPY of the real events/ dir (never the live one): rotate BENCH by date and then again by
size, and prove (1) concat(archives, live tail) == the original bytes, (2) read_events() and the
folded Index are identical before and after, (3) art_guard's git reader (ledger_at) folds a
rotated commit identically to the unrotated one, (4) an archive is never rewritten, and (5) a clone
still holding the old full shard that appends and union-merges lands exactly tail + new lines.
Planted defects, each of which MUST be caught: the pre-rotation reader (glob *.jsonl only) loses
the archives; a tail-before-archive order changes the fold; an append between plan and apply is
refused; a stray file under archive/ is refused, not skipped.

    python3 selftest_rotate.py [--events DIR]    default: the repo's infrastructure/state/art/events
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
FAILS = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def fold_digest(L, events=None) -> str:
    """sha256 of the folded Index's state (every projection the CLI reads)."""
    idx = L.Index(events)

    def canon(o):
        if isinstance(o, dict):
            return sorted(([json.dumps(k, default=str), canon(v)] for k, v in o.items()))
        if isinstance(o, (list, tuple)):
            return [canon(x) for x in o]
        if isinstance(o, set):
            return sorted(json.dumps(x, default=str) for x in o)
        return o
    state = {k: canon(v) for k, v in vars(idx).items()}
    return hashlib.sha256(json.dumps(state, sort_keys=True, default=str).encode()).hexdigest()


def git(cwd, *a):
    return subprocess.run(["git", *a], cwd=cwd, check=True, capture_output=True, text=True).stdout


def main(argv):
    src = Path(argv[argv.index("--events") + 1]) if "--events" in argv else \
        HERE.parents[3] / "infrastructure" / "state" / "art" / "events"
    tmp = Path(tempfile.mkdtemp(prefix="artrotate-selftest-"))
    try:
        return run(src, tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def run(src: Path, tmp: Path) -> int:
    led = tmp / "repo" / "infrastructure" / "state" / "art"
    ev = led / "events"
    ev.mkdir(parents=True)
    for f in src.glob("*.jsonl"):
        shutil.copy2(f, ev / f.name)
    if (src / "archive").is_dir():
        shutil.copytree(src / "archive", ev / "archive")
    os.environ["ART_LEDGER_DIR"] = str(led)
    import artledger as L
    import art_guard as G
    # Self-contained by construction: L.REPO_ROOT is untouched; ledger_dir() follows the env.
    check(L.ledger_dir() == led, f"fixture ledger dir in use ({L.ledger_dir()})")
    seat = "BENCH" if (ev / "BENCH.jsonl").exists() else sorted(p.stem for p in ev.glob("*.jsonl"))[0]
    live = ev / f"{seat}.jsonl"
    orig = live.read_bytes()
    check(len(orig) > 0, f"sanity probe: {seat}.jsonl has bytes ({len(orig):,})")
    before_events = L.read_events()
    before_fold = fold_digest(L)
    check(len(before_events) > 100, f"sanity probe: fold sees events ({len(before_events):,})")

    repo = tmp / "repo"
    git(repo, "init", "-q", "-b", "main")
    git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "add", "infrastructure")
    git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "orig")
    rev0 = git(repo, "rev-parse", "HEAD").strip()

    # 1. rotate by date: everything older than the newest day moves
    lines = orig.splitlines(keepends=True)
    days = sorted({json.loads(x).get("ts", "")[:10] for x in lines if x.strip()})
    cutoff = days[-1] if len(days) > 1 else "9999"
    plan = L.rotate_plan(seat, before=cutoff)
    check(plan["pure_move"], "date plan: concat(archives)+tail == original bytes")
    check(plan["moved_lines"] > 0, f"date plan moves something ({plan['moved_lines']:,} lines)")
    check(all(len(a["bytes"]) <= L.ROTATE_MAX_CHUNK for a in plan["archives"]), "every archive <= max chunk")
    written = L.rotate_apply(plan)
    arch1 = {p.name: p.read_bytes() for p in (ev / "archive").glob(f"{seat}.*.jsonl")}
    cat = b"".join(arch1[n] for n in sorted(arch1)) + live.read_bytes()
    check(cat == orig, "after apply: archives + live tail are byte-identical to the original")
    check(L.read_events() == before_events, "read_events() identical after date rotation")
    check(fold_digest(L) == before_fold, "folded Index identical after date rotation")
    check(len(live.read_bytes()) < len(orig), f"live shard shrank {len(orig):,} -> {len(live.read_bytes()):,} B")

    git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "add", "infrastructure")
    git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "rotate")
    rev1 = git(repo, "rev-parse", "HEAD").strip()
    check(G.ledger_at(repo, rev1) == G.ledger_at(repo, rev0) == before_events,
          "art_guard.ledger_at folds the rotated commit identically (git reader)")

    # 2. rotate again by size: a NEW archive seq; the first archives are untouched
    plan2 = L.rotate_plan(seat, keep_bytes=4096)
    check(plan2["pure_move"], "size plan is a pure move")
    if plan2["archives"]:
        L.rotate_apply(plan2)
        check(all((ev / "archive" / n).read_bytes() == b for n, b in arch1.items()),
              "earlier archives byte-unchanged by a second rotation (write-once)")
        check(any(".0002." in a["name"] or int(a["name"].split(".")[1]) > len(arch1) for a in plan2["archives"]),
              "second rotation takes the next seq")
    check(sum(1 for x in live.read_bytes().splitlines() if x.strip()) >= min(L.ROTATE_MIN_TAIL_LINES, len(lines)),
          f"live tail keeps >= {L.ROTATE_MIN_TAIL_LINES} lines (union-merge context)")
    check(L.read_events() == before_events and fold_digest(L) == before_fold, "fold identical after size rotation")

    # 3. a clone still on the old full shard appends and union-merges onto the rotated tail
    new = b'{"id":"zz_selftest_new","type":"probe","ts":"9999-01-01T00:00:00-0700"}\n'
    (tmp / "base").write_bytes(orig)
    (tmp / "theirs").write_bytes(orig + new)
    (tmp / "ours").write_bytes(live.read_bytes())
    subprocess.run(["git", "merge-file", "--union", str(tmp / "ours"), str(tmp / "base"), str(tmp / "theirs")],
                   capture_output=True)
    check((tmp / "ours").read_bytes() == live.read_bytes() + new,
          "union merge of an old-clone append onto the rotated tail == tail + new line (no resurrected prefix)")

    # ── planted defects: each must be caught ──
    old_reader = []
    seen = set()
    for f in sorted(ev.glob("*.jsonl")):
        for ln in f.read_text().splitlines():
            if ln.strip():
                e = json.loads(ln)
                if e.get("id") not in seen:
                    seen.add(e.get("id")); old_reader.append(e)
    check(old_reader != before_events, "PLANTED: the pre-rotation glob reader loses archived events (detected)")
    names = L.shard_files(ev)
    swapped = [p for p in names if p.parent.name != "archive"] + [p for p in names if p.parent.name == "archive"]
    wrong = []
    seen = set()
    for f in swapped:
        for ln in f.read_text().splitlines():
            if ln.strip():
                e = json.loads(ln)
                if e.get("id") not in seen:
                    seen.add(e.get("id")); wrong.append(e)
    check(wrong != before_events, "PLANTED: tail-before-archive order changes the fold (detected)")
    with open(live, "ab") as fh:   # give the planted plan something to move
        for i in range(2 * L.ROTATE_MIN_TAIL_LINES):
            fh.write(b'{"id":"zz_fill_%d","type":"probe","ts":"9999-01-01T00:00:00-0700"}\n' % i)
    p3 = L.rotate_plan(seat, keep_bytes=0)
    check(bool(p3["archives"]), "planted plan has something to move")
    with open(live, "ab") as fh:
        fh.write(new)
    try:
        L.rotate_apply(p3)
        refused = False
    except SystemExit:
        refused = True
    check(refused, "PLANTED: an append between plan and apply is refused")
    stray = ev / "archive" / "notes.jsonl"
    stray.write_text("")
    try:
        L.shard_files(ev)
        refused = False
    except ValueError:
        refused = True
    check(refused, "PLANTED: a stray file under archive/ is refused, never silently skipped")
    stray.unlink()

    print(f"\n{'FAIL' if FAILS else 'OK'}: {len(FAILS)} failure(s)")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
