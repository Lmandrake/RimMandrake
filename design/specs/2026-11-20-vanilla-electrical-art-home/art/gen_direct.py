#!/usr/bin/env python3
"""gen_direct.py — render make_jobs.py's rows with codex_image.py on the SHARED Codex home, one at a time.

    python3 design/specs/2026-11-20-vanilla-electrical-art-home/art/gen_direct.py wave1|wave2 [--only SUBSTR ...]

Why not the artpipe daemon: on 2026-11-20 at 15:53 PST every one of this item's 15 queued jobs failed in ~3 s
(worker homes ~/.codex_workers/artpipe/w0..w4 hold an auth.json last refreshed 2026-11-10 whose refresh token is
dead: "refresh token was already used"). Copying auth.json between homes forks the token lineage
(generating-rimworld-sprites traps), so this runs serially on the shared home, as the standing lamp's looks were made
(src/RimMandrake/Utils/mockups/messy_conduit/round5_art_jobs.py). The prompt is the job's prompt plus the canvas and the
house register (artpipe/common.HOUSE_ART_REGISTER), which the daemon would have added.

Raw renders: <agent storage>/rimmandrake/scratch/vea_20261120/raw/<id>.png (outside git). An existing output is skipped.
A wave-2 row is an edit of its derive_from row's raw render. Prints one line per row: OK / FAIL <why> / SKIP.
"""
import os, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "src" / "RimMandrake" / "Utils"))
sys.path.insert(0, str(REPO / "src" / "RimMandrake" / "Utils" / "artpipe"))
import make_jobs  # noqa: E402
from rmpaths import rm_str  # noqa: E402
import common  # noqa: E402

RAW = Path(rm_str("scratch", "vea_20261120")) / "raw"
CI = Path(os.environ.get("RM_IMAGE_SKILLS_ROOT") or os.path.expanduser("~/dev/MandrakeWorkflows/skills")) / \
    "generating-images/scripts/codex_image.py"


def prompt_of(row):
    return (row["prompt"] + " Canvas: %dx%d pixels, or a larger canvas of the same shape. "
            % (row["canvas_w"], row["canvas_h"]) + common.HOUSE_ART_REGISTER)


def main():
    wave = sys.argv[1]
    only = sys.argv[sys.argv.index("--only") + 1:] if "--only" in sys.argv else []
    rows = make_jobs.wave2() if wave == "wave2" else make_jobs.rows()
    RAW.mkdir(parents=True, exist_ok=True)
    bad = 0
    for r in rows:
        if only and not any(s in r["id"] for s in only):
            continue
        out = RAW / (r["id"] + ".png")
        if out.exists():
            print("SKIP %s (exists)" % r["id"], flush=True)
            continue
        cmd = [sys.executable, str(CI)]
        if r.get("derive_from"):
            src = RAW / (r["derive_from"] + ".png")
            if not src.exists():
                print("FAIL %s: its master %s has no render" % (r["id"], src.name), flush=True)
                bad += 1
                continue
            cmd += ["edit", "--image", str(src)]
        else:
            cmd += ["generate"]
        cmd += ["--out", str(out), "--prompt", prompt_of(r), "--timeout", "600"]
        t = time.time()
        p = subprocess.run(cmd, capture_output=True, text=True)
        ok = p.returncode == 0 and out.exists()
        if not ok:
            bad += 1
        print("%s %s %.0fs%s" % ("OK" if ok else "FAIL", r["id"], time.time() - t,
                                 "" if ok else ": exit %d %s" % (p.returncode, (p.stderr or p.stdout)[-300:].replace("\n", " "))),
              flush=True)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
