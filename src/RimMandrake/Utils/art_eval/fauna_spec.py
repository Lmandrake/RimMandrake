#!/usr/bin/env python3
"""Build art_eval specs for LIVE fauna defs (not the pilot bundle): one spec per PawnKind/ThingDef pair.

    python3 fauna_spec.py biome <Mod>=<BiomeDef xml> ...     # list a biome's inline <wildAnimals> (XML elements)
    python3 fauna_spec.py build DEF [DEF...] --out <dir>      # spec JSON + scale panel (+ departures brief if missing)

Reads only the repo: ThingDef (description, label), PawnKindDef lifeStages bodyGraphicData (texPath, adult drawSize =
max over life stages), the textures under src/**/Textures, and `flyingAnimationFramePathPrefix`/`MaxFlightTime` to
decide the `flyer` module. The facings the card shows are the loose PNG files `<texPath>_south|east|north|west`.
Flight frames are composed into one strip per direction from the stills (never a live capture).
"""
from __future__ import annotations

import argparse
import glob
import json
import re
import sys
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "art"))
import cards as C  # noqa: E402
import runner as R  # noqa: E402
import policy as P  # noqa: E402

SRC = C.ROOT / "src"


def index_defs():
    things, kinds = {}, {}
    for f in glob.glob(str(SRC / "**/Defs/**/*.xml"), recursive=True):
        try:
            root = ET.parse(f).getroot()
        except ET.ParseError:
            continue
        for d in root.iter("ThingDef"):
            n = d.findtext("defName")
            if n:
                things[n] = (f, d)
        for d in root.iter("PawnKindDef"):
            r = d.findtext("race")
            if r:
                kinds.setdefault(r, []).append((f, d))
    return things, kinds


def texture_index():
    idx = {}
    for f in glob.glob(str(SRC / "**/Textures/**/*.png"), recursive=True):
        idx.setdefault(f.split("/Textures/", 1)[1][:-4], []).append(f)
    return idx


def mod_of(path: str) -> str:
    rel = path.replace(str(SRC) + "/", "")
    return "/".join(rel.split("/")[:2])


def biome_roster(xmlpath: str):
    out = []
    for b in ET.parse(xmlpath).getroot().iter("BiomeDef"):
        w = b.find("wildAnimals")
        out.append((b.findtext("defName"), [(c.tag, (c.text or "").strip()) for c in (w if w is not None else [])]))
    return out


def build_spec(defname: str, things, kinds, tex, outdir: Path) -> dict:
    f, d = things[defname]
    label = d.findtext("label")
    desc = " ".join((d.findtext("description") or "").split())
    paths, draws = [], []
    for _, k in kinds.get(defname, []):
        for bg in k.iter("bodyGraphicData"):
            paths.append(bg.findtext("texPath"))
            ds = (bg.findtext("drawSize") or "1").replace("(", "").replace(")", "").split(",")
            draws.append(float(ds[0]))
    adult = max(range(len(draws)), key=lambda i: draws[i])
    tp = paths[adult]
    text = ET.tostring(d, encoding="unicode")
    flyer = "flyingAnimationFramePathPrefix" in text or "MaxFlightTime" in text
    home = mod_of(f)
    imgs = {}
    for face in ("south", "east", "north", "west"):
        hits = tex.get(f"{tp}_{face}", [])
        hits.sort(key=lambda p: mod_of(p) != home)
        if hits:
            imgs[face] = hits[0]
    spec = {"subject": defname, "label": label, "template": "creature", "module": "flyer" if flyer else "walker",
            "candidate": "live", "provenance": f"live installed art, texPath {tp} ({mod_of(imgs.get('south', f))})",
            "description": desc, "tier": defname.split("_")[0] + "_", "invented": True,
            "size": {"drawSize": [draws[adult], draws[adult]]}, "source": f.replace(str(SRC) + "/", ""),
            "owner_kept": False}
    # true-scale panel beside the vanilla human
    import scale_panel as SP
    outdir.mkdir(parents=True, exist_ok=True)
    if imgs.get("east"):
        compact, full = outdir / f"{defname}_scale.png", outdir / f"{defname}_scale_full.png"
        SP.render_panel(Path(imgs["east"]).read_bytes(), {"kind": "animal", "drawSize": (draws[adult], draws[adult])},
                        compact, full)
        imgs["scale"] = str(compact)
    if flyer:
        base = tp.rsplit("/", 1)[0]
        stem = tp.rsplit("/", 1)[1]
        frames = {}
        for k, v in tex.items():
            m = re.match(rf"{re.escape(base)}/{re.escape(stem)}_(?:Flying|Fly)_(\d*)_?(south|east|north)$", k)
            if m:
                frames.setdefault(m.group(2), []).append((int(m.group(1) or 0), v[0]))
        flight = []
        for face, lst in sorted(frames.items()):
            lst.sort()
            p = outdir / f"{defname}_flight_{face}.png"
            C.strip([x[1] for x in lst], [f"{face} f{x[0]}" for x in lst], tile=256, title=f"{defname} flight frames, {face}").save(p)
            flight.append(str(p))
        spec["images_flight_note"] = {k: len(v) for k, v in frames.items()}
        imgs["flight"] = flight
    spec["images"] = imgs
    bf = C.BRIEFS / f"{defname}.json"
    if bf.is_file():
        b = json.loads(bf.read_text())
        spec["departures"] = b.get("departures") or []
        spec["earth_body_named"] = bool(b.get("earth_body_named"))
        if b.get("body_plan"):
            spec["body_plan"] = b["body_plan"]
    return spec


def ensure_brief(spec: dict):
    bf = C.BRIEFS / f"{spec['subject']}.json"
    if bf.is_file():
        return
    prompt = (R.PROMPTS / "departures_brief.md").read_text() + "\n\n# Subject\n\n" + json.dumps(
        {"defName": spec["subject"], "label": spec.get("label"), "description": spec.get("description")}, indent=1)
    work = R.storage_root() / "briefs"
    work.mkdir(parents=True, exist_ok=True)
    text, meta = R.call_claude(prompt, work, "opus", timeout=240, tools="")
    b = P.parse_reply(text)
    b.update({"by": meta.get("models_reported"), "prompt_version": P.prompt_version(R.PROMPTS / "departures_brief.md"),
              "at": R.now(), "source": "description only (no image)"})
    C.BRIEFS.mkdir(parents=True, exist_ok=True)
    bf.write_text(json.dumps(b, indent=1))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("defs", nargs="+")
    b.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    things, kinds = index_defs()
    tex = texture_index()
    out = Path(a.out)

    def one(n):
        spec = build_spec(n, things, kinds, tex, out / "panels")
        ensure_brief(spec)
        bf = C.BRIEFS / f"{n}.json"
        b = json.loads(bf.read_text())
        spec["departures"], spec["earth_body_named"] = b.get("departures") or [], bool(b.get("earth_body_named"))
        if b.get("body_plan"):
            spec["body_plan"] = b["body_plan"]
        (out / f"{n}.spec.json").write_text(json.dumps(spec, indent=1))
        print(f"spec {n} module={spec['module']} faces={[k for k in spec['images'] if k in C.FACINGS]}", file=sys.stderr, flush=True)

    out.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(4) as ex:
        list(ex.map(one, a.defs))


if __name__ == "__main__":
    main()
