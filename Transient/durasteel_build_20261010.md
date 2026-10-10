# Durasteel build 20261010 (CANON_MATERIALS_BUILD_1, durasteel slice)
- Built `src/RimStarWars/Armoury/Defs/ThingDefs/RSW_Durasteel.xml`: KOTOR_AlloyDurasteel stats, sharp armor power 0.9, Metallic stuff, steel stack sprite tinted (115,125,120), no mineable producer.
- PROVISIONAL: stackLimit 75, tint (placeholder until art ledger render). Rest copied from donor.
- Validation: XML parses; validate_patch: only the texPath finding, identical to RSW_Zersium (vanilla Things/ path, outside the mod); --defs run UNMEASURABLE from WSL; Armoury melee/ranged selftest passes.
- Forge patch RSW_AlloyForge_Durasteel.xml is conditional on this def; now active (live check = L1, needs game).
- NOT done (separate work in same item): donor durasteel conversion/redirects (L2), kotor_IngotDurasteel_recipe removal. BRONZIUM_DROP_1 left alone (different def area).
