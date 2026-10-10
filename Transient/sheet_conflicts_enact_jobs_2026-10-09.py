#!/usr/bin/env python3
"""Jobs the 66-row conflict sheet needs that `art.py enact` does not file itself:
  * failed:A rows (Krayt, Blixus, Opee juv, Tooke trap) — "rewrite the prompt and re-file": the failed job's spec
    is cloned under a new id with the canon-check line it failed spelled out as a hard requirement;
  * del:B replacements with no render yet — Hawkbat juvenile north, Peko Peko male (all three facings);
  * Dark Vandal (noslot:A, port RM_Ossumatha) — the port's north/south never rendered (only east is live).
Filed through artpipe/fill_queue.py at priority 0 (owner-ruled work), same path enact uses.

    python3 Transient/sheet_conflicts_enact_jobs_2026-10-09.py [--apply]
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/RimMandrake/Utils/artpipe"))
sys.path.insert(0, str(ROOT / "src/RimMandrake/Utils/art"))
import fill_queue as FQ        # noqa: E402
import enact as E              # noqa: E402

AP = E.artpipe_dirs()
PASS_THRU = ("rimflow_item_id", "target_def", "target_original", "target_texpath", "owner_note", "background",
             "channel", "drawsize")


def spec(jid):
    for st in ("failed", "done", "pending", "active"):
        p = AP[st] / f"{jid}.json"
        if p.is_file():
            return json.loads(p.read_text())
    raise SystemExit(f"no job {jid}")


def base_prompt(j):
    p = j["prompt"]
    for pre in (FQ.DERIVE_PROMPT_PREFIX, getattr(FQ, "CANON_PROMPT_PREFIX", "")):
        if pre and p.startswith(pre):
            p = p[len(pre):]
    return p


def clone(old_id, new_base, facing, must, derive=None):
    j = spec(old_id)
    row = {k: j[k] for k in PASS_THRU if j.get(k) not in (None, "", [])}
    row.update({"id": new_base, "facings": [facing] if facing else [], "priority": 0,
                "canvas_w": j["canvas"]["width"], "canvas_h": j["canvas"]["height"],
                "style_notes": j.get("style_notes") or "",
                "prompt": base_prompt(j) + (f" HARD REQUIREMENT (the previous render failed the canon check on exactly "
                                            f"this): {must}" if must else "")})
    refs = [r for r in (j.get("canon_reference") or []) if Path(r).is_file()]   # library entries move; keep live ones
    if refs:
        row["canon_reference"] = refs
    row["biome_neutral"] = True
    if j.get("canvas", {}).get("width", 256) > 256:
        row["oversize_reason"] = "same canvas as the failed job it re-files"
    if j.get("target_canon"):
        row["canon"] = j["target_canon"]
    d = derive if derive is not None else j.get("derive_from")
    if d:
        row["derive_from"] = d
    return row


ROWS = [
    # failed:A — rewrite + re-file
    clone("stillsand_s2_RSW_KraytDragon_v3_south", "stillsand_s3_RSW_KraytDragon_v4", "south",
          "every foot, front and rear, shows 4 to 5 curved dark claws — never three."),
    clone("miasma_canon_blixus_v1_north", "miasma_canon_blixus_v2", "north",
          "exactly six stiff blade-like chitin legs, three on each side, every one of them clearly visible from this "
          "view (not four)."),
    clone("miasma_canon_blixus_v1_south", "miasma_canon_blixus_v2b", "south",
          "all five ringed pink tentacles are each clearly LONGER than the body, including the lower pair."),
    clone("miasma_canon_blixus_v1_swim_east", "miasma_canon_blixus_v2_swim", "east",
          "all five ringed pink tentacles are each clearly LONGER than the body — none shorter."),
    clone("miasma_canon_opeejuv_v2_south", "miasma_canon_opeejuv_v3", "south",
          "the three pairs of walking legs are THIN, spindly, jointed crab-like limbs — not short or stout."),
    clone("webwork_tooketrap_redo_v2", "webwork_tooketrap_redo_v3", None,
          "realistic natural rendering: waxy leaf surfaces and fleshy pod texture under natural light; no flat, "
          "angular, cel-style shading."),
    # del:B — replacement still to be drawn
    clone("regen_gt_canon_hawkbat_juv_v1_north", "regen_gt_canon_hawkbat_juv_v2", "north",
          "a young hawkbat (smaller, rounder proportions than the adult) seen from behind, matching the installed "
          "juvenile east/south facings."),
]
peko = clone("regen_gt_canon_pekopeko_m_v1_east", "conflict_pekopeko_m_v2", None, "", derive="")
peko.pop("derive_from", None)
peko["facings"] = ["east", "south", "north"]
ROWS.append(peko)
oss = clone("abyss_ossumatha_v3_east", "abyss_ossumatha_v5", None, "", derive="abyss_ossumatha_v3_east")
oss["facings"] = ["north", "south"]
oss["target_texpath"] = "RM_Abyss/Things/Pawn/Animal/RM_Ossumatha/RM_Ossumatha"
ROWS.append(oss)


def main(argv):
    out = ROOT / "Transient" / "sheet_conflicts_enact_jobs_2026-10-09.json"
    out.write_text(json.dumps(ROWS, indent=1))
    cmd = [sys.executable, str(ROOT / "src/RimMandrake/Utils/artpipe/fill_queue.py"), "--input", str(out),
           "--pending-dir", str(AP["pending"]), "--active-dir", str(AP["active"]),
           "--done-dir", str(AP["done"]), "--failed-dir", str(AP["failed"])]
    if "--apply" not in argv:
        cmd.append("--dry-run")
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
    print(r.stdout[-3000:], r.stderr[-3000:], "rc", r.returncode)


if __name__ == "__main__":
    main(sys.argv[1:])
