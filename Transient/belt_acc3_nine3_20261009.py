import sys,json
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
sc=S.Scene("nine",30,30,9,9)
S.run(3000)
print("smelter",sc.find("ElectricSmelter").get("id"), "hulks", json.dumps(S.call("jawa/list_things",rect=sc.rect,limit=30).get("perDef")))
print(json.dumps(S.call("jawa/drain_log",contains="Ninefold",limit=5))[:600])
