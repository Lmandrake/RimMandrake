"""Surface what the Rust Cathedral already has: place the landmarks its mutators imply.

Owner, 2026-09-07: it "reads as having a few random graphical additions but otherwise
is barren. It looks unfinished."

MEASURED: the Cathedral (AB_MechanoidIntrusion, 236 tiles) is not barren at all --
5.25 mutators per tile, every tile carrying at least one, across 34 defs. But only 8
of 236 tiles carry a LANDMARK, and landmarks are the only thing that draws an icon on
the world map (LandmarkDef has iconTexturePath/drawScale/drawType; TileMutatorDef has
no visual fields whatsoever). So the ground is dense and the map shows nothing.

So this does not invent content. It places the landmark that matches a mutator the
tile ALREADY carries. ⚠️ The landmark and the mutator often have different defNames --
`AncientRuins` is the mutator, `Ruins` is the landmark -- so the pairing is explicit.

OWNER'S RULING on density: rare landmarks in full, heat vents thinned to about a
third. 150 of the 184 eligible tiles would otherwise be the same AncientHeatVent icon,
and a wall of one icon reads worse than empty. Thinning is by a hash of the tile id,
never RNG, so the gaps are stable and reproducible and there is no seed.

Dry by default; --apply places them.
"""
import sys, csv, json, hashlib, collections

sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

R = r"D:\Luke\dev\Rimworld"
apply = "--apply" in sys.argv

# mutator defName -> landmark defName. NOT the same string in every case.
PAIR = {"AncientRuins": "Ruins",
        "AncientHeatVent": "AncientHeatVent",
        "AncientGarrison": "AncientGarrison",
        "AncientWarehouse": "AncientWarehouse",
        "AncientChemfuelRefinery": "AncientChemfuelRefinery",
        "AncientLaunchSite": "AncientLaunchSite",
        "AncientInfestedSettlement": "AncientInfestedSettlement",
        "TerraformingScar": "TerraformingScar"}
THIN = {"AncientHeatVent": 3}      # keep 1 in N of these

T = {int(r["tile"]): r for r in csv.DictReader(open(R + r"\Transient\base_e\tiles.csv"))}
mut = json.load(open(R + r"\Transient\mut_before_cathedral.json"))
have = {int(l["tile"]) for l in json.load(open(R + r"\Transient\base_e\landmarks.json"))}
rc = [t for t, r in T.items() if r["biome"] == "AB_MechanoidIntrusion"]


def keep(tile, n):
    """stable 1-in-n by tile id; no RNG, no seed"""
    return int(hashlib.sha256(str(tile).encode()).hexdigest(), 16) % n == 0


plan = {}
skipped = collections.Counter()
for t in sorted(rc):
    if t in have:
        continue
    hits = [PAIR[d] for d in mut.get(str(t), []) if d in PAIR]
    if not hits:
        continue
    # prefer the RARER landmark when a tile implies several
    rare = [h for h in hits if h not in THIN]
    pick = rare[0] if rare else hits[0]
    if pick in THIN and not keep(t, THIN[pick]):
        skipped[pick] += 1
        continue
    plan[t] = pick

print("RUST CATHEDRAL — surfacing the landmarks its mutators already imply")
print("  236 tiles, 8 with a landmark today, %d eligible" % (len(plan) + sum(skipped.values())))
print("  placing %d; thinned away %s" % (len(plan), dict(skipped)))
for k, v in collections.Counter(plan.values()).most_common():
    print("     %4d  %s" % (v, k))

if not apply:
    print("\nDRY RUN. --apply to place.")
    sys.exit(0)

host, port, token = resolve_endpoint()
by_def = collections.defaultdict(list)
for t, d in plan.items():
    by_def[d].append(t)
with RimBridge(host, port, token) as rb:
    for d, ts in sorted(by_def.items(), key=lambda kv: -len(kv[1])):
        r = rb.call("jawa/world_landmarks_set",
                    {"action": "add", "tiles": ",".join(str(x) for x in ts), "def": d})
        print("ADD %-28s %3d tiles -> success=%s added=%s"
              % (d, len(ts), r.get("success"), r.get("added")))
    c = rb.call("jawa/world_commit", {})
    print("COMMIT failedSteps=%s" % c.get("failedSteps"))
