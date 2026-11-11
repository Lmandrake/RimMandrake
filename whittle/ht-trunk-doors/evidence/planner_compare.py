from pathlib import Path
import sys,shutil,hashlib,json,subprocess,time
root=Path(__file__).resolve().parents[3];e=Path(__file__).resolve().parent
sys.path.insert(0,str(root/'src/RimMandrake/Utils'));import winbuild,ops_watch
quota=ops_watch.c_codex(time.time(),ops_watch.load_rules(),{})
(e/'raw/quota-before-comparison.json').write_text(json.dumps(quota,indent=2)+'\n')
assert quota['codex.week_used_pct']['m']=='MEASURED' and quota['codex.week_used_pct']['v']<88
program=r'''
using System;
using System.Collections.Generic;
using RimMandrake.HugeThings;
class Program {
 static long K(int x,int z)=>RM_HugeFootprintKernel.Key(x,z);
 static List<long> Wanted=new List<long>{K(-1,1),K(0,1)};
 static List<long> Plan(Func<long,CellFlags> flags) {
#if OLD
 return Planner.Plan(Wanted,new List<long>{K(0,0)},flags,new CellBox(-4,-3,4,7));
#else
 return Planner.Plan(Wanted,flags,new CellBox(-4,-3,4,7));
#endif
 }
 static int Main() {
 var walls=new HashSet<long>();
 for(int x=-3;x<=3;x++){if(x!=0)walls.Add(K(x,2));walls.Add(K(x,6));}
 for(int z=3;z<6;z++){walls.Add(K(-3,z));walls.Add(K(3,z));}
 foreach(var p in new[]{(-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(1,1)})walls.Add(K(p.Item1,p.Item2));
 Func<long,CellFlags> flags=k=>walls.Contains(k)?CellFlags.Protected:
  k==K(0,4)?CellFlags.Passable|CellFlags.Pawn:
  k==K(0,2)?CellFlags.Passable|CellFlags.Protected:CellFlags.Passable;
 var actual=Plan(flags);
 Console.WriteLine("entrance contacts accepted="+actual.Count+" of "+Wanted.Count);
 foreach(CellFlags exclusion in new[]{CellFlags.Pawn,CellFlags.Item,CellFlags.Protected}) {
 var negative=Plan(k=>Wanted.Contains(k)?CellFlags.Passable|exclusion:flags(k));
 Console.WriteLine("excluded="+exclusion+" accepted="+negative.Count);
 if(negative.Count!=0)return 2;
 }
 return actual.Count==2?0:1;
 }
}
'''
records=[]
for arm in ('before','after'):
 folder=e/'raw'/('planner-'+arm+'-inputs');folder.mkdir(exist_ok=False)
 for rel,name in [('src/RimMandrake/HugeThings/Source/Kernel/RM_HugeClaimsKernel.cs','Claims.cs'),
                  ('src/RimMandrake/HugeThings/Source/Kernel/RM_HugeFootprintKernel.cs','Geometry.cs'),
                  ('src/RimMandrake/_Shared/DrawnExtent/DrawnExtentKernel.cs','DrawnExtent.cs')]:
  src=e/'raw/source-before'/rel if arm=='before' else root/rel
  assert src.is_file(),src
  shutil.copyfile(src,folder/name)
 (folder/'Program.cs').write_text(program)
 (folder/'Planner.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework><DefineConstants>'+('OLD' if arm=='before' else '')+'</DefineConstants></PropertyGroup></Project>')
 inputs=[dict(path=str(p.relative_to(root)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in folder.iterdir()]
 started=time.time()
 with (e/'raw'/('planner-'+arm+'.stdout.txt')).open('w') as out,(e/'raw'/('planner-'+arm+'.stderr.txt')).open('w') as err:
  import contextlib
  with contextlib.redirect_stdout(out),contextlib.redirect_stderr(err):
   rc,stage=winbuild.stage_build(str(folder/'Planner.csproj'),stage_name='HTTrunkDoorCompare'+arm)
   build_rc=rc
   if rc==0:
    dll=winbuild.staged_win(stage,str(folder))+r'\bin\Release\net8.0\Planner.dll'
    rc=winbuild.run_interop([winbuild.dotnet_exe(),dll],cwd=stage['stage'],timeout=120)
 row=dict(arm=arm,inputs=inputs,build_rc=build_rc,execution_rc=rc,elapsed=time.time()-started,stage=stage)
 (e/'raw'/('planner-'+arm+'.receipt.json')).write_text(json.dumps(row,indent=2)+'\n');records.append(row)
 assert build_rc==0
assert records[0]['execution_rc']==1 and records[1]['execution_rc']==0,[(r['arm'],r['execution_rc']) for r in records]
print('matched planner comparison: before RED rc1; after GREEN rc0')
