# ANOMALY_EXCEPTION_ACCESS_1 — the Memory-Core revelation event

**RULED (owner, 2026-09-03): the Memory-Core event.** *"Yes the memory core event."*
The player reaches the containment and bioferrite buildings when the Utinni
surfaces them — not by research, and not by a day-one grant. Options (a) the
jawa-special class-item grant and (c) no player access are DEAD. What remains is
building it.

## spec

🔑 **The content was never cut** (owner, 2026-09-03): *"I did not cut the anomaly
content. I only cut the players ability to research that tech tree."* Every
Anomaly ThingDef, PawnKindDef and piece of map content stays for the campaign's
own repurposing — the sarlacc, the Assailant dungeons, the terminator/night-side
creatures. What died is the player's research route to it.

MEASURED 2026-09-03 against the live Cherry Picker list: the whole containment
and bioferrite economy is **present and uncut** — `HoldingPlatform`,
`ElectricInhibitor`, `ShardInhibitor`, `BioferriteGenerator`,
`BioferriteHarvester`, `Electroharvester` and `Bioferrite` itself. Nothing needs
restoring; only the unlock route is missing.

The gameplay at stake is the best resource loop in the 84 reviewed cuts: a
captured beast yields a material and 2,000 W, with containment strength as the
tension (`design/Jawa/research_review/recovery_drafts.md` §1, VERIFIED against
the ThingDefs). The event grants it as one package, in the ruled "research as
revelation" idiom of THE SHIP tree.

Buildable spec — mechanism, grant list, trigger, player-facing text and the
in-game check: `design/Jawa/anomaly_exception_access_spec.md`.
Consumer already in flight: `ASSAILANT_DUNGEON_BUILD_1` (FOUNDRY) builds the
content this grants access to.

## verify

The Memory-Core event exists as a def (not a plan), and a player in a game
holding zero Anomaly research reaches the containment buildings through it.

## criteria

1. **Resolved BEFORE the retag executes**, never after.
2. The route does not reintroduce a research row — that is the cut, reversed.
3. **No Anomaly content is cut in service of this item.** Rule 5 of the
   taxonomy's migration rules governs: a cut removes a `ResearchProjectDef` and
   nothing else.
4. `research_tree_taxonomy.md` states whichever route wins, in the row that
   currently names this item.
