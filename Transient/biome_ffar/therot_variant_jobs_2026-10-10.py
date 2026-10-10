#!/usr/bin/env python3
"""Build the artpipe job list for The Rot sheet's "two more (improved, more realistic) variants" notes, plus the
AA_AngelMoth south redraw and a second Snoruuk variant set. Each variant job references the picture he picked on the
sheet (never a ✕'d one). Writes Transient/biome_ffar/therot_variant_jobs_2026-10-10.json for fill_queue.py."""
import json, re, sys
sys.path.insert(0, "src/RimMandrake/Utils/art")
import artledger as L  # noqa: E402

snap = json.load(open("infrastructure/state/art/sheets/therot_sheet_2026-10-05.snapshot.json"))["rows"]
dec = json.load(open("Transient/biome_ffar/therot_sheet_2026-10-05.decisions.json"))["decisions"]
names = open("src/RimMandrake/TheRot/Patches/RotSpecies_NamesAndSizes.xml", encoding="utf-8").read()
flora = "".join(open(f, encoding="utf-8").read() for f in [
    "src/RimMandrake/TheRot/Defs/ThingDefs_Plants/RM_RotSporeKit_Flora.xml",
    "src/RimMandrake/TheRot/Defs/ThingDefs_Plants/RM_RotSporeKit_GuardianGroves.xml",
    "src/RimMandrake/TheRot/Defs/ThingDefs_Plants/RM_PaleTree.xml"])
ROWS = ["AB_Bryolux", "AB_DribblingCap", "AB_GiantAgarilux", "AB_GlowingAgarilux", "AB_Glowstool", "AB_LilacBeacon",
        "AB_SlimyPholiota", "AB_WitchesOyster", "RM_AgelessCap", "RM_BlastpodShroom", "RM_Brightbell", "RM_CrimsonCap",
        "RM_FalseFruit", "RM_FlakespireFungus", "RM_FruitingBodies", "RM_MortalMorelPlant", "RM_Nuitae", "RM_PaleTree",
        "RM_Pusmelon", "RM_RegenerantVeil", "RM_Sagecrust", "RM_Skulltop", "RM_VioletWimple", "RM_Wrinklecap"]
idx = L.Index()


def label_desc(dn):
    m = re.search(r'defName="%s"\]/label</xpath>\s*<value><label>([^<]*)' % dn, names)
    d = re.search(r'defName="%s"\]/description</xpath>\s*<value><description>([^<]*)' % dn, names)
    if m:
        return m.group(1), d.group(1) if d else ""
    b = re.search(r'<defName>%s</defName>\s*<label>([^<]*)</label>\s*<description>([^<]*)' % dn, flora)
    return b.group(1), b.group(2)


jobs = []
for row in ROWS:
    v, r = dec[row], snap[row]
    letter = v["decision"] if v["decision"] in r["columns"] else "A"
    sha = r["columns"][letter]["single"]
    assert not idx.is_purged(sha) and sha not in (v.get("purge") or []), row
    lab, desc = label_desc(row)
    note = v["note"]
    for suf, form in (("a", "a younger, sparser specimen"), ("b", "an older, fuller specimen")):
        jobs.append({
            "id": f"rotvar_{L.subject_key(row)}_{suf}_v1", "rimflow_item_id": "BIOME_FLORAFAUNA_ART_REVIEW_1",
            "target_def": row,
            "prompt": f"Owner's note, verbatim, overrides everything below: \"{note}\" RimWorld plant sprite of the "
                      f"{lab} ({desc}), painterly vanilla-RimWorld house style, realistic natural-history rendering. "
                      f"Draw a NEW, improved, more realistic variant of the same species, {form}, so it can sit beside "
                      f"the attached picture in a Graphic_Random set: same species, same palette and anatomy, different "
                      f"individual growth form. The attached image is the picture he picked, anatomy guidance only, "
                      f"not a sprite to copy.",
            "canvas_w": 256, "canvas_h": 256, "facings": [], "priority": 0, "owner_note": note,
            "canon_reference": [str(L.store_path(sha))], "biome_neutral": True})

# AA_AngelMoth: "Regenerate S" — he ✕'d render B's south and kept B east/north as variants
am = snap["AA_AngelMoth"]["columns"]["B"]
jobs.append({"id": "rotrow_angelmoth_south_v1", "rimflow_item_id": "BIOME_FLORAFAUNA_ART_REVIEW_1",
             "target_def": "AA_AngelMoth",
             "prompt": "Owner's note, verbatim, overrides everything below: \"Regenerate S. Otherwise accept. Rename and "
                       "regenerate description.\" RimWorld sprite of the angel moth, painterly "
                       "vanilla-RimWorld house style. The attached east and north pictures are the owner's kept variant "
                       "of this creature; draw this same animal from the front, eyes toward the viewer, matching those pictures in palette, anatomy and finish.",
             "canvas_w": 256, "canvas_h": 256, "facings": ["south"], "priority": 0,
             "owner_note": "Regenerate S. Otherwise accept. Rename and regenerate description.",
             "canon_reference": [str(L.store_path(am["east"])), str(L.store_path(am["north"]))], "biome_neutral": True})
# Snoruuk: "... offer some variants to choose from" — enact filed one set (v1); a second set
sn = snap["Snoruuk"]["columns"]["A"]["south"]
jobs.append({"id": "rotrow_snoruuk_v2", "rimflow_item_id": "BIOME_FLORAFAUNA_ART_REVIEW_1", "target_def": "Snoruuk",
             "prompt": "Owner's note, verbatim, overrides everything below: \"Regenerate following the MLIE donor art + the "
                       "canon art example carefully. Make it as realistic as you can and offer some variants to choose "
                       "from\" RimWorld sprite of the snoruuk, painterly vanilla-RimWorld house style, realistic. A second "
                       "variant for him to choose from: same species and anatomy as the attached in-game donor picture, "
                       "a different individual (posture, wear, colouring within the species).",
             "canvas_w": 256, "canvas_h": 256, "facings": ["east", "south", "north"], "priority": 0,
             "owner_note": "Regenerate following the MLIE donor art + the canon art example carefully. Make it as "
                           "realistic as you can and offer some variants to choose from",
             "canon_reference": [str(L.store_path(sn)), "/home/mandrake/rm/bench/design/RimStarWars/canon_references/snoruuk/wookieepedia_snoruuk.jpg"], "biome_neutral": True})
for j in jobs:
    for p in j["canon_reference"]:
        assert "canon_references" in p or L.store_has(p.rsplit("/", 1)[1][:64]), (j["id"], p)
json.dump(jobs, open("Transient/biome_ffar/therot_variant_jobs_2026-10-10.json", "w"), indent=1)
print(len(jobs), "jobs")
