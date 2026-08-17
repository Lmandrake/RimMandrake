#!/usr/bin/env python3
"""Build the race -> faction assignment review sheet.

Pre-fills a proposed faction for all 70 RimMandrake xenotypes, shows what each
race IS in one line, marks the contested calls, and writes a self-contained HTML
page the owner reviews by disagreeing.

    python3 src/RimMandrake/Utils/gen_race_faction_sheet.py

🔴 REFUSES to overwrite the decisions file once frozen. The SHEET is always safe to
regenerate - it reads the decisions back in.
"""
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
RACES = os.path.join(REPO, "src/Jawa/RimMandrake_StarWarsRaces/Defs/XenotypeDefs")
FACDIR = os.path.join(REPO, "src/Jawa/Jawa_Patches/Defs/FactionDefs")
OUT = os.path.join(REPO, "design/Jawa/worldbuilding/review/race_faction_assignment.html")
PREFILL = OUT.replace(".html", ".prefill.json")

FACTIONS = [
    ("Empire",                    "The Galactic Empire", "human-centric occupier; the one permanent enemy"),
    ("OutlanderCivil",            "Homestead Defense League", "moisture farmers on dry wells - numerous, decentralised"),
    ("TribeCivil",                "Deep Desert Tribes", "the dune-sea tribes of the deep desert"),
    ("Pirate",                    "Blackstar Company", "permanent enemy; slavers, raiders, contract killers"),
    ("Jawa_IndigenousTribes",     "Jawa Trade Moot", "the planetary Jawa - salvage traders, NOT the player"),
    ("Jawa_HuttCartel",           "Hutt Cartel", "spice, salvage yards, sarlacc grounds, slaves"),
    ("Jawa_Junkers",              "the Junkers", "scrap crews and the Fuel Works in the Sunreach"),
    ("Jawa_WildsteamClan",        "Wildsteam Clan", "rivers, jungle and poison marsh at the terminator"),
    ("Jawa_DeepwaterCompact",     "Deepwater Compact", "holds every body of water; the Twilight Sea stronghold"),
    ("Jawa_AscendantHelix",       "Ascendant Helix", "geneticists and bloodline purists"),
    ("Jawa_FreeDroidEnclaves",    "Free Droid Enclaves", "independent droids in the volcanic uplands"),
    ("Jawa_GeonosianFoundryHive", "Geonosian Foundry Hive", "insectile foundry caste"),
    ("UNASSIGNED",                "(no faction)", "exists, spawnable in dev/quests, occurs organically nowhere"),
]

