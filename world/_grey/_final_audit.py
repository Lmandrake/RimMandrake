import sys, json
sys.path.insert(0, r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint
h, p, t = resolve_endpoint()
with RimBridge(h, p, t) as rb:
    a = rb.call('jawa/world_mutators_audit', {
        'marineMutators': 'VEE_RisingWaters,Archipelago,Iceberg,VEE_AlluvialFan',
        'limit': 500, 'histogram': False,
    })
    print(json.dumps({'offenderCount': a.get('offenderCount'), 'offenders': a.get('offenders')}))
    json.dump(a, open(r'D:\Luke\dev\Rimworld\world\_grey\_final_audit.json', 'w'), indent=1)
