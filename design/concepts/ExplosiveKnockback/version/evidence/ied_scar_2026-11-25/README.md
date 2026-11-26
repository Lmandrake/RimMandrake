# Why an IED blast's crater scar went missing (RIMMANDRAKE_FIND_KNOCKBACK_IED_SCAR_MISSING_ONE_RUN_IN_THREE)

Instrument: LayScar writes a `scar` record per blast in RM_KnockbackJournal (laid, or why the cell refused it), and
RM_Patch_Filth_ScarGone writes `scar_gone` with the calls that removed a scar (build of d62ff67597). Probe:
`probe_ied_scar_journal.py`, 24 IEDs on soil set off one by one on a fresh quicktest map on ArchSmall, 2026-11-25.

- `probe1_roof_collapse.txt` (before the scene library repair 595acb512e): the station lay under a mountain roof. The
  station clean destroyed the rock and left the roof unsupported; on the first tick RoofCollapserImmediate dropped it,
  killed the first scar (KillFinalize) and crushed all 24 IEDs at once. SITE, repaired in the scene library: a cleaned
  station now loses its roof before anything is staged.
- `probe2_rot_thinning.txt` (after the repair): 24 of 24 scars laid, 0 refused. 8 of 24 were gone at 300 ticks, each
  removed (Vanish) by EnvironmentalHazards RM_MapComponent_AcceleratedRot.ThinOutdoorFilth: The Rot's living ground
  thins every outdoor filth (15% each 250 ticks); a scar has thickness 1, so one thinning removes it. Fresh quicktest maps
  and the RM_Stage_ExplosiveKnockback save lie on The Rot (tile 92494, biome RM_TheRot).

Visit 1's one miss carries no journal (the instrument did not exist). Its frame shows a giant agarilux, The Rot's flora,
and no collapsed rock, so the Rot's thinning is the likely cause [guess ~90%].

Ruling (delegated, evidence-for-ask): The Rot's design says "Filth barely accumulates"; its ground digesting a crater is a
physical condition of that biome (GUIDING_PRINCIPLES entry 1), so neither mod changes. The two blast-show scenes hold
that other mod's setting (`acceleratedRotEnabled`) off for their run, so their scar rows judge this mod alone.
