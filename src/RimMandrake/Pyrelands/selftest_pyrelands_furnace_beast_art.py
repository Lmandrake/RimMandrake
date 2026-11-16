#!/usr/bin/env python3
"""T_FURNACE_ART_OFFLINE (RIMMANDRAKE_REDRAW_FURNACE_BEAST_BIGGER_ART_CARD_PROMISED_IT): the furnace-beast's art fits
the 7.5-cell giant the owner's card made it (2026-11-15, "Keep 'twice', raise body to 9+ ... needs bigger art").

Reads the repo's PawnKindDef XML and textures only:
  files       every lifeStage texPath resolves to _south/_east/_north PNGs (Graphic_Multi; west mirrors east)
  budget      each canvas edge >= adult drawSize x 128 px (the owner's 128 px/cell rule, 2026-08-23)
  alpha       RGBA, clear corners (alpha <= 8, the sprite validator's bar), >= 40% of the canvas fully clear and >= 10% solid (alpha >= 128)
  fits        the solid silhouette stays >= 2 px inside every canvas edge (nothing clipped at the quad's edge)
  facings     facing_scale_lint.truth(elevation, quadruped) is ok: same height from every side, feet on one row
  giant       the adult's drawn solid length (cells) exceeds the Zeer adult's, and its solid height is >= 2.5 human
              meshes (the human-for-scale is a 1.5-cell mesh)
  judged      the installed shas are the pictures the art-eval pipeline ACCEPTed (run fauna_pyrelands_s2r2_00, which also won the fauna_compare head-to-head over the kept art)

Then every planted fault (a mutant copy of the textures) must turn a fact other than `judged` red, and the clean copy must stay green.
Run: python3 <this file>      exit 0 = PASS, 1 = a fact or a mutant failed
"""
import hashlib
import json
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / "src/RimMandrake/Utils/art"))
import facing_scale_lint as FSL  # noqa: E402

FAUNA = HERE / "Defs/ThingDefs_Races/RM_PyrelandsFauna.xml"
TEX = HERE / "Textures"
ZEER_XML = REPO / "src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Zeer.xml"
ZEER_TEX = REPO / "src/RimStarWars/SWBestiary/Textures"
RUN = REPO / "infrastructure/state/art_eval/runs/fauna_pyrelands_s2r2_00/decisions.jsonl"
FACES = ("south", "east", "north")
HUMAN_MESH = 1.5
CORNER_MAX_ALPHA = 8   # generating-rimworld-sprites validate_sprite.py's own bar: a cut-out's corners are clear


def stages(xml: Path, kind: str) -> list:
    """[(texPath, drawSize)] for every lifeStage bodyGraphicData of the PawnKindDef."""
    root = ET.parse(xml).getroot()
    pk = next(e for e in root if e.tag == "PawnKindDef" and e.findtext("defName") == kind)
    return [(gd.findtext("texPath"), float(gd.findtext("drawSize"))) for ls in pk.find("lifeStages")
            for gd in ls if gd.tag == "bodyGraphicData"]


def solid_bbox(im):
    return im.split()[-1].point(lambda v: 255 if v >= 128 else 0).getbbox()


