import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()

SPAWN_PAWN = "Actions\\Spawn Pawn..."

ROWS = [
    ("Probe_d1", "RSW_DW_KotORDroidBad_KX12UPD"),
    ("Heavy_d2", "RSW_DW_KotORDroidBad_ADMkI"),
    ("Power_d3", "RSW_DW_OuterRim_GNKDroid"),
]
COLS = [
    ("charge5", 0.05),
    ("charge50", 0.5),
    ("charge100", 1.0),
]
BASE_X, BASE_Z = 40, 40
SPACING = 25

grid = []
for ri, (rowlabel, kind) in enumerate(ROWS):
    for ci, (collabel, charge) in enumerate(COLS):
        x = BASE_X + ci * SPACING
        z = BASE_Z + ri * SPACING
        grid.append({"cell": "%s_x_%s" % (rowlabel, collabel), "kind": kind,
                     "charge": charge, "x": x, "z": z})

with RimBridge(host, port, token) as rb:
    lp = rb.call("jawa/list_pawns", {})
    print("pre-spawn pawn count:", lp.get("message"))

    kids = rb.call("rimworld/list_debug_action_children", {"path": SPAWN_PAWN})["children"]
    leaf_by_kind = {}
    for k in ROWS:
        pass
    kind_set = set(kind for _, kind in ROWS)
    for c in kids:
        leaf = c["path"].split(chr(92))[-1]
        if leaf in kind_set:
            leaf_by_kind[leaf] = c["path"]
    print("resolved leaves:", json.dumps(leaf_by_kind))
    missing = kind_set - set(leaf_by_kind)
    if missing:
        print("MISSING KIND LEAVES:", missing)
        # print a sample of children to see naming convention
        print("sample children:", [c["path"] for c in kids[:10]])
        raise SystemExit(1)

    for cell in grid:
        path = leaf_by_kind[cell["kind"]]
        r = rb.call("rimworld/execute_debug_action", {
            "path": path, "x": cell["x"], "z": cell["z"]})
        print(cell["cell"], "spawn ->", json.dumps(r)[:200])
        cell["spawn_result"] = r

    with open(r"D:\Luke\dev\Rimworld\Transient\droidworks_detonation_review\spawn_log.json", "w") as f:
        json.dump(grid, f, indent=2)
