"""Read-only scoped artifact, source-stamp and intended-tier inventory; no log copying."""
import hashlib,json,os,re,sys,xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
E=Path(os.environ.get('HT_PASSAGE_EVIDENCE',str(Path(__file__).resolve().parent)))
sys.path.insert(0,str(ROOT/'src/RimMandrake/Utils'))
import game_paths as G

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None

def pair(mod,filename):
    repo=ROOT/'src/RimMandrake'/mod/'Assemblies'/filename
    deployed=Path(G.LOCAL_MODS)/mod/'Assemblies'/filename
    return {name:dict(repo=str(r),deployed=str(d),repo_sha256=digest(r),deployed_sha256=digest(d),equal=digest(r) is not None and digest(r)==digest(d))
            for name,r,d in [('dll',repo,deployed),('stamp',Path(str(repo)+'.srchash'),Path(str(deployed)+'.srchash'))]}

rec={'HugeThings':pair('HugeThings','RM_HugeThings.dll'),'FlowWorks':pair('FlowWorks','RimMandrakeFlowWorks.dll')}
mod=ROOT/'src/RimMandrake/HugeThings'
stamp=(mod/'Assemblies/RM_HugeThings.dll.srchash').read_text()
rec['compiled_inputs']=[]
for sha,relative in re.findall(r'^([0-9a-f]{64}) (.+)$',stamp,re.M):
    f=mod/'Source'/relative.strip()
    rec['compiled_inputs'].append(dict(source=str(f.resolve()),expected=sha,actual=digest(f),equal=digest(f)==sha))
rec['stamp_declared_dll']=re.search(r'^# dll: (\w+)',stamp,re.M)[1]
rec['stamp_declared_matches_dll']=rec['stamp_declared_dll']==rec['HugeThings']['dll']['repo_sha256']
rec['HugeThings_xml']=[]
for f in sorted(mod.rglob('*.xml')):
    if any(x in f.parts for x in ('bin','obj','Source')): continue
    relative=f.relative_to(mod);d=Path(G.LOCAL_MODS)/'HugeThings'/relative
    rec['HugeThings_xml'].append(dict(relative=str(relative),repo_sha256=digest(f),deployed_sha256=digest(d),equal=digest(f)==digest(d)))
rec['ModsConfig']={'path':G.MODS_CONFIG,'sha256':digest(Path(G.MODS_CONFIG)),
                   'ordered':[x.text for x in ET.parse(G.MODS_CONFIG).find('activeMods')]}
rec['five_dlc_present']=all('ludeon.rimworld.'+x in rec['ModsConfig']['ordered'] for x in ('royalty','ideology','biotech','anomaly','odyssey'))
b=ROOT/'src/RimMandrake/Stillsand/Defs/BiomeDefs/RM_Stillsand_Biome.xml'
r=ET.parse(b).getroot();biome=r.find('BiomeDef')
rec['Stillsand_source_only']={'path':str(b),'sha256':digest(b),'defName':biome.findtext('defName'),
    'wildAnimals':{x.tag:x.text for x in biome.find('wildAnimals')},
    'passage_extensions':[ET.tostring(x,encoding='unicode') for x in biome.findall('modExtensions/li') if 'TitanPassage' in x.get('Class','')],
    'warning':'source only; not a resolved live roster and not proof of saved biome'}
rec['historical_named_kinds_in_intended_deployed_xml']={}
names=['RM_Reefback','RM_ReefbackJuv','RM_Lanternwhale','RSW_Reefback','RSW_Lanternwhale','RSW_ShadeWhale','RSW_SandoAquaMonster','RM_GrippingTerror','RM_Titanoslime']
# Inspect only the mandrake mods named by this intended tier, source-def XML only.
active=set(rec['ModsConfig']['ordered'])
for folder in sorted(Path(G.LOCAL_MODS).iterdir()):
    about=folder/'About/About.xml'
    if not about.is_file():continue
    try:pid=ET.parse(about).getroot().findtext('packageId','').lower()
    except ET.ParseError:continue
    if pid not in active or not pid.startswith('mandrake.'):continue
    for f in (folder/'Defs').rglob('*.xml'):
        try:root=ET.parse(f).getroot()
        except ET.ParseError:continue
        for kind in root.findall('PawnKindDef'):
            name=kind.findtext('defName')
            if name in names:rec['historical_named_kinds_in_intended_deployed_xml'].setdefault(name,[]).append(str(f))
rec['historical_named_kinds_absent_from_intended_deployed_xml']=[n for n in names if n not in rec['historical_named_kinds_in_intended_deployed_xml']]
rec['historical_kind_limit']='Static active custom Defs XML only. No loaded DefDatabase or live absence claim; patched/donor definitions not asserted absent.'
(E/'artifact-inventory.json').write_text(json.dumps(rec,indent=2)+'\n')
snap=E/'source';snap.mkdir(exist_ok=True)
for relative in ['Source/Titanic/Events/TitanPassage.cs','Source/Titanic/Events/TitanValidationHooks.cs','Source/Titanic/Events/RM_TitanPassageExtension.cs','Source/Kernel/RM_TitanicKernel.cs','Source/SelfTest/TitanicFuzz.cs','Defs/IncidentDefs/RM_TitanPassage.xml','Assemblies/RM_HugeThings.dll.srchash']:
    f=mod/relative;(snap/f.name).write_bytes(f.read_bytes())
(snap/b.name).write_bytes(b.read_bytes())
print(json.dumps({'HugeThings_pair_match':all(x['equal'] for x in rec['HugeThings'].values()),
    'FlowWorks_pair_match':all(x['equal'] for x in rec['FlowWorks'].values()),
    'compiled_inputs':len(rec['compiled_inputs']),'compiled_match':all(x['equal'] for x in rec['compiled_inputs']),
    'xml_match':all(x['equal'] for x in rec['HugeThings_xml']),'five_DLC':rec['five_dlc_present'],
    'absent_historical_kinds_static_only':rec['historical_named_kinds_absent_from_intended_deployed_xml']}))
