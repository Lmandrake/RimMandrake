using RimWorld;
using System.Linq;
using Verse;

namespace RimMandrake.Stillsand
{
    /// <summary>
    /// WATER_LEDGER_DOUBLE_CHARGE_1's live row (validation.py water chain, component "still_water_charged_once"): static_call surfaces that
    /// read the water ledger's debt and run ONE solar-still cycle outright, so the row does not wait 6,000 sunlit ticks.
    /// Read-only except ProofStillCycle, which does exactly what a fired CompTickRare does (FindFeed + Consume), and
    /// ProofDrinkHook, which runs the water item's ingestion hook once without consuming it.
    /// </summary>
    public static class RM_WaterLedgerProof
    {
        /// <summary>"-" -&gt; "LEDGER live=bool debt=litres def=defName|none enabled=bool".</summary>
        public static string ProofLedger(string arg)
        {
            RM_WaterLedgerDef def = RM_WaterLedger.ActiveDef;
            RM_WaterLedger ledger = RM_WaterLedger.Current;
            bool live = def != null && ledger != null && RM_StillsandWaterSettings.ledgerEnabled;
            return "LEDGER live=" + live + " debt=" + (ledger != null ? ledger.Debt.ToString("0.###") : "none")
                + " def=" + (def?.defName ?? "none") + " enabled=" + RM_StillsandWaterSettings.ledgerEnabled
                + " countsHere=" + (def != null && Find.CurrentMap != null && def.CountsOn(Find.CurrentMap));
        }

        /// <summary>"x,z" (a cell of a solar or wringing still on the current map) -&gt; one cycle run now:
        /// "CYCLE ran=bool feed=defName units=n litres=n water=defName".</summary>
        public static string ProofStillCycle(string arg)
        {
            Map map = Find.CurrentMap;
            string[] a = (arg ?? "").Split(',');
            if (map == null || a.Length != 2 || !int.TryParse(a[0], out int x) || !int.TryParse(a[1], out int z))
            {
                return "REFUSED: arg must be x,z on a current map";
            }
            IntVec3 c = new IntVec3(x, 0, z);
            if (!c.InBounds(map))
            {
                return "REFUSED: out of bounds";
            }
            foreach (Thing t in c.GetThingList(map))
            {
                RM_CompSolarStill still = t.TryGetComp<RM_CompSolarStill>();
                if (still == null)
                {
                    continue;
                }
                if (!still.FindFeed(out Thing stock, out int units, out int litres))
                {
                    return "CYCLE ran=False feed=none still=" + t.ThingID;
                }
                string feed = stock.def.defName;
                still.Consume(stock, units, litres);
                return "CYCLE ran=True feed=" + feed + " units=" + units + " litres=" + litres
                    + " water=" + (RM_CompSolarStill.WaterDef()?.defName ?? "none") + " still=" + t.ThingID;
            }
            return "NONE: no still at " + x + "," + z;
        }

        /// <summary>"x,z" (a cell holding a still's water item) -&gt; the item's own drink hook run once, as an ingestion by
        /// the first free colonist would run it (RM_CompWaterVolume.PostIngested: books unless bookedAtSource). The item is
        /// not consumed. "DRINK item=defName bookedAtSource=bool by=pawn".</summary>
        public static string ProofDrinkHook(string arg)
        {
            Map map = Find.CurrentMap;
            string[] a = (arg ?? "").Split(',');
            if (map == null || a.Length != 2 || !int.TryParse(a[0], out int x) || !int.TryParse(a[1], out int z))
            {
                return "REFUSED: arg must be x,z on a current map";
            }
            IntVec3 c = new IntVec3(x, 0, z);
            if (!c.InBounds(map))
            {
                return "REFUSED: out of bounds";
            }
            Pawn drinker = map.mapPawns.FreeColonistsSpawned.FirstOrFallback();
            if (drinker == null)
            {
                return "REFUSED: no free colonist on the map";
            }
            foreach (Thing t in c.GetThingList(map))
            {
                RM_CompWaterVolume comp = t.TryGetComp<RM_CompWaterVolume>();
                if (comp == null)
                {
                    continue;
                }
                comp.PostIngested(drinker);
                return "DRINK item=" + t.def.defName + " bookedAtSource=" + comp.Props.bookedAtSource + " by=" + drinker.ThingID;
            }
            return "NONE: no water item at " + x + "," + z;
        }

        // ── STILLSAND_RETURN_REMAINDER_1 A4: the REAL drink. ProofDrinkHook runs the hook by hand; these two let a
        //    thirsty colonist drink through Dubs Bad Hygiene's own thirst job giver, so the row sees whether that path
        //    reaches RM_CompWaterVolume.PostIngested. DBH is reached by type name only (no assembly reference).

        private static Need ThirstNeed(Pawn p)
        {
            return p?.needs?.AllNeeds?.FirstOrDefault(n => n.GetType().FullName == "DubsBadHygiene.Need_Thirst");
        }

