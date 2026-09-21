import sys, json; sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge
b=RimBridge(token="0370ddcc7f524e24a54e6cff36301136",timeout=60); b.connect()
tools=b.list_tools()
names=sorted(t.get("name") for t in (tools.get("tools") if isinstance(tools,dict) else tools))
print(len(names))
print([n for n in names if any(k in n for k in ("load","save","quick","debug_game","screenshot","current_map","list_maps"))])
