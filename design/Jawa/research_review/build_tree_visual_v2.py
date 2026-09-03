#!/usr/bin/env python3
"""Render the thirteen-trees PROPOSAL (vision pass v2) as one review page.

Reads restructured_model_v2.json (from classify_v2.py) and writes
research_trees_visual_v2.html. Run from repo root. Companion doc:
twelve_trees_proposal.md — this page IS that doc, made walkable.
"""
import html
import json
import re
from collections import defaultdict

M = json.load(open("design/Jawa/research_review/restructured_model_v2.json"))
surv = [m for m in M if m.get("tab2")]
newcut = [m for m in M if m["fate2"] == "cut" and m["fate"] != "cut"]
oldcut = [m for m in M if m["fate"] == "cut"]
merge = [m for m in M if m["fate"] == "merge"]
recost = [m for m in M if m.get("cost2")]

TREES = [
    ("Scavenger", "#c2a06a", "the pride-free floor — fire, water, food, hide, door, trap"),
    ("The Hearth", "#b98a4e", "comfort & culture — cooking, brew, furniture, art, music, cloth"),
    ("The Refinery", "#a8764e", "what sand and wreck become — fuels, chems, drugs, ores, synthetics"),
    ("The Workshop", "#bd6f4e", "making & mending — smithing, machining, electronics, vehicles, power"),
    ("Powder & Slug", "#8a8a6a", "kills by MASS — guns, cannon, mortars, blades, the Watch"),
    ("Blasterworks", "#c25a4a", "kills by HEAT — the blaster spine, plasma, beam, tibanna"),
    ("The Strange Schools", "#9c6b8a", "kills by STRANGER physics — ion, sonic, vibro, relics, saber"),
    ("The Shell", "#7089a0", "not dying — armors, shields, warcaskets, the maker doctrines"),
    ("Droidsmith", "#6f9083", "Ohm's hands — labor droids, parts, mechtech, drones"),
    ("The Waking Mind", "#5f8a74", "the flashpoint — war droids, the AI ladder, positronic minds"),
    ("THE SHIP", "#4a7d86", "the Utinni herself — gravtech, her systems, her guns, her memory"),
    ("The Reach", "#8a6b9c", "the trap — flesh, genes, bionics, archotech, priced brutally"),
    ("The Rites", "#a08a3a", "NEW — the liturgy: researching how to speak to the gods"),
]
TIERS = [("T0", "≤600"), ("T1", "600–1600"), ("T2", "1600–3000"), ("T3", "3000–5000"), ("T4", "5000+")]

RITES = [  # proposed rows — NOT part of the 522; dashed chips
    ("T0", "The Scrap Shrine", "RUT_Rites_ScrapShrine", 400),
    ("T1", "Conduit Choir", "RUT_Rites_ConduitChoir", 1200),
    ("T2", "God-Speaker Array", "RUT_Rites_GodSpeakerArray", 2600),
    ("T3", "Liturgy of the Hull", "RUT_Rites_HullLiturgy", 4000),
    ("T4", "The Gods Speak Back", "RUT_Rites_GodsSpeakBack", 8000),
]

NEWCUT_GROUPS = [
    ("Hero relic catalogs", "18",
     "Every row priced 100,000,000 by its own author — flagged unreachable — and each names a KotOR hero 4,000 years off era. Gear catalogs, not research.",
     "the items stay as loot; the best belong to Memory-Core quest rewards and trade finds",
     lambda m: "100000000" == str(m["cost"]) or m["defName"] == "guy762_ResearchKotOR_uncraftable"),
    ("VGE genetics", "6",
     "The gene-splicing laboratory register — 'strange genetic stuff the players won't even care about.'",
     "the creature-crafting GAMEPLAY returns v2 as an Oomo-sanctioned beast-breeding rite — hatchery, not laboratory",
     lambda m: m["defName"].startswith("GR_")),
    ("Deathrest", "1",
     "The vampire type case — sanguophage dormancy in a Jawa clan story.",
     "v2 'long-sleep cradle' ship structure if the dormancy gameplay is ever wanted",
     lambda m: m["defName"] == "Deathrest"),
    ("Torment Master", "2",
     "Torture-dungeon register, off the campaign's tone entirely.",
     "dead, nothing worth recovering",
     lambda m: "Torment" in m["mod"]),
    ("Dark Ages crypts", "2",
     "Gothic crypt register on a desert world.",
     "mass-interment gameplay could return as sand-tomb vaults in the clan idiom",
     lambda m: "Dark Ages" in m["mod"]),
    ("Dev-row hygiene", "1",
     "RimFridge power-factor row: cost 0, unlocks nothing, and the dump's one measured self-loop (requires itself).",
     "dead, nothing worth recovering",
     lambda m: m["defName"] == "RimFridge_PowerFactorSetting"),
]

