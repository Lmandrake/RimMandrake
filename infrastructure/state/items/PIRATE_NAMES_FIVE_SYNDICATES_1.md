
## spec
DECIDE ruled 2026-08-23 (`BLACKSTAR_NAME_ROUTE_DECISION_1`). ⭐ **Your route is already right** —
`Namer_BlackstarCompany.xml`'s one-rule `factionNameMaker` is the pattern; this item just fills
the other five with authored names instead of leaving them on generated ones.

| FactionDef | new name | flavour it matches |
|---|---|---|
| `Pirate` | **Blackstar Company** — ⛔ **unchanged**, already done | the only placed pirate: 4 settlements + cast roster |
| `PirateWaster` | **Nova Blades** | pollution-adapted wasters |
| `PirateYttakin` | **the Ohnaka Gang** | hairy cold-adapted brutes |
| `CannibalPirate` | **Crimson Dawn** | cannibal ideoligion |
| `AG_XenohumanPirates` | **Black Sun** | gene-modified xenohumans |
| `DV_PirateKeshig` | **Kanjiklub** | the Keshig xenotype |

All five are canon Star Wars criminal organisations — the same canon-for-what-the-player-reads
register ruled for the plant renames.

## verify
Six pirate factions, six different names, **none empty**. 🔴 The empty-string case is the one to
check: `FactionGenerator.cs:149` tests `fixedName != null`, not `NullOrEmpty`, so a blanked name
produces a faction called `""` that reads as a UI bug.

## criteria
- [ ] Five one-rule namers, following `Namer_BlackstarCompany.xml`.
- [ ] `Pirate` still reads Blackstar Company.
- [ ] No empty faction name.

## Watch out
⛔ **Never `fixedName`.** `Pirate` is also `PirateBandBase`, so anything on it is inherited by
all six — that is the bug this closes.
⚠️ `PirateYttakin`, `PirateWaster` and `DV_PirateKeshig` **already override `factionNameMaker`**
with their own namers. Replace those overrides; do not add beside them.
⚠️ Only `Pirate` has settlements, so the other five surface in raid letters and the faction tab,
not on the world map. That is expected, not a failed deploy.