# proposed: race -> (faction, one-line reason, contested?)
P = {
 "MandrakeJawa":            ("Jawa_IndigenousTribes","🔴 CANON, owner ruling 2026-08-17: this is the Jawa he built IN GAME and exported as the .xtp. Already fielded at 1.00",False),
 "RimMandrakeJawa":         ("UNASSIGNED","🔴 CUT - donor-generated duplicate. MandrakeJawa is canon (owner, 2026-08-17). Never field both",False),
 # already fielded - carried forward
 "RimMandrakeNikto":        ("Jawa_HuttCartel","already fielded 0.30",False),
 "RimMandrakeGamorrean":    ("Jawa_Junkers","already fielded 0.30 by Junkers, 0.10 by Hutts",False),
 "RimMandrakeRodian":       ("Jawa_HuttCartel","already fielded 0.10",False),
 "RimMandrakeTrandoshan":   ("Jawa_HuttCartel","already fielded 0.10",False),
 "RimMandrakeAqualish":     ("Jawa_HuttCartel","already fielded 0.10",False),
 "RimMandrakeTwilek":       ("Jawa_HuttCartel","already fielded 0.10",False),
 "RimMandrakePyke":         ("Jawa_HuttCartel","already fielded 0.10 - spice cartel",False),
 "RimMandrakeDevaronian":   ("Jawa_HuttCartel","already fielded 0.10",False),
 "RimMandrakeWeequay":      ("Jawa_Junkers","already fielded 0.10",False),
 "RimMandrakeUgnaught":     ("Jawa_FreeDroidEnclaves","MOVED: canonical droid-tinkerers; gives the droid enclaves an organic face",True),
 "RimMandrakeSnivvian":     ("Jawa_Junkers","already fielded 0.10",False),
 "RimMandrakeArkanian":     ("Jawa_AscendantHelix","already fielded 0.30 - canonical geneticists",False),
 "RimMandrakeKaminoan":     ("Jawa_AscendantHelix","already fielded 0.10 - cloners",False),
 "RimMandrakeCerean":       ("Jawa_AscendantHelix","already fielded 0.10",False),
 "RimMandrakeBith":         ("Jawa_AscendantHelix","already fielded 0.10",False),
 "RimMandrakeChiss":        ("Empire","MOVED from Helix: canonically Imperial (Thrawn)",True),
 "RimMandrakeRakata":       ("Jawa_AscendantHelix","already fielded 0.10 - the Forsaken bloodline",False),
 "RimMandrakeUmbaran":      ("Jawa_AscendantHelix","already fielded 0.10",False),
 "RimMandrakeNeimoidian":   ("Jawa_AscendantHelix","already fielded 0.10",False),
 "RimMandrakeQuarren":      ("Jawa_DeepwaterCompact","already fielded 0.28 - aquatic",False),
 "RimMandrakeMonCalamari":  ("Jawa_DeepwaterCompact","already fielded 0.12 - aquatic",False),
 "RimMandrakeSelkath":      ("Jawa_DeepwaterCompact","already fielded 0.12 - aquatic",False),
 "RimMandrakeGungan":       ("Jawa_DeepwaterCompact","already fielded 0.12 - amphibious",False),
 "RimMandrakeChagrian":     ("Jawa_DeepwaterCompact","already fielded 0.12 - amphibious",False),
 "RimMandrakeHerglic":      ("Jawa_DeepwaterCompact","already fielded 0.12 - cetacean",False),
 "RimMandrakeDuros":        ("Jawa_DeepwaterCompact","already fielded 0.12 - navigators",False),
 "RimMandrakeWookiee":      ("Jawa_WildsteamClan","already fielded 0.30",False),
 "RimMandrakeYttakin":      ("Jawa_WildsteamClan","already fielded 0.20 - note: a VANILLA xenotype, not ours",True),
 "RimMandrakeCathar":       ("Jawa_WildsteamClan","already fielded 0.12 - feline hunters",False),
 "RimMandrakeEwok":         ("Jawa_WildsteamClan","already fielded 0.12 - forest dwellers",False),
 "RimMandrakeTogruta":      ("Jawa_WildsteamClan","already fielded 0.12",False),
 "RimMandrakeIthorian":     ("Jawa_WildsteamClan","already fielded 0.12 - herd-mind botanists",False),
 "RimMandrakeGeonosianVariants": ("Jawa_GeonosianFoundryHive","already fielded 1.00",False),
 # the 37 orphans
 "RimMandrakeHutt":         ("Jawa_HuttCartel","⭐ the Cartel currently contains NO Hutts",False),
 "RimMandrakeKlatoonian":   ("Jawa_HuttCartel","canonically bound in service to the Hutts",False),
 "RimMandrakeKubaz":        ("Jawa_HuttCartel","informants and spies",False),
 "RimMandrakeOrtolan":      ("Jawa_HuttCartel","court musicians - and the owner pulled it INTO v1 for working art",False),
 "RimMandrakeZeltron":      ("Jawa_HuttCartel","pleasure-trade retinue",True),
 "RimMandrakeFalleen":      ("Jawa_HuttCartel","Black Sun crime nobility",True),
 "RimMandrakeTusken":       ("TribeCivil","⭐⭐ the fiction puts Tuskens in the near-desert and NO faction fields them",False),
 "RimMandrakeTaung":        ("TribeCivil","Mandalorian ancestors - warrior tribes",False),
 "RimMandrakeKaleesh":      ("TribeCivil","warrior clans (Grievous)",False),
 "RimMandrakeNelvaanian":   ("TribeCivil","tribal shamans",False),
 "RimMandrakeIridonian":    ("TribeCivil","Zabrak warrior tribes",True),
 "RimMandrakeMimbanese":    ("TribeCivil","mud-world tribals",False),
 "RimMandrakeAbednedo":     ("OutlanderCivil","common labourers and smallholders",False),
 "RimMandrakeSullustan":    ("OutlanderCivil","navigators and well-diggers",False),
 "RimMandrakeMirialan":     ("OutlanderCivil","settled smallholders",False),
 "RimMandrakePantoran":     ("OutlanderCivil","cold-world settlers",False),
 "RimMandrakeBothan":       ("OutlanderCivil","traders and information brokers",True),
 "RimMandrakeChadraFan":    ("Jawa_Junkers","tiny tinkerers - scrap crews",False),
 "RimMandrakeFeeorin":      ("Jawa_Junkers","pirate-adjacent muscle",False),
 "RimMandrakeGand":         ("Jawa_Junkers","⚠️ AMMONIA-BREATHERS - they belong at the Fuel Works in the Sunreach",True),
 "RimMandrakeZygerrian":    ("Pirate","canonical slavers",False),
 "RimMandrakeAnzati":       ("Pirate","assassins",False),
 "RimMandrakeDefel":        ("Pirate","shadow-shifting killers",False),
 "RimMandrakeNagai":        ("Pirate","raiders",False),
 "RimMandrakeSithMassassi":     ("Jawa_AscendantHelix","warped bloodline - the Helix's own work",True),
 "RimMandrakeSithKissaiPureblood": ("Jawa_AscendantHelix","⭐ purebloods for a faction built on bloodline purity",False),
 "RimMandrakeSithZ":        ("Jawa_AscendantHelix","Sith lineage",True),
 "RimMandrakeDathomirian":  ("Jawa_AscendantHelix","Nightsister bloodline magick",True),
 "RimMandrakeMuun":         ("Jawa_AscendantHelix","Banking Clan cold intellect",True),
 "RimMandrakeIktotchi":     ("Jawa_AscendantHelix","precognitives",False),
 "RimMandrakeKelDor":       ("Jawa_AscendantHelix","Baran Do sages - masked, atmosphere-dependent",True),
 "RimMandrakeEchani":       ("Empire","warrior culture serving as Imperial auxiliaries",True),
 "RimMandrakeNautolan":     ("Jawa_DeepwaterCompact","aquatic",False),
 "RimMandrakeTogorian":     ("Jawa_WildsteamClan","feline hunters",False),
 "RimMandrakeLasat":        ("Jawa_WildsteamClan","ashla-touched wanderers",False),
 "RimMandrakeYoderForceGremlin": ("UNASSIGNED","LEFT OPEN ON PURPOSE: extremely rare, factionlessGenerationWeight 0. Should it occur at all?",True),
}