TRADEOFFS = [
    ("1 · Thirteen tabs vs six", "Wider tab strip in the research screen (wraps at small UI scale) vs thirteen readable guilds. Middle option: 9 — fold the weapon trees to two (mass/energy), Rites into Reach.", "thirteen"),
    ("2 · Tier = cost band, enforced", "28 real price changes vs keeping techLevel tiers and the felt-wrongness (Light Installations in T4, ship systems at 100 points).", "enforce"),
    ("3 · VGE genetics", "Cut wholesale (loses creature-crafting gameplay) vs keep a small Flesh tree (keeps the lab register).", "cut; recover v2 as Oomo beast-breeding rites"),
    ("4 · Hero catalogs", "Cut 18 rows vs a Memory-Core relic-hunt chain. The relic hunt is attractive — but it is quest design, not research rows.", "cut now; relic hunt as a quest-layer item"),
    ("5 · Lightsabers", "Kept, re-costed as endgame hubris (peak Ozzik: a Jawa building a Jedi's weapon) vs cut as non-Jawa.", "kept — owner's call"),
    ("6 · Maker doctrines", "Czerka/Mando/Hutt/Tusken… equipment catalogs as a Shell sub-chain ('we learn each maker's ways') vs a 14th tree.", "sub-chain"),
    ("7 · Ritual mechanism size", "A: XML-only liturgy ladder · B: +development points (needs The Salvation ruled FLUID — it is not today) · C: ranked rites in C#.", "A now; B behind a fluidity ruling"),
    ("8 · Warcaskets", "Salvaged power-armor shells fit the register; the pirate flavor text does not.", "keep + reflavor pass"),
    ("9 · Droid Depot's flat catalog", "Sixteen rows all cost 2,000 → all land T2: a wall, not a ladder. Re-costing into 1,600→5,000 touches 16 more rows.", "re-cost at manifest draft"),
    ("10 · The Anomaly-exception debt", "The 42-row Anomaly cut removed the research route the sarlacc/Assailant exception relied on. That content needs a non-research route (item grant / Memory-Core event) BEFORE the cut ships.", "resolve at execution — hard gate"),
]

def esc(s): return html.escape(str(s))

