#!/usr/bin/env python3
"""Drive the art-eval regen loop for live fauna: rows -> artpipe jobs, finished jobs -> candidate specs -> install.

    python3 fauna_drive.py rows <run-id>... --out rows.json [--file]     # regen_jobs.json -> fill_queue rows
    python3 fauna_drive.py candidates <DEF>... --round N --out <dir>      # done arteval_<DEF>_rN_* renders -> specs
    python3 fauna_drive.py install <DEF> --round N --run <run-id>         # accepted candidate -> art.py install

Why `rows` rewrites the prompt: the regen prompt edit speaks about every facing at once ("the rear view shows ...",
"all facings"), but each artpipe job draws exactly ONE facing and the daemon stamps that facing's view direction
(common._refuse_contradicted_facing refuses the contradiction). So the prompt is rewritten facing-neutral — the visual
spec only, no view words — by a sonnet call, checked mechanically (no view words may remain; else sentences naming a
view are dropped), and the canvas follows the shipping rule (smallest power of two >= adult drawSize x 128, min 256).
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import runner as R  # noqa: E402
import cards as C  # noqa: E402

ROOT = C.ROOT
VIEWWORDS = re.compile(r"\b(facings?|views?|profile|front|rear|side|north|south|east|west|top-down|overhead|"
                       r"from behind|toward the viewer|camera)\b", re.I)


def canvas_for(draw: float) -> int:
    need = draw * 128
    c = 256
    while c < need and c < 1024:
        c *= 2
    return c


def neutral_prompt(prompt: str) -> tuple[str, str]:
    if not VIEWWORDS.search(prompt):
        return prompt, "unchanged"
    ask = ("Rewrite this image-generation prompt so it describes ONLY what the single creature looks like (body, "
           "colours, materials, markings, anatomy, expression, pose, style). Delete every word about camera, view, "
           "facing, side, front, rear, profile, top, direction, or which way anything points; where a sentence says what "
           "a feature looks like from some angle, keep the feature and drop the angle. Keep it positively phrased, "
           "keep the painterly realistic style and transparent background sentence, one paragraph. Return only the "
           "new prompt.\n\n" + prompt)
    text, meta = R.call_claude(ask, R.storage_root(), "sonnet", timeout=200, tools="")
    text = text.strip().strip('"')
    if text and not VIEWWORDS.search(text):
        return text, "sonnet"
    sents = re.split(r"(?<=[.!?])\s+", prompt)
    kept = [s for s in sents if not VIEWWORDS.search(s)]
    return " ".join(kept), "sentence-drop"


def cmd_rows(a):
    rows = []
    for rid in a.runs:
        rows += json.loads((ROOT / f"infrastructure/state/art_eval/runs/{rid}/regen_jobs.json").read_text())
    specs = {}
    for p in Path(a.specs).glob("**/*.spec.json"):
        s = json.loads(p.read_text())
        specs[s["subject"]] = s

    def fix(r):
        s = specs[r["target_def"]]
        d = s["size"]["drawSize"][0]
        r["prompt"], r["_prompt_by"] = neutral_prompt(r["prompt"])
        r["canvas_w"] = r["canvas_h"] = canvas_for(d)
        r["drawsize"] = d
        r["biome_neutral"] = True
        r.pop("source_run", None)
        return r

    with ThreadPoolExecutor(4) as ex:
        rows = list(ex.map(fix, rows))
    for r in rows:
        r.pop("_prompt_by", None)
    Path(a.out).write_text(json.dumps(rows, indent=1))
    print(f"{len(rows)} rows -> {a.out}")
    if a.file:
        subprocess.run([sys.executable, str(ROOT / "src/RimMandrake/Utils/artpipe/fill_queue.py"), "--input", a.out],
                       check=False, timeout=300)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("rows")
    r.add_argument("runs", nargs="+")
    r.add_argument("--specs", default=str(R.storage_root() / "fauna_specs"))
    r.add_argument("--out", required=True)
    r.add_argument("--file", action="store_true")
    a = ap.parse_args(argv)
    {"rows": cmd_rows}[a.cmd](a)


if __name__ == "__main__":
    main()
