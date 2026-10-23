import sys, json
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
def call(tool, args=None, timeout=60):
    h,p,t = resolve_endpoint()
    with RimBridge(h,p,t) as rb:
        return rb.call(tool, args or {})
if __name__ == "__main__":
    args = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    r = call(sys.argv[1], args)
    s = json.dumps(r, indent=None, default=str)
    print(s[:int(sys.argv[3]) if len(sys.argv) > 3 else 3000])
