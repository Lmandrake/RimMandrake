"""Clear every loose rock/slag chunk from the current map, with read-back proof.

Part of the Python-driven live-map validation library (owner, 2026-09-14:
keep the live chunk-clear as a scripting capability even though future maps
suppress chunks via BiomeDef preventGenSteps).

Run under Windows Python (the bridge binds Windows loopback):
    python.exe src/RimMandrake/Utils/rimbench/clear_chunks.py

Loops list_things(group=Chunk) -> destroy_batch(cells, categories=Item)
until the chunk count reads back 0. destroy_batch never touches pawns;
Item category in a chunk's own cell can also take other items sharing it.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from rimbridge_client import RimBridge, resolve_endpoint


def main():
    host, port, token = resolve_endpoint()
    b = RimBridge(host=host, port=port, token=token).connect()
    before = None
    rounds = 0
    while rounds <= 40:
        r = b.call("jawa/list_things", {"group": "Chunk"})
        n = r.get("countMatched", 0)
        if before is None:
            before = n
        if n == 0:
            break
        cells = ["%s,%s" % (t["x"], t["z"]) for t in r.get("things", [])]
        if not cells:
            print("MATCHED %d but no positions returned; aborting." % n)
            return 1
        d = b.call("jawa/destroy_batch",
                   {"rects": ";".join(cells), "categories": "Item"})
        rounds += 1
        print("round %d: %s" % (rounds, d.get("message")))
    after = b.call("jawa/list_things", {"group": "Chunk"}).get("countMatched", -1)
    print("chunks before=%s after=%s (MEASURED read-back)" % (before, after))
    return 0 if after == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