INVENTED = [
 "Chiss moved to the Empire and Echani added to it, on CANON Imperial alignment - the campaign has not ruled that the Empire fields any non-humans.",
 "Ugnaughts given to the Free Droid Enclaves so a droid faction has an organic face. The alternative is Inherit=False with an EMPTY set, i.e. droids only.",
 "Gand assigned to the Junkers because they breathe ammonia and the Junkers hold the Fuel Works. Nothing in the specs says so.",
 "The four vanilla reskins (Empire, OutlanderCivil, TribeCivil, Pirate) have NO xenotypeChances today, so they field vanilla xenohumans - Hussars, Dirtmoles, Genies. Every assignment to them is new content, and each will need a Baseliner share so they do not become 100% alien.",
 "Sith lineages, Dathomirians and Muun all parked in the Ascendant Helix because it is the only faction whose theme absorbs them. That is convenience, not design.",
 "RESOLVED, not invented: MandrakeJawa is canon and RimMandrakeJawa is cut - owner ruling 2026-08-17.",
]


def grade(chance):
    """A / S / R from an existing xenotypeChances weight."""
    if chance >= 0.25:
        return "A"
    if chance >= 0.08:
        return "S"
    return "R"


def main():
    if os.path.exists(PREFILL):
        try:
            if json.load(open(PREFILL)).get("frozen") and "--i-know-this-overwrites-the-owners-decisions" not in sys.argv:
                sys.exit("REFUSING: %s is frozen. Pass --i-know-this-overwrites-the-owners-decisions." % PREFILL)
        except Exception:
            pass

    races = {}
    for fn in os.listdir(RACES):
        s = open(os.path.join(RACES, fn), encoding="utf-8", errors="replace").read()
        for m in re.finditer(r"<XenotypeDef>(.*?)</XenotypeDef>", s, re.S):
            b = m.group(1)
            dn = re.search(r"<defName>(\w+)</defName>", b)
            if not dn:
                continue
            lab = re.search(r"<label>([^<]*)</label>", b)
            desc = re.search(r"<description>([^<]*)</description>", b)
            races[dn.group(1)] = {
                "label": lab.group(1) if lab else dn.group(1),
                "desc": (desc.group(1) if desc else "").strip(),
                "genes": len(re.findall(r"<li>\w+</li>", b)),
                "namer": bool(re.search(r"<nameMaker>", b)),
            }
    # vanilla baseline humans - the owner needs to place them everywhere
    races["Baseliner"] = {"label": "Baseliner (plain human)", "genes": 0, "namer": False,
        "desc": "Vanilla unmodified humans. Not one of ours, but every faction needs a human share "
                "or it becomes 100% alien."}

    # seed from what each faction ALREADY fields, graded off the real weights
    cur = {}
    for fn in sorted(os.listdir(FACDIR)):
        s = open(os.path.join(FACDIR, fn), encoding="utf-8", errors="replace").read()
        for m in re.finditer(r"<FactionDef[^>]*>(.*?)</FactionDef>", s, re.S):
            b = m.group(1)
            dn = re.search(r"<defName>([\w.]+)</defName>", b).group(1)
            xs = re.search(r"<xenotypeSet([^>]*)>(.*?)</xenotypeSet>", b, re.S)
            if not xs:
                continue
            for k, v in re.findall(r"<(\w+)(?:\s+[^>]*)?>([\d.]+)</\1>", xs.group(2)):
                cur.setdefault(k, {})[dn] = float(v)

    HUMAN = {"Empire": "A", "OutlanderCivil": "A", "TribeCivil": "A", "Pirate": "A",
             "Jawa_HuttCartel": "S", "Jawa_Junkers": "S", "Jawa_AscendantHelix": "S",
             "Jawa_DeepwaterCompact": "R", "Jawa_WildsteamClan": "R", "Jawa_IndigenousTribes": "R"}

    rows, grid = [], {}
    for dn, r in sorted(races.items(), key=lambda kv: kv[1]["label"].lower()):
        prop, why, contested = P.get(dn, ("UNASSIGNED", "not yet considered", True))
        cells = {}
        for fac, ch in (cur.get(dn) or {}).items():
            cells[fac] = grade(ch)
        if dn == "Baseliner":
            cells = dict(HUMAN)
            why = "PROPOSED: humans everywhere, dominant in the four vanilla-reskin factions"
            contested = True
        elif prop != "UNASSIGNED" and prop not in cells:
            cells[prop] = "A" if not cells else "S"
        grid[dn] = cells
        rows.append({"id": dn, "label": r["label"], "genes": r["genes"], "namer": r["namer"],
                     "desc": r["desc"][:300], "why": why, "contested": contested,
                     "wasOrphan": not (cur.get(dn))})

    pre = {"posture": "matrix", "generated": "2026-08-17",
           "meaning": "Per race x faction: A abundant, S some, R rare, N not present. "
                      "Absent from the file means N. Weights: A~0.30, S~0.10, R~0.03, "
                      "normalised per faction when written into xenotypeChances.",
           "grid": grid, "notes": {}}
    if not os.path.exists(PREFILL):
        json.dump(pre, open(PREFILL, "w"), indent=1)

    doc = (HTML.replace("__ROWS__", json.dumps(rows))
               .replace("__FACTIONS__", json.dumps(FACTIONS))
               .replace("__PREFILL__", json.dumps(pre))
               .replace("__INVENTED__", json.dumps(INVENTED)))
    open(OUT, "w", encoding="utf-8").write(doc)
    filled = sum(len(v) for v in grid.values())
    print("races: %d  factions: %d  cells pre-filled (non-N): %d  contested rows: %d"
          % (len(rows), len(FACTIONS) - 1, filled, sum(r["contested"] for r in rows)))
    print("wrote", OUT)


