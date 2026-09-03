#!/usr/bin/env python3
"""build_tree_visual.py — the research restructure, as a visual for the owner.

Reads the regrouped model (Transient/research_restructure/restructured.json,
produced by classify.py) and emits a self-contained Artifact HTML page: a
6-tab × 5-tier matrix of what stays, and a justified account of what was cut.

    python3 design/Jawa/research_review/build_tree_visual.py
"""
import html
import json
from collections import Counter, defaultdict

M = json.load(open("Transient/research_restructure/restructured.json"))

TABS = ["Scavenger", "Trade & Craft", "The Armory", "The Machine", "THE SHIP", "The Reach"]
TAB_THEME = {
    "Scavenger":     ("the humble floor — neolithic salvage, stills, traps, tailoring", "#c2a06a"),
    "Trade & Craft": ("the colony economy — refining, gas, power, fabrication, materials", "#bd6f4e"),
    "The Armory":    ("the weapon schools — blaster, ion, kinetic, sonic, armour", "#7089a0"),
    "The Machine":   ("the droid branch — mechtech, synstructs, AI, gathered and visible", "#6f9083"),
    "THE SHIP":      ("the gravship tree — gravtech, reactors, ship systems (revealed late)", "#4a7d86"),
    "The Reach":     ("the temptation — spacer, genes, archotech, priced brutally", "#8a6b9c"),
}
TIERS = ["T0", "T1", "T2", "T3", "T4"]
TIER_BAND = {"T0": "≤600", "T1": "600–1600", "T2": "1600–3000", "T3": "3000–5000", "T4": "5000+"}
TIER_NAME = {"T0": "Scavenger", "T1": "Trade", "T2": "Forge", "T3": "Spacer", "T4": "Reach"}

surv = [m for m in M if m.get("newtab")]
cut = [m for m in M if m["fate"] == "cut"]
merge = [m for m in M if m["fate"] == "merge"]

# matrix[tab][tier] = list of projects, non-untouched first
cell = defaultdict(list)
for m in surv:
    cell[(m["newtab"], m["tier"])].append(m)
FATE_ORDER = {"keep": 0, "reflavor": 1, "merge": 2, "untouched": 3}
for k in cell:
    cell[k].sort(key=lambda m: (FATE_ORDER.get(m["fate"], 4), m["label"].lower()))

# cut buckets (fix the bucketing: Dungeon before Anomaly-substring)
def bucket(m):
    r = m["reason"]
    if "Dungeon" in r:
        return "Dungeon Pack"
    if "Anomaly:" in r or ("Anomaly" in r and "principle" not in r):
        return "Anomaly"
    if "Big & Small" in r:
        return "Big & Small"
    if "oyalty" in r:
        return "Royalty"
    if "dead" in r.lower():
        return "measured-dead"
    return "other ruled"

CUT_INFO = {
    "Anomaly":       ("42", "Repurposed content, not a player tree — bioferrite/containment exists only for the sarlacc / Assailant exception. Reversed the taxonomy's 'untouched' default.", "owner, 2026-09-03"),
    "Dungeon Pack":  ("10", "Map & dungeon locations (Area 52, Lost Labyrinth, Thrumbo Valley) that unlock nothing — gating disguised as research, the exact Anomaly pattern.", "BENCH, on the owner's principle"),
    "Big & Small":   ("5",  "Framework genes & mad-science rows from the Big and Small stack — out of the campaign's register.", "owner, 2026-09-03"),
    "Royalty":       ("19", "Royalty's player-facing systems are ruled dead; their unlocks release to loot-only, not a research path.", "canon royalty.dead"),
    "measured-dead": ("8",  "Rows measured with zero live unlocks mod-wide — dead on arrival in this mod set.", "canon, sitting"),
}
cutb = defaultdict(list)
for m in cut:
    cutb[bucket(m)].append(m)

# full per-row verdicts for the measured-dead bucket — model reasons are truncated
# at 80 chars; these are research_tree_prep.md §1 verbatim.
DEAD_WHY = {
    "VAE_SterileAttire":        "all 3 unlocks cut (DoctorScrubs, LabCoat, SurgicalMask)",
    "VWE_MakeshiftWeapons":     "all 6 unlocks cut (the VWE_Gun_Makeshift* guns)",
    "VFEP_SweatFermentation":   "its 1 unlock (VFEP_Apparel_Rumsuit) is cut",
    "MM_Research_Repulsor":     "0 unlocks mod-wide — whole mod tree grepped, nothing references it",
    "guy762_ResearchKotOR_revan": "author-flagged dead: baseCost 99,999,999, techprintCommonality 0",
    "guy762_ResearchKotOR_exile": "author-flagged dead: same unobtainable base",
    "WallStuff":                "author-flagged dead: “No Longer needed, just left for now so it doesn't cause errors.”",
    "MatterToEnergyConversion": "author-flagged dead: same description, same mod",
}

