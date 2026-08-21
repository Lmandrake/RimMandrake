## spec
`world/ASHKARR_WORLDMAP_meta.json > factions[]` lists **`AM_EnemyPirate`**. It must list
**`Pirate`**.

Settled 2026-08-21 at `canon.yml > ruled.PIRATE_DEFNAME_DRIFT_1`. Measured from the
v1.6-loaded defs:

| | `AM_EnemyPirate` | `Pirate` |
|---|---|---|
| source | Ancient urban ruins `3316062206/1.6` | Core |
| `hidden` | 🔴 **true** | no |
| `settlementGenerationWeight` | 🔴 **absent ⇒ 0** | 1 |
| `settlementTexturePath` | 🔴 **absent** | present |
| label | *pirate scavenger* | *pirate gang* → reskinned **Blackstar Company** |

`world/ASHKARR_WORLDMAP_settlements.csv` places **4 rows against `Pirate` and zero against
`AM_EnemyPirate`**, out of 72.

⇒ **A hidden faction at weight 0 cannot own four holdings.** The meta is the stale artifact.

🔴 **And it is worse than a wrong label.** `AM_EnemyPirate` has a **null
`settlementTexturePath`**, and `Settlement.Material` calls
`MaterialPool.MatFrom(null, …)` → `ArgumentNullException` **once per settlement per frame**.
Measured on this project at four settlements: **60 TPS to 3.7**, with the world map
unusable. ⇒ an importer that trusts `meta.json` does not merely mislabel the faction, it can
wedge the map.

⚠️ **Find out whether the meta is generated.** If a script writes it, fix the script; if it
is hand-kept, fix the file. ⛔ Do not hand-edit a generated artifact without saying so.
⚠️ **Check `factions[]` for any other def that cannot place a settlement** while you are in
there — the same class of error would look identical.

## verify
- `python3 -c "import json;print(json.load(open('world/ASHKARR_WORLDMAP_meta.json'))['factions'])"`
  contains `Pirate` and not `AM_EnemyPirate`
- every entry in `factions[]` resolves to a def with `hidden` false **and**
  `settlementGenerationWeight > 0`, or is deliberately hidden and holds no rows in the
  settlements CSV
- the settlements CSV is unchanged at 72 rows

## criteria
No artifact describing the frozen world names a faction that cannot hold the settlements
attributed to it.
