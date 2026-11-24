#!/usr/bin/env python3
"""windows_codex_archive.py: the old Windows Codex worker folders, moved aside for a week, and put back by one command.

    windows_codex_archive.py plan       what would move, and what stays and why (changes nothing)
    windows_codex_archive.py move       move each folder, one manifest row for each; run it again to carry on
    windows_codex_archive.py status     what is archived, and the calls of the retired Windows route since
    windows_codex_archive.py restore    put every archived folder back where it was
    windows_codex_archive.py probe --id ID --why W   declare one logged call as our own proof call (kept in the log)
    windows_codex_archive.py delete     delete the archive: only after the date, and only when no call was logged

Item RIMMANDRAKE_MOVE_ALL_CODEX_WORK_TO_WSL_ONE_DISPATCH_DOOR_ONE_LOGIN (owner, 2026-11-23: "somehow disabling the
windows one without deleting it yet ... so we can prove we don't need it reversibly for a week or so").
What stays: `.codex` and AppData\\Local\\OpenAI\\Codex belong to the ChatGPT desktop app, which starts at login. Without
them its next start would set up a new folder, and that raises the Windows consent dialog. WindowsApps and the sandbox
service need administrator rights.
Exit: 0 done; 1 something is left or refused (named); 2 could not look.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

NAME = "windows-codex-2026-11-24"
KEEP_DAYS = 7
# Folder names in the Windows profile that only the retired route used. `.codex` itself never matches.
TAKES = re.compile(r"^\.codex_(workers|arena_judge|arena_judge_benchprobe|bacta_\w+|consult|sandbox_seed(\..+)?|"
                   r"sandbox_backup_\w+)$")
STAYS = {".codex": "the ChatGPT desktop app's own folder; without it the app's next start raises the consent dialog"}
MOVE_LIMIT_S = 3 * 3600     # hang guard for one folder: the largest is about 76 GB, measured disks move that in under 1 h


def profile() -> Path:
    env = os.environ.get("WINDOWS_CODEX_PROFILE")
    if env:
        return Path(env)
    r = subprocess.run(["cmd.exe", "/c", "echo %USERPROFILE%"], capture_output=True, text=True, timeout=60, cwd="/mnt/c")
    w = r.stdout.strip()
    m = re.match(r"^([A-Za-z]):\\(.+)$", w)
    if not m:
        raise OSError("the Windows profile could not be read (%r)" % w)
    return Path("/mnt/%s/%s" % (m.group(1).lower(), m.group(2).replace("\\", "/")))


def archive() -> Path:
    env = os.environ.get("WINDOWS_CODEX_ARCHIVE")
    if env:
        return Path(env)
    r = subprocess.run([sys.executable, os.path.expanduser("~/dev/Lodestar/bin/lib/agent_storage.py")],
                       capture_output=True, text=True, timeout=60)
    if r.returncode or not r.stdout.strip():
        raise OSError("the agent storage root could not be read: %s" % r.stderr.strip())
    return Path(r.stdout.strip()) / "retired-trees" / NAME


def manifest(a: Path) -> dict:
    f = a / "MANIFEST.json"
    return json.loads(f.read_text()) if f.is_file() else {"started": None, "rows": {}}


def save(a: Path, m: dict) -> None:
    a.mkdir(parents=True, exist_ok=True)
    tmp = a / "MANIFEST.json.tmp"
    tmp.write_text(json.dumps(m, indent=1, sort_keys=True) + "\n")
    os.replace(tmp, a / "MANIFEST.json")


def todo(p: Path) -> list[Path]:
    return sorted(d for d in p.iterdir() if TAKES.match(d.name) and d.is_dir() and not d.is_symlink())


def _robo(src: Path, dst: Path) -> None:
    """Move a folder between drives with robocopy (native speed); a run that stopped carries on when run again."""
    def w(x):
        return subprocess.run(["wslpath", "-w", str(x)], capture_output=True, text=True, timeout=30, check=True).stdout.strip()
    dst.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(["timeout", str(MOVE_LIMIT_S), "/mnt/c/Windows/System32/Robocopy.exe", w(src), w(dst), "/E", "/MOVE",
                        "/XJ", "/R:1", "/W:1", "/MT:16", "/NFL", "/NDL", "/NP", "/NJH"], capture_output=True, text=True,
                       errors="replace", cwd="/mnt/c", timeout=MOVE_LIMIT_S + 60)
    if r.returncode >= 8 or r.returncode < 0:            # robocopy: 8 and over means files were not moved
        raise OSError("robocopy exit %s: %s" % (r.returncode, (r.stdout or r.stderr).strip()))


def _rename(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    os.rename(src, dst)


def mover(src: Path, dst: Path) -> None:
    if os.environ.get("WINDOWS_CODEX_PROFILE"):          # tests: one disk
        return _rename(src, dst)
    _robo(src, dst)


def empty(d: Path) -> bool:
    return not d.exists() or not any(x.is_file() or x.is_symlink() for x in d.rglob("*"))


def move(p: Path, a: Path, only=None, mv=None) -> int:
    m = manifest(a)
    m["started"] = m["started"] or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    bad = 0
    for d in todo(p):
        if only and d.name not in only:
            continue
        row = {"from": str(d), "to": str(a / d.name), "state": "MOVING", "t": time.time()}
        m["rows"][d.name] = row
        save(a, m)                                       # the row is on disk before the first file moves
        try:
            (mv or mover)(d, a / d.name)
            if not empty(d):
                raise OSError("files are left in %s" % d)
            if d.exists():
                _rmtree_empty(d)
            row["state"] = "MOVED"
        except (OSError, subprocess.SubprocessError) as e:
            bad += 1
            row.update(state="PARTIAL", why=str(e))
        row["secs"] = round(time.time() - row["t"], 1)
        save(a, m)
        print("%s %s (%.0fs)%s" % (row["state"], d.name, row["secs"], " " + row.get("why", "")), flush=True)
    return 1 if bad else 0


def _rmtree_empty(d: Path) -> None:
    """Remove a tree that holds no file. A file that appears meanwhile stops it (rmdir refuses)."""
    for x in sorted((x for x in d.rglob("*") if x.is_dir()), key=lambda x: -len(x.parts)):
        x.rmdir()
    d.rmdir()


def restore(a: Path, mv=None) -> int:
    m = manifest(a)
    bad = 0
    for name, row in sorted(m["rows"].items()):
        src, dst = Path(row["to"]), Path(row["from"])
        if not src.exists():
            continue
        if row["state"] == "MOVED" and dst.exists() and not empty(dst):
            bad += 1
            print("REFUSED %s: %s exists and holds files; look at it first" % (name, dst))
            continue
        if dst.exists() and empty(dst):
            _rmtree_empty(dst)
        try:
            (mv or mover)(src, dst)
            if src.exists() and empty(src):
                _rmtree_empty(src)
            row["state"] = "RESTORED"
            print("RESTORED %s" % name, flush=True)
        except (OSError, subprocess.SubprocessError) as e:
            bad += 1
            print("FAILED %s: %s" % (name, e))
        save(a, m)
    return 1 if bad else 0


def calls(a: Path, log_dir=None) -> tuple[int | None, list, str]:
    """(count, callers, why) of WINDOWS_RETIRED records since the move. count None: the log could not be read."""
    m = manifest(a)
    if not m["started"]:
        return None, [], "nothing is archived"
    since = time.mktime(time.strptime(m["started"], "%Y-%m-%dT%H:%M:%SZ")) - time.timezone
    try:
        if log_dir is None:
            import dispatch_door
            log_dir = dispatch_door.load().log_dir()
        days = [d for d in Path(log_dir).iterdir() if d.is_dir()]
    except Exception as e:  # noqa: BLE001
        return None, [], "%s: %s" % (type(e).__name__, e)
    seen, total, torn = [], 0, 0
    for d in days:
        for f in d.glob("*.json"):
            try:
                r = json.loads(f.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                torn += 1
                continue
            if r.get("t", 0) < since:
                continue
            total += 1
            if r.get("outcome") == "WINDOWS_RETIRED" and r.get("id") not in m.get("probes", {}):
                seen.append(str(r.get("caller")))
    if not total:
        return None, [], "the log holds no call at all since the move: the reader is blind, not the route quiet"
    return len(seen), seen, "%d calls read, %d torn records" % (total, torn)


def probe(a: Path, cid: str | None, why: str | None, log_dir=None) -> int:
    if not cid or not (why or "").strip():
        print("REFUSED: give --id and --why")
        return 1
    if log_dir is None:
        import dispatch_door
        log_dir = dispatch_door.load().log_dir()
    for f in Path(log_dir).glob("*/*.json"):
        try:
            r = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if r.get("id") == cid and r.get("outcome") == "WINDOWS_RETIRED":
            m = manifest(a)
            m.setdefault("probes", {})[cid] = why.strip()
            save(a, m)
            print("DECLARED %s" % cid)
            return 0
    print("REFUSED: no logged WINDOWS_RETIRED call has the id %s" % cid)
    return 1


def delete_refusal(a: Path, now: float | None = None, log_dir=None) -> str:
    """'' when the archive may be deleted, else why not."""
    m = manifest(a)
    if not m["started"]:
        return "nothing is archived at %s" % a
    t0 = time.mktime(time.strptime(m["started"], "%Y-%m-%dT%H:%M:%SZ")) - time.timezone
    left = t0 + KEEP_DAYS * 86400 - (time.time() if now is None else now)
    if left > 0:
        return "%.1f days of %d are left" % (left / 86400, KEEP_DAYS)
    n, who, why = calls(a, log_dir)
    if n is None:
        return "UNMEASURED: %s" % why
    return "%d call(s) of the retired route: %s" % (n, sorted(set(who))) if n else ""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("do", choices=("plan", "move", "status", "restore", "probe", "delete"))
    ap.add_argument("--id")
    ap.add_argument("--why")
    ap.add_argument("--only", action="append", help="move: just this folder name; repeat")
    x = ap.parse_args(argv)
    try:
        p, a = profile(), archive()
        if x.do == "plan":
            for d in todo(p):
                print("MOVE %s -> %s" % (d, a / d.name))
            for n, why in STAYS.items():
                print("STAY %s: %s" % (p / n, why))
            return 0
        if x.do == "move":
            return move(p, a, x.only)
        if x.do == "restore":
            return restore(a)
        if x.do == "probe":
            return probe(a, x.id, x.why)
        m = manifest(a)
        n, who, why = calls(a)
        for cid, w in sorted(m.get("probes", {}).items()):
            print("declared probe %s: %s" % (cid, w))
        print("archive %s: %s" % (a, {s: sum(r["state"] == s for r in m["rows"].values())
                                      for s in sorted({r["state"] for r in m["rows"].values()})}))
        print("calls of the retired route since %s: %s %s (%s)" % (m["started"], "UNMEASURED" if n is None else n,
                                                                  sorted(set(who)), why))
        no = delete_refusal(a)
        if x.do == "status":
            print("may be deleted: %s" % ("yes" if not no else "no, " + no))
            return 2 if n is None and m["started"] else 0
        if no:
            print("REFUSED: " + no)
            return 1
        import shutil
        shutil.rmtree(a)
        print("DELETED %s" % a)
        return 0
    except OSError as e:
        print("COULD NOT LOOK: %s" % e)
        return 2


if __name__ == "__main__":
    sys.exit(main())
