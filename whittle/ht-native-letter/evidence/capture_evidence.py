"""Save raw post-edit source and read-only compatibility inspection receipts."""
import ast
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess
import time
import xml.etree.ElementTree as ET

root=Path(__file__).resolve().parents[3]
e=Path(__file__).resolve().parent
base=Path('src/RimMandrake/HugeThings')
changed=[base/'Languages/English/Keyed/RM_TitanicCreatures.xml',base/'Languages/English/Keyed/RM_HugeThings.xml',base/'northstar/titan_events_live.py']
raw_paths=changed+[base/'Source/Titanic/Events/TitanPassage.cs',base/'Source/Kernel/RM_TitanicKernel.cs',base/'Source/RM_HugeThingsSettings.cs',base/'Source/Titanic/Events/RM_TitanPassageExtension.cs',base/'Source/Titanic/Events/TitanValidationHooks.cs']
def git(*args):
    return subprocess.check_output(['git',*args],cwd=root)
sha=git('rev-parse','HEAD').decode().strip()
manifest={'git_sha':sha,'captured_at':time.time(),'files':{}}
for rel in raw_paths:
    raw=(root/rel).read_bytes()
    target=e/'source'/rel.relative_to(base)
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes(raw)
    manifest['files'][str(rel)]={'sha256':hashlib.sha256(raw).hexdigest(),'snapshot':str(target.relative_to(root)),'same_as_head':raw==git('show',f'HEAD:{rel}')}
(e/'source_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
(e/'source.diff').write_bytes(git('diff','HEAD','--',*[str(p) for p in changed]))
(e/'tracked.diff').write_bytes(git('diff','HEAD','--'))
(e/'git_status.txt').write_bytes(git('status','--short'))
check=subprocess.run(['git','diff','--check'],cwd=root,capture_output=True)
(e/'diff_check.stdout.txt').write_bytes(check.stdout)
(e/'diff_check.stderr.txt').write_bytes(check.stderr)
report={'git_sha':sha,'inspected_at':time.time(),'diff_check_rc':check.returncode,'xml':[]}
assert check.returncode==0
for rel in changed[:2]:
    old=ET.fromstring(git('show',f'HEAD:{rel}'))
    new=ET.fromstring((root/rel).read_bytes())
    assert old.tag==new.tag=='LanguageData'
    assert [x.tag for x in old]==[x.tag for x in new]
    assert all(n==1 for n in Counter(x.tag for x in new).values())
    different=[]
    for a,b in zip(old,new):
        assert a.attrib==b.attrib
        before=re.findall(r'\{\d+(?:[^}]*)\}',a.text or '')
        after=re.findall(r'\{\d+(?:[^}]*)\}',b.text or '')
        assert before==after,(a.tag,before,after)
        if a.text!=b.text:
            different.append({'key':a.tag,'before':a.text,'after':b.text,'format_args':after})
    assert len(different)==1
    report['xml'].append({'file':str(rel),'well_formed':True,'same_ordered_unique_keys':True,'all_format_args_unchanged':True,'changed_values':different})
old_ast=ast.parse(git('show',f'HEAD:{changed[2]}'))
new_ast=ast.parse((root/changed[2]).read_bytes())
old_ast.body=old_ast.body[1:]; new_ast.body=new_ast.body[1:]
assert ast.dump(old_ast)==ast.dump(new_ast)
report['python_executable_ast_unchanged']=True
assert set(git('diff','HEAD','--name-only').decode().splitlines())=={str(p) for p in changed}
assert all(manifest['files'][str(p)]['same_as_head'] for p in raw_paths[3:])
report['tracked_changes_exactly_requested_three_files']=True
report['all_inspected_cs_files_byte_identical_to_head']=True
letter=ET.fromstring((root/changed[0]).read_bytes()).findtext('RM_TitanPassage_TremorText')
settings=ET.fromstring((root/changed[1]).read_bytes())
report['directional_warning_examples']={d:letter.format(d).replace('\\n','\n') for d in ('north','south','east','west')}
report['warning_hours_example']=settings.findtext('RM_HugeThings_TitanWarning').format('6.0')
report['callsite_review']={'tremor':'TitanPassage.cs:42-43 passes EdgeName(map, start) as the sole argument','description':'RM_HugeThingsSettings.cs:399 translates description with zero arguments','warning':'RM_HugeThingsSettings.cs:402 passes formatted warning hours as the sole argument','limitations':'Offline XML/string/callsite inspection only; no game run or gameplay acceptance.'}
(e/'compatibility.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
