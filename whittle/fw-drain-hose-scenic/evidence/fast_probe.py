"""Compile actual production files in isolated D-drive staging; no shipping writes."""
import hashlib, json, subprocess, time
from pathlib import Path
here=Path(__file__).resolve().parent
root=here.parents[2]
stage=Path('/mnt/d/ClaudeWork/rimmandrake/scratch/fw-hose-scenic-fast')
stage.mkdir(exist_ok=True)
paths=['src/RimMandrake/_Shared/SlackGeometry/'+n+'.cs' for n in ['CordMath','CordWorld','CordPlanner','CordLayer','DrawOrder']]
paths+=['src/RimMandrake/FlowWorks/Source/Hose/'+n+'.cs' for n in ['HoseMath','HoseClothoid','HoseRelay','ReelIntakeGeometry','HoseCarry']]
paths+=['src/RimMandrake/FlowWorks/Source/Machinery/LiquidJoinRule.cs']
manifest={}
for p in paths:
 data=(root/p).read_bytes(); (stage/Path(p).name).write_bytes(data); manifest[p]=hashlib.sha256(data).hexdigest()
(stage/'Probe.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework><LangVersion>latest</LangVersion><ImplicitUsings>enable</ImplicitUsings><Nullable>disable</Nullable></PropertyGroup></Project>')
program='''using RimMandrake.Shared.Slack;
using RimMandrake.FlowWorks.Hose;
class Probe {
static void Main() {
var reel = new HoseReelRect(20,8,2,2);
var prm = new HoseShapeParams { MinBendRadius=1.2, MaxLength=40 };
Console.WriteLine($"mouth={reel.Mouth} outward={reel.Outward} lead={HoseMath.OutletLead(prm)}");
foreach(bool barrier in new[]{false,true}) {
var w = new CordWorld(44,24);
foreach(var r in new[]{reel,new HoseReelRect(20,11,2,2)})
 for(int x=r.X0;x<r.X0+r.W;x++) for(int z=r.Z0;z<r.Z0+r.H;z++) w.SetExtraCost(new Cell(x,z),HoseMath.BuildingCrossCost);
w.SetExtraCost(new Cell(20,10),HoseMath.BuildingCrossCost);
for(int x=0;x<44;x++){w.SetBlocked(new Cell(x,7),BlockKind.Wall);w.SetBlocked(new Cell(x,10),BlockKind.Wall);}
if(barrier) for(int x=12;x<14;x++) for(int z=8;z<10;z++) w.SetExtraCost(new Cell(x,z),HoseMath.BuildingCrossCost);
var target=new Cell(barrier?8:14,9).Centre;
var lay=HoseMath.Lay(w,reel.Mouth,target,prm,7,null,reel.Outward);
Console.WriteLine($"barrier={barrier} ok={lay.Ok} reason={lay.Reason} flat={lay.FlatLen} plump={lay.PlumpLen}");
if(lay.Ok) Console.WriteLine("crossed="+string.Join(";",HoseMath.CellsAlong(lay.Flat).Where(c=>c.X>=12&&c.X<14&&w.ExtraCost(c)>=HoseMath.BuildingCrossCost)));
}
}}
'''
(stage/'Program.cs').write_text(program)
(here/'probe_program.cs.txt').write_text(program)
(here/'probe_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
cmd=['/mnt/c/Users/Mandrake/.dotnet/dotnet.exe','run','--project','D:\\ClaudeWork\\rimmandrake\\scratch\\fw-hose-scenic-fast\\Probe.csproj','-c','Release']
start=time.time(); p=subprocess.run(cmd,capture_output=True,text=True,timeout=120)
(here/'probe_baseline_stdout.txt').write_text(p.stdout); (here/'probe_baseline_stderr.txt').write_text(p.stderr)
(here/'probe_baseline_receipt.json').write_text(json.dumps(dict(command=cmd,returncode=p.returncode,elapsed=time.time()-start),indent=2)+'\n')
print(p.stdout,p.stderr); print('rc',p.returncode)
