"""Stage the finalized candidates as artpipe renders and write the art_sheet texture manifest.

The route the GSS tap-clamp candidates took (2026-10-11): each candidate facing becomes an artpipe render dir
<data root>/artpipe/_artsrc/<job>/<job>.png + done/<job>.json (facing, target_texpath, prompt), `art.py backfill artpipe`
imports it into the art ledger, and a texture-manifest row names its families, so `art_sheet.py --textures` shows
local candidates at true scale. Installs nothing into any Textures folder.

    python3 stage_sheet.py MANIFEST_OUT
"""
import sys as _rm_sys, pathlib as _rm_pl  # noqa: E401
_rm_sys.path.insert(0, str(_rm_pl.Path(__file__).resolve().parents[5] / "src" / "RimMandrake" / "Utils"))
from rmpaths import rm_path, rm_str, rm_win  # noqa: E402,F401  (data root: rmpaths.py)
import json
import os
import shutil
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ARTPIPE = Path(os.environ.get("ARTPIPE_STATE_DIR") or rm_str("artpipe"))
TEXDIR = "Things/Building/FlowWorks/Canals"
KINDS = {"Hung": "slid DOWN, hung on the pit wall the rotation names (usable)",
         "Stowed": "slid UP, laid on the rim beside that wall (prisoners cannot reach it)"}
ITEM = "PIT_LADDER_REDRAW_HUNG_ON_THE_WALL"


def main(manifest_out):
    tags = sorted(p.name for p in (HERE / "out").iterdir() if p.is_dir())
    rows = []
    for kind, what in KINDS.items():
        fams = []
        for tag in tags:
            fam = f"ladder{kind.lower()}_{tag.lower()}"
            fams.append(fam)
            for fac in ("north", "east", "south", "west"):
                src = HERE / "out" / tag / f"RM_Ladder{kind}_{fac}.png"
                if not src.is_file():
                    continue
                job = f"{fam}_{fac}"
                d = ARTPIPE / "_artsrc" / job
                d.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, d / f"{job}.png")
                (ARTPIPE / "done" / f"{job}.json").write_text(json.dumps({
                    "id": job, "facing": fac, "channel": "codex", "created": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "drawsize": 1.0, "canvas": {"width": 256, "height": 256}, "background": "transparent",
                    "prompt": f"RM_Ladder{kind}_{fac}: {what}. Candidate {tag}; generator art_source/Ladder/gen.sh, "
                              f"guide art_source/Ladder/guide.py" + (" (west = east mirrored)" if fac == "west" else ""),
                    "rimflow_item_id": ITEM, "target_texpath": f"{TEXDIR}/RM_Ladder{kind}",
                    "source_file": str(src.relative_to(HERE.parents[4]))}, indent=2))
        rows.append({"key": f"RM_Ladder{kind}", "label": f"pit ladder, {what}", "part": "ladder", "look": kind.lower(),
                     "section": "FlowWorks pit ladder", "resources": [f"{TEXDIR}/RM_Ladder{kind}"],
                     "former": [f"{TEXDIR}/RM_Ladder" if kind == "Hung" else f"{TEXDIR}/RM_LadderRaised"],
                     "size": {"drawSize": [1, 1], "footprint": [1, 1],
                              "source": "RM_Ladder ThingDef: 1x1 building on the pit cell, drawSize 1 (Graphic_Multi by rotation = wall)"},
                     "jobs": fams, "render_match": "|".join(fams)})
    lead = ("<p><b>Pit ladder, redrawn to hang on a wall</b> (" + ITEM + "). Owner 2026-10-16: <i>“It clearly needs to be "
            "installed along a side of the pit, like a door to a room, and have a 'slid up' version that's inaccessible to the "
            "prisoners below or a 'slid down' version that is clearly visible.”</i> Rotation = the wall it hangs on: north = far "
            "wall (visible face), south = near wall (only the hooks show over the lip), east/west = side walls. Stowed is drawn "
            "0.55 cell toward its wall, on the rim. Each column is one candidate; the in-pit mock is "
            "Transient/ladder_art_2026-10-16/ladder_in_pit_mock.png.</p>")
    Path(manifest_out).parent.mkdir(parents=True, exist_ok=True)
    Path(manifest_out).write_text(json.dumps({"rows": rows, "lead_html": lead}, indent=1))
    print(manifest_out, [r["jobs"] for r in rows])


if __name__ == "__main__":
    main(sys.argv[1])
