# ROT_HEALTH_SHARING_1

## ruled table
The owner's Rot fauna sitting, RULED 2026-09-18 (ledger OWNER note 2026-09-19 on this item) on the draft
`Transient/rot_fauna_assignment_draft_20260918.md` (copied here because Transient decays):

- The **kin tag / wound-link / alarm** columns stand AS DRAFTED.
- The **kin-mend column is REPLACED**: heal per day is PROPORTIONAL TO BODY SIZE (one coefficient x
  pawn.BodySize — `CompProperties_KinMending.healPerDayPerBodySize`, default 3 — not a per-clique constant).
  So "mend" below is YES/no only; one hediff (`RM_KinMendingNetwork`) serves every mender.
- Q1 alarm misfires (a grove alarm ringing into empty forest): ACCEPTED as-is.
- Q2: WAIT for BMT_FAUNA_ABSORPTION_1 before patching any race def (done; wired by ROT_FAUNA_KIN_WIRING_1).
- Q3: one kin tag MAY span species within a named clique, **never biome-wide**.

Different tags never interact. Plumbing stays at shipped values (radius 12, share 0.6, gate 8, min 2 kin).

| creature (as drafted) | kin tag | wound-link | kin-mend | alarm | one-line trade |
|---|---|---|---|---|---|
| AA_Agaripod | RotAgarikin | YES | YES | no | herd shares pain and knits together |
| AA_Agaripawn | RotAgarikin | YES | YES | no | same organ as the pod |
| AA_Wildpod | RotWildkin | no | YES | no | fastest healer, only in company |
| AA_Wildpawn | RotWildkin | no | YES | no | same organ as the pod |
| BMT_ChemSnail | RotSlimekin | no | YES | no | flavor mend; commonest kind stays simple to hunt |
| BMT_GiantSnail | RotSlimekin | no | YES | no | joins the slime organ |
| BMT_GiantSlug | RotSlimekin | no | YES | no | joins the slime organ |
| RSW_FungalWeevil | RotBroodmates | no | YES | no | broods recover if survivors remain |
| BMT_Pillbug | RotBroodmates | no | YES | no | same brood organ |
| RSW_BovineBeetle | RotHerd | YES | YES | no | tamed train spreads a raid volley |
| AA_Swarmling | RotSwarm | YES | no | YES | one body: wound one, wound all — both ways |
| AA_MycoidColossus | — | no | no | YES | the forest walks over, when it's near |
| RSW_FungalMantis | — | no | no | YES | the trap you never saw answers |
| BMT_CaveSpider | — | no | no | YES | rare spice response |
| BMT_GlowBat | — | no | no | no | honest none |
| RUT_Emberscythe | — | no | no | no | Pyrelands animal; keep Rot mechanics out of fire country |

## where the rows live now (2026-10-25, ROT_FAUNA_KIN_WIRING_1)
| ruled row | today | wiring |
|---|---|---|
| AA_Agaripod / AA_Agaripawn | RM_Agaripod (gromma) / RM_Agaripawn (rennok) | native, `src/RimMandrake/TheRot/Defs/Fauna/RM_AgariPorts.xml` |
| AA_Wildpod / AA_Wildpawn | RM_Mullgoth / RM_Durrok (LeaningScrub defs) | `src/RimMandrake/TheRot/Patches/RotSpecies_WoundSharing.xml` (xpath-guarded) |
| AA_Swarmling | RM_Chittik | native, `src/RimMandrake/TheRot/Defs/Fauna/RM_Chittik.xml` |
| AA_MycoidColossus | RM_MycoidColossus (vorrugath) | native, `RM_AgariPorts.xml` |
| RSW_FungalWeevil / RSW_FungalMantis | RM_Grellik (grellik) / RM_Skerrith (skerrith) | native, `src/RimMandrake/TheRot/Defs/Fauna/RM_TheRot_Fauna_ThingDefs_Races.xml` (ROTKIN_FIX_RULED_ON_RETIRED_TWIN); the SWBestiary bodies, cast only by the frozen campaign twin RUT_TheRot, get the same rows from `src/RimUtinni/UtinniPatches/Patches/RotFauna_KinWiring.xml` |
| BMT_ChemSnail, GiantSnail, GiantSlug, Pillbug, CaveSpider, GlowBat | **RULED CUT** 2026-09-11 (`design/Jawa/worldbuilding/biomes/caverns_replacement_scoping.md`) | none — no def exists; RotSlimekin is empty, RotBroodmates is grelliks only |
| RSW_BovineBeetle | **no def** (only its larva/pupa remain; its remake as the bodySize-4 Grabber was cut by the owner 2026-10-05, `RM_LanternDeeps.xml`) | none — the RotHerd row is moot |
| RUT_Emberscythe | RM_Emberscythe | none, as ruled |

Alarm responders carry `RM_AlarmResponderExtension` tag `RotGrove`: a responder with a blank tag never answers
(`RM_ReactionResponders.Answers`); the grove plants' blank comp tag matches any tag.