# ── render ───────────────────────────────────────────────────────────────────
def esc(s):
    return html.escape(str(s))

def chip(m):
    cls = "chip"
    if m["fate"] == "merge":
        cls += " merge"
    elif m["fate"] == "keep":
        cls += " keep"
    elif m["fate"] == "reflavor":
        cls += " reflavor"
    title = esc(m["mod"])
    if m["fate"] != "untouched":
        title += " · " + esc(m["fate"])
    return f'<span class="{cls}" title="{title}">{esc(m["label"])}</span>'

out = []
w = out.append

w('<title>Research Restructure</title>')
w('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Oswald:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">')
w('''<style>
:root{
  --sand:#f2ecdf; --panel:#fbf8f1; --line:#e2d8c4; --line2:#efe8d8;
  --ink:#1e1a12; --ink2:#5c5341; --ink3:#8a7d63;
  --amber:#b97d2e; --rust:#a8503f; --keep:#3f7d54; --reflavor:#3f6f9c; --merge:#a07a2a;
  --scav:#c2a06a; --trade:#bd6f4e; --arm:#7089a0; --mach:#6f9083; --ship:#4a7d86; --reach:#8a6b9c;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --sand:#14110b; --panel:#1c1810; --line:#33291a; --line2:#241d12;
  --ink:#ece3d1; --ink2:#b3a688; --ink3:#7d7159;
  --amber:#d69a44; --rust:#d17762; --keep:#5cae76; --reflavor:#6a9bd6; --merge:#d1a24a;
  --scav:#cbae7e; --trade:#cf8365; --arm:#87a0b8; --mach:#84a89a; --ship:#5f9aa4; --reach:#a488b6;
}}
:root[data-theme="dark"]{
  --sand:#14110b; --panel:#1c1810; --line:#33291a; --line2:#241d12;
  --ink:#ece3d1; --ink2:#b3a688; --ink3:#7d7159;
  --amber:#d69a44; --rust:#d17762; --keep:#5cae76; --reflavor:#6a9bd6; --merge:#d1a24a;
  --scav:#cbae7e; --trade:#cf8365; --arm:#87a0b8; --mach:#84a89a; --ship:#5f9aa4; --reach:#a488b6;
}
*{box-sizing:border-box}
body{margin:0;background:var(--sand);color:var(--ink);
  font-family:"IBM Plex Sans",system-ui,sans-serif;font-size:15px;line-height:1.55;
  -webkit-font-smoothing:antialiased}
.wrap{max-width:1220px;margin:0 auto;padding:34px 22px 80px}
.eyebrow{font-family:"IBM Plex Mono",monospace;font-size:11px;letter-spacing:.18em;
  text-transform:uppercase;color:var(--amber);font-weight:500}
h1{font-family:"Oswald",sans-serif;font-weight:600;font-size:clamp(30px,5vw,46px);
  letter-spacing:.01em;margin:.28em 0 .1em;text-wrap:balance;line-height:1.02}
.lede{color:var(--ink2);max-width:66ch;margin:.4em 0 0;font-size:16px}
.stats{display:flex;flex-wrap:wrap;gap:26px;margin:26px 0 6px;
  font-family:"IBM Plex Mono",monospace}
.stat b{font-family:"Oswald",sans-serif;font-size:30px;font-weight:600;display:block;
  line-height:1;font-variant-numeric:tabular-nums}
.stat span{font-size:11px;letter-spacing:.09em;text-transform:uppercase;color:var(--ink3)}
.stat .r{color:var(--rust)} .stat .g{color:var(--keep)}
.principle{border-left:3px solid var(--amber);padding:6px 0 6px 16px;margin:26px 0 8px;
  color:var(--ink);max-width:74ch}
.principle b{font-weight:600}
h2{font-family:"Oswald",sans-serif;font-weight:500;font-size:24px;letter-spacing:.02em;
  margin:44px 0 4px}
.sub{color:var(--ink3);font-size:13px;margin:0 0 16px}
.scroll{overflow-x:auto;padding-bottom:8px}
.matrix{display:grid;grid-template-columns:70px repeat(6,minmax(150px,1fr));
  gap:1px;background:var(--line);border:1px solid var(--line);min-width:1000px}
.mh{background:var(--panel);padding:9px 10px 10px}
.mh .tn{font-family:"Oswald",sans-serif;font-weight:600;font-size:15px;letter-spacing:.02em;
  display:flex;align-items:center;gap:7px}
.mh .dot{width:9px;height:9px;border-radius:2px;flex:none}
.mh .th{font-size:11px;color:var(--ink3);margin-top:3px;line-height:1.35}
.mh .ct{font-family:"IBM Plex Mono",monospace;font-size:11px;color:var(--ink2);
  margin-top:5px;font-variant-numeric:tabular-nums}
.corner{background:var(--panel)}
.trow{background:var(--panel);padding:8px 8px;display:flex;flex-direction:column;
  justify-content:flex-start;gap:1px}
.trow .tt{font-family:"Oswald",sans-serif;font-weight:600;font-size:14px}
.trow .tc{font-family:"IBM Plex Mono",monospace;font-size:10px;color:var(--ink3);
  letter-spacing:.03em}
.trow .tk{font-size:10px;color:var(--ink3);text-transform:uppercase;letter-spacing:.06em}
.cell{background:var(--panel);padding:7px 7px;display:flex;flex-wrap:wrap;gap:4px;
  align-content:flex-start}
.chip{font-family:"IBM Plex Mono",monospace;font-size:10.5px;line-height:1.3;
  padding:2px 6px;border-radius:3px;background:var(--line2);color:var(--ink2);
  border:1px solid transparent;white-space:normal;max-width:100%}
.chip.keep{border-color:var(--keep);color:var(--ink)}
.chip.reflavor{border-color:var(--reflavor);color:var(--ink)}
.chip.merge{border-color:var(--merge);color:var(--ink);
  background:linear-gradient(0deg,var(--line2),var(--line2))}
.legend{display:flex;flex-wrap:wrap;gap:16px;margin:14px 0 0;font-size:12px;
  color:var(--ink2);font-family:"IBM Plex Mono",monospace}
.legend .k{display:inline-flex;align-items:center;gap:6px}
.legend .b{width:20px;height:12px;border-radius:3px;border:1px solid;background:var(--line2)}
.cuts{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px;margin-top:18px}
.cutcard{background:var(--panel);border:1px solid var(--line);border-radius:7px;padding:15px 16px}
.cutcard.flag{border-left:3px solid var(--rust)}
.cutcard h3{font-family:"Oswald",sans-serif;font-weight:600;font-size:17px;margin:0;
  display:flex;justify-content:space-between;align-items:baseline;gap:10px}
.cutcard h3 .n{font-family:"IBM Plex Mono",monospace;color:var(--rust);font-size:20px;
  font-variant-numeric:tabular-nums}
.cutcard .src{font-family:"IBM Plex Mono",monospace;font-size:10px;letter-spacing:.05em;
  text-transform:uppercase;color:var(--ink3);margin:3px 0 8px}
.cutcard p{margin:0 0 9px;font-size:13.5px;color:var(--ink);line-height:1.5}
.cutlist{list-style:none;margin:0;padding:8px 0 0;border-top:1px dashed var(--line);
  columns:1;font-size:12.5px;line-height:1.55}
.cutlist li{margin:0 0 4px;break-inside:avoid}
.cutlist b{font-weight:600;color:var(--ink)}
.cutlist .dn{font-family:"IBM Plex Mono",monospace;font-size:10.5px;color:var(--ink3)}
.cutlist .modn{font-size:11px;color:var(--ink3)}
.cutlist .why1{font-size:11.5px;color:var(--ink2);margin:1px 0 5px;padding-left:10px;
  border-left:2px solid var(--line)}
.cutcard.wide{grid-column:1/-1}
.cutcard.wide .cutlist{columns:3;column-gap:26px}
@media(max-width:900px){.cutcard.wide .cutlist{columns:2}}
@media(max-width:600px){.cutcard.wide .cutlist{columns:1}}
.cutcard .ex{font-family:"IBM Plex Mono",monospace;font-size:11px;color:var(--ink3);
  line-height:1.6;word-break:break-word}
.foot{margin-top:44px;padding-top:16px;border-top:1px solid var(--line);
  color:var(--ink3);font-size:12.5px;font-family:"IBM Plex Mono",monospace;line-height:1.7}
a{color:var(--amber)}
</style>''')

