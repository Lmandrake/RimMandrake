#!/usr/bin/env python3
"""wire_art.py — one-command step to copy REVIEWED Lantern Deeps art into place.

Do NOT run this before the owner's review sheet is decided. It reads a
decisions JSON (the review-sheets skill's format) and copies only PNGs marked
"keep" from infrastructure/artpipe/_artsrc/<job_id>/<job_id>.png to the def
texPath locations under this mod's Textures/ folder.

Decisions file schema (matches build_art_sheet.py's output):
{
  "sheet": "deeps_art_review_2026-09-18",
  "posture": "whitelist",          # undecided rows are stripped, not kept
  "decisions": {
    "<artpipe job id>": {"decision": "keep" | "regen", "note": "..."},
    ...
  }
}

Usage:
    python3 wire_art.py                 # dry run — prints the plan, writes nothing
    python3 wire_art.py --apply         # copies kept PNGs into Textures/
    python3 wire_art.py --decisions PATH --apply
    python3 wire_art.py --all-pass      # ignore decisions file; treat every
                                         # facts-PASS render as kept (quick
                                         # preview build only — not a
                                         # substitute for the owner's review)

Every entry below was hand-verified against src/RimUtinni/LanternDeeps/Defs
and infrastructure/artpipe/done/*.manifest.json on 2026-09-18. If a job is
renamed or a def's texPath changes, this table goes stale silently — re-derive
it, do not hand-patch one row.
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
ARTSRC = REPO_ROOT / "infrastructure" / "artpipe" / "_artsrc"
DONE = REPO_ROOT / "infrastructure" / "artpipe" / "done"
TEXTURES = Path(__file__).resolve().parent / "Textures"

# job_id -> (dest path relative to Textures/, expected (w,h))
# dest path with a "/" and a single uppercase/lowercase letter stem is a
# Graphic_Random / Graphic_StackCount folder member; a dest path with no
# letter stem is a single-file graphic (Graphic_Single) or the one file a
# TerrainDef / uiIconPath needs.
JOB_MAP = {
    # 1. terrain (TerrainDef <texturePath>, single square tile)
    "lanternstoneterrain_v1": ("RUT_LanternDeeps/Terrains/Lanternstone.png", (1024, 1024)),
    # 2/3. wall atlases — NO artpipe job exists for either as of 2026-09-18.
    #   Left out of JOB_MAP on purpose; see UNSERVED_TEXPATHS below.
    # 4. wall icon (<uiIconPath>, single file)
    "lanternstonewallicon_v1": ("RUT_LanternDeeps/Things/Natural/Linked/lanternstone_wall_icon.png", (64, 64)),
    # 5. LanternstoneSmall (folder, A/B/C)
    "lanternstonesmall_a_v1": ("RUT_LanternDeeps/Things/Crystals/LanternstoneSmall/A.png", (256, 256)),
    "lanternstonesmall_b_v1": ("RUT_LanternDeeps/Things/Crystals/LanternstoneSmall/B.png", (256, 256)),
    "lanternstonesmall_c_v1": ("RUT_LanternDeeps/Things/Crystals/LanternstoneSmall/C.png", (256, 256)),
    # 6. LanternstoneMedium (folder, A/B/C) — A FAILED, no PNG on disk.
    "lanternstonemedium_b_v1": ("RUT_LanternDeeps/Things/Crystals/LanternstoneMedium/B.png", (256, 256)),
    "lanternstonemedium_c_v1": ("RUT_LanternDeeps/Things/Crystals/LanternstoneMedium/C.png", (256, 256)),
    # 7. LanternstoneLarge (folder, A/B)
    "lanternstonelarge_a_v1": ("RUT_LanternDeeps/Things/Crystals/LanternstoneLarge/A.png", (384, 384)),
    "lanternstonelarge_b_v1": ("RUT_LanternDeeps/Things/Crystals/LanternstoneLarge/B.png", (384, 384)),
    # 8. LanternstoneHuge (folder, A/B)
    "lanternstonehuge_a_v1": ("RUT_LanternDeeps/Things/Crystals/LanternstoneHuge/A.png", (512, 512)),
    "lanternstonehuge_b_v1": ("RUT_LanternDeeps/Things/Crystals/LanternstoneHuge/B.png", (512, 512)),
    # 9. LanternstoneSowableImmature (single file)
    "lanternstonesowableimmature_v1": ("RUT_LanternDeeps/Things/Crystals/LanternstoneSowableImmature.png", (256, 256)),
    # 10. Item/Lanternstone (folder, A/B/C — Graphic_StackCount)
    "lanternstoneitem_a_v1": ("RUT_LanternDeeps/Things/Item/Lanternstone/A.png", (256, 256)),
    "lanternstoneitem_b_v1": ("RUT_LanternDeeps/Things/Item/Lanternstone/B.png", (256, 256)),
    "lanternstoneitem_c_v1": ("RUT_LanternDeeps/Things/Item/Lanternstone/C.png", (256, 256)),
    # 11. Chunks/LanternstoneChunk (folder, a-d)
    "lanternstonechunk_a_v1": ("RUT_LanternDeeps/Things/Chunks/LanternstoneChunk/a.png", (256, 256)),
    "lanternstonechunk_b_v1": ("RUT_LanternDeeps/Things/Chunks/LanternstoneChunk/b.png", (256, 256)),
    "lanternstonechunk_c_v1": ("RUT_LanternDeeps/Things/Chunks/LanternstoneChunk/c.png", (256, 256)),
    "lanternstonechunk_d_v1": ("RUT_LanternDeeps/Things/Chunks/LanternstoneChunk/d.png", (256, 256)),
    # 13. Plant/Mycelium (folder, A/B/C)
    "mycelium_a_v1": ("RUT_LanternDeeps/Things/Plant/Mycelium/A.png", (512, 512)),
    "mycelium_b_v1": ("RUT_LanternDeeps/Things/Plant/Mycelium/B.png", (512, 512)),
    "mycelium_c_v1": ("RUT_LanternDeeps/Things/Plant/Mycelium/C.png", (512, 512)),
    # 14. Plant/Gleamtip (folder, A/B)
    "gleamtip_a_v1": ("RUT_LanternDeeps/Things/Plant/Gleamtip/A.png", (128, 128)),
    "gleamtip_b_v1": ("RUT_LanternDeeps/Things/Plant/Gleamtip/B.png", (128, 128)),
    # 15. Plant/Fungusfern (folder, A-D)
    "fungusfern_a_v1": ("RUT_LanternDeeps/Things/Plant/Fungusfern/A.png", (128, 128)),
    "fungusfern_b_v1": ("RUT_LanternDeeps/Things/Plant/Fungusfern/B.png", (128, 128)),
    "fungusfern_c_v1": ("RUT_LanternDeeps/Things/Plant/Fungusfern/C.png", (128, 128)),
    "fungusfern_d_v1": ("RUT_LanternDeeps/Things/Plant/Fungusfern/D.png", (128, 128)),
    # 16. Plant/CrystaltipBrambles (folder, A/B)
    "crystaltipbrambles_a_v1": ("RUT_LanternDeeps/Things/Plant/CrystaltipBrambles/A.png", (128, 128)),
    "crystaltipbrambles_b_v1": ("RUT_LanternDeeps/Things/Plant/CrystaltipBrambles/B.png", (128, 128)),
    # 17. Plant/YumBulbs (folder, A/B)
    "yumbulbs_a_v1": ("RUT_LanternDeeps/Things/Plant/YumBulbs/A.png", (128, 128)),
    "yumbulbs_b_v1": ("RUT_LanternDeeps/Things/Plant/YumBulbs/B.png", (128, 128)),
    # 18. Plant/Dulcis/DulcisGrown (folder, a)
    "dulcisgrown_a_v1": ("RUT_LanternDeeps/Things/Plant/Dulcis/DulcisGrown/a.png", (256, 256)),
    # 18b. Plant/Dulcis/DulcisImmature (folder, a)
    "dulcisimmature_a_v1": ("RUT_LanternDeeps/Things/Plant/Dulcis/DulcisImmature/a.png", (256, 256)),
    # 18c. Plant/Dulcis/DulcisHarvested (folder, a)
    "dulcisharvested_a_v1": ("RUT_LanternDeeps/Things/Plant/Dulcis/DulcisHarvested/a.png", (256, 256)),
    # 19. Plant/Crystalcap (folder, A/B)
    "crystalcap_a_v1": ("RUT_LanternDeeps/Things/Plant/Crystalcap/A.png", (256, 256)),
    "crystalcap_b_v1": ("RUT_LanternDeeps/Things/Plant/Crystalcap/B.png", (256, 256)),
    # 20. Plant/GreyLady/GreyLadyGrown (folder, A/B/C)
    "greyladygrown_a_v1": ("RUT_LanternDeeps/Things/Plant/GreyLady/GreyLadyGrown/A.png", (256, 256)),
    "greyladygrown_b_v1": ("RUT_LanternDeeps/Things/Plant/GreyLady/GreyLadyGrown/B.png", (256, 256)),
    "greyladygrown_c_v1": ("RUT_LanternDeeps/Things/Plant/GreyLady/GreyLadyGrown/C.png", (256, 256)),
    # 20b. Plant/GreyLady/GreyLadyImmature (folder, a)
    "greyladyimmature_a_v1": ("RUT_LanternDeeps/Things/Plant/GreyLady/GreyLadyImmature/a.png", (256, 256)),
    # 21. Plant/Arpeau (folder, A/B) — NOTE: use arpeau_a/b_v1, never the
    #   older single-variant "arpeau_v1" (pre-facts-gate render, superseded).
    "arpeau_a_v1": ("RUT_LanternDeeps/Things/Plant/Arpeau/A.png", (256, 256)),
    "arpeau_b_v1": ("RUT_LanternDeeps/Things/Plant/Arpeau/B.png", (256, 256)),
    # 22. Plant/LuminousSpout (folder, a/b)
    "luminousspout_a_v1": ("RUT_LanternDeeps/Things/Plant/LuminousSpout/a.png", (256, 256)),
    "luminousspout_b_v1": ("RUT_LanternDeeps/Things/Plant/LuminousSpout/b.png", (256, 256)),
    # 23. Plant/Nuitae (folder, A/B) — use nuitae_a/b_v1, never the older
    #   single-variant "nuitae_v1" (pre-facts-gate render, superseded).
    "nuitae_a_v1": ("RUT_LanternDeeps/Things/Plant/Nuitae/A.png", (256, 256)),
    "nuitae_b_v1": ("RUT_LanternDeeps/Things/Plant/Nuitae/B.png", (256, 256)),
}

# texPaths with NO artpipe job at all as of 2026-09-18 — wire_art.py cannot
# serve these no matter what the decisions file says.
UNSERVED_TEXPATHS = [
    "RUT_LanternDeeps/Things/Natural/Linked/lanternstone_wall_atlas (2048x2048)",
    "RUT_LanternDeeps/Things/Natural/Linked/smoothedlanternstone_wall_atlas (2048x2048)",
]

# job ids that exist in done/ but are NOT current (superseded pre-facts-gate
# renders, or a job with no def referencing its texPath). Never wired.
EXCLUDED_JOB_IDS = {
    "arpeau_v1": "superseded by arpeau_a_v1/arpeau_b_v1 (pre-facts-gate render)",
    "nuitae_v1": "superseded by nuitae_a_v1/nuitae_b_v1 (pre-facts-gate render)",
    "dulciscropitem_v1": "no Def currently references Things/Item/Crops/Dulcis — orphan render, not wired",
}


def load_decisions(path):
    if not path.exists():
        return {}
    data = json.loads(path.read_text())
    return data.get("decisions", data)  # tolerate a bare {job_id: {...}} file too


def facts_pass(job_id):
    mf = DONE / f"{job_id}.manifest.json"
    if not mf.exists():
        return False
    try:
        d = json.loads(mf.read_text())
    except Exception:
        return False
    return d.get("facts") == "PASS"


def plan(decisions, all_pass):
    rows = []
    for job_id, (dest_rel, canvas) in JOB_MAP.items():
        src = ARTSRC / job_id / f"{job_id}.png"
        if all_pass:
            kept = facts_pass(job_id)
            reason = "facts PASS" if kept else "facts not PASS / no manifest"
        else:
            entry = decisions.get(job_id)
            kept = bool(entry) and entry.get("decision") == "keep"
            reason = f"decision={entry.get('decision') if entry else 'MISSING (whitelist posture strips it)'}"
        rows.append({
            "job_id": job_id,
            "src": src,
            "src_exists": src.exists(),
            "dest": TEXTURES / dest_rel,
            "canvas": canvas,
            "kept": kept,
            "reason": reason,
        })
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--decisions", type=Path,
                     default=Path("/mnt/d/Luke/dev/Rimworld/Transient/deeps_art_review_2026-09-18.decisions.json"))
    ap.add_argument("--apply", action="store_true", help="actually copy files (default: dry run, prints the plan only)")
    ap.add_argument("--all-pass", action="store_true",
                     help="ignore the decisions file; treat every facts-PASS render as kept (quick preview only)")
    args = ap.parse_args()

    decisions = {} if args.all_pass else load_decisions(args.decisions)
    rows = plan(decisions, args.all_pass)

    n_keep = sum(1 for r in rows if r["kept"])
    n_skip = len(rows) - n_keep
    print(f"# wire_art.py plan — {'--all-pass' if args.all_pass else args.decisions}")
    print(f"# {n_keep} kept, {n_skip} skipped, {len(UNSERVED_TEXPATHS)} texPaths have no job at all\n")

    for r in rows:
        mark = "KEEP" if r["kept"] else "skip"
        missing = "" if r["src_exists"] else "  ** SOURCE PNG MISSING **"
        print(f"[{mark}] {r['job_id']:32s} -> {r['dest'].relative_to(TEXTURES)}  ({r['reason']}){missing}")

    if UNSERVED_TEXPATHS:
        print("\n# Unserved texPaths (no artpipe job exists — this script cannot fix that):")
        for t in UNSERVED_TEXPATHS:
            print(f"  - {t}")

    if not args.apply:
        print("\nDry run only. Re-run with --apply to copy the KEEP rows into Textures/.")
        return 0

    copied, errors = 0, 0
    for r in rows:
        if not r["kept"]:
            continue
        if not r["src_exists"]:
            print(f"ERROR: {r['job_id']} marked keep but source PNG is missing: {r['src']}", file=sys.stderr)
            errors += 1
            continue
        r["dest"].parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(r["src"], r["dest"])
        copied += 1
    print(f"\nCopied {copied} file(s) into {TEXTURES}. {errors} error(s).")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
