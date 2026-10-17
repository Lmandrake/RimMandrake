"""One bridge call from argv: call.py <tool> '<json params>'  (python.exe)."""
import sys, json, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
h, p, tok = resolve_endpoint()
with RimBridge(h, p, tok) as rb:
    for i in range(1, len(sys.argv), 2):
        print(json.dumps(rb.call(sys.argv[i], json.loads(sys.argv[i + 1])))[:3000])
