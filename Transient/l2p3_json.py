import json,collections,sys
for m in sys.argv[1:]:
    try: d=json.load(open('Transient/l2sweep_%s.json'%m))
    except Exception as e: print(m,"nojson"); continue
    c=collections.Counter(); det=collections.Counter()
    for ch in d.get('chains',[]):
        for k in ch['components']:
            c[k['verdict']]+=1
            if k['verdict']!='PASS': det[(k['verdict'],k['detail'][:170])]+=1
    print("==",m,dict(c),"err",d.get('error'),"refused",str(d.get('refused'))[:100])
    for k,v in det.most_common(4): print("  ",v,k)
