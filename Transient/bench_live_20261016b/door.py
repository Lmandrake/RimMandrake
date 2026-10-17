from afk_lib import *
sys.stdout.reconfigure(encoding="utf-8",errors="replace")
def rot(x,z): 
    r=B.call("jawa/static_call",type="RimWorld.DoorUtility",method="DoorRotationAt",args="%d,%d|0|false"%(x,z)); return str(r.get("result"))
print("sluice E-W canal (80,214):",rot(80,214))
print(B.call("jawa/build_batch",ops="RM_SecurityGrateDoor:84,214",stuff="Steel",faction="player",wipeExisting=False).get("message"))
print("grate E-W canal (84,214):",rot(84,214))
for z in (215,216,217):
    r=B.call("jawa/flowworks_excavation_drive",x=85,z=z,deepenLevels=1,setFill=-1); 
print("dug N-S:",[(r["x"],r["z"],r["d"]) for r in rect(85,213,1,8)])
print(B.call("jawa/build_batch",ops="RM_Sluice:85,216;RM_SecurityGrateDoor:85,217",stuff="Steel",faction="player",wipeExisting=False).get("message"))
print("sluice N-S (85,216):",rot(85,216),"grate N-S (85,217):",rot(85,217))
print("control plain ground (85,219) no door:",rot(85,219))
