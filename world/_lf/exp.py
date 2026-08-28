import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t); b.connect()
r = b.call('jawa/world_tile_export', {"path": r"D:\Luke\dev\Rimworld\world\_lf\live_tiles.csv",
                                      "format":"csv", "extended": True})
print("export", json.dumps(r)[:400])
