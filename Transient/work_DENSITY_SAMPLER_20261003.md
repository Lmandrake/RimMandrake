# CHILL_DIVE_DENSITY_SAMPLER_1 work log 2026-10-03
Folder edited: src/RimMandrake/DivingInteraction only (GenStep_SeaFloorFauna.cs, RM_DivingSettings.cs, validation.py, new density_sampler.py).
Item has no prose; spec = propane-lake floor sitting agenda Q6 (one-of-each sampler; owner number set live, leaning 2-4).
Choices: Chill-only weighted draw (with replacement by commonality) of N animals, N = setting chillDiveAnimalCount (default 3, 1-8),
toggle chillDensityDrawEnabled (default on; off = legacy round(total*commonality) per species). Other seas untouched.
Offline sampler density_sampler.py simulates both modes from RM_TheChill roster XML (no game). Live count component UNMEASURED.
