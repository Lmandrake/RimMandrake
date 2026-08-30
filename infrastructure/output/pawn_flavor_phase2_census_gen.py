# Frozen methodology record for infrastructure/output/pawn_flavor_phase2_census.csv
# (PAWN_FLAVOR_PHASE2_PROSE_1). Kept for provenance of the COMMON/OCCASIONAL/
# DORMANT tiering logic (per-mod live/dormant lists, keyword tiers, hand-
# classified MentalBreakDef/XenotypeDef sets) - NOT directly re-runnable as-is:
# `dump.pkl` and `salvation_defs.txt` were session scratch paths that no longer
# exist. Re-deriving the census means rebuilding those two inputs (a live def
# dump + the colony's own ideoligion export) and pointing the paths below at them.
import sys, csv, json, re
sys.path.insert(0, 'src/RimMandrake/Utils')
import pickle

with open('/tmp/claude-1000/-mnt-d-Luke-dev-Rimworld/cfb7ccb8-8423-4984-85ab-c1a10f377e71/scratchpad/dump.pkl','rb') as f:
    ds = pickle.load(f)

salvation = set(l.strip() for l in open('/tmp/claude-1000/-mnt-d-Luke-dev-Rimworld/cfb7ccb8-8423-4984-85ab-c1a10f377e71/scratchpad/salvation_defs.txt') if l.strip())

DLC_LIVE = {'Core','Biotech','Ideology','Odyssey'}
DLC_DORMANT = {'Royalty','Anomaly'}
OURS = {'Jawa Ikee','RimMandrake - Star Wars Races','Jawa Patches (local)','Jawa Patches'}

THIRD_LIVE = {
 'Vanilla Traits Expanded','ISEKAI RPG LEVELING','Star Wars KotOR Resources and Materials',
 'Vanilla Factions Expanded - Pirates','Star Wars Animal Collection (Continued)',
 'Vanilla Gravship Expanded - Chapter 1','Vanilla Races Expanded - Saurid',
 'ABF: Synstructs Core','Alpha Genes','Integrated Genes','Vanilla Genetics Expanded',
 'More Slavery Stuff','Torture Pod','Prison Labor','Simple Slavery Collars',
 'Alpha Biomes','Alpha Animals','Biomes! Caverns','Biomes! Core','Biomes! Polluted Lands',
 'Biomes! Fossils','Mythic Ages: Megafauna Bestiary','EBSG Framework','Romance On The Rim',
 'Way Better Romance','Vanilla Vehicles Expanded','Custom Gas Types','Breeding Ritual',
 'Caravan Adventures','Stealing Mod','Tabula Rasa','Graffiti Mod (Continued)','Snap Out!',
 'Vanilla Factions Expanded - Tribals','Vanilla Ideology Expanded - Memes and Structures',
 'Alpha Memes','Humanoid Alien Races','Big and Small - Genes & More','Precepts and Memes (Continued)',
 'Outer Rim - Droid Depot',
}
THIRD_COMMON = {'Prisoner Realism','Vanilla Cooking Expanded','Vanilla Brewing Expanded'}

COMMON_KW = ['ate ','meal','food','hungry','slept','sleep','bed','weather','rain','hot ','cold ',
 'heat','temperature','talked','chatted','insulted','argu','fight','marri','broke up','breakup',
 'lover','friend','roommate','naked','dirty','filth','clean','work','beauty','ugly','room','wall',
 'dark','light','pain','hurt','wound','injur','scar','sick','disease','plague','died','death',
 'corpse','grave','burial','prisoner','guest','trade','caravan','animal','pet','bond','drug',
 'addict','alcohol','drunk','social','recreation','bored','idle','inspired','crowded','privacy']
RARE_KW = ['xenogerm','sanguophage','hemogen','royal','throne','permit','honor','title','psycast',
 'deathrest','mechanitor','gladiator','duel','gene bank','archite','shuttle','quest','apocriton',
 'void','noctolith']

def get_text(e):
    parts = []
    for tag in ('label','description'):
        v = e.findtext(tag)
        if v: parts.append(v)
    for st in e.findall('.//stages/li'):
        for tag in ('label','description'):
            v = st.findtext(tag)
            if v: parts.append(v)
    return ' | '.join(p.strip() for p in parts if p and p.strip())

def clip(s, n=180):
    s = re.sub(r'\s+',' ',s).strip()
    return s[:n] + ('...' if len(s) > n else '')

rows = []  # defType, defName, modName, text, tier, why
dormant_counts = {}
dormant_examples = {}

def record_dormant(t, modname, defname):
    dormant_counts[t] = dormant_counts.get(t,0)+1
    dormant_examples.setdefault(t, []).append((modname, defname))

recs_by_type = {}
for r in ds.records:
    if r.isAbstract: continue
    recs_by_type.setdefault(r.defType, []).append(r)

