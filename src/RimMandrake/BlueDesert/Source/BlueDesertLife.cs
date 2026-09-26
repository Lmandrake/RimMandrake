// BLUE_DESERT_LIFE_AUTHORING_1 (steps 2-5), moved here by
// BLUEDESERT_RM_MOD_BUILD_1 -- the Blue Desert's hydrocarbon fauna and flora:
// dorrak (Swallower), krissek (Burner), vekkit (Picker), palefloss/glassfern/
// chimeglobe (the transparent fractal flora), and RM_ColdWax (the shared
// butchery/harvest product).
//
// MIGRATION NOTE (fulfilled): this file previously lived in
// src/RimUtinni/UtinniPatches/Source, namespace RimMandrake.BlueDesert, with
// a header saying it would move here unchanged once this mod existed. It has
// moved unchanged except for one thing: every settings read below now points
// at this mod's own RM_BlueDesertSettings (Source/RM_BlueDesertMod.cs)
// instead of RimMandrake.Utinni.UtinniPatches.UtinniPatchesSettings -- the
// six fields moved there too, in the same change, so default behavior for an
// existing save is unaffected. No def's Class="RimMandrake.BlueDesert...."
// reference needed editing: namespace and every class name are unchanged.
//
// Every mechanic here is read from 1.6 engine source, not invented -- see the
// design brief's §1 "Engine facts" and §2 "the shared mechanism" for
// citations and line numbers:
// design/Jawa/worldbuilding/creatures/blue_desert_hydrocarbon_life.md
//
// KNOWN GAP, named rather than solved (brief §2e/§10): a corpse of any of these
// three natives does NOT carry RM_CompRuinedDetonator or the hump-destruction
// comp -- ThingDefGenerator_Corpses builds each corpse ThingDef from the race
// def and does not copy this mod's comps onto it. A warm corpse is therefore
// the one warm-safe hydrocarbon organic left standing against sheet §6 ban 3.
// Closing it needs a def-gen patch keyed on RM_HydrocarbonNativeExtension;
// filed as owed build work, not attempted here.
//
// SHARED WITH THE PROPANE LAKES (COMMISSION_LEDGER_CLEANUP_1, 2026-09-25): two
// classes here -- RM_CompEffecter_HaloAlways and RM_DeathActionWorker_BurnerBlast
// -- are also wired onto src/RimUtinni/UtinniPatches's own
// RUT_PropaneLakeFauna.xml (RUT_BurnerAscendant, "the Burners, ascendant" --
// the_propane_lakes.md §4's own "shared authoring with the Blue Desert's
// Burners"). RimWorld resolves an XML Class="..." attribute by scanning every
// loaded assembly's types, not by a compile-time or declared-dependency
// reference, so this works regardless of load order as long as
// mandrake.rm.bluedesert is active -- which UtinniPatches' own About.xml now
// declares (loadAfter) as a real, load-bearing dependency created by this move.
//   RM_CompEffecter_Halo: the krissek's own halo -- lit only while
//   jogging/fleeing/fighting/hunting (§4b).
//   RM_CompEffecter_HaloAlways: the propane lake's ascendant form's halo is
//   locomotion itself (the_propane_lakes.md §4: "not a sprint trick... it is
//   LOCOMOTION"), so it shows at any movement, not just Jog+/combat.
//   RM_DeathActionWorker_BurnerBlast: RM_Krissek's OWN shipped description
//   ("it goes, all at once, and the field goes with it") had no mechanism
//   behind it -- checked at authoring time (RM_BlueDesertFauna.xml carried no
//   deathAction node at all). Wraps vanilla DeathActionWorker_BigExplosion
//   (the Boomalope's own mechanism, zero new explosion math) behind this
//   mod's own nativeDetonationsEnabled toggle and wires it onto BOTH
//   RM_Krissek and RUT_BurnerAscendant, so the flavour text finally has teeth.

using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;
using Verse.AI.Group;

namespace RimMandrake.BlueDesert
{
    // Marker extension: "this race is a Blue Desert hydrocarbon native."
    // Read by RM_IngestionOutcomeDoer_ButaneGut (§2f) to exempt natives from
    // their own flora's toxin, and named here as the future key for the
    // corpse-comp gap in the file header above.
    public class RM_HydrocarbonNativeExtension : DefModExtension
    {
    }

