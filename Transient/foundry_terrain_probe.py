import sys, json, re, collections
sys.path.insert(0, r"\\wsl.localhost\Ubuntu\home\mandrake\rm\foundry\src\RimMandrake\Utils")
import rimbridge_client as rb
host, port, token = rb.resolve_endpoint()
c = rb.RimBridge(host=host, port=port, token=token, timeout=60.0); c.connect()
r = c.call("jawa/get_terrain_batch", {"rects": "0,0,250,250"})
cnt = collections.Counter()
for op in r["ops"].split(";"):
    m = re.match(r"([^:]+):(\d+),(\d+),(\d+),(\d+)", op)
    if m: cnt[m.group(1)] += int(m.group(4)) * int(m.group(5))
print(json.dumps(cnt.most_common(40)))
print([op for op in r["ops"].split(";") if op.startswith(("Water","InsectSludge","Soil"))][:40])
