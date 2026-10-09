#!/usr/bin/env python3
"""selftest_enact.py — `art.py enact` on a fixture sheet: one pass ingests, installs the pick, queues the redo,
purges the free ✕ and lists the protected ones as CONFLICTS, cuts a row from ITS biome only (def + egg + texture
deleted when nothing else names them; a def another biome still uses is kept), holds --hold rows, leaves a note
as a TODO until --mark-done; the dry run changes nothing; a second --apply is a no-op; ingest is idempotent by
content whatever path spells the decisions file. Fixture lives under /home/mandrake/rm/scratch/BENCH (never /tmp).
"""
from __future__ import annotations

import hashlib
import json
import os
import random
import shutil
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRATCH = Path(os.environ.get("ENACT_SELFTEST_ROOT") or "/home/mandrake/rm/scratch/BENCH")
FAILS = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def noise_png(seed: int) -> bytes:
    import io
    from PIL import Image
    rnd = random.Random(seed)
    im = Image.new("RGBA", (64, 64))
    im.putdata([(rnd.randrange(256), rnd.randrange(256), rnd.randrange(256), 255) for _ in range(64 * 64)])
    b = io.BytesIO()
    im.save(b, "PNG")
    return b.getvalue()


def tree_digest(root: Path) -> str:
    h = hashlib.sha256()
    for p in sorted(root.rglob("*")):
        if p.is_file():
            h.update(str(p.relative_to(root)).encode())
            h.update(p.read_bytes())
    return h.hexdigest()


MOD = "src/RimMandrake/TestMod"
BIOME_XML = """<?xml version="1.0" encoding="utf-8"?>
<Defs>
  <BiomeDef>
    <defName>RM_TestBiome</defName>
    <wildAnimals>
      <RM_Foo>0.5</RM_Foo>
      <RM_Cut>0.2</RM_Cut>  <!-- the cut creature -->
      <RM_Shared>0.1</RM_Shared>
    </wildAnimals>
  </BiomeDef>
  <BiomeDef>
    <defName>RM_OtherBiome</defName>
    <wildAnimals>
      <RM_Shared>0.3</RM_Shared>
    </wildAnimals>
  </BiomeDef>
</Defs>
"""
RACES_XML = """<?xml version="1.0" encoding="utf-8"?>
<Defs>
  <ThingDef ParentName="AnimalThingBase">
    <defName>RM_Cut</defName>
    <race><useMeatFrom>Cow</useMeatFrom></race>
    <comps><li Class="CompProperties_EggLayer"><eggFertilizedDef>RM_CutEgg</eggFertilizedDef></li></comps>
  </ThingDef>
  <PawnKindDef>
    <defName>RM_Cut</defName>
    <race>RM_Cut</race>
    <lifeStages><li><bodyGraphicData><texPath>Things/Pawn/Animal/RM_Cut/RM_Cut</texPath></bodyGraphicData></li></lifeStages>
  </PawnKindDef>
  <ThingDef>
    <defName>RM_CutEgg</defName>
  </ThingDef>
  <ThingDef ParentName="AnimalThingBase">
    <defName>RM_Shared</defName>
  </ThingDef>
  <ThingDef ParentName="AnimalThingBase">
    <defName>RM_Foo</defName>
  </ThingDef>
</Defs>
"""
PATCH_XML = """<?xml version="1.0" encoding="utf-8"?>
<Patch>
  <Operation Class="PatchOperationAdd">
    <xpath>Defs/BiomeDef[defName="RM_TestBiome"]/wildAnimals</xpath>
    <value>
      <RM_Cut>0.4</RM_Cut>
      <RM_Patched>0.1</RM_Patched>
    </value>
  </Operation>
</Patch>
"""