    // -----------------------------------------------------------------
    // 3b. The Dorrak's "wrong place" -- destroying the gut kills outright,
    // which then fires the ordinary HediffCompProperties_ExplodeOnDeath
    // already sitting on the same hediff (§1d/§2a). No duplicate explosion
    // logic lives in this comp.
    // -----------------------------------------------------------------
    public class HediffCompProperties_ExplodeOnPartDestroyed : HediffCompProperties
    {
        // BodyPartDef.defName, not a label -- matched by exact defName below.
        public string partDefName = "Hump";

        public HediffCompProperties_ExplodeOnPartDestroyed()
        {
            compClass = typeof(RM_HediffComp_ExplodeOnPartDestroyed);
        }
    }

    public class RM_HediffComp_ExplodeOnPartDestroyed : HediffComp
    {
        public HediffCompProperties_ExplodeOnPartDestroyed Props => (HediffCompProperties_ExplodeOnPartDestroyed)props;

        public override void Notify_PawnPostApplyDamage(DamageInfo dinfo, float totalDamageDealt)
        {
            base.Notify_PawnPostApplyDamage(dinfo, totalDamageDealt);
            if (!RM_BlueDesertSettings.masterEnabled || !RM_BlueDesertSettings.nativeDetonationsEnabled)
            {
                return;
            }
            Pawn pawn = Pawn;
            if (pawn == null || pawn.Dead || pawn.health == null)
            {
                return;
            }
            BodyPartRecord hitPart = dinfo.HitPart;
            if (hitPart == null || hitPart.def == null || hitPart.def.defName != Props.partDefName)
            {
                return;
            }
            if (!pawn.health.hediffSet.PartIsMissing(hitPart))
            {
                return; // wounded there, not destroyed -- an ordinary injury
            }
            pawn.Kill(dinfo);
        }
    }

    // -----------------------------------------------------------------
    // 2b. Flora charge -- the fractal flora's warm-detonation chain.
    // -----------------------------------------------------------------
    public class CompProperties_PlantCharge : CompProperties
    {
        public float radius = 1.1f;
        public float damage = 40f;
        public float fireChance = 0.2f;

        public CompProperties_PlantCharge()
        {
            compClass = typeof(CompPlantCharge);
        }
    }

    public class CompPlantCharge : ThingComp
    {
        // Two consecutive Long ticks (~66s game time, §2b) before a single
        // warm reading (e.g. a nearby blast's heat) chains the whole field.
        private int warmTicksInARow;

        public CompProperties_PlantCharge Props => (CompProperties_PlantCharge)props;

        public override void CompTickLong()
        {
            if (!RM_BlueDesertSettings.masterEnabled || !RM_BlueDesertSettings.floraChainReactionsEnabled)
            {
                warmTicksInARow = 0;
                return;
            }
            if (parent.Map == null)
            {
                return;
            }
            float threshold = RM_BlueDesertSettings.warmDetonationThresholdC;
            if (parent.AmbientTemperature > threshold)
            {
                warmTicksInARow++;
                if (warmTicksInARow >= 2)
                {
                    parent.Kill(new DamageInfo(DamageDefOf.Flame, 99999f));
                }
            }
            else
            {
                warmTicksInARow = 0;
            }
        }

        public override void PostDestroy(DestroyMode mode, Map previousMap)
        {
            base.PostDestroy(mode, previousMap);
            // §1g: eating (Vanish) and cutting/harvesting (KillFinalizeLeavingsOnly)
            // are both safe. Only a kill by damage (KillFinalize) fires --
            // a bullet, a flame, or a neighbouring plant/creature's blast.
            if (mode != DestroyMode.KillFinalize)
            {
                return;
            }
            if (!RM_BlueDesertSettings.masterEnabled || !RM_BlueDesertSettings.floraChainReactionsEnabled)
            {
                return;
            }
            if (previousMap == null)
            {
                return;
            }
            GenExplosion.DoExplosion(
                center: parent.Position,
                map: previousMap,
                radius: Props.radius,
                damType: DamageDefOf.Flame,
                instigator: null,
                damAmount: Mathf.RoundToInt(Props.damage),
                chanceToStartFire: Props.fireChance);
        }
    }

