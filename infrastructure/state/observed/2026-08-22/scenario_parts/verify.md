# JAWA_SCENARIO_PARTS_1 — offline verify, BUILD, 2026-08-22

Config: repo + deployed Steam copy + LIVE def set (capture 2026-08-23T05-05-29Z,
578 mods, RimWorld 1.6.4871 rev591). No bridge call — bridge belongs to CHECK.

## clause 1 — validate_patch.py, xpath MATCHING not merely well-formed
=== src/Jawa/Jawa_Patches/Patches/DrillTurret_ShootingJob.xml ===
  info    Operation[1] > match (PatchOperationReplace): 1 match(es)  in MiningCo. DrillTurret (Continued): WorkGivers.xml(1)

OK - 0 errors, 0 warning(s)

=== src/Jawa/Jawa_Patches/Defs/ScenarioDefs/Scenario_Utinni.xml ===

OK - 0 errors, 0 warning(s)

=== src/Jawa/RimMandrake_StarWarsRaces/Defs/GeneDefs/Jawa_MiningDisabled.xml ===
  WARN    GeneDef 'RimMandrake_Jawa_MiningDisabled': <iconPath>UI/Icons/Genes/Skills/Mining/Terrible</iconPath> - no file, folder or _north/_south/_east/_west variant of that path exists under any Textures/ root scanned. Cannot be called a typo: the GAME's own textures are inside Unity asset bundles, not loose files, so a correct vanilla path looks identical to a wrong one from here. 'ui/' is not this mod's namespace either. Check it against a def that already works.

OK - 0 errors, 1 warning(s)
OK TOTAL - 3 file(s), 0 error(s), 1 warning(s)
     ⇒ nothing here fails. 1 warning(s) are advisory; the add-if-missing `nomatch` shape is the common one and is intentional.

## clauses 2-4 — measured against the LIVE def set
LIVE DEF SET — capture 2026-08-23T05-05-29Z, 578 mods, RimWorld 1.6.4871 rev591
(this is the post-load def set the running game built: it answers 'in the LIVE def set'
 without a bridge call, which belongs to CHECK)

== §3  WorkGiverDef workType ==
  Drill                  workType='FSFDrilling'  Core
  OperateDrillTurret     workType='Hunting'     MiningCo. DrillTurret (Continued)

== §1a/§2  the two genes ==
  RimMandrake_Jawa_MiningDisabled    disabledWorkTags='Mining'   aptitudes=None  (RimMandrake - Star Wars Races)
  AptitudeTerrible_Plants            disabledWorkTags='None'     aptitudes=[{'$type': 'Aptitude', 'skill': 'Plants', 'level': -8}]  (Biotech)

== exclusivity: which xenotypes in the WHOLE live set carry each gene ==
  XenotypeDef records in live set: 139
  RimMandrake_Jawa_MiningDisabled    -> 1 xenotype(s): MandrakeJawa
  AptitudeTerrible_Plants            -> 20 xenotype(s): AG_Efreet, AG_Nereid, BS_BrokenTitan, BS_FireJotun, BS_FrostJotun, BS_FrostJotunInBlue, BS_Jotun, BS_Surtr, BS_Svartalf, BS_Ymir, BX_Beliar, Highmate, Hussar, MandrakeJawa, PureBlood, RimMandrakeSithMassassi, RimMandrakeSullustan, RimMandrakeWeequay, Starjack, XylTitan

== §1  the ScenarioDef, as the game resolved it ==
  Jawa_UtinniStart — 5 parts, mod=Jawa Patches (local)
      ScenPart_PlanetLayer
      ScenPart_PlanetLayer
      ScenPart_ConfigPage_ConfigureStartingPawns_Xenotypes
      ScenPart_PlayerPawnsArriveMethod
      ScenPart_GameStartDialog

## clause 5 — the Drill WorkGiver is untouched BY US
  grep Defs/WorkGiverDef[defName="Drill"] across src/          -> 0 hits
  our sole patch: WorkGiverDef[defName="OperateDrillTurret"]/workType, 1 match
  DrillTurret named in only 2 src def files (the patch + the gene comment)

  ⚠️ FINDING: Drill IS re-typed in the live game — workType FSFDrilling, by
     [FSF] Complex Jobs, not by us. FSFDrilling still carries the Mining
     workTAG, so disabledWorkTags:Mining still bars a Jawa from the deep
     drill and the owner-accepted asymmetry HOLDS. The gene def said the
     mechanism was the workTYPE; corrected in place.

## clause 6 — no new textures
  git log --diff-filter=A --name-only fe0064c~1..HEAD -- '*Textures*'  -> 0 files

## what is NOT proven offline, and is CHECK's
  The six-part play test in criteria: a Jawa cannot make a growing zone, cannot
  sow, cannot mine by hand, but CAN operate the laser and CAN harvest/cut/chop;
  a recruited non-Jawa mines normally. Def state is proven; behaviour is not.

## the defName cache is DERIVED and deliberately not committed
2.3 MB, regenerable by machine, so provenance goes in the repo and the bulk does not:

    python3 skills/rimworld-modding/scripts/validate_patch.py <any patch> \
      --defs "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data" \
      --defs "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods" \
      --defs "/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100" \
      --live "…/DefDump/captures/2026-08-23T05-05-29Z" \
      --write-defnames <out.txt>

68,500 defNames / 452 def types. Building it takes ~5 min off the slow /mnt/c mount;
reusing it with --defnames turns a 2-minute validate into seconds.
⚠️ The capture it came from is subject to keep-newest-three pruning and is NOT frozen.
