#!/usr/bin/env python3
"""Contact sheet for the 70 RimMandrake* xenotype icons, for the owner to triage.

WHY
===
The icons these xenotypes point at are mostly NOT LOADED on 1.6. Outer Rim keeps
43 species icons in `Common_Old/`, and its LoadFolders.xml routes 1.6 at
`Common/` instead, which holds none. So the art exists on disk and is invisible
in game. Another 17 point at vanilla's generic numbered "custom xenotype"
placeholders, which load fine and say nothing about the species.

The art is therefore a three-way decision per species that only the owner can
make by LOOKING at it: bring it over as-is, regenerate it, or drop the species.
This sheet puts the actual pixels in front of them at a size where that judgement
is possible, and lets them record the call.

OUTPUT: one self-contained HTML file, images inlined as base64 so it can be
opened from anywhere with no server and no broken relative paths.
"""
import base64
import io
import json
import os
import re
import subprocess
import sys

WS = "/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100"
GAME = "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld"
XENO = "src/Jawa/RimMandrake_StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml"
OUT = "design/Jawa/worldbuilding/review/xenotype_art_selector.html"
CACHE = "/tmp/claude-1000/-mnt-d-Luke-dev-Rimworld/texture_index.json"
# Bundle-extracted art. Biotech and several packs ship ZERO loose PNGs -- every
# icon lives inside a Unity AssetBundle, so a find(1) sweep reports them absent
# when they are merely compiled. genome_art_cache.py unpacks them; filenames are
# the RimWorld texture path with `/` written as `%`.
ART_CACHE = "observed/genome/art_cache"

# vanilla ships these inside Unity asset bundles, so they cannot be read off
# disk -- but they DO load. Absence from the index is not absence from the game.
VANILLA_PREFIXES = ("UI/Icons/Xenotypes/",)
PLACEHOLDER = re.compile(r"CustomXenotypeIcon\d+$", re.I)


def texture_index():
    if os.path.isfile(CACHE):
        return json.load(io.open(CACHE, encoding="utf-8"))
    idx = {}
    r = subprocess.run(["find", WS, GAME + "/Data", GAME + "/Mods",
                        "-type", "f", "-name", "*.png"],
                       capture_output=True, text=True, timeout=1800)
    for line in r.stdout.splitlines():
        idx.setdefault(os.path.basename(line)[:-4].lower(), []).append(line)
    return idx


def parse_defs():
    s = io.open(XENO, encoding="utf-8").read()
    out = []
    for blk in re.findall(r"<XenotypeDef>(.*?)</XenotypeDef>", s, re.S):
        def g(tag):
            m = re.search(r"<%s>(.*?)</%s>" % (tag, tag), blk, re.S)
            return m.group(1).strip() if m else ""
        out.append({
            "defName": g("defName"),
            "label": g("label"),
            "icon": g("iconPath"),
            "desc": g("description"),
            "genes": len(re.findall(r"<li>", blk)),
        })
    return out


def classify(icon, idx):
    """Three states, and the distinction that matters is LOADED vs merely
    PRESENT. A file under Common_Old is on disk and dead; a file inside a
    vanilla asset bundle is invisible here and alive."""
    if PLACEHOLDER.search(icon or ""):
        return "placeholder", None
    if any(icon.startswith(p) for p in VANILLA_PREFIXES):
        return "vanilla", None
    base = (icon or "").rsplit("/", 1)[-1].lower()
    hits = idx.get(base) or []
    if not hits:
        return "missing", None
    dead = all("common_old" in h.lower() or "/1.4/" in h or "/1.5/" in h
               for h in hits)
    return ("dead" if dead else "live"), hits[0]


def png_size(p):
    import struct
    try:
        with io.open(p, "rb") as f:
            h = f.read(24)
        if h[:8] != b"\x89PNG\r\n\x1a\n":
            return None
        return struct.unpack(">II", h[16:24])
    except Exception:
        return None


def art_pool(idx):
    """Every candidate icon on disk OR unpacked from a bundle, by basename."""
    pool = {}
    for base, paths in idx.items():
        pool.setdefault(base, []).extend(paths)
    try:
        for fn in os.listdir(ART_CACHE):
            if fn.endswith(".png"):
                key = fn[:-4].split("%")[-1].lower()
                pool.setdefault(key, []).append(os.path.join(ART_CACHE, fn))
    except OSError:
        pass
    return pool


