# Aerosol build wave 2026-10-07

(a) DONE. New patch src/RimMandrake/Scarlands/Patches/RM_AerosolScreen_PollutedBiomes.xml adds RM_PollutedBiomeExtension to RM_Wasteland, RM_Cauldron, RM_Contagion (add-if-missing on modExtensions). Patch, not inline XML, because those three mods do not depend on the Warscar assembly and a def naming an absent type is discarded whole. validate_patch: 0 errors, 3 intended warnings (add-if-missing xpath differs).
(b) STOPPED, no change. mandrake.rut.shipshields depends only on Odyssey; RM_CompAerosolScreen lives in RimMandrake.Warscar (mandrake.rm.warscar). Deriving would add a hard assembly dependency: without Warscar, CompShieldParticulateScreen fails to load and ShipShields breaks. Needs an owner/design call: (1) make ShipShields depend on mandrake.rm.warscar, or (2) move RM_CompAerosolScreen + prefixes to a small shared RM assembly that both depend on.
(c) nothing added.
Build: no C# changed, no build run.
