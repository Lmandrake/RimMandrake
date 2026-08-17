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

    current = {}
    for fn in sorted(os.listdir(FACDIR)):
        s = open(os.path.join(FACDIR, fn), encoding="utf-8", errors="replace").read()
        for m in re.finditer(r"<FactionDef[^>]*>(.*?)</FactionDef>", s, re.S):
            b = m.group(1)
            dn = re.search(r"<defName>([\w.]+)</defName>", b).group(1)
            xs = re.search(r"<xenotypeSet([^>]*)>(.*?)</xenotypeSet>", b, re.S)
            if not xs:
                continue
            for k, v in re.findall(r"<(\w+)(?:\s+[^>]*)?>([\d.]+)</\1>", xs.group(2)):
                current[k] = (dn, float(v), "Inherit=\"False\"" in xs.group(1))

    rows = []
    for dn, r in sorted(races.items(), key=lambda kv: kv[1]["label"].lower()):
        prop, why, contested = P.get(dn, ("UNASSIGNED", "not yet considered", True))
        cur = current.get(dn)
        rows.append({
            "id": dn, "label": r["label"], "genes": r["genes"], "namer": r["namer"],
            "desc": r["desc"][:200],
            "cur": cur[0] if cur else None, "curChance": cur[1] if cur else None,
            "proposed": prop, "why": why, "contested": contested,
            "moved": bool(cur and cur[0] != prop),
        })

    pre = {"posture": "assignment", "generated": "2026-08-17",
           "meaning": "Each race is assigned to exactly ONE faction, or UNASSIGNED. "
                      "UNASSIGNED means the def stays but no faction fields it, so it "
                      "never occurs organically.",
           "decisions": {r["id"]: r["proposed"] for r in rows},
           "notes": {}}
    if not os.path.exists(PREFILL):
        json.dump(pre, open(PREFILL, "w"), indent=1)

    facmap = {k: (lab, note) for k, lab, note in FACTIONS}
    J = json.dumps
    doc = HTML.replace("__ROWS__", J(rows)).replace("__FACTIONS__", J(FACTIONS)) \
              .replace("__PREFILL__", J(pre)).replace("__INVENTED__", J(INVENTED))
    open(OUT, "w", encoding="utf-8").write(doc)
    print("rows: %d   contested: %d   moved from current: %d   unassigned: %d"
          % (len(rows), sum(r["contested"] for r in rows), sum(r["moved"] for r in rows),
             sum(r["proposed"] == "UNASSIGNED" for r in rows)))
    print("wrote", OUT)