out = []
w = out.append
w('<title>Thirteen Trees</title>')
w('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Oswald:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">')
w("""<style>
:root{
  --sand:#f2ecdf; --panel:#fbf8f1; --line:#e2d8c4; --line2:#efe8d8;
  --ink:#1e1a12; --ink2:#5c5341; --ink3:#8a7d63;
  --amber:#b97d2e; --rust:#a8503f; --keep:#3f7d54; --reflavor:#3f6f9c; --merge:#a07a2a; --gold:#8a7020;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --sand:#14110b; --panel:#1c1810; --line:#33291a; --line2:#241d12;
  --ink:#ece3d1; --ink2:#b3a688; --ink3:#7d7159;
  --amber:#d69a44; --rust:#d17762; --keep:#5cae76; --reflavor:#6a9bd6; --merge:#d1a24a; --gold:#c7a94a;
}}
:root[data-theme="dark"]{
  --sand:#14110b; --panel:#1c1810; --line:#33291a; --line2:#241d12;
  --ink:#ece3d1; --ink2:#b3a688; --ink3:#7d7159;
  --amber:#d69a44; --rust:#d17762; --keep:#5cae76; --reflavor:#6a9bd6; --merge:#d1a24a; --gold:#c7a94a;
}
*{box-sizing:border-box}
body{margin:0;background:var(--sand);color:var(--ink);
  font-family:"IBM Plex Sans",system-ui,sans-serif;font-size:15px;line-height:1.55;-webkit-font-smoothing:antialiased}
.wrap{max-width:1380px;margin:0 auto;padding:34px 22px 80px}
.eyebrow{font-family:"IBM Plex Mono",monospace;font-size:11px;letter-spacing:.18em;text-transform:uppercase;color:var(--amber);font-weight:500}
h1{font-family:"Oswald",sans-serif;font-weight:600;font-size:clamp(30px,5vw,46px);letter-spacing:.01em;margin:.28em 0 .1em;text-wrap:balance;line-height:1.02}
.lede{color:var(--ink2);max-width:70ch;margin:.4em 0 0;font-size:16px}
.stats{display:flex;flex-wrap:wrap;gap:26px;margin:26px 0 6px;font-family:"IBM Plex Mono",monospace}
.stat b{font-family:"Oswald",sans-serif;font-size:30px;font-weight:600;display:block;line-height:1;font-variant-numeric:tabular-nums}
.stat span{font-size:11px;letter-spacing:.09em;text-transform:uppercase;color:var(--ink3)}
.stat .r{color:var(--rust)} .stat .g{color:var(--keep)} .stat .a{color:var(--amber)}
.principle{border-left:3px solid var(--amber);padding:6px 0 6px 16px;margin:26px 0 8px;color:var(--ink);max-width:78ch}
h2{font-family:"Oswald",sans-serif;font-weight:500;font-size:24px;letter-spacing:.02em;margin:44px 0 4px}
.sub{color:var(--ink3);font-size:13px;margin:0 0 16px;max-width:90ch}
.scroll{overflow-x:auto;padding-bottom:8px}
.matrix{display:grid;grid-template-columns:64px repeat(13,minmax(128px,1fr));gap:1px;background:var(--line);border:1px solid var(--line);min-width:1860px}
.mh{background:var(--panel);padding:8px 9px 9px}
.mh .tn{font-family:"Oswald",sans-serif;font-weight:600;font-size:13.5px;letter-spacing:.02em;display:flex;align-items:center;gap:6px;line-height:1.15}
.mh .dot{width:8px;height:8px;border-radius:2px;flex:none}
.mh .th{font-size:10px;color:var(--ink3);margin-top:3px;line-height:1.3}
.mh .ct{font-family:"IBM Plex Mono",monospace;font-size:10px;color:var(--ink2);margin-top:4px;font-variant-numeric:tabular-nums}
.corner{background:var(--panel)}
.trow{background:var(--panel);padding:8px 8px;display:flex;flex-direction:column;gap:1px}
.trow .tt{font-family:"Oswald",sans-serif;font-weight:600;font-size:14px}
.trow .tc{font-family:"IBM Plex Mono",monospace;font-size:9.5px;color:var(--ink3)}
.cell{background:var(--panel);padding:6px 6px;display:flex;flex-wrap:wrap;gap:3px;align-content:flex-start}
.chip{font-family:"IBM Plex Mono",monospace;font-size:10px;line-height:1.3;padding:2px 5px;border-radius:3px;background:var(--line2);color:var(--ink2);border:1px solid transparent;white-space:normal;max-width:100%}
.chip.keep{border-color:var(--keep);color:var(--ink)}
.chip.reflavor{border-color:var(--reflavor);color:var(--ink)}
.chip.recost{border-color:var(--amber);color:var(--ink)}
.chip.proposed{border:1px dashed var(--gold);color:var(--ink);background:transparent}
.legend{display:flex;flex-wrap:wrap;gap:16px;margin:14px 0 0;font-size:12px;color:var(--ink2);font-family:"IBM Plex Mono",monospace}
.legend .k{display:inline-flex;align-items:center;gap:6px}
.legend .b{width:20px;height:12px;border-radius:3px;border:1px solid;background:var(--line2)}
.cuts{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:14px;margin-top:18px}
.cutcard{background:var(--panel);border:1px solid var(--line);border-radius:7px;padding:15px 16px}
.cutcard.flag{border-left:3px solid var(--rust)}
.cutcard.rec{border-left:3px solid var(--keep)}
.cutcard.loot{border-left:3px solid var(--merge)}
.cutcard.dead{border-left:3px solid var(--line);opacity:.72}
.cutcard.rec .src{color:var(--keep)}
.cutcard.loot .src{color:var(--merge)}
.cutcard h3{font-family:"Oswald",sans-serif;font-weight:600;font-size:17px;margin:0;display:flex;justify-content:space-between;align-items:baseline;gap:10px}
.cutcard h3 .n{font-family:"IBM Plex Mono",monospace;color:var(--rust);font-size:20px;font-variant-numeric:tabular-nums}
.cutcard .src{font-family:"IBM Plex Mono",monospace;font-size:10px;letter-spacing:.05em;text-transform:uppercase;color:var(--ink3);margin:3px 0 8px}
.cutcard p{margin:0 0 9px;font-size:13.5px;color:var(--ink);line-height:1.5}
.recover{font-size:12.5px;color:var(--keep);margin:0 0 9px;padding-left:10px;border-left:2px solid var(--keep)}
.cutlist{list-style:none;margin:0;padding:8px 0 0;border-top:1px dashed var(--line);font-size:12.5px;line-height:1.55}
.cutlist li{margin:0 0 4px;break-inside:avoid}
.cutlist b{font-weight:600;color:var(--ink)}
.cutlist .dn{font-family:"IBM Plex Mono",monospace;font-size:10.5px;color:var(--ink3)}
.cutcard.wide{grid-column:1/-1}
.cutcard.wide .cutlist{columns:3;column-gap:26px}
@media(max-width:900px){.cutcard.wide .cutlist{columns:2}}
@media(max-width:600px){.cutcard.wide .cutlist{columns:1}}
table.rc{border-collapse:collapse;font-size:12.5px;margin-top:14px;min-width:640px}
table.rc th{font-family:"Oswald",sans-serif;font-weight:600;text-align:left;padding:6px 14px 6px 0;border-bottom:1px solid var(--line);font-size:13px}
table.rc td{padding:5px 14px 5px 0;border-bottom:1px solid var(--line2);vertical-align:top}
table.rc .mono{font-family:"IBM Plex Mono",monospace;font-size:11px;color:var(--ink2)}
table.rc .up{color:var(--rust)} table.rc .down{color:var(--keep)}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:7px;padding:18px 20px;margin-top:14px;max-width:96ch}
.panel h3{font-family:"Oswald",sans-serif;font-weight:600;font-size:16px;margin:0 0 6px}
.panel p{margin:0 0 10px;font-size:14px}
.opt{border-left:3px solid var(--line);padding:2px 0 2px 14px;margin:0 0 12px}
.opt.rec{border-left-color:var(--keep)}
.opt b{font-weight:600}
.opt .tag{font-family:"IBM Plex Mono",monospace;font-size:10px;letter-spacing:.06em;text-transform:uppercase;color:var(--keep)}
.tos{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:14px;margin-top:18px}
.to{background:var(--panel);border:1px solid var(--line);border-radius:7px;padding:14px 16px}
.to h3{font-family:"Oswald",sans-serif;font-weight:600;font-size:15px;margin:0 0 6px}
.to p{margin:0 0 8px;font-size:13px;color:var(--ink2)}
.to .rec{font-size:12px;font-family:"IBM Plex Mono",monospace;color:var(--keep)}
.foot{margin-top:44px;padding-top:16px;border-top:1px solid var(--line);color:var(--ink3);font-size:12.5px;font-family:"IBM Plex Mono",monospace;line-height:1.7}
a{color:var(--amber)}
.vquote{font-style:italic;color:var(--ink2)}
</style>""")

