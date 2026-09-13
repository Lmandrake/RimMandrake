import sys, time, shutil, os, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
SH = r"D:\Luke\dev\Rimworld\Transient\final_review\beauty"
with RimBridge(host, port, token) as rb:
    try:
        rb.call("jawa/world_features_set", {"zzz": 1})
    except Exception as e:
        print("params:", e)
