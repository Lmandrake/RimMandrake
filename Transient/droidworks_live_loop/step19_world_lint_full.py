import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("jawa/world_lint", {})
    lbs = r.get("checks", {}).get("landBiomeSubmerged", {})
    print("count:", lbs.get("count"))
    examples = lbs.get("examples", [])
    from collections import Counter
    c = Counter(e.get("biome") for e in examples)
    print("biome counts in examples (capped list):", dict(c))
    seas = [e for e in examples if e.get("biome") in ("RUT_TheScald","RUT_GreySea","RUT_TwilightSea")]
    print("sea biomes present in examples:", seas)