w('<div class="wrap">')
w('<div class="eyebrow">Research normalization · vision pass v2 · PROPOSAL — nothing here is ruled</div>')
w('<h1>Thirteen trees</h1>')
w('<p class="lede">The six trees, re-split along the clan’s own taxonomy: weapons by the <b>physics of how they kill</b>, droids along the <b>Ohm/Oomo fault</b>, the ship re-armed as the exotic payoff, the trap slimmed to what actually tempts — and one new tree for the liturgy. Tier is now <b>derived from the ruled cost band</b>, so every felt-tier disagreement became an explicit re-cost you can veto row by row.</p>')

w('<div class="stats">')
w(f'<div class="stat"><b>522</b><span>live projects</span></div>')
w(f'<div class="stat"><b class="g">{len(surv)}</b><span>kept, in the trees</span></div>')
w(f'<div class="stat"><b class="r">{len(oldcut)}+{len(newcut)}</b><span>cut (v1 + this pass)</span></div>')
w(f'<div class="stat"><b>{len(merge)}</b><span>merged</span></div>')
w(f'<div class="stat"><b class="a">{len(recost)}</b><span>re-costs proposed</span></div>')
w(f'<div class="stat"><b>13</b><span>trees</span></div>')
w('</div>')

w('<div class="principle">v1 fixed <b>tab follows content</b>. v2 adds the other half: <b>tier follows cost, and cost is a design decision.</b> Where a row’s price put it in a tier that reads wrong — ship systems at 100 points, ultra capstones at 500 — the fix is an explicit re-cost (amber border, ▲▼ in the table below), never a silent re-label.</div>')

