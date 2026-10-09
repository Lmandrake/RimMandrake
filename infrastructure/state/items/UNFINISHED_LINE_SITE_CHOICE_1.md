# UNFINISHED_LINE_SITE_CHOICE_1 — where the line stands (end of beat 2), carried to beats 3-5

Split from `UNFINISHED_LINE_ENVOY_BEAT_1` (beat 2 built without it). Design: `design/Jawa/proposals/droid_mass_production_quest_chain_2026-10-02.md` §2.2 table (sites A-D).

## blocked
The owner ruled Q1 = A on 2026-10-03 (the Enclaves get a working line and the player gets its fruits; no player-owned Foundry Line building). The design's site B, "your colony", reads "you get the building (Q1)". Does site B stay (the line stands at your colony but is the Enclaves'), or is it cut? Ask before building.

## criteria
- [ ] The choice is offered when The Envoy succeeds; each option's goodwill split per the §2.2 table.
- [ ] The chosen site reaches beats 3-5. A child cannot write the parent's slate: store it on the spine part or GameComponent_RUT_UnfinishedLine and pass it through the spine's InitSlate.
- [ ] Beat 1's grade (QuestPart_DroidRepairJobOutcome.gradedTier on the finished Count child) colours the choice letter.
- [ ] Whether a QuestPart_Choice with no Reward items renders is UNMEASURED; the fallback is a ChoiceLetter.

## built 2026-10-09 (owner card 2026-10-08: site B CUT)
A, C, D offered by `ChoiceLetter_RUT_LineSite` (QuestNode_RUT_SiteChoice on VisitDone, UnfinishedLineSite.cs); site stored on
`GameComponent_RUT_UnfinishedLine.lineSite`, beat 1 grade on `beat1Grade` (colours the letter). Goodwill deltas and an on/off
toggle are Mod Settings (PROVISIONAL). The reward-less QuestPart_Choice is not used. OWED: beats 3-5 still run at the colony;
per-site delivery / defence-site variant is `UNFINISHED_LINE_SITE_BEATS_1`.

## verify
- Offline: `python3 src/RimUtinni/UnfinishedLine/validation.py` (site_choice chain static pass).
- Live (when bridge is free): `jawa/static_call` UnfinishedLineSiteProof.ProofSite reads `options=ACD`; ProofChoose("B") returns REFUSED.
- Live visual (owner present): force Envoy success, the letter "Where the line stands" shows three options, one click sets ProofSite.
