"""Like call.py but prints top-level keys compactly (python.exe): callj.py <tool> '<json>'"""
import sys, json, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
h, p, tok = resolve_endpoint()
with RimBridge(h, p, tok) as rb:
    for i in range(1, len(sys.argv), 2):
        d = rb.call(sys.argv[i], json.loads(sys.argv[i + 1]))
        for k, v in d.items():
            if k in ("operation", "state"): continue
            print(k, json.dumps(v)[:int(os.environ.get("W", "600")) if not os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), "WIDE")) else 100000])
        print("----")
