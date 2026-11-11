from pathlib import Path
import sys,json,hashlib
root=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(root/'src/RimMandrake/Utils'))
import generator_inert_audit as I
from lint_harmony_targets import _fix_dnfile_coded_index_width
import dnfile
_fix_dnfile_coded_index_width(dnfile)
p=Path('/mnt/d/SteamLibrary/steamapps/common/RimWorld/RimWorldWin64_Data/Managed/Assembly-CSharp.dll')
a=I.Asm(str(p));rows=[]
for typename,base,methods,t in a.types():
 if typename!='RimWorld.GravshipPlacementUtility':continue
 for m in methods:
  if str(m.Name) not in ('ClearArea','ClearThingsAt'):continue
  rows.append(dict(type=typename,method=str(m.Name),signature=bytes(m.Signature.value).hex(),
   parameters=[dict(sequence=x.row.Sequence,name=str(x.row.Name)) for x in m.ParamList],
   il=[dict(op=hex(op),token=hex(tok) if tok is not None else None,name=a.token_name(tok) if tok is not None else None)
       for op,tok in I.il_instructions(I.method_body(a.pe,m.Rva))]))
r=dict(assembly_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),methods=rows)
Path(__file__).with_name('raw').joinpath('engine-gravship-metadata.json').write_text(json.dumps(r,indent=2)+'\n')
print('bounded methods',len(rows))
