"""inspect_things.py id[,id...]: jawa/inspect_string of things on the live map (visit 12 strange-thing probe)."""
import sys, json, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 6, "src", "RimMandrake", "Utils"))
import validation_core as V
B = V.Bridge()
for t in (B.call("jawa/inspect_string", thingIds=sys.argv[1]) or {}).get("things") or []:
    print(t.get("id"), "|", " | ".join(t.get("inspect") or []))
