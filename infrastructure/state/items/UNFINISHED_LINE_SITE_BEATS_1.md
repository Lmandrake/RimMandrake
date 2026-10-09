## spec
`GameComponent_RUT_UnfinishedLine.EffectiveSite` (A, C or D) is stored by UNFINISHED_LINE_SITE_CHOICE_1; beats 3-5 still run at the colony. Make them read it:
beat 3 delivers cores at the site; beat 4 sends the tithe as four TradeRequests to the site's settlement (design 2.4); beat 5 is a defence site with allied Enclave/Hive defenders and the line core whose loss fails it.

## criteria
- [ ] Beat 4 tithe delivered by caravan to the chosen site's settlement.
- [ ] Beat 5 held at a defence site for A/C/D, with allies by site faction.
- [ ] Mod Settings toggle, numbers PROVISIONAL.

## verify
- `python3 src/RimUtinni/UnfinishedLine/validation.py` static pass; live: ProofSite then force beats 3-5 and read ProofChain.
