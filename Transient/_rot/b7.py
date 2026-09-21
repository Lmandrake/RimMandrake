import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    print("MATCELL", json.dumps({k:v for k,v in rb.call("rimworld/get_cell_info", {"x":163,"z":103}).items() if k!="operation"})[:700])
    print("OUTCELL", json.dumps({k:v for k,v in rb.call("rimworld/get_cell_info", {"x":145,"z":120}).items() if k!="operation"})[:700])
