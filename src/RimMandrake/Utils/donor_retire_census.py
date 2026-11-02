#!/usr/bin/env python3
"""donor_retire_census.py — what still ties OUR content to the donor mods being retired (owner, 2026-10-18:
"Just put in placeholder art for now or donor copies and retire these mods!!! Just get it done.").

    python3 src/RimMandrake/Utils/donor_retire_census.py refs [--json OUT]   live (non-comment) references in src/
    python3 src/RimMandrake/Utils/donor_retire_census.py tex  [--json OUT]   our defs' texPaths the game does NOT serve
                                                                             from a mandrake.* mod
    python3 src/RimMandrake/Utils/donor_retire_census.py deps                active non-mandrake mods that hard-depend on
                                                                             a retiring donor
    python3 src/RimMandrake/Utils/donor_retire_census.py standin [--json OUT]  every XML text still drawing a StandIn/
                                                                             copy, and the art job that will retire it;
                                                                             exit 1 while any is UNCOVERED

refs  reads XML as ELEMENTS (comments never count): MayRequire/MayRequireAnyOf attributes, <li> text equal to a
      packageId (FindMod <mods>, About.xml modDependencies/loadAfter/loadBefore), <packageId> in modDependencies;
      .cs/.py/.json by plain string match (they have no comment-free parse here; each hit is listed).
tex   every texPath of a def defined by a mandrake.* mod (ThingDef body/extra + PawnKind bodies from gametex's
      deftex, TerrainDef texturePath, ThingDef uiIconPath — from the gametex DefDump capture) resolved with
      gametex.resolve_res: OURS (winner mandrake.*), DONOR (winner another mod, or only an inactive mod's copy, or a
      donor AssetBundle), VANILLA (ludeon.* loose or base bundles), MISSING (nowhere). UI/ icons are included.
      SANITY: a known-ours texPath must classify OURS, else the run aborts.
standin  every element text in src/ Defs+Patches XML that starts `StandIn/` (ANY tag: texPath, texturePath,
      pollutedTexturePath, leaflessGraphicPath ... — srctex's walk sees only tags containing "texpath" and misses
      terrain), joined to the artpipe queue (item STANDINS_RETIRE_AS_OUR_COATS_ARRIVE). A text is
        QUEUED    a pending/active dregen_ job targets it (its path, slot, install_to, or a def that draws it);
        RENDERED  a done job with status ok and a PNG in _artsrc/<id>/ targets it (the installer places it and
                  points the XML back: art_accept_finished.py);
        LANDED    the un-StandIn counterpart already exists in the same mod's Textures (repoint owed, not a render);
        FAILED    only failed jobs target it (requeue owed);   UNCOVERED  nothing targets it (file a job).
      FlowWorks is FOUNDRY's and listed apart (EXCLUDED), never counted as uncovered.
      COLLIDES  another mod of ours already ships the un-StandIn path (a rename is owed before any render);
        DONOR_DEF  the text decorates only a donor's def (a patch onto a donor gene): the regen gate never files it.
      Exit 1 while any text is FAILED or UNCOVERED. Coverage is per picture (facings, random-folder files).
      SANITY: the walker must see a built-in probe text and the queue must be readable, else it exits unreported.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SRC = REPO / "src"
sys.path.insert(0, str(REPO / "src/RimMandrake/Utils/art"))
sys.path.insert(0, str(REPO / "src/RimMandrake/Utils"))
import game_paths  # noqa: E402  the one path seam

# The retiring set: biome_sprint_kickoff_2026-10-15 §0.5.1 + DONOR_DEFS_PORT_TO_OURS_1's ten smaller donors.
DONORS = [
    "mlie.starwarsanimalcollection", "sarg.alphaanimals", "daria40k.alphaanimalspatchoutposts",
    "sarg.alphabiomes", "sarg.alphamemes", "sarg.alphagenes",
    "oskarpotocki.vfe.insectoid2", "who.vfee.isopodageneline", "mlie.horrors", "biomesteam.biomescaverns",
    "lingluo.cockroach", "regrowth.botr.core", "vanillaexpanded.vgeneticse",
]
# inactive mods whose OWN content paths our defs name (not retextures of base-game art): such a path is missing in game
CONTENT_DONORS = {"vanillaexpanded.vplantsesucculents"}
SKIP_DIRS = ("src/RimMandrake/FlowWorks/",)          # not ours to touch (coordinator, 2026-10-18)
MODSCONFIG = Path(game_paths.MODS_CONFIG)


def _donor_of(text: str):
    low = text.lower()
    return [d for d in DONORS if d in low]


def refs() -> list[dict]:
    out = []
    for p in sorted(SRC.rglob("*")):
        if not p.is_file() or p.suffix not in (".xml", ".cs", ".py", ".json"):
            continue
        rel = p.relative_to(REPO).as_posix()
        skip = rel.startswith(SKIP_DIRS)
        if p.suffix == ".xml":
            try:
                root = ET.parse(p).getroot()
            except ET.ParseError:
                txt = p.read_text(errors="replace")
                for d in _donor_of(txt):
                    out.append({"file": rel, "donor": d, "form": "UNPARSEABLE_XML", "skip": skip})
                continue
            parent = {c: q for q in root.iter() for c in q}
            for el in root.iter():
                for k, v in el.attrib.items():
                    for d in _donor_of(v):
                        out.append({"file": rel, "donor": d, "form": f"attr:{k}", "tag": el.tag,
                                    "value": v, "skip": skip})
                t = (el.text or "").strip()
                if t and len(t) < 120:
                    for d in _donor_of(t):
                        if t.lower() == d or el.tag == "packageId":
                            q = parent.get(el)
                            qq = parent.get(q) if q is not None else None
                            ctx = "/".join(x.tag for x in (qq, q) if x is not None)
                            out.append({"file": rel, "donor": d, "form": f"text:{ctx}/{el.tag}", "skip": skip})
        else:
            for i, line in enumerate(p.read_text(errors="replace").splitlines(), 1):
                for d in _donor_of(line):
                    out.append({"file": rel, "donor": d, "form": f"string{p.suffix}", "line": i,
                                "text": line.strip()[:160], "skip": skip})
    return out


def _texpaths():
    import gametex as G
    dt = G.deftex()
    cap = Path(dt["capture"]) / "defs"
    rows = []
    for dn, v in dt["defs"].items():
        pkg = v.get("packageId") or ""
        if not pkg.startswith("mandrake."):
            continue
        for t in v["tex"]:
            rows.append((dn, "ThingDef", "body", t, v.get("mod")))
        for t, role in (v.get("extra") or {}).items():
            rows.append((dn, "ThingDef", role, t, v.get("mod")))
    for typ, fld, role in (("TerrainDef", "texturePath", "terrain"), ("ThingDef", "uiIconPath", "icon")):
        f = cap / f"{typ}.json"
        for d in json.loads(f.read_text())["defs"]:
            if not (d.get("packageId") or "").startswith("mandrake."):
                continue
            t = (d.get("fields") or {}).get(fld)
            if isinstance(t, str) and t:
                rows.append((d["defName"], typ, role, t, d.get("modName")))
    keyre = re.compile(r"(texPath|texturePath|iconPath|IconPath|GraphicPath|texPathFaction)$")

    def walk(v, dn, typ, mod, path=""):
        if isinstance(v, dict):
            for k, x in v.items():
                if isinstance(x, str) and x and keyre.search(k):
                    rows.append((dn, typ, f"{path}{k}", x, mod))
                else:
                    walk(x, dn, typ, mod, f"{path}{k}.")
        elif isinstance(v, list):
            for x in v:
                walk(x, dn, typ, mod, path)
    for f in sorted(cap.glob("*.json")):              # every other def type: icons, flecks, motes, hediffs ...
        if f.stem in ("ThingDef", "PawnKindDef", "TerrainDef"):
            continue
        try:
            defs = json.loads(f.read_text()).get("defs") or []
        except (ValueError, OSError):
            continue
        for d in defs:
            if (d.get("packageId") or "").startswith("mandrake."):
                walk(d.get("fields") or {}, d["defName"], f.stem, d.get("modName"))
    return dt["capture"], rows


def classify(res: str, ix) -> dict:
    import gametex as G
    r = G.resolve_res(res, ix)
    win = next((c for c in r["copies"] if c.get("winner")), None)
    if win:
        pkg = (win["packageId"] or "").lower()
        cat = "OURS" if pkg.startswith("mandrake.") else ("VANILLA" if pkg.startswith("ludeon.") else "DONOR")
        if cat == "DONOR":                               # a retexture of a base-game path: vanilla serves it without
            vb = [b for b in G.resolve_res(res, {**ix, "files": {}})["bundle"]   # the donor
                  if (b["source"] or "").lower().startswith("ludeon.")]
            if vb:
                cat = "VANILLA_RETEXTURED"
        return {"cat": cat, "by": pkg, "file": next(iter(win["faces"].values()), None)}
    if not r["bundle"] and r["copies"]:                  # resolve_res fills bundle only when no copy exists
        r["bundle"] = G.resolve_res(res, {**ix, "files": {}})["bundle"]
    if r["bundle"]:
        b = next((x for x in r["bundle"] if (x["source"] or "").lower().startswith("ludeon.")), r["bundle"][0])
        src = (b["source"] or "").lower()
        return {"cat": "VANILLA" if src.startswith("ludeon.") else "DONOR_BUNDLE", "by": src, "file": b["path"]}
    if r["copies"]:                                      # only inactive mods ship it
        c = r["copies"][0]
        pkg = (c["packageId"] or "").lower()
        # a retexture pack shipping a base-game path: Core's art is not fully indexed, so this is vanilla, unproven
        cat = "DONOR_INACTIVE" if pkg in DONORS or pkg in CONTENT_DONORS \
            or not res.startswith(("Things/", "Terrain/", "UI/", "Buildings/")) else "VANILLA_UNINDEXED"
        return {"cat": cat, "by": pkg, "file": next(iter(c["faces"].values()), None)}
    return {"cat": "MISSING", "by": None, "file": None}


def tex() -> dict:
    import gametex as G
    ix = G.index()
    probe = classify("Things/Building/CrawlerRoad/RSW_WreckedSkiff", ix)
    if probe["cat"] != "OURS":
        raise SystemExit(f"SANITY FAIL: known-ours texPath classified {probe} — instrument blind, nothing reported")
    cap, rows = _texpaths()
    out, seen = [], {}
    for dn, typ, role, t, mod in rows:
        if t not in seen:
            seen[t] = classify(t, ix)
        out.append({"def": dn, "type": typ, "role": role, "tex": t, "mod": mod, **seen[t]})
    return {"capture": cap, "index_built": ix.get("built"), "load_order": ix.get("load_order"), "rows": out}


def srctex() -> dict:
    """Today's src/ (not a dump): every texPath our Defs/Patches XML names (placeholder_lint.texpaths, the
    texture_gap_lint walk), resolved first against our own src Textures, then by `classify`."""
    import gametex as G
    import placeholder_lint as PL
    ix = G.index()
    roots = PL.texture_roots()
    out = []
    for tp, files in PL.texpaths().items():
        files = sorted(files) if not isinstance(files, str) else [files]
        if PL.resolve(tp, roots):
            out.append({"tex": tp, "cat": "OURS_SRC", "by": None, "file": None, "files": files})
            continue
        c = classify(tp, ix)
        out.append({"tex": tp, **c, "files": files})
    return {"index_built": ix.get("built"), "load_order": ix.get("load_order"), "rows": out}


STANDIN_STATES = ("QUEUED", "RENDERED", "LANDED", "COLLIDES", "DONOR_DEF", "FAILED", "UNCOVERED")
BLOCKING = ("FAILED", "UNCOVERED")
STATE_ITEMS = {"COLLIDES": "STANDIN_PLANTS_RENAME_PATH_ALREADY_TAKEN", "DONOR_DEF": "HUTT_EYES_DECIDE_GENE_IS_NOT_OURS"}


def our_defnames() -> set:
    """Every defName a Defs/ XML of ours defines (patch-added defs included)."""
    out = set()
    for p in SRC.rglob("*.xml"):
        if "/Defs/" not in p.as_posix() and "/Patches/" not in p.as_posix():
            continue
        try:
            for el in ET.parse(p).getroot().iter("defName"):
                if (el.text or "").strip():
                    out.add(el.text.strip())
        except (ET.ParseError, OSError):
            continue
    return out


def _collides(mod: str, pic: str) -> list:
    """Other mods of ours that already ship the un-StandIn path `pic` (a file, facing or folder picture): a render
    installed there would share the texPath with someone else's art, so the regen gate refuses it by rule."""
    out = []
    for troot in SRC.glob("*/*/Textures"):
        m = troot.parent.relative_to(REPO).as_posix()
        if m != mod and Path(f"{troot / pic}.png").is_file():
            out.append(f"{m}/Textures/{pic}.png")
    return out