HTML = r"""<!doctype html><html><head><meta charset="utf-8">
<title>Ash'karr - race x faction matrix</title><style>
*{box-sizing:border-box}body{margin:0;background:#12151a;color:#d7dde5;font:13px/1.4 system-ui,sans-serif}
header{position:sticky;top:0;z-index:40;background:#171b22;border-bottom:1px solid #2a323d;padding:7px 12px}
h1{margin:0;font-size:15px;display:inline}
.bar{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-top:5px}
input[type=search],select{background:#0e1116;color:#d7dde5;border:1px solid #2f3946;border-radius:4px;padding:3px 6px;font:12px system-ui}
button{background:#243040;color:#d7dde5;border:1px solid #354458;border-radius:4px;padding:3px 8px;cursor:pointer;font:12px system-ui}
button:hover{background:#2d3b4e}
.count{color:#8e9aab;font-size:12px}.count b{color:#8fd48f}.warn{color:#ff9b9b}.ok{color:#8fd48f}
details{margin:6px 12px;background:#1b2027;border:1px solid #2a323d;border-radius:6px}
summary{cursor:pointer;padding:6px 10px;color:#ffcf6b;font-size:12px;text-transform:uppercase;letter-spacing:.04em}
details div,details ul{padding:0 12px 8px;color:#b9c3d0;font-size:12px}
table{border-collapse:separate;border-spacing:0;margin:8px 12px 40px}
th,td{padding:0;font-weight:400}
thead th{position:sticky;top:0;z-index:20;background:#202733;border-bottom:1px solid #3a4453;font-size:11px;color:#c7d2e0;
  height:120px;width:44px;min-width:44px;vertical-align:bottom;padding-bottom:5px}
thead th .rot{writing-mode:vertical-rl;transform:rotate(180deg);white-space:nowrap;max-height:110px;overflow:hidden}
thead th.first{position:sticky;left:0;z-index:30;width:300px;min-width:300px;text-align:left;vertical-align:bottom;padding:0 8px 5px}
tbody th{position:sticky;left:0;z-index:10;background:#161a20;border-right:1px solid #3a4453;border-bottom:1px solid #232a34;
  text-align:left;padding:3px 8px;width:300px;min-width:300px}
tbody tr:nth-child(even) th{background:#181d24}
.rn{font-weight:600}.rn .g{color:#68758a;font-weight:400;font-size:11px}
.flag{color:#ffcf6b}
td.c{border-bottom:1px solid #232a34;border-right:1px solid #202733;text-align:center;cursor:pointer;user-select:none;
  font-size:11.5px;font-weight:700;color:#5b6675}
td.c:hover{outline:1px solid #6f8199;outline-offset:-1px}
td.A{background:#2e5d34;color:#d8f5d8}td.S{background:#2b4560;color:#cfe4f7}td.R{background:#3b3a29;color:#e8e2b8}
tfoot td{position:sticky;bottom:0;background:#1b2027;border-top:1px solid #3a4453;text-align:center;font-size:10.5px;color:#8e9aab}
tfoot td.first{position:sticky;left:0;z-index:25;text-align:left;padding:3px 8px}
.desc{color:#8e9aab;font-size:11px;display:block;max-width:290px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
</style></head><body>
<header><h1>Ash'karr — race &times; faction matrix</h1>
<span class="count" id="ls" style="margin-left:10px"></span>
<div class="bar">
<input type="search" id="q" placeholder="search race…" size="24">
<select id="fState"><option value="">all races</option><option value="contested">contested only</option><option value="orphan">not fielded today</option><option value="empty">no faction at all</option><option value="placed">placed somewhere</option></select>
<button id="link">link to file…</button><button id="exp">copy JSON</button>
<span class="count">click a cell: N→R→S→A · shift-click reverses</span>
<span class="count" id="cnt"></span>
</div></header>
<details><summary>▸ Legend &amp; posture</summary><div>
<b>A</b> abundant (~0.30) &nbsp; <b>S</b> some (~0.10) &nbsp; <b>R</b> rare (~0.03) &nbsp; <b>N</b> not present.
Weights are normalised per faction when written into <code>xenotypeChances</code>, so the exact numbers do not need to sum to anything.
A faction column with no A gets flagged. Blank cell = N; only non-N cells are saved.
</div></details>
<details><summary>▸ Rules I invented — overrule these first</summary><ul id="inv"></ul></details>
<details><summary>▸ Race descriptions, for review</summary><div id="descs"></div></details>
<div id="body"></div>
<script>
const ROWS=__ROWS__, FACTIONS=__FACTIONS__.filter(f=>f[0]!=='UNASSIGNED'), PREFILL=__PREFILL__, INVENTED=__INVENTED__;
const ORDER=['N','R','S','A'];
let state=JSON.parse(localStorage.getItem('ashkarr_matrix')||'null')||{grid:{},notes:{}};
let filled=0,kept=0;
ROWS.forEach(r=>{ if(state.grid[r.id]===undefined){state.grid[r.id]=Object.assign({},PREFILL.grid[r.id]||{});filled++;} else kept++; });
INVENTED.forEach(t=>{const li=document.createElement('li');li.textContent=t;document.getElementById('inv').appendChild(li);});
document.getElementById('descs').innerHTML=ROWS.map(r=>'<div style="margin:4px 0"><b>'+r.label+'</b> <span class="g">'+r.genes+' genes'+(r.namer?', own namer':'')+'</span><br><span style="color:#9fb0c4">'+(r.desc||'(no description)')+'</span><br><span style="color:#7f8b9c;font-style:italic">'+r.why+'</span></div>').join('');

let handle=null,lastWrite='';
const DB=()=>new Promise(res=>{const r=indexedDB.open('ashkarr',1);r.onupgradeneeded=e=>{try{e.target.result.createObjectStore('h')}catch(x){}};r.onsuccess=e=>res(e.target.result);});
async function saveHandle(h){const db=await DB();db.transaction('h','readwrite').objectStore('h').put(h,'matrix');}
async function loadHandle(){const db=await DB();return new Promise(res=>{try{const q=db.transaction('h').objectStore('h').get('matrix');q.onsuccess=()=>res(q.result||null);q.onerror=()=>res(null);}catch(e){res(null)}});}
function payload(){const d=Object.assign({},PREFILL);d.grid=state.grid;d.notes=state.notes;
  d.placedCount=Object.values(state.grid).reduce((a,g)=>a+Object.keys(g).length,0);return JSON.stringify(d,null,1);}
let t=null;
function persist(){localStorage.setItem('ashkarr_matrix',JSON.stringify(state));clearTimeout(t);t=setTimeout(write,900);tally();}
async function write(){ if(!handle)return;
  const rowsWithAny=Object.values(state.grid).filter(g=>Object.keys(g).length).length;
  if(rowsWithAny < 10){document.getElementById('ls').innerHTML='<span class="warn">REFUSED to write: only '+rowsWithAny+' placed races in memory</span>';return;}
  try{const w=await handle.createWritable();await w.write(payload());await w.close();
    lastWrite=new Date().toLocaleTimeString();document.getElementById('ls').innerHTML='<span class="ok">saved '+lastWrite+'</span>';}
  catch(e){document.getElementById('ls').innerHTML='<span class="warn">write failed — click “link to file…”</span>';}}
document.getElementById('link').onclick=async()=>{ if(!window.showSaveFilePicker){document.getElementById('ls').innerHTML='<span class="warn">no File System Access API — use copy JSON</span>';return;}
  handle=await window.showSaveFilePicker({suggestedName:'race_faction_assignment.prefill.json',types:[{description:'JSON',accept:{'application/json':['.json']}}]});
  await saveHandle(handle);write();};
document.getElementById('exp').onclick=()=>{navigator.clipboard.writeText(payload());document.getElementById('ls').textContent='JSON copied';};
loadHandle().then(h=>{if(h){handle=h;document.getElementById('ls').innerHTML='<span class="ok">file link restored</span>';}});

function visible(){const q=document.getElementById('q').value.toLowerCase(),fs=document.getElementById('fState').value;
 return ROWS.filter(r=>{const g=state.grid[r.id]||{},n=Object.keys(g).length;
  if(q&&!(r.label+' '+r.id+' '+r.desc).toLowerCase().includes(q))return false;
  if(fs==='contested'&&!r.contested)return false;
  if(fs==='orphan'&&!r.wasOrphan)return false;
  if(fs==='empty'&&n)return false;
  if(fs==='placed'&&!n)return false;
  return true;});}
function tally(){
 const per={};FACTIONS.forEach(([k])=>per[k]={A:0,S:0,R:0});
 ROWS.forEach(r=>{const g=state.grid[r.id]||{};for(const k in g){if(per[k])per[k][g[k]]++;}});
 FACTIONS.forEach(([k],i)=>{const el=document.getElementById('t'+i);if(!el)return;
   const p=per[k];el.innerHTML=p.A?(p.A+'A '+p.S+'S '+p.R+'R'):'<span class="warn">no A</span>';});
 const placed=ROWS.filter(r=>Object.keys(state.grid[r.id]||{}).length).length;
 document.getElementById('cnt').innerHTML='· placed <b>'+placed+'</b>/'+ROWS.length+' races'+(lastWrite?'':' · <span class="warn">not linked to a file</span>');
}
function render(){
 const vis=visible();
 let h='<table><thead><tr><th class="first">race &nbsp;<span class="g">'+vis.length+' shown</span></th>';
 FACTIONS.forEach(([k,l])=>h+='<th title="'+l+'"><div class="rot">'+l+'</div></th>');
 h+='</tr></thead><tbody>';
 vis.forEach(r=>{const g=state.grid[r.id]||{};
  h+='<tr><th title="'+(r.desc||'').replace(/"/g,'&quot;')+'"><div class="rn">'+(r.contested?'<span class="flag">◆ </span>':'')+r.label+
     ' <span class="g">'+r.genes+'g'+(r.wasOrphan?', <span class="flag">orphan</span>':'')+'</span></div><span class="desc">'+r.why+'</span></th>';
  FACTIONS.forEach(([k])=>{const v=g[k]||'N';h+='<td class="c '+(v!=='N'?v:'')+'" data-r="'+r.id+'" data-f="'+k+'">'+(v==='N'?'':v)+'</td>';});
  h+='</tr>';});
 h+='</tbody><tfoot><tr><td class="first">column totals</td>';
 FACTIONS.forEach(([k],i)=>h+='<td id="t'+i+'"></td>');
 h+='</tr></tfoot></table>';
 document.getElementById('body').innerHTML=h;
 document.querySelectorAll('td.c').forEach(td=>td.onclick=e=>{
   const r=td.dataset.r,f=td.dataset.f,g=state.grid[r]||(state.grid[r]={});
   let i=ORDER.indexOf(g[f]||'N'); i=(i+(e.shiftKey?ORDER.length-1:1))%ORDER.length;
   const v=ORDER[i]; if(v==='N')delete g[f]; else g[f]=v;
   td.className='c '+(v!=='N'?v:''); td.textContent=(v==='N'?'':v); persist();});
 tally();
}
['q','fState'].forEach(id=>document.getElementById(id).oninput=render);
render();
</script></body></html>"""


if __name__ == "__main__":
    main()
