from pathlib import Path
import subprocess,json,hashlib,shutil,xml.etree.ElementTree as ET
root=Path.cwd();e=root/'whittle/ht-trunk-doors/evidence';scope=[
'design/RimMandrake/giant_footprint_design_2026-10-07.md','design/RimMandrake/huge_footprints_perf.md',
'design/RimMandrake/hugethings_codex_2026-11-09/QUESTIONS.md','design/RimMandrake/hugethings_codex_2026-11-09/REVIEW.md',
'design/RimMandrake/hugethings_codex_2026-11-09/record.json','src/RimMandrake/HugeThings','src/RimMandrake/HugeThingsTestRaces',
'src/RimMandrake/Utils/selftest_hugethings_budget.py','src/RimMandrake/Utils/selftest_hugethings_lint.py',
'src/RimMandrake/Utils/selftest_hugethings_trunk_doors.py']
paths=set(subprocess.check_output(['git','diff','--name-only','--',*scope],text=True).splitlines())
paths.update(subprocess.check_output(['git','ls-files','--others','--exclude-standard','--',*scope],text=True).splitlines())
rows=[]
for name in sorted(paths):
 p=root/name
 if '/__pycache__/' in name or '/obj/' in name or '/bin/' in name:continue
 row=dict(path=name,exists=p.is_file(),sha256=hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None)
 rows.append(row)
 if p.is_file():
  out=e/'raw/source-ready'/name;out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,out)
(root/'whittle/ht-trunk-doors/SOURCE_READY_INPUTS.json').write_text(json.dumps(rows,indent=2)+'\n')
project=root/'src/RimMandrake/HugeThings/Source/RM_HugeThings.csproj'
inputs=[]
for el in ET.parse(project).getroot().iter('Compile'):
 p=(project.parent/el.attrib['Include'].replace('\\','/')).resolve()
 assert p.is_file(),p
 rel=p.relative_to(root);digest=hashlib.sha256(p.read_bytes()).hexdigest()
 inputs.append(dict(path=str(rel),sha256=digest))
 out=e/'raw/source-ready'/rel
 if not out.exists():out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,out)
(e/'raw/source-ready-compiled-inputs.json').write_text(json.dumps(dict(project=str(project.relative_to(root)),project_sha256=hashlib.sha256(project.read_bytes()).hexdigest(),inputs=inputs),indent=2)+'\n')
q=chr(96)
lines=['# Source ready — trunk doors candidate 1','',
'All planned C# source/fixtures are written. Parent may commit the exact paths in SOURCE_READY_INPUTS.json. Worker has not committed, published, built the production DLL, or claimed CLEAN/acceptance.','',
'Production build remains gated on parent SOURCE_COMMITTED.json. Corrected old-build reproduction and fresh pilot review are pending; the first before attempt stopped at preflight with no Steam request. Any later source correction requires a new parent commit before rebuilding.','',
'Exact changed/new/deleted paths:','']
for row in rows:lines.append('- '+('delete ' if not row['exists'] else '')+q+row['path']+q)
lines+=['','Rationale:',
'- Delete door-approach/connectivity/root-access planner exceptions and enforcing live/static/fuzz callers. Preserve whole pawn bodies, item relocation/quest guards, protected buildings/frames/blueprints/interactions/trees/giants/indestructibles, shared owners and existing work/lifecycle budgets.',
'- Registered enclosed-root cutting retains vanilla PlantsCut policy and JobDriver_PlantCut_Designated: root reservation/work/yield/destruction. A fail-closed validated iterator transform redirects only approach/work-touch to owned C; production rewrite mutation tests cover count/argument drift, driver context, labels and exception boundaries.',
'- Broaden-driven functional script requires actual natural growth/per-cell claims, planted wall choke/reopen control, natural unforced pickup, matched reservation probes and mid-job save/reload. PrepareCutter only configures owned fixture work/schedule; CutState is read-only; OrderCut removed.',
'- Existing gravship implementation unchanged. Production map-component harness adds discriminating indestructible-only, quest-item and non-anchor pawn-body controls, each with matched positive/retry checks.',
'- Retain unrelated sparse scheduler/corpse checks in workload_corpse_live.py; delete p1_live.py and its connectivity case. Workload thresholds now reflect 200 retained contacts.',
'- Performance document retains intended density, dated old-DLL numbers, section2.1/2.2 references and measurement limits. Remove obsolete flood/root-access proposals and replace stale descriptions with coherent current lifecycle/cost/test sections. No external old-section fragment caller was found. No new latency result claimed.',
'- QUESTIONS is historical; record.json changes one placement inventory text. Original CRLF preserved in both. Frozen Whittle STATEMENT/NOTES and owner ANSWERS_OWNER are unchanged.',
'- Synthetic lint verifies exact declared unmeasured two-contact fixture geometry; no pretend measured oak art. Portable selftest resolves Harmony from game_paths; budget runner uses actual staged cwd.',
'','Validation/provenance:',
'- evidence/raw/tests-after4.receipt.json plus stdout/stderr: actual5/5 PASS rc0 after final C# changes. Earlier attempts retained; after2 changed-during-run evidence is not final.',
'- evidence/raw/source-ready-compiled-inputs.json: all '+str(len(inputs))+' exact runtime compile inputs/project hash. evidence/raw/source-ready preserves bytes and current changed spec/test paths.',
'- Installed door/edifice/plant-work IL, enum and metadata consumer audit retained under evidence/raw/engine*. Coexistence behavior was measured.',
'- SelfTest changes are net8 fixture source only. HugeThingsTestRaces has no C# source/project change; only its XML description changes, so deploy that XML. No TestRaces DLL rebuild needed/available.',
'','Parent-owned inbound update: PARENT_ACTIONS.md names shared runner_options current connectivity claim. Worker did not edit shared workflows.','',
'Prescribed build after SOURCE_COMMITTED.json:',
q+'python3 src/RimMandrake/Utils/winbuild.py HugeThings -- /p:HarmonyDll=D:/SteamLibrary/steamapps/workshop/content/294100/2009463077/1.6/Assemblies/0Harmony.dll /p:RimWorldManaged=D:/SteamLibrary/steamapps/common/RimWorld/RimWorldWin64_Data/Managed'+q,
'','Require zero warnings/errors, matching DLL/.srchash and exact committed inputs. No publication/self-CLEAN by worker.']
(root/'whittle/ht-trunk-doors/SOURCE_READY.md').write_text('\n'.join(lines)+'\n')
print('SOURCE_READY changed paths',len(rows),'runtime inputs',len(inputs))
