from PIL import Image, ImageDraw
R='/home/mandrake/rm/bench/src/RimMandrake/FlowWorks/Textures/'
L='/home/mandrake/rm/bench/Transient/bench_live_20261016/'
O='/home/mandrake/rm/bench/Transient/river_hose_art_review_2026-10-16/'
C=64
def lab(img,t):
    o=Image.new('RGB',(img.width,img.height+18),(20,20,20)); o.paste(img.convert('RGB'),(0,18)); ImageDraw.Draw(o).text((4,3),t,fill=(255,255,255)); return o
def scene(look):
    b=Image.new('RGBA',(6*C,3*C),(112,88,66,255))
    def p(path,x,y,w,h,ds):
        t=Image.open(path).convert('RGBA').resize((int(ds*C),int(ds*C)),Image.LANCZOS)
        b.alpha_composite(t,(int(x*C+w*C/2-t.width/2),int(y*C+h*C/2-t.height/2)))
    st=R+'RimMandrake/FlowWorks/Hose/Styles/'+look+'/Reel_PumpHookup.png'
    p(st,0.5,0.5,2,2,2.8)                      # reel 2x2 at cells (0.5..2.5)
    p(R+'Things/Building/FlowWorks/Machinery/RM_LiquidPump.png',2.5,1,1,1,1)  # pump 1x1 adjacent
    p(R+'RimMandrake/FlowWorks/Tank/%s/RM_LiquidTank.png'%look,3.5,0.5,2,2,2)  # tank 2x2 adjacent
    return b
for look in ['Industrial','Modern']:
    s=scene(look); lab(s.resize((s.width*2,s.height*2),Image.LANCZOS),'OFFLINE composite 2x of 64px/cell: reel(2x2, drawSize 2.8) | pump(1x1) | tank(2x2) adjacent, %s look (today; no joinFittings)'%look).save(O+'reel_pump_tank_adjacent_%s.png'%look)
im=Image.open(L+'owner_hose_1.jpg'); k=3467/2000
def crop(name,box,z,t):
    c=im.crop(tuple(int(v*k) for v in box)); c=c.resize((c.width*z,c.height*z),Image.LANCZOS) if z>1 else c
    lab(c,t).save(O+name)
crop('live_pump_reel_hose_crop.png',(600,440,940,640),1,'LIVE capture (owner_hose_1.jpg, 2026-10-16) crop: pump + hose coupling meeting rigid pipe; hose reel off-screen above (loose coils)')
crop('live_pipe_tank_crop.png',(820,350,1280,610),1,'LIVE capture crop: rigid pipe running to tank, hose coupling (brass) on pipe')
crop('live_reel_hose_crop.png',(660,130,940,520),1,'LIVE capture crop: reel (dark rectangle), orange hose loops')
print('ok')
