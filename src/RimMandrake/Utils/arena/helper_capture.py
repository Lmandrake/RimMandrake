#!/usr/bin/env python3
"""helper_capture.py - keep an arm TESTER's spend where the meter (arena_spend.py) reads it, attributed to the arm.

A tester (ralph_a/ralph_c/v3 tester, trio critic) runs in a fresh private root that the loop deletes afterwards, with
HOME inside it: its Claude transcripts and its GPT call log (RM_GPT_CALL_LOG=<root>/gpt/) die with the root. Before
the delete, the loop calls capture(rec, home=..., gpt_dir=...) with the test_start record it emitted; this copies

    <home>/.claude/projects/**/*.jsonl  ->  <base>/<arm>/<key>/claude/<same relative path>
    <gpt_dir>/*.jsonl                   ->  <base>/<arm>/<key>/gpt/<name>

and writes <base>/<arm>/<key>/manifest.json LAST (the dir is built under a temp name and renamed into place), where
<base> = $ARENA_METER_HELPERS or <arena root>/meter_helpers (a non-kept arena child: arm_sandbox masks it from arms)
and <key> = sha256 of the test_start record's (arm, run_id, task, ts, tester). arena_spend.meter() looks a manifest up
for EVERY model test_start in its window and BLOCKS (the analysis reads UNMEASURED) when it is missing, lists skipped
files, or holds no Claude transcript: a tester whose spend the meter cannot see never lets an arm win on it.

Copies never follow a symlink (a tester could plant one to a foreign transcript, or swap one in while the copy
runs): the walk goes through directory fds from the tester root down (O_NOFOLLOW at every component, os.fwalk), and a
symlinked home, .claude, projects, subdir or file is recorded under "skipped" (blocking), as is a file over MAX_FILE bytes. The copy is attributed to the arm
by the CAPTURE's location, never by the transcript's slug or the GPT record's own "arm" field.
Residual: the tester owns its root while it runs, so it can delete or shrink its own transcripts (undercount).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import stat
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

SCHEMA = "arena_helper_capture/1"
MAX_FILE = 64 << 20
ARM_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}")


def root() -> Path:
    env = os.environ.get("ARENA_METER_HELPERS", "").strip()
    if env:
        return Path(env)
    import arena_replay as R
    return R.arena_root() / "meter_helpers"


def ident(rec: dict) -> dict:
    """The fields of a test_start record that name one tester execution."""
    det = rec.get("detail") if isinstance(rec.get("detail"), dict) else {}
    return {"arm": rec.get("arm"), "run_id": rec.get("run_id"), "task": rec.get("task"), "ts": rec.get("ts"),
            "tester": det.get("tester")}


def key(rec: dict) -> str:
    return hashlib.sha256(json.dumps(ident(rec), sort_keys=True).encode()).hexdigest()[:32]


def cdir(rec: dict, base=None) -> Path:
    arm = rec.get("arm")
    if not isinstance(arm, str) or not ARM_NAME.fullmatch(arm) or arm.endswith("."):
        raise ValueError("bad arm name %r" % (arm,))
    return Path(base or root()) / arm / key(rec)


def _open_dir(anchor: Path, below: tuple, skipped: list, rel_base: str):
    """An O_DIRECTORY|O_NOFOLLOW fd for anchor/below..., opened one component at a time from the anchor (the
    harness-created tester root, resolved once; the tester cannot replace it): every component BELOW it must be a
    real directory, never a symlink -> fd or None (absent, or recorded as skipped)."""
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    parts = (os.path.realpath(anchor),) + tuple(below)
    try:
        fd = os.open(parts[0], os.O_RDONLY | os.O_DIRECTORY)
    except FileNotFoundError:
        return None
    try:
        for i, comp in enumerate(parts[1:], 1):
            try:
                nfd = os.open(comp, flags, dir_fd=fd)
            except FileNotFoundError:
                return None
            except OSError as e:
                skipped.append("%s: %s is not a plain directory (%s)" % (rel_base, os.path.join(*parts[:i + 1]),
                                                                         e.strerror or e))
                return None
            os.close(fd)
            fd = nfd
        out, fd = fd, None
        return out
    finally:
        if fd is not None:
            os.close(fd)


def _copy_tree(anchor: Path, below: tuple, dst: Path, rel_base: str, skipped: list, copied: list, flat=False):
    """Copy *.jsonl under src to dst through directory fds (os.fwalk, follow_symlinks=False; every file opened
    O_NOFOLLOW relative to its directory's fd), so a symlink planted or swapped in anywhere on the path, before or
    during the copy, is never followed; symlinks/unreadable dirs/oversize/non-regular files are recorded as skipped."""
    top = _open_dir(anchor, below, skipped, rel_base)
    if top is None:
        return

    def walk_err(e):                     # an unreadable subdirectory would otherwise vanish from the copy silently
        skipped.append("%s: unreadable (%s)" % (os.path.join(rel_base, str(e.filename or "?")), e.strerror or e))
    try:
        for dp, dns, fns, dfd in os.fwalk(".", dir_fd=top, follow_symlinks=False, onerror=walk_err):
            for d in list(dns):
                if stat.S_ISLNK(os.lstat(d, dir_fd=dfd).st_mode):
                    skipped.append("%s: symlinked dir" % os.path.normpath(os.path.join(rel_base, dp, d)))
                    dns.remove(d)
            if flat:
                dns[:] = []
            for f in fns:
                if not f.endswith(".jsonl"):
                    continue
                rel = os.path.normpath(os.path.join(dp, f))
                try:
                    fd = os.open(f, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=dfd)
                except OSError as e:
                    skipped.append("%s: %s" % (os.path.join(rel_base, rel), e.strerror or e))
                    continue
                with os.fdopen(fd, "rb") as fh:
                    fst = os.fstat(fh.fileno())
                    if not stat.S_ISREG(fst.st_mode) or fst.st_size > MAX_FILE:
                        skipped.append("%s: not a regular file or over %d bytes" % (os.path.join(rel_base, rel),
                                                                                    MAX_FILE))
                        continue
                    data = fh.read(MAX_FILE + 1)
                if len(data) > MAX_FILE:
                    skipped.append("%s: grew over %d bytes" % (os.path.join(rel_base, rel), MAX_FILE))
                    continue
                out = dst / rel
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_bytes(data)
                copied.append(rel)
    finally:
        os.close(top)


def capture(rec: dict, *, home, gpt_dir=None, rc=None, base=None) -> Path:
    """Copy one finished tester's transcripts + GPT records next to a manifest. Returns the capture dir.
    A capture for the same record is replaced (never merged)."""
    final = cdir(rec, base)
    final.parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix=".cap-", dir=str(final.parent)))
    skipped, claude, gpt = [], [], []
    home = Path(home)
    _copy_tree(home.parent, (home.name, ".claude", "projects"), tmp / "claude", "projects", skipped, claude)
    (tmp / "claude").mkdir(exist_ok=True)
    (tmp / "gpt").mkdir(exist_ok=True)
    if gpt_dir is not None:
        _copy_tree(Path(gpt_dir).parent, (Path(gpt_dir).name,), tmp / "gpt", "gpt", skipped, gpt, flat=True)
    man = dict(ident(rec), schema=SCHEMA, rc=rc, claude_files=sorted(claude), gpt_files=sorted(gpt),
               skipped=skipped)
    (tmp / "manifest.json").write_text(json.dumps(man, indent=1, sort_keys=True) + "\n")
    if final.exists():
        shutil.rmtree(final)
    os.rename(tmp, final)
    return final


def load(rec: dict, base=None):
    """-> (manifest dict, capture dir) or (None, reason)."""
    try:
        d = cdir(rec, base)
    except ValueError as e:
        return None, str(e)
    mp = d / "manifest.json"
    if d.is_symlink() or mp.is_symlink():
        return None, "capture %s is a symlink" % d
    try:
        man = json.loads(mp.read_text())
    except FileNotFoundError:
        return None, "no capture at %s" % d
    except (OSError, ValueError) as e:
        return None, "unreadable capture manifest %s: %s" % (mp, e)
    if not isinstance(man, dict) or man.get("schema") != SCHEMA or \
            any(man.get(k) != v for k, v in ident(rec).items()):
        return None, "capture manifest %s does not match its test_start" % mp
    return man, d
