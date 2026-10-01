# CRACKEDLANDS_WOOLAMANDER_FLIGHT_1 — the woolamander is a ruled flier but cannot fly

Found by `CRACKEDLANDS_GPT_ENRICHMENT_1` §5 (the recede feast). The owner-picked text has
"convor, can-cell and woolamander migrants physically fly in, feed, and fly out overhead".
`CRACKEDLANDS_RULED_CONTENT_1` also rules the three as "Fliers (CanCell/Convor/Woolamander) STAY —
guests and migrants".

## the fact

`src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Woolamander.xml` has **no `MaxFlightTime`** and
no `canFlyIntoMap` (grep, 2026-10-01). `RSW_Convor` (30) and `RSW_CanCell` (60) have both. The
recede feast chooses its migrants from the biome's own flight-capable roster
(`canFlyIntoMap` and `MaxFlightTime > 0`), so the woolamander is never among them, and it still
spawns as a walking resident.

## open question (owner)

Does the woolamander fly in our fiction? If yes, the standing rule *"if it flies in the fiction, it
flies in the game"* applies: add the Locust-shaped stats and race flags. The flip-book frames are
separate and never block flight. If no, the "flier-commuter" label on the Cracked Lands roster row
is wrong and should be corrected. Verify canon with the Wookieepedia search API before asking.