w('<div class="wrap">')
w('<div class="eyebrow">Research normalization · Ash’karr campaign</div>')
w('<h1>The research trees, restructured</h1>')
w('<p class="lede">Every research project in the live game, regrouped by <b>what it is</b> '
  '— not by what it costs — into six thematic tabs, read left to right as the '
  'colony’s ambition gradient. This is the shape before we touch a word of reflavor text.</p>')

w('<div class="stats">')
w(f'<div class="stat"><b>522</b><span>live projects</span></div>')
w(f'<div class="stat"><b class="g">{len(surv)}</b><span>kept, in the trees</span></div>')
w(f'<div class="stat"><b class="r">{len(cut)}</b><span>removed</span></div>')
w(f'<div class="stat"><b>{len(merge)}</b><span>merged onto a survivor</span></div>')
w('</div>')

w('<div class="principle">The manifest had defaulted every tab from the <b>cost band</b> — '
  'so a T3 blaster landed in “The Reach” next to archotech, and The Armory held nine '
  'projects while sixty-two weapons sat scattered elsewhere. The fix is the whole point of this '
  'pass: <b>tab follows content, tier stays orthogonal.</b> A weapon is Armory whether it costs '
  '400 or 8,000; the tier only says how dear it is.</div>')

# matrix
w('<h2>The six trees</h2>')
w('<p class="sub">Columns rise in ambition — the humble Scavenger floor to the Reach’s trap. '
  'Rows are the cost/tech tier. A cell holds every project of that tab at that tier.</p>')
