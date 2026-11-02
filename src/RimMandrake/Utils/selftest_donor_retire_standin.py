#!/usr/bin/env python3
"""selftest_donor_retire_standin.py -- `donor_retire_census.py standin` sees every StandIn/ text (any *Path tag, patch
xpath defs), judges coverage per PICTURE against the artpipe queue, and names the states that block nothing yet
(COLLIDES, DONOR_DEF); plus the two installer guards from the same item (STANDINS_RETIRE_AS_OUR_COATS_ARRIVE):
bulk_accept_renders.own_text (a polluted / leafless sibling is no facing of the main text) and repoint_complete (a
repoint never outruns its renders -- the RM_TarSealing.xml incident).

    python3 src/RimMandrake/Utils/selftest_donor_retire_standin.py
"""
import json
import os
import sys
import tempfile
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "art"))
import donor_retire_census as DRC  # noqa: E402
import bulk_accept_renders as BA  # noqa: E402

FAILS = []


def check(cond, what, detail=""):
    print(("PASS " if cond else "FAIL ") + what + ("" if cond else "  -- %s" % (detail,)))
    if not cond:
        FAILS.append(what)


def write(p: Path, text: str = ""):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def png(p: Path):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b"\x89PNG\r\n\x1a\n")          # existence is all the census reads


DEFS = """<Defs>
  <TerrainDef><defName>RM_Grass</defName>
    <texturePath>StandIn/Terrain/AB_Grass</texturePath>
    <pollutedTexturePath>StandIn/Terrain/AB_Grass_Polluted</pollutedTexturePath></TerrainDef>
  <ThingDef><defName>RM_Tree</defName>
    <graphicData><texPath>StandIn/Plants/AB_Tree</texPath></graphicData>
    <plant><leaflessGraphicPath>StandIn/Plants/AB_TreeLeafless</leaflessGraphicPath></plant></ThingDef>
  <ThingDef><defName>RM_Beast</defName><graphicData><texPath>StandIn/Animal/Beast</texPath></graphicData></ThingDef>
  <ThingDef><defName>RM_Fern</defName><graphicData><texPath>StandIn/Plants/AB_Fern</texPath></graphicData></ThingDef>
</Defs>"""
PATCH = """<Patch><Operation Class="PatchOperationFindMod"><mods><li>Donor</li></mods><match Class="PatchOperationAdd">
  <xpath>/Defs/GeneDef[defName="Eyes_Gold"]</xpath>
  <value><renderNodeProperties><li><texPath>StandIn/Eyes/Gold</texPath></li></renderNodeProperties></value>
</match></Operation></Patch>"""


def fixture(t: Path):
    mod = t / "src/RimMandrake/ModA"
    write(mod / "Defs/Things.xml", DEFS)
    write(mod / "Patches/Eyes.xml", PATCH)
    tex = mod / "Textures/StandIn"
    for f in ("Terrain/AB_Grass", "Terrain/AB_Grass_Polluted", "Plants/AB_Fern", "Eyes/Gold",
              "Plants/AB_Tree/AB_TreeA", "Plants/AB_Tree/AB_TreeB", "Plants/AB_TreeLeafless/AB_TreeA",
              "Animal/Beast_east", "Animal/Beast_south", "Animal/Beast_north", "Animal/Beast_eastm"):
        png(tex / (f + ".png"))
    png(t / "src/RimUtinni/ModB/Textures/Plants/AB_Fern.png")       # another mod already ships the un-StandIn path
    art = t / "artpipe"
    for st in ("pending", "active", "done", "failed"):
        (art / st).mkdir(parents=True)
    return art


def job(art: Path, st: str, jid: str, ok: bool = True, **kw):
    write(art / st / f"{jid}.json", json.dumps({"id": jid, **kw}))
    if st == "done":
        write(art / st / f"{jid}.manifest.json", json.dumps({"status": "ok" if ok else "failed"}))
        if ok:
            png(art / "_artsrc" / jid / f"{jid}.png")


def run(t: Path, art: Path) -> dict:
    DRC.REPO, DRC.SRC = t, t / "src"
    return {r["text"]: r for r in DRC.standin(art=art)["rows"]}


