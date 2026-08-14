#!/usr/bin/env python3
"""Render the genome register: every candidate xenotype, aligned by gene.

WHAT IT ANSWERS
===============
"Which genes are in which race, and where do two implementations of the same
species disagree?" Three Star Wars xenotype packs are live at once -- BTD REMIX
(70), guy762 Star Wars Xenotypes (58) and Outer Rim Galactic Diversity (44) --
and 172 of the 250 installed xenotypes come from them. They are near-duplicate
species sets under different defName prefixes. Nobody can pick a pack by reading
three folders; you have to see Twi'lek next to Twi'lek next to Twi'lek with the
gene columns lined up. That is what this builds.

DATA SOURCE
===========
The LIVE def dump, not the on-disk XML:

    <LocalLow>/DefDump/defs/XenotypeDef.json     250 defs, post-patch
    <LocalLow>/DefDump/defs/GeneDef.json        4833 defs

Post-patch matters. The XML on disk is what mods ship; the dump is what the game
actually built after every PatchOperation ran, and it includes the ~190 genes
RimWorld generates at load from GeneTemplateDefs (AptitudeRemarkable_Mining and
friends) which exist in no file anywhere.

ART
===
Vanilla and several big mods ship art compiled into Unity AssetBundles, so icons
come from two places: loose PNGs found by walking active mods, and
`observed/genome/art_cache/` written by genome_art_cache.py. Run that first.

    ~/.venvs/rimart/bin/python src/RimMandrake/Utils/genome_art_cache.py
    ~/.venvs/rimart/bin/python src/RimMandrake/Utils/genome_matrix_build.py

Needs Pillow (icons are downscaled to 28px before inlining -- at full 128px the
page is ~40 MB and unopenable).
"""

from __future__ import annotations

import argparse
import base64
import html
import io
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from game_paths import LOCALLOW  # noqa: E402
from genome_scan import (  # noqa: E402
    active_package_ids,
    build_texture_index,
    discover_mod_dirs,
)

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow is required. Run with ~/.venvs/rimart/bin/python.")

DUMP = Path(LOCALLOW) / "DefDump" / "defs"
ICON_PX = 28

# ---------------------------------------------------------------- row selection

# The packs whose xenotypes are candidates for this campaign. Everything else
# installed (Big and Small's Norse giants, Alpha Genes' elementals, Yautja) is a
# different game's setting and is listed as excluded rather than silently
# dropped -- see the footer the renderer writes.
CANDIDATE_PACKS = {
    "btd.xenotyperemix.starwars": ("BTD REMIX", "btd"),
    "guy762.starwarsxenotypes": ("SW Xenotypes", "guy"),
    "neronix17.outerrim.galacticdiversity": ("Outer Rim GD", "orim"),
    "ludeon.rimworld.biotech": ("Biotech", "vanilla"),
    "ludeon.rimworld.odyssey": ("Odyssey", "vanilla"),
    "jawa.patches": ("Jawa Patches (ours)", "ours"),
}

PACK_PREFIX = re.compile(
    r"^(btd_|guy762_xenotype_|guy762_debugxenotype_|outerrim_|jawa_xeno_|lee_xenotype_)",
    re.I,
)

# Same species, different spelling. Left side is the post-prefix defName tail,
# lowercased with non-letters stripped.
SPECIES_SYNONYM = {
    "moncal": "moncalamari",
    "nemoidian": "neimoidian",
    "zabrak": "iridonian",          # Iridonia is the Zabrak homeworld; one species
    "zabrakdathomiri": "dathomirian",
    "geonosiandrone": "geonosian",
    "sithk": "sith",
    "sithm": "sith",
    "sithz": "sith",
    "chadrafan": "chadrafan",
}

# Species the faction roster actually fields. Anything else in the candidate
# packs is a shopping-list entry, not a commitment.
# Source: design/Jawa/worldbuilding/faction_roster_v2.md and review/species_register.html
ROSTER_SPECIES = {
    "jawa", "hutt", "tusken", "wookiee", "geonosian", "moncalamari", "quarren",
    "arkanian", "kaminoan", "gamorrean", "twilek", "rodian", "trandoshan",
    "weequay", "nikto", "devaronian", "bothan", "chiss", "umbaran", "kaleesh",
    "zabrak", "iridonian", "sith", "duros", "sullustan", "ithorian", "aqualish",
    "togruta", "mirialan", "pantoran", "zeltron", "ugnaught",
}


