import json,sys
d=json.load(open(sys.argv[1]))
for r in d['rows']:
    print(r['id'], r['status'], (r['detail'][:700] if r['status']!='PASS' else ''))
if len(sys.argv)>2:
    last=None
    for l in d.get('moatCaptureTrace',[]):
        l=l.replace('RM_CaptureDown','CD').replace('Human','')
        body=l.split(' ',1)[1] if ' ' in l else l
        if body!=last: print('  ',l)
        last=body
    print('  hits',json.dumps(d.get('moatWardenHits'))[:900])