def _walk_standins(root, rel: str, out: dict):
    """Add every leaf text under `root` that starts StandIn/ (any tag) to `out`, with its file, tag and def."""
    parent = {c: q for q in root.iter() for c in q}
    for el in root.iter():
        t = (el.text or "").strip().replace("\\", "/")
        if not isinstance(el.tag, str) or not t.startswith("StandIn/") or list(el):
            continue
        r = out.setdefault(t, {"files": set(), "defs": set(), "tags": set()})
        r["files"].add(rel)
        r["tags"].add(el.tag)
        q = parent.get(el)          # nearest enclosing def (a patch-ADDED def is nested in <value>), else the
        while q is not None:        # def a patch operation's <xpath> names (a node added to someone's GeneDef)
            dn = (q.findtext("defName") or "").strip()
            names = re.findall(r"defName\s*=\s*[\"']([^\"']+)[\"']", q.findtext("xpath") or "")
            if dn or names:
                r["defs"].update([dn] if dn else names)
                break
            q = parent.get(q)


_PROBE = ("<Patch><Operation><xpath>/Defs/GeneDef[defName=\"P_Gene\"]</xpath><value><TerrainDef>"
          "<pollutedTexturePath>StandIn/P/T</pollutedTexturePath></TerrainDef></value></Operation></Patch>")


