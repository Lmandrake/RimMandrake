"""Compile complete actual production files selected by the SelfTest project.
Mutants exist only in isolated staging. Preserve each build/run and all inputs.
"""
from pathlib import Path
import difflib
import hashlib
import json
import os
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

here = Path(__file__).resolve().parent
root = here.parents[2]
label, version, mutant, *arguments = sys.argv[1:]
assert version in ('original', 'current')
assert mutant in ('production', 'total', 'outlet', 'free')
actual_entry = bool(arguments and arguments[0] == '--actual-entry')
if actual_entry:
    arguments.pop(0)
out = here / ('fast_' + label)
out.mkdir(exist_ok=False)
stage = Path('/mnt/d/ClaudeWork/rimmandrake/scratch/fw-hose-fuzz') / label
stage.mkdir(parents=True, exist_ok=False)
project = root / 'src/RimMandrake/FlowWorks/Source/SelfTest/RimMandrakeFlowWorks.SelfTest.csproj'
paths = []
for item in ET.parse(project).findall('./ItemGroup/Compile'):
    path = (project.parent / item.attrib['Include'].replace('\\', '/')).resolve()
    if actual_entry or 'SelfTest' not in path.parts:
        paths.append(path)
hose_path = root / 'src/RimMandrake/FlowWorks/Source/SelfTest/HoseFuzz.cs'
if actual_entry:
    paths.extend([project, project.parent.parent / 'RM_LiquidStock.cs'])
else:
    paths.append(hose_path)
source_hashes, staged_hashes = {}, {}
sha = lambda data: hashlib.sha256(data).hexdigest()
for path in paths:
    relative = str(path.relative_to(root))
    original = path.read_bytes()
    source_hashes[relative] = sha(original)
    content = original
    if path == hose_path and version == 'original':
        content = (here / 'original_HoseFuzz.cs').read_bytes()
    if path.name == 'HoseMath.cs' and mutant != 'production':
        code = content.decode()
        signature = 'internal static HoseLay Lay(CordWorld w, V2 a, V2 b, HoseShapeParams p, ulong seed, V2? endInward = null, V2? startOutward = null)'
        assert code.count(signature) == 1
        start = code.index('{', code.index(signature)) + 1
        condition = {'total': 'p != null', 'outlet': 'startOutward.HasValue', 'free': '!startOutward.HasValue'}[mutant]
        code = code[:start] + '\n            // ISOLATED MUTANT ONLY\n            if (' + condition + ') return new HoseLay { Reason = "isolated refusal mutant" };\n' + code[start:]
        content = code.encode()
    target = stage / 'inputs' / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content)
    saved = out / 'inputs' / relative
    saved.parent.mkdir(parents=True, exist_ok=True)
    saved.write_bytes(content)
    staged_hashes[relative] = sha(content)
    if original != content:
        (out / (path.stem + '.diff')).write_text(''.join(difflib.unified_diff(original.decode().splitlines(True), content.decode().splitlines(True), fromfile=relative, tofile='isolated/' + relative)))
program = '''using System;
using RimMandrake.FlowWorks.Hose;
namespace RimMandrake.FlowWorks.SelfTest {
internal static class Program {
    private static int failures;
    public static void Check(bool ok, string message) {
        Console.WriteLine((ok ? "PASS " : "FAIL ") + message);
        if (!ok) failures++;
    }
    public static int Main(string[] args) {
        if (Array.IndexOf(args, "g2off") >= 0) HoseMath.G2On = false;
        if (Array.IndexOf(args, "g2") >= 0) HoseMath.G2On = true;
        if (Array.IndexOf(args, "--inspect") >= 0) {
            for (long seed = 1; seed <= 40; seed++) {
                foreach (bool outlet in new[] { true, false }) {
                    long steps = 0;
                    var c = HoseFuzz.MakeHose(seed);
                    string msg = HoseFuzz.RunHose(seed, null, ref steps, out int laid, out int fallback, outlet);
                    Console.WriteLine($"INSPECT seed={seed} outlet={outlet} reel={c.Reel.W} laid={laid} fallback={fallback} steps={steps} install={HoseMath.CheckInstall(c.W, c.Reel, c.Target, c.MaxLen) ?? "ok"} msg={msg ?? "ok"}");
                }
            }
        } else HoseFuzz.Run(args);
        Console.WriteLine("FAILED checks: " + failures);
        return failures == 0 ? 0 : 1;
    }
}}
'''
includes = ''.join('<Compile Include="inputs/' + str(p.relative_to(root)) + '"/>' for p in paths)
csproj = '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework><EnableDefaultCompileItems>false</EnableDefaultCompileItems><ImplicitUsings>enable</ImplicitUsings><Nullable>disable</Nullable></PropertyGroup><ItemGroup>' + includes + ('' if actual_entry else '<Compile Include="Program.cs"/>') + '</ItemGroup></Project>\n'
for name, text in [('Program.cs', program), ('Probe.csproj', csproj)]:
    (stage / name).write_text(text)
    (out / name).write_text(text)
build_project = stage / 'inputs' / project.relative_to(root) if actual_entry else stage / 'Probe.csproj'
cmd = ['/mnt/c/Users/Mandrake/.dotnet/dotnet.exe', 'run', '--project', subprocess.check_output(['wslpath', '-w', str(build_project)], text=True).strip(), '-c', 'Release', '--', *arguments]
started = time.time()
proc = subprocess.run(cmd, cwd=stage, capture_output=True, timeout=180, env=dict(os.environ, TMPDIR='/home/mandrake/.seat-tmp/fw-hose-fuzz'))
(out / 'stdout.txt').write_bytes(proc.stdout)
(out / 'stderr.txt').write_bytes(proc.stderr)
receipt = dict(actual_entry=actual_entry, label=label, version=version, mutant=mutant, command=cmd, stage=str(stage), started=started, elapsed=time.time()-started, returncode=proc.returncode, source_sha256=source_hashes, staged_sha256=staged_hashes)
receipt['staged_inputs_match_saved'] = all((stage / 'inputs' / p).read_bytes() == (out / 'inputs' / p).read_bytes() for p in staged_hashes)
(out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(proc.stdout.decode(errors='replace'))
print(proc.stderr.decode(errors='replace'))
print(json.dumps({k:v for k,v in receipt.items() if 'sha256' not in k}, indent=2))
