#!/usr/bin/env python3
"""Extract every '## Lukas' block from conversations/*.md to jsonl (id,date,file,card,text)."""
import re,sys,json,glob,os
root=sys.argv[1] if len(sys.argv)>1 else 'conversations'
out=sys.argv[2] if len(sys.argv)>2 else 'owner_msgs.jsonl'
n=0
with open(out,'w') as o:
  for f in sorted(glob.glob(os.path.join(root,'*.md'))):
    date=os.path.basename(f)[:10]
    parts=re.split(r'^## (Lukas|Claude)\s*$',open(f,encoding='utf-8',errors='replace').read(),flags=re.M)
    for i in range(1,len(parts)-1,2):
      if parts[i]!='Lukas': continue
      t=parts[i+1].strip()
      card=t.startswith('_(card answer)_')
      o.write(json.dumps(dict(id=n,date=date,file=os.path.basename(f),card=card,text=t),ensure_ascii=False)+'\n'); n+=1
print(n)