def standin_texts() -> dict:
    """{StandIn text: {"files": [...], "defs": [...], "tags": [...]}} over every Defs/Patches XML in src/.
    SANITY: the walker must first find the probe's pollutedTexturePath text and its xpath def, else nothing is
    reported (a tag-name filter once hid 34 of 55 texts)."""
    probe: dict = {}
    _walk_standins(ET.fromstring(_PROBE), "probe", probe)
    if probe.get("StandIn/P/T", {}).get("defs") != {"P_Gene"}:
        raise SystemExit(f"SANITY FAIL: the StandIn walker cannot see a probe text ({probe}) — nothing reported")
    out: dict = {}
    for p in sorted(SRC.rglob("*.xml")):
        rel = p.relative_to(REPO).as_posix()
        if "/Defs/" not in rel and "/Patches/" not in rel:
            continue
        try:
            root = ET.parse(p).getroot()
        except (ET.ParseError, OSError):
            continue
        _walk_standins(root, rel, out)
    return {k: {f: sorted(v) for f, v in r.items()} for k, r in sorted(out.items())}


# RimWorld mask files: `<path>_m` (single) and `<path>_<facing>m` (multi); never a bare trailing "m" ("Palm")
MASK_STEM = re.compile(r"(_m|_(south|east|north|west)m)$|[Mm]ask")
FACINGS3 = ("east", "south", "north")       # a missing _west is drawn as east mirrored: no render owes one


