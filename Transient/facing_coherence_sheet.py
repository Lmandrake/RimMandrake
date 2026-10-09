import sys, json
from pathlib import Path
from PIL import Image, ImageDraw
R=Path('/home/mandrake/rm/bench')
def sheet(stems, out, cell=170):
    W=cell*3+230; H=cell*len(stems)
    im=Image.new('RGB',(W,H),(118,108,98)); d=ImageDraw.Draw(im)
    for i,s in enumerate(stems):
        d.text((4,i*cell+4),f'{i+1}. '+Path(s).name+'\n(N | S | E)',fill=(255,255,255))
        for j,f in enumerate(('north','south','east')):
            t=Image.open(f'{R}/{s}_{f}.png').convert('RGBA'); t.thumbnail((cell-4,cell-4))
            im.paste(t,(230+j*cell,i*cell+2),t)
    im.save(out)
if __name__=='__main__':
    stems=json.load(open(sys.argv[1])); sheet(stems,sys.argv[2])
