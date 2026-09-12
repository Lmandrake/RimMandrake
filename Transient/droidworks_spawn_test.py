import sys, time, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()

KINDS = [
    "RSW_DW_JDSCIS_B1_Battle_Droid",       # JDS wave (mechanoid-family conversion)
    "RSW_DW_OuterRim_GNKDroid",            # OuterRim wave, gonk / detonation chassis
    "RSW_DW_OuterRim_BattleDroid",         # OuterRim wave, battle chassis
    "RSW_DW_KotORDroidColonist_T3UD",      # KotOR wave, colonist-capable
    "RSW_DW_KotORDroidBad_KM1MD",          # KotOR wave, hostile-capable
    "RSW_DW_Primitive_G2",                 # Primitive tier
    "RSW_DW_Primitive_Junker",             # Primitive tier
]

with RimBridge(host, port, token) as rb:
    st = rb.call("rimbridge/get_bridge_status", {})
    print("status ok:", st.get("success"))

    # find a real KotORDroidBad_* kind name via get_defs? just try a known one
    r = rb.call("jawa/list_pawns", {})
    print("pre-spawn pawn count:", r.get("message"))

    results = []
    x0, z0 = 40, 40
    spacing = 4
    idx = 0
    per_kind = 3
    kinds_final = [k for k in KINDS if k]
    for kind in kinds_final:
        # resolve the spawn debug action path
        roots = rb.call("rimworld/list_debug_action_roots", {})
        for n in range(per_kind):
            x = x0 + (idx % 10) * spacing
            z = z0 + (idx // 10) * spacing
            sep = chr(92)
            path = "Actions" + sep + "Spawn Pawn..." + sep + kind
            resp = rb.call("rimworld/execute_debug_action", {"path": path, "x": x, "z": z})
            results.append({"kind": kind, "x": x, "z": z, "resp": resp})
            idx += 1

    for res in results:
        print(res["kind"], res["x"], res["z"], "->", json.dumps(res["resp"])[:200])

    time.sleep(2)
    r2 = rb.call("jawa/list_pawns", {})
    print("post-spawn pawn count:", r2.get("message"))
    with open(r"D:\Luke\dev\Rimworld\Transient\droidworks_spawn_pawns.json", "w") as f:
        json.dump(r2, f, indent=2)
