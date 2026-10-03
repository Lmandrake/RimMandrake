# WARSCAR_FREE_TIER_BODY_1 work log (2026-10-03)
Choices recorded as made.
- Base: recovered WIP branch origin/wip/warscar-free-tier-body-recovered (stale base) cherry-extracted by file, not merged. Re-read every def before use.
- Totchak: RM_Totchak already exists (WARSCAR_TOTCHAK_WAKES_1); WIP's duplicate dropped. Art wired (3 facings + dormant PNG kept unreferenced). NOT a wildAnimals row: genstep-only by that item's design (spec criterion "lists totchak inline" overridden).
- Art: ALL real, from artpipe _artsrc (WIP shipped flat placeholders for chatrak/totchak/tetchik/lichen/scrapings; real jobs were already done). Pallbearer/scar roach art copied from existing RUT textures; glower = rutglower_v1, glower crust = rutglowercrust_v1 (_a.png).
- Save check (CANONICAL_ASHKARR_START_2026-09-12.rws, probe <def>Human</def>=75): RUT_MortuaryCrawler 0 -> def deleted outright; RUT_ScarRoach 3 list refs, 0 pawns -> RUT_ScarRoach kept as hidden alias (wildBiomes removed). RUT_MortuaryCrawler textures left in UtinniPatches (orphan, harmless).
- Corpse-eating: vanilla CarnivoreAnimal behaviour; no RM_Filth_PickedBones shipped (spec allowed vanilla dessicated).
- Harmony: existing PatchAll(assembly) in RM_Totchak/RM_Chotrix patches the new patch classes; no extra PatchAll added (would double-apply).
- Tetchik gate: Harmony postfix on WildAnimalSpawner.CommonalityOfAnimalNow (private, signature confirmed via RimSage). Chatrak plate no-dye: prefix on CompColorable.DesiredColor setter.
- Settings: enableChatrak/Tetchik/Pallbearer/ScarRoach/InterimDonors/WreckLichenSeeder; startup removes rows. About: +CreatureBehaviors dep (RM_EatCleanableExtension).
- Outside Scarlands (needed for retire/alias): src/RimUtinni/{RustCathedralRoaches RUT_ScarRoach.xml, UtinniPatches RUT_Scarlands.xml, WildAnimals_Warscar.xml, RUT_MortuaryCrawler.xml deleted}.
