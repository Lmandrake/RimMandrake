#!/usr/bin/env python3
"""Round two: the blistered hull and five colour treatments. Self-contained page."""
import base64, json, os

ROOT = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(ROOT, "web2")
MAN = json.load(open(os.path.join(ROOT, "v2", "manifest.json")))

def uri(n):
    with open(os.path.join(WEB, n), "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()

TILES = [
    ("CONNECT", "AG_RustedTile", "rusted biotech lab tile", "1,272", "Connective. Ring, spine shoulders, everywhere between."),
    ("PLATE", "guy762_FloorTiles_DoomgiverFoorMetal_dark", "metal plating (iron)", "1,780", "Machine bays, the whole lower ship, the pod and the stern."),
    ("GRATE_I", "guy762_FloorTiles_XGrate_iron", "crossed grate (iron)", "546", "Plating GONE. 37 blisters grown from noise, not placed by hand."),
    ("DIVOT", "guy762_FloorTiles_DivotedTile_rust", "divoted tile (rust)", "197", "The spine, and nowhere else. Still the reserved tile."),
    ("SCAFF", "UCScaffoldTile", "scaffold tile", "99", "Engine core only, as agreed."),
    ("GROUND", "\u2014 no floor, no substrate \u2014", "eaten through", "140", "Foundation removed. You see the map through it."),
]

DET = {"pod": "The pod \u2014 eaten out", "stern": "Stern flank \u2014 the new thrusters",
       "north": "North machine deck"}

NOTES = {
 "bare_metal": "Nothing here is spent. Compare everything else against it \u2014 and notice the hull is already dark. The bright thing on this ship is the WALLS, not the deck.",
 "oxide_bloom": "Safest. One rate of corrosion, no story. If the ship should read old-and-uniform rather than old-and-wounded, this is it.",
 "bleed_down": "The only scheme that knows which way the ship flies. Brown deepens toward the stern, where the thrusters now are; the bow stays paler.",
 "corrosion_halo": "The most aggressive read: every blister is a wound with a hot orange lip, and the sound plating stays cold grey. The holes become the subject.",
 "two_tone": "Graphic instead of noisy \u2014 a warm umber ring over a cold undercarriage, hot rust only within two cells of a hole. The one that still reads at map zoom.",
}

secs = []
for i, t in enumerate(MAN["treatments"]):
    dets = "".join('<figure><img src="%s" alt="%s" loading="lazy"><figcaption>%s</figcaption></figure>'
                   % (uri(d["file"]), DET[d["name"]], DET[d["name"]]) for d in t["details"])
    cols = "".join('<li><i style="background:rgb(%d,%d,%d)"></i><code>%s</code><b>%d</b></li>'
                   % (0, 0, 0, k or "no tint", v) for k, v in t["colors"][:6])
    secs.append("""
<section class="scheme">
  <div class="plan"><img src="{full}" alt="{title}"></div>
  <div class="notes">
    <p class="eyebrow">{n}</p>
    <h2>{title}</h2>
    <p class="thesis">{blurb}</p>
    <p class="reads"><span>Verdict</span>{note}</p>
    <div class="details">{dets}</div>
    <p class="colorlist"><span>ColorDefs</span>{cl}</p>
  </div>
</section>""".format(full=uri(t["file"]), title=t["title"], n=("Control" if i == 0 else "Treatment %d" % i),
                     blurb=t["blurb"], note=NOTES[t["slug"]], dets=dets,
                     cl=" &nbsp;".join("<code>%s</code>&#8202;<b>%d</b>" % (k or "none", v)
                                       for k, v in t["colors"][:7])))

tiles_html = "".join(
    '<li><img src="%s" alt="%s"><div><h3>%s</h3><code>%s</code><p><b>%s</b> cells &mdash; %s</p></div></li>'
    % (uri("pal_%s.png" % k), lab, lab, dn, n, note) for k, dn, lab, n, note in TILES)

HTML = """<title>Blistered Transport</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=IBM+Plex+Mono:wght@400;500&family=Source+Serif+4:ital,opsz,wght@0,8..60,300;0,8..60,400;0,8..60,600;1,8..60,400&display=swap">
<style>
:root{--ground:#e6e7e3;--surface:#f2f3ef;--sunk:#dcded8;--ink:#161a18;--muted:#5b6360;
 --faint:#8a918d;--line:#c7cac3;--line2:#d8dbd4;--accent:#8a4f14;--hot:#a8551a}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
 --ground:#12100e;--surface:#1a1815;--sunk:#0c0b09;--ink:#e6e2dc;--muted:#a09890;
 --faint:#756d66;--line:#332d27;--line2:#26211c;--accent:#d0803a;--hot:#e0873a}}
:root[data-theme="dark"]{--ground:#12100e;--surface:#1a1815;--sunk:#0c0b09;--ink:#e6e2dc;
 --muted:#a09890;--faint:#756d66;--line:#332d27;--line2:#26211c;--accent:#d0803a;--hot:#e0873a}
*{box-sizing:border-box}
body{margin:0;background:var(--ground);color:var(--ink);font-family:"Source Serif 4",Georgia,serif;
 font-size:17px;line-height:1.62;-webkit-font-smoothing:antialiased}
.wrap{max-width:1180px;margin:0 auto;padding:0 28px 96px}
h1,h2,h3,.eyebrow{font-family:"Barlow Condensed","Arial Narrow",sans-serif}
code,b,.mono{font-family:"IBM Plex Mono",ui-monospace,monospace}
header.top{padding:62px 0 32px;border-bottom:2px solid var(--ink)}
.kicker{font-family:"IBM Plex Mono",monospace;font-size:11.5px;letter-spacing:.20em;
 text-transform:uppercase;color:var(--accent);margin:0 0 18px}
h1{font-size:clamp(44px,7.4vw,84px);line-height:.92;margin:0;text-transform:uppercase;
 font-weight:700;text-wrap:balance}
h1 em{font-style:normal;color:var(--muted);display:block;font-weight:500}
.standfirst{max-width:64ch;margin:22px 0 0;font-size:19px;color:var(--muted)}
.facts{display:flex;flex-wrap:wrap;margin:28px 0 0;border-top:1px solid var(--line)}
.facts div{padding:14px 26px 12px 0;margin-right:26px;border-right:1px solid var(--line)}
.facts div:last-child{border-right:0}
.facts dt{font-family:"IBM Plex Mono",monospace;font-size:10.5px;letter-spacing:.16em;
 text-transform:uppercase;color:var(--faint);margin:0}
.facts dd{margin:2px 0 0;font-family:"Barlow Condensed",sans-serif;font-size:27px;font-weight:600;
 font-variant-numeric:tabular-nums}
h2{font-size:clamp(28px,3.2vw,42px);line-height:1;margin:6px 0 14px;text-transform:uppercase;
 font-weight:700;text-wrap:balance}
.eyebrow{font-size:12px;letter-spacing:.22em;text-transform:uppercase;color:var(--accent);
 margin:0;font-weight:600}
.rule{margin:72px 0 24px;border-top:1px solid var(--line);padding-top:10px;display:flex;
 justify-content:space-between;align-items:baseline;gap:20px}
.rule h2{font-size:clamp(23px,2.5vw,31px);margin:0}
.rule p{margin:0;color:var(--faint);font-size:14px;max-width:48ch;text-align:right}
ul.tiles{list-style:none;padding:0;margin:0;display:grid;gap:1px;background:var(--line2);
 grid-template-columns:repeat(auto-fill,minmax(340px,1fr));border:1px solid var(--line2)}
ul.tiles li{background:var(--surface);display:flex;gap:15px;padding:15px}
ul.tiles img{width:76px;height:76px;flex:none;image-rendering:pixelated;border:1px solid var(--line)}
ul.tiles h3{margin:0 0 3px;font-size:19px;font-weight:600;line-height:1.05}
ul.tiles code{display:block;font-size:11px;color:var(--faint);word-break:break-all;margin-bottom:5px}
ul.tiles p{margin:0;font-size:14px;line-height:1.42;color:var(--muted)}
.scheme{display:grid;grid-template-columns:minmax(290px,40%) 1fr;gap:38px;padding:32px 0 0;
 border-top:1px solid var(--line);margin-top:32px}
.scheme:first-of-type{border-top:0}
.plan img{width:100%;display:block;border:1px solid var(--line);background:var(--sunk)}
.notes{min-width:0}
.thesis{margin:0 0 16px;font-size:17.5px;max-width:60ch}
.reads{display:flex;gap:14px;align-items:baseline;margin:0 0 20px;border-left:3px solid var(--accent);
 padding-left:14px;font-style:italic;font-size:17.5px}
.reads span{font-family:"IBM Plex Mono",monospace;font-size:10.5px;letter-spacing:.14em;
 text-transform:uppercase;color:var(--faint);flex:none;width:72px;padding-top:4px;font-style:normal}
.details{display:grid;grid-template-columns:repeat(3,1fr);gap:11px;margin:0 0 18px}
.details figure{margin:0}
.details img{width:100%;display:block;border:1px solid var(--line);background:var(--sunk)}
.details figcaption{font-family:"IBM Plex Mono",monospace;font-size:10px;color:var(--faint);margin-top:5px}
.colorlist{margin:0;font-size:12px;color:var(--muted);line-height:2}
.colorlist span{font-family:"IBM Plex Mono",monospace;font-size:10.5px;letter-spacing:.14em;
 text-transform:uppercase;color:var(--faint);margin-right:10px}
.colorlist code{font-size:11px}
.colorlist b{color:var(--ink);font-size:11px;font-weight:500}
.finding{display:grid;grid-template-columns:1fr 300px;gap:32px;background:var(--surface);
 border:1px solid var(--line);padding:26px;margin-top:22px;align-items:start}
.finding h3{margin:0 0 8px;font-size:23px;text-transform:uppercase}
.finding p{margin:0 0 12px;max-width:64ch}
.finding p:last-child{margin-bottom:0}
.finding img{width:100%;display:block;border:1px solid var(--line);image-rendering:pixelated}
.finding figcaption{font-family:"IBM Plex Mono",monospace;font-size:10.5px;color:var(--faint);margin-top:6px}
.two{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1px;
 background:var(--line2);border:1px solid var(--line2);margin-top:22px}
.two div{background:var(--surface);padding:18px 20px}
.two h3{margin:0 0 6px;font-size:19px;text-transform:uppercase}
.two p{margin:0;font-size:14.5px;color:var(--muted)}
.warn{border-left:3px solid var(--hot);padding-left:14px;margin-top:20px}
footer{margin-top:70px;padding-top:16px;border-top:1px solid var(--line);color:var(--faint);
 font-size:13px;font-family:"IBM Plex Mono",monospace}
footer p{margin:0 0 4px}
@media (max-width:860px){.scheme,.finding{grid-template-columns:1fr}.rule{flex-direction:column}
 .rule p{text-align:left}}
</style>
<div class="wrap">
<header class="top">
  <p class="kicker">Round two &nbsp;·&nbsp; Cargo Decks, blistered &nbsp;·&nbsp; 2026-08-27</p>
  <h1>Blistered<em>Transport</em></h1>
  <p class="standfirst">Cargo Decks with the grate turned into damage: 37 blisters of missing
  plating grown from a seeded noise field, the eight biggest eaten clean through the substrate.
  Then five ways to colour it. The thrusters have moved to the western flank &mdash; she flies
  right now.</p>
  <dl class="facts">
    <div><dt>Blisters</dt><dd>37</dd></div>
    <div><dt>Plating gone</dt><dd>546</dd></div>
    <div><dt>Eaten through</dt><dd>140</dd></div>
    <div><dt>Biggest blister</dt><dd>118</dd></div>
    <div><dt>Thrusters</dt><dd>x&nbsp;6, west</dd></div>
  </dl>
</header>

<div class="rule"><h2>What is on the deck now</h2>
  <p>Six surfaces, and one of them is not a surface at all.</p></div>
<ul class="tiles">TILES</ul>

<div class="rule"><h2>Two things the game decided for us</h2>
  <p>Both were measured live this session, and both change what a colour scheme can be.</p></div>

<div class="finding">
  <div>
    <h3>The walls carry the theme, not the floor</h3>
    <p>The colour grid is a <strong>multiply</strong>. Rusted biotech tile already renders
    <span class="mono">63&#8202;63&#8202;60</span> and the iron plating
    <span class="mono">57&#8202;53&#8202;49</span> &mdash; there is almost no room left to take
    them anywhere. Tint a floor past about 0.6 and the crossed grate, which renders
    <span class="mono">35&#8202;29&#8202;22</span>, stops reading as damage at all: everything
    becomes one dark smear. That was the first render of this round and it was unusable.</p>
    <p>A hull wall renders about <span class="mono">152</span> light grey. That is the headroom.
    Painted <code>Structure_UmberBurnt</code> it measures <span class="mono">55&#8202;33&#8202;17</span>
    &mdash; a straight multiply, and a total change of character. <strong>So the floors keep
    light tints that only shift hue, and the walls do the rusting.</strong> Every treatment below
    is built that way.</p>
    <p class="warn">Proven live, right: three rows of hull painted <code>Structure_UmberBurnt</code>,
    <code>guy762_StructureColor_HK47Rust</code> and <code>Structure_BrownDirt</code>, over
    unpainted grey. Not a mock-up.</p>
  </div>
  <figure><img src="WALLPROOF" alt="Three rows of gravship hull painted umber, rust and brown over unpainted grey">
    <figcaption>live test block, 8&times;6 hull</figcaption></figure>
</div>

<div class="two">
  <div><h3>Floors: one call, today</h3><p><code>jawa/set_terrain_layer layer='color'</code> takes a
  rect and a ColorDef. 144 of 144 cells, no refusals. The whole deck is a handful of calls.</p></div>
  <div><h3>Walls: two calls each</h3><p>There is no bridge tool for building colour. The route is
  the dev tool <code>Actions\\T: Set Color</code> plus a click on the ColorDef in its float menu
  &mdash; about 1,540 calls for 768 walls, a couple of minutes. A companion tool calling
  <code>Thing.SetColor</code> over a rect would make it one, but that needs the game down.</p></div>
  <div><h3>Holes cost substructure</h3><p>140 eaten cells means 140 fewer connected substructure
  cells, and the pod hangs off a one-cell stalk that the damage cuts. Cosmetically right;
  it will read as disconnected to the grav engine. Say the word if the pod should stay attached.</p></div>
</div>

<div class="rule"><h2>Five colour treatments</h2>
  <p>Same blistered layout in all five. Only the ColorDefs change.</p></div>
SCHEMES

<div class="rule"><h2>Where I would go next</h2>
  <p>Say which, and how far, and I will lay it on the live ship.</p></div>
<div class="two">
  <div><h3>Halo, dialled back</h3><p>Corrosion Halo has the right idea and is one notch too hot.
  Same scheme with <code>ReddishBrown</code> instead of <code>212thOrange</code> at the lips would
  keep the wound reading without the ship looking on fire.</p></div>
  <div><h3>More blisters, smaller</h3><p>37 blobs at 17% coverage. Pushing coverage to 25% with a
  finer noise scale gives many more small bites and fewer big ones &mdash; grubbier, less dramatic.
  One number.</p></div>
  <div><h3>Bleed plus halo</h3><p>The two are not exclusive: streak the walls aft to bow, then add
  the hot lip only around holes. That is probably the real answer and it is ten minutes.</p></div>
</div>

<footer>
  <p>Renders: gravship_floor_v2.py &mdash; seeded value noise, seed 20260827, coverage 0.17, eat threshold 26 cells.</p>
  <p>Tiles are 4-cell swatches cut from live captures at 30.17 px/cell. Wall base 152 grey, measured. Ground seen through holes is the real GrasslandSoil swatch.</p>
  <p>D:\\Luke\\dev\\Rimworld\\world\\_ship\\v2</p>
</footer>
</div>
"""

out = (HTML.replace("TILES", tiles_html)
           .replace("SCHEMES", "".join(secs))
           .replace("WALLPROOF", uri("wallproof.png")))
p = os.path.join(ROOT, "blistered.html")
open(p, "w").write(out)
print(p, round(os.path.getsize(p) / 1e6, 2), "MB")