HTML = r"""<!doctype html><html><head><meta charset="utf-8">
<title>Ash'karr - race / faction assignment</title><style>
*{box-sizing:border-box}body{margin:0;background:#12151a;color:#d7dde5;font:13px/1.45 system-ui,sans-serif}
header{position:sticky;top:0;z-index:30;background:#171b22;border-bottom:1px solid #2a323d;padding:10px 14px}
h1{margin:0 0 4px;font-size:16px}.sub{color:#8e9aab;font-size:12px}
.panel{background:#1b2027;border:1px solid #2a323d;border-radius:6px;padding:8px 10px;margin:8px 0}
.panel h3{margin:0 0 4px;font-size:12px;color:#ffcf6b;text-transform:uppercase;letter-spacing:.05em}
.panel li{margin:2px 0;color:#b9c3d0}
.bar{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-top:6px}
input[type=search],select{background:#0e1116;color:#d7dde5;border:1px solid #2f3946;border-radius:4px;padding:4px 6px;font:12px system-ui}
.count{color:#8e9aab;font-size:12px}.count b{color:#8fd48f}
.grp{margin:14px 8px 0}.ghdr{background:#202733;border:1px solid #2f3946;border-radius:6px 6px 0 0;padding:7px 10px;font-weight:600}
.ghdr .n{color:#8e9aab;font-weight:400;margin-left:6px}.ghdr .note{display:block;color:#8e9aab;font-weight:400;font-size:11.5px}
table{width:100%;border-collapse:collapse;background:#161a20}
td{border-top:1px solid #232a34;padding:5px 8px;vertical-align:top}
tr.contested td{background:#1d1a13}tr.moved .lbl:after{content:" moved";color:#ffcf6b;font-size:10.5px}
.lbl{font-weight:600}.id{color:#68758a;font-size:11px;font-family:ui-monospace,monospace}
.eff{color:#9fb0c4;font-size:12px}.why{color:#7f8b9c;font-size:11.5px;font-style:italic}
.cur{font-size:11px;color:#8e9aab;white-space:nowrap}
.note{width:100%;background:#0e1116;color:#e6b96b;border:1px solid #2f3946;border-radius:3px;padding:3px 5px;font:12px system-ui}
.flag{color:#ffcf6b}.link{font-size:11.5px;color:#8fd48f}.warn{color:#ff9b9b}
button{background:#243040;color:#d7dde5;border:1px solid #354458;border-radius:4px;padding:4px 9px;cursor:pointer;font:12px system-ui}
button:hover{background:#2d3b4e}
</style></head><body>
<header>
<h1>Ash'karr the Sundered — race / faction assignment</h1>
<div class="sub">Every RimMandrake xenotype gets <b>exactly one</b> faction, or <b>(no faction)</b>. Pre-filled with my guesses — <b>you only need to disagree.</b> Saves as you type.</div>
<div class="bar">
<input type="search" id="q" placeholder="search race, effect or reason…" size="34">
<select id="fFac"><option value="">all factions</option></select>
<select id="fState"><option value="">all rows</option><option value="contested">contested only</option><option value="moved">moved from current</option><option value="orphan">currently orphaned</option><option value="unassigned">proposed (no faction)</option><option value="touched">I changed these</option></select>
<button id="link">link to file…</button><button id="exp">export JSON</button>
<span class="count" id="cnt"></span><span class="link" id="ls"></span>
</div>
<div class="panel"><h3>Posture</h3><div class="sub" id="posture"></div></div>
<div class="panel"><h3>⚠ Rules I invented — overrule these first</h3><ul id="inv"></ul></div>
</header>
<div id="body"></div>
<script>
const ROWS=__ROWS__, FACTIONS=__FACTIONS__, PREFILL=__PREFILL__, INVENTED=__INVENTED__;
const FMAP={}; FACTIONS.forEach(([k,l,n])=>FMAP[k]=[l,n]);
let state=JSON.parse(localStorage.getItem('ashkarr_races')||'null')||{decisions:{},notes:{}};
let filled=0,kept=0;
ROWS.forEach(r=>{ if(state.decisions[r.id]===undefined){state.decisions[r.id]=r.proposed;filled++;} else kept++; });
document.getElementById('posture').innerHTML=PREFILL.meaning+
 " &nbsp;·&nbsp; Filled <b>"+filled+"</b> rows from the pre-fill; kept <b>"+kept+"</b> decisions you had already made.";
INVENTED.forEach(t=>{const li=document.createElement('li');li.textContent=t;document.getElementById('inv').appendChild(li);});
FACTIONS.forEach(([k,l])=>{const o=document.createElement('option');o.value=k;o.textContent=l;document.getElementById('fFac').appendChild(o);});

let handle=null,lastWrite='';
const DB=()=>new Promise(res=>{const r=indexedDB.open('ashkarr',1);r.onupgradeneeded=e=>e.target.result.createObjectStore('h');r.onsuccess=e=>res(e.target.result);});
async function saveHandle(h){const db=await DB();db.transaction('h','readwrite').objectStore('h').put(h,'races');}
async function loadHandle(){const db=await DB();return new Promise(res=>{const q=db.transaction('h').objectStore('h').get('races');q.onsuccess=()=>res(q.result||null);q.onerror=()=>res(null);});}
function payload(){
  const d=Object.assign({},PREFILL);
  d.decisions=state.decisions; d.notes=state.notes;
  d.decidedCount=Object.keys(state.decisions).length;
  return JSON.stringify(d,null,1);
}
let t=null;
function persist(){
  localStorage.setItem('ashkarr_races',JSON.stringify(state));
  clearTimeout(t); t=setTimeout(write,900);
  render(true);
}
async function write(){
  if(!handle) return;
  const decided=Object.keys(state.decisions).length;
  if(decided < ROWS.length*0.5){ document.getElementById('ls').innerHTML='<span class="warn">REFUSED to write: only '+decided+' rows in memory</span>'; return; }
  try{ const w=await handle.createWritable(); await w.write(payload()); await w.close();
    lastWrite=new Date().toLocaleTimeString();
    document.getElementById('ls').textContent='saved to file '+lastWrite;
  }catch(e){ document.getElementById('ls').innerHTML='<span class="warn">write failed — click “link to file…”</span>'; }
}
document.getElementById('link').onclick=async()=>{
  if(!window.showSaveFilePicker){document.getElementById('ls').innerHTML='<span class="warn">this browser has no File System Access API — use export</span>';return;}
  handle=await window.showSaveFilePicker({suggestedName:'race_faction_assignment.prefill.json',types:[{description:'JSON',accept:{'application/json':['.json']}}]});
  await saveHandle(handle); write();
};
document.getElementById('exp').onclick=()=>{navigator.clipboard.writeText(payload());document.getElementById('ls').textContent='JSON copied to clipboard';};
loadHandle().then(h=>{if(h){handle=h;document.getElementById('ls').textContent='file link restored — edit once to write';}});

function render(countOnly){
  const q=document.getElementById('q').value.toLowerCase();
  const ff=document.getElementById('fFac').value, fs=document.getElementById('fState').value;
  const vis=ROWS.filter(r=>{
    const cur=state.decisions[r.id];
    if(q && !(r.label+' '+r.id+' '+r.desc+' '+r.why).toLowerCase().includes(q)) return false;
    if(ff && cur!==ff) return false;
    if(fs==='contested'&&!r.contested) return false;
    if(fs==='moved'&&!r.moved) return false;
    if(fs==='orphan'&&r.cur) return false;
    if(fs==='unassigned'&&cur!=='UNASSIGNED') return false;
    if(fs==='touched'&&cur===r.proposed) return false;
    return true;
  });
  const un=ROWS.filter(r=>state.decisions[r.id]==='UNASSIGNED').length;
  document.getElementById('cnt').innerHTML='showing <b>'+vis.length+'</b> of '+ROWS.length+
    ' · fielded <b>'+(ROWS.length-un)+'</b> · no faction <b>'+un+'</b>'+(lastWrite?'':' · <span class="warn">not linked to a file yet</span>');
  if(countOnly) return;
  const by={}; vis.forEach(r=>{(by[state.decisions[r.id]]=by[state.decisions[r.id]]||[]).push(r);});
  const out=[];
  FACTIONS.forEach(([k,l,n])=>{
    const g=by[k]; if(!g) return;
    const sticky=g.length>3?'position:sticky;top:0;':'';
    out.push('<div class="grp"><div class="ghdr" style="'+sticky+'">'+l+'<span class="n">'+g.length+' race'+(g.length===1?'':'s')+'</span><span class="note">'+n+'</span></div><table>');
    g.forEach(r=>{
      const cls=(r.contested?'contested ':'')+(state.decisions[r.id]!==r.cur&&r.cur?'moved':'');
      const opts=FACTIONS.map(([fk,fl])=>'<option value="'+fk+'"'+(state.decisions[r.id]===fk?' selected':'')+'>'+fl+'</option>').join('');
      out.push('<tr class="'+cls+'"><td style="width:210px"><div class="lbl">'+(r.contested?'<span class="flag">◆ </span>':'')+r.label+'</div><div class="id">'+r.id+'</div></td>'+
        '<td><div class="eff">'+r.genes+' genes'+(r.namer?' · own name-maker':' · vanilla names')+' — '+(r.desc||'no description')+'</div><div class="why">'+r.why+'</div></td>'+
        '<td class="cur" style="width:150px">'+(r.cur?FMAP[r.cur][0]+'<br>at '+r.curChance:'<span class="flag">orphaned</span>')+'</td>'+
        '<td style="width:190px"><select data-id="'+r.id+'">'+opts+'</select></td>'+
        '<td style="width:230px"><input class="note" data-id="'+r.id+'" placeholder="your note…" value="'+(state.notes[r.id]||'').replace(/"/g,'&quot;')+'"></td></tr>');
    });
    out.push('</table></div>');
  });
  document.getElementById('body').innerHTML=out.join('');
  document.querySelectorAll('select[data-id]').forEach(s=>s.onchange=e=>{state.decisions[e.target.dataset.id]=e.target.value;persist();render();});
  document.querySelectorAll('input.note').forEach(i=>i.oninput=e=>{state.notes[e.target.dataset.id]=e.target.value;persist();});
}
['q','fFac','fState'].forEach(id=>document.getElementById(id).oninput=()=>render());
render();
</script></body></html>"""


if __name__ == "__main__":
    main()
