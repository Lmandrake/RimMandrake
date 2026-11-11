"""Content identity only; no mtime manipulation, builds or deployment."""
import hashlib,json,subprocess,sys,time
from pathlib import Path
h=Path(__file__).resolve().parent
root=h.parents[2]
sha=lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
paths=subprocess.check_output(['git','ls-files','src/RimMandrake/FlowWorks','src/RimMandrake/GimmeSomeSlack','src/RimMandrake/_Shared','src/RimMandrake/Utils','src/Directory.Build.props','src/Directory.Build.targets'],cwd=root,text=True).splitlines()
paths += [str(p.relative_to(root)) for p in (root/'src/RimMandrake/FlowWorks/Source/SelfTest').glob('HoseShadow*') if str(p.relative_to(root)) not in paths]
manifest={p:sha(root/p) for p in paths if (root/p).is_file()}
assembly=Path('/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/RimWorldWin64_Data/Managed/Assembly-CSharp.dll')
ref=root/'whittle/fw-drain-selftest-resume/evidence/reference/RimWorld/Pawn_NeedsTracker.cs'
provenance=json.loads((root/'whittle/fw-drain-selftest-resume/evidence/reference_provenance.json').read_text())
assert sha(assembly)==provenance['assembly_sha256']
assert sha(ref)==provenance['source_sha256']
stamp=root/'src/RimMandrake/FlowWorks/Assemblies/RimMandrakeFlowWorks.dll.srchash'
rows={}
for row in stamp.read_text().splitlines():
 if not row or row.startswith('#'): continue
 expected,p=row.split(' ',1)
 source=root/'src/RimMandrake/FlowWorks/Source'/p
 rows[p]={'expected':expected,'actual':sha(source)}
assert all(v['expected']==v['actual'] for v in rows.values()),'Shipping inputs differ from stamp'
dll=root/'src/RimMandrake/FlowWorks/Assemblies/RimMandrakeFlowWorks.dll'
assert '# dll: '+sha(dll) in stamp.read_text()
out=dict(time=time.time(),HEAD=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),sha256=manifest,shipping_stamp_rows=rows,shipping_dll_sha256=sha(dll),shipping_stamp_sha256=sha(stamp),installed_assembly=str(assembly),installed_assembly_sha256=sha(assembly),extracted_reference=str(ref),reference_sha256=sha(ref),reference_provenance=provenance)
path=h/('identity_'+sys.argv[1]+'.json')
assert not path.exists()
path.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(dict(manifest_paths=len(manifest),shipping_rows=len(rows),dll=sha(dll),assembly=sha(assembly),path=str(path))))