def best_art(label, defname, pool):
    """Highest-resolution XENOTYPE PORTRAIT for this species.

    🔴 Substring matching on the species name is catastrophically wrong and was
    the first thing I shipped: `Hutt` matches "CrashedThemisS-hutt-le",
    `Gand` matches "Big -and- Small Framework", `Bith` matches half the game.
    The species name is far too short a needle to throw at 77,000 filenames.

    So the path must LOOK like a xenotype icon, and the species must match the
    part of the name that identifies it, not appear anywhere inside it. Head and
    gene textures (`heads/herglic/herglic_south`, `Gene_DurosHead`) are excluded
    on the same grounds: they are art OF the species but they are not its icon.
    """
    key = re.sub(r"[^a-z0-9]", "", (label or "").lower())
    alt = re.sub(r"[^a-z0-9]", "", (defname or "").replace("RimMandrake", "").lower())
    if not key:
        return None
    hits = []
    for base, paths in pool.items():
        bl = base.lower()
        for p in paths:
            pl = p.lower().replace("\\", "/")
            # 1. the path has to be a xenotype-icon location
            in_icon_tree = ("xenotypeicons" in pl or "icons/xenotypes" in pl
                            or "%xenotypeicons%" in pl or "icons%xenotypes" in pl)
            named_icon = bl.startswith("xenotype_") or bl.startswith("xeno_")
            if not (in_icon_tree or named_icon):
                continue
            # 2. and the SPECIES part has to match, not merely occur
            stem = re.sub(r"^(xenotype|xeno)[_%]", "", bl)
            stem = re.sub(r"[^a-z0-9]", "", stem)
            if stem not in (key, alt) and key not in (stem,) and alt not in (stem,):
                continue
            sz = png_size(p)
            if sz:
                hits.append((sz[0] * sz[1], sz, p))
    hits.sort(reverse=True)
    return hits[0] if hits else None


def cache_path(icon):
    """Resolve a RimWorld texture path against the bundle-extracted cache."""
    if not icon:
        return None
    flat = icon.replace("/", "%").lower() + ".png"
    direct = os.path.join(ART_CACHE, flat)
    if os.path.isfile(direct):
        return direct
    # some packs nest one level deeper than the def's path implies; fall back to
    # the distinctive basename, which is what actually identifies the icon
    base = icon.rsplit("/", 1)[-1].lower()
    try:
        for fn in os.listdir(ART_CACHE):
            if fn.lower().endswith("%" + base + ".png") or fn.lower() == base + ".png":
                return os.path.join(ART_CACHE, fn)
    except OSError:
        pass
    return None


def b64(path):
    if not path or not os.path.isfile(path):
        return None
    try:
        return base64.b64encode(io.open(path, "rb").read()).decode("ascii")
    except OSError:
        return None


STATE_COPY = {
    "rescue": ("RESCUABLE", "Sharp art exists in one of the packs. This is the "
               "best available version, not the one the REMIX was pointing at."),
    "lowres": ("LOW RES ONLY", "Nothing better than 64px exists; it will look "
               "soft at any usable size."),
    "noart": ("NO SPECIES ART", "No portrait for this species anywhere on disk "
              "or in any bundle. Regenerate it or drop the species."),
    "dead": ("ON DISK, NOT LOADED",
             "Outer Rim keeps it in Common_Old; 1.6 loads Common. Copying it "
             "into our own Textures folder makes it work."),
    "live": ("LOADED", "Already works in game."),
    "vanilla": ("VANILLA", "Ships inside a Unity asset bundle, so it cannot be "
                "previewed here, but it loads."),
    "placeholder": ("GENERIC PLACEHOLDER",
                    "Vanilla's numbered custom-xenotype icon. Loads, but says "
                    "nothing about the species."),
    "missing": ("NO ART FOUND", "No file of that name anywhere on disk."),
}