# ── matrix ───────────────────────────────────────────────────────────────────
w('<h2>The thirteen trees</h2>')
w('<p class="sub">Columns left→right are the ambition gradient; rows are the cost-band tiers. Hover a chip for its source mod and any re-cost. Dashed gold chips are PROPOSED new projects that do not exist yet.</p>')
w('<div class="scroll"><div class="matrix">')
w('<div class="mh corner"></div>')
bytree = defaultdict(list)
for m in surv: bytree[m["tab2"]].append(m)
for name, color, theme in TREES:
    n = len(bytree[name]) if name != "The Rites" else 0
    ct = f"{n} projects" if name != "The Rites" else "5 proposed"
    w(f'<div class="mh"><div class="tn"><span class="dot" style="background:{color}"></span>{esc(name)}</div>'
      f'<div class="th">{esc(theme)}</div><div class="ct">{ct}</div></div>')
for tier, band_label in TIERS:
    w(f'<div class="trow"><div class="tt">{tier}</div><div class="tc">{band_label}</div></div>')
    for name, color, theme in TREES:
        w('<div class="cell">')
        if name == "The Rites":
            for rt, rlabel, rdn, rcost in RITES:
                if rt == tier:
                    w(f'<span class="chip proposed" title="PROPOSED — {esc(rdn)} · cost {rcost}">{esc(rlabel)}</span>')
        else:
            rows = sorted((m for m in bytree[name] if m["tier2"] == tier), key=lambda x: x["label"].lower())
            for m in rows:
                cls = "chip"
                title = m["mod"]
                if m.get("cost2"):
                    cls += " recost"
                    title += f' · re-cost {m["cost"]}→{m["cost2"]}: {m["recost_why"]}'
                if m["fate"] == "keep": cls += " keep"; title += " · keep (ruled)"
                if m["fate"] == "reflavor": cls += " reflavor"; title += " · reflavor"
                w(f'<span class="{cls}" title="{esc(title)}">{esc(m["label"])}</span>')
        w('</div>')
w('</div></div>')
w('<div class="legend">'
  '<span class="k"><span class="b" style="border-color:var(--keep)"></span>keep (ruled)</span>'
  '<span class="k"><span class="b" style="border-color:var(--reflavor)"></span>reflavor</span>'
  '<span class="k"><span class="b" style="border-color:var(--amber)"></span>re-cost proposed</span>'
  '<span class="k"><span class="b" style="border:1px dashed var(--gold);background:transparent"></span>PROPOSED new project</span>'
  '<span class="k"><span class="b"></span>untouched</span></div>')

# ── re-costs ─────────────────────────────────────────────────────────────────
w('<h2>The 28 re-costs</h2>')
w('<p class="sub">Every one is a real balance change to a base cost (Research Reinvented’s techprint economy multiplies on top). Veto row by row.</p>')
w('<div class="panel" style="margin:0 0 16px"><p style="margin:0"><b>Checked before you rule:</b> the XML cost <b>is</b> what the player pays — '
  '<span style="font-family:\'IBM Plex Mono\',monospace;font-size:12px">ResearchProjectDef.Cost</span> returns '
  '<span style="font-family:\'IBM Plex Mono\',monospace;font-size:12px">baseCost</span> directly, and difficulty scales research '
  '<i>speed</i>, never the cost (VERIFIED in source). Research Reinvented, Cherry Picker and five other research mods write it nowhere. '
  '<b>One exception:</b> <i>Configurable Techprints</i> is active and ships a real load-time rewrite of every baseCost — dormant, because '
  'its “Modify Base Costs” setting defaults off and this install has no settings file for it. Ticking that one checkbox would silently '
  'invalidate every tier on this page.</p></div>')
