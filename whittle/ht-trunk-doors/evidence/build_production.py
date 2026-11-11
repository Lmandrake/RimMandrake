from pathlib import Path
import subprocess,json,time,hashlib
root=Path(__file__).resolve().parents[3];e=Path(__file__).resolve().parent
commit=json.loads((e.parent/'SOURCE_COMMITTED.json').read_text())
assert commit['sha']=='974537eeb71866efdecf527afea150a14905a998'
manifest=e/'raw/source-ready-v2-compiled-inputs.json';m=json.loads(manifest.read_text())
for row in m['inputs']:
 assert hashlib.sha256((root/row['path']).read_bytes()).hexdigest()==row['sha256'],row['path']
assert hashlib.sha256((root/m['project']).read_bytes()).hexdigest()==m['project_sha256']
cmd=['python3','src/RimMandrake/Utils/winbuild.py','HugeThings','--',
 '/p:HarmonyDll=D:/SteamLibrary/steamapps/workshop/content/294100/2009463077/1.6/Assemblies/0Harmony.dll',
 '/p:RimWorldManaged=D:/SteamLibrary/steamapps/common/RimWorld/RimWorldWin64_Data/Managed']
start=time.time()
with (e/'raw/build-production.stdout.txt').open('wb') as out,(e/'raw/build-production.stderr.txt').open('wb') as err:r=subprocess.run(cmd,stdout=out,stderr=err)
record=dict(command=cmd,rc=r.returncode,elapsed=time.time()-start,commit=commit['sha'],compile_manifest_sha256=hashlib.sha256(manifest.read_bytes()).hexdigest())
for ext in ('dll','dll.srchash'):
 p=root/('src/RimMandrake/HugeThings/Assemblies/RM_HugeThings.'+ext)
 if p.exists():record[ext]=dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),path=str(p.relative_to(root)))
(e/'raw/build-production.receipt.json').write_text(json.dumps(record,indent=2)+'\n')
print('production build rc',r.returncode)
raise SystemExit(r.returncode)
