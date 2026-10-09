using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.TerminalBiomes
{
    // ════════════════════════════════════════════════════════════════════
    // TWILIGHTSEA_FLORA_PASS_1 — Route B placement and the two Route C comps of
    // design/Jawa/worldbuilding/biomes/the_twilight_deep_flora_pass_2026-09-27.md
    // (defs: Defs/ThingDefs_Plants/RM_TwilightUnderstorey.xml).
    //
    // ROUTE B, in two halves, because the Twilight's skylights are not placed at
    // map gen — RM_MapComponent_WellLedger opens and closes them at runtime:
    //   - RM_GenStep_TwilightFloraDressing (after the vanilla Plants step):
    //     tithemoss on cells beside wild hoolimbre/noothelm hosts. Never on a
    //     vaulisk lure (a different def — the lure is not a host).
    //   - RM_TwilightWellFlora, called from the ledger's Opened/Closed:
    //     gleamfloss on shaft cells (killed when the well closes), one farwick
    //     bud at the end of a 4-8 cell straight run outward from the shaft rim
    //     (dies when its home well closes), and tollhorn seeded under the well
    //     on each opening. JUDGEMENT CALL: the design's "well-recurrence ground
    //     (the skylight-site clusters the generator already knows)" names
    //     clusters the ledger does not have — sites are random. Seeding on every
    //     opening makes tollhorn (growDays 20) accumulate where wells HAVE
    //     opened, which is the readable recurrence record the design asks for.
    //
    // ROUTE C: RM_CompGloamurnBank (charge under an open well, lit only while
    // discharging) and RM_CompWiltAboveGlow (murkspindle dies in strong light).
    // Both glow-grid only (spec §1.4 trap), never the sky. Plant comps tick in
    // CompTickLong — Plant never runs the Normal ticker.
    //
    // Mod Settings: twilightFloraDressingEnabled, twilightFloraLightCompsEnabled.
    // ════════════════════════════════════════════════════════════════════
    public static class RM_TwilightWellFlora
    {
        private const float ShaftRadius = 3f;
        private const int GleamflossMin = 6;
        private const int GleamflossMax = 10;
        private const int FarwickRunMin = 4;
        private const int FarwickRunMax = 8;
        private const float TollhornChance = 0.6f;
        private const int TollhornMax = 3;

        private static float RimRadius => RM_WellKernel.BaseRadius;
        private static float FarwickReach => RM_WellKernel.BaseRadius + FarwickRunMax + 1;

        public static bool IsTwilightFloor(Map map)
        {
            string b = map?.Biome?.defName;
            return b == "RM_TwilightSea" || b == "RM_SeabedFloor_TwilightSea";
        }

        public static void OnWellOpened(Map map, IntVec3 pos)
        {
            if (map == null || !pos.IsValid || !RM_TerminalBiomesSettings.TwilightFloraDressingActive)
            {
                return;
            }

            ThingDef gleamfloss = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Gleamfloss");
            if (gleamfloss != null)
            {
                int target = Rand.RangeInclusive(GleamflossMin, GleamflossMax);
                List<IntVec3> cells = new List<IntVec3>(GenRadial.RadialCellsAround(pos, ShaftRadius, useCenter: false));
                cells.Shuffle();
                int placed = 0;
                foreach (IntVec3 c in cells)
                {
                    if (placed >= target) break;
                    if (TrySpawnPlant(map, gleamfloss, c, 0.15f, 0.5f) != null) placed++;
                }
            }

            ThingDef farwick = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Farwick");
            if (farwick != null)
            {
                int runners = Rand.RangeInclusive(1, 2);
                for (int i = 0; i < runners; i++)
                {
                    for (int attempt = 0; attempt < 4; attempt++)
                    {
                        float angle = Rand.Range(0f, 360f);
                        Vector3 dir = Quaternion.AngleAxis(angle, Vector3.up) * Vector3.forward;
                        float dist = RimRadius + Rand.RangeInclusive(FarwickRunMin, FarwickRunMax);
                        IntVec3 bud = (pos.ToVector3Shifted() + dir * dist).ToIntVec3();
                        if (TrySpawnPlant(map, farwick, bud, 0.5f, 1f) != null) break;
                    }
                }
            }

            ThingDef tollhorn = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Tollhorn");
            if (tollhorn != null && Rand.Chance(TollhornChance))
            {
                int target = Rand.RangeInclusive(1, TollhornMax);
                List<IntVec3> cells = new List<IntVec3>(GenRadial.RadialCellsAround(pos, RimRadius, useCenter: false));
                cells.Shuffle();
                int placed = 0;
                foreach (IntVec3 c in cells)
                {
                    if (placed >= target) break;
                    if (c.DistanceTo(pos) < 2f) continue;
                    if (TrySpawnPlant(map, tollhorn, c, 0.1f, 0.9f) != null) placed++;
                }
            }
        }

        // Called while the closing well is still in the ledger with stage Closed; every OTHER
        // non-closed well keeps the buds and floss inside its own reach.
        public static void OnWellClosed(Map map, IntVec3 pos, IEnumerable<IntVec3> otherOpenWells)
        {
            if (map == null || !pos.IsValid || !RM_TerminalBiomesSettings.TwilightFloraDressingActive)
            {
                return;
            }
            List<IntVec3> others = new List<IntVec3>(otherOpenWells);
            KillNear(map, "RM_Gleamfloss", pos, RimRadius, others, RimRadius);
            KillNear(map, "RM_Farwick", pos, FarwickReach, others, FarwickReach);
        }

        private static void KillNear(Map map, string defName, IntVec3 pos, float radius, List<IntVec3> others, float otherRadius)
        {
            ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(defName);
            if (def == null) return;
            foreach (Thing t in new List<Thing>(map.listerThings.ThingsOfDef(def)))
            {
                if (!t.Spawned || t.Position.DistanceTo(pos) > radius) continue;
                bool kept = false;
                foreach (IntVec3 o in others)
                {
                    if (t.Position.DistanceTo(o) <= otherRadius) { kept = true; break; }
                }
                if (!kept) t.Destroy(DestroyMode.Vanish);
            }
        }

        /// <summary>A plant on a free, standable, non-water cell off the channel bed; null when refused.</summary>
        public static Plant TrySpawnPlant(Map map, ThingDef def, IntVec3 c, float growthMin, float growthMax)
        {
            if (!c.InBounds(map) || !c.Standable(map) || c.GetEdifice(map) != null || c.GetPlant(map) != null)
            {
                return null;
            }
            TerrainDef terrain = c.GetTerrain(map);
            if (terrain == null || terrain.IsWater || (terrain.tags != null && terrain.tags.Contains("RM_ChannelBed")))
            {
                return null;
            }
            if (map.GetComponent<RM_MapComponent_ChannelCurrent>()?.HasCurrent(c) == true)
            {
                return null;
            }
            if (!GenSpawn.CanSpawnAt(def, c, map))
            {
                return null;
            }
            Plant p = ThingMaker.MakeThing(def) as Plant;
            if (p == null) return null;
            p.Growth = Rand.Range(growthMin, growthMax);
            GenSpawn.Spawn(p, c, map);
            return p;
        }
    }

    /// <summary>Route B at map gen: tithemoss on cells beside wild living-lamp hosts.</summary>
    public class RM_GenStep_TwilightFloraDressing : GenStep
    {
        private const float HostChance = 0.5f;
        private const int MaxPerHost = 2;

        public override int SeedPart => 5140939;

        public override void Generate(Map map, GenStepParams parms)
        {
            if (!RM_TwilightWellFlora.IsTwilightFloor(map) || !RM_TerminalBiomesSettings.TwilightFloraDressingActive)
            {
                return;
            }
            ThingDef tithemoss = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Tithemoss");
            if (tithemoss == null)
            {
                return;
            }

            List<Thing> hosts = new List<Thing>();
            foreach (string host in new[] { "RM_HoolimbrePlant", "RM_NoothelmPlant" })
            {
                ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(host);
                if (def != null) hosts.AddRange(map.listerThings.ThingsOfDef(def));
            }

            foreach (Thing host in hosts)
            {
                // Wild and Compact hosts only (ruled): at map gen nothing is the player's, but a
                // faction-owned host is skipped all the same.
                if (host.Faction == Faction.OfPlayer || !Rand.Chance(HostChance))
                {
                    continue;
                }
                int target = Rand.RangeInclusive(1, MaxPerHost);
                int placed = 0;
                foreach (IntVec3 c in GenAdj.CellsAdjacent8Way(host).InRandomOrder())
                {
                    if (placed >= target) break;
                    if (RM_TwilightWellFlora.TrySpawnPlant(map, tithemoss, c, 0.4f, 1f) != null) placed++;
                }
            }
        }
    }

    public class RM_CompProperties_GloamurnBank : CompProperties
    {
        public float chargeDays = 3f;   // under a standing well, empty to full
        public float spendDays = 5f;    // "spending the hoard down over most of a week"
        public float minChargeToGlow = 0.05f;

        public RM_CompProperties_GloamurnBank()
        {
            compClass = typeof(RM_CompGloamurnBank);
        }
    }

    /// <summary>Gloamurn: banks a well's light while one stands over it, glows only while spending it.</summary>
    public class RM_CompGloamurnBank : ThingComp, IThingGlower
    {
        private const float DaysPerLongTick = 2000f / 60000f;
        private float charge;
        private bool discharging;
        private bool charging;

        public RM_CompProperties_GloamurnBank Props => (RM_CompProperties_GloamurnBank)props;

        public bool ShouldBeLitNow()
        {
            return discharging && RM_TerminalBiomesSettings.TwilightFloraLightCompsActive;
        }

        public override void CompTickLong()
        {
            base.CompTickLong();
            if (!parent.Spawned)
            {
                return;
            }
            Map map = parent.Map;
            if (RM_TerminalBiomesSettings.TwilightFloraLightCompsActive)
            {
                RM_MapComponent_WellLedger ledger = RM_MapComponent_WellLedger.GetFor(map);
                // Lid-dark counts as the sky going out: the urns spend (design: brighter when the sky goes out).
                charging = ledger != null && !ledger.LidDark && ledger.IsUnderOpenWell(parent.Position);
                if (charging)
                {
                    charge = Mathf.Min(1f, charge + DaysPerLongTick / Props.chargeDays);
                    discharging = false;
                }
                else if (charge > Props.minChargeToGlow)
                {
                    discharging = true;
                    charge = Mathf.Max(0f, charge - DaysPerLongTick / Props.spendDays);
                }
                else
                {
                    discharging = false;
                }
            }
            parent.GetComp<CompGlower>()?.UpdateLit(map);
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref charge, "rmGloamCharge");
            Scribe_Values.Look(ref discharging, "rmGloamDischarging");
        }

        public override string CompInspectStringExtra()
        {
            string state = discharging ? "spending" : charging ? "charging" : "dark";
            return "Banked light: " + charge.ToStringPercent() + " (" + state + ")";
        }
    }

    public class RM_CompProperties_WiltAboveGlow : CompProperties
    {
        public float glowThreshold = 0.35f; // artificial glow caps at 0.5 (GlowGrid.GroundGlowAt)
        public float daysToDie = 2.5f;      // "a well opening overhead kills a stand in days"

        public RM_CompProperties_WiltAboveGlow()
        {
            compClass = typeof(RM_CompWiltAboveGlow);
        }
    }

    /// <summary>Murkspindle: photophobic — rots while the glow grid on its cell is above a threshold. Sky ignored.</summary>
    public class RM_CompWiltAboveGlow : ThingComp
    {
        private bool wilting;

        public RM_CompProperties_WiltAboveGlow Props => (RM_CompProperties_WiltAboveGlow)props;

        public override void CompTickLong()
        {
            base.CompTickLong();
            if (!parent.Spawned || !RM_TerminalBiomesSettings.TwilightFloraLightCompsActive)
            {
                wilting = false;
                return;
            }
            float glow = parent.Map.glowGrid.GroundGlowAt(parent.Position, false, true);
            wilting = glow > Props.glowThreshold;
            if (wilting)
            {
                float amount = Mathf.Max(1f, parent.MaxHitPoints * (2000f / 60000f) / Props.daysToDie);
                parent.TakeDamage(new DamageInfo(DamageDefOf.Rotting, amount));
            }
        }

        public override string CompInspectStringExtra()
        {
            return wilting ? "Wilting in the light." : null;
        }
    }
}