def build(root: Path) -> dict:
    if root.exists():
        shutil.rmtree(root)
    src = root / "src"
    led = root / "ledger"
    store = root / "store"
    ap = root / "artpipe"
    for d in (led / "events", store, ap / "pending", ap / "active", ap / "done", ap / "failed",
              src / "RimMandrake/TestMod/About", src / "RimMandrake/TestMod/Defs/BiomeDefs",
              src / "RimMandrake/TestMod/Defs/ThingDefs_Races", src / "RimMandrake/TestMod/Patches"):
        d.mkdir(parents=True, exist_ok=True)
    os.environ.update(ART_LEDGER_DIR=str(led), ARTSTORE=str(store), ART_SRC_ROOT=str(src),
                      ENACT_ARTPIPE_ROOT=str(ap), ENACT_CENSUS=str(root / "census.json"), RIMFLOW_SEAT="TEST")
    (src / "RimMandrake/TestMod/About/About.xml").write_text("<ModMetaData><packageId>test.enact</packageId></ModMetaData>")
    (src / "RimMandrake/TestMod/Defs/BiomeDefs/Biomes.xml").write_text(BIOME_XML)
    (src / "RimMandrake/TestMod/Defs/ThingDefs_Races/Races.xml").write_text(RACES_XML)
    (src / "RimMandrake/TestMod/Patches/WildAnimals_Test.xml").write_text(PATCH_XML)
    (root / "census.json").write_text(json.dumps({"biomes": {"RM_TestBiome": {"rows": [
        {"key": "RM_Cut", "defNames": ["RM_Cut"]}]}}}))
    sys.path.insert(0, str(HERE))
    import artledger as L
    shas = {}
    for i, k in enumerate(("old", "new", "rej", "livex", "kept", "cut", "redo")):
        shas[k] = L.store_put_bytes(noise_png(i + 1))
    tex = src / "RimMandrake/TestMod/Textures"

    def place(rel, key):
        p = tex / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(L.store_get(shas[key]))
        return {"type": "live", "id": L.det_id("live", rel), "mod": MOD, "rel": rel, "sha": shas[key], "prev": None,
                "reason": "fixture", "ts": "2026-10-01T00:00:00"}
    evs = [place("Things/Pawn/Animal/RM_Foo/RM_Foo_east.png", "old"),
           place("Things/Pawn/Animal/RM_Bar/RM_Bar_east.png", "livex"),
           place("Things/Pawn/Animal/RM_Cut/RM_Cut_east.png", "cut"),
           place("Things/Pawn/Animal/RM_Redo/RM_Redo_east.png", "redo"),
           {"type": "ruling", "id": "keepfixture", "target": {"shas": [shas["kept"]], "row": "RM_Elsewhere",
            "column": "A"}, "verdict": "keep", "by": "owner", "trust": "ruled", "at": "2026-10-01T00:00:00Z",
            "via": "other_sheet.decisions.json", "subject_key": "elsewhere"}]
    for k, s in shas.items():
        evs.append({"type": "variant", "id": L.det_id("variant", k), "sha": s, "res": f"Things/Pawn/Animal/x/{k}",
                    "kind": "fixture"})
    with open(led / "events" / "TEST.jsonl", "w") as fh:
        for e in evs:
            fh.write(json.dumps(e) + "\n")
    g = "Things/Pawn/Animal/RM_Foo/RM_Foo"
    snap = {"sheetId": "test_sheet", "snapshotId": "s1", "biome": "RM_TestBiome", "rows": {
        "RM_Foo": {"columns": {"A": {"east": shas["old"]}, "B": {"east": shas["new"]}}, "graphic_of": {"A": g, "B": g},
                   "labels": {"A": "IN GAME — TestMod", "B": "render foo_v1"}, "res": g, "subject_key": "foo"},
        "RM_Redo": {"columns": {"A": {"east": shas["redo"]}}, "graphic_of": {"A": "Things/Pawn/Animal/RM_Redo/RM_Redo"},
                    "labels": {"A": "IN GAME — TestMod"}, "subject_key": "redo"},
        "RM_Cut": {"columns": {"A": {"east": shas["cut"]}}, "graphic_of": {"A": "Things/Pawn/Animal/RM_Cut/RM_Cut"},
                   "labels": {"A": "IN GAME — TestMod"}, "subject_key": "cut"},
        "RM_Shared": {"columns": {}, "subject_key": "shared"},
        "RM_Note": {"columns": {"A": {"east": shas["livex"]}}, "graphic_of": {"A": "Things/Pawn/Animal/RM_Bar/RM_Bar"},
                    "labels": {"A": "IN GAME — TestMod"}, "subject_key": "note"},
        "RM_HeldVine": {"columns": {"A": {"east": shas["old"]}}, "subject_key": "heldvine"}}}
    sp = root / "test_sheet.snapshot.json"
    sp.write_text(json.dumps(snap))
    at = "2026-10-08T10:00:00.000Z"
    doc = {"savedBy": "review-sheet-sidecar", "writeCount": 9, "sheetId": "test_sheet", "snapshot": str(sp),
           "snapshotId": "s1", "biome": "RM_TestBiome", "decisions": {
               "RM_Foo": {"decision": "B", "at": at, "decidedAt": at, "note": "",
                          "purge": [shas["rej"], shas["livex"], shas["kept"]]},
               "RM_Redo": {"decision": "redo", "at": at, "decidedAt": at, "note": "make it scarier"},
               "RM_Cut": {"decision": "hold", "at": at, "decidedAt": at, "note": "Just cut this, not needed"},
               "RM_Shared": {"decision": "hold", "at": at, "decidedAt": at, "note": "cut this"},
               "RM_Note": {"decision": "A", "at": at, "decidedAt": at, "note": "make it 0.3 cells"},
               "RM_HeldVine": {"decision": "redo", "at": at, "decidedAt": at, "note": "hold me", "purge": [shas["rej"]]},
               "RM_Untouched": {"decision": "A", "prefill": "A"}}}
    dp = root / "test_sheet.decisions.json"
    dp.write_text(json.dumps(doc))
    return {"root": root, "src": src, "store": store, "ap": ap, "shas": shas, "decisions": dp, "led": led}


