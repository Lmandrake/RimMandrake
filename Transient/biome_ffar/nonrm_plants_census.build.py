#!/usr/bin/env python3
"""Builds the proposal table + data for the nonrm_plants_census sheet (PLANT_TIERS_RECONCILE_MOST_ARE_BAROQUE).
Census facts were measured by ET-parsing src/RimUtinni + src/RimStarWars (ParentName chains resolved); verdicts are an
AGENT PROPOSAL, never a ruling. Usage: python3 nonrm_plants_census.build.py  -> writes .proposals.json and .lead.html"""
import json, html, pathlib
H = pathlib.Path(__file__).parent
P = json.load(open(str(H/'nonrm_plants_census.plants.json'))); P = {p['defName']: p for p in P}
U = json.load(open(str(H/'nonrm_plants_census.use.json')))
CANON = {  # defName -> (verdict text, Wookieepedia page)
 'RSW_Plant_Bloddle': 'Bloddle (Tatooine hydroponic vegetable)', 'RSW_Plant_Chakroot_Wild': 'Chak-root (a smuggled substance; plant status thin)',
 'RSW_Plant_HubbaGourd_Wild': 'Hubba gourd (Visual Encyclopedia)', 'RSW_Plant_HydenockTree_Wild': 'Hydenock (Alderaan tree, red dye bark)',
 'RSW_Plant_JoganTree_Wild': 'Jogan tree (Lothal orchards)', 'RSW_Plant_Nysyllin_Wild': 'Nysillin (healing herb crop)',
 'RSW_Plant_TookeTrap_Wild': 'Tooke-trap plant (Naboo carnivorous plant)'}
BASE = {'RSW_Plant_Nysyllin_Wild': 'RM_WildHealroot (healing herb, LeaningScrub) - candidate',
        'RSW_Plant_HubbaGourd_Wild': 'RM_Dewgourd (WeepingStones) - candidate, else new base'}
PLACEHOLDER = ['RSW_JekkaGrass', 'RSW_Thornscrub', 'RSW_QuissaBloom', 'RSW_RuzzoCarpet', 'RSW_TanniVine']
rows = []
for n, p in P.items():
    if 'Raw' in n or n in ('RSW_CactusMeat', 'RSW_MarshFungus'): continue
    folder = p['file'].split('src/')[1].split('/')
    mod = folder[1] if len(folder) > 1 else folder[0]
    biomes = sorted({b for b, _ in U[n]['biomes']}) if n in U else []
    twin = 'RM_' + n.split('_', 1)[1]
    has_twin = n.startswith('RUT_') and n not in ('RUT_BloomCrop', 'RUT_DyingCreep', 'RUT_TwinkleSpikeTestPlant')
    if n in CANON:
        canon, prop = 'GENUINE canon: ' + CANON[n], 'CANON RESKIN'
        base = BASE.get(n, 'new base needed')
    elif has_twin:
        canon, prop, base = 'invented / generic', 'MOVE (done: ' + twin + ' already exists - retire this def)', twin
    elif n == 'RUT_TwinkleSpikeTestPlant':
        canon, prop, base = 'test fixture (not a real plant)', 'KEEP (test fixture)', ''
    elif n.startswith('VCE_'):
        canon, prop, base = 'real-world succulent (donor VE Succulents port)', 'MOVE to Baroque (RM_ rename); needs a Baroque home - no RM biome uses it today', ''
    else:
        canon, prop, base = 'invented / generic', 'MOVE to Baroque (RM_ rename)', ''
    rows.append(dict(defName=n, label=p['label'], mod=mod, file=p['file'], texPath=p['tex'], biomes=biomes, canon=canon,
                     proposal=prop, base=base, placeholder_art=n in PLACEHOLDER))
json.dump(rows, open(H / 'nonrm_plants_census.proposals.json', 'w'), indent=1)
e = html.escape
tr = ''.join(f"<tr><td><b>{e(r['defName'])}</b><br><span class=sub>{e(r['label'] or '')} - {e(r['mod'])}</span></td>"
             f"<td class=sub>{e(r['texPath'] or '')}{' (PLACEHOLDER art, not on this sheet)' if r['placeholder_art'] else ''}</td>"
             f"<td class=sub>{e(', '.join(r['biomes']) or 'no biome row')}</td><td>{e(r['canon'])}</td>"
             f"<td><b>{e(r['proposal'])}</b>{('<br><span class=sub>base: ' + e(r['base']) + '</span>') if r['base'] and r['proposal'].startswith('CANON') else ''}</td></tr>" for r in rows)
lead = ("<p><b>AGENT PROPOSAL, not a ruling.</b> Every plant defined in src/RimUtinni and src/RimStarWars (measured: "
        f"{len(rows)}), with the canon check (Wookieepedia search API) and a suggested home. Your picks go in each row's Belongs/note fields; "
        "nothing here moves a def.</p><table border=1 cellpadding=4 style='border-collapse:collapse;font-size:12px'>"
        "<tr><th>def</th><th>texPath</th><th>biomes using it</th><th>canon?</th><th>proposal</th></tr>" + tr + "</table>")
(H / 'nonrm_plants_census.lead.html').write_text(lead)
from collections import Counter
print(len(rows), Counter(r['proposal'].split(' (')[0].split(';')[0] for r in rows))
