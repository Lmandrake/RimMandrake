# ROLE_KINDS_ARMED_5_OF_5 - the 5x live spawn sweep, 2026-08-21

Config: full 578 minus thereallemon.factioncontrol. Map generated via DEV: Generate
Settlement. 54 arming kinds x 5 spawns = 270 pawns, faction hostile, spawned at one cell,
game paused throughout. Equipment read with `jawa/pawn_get` -> `pawns[0].equipment`.

⚠️ `jawa/pawn_gear` was NOT used to read - it is a WRITER and answers a read with
"Give a ThingDef.", reporting every pawn as bare. That is the documented false pass.
⚠️ And the parameter is `pawn`, not `pawnId`. A first pass passed `pawnId`, which the bridge
silently drops, and the tool returned a brief listing with no equipment field at all - a
clean 0/270 that looked like a catastrophic finding and was my own bug.

VERDICT: **31 of 54 kinds are 5/5. 23 field at least one bare pawn in five rolls.**

Spot-verified on Jawa_Blackstar_Grunt: the two bare ones are Adults aged 28 and 36 wearing
4 and 6 pieces of apparel with empty hands. They are fully generated pawns carrying nothing.

🔑 THE POINT: `jawa/pawnkind_audit` - the engine's own eligibility table - reports ZERO
broken kinds for this filter. It is right, and it is answering a different question. It asks
"can this kind afford its cheapest eligible weapon", which is about the tag pool and the
budget CEILING. It cannot see the ROLL. `weaponMoney` is a RANGE, and a low roll lands below
the cheapest weapon the tags allow, so a kind that is healthy on paper still fields empty
hands some fraction of the time. That is exactly why the item demanded five spawns and not
one.

kinds tested: 54  fully 5/5 armed: 31

