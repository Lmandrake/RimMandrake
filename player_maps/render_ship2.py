import numpy as np, json
from PIL import Image, ImageDraw, ImageFont
g=np.load('ship_grid.npy'); GH,GW=g.shape
place=json.load(open('placements.json'))
col={'M':(150,170,205),'K':(120,120,128),'.':(95,95,100),'F':(196,150,205),
 'E':(214,120,120),'D':(150,190,150),'B':(210,140,90),'C':(225,205,120),
 'A':(150,130,95),'R':(120,160,200),'T':(60,60,66),'S':(180,90,90)}
def font(sz):
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf","/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
        try:return ImageFont.truetype(p,sz)
        except:pass
    return ImageFont.load_default()
fT=font(30);fP=font(22);fL=font(17);fS=font(15);fW=font(14)

# ---------- LEFT PANEL: true scale on ACTUAL 250x250 map ----------
MAP=250; PX=4; MW=MAP*PX  # 1000
rng=np.random.default_rng(7)
# A more map-like desert: sand base + a few rock outcrops + a dry riverbed + scattered
base=np.full((MAP,MAP,3),[204,178,130],dtype=int)
base+=rng.integers(-9,9,size=(MAP,MAP,3))
# rocky hills (mountain) in NE corner + SW
def blob(cx,cy,r,color,jit=6):
    yy,xx=np.mgrid[0:MAP,0:MAP]
    m=(xx-cx)**2+(yy-cy)**2 < (r+rng.integers(-jit,jit,size=(MAP,MAP)))**2
    base[m]=np.array(color)+rng.integers(-8,8,size=(m.sum(),3))
blob(215,40,42,[120,112,104])   # rocky NE
blob(30,210,34,[128,120,110])   # rocky SW
blob(70,60,18,[96,90,84])       # small crag
# dry riverbed diagonal (lighter sand / gravel)
yy,xx=np.mgrid[0:MAP,0:MAP]
river=np.abs((yy - (0.35*xx+150)))<7
base[river]=[196,186,150]
base=np.clip(base,70,240).astype('uint8')
left=Image.fromarray(np.kron(base,np.ones((PX,PX,1),dtype='uint8')),'RGB')
dL=ImageDraw.Draw(left)
for k in range(0,MAP+1,10):
    lw=2 if k%50==0 else 1
    cc=(150,132,96) if k%50==0 else (185,164,120)
    dL.line([(k*PX,0),(k*PX,MW)],fill=cc,width=lw); dL.line([(0,k*PX),(MW,k*PX)],fill=cc,width=lw)
ox,oy=104,86
for y in range(GH):
    for x in range(GW):
        c=g[y,x]
        if c=='':continue
        X=(ox+x)*PX;Y=(oy+y)*PX
        dL.rectangle([X,Y,X+PX,Y+PX],fill=col[c],outline=(15,15,18),width=1)
# engine/extender markers on left too (small)
for typ,cy,ccx,r in place:
    X=(ox+ccx)*PX+PX//2;Y=(oy+cy)*PX+PX//2
    rr=6 if typ=='ENGINE' else 4
    dL.ellipse([X-rr,Y-rr,X+rr,Y+rr],fill=(255,240,60) if typ=='ENGINE' else (60,220,255),outline=(0,0,0))
