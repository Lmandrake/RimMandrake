from PIL import Image
T='Transient/drawbridge_bollards_20261023'
old=Image.open('Transient/drawbridge_cables_20261023/art_eval/scale_Timber.png').convert('RGB'); pawn=old.crop((600,0,768,288))
for look in ['Scrapper','Industrial','Modern','Futuristic']:
  for mat in ['Timber','Steel']:
    im=Image.open(f'{T}/after/after_{look}_{mat}_lowered_E.png').convert('RGB'); im.paste(pawn,(600,0)); im.save(f'{T}/art_eval/scale_{look}_{mat}.png')
    strip=Image.new('RGB',(768,256),(140,120,90))
    for k,f in enumerate(['south','east','north']):
      a=Image.open(f'{T}/cand/RimMandrake/FlowWorks/SuspensionBridge/{look}/RM_SuspensionAnchor_{mat}_{f}.png').convert('RGBA'); strip.paste(a,(k*256,0),a)
    strip.save(f'{T}/art_eval/sprites_{look}_{mat}.png')
