#!/usr/bin/env python3
"""selftest_enact_ws.py — the five enact defects the Weeping Stones verification found (2026-10-10), each a check
that FAILS on the pre-fix enact.py:

  1 PICK ON DONOR ART: a render picked for a row whose def texPaths vanilla art (Warg) was counted "already live";
    now it installs at OUR path and the def's texPath moves to it (placeholder <color> tint dropped). A render picked
    for a Graphic_Random folder of ours goes into the folder (<base>_<letter>.png), and a folder this run fills sheds
    the pictures he did not keep.
  2 TICKED VARIANTS SHIPPED: an explicit variant tick goes into the plant folder, or (a creature) to <res>V_<L> with an
    alternateGraphics entry; a DEFAULT variant tick ships nothing.
  3 ART + DEF NOTES: a note asking for a rename/description is not "followed" because an art job exists — it is a
    TODO until --mark-done, both for an open note and for one an earlier run already moved to notes_followed.
  4 REDRAW REFERENCES: "drop the art" / "total regen" -> no reference; "based on (b)" -> column B; otherwise the
    in-game picture (control).
  5 CATCH WAITS FOR ITS CREATURE: RM_XCatch is not filed while RM_X is being redrawn; a catch job drawn before is
    withdrawn to _withdrawn/; once RM_X is picked the catch is filed with RM_X's picture as its reference.
Fixture under /home/mandrake/rm/scratch/BENCH (never /tmp).
"""
from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import selftest_enact as T  # noqa: E402

FAILS = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


KINDS = """<?xml version="1.0" encoding="utf-8"?>
<Defs>
  <ThingDef ParentName="AnimalThingBase">
    <defName>RM_Bur</defName>
  </ThingDef>
  <PawnKindDef ParentName="AnimalKindBase">
    <defName>RM_Bur</defName>
    <race>RM_Bur</race>
    <lifeStages>
      <li>
        <bodyGraphicData>
          <texPath>Things/Pawn/Animal/Warg/Warg</texPath>
          <drawSize>1.5</drawSize>
          <color>(120, 110, 95)</color>
        </bodyGraphicData>
        <dessicatedBodyGraphicData>
          <texPath>Things/Pawn/Animal/Warg/Dessicated_Warg</texPath>
        </dessicatedBodyGraphicData>
      </li>
    </lifeStages>
  </PawnKindDef>
  <PawnKindDef ParentName="AnimalKindBase">
    <defName>RM_OtherWarg</defName>
    <race>RM_Bur</race>
    <lifeStages><li><bodyGraphicData><texPath>Things/Pawn/Animal/Warg/Warg</texPath></bodyGraphicData></li></lifeStages>
  </PawnKindDef>
  <PawnKindDef ParentName="AnimalKindBase">
    <defName>RSW_Fan</defName>
    <race>RSW_Fan</race>
    <lifeStages><li><bodyGraphicData><texPath>swanimals/Fan/Fan</texPath></bodyGraphicData></li></lifeStages>
  </PawnKindDef>
</Defs>
"""


