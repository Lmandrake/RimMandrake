using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Wreckage
{
    // SALVAGE_WRECKAGE_EVERYWHERE_1, design §3c. Loot on CAREFUL salvage only.
    //
    // ThingWithComps.Destroy calls base.Destroy(mode) first (which drops the
    // vanilla costList x resourcesFractionWhenDeconstructed, or killedLeavings
    // when smashed) and then every comp's PostDestroy(mode, mapHeld). So this
    // comp adds a roll on top of vanilla's yield, and only for
    // DestroyMode.Deconstruct: smash a wreck and you get slag, strip it and
    // you get the costList plus this roll. (RimSage, ThingWithComps.Destroy and
    // JobDriver_Deconstruct.FinishedRemoving, read 2026-10-06.)
    //
    // The tier names a ThingSetMakerDef by convention, RM_SalvageLoot_<tier>,
    // and its rare twin RM_SalvageLoot_<tier>_Rare. Plain defs, so the RUT_/
    // RSW_ layers add Star Wars parts by patching the def, never this class.
    public class RM_CompProperties_SalvageLoot : CompProperties
    {
        public string lootTier = "Scrap";

        // Base chance of the rare roll at the reference skill. 0 = no rare roll.
        // PROVISIONAL: design §3c's "1 in 20" for a Hull.
        public float rareChance = 0.05f;

        // Set at resolve time by a noLoot weathering (Picked): no roll of any kind.
        public bool noLoot;

        // Set at resolve time from the weathering (RM_WreckWeatheringDef.extraLoot /
        // salvageHediff), or directly on a def that is not a weathered wreck.
        public ThingSetMakerDef extraLoot;
        public HediffDef salvageHediff;
        public float salvageHediffSeverity;

        public RM_CompProperties_SalvageLoot()
        {
            compClass = typeof(RM_CompSalvageLoot);
        }

        public ThingSetMakerDef CommonMaker => DefDatabase<ThingSetMakerDef>.GetNamedSilentFail("RM_SalvageLoot_" + lootTier);

        public ThingSetMakerDef RareMaker => DefDatabase<ThingSetMakerDef>.GetNamedSilentFail("RM_SalvageLoot_" + lootTier + "_Rare");

        public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string e in base.ConfigErrors(parentDef))
            {
                yield return e;
            }
            if (!noLoot && CommonMaker == null)
            {
                yield return "RM_CompProperties_SalvageLoot: no ThingSetMakerDef RM_SalvageLoot_" + lootTier;
            }
            if (rareChance > 0f && RareMaker == null)
            {
                yield return "RM_CompProperties_SalvageLoot: rareChance > 0 but no ThingSetMakerDef RM_SalvageLoot_" + lootTier + "_Rare";
            }
            if (parentDef.building == null || !parentDef.building.alwaysDeconstructible)
            {
                yield return "RM_CompProperties_SalvageLoot on " + parentDef.defName + ": parent is not alwaysDeconstructible, so the loot can never drop";
            }
        }
    }

    public class RM_CompSalvageLoot : ThingComp
    {
        public RM_CompProperties_SalvageLoot Props => (RM_CompProperties_SalvageLoot)props;

        public override void PostDestroy(DestroyMode mode, Map previousMap)
        {
            base.PostDestroy(mode, previousMap);
            if (mode != DestroyMode.Deconstruct || previousMap == null)
            {
                return;
            }
            Pawn salvager = RM_SalvageContext.Salvager;
            ApplyHazard(salvager);
            if (Props.noLoot || !RM_WreckageSettings.SalvageLootActive)
            {
                return;
            }
            IntVec3 cell = parent.Position;
            var loot = new List<Thing>();

            ThingSetMakerDef common = Props.CommonMaker;
            if (common != null)
            {
                loot.AddRange(common.root.Generate());
            }
            ThingSetMakerDef rare = Props.RareMaker;
            if (rare != null && Props.rareChance > 0f && Rand.Chance(RareChanceFor(salvager)))
            {
                loot.AddRange(rare.root.Generate());
            }
            if (Props.extraLoot != null)
            {
                loot.AddRange(Props.extraLoot.root.Generate());
            }

            float generosity = RM_WreckageSettings.lootGenerosity;
            foreach (Thing t in loot)
            {
                if (t.def.stackLimit > 1 && !Mathf.Approximately(generosity, 1f))
                {
                    t.stackCount = Mathf.Clamp(Mathf.RoundToInt(t.stackCount * generosity), 1, t.def.stackLimit);
                }
                GenPlace.TryPlaceThing(t, cell, previousMap, ThingPlaceMode.Near);
            }
        }

        // The salvager's dose (design §4 Wasteland "radiation on deconstruct"). ToxicBuildup is the
        // vanilla dose the Wasteland's own waste casks deal through tox gas, so it is scaled by
        // ToxicResistance exactly as gas exposure is. No pawn known (a debug destroy) = no dose.
        public void ApplyHazard(Pawn salvager)
        {
            if (Props.salvageHediff == null || salvager == null || salvager.Dead || !RM_WreckageSettings.wreckHazards)
            {
                return;
            }
            float severity = Props.salvageHediffSeverity;
            if (Props.salvageHediff == HediffDefOf.ToxicBuildup)
            {
                severity *= Mathf.Max(0f, 1f - salvager.GetStatValue(StatDefOf.ToxicResistance));
            }
            if (severity > 0f)
            {
                HealthUtility.AdjustSeverity(salvager, Props.salvageHediff, severity);
            }
        }

        // The rare-part chance scales with skill (owner ruling 2026-10-03, design §3c).
        // PROVISIONAL: reads Construction until RM_Salvaging exists (the scavenge
        // design's §4); 0.25x at level 0 rising to 2x at level 20, 1x near level 8.
        // No pawn known (a debug destroy) = 1x.
        public float RareChanceFor(Pawn salvager)
        {
            float factor = 1f;
            if (RM_WreckageSettings.skillScalesRare && salvager?.skills != null)
            {
                int level = salvager.skills.GetSkill(SkillDefOf.Construction).Level;
                factor = Mathf.Lerp(0.25f, 2f, level / 20f);
            }
            return Mathf.Clamp01(Props.rareChance * factor);
        }

        public override string CompInspectStringExtra()
        {
            if (!RM_WreckageSettings.SalvageLootActive)
            {
                return null;
            }
            if (Props.noLoot)
            {
                return "RM_Wreckage_InspectNothingInside".Translate().Resolve();
            }
            string tier = ("RM_Wreckage_Tier_" + Props.lootTier).Translate().Resolve();
            string s = "RM_Wreckage_InspectLootTier".Translate(tier).Resolve();
            if (Props.salvageHediff != null && RM_WreckageSettings.wreckHazards)
            {
                s += "\n" + "RM_Wreckage_InspectHazard".Translate(Props.salvageHediff.label).Resolve();
            }
            return s;
        }
    }
}
