# shot.py <name> <ticks> : advance, print hostile+warden positions, cell-rect capture of the moat
import sys,json,shutil
sys.path.insert(0,r'src/RimMandrake/Utils'); sys.path.insert(0,r'src/RimMandrake/Utils/modcheck')
import validation_core as V
B=V.Bridge(); B.stop_on='clock_discontinuity,modal_stuck,colony_loss,cancel'
n=int(sys.argv[2])
if n: B.ticks(n)
d=B.call('jawa/site_state')
print([(p['id'],p.get('label'),p['x'],p['z'],p.get('job')) for p in d['pawns'] if 55<p['x']<76 and 55<p['z']<76])
r=B.call('rimworld/screenshot_cell_rect',x=59,z=58,width=14,height=14,fileName=sys.argv[1],suppressMessage=True)
print(r.get('path'))
