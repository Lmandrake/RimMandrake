"""Read-only Windows-native versus retained UNC file measurement; no bridge/game calls."""
from pathlib import Path
import json,hashlib,time,xml.etree.ElementTree as ET
u=Path(__file__).resolve().parent.parent
d=json.loads((u/'evidence/raw/live-after9/trunk-doors.json').read_text())
files=[('native-original',Path(d['supplement_saves'][0]['path'])),('retained-UNC',u/'evidence/raw/after9-invalid-observe.rws')]
rows=[]
for label,p in files:
 samples=[]
 for _ in range(3):
  data=p.read_bytes()
  try:ET.fromstring(data);parse='PASS'
  except ET.ParseError as e:parse=str(e)
  samples.append(dict(utc=time.time(),bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),NUL_count=data.count(b'\x00'),parse=parse))
  time.sleep(.25)
 rows.append(dict(label=label,samples=samples))
print(json.dumps(dict(utc=time.time(),reader='Windows python.exe',rows=rows,limit='Current stable retained/original bytes only; cannot identify initial producer/expansion/write stage.'),indent=2))
