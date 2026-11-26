#!/usr/bin/env python3
"""Selftest: the art-eval flyer module carries the C5a checks and shows the judge the cut-out parts sheet.

Owner 2026-11-07 (criteria ledger CL-047 FireHawk, CL-048 Porg): a judge passed a wing baked into the plate, a wing that
breaks into specks edge-on and belly pixels ripped away with a lifted wing, from contact sheets. The brief's C5a says how
to look; this test holds the pipeline to it:

- a flyer card with flight frames asks BODY_STATIC and every C5a item (card_facts once read a `flight` key that no
  spec sets, so BODY_STATIC was never asked: shirrel_flight_w86r2 ACCEPTed with no BODY_STATIC answer);
- every C5a code is blocking in the severity policy;
- the parts sheet (flyer_eye_checks.py parts) reaches the card as a panel the judge is told how to read;
- fauna_spec gives flight frames one at a time at full size, labelled by facing and frame, and builds the parts sheet
  for a def with a cut-out set.

Synthetic frames in a temporary directory; no media file and no model call.

    python3 src/RimMandrake/Utils/art_eval/selftest_flyer_c5a.py      exit 0 all pass, 1 any fail
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import policy as P  # noqa: E402

C5A = {"HEAD_STILL": "FLYER_HEAD_MOVES", "WING_BAKED": "FLYER_WING_BAKED", "WING_SPECKS": "FLYER_WING_SPECKS",
       "BODY_RIP": "FLYER_BODY_RIP", "PART_MISSING": "FLYER_PART_MISSING"}
FAILS, PASSED = [], []
PREFIX, N, SIZE = "Bird_Flying_", 3, 128
LIFT = [30, 0, 30]


def check(name, cond, detail=""):
    (PASSED if cond else FAILS).append(name)
    print(("ok   " if cond else "FAIL ") + name + ("" if cond else f"  {detail}"))


def frame(k: int) -> Image.Image:
    im = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for x0, x1 in ((54, 6), (74, 122)):
        y = 50 + LIFT[k]
        d.polygon([(x0, 60), (x1, y), (x1, y + 14), (x0, 72)], fill=(200, 90, 20, 255))
    d.ellipse((52, 44, 76, 110), fill=(90, 80, 70, 255))
    d.ellipse((54, 24, 74, 44), fill=(150, 140, 120, 255))
    return im


def write_frames(folder: Path) -> dict:
    folder.mkdir(parents=True)
    out = {}
    for facing in ("east", "north", "south"):
        for k in range(N):
            p = folder / f"{PREFIX}{k + 1}_{facing}.png"
            frame(k).save(p)
            out.setdefault(facing, []).append((k + 1, str(p)))
    return out


def write_config(path: Path, folder: Path) -> Path:
    wing = {"poly": [[0, 40], [54, 40], [54, 100], [0, 100]], "hinge": [54, 60], "sign": 1,
            "poses": [[0, 1, 1.0], [10, 1, 0.8], [0, 1, 1.0]]}
    cfg = {"set": "Bird", "folder": str(folder), "prefix": PREFIX,
           "facings": {f: {"master": 2, "protect": [[[48, 20], [80, 20], [80, 50], [48, 50]]], "wings": [wing]}
                       for f in ("east", "north", "south")}}
    path.write_text(json.dumps(cfg))
    return path


def regress_holds_checks():
    """regress_holds.py, the item's judge of done, on planted regression runs."""
    import regress_holds as RH

    def state(td: Path, rows, key="K", blocking=None) -> Path:
        (td / "regression_runs").mkdir(parents=True)
        (td / "runs" / "r1").mkdir(parents=True)
        (td / "regression_runs" / "r1.json").write_text(json.dumps(
            {"versions_key": key, "run": "r1", "at": "2026-11-26T00:00:00", "passed": 0, "total": len(rows), "rows": rows}))
        (td / "runs" / "r1" / "decisions.jsonl").write_text("".join(json.dumps(
            {"subject": s, "opus": {"detail": {"blocking": [{"code": c} for c in cs]}}}) + "\n"
            for s, cs in (blocking or {}).items()))
        return td

    def row(subj, ok=True, got="REGEN", unmeasured=False, miss=None):
        r = {"subject": subj, "expect": "NOT_ACCEPT", "got": got, "pass": ok, "unmeasured": unmeasured}
        return dict(r, known_miss=miss) if miss else r

    cases = [
        ("a run whose rows all pass, the bird refused on its code, holds", 0,
         [row("RM_Bird"), row("RM_Walker", ok=False, got="ACCEPT", miss="CL-001")], "K", {"RM_Bird": ["FLYER_WING_BAKED"]}),
        ("a HOLD row is not a pass", 1, [row("RM_Bird"), row("RM_X", ok=False, got="HOLD_ERROR", unmeasured=True)], "K",
         {"RM_Bird": ["FLYER_WING_BAKED"]}),
        ("a failed row with no open miss does not hold", 1, [row("RM_Bird"), row("RM_X", ok=False, got="ACCEPT")], "K",
         {"RM_Bird": ["FLYER_WING_BAKED"]}),
        ("a bird refused on another code does not count", 1, [row("RM_Bird"), row("RM_X")], "K", {"RM_Bird": ["STYLE_OFF"]}),
        ("a run on older versions is not read", 1, [row("RM_Bird"), row("RM_X")], "OLD", {"RM_Bird": ["FLYER_WING_BAKED"]}),
        ("a missing bird row does not hold", 1, [row("RM_X"), row("RM_Y")], "K", {}),
    ]
    for name, want, rows, key, blocking in cases:
        with tempfile.TemporaryDirectory() as td:
            rc, why = RH.verdict(["RM_Bird"], {"FLYER_WING_BAKED"}, state=state(Path(td), rows, key, blocking),
                                 current=(2, "K"))
        check("regress_holds: " + name, rc == want, why)


