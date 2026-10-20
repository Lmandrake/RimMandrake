#!/usr/bin/env python3
"""saves_prune.py — report (and with --apply, prune) the Windows Saves folder down to what we keep.

Owner, 2026-10-18 (BUILDUP_BUILD_CLONES_STOP_BREEDING, Q4): *"We need only save canonical saves plus those
awaiting review… we don't need records of long-gone review saves or debugging saves past their
usefulness."* A Saves-folder backup lives only until the operation it guards is verified.

    saves_prune.py                 dry run: every save with its verdict and reason; changes nothing
    saves_prune.py --apply         delete the PRUNE rows (re-checked one by one just before each delete)
    saves_prune.py --json

Verdicts:
  KEEP   canonical       CANONICAL_ASHKARR_START_2026-09-12.rws and every CANONICAL_* save — never deleted,
                         never even offered (a backup of one is HOLD, deleted only by hand)
  KEEP   autosave        Autosave-N.rws — the game rotates them itself
  KEEP   awaiting        named in infrastructure/state/saves_awaiting_review.txt (one save name per line)
  KEEP   cited           its name appears in a live item, src/ (test fixtures such as RM_TestSite_*), design/,
                         infrastructure/state/*.md|canon.yml, or a Transient review page / keysheet /
                         decisions file — something still points at it
  HOLD   young           a debug save newer than --debug-hours (72), or a backup newer than --backup-hours (24)
  PRUNE  debug|backup    none of the above: a debugging save past its usefulness, or a backup whose
                         operation is long over

Also reported (never deleted by this tool): ~/.seat-tmp/*/saves_backup_* folder copies (PRUNE-able on the same
backup rule, listed separately) and the save_guard keeper store size.
"""
from __future__ import annotations

import sys as _rm_sys, pathlib as _rm_pl  # noqa: E401
_rm_sys.path.insert(0, str(_rm_pl.Path(__file__).resolve().parents[3] / "src" / "RimMandrake" / "Utils"))
from rmpaths import rm_path, rm_str, rm_win  # noqa: E402,F401  (data root: rmpaths.py)
import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CANONICAL = "CANONICAL_ASHKARR_START_2026-09-12.rws"
AWAITING = ROOT / "infrastructure" / "state" / "saves_awaiting_review.txt"
AUTOSAVE = re.compile(r"^Autosave-\d+\.rws$", re.I)
BACKUP = re.compile(r"(\.bak|bak-pre|\.before[_-]|before_|_backup|\.prev|\.orig|pre_?edit|\.old$)", re.I)
KEEPER_STORE = Path(rm_str("scratch", "save_keepers"))
TEXT_EXT = {".md", ".html", ".json", ".txt", ".yml", ".yaml", ".py", ".xml", ".csv"}


def saves_dir() -> Path:
    v = os.environ.get("SAVES_PRUNE_DIR")
    if v:
        return Path(v)
    sys.path.insert(0, str(HERE))
    from game_paths import SAVES
    return Path(SAVES)


def stem(name: str) -> str:
    """The save's identity: name without .rws and without a trailing backup suffix."""
    s = name
    i = s.lower().find(".rws")
    return s[:i] if i > 0 else s


def awaiting() -> set[str]:
    try:
        lines = AWAITING.read_text(encoding="utf-8").splitlines()
    except OSError:
        return set()
    return {stem(ln.split("#", 1)[0].strip()) for ln in lines if ln.split("#", 1)[0].strip()}


def cited_by(stems: list[str]) -> dict[str, str]:
    """stem -> where it is named (word-bounded: RM_x does not match RM_x2). Places whose mention means a
    save is still pointed at: live items, infrastructure/state/*.md + canon.yml, tracked src/ and design/
    (test fixtures such as RM_TestSite_*), and Transient review pages / keysheets / decisions files.
    grep -F does the multi-pattern search in C; a Python regex alternation took 100 s."""
    todo = sorted({s for s in stems if len(s) >= 6})
    hits: dict[str, str] = {}
    if not todo:
        return hits
    pat = "\n".join(todo) + "\n"
    st = ROOT / "infrastructure" / "state"
    runs = [
        (["git", "-C", str(ROOT), "grep", "-I", "-F", "-w", "-o", "-f", "-", "--", "src", "design"], "src/ or design/"),
        (["grep", "-r", "-I", "-F", "-w", "-o", "-h", "-f", "-", "--include=*.md", "--include=canon.yml",
          str(st / "items"), *glob.glob(str(st / "*.md")), str(st / "canon.yml")], "a live item or state doc"),
        (["grep", "-r", "-I", "-F", "-w", "-o", "-h", "-f", "-", "--include=*.md", "--include=*.html",
          "--include=*.json", "--exclude-dir=img", "--exclude-dir=.gatecheck_*", str(ROOT / "Transient")],
         "a Transient review page"),
    ]
    for cmd, where in runs:
        r = subprocess.run(cmd, input=pat, capture_output=True, text=True)
        for ln in r.stdout.splitlines():
            m = ln.rsplit(":", 1)[-1] if cmd[0] == "git" else ln
            if m in todo:
                hits.setdefault(m, where)
    return hits


