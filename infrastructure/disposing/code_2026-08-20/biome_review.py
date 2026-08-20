#!/usr/bin/env python3
"""biome_review.py — review every BiomeDef in the load set and mark keep/cut.

Biomes have no sprite, but they DO have a world-map tile texture, so this is a
contact sheet like the others: look at the tile, read the stats that decide
whether a biome earns a place on the planet, tick the ones to cut.

    python3 src/RimMandrake/Utils/biome_review.py        ->  http://localhost:8789

Decisions autosave to observed/inventory/decisions_biomes.json, keyed by defName
so they survive a regeneration.

Deliberately NOT shown: per-animal spawn frequency. Which beast lives where is
chain step 2 and a separate pass; this page answers "do we want this biome at
all".
"""
from __future__ import annotations

import base64
import glob
import json
import os
import re
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
INVENTORY = REPO / "observed" / "inventory"
DECISIONS = INVENTORY / "decisions_biomes.json"
BUNDLE_INDEX = INVENTORY / "bundle_textures" / "index.csv"
BUNDLE_DIR = INVENTORY / "bundle_textures"

LOWLOW = Path("/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios")
DEFDUMP = LOWLOW / "DefDump" / "defs" / "BiomeDef.json"
WORKSHOP = Path("/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100")
LOCALMODS = Path("/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods")

SUFFIXES = ("", "_south", "_north", "_east", "_a", "A", "_c", "C")


# ---------------------------------------------------------------- extraction
def _num(v, nd=2):
    if v is None:
        return ""
    if isinstance(v, (int, float)):
        s = f"{v:.{nd}f}".rstrip("0").rstrip(".")
        return s or "0"
    return str(v)


def _top(records, key, n=3):
    """Top-n entries of a commonality list, biggest first."""
    out = []
    for r in records or []:
        if not isinstance(r, dict):
            continue
        name = r.get(key)
        if not name:
            continue
        out.append((r.get("commonality", 0) or 0, str(name)))
    out.sort(reverse=True)
    return [n_ for _, n_ in out[:n]]


def _terrains(records, n=3):
    out = []
    for r in records or []:
        if isinstance(r, dict) and r.get("terrain"):
            out.append(str(r["terrain"]))
    return out[:n]


def load_biomes():
    raw = json.loads(DEFDUMP.read_text(encoding="utf-8", errors="replace"))
    defs = raw["defs"] if isinstance(raw, dict) else raw
    rows = []
    for d in defs:
        f = d.get("fields", {}) or {}
        rows.append({
            "defName": d.get("defName", ""),
            "label": d.get("label", "") or d.get("defName", ""),
            "mod": d.get("modName", "?"),
            "packageId": (d.get("packageId") or "").lower(),
            "desc": (f.get("description") or "").strip(),
            "texture": f.get("texture") or "",
            # -- does it even appear, and can you live there
            "generatesNaturally": bool(f.get("generatesNaturally")),
            "canBuildBase": bool(f.get("canBuildBase")),
            "canAutoChoose": bool(f.get("canAutoChoose")),
            "impassable": bool(f.get("impassable")),
            "isWaterBiome": bool(f.get("isWaterBiome")),
            "inVacuum": bool(f.get("inVacuum")),
            "isExtreme": bool(f.get("isExtremeBiome")),
            "settleWeight": _num(f.get("settlementSelectionWeight")),
            "settleWarning": (f.get("settleWarning") or ""),
            # -- what living there is like
            "movement": _num(f.get("movementDifficulty")),
            "forage": _num(f.get("forageability")),
            "plantDensity": _num(f.get("plantDensity")),
            "animalDensity": _num(f.get("animalDensity")),
            "diseaseMtb": _num(f.get("diseaseMtbDays"), 0),
            "regrowDays": _num(f.get("wildPlantRegrowDays"), 0),
            "constTemp": _num(f.get("constantOutdoorTemperature"), 0),
            # -- what it looks and feels like
            "terrains": _terrains(f.get("terrainsByFertility")),
            "weathers": _top(f.get("baseWeatherCommonalities"), "weather"),
            "nPlants": len(f.get("wildPlants") or []),
            "nAnimals": len(f.get("wildAnimals") or []),
            "packAnimals": [str(x) for x in (f.get("allowedPackAnimals") or [])][:4],
        })
    rows.sort(key=lambda r: (r["mod"].lower(), r["label"].lower()))
    return rows