def species_of(def_name: str) -> str:
    tail = PACK_PREFIX.sub("", def_name)
    key = re.sub(r"[^a-z]", "", tail.lower())
    return SPECIES_SYNONYM.get(key, key)


def pretty_species(key: str) -> str:
    special = {
        "moncalamari": "Mon Calamari", "chadrafan": "Chadra-Fan",
        "keldor": "Kel Dor", "twilek": "Twi'lek", "forcegremlin": "Force Gremlin",
        "iridonian": "Zabrak / Iridonian",
    }
    return special.get(key, key.capitalize())


# ------------------------------------------------------------------ data layer


def load_dump(name: str) -> list[dict]:
    p = DUMP / f"{name}.json"
    if not p.is_file():
        sys.exit(f"def dump missing: {p}\nRun a dump from the live game first "
                 f"(src/RimMandrake/RimDefDump/README).")
    return json.loads(p.read_text(encoding="utf-8"))["defs"]


def log(m: str) -> None:
    print(m, file=sys.stderr, flush=True)


# ------------------------------------------------------------------------ art


def resolve_icons(paths: set[str], cache_dir: Path) -> dict[str, str]:
    """iconPath -> absolute PNG. Loose files win over bundle extracts, as in game."""
    active = active_package_ids()
    mod_dirs = discover_mod_dirs()
    loose = build_texture_index(mod_dirs, active)
    cache: dict[str, str] = {}
    if cache_dir.is_dir():
        for f in cache_dir.iterdir():
            if f.suffix.lower() == ".png":
                cache[f.stem.replace("%", "/").lower()] = str(f)
    log(f"art: {len(loose)} loose PNGs indexed, {len(cache)} from bundles")

    out: dict[str, str] = {}
    for ip in paths:
        key = ip.lower().replace("\\", "/")
        hit = loose.get(key) or cache.get(key)
        if hit:
            out[ip] = hit
    return out


_data_uri_cache: dict[str, str] = {}


def data_uri(png_path: str, px: int = ICON_PX) -> str | None:
    if png_path in _data_uri_cache:
        return _data_uri_cache[png_path]
    try:
        with Image.open(png_path) as im:
            im = im.convert("RGBA")
            im.thumbnail((px, px), Image.LANCZOS)
            buf = io.BytesIO()
            im.save(buf, format="PNG", optimize=True)
        uri = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
    except Exception:
        return None
    _data_uri_cache[png_path] = uri
    return uri


# -------------------------------------------------------------------- rendering

