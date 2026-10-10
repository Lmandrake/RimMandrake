#!/usr/bin/env python3
"""The Rot sheet fix pass (therot_verify_2026-10-10.md): retire through the art ledger
  - Brightbell_p3a: pixel-identical re-encode of render B (465c0328) he ✕'d; the re-encoded bytes are purged too
  - BMT_PusmelonB / BMT_SagecrustB: never shown on the sheet, drew beside his single pick
  - _p3a/_p3b duplicates of pictures already installed under the sheet's names (each picked image present once)
    python3 Transient/biome_ffar/therot_fix_2026-10-10.py [--apply]
"""
import sys, json
sys.path.insert(0, "src/RimMandrake/Utils/art")
import artledger as L  # noqa: E402

MOD = "src/RimMandrake/TheRot"
P = "RotSporeKit/Things/Plant/"
ME = "script:Transient/biome_ffar/therot_fix_2026-10-10.py"
XD = P + "Brightbell/Brightbell_p3a.png"
RETIRE = [XD, P + "Pusmelon/BMT_PusmelonB.png", P + "Sagecrust/BMT_SagecrustB.png",
          # duplicates (pixel-identical or resized-identical) of: Arpeau_C/_B, Nuitae_B/_C, ShinecapGrown_b/_c,
          # ShinecapImmature_d/_e, Brightbell_A (pick C), MortalMorel_A (pick B)
          P + "Arpeau/Arpeau_p3a.png", P + "Arpeau/Arpeau_p3b.png",
          P + "Nuitae/Nuitae_p3a.png", P + "Nuitae/Nuitae_p3b.png",
          P + "Shinecap/ShinecapGrown/ShinecapGrown_p3a.png", P + "Shinecap/ShinecapGrown/ShinecapGrown_p3b.png",
          P + "Shinecap/ShinecapImmature/ShinecapImmature_p3a.png", P + "Shinecap/ShinecapImmature/ShinecapImmature_p3b.png",
          P + "Brightbell/Brightbell_p3b.png", P + "MortalMorel/MortalMorel_p3a.png"]


def main(apply):
    note = json.load(open("Transient/biome_ffar/therot_sheet_2026-10-05.decisions.json"))["decisions"]["RM_Brightbell"]["note"]
    xd_sha = None
    for rel in RETIRE:
        if not apply:
            print(rel, "would retire"); continue
        r = L.retire(f"{MOD}/Textures/{rel}", reason=ME)
        print(rel, r["status"], (r.get("old") or "")[:8])
        if rel == XD and r["status"] == "retired":
            xd_sha = r["old"]
    if apply and xd_sha:
        print("purge", xd_sha[:8], L.purge(xd_sha, owner_said=note,
              via="Transient/biome_ffar/therot_sheet_2026-10-05.decisions.json (✕ B 465c0328; these bytes are its "
                  "pixel-identical re-encode)"))


if __name__ == "__main__":
    main("--apply" in sys.argv)
