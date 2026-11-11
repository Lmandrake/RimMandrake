"""Run auto-extracted exact ScenicRoute fixtures against staged production kernels.

Only mutant: cost>=BuildingCrossCost becomes unwalkable, except the source mouth cell.
No source in src/ is written. Fixture method is extracted at execution, never reimplemented.
"""
import difflib, hashlib, json, subprocess, time
from pathlib import Path
here=Path(__file__).resolve().parent
root=here.parents[2]
source='src/RimMandrake/FlowWorks/Source/SelfTest/HoseReviewChecks.cs'
production=json.loads((here/'probe_manifest.json').read_text())
old=subprocess.check_output(['git','show','HEAD:'+source],cwd=root,text=True)
final=(root/source).read_text()
def method(s):
 start=s.index('        private static void ScenicRoute()')
 a=s.index('{',start); depth=0
 for end in range(a,len(s)):
  if s[end]=='{': depth+=1
  elif s[end]=='}':
   depth-=1
   if depth==0: return s[start:end+1]
 raise ValueError('unbalanced fixture')
records=[]
for mutant in (False,True):
 stage=Path('/mnt/d/ClaudeWork/rimmandrake/scratch/fw-hose-scenic-'+('mutant' if mutant else 'exact'))
 stage.mkdir(exist_ok=True)
 manifests={}
 for p in production:
  data=(root/p).read_bytes()
  assert hashlib.sha256(data).hexdigest()==production[p]
  if mutant and p.endswith('/CordWorld.cs'):
   original=data.decode()
   before='public bool IsWalkable(Cell c) => InBounds(c) && block[Idx(c)] == 0;'
   after='public bool IsWalkable(Cell c) => InBounds(c) && block[Idx(c)] == 0 && (c == new Cell(20, 8) || extraCost[Idx(c)] < RimMandrake.FlowWorks.Hose.HoseMath.BuildingCrossCost);'
   assert original.count(before)==1
   modified=original.replace(before,after)
   data=modified.encode()
   (here/'building_block_mutant.patch').write_text(''.join(difflib.unified_diff(original.splitlines(True),modified.splitlines(True),fromfile=p,tofile='isolated-stage/CordWorld.cs')))
  (stage/Path(p).name).write_bytes(data)
  manifests[p]=dict(source_sha256=production[p],stage_sha256=hashlib.sha256(data).hexdigest())
 (stage/'Probe.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework><LangVersion>latest</LangVersion><ImplicitUsings>enable</ImplicitUsings><Nullable>disable</Nullable><NoWarn>0649</NoWarn></PropertyGroup></Project>')
 classes=[]
 for label,s in [('Original',old),('Final',final)]:
  extracted=method(s)
  (here/(label.lower()+'_scenic_exact.cs.txt')).write_text(extracted+'\n')
  classes.append('static class '+label+' { public static bool forcedPassed; static void Check(bool ok,string msg) { Console.WriteLine((ok?"PASS ":"FAIL ")+"'+label+' "+msg); if(msg.StartsWith("scenic: the cost never blocks")) forcedPassed=ok; } public static void Run()=>ScenicRoute();\n'+extracted+'\n}')
 shim='''using System;
using System.Linq;
using System.Collections.Generic;
using RimMandrake.FlowWorks.Hose;
using RimMandrake.Shared.Slack;
static class RiverSwitchFlipChecks { public static string Src(string p)=>System.IO.File.ReadAllText(@"ROOT/src/RimMandrake/FlowWorks/Source/"+p); }
class Probe { static void Main() {
var reel=new HoseReelRect(20,8,2,2); var w=new CordWorld(44,24);
w.SetExtraCost(reel.Mouth.Floor,HoseMath.BuildingCrossCost);
Console.WriteLine($"mouth={reel.Mouth} floor={reel.Mouth.Floor} walkable={w.IsWalkable(reel.Mouth.Floor)} outlet_clear={HoseMath.OutletClear(w,reel.Mouth,reel.Outward.Value,HoseMath.FullLeadOut(new HoseShapeParams {MinBendRadius=1.2,MaxLength=40}))}");
w.SetExtraCost(new Cell(12,8),HoseMath.BuildingCrossCost);
Console.WriteLine($"remote_cost_walkable={w.IsWalkable(new Cell(12,8))}");
Original.Run(); Final.Run();
if(!Original.forcedPassed || Final.forcedPassed==MUTANT) Environment.Exit(1);
}}
'''.replace('ROOT',str(root)).replace('MUTANT',str(mutant).lower())
 program=shim+'\n'+'\n'.join(classes)
 (stage/'Program.cs').write_text(program)
 (here/(('mutant' if mutant else 'exact')+'_program.cs.txt')).write_text(program)
 cmd=['/mnt/c/Users/Mandrake/.dotnet/dotnet.exe','run','--project',subprocess.check_output(['wslpath','-w',str(stage/'Probe.csproj')],text=True).strip(),'-c','Release']
 started=time.time(); proc=subprocess.run(cmd,capture_output=True,text=True,timeout=120)
 label='mutant' if mutant else 'exact'
 (here/(label+'_stdout.txt')).write_text(proc.stdout); (here/(label+'_stderr.txt')).write_text(proc.stderr)
 record=dict(time=started,elapsed=time.time()-started,command=cmd,returncode=proc.returncode,mutant=mutant,stage=str(stage),production_inputs=manifests,fixture_source_sha256=hashlib.sha256(final.encode()).hexdigest(),original_source_sha256=hashlib.sha256(old.encode()).hexdigest(),program_sha256=hashlib.sha256(program.encode()).hexdigest())
 (here/(label+'_receipt.json')).write_text(json.dumps(record,indent=2)+'\n')
 print(label,proc.returncode,proc.stdout,proc.stderr,flush=True)
 assert proc.returncode==0
