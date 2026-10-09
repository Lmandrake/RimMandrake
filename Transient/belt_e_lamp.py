import sys,json
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
call=S.call
with S.Scene("lampe",60,60,12,10) as sc:
    sc.room(); sc.grid()
    x,z=sc.abs(5,3)
    print(call("jawa/build_batch",ops=f"StandingLamp:{x},{z}",faction="PlayerColony").get("message"))
    call("jawa/map_commit",power=True,regions=True)
    pid=sc.colonist(8,8); sc.fuel(pid,n=75,ticks=1500)
    print("net",sc.netsize("StandingLamp"))
    S.run(1500)
    l=sc.find("StandingLamp"); print("LAMP",sc.inspect(l["id"])[:500])
    S.run(3000)
    print("LAMP2",sc.inspect(l["id"])[:500])