# ------------------------------------------------------------------ textures
def package_dirs():
    """packageId (lower) -> mod folder. Cheap: one About.xml read per mod."""
    out = {}
    for about in glob.glob(str(WORKSHOP / "*" / "About" / "About.xml")) + \
                 glob.glob(str(LOCALMODS / "*" / "About" / "About.xml")):
        try:
            # read the whole file: packageId is not always near the top, and a
            # truncated read silently drops the mod from the map
            s = open(about, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        # 🪤 The mod's OWN packageId is not necessarily the first one in the file:
        # every <modDependencies> entry carries a <packageId> of its own, and they
        # are often declared above it. Strip the dependency blocks first.
        s = re.sub(r"<(modDependencies|loadAfter|loadBefore|incompatibleWith)"
                   r"[^>]*>.*?</\1>", "", s, flags=re.S | re.I)
        m = re.search(r"<packageId>([^<]+)</packageId>", s, re.I)
        if m:
            out.setdefault(m.group(1).strip().lower(), str(Path(about).parent.parent))
    return out


def bundle_lookup():
    """m_Name (lower) -> extracted png path. The base game's art lives here."""
    out = {}
    if not BUNDLE_INDEX.exists():
        return out
    import csv
    with open(BUNDLE_INDEX, encoding="utf-8-sig", errors="replace") as fh:
        for r in csv.DictReader(fh):
            out.setdefault(r["m_Name"].lower(), r["file"])
    return out


def resolve_textures(rows):
    """Find each biome's world tile. Loose PNGs first, then the bundle cache.

    Only the mod folders that actually own a biome are walked — walking the whole
    workshop tree for PNGs times out on this mount.
    """
    pkgs = package_dirs()
    bundles = bundle_lookup()

    # leaf name -> path, built ONLY for the ~15 mods that own a biome.
    # Walking the whole workshop tree for PNGs times out on this mount.
    loose = {}
    wanted_dirs = {pkgs[p] for p in {r["packageId"] for r in rows} if p in pkgs}
    for d in wanted_dirs:
        for dp, _dn, fn in os.walk(d):
            if "Textures" not in dp:
                continue
            for f in fn:
                if f.endswith(".png"):
                    loose.setdefault(f[:-4].lower(), os.path.join(dp, f))

    for r in rows:
        tex = r["texture"]
        r["img"] = ""
        r["imgsrc"] = ""
        if not tex:
            continue
        leaf = tex.split("/")[-1].lower()
        for suf in SUFFIXES:
            cand = (leaf + suf.lower()) if suf else leaf
            if cand in loose:
                r["img"], r["imgsrc"] = loose[cand], "loose"
                break
            if cand in bundles:
                p = bundles[cand]
                p = p if os.path.isabs(p) else str(BUNDLE_DIR / p)
                r["img"], r["imgsrc"] = p, "bundle"
                break
    return rows


def embed(path):
    try:
        with open(path, "rb") as fh:
            return "data:image/png;base64," + base64.b64encode(fh.read()).decode()
    except OSError:
        return ""


# ---------------------------------------------------------------------- page
CSS = """
:root{--bg:#14161a;--fg:#e8e6e3;--dim:#9aa0a6;--line:#2c3038;--cut:#7a2230;--keep:#1d3a24}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.45 system-ui,sans-serif}
header{position:sticky;top:0;background:#0f1114;border-bottom:1px solid var(--line);
       padding:10px 16px;z-index:5;display:flex;gap:18px;align-items:center;flex-wrap:wrap}
h1{font-size:16px;margin:0;font-weight:600}
.count{color:var(--dim)}
.modhdr{background:#1b1e24;padding:8px 16px;margin-top:22px;border-top:1px solid var(--line);
        font-weight:600;position:sticky;top:44px;z-index:4}
table{width:100%;border-collapse:collapse}
td,th{padding:7px 10px;border-bottom:1px solid var(--line);vertical-align:top;text-align:left}
th{color:var(--dim);font-weight:500;font-size:12px;white-space:nowrap}
tr.cut{background:var(--cut)}
tr.cut td{opacity:.72}
img.tile{width:52px;height:52px;object-fit:cover;border-radius:4px;background:#000;display:block}
.no-img{width:52px;height:52px;border:1px dashed #3a3f48;border-radius:4px;color:#555;
        font-size:10px;display:flex;align-items:center;justify-content:center}
.nm{font-weight:600}
.dn{color:var(--dim);font-size:11px;font-family:ui-monospace,monospace}
.desc{color:var(--dim);font-size:12px;max-width:46ch}
.flag{display:inline-block;padding:1px 6px;border-radius:9px;font-size:11px;margin:0 3px 3px 0;
      border:1px solid #3a3f48;color:#cfd4da;white-space:nowrap}
.flag.warn{border-color:#7a5a22;color:#f0c674}
.flag.bad{border-color:#7a2230;color:#f08a97}
.flag.ok{border-color:#2c5a34;color:#96d9a5}
.num{font-family:ui-monospace,monospace;white-space:nowrap}
.terr{color:var(--dim);font-size:11px;font-family:ui-monospace,monospace}
input[type=checkbox]{width:19px;height:19px;cursor:pointer}
button{background:#232830;color:var(--fg);border:1px solid var(--line);border-radius:5px;
       padding:5px 11px;cursor:pointer}
#saved{color:#96d9a5}
"""

JS = """
const rows=%(rows)s;
function state(){return JSON.parse(localStorage.getItem('biomecut')||'{}')}
function paint(){
  const s=state();let n=0;
  for(const r of rows){
    const tr=document.getElementById('r_'+r);
    const cb=document.getElementById('c_'+r);
    if(!tr)continue;
    const cut=!!s[r];cb.checked=cut;tr.classList.toggle('cut',cut);if(cut)n++;
  }
  document.getElementById('n').textContent=n;
}
function toggle(dn){const s=state();if(s[dn])delete s[dn];else s[dn]=1;
  localStorage.setItem('biomecut',JSON.stringify(s));paint();save();}
let t=null;
function save(){clearTimeout(t);t=setTimeout(()=>{
  fetch('/save',{method:'POST',body:JSON.stringify({cut:Object.keys(state())})})
   .then(()=>{const e=document.getElementById('saved');e.textContent='saved';
              setTimeout(()=>e.textContent='',1400)});},400)}
function clearAll(){localStorage.setItem('biomecut','{}');paint();save()}
window.addEventListener('DOMContentLoaded',()=>{
  fetch('/load').then(r=>r.json()).then(d=>{
    const s={};for(const k of (d.cut||[]))s[k]=1;
    localStorage.setItem('biomecut',JSON.stringify(s));paint();});
});
"""


def render(rows):
    body = []
    cur = None
    for r in rows:
        if r["mod"] != cur:
            if cur is not None:
                body.append("</table>")
            cur = r["mod"]
            n = sum(1 for x in rows if x["mod"] == cur)
            body.append(f'<div class="modhdr">{cur} <span class="count">· {n}</span></div>')
            body.append("<table><tr><th>cut</th><th>tile</th><th>biome</th>"
                        "<th>status</th><th>living there</th><th>ground &amp; weather</th>"
                        "<th>what it is</th></tr>")

        flags = []
        if not r["generatesNaturally"]:
            flags.append('<span class="flag bad">never generates</span>')
        if not r["canBuildBase"]:
            flags.append('<span class="flag bad">cannot settle</span>')
        elif not r["canAutoChoose"]:
            flags.append('<span class="flag warn">not auto-chosen</span>')
        if r["impassable"]:
            flags.append('<span class="flag bad">impassable</span>')
        if r["isWaterBiome"]:
            flags.append('<span class="flag">water</span>')
        if r["inVacuum"]:
            flags.append('<span class="flag warn">vacuum</span>')
        if r["isExtreme"]:
            flags.append('<span class="flag warn">extreme</span>')
        if r["constTemp"]:
            flags.append(f'<span class="flag warn">fixed {r["constTemp"]}&deg;C</span>')
        if r["settleWeight"] and r["settleWeight"] != "0":
            flags.append(f'<span class="flag ok">settle wt {r["settleWeight"]}</span>')
        if r["settleWarning"]:
            flags.append('<span class="flag warn">settle warning</span>')

        live = (f'<span class="num">move {r["movement"]} &middot; forage {r["forage"]}<br>'
                f'plants {r["plantDensity"]} &middot; beasts {r["animalDensity"]}<br>'
                f'disease {r["diseaseMtb"]}d &middot; regrow {r["regrowDays"]}d</span>')

        ground = ", ".join(r["terrains"]) or "&mdash;"
        weather = ", ".join(r["weathers"]) or "&mdash;"
        pack = ", ".join(r["packAnimals"])
        gw = (f'<span class="terr">{ground}</span><br><span class="terr">{weather}</span>'
              + (f'<br><span class="terr">pack: {pack}</span>' if pack else ""))

        img = (f'<img class="tile" src="{embed(r["img"])}" title="{r["texture"]}">'
               if r["img"] else '<div class="no-img">no tile</div>')

        eco = f'<span class="terr">{r["nPlants"]} plants &middot; {r["nAnimals"]} beasts</span>'
        desc = r["desc"].replace("<", "&lt;")
        if len(desc) > 260:
            desc = desc[:257] + "..."

        body.append(
            f'<tr id="r_{r["defName"]}">'
            f'<td><input type="checkbox" id="c_{r["defName"]}" '
            f'onchange="toggle(\'{r["defName"]}\')"></td>'
            f'<td>{img}</td>'
            f'<td><span class="nm">{r["label"]}</span><br><span class="dn">{r["defName"]}</span><br>{eco}</td>'
            f'<td>{"".join(flags) or "&mdash;"}</td>'
            f'<td>{live}</td>'
            f'<td>{gw}</td>'
            f'<td class="desc">{desc}</td></tr>')
    body.append("</table>")

    js = JS % {"rows": json.dumps([r["defName"] for r in rows])}
    return (f'<!doctype html><meta charset="utf-8"><title>Biome review</title>'
            f'<style>{CSS}</style>'
            f'<header><h1>Biome review</h1>'
            f'<span class="count">{len(rows)} biomes &middot; '
            f'{len({r["mod"] for r in rows})} mods</span>'
            f'<span class="count">cut: <b id="n">0</b></span>'
            f'<button onclick="clearAll()">clear all</button>'
            f'<span id="saved"></span>'
            f'<span class="count">tick = cut it</span></header>'
            f'{"".join(body)}<script>{js}</script>')


# -------------------------------------------------------------------- server
class Handler(BaseHTTPRequestHandler):
    page = b""
    rows = []

    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="text/html; charset=utf-8"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.startswith("/load"):
            cut = []
            if DECISIONS.exists():
                cut = json.loads(DECISIONS.read_text()).get("cut", [])
                cut = [c["defName"] if isinstance(c, dict) else c for c in cut]
            self._send(200, json.dumps({"cut": cut}).encode(), "application/json")
        else:
            self._send(200, self.page)

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        data = json.loads(self.rfile.read(n) or b"{}")
        cut = set(data.get("cut", []))
        by = {r["defName"]: r for r in self.rows}
        payload = {
            "updated": __import__("datetime").datetime.now().astimezone().isoformat(timespec="seconds"),
            "total_count": len(self.rows),
            "cut": [{"defName": d, "label": by.get(d, {}).get("label", ""),
                     "mod": by.get(d, {}).get("mod", "")} for d in sorted(cut)],
        }
        DECISIONS.parent.mkdir(parents=True, exist_ok=True)
        DECISIONS.write_text(json.dumps(payload, indent=1, ensure_ascii=False))
        self._send(200, json.dumps({"ok": True, "cut": len(cut)}).encode(), "application/json")


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8789
    rows = resolve_textures(load_biomes())
    have = sum(1 for r in rows if r["img"])
    print(f"{len(rows)} biomes · {len({r['mod'] for r in rows})} mods · "
          f"{have} tiles resolved, {len(rows)-have} without")
    Handler.rows = rows
    Handler.page = render(rows).encode()
    print(f"http://localhost:{port}   (decisions -> {DECISIONS})")
    HTTPServer(("127.0.0.1", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
