import hashlib,json,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[3]/'src/RimMandrake/Utils'))
import generator_inert_audit as I
from lint_harmony_targets import _fix_dnfile_coded_index_width
import dnfile
_fix_dnfile_coded_index_width(dnfile)
p=Path('/mnt/d/SteamLibrary/steamapps/common/RimWorld/RimWorldWin64_Data/Managed/Assembly-CSharp.dll')
a=I.Asm(str(p)); matches=[]; methods=0; target=None
for row,t in enumerate(a.md.TypeDef,1):
 if str(t.TypeNamespace)== 'RimWorld' and str(t.TypeName)=='JobDefOf':
  for f in t.FieldList:
   if str(f.row.Name)=='CutPlantDesignated': target=0x04000000|f.row_index
assert target is not None
for typename,base,ms,t in a.types():
 for m in ms:
  methods+=1
  for op,tok in I.il_instructions(I.method_body(a.pe,m.Rva)):
   if op==0x7e and tok==target:matches.append(dict(type=typename,method=str(m.Name)))
r=dict(assembly=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),field_token=target,methods_scanned=methods,reads=matches)
Path(__file__).with_name('raw').joinpath('engine-cut-consumers-metadata.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