w('<div class="scroll"><table class="rc"><tr><th>project</th><th>defName</th><th>old → new</th><th>why</th></tr>')
for m in sorted(recost, key=lambda x: (x["tab2"] or "", x["label"])):
    old, new = int(m["cost"]), int(m["cost2"])
    arrow = '<span class="up">▲</span>' if new > old else '<span class="down">▼</span>'
    w(f'<tr><td><b>{esc(m["label"])}</b> <span class="mono">{esc(m["tab2"])}</span></td>'
      f'<td class="mono">{esc(m["defName"])}</td>'
      f'<td class="mono">{old:,} → {new:,} {arrow}</td><td>{esc(m["recost_why"])}</td></tr>')
w('</table></div>')

# ── new cuts ─────────────────────────────────────────────────────────────────
w('<h2>Cut this pass — and what each cut can give back</h2>')
w('<div class="panel" style="margin:0 0 16px;border-left:3px solid var(--rust)"><p style="margin:0">'
  '<b>What “cut” means here:</b> a cut removes a <span style="font-family:\'IBM Plex Mono\',monospace;font-size:12px">'
  'ResearchProjectDef</span> from the player’s tree — <b>and nothing else</b>. Every thing, building, creature and piece '
  'of map content it unlocked stays in the game for our own repurposing: the sarlacc, the Assailant dungeons, the '
  'terminator/night-side creatures. Measured against the live cut list, the whole containment and bioferrite economy '
  '(holding platforms, inhibitors, harvesters, Bioferrite itself) is present and uncut.</p></div>')
w(f'<p class="sub">{len(newcut)} further rows leave the trees under the aggressive-filter directive. Every card carries a <b>recover line</b>: how the underlying GAMEPLAY could return without the non-canon weirdness — or an honest “dead.” The v1 cuts ({len(oldcut)}: Anomaly 42 · Royalty 19 · Dungeon 10 · measured-dead 8 · Big &amp; Small 5) are unchanged and listed in the v1 visual.</p>')
w('<div class="cuts">')
claimed = set()
for gname, n, why, recover, pred in NEWCUT_GROUPS:
    rows = [m for m in newcut if pred(m) and m["defName"] not in claimed]
    for m in rows: claimed.add(m["defName"])
    if not rows: continue
    flag = " flag wide" if len(rows) > 12 else " flag" if len(rows) > 4 else ""
    lis = "".join(f'<li><b>{esc(m["label"])}</b> <span class="dn">{esc(m["defName"])}</span></li>'
                  for m in sorted(rows, key=lambda x: x["label"].lower()))
    w(f'<div class="cutcard{flag}"><h3>{esc(gname)}<span class="n">{len(rows)}</span></h3>'
      f'<div class="src">Fable proposal · owner reviews</div><p>{why}</p>'
      f'<div class="recover">recover? {esc(recover)}</div>'
      f'<ul class="cutlist">{lis}</ul></div>')
w('</div>')
unclaimed = [m for m in newcut if m["defName"] not in claimed]
if unclaimed:
    w(f'<p class="sub">⚠ unbucketed new cuts (bug if nonempty): {", ".join(m["defName"] for m in unclaimed)}</p>')

# ── recoveries from the 84 v1 cuts ───────────────────────────────────────────
# parsed from recovery_drafts.md so the doc stays the single source
REC_DOC = "design/Jawa/research_review/recovery_drafts.md"
try:
    _doc = open(REC_DOC, encoding="utf-8").read()
except OSError:
    _doc = ""
