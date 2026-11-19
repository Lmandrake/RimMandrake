#!/usr/bin/env python3
"""Head-to-head second opinion before a regen candidate REPLACES installed art (fauna helper, 2026-10-23).

Why it exists: the departures brief the first pass uses is written from the description by a model and invents
specifics the def never states (ARTEVAL_DEPARTURES_TUNE_ALMOST_EVERYTHING), so a candidate redrawn to satisfy those
inventions can pass the pipeline while being a WORSE picture of what the description says (RM_Tikkit: a painterly
katydid, the description's "dry chorus ... it clicks", was redrawn as a hedgehog-cone flock). This judge is a fresh
Opus that sees only the def text (no brief, no prior verdict), the installed art (A) and the candidate (B), and
decides which better serves the description and the house rules. Install only when B wins and has no hard defect.

    python3 fauna_compare.py <DEF> --cand <candidate spec.json> --out <dir>
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cards as C  # noqa: E402
import runner as R  # noqa: E402
import policy as P  # noqa: E402

PROMPT = """You are an independent art judge for RimWorld animal sprites. Two sets of the same creature's facings are
image files in the current directory: A.png = the art installed now, B.png = a new candidate (B_scale.png shows B
beside a human). Read all of them (Read tool) at full resolution before answering, then answer with ONE JSON object and nothing else.

The creature (the description is the ONLY authority on what it should look like; do not demand features it does not
state, and do not punish a plain, realistic animal when the description describes one):

{desc}

House rules (each is a defect on the set that breaks it):
- south = face toward the camera; north = the rear (back/tail, no face, no eyes); east = true side profile. A top-down
  / overhead plan view on any facing is a hard defect; so is a facing that is a different animal or pose family.
- The three facings are the same size and the same individual (same markings, horns, tail, colours).
- Realistic and painterly, not cartoon, not cute (glossy round eyes, smiling face, thick uniform black keyline are
  defects). Alien where the description says alien; an ordinary Earth body is fine when the description names one.
- Clean real alpha: no baked ground, no halo, no cropped limbs.
- It reads as the creature at game size (scale panel shown for B).

Reply:
{{"a": {{"hard_defects": ["..."], "polish": ["..."], "serves_description": 0-10}},
  "b": {{"hard_defects": ["..."], "polish": ["..."], "serves_description": 0-10}},
  "winner": "A|B|tie", "install_b": true|false, "reason": "<two sentences>"}}
install_b is true only when B is clearly the better picture of THIS description with no hard defect of its own, or A
has a hard defect that B fixes without introducing another.
"""


def compose(spec: dict, cand: dict, out: Path):
    out.mkdir(parents=True, exist_ok=True)
    faces = [f for f in ("south", "east", "north") if spec["images"].get(f) and cand["images"].get(f)]
    a = C.strip([spec["images"][f] for f in faces], [f"A {f}" for f in faces], tile=512, title=f"A installed - {spec['subject']}")
    b = C.strip([cand["images"][f] for f in faces], [f"B {f}" for f in faces], tile=512, title=f"B candidate - {spec['subject']}")
    a.save(out / "A.png")
    b.save(out / "B.png")
    if cand["images"].get("scale"):
        from PIL import Image
        Image.open(cand["images"]["scale"]).convert("RGB").save(out / "B_scale.png")
    return faces


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("defname")
    ap.add_argument("--cand", required=True)
    ap.add_argument("--base", help="base spec of the installed art (default: sibling fauna_specs search)")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    cand = json.loads(Path(a.cand).read_text())
    base = Path(a.base) if a.base else next((R.storage_root() / "fauna_specs").glob(f"**/{a.defname}.spec.json"))
    spec = json.loads(base.read_text())
    out = Path(a.out)
    compose(spec, cand, out)
    text, meta = R.call_claude(PROMPT.format(desc=spec["description"]), out, "opus", timeout=420, tools="Read")
    try:
        reply = P.parse_reply(text)
    except Exception as e:  # noqa: BLE001
        reply = {"error": str(e), "raw": text[:800]}
    reply["_meta"] = {k: meta.get(k) for k in ("models_reported", "seconds", "cost_usd", "error")}
    (out / "compare.json").write_text(json.dumps(reply, indent=1))
    print(a.defname, reply.get("winner"), reply.get("install_b"), "-", str(reply.get("reason"))[:300])


if __name__ == "__main__":
    main()
