import sys, os
from PIL import Image, ImageDraw
A="/mnt/d/ClaudeWork/rimmandrake/artpipe/_artsrc"
B="/home/mandrake/rm/bench/src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/Hose/"
LOOKS={"scrapper":"","industrial":"Styles/Industrial/","modern":"Styles/Modern/","futuristic":"Styles/Futuristic/"}
ST={"stored":"PumpHookup","laid":"Deployed"}
out=Image.new("RGBA",(3*260*2+20, 4*280),(122,104,84,255)); d=ImageDraw.Draw(out)
for r,(lk,sub) in enumerate(LOOKS.items()):
  for c,(st,tex) in enumerate(ST.items()):
    x0=c*(3*260+20)
    for k,face in enumerate(["west","north","south"]):
      p = B+sub+f"Reel_{tex}.png" if face=="west" else f"{A}/reelns_{lk}_{st}_{face}_v1/reelns_{lk}_{st}_{face}_v1.png"
      if os.path.exists(p):
        im=Image.open(p).convert("RGBA")
        if im.size!=(256,256): d.text((x0+k*260+4,r*280+262),f"{im.size}",fill=(255,255,0))
        im=im.resize((256,256))
        out.alpha_composite(im,(x0+k*260,r*280))
      d.text((x0+k*260+4,r*280+4),f"{lk} {st} {face}",fill=(255,255,255))
out.save(sys.argv[1])
