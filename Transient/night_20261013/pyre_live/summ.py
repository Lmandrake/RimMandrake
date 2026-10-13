import json,sys
d=json.load(open(sys.argv[1]))
for t in d['trials']:
    comp=[]
    for x in t['jobs']:
        if not comp or comp[-1][0]!=x: comp.append([x,1])
        else: comp[-1][1]+=1
    print(t['i'],t['kind'],'burrowAt',t['burrowedAt'],'flee',t['firstFlee'],'end',t['burrowedHediffEnd'],' '.join('%s x%d'%(a,b) for a,b in comp))
