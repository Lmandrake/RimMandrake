#!/usr/bin/env python3
"""selftest_subject.py — art/subject.py's guarantees (ART_SUBJECT_RESOLVER_1).

Part 1, a disposable fixture: canon exact/base-species/none with a searched trail; original (donor) names map
both ways; art bound by ledger texPath, by job target_def/target_original, by collected.jsonl; name matches are
whole-token (no B0 'Plant' folder alias, no B2 prefix); an RM_ stand-in drawn with a canon texture is NOT given
that canon entry; fill_queue.bind_subject fills target/originals/texPath/canon images from the resolver.
Part 2, a SANITY PROBE on the real repo + artpipe state dir: wraid (exact + base species) and bluedesert_ renders
must be found, or the run fails; an absent state dir is UNMEASURED, not a pass.
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "artpipe"))
import artledger as L  # noqa: E402
import subject as S  # noqa: E402

FAILS = []


def check(cond, msg, detail=""):
    print(("PASS " if cond else "FAIL ") + msg + ("" if cond else f"  [{str(detail)[:300]}]"))
    if not cond:
        FAILS.append(msg)


DEFS = """<Defs>
  <!-- Wraid -> RSW_Wraid -->
  <ThingDef><defName>RSW_Wraid</defName><label>wraid</label><race/></ThingDef>
  <PawnKindDef><defName>RSW_Wraid</defName><race>RSW_Wraid</race>
    <lifeStages><li><bodyGraphicData><texPath>swanimals/Wraid/Wraid</texPath></bodyGraphicData></li></lifeStages></PawnKindDef>
  <PawnKindDef><defName>RSW_WraidAlpha</defName><race>RSW_Wraid</race>
    <lifeStages><li><bodyGraphicData><texPath>swanimals/Wraid/Wraid</texPath></bodyGraphicData></li></lifeStages></PawnKindDef>
  <ThingDef><defName>RSW_Kinrath</defName><label>kinrath</label>
    <graphicData><texPath>Things/Kinrath/Kinrath</texPath></graphicData></ThingDef>
  <ThingDef><defName>RSW_VentStalker</defName><label>vent stalker</label>
    <graphicData><texPath>Things/Kinrath/Kinrath</texPath></graphicData></ThingDef>
  <ThingDef><defName>RM_Vellak</defName><label>vellak</label>
    <graphicData><texPath>Things/Kinrath/Kinrath</texPath></graphicData></ThingDef>
  <ThingDef><defName>RM_Lashgrass</defName><label>lashgrass</label><plant/>
    <graphicData><texPath>Things/Plant/RM_Lashgrass</texPath></graphicData></ThingDef>
  <ThingDef><defName>RM_Fuzzrunner</defName><label>fuzzrunner</label>
    <graphicData><texPath>Things/Fuzzrunner/Fuzzrunner</texPath></graphicData></ThingDef>
  <ThingDef><defName>RM_Nobody</defName><label>nobody</label></ThingDef>
