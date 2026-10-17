"""ui.py  click <substr label> | dump | shot <out>  -- real OS click on the game's dialog via layout rects. Focus given back after."""
import sys,json,os,ctypes,time
sys.stdout.reconfigure(encoding="utf-8")
os.environ["RM_FOCUS_OPT_IN"]="focus"
sys.path.insert(0,"src/RimMandrake/Utils")
from rimbridge_client import RimBridge, resolve_endpoint
from game_focus import focus_game, restore_focus
user32=ctypes.windll.user32; ctypes.windll.shcore.SetProcessDpiAwareness(2)
h,p,t=resolve_endpoint()
def layout(rb):
    r=rb.call("rimworld/get_ui_layout",{})
    out=[]
    for s in r["surfaces"]:
        if "Dialog" in s["type"] or "Window_" in s["type"] or "Dialog" in s.get("surfaceTargetId",""):
            for e in s["elements"]:
                if e["kind"]!="group": out.append((s["type"],e))
    return out
def show(els):
    for ty,e in els:
        print(e["kind"],repr(e.get("label"))[:70],{k:v for k,v in e.items() if k in("isChecked","disabled","valueText","actionable")},e["screenRect"])
cmd=sys.argv[1]
prev=focus_game()
try:
    time.sleep(0.8)
    with RimBridge(h,p,t) as rb:
        els=layout(rb)
        if cmd=="dump": show(els)
        elif cmd=="shot":
            import subprocess; subprocess.run(["python.exe","src/RimMandrake/Utils/system_screenshot.py",sys.argv[2]]); hwnd=user32.FindWindowW(None,"RimWorld by Ludeon Studios")
            class R(ctypes.Structure): _fields_=[("l",ctypes.c_long),("t",ctypes.c_long),("r",ctypes.c_long),("b",ctypes.c_long)]
            r=R(); user32.GetWindowRect(hwnd,ctypes.byref(r)); print("win",r.l,r.t,r.r,r.b)
        elif cmd=="click":
            q=sys.argv[2]; idx=int(sys.argv[3]) if len(sys.argv)>3 else 0; dy=int(sys.argv[4]) if len(sys.argv)>4 else 0
            m=[e for ty,e in els if e.get("actionable") and q.lower() in (e.get("label") or "").lower()]
            e=m[idx]; r=e["screenRect"]
            x=int(r["x"]+r["width"]/2); y=int(r["y"]+r["height"]/2)
            hwnd=user32.FindWindowW(None,"RimWorld by Ludeon Studios")
            class P(ctypes.Structure): _fields_=[("x",ctypes.c_long),("y",ctypes.c_long)]
            pt=P(0,0); user32.ClientToScreen(hwnd,ctypes.byref(pt))
            X,Y=pt.x+x,pt.y+y+dy
            user32.SetCursorPos(X,Y); time.sleep(0.15)
            user32.mouse_event(2,0,0,0,0); time.sleep(0.08); user32.mouse_event(4,0,0,0,0); time.sleep(0.6)
            print("clicked",e.get("label"),X,Y)
            show(layout(rb))
finally:
    restore_focus(prev)
