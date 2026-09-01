import sys, collections
sys.path.insert(0, r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
before = {'GravshipHull':914,'HiddenConduit':288,'PowerConduit':274,'VGE_AstrofuelPipe':190,
'VFEFactory_FactoryHopper':28,'GravFieldExtender':9,'LandingPadBeacon':8,'SmallThruster':4,
'VFEFactory_Heatsink':4,'Door':3,'VFE_LargeAdvancedBattery':3,'AncientTunnelerHusk':3,
'AncientChembarrel':2,'OuterRim_AurebeshWordReactor':2,'OuterRim_AurebeshWordLanding':2,
'AncientCratePallet':2,'VFEFactory_Booster':2,'Spaceports_ShuttleLandingPad':2}
with RimBridge(host, port, token) as rb:
    r = rb.call('jawa/list_things', {'group':'BuildingArtificial', 'limit': 6000})
    now = collections.Counter(t['def'] for t in r.get('things', []))
    for k, v in before.items():
        if now.get(k, 0) != v:
            print(f'{k}: was {v} now {now.get(k,0)}')
    # damage with damageDef this time
    for tid, c in [('VGE_AstrofuelPipe64670',(129,153)),('VGE_AstrofuelPipe64678',(129,154)),
                   ('VGE_AstrofuelPipe64828',(153,173)),('VGE_AstrofuelPipe64863',(148,176)),
                   ('VGE_AstrofuelPipe64931',(146,181))]:
        last = None
        for _ in range(6):
            last = rb.call('jawa/damage', {'thingId': tid, 'amount': 999, 'damageDef': 'Cut'})
            if last.get('destroyed') or not last.get('success'): break
        print('kill', c, '->', last.get('success'), 'destroyed:', last.get('destroyed'), last.get('message'))
