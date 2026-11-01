# CRACKEDLANDS_SALVAGE_CLAIM_CREW_1 — claim stakes and the rival salvage crew

Split from `CRACKEDLANDS_GPT_ENRICHMENT_1` §6. Also covers the mechanics item §6's "rival Jawa
crawler-crew VISITOR incident (not a raid)" and review §H.

## built in the parent

`RM_MapComponent_RecedeAftermath` scatters a small amount of floodline salvage at every recede:
1–3 `ComponentIndustrial` and 1–3 `ChunkSlagSteel` on the wetted cells, spawned forbidden (TUNED).
Anything still forbidden where it was exposed after `salvageDecayDays` (TUNED 3) is taken back by
the mud, and a message says so. Toggle: "Floodline salvage".

## owed

1. **Claim stakes**: a stake thing appears beside the salvage. Needs art.
2. **The rival crew**: a temporary visitor lord with claim-area jobs. It negotiates, races the player
   for the salvage, or steals once relations collapse. The RM layer uses generic scavengers; the
   Utinni patch substitutes Jawas, crawler props and Star Wars dialogue.
3. **Wreck silhouettes**: half-buried wreck art on the flood line.

## open questions (owner)

1. Which faction is the RM layer's "generic scavengers"? An existing vanilla faction type, or a new
   one?
2. What does "negotiate" offer? A split of the salvage, a trade, or a toll?
3. How often does the crew come? Every flood, or a chance per flood?

## criteria

Quicktest: after a debug recede, stakes stand beside the salvage. A forced crew arrives as visitors
(not a raid), works the claim area, and turns hostile only after relations collapse (state reads).
