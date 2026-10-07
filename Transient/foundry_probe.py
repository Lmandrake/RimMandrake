import sys, json
sys.path.insert(0, r"\\wsl.localhost\Ubuntu\home\mandrake\rm\foundry\src\RimMandrake\Utils")
import rimbridge_client as rb
host, port, token = rb.resolve_endpoint()
c = rb.RimBridge(host=host, port=port, token=token, timeout=60.0); c.connect()
for spec in sys.argv[1:]:
    tool, _, js = spec.partition(" ")
    r = c.call(tool, json.loads(js or "{}"))
    print(tool, json.dumps(r)[:int(1800)])
