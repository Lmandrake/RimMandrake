# -*- coding: utf-8 -*-
"""TEMPLATE_ENGINE_ACCEPTANCE_1: compile the dwelling into a transportable call list + the plan."""
import sys, json
sys.path.insert(0, "/mnt/d/Luke/dev/Rimworld/src/RimMandrake/Utils")
from rimplace.cli import _build, compile_calls
import argparse
a = argparse.Namespace(command="calls", template="dwelling", rect="170,170,18,10",
                       faction="Jawa_IndigenousTribes", rooms=3, occupants=4, wealth=None,
                       tech=None, defended=None, condition=None, climate=None,
                       temperature=None, seed=1, roof=False, json=False)
path, plan = _build(a)
calls = compile_calls(plan, faction=a.faction)
out = [{"tool": c["tool"], "params": {k: v for k, v in c["params"].items() if k != "_dryRun"}}
       for c in calls]
json.dump(out, open("/mnt/d/Luke/dev/Rimworld/world/_lf/tpl_calls.json", "w"), indent=1)
open("/mnt/d/Luke/dev/Rimworld/world/_lf/tpl_plan.json","w").write(plan.to_json())
print("calls:", len(out), "| ops:", sum(len(str(c['params'].get('ops','')).split(';')) if c['params'].get('ops') else 0 for c in out))
print("tools:", sorted({c['tool'] for c in out}))
pj = json.loads(plan.to_json())
print("plan keys:", sorted(pj.keys()))
for k in pj:
    v = pj[k]
    print("   %-14s %s"%(k, (str(len(v)) + " entries") if isinstance(v,(list,dict)) else str(v)[:60]))
