#!/usr/bin/env python3
"""Summarise /tmp/agp_bulk_plan.json (bulk_accept_renders.py plan, the hourly donor-render installer's planner) for AgariluxPrime."""
import json
d = json.load(open('/tmp/agp_bulk_plan.json')); s = json.dumps(d)
print("bulk_accept_renders.py plan (the hourly donor-render installer's planner), run after the retire; plan generated", d.get("generated"))
print("  artpipe jobs named *agarilux* in done/ (20,378 files; a full-content grep timed out) whose JSON names the old slot: one,")
print("  dregen_RM_AgariluxPrime_ABAgariluxPrime_v1; pending/ and active/ hold no *agariluxprime* job. Its install_to is")
print("  src/RimMandrake/TheRot/Textures/Things/Plants/AB_AgariluxPrime.png (retired).")
print("  occurrences of 'dregen_RM_AgariluxPrime' anywhere in the plan (rows, repoints, retires, every skip list):", s.count('dregen_RM_AgariluxPrime'))
print("  occurrences of 'AgariluxPrime' anywhere in the plan:", s.count('AgariluxPrime'))
print("  sanity probe -- dregen_ jobs the plan does see:", s.count('dregen_'), "(the instrument sees dregen jobs)")
print("  plan totals:", {k: len(v) for k, v in d.items() if isinstance(v, list)}, {k: len(v) for k, v in d['skipped'].items()})
