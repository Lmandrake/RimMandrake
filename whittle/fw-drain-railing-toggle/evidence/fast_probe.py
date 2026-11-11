"""Run the normal durable railing cases against entire actual methods and explicit engine doubles."""
from pathlib import Path
import sys,subprocess,json,os,time,hashlib
here=Path(__file__).resolve().parent;root=here.parents[2]
label,mode=sys.argv[1:];assert mode in ('original','current','delete_all','first_only')
out=here/('fast_'+label);out.mkdir(exist_ok=False)
stage=Path('/mnt/d/ClaudeWork/rimmandrake/scratch/fw-railing-toggle')/label;stage.mkdir(parents=True,exist_ok=False)
prefix=root/'src/RimMandrake/FlowWorks/Source'
paths=[prefix/'SelfTest'/n for n in ['RailingToggleHarness.cs','RailingToggleHarness.targets']]+[prefix/'Pits/Suspension'/n for n in ['RM_MapComponent_SuspensionBridges.cs','RM_SuspensionProofs.cs']]
inputs={}
for p in paths:
 data=p.read_bytes()
 if p.name=='RM_MapComponent_SuspensionBridges.cs':
  if mode=='original': data=(here/('original_'+p.name)).read_bytes()
  elif mode=='delete_all': data=data.replace(b'map.designationManager.DesignationOn(existing, DesignationDefOf.Deconstruct)?.Delete();',b'foreach (var d in map.designationManager.all.ToList()) if (d.target == existing) d.Delete();')
  elif mode=='first_only':data=data.replace(b'if (t is Building_SuspensionRailing existing)',b'if (t == BuiltAt<Building_SuspensionRailing>(map, c) && t is Building_SuspensionRailing existing)')
 (stage/p.name).write_bytes(data);(out/p.name).write_bytes(data);inputs[p.name]=hashlib.sha256(data).hexdigest()
main='''using System;using RimMandrake.FlowWorks.SelfTest.RailingHarness;
class P {static int Main(){int n=0,f=0;RailingToggleChecks.Run((name,a)=>{n++;try{a();Console.WriteLine("PASS "+name);}catch(Exception e){f++;Console.WriteLine("FAIL "+name+": "+e.Message);}});Console.WriteLine($"{n-f}/{n} PASS; {f} FAIL");return f==0?0:1;}}'''
(stage/'Main.cs').write_text(main);(out/'Main.cs').write_text(main)
proj='''<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework><EnableDefaultCompileItems>false</EnableDefaultCompileItems><ImplicitUsings>enable</ImplicitUsings><RailingProductionSource>$(MSBuildProjectDirectory)\\RM_MapComponent_SuspensionBridges.cs</RailingProductionSource><RailingProofSource>$(MSBuildProjectDirectory)\\RM_SuspensionProofs.cs</RailingProofSource></PropertyGroup><ItemGroup><Compile Include="RailingToggleHarness.cs"/><Compile Include="Main.cs"/></ItemGroup><Import Project="RailingToggleHarness.targets"/></Project>'''
(stage/'Probe.csproj').write_text(proj);(out/'Probe.csproj').write_text(proj)
cmd=['/mnt/c/Users/Mandrake/.dotnet/dotnet.exe','run','--project',subprocess.check_output(['wslpath','-w',str(stage/'Probe.csproj')],text=True).strip(),'-c','Release']
t=time.time();p=subprocess.run(cmd,capture_output=True,timeout=120,env=dict(os.environ,TMPDIR='/home/mandrake/.seat-tmp/fw-railing-toggle'))
for name,data in [('stdout.txt',p.stdout),('stderr.txt',p.stderr)]: (out/name).write_bytes(data)
generated=stage/'obj/Release/net8.0/RailingToggle.g.cs'
if generated.exists():(out/'RailingToggle.g.cs').write_bytes(generated.read_bytes())
(out/'receipt.json').write_text(json.dumps(dict(command=cmd,mode=mode,started=t,elapsed=time.time()-t,returncode=p.returncode,inputs_sha256=inputs,stage=str(stage)),indent=2)+'\n')
print(p.stdout.decode(errors='replace'));print(p.stderr.decode(errors='replace'));print('RETURN',p.returncode)
