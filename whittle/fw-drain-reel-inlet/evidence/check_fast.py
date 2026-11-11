import hashlib,json,re,subprocess,time
from pathlib import Path
here=Path(__file__).resolve().parent;root=here.parents[2]
rows=[]
for label,expected in [('original_retry',(34,14)),('repaired',(34,0)),('expanded',(39,0)),('broaden',(42,1)),('final',(46,1)),('final_correct_fixture',(47,0)),('original_expanded',(43,17)),('unfiltered_mutant',(47,1))]:
 p=here/('fast_'+label);r=json.loads((p/'receipt.json').read_text());out=(p/'stdout.txt').read_text();m=re.search(r'CHECKS (\d+) FAILURES (\d+)',out);assert m and tuple(map(int,m.groups()))==expected,(label,m)
 for path,h in r['staged_sha256'].items():
  assert hashlib.sha256((p/'inputs'/path).read_bytes()).hexdigest()==h
  assert hashlib.sha256((Path(r['stage'])/'inputs'/path).read_bytes()).hexdigest()==h
 rows.append(dict(label=label,checks=expected[0],failures=expected[1],returncode=r['returncode'],receipt_sha256=hashlib.sha256((p/'receipt.json').read_bytes()).hexdigest()))
for name in ['HosePorts.cs','HoseMath.cs']:
 data=subprocess.check_output(['git','show','77e71c52f58a706f41466b6192b4838ba1a40821:src/RimMandrake/FlowWorks/Source/Hose/'+name],cwd=root)
 assert data==(here/('original_'+name)).read_bytes()
r=json.loads((here/'fast_final_correct_fixture/receipt.json').read_text())
for p,h in r['source_sha256'].items():assert hashlib.sha256((root/p).read_bytes()).hexdigest()==h,p
old=(here/'original_HosePorts.cs').read_text();now=(root/'src/RimMandrake/FlowWorks/Source/Hose/HosePorts.cs').read_text()
body=lambda s:s[s.index('        private static Thing RawFindAt('):s.index('        // end RawFindAt')]
assert body(old)==body(now),'free-end method changed'
proof=dict(time=time.time(),rows=rows,originals_match_start_HEAD=True,final_inputs_match_current=True,free_end_RawFindAt_byte_identical=True)
(here/'fast_checks.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof,indent=2))
