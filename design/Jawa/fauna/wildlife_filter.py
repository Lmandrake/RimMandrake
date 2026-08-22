#!/usr/bin/env python3
"""Who is eligible to be WILDLIFE, and how defended is each one.

Owner's ruling, 2026-08-22: "I never meant droids, mechs, vehicles for wildlife... we're
allocating existing animals to biomes, not inventing new animals from scratch. Some
anomaly may be re-used in the bioweapon-related biomes though! That stays."

And on colour: "finding things that are WILDLY differently colored is also biologically
plausible if they can defend themselves with poison or hostility though... or even
biological exuberance. So that's just one criteria."
=> STANDOUT is not a defect to be minimised. It is LICENSED BY DEFENCE. A gaudy creature
   that can hurt you is aposematism; a gaudy defenceless one would have been eaten.
"""
import csv, json, os
FA = os.path.dirname(os.path.abspath(__file__))
D = "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/DefDump"
A = {x['defName']: x for x in json.load(open(D + "/animals.json", encoding='utf-8'))['animals']}

MECH_FLESH = {'Mechanoid', 'MetalVehicle', 'Asimov_Automaton', 'GR_Mechanoid',
              'ABF_FleshType_Synstruct_Base'}
MECH_CLASS = {'Vehicles.VehiclePawn', 'Asimov.Automaton'}

def num(v, d=0.0):
    return float(v) if isinstance(v, (int, float)) else d

def eligibility(dn):
    """-> (eligible: bool, reason: str). 'anomaly' is eligible but restricted."""
    x = A.get(dn)
    if not x: return False, 'not_in_census'
    r = x.get('race') or {}
    # ANOMALY FIRST. These carry isAnimal=False, so testing "is it an animal" before this
    # threw every one of them out as not_an_animal - which is how the owner's "some anomaly
    # may be re-used in the bioweapon-related biomes" would have been silently dropped.
    # NOT `canBecomeShambler` either: that is True on 1,064 of 1,260 and merely means "can be
    # raised as a shambler". Using it classified 1,006 creatures as anomalies.
    if x.get('modName') == 'Anomaly' or num(r.get('anomalyKnowledge')) > 0 \
       or r.get('hasUnnaturalCorpse'):
        return True, 'anomaly'                             # eligible, but ONLY bioweapon biomes
    if x.get('thingClass') in MECH_CLASS: return False, 'vehicle_or_automaton'
    if str(r.get('fleshType')) in MECH_FLESH: return False, 'mechanoid_flesh'
    if not x.get('isAnimal') or str(x.get('intelligence')) != 'Animal':
        return False, 'not_an_animal'                      # droids, humanlikes, faction units
    return True, 'wildlife'

def defence(dn):
    """0..1. How well can this thing look after itself? Licenses bright colouring."""
    x = A.get(dn) or {}
    r = x.get('race') or {}; s = x.get('stats') or {}
    armour = (num(s.get('ArmorRating_Sharp')) + num(s.get('ArmorRating_Blunt'))
              + num(s.get('ArmorRating_Heat'))) / 3.0
    hostile = max(num(r.get('manhunterOnDamageChance')), num(r.get('manhunterOnTameFailChance')))
    bits = [
        min(armour / 0.6, 1.0) * 0.30,
        min(hostile / 0.5, 1.0) * 0.25,
        0.15 if r.get('predator') else 0.0,
        0.10 if r.get('alwaysViolent') else 0.0,
        0.10 if r.get('deathAction') else 0.0,        # explodes / leaves something nasty
        min(num(r.get('baseBodySize')) / 4.0, 1.0) * 0.10,
        min(num(s.get('ToxicResistance')), 1.0) * 0.10,
    ]
    return round(min(sum(bits), 1.0), 3)

def main():
    rows = list(csv.DictReader(open(os.path.join(FA, 'sprite_features.csv'), encoding='utf-8')))
    out = os.path.join(FA, 'wildlife.csv')
    counts = {}
    with open(out, 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(['defName', 'label', 'mod', 'bodySize', 'status', 'eligible', 'reason', 'defence'])
        for r in rows:
            ok, why = eligibility(r['defName'])
            counts[why] = counts.get(why, 0) + 1
            w.writerow([r['defName'], r['label'], r['mod'], r['bodySize'], r['status'],
                        int(ok), why, defence(r['defName'])])
    print(f"wrote {out}")
    for k, v in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"  {v:5}  {k}")

if __name__ == '__main__':
    main()
