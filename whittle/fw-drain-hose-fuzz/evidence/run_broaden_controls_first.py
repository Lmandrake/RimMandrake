"""Additional controls requested by the independent broaden review."""
from pathlib import Path
import json
import subprocess
import sys
import time

here=Path(__file__).resolve().parent
cases=[
 ('original_total_full','original','total',['--fuzz-only','hose'],0),
 ('final_total_full','current','total',['--fuzz-only','hose'],1),
 ('entry_g2','current','production',['--actual-entry','--hose-fuzz','g2','--fuzz-only','hose','--fuzz-scale','0.0001'],0),
 ('entry_g2off','current','production',['--actual-entry','--hose-fuzz','g2off','--fuzz-only','hose','--fuzz-scale','0.0001'],0),
 ('entry_refusal','current','production',['--actual-entry','--hose-fuzz','--fuzz-only','hose','--fuzz-seed','18'],0),
 ('entry_total','current','total',['--actual-entry','--hose-fuzz','--fuzz-only','hose','--fuzz-scale','0.0001'],1),
]
results=[]
for label, version, mutant, args, expected in cases:
    cmd=[sys.executable,str(here/'fast_probe.py'),label,version,mutant,*args]
    console=here/(label+'_console.txt')
    assert not console.exists()
    with console.open('wb') as out:
        p=subprocess.run(cmd,stdout=out,stderr=subprocess.STDOUT,timeout=200)
    receipt=json.loads((here/('fast_'+label)/'receipt.json').read_text())
    result=dict(label=label,returncode=receipt['returncode'],expected=expected,transport_returncode=p.returncode,match=receipt['returncode']==expected and p.returncode==0)
    results.append(result)
    print(json.dumps(result),flush=True)
    (here/'broaden_controls_progress.json').write_text(json.dumps(dict(time=time.time(),results=results),indent=2)+'\n')
    if not result['match']:
        raise SystemExit('Unexpected result preserved. Diagnose before further runs.')
(here/'broaden_controls.json').write_text(json.dumps(dict(time=time.time(),results=results),indent=2)+'\n')
