"""Whole production HosePorts/RM_HoseBands with explicit engine doubles; no algorithm extraction."""
from pathlib import Path
import subprocess,sys,os,json,hashlib,xml.etree.ElementTree as ET,time
here=Path(__file__).resolve().parent;root=here.parents[2]
label,version=sys.argv[1:];assert version in ('original','current','unfiltered')
out=here/('fast_'+label);out.mkdir(exist_ok=False)
stage=Path('/mnt/d/ClaudeWork/rimmandrake/scratch/fw-reel-inlet')/label;stage.mkdir(parents=True,exist_ok=False)
project=root/'src/RimMandrake/FlowWorks/Source/SelfTest/RimMandrakeFlowWorks.SelfTest.csproj'
paths=[(project.parent/p.attrib['Include'].replace('\\','/')).resolve() for p in ET.parse(project).findall('./ItemGroup/Compile')]
paths=[p for p in paths if 'SelfTest' not in p.parts]
paths += [root/'src/RimMandrake/FlowWorks/Source/Hose'/p for p in ['HosePorts.cs','RM_HoseBands.cs']]
if version != 'original': paths.append(project.parent/'HoseBodyInletChecks.cs')
source={};staged={};incs=[]
for p in paths:
 rel=str(p.relative_to(root));data=p.read_bytes();source[rel]=hashlib.sha256(data).hexdigest()
 if version=='original' and p.name in ('HosePorts.cs','HoseMath.cs'):data=(here/('original_'+p.name)).read_bytes()
 if version=='unfiltered' and p.name=='HosePorts.cs':
  s=data.decode();old='HosePortRule.Pick(rect, cands, out side, out contact, reachable)';assert old in s;s=s.replace(old,'HosePortRule.Pick(rect, cands, out side, out contact)');data=s.encode()
 target=stage/'inputs'/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 saved=out/'inputs'/rel;saved.parent.mkdir(parents=True,exist_ok=True);saved.write_bytes(data)
 staged[rel]=hashlib.sha256(data).hexdigest();incs.append('<Compile Include="inputs/'+rel+'"/>')
for name in ['AdapterStubs.cs','AdapterCases.cs']:
 data=(here/name).read_bytes();(stage/name).write_bytes(data);(out/name).write_bytes(data);incs.append('<Compile Include="'+name+'"/>')
csproj='<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework><EnableDefaultCompileItems>false</EnableDefaultCompileItems><ImplicitUsings>enable</ImplicitUsings><DefineConstants>' + ('CURRENT' if version != 'original' else '') + '</DefineConstants><Nullable>disable</Nullable></PropertyGroup><ItemGroup>'+''.join(incs)+'</ItemGroup></Project>'
(stage/'Probe.csproj').write_text(csproj);(out/'Probe.csproj').write_text(csproj)
cmd=['/mnt/c/Users/Mandrake/.dotnet/dotnet.exe','run','--project',subprocess.check_output(['wslpath','-w',str(stage/'Probe.csproj')],text=True).strip(),'-c','Release']
t=time.time();p=subprocess.run(cmd,capture_output=True,timeout=180,env=dict(os.environ,TMPDIR='/home/mandrake/.seat-tmp/fw-reel-inlet'))
(out/'stdout.txt').write_bytes(p.stdout);(out/'stderr.txt').write_bytes(p.stderr)
(out/'receipt.json').write_text(json.dumps(dict(command=cmd,started=t,elapsed=time.time()-t,returncode=p.returncode,source_sha256=source,staged_sha256=staged,stage=str(stage)),indent=2)+'\n')
print(p.stdout.decode(errors='replace'));print(p.stderr.decode(errors='replace'));print('RETURN',p.returncode)
