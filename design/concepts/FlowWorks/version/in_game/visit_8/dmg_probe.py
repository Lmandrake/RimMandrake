import sys,json
sys.path.insert(0,r'src/RimMandrake/Utils'); sys.path.insert(0,r'src/RimMandrake/Utils/modcheck')
import validation_core as V
B=V.Bridge()
r=B.call('jawa/site_state'); ps=r.get('pawns') or []
print(len(ps), json.dumps(ps[0])[:400] if ps else None)
for pid in sys.argv[1:]:
    print(pid, json.dumps(B.call('jawa/damage_log', thingId=pid, limit=10))[:500])