    // -----------------------------------------------------------------
    // 2c. RM_ColdWax -- CompExplosive does not listen for CompTemperatureRuinable's
    // "RuinedByTemperature" signal on its own; this comp is the missing wire.
    // -----------------------------------------------------------------
    public class RM_CompRuinedDetonator : ThingComp
    {
        public override void ReceiveCompSignal(string signal)
        {
            base.ReceiveCompSignal(signal);
            if (signal != CompTemperatureRuinable.RuinedSignal)
            {
                return;
            }
            if (!RM_BlueDesertSettings.masterEnabled || !RM_BlueDesertSettings.coldWaxWarmReactiveEnabled)
            {
                return;
            }
            CompExplosive explosive = parent.GetComp<CompExplosive>();
            explosive?.StartWick();
        }
    }

    // -----------------------------------------------------------------
    // 4b. The Burner's halo -- lit only while moving fast, fighting, or
    // hunting; a grazing walk shows nothing (§4b).
    // -----------------------------------------------------------------
    public class RM_CompEffecter_Halo : CompEffecter
    {
        protected override bool ShouldShowEffecter()
        {
            if (!RM_BlueDesertSettings.masterEnabled || !RM_BlueDesertSettings.burnerHaloEnabled)
            {
                return false;
            }
            if (!base.ShouldShowEffecter())
            {
                return false;
            }
            Pawn pawn = parent as Pawn;
            if (pawn == null)
            {
                return false;
            }
            bool jogging = pawn.pather != null && pawn.pather.MovingNow
                && pawn.CurJob != null && pawn.CurJob.locomotionUrgency >= LocomotionUrgency.Jog;
            bool aggro = pawn.InAggroMentalState;
            bool targeting = pawn.mindState != null && pawn.mindState.enemyTarget != null;
            return jogging || aggro || targeting;
        }
    }

    // -----------------------------------------------------------------
    // 4c. The propane lake's ascendant Burner -- the halo is locomotion,
    // not a sprint/combat tell, so it shows at ANY movement (the_propane_
    // lakes.md §4). Sibling of RM_CompEffecter_Halo rather than a subclass
    // of it: the parent's ShouldShowEffecter is itself the jog/aggro/target
    // gate, so subclassing it would fight the override instead of loosening
    // it. Same settings gate and effecter plumbing.
    // -----------------------------------------------------------------
    public class RM_CompEffecter_HaloAlways : CompEffecter
    {
        protected override bool ShouldShowEffecter()
        {
            if (!RM_BlueDesertSettings.masterEnabled || !RM_BlueDesertSettings.burnerHaloEnabled)
            {
                return false;
            }
            if (!base.ShouldShowEffecter())
            {
                return false;
            }
            Pawn pawn = parent as Pawn;
            if (pawn == null)
            {
                return false;
            }
            return pawn.pather != null && pawn.pather.MovingNow;
        }
    }

    // -----------------------------------------------------------------
    // 4d. The Burner lineage's death -- "it goes, all at once, and the field
    // goes with it" (RM_Krissek's own shipped description). Wraps vanilla
    // DeathActionWorker_BigExplosion (Boomalope's own mechanism) behind this
    // mod's existing native-detonation toggle rather than firing unconditionally.
    // -----------------------------------------------------------------
    public class RM_DeathActionWorker_BurnerBlast : DeathActionWorker_BigExplosion
    {
        public override void PawnDied(Corpse corpse, Lord prevLord)
        {
            if (!RM_BlueDesertSettings.masterEnabled || !RM_BlueDesertSettings.nativeDetonationsEnabled)
            {
                return;
            }
            base.PawnDied(corpse, prevLord);
        }
    }

    // -----------------------------------------------------------------
    // 2f. Foreign (water-based) grazers pay for eating the flora; the three
    // natives' own hydrocarbon metabolism is exempt, in code.
    // -----------------------------------------------------------------
    public class RM_IngestionOutcomeDoer_ButaneGut : IngestionOutcomeDoer_GiveHediff
    {
        protected override void DoIngestionOutcomeSpecial(Pawn pawn, Thing ingested, int ingestedCount)
        {
            if (!RM_BlueDesertSettings.masterEnabled || !RM_BlueDesertSettings.butaneGutEnabled)
            {
                return;
            }
            if (pawn?.def != null && pawn.def.HasModExtension<RM_HydrocarbonNativeExtension>())
            {
                return; // the Swallower's "anaerobic gut" and the other natives' own metabolism
            }
            base.DoIngestionOutcomeSpecial(pawn, ingested, ingestedCount);
        }
    }
}
