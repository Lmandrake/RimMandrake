#!/usr/bin/env python3
"""Print tool names (and one schema) from the bridge's recorded schema file."""
import json, re, sys
d = json.load(open("src/RimMandrake/Utils/northstar_driver/tool_schemas.json"))
for a in sys.argv[1:]:
    if a in d:
        print(a, json.dumps(d[a])[:900])
    else:
        print(a, "->", " ".join(k for k in d if re.search(a, k)))
