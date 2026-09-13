import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

# DROIDWORKS_PERSONALITY_VERIFY_1 -- 20 spawns/family, forced traits + protocol pedantry.
# family -> (representative PawnKindDef defName, expected forcedTraits defNames)
FAMILIES = {
    "labour":    ("RSW_DW_JDSCIS_Pistoeka_Sotage_Droid", ["Industriousness"]),
    "battle":    ("RSW_DW_JDSCIS_B1_Battle_Droid", ["ShootingAccuracy"]),
    "heavy":     ("RSW_DW_JDSCIS_IG-100_MagnaGuards", ["Tough"]),
    "astromech": ("RSW_DW_KotORDroidColonist_T3UD", ["TooSmart"]),
    "protocol":  ("RSW_DW_KotORDroidColonist_GE3PD", ["Abrasive", "RSW_DW_Trait_ProtocolPedantry"]),
    "probe":     ("RSW_DW_KotORDroidColonist_KX12UPD", ["GreatMemory"]),
    "power":     ("RSW_DW_OuterRim_GNKDroid", ["Nerves"]),
    "primitive": ("RSW_DW_Primitive_G2", ["SlowLearner"]),
}
N = 20

host, port, token = resolve_endpoint()
out = {}

with RimBridge(host, port, token) as rb:
    # sanity: confirm defs exist before burning a spawn budget on typos
    defq = ";".join("PawnKindDef/%s" % k for k, _ in FAMILIES.values())
    d = rb.call("jawa/get_defs", {"defs": defq})
    for row in d.get("defs", []):
        if not row.get("found"):
            print("MISSING DEF:", row)

    n = 0
    fam_list = list(FAMILIES.items())
    for fam, (kind, expected) in fam_list:
        ok = 0
        fails = []
        for i in range(N):
            x = 100 + (n % 20) * 2
            z = 100 + (n // 20) * 2
            n += 1
            r = rb.call("jawa/spawn_pawn", {"kindDef": kind, "x": x, "z": z, "faction": "player", "count": 1})
            if not r.get("success"):
                fails.append(("spawn_fail", i, str(r)[:200]))
        print(fam, kind, "spawn pass done")

    time.sleep(2)
    lp = rb.call("jawa/list_pawns", {"limit": 1000})
    print("list_pawns success:", lp.get("success"), "message:", lp.get("message"))
    pawns = lp.get("pawns", [])
    by_kind = {}
    for p in pawns:
        by_kind.setdefault(p.get("kindDef"), []).append(p)

    for fam, (kind, expected) in fam_list:
        matched = by_kind.get(kind, [])
        out[fam] = {"kind": kind, "expected": expected, "spawned_seen": len(matched), "per_pawn": []}
        hit = 0
        for p in matched:
            pid = p.get("id")
            pg = rb.call("jawa/pawn_get", {"pawn": pid})
            pawns_field = pg.get("pawns") or [pg]
            rec = pawns_field[0] if pawns_field else {}
            traits = rec.get("traits", [])
            trait_names = []
            for t in traits:
                if isinstance(t, dict):
                    trait_names.append(t.get("defName") or t.get("def") or t.get("trait") or str(t))
                else:
                    trait_names.append(str(t))
            actual_kind = rec.get("kindDef") or rec.get("kind") or p.get("kindDef")
            has_all = all(e in trait_names for e in expected)
            if has_all:
                hit += 1
            out[fam]["per_pawn"].append({
                "id": pid, "actual_kindDef": actual_kind, "traits": trait_names, "has_all_expected": has_all
            })
        out[fam]["hit"] = hit
        out[fam]["total_checked"] = len(matched)
        print(fam, "-> %d/%d matched-kind pawns show all expected traits" % (hit, len(matched)))

with open(r"D:\Luke\dev\Rimworld\Transient\dwv_results.json", "w") as f:
    json.dump(out, f, indent=2)
print("WROTE Transient/dwv_results.json")