def classify(name: str, mtime: float, now: float, aw: set[str], cites: dict[str, str], a) -> tuple[str, str]:
    s = stem(name)
    is_backup = bool(BACKUP.search(name[len(s):] if name.lower().endswith(".rws") else name)) \
        or not name.lower().endswith(".rws") or bool(BACKUP.search(s))
    if name == CANONICAL or (s.startswith("CANONICAL_") and not is_backup):
        return "KEEP", "canonical"
    if s.startswith("CANONICAL_"):
        return "HOLD", "backup of a canonical save — delete only by hand, after checking the live file"
    if AUTOSAVE.match(name):
        return "KEEP", "autosave (the game rotates these)"
    base = re.sub(r"(\.bak.*|bak-pre.*|[._-]before[_-].*|_backup.*)$", "", s, flags=re.I)
    for k in (s, base):
        if k in aw:
            return "KEEP", "awaiting review (saves_awaiting_review.txt)"
    for k in (s, base):
        if k in cites:
            return "KEEP", "cited by %s" % cites[k]
    age_h = (now - mtime) / 3600
    limit = a.backup_hours if is_backup else a.debug_hours
    if age_h < limit:
        return "HOLD", "young (%.0f h < %d h)" % (age_h, limit)
    return "PRUNE", ("backup" if is_backup else "debug") + " %.1f d old, cited nowhere" % (age_h / 24)


def human(n: float) -> str:
    for u in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return "%.0f %s" % (n, u)
        n /= 1024
    return "%.1f TB" % n


def dir_size(p: str) -> int:
    t = 0
    for dp, _, fns in os.walk(p):
        for fn in fns:
            try:
                t += os.lstat(os.path.join(dp, fn)).st_size
            except OSError:
                pass
    return t


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--apply", action="store_true", help="delete the PRUNE rows in the Saves folder")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--debug-hours", type=int, default=72)
    ap.add_argument("--backup-hours", type=int, default=24)
    a = ap.parse_args(argv)
    sd = saves_dir()
    if not sd.is_dir():
        print("UNMEASURED: Saves folder not reachable: %s" % sd)
        return 2
    now = time.time()
    entries = []
    for e in os.scandir(sd):
        if e.is_file(follow_symlinks=False):
            st = e.stat()
            entries.append((e.name, st.st_mtime, st.st_size))
    stems = [stem(n) for n, _, _ in entries]
    stems += [re.sub(r"(\.bak.*|bak-pre.*|[._-]before[_-].*|_backup.*)$", "", s, flags=re.I) for s in stems]
    aw = awaiting()
    cites = cited_by(stems)
    rows = []
    for n, mt, sz in sorted(entries):
        v, why = classify(n, mt, now, aw, cites, a)
        rows.append({"name": n, "verdict": v, "why": why, "bytes": sz, "age_d": round((now - mt) / 86400, 1)})
    if CANONICAL not in {r["name"] for r in rows}:
        print("WARNING: the canonical start save %s is NOT in %s" % (CANONICAL, sd))
    freed = 0
    if a.apply:
        for r in rows:
            if r["verdict"] != "PRUNE" or r["name"] == CANONICAL or r["name"].startswith("CANONICAL_"):
                continue
            p = sd / r["name"]
            v, why = classify(r["name"], p.stat().st_mtime, time.time(), awaiting(), cites, a)
            if v != "PRUNE":
                r.update(verdict=v, why="changed since the scan: " + why)
                continue
            p.unlink()
            r["verdict"] = "PRUNED"
            freed += r["bytes"]
    seat_backups = []
    for p in sorted(glob.glob(str(Path.home() / ".seat-tmp" / "*" / "saves_backup*"))):
        age_h = (now - os.path.getmtime(p)) / 3600
        seat_backups.append({"path": p, "bytes": dir_size(p), "age_d": round(age_h / 24, 1),
                             "verdict": "PRUNE-able (by hand)" if age_h >= a.backup_hours else "HOLD young"})
    if a.json:
        print(json.dumps({"saves": rows, "seat_backups": seat_backups}, indent=1))
        return 0
    order = {"PRUNED": 0, "PRUNE": 1, "HOLD": 2, "KEEP": 3}
    for r in sorted(rows, key=lambda r: (order[r["verdict"]], r["name"])):
        print("%-6s %9s %6.1fd  %s  — %s" % (r["verdict"], human(r["bytes"]), r["age_d"], r["name"], r["why"]))
    for b in seat_backups:
        print("SEAT   %9s %6.1fd  %s  — %s" % (human(b["bytes"]), b["age_d"], b["path"], b["verdict"]))
    if KEEPER_STORE.is_dir():
        print("STORE  %9s          %s  — save_guard keeper store (not this tool's)" % (human(dir_size(str(KEEPER_STORE))), KEEPER_STORE))
    tot = {v: [r for r in rows if r["verdict"] == v] for v in order}
    print("\n%d saves: %s; %s %s%s" % (
        len(rows), ", ".join("%s %d" % (v, len(x)) for v, x in tot.items() if x),
        "freed" if a.apply else "would free",
        human(freed if a.apply else sum(r["bytes"] for r in tot["PRUNE"])),
        "" if a.apply else "  (dry run — --apply deletes the PRUNE rows; add a name to "
                            "infrastructure/state/saves_awaiting_review.txt to keep it)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
