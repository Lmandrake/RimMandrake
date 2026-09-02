#!/usr/bin/env python3
"""Generate the south + north facings for named sea beasts.

east/west are NOT generated: the owner's kept mockup IS a left-facing side
profile, which is exactly the west facing, so west comes from the mockup itself
and east is its mirror. That is two calls per creature instead of four, and it
makes two of the four facings a pixel-exact match to the approved concept.

    python3 gen_sea_facings.py CrimsonOpee ShaleGorger ...

Skips any raw that already exists. No cleanup/kill line anywhere: `timeout`
inside codex_image.py reaps its own child, and a pgrep-based cleanup would
match this script's own argv and SIGKILL the job it is retrying.
"""
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sea_creatures import CREATURES, MOCKUPS, RAW, prompt_for  # noqa: E402

GEN = "/mnt/d/Luke/dev/Rimworld/skills/generating-images/scripts/codex_image.py"
# Measured on this batch: an `edit` carrying a ~1.5 Mpx mockup lands at
# 120-170 s, not the ~80 s the skill measured for generate. At 120 s the call
# was killed AFTER codex had produced the image, so the retry then refused to
# overwrite its own good output - the FAIL was a harness artefact, not a
# generation failure. Hence 210 s, and the late-file recovery below.
TIMEOUT = "210"
ATTEMPTS = 3


def one(job):
    slug, facing = job
    mock = Path(MOCKUPS) / (CREATURES[slug][0] + ".png")
    out = Path(RAW) / f"{slug}_{facing}_raw.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        return f"SKIP {out.name}"
    prompt = prompt_for(slug, facing)
    last = ""
    for attempt in range(1, ATTEMPTS + 1):
        t0 = time.time()
        r = subprocess.run(
            [sys.executable, GEN, "edit", "--out", str(out), "--prompt", prompt,
             "--image", str(mock), "--chroma-key", "#00ff00",
             "--timeout", TIMEOUT],
            capture_output=True, text=True)
        dt = int(time.time() - t0)
        if r.returncode == 0 and out.exists():
            return f"OK   {out.name} ({dt}s, try {attempt})"
        last = ((r.stderr or r.stdout or "").strip().splitlines() or ["no output"])[-1]
        time.sleep(4)
        if out.exists():          # arrived after its own timeout killed the call
            return f"LATE {out.name} ({dt}s, try {attempt})"
    return f"FAIL {out.name}: {last[:110]}"


def main():
    slugs = sys.argv[1:]
    bad = [s for s in slugs if s not in CREATURES]
    if not slugs or bad:
        print("usage: gen_sea_facings.py <slug> ...   unknown: %s" % bad, file=sys.stderr)
        return 2
    jobs = [(s, f) for s in slugs for f in ("south", "north")]
    with ThreadPoolExecutor(max_workers=3) as ex:
        for res in ex.map(one, jobs):
            print(res, flush=True)
    print("DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
