# Aerosol wave 2 (2026-10-07)
1. ShieldHazardUtility.HasParticulateHazard now calls RM_PollutionSense.IsPollutedHere (sandRate half kept). ShipShields builds clean.
2. BIOME_SHIP_CONTRIBUTIONS_1.md: Warscar row added (mechanism built, never run, gravship-placeability unverified).
3. RM_AerosolScreenPatches_PawnInspect (Postfix on Pawn.GetInspectString) in RM_AerosolScreen.cs; gated by aerosolScreenEnabled. Warscar builds clean.
Left: ShipShields own two Harmony prefixes still present (criterion "one patch class"); DLLs rebuilt, uncommitted.
