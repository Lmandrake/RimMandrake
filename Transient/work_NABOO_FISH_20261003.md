# NABOO_FISH_TO_TWILIGHT_1 work log 2026-10-03
Folder edited: src/RimUtinni/UtinniPatches only (Patches/ + validation.py). RM_TheScald.xml / RM_TwilightSea.xml untouched.
Why UtinniPatches: mee/faa (RSW_Mee, RSW_Faa, catches RSW_MeeCatch/RSW_FaaCatch) are canon Star Wars scalefish (RSW_ SWBestiary),
so they ride the campaign patch layer (MayRequire mandrake.rsw.swbestiary), same as WildAnimals_TheScald/Greentide.
Choices:
- Scald: removed RSW_Faa/RSW_Mee rows from Patches/WildAnimals_TheScald.xml (Sando aqua monster stays). Scald's own catch never had them.
- Twilight: new Patches/WildAnimals_TwilightSea.xml adds both as RM_TwilightSea wildAnimals floor residents (0.5 each, the commonalities they had in the Scald)
  and catches into fishTypes: RSW_MeeCatch 0.4 -> saltwater_Common, RSW_FaaCatch 0.3 -> saltwater_Uncommon (Greentide's freshwater 0.4/0.3 split, mapped to the sea buckets).
  Patched via PatchOperationConditional on the bucket (fishTypes is Odyssey-gated).
- NOT touched (evictions stopped, owner 2026-09-22): Greentide + Miasma keep their mee/faa rows (Miasma has juveniles).
- Art: catch/creature art already ships in SWBestiary; no new art queued.
- Open: AnimalTolerances_Ashkarr pins RSW_Faa comfy 10..60C; Twilight temperature vs that is UNMEASURED (not changed).
