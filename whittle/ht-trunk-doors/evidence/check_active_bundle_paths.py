from pathlib import Path
import sys,json,re,xml.etree.ElementTree as ET
root=Path(__file__).resolve().parents[3];sys.path.insert(0,str(root/'src/RimMandrake/Utils'))
import modset_builder as M
tier='mods__mandrake_rm_flowworks__mandrake_rm_hugethingstestraces__mandrake_rm_patches__mandrake_rm_biomes__oskarpotocki_vanillafactionsexpanded_core'
installed=M.scan();resolved=M.resolve_tier(tier,installed)
# Inspect actual return schema before any filesystem expansion.
print('resolved tuple length',len(resolved),'types',[type(x).__name__ for x in resolved])
ordered=resolved[0];assert len(ordered)==17
rows=[]
bad=re.compile(r'[\x00-\x1f<>"|]')
for pid in ordered:
 d=Path(installed[pid]['dir']);folders=['','Common','1.6']
 for name in ('LoadFolders.xml','loadFolders.xml'):
  p=d/name
  if p.exists():
   t=ET.parse(p).getroot();n=t.find('v1.6')
   if n is not None:folders+= [x.text or '' for x in n.findall('li')]
 bundles=[]
 for folder in dict.fromkeys(folders):
  b=d/folder/'AssetBundles'
  if b.is_dir():
   bundles += [dict(path=str(p),invalid=bool(bad.search(str(p)))) for p in b.iterdir() if p.is_file()]
 rows.append(dict(package_id=pid,root=str(d),folder_name=d.name,invalid_root=bool(bad.search(str(d))),
                  invalid_package_id=bool(bad.search(pid)),asset_bundle_files=bundles))
Path(__file__).with_name('raw').joinpath('active-bundle-paths.json').write_text(json.dumps(dict(tier=tier,mods=rows),indent=2)+'\n')
print('active mods',len(rows),'invalid physical roots',sum(r['invalid_root'] or r['invalid_package_id'] for r in rows),
      'bundle files',sum(len(r['asset_bundle_files']) for r in rows))
