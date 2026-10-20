"""Shared bridge helpers for the 2026-10-20c sweep (python.exe, repo root)."""
import sys, json, os, time
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils"))
import rimbridge_client as rb
PLAYER_LOG = r"C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Player.log"
_h, _p, _t = rb.resolve_endpoint()
S = rb.RimBridge(host=_h, port=_p, token=_t, timeout=300.0); S.connect()


def call(tool, **kw):
    try:
        r = S.call(tool, kw) or {}
    except Exception as e:
        return {"success": False, "error": "call failed: %r" % (e,)}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r


def j(x, n=400):
    return json.dumps(x, default=str, ensure_ascii=True)[:n]


def log_clear():
    return call("jawa/static_call", type="Verse.Log", method="Clear")


def log_lines():
    with open(PLAYER_LOG, encoding="utf-8", errors="replace") as f:
        return f.read().splitlines()


def log_since(mark):
    return log_lines()[mark:]


def out(name):
    return os.path.join(HERE, name)