def standin_files(mod: str, text: str) -> list:
    """[(rel-without-.png under Textures, facing or None)] of the stand-in `text` in `mod`: its facings, a single
    file, or every picture of a Graphic_Random folder. Masks are no picture and are left out."""
    troot = REPO / mod / "Textures"
    base = troot / text
    if base.is_dir():
        return [(q.relative_to(troot).as_posix()[:-4], None) for q in sorted(base.glob("*.png"))
                if not MASK_STEM.search(q.stem)]
    fac = [f for f in FACINGS3 if Path(f"{base}_{f}.png").is_file()]
    if fac:
        return [(text, f) for f in fac]
    return [(text, None)] if Path(f"{base}.png").is_file() else []


def _mods_of(files: list) -> list:
    return sorted({f.split("/Defs/")[0].split("/Patches/")[0] for f in files})


def artpipe_jobs(art: Path) -> list:
    """Every dregen_ job in pending/active/done/failed: {id, state, ok, keys} where keys are the paths it covers."""
    jobs = []
    for st in ("pending", "active", "done", "failed"):
        d = art / st
        if not d.is_dir():
            raise SystemExit(f"SANITY FAIL: artpipe queue {d} unreadable — nothing reported")
        for f in d.iterdir():
            if not f.name.startswith("dregen_") or not f.name.endswith(".json") or f.name.endswith(".manifest.json"):
                continue
            try:
                j = json.loads(f.read_text())
            except FileNotFoundError:
                continue
            except (OSError, ValueError):
                j = {}
            # install_to is the exact file; only without it do slot / target_texpath say where it goes (fill_queue
            # back-fills target_texpath with the def's MAIN texture, so a leafless job would "cover" the tree itself)
            keys = set()
            it = (j.get("install_to") or "").split("/Textures/", 1)
            if len(it) == 2:
                keys.add(re.sub(r"\.png$", "", it[1]).removeprefix("StandIn/"))
            else:
                for k in ("target_texpath", "slot"):
                    v = (j.get(k) or "").strip()
                    if v:
                        keys.add(v.removeprefix("StandIn/"))
            fac = j.get("facings") if isinstance(j.get("facings"), list) else []
            for k in list(keys):                # a facing template renders exactly those facings, nothing else
                if "{facing}" in k:
                    keys.discard(k)
                    keys |= {k.replace("{facing}", f) for f in (fac or FACINGS3)}
                elif fac and len(it) != 2:
                    keys |= {f"{k}_{f}" for f in fac}
            ok = False
            if st == "done":
                man = d / (f.stem + ".manifest.json")
                try:
                    ok = json.loads(man.read_text()).get("status") == "ok"
                except (OSError, ValueError):
                    ok = False
                ok = ok and any((art / "_artsrc" / f.stem).glob("*.png"))
            jobs.append({"id": f.stem, "state": st, "ok": ok, "def": j.get("target_def"), "keys": keys})
    return jobs


