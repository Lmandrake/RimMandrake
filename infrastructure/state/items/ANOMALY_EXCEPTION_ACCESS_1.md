# ANOMALY_EXCEPTION_ACCESS_1 — a non-research route to the containment buildings

The Anomaly research rows are cut, so the player has no way to unlock holding
platforms, inhibitors and harvesters. This decides how they get that access.
The cut is not re-litigated here.

## spec

🔑 **The content was never cut** (owner, 2026-09-03): *"I did not cut the anomaly
content. I only cut the players ability to research that tech tree."* Every
Anomaly ThingDef, PawnKindDef and piece of map content stays in the game for the
campaign's own repurposing — the sarlacc, the Assailant dungeons, the
terminator/night-side creatures. What died is the player's research route to it.

MEASURED 2026-09-03 against the live Cherry Picker list: the whole containment
and bioferrite economy is **present and uncut** — `HoldingPlatform`,
`ElectricInhibitor`, `ShardInhibitor`, `BioferriteGenerator`,
`BioferriteHarvester`, `Electroharvester` and `Bioferrite` itself. So nothing
needs restoring there; only the unlock route is missing.

Separately, a handful of Anomaly defs ARE cut from an earlier ruled moderation
pass and may be in scope of the owner's "restore the content" instruction —
they are listed on the item's note, not assumed here.

The gameplay at stake is the best resource loop in the 84 reviewed cuts:
a captured beast yields a material and 2,000 W, with containment strength as the
tension (`design/Jawa/research_review/recovery_drafts.md` §1, VERIFIED against
the ThingDefs). Options to put to the owner:

- **(a) Class-item grant** — the jawa-special start owns the containment gear.
  Cheapest; hands over a working industry on day one with no discovery.
- **(b) Memory-Core revelation** *(recommended by the recovery analysis)* — the
  ship surfaces the five buildings plus Bioferrite as one event package,
  matching THE SHIP tree's ruled "research as revelation" idiom. Costs an event
  author.
- **(c) No player access** — the content stays purely ours for dungeons and
  creatures, and the player never builds containment.

## verify

The owner has ruled one option, and the chosen route exists as a def or event
(not a plan), with a player in a game holding zero Anomaly research able to
reach the containment buildings — or, under (c), the ruling recorded that they
deliberately cannot.

## criteria

1. **Resolved BEFORE the retag executes**, never after.
2. The route does not reintroduce a research row — that is the cut, reversed.
3. **No Anomaly content is cut in service of this item.** Rule 5 of the
   taxonomy's migration rules governs: a cut removes a `ResearchProjectDef` and
   nothing else.
4. `research_tree_taxonomy.md` states whichever route wins, in the row that
   currently names this item.