def build(root: Path) -> dict:
    F = T.build(root)
    import artledger as L
    src, led = F["src"], F["led"]
    (src / "RimMandrake/TestMod/Defs/ThingDefs_Races/Kinds.xml").write_text(KINDS)
    names = ("wa", "bb", "pa", "pb", "da", "db", "fa", "fb", "fc", "ka", "am", "va", "vb", "la", "ha", "hc")
    s = {k: L.store_put_bytes(T.noise_png(100 + i)) for i, k in enumerate(names)}
    tex = src / "RimMandrake/TestMod/Textures"
    evs = []
    for rel, k in (("Things/Plant/RM_Quill/RM_Quill_a.png", "pa"), ("Things/Plant/RM_Dew/RM_Dew_a.png", "da"),
                   ("swanimals/Fan/Fan_east.png", "fa")):
        p = tex / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(L.store_get(s[k]))
        evs.append({"type": "live", "id": L.det_id("live", rel), "mod": T.MOD, "rel": rel, "sha": s[k], "prev": None,
                    "reason": "fixture", "ts": "2026-10-01T00:00:00"})
    with open(led / "events" / "TEST.jsonl", "a") as fh:
        for e in evs:
            fh.write(json.dumps(e) + "\n")
    W = "Things/Pawn/Animal/Warg/Warg"
    IG, DO = "IN GAME — TestMod", "donor original — Vanilla Textures Expanded"
    rows = {
        "RM_Bur": {"columns": {"A": {"east": s["wa"]}, "B": {"east": s["bb"]}}, "graphic_of": {"A": W, "B": "_byname"},
                   "labels": {"A": DO, "B": "render bur_v1"}, "res": W, "subject_key": "bur"},
        "RM_Quill": {"columns": {"A": {"single": s["pa"]}, "B": {"single": s["pb"]}},
                     "graphic_of": {"A": "Things/Plant/RM_Quill", "B": "Things/Plant/RM_Quill"},
                     "labels": {"A": "our deployed art", "B": "render quill_v1"}, "res": "Things/Plant/RM_Quill",
                     "subject_key": "quill"},
        "RM_Dew": {"columns": {"A": {"single": s["da"]}, "B": {"single": s["db"]}},
                   "graphic_of": {"A": "Things/Plant/RM_Dew", "B": "Things/Plant/RM_Dew"},
                   "labels": {"A": "our deployed art", "B": "render dew_v1"}, "res": "Things/Plant/RM_Dew",
                   "subject_key": "dew"},
        "RSW_Fan": {"columns": {"A": {"east": s["fa"]}, "B": {"east": s["fb"]}, "C": {"east": s["fc"]}},
                    "graphic_of": {"A": "swanimals/Fan/Fan", "B": "swanimals/Fan/Fan", "C": "swanimals/Fan/Fan"},
                    "labels": {"A": IG, "B": "render fan_b", "C": "render fan_c"}, "res": "swanimals/Fan/Fan",
                    "subject_key": "fan"},
        "RM_Kir": {"columns": {"A": {"east": s["ka"]}}, "graphic_of": {"A": "Things/Pawn/Animal/Chicken/Chicken"},
                   "labels": {"A": IG}, "subject_key": "kir"},
        "RM_Amb": {"columns": {"A": {"single": s["am"]}}, "graphic_of": {"A": "Things/Plant/Ambrosia"},
                   "labels": {"A": IG}, "subject_key": "amb"},
        "RM_Vel": {"columns": {"A": {"east": s["va"]}, "B": {"east": s["vb"]}},
                   "graphic_of": {"A": "Things/Pawn/Animal/Dromedary/Dromedary", "B": "_byname"},
                   "labels": {"A": DO, "B": "render vel_v1"}, "subject_key": "vel"},
        "RM_Lum": {"columns": {"A": {"east": s["la"]}}, "graphic_of": {"A": "Things/Pawn/Animal/Lum/Lum"},
                   "labels": {"A": IG}, "subject_key": "lum"},
        "RM_Hul": {"columns": {"A": {"east": s["ha"]}}, "graphic_of": {"A": "Things/Pawn/Animal/Hul/Hul"},
                   "labels": {"A": IG}, "subject_key": "hul"},
        "RM_HulCatch": {"columns": {"A": {"east": s["hc"]}}, "graphic_of": {"A": "Things/Item/RM_HulCatch"},
                        "labels": {"A": IG}, "subject_key": "hulcatch"},
        "RM_Viz": {"columns": {}, "subject_key": "viz"},
    }
    snap = json.loads(Path(json.loads(F["decisions"].read_text())["snapshot"]).read_text())
    snap["rows"] = rows
    Path(json.loads(F["decisions"].read_text())["snapshot"]).write_text(json.dumps(snap))
    at = "2026-10-08T10:00:00.000Z"

    def d(dec, note="", **kw):
        return dict({"decision": dec, "at": at, "decidedAt": at, "note": note}, **kw)
    doc = json.loads(F["decisions"].read_text())
    doc["decisions"] = {
        "RM_Bur": d("B", picks={"_byname": "B"}, variants=["B"], variantsDefault=True),
        "RM_Quill": d("B", variants=["A", "B"]),
        "RM_Dew": d("B", variants=["B"], variantsDefault=True),
        "RSW_Fan": d("B", variants=["B", "C"]),
        "RM_Kir": d("redo", 'Total regen. Quasi-avian glider. Rename to "Dewglider"'),
        "RM_Amb": d("redo", "Make the art very special. Drop the art currently here."),
        "RM_Vel": d("redo", "Make more alien based on (b), less camel."),
        "RM_Lum": d("redo", "make it scarier"),
        "RM_Hul": d("redo", "An alien otter with a whale tail."),
        "RM_HulCatch": d("redo", "Make it look like a dead one of these. Of course generate AFTER the source is settled"),
        "RM_Viz": d("redo", "", notes_followed=[{"note": "Close. Beef up description, rename to the Fan Eel. Drop all "
                                                         "this art.", "at": at, "followed_by": ["enact_old_viz_v1"],
                                                 "when": "2026-10-08T10:05:00-0700"}]),
    }
    F["decisions"].write_text(json.dumps(doc))
    # a catch job an earlier enact filed before the creature was settled: rendered, no reference to the creature
    early = {"id": "enact_early_hulcatch_v1_east", "target_def": "RM_HulCatch", "facing": "east", "prompt": "x",
             "created": "2026-10-08T11:00:00Z", "owner_note": doc["decisions"]["RM_HulCatch"]["note"],
             "canon_reference": []}
    (F["ap"] / "done" / f"{early['id']}.json").write_text(json.dumps(early))
    F["s"] = s
    return F


