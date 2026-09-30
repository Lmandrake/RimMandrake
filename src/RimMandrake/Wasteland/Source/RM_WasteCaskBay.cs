using System.Collections.Generic;
using System.Linq;
using System.Text;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.Wasteland
{
    // ════════════════════════════════════════════════════════════════════
    // WASTELAND_GPT_ENRICHMENT_1 §3 — the SEALED CASK BAY (RM_WasteCaskBay) and
    // the waste cask it holds (RM_WasteCask). ⚠️ Not the warcasket suit bay:
    // that is Warcasket's RM_CaskBay (WARCASKET_CASK_BAY_AND_SARCOPHAGI_1).
    //
    //   Cask (RM_CompWasteCask): a physical waste object with a stored dose. Below
    //     its leak threshold of hit points it LEAKS — pollution, tox gas, a fleck,
    //     a message and the Alert below every pulse: a leak is never silent. It can
    //     be marked for illegal reburial (WorkGiver/JobDriver below; §4 hooks it).
    //   Bay (RM_CompWasteContainment on a Building_Storage): shows seal integrity,
    //     internal heat, stored dose and launch safety. Powered seals contain;
    //     unpowered, the seal charge drains, and below the leak threshold (or with
    //     the bay's hit points shot away) the bay leaks, visibly. A tamed processor
    //     animal (RM_CompProcessorGatherable: sloghog, sootgrazer) standing by the
    //     bay converts casks into its own product when processing is switched on.
    //   Launch: Building_GravEngine.CanLaunch has NO extension point (RimSage,
    //     decompiled 1.6), so a Harmony postfix refuses a launch while a bay on the
    //     ship's substructure is unsafe or a cask sits aboard outside a bay.
    // ════════════════════════════════════════════════════════════════════

    public class RM_CompProperties_WasteCask : CompProperties
    {
        public FloatRange doseRange = new FloatRange(0.6f, 1f);
        /// <summary>Leaks once hit points fall below this fraction of max.</summary>
        public float leakHpFraction = 0.5f;
        public int leakIntervalTicks = 2500;
        /// <summary>Cells polluted per leak pulse (x the leak-severity setting).</summary>
        public int leakPollutionCells = 3;
        /// <summary>Tox gas released per leak pulse (x the leak-severity setting).</summary>
        public int leakGasAmount = 80;
        /// <summary>Stored dose lost per leak pulse.</summary>
        public float dosePerLeak = 0.05f;
        /// <summary>Internal heat (°C over ambient) per unit of stored dose, read by the bay.</summary>
        public float heatPerDose = 18f;
        /// <summary>Ticks of work to rebury one cask.</summary>
        public int reburyTicks = 900;

        public RM_CompProperties_WasteCask()
        {
            compClass = typeof(RM_CompWasteCask);
        }
    }

    public class RM_CompWasteCask : ThingComp
    {
        private float storedDose = -1f;
        private int nextLeakTick = -1;
        private bool everLeaked;
        public bool reburyMarked;

        public RM_CompProperties_WasteCask Props => (RM_CompProperties_WasteCask)props;
        public float StoredDose => Mathf.Max(0f, storedDose);

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            if (storedDose < 0f)
            {
                storedDose = Props.doseRange.RandomInRange;
            }
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref storedDose, "storedDose", -1f);
            Scribe_Values.Look(ref nextLeakTick, "nextLeakTick", -1);
            Scribe_Values.Look(ref everLeaked, "everLeaked", false);
            Scribe_Values.Look(ref reburyMarked, "reburyMarked", false);
        }

        /// <summary>The bay this cask sits in, if any.</summary>
        public RM_CompWasteContainment Bay
        {
            get
            {
                if (!parent.Spawned)
                {
                    return null;
                }
                Building edifice = parent.Position.GetEdifice(parent.Map);
                return edifice?.GetComp<RM_CompWasteContainment>();
            }
        }

        /// <summary>A breached cask: hit points below the leak threshold and not inside a sealed bay.</summary>
        public bool Breached =>
            parent.def.useHitPoints && parent.HitPoints < parent.MaxHitPoints * Props.leakHpFraction && StoredDose > 0f;

        public bool Leaking
        {
            get
            {
                if (!parent.Spawned || !Breached || !RM_WastelandSettings.wastelandEnabled || !RM_WastelandSettings.caskLeaksEnabled)
                {
                    return false;
                }
                RM_CompWasteContainment bay = Bay;
                return bay == null || !bay.Contained;
            }
        }

        public override void CompTickRare()
        {
            base.CompTickRare();
            bool leaking = Leaking;
            RM_WasteLeakRegistry.Set(parent, leaking);
            if (!leaking)
            {
                return;
            }
            int now = Find.TickManager.TicksGame;
            if (nextLeakTick < 0 || now >= nextLeakTick)
            {
                LeakPulse();
                nextLeakTick = now + Props.leakIntervalTicks;
            }
        }

        /// <summary>One visible leak pulse. Public so a debug action / state read can drive it.</summary>
        public int LeakPulse()
        {
            Map map = parent.Map;
            if (map == null)
            {
                return 0;
            }
            float sev = RM_WastelandSettings.caskLeakSeverity;
            int polluted = RM_WasteLeakRegistry.PolluteAround(parent.Position, map, Mathf.Max(1, Mathf.RoundToInt(Props.leakPollutionCells * sev)));
            RM_WasteLeakRegistry.GasAndFleck(parent.Position, map, Mathf.RoundToInt(Props.leakGasAmount * sev));
            storedDose = Mathf.Max(0f, StoredDose - Props.dosePerLeak);
            RM_WasteLeakRegistry.Announce(map, parent,
                (everLeaked ? "A breached waste cask is still leaking" : "A waste cask has been breached and is leaking")
              + ": tox gas and pollution around " + parent.LabelShort + ". Repair nothing — move it into a powered sealed cask bay, or get it off the map.",
                !everLeaked);
            everLeaked = true;
            return polluted;
        }

        public override void PostDestroy(DestroyMode mode, Map previousMap)
        {
            base.PostDestroy(mode, previousMap);
            RM_WasteLeakRegistry.Set(parent, false);
            if (mode == DestroyMode.KillFinalize && previousMap != null && StoredDose > 0f
                && RM_WastelandSettings.wastelandEnabled && RM_WastelandSettings.caskLeaksEnabled)
            {
                // A destroyed cask dumps everything left in it, loudly.
                IntVec3 c = parent.PositionHeld;
                int cells = Mathf.RoundToInt(Props.leakPollutionCells * 4 * RM_WastelandSettings.caskLeakSeverity);
                RM_WasteLeakRegistry.PolluteAround(c, previousMap, Mathf.Max(4, cells));
                RM_WasteLeakRegistry.GasAndFleck(c, previousMap, Mathf.RoundToInt(Props.leakGasAmount * 3 * RM_WastelandSettings.caskLeakSeverity));
                Messages.Message("A waste cask has burst open, spilling its whole load.",
                    new LookTargets(new TargetInfo(c, previousMap)), MessageTypeDefOf.NegativeEvent);
            }
        }

        public override string CompInspectStringExtra()
        {
            StringBuilder sb = new StringBuilder();
            sb.Append("Stored dose: " + StoredDose.ToString("0.00"));
            if (Leaking)
            {
                sb.AppendInNewLine("LEAKING: breached below " + Props.leakHpFraction.ToStringPercent() + " hit points.");
            }
            else if (Breached)
            {
                sb.AppendInNewLine("Breached, but held by a sealed cask bay.");
            }
            if (reburyMarked)
            {
                sb.AppendInNewLine("Marked for illegal reburial.");
            }
            return sb.ToString();
        }

        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            foreach (Gizmo g in base.CompGetGizmosExtra())
            {
                yield return g;
            }
            if (!parent.Spawned || !RM_WastelandSettings.wastelandEnabled || !RM_WastelandSettings.caskReburialEnabled)
            {
                yield break;
            }
            Command_Toggle toggle = new Command_Toggle
            {
                defaultLabel = "Rebury illegally",
                defaultDesc = "Have a colonist dig this cask back into the ground where it lies. It disappears from the "
                            + "map, but the ground around it is fouled with pollution, and anyone who licensed or "
                            + "financed your waste handling may find out. Needs diggable ground.",
                icon = TexCommand.ForbidOff,
                isActive = () => reburyMarked,
                toggleAction = () => reburyMarked = !reburyMarked
            };
            if (!RM_CompWasteCask.CanReburyAt(parent.Position, parent.Map))
            {
                toggle.Disable("The ground here cannot be dug.");
            }
            yield return toggle;
        }

        public static bool CanReburyAt(IntVec3 c, Map map)
        {
            TerrainDef t = c.GetTerrain(map);
            if (diggable == null)
            {
                diggable = DefDatabase<TerrainAffordanceDef>.GetNamedSilentFail("Diggable");
            }
            return t != null && t.affordances != null && diggable != null && t.affordances.Contains(diggable)
                && c.GetEdifice(map) == null;
        }

        private static TerrainAffordanceDef diggable;

        /// <summary>The reburial completes: the cask goes into the ground and fouls it.</summary>
        public void Rebury(Pawn by)
        {
            Map map = parent.Map;
            IntVec3 c = parent.Position;
            if (map == null)
            {
                return;
            }
            RM_WasteLeakRegistry.PolluteAround(c, map, 9);
            Messages.Message((by != null ? by.LabelShort + " has" : "A waste cask has been")
                           + " illegally reburied a waste cask. The ground around it is fouled, and the burial may yet be discovered.",
                new LookTargets(new TargetInfo(c, map)), MessageTypeDefOf.NegativeEvent);
            RM_TippingUtility.Notify_IllegalReburial(map, c);
            parent.Destroy(DestroyMode.Vanish);
        }

        private static List<ThingDef> caskDefs;
        public static List<ThingDef> CaskDefs =>
            caskDefs ?? (caskDefs = DefDatabase<ThingDef>.AllDefsListForReading
                .Where(d => d.comps != null && d.comps.Any(p => p is RM_CompProperties_WasteCask)).ToList());

        public static IEnumerable<Thing> AllCasks(Map map)
        {
            List<ThingDef> defs = CaskDefs;
            for (int i = 0; i < defs.Count; i++)
            {
                List<Thing> list = map.listerThings.ThingsOfDef(defs[i]);
                for (int j = 0; j < list.Count; j++)
                {
                    yield return list[j];
                }
            }
        }
    }

    /// <summary>Shared leak effects and the registry the leak Alert reads.</summary>
    public static class RM_WasteLeakRegistry
    {
        private static readonly HashSet<Thing> leaking = new HashSet<Thing>();
        private static readonly Dictionary<int, int> lastMessageTick = new Dictionary<int, int>();

        public static void Set(Thing t, bool isLeaking)
        {
            if (isLeaking)
            {
                leaking.Add(t);
            }
            else
            {
                leaking.Remove(t);
            }
        }

        public static List<Thing> LeakingOn(Map map)
        {
            leaking.RemoveWhere(t => t == null || t.Destroyed || !t.Spawned);
            return leaking.Where(t => t.Map == map).ToList();
        }

        public static List<Thing> AllLeaking()
        {
            leaking.RemoveWhere(t => t == null || t.Destroyed || !t.Spawned);
            return leaking.ToList();
        }

        public static int PolluteAround(IntVec3 center, Map map, int cells)
        {
            if (!ModsConfig.BiotechActive || cells <= 0)
            {
                return 0;
            }
            int done = 0;
            int num = GenRadial.NumCellsInRadius(6f);
            for (int i = 0; i < num && done < cells; i++)
            {
                IntVec3 c = center + GenRadial.RadialPattern[i];
                if (!c.InBounds(map) || !map.pollutionGrid.CanPollute(c))
                {
                    continue;
                }
                map.pollutionGrid.SetPolluted(c, true, silent: false);
                done++;
            }
            return done;
        }

        public static void GasAndFleck(IntVec3 c, Map map, int gas)
        {
            if (gas > 0)
            {
                GasUtility.AddGas(c, map, GasType.ToxGas, gas);
            }
            if (map == Find.CurrentMap)
            {
                FleckMaker.ThrowDustPuffThick(c.ToVector3Shifted(), map, 1.6f, new Color(0.55f, 0.75f, 0.3f));
            }
        }

        /// <summary>A leak message. <paramref name="force"/> = always (first leak); otherwise at most one per map per 600 ticks.</summary>
        public static void Announce(Map map, Thing culprit, string text, bool force)
        {
            int now = Find.TickManager.TicksGame;
            if (!force && lastMessageTick.TryGetValue(map.uniqueID, out int last) && now - last < 600)
            {
                return;
            }
            lastMessageTick[map.uniqueID] = now;
            Messages.Message(text, new LookTargets(culprit), MessageTypeDefOf.NegativeEvent);
        }
    }

    /// <summary>Persistent alert for every leaking cask or bay: a leak is never silent.</summary>
    public class Alert_RM_WasteLeaking : Alert_Critical
    {
        public Alert_RM_WasteLeaking()
        {
            defaultLabel = "Waste leaking";
        }

        public override string GetLabel()
        {
            int n = RM_WasteLeakRegistry.AllLeaking().Count;
            return n == 1 ? "Waste leaking" : "Waste leaking (" + n + ")";
        }

        public override TaggedString GetExplanation()
        {
            return "Breached waste is leaking tox gas and pollution. A breached cask stops leaking inside a "
                 + "powered, intact sealed cask bay; a leaking bay needs power and repair.\n\nClick to see the leak.";
        }

        public override AlertReport GetReport()
        {
            List<Thing> all = RM_WasteLeakRegistry.AllLeaking();
            return all.Count == 0 ? AlertReport.Inactive : AlertReport.CulpritsAre(all);
        }
    }

    // ────────────────────────────────────────────────────────────────────
    // The bay.
    // ────────────────────────────────────────────────────────────────────

    public class RM_CompProperties_WasteContainment : CompProperties
    {
        /// <summary>Seal integrity below which the bay stops containing and leaks.</summary>
        public float leakThreshold = 0.5f;
        /// <summary>Seal integrity required to launch.</summary>
        public float launchIntegrity = 0.75f;
        /// <summary>Internal heat (°C over ambient) above which launch is refused.</summary>
        public float launchHeatLimit = 40f;
        /// <summary>Seal charge lost per rare tick while unpowered (0.005 = ~20 h from full).</summary>
        public float chargeDrainPerRare = 0.005f;
        public float chargeRegenPerRare = 0.02f;
        /// <summary>Fraction of internal heat still built while powered (cooling).</summary>
        public float poweredHeatFactor = 0.25f;
        public int leakIntervalTicks = 2500;
        public int leakPollutionCells = 6;
        public int leakGasAmount = 150;
        /// <summary>Cells from the bay a processor animal must stand within.</summary>
        public float processorRadius = 4.9f;
        /// <summary>Output per processed cask, as a multiple of the animal's own gather amount.</summary>
        public float processedOutputFactor = 2f;

        public RM_CompProperties_WasteContainment()
        {
            compClass = typeof(RM_CompWasteContainment);
        }
    }

    public class RM_CompWasteContainment : ThingComp
    {
        private float sealCharge = 1f;
        private float internalHeat;
        private int nextLeakTick = -1;
        private bool everLeaked;
        public bool processingEnabled;
        private float processProgress;

        public RM_CompProperties_WasteContainment Props => (RM_CompProperties_WasteContainment)props;

        private CompPowerTrader power;
        private CompPowerTrader Power => power ?? (power = parent.GetComp<CompPowerTrader>());

        public bool Powered => Power == null || Power.PowerOn;
        public float HpFraction => parent.MaxHitPoints > 0 ? parent.HitPoints / (float)parent.MaxHitPoints : 1f;
        /// <summary>Seal integrity: the lower of the seal charge and the bay's structural state.</summary>
        public float SealIntegrity => Mathf.Min(sealCharge, HpFraction);
        public float InternalHeat => internalHeat;
        public bool Contained => SealIntegrity >= Props.leakThreshold;

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref sealCharge, "sealCharge", 1f);
            Scribe_Values.Look(ref internalHeat, "internalHeat", 0f);
            Scribe_Values.Look(ref nextLeakTick, "nextLeakTick", -1);
            Scribe_Values.Look(ref everLeaked, "everLeaked", false);
            Scribe_Values.Look(ref processingEnabled, "processingEnabled", false);
            Scribe_Values.Look(ref processProgress, "processProgress", 0f);
        }

        public List<Thing> Casks()
        {
            List<Thing> list = new List<Thing>();
            if (!parent.Spawned)
            {
                return list;
            }
            foreach (IntVec3 c in parent.OccupiedRect())
            {
                List<Thing> things = c.GetThingList(parent.Map);
                for (int i = 0; i < things.Count; i++)
                {
                    if (things[i].TryGetComp<RM_CompWasteCask>() != null)
                    {
                        list.Add(things[i]);
                    }
                }
            }
            return list;
        }

        public float StoredDose()
        {
            float d = 0f;
            foreach (Thing t in Casks())
            {
                d += t.TryGetComp<RM_CompWasteCask>().StoredDose;
            }
            return d;
        }

        public override void CompTickRare()
        {
            base.CompTickRare();
            if (!parent.Spawned)
            {
                return;
            }
            bool on = RM_WastelandSettings.wastelandEnabled;
            List<Thing> casks = Casks();
            float dose = 0f;
            float heatTarget = 0f;
            foreach (Thing t in casks)
            {
                RM_CompWasteCask c = t.TryGetComp<RM_CompWasteCask>();
                dose += c.StoredDose;
                heatTarget += c.StoredDose * c.Props.heatPerDose;
            }
            if (Powered)
            {
                sealCharge = Mathf.Min(1f, sealCharge + Props.chargeRegenPerRare);
                heatTarget *= Props.poweredHeatFactor;
            }
            else
            {
                sealCharge = Mathf.Max(0f, sealCharge - Props.chargeDrainPerRare);
            }
            internalHeat = Mathf.Lerp(internalHeat, heatTarget, 0.1f);
            if (internalHeat > 1f)
            {
                GenTemperature.PushHeat(parent.Position, parent.Map, internalHeat * 0.5f);
            }

            bool leaking = on && RM_WastelandSettings.caskLeaksEnabled && casks.Count > 0 && dose > 0f && !Contained;
            RM_WasteLeakRegistry.Set(parent, leaking);
            if (leaking)
            {
                int now = Find.TickManager.TicksGame;
                if (nextLeakTick < 0 || now >= nextLeakTick)
                {
                    LeakPulse(casks);
                    nextLeakTick = now + Props.leakIntervalTicks;
                }
            }

            if (on && processingEnabled && casks.Count > 0)
            {
                TickProcessing(casks);
            }
        }

        /// <summary>One visible bay leak pulse. Public so a debug action / state read can drive it.</summary>
        public int LeakPulse(List<Thing> casks)
        {
            Map map = parent.Map;
            float sev = RM_WastelandSettings.caskLeakSeverity;
            int polluted = RM_WasteLeakRegistry.PolluteAround(parent.Position, map, Mathf.Max(1, Mathf.RoundToInt(Props.leakPollutionCells * sev)));
            RM_WasteLeakRegistry.GasAndFleck(parent.OccupiedRect().RandomCell, map, Mathf.RoundToInt(Props.leakGasAmount * sev));
            RM_WasteLeakRegistry.Announce(map, parent,
                "The sealed cask bay's seals have failed (" + SealIntegrity.ToStringPercent() + " integrity"
              + (Powered ? "" : ", no power") + "): it is leaking tox gas and pollution.", !everLeaked);
            everLeaked = true;
            return polluted;
        }

        private void TickProcessing(List<Thing> casks)
        {
            Pawn animal = FindProcessor(out RM_CompProcessorGatherable proc);
            if (animal == null)
            {
                return;
            }
            processProgress += RM_WastelandSettings.caskProcessingPerDay * GenTicks.TickRareInterval / (float)GenDate.TicksPerDay;
            if (processProgress < 1f)
            {
                return;
            }
            processProgress = 0f;
            Thing cask = casks[0];
            CompProperties_Milkable mp = (CompProperties_Milkable)proc.props;
            int amount = Mathf.Max(1, Mathf.RoundToInt(mp.milkAmount * Props.processedOutputFactor));
            cask.Destroy(DestroyMode.Vanish);
            Thing product = ThingMaker.MakeThing(mp.milkDef);
            product.stackCount = Mathf.Min(amount, mp.milkDef.stackLimit);
            GenPlace.TryPlaceThing(product, parent.InteractionCell.IsValid ? parent.InteractionCell : parent.Position, parent.Map, ThingPlaceMode.Near);
            Messages.Message(animal.LabelShort + " has processed a waste cask into " + product.LabelCap + ".",
                new LookTargets(product), MessageTypeDefOf.PositiveEvent);
        }

        public Pawn FindProcessor(out RM_CompProcessorGatherable proc)
        {
            proc = null;
            IReadOnlyList<Pawn> pawns = parent.Map.mapPawns.SpawnedColonyAnimals;
            IntVec3 center = parent.OccupiedRect().CenterCell;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if (p.Dead || p.Downed || !p.Position.InHorDistOf(center, Props.processorRadius))
                {
                    continue;
                }
                RM_CompProcessorGatherable c = p.GetComp<RM_CompProcessorGatherable>();
                if (c != null)
                {
                    proc = c;
                    return p;
                }
            }
            return null;
        }

        // ── gravship membership + launch safety ─────────────────────────

        public Building_GravEngine AboardEngine()
        {
            if (!parent.Spawned)
            {
                return null;
            }
            List<Building> list = parent.Map.listerBuildings.allBuildingsColonist;
            for (int i = 0; i < list.Count; i++)
            {
                if (list[i] is Building_GravEngine e && e.ValidSubstructureAt(parent.Position))
                {
                    return e;
                }
            }
            return null;
        }

        public AcceptanceReport LaunchSafety()
        {
            if (Casks().Count == 0)
            {
                return AcceptanceReport.WasAccepted;
            }
            if (!Powered)
            {
                return "sealed cask bay has no power to its seals";
            }
            if (SealIntegrity < Props.launchIntegrity)
            {
                return "sealed cask bay seal integrity is " + SealIntegrity.ToStringPercent()
                     + " (needs " + Props.launchIntegrity.ToStringPercent() + ")";
            }
            if (internalHeat > Props.launchHeatLimit)
            {
                return "sealed cask bay is running hot (+" + internalHeat.ToString("0") + " °C, limit +"
                     + Props.launchHeatLimit.ToString("0") + " °C)";
            }
            return AcceptanceReport.WasAccepted;
        }

        public override string CompInspectStringExtra()
        {
            List<Thing> casks = Casks();
            StringBuilder sb = new StringBuilder();
            sb.Append("Casks: " + casks.Count + " / " + RM_WasteCaskBayUtility.Capacity(parent.def));
            sb.AppendInNewLine("Seal integrity: " + SealIntegrity.ToStringPercent()
                             + (Powered ? "" : " (NO POWER: seals draining)")
                             + (Contained ? "" : " — LEAKING"));
            sb.AppendInNewLine("Internal heat: +" + internalHeat.ToString("0.0") + " °C");
            sb.AppendInNewLine("Stored dose: " + StoredDose().ToString("0.00"));
            Building_GravEngine engine = AboardEngine();
            AcceptanceReport safe = LaunchSafety();
            sb.AppendInNewLine("Launch safety: " + (engine == null ? "not aboard a gravship" : (safe.Accepted ? "SAFE" : "UNSAFE — " + safe.Reason)));
            if (processingEnabled)
            {
                Pawn a = FindProcessor(out _);
                sb.AppendInNewLine("Processing: " + (a != null ? a.LabelShort + " working, " + processProgress.ToStringPercent() : "waiting for a tamed processor animal nearby"));
            }
            return sb.ToString();
        }

        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            foreach (Gizmo g in base.CompGetGizmosExtra())
            {
                yield return g;
            }
            if (!RM_WastelandSettings.caskProcessingEnabled)
            {
                yield break;
            }
            yield return new Command_Toggle
            {
                defaultLabel = "Feed casks to processors",
                defaultDesc = "A tamed sloghog or sootgrazer standing next to the bay converts stored casks, one at a "
                            + "time, into bezoars or soot bricks.",
                icon = TexCommand.ForbidOff,
                isActive = () => processingEnabled,
                toggleAction = () => processingEnabled = !processingEnabled
            };
            if (DebugSettings.ShowDevGizmos)
            {
                yield return new Command_Action
                {
                    defaultLabel = "DEV: drain seals",
                    action = () => sealCharge = 0f
                };
            }
        }

        public override void PostDeSpawn(Map map, DestroyMode mode = DestroyMode.Vanish)
        {
            base.PostDeSpawn(map, mode);
            RM_WasteLeakRegistry.Set(parent, false);
        }
    }

    /// <summary>The bay's storage body; capacity comes from Mod Settings via maxItemsInCell.</summary>
    public class Building_RM_WasteCaskBay : Building_Storage
    {
    }

    [StaticConstructorOnStartup]
    public static class RM_WasteCaskBayUtility
    {
        static RM_WasteCaskBayUtility()
        {
            ApplyCapacity();
            new Harmony("mandrake.rm.wasteland").Patch(
                AccessTools.Method(typeof(Building_GravEngine), nameof(Building_GravEngine.CanLaunch)),
                postfix: new HarmonyMethod(typeof(RM_WasteCaskBayUtility), nameof(CanLaunchPostfix)));
        }

        public static int Capacity(ThingDef bayDef)
        {
            return bayDef.size.x * bayDef.size.z * Mathf.Max(1, bayDef.building?.maxItemsInCell ?? 1);
        }

        /// <summary>Casks-per-cell from Mod Settings into every bay def (live: StoreUtility reads it per call).</summary>
        private static List<ThingDef> bayDefs;

        public static void ApplyCapacity()
        {
            if (bayDefs == null)
            {
                bayDefs = DefDatabase<ThingDef>.AllDefsListForReading
                    .Where(d => d.building != null && d.thingClass != null
                             && typeof(Building_RM_WasteCaskBay).IsAssignableFrom(d.thingClass))
                    .ToList();
            }
            int perCell = Mathf.Clamp(RM_WastelandSettings.caskBayPerCell, 1, 6);
            for (int i = 0; i < bayDefs.Count; i++)
            {
                bayDefs[i].building.maxItemsInCell = perCell;
            }
        }

        public static void CanLaunchPostfix(Building_GravEngine __instance, ref AcceptanceReport __result)
        {
            if (!__result.Accepted || !RM_WastelandSettings.wastelandEnabled || !RM_WastelandSettings.caskLaunchCheckEnabled)
            {
                return;
            }
            Map map = __instance.Map;
            if (map == null)
            {
                return;
            }
            AcceptanceReport r = CheckShip(__instance, map);
            if (!r.Accepted)
            {
                __result = r;
            }
        }

        public static AcceptanceReport CheckShip(Building_GravEngine engine, Map map)
        {
            List<Building> list = map.listerBuildings.allBuildingsColonist;
            for (int i = 0; i < list.Count; i++)
            {
                RM_CompWasteContainment bay = list[i].GetComp<RM_CompWasteContainment>();
                if (bay == null || !engine.ValidSubstructureAt(list[i].Position))
                {
                    continue;
                }
                AcceptanceReport r = bay.LaunchSafety();
                if (!r.Accepted)
                {
                    return new AcceptanceReport(("Unsafe waste aboard: " + r.Reason).CapitalizeFirst());
                }
            }
            foreach (Thing cask in RM_CompWasteCask.AllCasks(map))
            {
                if (!cask.Spawned || !engine.ValidSubstructureAt(cask.Position))
                {
                    continue;
                }
                if (cask.TryGetComp<RM_CompWasteCask>().Bay == null)
                {
                    return new AcceptanceReport("Unsafe waste aboard: a waste cask is loose on the deck. Store it in a sealed cask bay.");
                }
            }
            return AcceptanceReport.WasAccepted;
        }
    }

    // ────────────────────────────────────────────────────────────────────
    // Illegal reburial: WorkGiver + JobDriver.
    // ────────────────────────────────────────────────────────────────────

    public class WorkGiver_RM_ReburyWasteCask : WorkGiver_Scanner
    {
        public override PathEndMode PathEndMode => PathEndMode.Touch;

        public override IEnumerable<Thing> PotentialWorkThingsGlobal(Pawn pawn)
        {
            foreach (Thing t in RM_CompWasteCask.AllCasks(pawn.Map))
            {
                if (t.TryGetComp<RM_CompWasteCask>().reburyMarked)
                {
                    yield return t;
                }
            }
        }

        public override bool ShouldSkip(Pawn pawn, bool forced = false)
        {
            return !RM_WastelandSettings.wastelandEnabled || !RM_WastelandSettings.caskReburialEnabled
                || !PotentialWorkThingsGlobal(pawn).Any();
        }

        public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            RM_CompWasteCask c = t.TryGetComp<RM_CompWasteCask>();
            return c != null && c.reburyMarked && t.Spawned && !t.IsForbidden(pawn)
                && RM_CompWasteCask.CanReburyAt(t.Position, t.Map)
                && pawn.CanReserve(t, 1, -1, null, forced);
        }

        public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            return JobMaker.MakeJob(RM_WastelandDefOf.RM_ReburyWasteCask, t);
        }
    }

    public class JobDriver_RM_ReburyWasteCask : JobDriver
    {
        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(job.targetA, job, 1, -1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedNullOrForbidden(TargetIndex.A);
            this.FailOn(() => !(job.targetA.Thing?.TryGetComp<RM_CompWasteCask>()?.reburyMarked ?? false));
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);
            int ticks = job.targetA.Thing?.TryGetComp<RM_CompWasteCask>()?.Props.reburyTicks ?? 900;
            Toil dig = Toils_General.Wait(ticks, TargetIndex.A)
                .WithProgressBarToilDelay(TargetIndex.A)
                .FailOnCannotTouch(TargetIndex.A, PathEndMode.Touch);
            yield return dig;
            yield return Toils_General.Do(() =>
            {
                job.targetA.Thing?.TryGetComp<RM_CompWasteCask>()?.Rebury(pawn);
            });
        }
    }

    [DefOf]
    public static class RM_WastelandDefOf
    {
        public static JobDef RM_ReburyWasteCask;
        public static ThingDef RM_WasteCask;

        static RM_WastelandDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_WastelandDefOf));
        }
    }
}
