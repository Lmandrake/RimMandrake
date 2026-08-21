## spec
Ruling: `items/FACTION_SLATE_ZEROES_KEEPS_1.md` `## ruling`. This is the checklist edit.

`infrastructure/state/WORLDGEN_FACTION_CHECKLIST.md` **Section 4** lists 6 KEEPs. Two are
retired; the count becomes **21 untick / 4 keep**.

| row | ruling |
|---|---|
| `OuterRim_BinaryStarRaiders` | ⛔ **RETIRE.** Not hidden, `settlementGenerationWeight 1` ⇒ it would place holdings on a planet whose 72 settlements are already hand-placed for 13 factions |
| `OuterRim_MoistureFarmers` | ⛔ **RETIRE.** Same reason, plus ⭐ **it duplicates a role we authored** — the Homestead Defense League *is* this planet's moisture farmers, thirteen settlements of them |
| `guy762_KotORFaction_RogueDroids` | ✅ **KEEP, emphatically.** `hidden: true` ⇒ places nothing, costs the map nothing, and the checklist already calls it *"quest-critical — antagonist of the KotOR distress call. Never untick"* |
| `JDSCIS_CIS_Faction` | ✅ **KEEP.** Also `hidden: true`, also free |
| vanilla `Empire` | ✅ unchanged |
| ~~Rebel Alliance~~ | already retired, unchanged |

Strike the two rows the way the file already strikes `OuterRim_GalacticEmpire` and the Rebel
Alliance — ⛔ **struck in place with the reason, never deleted.** A reader who ticked them
last time must find out why they are gone.

Update the ratified count wherever it appears (`:32`, `:90`, `:109` say *"21 untick / 6
keep"*).

⚠️ **This is a change to a RATIFIED artifact**, so say so in the header: the ratification
stands for the tick-list; two KEEP rows are retired on evidence that did not exist when it
was ratified — namely that both place settlements on a map that is now hand-authored and
frozen.

## verify
`WORLDGEN_FACTION_CHECKLIST.md` Section 4 shows four live KEEP rows and two struck ones with
reasons, and no line still reads "6 keep".

## criteria
The owner ticks a list where every live row is a faction the campaign actually wants.
