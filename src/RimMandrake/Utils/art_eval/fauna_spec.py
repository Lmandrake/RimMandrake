#!/usr/bin/env python3
"""Build art_eval specs for LIVE fauna defs (not the pilot bundle): one spec per PawnKind/ThingDef pair.

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


def ledger_kept_install(files: list):
    """[{mod, rel, sha}] for every file the art ledger says the owner kept (PROTECTED); None when the ledger could
    not be read (UNMEASURED — the caller must not read that as 'not kept')."""
    import hashlib
    try:
        import artledger as L
        idx = L.Index()
    except Exception:
        return None
    out = []
    for p in files:
        sha = hashlib.sha256(Path(p).read_bytes()).hexdigest()
        if idx.protected(sha):
            out.append({"mod": mod_of(p), "rel": p.split("/Textures/", 1)[1], "sha": sha})
    return out


def build_spec(defname: str, things, kinds, tex, outdir: Path, kept_lookup=ledger_kept_install) -> dict:
    if defname not in things:
        raise SystemExit(f"fauna_spec: no ThingDef {defname!r} under {SRC}")
    f, d = things[defname]
    label = d.findtext("label")
    desc = " ".join((d.findtext("description") or "").split())
    paths, draws, classes = [], [], []
    for _, k in kinds.get(defname, []):
        for bg in k.iter("bodyGraphicData"):
            paths.append(bg.findtext("texPath"))
            classes.append((bg.findtext("graphicClass") or "Graphic_Multi").strip())
            ds = (bg.findtext("drawSize") or "1").replace("(", "").replace(")", "").split(",")
            draws.append(float(ds[0]))
    if not draws:
        raise SystemExit(f"fauna_spec: {defname} has no PawnKindDef lifeStage bodyGraphicData (race={defname}); "
                         f"nothing to judge")
    adult = max(range(len(draws)), key=lambda i: draws[i])
    tp = paths[adult]
    text = ET.tostring(d, encoding="unicode")
    flyer = "flyingAnimationFramePathPrefix" in text or "MaxFlightTime" in text
    home = mod_of(f)
    imgs = {}
    gclass = classes[adult]
    if gclass == "Graphic_Single":
        # the game draws exactly <texPath>.png for every facing: judge that one file, never _east/_north files
        hits = sorted(tex.get(tp, []), key=lambda p: mod_of(p) != home)
        if hits:
            imgs["single"] = hits[0]
    elif gclass == "Graphic_Random":
        # texPath is a folder; the game picks one of its files at random
        vs = sorted(p for k, v in tex.items() if k.startswith(tp + "/") for p in sorted(v, key=lambda p: mod_of(p) != home)[:1])
        if vs:
            imgs["variants"] = vs
    else:
        for face in ("south", "east", "north", "west"):
            # sorted(), never .sort(): the list belongs to the shared texture index and specs build on 4 threads
            hits = sorted(tex.get(f"{tp}_{face}", []), key=lambda p: mod_of(p) != home)
            if hits:
                imgs[face] = hits[0]
    shown = imgs.get("south") or imgs.get("single") or (imgs.get("variants") or [None])[0]
    spec = {"subject": defname, "label": label, "template": "creature", "module": "flyer" if flyer else "walker",
            "candidate": "live", "provenance": f"live installed art, texPath {tp} ({mod_of(shown or f)}), graphicClass {gclass}",
            "description": desc, "tier": defname.split("_")[0] + "_", "invented": True,
            "size": {"drawSize": [draws[adult], draws[adult]]}, "source": f.replace(str(SRC) + "/", ""),
            "owner_kept": False}
    # true-scale panel beside the vanilla human
    import scale_panel as SP
    outdir.mkdir(parents=True, exist_ok=True)
    scale_src = imgs.get("east") or imgs.get("south") or imgs.get("single") or (imgs.get("variants") or [None])[0]
    if scale_src:
        compact, full = outdir / f"{defname}_scale.png", outdir / f"{defname}_scale_full.png"
        SP.render_panel(Path(scale_src).read_bytes(), {"kind": "animal", "drawSize": (draws[adult], draws[adult])},
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
    spec["graphic_class"] = gclass
    # owner keeps come from the art ledger (art.py status PROTECTED), never a hard-coded False
    files = [v for k, v in imgs.items() if isinstance(v, str) and k != "scale"] + list(imgs.get("variants") or [])
    kept = kept_lookup(files) if kept_lookup and files else []
    if kept is None:
        spec["owner_kept_unmeasured"] = "art ledger unreadable: owner_kept NOT established"
    elif kept:
        spec["owner_kept"], spec["kept_install"] = True, kept
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
