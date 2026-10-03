using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Stillsand
{
    // ════════════════════════════════════════════════════════════════════
    // STILLSAND_SOLAR_STILL_1 — the solar still and the wringing still.
    //
    // A storage building (hauled feedstock sits on its cells) that carries two comps:
    //   RM_CompSunPowered  (kind=still) is the sun gate. REUSED, not reinvented: roof, shade grid,
    //                      pinned-sun elevation and the gale by name all come from RM_SunPower.
    //   RM_CompSolarStill  turns the sun factor into progress, and a full cycle consumes one
    //                      batch of feedstock and makes water.
    // A pearl lens (RM_PearlLens) lying in the still doubles the rate. It is not consumed.
    //
    // Feedstock (see RM_CompProperties_SolarStill.feeds): brine, eggs, raw meat. A wringing
    // still (allowCorpses) also takes corpses: water by body size, a witness thought for
    // colonists (RM_Thought_DeadDistilled; the Utinni layer patches in the Sun-Debt believers'
    // "drawing" stage on the same def). Every litre is booked on the water ledger
    // (RM_WaterLedger.Notify_Drawn). Output: Dubs Bad Hygiene's water bottle when that def is
    // live, otherwise the mod's own RM_StilledWater item.
    // ════════════════════════════════════════════════════════════════════
    public class RM_StillFeed
    {
        public string defName;        // a ThingDef name, or a ThingCategoryDef name
        public int perCycle = 1;      // units consumed per cycle
        public int litres = 2;        // water produced per cycle
    }

    public class RM_CompProperties_SolarStill : CompProperties
    {
        public int ticksPerCycle = 6000;     // at full sun, no pearl lens, rate slider 1
        public bool allowCorpses = false;    // the wringing still
        public float litresPerBodySize = 4f; // corpse water = bodySize x this
        public string pearlLensDef = "RM_PearlLens";
        public float pearlFactor = 2f;
        public string thoughtDef = "RM_Thought_DeadDistilled";
        public List<RM_StillFeed> feeds = new List<RM_StillFeed>();

        public RM_CompProperties_SolarStill()
        {
            compClass = typeof(RM_CompSolarStill);
        }
    }

    public class RM_CompSolarStill : ThingComp
    {
        private const int StepTicks = 250;   // CompTickRare
        private float progress;              // 0..1
        public RM_CompProperties_SolarStill Props => (RM_CompProperties_SolarStill)props;

        public override void PostExposeData()
        {
            Scribe_Values.Look(ref progress, "stillProgress", 0f);
        }

        public bool EnabledInSettings
        {
            get { return RM_GlassChainSettings.solarStillEnabled && (!Props.allowCorpses || RM_GlassChainSettings.wringingStillEnabled); }
        }

        private IEnumerable<Thing> Contents()
        {
            Map map = parent.Map;
            foreach (IntVec3 c in parent.OccupiedRect())
                foreach (Thing t in c.GetThingList(map))
                    if (t != parent && t.def.category != ThingCategory.Building) yield return t;
        }

        public bool HasPearlLens()
        {
            ThingDef d = DefDatabase<ThingDef>.GetNamedSilentFail(Props.pearlLensDef);
            if (d == null) return false;
            foreach (Thing t in Contents()) if (t.def == d) return true;
            return false;
        }

        public float RateFactor()
        {
            RM_CompSunPowered sun = parent.TryGetComp<RM_CompSunPowered>();
            if (sun == null || !sun.CanWork) return 0f;
            float f = sun.SunFactor * RM_GlassChainSettings.stillRateMultiplier;
            if (HasPearlLens()) f *= Props.pearlFactor;
            return f;
        }

        public override void CompTickRare()
        {
            base.CompTickRare();
            if (!parent.Spawned || !EnabledInSettings) return;
            if (!FindFeed(out Thing stock, out int units, out int litres)) { progress = 0f; return; }
            float rate = RateFactor();
            if (rate <= 0f) return;
            progress += StepTicks * rate / Mathf.Max(1, Props.ticksPerCycle);
            if (progress < 1f) return;
            progress = 0f;
            Consume(stock, units, litres);
        }

        /// <summary>Public so a test can run one cycle outright.</summary>
        public bool FindFeed(out Thing stock, out int units, out int litres)
        {
            stock = null; units = 0; litres = 0;
            foreach (Thing t in Contents())
            {
                Corpse corpse = t as Corpse;
                if (corpse != null)
                {
                    if (!Props.allowCorpses || corpse.InnerPawn == null) continue;
                    stock = t; units = 1;
                    litres = Mathf.Max(1, Mathf.RoundToInt(corpse.InnerPawn.BodySize * Props.litresPerBodySize));
                    return true;
                }
                foreach (RM_StillFeed f in Props.feeds)
                {
                    if (!Matches(t, f.defName) || t.stackCount < f.perCycle) continue;
                    stock = t; units = f.perCycle; litres = f.litres;
                    return true;
                }
            }
            return false;
        }

        private static bool Matches(Thing t, string name)
        {
            if (t.def.defName == name) return true;
            if (t.def.thingCategories == null) return false;
            foreach (ThingCategoryDef c in t.def.thingCategories)
                for (ThingCategoryDef p = c; p != null; p = p.parent)
                    if (p.defName == name) return true;
            return false;
        }

        public void Consume(Thing stock, int units, int litres)
        {
            Map map = parent.Map;
            IntVec3 at = parent.Position;
            bool dead = stock is Corpse;
            if (dead)
            {
                stock.Destroy();
                WitnessDeadDistilled(map);
            }
            else
            {
                stock.SplitOff(units).Destroy();
            }
            ThingDef water = WaterDef();
            if (water != null)
            {
                Thing w = ThingMaker.MakeThing(water);
                w.stackCount = litres;
                GenPlace.TryPlaceThing(w, parent.InteractionCell.IsValid ? parent.InteractionCell : at, map, ThingPlaceMode.Near);
            }
            RM_WaterLedger.Notify_Drawn(map, litres, dead ? "wrung from the dead" : "still");
        }

        /// <summary>Dubs Bad Hygiene's bottle when live, else the mod's own water item.</summary>
        public static ThingDef WaterDef()
        {
            return DefDatabase<ThingDef>.GetNamedSilentFail("DBH_WaterBottle")
                ?? DefDatabase<ThingDef>.GetNamedSilentFail("RM_StilledWater");
        }

        private void WitnessDeadDistilled(Map map)
        {
            ThoughtDef td = DefDatabase<ThoughtDef>.GetNamedSilentFail(Props.thoughtDef);
            if (td == null) return;
            foreach (Pawn p in map.mapPawns.FreeColonistsSpawned)
                p.needs?.mood?.thoughts?.memories?.TryGainMemory(td);
        }

        public override string CompInspectStringExtra()
        {
            if (!parent.Spawned) return null;
            if (!EnabledInSettings) return "Disabled in Mod Settings (Stillsand: glass and lenses).";
            if (!FindFeed(out Thing s, out int u, out int l))
                return "Nothing to distil. Put " + (Props.allowCorpses ? "brine, eggs, raw meat or a corpse" : "brine, eggs or raw meat") + " in it.";
            float r = RateFactor();
            return "Distilling " + s.LabelNoCount + ": " + progress.ToStringPercent()
                   + (r > 0f ? " (rate x" + r.ToString("0.00") + (HasPearlLens() ? ", pearl lens" : "") + ")" : " (no sun)");
        }
    }
}
