import sys, time, shutil, os
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
SH = r"D:\Luke\dev\Rimworld\Transient\final_review\beauty"
with RimBridge(host, port, token) as rb:
    for fid in (67, 68, 86):
        r = rb.call("jawa/world_features_set", {"action": "edit", "featureId": fid, "maxDrawSizeInTiles": 0.01})
        assert r.get("success") is True, r
    rb.call("jawa/world_commit", {})
    time.sleep(0.5)
    rb.call("jawa/world_view", {"centerTile": 11942, "altitude": 430, "northUp": True})
    time.sleep(1.5)
    s = rb.call("rimworld/take_screenshot", {"suppressMessage": True})
    shutil.copy(s.get("path") or s.get("filePath"), os.path.join(SH, "A2_crater_nolabel.png"))
    # restore
    for fid in (67, 68, 86):
        r = rb.call("jawa/world_features_set", {"action": "edit", "featureId": fid, "maxDrawSizeInTiles": 10.0})
        assert r.get("success") is True, r
    rb.call("jawa/world_commit", {})
    g = rb.call("jawa/world_features_get", {"limit": 100})
    vals = {x['uniqueID']: x['maxDrawSizeInTiles'] for x in g['features'] if x['uniqueID'] in (67,68,86)}
    print("restored:", vals)