# ---------- ThoughtDef ----------
tier_counts = {'ThoughtDef':{'COMMON':0,'OCCASIONAL':0,'DORMANT':0},
               'MentalBreakDef':{'COMMON':0,'OCCASIONAL':0,'DORMANT':0},
               'XenotypeDef':{'COMMON':0,'OCCASIONAL':0,'DORMANT':0}}

for r in recs_by_type.get('ThoughtDef', []):
    mod = r.modName
    text = get_text(r.element)
    textl = text.lower()
    if mod in OURS:
        tier='COMMON'; why='First-party Jawa/RimMandrake def — always live.'
    elif r.defName in salvation:
        tier='COMMON'; why="Confirmed: this defName appears in the colony's own ideoligion export (The Salvation.rid) — an active precept/ritual/role in the current game, not inferred."
    elif mod in DLC_DORMANT:
        tier='DORMANT'; why=''
    elif mod in DLC_LIVE:
        if any(k in textl for k in RARE_KW):
            tier='OCCASIONAL'; why=f'{mod} DLC is live, but text matches a rare/gated keyword — quest, royal, psycast, gene-lab or similar special trigger.'
        elif any(k in textl for k in COMMON_KW):
            tier='COMMON'; why=f'{mod} DLC is live; text matches a routine mood-trigger keyword (food/sleep/social/environment/health) — reachable through ordinary colony play.'
        else:
            tier='OCCASIONAL'; why=f'{mod} DLC is live but this thought has no routine-trigger keyword match — likely precept-specific, ritual-specific, or otherwise gated; not individually verified against the 12 ideoligions.'
    elif mod in THIRD_COMMON:
        tier='COMMON'; why=f'{mod} is a confirmed-live behavioral backbone mod for this campaign (design doc: required_mods.md, ADOPTED) — its core thoughts fire in routine play.'
    elif mod in THIRD_LIVE:
        tier='OCCASIONAL'; why=f'{mod} is confirmed live for this campaign (design/canon evidence — see report), but this specific thought/stance is not individually verified as the chosen variant for any of the 12 ideoligions/factions.'
    else:
        tier='DORMANT'; why=''

    if tier=='DORMANT':
        record_dormant('ThoughtDef', mod, r.defName)
    else:
        rows.append(('ThoughtDef', r.defName, mod, clip(text) or r.defName, tier, why))
    tier_counts['ThoughtDef'][tier]+=1

# ---------- MentalBreakDef (hand-classified) ----------
MBD_COMMON = {'BedroomTantrum','Berserk','Binging_DrugExtreme','Binging_DrugMajor','Binging_Food',
 'Catatonic','CorpseObsession','GiveUpExit','InsultingSpree','Jailbreaker','MurderousRage','RunWild',
 'SadisticRage','Slaughterer','Tantrum','TargetedInsultingSpree','TargetedTantrum','Wander_OwnRoom',
 'Wander_Psychotic','Wander_Sad','FireTerror','Rebellion'}
MBD_OCC = {'FireStartingSpree':'Requires the Pyromaniac trait — common trait, but not every pawn has it.',
 'IdeoChange':'Fires only when a pawn\'s ideoligion is actively being converted — happens with captives/converts, not routine.',
 'VTE_Kleptomaniac':'Vanilla Traits Expanded is a confirmed live trait-pool mod; this break needs the matching VTE trait.',
 'VTE_PanicFreezing':'Requires the VTE_Anxious trait specifically.',
 'VTE_TechnophobeTantrum':'Requires a VTE technophobe-type trait.',
 'ABF_MentalBreak_Synstruct_FriendlyGrassObsession':'ABF: Synstructs is the confirmed droid/synthetic pawn framework; fires only for synstruct (droid) pawns.',
 'ABF_MentalBreak_Synstruct_HostileGrassObsession':'ABF: Synstructs is the confirmed droid/synthetic pawn framework; fires only for synstruct (droid) pawns.',
 'OuterRim_MSLooseScrews':'Outer Rim - Droid Depot is adopted (required_mods.md); requires the OuterRim_LooseScrews droid quirk trait.',
 'OuterRim_MSRebellious':'Outer Rim - Droid Depot is adopted; requires the OuterRim_Rebellious droid quirk trait.',
 'Turn_MentalBreak_FreeSpiritRampage':'Integrated Genes is weakly evidenced as live (genome_register.html review); worker is slave/prisoner-specific, fits the campaign\'s slave economy — inference, not directly confirmed.',
 'Turn_MentalBreak_TerrifiedFaintingSpell':'Integrated Genes is weakly evidenced as live; not individually confirmed.'}

