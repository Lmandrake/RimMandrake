import json,sys
d=json.load(sys.stdin)
for s in d['surfaces']:
    if 'Dialog' in s['type']:
        print(s['type'])
        for e in s['elements']:
            if e['kind']!='group': print(' ',e['targetId'],e['kind'],e.get('actionable'),repr(e.get('label'))[:60],{k:v for k,v in e.items() if k not in('targetId','kind','source','actionable','depth','screenRect','label','parentTargetId')})