Jawa_Blackstar_Grunt                     3/5  JawaIon_Blaster,OuterRim_CyclerRifle,VFEPGun   <-- BARE
Jawa_Blackstar_Heavy                     5/5  guy762_lgtrepeater_carbine
Jawa_Blackstar_Leader                    5/5  OuterRim_A180Blaster,OuterRim_DG29Blaster,Ou
Jawa_Blackstar_Specialist                5/5  OuterRim_IonBlaster,OuterRim_T21RepeatingBla
Jawa_DeepDesert_Grunt                    5/5  MA_MegaboneClub,OuterRim_GaderffiiStick
Jawa_DeepDesert_Heavy                    4/5  BMT_RoyalRhinoHorn,MA_AminoxHorn,MA_Megabone   <-- BARE
Jawa_DeepDesert_Leader                   5/5  BMT_RoyalRhinoHorn,MA_Brontorhin,MA_ClawSabe
Jawa_DeepDesert_Specialist               5/5  guy762_slugrifle_SovTusken,guy762_slugrifle_
Jawa_Deepwater_Grunt                     5/5  guy762_hvypistol,guy762_sonrifle_carbine
Jawa_Deepwater_Heavy                     3/5  guy762_lgtrepeater_carbine   <-- BARE
Jawa_Deepwater_Leader                    5/5  OuterRim_VibroAxe,OuterRim_VibroDagger,Outer
Jawa_Deepwater_Specialist                4/5  OuterRim_VibroBlade,OuterRim_VibroDagger,Out   <-- BARE
Jawa_Droid_Grunt                         5/5  OuterRim_DroidWeapon_TwinWristBlaster,OuterR
Jawa_Droid_Heavy                         5/5  OuterRim_DroidWeapon_WristBlaster,OuterRim_D
Jawa_Droid_Leader                        4/5  OuterRim_DroidWeapon_BlasterCannon,OuterRim_   <-- BARE
Jawa_Droid_Specialist                    3/5  OuterRim_DroidWeapon_BlasterCannon,OuterRim_   <-- BARE
Jawa_Empire_Grunt                        2/3  OuterRim_SE14RBlaster   <-- BARE
Jawa_Empire_Heavy                        4/4  OuterRim_DLT19HeavyBlasterRifle,OuterRim_E22
Jawa_Empire_Leader                       4/5  OuterRim_A180Blaster,OuterRim_DE10Blaster,Ou   <-- BARE
Jawa_Empire_Specialist                   5/5  OuterRim_A180Blaster,OuterRim_DG29Blaster,Ou
Jawa_Gamorrean_Enforcer                  4/5  guy762_vaxe,guy762_vaxe_hutt,guy762_vglaive   <-- BARE
Jawa_Gamorrean_Guard                     4/5  guy762_baton,guy762_vaxe   <-- BARE
Jawa_Geonosian_Grunt                     5/5  guy762_sonpistol,guy762_sonrifle
Jawa_Geonosian_Heavy                     4/5  guy762_lgtrepeater,guy762_lgtrepeater_carbin   <-- BARE
Jawa_Geonosian_Leader                    5/5  guy762_sonpistol_bothan,guy762_sonrifle,guy7
Jawa_Geonosian_Specialist                5/5  guy762_sonrifle,guy762_sonrifle_bothan
Jawa_Helix_Grunt                         5/5  guy762_bpistol_republic,guy762_hvypistol,guy
Jawa_Helix_Heavy                         5/5  guy762_bowcaster,guy762_disrifle,guy762_disr
Jawa_Helix_Leader                        5/5  guy762_ionpistol_aratech,guy762_ionrifle_bar
Jawa_Helix_Specialist                    5/5  OuterRim_DLT19XTargetingBlaster,OuterRim_T21
Jawa_Homestead_DesertRanger              5/5  guy762_slugrifle
Jawa_Homestead_Grunt                     5/5  guy762_bpistol,guy762_holdout
Jawa_Homestead_Heavy                     5/5  VFEPGun_MiniBlaster,guy762_hvypistol,guy762_
Jawa_Homestead_Leader                    4/5  OuterRim_BARMST12Scattergun,guy762_bpistol_r   <-- BARE
Jawa_Homestead_Specialist                4/5  OuterRim_CyclerRifle   <-- BARE
Jawa_Hutt_Grunt                          5/5  guy762_bpistol,guy762_holdout,guy762_sonpist
Jawa_Hutt_Heavy                          5/5  guy762_brifle,guy762_carbine
Jawa_Hutt_Leader                         3/5  guy762_bpistol_onasi,guy762_ionpistol_aratec   <-- BARE
Jawa_Hutt_Specialist                     5/5  guy762_bpistol_mandalorian,guy762_bpistol_re
Jawa_Junkers_Grunt                       3/5  MeleeWeapon_Knife,RR_Weapon_Torch,VFET_Stake   <-- BARE
Jawa_Junkers_Heavy                       5/5  guy762_bpistol,guy762_holdout
Jawa_Junkers_Leader                      4/5  OuterRim_GaderffiiStick   <-- BARE
Jawa_Junkers_Specialist                  5/5  guy762_slugrifle
Jawa_TradeMoot_Grunt                     3/5  guy762_holdout,guy762_ionpistol   <-- BARE
Jawa_TradeMoot_Heavy                     4/5  guy762_bpistol,guy762_dispistol,guy762_ionpi   <-- BARE
Jawa_TradeMoot_Leader                    5/5  guy762_ionpistol,guy762_ionrifle_bothan,guy7
Jawa_TradeMoot_Specialist                5/5  IW_Gun_IonPDW,IW_Gun_IonPistol,guy762_ionrif
Jawa_Tribal_Elder                        4/4  BMT_BunkerClaw,MA_DuskSpear,MankaTooth,Melee
Jawa_Tribal_Scavenger                    4/5  BMT_FungalMantisClaw,BMT_PustuleHornetStinge   <-- BARE
Jawa_Tribal_Slinger                      5/5  NerveSpiker,VWE_Throwing_Knives
Jawa_Wildsteam_Grunt                     4/5  guy762_bowcaster   <-- BARE
Jawa_Wildsteam_Heavy                     4/5  guy762_lgtrepeater   <-- BARE
Jawa_Wildsteam_Leader                    4/5  guy762_bowcaster_war   <-- BARE
Jawa_Wildsteam_Specialist                4/5  OuterRim_VibroBlade,OuterRim_VibroCleaver,Ou   <-- BARE

KINDS NOT 5/5: ['Jawa_Gamorrean_Guard', 'Jawa_Gamorrean_Enforcer', 'Jawa_Tribal_Scavenger', 'Jawa_Empire_Grunt', 'Jawa_Empire_Leader', 'Jawa_Hutt_Leader', 'Jawa_Homestead_Specialist', 'Jawa_Homestead_Leader', 'Jawa_DeepDesert_Heavy', 'Jawa_Droid_Specialist', 'Jawa_Droid_Leader', 'Jawa_Wildsteam_Grunt', 'Jawa_Wildsteam_Heavy', 'Jawa_Wildsteam_Specialist', 'Jawa_Wildsteam_Leader', 'Jawa_Deepwater_Heavy', 'Jawa_Deepwater_Specialist', 'Jawa_Geonosian_Heavy', 'Jawa_Blackstar_Grunt', 'Jawa_TradeMoot_Grunt', 'Jawa_TradeMoot_Heavy', 'Jawa_Junkers_Grunt', 'Jawa_Junkers_Leader']
