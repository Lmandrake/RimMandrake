import sys, json, time; sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge
b=RimBridge(token="0370ddcc7f524e24a54e6cff36301136",timeout=120); b.connect()
r=b.call("rimworld/go_to_main_menu",{},check=False); print(json.dumps(r)[:200])
time.sleep(8)
b=RimBridge(token="0370ddcc7f524e24a54e6cff36301136",timeout=60); b.connect()
print(json.dumps(b.call("rimworld/get_game_info",{},check=False))[:200])
