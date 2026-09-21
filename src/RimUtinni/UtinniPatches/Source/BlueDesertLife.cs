// BLUE_DESERT_LIFE_AUTHORING_1 (steps 2-5) -- the Blue Desert's hydrocarbon
// fauna and flora: dorrak (Swallower), krissek (Burner), vekkit (Picker),
// palefloss/glassfern/chimeglobe (the transparent fractal flora), and
// RM_ColdWax (the shared butchery/harvest product).
//
// HOUSED TEMPORARILY in RimUtinni/UtinniPatches -- namespace RimMandrake.BlueDesert
// on purpose, NOT RimMandrake.Utinni.UtinniPatches. The design brief
// (design/Jawa/worldbuilding/creatures/blue_desert_hydrocarbon_life.md §0c) rules
// this content RimMandrake tier (mandrake.rm.bluedesert), but that mod does not
// exist yet -- BLUEDESERT_RM_MOD_BUILD_1 is the separate item that scaffolds it.
// Until then this lives here, wired onto the live RUT_BlueDesert biome def, so
// the biome has real spawnable life now rather than waiting on that mod split.
// MIGRATION NOTE: when BLUEDESERT_RM_MOD_BUILD_1 lands, this whole file moves
// into that mod's Source/ unchanged -- only .csproj membership and the
// Assemblies/ output path change, never the namespace or a class name, so no
// def's Class="RimMandrake.BlueDesert...." reference needs editing either.
//
// Every mechanic here is read from 1.6 engine source, not invented -- see the
// brief's §1 "Engine facts" and §2 "the shared mechanism" for citations and
// line numbers. Settings gates read RimMandrake.Utinni.UtinniPatches.
// UtinniPatchesSettings (this mod's existing settings screen), for the same
// reason: no RimMandrake.BlueDesert settings screen exists yet either --
// migrate those fields alongside this file when the split happens.
//
// KNOWN GAP, named rather than solved (brief §2e/§10): a corpse of any of these
// three natives does NOT carry RM_CompRuinedDetonator or the hump-destruction
// comp -- ThingDefGenerator_Corpses builds each corpse ThingDef from the race
// def and does not copy this mod's comps onto it. A warm corpse is therefore
// the one warm-safe hydrocarbon organic left standing against sheet §6 ban 3.
// Closing it needs a def-gen patch keyed on RM_HydrocarbonNativeExtension;
// filed as owed build work, not attempted here.

using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

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
            if (!RimMandrake.Utinni.UtinniPatches.UtinniPatchesSettings.nativeDetonationsEnabled)
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
            if (!RimMandrake.Utinni.UtinniPatches.UtinniPatchesSettings.floraChainReactionsEnabled)
            {
                warmTicksInARow = 0;
                return;
            }
            if (parent.Map == null)
            {
                return;
            }
            float threshold = RimMandrake.Utinni.UtinniPatches.UtinniPatchesSettings.warmDetonationThresholdC;
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
            if (!RimMandrake.Utinni.UtinniPatches.UtinniPatchesSettings.floraChainReactionsEnabled)
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
            if (!RimMandrake.Utinni.UtinniPatches.UtinniPatchesSettings.coldWaxWarmReactiveEnabled)
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
            if (!RimMandrake.Utinni.UtinniPatches.UtinniPatchesSettings.burnerHaloEnabled)
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
    // 2f. Foreign (water-based) grazers pay for eating the flora; the three
    // natives' own hydrocarbon metabolism is exempt, in code.
    // -----------------------------------------------------------------
    public class RM_IngestionOutcomeDoer_ButaneGut : IngestionOutcomeDoer_GiveHediff
    {
        protected override void DoIngestionOutcomeSpecial(Pawn pawn, Thing ingested, int ingestedCount)
        {
            if (!RimMandrake.Utinni.UtinniPatches.UtinniPatchesSettings.butaneGutEnabled)
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
