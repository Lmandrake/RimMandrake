using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Wreckage
{
    // SALVAGE_WRECKAGE_EVERYWHERE_1, design §3b. A placed wreck is family x weathering:
    // the family (an abstract RM_WreckFamily_* ThingDef parent, Defs/ThingDefs_Buildings/
    // RM_WreckFamilies.xml) is what the wreck WAS; the weathering is what the biome DID
    // to it. One weathering row is shared by every biome with that weathering, so
    // re-tuning "Cooked" re-tunes every cooked wreck. All numbers PROVISIONAL.
    public class RM_WreckWeatheringDef : Def
    {
        // Multiplies the family's deconstruct yield once, at resolve time. Applied to
        // resourcesFractionWhenDeconstructed (the family base sets 1.0), not to the
        // costList counts: GenLeaving's Deconstruct branch is
        // Min(RoundRandom(count * fraction), count) (RimSage, GenLeaving.cs:320), so the
        // expected yield is exactly costList x yieldFactor and a 1-count component is
        // never truncated to 0, while market value (which reads costList) is untouched.
        public float yieldFactor = 1f;

        // Moves the family's loot tier on the ladder Scrap < Hull/Tank/Carapace < Sealed.
        public int lootTierShift;

        // Used only when a child def sets no label: "<prefix> wreck".
        public string labelPrefix;

        // Biome by-product appended to killedLeavings (what smashing leaves).
        public List<ThingDefCountClass> extraLeavings;

        // "Nothing inside": careful salvage gives the costList only, no loot roll at all
        // (the Twilight Deep's picked wrecks, design §4 "Picked: x0.2, no loot roll").
        public bool noLoot;

        // A regional extra roll on careful salvage, on top of the tier tables (design §3c:
        // "Biomes may name an extra ThingSetMaker in the weathering for regional goods").
        public ThingSetMakerDef extraLoot;

        // A dose the salvager takes on careful salvage (design §4 Wasteland: "radiation on
        // deconstruct"; §3b hazards). ToxicBuildup is scaled by the pawn's ToxicResistance.
        // Gated by the "Wreck hazards" setting (design §6).
        public HediffDef salvageHediff;
        public float salvageHediffSeverity;

        // A mineable shell the wreck field rings every wreck of this weathering with at map
        // generation, so it must be mined free before it can be reached (design §4: Grey Deep
        // "Crystal-jacketed: mine the jacket first", Blue Desert "Ice-locked: must mine free first").
        public ThingDef jacket;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors())
            {
                yield return e;
            }
            if (salvageHediff != null && salvageHediffSeverity <= 0f)
            {
                yield return "salvageHediff " + salvageHediff.defName + " with salvageHediffSeverity <= 0";
            }
            if (jacket != null && (jacket.category != ThingCategory.Building || !jacket.mineable))
            {
                yield return "jacket " + jacket.defName + " is not a mineable building";
            }
            if (yieldFactor <= 0f || yieldFactor > 1.5f)
            {
                yield return "yieldFactor " + yieldFactor + " outside (0, 1.5]";
            }
            if (lootTierShift < -2 || lootTierShift > 2)
            {
                yield return "lootTierShift " + lootTierShift + " outside [-2, 2]";
            }
        }
    }

    // On a concrete wreck child: <li Class="RimMandrake.Wreckage.RM_WreckWeathering">.
    // Def.ResolveReferences calls every extension's ResolveReferences(this) (RimSage,
    // Verse/Def.cs:93-103), which is where the weathering is folded into the def, so
    // a biome child never restates a cost, a fraction or a tier.
    public class RM_WreckWeathering : DefModExtension
    {
        public RM_WreckWeatheringDef weathering;

        // Per-child shift on top of the weathering's, for the one wreck in a biome that kept
        // more than its neighbours (design §4: the Wasteland's warcasket sarcophagus is
        // "Carapace +1" under the shared Irradiated row).
        public int extraTierShift;

        [Unsaved(false)]
        private bool applied;

        public static readonly string[] MidTiers = RM_WreckageKernel.MidTiers;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors())
            {
                yield return e;
            }
            if (weathering == null)
            {
                yield return "RM_WreckWeathering with no weathering (an unresolved RM_WreckWeatheringDef?)";
            }
        }

        public override void ResolveReferences(Def parentDef)
        {
            base.ResolveReferences(parentDef);
            if (applied || weathering == null || !(parentDef is ThingDef td))
            {
                return;
            }
            applied = true;
            td.resourcesFractionWhenDeconstructed = RM_WreckageKernel.YieldFraction(td.resourcesFractionWhenDeconstructed, weathering.yieldFactor);
            if (td.label.NullOrEmpty() && !weathering.labelPrefix.NullOrEmpty())
            {
                td.label = weathering.labelPrefix + " wreck";
            }
            if (weathering.extraLeavings != null && weathering.extraLeavings.Count > 0)
            {
                if (td.killedLeavings == null)
                {
                    td.killedLeavings = new List<ThingDefCountClass>();
                }
                td.killedLeavings.AddRange(weathering.extraLeavings);
            }
            if (td.comps != null)
            {
                int shift = weathering.lootTierShift + extraTierShift;
                foreach (CompProperties cp in td.comps)
                {
                    if (cp is RM_CompProperties_SalvageLoot loot)
                    {
                        // "nothing inside" first, then the tier shift (landing on Scrap removes the rare roll: Scrap has no rare table, design 3c)
                        LootFold folded = RM_WreckageKernel.Fold(loot.lootTier, loot.rareChance, loot.noLoot, weathering.noLoot, shift);
                        loot.lootTier = folded.tier;
                        loot.rareChance = folded.rareChance;
                        loot.noLoot = folded.noLoot;
                        if (weathering.extraLoot != null && loot.extraLoot == null)
                        {
                            loot.extraLoot = weathering.extraLoot;
                        }
                        if (weathering.salvageHediff != null && loot.salvageHediff == null)
                        {
                            loot.salvageHediff = weathering.salvageHediff;
                            loot.salvageHediffSeverity = weathering.salvageHediffSeverity;
                        }
                    }
                }
            }
        }

        // PROVISIONAL ladder: Scrap(0) < Hull/Tank/Carapace(1) < Sealed(2). A mid tier
        // shifted up becomes Sealed, down becomes Scrap; Scrap shifted up becomes Hull.
        public static string ShiftTier(string tier, int shift)
        {
            return RM_WreckageKernel.ShiftTier(tier, shift);
        }
    }
}
