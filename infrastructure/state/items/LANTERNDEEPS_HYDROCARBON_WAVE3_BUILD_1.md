# LANTERNDEEPS_HYDROCARBON_WAVE3_BUILD_1 — hush, sipper, tapper, pooler

Split from `LANTERNDEEPS_HYDROCARBON_FAUNA_BUILD_1` (wave 1 `97ecd0d1e`, wave 2 `b68999554`). Concepts and
mechanics: `design/Jawa/worldbuilding/biomes/rosters/lantern_deeps_repopulation_proposals.md` §1, §4, §6, §7.
Art is DONE and unwired: artpipe `_artsrc/RM_{Hush,Sipper,Tapper,Pooler}_{south,east,north}` (drawsizes 2.0, 0.6,
1.0, 1.0). Same premises as waves 1-2: `RM_HydrocarbonBloodExtension`, Filth_Fuel blood, no meat/leather, fuel
butcher products, `RM_` inline in `RM_LanternDeeps`, Mod Settings toggle per mechanic, a validation.py chain.

## criteria
- [ ] Hush: undrawn and untargetable on cells below a ground-glow threshold (Harmony on draw + targeting), lunges
      at 2 cells from unlit fungal floor; 1-2 per map, not tameable.
- [ ] Sipper: swarm vermin seeking the brightest glower; N within 1 cell shrink that glower's radius
      (`CompGlower.GlowRadius` + `ForceRegister`, batched); population cap.
- [ ] Tapper: wild ones seek and drain `CompPowerBattery` (`DrawPower`); tame one charges on `RM_DeepAurora` and
      gives charge to an adjacent battery.
- [ ] Pooler: seeks the hottest fire/heater/warm pawn; fire dies (`Fire.Destroy`), heater stops while draped,
      pawn chills (Hypothermia); fire never hurts it.
