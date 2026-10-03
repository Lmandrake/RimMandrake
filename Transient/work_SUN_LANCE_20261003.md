# SUN_LANCE work 2026-10-03
- claimed+started STILLSAND_SUN_LANCE_1.
- Plan: reuse RM_Verb_MirrorBeam on a Building_TurretGun gun (no new verb). Verb SunFactor: for a non-pawn caster use RM_SunPower.FactorAt (pinned-sun elevation, shade, roof, gale); Available gated by new RM_GlassChainSettings.sunLanceEnabled (muurrok keeps mirrorBeamEnabled).
- Heat-never-ignites: verb has no fire path; damage def RM_MirrorGlare (checked below); beamChanceToStartFire/AttachFire 0.
- DONE offline: Defs/ThingDefs_Buildings/RM_SunLance.xml (RM_SunLance 1x1 Building_TurretGun, no power; RM_SunLance_Gun using shared RM_Verb_MirrorBeam; both fire chances 0). RM_MirrorBeamExtension sits on the BUILDING def because the verb reads sun rules from caster.def (a turret's caster is the building, not the gun).
- Verb edit: non-pawn caster -> RM_SunPower.FactorAt (elevation via pinned sun, shade, roof, gale), min 0.3; Available() uses sunLanceEnabled for turrets, mirrorBeamEnabled stays for the muurrok. No new .cs so no csproj change.
- Settings: RM_GlassChainSettings.sunLanceEnabled (checkbox). validation.py: SETTINGS + sun_lance_defs component (static no-fire pin, live def resolve) + roundtrip.
- Art: reused finished artpipe RM_SunLance_Base/_Top from _artsrc -> Textures/Things/Building/Security/. No new jobs queued.
- Heat-never-ignites: not RimSage-verified; relies on the verb having no fire path (already in muurrok) and Beam DamageDef (AddInjury, Burn hediff). Live proof owed (no fire after firing at flammable target, nothing in shade/gale).
- Build OK (stage_build + extra_dirs), selftest 76/76, validate_patch 0 errors. No research prerequisite (design: none specified).