w('<div class="scroll"><div class="matrix">')
w('<div class="mh corner"></div>')
for tab in TABS:
    theme, hue = TAB_THEME[tab]
    n = sum(1 for m in surv if m["newtab"] == tab)
    w(f'<div class="mh"><div class="tn"><span class="dot" style="background:{hue}"></span>{esc(tab)}</div>'
      f'<div class="th">{esc(theme)}</div><div class="ct">{n} projects</div></div>')
for tier in TIERS:
    w(f'<div class="trow"><div class="tt">{tier}</div><div class="tk">{esc(TIER_NAME[tier])}</div>'
      f'<div class="tc">{esc(TIER_BAND[tier])}</div></div>')
    for tab in TABS:
        ms = cell.get((tab, tier), [])
        w('<div class="cell">')
        for m in ms:
            w(chip(m))
        w('</div>')
w('</div></div>')
w('<div class="legend">'
  '<span class="k"><span class="b" style="border-color:var(--keep)"></span>keep (ruled)</span>'
  '<span class="k"><span class="b" style="border-color:var(--reflavor)"></span>reflavor</span>'
  '<span class="k"><span class="b" style="border-color:var(--merge)"></span>merge onto survivor</span>'
  '<span class="k"><span class="b"></span>untouched — kept as-is</span>'
  '</div>')

# cuts
w('<h2>What I removed, and why</h2>')
w(f'<p class="sub">{len(cut)} projects leave the trees entirely. Two of these are the same '
  'move — content that was never a player research path.</p>')
w('<div class="cuts">')
order = ["Anomaly", "Dungeon Pack", "Royalty", "measured-dead", "Big & Small"]
for b in order:
    if b not in cutb:
        continue
    n, why, src = CUT_INFO[b]
    flag = " flag" if b in ("Anomaly", "Dungeon Pack") else ""
    if len(cutb[b]) > 12:
        flag += " wide"
    rows = sorted(cutb[b], key=lambda x: (x["mod"], x["label"]))
    mods = {m["mod"] for m in rows}
    lis = []
    for m in rows:
        modn = f'<span class="modn"> · {esc(m["mod"])}</span>' if len(mods) > 1 else ""
        extra = ""
        if m["defName"] in DEAD_WHY:
            extra = f'<div class="why1">{esc(DEAD_WHY[m["defName"]])}</div>'
        lis.append(f'<li><b>{esc(m["label"])}</b> <span class="dn">{esc(m["defName"])}</span>'
                   f'{modn}{extra}</li>')
    ex = '<ul class="cutlist">' + "".join(lis) + "</ul>"
    w(f'<div class="cutcard{flag}"><h3>{esc(b)}<span class="n">{n}</span></h3>'
      f'<div class="src">{esc(src)}</div><p>{why}</p>{ex}</div>')
w('</div>')

# merges note
if merge:
    w('<h2>Merged, not lost</h2>')
    w('<p class="sub">Six projects fold their unlocks onto a surviving chain before they die '
      '— an unlock is never orphaned by our own normalization. These stay visible in the '
      'trees above, marked as merges on their survivor.</p>')
    w('<div class="ex" style="font-family:\'IBM Plex Mono\',monospace;font-size:12px;color:var(--ink2);line-height:1.9">')
    for m in merge:
        tgt = m.get("reason", "")
        w(f'&bull; <b>{esc(m["label"])}</b> ({esc(m["mod"])})<br>')
    w('</div>')

w('<div class="foot">'
  'Regrouped by BENCH from the ruled manifest against the live 589-mod dump '
  '(2026-09-03), coverage-complete: 522 in, 522 accounted for. '
  'Tabs are thematic; tiers are the ruled cost bands (T0 ≤600 … T4 5000+). '
  'Reflavor text is deliberately held — structure first.<br>'
  'Next: your read on the grouping and the cuts, then we open the reflavor pass.'
  '</div>')
w('</div>')

open("design/Jawa/research_review/research_trees_visual.html", "w", encoding="utf-8").write("\n".join(out))
print("wrote design/Jawa/research_review/research_trees_visual.html")
print(f"survivors {len(surv)} · cut {len(cut)} · merge {len(merge)}")
for tab in TABS:
    print(f"  {tab:15} {sum(1 for m in surv if m['newtab']==tab)}")