def main():
    F = build(SCRATCH / f"enact_selftest_{os.getpid()}")
    import artledger as L
    import enact as E
    src, shas = F["src"], F["shas"]
    races = src / "RimMandrake/TestMod/Defs/ThingDefs_Races/Races.xml"
    biomes = src / "RimMandrake/TestMod/Defs/BiomeDefs/Biomes.xml"
    patch = src / "RimMandrake/TestMod/Patches/WildAnimals_Test.xml"
    foo = src / "RimMandrake/TestMod/Textures/Things/Pawn/Animal/RM_Foo/RM_Foo_east.png"
    cut_tex = src / "RimMandrake/TestMod/Textures/Things/Pawn/Animal/RM_Cut/RM_Cut_east.png"
    try:
        before = tree_digest(F["root"])
        R = E.enact(F["decisions"], apply=False, holds=["vine"], no_deploy=True)
        out = E.report(R)
        P = R["plan"]
        check(R["ok"], "dry run succeeds")
        check(tree_digest(F["root"]) == before, "dry run changes nothing on disk (ledger, store, src, queue)")
        check(R["ingest_new"] > 0, f"dry run counts the rulings ingest would add ({R['ingest_new']})")
        check(len(P["install"]) == 1 and P["install"][0]["rel"].endswith("RM_Foo_east.png"), "plans the RM_Foo pick B install")
        check(len(P["purge"]) == 1 and P["purge"][0]["sha"] == shas["rej"], "plans exactly the one free ✕")
        conf = "\n".join(R["conflicts"])
        check(shas["livex"][:12] in conf and "live at" in conf, "a ✕ on a live picture is a CONFLICT")
        check(shas["kept"][:12] in conf and "owner-kept" in conf, "a ✕ on an owner-kept picture is a CONFLICT")
        check(len(P["queue"]) == 1 and P["queue"][0]["row"] == "RM_Redo", "plans one redraw (RM_Redo)")
        check(P["held"] == ["RM_HeldVine"], "--hold vine skips the held row in every step")
        check(any(t.startswith("RM_Note: note not enacted") for t in R["todo"]), "a note that is no redo is a TODO, not a guess")
        cuts = {c["row"]: c["plan"] for c in P["cuts"]}
        check(set(cuts) == {"RM_Cut", "RM_Shared"}, "hold + 'cut' notes are cuts")
        check(set(cuts["RM_Cut"]["deleted"]) == {"RM_Cut", "RM_CutEgg"}, "cut deletes the def and the egg it alone used")
        check(len([s for s in cuts["RM_Cut"]["sites"] if "region" in s]) == 2, "cut finds the inline AND the patch-added roster row")
        check(not cuts["RM_Shared"]["deleted"] and "RM_Shared" in cuts["RM_Shared"]["kept"],
              "a def another biome still uses is kept (sheet cut is scoped to its biome)")
        check(cuts["RM_Cut"]["tex_retire"] == ["Things/Pawn/Animal/RM_Cut/RM_Cut"], "cut retires the def's texture")
        check("CONFLICTS (2)" in out and "TODO (1)" in out, "report lists conflicts and TODOs")

        # a LATER owner keep of the live picture on this row (another decisions file) must not be undone by re-enacting this one
        evf = F["led"] / "events" / "TEST.jsonl"
        evtxt = evf.read_text()
        evf.write_text(evtxt + json.dumps({"type": "ruling", "id": "newerkeep", "target": {"shas": [shas["old"]], "row": "RM_Foo", "column": "A"},
                                           "verdict": "keep", "by": "owner", "trust": "ruled", "at": "2026-10-09T00:00:00Z",
                                           "via": "later_sheet.decisions.json", "subject_key": "foo"}) + "\n")
        Pn = E.build_plan(F["decisions"], ["vine"])
        check(not Pn["install"] and any("RM_Foo" in c and "owner-kept" in c for c in Pn["conflicts"]),
              "a pick is not installed over a LATER same-row owner keep from another file (CONFLICT)")
        evf.write_text(evtxt)
        Pe = E.build_plan(F["decisions"], ["vine"])
        check(len(Pe["install"]) == 1, "...and with that later keep gone the pick installs again")
        # stale letters: a used letter the ruled snapshot never had, clicked before the current snapshot was built
        import ingest as I
        ruled = {"rows": {"R": {"columns": {"A": {"east": "1"}}}}}
        now = {"built": "2026-10-09T10:00:00-0700", "rows": {"R": {"columns": {"A": {"east": "1"}, "F": {"east": "2"}}}}}
        d_old = {"decisions": {"R": {"decision": "F", "at": "2026-10-09T16:00:00.000Z"}}}
        d_new = {"decisions": {"R": {"decision": "F", "at": "2026-10-09T18:30:00.000Z"}}}
        check(I.stale_letter_rows(d_old, ruled, now) == {"R": ["F"]}, "letter new since the ruled snapshot, clicked before the rebuild: stale")
        check(I.stale_letter_rows(d_new, ruled, now) == {}, "...clicked after the rebuild: fine")
        check(I.stale_letter_rows({"decisions": {"R": {"decision": "A", "at": "2026-10-09T16:00:00Z"}}}, ruled, now) == {},
              "a letter the ruled snapshot had is left to letter_mismatches")
        P_st = E.build_plan(F["decisions"], ["vine"], stale={"RM_Foo": ["B"]})
        check(not P_st["install"] and any(c.startswith("RM_Foo: letter(s) B") for c in P_st["conflicts"]), "a stale row is a CONFLICT and does nothing")
        # clear_followed: a sidecar save landing between read and replace is merged over, never lost
        cf = F["root"] / "cf.json"
        cf.write_text(json.dumps({"decisions": {"X": {"note": "do it", "at": "a"}, "Y": {"note": "", "decision": "A"}}}))
        real_fsync, hit = E.os.fsync, []
        def racing_fsync(fd):
            if not hit:
                hit.append(1)
                d = json.loads(cf.read_text())
                d["decisions"]["Y"]["decision"] = "B"
                cf.write_text(json.dumps(d))
            return real_fsync(fd)
        E.os.fsync = racing_fsync
        try:
            got = E.clear_followed(cf, {"X": {"note": "do it", "by": ["j1"]}})
        finally:
            E.os.fsync = real_fsync
        dcf = json.loads(cf.read_text())["decisions"]
        check(got == ["X"] and dcf["Y"]["decision"] == "B" and dcf["X"]["note"] == "" and dcf["X"]["notes_followed"][0]["note"] == "do it",
              "clear_followed redoes its merge when his save lands mid-write (his edit survives)")
        check(not list(F["root"].glob(".enact-*.tmp")), "clear_followed leaves no temp file")

        JOBS = F["root"] / "jobs_out.json"      # never Transient/ of the real repo
        R = E.enact(F["decisions"], apply=True, holds=["vine"], no_deploy=True, redo_jobs_out=JOBS)
        check(R["ok"], "apply succeeds")
        check(foo.read_bytes() == L.store_get(shas["new"]), "pick B is installed in the live slot")
        check(not L.store_has(shas["rej"]) and L.store_has(shas["livex"]) and L.store_has(shas["kept"]),
              "the free ✕ is purged; the protected two are untouched")
        bt, rt, pt = biomes.read_text(), races.read_text(), patch.read_text()
        check("<RM_Cut>" not in bt and "<RM_Foo>0.5" in bt, "cut row gone from the inline roster, others stay")
        check(bt.count("<RM_Shared>") == 1 and "RM_OtherBiome" in bt and "<RM_Shared>0.3" in bt,
              "RM_Shared cut from RM_TestBiome only; RM_OtherBiome keeps it")
        check("<RM_Cut>" not in pt and "<RM_Patched>" in pt, "patch-added row removed, its neighbour kept")
        check("RM_CutEgg" not in rt and "<defName>RM_Cut</defName>" not in rt and "<defName>RM_Shared</defName>" in rt,
              "RM_Cut ThingDef + PawnKindDef + egg deleted, RM_Shared def kept")
        import xml.etree.ElementTree as ET
        try:
            for f in (bt, rt, pt):
                ET.fromstring(f)
            ok = True
        except ET.ParseError:
            ok = False
        check(ok, "every edited XML file still parses")
        check(not cut_tex.exists(), "the cut def's texture is retired (archived in the store, removed)")
        jobs = list((F["ap"] / "pending").glob("*.json"))
        check(R["queued_jobs"] == 1 and jobs and all(json.loads(j.read_text()).get("owner_note") == "make it scarier"
                                                     and json.loads(j.read_text()).get("priority") == 0 for j in jobs),
              f"redo queued at priority 0 with his note verbatim ({len(jobs)} job file(s))")
        mid = tree_digest(F["root"] / "src") + tree_digest(F["led"]) + tree_digest(F["ap"])

        # a followed note comes OFF the open notes (owner, 2026-10-08): queued, cut -> notes_followed, his words kept
        D = json.loads(F["decisions"].read_text())["decisions"]
        nf = D["RM_Redo"].get("notes_followed") or [{}]
        check(D["RM_Redo"]["note"] == "" and nf[0].get("note") == "make it scarier" and nf[0].get("followed_by")
              and nf[0].get("when") and nf[0].get("at"), "a queued note moves to notes_followed (exact words, job ids, when)")
        check(D["RM_Cut"]["note"] == "" and D["RM_Cut"]["notes_followed"][0]["followed_by"] == ["cut"]
              and D["RM_Cut"]["notes_followed"][0]["note"] == "Just cut this, not needed", "an executed cut's note is followed by 'cut'")
        check(D["RM_Note"]["note"] == "make it 0.3 cells" and "notes_followed" not in D["RM_Note"]
              and D["RM_HeldVine"]["note"] == "hold me", "an un-enacted note and a held row keep their open note")
        check(D["RM_Foo"]["purge"] and D["RM_Redo"]["decision"] == "redo" and D["RM_Redo"]["at"] == "2026-10-08T10:00:00.000Z",
              "clearing a note leaves decision, at and picks untouched")
        check(R["notes_cleared"] and "notes followed, taken off" in E.report(R), "the report names the notes it took off")
        import ingest as I0
        stale = dict(D["RM_Redo"], note="make it scarier")       # a stale browser tab re-posting the followed text
        check(I0.open_note(stale) == "" and I0.open_note(dict(stale, note="make it scarier AND bluer")) != "",
              "a note identical to a followed one is not open; a new note is")
        # his new note typed before enact writes survives: clear only rows whose note STILL matches
        Dm = json.loads(F["decisions"].read_text())
        Dm["decisions"]["RM_Note"]["note"] = "make it 0.5 cells"
        F["decisions"].write_text(json.dumps(Dm))
        got = E.clear_followed(F["decisions"], {"RM_Note": {"note": "make it 0.3 cells", "by": ["mark-done"]}})
        check(got == [] and json.loads(F["decisions"].read_text())["decisions"]["RM_Note"]["note"] == "make it 0.5 cells",
              "a note he changed meanwhile is NOT removed")
        Dm["decisions"]["RM_Note"]["note"] = "make it 0.3 cells"
        F["decisions"].write_text(json.dumps(Dm))
        import serve_gated as SGT
        ops = {"RM_Redo": dict(D["RM_Redo"], note="make it scarier", notes_followed=None),
               "RM_Foo": {"decision": "B", "note": "fresh"}}
        ops["RM_Redo"].pop("notes_followed")
        g = SGT.guard_ops(ops, D)
        check(g["RM_Redo"]["note"] == "" and g["RM_Redo"]["notes_followed"] == D["RM_Redo"]["notes_followed"]
              and g["RM_Foo"] == ops["RM_Foo"], "server-side save drops a followed note and keeps the history")
        check(SGT.guard_ops({"RM_Redo": dict(ops["RM_Redo"], note="new words")}, D)["RM_Redo"]["note"] == "new words",
              "server-side save keeps a genuinely new note")

        R2 = E.enact(F["decisions"], apply=True, holds=["vine"], no_deploy=True, redo_jobs_out=JOBS)
        zero = (R2["ingest_new"], R2["installed"], R2["queued_jobs"], R2["purged"], R2["cut_rows"], R2["textures_retired"])
        check(zero == (0, 0, 0, 0, 0, 0), f"second --apply is a no-op {zero}")
        check(tree_digest(F["root"] / "src") + tree_digest(F["led"]) + tree_digest(F["ap"]) == mid,
              "second --apply writes nothing")

        # a ruled redraw whose job FAILED is re-filed, never counted as handled (bug 2026-10-08)
        ap = F["ap"]
        job = sorted((ap / "pending").glob("*.json"))[0]
        jid = job.stem
        job.rename(ap / "failed" / job.name)
        (ap / "failed" / f"{jid}.manifest.json").write_text(json.dumps({"id": jid, "status": "failed",
                                                                        "worker_status": "worker_error"}))
        R5 = E.enact(F["decisions"], apply=False, holds=["vine"], no_deploy=True)
        check([x["job"]["id"] for x in R5["plan"]["refile"]] == [jid] and not any(
            q.startswith("RM_Redo") for q in R5["plan"]["queued_already"]),
            "a failed-only redraw is planned for RE-FILE, not listed as already queued")
        check(E.ruling_status(F["decisions"])["rows"]["RM_Redo"]["state"] == "refiled", "ruling_status: failed, re-filed")
        R6 = E.enact(F["decisions"], apply=True, holds=["vine"], no_deploy=True, redo_jobs_out=JOBS)
        check(R6["refiled"] == 1 and (ap / "pending" / f"{jid}.json").exists()
              and not (ap / "failed" / f"{jid}.json").exists()
              and len(list((ap / "_requeued_manifests").glob(f"{jid}.manifest*.json"))) == 1,
              "--apply moves it failed/ -> pending/ and parks its manifest")
        # a DONE render that is neither live nor rejected is AWAITING OWNER PICK (and the row reads 'redrawn')
        j = json.loads((ap / "pending" / f"{jid}.json").read_text())
        j["target_def"], j["target_original"] = "RM_Renamed", ["RM_Redo"]     # filed under the NEW name
        (ap / "done" / f"{jid}.json").write_text(json.dumps(j))
        (ap / "pending" / f"{jid}.json").unlink()
        (ap / "_artsrc" / jid).mkdir(parents=True)
        (ap / "_artsrc" / jid / f"{jid}.png").write_bytes(noise_png(99))
        R7 = E.enact(F["decisions"], apply=False, holds=["vine"], no_deploy=True)
        check(any(a.startswith("RM_Redo:") and jid in a for a in R7["plan"]["awaiting_pick"]),
              "a finished render filed under the row's NEW name (target_original) is AWAITING OWNER PICK")
        check(E.ruling_status(F["decisions"])["rows"]["RM_Redo"]["state"] == "redrawn", "ruling_status: redrawn")
        check(E.ruling_status(F["decisions"])["rows"]["RM_Note"]["state"] == "not_acted",
              "ruling_status: an un-enacted note is NOT YET ACTED ON")

        alt = F["root"] / "elsewhere" / "copy.decisions.json"
        alt.parent.mkdir()
        shutil.copy(F["decisions"], alt)
        import ingest as I
        r = I.ingest(alt, defer_redo_jobs=True, purge=False, skip_rows=["RM_HeldVine"])
        check(r["ok"] and r["rulings"] == 0 and not r.get("rejected"), "ingest is idempotent by content, not path string")
        check(I.rel_via(L.REPO_ROOT / "Transient" / "x.json") == "Transient/x.json"
              and I.rel_via(Path("/mnt/d/Luke/dev/RimMandrake/Transient/x.json")) == "Transient/x.json",
              "via is recorded repo-relative (clone or D: mirror)")

        R3 = E.enact(F["decisions"], apply=False, holds=["vine"], mark_done=["RM_Note"], no_deploy=True)
        R4 = E.enact(F["decisions"], apply=False, holds=["vine"], no_deploy=True)
        check(not R4["todo"] and any(d.startswith("RM_Note") for d in R4["plan"]["done"]),
              "--mark-done records the note as done; later runs list it as done, not TODO")
        E.enact(F["decisions"], apply=True, holds=["vine"], no_deploy=True, redo_jobs_out=JOBS)
        D2 = json.loads(F["decisions"].read_text())["decisions"]["RM_Note"]
        check(D2["note"] == "" and D2["notes_followed"][0]["followed_by"] == ["mark-done"], "a marked-done note is taken off on --apply")
        # a leftover "redo" letter on a row whose note was carried out must NOT re-queue it; a NEW note must
        dd = json.loads(F["decisions"].read_text())
        dd["decisions"]["RM_Note"]["decision"] = "redo"
        F["decisions"].write_text(json.dumps(dd))
        P8 = E.build_plan(F["decisions"])["queue"]
        check(not any(q["row"] == "RM_Note" for q in P8), "redo + note already followed (notes_followed) is not re-queued")
        dd["decisions"]["RM_Note"]["note"] = "a brand new note"
        F["decisions"].write_text(json.dumps(dd))
        P9 = E.build_plan(F["decisions"])["queue"]
        check(any(q["row"] == "RM_Note" for q in P9), "redo + a NEW typed note does queue")
        dd["decisions"]["RM_Note"]["note"] = "make it 0.3 cells"
        F["decisions"].write_text(json.dumps(dd))
        P10 = E.build_plan(F["decisions"])
        check(not any(q["row"] == "RM_Note" for q in P10["queue"]), "redo + note whose mark-done event exists is not re-queued")
        check(not E.CUT_NOTE.search("variations") and E.CUT_NOTE.search("no longer needed"), "cut-note matcher")
    finally:
        shutil.rmtree(F["root"], ignore_errors=True)
    print(f"\n{'ALL PASS' if not FAILS else f'{len(FAILS)} FAILED'}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
