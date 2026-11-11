import sys,os,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'src/RimMandrake/Utils'))
os.environ['RIMFLOW_SEAT']='BENCH'
os.environ.pop('RM_FOCUS_OPT_IN',None)
from northstar_driver import live_session as L
if sys.argv[1]=='stop': L.stop_game()
elif sys.argv[1]=='launch': L.launch_and_wait()
print(json.dumps({'action':sys.argv[1],'running_after':L.running(),'time':time.time()}))
