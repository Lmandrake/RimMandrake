#!/usr/bin/env python3
"""The Rot sheet (therot_sheet_2026-10-05) picks and clicked variants that `art.py enact` reported "already live"
or never ships (variants). Each install is authorised by his keep ruling for that row/column in the art ledger;
each retire removes the in-game A picture he did not pick and did not keep as a variant.

    python3 Transient/biome_ffar/therot_todo_installs_2026-10-10.py [--apply]
"""
import sys
sys.path.insert(0, "src/RimMandrake/Utils/art")
import artledger as L  # noqa: E402
import enact as E  # noqa: E402

MOD = "src/RimMandrake/TheRot"
P = "RotSporeKit/Things/Plant/"
ME = "script:Transient/biome_ffar/therot_todo_installs_2026-10-10.py"
FULL = {}  # short sha -> full, filled from the snapshot
import json  # noqa: E402
snap = json.load(open("infrastructure/state/art/sheets/therot_sheet_2026-10-05.snapshot.json"))["rows"]

# (row, column letter, slot rel under Textures)
INSTALL = [
    ("RM_Arpeau", "B", P + "Arpeau/Arpeau_B.png"),               # pick B
    ("RM_Arpeau", "C", P + "Arpeau/Arpeau_C.png"),               # clicked variant C (A stays as Arpeau_A, kept)
    ("RM_Brightbell", "C", P + "Brightbell/Brightbell_A.png"),   # pick C replaces A
    ("RM_EuphoricCrown", "B", P + "EuphoricCrown/EuphoricCrown_A.png"),
    ("RM_FalseFruit", "B", P + "FalseFruit/FalseFruit_A.png"),
    ("RM_GreyLady", "B", P + "GreyLady/GreyLadyGrown/GreyLadyGrown_A.png"),
    ("RM_MortalMorelPlant", "B", P + "MortalMorel/MortalMorel_A.png"),
    ("RM_AgelessCap", "B", P + "AgelessCap/AgelessCap_B.png"),   # clicked variant
    ("RM_Nuitae", "B", P + "Nuitae/Nuitae_B.png"),               # clicked variants
    ("RM_Nuitae", "C", P + "Nuitae/Nuitae_C.png"),
    ("RM_RegenerantVeil", "C", P + "RegenerantVeil/RegenerantVeil_C.png"),
    ("RM_Shinecap", "B", P + "Shinecap/ShinecapGrown/ShinecapGrown_b.png"),
    ("RM_Shinecap", "C", P + "Shinecap/ShinecapGrown/ShinecapGrown_c.png"),
    ("RM_Shinecap", "D", P + "Shinecap/ShinecapImmature/ShinecapImmature_d.png"),  # renders of the immature form
    ("RM_Shinecap", "E", P + "Shinecap/ShinecapImmature/ShinecapImmature_e.png"),
]
# in-game A pictures he picked against (pick is already live beside them)
RETIRE = [P + "Pusmelon/BMT_PusmelonA.png", P + "Sagecrust/BMT_SagecrustA.png"]


def main(apply: bool) -> None:
    idx = L.Index()
    for row, letter, rel in INSTALL:
        sha = snap[row]["columns"][letter]["single"]
        r = E.keep_ruling(idx, row, letter, sha)
        if r:
            res = L.install(MOD, rel, sha, ruling_id=r["id"], dry_run=not apply)
        else:
            # rows enact's ingest reads as undecided (✕ clicked, no letter click) carry no keep ruling, but his
            # variant ticks are in the decisions file (variantsAt); a new slot displaces nothing
            res = L.install(MOD, rel, sha, reason=ME, dry_run=not apply,
                            provenance={"sheet": "therot_sheet_2026-10-05", "row": row, "variant_tick": letter})
        print(row, letter, rel, res["status"])
    for rel in RETIRE:
        if apply:
            print(rel, L.retire(f"{MOD}/Textures/{rel}", reason=ME)["status"])
        else:
            print(rel, "would retire")


if __name__ == "__main__":
    main("--apply" in sys.argv)