for r in recs_by_type.get('MentalBreakDef', []):
    e = r.element
    ms = e.findtext('mentalState') or ''
    text = f"mentalState={ms}"
    if r.defName in MBD_COMMON:
        tier='COMMON'
        if r.defName in ('FireTerror',):
            why='Biotech base mechanic — any pawn panics and flees from a nearby fire; fires happen routinely in colony life.'
        elif r.defName == 'Rebellion':
            why="Vanilla Ideology slave-rebellion mental break — explicitly hooked by this campaign's Unbending/Broken rebellion-walk design (pawn_flavor_design.md), core to the permanent slave economy."
        else:
            why='Core vanilla mental break — reachable by any pawn via the base mood-threshold system, no faction/precept/xenotype gate.'
    elif r.defName in MBD_OCC:
        tier='OCCASIONAL'; why=MBD_OCC[r.defName]
    else:
        tier='DORMANT'; why=''
    if tier=='DORMANT':
        record_dormant('MentalBreakDef', r.modName, r.defName)
    else:
        rows.append(('MentalBreakDef', r.defName, r.modName, text, tier, why))
    tier_counts['MentalBreakDef'][tier]+=1

# ---------- XenotypeDef ----------
XENO_COMMON_MODS = {'RimMandrake - Star Wars Races'} | OURS
XENO_COMMON_NAMES = {'Baseliner'}
XENO_OCC_NAMES = {'Dirtmole','Genie','Highmate','Hussar','Impid','Neanderthal','Pigskin','Sanguophage',
 'Waster','Yttakin','Starjack','guy762_debugxenotype_droid','VRESaurids_Saurid'}
XENO_OCC_WHY = {
 'Sanguophage':'Biotech DLC main-story xenotype; rare and quest/event-gated (Sanguophage bloodline), not a faction default.',
 'Starjack':"Odyssey DLC xenotype (space nomads); Odyssey/gravship is live this campaign, but Starjack is not one of the 12 factions' species.",
 'guy762_debugxenotype_droid':'Star Wars KotOR Resources droid xenotype — droid pawns are a live, major design pillar (Free Droid Enclaves, Junker warcaskets) but this specific debug/utility xenotype is a narrow case.',
 'VRESaurids_TownGuard_Saurid':'confirmed',
 'VRESaurids_Saurid':"Confirmed live: VRESaurids_TownGuard_Saurid is an actual consumer pawnkind present in the frozen WORLDMAP_V1_original.rws save (pawn_flavor_design.md CUT PASS notes) — this species is reachable, just not part of the primary 71-species roster.",
}
for name in ('Dirtmole','Genie','Highmate','Hussar','Impid','Neanderthal','Pigskin','Waster','Yttakin'):
    XENO_OCC_WHY[name] = 'Biotech default xenotype; not part of the 71-species Star Wars roster (canon.yml species.ours_on_disk) but remains a possible random-pawn-generation fallback where no faction-specific species is forced.'

for r in recs_by_type.get('XenotypeDef', []):
    lbl = r.element.findtext('label') or r.defName
    desc = r.element.findtext('description') or ''
    text = clip(f"{lbl} — {desc}")
    if r.modName in XENO_COMMON_MODS:
        tier='COMMON'; why="Part of the campaign's shipped 71-species Star Wars roster (canon.yml species.ours_on_disk=71; RimMandrake - Star Wars Races 70 + Jawa_Xeno_Gamorrean 1) — the actual playable/spawnable species set."
    elif r.defName in XENO_COMMON_NAMES:
        tier='COMMON'; why='Biotech default "no genes" xenotype — the fallback for any human pawn without a forced species/gene set; always reachable.'
    elif r.defName in XENO_OCC_NAMES:
        tier='OCCASIONAL'; why=XENO_OCC_WHY.get(r.defName,'Live DLC/mod, narrow trigger.')
    else:
        tier='DORMANT'; why=''
    if tier=='DORMANT':
        record_dormant('XenotypeDef', r.modName, r.defName)
    else:
        rows.append(('XenotypeDef', r.defName, r.modName, text, tier, why))
    tier_counts['XenotypeDef'][tier]+=1

# ---------- write CSV ----------
out_csv = 'infrastructure/output/pawn_flavor_phase2_census.csv'
with open(out_csv, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['defType','defName','modName','currentLabelOrText','tier','oneLineWhy'])
    for row in sorted(rows, key=lambda x: (x[0], x[4], x[2], x[1])):
        w.writerow(row)

print('rows written', len(rows))
print(json.dumps(tier_counts, indent=2))

# dormant examples (5-10 per type)
summary = {'tier_counts': tier_counts, 'dormant_counts': dormant_counts, 'dormant_examples': {}}
import random
random.seed(42)
for t, examples in dormant_examples.items():
    mods_seen = {}
    picked = []
    for mod, dn in examples:
        if mod not in mods_seen:
            mods_seen[mod] = 0
        if mods_seen[mod] < 1 and len(picked) < 10:
            picked.append((mod, dn))
            mods_seen[mod]+=1
    summary['dormant_examples'][t] = picked

with open('infrastructure/output/.tmp_census_summary.json','w') as f:
    json.dump(summary, f, indent=2)
print('done')
