# RIMMANDRAKE_RETIRE_ROT_DONOR_SLOT_COPIES_ELEVEN_SHADOWED

Found 2026-11-11 by CLAUDE_ARCHMAGI_OFFLINE2 while doing AGARILUX_PRIME_COPIES_RECONCILE_SPLIT (done there for RM_AgariluxPrime, 45408f140e).

The 11 other Alpha Biomes ports in `src/RimMandrake/TheRot/Defs/ThingDefs_Plants/RM_TheRot_DonorPorts.xml` follow the same pattern.
Each base def names the donor slot (`Things/Plants/AB_*` or `Things/Plant/*`), and `TheRot/Patches/RotSpecies_NamesAndSizes.xml` repoints
it to `RotSpecies/<Name>`, which is what the game draws (2026-11-02 live dump). Files at the donor slots in TheRot and/or
UtinniPatches therefore ship and load, but nothing draws them (Alpha Biomes is retired). Measured 2026-11-11:

RM_Bryolux, RM_Glowstool, RM_GlowingAgarilux (UtinniPatches only); RM_WitchesOyster, RM_RecurvedStropharia, RM_SlimyPholiota
(TheRot only); RM_GiantAgarilux, RM_LilacBeacon, RM_ArbuscularMycorrhiza, RM_AgaricusDomeCap, RM_DribblingCap (both).

## spec
For each def: set the base texPath to the repointed `RotSpecies/<Name>` and delete its repoint operation. Retire the donor-slot
files through the art ledger, copying `src/RimMandrake/Utils/art/agarilux_prime_retire_copies.py`. First check that no other def
of ours draws the slot (`Things/Plant/Agarilux` and similar vanilla-looking paths need checking), then re-run
`selftest_alpha_plants_renders.py`. Model, evidence and resolver: `whittle/agarilux_prime_copies_reconcile_split/`
(`evidence/resolve_agarilux_prime.py`). A donor-slot copy that an art-eval or sheet judged was judged as a picture the game never drew,
so the judgement does not carry to the drawn texture.
