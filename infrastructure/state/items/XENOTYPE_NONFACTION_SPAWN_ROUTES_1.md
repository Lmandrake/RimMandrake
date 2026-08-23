
## spec
`XENOTYPE_ROSTER_PURE_SW_1` measured that **66 of 67 non-canon xenotypes cannot reach a player
through a placed faction** — their factions all carry `startingCountAtWorldCreation: 0`. Only
`Baseliner` is reachable, and it stays.

🔴 **But `FactionDef.xenotypeSet` is not the only route into a colony, and the others were not
checked.** A non-canon species arriving by one of these would defeat the owner's ruling while
every faction-side measurement still reads clean:

| route | what to check |
|---|---|
| **wanderer joins / refugee chains** | what xenotype the generated pawn draws, and from which pool |
| **quest-reward pawns** | `QuestNode_GeneratePawn` and the `Util_` sub-scripts — do they constrain xenotype at all? |
| **sanguophage / Anomaly entities** | `Sanguophage` is a xenotype and arrives by its own events, not by a faction |
| **gene extraction & xenogermination** | a player can BUILD a non-canon xenotype from genes; is that in scope of "cut"? |
| **`PawnKindDef.xenotype`** on any kind a placed faction fields | a kind can name a xenotype the faction's `xenotypeSet` does not |

⭐ **The last row is the cheapest and most likely.** Start there: for every PawnKindDef fielded
by our twelve factions, read its `xenotype` field and check it against the Star Wars roster.

## verify
Name each route CHECKED or UNMEASURED. 🔴 **Do not report a route as safe because you could not
find a case** — absence of a found example is not absence of the route.

## criteria
- [ ] Each route is CHECKED or explicitly UNMEASURED with what would measure it.
- [ ] Any route that can deliver a non-canon xenotype is filed with the defName it delivers.

## Watch out
⚠️ **`xenotypeChances` is dictionary-keyed — an `<li>` there discards the WHOLE FactionDef,
silently.** If a fix is proposed for any faction's xenotype block, that is the trap.
⛔ **Do not propose cutting XenotypeDefs.** `XENOTYPE_ROSTER_PURE_SW_1` ruled against it: they
are referenced by GeneDefs, quests and PawnKindDefs, and cutting a referenced def yields
`Could not resolve cross-reference` for zero gain, since they already cannot spawn.
