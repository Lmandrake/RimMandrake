from pathlib import Path
import subprocess,json,hashlib,time,sys
e=Path(__file__).resolve().parent;root=e.parents[2];rows=[]
for arm,expected in [('before',1),('after',0)]:
 cmd=[sys.executable,str(e/'planner_compare_execute.py'),arm];start=time.time()
 r=subprocess.run(cmd,cwd=root,capture_output=True)
 for ext,data in [('stdout.txt',r.stdout),('stderr.txt',r.stderr),('rc',(str(r.returncode)+'\n').encode())]:
  (e/'raw'/('planner-'+arm+'-replay.'+ext)).write_bytes(data)
 row=dict(command=cmd,rc=r.returncode,expected_rc=expected,elapsed=time.time()-start,
          input_manifest='planner-'+arm+'.receipt.json',
          stdout_sha256=hashlib.sha256(r.stdout).hexdigest(),stderr_sha256=hashlib.sha256(r.stderr).hexdigest())
 (e/'raw'/('planner-'+arm+'-replay.receipt.json')).write_text(json.dumps(row,indent=2)+'\n');rows.append(row)
 assert r.returncode==expected
 assert b'excluded=Pawn accepted=0' in r.stdout and b'excluded=Item accepted=0' in r.stdout and b'excluded=Protected accepted=0' in r.stdout
 assert ('entrance contacts accepted='+('0' if arm=='before' else '2')+' of 2').encode() in r.stdout
print('comparison raw-stream replay PASS')
