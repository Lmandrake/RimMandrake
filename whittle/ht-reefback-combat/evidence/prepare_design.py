"""Prepare a neutral, source-only brief before choosing a remedy."""
import importlib.util
from pathlib import Path
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parents[3]
here = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('calf_shapes', root/'src/RimMandrake/HugeThings/northstar/measure_reefback_calf.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
chunks = ['''Independent fresh delegated DESIGN judgment. You did not make this work. Tools are disabled.
Decide coherent combat roles for young reefback, open-sea adult reefback, and resident warden mother.
Return KEEP for an explicitly chosen coherent remedy (including spec-only if warranted), or REDO/UNSURE with violated constraints and reasons. Give exact smallest warranted local stat/profile and prose corrections and effective stage values. Do not assume a damage nerf is necessary. The discrepancy is source tension, not an observed combat defect.
Scope: two L0 offline criteria; generic animal combat is the existing observed mechanism. No new mechanism, game/build/deploy, C#/DLL changes, roster removals, art changes, owner questions, or new work items. Preserve young body sizes 6.4/16, its two-stage lifecycle, Miasma weight 0.15, all adults and mothers. No owner approval may be inferred. Existing owner-answer work remains separate.
Frozen hunting MODEL, established before tuning: two modest ranged hunters; each fires one hypothetical sharp projectile of damage 12 and armor penetration 0.15 every 3 seconds, hit probability 0.60. These are explicit illustrative inputs, not claims about a named gun, pawn skill or live shots. Healthy unmodified targets, no apparel/cover, all nominal melee multipliers 1 except installed life stage. Use naked sharp armor, residual r=max(armor-0.15,0), natural-armor expected remaining fraction 1-0.75*r for 0<=r<=1. Calculate landed-hit damage and team expected DPS (4.8 * remaining fraction), and ceil(40 * HealthScale)/DPS as a common body-part damage-budget comparison, NOT kill/downing time. Pinniped core Body base hitPoints40 is installed source; actual damage distributes over parts, with bleed, pain, retaliation, pathing and wounds. Also compare a fixed 30 seconds of shooting and contact/retaliation limits. Decide whether this model supports your proposed nursery wording and how much softer than adult/mother is warranted.
Ask meaningful missed cases and negative controls: inherited tool list append versus replacement, missing local overrides, missing health/stage factors, adult/mother controls, juvenile held indefinitely in its final stage, broken parent lookup, and any other important omission. These will be acted upon as BROADEN. Discuss any incompatibility in constraints explicitly rather than changing owner rulings.
''']
for rel in ['whittle/ht-reefback-combat/evidence/item-before.txt',
            'design/RimMandrake/delegation_policy.md']:
    chunks += ['\nSOURCE '+rel+'\n'+(root/rel).read_text()]
chunks += ['\nSTANDING OWNER CONSTRAINTS (CLAUDE.md / CHARTER): "Let\'s stop evictions right now"; "This is a human review process issue." Agents decide design details inside standing rulings; may not overturn them. No new mechanism means ordinary owner play remains default live validation; L0 does not claim actual hits, populations, art, flight or feel. The nursery prose below is frozen in its rulings; clarification adds detail without weakening its small/parent contrast.']
for rel in ['design/Jawa/worldbuilding/biomes/the_miasma.md',
            'design/Jawa/worldbuilding/biomes/the_grey_deep.md',
            'design/Jawa/worldbuilding/biomes/rosters/the_miasma.json',
            'design/Jawa/worldbuilding/biomes/rosters/the_grey_sea.json']:
    text = (root/rel).read_text()
    if rel.endswith('the_miasma.md'):
        text = '\n'.join(text.splitlines()[96:127])
    elif rel.endswith('the_grey_deep.md'):
        text = '\n'.join(text.splitlines()[95:130])
    elif rel.endswith('.json'):
        import json
        d=json.loads(text)
        text=json.dumps({k:([x for x in v if any(t in json.dumps(x).lower() for t in ['nursery','reefback','warden'])] if isinstance(v,list) else v) for k,v in d.items() if k in ['notes','fauna','new_defs']},indent=2)
    chunks += ['\nSOURCE '+rel+'\n'+text]
chunks += ['\nThe requested the_grey_sea.md does not exist; the current Grey Sea roster references terminator_sea.md and the_grey_deep.md. No missing source is invented.']
game=Path('/mnt/d/SteamLibrary/steamapps/common/RimWorld')
for p, ids in [
    (game/'Data/Core/Defs/Misc/LifeStageDefs/LifeStages.xml', ['AnimalBaby','AnimalJuvenile','AnimalAdult']),
    (game/'Data/Core/Defs/ThingDefs_Races/Races_Animal_Base.xml',['BasePawn','AnimalThingBase','AnimalKindBase']),
    (root/m.SEA,['RM_Reefback','RM_ReefbackJuv']),
    (root/m.MOTHER,['RM_WardenMother','RM_WardenMotherElder']),
    (game/'Data/Core/Defs/Bodies/BodyParts_General.xml',['Body'])]:
    nodes=[n for n in ET.parse(p).getroot() if n.get('Name') in ids or n.findtext('defName') in ids]
    chunks += ['\nEXACT RAW XML '+str(p.relative_to(root) if p.is_relative_to(root) else 'installed/'+p.relative_to(game).as_posix())+'\n'+''.join(ET.tostring(n,encoding='unicode') for n in nodes)]
il=(here/'raw/engine-design2.stdout.txt').read_text()
blocks=il.split('METHOD ')
for b in blocks[1:]:
    if b.startswith(('Verse.Pawn::','Verse.BodyPartDef::','Verse.VerbProperties::GetDamageFactorFor','Verse.ArmorUtility::ApplyArmor','RimWorld.LifeStageDef::')):
        chunks += ['\nINSTALLED REFLECTION-ONLY IL\nMETHOD '+b.split('AVAILABLE XML METHODS')[0]]
(here/'design_prompt.txt').write_text('\n'.join(chunks)+'\n')
