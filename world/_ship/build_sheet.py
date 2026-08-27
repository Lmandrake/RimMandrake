#!/usr/bin/env python3
"""Build the deck-floor review page. Images are embedded, so the page is self-contained."""
import base64, json, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(ROOT, "web")
MAN = json.load(open(os.path.join(ROOT, "designs", "manifest.json")))

def uri(name):
    with open(os.path.join(WEB, name), "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()

PAL = [
    ("CONNECT", "AG_RustedTile", "rusted biotech lab tile", "CONNECTIVE",
     "Runs everywhere. The tissue that ties the ship into one place.", "#3f4340"),
    ("PLATE", "guy762_FloorTiles_DoomgiverFoorMetal_dark", "metal plating (iron)", "HEAVY INDUSTRY",
     "Under and around machinery. Where the work happened.", "#39352f"),
    ("GRATE_I", "guy762_FloorTiles_XGrate_iron", "crossed grate (iron)", "TRIM",
     "Edges a bay. Quiet delineation you notice second.", "#231d16"),
    ("GRATE_Y", "guy762_FloorTiles_XGrate_yellow", "crossed grate (worn yellow)", "TRIM · WARNING",
     "Entrances, pad lips, messy ground. The one loud colour.", "#382f1d"),
    ("SCAFF", "UCScaffoldTile", "scaffold tile", "ENGINE ROOM",
     "The core, and only the core. Kept as-is.", "#7e7669"),
    ("HULL", "VQE_AncientHullTile", "ancient hull tile", "SUBSTRATE",
     "The oldest surface. What everything else was laid over.", "#47474b"),
    ("DIVOT", "guy762_FloorTiles_DivotedTile_rust", "divoted tile (rust)", "RESERVED",
     "Held back. Used in one scheme only, for one axis.", "#59473c"),
    ("MECH", "GR_RustedMechTile", "rusted mech lab tile", "UNUSED",
     "On the bench — too pink beside the oxide palette.", "#6b615b"),
]

READS = {
    "service_rings": "Somebody maintained this, bay by bay, for centuries.",
    "hazard_lanes": "This was a plant with a shift pattern and marked routes.",
    "cargo_decks": "This was a hauler, and the spine was the part that mattered.",
    "stratified_hull": "The rust is a later layer. Something under it outlasted the crew.",
}
COST = {
    "service_rings": "Lowest risk. The bays fall out of the machine footprints, so it survives you moving a machine later.",
    "hazard_lanes": "Same bays plus 453 lane cells. The lanes are hand-placed, so they break if the legs are re-cut.",
    "cargo_decks": "Biggest single block of plate — 1,948 cells. Cheapest to paint, least information per cell.",
    "stratified_hull": "1,031 hull cells scattered by a hash. Deterministic, so it reproduces exactly, but it wants a look before it lands.",
}
DETAIL_LABEL = {"engine": "Engine core", "north": "North machine deck", "leg": "Leg and landing pad"}

COLOR_OF = {k: c for k, _, _, _, _, c in PAL}
LABEL_OF = {d: l for _, d, l, _, _, _ in PAL}
KEY_OF = {d: k for k, d, _, _, _, _ in PAL}

TINTS = [("SCAFF_none", "no tint", "126 118 103", ""),
         ("SCAFF_grayLight", "Structure_GrayLight", "120 120 120", "neutral, same lightness"),
         ("SCAFF_marble", "Structure_Marble", "95 97 95", "neutral, a shade under"),
         ("SCAFF_granite", "Structure_Granite", "73 66 68", "the match"),
         ("HULL_ref", "ancient hull tile", "71 71 71", "the target")]

def bar(design):
    total = sum(design["cells"].values())
    segs = []
    for dn, n in sorted(design["cells"].items(), key=lambda kv: -kv[1]):
        pct = 100.0 * n / total
        segs.append('<span class="seg" style="width:%.3f%%;background:%s" '
                    'title="%s — %d cells"></span>' % (pct, COLOR_OF[KEY_OF[dn]], LABEL_OF[dn], n))
    keys = []
    for dn, n in sorted(design["cells"].items(), key=lambda kv: -kv[1]):
        keys.append('<li><i style="background:%s"></i><span>%s</span><b>%d</b></li>'
                    % (COLOR_OF[KEY_OF[dn]], LABEL_OF[dn], n))
    return '<div class="bar">%s</div><ul class="barkey">%s</ul>' % ("".join(segs), "".join(keys))

secs = []
for i, d in enumerate(MAN["designs"]):
    dets = "".join(
        '<figure><img src="%s" alt="%s, %s" loading="lazy"><figcaption>%s</figcaption></figure>'
        % (uri(x["file"]), d["title"], x["name"], DETAIL_LABEL[x["file"].rsplit("_", 1)[-1][:-4]])
        for x in d["details"])
    secs.append("""
<section class="scheme" id="{slug}">
  <div class="plan"><img src="{full}" alt="{title} — full deck plan"></div>
  <div class="notes">
    <p class="eyebrow">Scheme {n} of 4</p>
    <h2>{title}</h2>
    <p class="thesis">{blurb}</p>
    <p class="reads"><span>Reads as</span>{reads}</p>
    {bar}
    <div class="details">{dets}</div>
    <p class="cost"><span>Cost to lay</span>{cost}</p>
  </div>
</section>""".format(slug=d["slug"], full=uri(d["file"]), title=d["title"], n=i + 1,
                     blurb=d["blurb"], reads=READS[d["slug"]], bar=bar(d),
                     dets=dets, cost=COST[d["slug"]]))

palette_html = "".join(
    '<li><img src="%s" alt="%s"><div><p class="role">%s</p><h3>%s</h3>'
    '<code>%s</code><p>%s</p></div></li>' % (uri("pal_%s.png" % k), label, role, label, dn, note)
    for k, dn, label, role, note, _ in PAL)

tint_html = "".join(
    '<li><img src="%s" alt="%s"><p class="tn">%s</p><p class="tv">%s</p><p class="tc">%s</p></li>'
    % (uri("tint_%s.png" % k), name, name, rgb, note) for k, name, rgb, note in TINTS)

HTML = """<title>Helpful Transport Decks</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=IBM+Plex+Mono:wght@400;500&family=Source+Serif+4:ital,opsz,wght@0,8..60,300;0,8..60,400;0,8..60,600;1,8..60,400&display=swap">
<style>
:root{
  --ground:#e6e7e3; --surface:#f2f3ef; --sunk:#dcded8;
  --ink:#161a18; --muted:#5b6360; --faint:#8a918d;
  --line:#c7cac3; --line2:#d8dbd4;
  --accent:#836612; --accent-soft:#b9a14a;
}
:root:not([data-theme="light"]){ }
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --ground:#111412; --surface:#191d1a; --sunk:#0c0f0d;
    --ink:#e3e6e1; --muted:#9aa29b; --faint:#6f776f;
    --line:#2b322d; --line2:#232924;
    --accent:#cba32c; --accent-soft:#8a7526;
  }
}
:root[data-theme="dark"]{
  --ground:#111412; --surface:#191d1a; --sunk:#0c0f0d;
  --ink:#e3e6e1; --muted:#9aa29b; --faint:#6f776f;
  --line:#2b322d; --line2:#232924;
  --accent:#cba32c; --accent-soft:#8a7526;
}
*{box-sizing:border-box}
body{
  margin:0; background:var(--ground); color:var(--ink);
  font-family:"Source Serif 4",Georgia,serif; font-size:17px; line-height:1.62;
  -webkit-font-smoothing:antialiased;
}
.wrap{max-width:1180px;margin:0 auto;padding:0 28px 96px}
h1,h2,h3,.eyebrow,.role,th{font-family:"Barlow Condensed","Arial Narrow",sans-serif}
code,.mono,b,.tv{font-family:"IBM Plex Mono",ui-monospace,monospace}
a{color:var(--accent)}

header.top{padding:64px 0 34px;border-bottom:2px solid var(--ink)}
.kicker{font-family:"IBM Plex Mono",monospace;font-size:11.5px;letter-spacing:.20em;
  text-transform:uppercase;color:var(--accent);margin:0 0 18px}
h1{font-size:clamp(44px,7.4vw,86px);line-height:.92;letter-spacing:.012em;margin:0;
  text-transform:uppercase;font-weight:700;text-wrap:balance}
h1 em{font-style:normal;color:var(--muted);display:block;font-weight:500}
.standfirst{max-width:63ch;margin:22px 0 0;font-size:19px;color:var(--muted)}
.facts{display:flex;flex-wrap:wrap;gap:0;margin:30px 0 0;border-top:1px solid var(--line)}
.facts div{padding:14px 26px 12px 0;margin-right:26px;border-right:1px solid var(--line);}
.facts div:last-child{border-right:0}
.facts dt{font-family:"IBM Plex Mono",monospace;font-size:10.5px;letter-spacing:.16em;
  text-transform:uppercase;color:var(--faint);margin:0}
.facts dd{margin:2px 0 0;font-family:"Barlow Condensed",sans-serif;font-size:27px;font-weight:600;
  font-variant-numeric:tabular-nums}

h2{font-size:clamp(30px,3.4vw,44px);line-height:1;margin:6px 0 14px;text-transform:uppercase;
  letter-spacing:.01em;font-weight:700;text-wrap:balance}
.eyebrow{font-size:12px;letter-spacing:.22em;text-transform:uppercase;color:var(--accent);
  margin:0;font-weight:600}
.rule{margin:74px 0 26px;border-top:1px solid var(--line);padding-top:10px;
  display:flex;justify-content:space-between;align-items:baseline;gap:20px}
.rule h2{font-size:clamp(24px,2.6vw,32px);margin:0}
.rule p{margin:0;color:var(--faint);font-size:14px;max-width:46ch;text-align:right}

ul.palette{list-style:none;padding:0;margin:0;display:grid;gap:1px;background:var(--line2);
  grid-template-columns:repeat(auto-fill,minmax(330px,1fr));border:1px solid var(--line2)}
ul.palette li{background:var(--surface);display:flex;gap:16px;padding:16px}
ul.palette img{width:80px;height:80px;flex:none;image-rendering:pixelated;
  border:1px solid var(--line)}
ul.palette h3{margin:1px 0 3px;font-size:20px;font-weight:600;line-height:1.05}
ul.palette code{display:block;font-size:11px;color:var(--faint);word-break:break-all;margin-bottom:6px}
ul.palette p{margin:0;font-size:14.5px;line-height:1.45;color:var(--muted)}
.role{margin:0;font-size:10.5px;letter-spacing:.18em;text-transform:uppercase;color:var(--accent);
  font-weight:600}

.scheme{display:grid;grid-template-columns:minmax(300px,42%) 1fr;gap:40px;
  padding:34px 0 0;border-top:1px solid var(--line);margin-top:34px}
.scheme:first-of-type{border-top:0}
.plan img{width:100%;display:block;border:1px solid var(--line);background:var(--sunk)}
.notes{min-width:0}
.thesis{margin:0 0 16px;font-size:17.5px;max-width:60ch}
.reads,.cost{display:flex;gap:14px;align-items:baseline;margin:0 0 20px;
  border-left:3px solid var(--accent);padding-left:14px}
.reads span,.cost span{font-family:"IBM Plex Mono",monospace;font-size:10.5px;letter-spacing:.14em;
  text-transform:uppercase;color:var(--faint);flex:none;width:88px;padding-top:4px}
.reads{font-style:italic;font-size:18px}
.cost{border-left-color:var(--line);font-size:14.5px;color:var(--muted);margin-bottom:0}

.bar{display:flex;height:15px;width:100%;overflow:hidden;border:1px solid var(--line);
  margin:0 0 10px}
.bar .seg{display:block;height:100%}
ul.barkey{list-style:none;display:flex;flex-wrap:wrap;gap:6px 20px;padding:0;margin:0 0 24px}
ul.barkey li{display:flex;align-items:center;gap:7px;font-size:12.5px;color:var(--muted)}
ul.barkey i{width:11px;height:11px;display:block;border:1px solid var(--line)}
ul.barkey b{font-size:12px;font-variant-numeric:tabular-nums;color:var(--ink);font-weight:500}

.details{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:0 0 22px}
.details figure{margin:0}
.details img{width:100%;display:block;border:1px solid var(--line);background:var(--sunk)}
.details figcaption{font-family:"IBM Plex Mono",monospace;font-size:10.5px;letter-spacing:.06em;
  color:var(--faint);margin-top:6px}

ul.tints{list-style:none;padding:0;margin:0;display:grid;gap:14px;
  grid-template-columns:repeat(auto-fit,minmax(150px,1fr))}
ul.tints img{width:100%;display:block;image-rendering:pixelated;border:1px solid var(--line)}
.tn{margin:8px 0 0;font-family:"IBM Plex Mono",monospace;font-size:12px;word-break:break-all}
.tv{margin:2px 0 0;font-size:11.5px;color:var(--faint);font-variant-numeric:tabular-nums}
.tc{margin:2px 0 0;font-size:12.5px;color:var(--accent);font-family:"Barlow Condensed",sans-serif;
  text-transform:uppercase;letter-spacing:.08em}

.verdict{background:var(--surface);border:1px solid var(--line);padding:24px 26px;margin:26px 0 0}
.verdict p{margin:0;max-width:70ch}
.verdict p+p{margin-top:12px}
.pick{margin-top:22px;display:grid;gap:1px;background:var(--line2);border:1px solid var(--line2);
  grid-template-columns:repeat(auto-fit,minmax(250px,1fr))}
.pick div{background:var(--surface);padding:18px 20px}
.pick h3{margin:0 0 6px;font-size:19px;text-transform:uppercase;letter-spacing:.02em}
.pick p{margin:0;font-size:14.5px;color:var(--muted)}
footer{margin-top:70px;padding-top:16px;border-top:1px solid var(--line);color:var(--faint);
  font-size:13px;font-family:"IBM Plex Mono",monospace}
footer p{margin:0 0 4px}
@media (max-width:860px){
  .scheme{grid-template-columns:1fr}
  .rule{flex-direction:column;gap:6px}
  .rule p{text-align:left}
}
</style>

<div class="wrap">
<header class="top">
  <p class="kicker">Floor plan review &nbsp;·&nbsp; The Helpful Transport &nbsp;·&nbsp; 2026-08-27</p>
  <h1>Helpful Transport<em>Deck floors</em></h1>
  <p class="standfirst">Four ways to lay the same 4,034 cells. Every tile below is a real
  TerrainDef painted in the live game and photographed &mdash; the colour, the tiling and the
  shading are the game&rsquo;s, not a mock-up. Pick one and it goes down on the ship.</p>
  <dl class="facts">
    <div><dt>Deck cells</dt><dd>4,034</dd></div>
    <div><dt>Hull</dt><dd>86 &times; 133</dd></div>
    <div><dt>Doors</dt><dd>3</dd></div>
    <div><dt>Heavy machines</dt><dd>29</dd></div>
    <div><dt>Age to read</dt><dd>~1,000 yr</dd></div>
  </dl>
</header>

<div class="rule"><h2>The palette</h2>
  <p>Roles are yours, from the brief. One tile is on the bench and one is held in reserve.</p></div>
<ul class="palette">PALETTE</ul>

<div class="rule"><h2>Four schemes</h2>
  <p>Same palette, same rules, different story about what this ship used to be.</p></div>
SCHEMES

<div class="rule"><h2>Can the greys be pushed to ancient hull?</h2>
  <p>Yes. RimWorld&rsquo;s 1.6 colour grid tints any floor &mdash; and it multiplies, so it can only darken.</p></div>
<ul class="tints">TINTS</ul>
<div class="verdict">
  <p><strong>Structure_Granite lands it.</strong> Scaffold tile reads <span class="mono">126 118 103</span>
  raw &mdash; warm, sandy, the lightest thing on the ship. Tinted Granite it reads
  <span class="mono">73 66 68</span> against ancient hull&rsquo;s <span class="mono">71 71 71</span>.
  Same lightness, a hair warmer. Structure_Marble is the softer version if the engine room should
  still be the brightest room aboard.</p>
  <p>The catch is worth knowing before you rely on it: the tint is a <em>multiply</em>, so every
  ColorDef darkens and none can lighten. A floor can always be pushed toward oxide and toward hull.
  Nothing can be pushed back up. Choose the lightest tile you might want, then tint down.</p>
</div>

<div class="rule"><h2>How to pick</h2>
  <p>Three questions decide it. The rest is paint.</p></div>
<div class="pick">
  <div><h3>Islands or blocks?</h3><p>Service Rings and Hazard Lanes read the ship as bays in a
  field of rust. Cargo Decks reads it as two big zones with a spine. Islands carry more information;
  blocks carry more weight.</p></div>
  <div><h3>How loud is the yellow?</h3><p>Service Rings keeps it to 122 cells &mdash; lips and
  thresholds only. Hazard Lanes spends 453 on marked routes. Yellow is the only thing on this ship
  a player will follow with their eyes.</p></div>
  <div><h3>Is the ship old, or is it older than itself?</h3><p>Three schemes say a thousand years of
  maintenance. Stratified Hull says the rust is a recent layer over something that was already
  ancient &mdash; and the legs never got the upgrade.</p></div>
</div>

<footer>
  <p>Renders: gravship_floor_designs.py &mdash; ShipLayoutDefV2 + 4-cell swatches cut from live captures at 30.17 px/cell.</p>
  <p>Machinery is drawn as a translucent slab so the floor under it still reads. Walls are grey; the three doors are gold.</p>
  <p>D:\\Luke\\dev\\Rimworld\\world\\_ship\\designs</p>
</footer>
</div>
"""

out = HTML.replace("PALETTE", palette_html).replace("SCHEMES", "".join(secs)).replace("TINTS", tint_html)
path = os.path.join(ROOT, "deck_floors.html")
open(path, "w").write(out)
print(path, round(os.path.getsize(path) / 1e6, 2), "MB")