def standin(art: Path | None = None, texts: dict | None = None) -> dict:
    import bulk_accept_renders as BA
    art = Path(art or BA.ART)
    if texts is None:
        texts = standin_texts()
    jobs = artpipe_jobs(art)
    ours = our_defnames()
    rows = []
    for t, r in texts.items():
        orig = t.removeprefix("StandIn/")
        excluded = all(f.startswith(SKIP_DIRS) for f in r["files"])
        # coverage is per PICTURE: every facing / random-folder file of the stand-in needs its own job
        pics = [(k.removeprefix("StandIn/") + (f"_{f}" if f else "")) for m in _mods_of(r["files"])
                for k, f in standin_files(m, t)] or [orig]
        hit, per = [], {}
        for pic in pics:
            js = [j for j in jobs if pic in j["keys"]]
            hit += js
            landed = any(Path(f"{REPO / m / 'Textures' / pic}.png").is_file() for m in _mods_of(r["files"]))
            per[pic] = "LANDED" if landed else ("QUEUED" if any(j["state"] in ("pending", "active") for j in js) else
                        "RENDERED" if any(j["state"] == "done" and j["ok"] for j in js) else
                        "FAILED" if js else "UNCOVERED")
        hint = sorted({j["id"] for j in jobs if j["def"] and j["def"] in r["defs"]} - {j["id"] for j in hit})
        q = sorted({j["id"] for j in hit if j["state"] in ("pending", "active")})
        done = sorted({j["id"] for j in hit if j["state"] == "done" and j["ok"]})
        failed = sorted({j["id"] for j in hit if j["state"] == "failed"})
        mods = _mods_of(r["files"])
        for pic, v in list(per.items()):        # a refused/unfiled picture whose path another mod of ours already
            if v in ("FAILED", "UNCOVERED") and any(_collides(m, pic) for m in mods):   # ships: a rename is owed
                per[pic] = "COLLIDES"
        if r["defs"] and not set(r["defs"]) & ours:  # decorates only a DONOR def (a patch onto a donor gene): the
            per = {p: ("DONOR_DEF" if v == "UNCOVERED" else v) for p, v in per.items()}   # gate never files it
        got = set(per.values())
        if excluded:
            state = "EXCLUDED"
        else:                                   # the worst picture decides; LANDED only when every picture has
            state = next(s for s in ("UNCOVERED", "FAILED", "COLLIDES", "DONOR_DEF", "QUEUED", "RENDERED", "LANDED")
                         if s in got)           # its un-StandIn twin on disk (a repoint is owed)
        uncovered_pics = sorted(p for p, v in per.items() if v not in ("QUEUED", "RENDERED", "LANDED"))
        rows.append({"text": t, "state": state, "queued": q, "rendered": done, "failed": failed,
                     "pictures": per, "pictures_owed": uncovered_pics, "def_jobs_hint": hint, **r})
    return {"artpipe": str(art), "jobs_read": len(jobs), "rows": rows}


