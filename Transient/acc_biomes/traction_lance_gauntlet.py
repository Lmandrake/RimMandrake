"""WEBWORK_TRACTION_LANCE_BUILD_1 A3 gauntlet via RM_TractionLanceProof (jawa/static_call). Records each raw result.
Run on a map with a clear 13x5 strip; python.exe. Findings: read the outcome strings, none are asserted here."""
import sys, json
sys.path.insert(0, r"src\RimMandrake\Utils")
import rimbridge_client as rbc
host,port,token=rbc.resolve_endpoint()
T="RimMandrake.CreatureBehaviors.RM_TractionLanceProof"
out=[]
with rbc.RimBridge(host,port,token,timeout=120.0) as rb:
    def sc(m,args):
        r=rb.call("jawa/static_call",{"type":T,"method":m,"args":args.replace(",","|")},check=False)
        res=str((r or {}).get("result",r))[:400]; out.append((m,args,res)); print(m,args,"->",res)
    sc("ProofStuffTable","")
    for stuff in ("Cloth","DevilstrandCloth","Hyperweave"):
        for mode in ("raider","wall","unmanned","heavy","downed"):
            sc("ProofPull",f"{stuff},{mode}")
json.dump(out,open(r"Transient\acc_biomes\traction_lance_results.json","w"),indent=1)