def facts(tex: Path) -> dict:
    out = {}
    st = stages(FAUNA, "RM_FurnaceBeast")
    adult = max(d for _, d in st)
    paths = {(tp, f): tex / f"{tp}_{f}.png" for tp, _ in st for f in FACES}
    missing = [str(p) for p in paths.values() if not p.is_file()]
    out["files"] = (not missing, missing or f"{len(paths)} files")
    if missing:
        return out
    bad_b, bad_a, bad_f = [], [], []
    for p in sorted(set(paths.values())):
        im = Image.open(p)
        if min(im.size) < adult * 128:
            bad_b.append(f"{p.name} {im.size}")
        if im.mode != "RGBA":
            bad_a.append(f"{p.name} mode {im.mode}")
            continue
        a = im.split()[-1]
        W, H = im.size
        hist = a.histogram()
        clear, solid = hist[0] / (W * H), sum(hist[128:]) / (W * H)
        corners = [a.getpixel(c) for c in ((0, 0), (W - 1, 0), (0, H - 1), (W - 1, H - 1))]
        if max(corners) > CORNER_MAX_ALPHA or clear < 0.40 or solid < 0.10:
            bad_a.append(f"{p.name} corners {corners} clear {clear:.2f} solid {solid:.2f}")
        bb = solid_bbox(im)
        if not bb or bb[0] < 2 or bb[1] < 2 or bb[2] > W - 2 or bb[3] > H - 2:
            bad_f.append(f"{p.name} solid bbox {bb} on {W}x{H}")
    out["budget"] = (not bad_b, bad_b or f"every canvas >= {adult * 128:.0f} px")
    out["alpha"] = (not bad_a, bad_a or "real alpha")
    out["fits"] = (not bad_f, bad_f or "inside the quad")
    tp = st[0][0]
    t = FSL.truth({f: str(tex / f"{tp}_{f}.png") for f in FACES}, "elevation", "quadruped")
    out["facings"] = (t["verdict"] == "ok", t["verdict"] if t["verdict"] == "ok" else t["flags"])
    east = Image.open(tex / f"{tp}_east.png")
    bb = solid_bbox(east)
    length, height = (bb[2] - bb[0]) / east.size[0] * adult, (bb[3] - bb[1]) / east.size[1] * adult
    ztp, zdraw = max(stages(ZEER_XML, "RSW_Zeer"), key=lambda x: x[1])
    zeer = Image.open(ZEER_TEX / f"{ztp}_east.png")
    zb = solid_bbox(zeer)
    zlen = (zb[2] - zb[0]) / zeer.size[0] * zdraw
    out["giant"] = (length > zlen and height >= 2.5 * HUMAN_MESH,
                    f"adult {length:.2f}x{height:.2f} cells; Zeer length {zlen:.2f}; human mesh {HUMAN_MESH}")
    want = {}
    if RUN.is_file():
        recs = [json.loads(x) for x in RUN.read_text().splitlines() if x.strip()]
        acc = [r for r in recs if r.get("subject") == "RM_FurnaceBeast" and r.get("decision") == "ACCEPT"]
        want = (acc[-1].get("source_sha256") or {}) if acc else {}
    got = {f: hashlib.sha256((tex / f"{tp}_{f}.png").read_bytes()).hexdigest() for f in FACES}
    out["judged"] = (bool(want) and all(want.get(f) == got[f] for f in FACES),
                     "installed = ACCEPTed" if want else f"no ACCEPT record in {RUN}")
    return out


def red(out: dict) -> list:
    return [k for k, (ok, _) in out.items() if not ok]


def mutants(tex: Path):
    tp = stages(FAUNA, "RM_FurnaceBeast")[0][0]
    p = lambda root, f: root / f"{tp}_{f}.png"  # noqa: E731

    def no_alpha(root):
        Image.open(p(root, "east")).convert("RGB").save(p(root, "east"))

    def clipped(root):
        im = Image.open(p(root, "east")).convert("RGBA")
        out = Image.new("RGBA", im.size, (0, 0, 0, 0))
        out.paste(im, (40, 0))
        out.save(p(root, "east"))

    def south_too_big(root):
        im = Image.open(p(root, "south")).convert("RGBA")
        FSL.rescale(im, 1.5).save(p(root, "south"))

    def missing_north(root):
        p(root, "north").unlink()

    def small_canvas(root):
        im = Image.open(p(root, "north"))
        im.resize((512, 512)).save(p(root, "north"))

    def dwarf(root):
        for f in FACES:
            im = Image.open(p(root, f)).convert("RGBA")
            out = Image.new("RGBA", im.size, (0, 0, 0, 0))
            small = im.resize((im.size[0] // 2, im.size[1] // 2))
            out.paste(small, (im.size[0] // 4, im.size[1] // 4))
            out.save(p(root, f))

    return [no_alpha, clipped, south_too_big, missing_north, small_canvas, dwarf]


def main() -> int:
    out = facts(TEX)
    for k, (ok, why) in out.items():
        print(f"{'ok  ' if ok else 'FAIL'} {k}: {why}")
    fails = red(out)
    tp = stages(FAUNA, "RM_FurnaceBeast")[0][0]
    for m in mutants(TEX):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for f in FACES:
                dst = root / f"{tp}_{f}.png"
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(TEX / f"{tp}_{f}.png", dst)
            m(root)
            r = [k for k in red(facts(root)) if k != "judged"]   # every mutant changes the sha: judged proves nothing here
            print(f"{'ok  ' if r else 'FAIL'} mutant {m.__name__}: red on {r}")
            if not r:
                fails.append(f"mutant {m.__name__} stayed green")
    print("PASS" if not fails else f"FAIL: {fails}")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
