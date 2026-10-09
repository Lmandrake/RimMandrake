## spec
`GameComponent_RUT_UnfinishedLine.EffectiveSite` (A, C or D) is stored by UNFINISHED_LINE_SITE_CHOICE_1; beats 3-5 still run at the colony. Make them read it:
beat 3 delivers cores at the site; beat 4 sends the tithe as four TradeRequests to the site's settlement (design 2.4); beat 5 is a defence site with allied Enclave/Hive defenders and the line core whose loss fails it.

## criteria
- [ ] Beat 4 tithe delivered by caravan to the chosen site's settlement.
- [ ] Beat 5 held at a defence site for A/C/D, with allies by site faction.
- [ ] Mod Settings toggle, numbers PROVISIONAL.

## verify
- `python3 src/RimUtinni/UnfinishedLine/validation.py` static pass; live: ProofSite then force beats 3-5 and read ProofChain.

## built 2026-10-09 (offline)
`UnfinishedLineSiteBeats.cs`: `QuestNode_RUT_LineSiteSetup` (beats 3-5 slate: lineSite/lineSiteName/lineSiteFaction; texts name the site),
beat 4 lends the crafter to the faction that runs the site (C Enclaves, D Hive, A as before), beat 5 `QuestNode_RUT_SiteAllies` sends that
faction's defenders (vanilla RaidFriendly, LordJob_AssistColony) when the strike arrives. Mod Settings `siteBeatsEnabled`, `siteAllyPoints` (300), PROVISIONAL.
NOT built, needs an owner/engine decision: caravan TradeRequests to the site settlement (beat 4) and a separate defence-site map with a line core (beat 5; Q1=A ordered no core building).
Live: `UnfinishedLineSiteBeatsProof.ProofSiteBeats` (chain `site_beats`), first poke `ProofSendAllies` on a throwaway map.