        /// <summary>"x,z" (a cell holding a water item) -&gt; one unit moved into the first free colonist's inventory,
        /// that colonist's DBH thirst set to 0, DBH's JobGiver_DrinkWater asked for a job and the job started:
        /// "THIRSTJOB dbh=bool job=defName target=defName item=defName pawn=ThingID". dbh=False when DBH's thirst need
        /// or giver is not loaded (nothing else is done then).</summary>
        public static string ProofThirstJob(string arg)
        {
            Map map = Find.CurrentMap;
            string[] a = (arg ?? "").Split(',');
            if (map == null || a.Length != 2 || !int.TryParse(a[0], out int x) || !int.TryParse(a[1], out int z))
            {
                return "REFUSED: arg must be x,z on a current map";
            }
            IntVec3 c = new IntVec3(x, 0, z);
            if (!c.InBounds(map))
            {
                return "REFUSED: out of bounds";
            }
            Pawn drinker = map.mapPawns.FreeColonistsSpawned.FirstOrFallback();
            if (drinker == null)
            {
                return "REFUSED: no free colonist on the map";
            }
            System.Type giverType = GenTypes.GetTypeInAnyAssembly("DubsBadHygiene.JobGiver_DrinkWater");
            Need thirst = ThirstNeed(drinker);
            if (giverType == null || thirst == null)
            {
                return "THIRSTJOB dbh=False giver=" + (giverType != null) + " need=" + (thirst != null);
            }
            Thing item = c.GetThingList(map).FirstOrDefault(t => t.TryGetComp<RM_CompWaterVolume>() != null);
            if (item == null)
            {
                return "NONE: no water item at " + x + "," + z;
            }
            Thing one = item.SplitOff(1);
            if (!drinker.inventory.innerContainer.TryAddOrTransfer(one))
            {
                return "REFUSED: the item would not go into " + drinker.ThingID + "'s inventory";
            }
            if (drinker.drafter != null)
            {
                drinker.drafter.Drafted = false;
            }
            thirst.CurLevel = 0f;
            Verse.AI.ThinkNode_JobGiver giver = (Verse.AI.ThinkNode_JobGiver)System.Activator.CreateInstance(giverType);
            Verse.AI.Job job = giver.TryIssueJobPackage(drinker, default(Verse.AI.JobIssueParams)).Job;
            if (job == null)
            {
                return "THIRSTJOB dbh=True job=none target=none item=" + one.def.defName + " pawn=" + drinker.ThingID;
            }
            drinker.jobs.StartJob(job, Verse.AI.JobCondition.InterruptForced);
            Log.Message("[RM_WaterLedgerProof] DBH thirst job " + job.def.defName + " on " + (job.targetA.Thing?.def.defName ?? "a cell")
                + " for " + drinker.ThingID);
            return "THIRSTJOB dbh=True job=" + job.def.defName + " target=" + (job.targetA.Thing?.def.defName ?? "none")
                + " item=" + one.def.defName + " pawn=" + drinker.ThingID;
        }

        /// <summary>"pawnThingID" -&gt; "THIRSTDONE held=n job=defName|none thirst=level": n = water-volume items still
        /// in that pawn's inventory or hands.</summary>
        public static string ProofThirstDone(string arg)
        {
            Map map = Find.CurrentMap;
            Pawn p = map?.mapPawns.AllPawnsSpawned.FirstOrDefault(q => q.ThingID == arg);
            if (p == null)
            {
                return "NONE: no spawned pawn " + arg;
            }
            int held = p.inventory.innerContainer.Where(t => t.TryGetComp<RM_CompWaterVolume>() != null).Sum(t => t.stackCount);
            Thing carried = p.carryTracker?.CarriedThing;
            if (carried != null && carried.TryGetComp<RM_CompWaterVolume>() != null)
            {
                held += carried.stackCount;
            }
            return "THIRSTDONE held=" + held + " job=" + (p.CurJobDef?.defName ?? "none")
                + " thirst=" + (ThirstNeed(p)?.CurLevel.ToString("0.###") ?? "none");
        }

        // ── STILLSAND_RETURN_REMAINDER_1 (prove_stillsand_return.py): the Sun-Debt colony, the Return's opening,
        //    one outcome at a stone, and the drawn wet-sand line. All read-only except ProofBelieve (adds the
        //    ledger's believer precept to the player's primary ideo, as the ideo editor would) and
        //    ProofReturnOutcome (runs the outcome the ritual would run, without staging the ritual).

        private static Precept_Ritual ReturnRitual(out Ideo ideo)
        {
            ideo = Faction.OfPlayer?.ideos?.PrimaryIdeo;
            PreceptDef pd = RM_WaterLedger.ActiveDef?.believerPrecept;
            if (ideo == null || pd == null)
            {
                return null;
            }
            return ideo.PreceptsListForReading.FirstOrDefault(p => p.def == pd) as Precept_Ritual;
        }

