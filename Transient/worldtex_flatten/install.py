"""Install the flattened textures through the art ledger (same route as the original apply.py). usage: install.py [--dry-run]"""
import json,subprocess,sys
OWN="Yes, file a ticket for Bench to include the worldmap adjustment in its current work."
P=json.load(open("Transient/worldtex_flatten/plan.json")); bad=0
for r in P:
    if r["action"]!="flatten": continue
    x=subprocess.run(["python3","src/RimMandrake/Utils/art/art.py","install",r["mod"],r["rel"],"--file",r["stage"],"--owner-said",OWN]+sys.argv[1:],capture_output=True,text=True)
    out=(x.stdout+x.stderr).strip().splitlines(); bad+=x.returncode!=0
    print(x.returncode, r["mod"], r["rel"], (out[-1] if out else "")[:110])
print("failures",bad)