rec_clusters = []
if _doc:
    roster = {}
    rb = re.search(r"```roster\n(.*?)```", _doc, re.S)
    if rb:
        for line in rb.group(1).strip().splitlines():
            parts = line.split()
            if len(parts) >= 3 and parts[0].isdigit():
                roster[int(parts[0])] = (parts[1], parts[2:])
    for mt in re.finditer(r"^## (\d+)\.\s+(.*?)\s+—\s+([A-Z-]+(?:, as a pointer)?)\s+\((\d+) rows?\)$",
                          _doc, re.M):
        cid, title, verdict, n = int(mt.group(1)), mt.group(2), mt.group(3), int(mt.group(4))
        body = _doc[mt.end():]
        nxt = re.search(r"^## \d+\.", body, re.M)
        body = body[:nxt.start()] if nxt else body
        # RECOVER clusters carry "**The draft.**"; DEAD/LOOT-ONLY carry their
        # verdict as a bolded "Dead because…" / plain paragraph instead
        dm = (re.search(r"\*\*The draft\.?\*\*\s*(.+?)(?:\n\n|\Z)", body, re.S)
              or re.search(r"\*\*(?:Dead because[^*]*)\*\*\s*(.+?)(?:\n\n|\Z)", body, re.S))
        if dm:
            draft = re.sub(r"\s+", " ", dm.group(1)).strip()
        else:
            def _is_prose(p):
                p = p.strip()
                if not p or set(p) <= set("-—*_ "):
                    return False                      # rule / separator
                # a roster line is only backticked names, costs and separators
                return bool(re.sub(r"`[^`]*`|\([^)]*\)|[·,;\s]", "", p))
            paras = [p for p in re.split(r"\n\n", body.strip()) if _is_prose(p)]
            draft = re.sub(r"\s+", " ", paras[0]).strip() if paras else ""
        draft = re.sub(r"[*`]", "", draft)
        if len(draft) > 400:
            draft = draft[:397].rsplit(" ", 1)[0] + "…"
        rec_clusters.append((cid, title, verdict.split(",")[0], n,
                             roster.get(cid, ("", []))[1], draft))
if rec_clusters:
    nrec = sum(c[3] for c in rec_clusters if c[2] == "RECOVER")
    ndead = sum(c[3] for c in rec_clusters if c[2] == "DEAD")
    nloot = sum(c[3] for c in rec_clusters if c[2] == "LOOT-ONLY")
    w('<h2>What the 84 earlier cuts could give back</h2>')
    w(f'<p class="sub">The v1 cuts stay cut — this asks the owner\'s other question: what GAMEPLAY did each carry, '
      f'and can it re-enter stripped of the weirdness? {nrec} rows recover, {nloot} are loot-only, {ndead} are '
      f'honestly dead. Grouped by idea, not by row — the bioferrite chain is one economy, not six recoveries.</p>')
    w('<div class="cuts">')
    for cid, title, verdict, n, names, draft in rec_clusters:
        cls = {"RECOVER": " rec", "LOOT-ONLY": " loot"}.get(verdict, " dead")
        wide = " wide" if len(names) > 10 else ""
        lis = "".join(f'<li><span class="dn">{esc(x)}</span></li>' for x in names)
        w(f'<div class="cutcard{cls}{wide}"><h3>{esc(title)}<span class="n">{n}</span></h3>'
          f'<div class="src">{esc(verdict)}</div>'
          + (f'<p>{esc(draft)}</p>' if draft else '')
          + f'<ul class="cutlist">{lis}</ul></div>')
    w('</div>')

