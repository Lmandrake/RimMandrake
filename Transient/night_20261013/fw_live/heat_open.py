"""LIQUID_HEAT_PUSH_1 A3: an open boiling patch identifies hot but reads outdoor, and the outdoor temp beside it is unchanged."""
import sys,os,json
sys.path.insert(0, os.path.join(os.getcwd(),"src","RimMandrake","FlowWorks","northstar"))
import proof_hose as PH
B=PH.PB()
H="RimMandrake.FlowWorks.RM_LiquidHeatProof"
def heat(c): return B.call("jawa/static_call", type=H, method="ProofHeat", args="%d,%d"%c).get("result")
patch=[(161+dx,94+dz) for dx in range(3) for dz in range(3)]
side=(165,95); far=(161,104)
print(B.call("jawa/set_terrain_batch", ops="RM_WaterBoilingShallow:161,94,3,3").get("success"))
out={"t0":{"patch":heat((162,95)),"beside":heat(side),"far":heat(far)}}
B.ticks(1500)
out["t1"]={"patch":heat((162,95)),"beside":heat(side),"far":heat(far)}
print(json.dumps(out,indent=1))
json.dump(out,open("heat_open.json","w"),indent=1)
