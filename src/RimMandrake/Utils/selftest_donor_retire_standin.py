#!/usr/bin/env python3
"""selftest_donor_retire_standin.py -- `donor_retire_census.py standin` sees every StandIn/ text (any *Path tag, patch
xpath defs), judges coverage per PICTURE against the artpipe queue, and exits 0 ONLY when every text has a queued
dregen_ row or a finished render (FAILED, UNCOVERED and COLLIDES each exit 1); the regen gate files a texture a patch
of ours draws onto a donor's def; the stand-in job builder files only owed pictures; plus the two installer guards
from the same item (STANDINS_RETIRE_AS_OUR_COATS_ARRIVE):
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
# hermetic: every queue this test reads is a fixture; a throwaway data root keeps the art modules importable where the
# real one is unreachable (a blind checker) and keeps them off it where it is not
os.environ["RM_DATA_ROOT"] = tempfile.mkdtemp(prefix="selftest_drs_")
os.environ.pop("ARTPIPE_STATE", None)
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
            check(all(r["state"] in ("UNCOVERED", "COLLIDES") for r in R.values())
                  and R["StandIn/Terrain/AB_Grass"]["state"] == "UNCOVERED", "an empty queue covers nothing",
                  {k: r["state"] for k, r in R.items()})
            check(R["StandIn/Eyes/Gold"]["state"] == "UNCOVERED",
                  "a stand-in a patch draws onto a donor def is owed a job like any other (no DONOR_DEF pass)",
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


def gene_icon_rows():
    """donor_regen_jobs.standin: an UNCOVERED GeneDef iconPath gets a gene-icon job, not a generic sprite."""
    sys.path.insert(0, str(Path(__file__).resolve().parent / "art"))
    import donor_regen_jobs as DRJ
    from PIL import Image
    keep = DRJ.REPO, DRJ._def_words, DRC.standin, DRC.standin_files
    try:
        with tempfile.TemporaryDirectory() as td:
            t = Path(td)
            mod, text = "src/RimStarWars/Races", "StandIn/UI/Icons/Genes/Gene_Fast"
            f = t / mod / "Textures" / (text + ".png")
            f.parent.mkdir(parents=True)
            Image.new("RGBA", (64, 64)).save(f)
            DRJ.REPO = t
            DRJ._def_words = lambda defs: ("fast thing", "Goes fast.")
            DRC.standin = lambda art=None: {"rows": [{"state": "UNCOVERED", "text": text, "tags": ["iconPath"],
                                                      "files": [mod + "/Defs/Genes.xml"], "defs": ["X_Fast"]}]}
            DRC.standin_files = lambda m, tx: [(tx, None)]
            rows = DRJ.standin_rows()
            r = rows[0] if len(rows) == 1 else {}
            check(r.get("kind") == "icon" and "gene icon" in r.get("prompt", "")
                  and r.get("style_notes") == DRJ.GENE_ICON_STYLE
                  and r.get("install_to") == mod + "/Textures/UI/Icons/Genes/Gene_Fast.png"
                  and r.get("id") == "dregen_X_Fast_GeneFast_v1",
                  "a GeneDef iconPath stand-in gets a gene-icon job (Gene_PregnancyShort)", r)
            # a random folder with one picture owed: only that picture is filed, as a plant
            ptext = "StandIn/Things/Plants/RM_Tree"
            for n in ("RM_TreeA", "RM_TreeB"):
                g = t / mod / "Textures" / ptext / (n + ".png")
                g.parent.mkdir(parents=True, exist_ok=True)
                Image.new("RGBA", (64, 64)).save(g)
            DRC.standin = lambda art=None: {"rows": [{
                "state": "UNCOVERED", "text": ptext, "tags": ["texPath"], "files": [mod + "/Defs/Plants.xml"],
                "defs": ["RM_Tree"], "pictures": {"Things/Plants/RM_Tree/RM_TreeA": "UNCOVERED",
                                                  "Things/Plants/RM_Tree/RM_TreeB": "RENDERED"}}]}
            DRC.standin_files = lambda m, tx: [(tx + "/RM_TreeA", None), (tx + "/RM_TreeB", None)]
            rows = DRJ.standin_rows()
            check([(x["install_to"], x["kind"]) for x in rows]
                  == [(mod + "/Textures/Things/Plants/RM_Tree/RM_TreeA.png", "plant")],
                  "the stand-in builder files only the owed picture of a folder, as a plant job", rows)
    finally:
        DRJ.REPO, DRJ._def_words, DRC.standin, DRC.standin_files = keep


EXIT_DEFS = """<Defs>
  <ThingDef><defName>RM_Q</defName><graphicData><texPath>StandIn/Things/Q</texPath></graphicData></ThingDef>
  <ThingDef><defName>RM_R</defName><graphicData><texPath>StandIn/Things/R</texPath></graphicData></ThingDef>
  <ThingDef><defName>RM_Fern</defName><graphicData><texPath>StandIn/Plants/AB_Fern</texPath></graphicData></ThingDef>
