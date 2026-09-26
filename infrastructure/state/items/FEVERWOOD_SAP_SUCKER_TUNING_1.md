# FEVERWOOD_SAP_SUCKER_TUNING_1 — real numbers and the mishandling trigger

## spec

Follow-on from `FEVERWOOD_SAP_SUCKER_GUILD_1` (closed), same pattern as
`FEVERWOOD_TENTACLE_SETPIECE_TUNING_1`/`FEVERWOOD_DIANOGA_TANK_TUNING_1`: the
guild build shipped real, compiling, deterministic mechanisms with every
numeric field flagged `INVENTED placeholder` in-file, per
`fever_wood_deep_and_mud_2026-09-23.md` §6n/§7 and
`fever_wood_fauna_roster_2026-09-23.md` §7 explicitly leaving these unset
rather than letting an agent guess them.

Owed:

1. **Every INVENTED stat/value** in
   `src/RimMandrake/FeverWood/Defs/ThingDefs_Races/RM_SapSuckerGuild.xml`
   (MoveSpeed/Wildness/MarketValue/combatPower/wildGroupSize/manhunter
   chances on `RM_SapSuckerBase` and all four species),
   `RM_SapSuckerGuild_Hediffs.xml` (RM_Hediff_SapSealed/RM_Hediff_Swollen
   stat offsets, severityPerDay decay rates), and
   `RM_SapSuckerGuildProducts.xml` (market values, rot rates, stack limits
   on RM_ThornbugNectar/RM_VaulmLacquer/RM_DrommathSap/RM_DrommathBurstSap).
   None of these are ruled; a real tuning pass (or an owner card) is owed.

2. **The "mishandled" refusal trigger** (`fever_wood_deep_and_mud_2026-09-23
   .md` §6n: *"they still trigger their refusal when frightened or
   mishandled"* — the guild build only shipped the damage-taken half of
   this, verified real against `RM_CompPlantAlarm`/`RM_CompGrappler`'s
   already-shipped `PostPostApplyDamage` precedent. Which job/interaction
   hook fires on a FAILED taming/training attempt specifically (as opposed
   to combat damage) is a real engine question this pass could not verify
   — RimSage does not connect from this machine. Whoever picks this up:
   confirm the real seam against source (RimSage on the Desktop, or the
   decompile) before wiring it — do not guess a hook name.

3. **RM_Ollareth's alarm has zero live responders.** `RM_CompProperties_
   PlantAlarm` is wired and fires for real, but no Fever Wood race carries
   `RimMandrake.CreatureBehaviors.RM_AlarmResponderExtension` with tag
   `FeverWoodCrown` yet — the crown's own ambush predator (`RM_Silloch`,
   `fever_wood_fauna_roster_2026-09-23.md` row 7) is not built by any item
   yet, and the current wait-ambush occupant (`RSW_LongtailGorg`) is
   Star-Wars-tier and lives on the RUT/RSW patch layer, out of reach of the
   franchise-free RM mod (Q11a). Tag whichever crown predator lands with
   that extension + tag once it's built — a one-line finish, not a redesign.

4. **Real bespoke art** for `RM_Vaulm`/`RM_Ollareth`/`RM_Drommath` — all
   three currently ship flat-color 128×128 placeholders (checked artpipe
   done/_artsrc/registry.jsonl first; nothing existed for any of the three).
   `RM_Thornbug` already ships real, validated three-facing art recovered
   from `infrastructure/artpipe/_artsrc/feverwood_thornbug_{south,east,
   north}/` — no work owed there.

## Not this item's job

- Anything about ant hives (`FEVERWOOD_ANT_HIVE_DUNGEON_1`, sibling, open).
- `RM_Brathek`'s digging rate, the borers, the crown grazer/predator
  (`RM_Lommerel`/`RM_Silloch`), or the birds (`RM_Chellow`/`RM_Murrelith`/
  `RM_Thavrik`/`RM_Skellick`) — all separate roster rows, none built by
  `FEVERWOOD_SAP_SUCKER_GUILD_1`, none this item's to tune.
