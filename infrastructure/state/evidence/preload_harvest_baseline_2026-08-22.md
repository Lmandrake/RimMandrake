# Pre-load harvest baseline — captured 2026-08-22 by BUILD

_The readings from the PREVIOUS session's Player.log, taken BEFORE the next cold load,
so the load's own harvest is a delta and not a fresh guess. Every RED below is expected
to move; a RED that does NOT move is the finding._

```

WHICH RUN IS THIS
  log            /mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Player.log
  1,934,280 lines   last written 2026-08-22 08:40:10
  build          RimWorld 1.6.4871 rev591
  state          EXITED - this run is over, the game is not writing to it
  ModsConfig     578 active mods, written 2026-08-21 04:00:27  (-103183s vs the log)

STANDING CHECKS
    ok  DEAD MODS (static ctor)              0   = baseline 0
        a dead mod is the highest-priority finding in any log
    ok  DEAD MODS (type load)                0   = baseline 0
        was 2+24 for RimAI; the load-order fix should take these to 0
   RED  DEFS DISCARDED                     103   ABOVE baseline 2
        baseline 2 = Onimods torches (benign). Was 5; 3 were RimAI collateral
   RED  cross-reference (def loader)       128   ABOVE baseline 25
        16 Punch_HitBuilding + 1 VWE_Tool_Whip + 8 BMT_* = 25, all triaged. 2026-08-22 read 128: the excess 101 were ALL 'No RimWorld.SkillDef named li', one per cast def discarded by CAST_ROSTER_SKILLS_DISCARDED_1. When that lands this should fall straight back to 25 - if it does not, the remainder is NEW
   RED  stale saved data (Scribe)            8   ABOVE baseline 0
        a SAVED FILE holds a dead name - different system from cross-ref. The 8 seen 2026-08-22 were cleaned out of pokean.xtp and Deep Storage's settings; any hit now is NEW
    ok  Harmony patch failures (C#)          1   = baseline 1
        baseline 1 = HAR vs Universal Pregnancy on CanEverProduceChild, triaged. ANY rise means a new transpiler collision - name the target METHOD
    ok  texture path failures                0   = baseline 0
        fires ONLY if ALL directions missing - a partial set is silent
    ok  patch operations failed              5   = baseline 5
        5 = 3 Intimacy + 1 Mining Outpost + 1 Biomes! Caverns, all pre-existing and all other mods. A 6th is NEW - read it with --show patchfail
    ok  dictionary field given <li> children     0   = baseline 0
        was 28 for JawaWorld_BiomeMix before 2026-08-19. A dictionary-keyed field fed <li> loses the WHOLE field and keeps loading. Same family as B56, where the reverse shape discarded five FactionDefs outright
    ok  defNames we retired (should be extinct)     0   = baseline 0
        OuterRim_Jawa and BTD_Jawa both stopped existing when the donor mods went off; HC_gamorreanaxe never existed at all. Retargeted 2026-08-19/20

QUEUED FOR THIS LOAD
    ok  MegafaunaYield fix (THE must-confirm)      0   = baseline 0
    ok  Jawa_Patches ops                           0   = baseline 0
    ok  JawaVoice ops                              2   = baseline 2
    ok  Jawa eye glow art resolved                 0   = baseline 0
    ok  Hutt reptile eyes resolved                 0   = baseline 0
    ok  Hutt feline eyes (saved pawns)             0   = baseline 0
    ok  Twi'lek Lekku head types                   0   = baseline 0
    ok  Wookiee head swap                          0   = baseline 0
    ok  RimAI errors (fix should hold)             0   = baseline 0
    ok  Rebel suppression collateral               0   = baseline 0
    ok  Outer Rim new-mod errors                   0   = baseline 0
    ok  LK mineables / mineshaft errors            0   = baseline 0

EXPECTED PRESENT (absence is the finding)
    ok  RimAI Core booted                          1   present
    ok  Inhabited ready (READ THE COUNT)           1   present

THE LOG CANNOT ANSWER THESE - go and look
  A green run above does NOT cover any of the following.
  [ ]  JawaIonWeapons - ion vs a KotOR droid ACTUALLY does something
        Dev-spawn a KotOR droid, hit it with the ion weapon. Want: severity
        climbs, 'downed: true', pawn still exists (stunned, not killed).
        PROTECT THIS TEST IF THE SESSION RUNS SHORT - a clean log is NOT
        evidence it worked, and no other observation substitutes.
  [ ]  W6 - Rebel Alliance faction is ABSENT
        World map -> faction list. NOT the visible tiles; scroll the list. A
        settlement anywhere means the suppression did not apply.
  [ ]  W6 - OuterRim_A280Blaster still SPAWNS
        Dev mode -> spawn the weapon. This is the half that proves the
        suppression cut the faction WITHOUT taking its gear with it.
  [ ]  Hutt eyes at drawSize 0.42 read as TWO separated eyes
        Dev-spawn a FRESH Hutt. Too small -> 0.48. Never above 0.55, which
        is measured to abut.
  [ ]  V2 Ideology lines fire
        Needs the game UNPAUSED - SpeakUp will not fire at TPS 0. Prisoner
        AND slave.

REMEMBER
  A no-op patch logs NOTHING. PatchOperationConditional and
  PatchOperationFindMod both return true on no match, so a clean
  log is not evidence the eyes, the yields or the art worked.
  Those are settled on screen. Use --show <key> to read lines.

```
