"""Recheck current source/XML against the original snapshots and preserve reviewable evidence."""
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parents[3]
e = Path(__file__).resolve().parent
sys.path.insert(0, str(e))
import prune_corpses as P
E = P.E
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
write = lambda name, data: (e/name).write_text(json.dumps(data, indent=2)+'\n')
base = json.loads((e/'baseline.json').read_text())
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip() == base['git_base_sha']
allowed = set(base['source_snapshots'])
changed = set(subprocess.check_output(['git','diff','--name-only'],cwd=root,text=True).splitlines())
assert changed == allowed, changed
scope = {p: {'before_sha256': old, 'after_sha256': sha(root/p)} for p,old in base['scope_hashes'].items()}
unexpected = [p for p,v in scope.items() if v['before_sha256'] != v['after_sha256'] and p not in allowed]
assert not unexpected, unexpected
write('scope_comparison.json', {'only_tracked_changes': sorted(changed), 'unexpected_protected_changes': unexpected,
                                'protected_files': scope})
for p,h in base['source_snapshots'].items():
    assert sha(e/'before'/Path(p).name) == h
    assert hashlib.sha256(subprocess.check_output(['git','show',base['git_base_sha']+':'+p],cwd=root)).hexdigest() == h
old = ast.parse((e/'before/biome_wildbiomes_evictions.py').read_text())
new = ast.parse((root/'src/RimMandrake/Utils/biome_wildbiomes_evictions.py').read_text())
names = ['is_rostered','shrink_guard','shipped_op_count']
for name in names:
    get = lambda tree: ast.dump(next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name),include_attributes=False)
    assert get(old) == get(new), name
fraction = lambda tree: ast.dump(next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='SHRINK_FRACTION' for t in n.targets)),include_attributes=False)
assert fraction(old)==fraction(new)
xml = root/'src/RimUtinni/UtinniPatches/Patches/BiomeCastEvictions_WildBiomes.xml'
proof = P.compare((e/'before'/xml.name).read_bytes(), xml.read_bytes())
assert b'defName="Corpse_' not in xml.read_bytes()
proof.update(preserved_helper_AST=names, SHRINK_FRACTION_AST_unchanged=True,
             proposed_cleanup_guard=E.shrink_guard(proof['after_operations'],proof['before_operations']),
             proposed_cleanup_explicit_accept=E.shrink_guard(proof['after_operations'],proof['before_operations'],True),
             zero_regeneration_current_shipped_guard=E.shrink_guard(0,E.shipped_op_count()))
assert proof['proposed_cleanup_guard'] and proof['zero_regeneration_current_shipped_guard']
assert proof['proposed_cleanup_explicit_accept'] is None
write('final_structure.json',proof)
write('after_counts.json',{k:v for k,v in proof.items() if k in ('before_operations','after_operations','removed_corpse_operations','after_corpse_operations','after_biomes')})
cmd=[sys.executable,str(e/'prune_corpses.py'),'--before',str(e/'before'/xml.name),'--output',str(e/'reproduced.xml'),'--accept-corpse-only-shrink']
started=time.time(); p=subprocess.run(cmd,cwd=root,capture_output=True)
(e/'reproduce.stdout.txt').write_bytes(p.stdout); (e/'reproduce.stderr.txt').write_bytes(p.stderr)
write('reproduce.receipt.json',{'command':cmd,'started':started,'elapsed_seconds':time.time()-started,'returncode':p.returncode})
assert p.returncode==0 and (e/'reproduced.xml').read_bytes()==xml.read_bytes()
(e/'after').mkdir(exist_ok=True)
for p in sorted(allowed): (e/'after'/Path(p).name).write_bytes((root/p).read_bytes())
(e/'source.diff').write_bytes(subprocess.check_output(['git','diff','--',*sorted(allowed)],cwd=root))
manifest_paths=allowed | {'src/RimMandrake/Utils/selftest_biome_evictions_guard.py','src/RimMandrake/Utils/selftest_wildbiomes_evictions_moved.py','src/RimMandrake/Utils/run_selftests.py'} | {str(p.relative_to(root)) for p in e.glob('*.py')} | set(base['scope_hashes'])
write('final_manifest.json',{'git_base_sha':base['git_base_sha'],'git_HEAD':base['git_base_sha'],
                           'recorded_at':time.time(),'sha256_after_final_edit':{p:sha(root/p) for p in sorted(manifest_paths)}})
print(json.dumps({'operations':proof['after_operations'],'corpse_operations':proof['after_corpse_operations'],
                  'removed':proof['removed_corpse_operations'],'retained_bytes_canonical_order_identical':True,
                  'reproduction_byte_identical':True,'protected_scope_unchanged':not unexpected,
                  'preserved_helper_AST':names,'zero_output_regeneration_refused':True},indent=2))
