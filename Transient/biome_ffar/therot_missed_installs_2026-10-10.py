"""The Rot sheet 2026-10-10: install the picks/ticks therot_newcols_verify_2026-10-10.md found missing.

AA_AngelMoth C (east+north of gapall_AA_AngelMoth_v1; C has no south and B's south is ✕'d+purged, so the donor
south A is copied as the only south there is) -> RotSpecies/AngelMoth/AngelMoth_<facing>.png in TheRot; the def is
Alpha Animals', so its texPath moves there by patch (RotSpecies_NamesAndSizes.xml).
MortalMorel D, PaleTree B/C, GreyLady C/D -> their Graphic_Random folders.
AB_WitchesOyster A/B/C -> RotSpecies/WitchesOyster/ folder (single file retired), def to Graphic_Random by patch.
Usage: python3 therot_missed_installs_2026-10-10.py [--apply]
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src/RimMandrake/Utils/art"))
import artledger as L  # noqa: E402
import enact as E  # noqa: E402

APPLY = "--apply" in sys.argv
DEC = Path(__file__).resolve().parent / "therot_sheet_2026-10-05.decisions.json"
MOD = "src/RimMandrake/TheRot"
P = "RotSporeKit/Things/Plant/"
SCRIPT = "script:Transient/biome_ffar/therot_missed_installs_2026-10-10.py"

doc = json.loads(DEC.read_text())
snap = json.loads((ROOT / doc["snapshot"]).read_text())["rows"]
col = lambda row, letter: snap[row]["columns"][letter]  # noqa: E731

# (row, letter, facing, rel) — every one authorised by his keep ruling on that row/letter/sha
PLAN = [
    ("AA_AngelMoth", "C", "east", "RotSpecies/AngelMoth/AngelMoth_east.png"),
    ("AA_AngelMoth", "C", "north", "RotSpecies/AngelMoth/AngelMoth_north.png"),
    ("RM_MortalMorelPlant", "D", "single", P + "MortalMorel/MortalMorel_d.png"),
    ("RM_PaleTree", "B", "single", P + "PaleTree/PaleTree_b.png"),
    ("RM_PaleTree", "C", "single", P + "PaleTree/PaleTree_c.png"),
    ("RM_GreyLady", "C", "single", P + "GreyLady/GreyLadyGrown/GreyLadyGrown_c.png"),
    ("RM_GreyLady", "D", "single", P + "GreyLady/GreyLadyGrown/GreyLadyGrown_d.png"),
    ("AB_WitchesOyster", "A", "single", "RotSpecies/WitchesOyster/WitchesOyster_A.png"),
    ("AB_WitchesOyster", "B", "single", "RotSpecies/WitchesOyster/WitchesOyster_b.png"),
    ("AB_WitchesOyster", "C", "single", "RotSpecies/WitchesOyster/WitchesOyster_c.png"),
]


def main():
    idx = L.Index()
    out = []
    for row, letter, facing, rel in PLAN:
        sha = col(row, letter)[facing]
        rul = E.keep_ruling(idx, row, letter, sha)
        if not rul:
            out.append(f"PROBLEM {row} {letter} {facing}: no keep ruling for {sha[:12]}")
            continue
        r = L.install(MOD, rel, sha, ruling_id=rul["id"], dry_run=not APPLY)
        out.append(f"{row} {letter} {facing}: {rel} {r['status']} ({sha[:8]}, ruling {rul['id'][:12]})")
    # AngelMoth south: C has none, B's is ✕'d and purged; the donor's own south (column A) is the only south there is
    sha = col("AA_AngelMoth", "A")["south"]
    r = L.install(MOD, "RotSpecies/AngelMoth/AngelMoth_south.png", sha, dry_run=not APPLY,
                  reason=SCRIPT, provenance={"kind": "donor-fallback",
                                             "why": "pick C has no south; B south purged; Alpha Animals AA_AngelMoth_south"})
    out.append(f"AA_AngelMoth A south (donor fallback): RotSpecies/AngelMoth/AngelMoth_south.png {r['status']} ({sha[:8]})")
    # WitchesOyster: the single file leaves once its picture is in the folder
    old = ROOT / MOD / "Textures/RotSpecies/WitchesOyster.png"
    if APPLY and old.is_file():
        r = L.retire(old, owner_said="AB_WitchesOyster variants A,B,C ticked on therot_sheet_2026-10-05 "
                                     "(variantsAt 2026-10-10T17:33:42Z): picture moved into RotSpecies/WitchesOyster/")
        out.append(f"retired RotSpecies/WitchesOyster.png: {r['status']}")
    else:
        out.append(f"WOULD retire RotSpecies/WitchesOyster.png (exists={old.is_file()})")
    print("\n".join(out))


if __name__ == "__main__" and "--young" not in sys.argv:
    main()


def blastpod_and_young(apply: bool):
    """Card rulings 2026-10-10 (decision taken by question card): Blastpod grown draws only E/F; young redraws queued."""
    import subprocess
    idx = L.Index()
    g = "RotSporeKit/Things/Plant/Boomshroom/BoomshroomGrown/BoomshroomGrown_A.png"
    p = ROOT / MOD / "Textures" / g
    if apply and p.is_file():
        r = L.retire(p, owner_said="decision taken by question card 2026-10-10: RM_BlastpodShroom grown draws only E and F")
        print("retired", g, r["status"])
    else:
        print("WOULD retire", g, p.is_file())
    young = [
        ("RM_BlastpodShroom", "kabbrik pod", snap["RM_BlastpodShroom"]["columns"]["E"]["single"],
         "RotSporeKit/Things/Plant/Boomshroom/BoomshroomImmature",
         "A low cluster of taut, rounded pods on short stems, the skins grey-white and glossy, each seam showing a faint "
         "warm glow."),
        ("RM_GreyLady", "sylla lace", snap["RM_GreyLady"]["columns"]["B"]["single"],
         "RotSporeKit/Things/Plant/GreyLady/GreyLadyImmature",
         "A slender grey mushroom that grows a fine lace from beneath its cap, falling to the ground around the stalk "
         "like a veil."),
    ]
    rows = []
    for row, label, sha, tex, desc in young:
        base = f"rotimmature_{L.subject_key(row)}"
        rows.append({"id": f"{base}_v{E.next_version(base)}", "rimflow_item_id": "BIOME_FLORAFAUNA_ART_REVIEW_1",
                     "target_def": row, "target_texpath": tex,
                     "prompt": f"RimWorld plant sprite of a YOUNG, immature {label} ({desc}), painterly vanilla-RimWorld "
                               "house style, realistic natural-history rendering. Draw the same species as the attached "
                               "grown picture (the owner's pick) at an early growth stage: smaller, fewer and less developed "
                               "parts, same palette and anatomy. The attached image is anatomy guidance only, not a sprite "
                               "to copy. A single young plant on a transparent background.",
                     "canvas_w": 256, "canvas_h": 256, "facings": [], "priority": 0,
                     "owner_note": "decision taken by question card 2026-10-10: new young-plant art, from his grown pick",
                     "canon_reference": [str(L.store_path(sha))], "biome_neutral": True})
    jp = ROOT / "Transient/biome_ffar/therot_young_jobs_2026-10-10.json"
    jp.write_text(json.dumps(rows, indent=1))
    d = E.artpipe_dirs()
    fq = [sys.executable, str(ROOT / "src/RimMandrake/Utils/artpipe/fill_queue.py"), "--input", str(jp),
          "--pending-dir", str(d["pending"]), "--active-dir", str(d["active"]), "--done-dir", str(d["done"]),
          "--failed-dir", str(d["failed"])] + ([] if apply else ["--dry-run"])
    r = subprocess.run(fq, capture_output=True, text=True, cwd=str(ROOT))
    print("fill_queue rc", r.returncode, (r.stdout + r.stderr).strip()[-1500:])


if __name__ == "__main__" and "--young" in sys.argv:
    blastpod_and_young(APPLY)
