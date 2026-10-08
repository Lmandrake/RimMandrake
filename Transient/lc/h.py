import sys, os, json
root=os.getcwd()
U=os.path.join(root,"src","RimMandrake","Utils")
sys.path.insert(0,U)
from rimdrive import Session
def S(): return Session(lock=None, focus=False)
def pj(x): print(json.dumps(x, default=str)[:3000])
def wait(s,n,chunk=1500):
    st=s._ticks(); adv=0; calls=0
    while adv<n and calls<80:
        s.call("rimworld/step_game_ticks",ticks=min(chunk,n-adv),pauseFirst=True); calls+=1
        adv=s._ticks()-st
    return adv
def things(s,defn,rect=None,limit=200):
    kw=dict(defName=defn,limit=limit)
    if rect: kw["rect"]=rect
    r=s.call("jawa/list_things",**kw); return r
def pawns(s,**kw): return s.call("jawa/list_pawns",**kw).get("pawns",[])