</Defs>"""


def exit_code():
    """The census's own exit code (`standin` exits 0 only when every text is QUEUED/RENDERED): main() run end to end
    over a fixture tree and queue, so a broken BLOCKING or exit clause goes red here."""
    import contextlib
    import io
    keep = DRC.REPO, DRC.SRC, BA.ART
    try:
        with tempfile.TemporaryDirectory() as td:
            t = Path(td)
            mod = t / "src/RimMandrake/ModA"
            write(mod / "Defs/Things.xml", EXIT_DEFS)
            write(mod / "Patches/Eyes.xml", PATCH)
            for f in ("Things/Q", "Things/R", "Plants/AB_Fern", "Eyes/Gold"):
                png(mod / "Textures/StandIn" / (f + ".png"))
            png(t / "src/RimUtinni/ModB/Textures/Plants/AB_Fern.png")
            art = t / "artpipe"
            for st in ("pending", "active", "done", "failed"):
                (art / st).mkdir(parents=True)
            DRC.REPO, DRC.SRC, BA.ART = t, t / "src", art

            def rc():
                out = io.StringIO()
                with contextlib.redirect_stdout(out):
                    code = DRC.main(["standin"])
                return code, {r["text"]: r["state"] for r in DRC.standin(art=art)["rows"]}

            job(art, "pending", "dregen_RM_Q_v1", target_def="RM_Q", install_to=str(mod.relative_to(t)) +
                "/Textures/Things/Q.png")
            code, st = rc()
            check(code == 1 and st["StandIn/Things/R"] == "UNCOVERED" and st["StandIn/Eyes/Gold"] == "UNCOVERED",
                  "standin exits 1 while a text is UNCOVERED (a patch-drawn donor-def text too)", (code, st))
            job(art, "pending", "dregen_Eyes_Gold_v1", target_def="Eyes_Gold", install_to=str(mod.relative_to(t)) +
                "/Textures/Eyes/Gold.png")
            job(art, "done", "dregen_RM_R_v1", ok=False, target_def="RM_R", install_to=str(mod.relative_to(t)) +
                "/Textures/Things/R.png")
            code, st = rc()
            check(code == 1 and st["StandIn/Things/R"] == "FAILED" and "UNCOVERED" not in st.values(),
                  "standin exits 1 while a text is FAILED (nothing UNCOVERED)", (code, st))
            job(art, "done", "dregen_RM_R_v2", target_def="RM_R", install_to=str(mod.relative_to(t)) +
                "/Textures/Things/R.png")
            code, st = rc()
            check(code == 1 and st == {"StandIn/Things/Q": "QUEUED", "StandIn/Things/R": "RENDERED",
                                       "StandIn/Plants/AB_Fern": "COLLIDES", "StandIn/Eyes/Gold": "QUEUED"},
                  "COLLIDES alone blocks: a text whose un-StandIn path another mod ships has no render (exit 1)",
                  (code, st))
            (t / "src/RimUtinni/ModB/Textures/Plants/AB_Fern.png").unlink()     # the rename landed: path is free
            job(art, "pending", "dregen_RM_Fern_v1", target_def="RM_Fern", install_to=str(mod.relative_to(t)) +
                "/Textures/Plants/AB_Fern.png")
            code, st = rc()
            check(code == 0 and set(st.values()) <= {"QUEUED", "RENDERED"},
                  "standin exits 0 only when every text is QUEUED/RENDERED", (code, st))

            # the committed-snapshot route: --snapshot freezes the jobs read, --queue rereads them with no artpipe
            snap = t / "snap.json"
            with contextlib.redirect_stdout(io.StringIO()):
                code_live = DRC.main(["standin", "--snapshot", str(snap)])
            live = {r["text"]: r["state"] for r in DRC.standin(art=art)["rows"]}
            BA.ART = t / "no_artpipe_here"
            with contextlib.redirect_stdout(io.StringIO()):
                code_q = DRC.main(["standin", "--queue", str(snap)])
            q = {r["text"]: r["state"] for r in DRC.standin(queue=snap)["rows"]}
            ids = {j["id"] for j in json.loads(snap.read_text())["jobs"]}
            check(code_live == code_q == 0 and q == live,
                  "--queue <snapshot> judges exactly as the live queue it froze, with no artpipe present",
                  (code_live, code_q, q, live))
            check("dregen_RM_R_v1" in ids and "dregen_RM_Q_v1" in ids,
                  "the snapshot keeps every job that bears on a StandIn text (failed ones too)", ids)
            write(mod / "Defs/Late.xml", '<Defs><ThingDef><defName>RM_S</defName><graphicData>'
                  '<texPath>StandIn/Things/S</texPath></graphicData></ThingDef></Defs>')
            png(mod / "Textures/StandIn/Things/S.png")
            with contextlib.redirect_stdout(io.StringIO()):
                code_q = DRC.main(["standin", "--queue", str(snap)])
            check(code_q == 1 and DRC.standin(queue=snap)["rows"] and
                  {r["text"]: r["state"] for r in DRC.standin(queue=snap)["rows"]}["StandIn/Things/S"] == "UNCOVERED",
                  "a StandIn text added after the snapshot reads UNCOVERED and exits 1 until it is retaken", code_q)
            for bad in ("", '{"captured_utc": "x", "jobs": []}', '{"jobs": [{"id": 1}]}'):
                snap.write_text(bad)
                try:
                    DRC.standin(queue=snap)
                    refused = False
                except SystemExit as e:
                    refused = "SANITY FAIL" in str(e)
                check(refused, "an unreadable, empty or malformed snapshot is refused, never read as all-clear", bad)
    finally:
        DRC.REPO, DRC.SRC, BA.ART = keep


def gate_patch_defs():
    """regen_eligibility: a def our XML never defines is no renamed-away def when a patch of ours draws a texture on it
    (Hutt eyes on [LFS] genes, HUTT_EYES_DECIDE_GENE_IS_NOT_OURS); a def nothing of ours names still is."""
    import regen_eligibility as RE

    class G:
        def_tex, patch_defs, bound_subject = {}, {"Eyes_Gold"}, {}
    check(RE.Gate._def_alias(G(), "Eyes_Gold") is None, "a patch-drawn donor def is judged, not refused as renamed")
    check("no longer exists" in (RE.Gate._def_alias(G(), "Eyes_Gone") or ""), "an unnamed def is still refused")
    G.bound_subject = {"eyes_gold": [("x", "binding b1 job j1")]}
    check("renders are bound" in (RE.Gate._def_alias(G(), "Eyes_Gold") or ""),
          "a patch-drawn def with renders bound to it is still refused as regenerated")


if __name__ == "__main__":
    census()
    gate_patch_defs()
    exit_code()
    installer_guards()
    gene_icon_rows()
    print("RESULT:", "FAIL %d" % len(FAILS) if FAILS else "PASS")
    sys.exit(1 if FAILS else 0)
