#!/usr/bin/env python3
"""signin_health: is each art worker's Codex sign-in its own, and alive? (no network, no token ever printed)

Each art worker home (`<root>/w<N>`, default ~/.codex_workers/artpipe) holds its OWN ChatGPT sign-in. OpenAI: "Use
one auth.json per runner or per serialized workflow stream. Do not share the same file across concurrent jobs"
(developers.openai.com/codex/auth/ci-cd-auth, read 2026-11-22). Refresh tokens rotate: two homes that hold copies of
one lineage cannot both refresh, and the second gets "refresh token was already used". That killed all five worker
homes on 2026-11-20 (60 of 60 jobs failed); the owner signed each in by device on 2026-11-21. Nothing copies a
sign-in between homes now; this module says when a home's sign-in is gone, shared or dead.

A home's verdict, from a read of its auth.json and its `.artpipe_signin.json` (written by the daemon after each job):
  live         its own lineage, and its last job did not fail on sign-in (or it has run no job on this lineage)
  no_signin    the folder exists (a leased slot) and holds no auth.json: a job there fails at once
  unreadable   auth.json does not parse or has no refresh token
  shared       its refresh token is also in another worker home or the base home (~/.codex, the GPT consults'):
               the two race each other's refresh, and one dies
  auth_failed  the daemon's last job on this exact lineage failed on sign-in (Codex's own refresh-token wording)
A device sign-in gives a new lineage, so it clears auth_failed by itself.

    python3 src/RimMandrake/Utils/artpipe/signin_health.py [--root DIR] [--base DIR]   one line per home; exit 0 all
                                                                                       live, 1 one or more bad, 2
                                                                                       could not look
Page: design/specs/2026-11-22-art-worker-own-signin/boundary.md.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path

OUTCOME_FILE = ".artpipe_signin.json"
HOME_RX = re.compile(r"^w\d+$")
BAD = ("no_signin", "unreadable", "shared", "auth_failed")


def lineage(home: Path) -> str | None:
    """A short digest of `home`'s refresh token: the lineage's name. None when there is no auth.json, it does not
    parse, or it has no refresh token. The token itself never leaves this function."""
    try:
        data = json.loads((Path(home) / "auth.json").read_text())
    except (OSError, ValueError):
        return None
    tok = ((data.get("tokens") or {}) if isinstance(data, dict) else {}).get("refresh_token")
    if not isinstance(tok, str) or not tok:
        return None
    return hashlib.sha256(tok.encode()).hexdigest()[:16]


def record_outcome(home: Path, auth_failed: bool, job_id: str = "", now: float | None = None) -> None:
    """The daemon's note after one codex job on `home`: did it fail on sign-in, on which lineage. Best effort: a
    write that fails costs this record only, never the job."""
    rec = {"ts": time.time() if now is None else now, "auth_failed": bool(auth_failed),
           "lineage": lineage(home), "job": str(job_id)}
    try:
        tmp = Path(home) / (OUTCOME_FILE + ".tmp")
        tmp.write_text(json.dumps(rec))
        os.replace(tmp, Path(home) / OUTCOME_FILE)
    except OSError:
        pass


def _outcome(home: Path) -> dict | None:
    try:
        d = json.loads((Path(home) / OUTCOME_FILE).read_text())
        return d if isinstance(d, dict) else None
    except (OSError, ValueError):
        return None


def worker_homes(root: Path) -> list[Path]:
    """The provisioned worker homes under `root` (folders named w<N>), in slot order. Raises OSError when `root`
    cannot be listed: a caller must not read that as "no homes"."""
    root = Path(root)
    if not root.is_dir():
        raise OSError("no worker-home root %s" % root)
    homes = [p for p in root.iterdir() if p.is_dir() and HOME_RX.match(p.name)]
    return sorted(homes, key=lambda p: int(p.name[1:]))


def check(root: Path, base: Path | None = None) -> dict:
    """{home name: verdict} for every worker home under `root` (see the module text). `base` is the shared home whose
    lineage no worker may hold. Raises OSError when `root` cannot be read."""
    homes = worker_homes(root)
    lin = {h.name: lineage(h) for h in homes}
    base_lin = lineage(base) if base is not None else None
    seen: dict = {}
    for name, l in lin.items():
        if l is not None:
            seen.setdefault(l, []).append(name)
    out = {}
    for h in homes:
        l = lin[h.name]
        if not (h / "auth.json").is_file():
            out[h.name] = "no_signin"
        elif l is None:
            out[h.name] = "unreadable"
        elif len(seen[l]) > 1 or l == base_lin:
            out[h.name] = "shared"
        else:
            rec = _outcome(h)
            out[h.name] = ("auth_failed" if rec and rec.get("auth_failed") and rec.get("lineage") == l else "live")
    return out


def default_root() -> Path:
    """The daemon's own default worker-home root (common._default_codex_home_root)."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import common  # noqa: E402
    return common._default_codex_home_root()


def default_base() -> Path | None:
    """The shared Codex home (codex_image.base_codex_home), or None when it cannot be found."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import common  # noqa: E402
    try:
        return common._import_codex_image().base_codex_home()
    except Exception:  # noqa: BLE001 - no base home: nothing to compare with, not a verdict on the workers
        return None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", type=Path)
    ap.add_argument("--base", type=Path)
    a = ap.parse_args(argv)
    try:
        root = a.root or default_root()
        verdicts = check(root, a.base if a.base else default_base())
    except Exception as e:  # noqa: BLE001
        print("UNMEASURED: could not read the worker homes: %s: %s" % (type(e).__name__, e))
        return 2
    if not verdicts:
        print("no worker homes under %s (looked, found none)" % root)
        return 0
    for name, v in verdicts.items():
        print("%s %s" % (name, v))
    bad = [n for n, v in verdicts.items() if v in BAD]
    print("%d of %d worker sign-ins bad%s" % (len(bad), len(verdicts),
          "; sign a home in with: CODEX_HOME=<home> codex login --device-auth" if bad else ""))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
