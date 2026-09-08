import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    get1 = rb.call("jawa/log_autoopen_suppress", {"action": "get"})
    print("GET1:", get1)
    result = rb.call("jawa/log_autoopen_suppress", {"action": "testerror"})
    print("TESTERROR:", result)
