"""Check game info / time of day, and look for a light-emitting ThingDef we can spawn."""
import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()

with RimBridge(host, port, token) as rb:
    gi = rb.call("rimworld/get_game_info", {})
    print("game_info:", json.dumps(gi)[:1200])
