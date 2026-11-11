from pathlib import Path
import sys,json,hashlib,struct,time
root=Path(__file__).resolve().parents[3];sys.path.insert(0,str(root/'src/RimMandrake/Utils'))
import generator_inert_audit as I
from lint_harmony_targets import _fix_dnfile_coded_index_width
import dnfile
_fix_dnfile_coded_index_width(dnfile)
p=Path('/mnt/d/SteamLibrary/steamapps/common/RimWorld/RimWorldWin64_Data/Managed/Assembly-CSharp.dll');a=I.Asm(str(p));rows=[]
want={'Verse.Game':{'LoadGame','FinalizeInit'},'Verse.TickManager':{'DoSingleTick'},'Verse.Pawn':{'Tick','TickInterval'},'Verse.Thing':{'Tick','TickInterval','get_TickInterval'},'Verse.ThingWithComps':{'Tick','TickInterval'},'Verse.AI.Pawn_JobTracker':{'JobTrackerTickInterval'},'Verse.AI.JobDriver':{'DriverTickInterval','DriverTick','DriverTickIntervalInternal'},'Verse.TickList':{'DoTick','Tick','TickInterval'},'Verse.Gen':{'IsHashIntervalTick'},'Verse.GenTicks':{'IsHashIntervalTick'}}
for ty,base,methods,t in a.types():
 if ty not in want:continue
 for m in methods:
  if str(m.Name) not in want[ty] and not (ty=='Verse.AI.JobDriver' and 'DriverTickInterval' in str(m.Name)):continue
  code=I.method_body(a.pe,m.Rva);i=0;il=[]
  while i<len(code):
   at=i;op=code[i];i+=1
   if op==0xfe:op2=code[i];i+=1;n=I._operand_size_fe(op2);op=0xfe00|op2
   else:n=I._operand_size(op,code,i)
   tok=struct.unpack_from('<I',code,i)[0] if n==4 else None
   row={'offset':hex(at),'op':hex(op),'operand':code[i:i+n].hex()};i+=n
   if tok and op in (0x28,0x6f,0x7b,0x7c,0x7d,0x7e,0x80,0x73):row['member']=str(a.md.Field[(tok&0xffffff)-1].Name) if tok>>24==4 else a.token_name(tok)
   if op==0x72:row['literal']=str(a.pe.net.user_strings.get(tok&0xffffff))
   il.append(row)
  rows.append({'type':ty,'method':str(m.Name),'il':il})
out=Path(__file__).with_name('raw')/'engine-load-work-contract-v4.json';assert not out.exists();out.write_text(json.dumps({'assembly_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'methods':rows},indent=2)+'\n')
for m in rows:
 print(m['type'],m['method'],'instructions',len(m['il']))
 for i,r in enumerate(m['il']):
  if any(s in r.get('member','') for s in ('DoSingleTick','TickInterval','tickAction','get_TicksGame','DriverTick')):print(json.dumps(m['il'][max(0,i-6):i+3]))
