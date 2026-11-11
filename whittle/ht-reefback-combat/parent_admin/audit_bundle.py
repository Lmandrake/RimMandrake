import hashlib,json,re
from pathlib import Path
root=Path(__file__).resolve().parents[3]
work=root/'whittle/ht-reefback-combat'
patterns=[
 ('private_key',re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')),
 ('api_key_shape',re.compile(rb'sk-(?:proj-|ant-)?[A-Za-z0-9_-]{32,}')),
 ('bearer_value',re.compile(rb'(?i)authorization[\"\s:]+bearer[ ]+[A-Za-z0-9._~+/-]{20,}')),
 ('bridge_token_value',re.compile(rb'(?i)(?:bridge[_ -]?token|bridge[_ -]?password)[\"\s:=]+[A-Za-z0-9_-]{24,}')),
]
files=[]; hits=[]
for p in sorted(work.rglob('*')):
 if not p.is_file() or '__pycache__' in p.parts or p.name in ('.stop_state.json','bundle-audit.json'): continue
 data=p.read_bytes()
 for label,rx in patterns:
  if rx.search(data): hits.append({'file':p.relative_to(root).as_posix(),'pattern':label})
 files.append({'file':p.relative_to(root).as_posix(),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
report={'files':len(files),'bytes':sum(r['bytes'] for r in files),'sensitive_pattern_hits':hits,'largest_bytes':max(r['bytes'] for r in files),'manifest':files}
(work/'parent_admin/bundle-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='manifest'}))
assert not hits and report['largest_bytes']<50000000
