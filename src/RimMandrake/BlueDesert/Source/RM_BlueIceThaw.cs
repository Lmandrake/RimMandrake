// BLUEDESERT_MECHANICS_BUILD_1 §3 — blue-ice quarrying's push-your-luck
// thaw roll, DEBRIS-ONLY (the item: "Ship with debris-only rolls first; the
// release table joins when the Horrors item lands").
//
// Every blocksPerRoll blue-ice blocks MINED by a pawn on one map, the face
// rolls once: nothing, or a fallen-debris find (a weighted XML table on the
// comp's props) dropped at the last mined cell.
//
// Engine seams (RimSage, decompiled 1.6, 2026-09-29):
//  - Mineable.DestroyMined(pawn) calls Destroy(KillFinalize) — the same mode
//    an explosion kill uses — so PostDestroy alone cannot tell mining from a
//    blast. Pick hits arrive as DamageDefOf.Mining with the pawn as
//    Instigator (JobDriver_Mine.DoDamage -> TakeDamage), which
//    ThingWithComps forwards to ThingComp.PostPreApplyDamage, so the comp
//    stamps "last hit was mining, by a pawn" there and PostDestroy only
//    counts a block so stamped.
//  - The per-map block counter lives on RM_MapComponent_BlueIceThaw (a
//    MapComponent is auto-instantiated per map by the engine for every
//    subclass; saved with the map).
//
// Cold-cutting (§2, not built): the Warnings ladder's tier-(ii) technique
// suppresses this roll. RM_MapComponent_BlueIceThaw.ColdCuttingSuppresses is
// the single seam it plugs into; today it returns false (no tier can be
// earned yet, so nothing is suppressed).
//
// Gate: RM_BlueDesertSettings.masterEnabled && thawRollEnabled. Off: blue ice
// mines cleanly to its item with no roll, exactly the pre-mechanic behaviour.

using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.BlueDesert
{
    public class RM_ThawDebrisOption
    {
        public ThingDef thing;
        public IntRange count = new IntRange(1, 1);
        public float weight = 1f;
    }

    public class CompProperties_BlueIceThaw : CompProperties
    {
        public int blocksPerRoll = 3;
        public float debrisChance = 0.35f;
        public List<RM_ThawDebrisOption> debris;

        public CompProperties_BlueIceThaw()
        {
            compClass = typeof(RM_CompBlueIceThaw);
        }

        public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string e in base.ConfigErrors(parentDef))
            {
                yield return e;
            }
            if (blocksPerRoll < 1)
            {
                yield return "CompProperties_BlueIceThaw.blocksPerRoll must be >= 1.";
            }
            if (debris.NullOrEmpty())
            {
                yield return "CompProperties_BlueIceThaw has no debris options: every roll would find nothing.";
            }
            else
            {
                foreach (RM_ThawDebrisOption opt in debris)
                {
                    if (opt?.thing == null)
                    {
                        yield return "CompProperties_BlueIceThaw has a debris option with no thing.";
                    }
                }
            }
        }
    }

    public class RM_CompBlueIceThaw : ThingComp
    {
        // JobDriver_Mine.DoDamage lands every hit but the last through
        // TakeDamage(Mining) and then finishes the block with a direct
        // DestroyMined(actor) that raises NO damage — so the stamp comes from
        // the earlier hits (MaxHitPoints 260 vs 40 per pick hit guarantees
        // several). Any non-mining damage clears it, so a blast that finishes
        // a half-mined block is not counted. Saved, because a save can fall
        // between two pick hits.
        private Pawn lastMiner;

        public CompProperties_BlueIceThaw Props => (CompProperties_BlueIceThaw)props;

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_References.Look(ref lastMiner, "rmLastMiner");
        }

        public override void PostPreApplyDamage(ref DamageInfo dinfo, out bool absorbed)
        {
            base.PostPreApplyDamage(ref dinfo, out absorbed);
            lastMiner = dinfo.Def == DamageDefOf.Mining ? dinfo.Instigator as Pawn : null;
        }

        public override void PostDestroy(DestroyMode mode, Map previousMap)
        {
            base.PostDestroy(mode, previousMap);
            Pawn miner = lastMiner;
            lastMiner = null;
            if (mode != DestroyMode.KillFinalize || miner == null || previousMap == null)
            {
                return;
            }
            if (!RM_BlueDesertSettings.masterEnabled || !RM_BlueDesertSettings.thawRollEnabled)
            {
                return;
            }
            RM_MapComponent_BlueIceThaw thaw = previousMap.GetComponent<RM_MapComponent_BlueIceThaw>();
            thaw?.Notify_BlockMined(parent.Position, Props, miner);
        }
    }

    public class RM_MapComponent_BlueIceThaw : MapComponent
    {
        private int blocksSinceRoll;

        public RM_MapComponent_BlueIceThaw(Map map) : base(map)
        {
        }

        /// <summary>The §2 cold-cutting seam: true when this miner's technique
        /// keeps the face below the phase line. No Warnings tier exists yet,
        /// so nothing suppresses the roll.</summary>
        public static bool ColdCuttingSuppresses(Pawn miner)
        {
            return false;
        }

        public void Notify_BlockMined(IntVec3 cell, CompProperties_BlueIceThaw props, Pawn miner)
        {
            if (ColdCuttingSuppresses(miner))
            {
                return;
            }
            if (!RM_BlueKernel.ThawCounts(ref blocksSinceRoll, props.blocksPerRoll))
            {
                return;
            }
            if (!Rand.Chance(props.debrisChance) || props.debris.NullOrEmpty())
            {
                return;
            }
            float[] weights = new float[props.debris.Count];
            for (int i = 0; i < weights.Length; i++)
            {
                weights[i] = props.debris[i]?.thing != null ? props.debris[i].weight : 0f;
            }
            int index = RM_BlueKernel.PickWeighted(weights, weights.Length, Rand.Value);
            RM_ThawDebrisOption pick = index >= 0 ? props.debris[index] : null;
            if (pick?.thing == null)
            {
                return;
            }
            Thing thing = ThingMaker.MakeThing(pick.thing, GenStuff.DefaultStuffFor(pick.thing));
            thing.stackCount = RM_BlueKernel.ThawStack(pick.count.RandomInRange, pick.thing.stackLimit);
            if (GenPlace.TryPlaceThing(thing, cell, map, ThingPlaceMode.Near))
            {
                Messages.Message(
                    "The thawing ice face gave up something the sky dropped long ago: " + thing.LabelCap + ".",
                    new LookTargets(thing), MessageTypeDefOf.PositiveEvent);
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref blocksSinceRoll, "blocksSinceRoll", 0);
        }
    }
}
