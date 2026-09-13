import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()

IDS = {
 "astromech": ["RSW_DW_Race_OuterRim_AstromechDroid37060","RSW_DW_Race_OuterRim_AstromechDroid37061","RSW_DW_Race_OuterRim_AstromechDroid37062"],
 "battle": ["RSW_DW_Race_OuterRim_BattleDroid37063","RSW_DW_Race_OuterRim_BattleDroid37064","RSW_DW_Race_OuterRim_BattleDroid37065"],
 "heavy": ["RSW_DW_Race_OuterRim_SuperTacticalDroid37066","RSW_DW_Race_OuterRim_SuperTacticalDroid37067","RSW_DW_Race_OuterRim_SuperTacticalDroid37068"],
 "labour": ["RSW_DW_Race_OuterRim_ImperialLaborDroid37052","RSW_DW_Race_OuterRim_ImperialLaborDroid37053","RSW_DW_Race_OuterRim_ImperialLaborDroid37054"],
 "power": ["RSW_DW_Race_OuterRim_GNKDroid37074","RSW_DW_Race_OuterRim_GNKDroid37075","RSW_DW_Race_OuterRim_GNKDroid37076"],
 "probe": ["RSW_DW_Race_guy762_DroidRace_KX12UPD37069","RSW_DW_Race_guy762_DroidRace_KX12UPD37070"],
 "protocol": ["RSW_DW_Race_OuterRim_ProtocolDroid37055","RSW_DW_Race_OuterRim_ProtocolDroid37059"],
 "primitive": ["RSW_DW_Race_Primitive_G2Unit37077","RSW_DW_Race_Primitive_G2Unit37078","RSW_DW_Race_Primitive_G2Unit37080"],
}

out = {}
with RimBridge(host, port, token) as rb:
    for fam, ids in IDS.items():
        out[fam] = []
        for pid in ids:
            r = rb.call("jawa/pawn_get", {"pawn": pid})
            p = r.get("pawns", [{}])[0]
            traits = [t.get("def") for t in (p.get("traits") or [])]
            out[fam].append({"id": pid, "traits": traits})

for fam, rows in out.items():
    print(f"=== {fam} ===")
    for row in rows:
        print(" ", row["id"], row["traits"])

with open(r"D:\Luke\dev\Rimworld\Transient\dw_personality_traits_full.json", "w") as f:
    json.dump(out, f, indent=1)
