#!/usr/bin/env python3
"""signin_health: is the one Codex sign-in alive? (no network, no launch, no token ever printed)

One sign-in folder serves every question, picture and agent run (Dispatch, design/specs/2026-11-23-one-codex-door). Its
verdict, from the folder and from the door's own call log of the last days:
  live         a sign-in is there, and the last call that could tell did not fail on it
  no_signin    the folder holds no auth.json
  unreadable   auth.json does not parse
  auth_failed  the last call that could tell ended AUTH (the server refused this login)

    python3 src/RimMandrake/Utils/artpipe/signin_health.py [--home DIR] [--log DIR]
        exit 0 live, 1 bad, 2 could not look
Page: design/specs/2026-11-24-art-daemon-over-the-one-door/boundary.md.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dispatch_door  # noqa: E402

BAD = ("no_signin", "unreadable", "auth_failed")
LOG_DAYS = 3        # how far back the last telling call is looked for; older than that says nothing about now
# A call that reached the server on this login, whatever it then said.
TELLING = ("ANSWERED", "AUTH", "MODEL_REFUSED", "NO_IMAGE", "FOREIGN_IMAGE", "BAD_IMAGE", "ALLOWANCE")


def last_telling(log_dir: Path, home: Path, now: float | None = None) -> dict | None:
    """The newest log record of a call on `home` that says whether the login works; None when there is none. Raises
    OSError when the log folder cannot be read."""
    now = time.time() if now is None else now
    days = sorted((d for d in Path(log_dir).iterdir() if d.is_dir()), key=lambda d: d.name, reverse=True)
    oldest = time.strftime("%Y-%m-%d", time.gmtime(now - LOG_DAYS * 86400))
    for d in days:
        if d.name < oldest:
            break
        best = None
        for p in d.glob("*.json"):
            try:
                r = json.loads(p.read_text(encoding="utf-8"))
            except ValueError:
                continue                # a torn record says nothing
            if isinstance(r, dict) and r.get("outcome") in TELLING and r.get("kind") != "could_not_start" \
                    and str(r.get("home")) == str(home) and (best is None or r.get("t", 0) > best.get("t", 0)):
                best = r
        if best:
            return best
    return None


def check(home: Path, log_dir: Path) -> tuple[str, dict]:
    """(verdict, facts). Raises OSError when the log cannot be read: a caller must not read that as live."""
    f = Path(home) / "auth.json"
    if not f.is_file():
        return "no_signin", {}
    try:
        tok = (json.loads(f.read_text()).get("tokens") or {}).get("refresh_token")
    except (ValueError, AttributeError):
        tok = None
    if not isinstance(tok, str) or not tok:
        return "unreadable", {}
    r = last_telling(Path(log_dir), Path(home))
    facts = {"last": r["outcome"], "last_t": r.get("t")} if r else {}
    if r and r["outcome"] == "AUTH" and f.stat().st_mtime <= r.get("t", 0) + (r.get("secs") or 0):
        return "auth_failed", facts         # a newer auth.json is a renewed login: it has not failed yet
    return "live", facts


def defaults() -> tuple[Path, Path]:
    """(the one sign-in folder, the door's log folder). Raises by name when the door is absent or has no log."""
    door = dispatch_door.load()
    d = door.log_dir()
    if d is None:
        raise OSError("the Codex door has no log folder: set GPT_DOOR_LOG_DIR")
    return Path(door.default_home("linux")), Path(d)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--home", type=Path)
    ap.add_argument("--log", type=Path)
    a = ap.parse_args(argv)
    try:
        h, d = (a.home, a.log) if a.home and a.log else defaults()
        v, facts = check(a.home or h, a.log or d)
    except Exception as e:  # noqa: BLE001
        print("UNMEASURED: could not read the sign-in: %s: %s" % (type(e).__name__, e))
        return 2
    print("%s %s %s" % (a.home or h, v, json.dumps(facts)))
    if v in BAD:
        print("renew: python3 %s renew" % (dispatch_door.BIN / "gpt_door.py"))
    return 1 if v in BAD else 0


if __name__ == "__main__":
    sys.exit(main())
