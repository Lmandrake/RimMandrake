## spec
🔴 **ONE READING IS ASKED FOR. Nothing else, and no build decision rides on this
item** — the number comes back here, BUILD decides what to do with it.
WHAT IS MEASURED OFFLINE: in the 577-mod dump, all 14 `Force_*` lightsabers carry
blade tools at power 92-120 with `armorPenetration` **0**. Their abstract parent
`Force_LightsaberBase` declares point and edge at power 28 with
`armorPenetration 1`, so the shipped values are neither the parent's power nor
its penetration — something replaces both.
⛔ WHY OFFLINE CANNOT SETTLE IT: `Lightsaber.dll` exports
`AdjustedArmorPenetration`, `GetArmorPenetration`, `get_ArmorPenetrationInt` and
`SelectWeightedTool`. **The mod computes armour penetration in C# at runtime**,
so the 0 in the tool field may not be the number the game uses. A def dump is XML
state; it is not evidence about a value a comp calculates.

## verify
n/a offline — that is the finding.

## criteria
**Equip any lightsaber and read the `Armor Penetration` figure off the weapon's
info card. Report the number.** That is the whole ask; it needs no map, no
spawn and no combat.
⚠️ Report it even if it looks unremarkable — an ordinary-looking number is the
result that tells BUILD the offline reading was wrong, which is worth as much as
a bad one and is the more likely outcome.

## notes
**from:** BUILD, 2026-08-20.

**Imported from `queue/CHECK.md`. Its `state:` read, verbatim:**

ready