def jobs_written(F) -> dict:
    out = {}
    for f in (F["ap"] / "pending").glob("*.json"):
        if f.name.endswith(".manifest.json"):
            continue
        j = json.loads(f.read_text())
        out.setdefault(j["target_def"], []).append(j)
    return out


def main():
    F = build(T.SCRATCH / f"enact_ws_{os.getpid()}")
    import artledger as L
    import enact as E
    src, s = F["src"], F["s"]
    kinds = src / "RimMandrake/TestMod/Defs/ThingDefs_Races/Kinds.xml"
    tex = src / "RimMandrake/TestMod/Textures"
    try:
        if hasattr(E, "reset_caches"):
            E.reset_caches()
        E._TEXPATHS.clear()
        R = E.enact(F["decisions"], apply=False, no_deploy=True)
        P = R["plan"]
        inst = {(i["row"], i["rel"]) for i in P["install"]}
        # 1 donor-texPath pick and folder pick
        check(("RM_Bur", "Things/Pawn/Animal/RM_Bur/RM_Bur_east.png") in inst,
              "1 a render picked over donor Warg art is planned for OUR path (not 'already live')")
        check(not any(r == "RM_Bur" and "donor art" in str(m) for r, m, *_ in P["installed_already"]),
              "1 ...and is not counted 'def texPath (donor art)' live")
        check(("RM_Quill", "Things/Plant/RM_Quill/RM_Quill_b.png") in inst and
              ("RM_Dew", "Things/Plant/RM_Dew/RM_Dew_b.png") in inst, "1 a folder-plant pick B goes into the folder as _b")
        # 2 variants
        check(("RSW_Fan", "swanimals/Fan/FanV_C_east.png") in inst, "2 ticked creature variant C -> FanV_C (alternate)")
        check(not any(r == "RM_Bur" and i.get("variant") for i in P["install"] for r in [i["row"]]),
              "2 a DEFAULT variant tick ships nothing extra")
        # 3 def half
        check(any(t.startswith("RM_Kir: def half") for t in R["todo"]) and "RM_Kir" not in P["followed"],
              "3 rename note with an art job is a TODO, not followed")
        check(any(t.startswith("RM_Viz: def half") for t in R["todo"]),
              "3 a followed note whose rename/description half nobody did is a TODO again")
        # 5 catch blocked
        check(not any(q["row"] == "RM_HulCatch" for q in P["queue"])
              and any(b.startswith("RM_HulCatch:") for b in P.get("blocked", [])), "5 catch is NOT filed while its creature is redrawn")
        check([w["job"]["id"] for w in P.get("withdraw", [])] == ["enact_early_hulcatch_v1_east"],
              "5 the catch render drawn before the creature was settled is planned for withdrawal")

        JOBS = F["root"] / "jobs_out.json"
        R = E.enact(F["decisions"], apply=True, no_deploy=True, redo_jobs_out=JOBS)
        check(R["ok"], "apply succeeds")
        bur = tex / "Things/Pawn/Animal/RM_Bur/RM_Bur_east.png"
        check(bur.is_file() and L.sha256_file(bur) == s["bb"], "1 picked Bur render installed at our path, sha == pick")
        kt = kinds.read_text()
        import xml.etree.ElementTree as ET
        root = ET.fromstring(kt)
        bur_kind = [k for k in root.findall("PawnKindDef") if k.findtext("defName") == "RM_Bur"][0]
        other = [k for k in root.findall("PawnKindDef") if k.findtext("defName") == "RM_OtherWarg"][0]
        check(bur_kind.find("lifeStages/li/bodyGraphicData/texPath").text == "Things/Pawn/Animal/RM_Bur/RM_Bur"
              and bur_kind.find("lifeStages/li/bodyGraphicData/color") is None
              and bur_kind.find("lifeStages/li/dessicatedBodyGraphicData/texPath").text.endswith("Dessicated_Warg"),
              "1 Bur's body texPath moved to our path, placeholder tint dropped, dessicated untouched")
        check(other.find("lifeStages/li/bodyGraphicData/texPath").text == "Things/Pawn/Animal/Warg/Warg",
              "1 another def using vanilla Warg is NOT repointed (no global overwrite)")
        q = tex / "Things/Plant/RM_Quill"
        check(sorted(p.name for p in q.iterdir()) == ["RM_Quill_a.png", "RM_Quill_b.png"]
              and L.sha256_file(q / "RM_Quill_b.png") == s["pb"], "2 Quill folder holds pick B AND ticked variant A")
        dw = tex / "Things/Plant/RM_Dew"
        check(sorted(p.name for p in dw.iterdir()) == ["RM_Dew_b.png"] and L.store_has(s["da"]),
              "1 Dew folder holds only pick B; the unkept A is retired (archived in the store)")
        fan = [k for k in root.findall("PawnKindDef") if k.findtext("defName") == "RSW_Fan"][0]
        alts = [li.findtext("texPath") for li in fan.findall("alternateGraphics/li")]
        check((tex / "swanimals/Fan/FanV_C_east.png").is_file() and alts == ["swanimals/Fan/FanV_C"]
              and fan.findtext("alternateGraphicChance") == "0.5", "2 Fan variant C shipped + alternateGraphics, chance 0.5")
        check((tex / "swanimals/Fan/Fan_east.png").is_file() and L.sha256_file(tex / "swanimals/Fan/Fan_east.png") == s["fb"],
              "2 Fan pick B installed in its own slot")
        J = jobs_written(F)
        # 4 references
        ref = lambda row: " ".join(str(x) for j in J.get(row, []) for x in (j.get("canon_reference") or [])
                                   + [j.get("reference") or ""])
        check("RM_Amb" in J and not ref("RM_Amb").strip() and "RM_Kir" in J and not ref("RM_Kir").strip(),
              "4 'drop the art' / 'total regen' redraws carry NO reference")
        check(s["vb"] in ref("RM_Vel") and s["va"] not in ref("RM_Vel"), "4 'based on (b)' attaches column B")
        check(s["la"] in ref("RM_Lum"), "4 control: a plain redo still attaches the in-game picture")
        # 3 note stays open
        D = json.loads(F["decisions"].read_text())["decisions"]
        check(D["RM_Kir"]["note"].startswith("Total regen") and D["RM_Lum"]["note"] == "",
              "3 the rename note stays OPEN after apply; a pure-art note is taken off")
        # 5 withdrawal + catch filed after settle
        check((F["ap"] / "_withdrawn" / "enact_early_hulcatch_v1_east.json").is_file()
              and not (F["ap"] / "done" / "enact_early_hulcatch_v1_east.json").exists()
              and json.loads((F["ap"] / "_withdrawn" / "enact_early_hulcatch_v1_east.json").read_text()).get("withdrawn_reason"),
              "5 the early catch render is withdrawn to _withdrawn/ with a reason")
        check("RM_HulCatch" not in J, "5 no catch job filed while RM_Hul is unsettled")
        doc = json.loads(F["decisions"].read_text())
        doc["decisions"]["RM_Hul"]["decision"] = "A"         # he picks the creature
        F["decisions"].write_text(json.dumps(doc))
        P2 = E.build_plan(F["decisions"])
        cq = [x for x in P2["queue"] if x["row"] == "RM_HulCatch"]
        check(cq and cq[0].get("ref_shas") == [s["ha"]] and not P2.get("blocked"),
              "5 once RM_Hul is picked the catch is filed with RM_Hul's picture as its reference")
        rows = E.job_rows({"queue": cq, "sheet": "test_sheet"})
        check(rows and any(s["ha"] in str(x) for x in rows[0]["canon_reference"])
              and rows[0]["id"] != "enact_early_hulcatch_v1", "5 ...the job row carries that reference, with a fresh id")
        # mark-done for both def halves
        E.enact(F["decisions"], apply=False, mark_done=["RM_Kir", "RM_Viz"], no_deploy=True)
        R3 = E.enact(F["decisions"], apply=False, no_deploy=True)
        check(not any("def half" in t for t in R3["todo"]), "3 --mark-done clears the def-half TODOs")
        R4 = E.enact(F["decisions"], apply=True, no_deploy=True, redo_jobs_out=JOBS)
        check(R4["installed"] == 0 and R4.get("retired") == 0 and R4.get("rebound") == 0 and R4.get("alts_added") == 0,
              "a second apply installs/rebinds/retires nothing")
        check(ET.fromstring(kinds.read_text()) is not None, "edited XML still parses")
    finally:
        shutil.rmtree(F["root"], ignore_errors=True)
    print(f"\n{'ALL PASS' if not FAILS else f'{len(FAILS)} FAILED'}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