def census():
    keep = DRC.REPO, DRC.SRC
    try:
        with tempfile.TemporaryDirectory() as td:
            t = Path(td)
            art = fixture(t)
            DRC.REPO, DRC.SRC = t, t / "src"
            texts = DRC.standin_texts()
            check(set(texts) == {"StandIn/Terrain/AB_Grass", "StandIn/Terrain/AB_Grass_Polluted",
                                 "StandIn/Plants/AB_Tree", "StandIn/Plants/AB_TreeLeafless", "StandIn/Animal/Beast",
                                 "StandIn/Plants/AB_Fern", "StandIn/Eyes/Gold"},
                  "the walk sees every *Path tag (texturePath, pollutedTexturePath, leaflessGraphicPath)", sorted(texts))
            check(texts.get("StandIn/Eyes/Gold", {}).get("defs") == ["Eyes_Gold"],
                  "a node patched onto a def is attributed to the def its xpath names", texts.get("StandIn/Eyes/Gold"))

            R = run(t, art)
            check(all(r["state"] in ("UNCOVERED", "COLLIDES", "DONOR_DEF") for r in R.values())
                  and R["StandIn/Terrain/AB_Grass"]["state"] == "UNCOVERED", "an empty queue covers nothing",
                  {k: r["state"] for k, r in R.items()})
            check(R["StandIn/Eyes/Gold"]["state"] == "DONOR_DEF", "a stand-in on a donor def only is DONOR_DEF",
                  R["StandIn/Eyes/Gold"]["state"])
            check(R["StandIn/Plants/AB_Fern"]["state"] == "COLLIDES",
                  "a path another mod of ours ships is COLLIDES", R["StandIn/Plants/AB_Fern"]["state"])

            # the main texture's job, back-filled with target_texpath, covers neither the polluted twin nor itself twice
            job(art, "pending", "dregen_RM_Grass_v1", target_def="RM_Grass", target_texpath="StandIn/Terrain/AB_Grass",
                install_to="src/RimMandrake/ModA/Textures/Terrain/AB_Grass.png")
            # a leafless job whose fill_queue target_texpath names the MAIN tree must not cover the main tree
            job(art, "pending", "dregen_RM_Tree_LeaflessA_v1", target_def="RM_Tree",
                target_texpath="StandIn/Plants/AB_Tree",
                install_to="src/RimMandrake/ModA/Textures/Plants/AB_TreeLeafless/AB_TreeA.png")
            job(art, "done", "dregen_RM_Tree_A_v1", target_def="RM_Tree",
                install_to="src/RimMandrake/ModA/Textures/Plants/AB_Tree/AB_TreeA.png")
            job(art, "pending", "dregen_RM_Beast_v1", target_def="RM_Beast",
                install_to="src/RimMandrake/ModA/Textures/Animal/Beast_{facing}.png")
            R = run(t, art)
            check(R["StandIn/Terrain/AB_Grass"]["state"] == "QUEUED", "a pending job at the exact path is QUEUED")
            check(R["StandIn/Terrain/AB_Grass_Polluted"]["state"] == "UNCOVERED",
                  "the main texture's job does not cover its polluted twin", R["StandIn/Terrain/AB_Grass_Polluted"])
            check(R["StandIn/Terrain/AB_Grass_Polluted"]["def_jobs_hint"] == ["dregen_RM_Grass_v1"],
                  "the def's other job is reported as a hint only")
            check(R["StandIn/Plants/AB_TreeLeafless"]["state"] == "QUEUED", "a leafless folder picture's job covers it")
            check(R["StandIn/Plants/AB_Tree"]["state"] == "UNCOVERED"
                  and R["StandIn/Plants/AB_Tree"]["pictures_owed"] == ["Plants/AB_Tree/AB_TreeB"],
                  "a random folder is covered per picture (B has no job); target_texpath back-fill is ignored",
                  R["StandIn/Plants/AB_Tree"])
            check(R["StandIn/Animal/Beast"]["state"] == "QUEUED"
                  and set(R["StandIn/Animal/Beast"]["pictures"]) == {"Animal/Beast_east", "Animal/Beast_south",
                                                                     "Animal/Beast_north"},
                  "a {facing} job covers every facing; masks are no picture", R["StandIn/Animal/Beast"].get("pictures"))

            job(art, "done", "dregen_RM_Tree_B_v1", ok=False, target_def="RM_Tree",
                install_to="src/RimMandrake/ModA/Textures/Plants/AB_Tree/AB_TreeB.png")
            check(run(t, art)["StandIn/Plants/AB_Tree"]["state"] == "FAILED",
                  "a done job whose manifest is not ok is no render (FAILED)")
            job(art, "done", "dregen_RM_Tree_B_v2", target_def="RM_Tree",
                install_to="src/RimMandrake/ModA/Textures/Plants/AB_Tree/AB_TreeB.png")
            check(run(t, art)["StandIn/Plants/AB_Tree"]["state"] == "RENDERED", "every picture rendered -> RENDERED")
            # GPT review 2026-11-01: a single-file job covers no facing; one landed facing hides no other
            (art / "pending" / "dregen_RM_Beast_v1.json").unlink()
            job(art, "pending", "dregen_RM_Beast_single_v1", target_def="RM_Beast",
                install_to="src/RimMandrake/ModA/Textures/Animal/Beast.png")
            check(run(t, art)["StandIn/Animal/Beast"]["state"] == "UNCOVERED",
                  "a single-file job at the base path covers none of its facings")
            png(t / "src/RimMandrake/ModA/Textures/Animal/Beast_south.png")
            b = run(t, art)["StandIn/Animal/Beast"]
            check(b["state"] == "UNCOVERED" and b["pictures_owed"] == ["Animal/Beast_east", "Animal/Beast_north"],
                  "one landed facing marks only itself LANDED", b)
            png(t / "src/RimMandrake/ModA/Textures/StandIn/Plants/AB_Tree/AB_Palm.png")
            check("Plants/AB_Tree/AB_Palm" in run(t, art)["StandIn/Plants/AB_Tree"]["pictures"],
                  "a picture whose name ends in m (Palm) is no mask")
            png(t / "src/RimMandrake/ModA/Textures/Terrain/AB_Grass_Polluted.png")
            check(run(t, art)["StandIn/Terrain/AB_Grass_Polluted"]["state"] == "LANDED",
                  "the un-StandIn twin on disk is LANDED (repoint owed)")

            (art / "active").rmdir()
            try:
                run(t, art)
                check(False, "an unreadable queue refuses to report")
            except SystemExit as e:
                check("SANITY FAIL" in str(e), "an unreadable queue refuses to report", e)
    finally:
        DRC.REPO, DRC.SRC = keep


