# MIASMA_FREE_SALT_CRUST_1 work note (2026-10-03)
- Started.
## Choices
- Author RM_MiasmaSaltCrust in the Miasma mod (not reuse RM_SaltCrustShore: Miasma does not depend on terminalbiomes, and that text is the Grey Sea's).
- Fields copied from RUT_Jawa_SaltCrust (cosmetic hardpan, fertility 0), invented-neutral description; Odyssey DryLakeBed texture (all DLC assumed).
- No C# change, so no build/csproj edit; no new settings toggle (a terrain def is not a feature); no art queued (reuses Odyssey DryLakeBed).
## Proof
- Offline: RM_Miasma.xml landTerrain/dryTerrain now RM_MiasmaSaltCrust; no RUT_ in gradient/pool terrain fields. validation.py static PASS (new checks); validate_patch 0 errors.
- Live criterion (tier without mandrake.rut.patches, surge recede repaint) UNMEASURED; suite component salt_crust_free_tier reports it.
