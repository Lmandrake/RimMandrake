"""Check weather_get for hour/season/light info."""
import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()

with RimBridge(host, port, token) as rb:
    try:
        r = rb.call("jawa/weather_get", {})
        print("weather_get:", json.dumps(r)[:1500])
    except Exception as e:
        print("weather_get EXC", e)