def installer_guards():
    class Repo:
        path_texts = {"StandIn/T/AB_Grass", "StandIn/T/AB_Grass_Polluted", "StandIn/P/Moss", "StandIn/P/Moss_Leafless"}
    r = Repo()
    check(BA.own_text(r, "StandIn/T/AB_Grass", "StandIn/T/AB_Grass_Polluted"),
          "own_text: a polluted sibling drawn by its own element is not a facing")
    check(BA.own_text(r, "StandIn/P/Moss", "StandIn/P/Moss_Leafless/MossA"),
          "own_text: a picture in a sibling's random folder is not the main text's")
    check(not BA.own_text(r, "StandIn/T/AB_Grass", "StandIn/T/AB_Grass_south"), "own_text: a real facing still counts")
    check(not BA.own_text(r, "StandIn/P/Moss", "StandIn/P/Moss/MossA"), "own_text: the text's own folder still counts")
    r.path_texts = r.path_texts | {"StandIn/T/AB_Grass_north"}     # an icon names one facing on its own
    check(not BA.own_text(r, "StandIn/T/AB_Grass", "StandIn/T/AB_Grass_north"),
          "own_text: a facing another element also names is still owed by the repoint")

    rp = {"mod": "src/M", "from": "Things/ToolCabinet", "to": "Things/Vat/Vat"}
    rows = [{"dest": f"src/M/Textures/Things/Vat/Vat_{f}.png", "fix": dict(rp, kind="external")}
            for f in ("east", "south", "north")]
    other = [{"dest": "src/M/Textures/Terrain/X.png", "fix": {"from": "StandIn/Terrain/X", "to": "Terrain/X"}}]
    check(not BA.repoint_complete(rp, rows + other, {"src/M/Textures/Terrain/X.png"}),
          "repoint_complete: another render in the same mod does not license the repoint (RM_TarSealing.xml)")
    check(not BA.repoint_complete(rp, rows, {rows[0]["dest"], rows[1]["dest"]}),
          "repoint_complete: one facing short withholds it")
    check(BA.repoint_complete(rp, rows, {r["dest"] for r in rows}), "repoint_complete: every bound render in -> go")
    check(not BA.repoint_complete(rp, other, {"src/M/Textures/Terrain/X.png"}),
          "repoint_complete: a repoint no plan row binds never goes")


if __name__ == "__main__":
    census()
    installer_guards()
    print("RESULT:", "FAIL %d" % len(FAILS) if FAILS else "PASS")
    sys.exit(1 if FAILS else 0)