</Defs>
"""


def fixture(tmp: Path) -> S.World:
    d = tmp / "src" / "RimStarWars" / "Fix" / "Defs"
    d.mkdir(parents=True)
    (d / "Fix.xml").write_text(DEFS)
    canon = tmp / "canon"
    for slug in ("wraid", "kinrath"):
        (canon / slug).mkdir(parents=True)
        (canon / slug / "description.md").write_text(f"# {slug}\n\n## Must show\n- legs\n")
        (canon / slug / "wookieepedia_canon_1.webp").write_bytes(b"x")
        (canon / slug / "donor_current_sprite.png").write_bytes(b"x")
    (canon / "INDEX.md").write_text("| slug | category | defName(s) |\n|---|---|---|\n"
                                    "| [wraid](wraid/description.md) | creature | RSW_Wraid |\n"
                                    "| [kinrath](kinrath/description.md) | creature | RSW_Kinrath |\n")
    ap = tmp / "artpipe"
    for fam in ("desert_swaca_wraid_east", "chill_plant_eldspar_east", "desertportb_plant_bloddle_south",
                "bluedesert_fuzz_east", "desert_lashgrass_north", "wraidhound_east", "fixjob_east", "coll_east",
                "origjob_east"):
        (ap / "_artsrc" / fam).mkdir(parents=True)
    (ap / "done").mkdir()
    (ap / "done" / "fixjob_east.json").write_text(json.dumps({"id": "fixjob_east", "target_def": "RM_Fuzzrunner"}))
    (ap / "done" / "origjob_east.json").write_text(json.dumps({"id": "origjob_east", "target_original": ["Wraid"]}))
    (ap / "collected.jsonl").write_text(json.dumps(
        {"job_id": "coll_east", "dest": "src/RimMandrake/X/Textures/Things/Plant/RM_Lashgrass_east.png"}) + "\n")
    idx = L.Index(events=[{"type": "variant", "sha": "a" * 64, "res": "swanimals/Wraid/Wraid", "kind": "repo"},
                          {"type": "variant", "sha": "b" * 64, "res": "Things/Plant/RM_Lashgrass", "kind": "git"}])
    facts = tmp / "facts"
    facts.mkdir()
    return S.World(src_root=tmp / "src", canon_root=canon, artpipe_root=ap, facts_root=facts, index=idx)


def fixture_tests(w: S.World):
    c = S.resolve_canon("RSW_Wraid", w)
    check(c["match"] == "exact" and c["confidence"] == "bound" and c["slug"] == "wraid", "canon: INDEX defName is exact+bound", c)
    check(all("donor_" not in Path(i).name for i in c["images"]) and len(c["images"]) == 1,
          "canon: images exclude the donor sprite", c["images"])
    c = S.resolve_canon("RSW_WraidAlpha", w)
    check(c["match"] == "base-species" and c["slug"] == "wraid" and c["confidence"] == "name-matched",
          "canon: RSW_WraidAlpha -> wraid as base species (A1)", c)
    c = S.resolve_canon("RSW_VentStalker", w)
    check(c["match"] == "base-species" and c["slug"] == "kinrath", "canon: RSW_ def drawn with a canon texture -> twin's entry", c)
    c = S.resolve_canon("RM_Vellak", w)
    check(c["match"] == "none", "canon: an RM_ stand-in drawn with a canon texture is NOT that creature", c)
    check(c["searched"]["canon dirs (exact)"] == ["vellak"] and "RM_Vellak" in c["searched"]["INDEX.md defNames"],
          "canon: none carries what was searched", c["searched"])
    check("vellak" in S.describe_none(c["searched"]), "describe_none names the keys tried")

    ours, orig = w.identify("Wraid")
    check(ours == "RSW_Wraid" and "Wraid" in orig, "identity: a donor name maps to our defName and stays an original", (ours, orig))
    r = S.resolve("Wraid", w)
    check(r["subject"] == "RSW_Wraid" and r["canon"]["slug"] == "wraid", "resolve: matching on the ORIGINAL name works", r["subject"])

    a = S.resolve_art("RSW_Wraid", w)
    by = {(x["confidence"], x["ref"]) for x in a["columns"]}
    check(("bound", "a" * 64) in by, "art: ledger variant of the def's texPath is bound", by)
    check(("bound", "origjob") in by, "art: a job whose target_original is our donor name is bound", by)
    check(("name-matched", "desert_swaca_wraid") in by, "art: whole-token job id match is name-matched", by)
    check(not any(r_ == "wraidhound" for _, r_ in by), "art: 'wraid' does not prefix-match 'wraidhound' (B2)", by)
    check(a["columns"][0]["confidence"] == "bound", "art: bound columns come first", a["columns"][:1])

    a = S.resolve_art("RM_Lashgrass", w)
    refs = {x["ref"]: x["confidence"] for x in a["columns"]}
    check("chill_plant_eldspar" not in refs and "desertportb_plant_bloddle" not in refs,
          "art: no 'Plant' folder-word alias (B0)", refs)
    check(refs.get("coll") == "bound", "art: collected.jsonl install at the def's texPath is bound", refs)
    check(refs.get("desert_lashgrass") == "name-matched", "art: plant's own render found by its name", refs)

    a = S.resolve_art("RM_Fuzzrunner", w)
    refs = {x["ref"]: x["confidence"] for x in a["columns"]}
    check(refs.get("fixjob") == "bound", "art: job target_def binds", refs)
    check("bluedesert_fuzz" not in refs, "art: 'fuzz' render is not the fuzzrunner's (B2)", refs)

    a = S.resolve_art("RM_Nobody", w)
    check(a["columns"] == [] and a["searched"]["name keys (whole-token)"] and a["searched"]["render families"] > 0,
          "art: none still reports the keys and sources searched", a["searched"])

    import fill_queue  # noqa: E402
    b = fill_queue.bind_subject({"id": "x", "target_def": "Wraid"}, world=w)
    check(b["target_def"] == "RSW_Wraid" and "Wraid" in b["target_original"], "bind: donor target maps to ours, keeps the original", b)
    check(b.get("target_canon") == "wraid" and len(b.get("canon_reference", [])) == 1,
          "bind: canon images default from the resolver", b)
    check(b.get("target_texpath") == "swanimals/Wraid/Wraid", "bind: texPath defaults to the def's single body texPath", b)
    b = fill_queue.bind_subject({"id": "x", "target_def": "RM_Vellak"}, world=w)
    check("canon_reference" not in b and "target_canon" not in b, "bind: no canon images for a stand-in", b)


def live_probe():
    w = S.World()
    if not (w.artpipe / "_artsrc").is_dir():
        print(f"artpipe state dir {w.artpipe} absent — live probe UNMEASURED, not a pass or a fail")
        return
    fams = w.families
    nblue = sum(1 for f in fams if f.lower().startswith("bluedesert_"))
    check(nblue > 0, f"probe: bluedesert_ render families visible ({nblue})", nblue)
    c = S.resolve_canon("RSW_Wraid", w)
    check(c["slug"] == "wraid" and c["confidence"] == "bound", "probe: RSW_Wraid canon is wraid, bound", c["evidence"])
    c = S.resolve_canon("RSW_WraidAlpha", w)
    check(c["slug"] == "wraid" and c["match"] == "base-species", "probe: RSW_WraidAlpha -> wraid base species", c["match"])
    refs = {x["ref"] for x in S.resolve_art("RSW_Wraid", w)["columns"]}
    check("desert_swaca_wraid" in refs, "probe: desert_swaca_wraid found for RSW_Wraid", sorted(refs)[:8])
    refs = {x["ref"] for x in S.resolve_art("RM_Dorrak", w)["columns"]}
    check("bluedesert_dorrak" in refs, "probe: bluedesert_dorrak found for RM_Dorrak (2b)", sorted(refs)[:8])
    refs = {x["ref"] for x in S.resolve_art("RSW_Plant_Chakroot_Wild", w)["columns"]}
    check("chill_plant_eldspar" not in refs, "probe: no B0 plant alias on a real plant row", sorted(refs)[:8])


def main():
    tmp = Path(tempfile.mkdtemp(prefix="subject-selftest-"))
    try:
        fixture_tests(fixture(tmp))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    live_probe()
    print(f"\n{'ALL PASS' if not FAILS else str(len(FAILS)) + ' FAIL'}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
