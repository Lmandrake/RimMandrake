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

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors())
            {
                yield return e;
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

        [Unsaved(false)]
        private bool applied;

        public static readonly string[] MidTiers = { "Hull", "Tank", "Carapace" };

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
            td.resourcesFractionWhenDeconstructed = Mathf.Clamp01(td.resourcesFractionWhenDeconstructed * weathering.yieldFactor);
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
            if (weathering.lootTierShift != 0 && td.comps != null)
            {
                foreach (CompProperties cp in td.comps)
                {
                    if (cp is RM_CompProperties_SalvageLoot loot)
                    {
                        loot.lootTier = ShiftTier(loot.lootTier, weathering.lootTierShift);
                        if (loot.lootTier == "Scrap")
                        {
                            loot.rareChance = 0f; // Scrap has no rare table (design §3c)
                        }
                    }
                }
            }
        }

        // PROVISIONAL ladder: Scrap(0) < Hull/Tank/Carapace(1) < Sealed(2). A mid tier
        // shifted up becomes Sealed, down becomes Scrap; Scrap shifted up becomes Hull.
        public static string ShiftTier(string tier, int shift)
        {
            int rank = tier == "Scrap" ? 0 : tier == "Sealed" ? 2 : 1;
            int to = Mathf.Clamp(rank + shift, 0, 2);
            if (to == rank)
            {
                return tier;
            }
            if (to == 0)
            {
                return "Scrap";
            }
            if (to == 2)
            {
                return "Sealed";
            }
            return rank == 0 ? "Hull" : tier;
        }
    }
}