CSS = """
:root{--bg:#f6f4ef;--fg:#1c1a17;--dim:#6b6559;--rule:#ddd7ca;--card:#fff;
--star:#a8741a;--cand:#7d8a99;--ours:#2f8f4e;--warn:#c0392b;--band:#efece4;}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
--bg:#16150f;--fg:#e9e5da;--dim:#9d9689;--rule:#332f26;--card:#1e1c15;
--star:#d9a441;--cand:#8fa0b2;--ours:#4ec27a;--warn:#e2725b;--band:#221f18;}}
:root[data-theme="dark"]{--bg:#16150f;--fg:#e9e5da;--dim:#9d9689;--rule:#332f26;
--card:#1e1c15;--star:#d9a441;--cand:#8fa0b2;--ours:#4ec27a;--warn:#e2725b;--band:#221f18;}
*{box-sizing:border-box}
body{margin:0;padding:2rem 1.5rem 5rem;background:var(--bg);color:var(--fg);
font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;}
h1{font-size:1.9rem;margin:0 0 .4rem;letter-spacing:-.02em}
h2{font-size:1.15rem;margin:2.6rem 0 .5rem;padding-bottom:.3rem;
border-bottom:2px solid var(--rule)}
.lede{max-width:64ch;color:var(--dim);margin:0 0 1.4rem}
.callout{max-width:78ch;border-left:4px solid var(--warn);background:var(--card);
padding:.8rem 1rem;margin:1.2rem 0 1.8rem;border-radius:0 4px 4px 0}
.callout b{color:var(--warn)}
code,.mono{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.82em}
.chip{display:inline-block;padding:.05rem .45rem;border:1px solid var(--rule);
border-radius:999px;font-size:.72rem;color:var(--dim);vertical-align:middle}
.legend{display:flex;flex-wrap:wrap;gap:1.2rem;margin:.6rem 0 1.6rem;font-size:.85rem;
color:var(--dim)}
.scroll{overflow:auto;max-height:88vh;border:1px solid var(--rule);border-radius:6px;
background:var(--card)}
table{border-collapse:separate;border-spacing:0;font-size:.8rem}
th,td{padding:0;margin:0}
thead th{position:sticky;top:0;z-index:3;background:var(--card);
border-bottom:2px solid var(--rule);vertical-align:bottom;height:11.5rem}
thead th.corner{left:0;z-index:5;border-right:2px solid var(--rule)}
th.rot>div{width:1.55rem;transform:rotate(180deg);writing-mode:vertical-rl;
padding:.35rem .15rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
max-height:9.4rem;color:var(--dim);font-weight:500;font-size:.72rem}
th.rot img{display:block;margin:.25rem auto .1rem;width:18px;height:18px}
tbody th{position:sticky;left:0;z-index:2;background:var(--card);text-align:left;
padding:.2rem .6rem .2rem .5rem;white-space:nowrap;border-right:2px solid var(--rule);
font-weight:500}
tbody th img{width:20px;height:20px;vertical-align:-4px;margin-right:.35rem}
tr.band th,tr.band td{background:var(--band);color:var(--dim);font-size:.75rem;
text-transform:uppercase;letter-spacing:.08em;padding:.3rem .5rem;font-weight:600}
tbody td{text-align:center;border-bottom:1px solid var(--rule);width:1.55rem}
tbody tr:hover td{background:rgba(127,127,127,.10)}
td.on img{width:17px;height:17px;display:block;margin:1px auto}
td.on.noart::after{content:"\\25CF";color:var(--fg);font-size:.7rem}
.sp{font-size:.7rem;color:var(--dim);letter-spacing:.06em;text-transform:uppercase}
.tag{font-size:.68rem;padding:0 .3rem;border-radius:3px;margin-left:.3rem}
.tag.btd{background:#7b5ea733;color:var(--fg)}
.tag.guy{background:#3f7fa733;color:var(--fg)}
.tag.orim{background:#a7743f33;color:var(--fg)}
.tag.vanilla{background:#7f7f7f33;color:var(--fg)}
.tag.ours{background:#2f8f4e33;color:var(--fg)}
.star{color:var(--star)}
.only{font-size:.72rem;color:var(--dim);max-width:70ch}
.sbs{margin:0 0 2.2rem;border:1px solid var(--rule);border-radius:6px;
background:var(--card);overflow:hidden}
.sbs>h3{margin:0;padding:.55rem .8rem;font-size:1rem;border-bottom:1px solid var(--rule);
display:flex;align-items:center;gap:.5rem;flex-wrap:wrap}
.sbs>h3 img{width:22px;height:22px}
.sbs .verdict{font-size:.8rem;color:var(--dim);font-weight:400;margin-left:auto}
.sbs .inner{overflow-x:auto}
.sbs table{font-size:.78rem;min-width:100%}
.sbs thead th{height:8.5rem;background:var(--card)}
.sbs th.rot>div{max-height:6.6rem}
.sbs tbody th{min-width:15rem}
.agree{color:var(--ours)}
.disagree{color:var(--warn)}
.chips{display:flex;flex-wrap:wrap;gap:.3rem;padding:.5rem .8rem}
.g{display:inline-flex;align-items:center;gap:.25rem;border:1px solid var(--rule);
border-radius:4px;padding:.05rem .35rem .05rem .2rem;font-size:.75rem;background:var(--bg)}
.g img{width:16px;height:16px}
.solo{border:1px solid var(--rule);border-radius:6px;background:var(--card);
margin:0 0 .9rem}
.solo>h3{margin:0;padding:.45rem .8rem;font-size:.92rem;font-weight:600;
border-bottom:1px solid var(--rule);display:flex;align-items:center;gap:.45rem}
.solo>h3 img{width:20px;height:20px}
footer{margin-top:3rem;padding-top:1rem;border-top:1px solid var(--rule);
color:var(--dim);font-size:.85rem;max-width:78ch}
"""


def esc(s: str | None) -> str:
    return html.escape(s or "", quote=True)


