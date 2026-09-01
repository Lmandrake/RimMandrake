import xml.etree.ElementTree as ET
import csv, math, sys

SRC = "/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/3497316713/1.6/Defs/ThingDefs_Races/Races_Animal_SW.xml"
OUT = "/mnt/d/Luke/dev/Rimworld/design/Jawa/worldbuilding/data/beast_norm_manifest.csv"

K = 15.0            # top of the owner-ruled 12-15 band; see item notes for why
DPS_TARGET_COEF = 10.0   # midpoint of the ruled 8-12*sqrt(bodySize) band

tree = ET.parse(SRC)
root = tree.getroot()

rows = []
herbivore_tags = {"VegetarianRoughAnimal", "DendrovoreAnimal"}
carnivore_tags = {"CarnivoreAnimal"}

for td in root.findall("ThingDef"):
    defName = td.findtext("defName")
    if not defName:
        continue
    race = td.find("race")
    if race is None:
        continue
    bs_text = race.findtext("baseBodySize")
    if bs_text is None:
        continue
    bodySize = float(bs_text)

    tools = td.find("tools")
    tool_rows = []
    if tools is not None:
        for i, li in enumerate(tools.findall("li")):
            power = li.findtext("power")
            cd = li.findtext("cooldownTime")
            label = li.findtext("label") or ""
            caps = [c.text for c in li.findall("capacities/li")]
            if power is None or cd is None:
                continue
            tool_rows.append({
                "index": i, "power": float(power), "cooldownTime": float(cd),
                "label": label, "capacities": "+".join(caps or []),
            })
    if not tool_rows:
        continue

    best = max(tool_rows, key=lambda t: t["power"])
    old_dps = best["power"] / best["cooldownTime"] if best["cooldownTime"] else 0.0

    food = race.findtext("foodType") or ""
    food_tags = {t.strip() for t in food.split(",") if t.strip()}
    is_herbivore = bool(food_tags & herbivore_tags) and not (food_tags & carnivore_tags)
    is_big = bodySize >= 1.5
    raise_revenge = is_herbivore and is_big

    mh_dmg_present = race.find("manhunterOnDamageChance") is not None
    mh_tame_present = race.find("manhunterOnTameFailChance") is not None
    mh_dmg_val = race.findtext("manhunterOnDamageChance")
    mh_tame_val = race.findtext("manhunterOnTameFailChance")

    if bodySize < 1.0:
        # Law 3 is scoped to bs >= 1; leave small beasts alone.
        new_power = best["power"]
        new_cd = best["cooldownTime"]
        exempt = "bs<1"
    else:
        new_power = round(K * bodySize, 2)
        new_dps = DPS_TARGET_COEF * math.sqrt(bodySize)
        new_cd = round(new_power / new_dps, 2) if new_dps > 0 else best["cooldownTime"]
        exempt = ""

    new_mh_dmg = ""
    new_mh_tame = ""
    if raise_revenge:
        cur_dmg = float(mh_dmg_val) if mh_dmg_val else 0.0
        cur_tame = float(mh_tame_val) if mh_tame_val else 0.0
        new_mh_dmg = round(max(cur_dmg, 0.9), 2)
        new_mh_tame = round(max(cur_tame, 0.4), 2)

    rows.append({
        "defName": defName,
        "bodySize": bodySize,
        "best_tool_index": best["index"],
        "best_tool_label": best["label"],
        "best_tool_capacities": best["capacities"],
        "old_power": best["power"],
        "old_cooldown": best["cooldownTime"],
        "old_dps": round(old_dps, 2),
        "new_power": new_power,
        "new_cooldown": new_cd,
        "new_dps": round(new_power / new_cd, 2) if new_cd else 0.0,
        "is_herbivore": is_herbivore,
        "raise_revenge": raise_revenge,
        "manhunterOnDamageChance_present": mh_dmg_present,
        "manhunterOnDamageChance_old": mh_dmg_val,
        "manhunterOnDamageChance_new": new_mh_dmg,
        "manhunterOnTameFailChance_present": mh_tame_present,
        "manhunterOnTameFailChance_old": mh_tame_val,
        "manhunterOnTameFailChance_new": new_mh_tame,
        "exempt": exempt,
    })

with open(OUT, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    for r in rows:
        w.writerow(r)

print(f"{len(rows)} beasts written to {OUT}")
print(f"herbivore+big (revenge-knob candidates): {sum(1 for r in rows if r['raise_revenge'])}")
print(f"exempt (bs<1): {sum(1 for r in rows if r['exempt'])}")
print(f"manhunterOnDamageChance present directly on def: {sum(1 for r in rows if r['manhunterOnDamageChance_present'])}/{len(rows)}")
print(f"manhunterOnTameFailChance present directly on def: {sum(1 for r in rows if r['manhunterOnTameFailChance_present'])}/{len(rows)}")