        /// <summary>"-" -&gt; the player's primary ideo holds the ledger's believer precept (added if absent):
        /// "BELIEVE added=bool ideo=name precept=defName ritual=bool".</summary>
        public static string ProofBelieve(string arg)
        {
            PreceptDef pd = RM_WaterLedger.ActiveDef?.believerPrecept;
            if (pd == null)
            {
                return "REFUSED: no ledger def with a believer precept (this tier ships none)";
            }
            Precept_Ritual r = ReturnRitual(out Ideo ideo);
            if (ideo == null)
            {
                return "REFUSED: the player has no primary ideo";
            }
            bool added = false;
            if (r == null)
            {
                ideo.AddPrecept(PreceptMaker.MakePrecept(pd), true, null, pd.ritualPatternBase);
                added = true;
                r = ReturnRitual(out ideo);
            }
            return "BELIEVE added=" + added + " ideo=" + ideo.name.Replace(' ', '_') + " precept=" + pd.defName
                + " ritual=" + (r != null);
        }

        /// <summary>"-" -&gt; "RETURN serial=n obligations=n sinceOpen=ticks gap=ticks debt=litres ritual=bool"
        /// (an opening is refused while sinceOpen &lt; gap, the def's minTicksBetweenOpenings).</summary>
        public static string ProofReturnState(string arg)
        {
            RM_WaterLedger ledger = RM_WaterLedger.Current;
            Precept_Ritual r = ReturnRitual(out Ideo _);
            return "RETURN serial=" + (ledger?.OpeningSerial.ToString() ?? "none")
                + " obligations=" + (r?.activeObligations?.Count ?? 0)
                + " sinceOpen=" + (ledger != null ? (Find.TickManager.TicksGame - ledger.LastOpeningTick).ToString() : "none")
                + " gap=" + (RM_WaterLedger.ActiveDef?.minTicksBetweenOpenings.ToString() ?? "none")
                + " debt=" + (ledger != null ? ledger.Debt.ToString("0.###") : "none") + " ritual=" + (r != null);
        }

        /// <summary>"x,z,positivity" (a debt stone's cell; positivity -2..2) -&gt; the Return's outcome run there:
        /// "OUTCOME debt0=n debt1=n bloom0=n bloom1=n stone=defName". bloom counts the biome's bloom plant within
        /// the ring radius + 1 of the stone.</summary>
        public static string ProofReturnOutcome(string arg)
        {
            Map map = Find.CurrentMap;
            RM_WaterLedgerDef def = RM_WaterLedger.ActiveDef;
            string[] a = (arg ?? "").Split(',');
            if (map == null || def == null || a.Length != 3 || !int.TryParse(a[0], out int x) || !int.TryParse(a[1], out int z)
                || !int.TryParse(a[2], out int pos))
            {
                return "REFUSED: arg must be x,z,positivity on a current map with a ledger def";
            }
            IntVec3 c = new IntVec3(x, 0, z);
            Thing stone = c.InBounds(map) ? c.GetFirstBuilding(map) : null;
            if (stone == null)
            {
                return "NONE: no building at " + x + "," + z;
            }
            ThingDef bloomDef = RM_StillsandWater.Ext(map)?.bloomPlant;
            float radius = def.bloomRingRadius + 1f;
            int Bloom() => bloomDef == null ? 0 : map.listerThings.ThingsOfDef(bloomDef).Count(t => t.Position.InHorDistOf(c, radius));
            float d0 = RM_WaterLedger.Current?.Debt ?? -1f;
            int b0 = Bloom();
            LookTargets look = null;
            string text = RM_RitualOutcomeEffectWorker_WaterReturn.ApplyReturn(def, map, new TargetInfo(stone), pos, pos > 0, ref look);
            float d1 = RM_WaterLedger.Current?.Debt ?? -1f;
            Log.Message("[RM_WaterLedgerProof] Return outcome " + pos + " at " + stone.def.defName + ": " + (text ?? "").Replace('\n', ' '));
            return "OUTCOME debt0=" + d0.ToString("0.###") + " debt1=" + d1.ToString("0.###") + " bloom0=" + b0
                + " bloom1=" + Bloom() + " stone=" + stone.def.defName;
        }

        /// <summary>"-" -&gt; the current map's wet sand and its drawn line: "WET cells=n live=n inView=n drawn=n drawTick=t
        /// now=t setting=bool". drawn is the stain count of the last frame the map was on screen; inView counts the live
        /// wet cells inside the camera's view now.</summary>
        public static string ProofWetSand(string arg)
        {
            Map map = Find.CurrentMap;
            RM_MapComponent_WetSand wet = RM_MapComponent_WetSand.For(map);
            if (wet == null)
            {
                return "NONE: no wet-sand component on the current map";
            }
            CellRect view = Find.CameraDriver.CurrentViewRect;
            return "WET cells=" + wet.WetCellCount + " live=" + wet.WetCells.Count(wet.IsWet)
                + " inView=" + wet.WetCells.Count(c => wet.IsWet(c) && view.Contains(c)) + " drawn=" + wet.DrawnLastFrame
                + " drawTick=" + wet.LastDrawTick + " now=" + Find.TickManager.TicksGame
                + " setting=" + RM_StillsandWaterSettings.drawReturnLine;
        }
    }
}
