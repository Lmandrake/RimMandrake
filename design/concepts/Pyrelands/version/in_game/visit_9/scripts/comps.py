import json,sys
for p in sys.argv[1:]:
    for c in json.load(open(p))["components"]:
        if not str(c.get("name")).startswith("skipped"): print(p.split("pv9_")[-1],c["chain"],c["name"],c["verdict"],str(c.get("detail"))[:700])
