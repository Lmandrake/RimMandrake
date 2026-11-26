import sys
from PIL import Image
out,*ps=sys.argv[1:]
n=len(ps); cols=int(2 if n<=4 else 3); w=900 if n<=4 else 640
ims=[Image.open(p).convert("RGB") for p in ps]
for i in ims: i.thumbnail((w,w))
h=max(i.size[1] for i in ims); rows=-(-n//cols)
s=Image.new("RGB",(cols*w,rows*h))
for k,i in enumerate(ims): s.paste(i,((k%cols)*w,(k//cols)*h))
s.save(out,quality=82)