# scale bar
sx,sy=14,MW-38
dL.rectangle([sx,sy,sx+50*PX,sy+9],fill=(35,30,25)); dL.text((sx,sy-20),"50 tiles",font=fS,fill=(35,30,25))
dL.text((14,10),"TRUE SCALE on a 250 x 250 desert map",font=fP,fill=(25,20,16))
dL.text((14,40),"1,732 tiles = ~2.8% of the map's 62,500",font=fS,fill=(55,45,36))
# arrow to ship
dL.text(((ox-24)*PX,(oy+GH//2)*PX-8),"ship",font=fW,fill=(30,25,20))

# ---------- RIGHT PANEL: detail with engine + extender coverage ----------
ZP=11
zw=GW*ZP; zh=GH*ZP
right=Image.new('RGB',(zw,zh),(236,229,214))
dR=ImageDraw.Draw(right)
# draw coverage disks faint first (engine r19, ext r16)
overlay=Image.new('RGBA',(zw,zh),(0,0,0,0)); dO=ImageDraw.Draw(overlay)
for typ,cy,ccx,r in place:
    X=ccx*ZP+ZP//2;Y=cy*ZP+ZP//2;R=r*ZP
    fillc=(255,235,60,26) if typ=='ENGINE' else (60,200,255,20)
    dO.ellipse([X-R,Y-R,X+R,Y+R],fill=fillc)
right=Image.alpha_composite(right.convert('RGBA'),overlay).convert('RGB')
dR=ImageDraw.Draw(right)
for y in range(GH):
    for x in range(GW):
        c=g[y,x]
        if c=='':continue
        X=x*ZP;Y=y*ZP
        dR.rectangle([X,Y,X+ZP,Y+ZP],fill=col[c],outline=(15,15,18),width=1)
# engine + extender glyphs
for typ,cy,ccx,r in place:
    X=ccx*ZP+ZP//2;Y=cy*ZP+ZP//2
    if typ=='ENGINE':
        dR.ellipse([X-9,Y-9,X+9,Y+9],fill=(255,235,60),outline=(0,0,0),width=2)
        dR.text((X-5,Y-8),"G",font=fW,fill=(0,0,0))
    else:
        dR.ellipse([X-7,Y-7,X+7,Y+7],fill=(60,200,255),outline=(0,0,0),width=2)
dR.text((6,4),"DETAIL — 1 square = 1 tile · G=grav engine (r19) · blue=extender (r16)",font=fW,fill=(20,16,12))

# ---------- COMPOSE ----------
pad=20; legw=372
H=max(MW,zh)+120
Wt=MW+pad+zw+pad+legw
canvas=Image.new('RGB',(Wt,H+30),(250,247,240))
dC=ImageDraw.Draw(canvas)
dC.text((14,6),"Gravship footprint & extender coverage",font=fT,fill=(20,16,12))
canvas.paste(left,(0,60))
canvas.paste(right,(MW+pad,60))
dC.rectangle([MW+pad-1,59,MW+pad+zw,60+zh],outline=(60,50,40),width=2)
# legend far right
lx=MW+pad+zw+pad; ly=60
order=[('M','Command core'),('K','Keel / utility spine'),('F','Wing F - precision'),
 ('E','Wing E - adv. materials (HOT)'),('D','Wing D - textile / ammo'),
 ('B','Wing B - bulk / dirty (HOT)'),('C','Wing C - food'),('A','Wing A - raw extraction'),
 ('R','Habitat ring'),('T','Carbonite bay'),('S','Stern - thrusters/fuel/power')]
dC.rectangle([lx,ly,lx+legw-14,ly+len(order)*25+70],fill=(246,241,231),outline=(90,80,66),width=2)
for i,(c,name) in enumerate(order):
    yy=ly+10+i*25
    dC.rectangle([lx+12,yy,lx+32,yy+20],fill=col[c],outline=(15,15,18),width=1)
    dC.text((lx+42,yy+2),name,font=fL,fill=(28,22,18))
yy=ly+10+len(order)*25+6
dC.ellipse([lx+12,yy,lx+30,yy+18],fill=(255,235,60),outline=(0,0,0),width=2); dC.text((lx+42,yy),"Grav engine (radius 19)",font=fL,fill=(28,22,18))
dC.ellipse([lx+12,yy+26,lx+28,yy+42],fill=(60,200,255),outline=(0,0,0),width=2); dC.text((lx+42,yy+26),"Field extender x6 (radius 16)",font=fL,fill=(28,22,18))
canvas.save('ship_scale_map.png'); print("saved",canvas.size)
