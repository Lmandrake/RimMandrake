import numpy as np
from PIL import Image, ImageDraw, ImageFont

g = np.load('ship_grid.npy')
GH, GW = g.shape
MAP=250; PX=5; IMGW=IMGH=MAP*PX

col = {'M':(150,170,205),'K':(120,120,128),'.':(95,95,100),'F':(196,150,205),
 'E':(214,120,120),'D':(150,190,150),'B':(210,140,90),'C':(225,205,120),
 'A':(150,130,95),'R':(120,160,200),'T':(60,60,66),'S':(180,90,90)}

rng=np.random.default_rng(7)
base=np.array([206,180,132]); noise=rng.integers(-10,10,size=(MAP,MAP,3))
arr=np.clip(base+noise,150,235).astype('uint8')
img=Image.fromarray(np.kron(arr,np.ones((PX,PX,1),dtype='uint8')),'RGB')
draw=ImageDraw.Draw(img)

ox,oy=104,86
def font(sz):
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
        try:return ImageFont.truetype(p,sz)
        except:pass
    return ImageFont.load_default()
fT=font(30);fL=font(17);fS=font(15);fW=font(13)

for k in range(0,MAP+1,10):
    lw=2 if k%50==0 else 1
    cc=(150,132,96) if k%50==0 else (188,166,122)
    draw.line([(k*PX,0),(k*PX,IMGH)],fill=cc,width=lw)
    draw.line([(0,k*PX),(IMGW,k*PX)],fill=cc,width=lw)

def paint(dr,gx,gy,ppt,x,y):
    for yy in range(GH):
        for xx in range(GW):
            c=g[yy,xx]
            if c=='':continue
            X=x+(xx)*ppt; Y=y+(yy)*ppt
            dr.rectangle([X,Y,X+ppt,Y+ppt],fill=col.get(c,(255,0,255)),
                         outline=(15,15,18),width=1)

# ship on the map
paint(draw,ox,oy,PX,ox*PX,oy*PX)

draw.text((14,10),"Gravship footprint on a typical 250 x 250 RimWorld map",font=fT,fill=(25,20,16))
draw.text((14,46),"1,732 of 2,000 connected substructure tiles  •  each square = 1 tile  •  hull covers ~2.8% of the map's 62,500 tiles",font=fS,fill=(55,45,36))

# scale bar 50 tiles
sx,sy=14,IMGH-40
draw.rectangle([sx,sy,sx+50*PX,sy+10],fill=(40,35,30))
draw.text((sx,sy-20),"50 tiles",font=fS,fill=(40,35,30))

# LEGEND (top-right, sized to fit)
order=[('M','Command core'),('K','Keel / utility spine'),('F','Wing F - precision'),
 ('E','Wing E - adv. materials (HOT)'),('D','Wing D - textile / ammo'),
 ('B','Wing B - bulk / dirty (HOT)'),('C','Wing C - food'),
 ('A','Wing A - raw extraction'),('R','Habitat ring'),('T','Carbonite bay'),
 ('S','Stern - thrusters/fuel/power')]
LW=316
lx=IMGW-LW-14; ly=78
draw.rectangle([lx,ly,lx+LW,ly+len(order)*25+16],fill=(246,241,231),outline=(90,80,66),width=2)
for i,(c,name) in enumerate(order):
    yy=ly+10+i*25
    draw.rectangle([lx+12,yy,lx+32,yy+20],fill=col[c],outline=(15,15,18),width=1)
    draw.text((lx+42,yy+2),name,font=fL,fill=(28,22,18))

# ZOOM INSET (bottom-right): higher resolution of the ship so tile lines are crisp
ZP=9
zw=GW*ZP+2; zh=GH*ZP+2
inset=Image.new('RGB',(zw,zh),(232,224,208))
zdraw=ImageDraw.Draw(inset)
paint(zdraw,0,0,ZP,1,1)
# frame + place
iy=IMGH-zh-14; ix=IMGW-zw-14
img.paste(inset,(ix,iy))
draw.rectangle([ix-1,iy-1,ix+zw,iy+zh],outline=(60,50,40),width=2)
draw.text((ix,iy-24),"Detail: bow at top, stern at bottom  (1 square = 1 tile)",font=fW,fill=(40,35,30))
# connector note
draw.text((ox*PX-150,(oy+GH//2)*PX),"actual size on map",font=fW,fill=(35,30,25))
draw.line([(ox*PX-24,(oy+GH//2)*PX+7),(ox*PX-4,(oy+GH//2)*PX+7)],fill=(35,30,25),width=2)

img.save('ship_scale_map.png')
print("saved",img.size,"inset",inset.size)