def build(args) -> int:
    xenos = load_dump("XenotypeDef")
    genes_raw = load_dump("GeneDef")
    gene_by_name = {g["defName"]: g for g in genes_raw}
    log(f"dump: {len(xenos)} xenotypes, {len(genes_raw)} genes")

    rows = [x for x in xenos if x.get("packageId", "").lower() in CANDIDATE_PACKS]
    excluded = Counter(x.get("modName", "?") for x in xenos
                       if x.get("packageId", "").lower() not in CANDIDATE_PACKS)
    log(f"rows: {len(rows)} selected, {sum(excluded.values())} excluded")

    # Gene frequency across the selected rows only.
    freq = Counter()
    for x in rows:
        for g in x["fields"].get("genes") or []:
            freq[g] += 1

    shared = {g for g, n in freq.items() if n >= args.min_shared}
    singles = {g for g in freq if g not in shared}
    log(f"gene columns: {len(shared)} shared (>={args.min_shared} rows), "
        f"{len(singles)} unique-to-one moved to the overflow column")

    # Columns banded by the game's own displayCategory, then by how many rows
    # carry them -- the widely-shared genes read first inside each band.
    def cat_of(g: str) -> str:
        rec = gene_by_name.get(g) or {}
        return (rec.get("fields") or {}).get("displayCategory") or "Uncategorised"

    bands: dict[str, list[str]] = defaultdict(list)
    for g in shared:
        bands[cat_of(g)].append(g)
    for b in bands:
        bands[b].sort(key=lambda g: (-freq[g], (gene_by_name.get(g) or {}).get("label") or g))
    band_order = sorted(bands, key=lambda b: (-len(bands[b]), b))
    columns = [g for b in band_order for g in bands[b]]

    # Art
    want_paths = set()
    for g in columns:
        ip = (gene_by_name.get(g) or {}).get("fields", {}).get("iconPath")
        if ip:
            want_paths.add(ip)
    for x in rows:
        ip = x["fields"].get("iconPath")
        if ip:
            want_paths.add(ip)
    icons = resolve_icons(want_paths, Path(args.art_cache))
    log(f"art: resolved {len(icons)} of {len(want_paths)} icon paths")

    # Rows grouped by species, each species' implementations adjacent.
    by_species: dict[str, list[dict]] = defaultdict(list)
    for x in rows:
        by_species[species_of(x["defName"])].append(x)
    for s in by_species:
        by_species[s].sort(key=lambda x: x["defName"])

    # Contested species first: those are the rows that carry a decision.
    species_order = sorted(
        by_species,
        key=lambda s: (-len(by_species[s]), 0 if s in ROSTER_SPECIES else 1, s),
    )

    out: list[str] = []
    w = out.append
    w("<!-- generated by src/RimMandrake/Utils/genome_matrix_build.py -->")
    w(f"<title>Genome Register</title><style>{CSS}</style>")
    w("<h1>Genome Register</h1>")
    w(f'<p class="lede">Every candidate xenotype in the live load order, aligned '
      f'by gene. {len(rows)} xenotypes across {len(CANDIDATE_PACKS)} packs, '
      f'{len(columns)} gene columns, read from the def dump captured '
      f'{esc(dump_stamp())} &mdash; post-patch, so this is what the game actually '
      f'built, not what the XML ships. Icons are the game\'s own, '
      f'{len(icons)} of {len(want_paths)} recovered '
      f'(vanilla and Outer Rim art lives inside Unity AssetBundles).</p>')

    contested = [s for s in species_order if len(by_species[s]) > 1]
    w('<div class="callout"><b>The decision this document exists for:</b> '
      f'{len(contested)} species are implemented by more than one pack at the same '
      'time. BTD REMIX, SW Xenotypes and Outer Rim GD are all active, and all three '
      'define a Twi’lek, a Wookiee, a Jawa. The game will happily generate all '
      'of them side by side. Pick one pack per species &mdash; or one pack outright '
      '&mdash; and disable the rest. The contested species are listed first below.</div>')

    w('<div class="legend">'
      '<span><span class="star">&#9733;</span> species the faction roster fields</span>'
      '<span>&#9675; candidate, not yet committed</span>'
      '<span><span class="tag btd">BTD</span><span class="tag guy">SWX</span>'
      '<span class="tag orim">ORIM</span><span class="tag vanilla">vanilla</span>'
      '<span class="tag ours">ours</span> source pack</span>'
      '<span>&#9679; gene present, art not recovered</span>'
      '</div>')

    # ---- helpers shared by the species blocks and the full grid
    def glabel(g: str) -> str:
        return (gene_by_name.get(g) or {}).get("label") or g

    def gicon(g: str, px: int) -> str | None:
        ip = (gene_by_name.get(g) or {}).get("fields", {}).get("iconPath")
        return data_uri(icons[ip], px) if ip and ip in icons else None

    def xicon(x: dict, px: int) -> str:
        ip = x["fields"].get("iconPath")
        uri = data_uri(icons[ip], px) if ip and ip in icons else None
        return f'<img src="{uri}" alt="">' if uri else ""

    def cell(g: str, present: bool) -> str:
        if not present:
            return "<td></td>"
        tip = esc(f"{glabel(g)} — {g}")
        uri = gicon(g, 20)
        if uri:
            return f'<td class="on"><img src="{uri}" alt="{esc(glabel(g))}" title="{tip}"></td>'
        return f'<td class="on noart" title="{tip}"></td>'

    # ---- Section 1: the contested species, side by side.
    w("<h2>Contested species &mdash; where the packs disagree</h2>")
    w('<p class="lede">One block per species that more than one active pack '
      'defines. Columns are that species&rsquo; gene union only, ordered by how many '
      'implementations carry them, so the leftmost columns are the agreed core and '
      'everything to the right is a pack making its own call.</p>')

    for s in contested:
        impls = by_species[s]
        union: Counter = Counter()
        for x in impls:
            for g in x["fields"].get("genes") or []:
                union[g] += 1
        cols = sorted(union, key=lambda g: (-union[g], glabel(g)))
        agreed = sum(1 for g in cols if union[g] == len(impls))
        marker = ('<span class="star">&#9733;</span>' if s in ROSTER_SPECIES
                  else "&#9675;")
        w('<div class="sbs">')
        w(f'<h3>{xicon(impls[0], 22)}{marker} {esc(pretty_species(s))}'
          f'<span class="chip">{len(impls)} implementations</span>'
          f'<span class="verdict"><span class="agree">{agreed} genes agreed</span>'
          f' &middot; <span class="disagree">{len(cols) - agreed} contested</span>'
          f' of {len(cols)}</span></h3>')
        w('<div class="inner"><table><thead><tr><th class="corner">&nbsp;</th>')
        for g in cols:
            uri = gicon(g, 18)
            img = f'<img src="{uri}" alt="">' if uri else ""
            cls = "rot"
            tip = f"{glabel(g)} — {g}\ncarried by {union[g]} of {len(impls)}"
            w(f'<th class="{cls}" title="{esc(tip)}">{img}<div>{esc(glabel(g))}</div></th>')
        w("</tr></thead><tbody>")
        for x in impls:
            have = set(x["fields"].get("genes") or [])
            pack_label, pack_cls = CANDIDATE_PACKS[x["packageId"].lower()]
            w("<tr>")
            w(f'<th title="{esc(x["defName"])}">{xicon(x, 20)}'
              f'{esc(x.get("label") or x["defName"])}'
              f'<span class="tag {pack_cls}">{esc(pack_label)}</span>'
              f'<span class="chip">{len(have)} genes</span></th>')
            for g in cols:
                w(cell(g, g in have))
            w("</tr>")
        w("</tbody></table></div></div>")

    # ---- Section 2: the full grid.
    w("<h2>The full grid &mdash; every candidate, every shared gene</h2>")
    w(f'<p class="lede">All {len(rows)} rows against all {len(columns)} gene '
      f'columns. Wide by construction: this is the view for spotting a gene that '
      f'runs across species, not for picking one. Row labels and the header stay '
      f'put as you scroll.</p>')
    w('<div class="scroll"><table><thead><tr>')
    w('<th class="corner">&nbsp;</th>')
    for g in columns:
        rec = gene_by_name.get(g) or {}
        label = rec.get("label") or g
        ip = (rec.get("fields") or {}).get("iconPath")
        uri = data_uri(icons[ip]) if ip and ip in icons else None
        img = f'<img src="{uri}" alt="">' if uri else ""
        tip = f'{label} — {g}\ncarried by {freq[g]} of {len(rows)}'
        w(f'<th class="rot" title="{esc(tip)}">{img}<div>{esc(label)}</div></th>')
    w('<th class="rot"><div>unique to this row</div></th>')
    w('</tr></thead><tbody>')

    current_band = None
    for s in species_order:
        impls = by_species[s]
        marker = '<span class="star">&#9733;</span>' if s in ROSTER_SPECIES else "&#9675;"
        note = ""
        if len(impls) > 1:
            note = f' <span class="chip">{len(impls)} packs disagree</span>'
        w(f'<tr class="band"><th colspan="{len(columns) + 2}">{marker} '
          f'{esc(pretty_species(s))}{note}</th></tr>')
        for x in impls:
            f = x["fields"]
            have = set(f.get("genes") or [])
            ip = f.get("iconPath")
            uri = data_uri(icons[ip], 22) if ip and ip in icons else None
            img = f'<img src="{uri}" alt="">' if uri else ""
            pack_label, pack_cls = CANDIDATE_PACKS[x["packageId"].lower()]
            w("<tr>")
            w(f'<th title="{esc(x["defName"])}">{img}{esc(x.get("label") or x["defName"])}'
              f'<span class="tag {pack_cls}">{esc(pack_label)}</span></th>')
            for g in columns:
                if g in have:
                    rec = gene_by_name.get(g) or {}
                    gip = (rec.get("fields") or {}).get("iconPath")
                    guri = data_uri(icons[gip], 20) if gip and gip in icons else None
                    if guri:
                        w(f'<td class="on"><img src="{guri}" alt="'
                          f'{esc(rec.get("label") or g)}" title="'
                          f'{esc((rec.get("label") or g) + " — " + g)}"></td>')
                    else:
                        w(f'<td class="on noart" title="'
                          f'{esc((rec.get("label") or g) + " — " + g)}"></td>')
                else:
                    w("<td></td>")
            uniq = sorted(have & singles)
            names = ", ".join((gene_by_name.get(u) or {}).get("label") or u for u in uniq)
            w(f'<td class="only" title="{esc(names)}">{len(uniq)}</td>')
            w("</tr>")
    w("</tbody></table></div>")

    # ---- Section 3: the species only one pack defines.
    uncontested = [s for s in species_order if len(by_species[s]) == 1]
    w("<h2>Uncontested &mdash; one pack, no decision to make</h2>")
    w(f'<p class="lede">{len(uncontested)} species come from exactly one active '
      f'pack, so there is nothing to choose. Listed with their full gene set for '
      f'reference; a gene the game generated from a template rather than shipping '
      f'as a file is included the same as any other.</p>')
    for s in uncontested:
        x = by_species[s][0]
        have = sorted(x["fields"].get("genes") or [], key=glabel)
        pack_label, pack_cls = CANDIDATE_PACKS[x["packageId"].lower()]
        marker = ('<span class="star">&#9733;</span>' if s in ROSTER_SPECIES
                  else "&#9675;")
        w('<div class="solo">')
        w(f'<h3>{xicon(x, 20)}{marker} {esc(pretty_species(s))}'
          f'<span class="tag {pack_cls}">{esc(pack_label)}</span>'
          f'<span class="chip">{len(have)} genes</span></h3>')
        w('<div class="chips">')
        for g in have:
            uri = gicon(g, 16)
            img = f'<img src="{uri}" alt="">' if uri else ""
            w(f'<span class="g" title="{esc(g)}">{img}{esc(glabel(g))}</span>')
        w("</div></div>")

    w("<h2>What was left out, and why</h2>")
    w("<p class=\"lede\">These xenotypes are installed and loading, but belong to a "
      "different setting. They are excluded from the grid, not from the game.</p><ul>")
    for mod, n in excluded.most_common():
        w(f"<li>{esc(mod)} &mdash; {n}</li>")
    w("</ul>")

    w(f'<footer>Generated by <code>src/RimMandrake/Utils/genome_matrix_build.py</code> '
      f'from the def dump at <code>&lt;LocalLow&gt;/DefDump/</code>. '
      f'A gene column appears when at least {args.min_shared} of the selected '
      f'xenotypes carry it; genes carried by exactly one are counted in the final '
      f'column instead of widening the grid by {len(singles)} columns. '
      f'Recommendations, not decisions &mdash; the pack choice is the owner’s.'
      f'</footer>')

    dest = Path(args.out)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text("\n".join(out), encoding="utf-8")
    log(f"wrote {dest} ({dest.stat().st_size / 1e6:.1f} MB)")
    return 0


def dump_stamp() -> str:
    man = Path(LOCALLOW) / "DefDump" / "manifest.json"
    try:
        m = json.loads(man.read_text(encoding="utf-8"))
        return f'{m.get("capturedUtc", "?")} (game {m.get("gameVersion", "?")})'
    except Exception:
        return "unknown"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="design/Jawa/worldbuilding/review/genome_register.html")
    ap.add_argument("--art-cache", default="observed/genome/art_cache")
    ap.add_argument("--min-shared", type=int, default=2,
                    help="a gene needs this many carriers to earn a column")
    return build(ap.parse_args())


if __name__ == "__main__":
    sys.exit(main())
