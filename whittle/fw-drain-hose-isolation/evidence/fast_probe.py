"""Small executable lab: compile whole production kernel and HoseNetChecks, never a copied algorithm.

Each mode has its own isolated Windows stage. Negative modes are expected to return 1.
"""
from pathlib import Path
import difflib, hashlib, json, os, subprocess, sys, time
here=Path(__file__).resolve().parent
root=here.parents[2]
mode=sys.argv[1]
assert mode in ('reproduce', 'final', 'old_fixture', 'tank_conduction')
out=here/('fast_'+mode)
assert not out.exists(), 'Preserve actual runs'
out.mkdir()
stage=Path('/mnt/d/ClaudeWork/rimmandrake/scratch/fw-hose-isolation')/mode
stage.mkdir(parents=True, exist_ok=False)
kpath=root/'src/RimMandrake/FlowWorks/Source/Machinery/RM_LiquidNetKernel.cs'
hpath=root/'src/RimMandrake/FlowWorks/Source/SelfTest/HoseNetChecks.cs'
kernel=kpath.read_text(); hose=hpath.read_text()
(stage/'original_kernel.cs.txt').write_text(kernel)
(stage/'original_hose.cs.txt').write_text(hose)
if mode=='old_fixture':
    for a,b in [('"cA1"','"a1"'),('"cB1"','"b1"')]:
        assert a in hose
        hose=hose.replace(a,b)
if mode=='tank_conduction':
    old='foreach (object t in g.PipeTanks(v)) { AttachMember(comp, t, i, comp.Tanks); st?.Add(new Step { Kind = 0, Obj = t }); }'
    new='''foreach (object t in g.PipeTanks(v))
                    {
                        AttachMember(comp, t, i, comp.Tanks); st?.Add(new Step { Kind = 0, Obj = t });
                        // MUTANT ONLY: traverse across a tank into all its attached pipe runs.
                        foreach (object n in g.OriginPipeCells(t))
                        { Visit(comp, n, i, q); st?.Add(new Step { Kind = 3, Obj = n }); }
                    }'''
    assert kernel.count(old)==1
    kernel=kernel.replace(old,new)
main='HoseNetChecks.Run();'
if mode=='reproduce':
    main='''var g = new HoseNetChecks.G();
            HoseNetChecks.G.Add(g.PipeOf, "P1", "a1");
            HoseNetChecks.G.Add(g.PT, "a1", "T");
            HoseNetChecks.G.Add(g.PT, "b1", "T");
            HoseNetChecks.G.Add(g.PT, "b1", "TV");
            var tanks = HoseNetChecks.Walk(g, "P1").Tanks;
            Console.WriteLine("MEASURED roles a1=" + g.RoleOf("a1") + " b1=" + g.RoleOf("b1") + " tanks=[" + string.Join(",", tanks) + "]");
            Check(!tanks.Contains("TV"), "OLD exclusion passes with no recognized pipes");
            Check(tanks.Contains("T") && !tanks.Contains("TV"), "REPAIRED reach-T-and-exclude-TV assertion on OLD fixture");'''
program='''using System;
namespace RimMandrake.FlowWorks.SelfTest {
internal static class Program {
    private static int failures;
    public static void Check(bool ok, string message) {
        Console.WriteLine((ok ? "PASS " : "FAIL ") + message);
        if (!ok) failures++;
    }
    public static int Main() {
        MAIN
        Console.WriteLine("FAILED checks: " + failures);
        return failures == 0 ? 0 : 1;
    }
}}
'''.replace('MAIN',main)
project='<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework><EnableDefaultCompileItems>false</EnableDefaultCompileItems></PropertyGroup><ItemGroup><Compile Include="Kernel.cs"/><Compile Include="HoseNetChecks.cs"/><Compile Include="Program.cs"/></ItemGroup></Project>\n'
inputs={'Kernel.cs':kernel,'HoseNetChecks.cs':hose,'Program.cs':program,'Probe.csproj':project}
for name,text in inputs.items():
    (stage/name).write_text(text)
    (out/name).write_text(text)
for name,original,changed in [('kernel',kpath.read_text(),kernel),('hose',hpath.read_text(),hose)]:
    (out/(name+'.diff')).write_text(''.join(difflib.unified_diff(original.splitlines(True),changed.splitlines(True),fromfile='actual_source',tofile=mode)))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
cmd=['/mnt/c/Users/Mandrake/.dotnet/dotnet.exe','run','--project',subprocess.check_output(['wslpath','-w',str(stage/'Probe.csproj')],text=True).strip(),'-c','Release']
started=time.time()
proc=subprocess.run(cmd,cwd=stage,capture_output=True,timeout=120,env=dict(os.environ,TMPDIR='/home/mandrake/.seat-tmp/fw-hose-isolation'))
(out/'stdout.txt').write_bytes(proc.stdout); (out/'stderr.txt').write_bytes(proc.stderr)
receipt=dict(mode=mode,command=cmd,stage=str(stage),started=started,elapsed=time.time()-started,returncode=proc.returncode,source_sha256={str(p.relative_to(root)):sha(p) for p in (kpath,hpath)},staged_sha256={n:sha(stage/n) for n in inputs},evidence_sha256={n:sha(out/n) for n in inputs},expected_returncode=0 if mode=='final' else 1)
receipt['staged_inputs_match_saved']=receipt['staged_sha256']==receipt['evidence_sha256']
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(proc.stdout.decode(errors='replace')); print(proc.stderr.decode(errors='replace')); print(json.dumps(receipt,indent=2))
assert receipt['staged_inputs_match_saved'] and proc.returncode==receipt['expected_returncode']
if mode=='tank_conduction':
    assert b'FAIL hosenet: two pipe runs' in proc.stdout, 'The repaired assertion must reject actual tank traversal'
