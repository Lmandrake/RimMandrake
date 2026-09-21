import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

BS = chr(92)
ROOT = "Actions" + BS + "Spawn Pawn..."

def spawn_batch(rb, kind, n, x0, z0, step=2):
    ids = []
    for i in range(n):
        x = x0 + (i % 10) * step
        z = z0 + (i // 10) * step
        r = rb.call("rimworld/execute_debug_action", {"path": ROOT + BS + kind, "x": x, "z": z})
        if not r.get("success"):
            print("SPAWN FAIL", kind, i, r)
    return

def read_new(rb, kind, before_ids):
    pawns = rb.call("jawa/pawn_get", {"limit": 500})
    rows = pawns.get("pawns") or []
    out = []
    for p in rows:
        if p.get("kindDef") == kind and p.get("thingId") not in before_ids:
            out.append(p.get("thingId"))
    return out

def apparel_report(rb, tid):
    d = rb.call("jawa/pawn_get", {"pawn": tid})
    p = (d.get("pawns") or [{}])[0]
    ap = p.get("apparel") or []
    return [a.get("def") for a in ap]

def main():
    host, port, token = resolve_endpoint()
    with RimBridge(host, port, token) as rb:
        rb.call("rimworld/set_god_mode", {"enabled": True})

        before = set(p.get("thingId") for p in (rb.call("jawa/pawn_get", {"limit": 500}).get("pawns") or []))

        kinds_to_test = [
            ("RSW_DW_KotORDroidGood_KM1HMD", 20, 20, 20),
            ("RSW_DW_KotORDroidBad_hk50", 5, 20, 60),
            ("RSW_DW_KotORDroidBad_ADMkI", 5, 20, 80),
            ("RSW_DW_KotORDroidGood_KX12UPD", 5, 20, 100),
            ("RSW_DW_OuterRim_GNKDroid", 5, 20, 120),
        ]

        results = {}
        for kind, n, x0, z0 in kinds_to_test:
            spawn_batch(rb, kind, n, x0, z0)
            time.sleep(0.3)
            new_ids = read_new(rb, kind, before)
            before |= set(new_ids)
            rows = []
            for tid in new_ids:
                items = apparel_report(rb, tid)
                rows.append((tid, items))
            dressed = sum(1 for _, items in rows if items)
            results[kind] = {"n_spawned": len(new_ids), "dressed": dressed, "rows": rows}
            print(kind, "spawned=%d dressed=%d" % (len(new_ids), dressed))
            for tid, items in rows:
                print("   ", tid, items)

        with open(r"D:\Luke\dev\Rimworld\Transient\mapgen_gl\apparelmoney2\results.json", "w") as f:
            json.dump(results, f, indent=2)
        print("WROTE results.json")

if __name__ == "__main__":
    main()
