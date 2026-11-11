"""Run item-scoped controls once each, preserving expected negatives and failures."""
from pathlib import Path
import json
import subprocess
import sys
import time

here = Path(__file__).resolve().parent
cases = [
    ('repaired_total', 'current', 'total', ['--fuzz-only','hose','--fuzz-scale','0.0001'], 1),
    ('positive_tiny', 'current', 'production', ['--fuzz-only','hose','--fuzz-scale','0.0001'], 0),
    ('positive_g2off', 'current', 'production', ['g2off','--fuzz-only','hose','--fuzz-scale','0.0001'], 0),
    ('positive_g2', 'current', 'production', ['g2','--fuzz-only','hose','--fuzz-scale','0.0001'], 0),
    ('refuse_outlet', 'current', 'outlet', ['--fuzz-only','hose','--fuzz-scale','0.0001'], 1),
    ('refuse_free', 'current', 'free', ['--fuzz-only','hose','--fuzz-scale','0.0001'], 1),
    ('debug_refusal', 'current', 'production', ['--fuzz-only','hose','--fuzz-seed','18'], 0),
    ('debug_partial_refusal', 'current', 'production', ['--fuzz-only','hose','--fuzz-seed','7'], 0),
    ('debug_positive', 'current', 'production', ['--fuzz-only','hose','--fuzz-seed','2'], 0),
    ('debug_mutant', 'current', 'total', ['--fuzz-only','hose','--fuzz-seed','2'], 0),
    ('disabled', 'current', 'total', ['--fuzz-only','hose','--fuzz-scale','0'], 0),
    ('trail_only', 'current', 'total', ['--fuzz-only','trail','--fuzz-scale','0.0001'], 0),
    ('both_families', 'current', 'production', ['--fuzz-scale','0.0001'], 0),
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
    (here/'fast_matrix_progress.json').write_text(json.dumps(dict(time=time.time(),results=results),indent=2)+'\n')
    if not result['match']:
        raise SystemExit('Unexpected result preserved. Diagnose before further runs.')
(here/'fast_matrix.json').write_text(json.dumps(dict(time=time.time(),results=results),indent=2)+'\n')
