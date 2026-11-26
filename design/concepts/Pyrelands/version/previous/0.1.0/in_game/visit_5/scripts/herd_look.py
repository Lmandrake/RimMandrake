"""Visit 5 diagnostic (no verdict): after ullai_and_giant on the same map (runner '+' item), where are the ullai, and does a
cell-rect capture over them show them? Prints every living RM_Ullai's cell and the capture path. Exit 0 always."""
import json, os, sys
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 7))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils"))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils", "modcheck"))
from rimbridge_client import RimBridge, resolve_endpoint  # noqa: E402
import clockgate  # noqa: E402
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as raw:
    def call(name, **kw):
        return clockgate._unwrap(raw.call(name, kw))
    pawns = (call("jawa/list_pawns", limit=1000) or {}).get("pawns") or []
    ull = [(p.get("id"), p.get("x"), p.get("z"), p.get("dead")) for p in pawns if p.get("kindDef") == "RM_Ullai"]
    print("ULLAI", len(ull), json.dumps(ull)[:2000])
    st = (call("jawa/site_state") or {}).get("pawns") or []
    su = [(p.get("id"), p.get("x"), p.get("z"), p.get("kindDef") or p.get("def")) for p in st if "Ullai" in str(p)]
    print("SITE_STATE_ULLAI", len(su), json.dumps(su)[:1500])
    live = [(x, z) for _, x, z, dead in ull if not dead and x is not None]
    if live:
        xs, zs = [c[0] for c in live], [c[1] for c in live]
        x0, z0, x1, z1 = min(xs), min(zs), max(xs), max(zs)
        call("jawa/clear_ui")
        r = call("rimworld/screenshot_cell_rect", x=x0 - 3, z=z0 - 3, width=x1 - x0 + 7, height=z1 - z0 + 7, paddingCells=1)
        print("SHOT", json.dumps({k: r.get(k) for k in ("path", "success", "message")})[:600])
