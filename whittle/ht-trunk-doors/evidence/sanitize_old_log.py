"""Parent-authorized stopped-process log sanitization, no original full-log copy."""
from pathlib import Path
import hashlib,json,os,re,subprocess,sys
root=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(root/'src/RimMandrake/Utils'))
import game_paths as G
import rimbridge_client as B
out=Path(sys.argv[1])
guard=json.loads(subprocess.check_output([sys.executable,str(root/'src/RimMandrake/rimflow/host_guard.py'),'status','--json']))
assert guard['state']=='HELD' and guard['host']=='stevedesktop' and guard['seat']==os.environ['RIMFLOW_SEAT']
assert str(guard['generation'])==os.environ['RM_HOST_GUARD_GEN'] and str(guard['identity']['pid'])==os.environ['RM_DRIVER_PID']
status=subprocess.run(['bash','/home/mandrake/rm/runner/infrastructure/stevedesktop/rw_game.sh','status'],capture_output=True)
assert status.returncode==3 and b'stopped' in status.stdout
p=Path(G.PLAYER_LOG);stat=p.stat();original=p.read_bytes();lines=original.decode('utf-8',errors='replace').splitlines(keepends=True)
sensitive=re.compile(r'token|authorization|bearer|api[-_]key|password|secret|credential',re.I)
def redact(s):return '[redacted]\n' if sensitive.search(s) or B._TOKEN_RE.search(s) else s
clean=[redact(s) for s in lines];changed=sum(a!=b for a,b in zip(lines,clean))
exceptions=[(i+1,redact(s).rstrip()) for i,s in enumerate(lines) if re.search(r'Exception|Traceback',s)]
configs=[(i+1,redact(s).rstrip()) for i,s in enumerate(lines) if 'Config error' in s]
data=''.join(clean).encode()
assert not B._TOKEN_RE.search(data.decode())
assert not any(sensitive.search(s) for s in data.decode().splitlines())
p.write_bytes(data)
out.write_text(json.dumps(dict(original_sha256=hashlib.sha256(original).hexdigest(),original_size=stat.st_size,
original_mtime_ns=stat.st_mtime_ns,original_line_count=len(lines),redaction_count=changed,
sanitized_sha256=hashlib.sha256(data).hexdigest(),script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
first_exception=exceptions[0] if exceptions else None,config_errors=configs,guard_generation=guard['generation'],
game_status_rc=status.returncode),indent=2)+'\n')
print('sanitized old log; receipt written')
