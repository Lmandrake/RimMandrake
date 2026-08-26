import sys, json, csv, os, collections
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
A=r"D:\Luke\dev\Rimworld\world\_audit"
h,p,t=rc.resolve_endpoint(); b=rc.RimBridge(host=h,port=p,token=t); b.connect()
lm=b.call('jawa/world_landmarks_get',{'limit':30000})['landmarks']
json.dump(lm, open(os.path.join(A,'final_landmarks.json'),'w'))
REG={int(r['tile']):r['region'] for r in csv.DictReader(open(os.path.join(A,'LIVE_tiles.csv'),encoding='utf-8'))}
have=collections.Counter(REG.get(x['tile']) for x in lm)
allreg=set(REG.values())
empty=sorted(r for r in allreg if have.get(r,0)==0)
print("regions with zero landmarks: %d"%len(empty))
print(", ".join(empty) if empty else "  none")
