import re,shutil,subprocess,json,os
T='Transient/biome_worldtex_2026-10-18'
OWN="Please make new world-map textures for ALL of our Biomes at this time. These are placeholder for now, to enable worldmap painting. We will refine them later. So simply read each of their descriptions and create something appropriate. Make each of them distinct from each other in color and texture. Then simply install them. I can review them in parallel, but do not block on me."
rows=[l.rstrip('\n').split('|') for l in open('/home/mandrake/.seat-tmp/BENCH/census.txt')]
KEY={'Desert':'LongShade','FuelSnows':'Umbra','Jawa_BackgroundWater':'MineralWater','PropaneLake':'Chill','Scarlands':'Warscar','NightsideIce':'SleepingIce','TheScald':'Scald','TheForge':'Forge','Wasteland':'Wasteland','ExtremeDesert':'Stillsand','AridShrubland':'LeaningScrub','Warscar':'Warscar','TheChill':'Chill','FloodedCanyon':'CrackedLands','TheSump':'Sump','GelatinousSlime':'Slime','LongShade':'LongShade','LeaningScrub':'LeaningScrub','TheRot':'TheRot','SeabedFloor_TheScald':'SeabedScald','SeabedFloor_GreySea':'SeabedGrey','SeabedFloor_TwilightSea':'SeabedTwilight','SeabedFloor_TheChill':'SeabedChill','SeabedUnavailable':'SeabedBedrock','SeabedFloor':'SeabedFloor'}
res=[]
for dn,label,desc,tex,path in rows:
    if 'Fixture' in dn: continue
    pre,name=dn.split('_',1); key=KEY.get(name,name)
    tier,mod=path.split('/')[1:3]
    newname=f"{pre}_{key}"
    src=f"{T}/tex/{key}.png"; stage=f"{T}/tex/{newname}.png"
    if not os.path.exists(stage): shutil.copy(src,stage)
    r=subprocess.run(['python3','src/RimMandrake/Utils/art/art.py','install',f'{tier}/{mod}',f'World/Biomes/{newname}.png','--file',stage,'--owner-said',OWN],capture_output=True,text=True)
    st=(r.stdout.strip().splitlines() or [''])[-1][:160]
    ok='"installed"' in st or '"status": "ok' in st or r.returncode==0
    if ok:
        s=open(path).read()
        # edit only this def's texture
        m=re.search(r'<BiomeDef[^>]*>(?:(?!</BiomeDef>).)*?<defName>%s</defName>.*?</BiomeDef>'%re.escape(dn),s,re.S)
        blk=m.group(0); nb=re.sub(r'<texture>[^<]*</texture>',f'<texture>World/Biomes/{newname}</texture>',blk,count=1)
        assert nb!=blk or f'World/Biomes/{newname}<' in blk,(dn,'no texture tag')
        open(path,'w').write(s[:m.start()]+nb+s[m.end():])
    res.append((dn,key,f'{tier}/{mod}',newname,tex,ok,st if not ok else r.stdout.strip().splitlines()[-1][:60],r.stderr.strip()[-200:] if not ok else ''))
json.dump(res,open(f'{T}/apply_result.json','w'),indent=1)
for x in res: print(x[0],x[3],x[5],x[6][:70],x[7][:100])
