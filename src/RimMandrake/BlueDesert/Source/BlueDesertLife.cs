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
using Verse.Sound;

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
            Pawn pawn = Pawn;
            if (pawn == null || pawn.health == null)
            {
                return;
            }
            BodyPartRecord hitPart = dinfo.HitPart;
            bool matches = hitPart != null && hitPart.def != null && hitPart.def.defName == Props.partDefName;
            // wounded there, not destroyed -- an ordinary injury
            if (!RM_BlueKernel.PartKills(RM_BlueDesertSettings.masterEnabled && RM_BlueDesertSettings.nativeDetonationsEnabled, !pawn.Dead, matches,
                    matches && pawn.health.hediffSet.PartIsMissing(hitPart)))
            {
                return;
            }
            pawn.Kill(dinfo);
        }
    }

    // The seven natives' (non-vhaulk) death charges: vanilla HediffComp_ExplodeOnDeath, gated on the mod settings.
    // LIVE 2026-10-03 (krissek_off_quiet): the vanilla comp ignores RM_BlueDesertSettings, so "Native detonations off"
    // still blew a colonist beside a dying krissek. Same blast, same fields; only the two toggles are new.
    public class HediffCompProperties_GatedExplodeOnDeath : HediffCompProperties_ExplodeOnDeath
    {
        public HediffCompProperties_GatedExplodeOnDeath()
        {
            compClass = typeof(RM_HediffComp_GatedExplodeOnDeath);
        }
    }

    public class RM_HediffComp_GatedExplodeOnDeath : HediffComp_ExplodeOnDeath
    {
        public override void Notify_PawnKilled()
        {
            if (!RM_BlueDesertSettings.masterEnabled || !RM_BlueDesertSettings.nativeDetonationsEnabled)
            {
                return;
            }
            base.Notify_PawnKilled();
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

        /// <summary>BLUEDESERT_FLORA_EXPANSION_BUILD_1: left behind ONLY when the plant is killed by damage
        /// (KillFinalize), never on cut/harvest. Vanilla killedLeavings also fires on harvest
        /// (GenLeaving.DoLeavingsFor treats KillFinalizeLeavingsOnly as a kill), so the kethevar's char-lace
        /// is dropped here instead.</summary>
        public ThingDef killedLeavingDef;
        public int killedLeavingCount = 1;

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
            bool enabled = RM_BlueDesertSettings.masterEnabled && RM_BlueDesertSettings.floraChainReactionsEnabled;
            bool hasMap = parent.Map != null;
            int action = RM_BlueKernel.ChargeStep(ref warmTicksInARow, enabled, hasMap,
                enabled && hasMap && parent.AmbientTemperature > RM_BlueDesertSettings.warmDetonationThresholdC);
            if (action == 2)
            {
                parent.Kill(new DamageInfo(DamageDefOf.Flame, 99999f));
            }
            else if (action == 1)
            {
                PlayCrackCue();
            }
        }

        // BLUEDESERT_MECHANICS_BUILD_1 §5: the crack cue. Played on the FIRST
        // warm long tick of the two-long-tick countdown above, so a listening
        // player gets roughly one long tick (~33 s) to run before the charge
        // goes. A one-shot, not a sustainer: a plant only ever ticks Long
        // (Plant overrides TickLong, never Tick), and a Sustainer must be
        // Maintain()ed every frame-tick or it ends, so a plant cannot keep one
        // alive. RM_PhaseCrack's maxSimultaneous 1 stops a warming field from
        // stacking a hundred copies.
        private void PlayCrackCue()
        {
            if (!RM_BlueDesertSettings.crackCueEnabled || parent.Map == null)
            {
                return;
            }
            SoundDef crack = DefDatabase<SoundDef>.GetNamedSilentFail("RM_PhaseCrack");
            crack?.PlayOneShot(new TargetInfo(parent.Position, parent.Map));
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
            if (!RM_BlueDesertSettings.masterEnabled)
            {
                return;
            }
            if (previousMap == null)
            {
                return;
            }
            if (Props.killedLeavingDef != null && RM_BlueDesertSettings.floraExpansionEnabled)
            {
                Thing leaving = ThingMaker.MakeThing(Props.killedLeavingDef);
                leaving.stackCount = Props.killedLeavingCount;
                GenPlace.TryPlaceThing(leaving, parent.Position, previousMap, ThingPlaceMode.Near);
            }
            if (!RM_BlueDesertSettings.floraChainReactionsEnabled)
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

    /// <summary>BLUEDESERT_FLORA_EXPANSION_BUILD_1: with the setting off, the four expansion plants are removed from
    /// RM_BlueDesert's wildPlants at startup (takes effect on restart), so the biome degrades to its original four.</summary>
    [StaticConstructorOnStartup]
    public static class RM_BlueDesertFloraGate
    {
        private static readonly string[] Expansion = { "RM_Qeshra", "RM_Kethevar", "RM_Lisqueth", "RM_Vashpuk" };

        static RM_BlueDesertFloraGate()
        {
            if (RM_BlueDesertSettings.floraExpansionEnabled)
            {
                return;
            }
            BiomeDef biome = DefDatabase<BiomeDef>.GetNamedSilentFail("RM_BlueDesert");
            if (biome == null)
            {
                return;
            }
            biome.wildPlants.RemoveAll(r => r.plant != null && System.Array.IndexOf(Expansion, r.plant.defName) >= 0);
        }
    }
}