# ── the rites ────────────────────────────────────────────────────────────────
w('<h2>The Rites — researching the liturgy</h2>')
w('<p class="sub vquote">“Could they research better shipwide rituals that would be more ideologically active and powerful as they learn from their shipboard gods?”</p>')
w('<div class="panel">')
w('<p>Yes — and most of it needs no C#. Two engine facts shape it: the ideoligion <b>bakes at world creation</b> (XML cannot add rituals to a live ideo; the campaign’s <span class="mono" style="font-family:\'IBM Plex Mono\',monospace">The Salvation.rid</span> is not fluid today), and ritual <b>outcome quality is computed from data</b> — the engine’s <i>RitualOutcomeComp_RoomStat</i> and <i>RitualOutcomeComp_BuildingsPresent</i> read the ritual room and named buildings in it (both VERIFIED in source). So research that unlocks better liturgy <b>buildings</b> makes every ritual measurably stronger through the vanilla quality table.</p>')
w('<div class="opt rec"><span class="tag">recommended · XML-only</span><br><b>A — the liturgy infrastructure ladder.</b> Five projects (dashed gold in the matrix): Scrap Shrine → Conduit Choir → God-Speaker Array → Liturgy of the Hull → The Gods Speak Back. Each unlocks ritual buildings; a patch adds their quality comps to the campaign rituals’ outcome defs. Better moods, better rewards, fewer disasters — zero new mechanics, zero theology coupling (canon §6.3 holds). The T3/T4 projects are ship-only / memory-gated: the deep liturgy is <b>revealed by the Utinni, not derived</b> — research-as-revelation applied to worship.</div>')
w('<div class="opt"><span class="tag" style="color:var(--amber)">small C# · needs one ruling</span><br><b>B — the gods answer.</b> Completing a Rites project grants ideo development points, so the player reforms in new rituals/precepts — research literally funds doctrinal growth. Requires ruling The Salvation FLUID (a real campaign decision: fluid ideos can drift). Sits cleanly on top of A.</div>')
w('<div class="opt"><span class="tag" style="color:var(--ink3)">big C# · parked</span><br><b>C — ranked rites.</b> Per-ritual rank in a WorldComponent, research raises it, a Harmony postfix scales outcomes. Most powerful, most coupling; v2 only if A+B under-deliver.</div>')
w('</div>')

# ── royalty ──────────────────────────────────────────────────────────────────
w('<h2>Royalty’s inspiration — does tech gate the world?</h2>')
w('<div class="panel">')
w('<p><b>No — the campaign already ruled the stronger inversion: the world gates tech.</b> The sitting’s four access classes (common · faction-held via techprints · jawa-special · ship-only) are exactly the Royalty idea worth keeping — progression bound to <b>standing and place</b> rather than points — without its literal permits. Faction-held techprints are the permit: the high tree ends up gated on who you trade with, raid, or befriend (TECHPRINT_FACTION_GATING_1 executes this). Ship-only is the title: the Utinni is the throne room, and her memory decides what you may know next.</p>')
w('<p>The Dungeon Pack cut set the boundary from the other side: research must never unlock a <i>place</i>. Places unlock <b>research</b> — the Memory-Core reveal, a vault’s schematics — which is already canon. Recommendation: no new world gate; add an <span style="font-family:\'IBM Plex Mono\',monospace;font-size:12px">access</span> column to the manifest so the gate is data.</p>')
w('</div>')

# ── trade-offs ───────────────────────────────────────────────────────────────
w('<h2>Trade-offs — for your later review</h2>')
w('<p class="sub">Each is a real decision with a stated recommendation. None is ruled by this page.</p>')
w('<div class="tos">')
for title, body, rec in TRADEOFFS:
    w(f'<div class="to"><h3>{esc(title)}</h3><p>{esc(body)}</p><div class="rec">recommend: {esc(rec)}</div></div>')
w('</div>')

w(f'<div class="foot">Vision pass v2, Fable design agent, 2026-09-03 — built from restructured_model_v2.json (coverage: 522 = {len(oldcut)} v1-cut + {len(merge)} merge + {len(newcut)} new-cut + {len(surv)} placed, asserted at generation). Prose: design/Jawa/research_review/twelve_trees_proposal.md. Tier bands: T0 ≤600 · T1 ≤1600 · T2 ≤3000 · T3 ≤5000 · T4 5000+. No defName renamed; cuts are Cherry Picker cuts; merges re-point unlocks first. Reflavor text still deliberately held — structure first.<br>Next: your read — the roster, the 30 cuts, the 28 re-costs, the Rites, the ten trade-offs.</div>')
w('</div>')

path = "design/Jawa/research_review/research_trees_visual_v2.html"
open(path, "w").write("\n".join(out))
print(f"wrote {path}")
for name, _, _ in TREES:
    print(f"  {name:22} {len(bytree[name]):3}")
print(f"survivors {len(surv)} · new-cut {len(newcut)} · re-cost {len(recost)}")