def deps():
    """Every installed mod's About.xml (both game roots) — not the texture index, which skips mods with no Textures."""
    active = {l.text.strip().lower() for l in ET.parse(MODSCONFIG).getroot().find("activeMods")}
    roots = [Path("/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods"),
             Path("/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100")]
    hits, seen = [], 0
    for root in roots:
        for d in root.iterdir():
            about = d / "About" / "About.xml"
            try:
                r = ET.parse(about).getroot()
            except (ET.ParseError, OSError):
                continue
            pkg = (r.findtext("packageId") or "").strip().lower()
            if pkg not in active or pkg.startswith(("mandrake.", "ludeon.")):
                continue
            seen += 1
            md = r.find("modDependencies")
            for el in (md.iter("packageId") if md is not None else []):
                v = (el.text or "").strip().lower()
                if v in DONORS:
                    hits.append((pkg, v, pkg in DONORS))
    print(f"active non-mandrake mods read: {seen}; hard dependencies on a retiring donor: {len(hits)}")
    for pkg, v, internal in hits:
        print(f"   {pkg} -> {v}" + ("   (itself retiring)" if internal else ""))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["refs", "tex", "srctex", "deps", "standin"])
    ap.add_argument("--json")
    a = ap.parse_args(argv)
    if a.cmd == "deps":
        deps()
        return 0
    if a.cmd == "standin":
        data = standin()
        rows = data["rows"]
        c = Counter(r["state"] for r in rows)
        print(f"StandIn/ texts in src/ XML: {len(rows)}   (dregen_ jobs read: {data['jobs_read']} in {data['artpipe']})")
        for st in STANDIN_STATES + ("EXCLUDED",):
            print(f"  {st:10} {c.get(st, 0)}" + (f"   (item {STATE_ITEMS[st]})" if st in STATE_ITEMS else ""))
        for r in rows:
            if r["state"] not in ("QUEUED", "RENDERED", "EXCLUDED"):
                why = ",".join(r["failed"][:2]) if r["failed"] else (
                    "def has " + r["def_jobs_hint"][0] if r["def_jobs_hint"] else "")
                print(f"    {r['state']:9} {r['text']:60} {','.join(r['defs'][:3])}  {why}")
        if a.json:
            Path(a.json).write_text(json.dumps(data, indent=1, default=sorted))
        return 1 if any(c.get(b) for b in BLOCKING) else 0
    if a.cmd == "refs":
        rs = refs()
        c = Counter((r["donor"], r["form"].split(":")[0] + (":" + r["form"].split(":")[1] if ":" in r["form"] else ""))
                    for r in rs if not r["skip"])
        print(f"live references in src/ (FlowWorks excluded: {sum(1 for r in rs if r['skip'])} there): "
              f"{sum(1 for r in rs if not r['skip'])}")
        for (d, f), n in sorted(c.items()):
            print(f"  {n:4}  {d:36} {f}")
        data = rs
    elif a.cmd == "srctex":
        data = srctex()
        rows = data["rows"]
        print(f"texPaths named by src/ XML: {len(rows)}")
        for cat, n in Counter(r["cat"] for r in rows).most_common():
            print(f"  {cat:18} {n}")
        for (cat, b), n in Counter((r["cat"], r["by"]) for r in rows
                                   if r["cat"] not in ("OURS_SRC", "VANILLA")).most_common(40):
            print(f"    {cat:18} {str(b):45} {n}")
    else:
        data = tex()
        rows = data["rows"]
        print(f"capture {data['capture']}; index {data['index_built']}; {data['load_order']}")
        print(f"texPath slots of mandrake.* defs: {len(rows)} ({len({r['tex'] for r in rows})} distinct texPaths)")
        for cat, n in Counter(r["cat"] for r in rows).most_common():
            print(f"  {cat:15} {n}")
        by = Counter((r["cat"], r["by"]) for r in rows if r["cat"] not in ("OURS",))
        for (cat, b), n in by.most_common(40):
            print(f"    {cat:15} {str(b):45} {n}")
    if a.json:
        Path(a.json).write_text(json.dumps(data, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
