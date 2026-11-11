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
target=a.md.MethodSpec[0x392-1].Method.row
for ty,base,methods,t in a.types():
 for m in methods:
  if m is not target:continue
  il=[]
  for index,(op,tok) in enumerate(I.il_instructions(I.method_body(a.pe,m.Rva))):
   row=dict(index=index,op=hex(op),token=hex(tok) if tok is not None else None)
   if tok is not None and op in (0x28,0x6f,0x7b,0x7c,0x7d,0x7e,0x80,0x73):
    row['member']=str(a.md.Field[(tok&0xffffff)-1].Name) if tok>>24==4 else a.token_name(tok)
   if op==0x72:row['literal']=str(a.pe.net.user_strings.get(tok&0xffffff))
   il.append(row)
  rows.append(dict(type=ty,method=str(m.Name),il=il))
out=dict(assembly_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),methods=rows)
Path(__file__).with_name('raw').joinpath('engine-contentpath.json').write_text(json.dumps(out,indent=2)+'\n')
print('bounded ContentFinder methods',len(rows))
