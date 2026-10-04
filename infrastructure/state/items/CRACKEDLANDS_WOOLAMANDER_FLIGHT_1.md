# CRACKEDLANDS_WOOLAMANDER_FLIGHT_1 — the woolamander is a walking resident, not a flier

## ruling

Owner, 2026-10-03 ~21:20 PDT, decision taken by question card: the woolamander is a **walking resident**
of the Cracked Lands and follows canon (arboreal, no flight). No flight stats are added.

## canon source

Wookieepedia, page `Woolamander` (parse API, `action=parse&page=Woolamander&prop=wikitext`, read
2026-10-03): a species native to Yavin 4 living in the canopy of the Massassi trees, with long arms, short
legs and a tufted tail; categories *Arboreal creatures* and *Primates*. Nothing in the article mentions
wings or flight. Sources cited there: *Ultimate Star Wars* (2015), *Star Wars: Galactic Atlas*.

## what changed

`RSW_Woolamander.xml` already had no `MaxFlightTime` or `canFlyIntoMap`, so the def was right. The text
that called it a flier was corrected to match it: the roster comments in `RUT_CrackedLands.xml` and
`WildAnimals_CrackedLands.xml`, the Cracked Lands bible, its roster JSON, the bedazzle cast and review
docs, `cast_assignment.csv`, `CRACKEDLANDS_RULED_CONTENT_1`, and the recede-feast text in the closed
`CRACKEDLANDS_GPT_ENRICHMENT_1`. The recede feast's migrants are the convor and the can-cell.
