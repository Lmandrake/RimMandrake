## spec
`cherrypick_build.py` used to UNION `observed/inventory/decisions_*.json` into the output
even where the key was absent from the ratified freeze — against its own docstring, which
has said "REPORTED, never added" since it was written. On 2026-08-23 that pushed **10
unratified cuts into the live Cherry Picker config** in the course of an unrelated item.
It was caught in the same session, reverted, and the code now matches the docstring.

**These twelve are recorded as YOUR cuts in `observed/inventory/decisions_*.json` but are
NOT in the ratified list, so they are NOT cut and nothing is cutting them:**

| key | why it needs your eye |
|---|---|
| `ThingDef/Bow_Short` | 🔴 a BOW, against the standing *"bows and knives for anyone"* floor |
| `ThingDef/Flamebow` | 🔴 a BOW, same ruling |
| `ThingDef/VFEM_Bow_HeavyCrossbow` | 🔴 neolithic ranged, same ruling |
| `BiomeDef/IceSheet` | a biome on a frozen hand-authored planet — check the tile count first |
| `BiomeDef/SeaIce` | same |
| `ThingDef/Gun_Needle` | vanilla industrial gun; consistent with the gun cut |
| `ThingDef/Gun_Scattergun` | same |
| `ThingDef/VFEP_WarcasketGun_Autorifle` | Warcasket weapon |
| `ThingDef/VFEP_WarcasketGun_HandheldCannon` | same |
| `ThingDef/VFEP_WarcasketGun_Minigun` | same |
| `ThingDef/<nodef#10>` | ⛔ malformed — XML-illegal `<`/`>`; ratifying it makes the game DISCARD EVERY KEY |
| `ThingDef/<nodef#11>` | ⛔ same. These two must never be ratified |

## verify
`python3 src/RimMandrake/Utils/cherrypick_build.py` lists them under
"recorded cut(s) are NOT in the ratified list and were NOT written".

## criteria
- [ ] Each of the ten real keys is either added to `deployed/config/v1_freeze/Mod_3521312241_Mod_CherryPicker.xml` or left alone deliberately.
- [ ] The two `<nodef#>` keys are never ratified.
- [ ] The three bows are reconciled against the weapon floor before anything is cut.
