"""One bridge call per invocation, fresh connection. usage: python.exe bx.py TOOL '{json args}' [timeout]"""
import sys, json
sys.path.insert(0, r"D:\Luke\dev\RimMandrake\src\RimMandrake\Utils")
import rimbridge_client as rb


def call(tool, args=None, timeout=120.0):
    h, p, t = rb.resolve_endpoint()
    S = rb.RimBridge(host=h, port=p, token=t, timeout=timeout)
    S.connect()
    try:
        r = S.call(tool, args or {}) or {}
    finally:
        try:
            S.close()
        except Exception:
            pass
    if isinstance(r, dict) and r.get("content"):
        try:
            r = json.loads(r["content"][0]["text"])
        except Exception:
            pass
    if isinstance(r, dict):
        r.pop("operation", None)
    return r


if __name__ == "__main__":
    a = json.loads(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2] else {}
    to = float(sys.argv[3]) if len(sys.argv) > 3 else 120.0
    print(json.dumps(call(sys.argv[1], a, to), indent=1, default=str))
