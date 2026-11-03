#!/usr/bin/env python3
"""dessicated_render_check.py — proof for DESSICATED_CORPSES_REDRAW_ONE_BY_ONE.

Every dessic_* job in design/RimMandrake/dessicated_corpses_commission_2026-10-16.json must be DRAWN, which is
one of:
  INSTALLED  artpipe collected.jsonl binds the job (or a later _vN / per-facing _<facing> of it) to its install_to,
             and the repo file there has that sha256 and placeholder_detect reads it REAL;
  RENDERED   the job (or a later _vN) is in artpipe done/ and its picture _artsrc/<id>/<id>.png reads REAL
             (installing it is DESSICATED_CORPSES_INSTALL_AFTER_PICKS, not this item);
  RETIRED    the species was cut or its corpse art redrawn under another job (EXEMPT below, each with the
             commit or files that prove it; those files must exist and read REAL).
Anything else (pending, failed, a placeholder, a lost picture) fails the check.

Sanity probe: the detector must flag a flat synthetic rectangle, or the run is UNMEASURED (exit 2).

    python3 src/RimMandrake/Utils/art/dessicated_render_check.py [--state <artpipe dir>] [-v]
exit 0 all drawn · 1 some not drawn · 2 instrument blind
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import warnings
from pathlib import Path

warnings.filterwarnings("ignore", category=DeprecationWarning)
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "src" / "RimMandrake" / "Utils" / "artpipe"))
import placeholder_detect as P  # noqa: E402

COMMISSION = REPO / "design" / "RimMandrake" / "dessicated_corpses_commission_2026-10-16.json"
TAOZIN = "src/RimStarWars/SWBestiary/Textures/Things/Pawn/Animal"
# job id -> (why, commit that must be an ancestor of HEAD or None, repo files that must exist and read REAL)
EXEMPT = {
    "dessic_rycrit_dessicated_v1": ("RSW_Rycrit cut by the owner per facings sheet", "0a0d2fcc62", []),
    "dessic_taozin_dessicated_v1": ("RSW_Taozin split; corpse redrawn as Dessicated_RSW_Taozin_* (taozin_split jobs)",
                                    "d2b1afb643", [f"{TAOZIN}/RSW_Taozin/Dessicated_RSW_Taozin_{f}.png"
                                                   for f in ("north", "east", "south")]),
    "dessic_taozin_j_dessicated_v1": ("juvenile split out as RSW_TaozinGrub; corpse redrawn as Dessicated_RSW_TaozinGrub_*",
                                      "d2b1afb643", [f"{TAOZIN}/RSW_TaozinGrub/Dessicated_RSW_TaozinGrub_{f}.png"
                                                     for f in ("north", "east", "south")]),
}


def state_dir(arg):
    if arg:
        return Path(arg)
    from state_dir import resolve  # artpipe's own resolver
    return Path(resolve())


def probe() -> bool:
    from PIL import Image
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "flat.png"
        im = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
        im.paste((180, 140, 90, 255), (96, 160, 416, 352))
        im.save(p)
        return bool(P.placeholder_reason(p))


def family(jid: str):
    """'dessic_akk_dessicated_v1' -> regex matching that job, its later versions and its per-facing ids."""
    base = re.sub(r"_v\d+$", "", jid)
    return re.compile(re.escape(base) + r"_v\d+(_(north|east|south|west))?$")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def is_ancestor(commit: str) -> bool:
    return subprocess.run(["git", "-C", str(REPO), "merge-base", "--is-ancestor", commit, "HEAD"],
                          capture_output=True).returncode == 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--state")
    ap.add_argument("-v", action="store_true", help="print every job's verdict")
    a = ap.parse_args()
    S = state_dir(a.state)
    if not probe():
        print("UNMEASURED: placeholder_detect did not flag a flat synthetic rectangle")
        return 2
    jobs = json.loads(COMMISSION.read_text())
    if not jobs:
        print("UNMEASURED: commission file lists no jobs")
        return 2
    collected = []
    for line in (S / "collected.jsonl").read_text(errors="replace").splitlines():
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if str(d.get("job_id", "")).startswith("dessic_"):
            collected.append(d)
    if not collected:
        print(f"UNMEASURED: no dessic_* rows in {S / 'collected.jsonl'}")
        return 2
    done_ids = [p.stem for p in (S / "done").glob("dessic_*.json") if not p.name.endswith(".manifest.json")]

    tally, bad = {}, []
    for j in jobs:
        jid, fam = j["id"], family(j["id"])
        verdict = why = None
        if jid in EXEMPT:
            reason, commit, files = EXEMPT[jid]
            miss = [f for f in files if not (REPO / f).exists() or P.placeholder_reason(REPO / f)]
            if commit and not is_ancestor(commit):
                why = f"exemption commit {commit} not in HEAD"
            elif miss:
                why = f"exemption files missing or placeholder: {miss}"
            else:
                verdict = f"RETIRED ({reason})"
        if verdict is None and why is None:
            for c in collected:
                if not fam.match(c["job_id"]):
                    continue
                dest = REPO / c["dest"]
                if dest.exists() and sha(dest) == c["sha256"] and not P.placeholder_reason(dest):
                    verdict = f"INSTALLED {c['job_id']} -> {c['dest']}"
                    break
        if verdict is None and why is None:
            for d in sorted(i for i in done_ids if fam.match(i)):
                png = S / "_artsrc" / d / f"{d}.png"
                if png.exists() and not P.placeholder_reason(png):
                    verdict = f"RENDERED {d} (awaiting install)"
                    break
        if verdict is None:
            where = [f"{q}/{p.stem}" for q in ("pending", "active", "failed")
                     for p in (S / q).glob(re.sub(r"_v\d+$", "", jid) + "_v*.json")
                     if not p.name.endswith(".manifest.json")]
            bad.append(f"{jid}: {why or 'not drawn'}  {' '.join(where)}")
        else:
            tally[verdict.split()[0]] = tally.get(verdict.split()[0], 0) + 1
            if a.v:
                print(f"  ok {jid}: {verdict}")
    n = len(jobs)
    print(f"{n - len(bad)}/{n} dessic_* jobs drawn {tally}  state={S}")
    for b in bad:
        print("  NOT DRAWN", b)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