def main():
    idx = texture_index()
    pool = art_pool(idx)
    defs = parse_defs()
    rows = []
    for d in defs:
        best = best_art(d["label"], d["defName"], pool)
        if best:
            _area, (w, h), path = best
            d["res"] = "%dx%d" % (w, h)
            d["src"] = os.path.basename(path)
            state = "rescue" if w >= 128 else "lowres"
            img = b64(path)
        else:
            d["res"] = ""
            d["src"] = ""
            state, img = "noart", None
        rows.append((d, state, None, img))

    order = {"noart": 0, "lowres": 1, "rescue": 2}
    rows.sort(key=lambda r: (order.get(r[1], 9), r[0]["label"].lower()))
    counts = {}
    for _, st, _, _ in rows:
        counts[st] = counts.get(st, 0) + 1

    h = []
    h.append("<!doctype html><meta charset='utf-8'>")
    h.append("<title>Xenotype art selector</title>")
    h.append("""<style>
 body{background:#14161a;color:#e8e6e3;font:14px/1.5 system-ui,sans-serif;margin:0;padding:24px}
 h1{font-size:20px;margin:0 0 4px} .sub{color:#9aa0a6;margin-bottom:18px}
 .legend{display:flex;gap:18px;flex-wrap:wrap;margin:0 0 20px;font-size:13px}
 .legend b{padding:2px 8px;border-radius:4px}
 .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:14px}
 .card{background:#1d2027;border:1px solid #2c313a;border-radius:8px;padding:12px}
 .card.noart{border-color:#7a2a2a}.card.lowres{border-color:#6a6320}
 .card.rescue{border-color:#2a6a3a}
 .art{display:flex;align-items:center;justify-content:center;height:96px;
      background:#0e1013;border-radius:6px;margin-bottom:10px}
 .art img{width:80px;height:80px;image-rendering:pixelated}
 .none{color:#6a7078;font-size:12px;text-align:center}
 .name{font-weight:600} .dn{color:#7f868f;font-size:11px;font-family:ui-monospace,monospace;word-break:break-all}
 .tag{display:inline-block;font-size:10px;padding:1px 6px;border-radius:3px;margin:6px 0}
 .t-noart{background:#7a2a2a}.t-lowres{background:#6a6320}.t-rescue{background:#2a6a3a}
 .why{color:#9aa0a6;font-size:11px;margin-bottom:8px}
 .pick{display:flex;gap:4px} .pick label{flex:1;text-align:center;font-size:11px;
   padding:5px 2px;border:1px solid #343a44;border-radius:5px;cursor:pointer;background:#171a1f}
 .pick input{display:none}
 .pick input:checked + span{font-weight:700}
 .pick label:has(input[value=keep]:checked){background:#20402c;border-color:#3f7a52}
 .pick label:has(input[value=regen]:checked){background:#403520;border-color:#7a6a2a}
 .pick label:has(input[value=drop]:checked){background:#402020;border-color:#7a3a3a}
 #bar{position:sticky;top:0;background:#14161a;padding:12px 0;z-index:5;
      border-bottom:1px solid #2c313a;margin-bottom:18px}
 button{background:#2f6feb;color:#fff;border:0;padding:9px 16px;border-radius:6px;
        font-size:14px;cursor:pointer} #tally{color:#9aa0a6;margin-left:14px}
 textarea{width:100%;height:180px;margin-top:12px;background:#0e1013;color:#e8e6e3;
          border:1px solid #2c313a;border-radius:6px;padding:10px;font-family:ui-monospace,monospace;font-size:12px}
</style>""")
    h.append("<h1>Xenotype art selector &mdash; %d species</h1>" % len(rows))
    h.append("<div class='sub'>Pick one per species. <b>Keep</b> = bring this art "
             "across as-is. <b>Regen</b> = the species stays, the art gets remade. "
             "<b>Drop</b> = cut the species entirely.</div>")
    h.append("<div class='legend'>")
    for st in ("noart", "lowres", "rescue"):
        if counts.get(st):
            h.append("<span><b class='t-%s'>%s</b> &times;%d &mdash; %s</span>"
                     % (st, STATE_COPY[st][0], counts[st], STATE_COPY[st][1]))
    h.append("</div>")
    h.append("<div id='bar'><button onclick='exportPicks()'>Export choices</button>"
             "<span id='tally'></span><textarea id='out' style='display:none'></textarea></div>")
    h.append("<div class='grid'>")
    for d, state, path, img in rows:
        h.append("<div class='card %s'>" % state)
        h.append("<div class='art'>")
        if img:
            h.append("<img src='data:image/png;base64,%s'>" % img)
        else:
            h.append("<div class='none'>%s<br>no preview</div>" % STATE_COPY[state][0])
        h.append("</div>")
        h.append("<div class='name'>%s</div>" % d["label"])
        h.append("<div class='dn'>%s</div>" % d["defName"])
        h.append("<span class='tag t-%s'>%s</span>" % (state, STATE_COPY[state][0]))
        h.append("<div class='why'>%d genes%s</div>"
                 % (d["genes"], (" &middot; <b>%s</b>" % d["res"]) if d["res"] else ""))
        h.append("<div class='pick'>")
        for val, lab in (("keep", "Keep"), ("regen", "Regen"), ("drop", "Drop")):
            chk = " checked" if (val == "keep" and state == "rescue") else ""
            h.append("<label><input type='radio' name='%s' value='%s'%s>"
                     "<span>%s</span></label>" % (d["defName"], val, chk, lab))
        h.append("</div></div>")
    h.append("</div>")
    h.append("""<script>
function tally(){const c={keep:0,regen:0,drop:0};
 document.querySelectorAll('input:checked').forEach(i=>c[i.value]++);
 document.getElementById('tally').textContent =
   c.keep+' keep · '+c.regen+' regen · '+c.drop+' drop';}
document.addEventListener('change',tally); tally();
function exportPicks(){const o={};
 document.querySelectorAll('input:checked').forEach(i=>o[i.name]=i.value);
 const t=document.getElementById('out'); t.style.display='block';
 t.value=JSON.stringify(o,null,1); t.select();}
</script>""")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    io.open(OUT, "w", encoding="utf-8").write("\n".join(h))
    print("wrote %s" % OUT)
    for st in ("noart", "lowres", "rescue"):
        if counts.get(st):
            print("  %-12s %3d  %s" % (st, counts[st], STATE_COPY[st][0]))


if __name__ == "__main__":
    sys.exit(main())
