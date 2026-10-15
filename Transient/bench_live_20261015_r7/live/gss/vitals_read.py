import json,sys
d=json.load(open(sys.argv[1])); v=d['vitals_events']
print('seq',v.get('seq'),'overflow',v.get('overflow'),'truncated',v.get('truncated'),'hostilesNow',len(d['hostile_pawns']),'tick',v.get('ticksGame'))
for t in v.get('triggers',[]):
  print(' ',t['seq'],t['tick'],t['kind'],t['severity'],t.get('subject'),(t.get('detail') or '')[:110])
