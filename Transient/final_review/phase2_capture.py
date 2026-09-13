"""Phase 2 STARE capture: 18 global segments + closeups. python.exe only."""
import sys, csv, json, math, os, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
import game_focus

HOST, PORT, TOK = resolve_endpoint()
OUT = r"D:\Luke\dev\Rimworld\Transient\final_review\stare_shots"
os.makedirs(OUT, exist_ok=True)

def call(tool, params):
    with RimBridge(HOST, PORT, TOK) as rb:
        return rb.call(tool, params)

# tiles: nearest tile to a (lat,long)
rows = list(csv.DictReader(open(r"D:\Luke\dev\Rimworld\Transient\final_review\world_tiles_live.csv")))
def nearest(lat, lon):
    best, bd = None, 1e9
    for r in rows:
        la, lo = float(r["lat"]), float(r["long"])
        dla = la - lat
        dlo = (lo - lon + 180) % 360 - 180
        d = dla*dla + (dlo*math.cos(math.radians(lat)))**2
        if d < bd: bd, best = d, int(r["tile"])
    return best

shots = [("substellar", nearest(0,0), 800)]
for name, lat, lon in [("dayside_N",45,0),("dayside_S",-45,0),("dayside_E",0,45),("dayside_W",0,-45)]:
    shots.append((name, nearest(lat,lon), 800))
for i in range(8):
    ang = i*45
    lat = 90*math.sin(math.radians(ang))
    lon = 90*math.cos(math.radians(ang))
    lat = max(min(lat,84),-84)
    shots.append((f"terminator_{ang:03d}", nearest(lat, lon if abs(lat)<84 else 0), 800))
for name, lat, lon in [("nightside_N",45,180),("nightside_S",-45,180),("nightside_E",0,135),("nightside_W",0,-135)]:
    shots.append((name, nearest(lat,lon), 800))
shots.append(("antistellar", nearest(0,180), 800))

# closeups from features by name
feats = json.load(open(r"D:\Luke\dev\Rimworld\Transient\final_review\world_features.json"))["features"]
WANT = ["Scald","Anvil","Dune Sea","Twilight Sea","Fall Line","Pyrelands","Cinders","Umbra","Long Sand","Notch","Dew Belt","Pan"]
def feat_tile(fname):
    for f in feats:
        if f.get("name","").lower() == fname.lower():
            c = f["drawCenter"]
            lat = math.degrees(math.asin(max(-1,min(1, c["y"]/max(1e-6,math.sqrt(c["x"]**2+c["y"]**2+c["z"]**2))))))
            lon = math.degrees(math.atan2(c["x"], -c["z"]))
            return nearest(lat, lon)
    return None
for w in WANT:
    t = feat_tile(w)
    if t is not None: shots.append((f"closeup_{w.replace(' ','_')}", t, 350))

game_focus.focus_game()
print(f"capturing {len(shots)} shots", flush=True)
manifest = []
for name, tile, alt in shots:
    try:
        call("jawa/world_view", {"show": True, "centerTile": tile, "altitude": alt, "northUp": True})
        call("jawa/clear_ui", {"all": True})
        time.sleep(1.2)
        r = call("rimworld/take_screenshot", {"fileName": f"stare_{name}", "suppressMessage": True})
        src = r.get("path") or r.get("filePath")
        manifest.append({"name": name, "tile": tile, "altitude": alt, "path": src, "ok": bool(r.get("success"))})
        print(name, tile, "->", src, flush=True)
    except Exception as e:
        manifest.append({"name": name, "tile": tile, "error": str(e)[:120]})
        print(name, "ERR", str(e)[:100], flush=True)
json.dump(manifest, open(os.path.join(OUT, "shots_manifest.json"), "w"), indent=1)
print("DONE", sum(1 for m in manifest if m.get("ok")), "/", len(shots), flush=True)