def main() -> int:
    import cards as C
    import fauna_spec as FS
    import runner as RN

    tpl, pol = P.load_template("creature"), P.load_policy()
    with tempfile.TemporaryDirectory() as td:
        t = Path(td)
        frames = write_frames(t / "frames")
        sets = t / "sets"
        sets.mkdir()
        write_config(sets / "Bird.json", t / "frames")

        # --- fauna_spec: frames one at a time at full size, labelled; the parts sheet for a cut-out def
        fl = FS.flight_panels("RM_TestBird", frames, t / "spec", def_sets={"RM_TestBird": ["Bird"]}, sets_dir=sets)
        check("one flight panel per frame, not a strip per facing", len(fl["flight"]) == 3 * N, fl["flight"])
        check("flight frames keep their full size",
              all(Image.open(p).size == (SIZE, SIZE) for p in fl["flight"]), [Image.open(p).size for p in fl["flight"]])
        check("each flight frame is labelled by facing and frame",
              fl["flight_labels"][:2] == ["east f1", "east f2"] and len(fl["flight_labels"]) == 3 * N, fl["flight_labels"])
        check("a cut-out def gets its parts sheet", len(fl["parts"]) == 1 and Path(fl["parts"][0]).is_file(), fl)
        none = FS.flight_panels("RM_Other", frames, t / "spec2", def_sets={}, sets_dir=sets)
        check("a def with no cut-out set gets no parts sheet", none["parts"] == [], none)

        # --- the card carries the parts panel and the flight fact
        spec = {"subject": "RM_TestBird", "label": "test bird", "template": "creature", "module": "flyer",
                "candidate": "live", "description": "A small bird.", "invented": True,
                "flight_labels": fl["flight_labels"],
                "images": {"south": frames["south"][0][1], "east": frames["east"][0][1], "north": frames["north"][0][1],
                           "scale": frames["east"][0][1], "flight": fl["flight"], "parts": fl["parts"]}}
        card = C.build_card(spec, t / "card")
        check("card carries the parts panel", card["panels"].get("parts") == ["parts_1"]
              and (t / "card" / "parts_1.png").is_file(), card["panels"].get("parts"))
        check("the judge is sent the parts sheet", "parts_1.png" in RN.image_list(card), RN.image_list(card))
        capped = [p.name for p in RN.capped_images(card, t / "card", cap=8)]
        check("a capped judge still gets the parts sheet whole, not tiled", "parts_1.png" in capped, capped)
        md = (t / "card" / "card.md").read_text()
        check("card.md says how to read the parts sheet", "Parts sheet" in md and "plate" in md, md[-600:])
        check("card.md names each flight frame's facing and frame", "flight_1.png = east f1" in md, md[-600:])

        facts = P.card_facts(card, pol)
        check("flight frames on the card make the `flight` fact", "flight" in facts, facts)
        ids = {it["id"] for it in P.checklist_for(tpl, "flyer", facts)}
        check("a flyer card with flight frames asks BODY_STATIC", "BODY_STATIC" in ids, sorted(ids))
        for item in C5A:
            check(f"a flyer card with flight frames asks {item}", item in ids, sorted(ids))
        walker = {it["id"] for it in P.checklist_for(tpl, "walker", facts)}
        check("a walker is never asked the flyer items", not (walker & (set(C5A) | {"BODY_STATIC"})), walker)
        bare = {it["id"] for it in P.checklist_for(tpl, "flyer", P.card_facts(dict(card, panels={}), pol))}
        check("a flyer with no flight frames is not asked the flight items", not (bare & set(C5A)), bare)

    # --- the codes: each item answers with its C5a code, each code blocks
    items = {it["id"]: it for it in tpl["checklist"]}
    for item, code in C5A.items():
        it = items.get(item, {})
        check(f"{item} files {code}", it.get("code") == code, it)
        c = pol["codes"].get(code, {})
        check(f"{code} is blocking under brief C5a", c.get("default") == "blocking" and c.get("brief") == "C5a", c)
    check("the template version moved past creature@v4", tpl["version"] != "creature@v4", tpl["version"])
    module = (P.REFS / "templates" / "creature.md").read_text().split("### Module: flyer", 1)[-1].split("###", 1)[0]
    check("the flyer module tells the judge to read the parts sheet", "parts" in module and "plate" in module, module)

    regress_holds_checks()
    print(f"selftest_flyer_c5a: {len(PASSED)} passed, {len(FAILS)} failed")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
