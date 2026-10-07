import json,glob,collections,sys
for m in sys.argv[1:]:
    fs=sorted(glob.glob('Transient/modcheck/%s_2*.json'%m))
    if not fs: print(m,'none'); continue
    f=fs[-1]; d=json.load(open(f))['summary']
    c=collections.Counter(); rows=[]
    for ch in d['chains']:
        for comp in ch['components']:
            c[comp['verdict']]+=1
            if comp['verdict']!='PASS': rows.append((ch['name'],comp['name'],comp['verdict'][0],str(comp.get('detail'))[:170]))
    print(m,f.split('/')[-1],dict(c))
    for r in rows: print('   ',r)
