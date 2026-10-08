using System.Collections.Generic;
using System.Text;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.Scarlands
{
    // WARSCAR_HOSPICE_DESERTERS_1 (standalone slice). Kneeling chassis rings, deserter histories, the
    // five-stage hospice cradle, the overseer-free servitor, named failed wrecks, a walk-in incident.
    // Not built here: Droidworks swap (campaign layer), pursuers, refusing a walk-in, etchant (pools unbuilt:
    // the limbs stage degrades to slower+riskier when RM_Etchant does not exist), cradle lights art.

    public class RM_DeserterHistoryDef : Def
    {
        public List<HediffDef> modifications;   // hediffs kept on waking
        public string damageText;               // how it died
        public string oddityText;               // what was done to it (shown at diagnosis / waking)
        public List<string> memories;           // three lines: lights, limbs, voice
        public string quietRead;                // optional: what a high-Intellectual pawn reads in the tones
    }

    [DefOf]
    public static class RM_HospiceDefOf
    {
        public static ThingDef RM_HospiceCradle;
        public static ThingDef RM_KneelingChassis_Intact;
        public static ThingDef RM_KneelingChassis_Slagged;
        public static ThingDef RM_KneelingChassis_Posed;
        public static ThingDef RM_FailedChassis;
        public static ThingDef RM_ChassisCore;
        public static PawnKindDef RM_AncientServitor;
        public static JobDef RM_HospiceHaul;
        static RM_HospiceDefOf() { DefOfHelper.EnsureInitializedInCtor(typeof(RM_HospiceDefOf)); }
    }

    public class CompProperties_DeserterHistory : CompProperties
    {
        public bool describeOddities;   // the failed wreck states what was wrong with it on hover
        public CompProperties_DeserterHistory() { compClass = typeof(CompDeserterHistory); }
    }

    // Rolls and saves one history and a unit name; carried by the intact chassis, the walk-in servitor and the failed wreck.
    public class CompDeserterHistory : ThingComp
    {
        public RM_DeserterHistoryDef history;
        public string unitName;
        public CompProperties_DeserterHistory Props { get { return (CompProperties_DeserterHistory)props; } }

        public void Roll()
        {
            if (history == null)
            {
                List<RM_DeserterHistoryDef> all = DefDatabase<RM_DeserterHistoryDef>.AllDefsListForReading;
                if (all.Count > 0) history = all.RandomElement();
            }
            if (unitName.NullOrEmpty()) unitName = "Unit " + Rand.RangeInclusive(1000, 9999);
        }
        public void CopyFrom(CompDeserterHistory o)
        {
            if (o == null) return;
            history = o.history;
            unitName = o.unitName;
        }
        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            if (!respawningAfterLoad && (history == null || unitName.NullOrEmpty())) Roll();
        }
        public override void PostExposeData()
        {
            Scribe_Defs.Look(ref history, "deserterHistory");
            Scribe_Values.Look(ref unitName, "deserterUnit");
        }
        public override string TransformLabel(string label)
        {
            return unitName.NullOrEmpty() ? label : label + " (" + unitName + ")";
        }
        public override string GetDescriptionPart()
        {
            if (!Props.describeOddities || history == null) return null;
            return history.oddityText + " " + history.damageText;
        }
    }

    // Walk-in state on the servitor pawn: walks to the nearest cradle, then kneels there as an intact chassis.
    public class CompProperties_DeserterWalker : CompProperties
    {
        public CompProperties_DeserterWalker() { compClass = typeof(CompDeserterWalker); }
    }

    public class CompDeserterWalker : ThingComp
    {
        public bool walking;
        public override void PostExposeData() { Scribe_Values.Look(ref walking, "deserterWalking", false); }

        public override void CompTick()
        {
            if (!walking || !parent.Spawned || !parent.IsHashIntervalTick(250)) return;
            Pawn p = parent as Pawn;
            if (p == null || p.Dead || p.Downed) { walking = false; return; }
            Map map = p.Map;
            Thing cradle = null;
            List<Thing> cradles = map.listerThings.ThingsOfDef(RM_HospiceDefOf.RM_HospiceCradle);
            for (int i = 0; i < cradles.Count; i++)
            {
                if (cradle != null && cradles[i].Position.DistanceTo(p.Position) >= cradle.Position.DistanceTo(p.Position)) continue;
                if (!p.CanReach(cradles[i].InteractionCell, PathEndMode.OnCell, Danger.Deadly)) continue;   // never walk at a sealed-off cradle forever
                cradle = cradles[i];
            }
            IntVec3 goal = cradle != null ? cradle.InteractionCell : p.Position;
            if (cradle == null || p.Position.DistanceTo(goal) <= 2.5f) { Kneel(p, goal, map); return; }
            if (p.CurJob == null || p.CurJob.def != JobDefOf.Goto)
            {
                Job j = JobMaker.MakeJob(JobDefOf.Goto, goal);
                j.locomotionUrgency = LocomotionUrgency.Walk;
                p.jobs.StartJob(j, JobCondition.InterruptForced);
            }
        }

        private void Kneel(Pawn p, IntVec3 at, Map map)
        {
            walking = false;
            CompDeserterHistory h = p.TryGetComp<CompDeserterHistory>();
            Thing chassis = ThingMaker.MakeThing(RM_HospiceDefOf.RM_KneelingChassis_Intact);
            CompDeserterHistory c = chassis.TryGetComp<CompDeserterHistory>();
            if (c != null) { c.CopyFrom(h); c.Roll(); }
            string unit = c != null ? c.unitName : "the machine";
            Thing min = MinifyUtility.MakeMinified(chassis);
            // Place the chassis first; the walker is consumed only once its replacement exists.
            if (!GenPlace.TryPlaceThing(min, at, map, ThingPlaceMode.Near)) { min.Destroy(); return; }
            p.Destroy();
            Find.LetterStack.ReceiveLetter("A deserter knelt", unit + " reached the cradle, stopped, and knelt. Haul it in to begin the repair.",
                LetterDefOf.NeutralEvent, min);
        }
    }

    public class Building_KneelingChassis : Building
    {
        public override void Destroy(DestroyMode mode = DestroyMode.Vanish)
        {
            Map m = Map;
            IntVec3 p = Position;
            float chance = def == RM_HospiceDefOf.RM_KneelingChassis_Posed ? 0.4f : (def == RM_HospiceDefOf.RM_KneelingChassis_Slagged ? 0.15f : 0f);
            bool core = mode == DestroyMode.Deconstruct && Rand.Chance(chance);
            base.Destroy(mode);
            if (core && m != null) GenPlace.TryPlaceThing(ThingMaker.MakeThing(RM_HospiceDefOf.RM_ChassisCore), p, m, ThingPlaceMode.Near);
        }
    }

    // The five-stage cradle. stage: 0 empty, 1 diagnosis, 2 lights, 3 limbs, 4 voice, 5 waking.
    public class Building_HospiceCradle : Building
    {
        public const int Rare = 250;
        public const int EtchantGraceTicks = 15000;
        private static readonly string[] StageLabels = { "empty", "diagnosis", "lights", "twitching limbs", "voice fragments", "waking" };

        private int stage;
        private RM_DeserterHistoryDef history;
        private string unitName;
        private bool partIn;
        private bool etchantIn;
        private int ticksLeft = -1;
        private int graceTicks;
        private int revealed;
        private bool oddities;

        public static ThingDef EtchantDef { get { return DefDatabase<ThingDef>.GetNamedSilentFail("RM_Etchant"); } }
        private static float StageDays { get { return RM_WarscarSettings.hospiceStageDays; } }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref stage, "stage", 0);
            Scribe_Defs.Look(ref history, "history");
            Scribe_Values.Look(ref unitName, "unitName");
            Scribe_Values.Look(ref partIn, "partIn", false);
            Scribe_Values.Look(ref etchantIn, "etchantIn", false);
            Scribe_Values.Look(ref ticksLeft, "ticksLeft", -1);
            Scribe_Values.Look(ref graceTicks, "graceTicks", 0);
            Scribe_Values.Look(ref revealed, "revealed", 0);
            Scribe_Values.Look(ref oddities, "oddities", false);
        }

        public override string Label
        {
            get { return stage == 0 ? base.Label : base.Label + " (" + StageLabels[stage] + ")"; }
        }

        private ThingDef WantedPart()
        {
            if (stage == 0 || ticksLeft >= 0) return null;
            switch (stage)
            {
                case 2: return partIn ? null : ThingDefOf.ComponentIndustrial;
                case 3:
                    if (etchantIn || EtchantDef == null || graceTicks >= EtchantGraceTicks) return null;
                    return EtchantDef;
                case 4: return partIn ? null : RM_HospiceDefOf.RM_ChassisCore;
            }
            return null;
        }

        public bool Accepts(Thing t)
        {
            if (t == null || !Spawned || !RM_WarscarSettings.hospiceEnabled) return false;
            if (stage == 0)
            {
                MinifiedThing m = t as MinifiedThing;
                return m != null && m.InnerThing != null && m.InnerThing.def == RM_HospiceDefOf.RM_KneelingChassis_Intact;
            }
            ThingDef w = WantedPart();
            return w != null && t.def == w;
        }

        public void Accept(Thing t)
        {
            if (stage == 0)
            {
                MinifiedThing m = (MinifiedThing)t;
                CompDeserterHistory c = m.InnerThing.TryGetComp<CompDeserterHistory>();
                if (c != null) { c.Roll(); history = c.history; unitName = c.unitName; }
                stage = 1; ticksLeft = -1; revealed = 0; oddities = false; graceTicks = 0; partIn = false; etchantIn = false;
                return;
            }
            if (stage == 3) etchantIn = true; else partIn = true;
        }

        public override void TickRare()
        {
            base.TickRare();
            if (stage == 0 || !RM_WarscarSettings.hospiceEnabled) return;
            if (ticksLeft < 0)
            {
                bool ready = true;
                if (stage == 2 || stage == 4) ready = partIn;
                else if (stage == 3 && !etchantIn && EtchantDef != null)
                {
                    graceTicks += Rare;
                    ready = graceTicks >= EtchantGraceTicks;
                }
                if (!ready) return;
                float f = (stage == 3 && !etchantIn) ? 1.5f : 1f;   // no etchant: slower
                ticksLeft = Mathf.Max(Rare, Mathf.RoundToInt(StageDays * 60000f * f));
                return;
            }
            ticksLeft -= Rare;
            if (ticksLeft <= 0) Complete();
        }

        private void Complete()
        {
            if (stage >= 2 && stage <= 4)
            {
                float chance = RM_WarscarSettings.hospiceFailureChance;
                if (RM_OldTongue.HospiceUnlocked) chance -= 0.04f;
                if (stage == 3 && !etchantIn) chance += 0.15f;
                if (Rand.Chance(Mathf.Clamp01(chance))) { Fail(); return; }
            }
            switch (stage)
            {
                case 1:
                    oddities = RM_OldTongue.HospiceUnlocked && history != null;   // a history def removed since saving loads null
                    Find.LetterStack.ReceiveLetter(unitName + ": diagnosis",
                        oddities ? history.oddityText + "\n\n" + history.damageText
                                 : "The chassis is open on the cradle. The protocols for reading it are not yours yet; what was done to it will show when it wakes.",
                        LetterDefOf.NeutralEvent, this);
                    break;
                case 2: Reveal(0); break;
                case 3: LashOut(); Reveal(1); break;
                case 4: Reveal(2); break;
                case 5: Wake(); return;
            }
            stage++;
            partIn = false; etchantIn = false; ticksLeft = -1; graceTicks = 0;
        }

        private bool ReaderPresent()
        {
            List<Pawn> cols = Map.mapPawns.FreeColonistsSpawned;
            for (int i = 0; i < cols.Count; i++)
            {
                SkillRecord s = cols[i].skills != null ? cols[i].skills.GetSkill(SkillDefOf.Intellectual) : null;
                if (s != null && !s.TotallyDisabled && s.Level >= 10) return true;
            }
            return false;
        }

        private string MemoryLine(int i)
        {
            string line = history.memories[i];
            if (i == 2 && !history.quietRead.NullOrEmpty() && ReaderPresent()) line += "  (read: \"" + history.quietRead + "\")";
            return line;
        }

        private void Reveal(int i)
        {
            if (history == null || history.memories == null || i >= history.memories.Count) return;
            revealed = i + 1;
            string line = MemoryLine(i);
            Find.LetterStack.ReceiveLetter(unitName + ": " + StageLabels[stage], line, LetterDefOf.NeutralEvent, this);
            if (i == 2) MoteMaker.ThrowText(DrawPos, Map, line.Length > 60 ? line.Substring(0, 60) : line, Color.white, 4f);
        }

        private void LashOut()
        {
            if (!RM_WarscarSettings.hospiceLashOut || !Rand.Chance(0.35f)) return;
            foreach (IntVec3 c in GenAdj.CellsAdjacent8Way(this))
            {
                if (!c.InBounds(Map)) continue;
                Pawn p = c.GetFirstPawn(Map);
                if (p == null || p.Dead) continue;
                p.TakeDamage(new DamageInfo(DamageDefOf.Blunt, 4f, 0f, -1f, this));
                Messages.Message(unitName + " lashed out at " + p.LabelShort + " and went still again.", p, MessageTypeDefOf.NegativeEvent);
                return;
            }
        }

        private void Fail()
        {
            Thing f = ThingMaker.MakeThing(RM_HospiceDefOf.RM_FailedChassis);
            CompDeserterHistory c = f.TryGetComp<CompDeserterHistory>();
            if (c != null) { c.history = history; c.unitName = unitName; }
            GenPlace.TryPlaceThing(f, InteractionCell, Map, ThingPlaceMode.Near);
            Find.LetterStack.ReceiveLetter(unitName + " did not wake",
                "The repair failed at " + StageLabels[stage] + ". What is left keeps its name and what was wrong with it.", LetterDefOf.NegativeEvent, f);
            Reset();
        }

        private void Wake()
        {
            Pawn p = PawnGenerator.GeneratePawn(RM_HospiceDefOf.RM_AncientServitor, Faction.OfPlayer);
            if (history != null && history.modifications != null)
                for (int i = 0; i < history.modifications.Count; i++) p.health.AddHediff(history.modifications[i]);
            if (!unitName.NullOrEmpty()) p.Name = new NameSingle(unitName);
            CompDeserterHistory c = p.TryGetComp<CompDeserterHistory>();
            if (c != null) { c.history = history; c.unitName = unitName; }
            GenSpawn.Spawn(p, InteractionCell, Map);
            string body = "It looked at the Cathedral first.";
            if (history != null && !oddities) body += "\n\n" + history.oddityText;
            Find.LetterStack.ReceiveLetter(unitName + " is awake", body, LetterDefOf.PositiveEvent, p);
            Reset();
        }

        private void Reset()
        {
            stage = 0; history = null; unitName = null; partIn = false; etchantIn = false; ticksLeft = -1; graceTicks = 0; revealed = 0; oddities = false;
        }

        public override string GetInspectString()
        {
            StringBuilder sb = new StringBuilder();
            string b = base.GetInspectString();
            if (!b.NullOrEmpty()) sb.AppendLine(b);
            if (stage == 0) { sb.Append("Empty. Haul an intact kneeling chassis here."); return sb.ToString(); }
            sb.AppendLine(unitName + ": " + StageLabels[stage]);
            if (ticksLeft >= 0) sb.AppendLine("Time left in this stage: " + ticksLeft.ToStringTicksToPeriod());
            else
            {
                ThingDef w = WantedPart();
                if (w != null) sb.AppendLine("Needs: " + w.label + (stage == 3 ? " (or proceeds slower and riskier in " + (EtchantGraceTicks - graceTicks).ToStringTicksToPeriod() + ")" : ""));
                else if (stage == 3 && EtchantDef == null) sb.AppendLine("No etchant exists yet: this stage is slower and riskier.");
            }
            if (oddities && history != null) sb.AppendLine(history.oddityText);
            for (int i = 0; history != null && history.memories != null && i < revealed && i < history.memories.Count; i++) sb.AppendLine(MemoryLine(i));
            return sb.ToString().TrimEndNewlines();
        }
    }

    public class WorkGiver_HospiceHaul : WorkGiver_Scanner
    {
        public override ThingRequest PotentialWorkThingRequest { get { return ThingRequest.ForDef(RM_HospiceDefOf.RM_HospiceCradle); } }
        public override PathEndMode PathEndMode { get { return PathEndMode.Touch; } }

        public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false) { return JobOnThing(pawn, t, forced) != null; }

        public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            Building_HospiceCradle c = t as Building_HospiceCradle;
            if (c == null || !RM_WarscarSettings.hospiceEnabled || t.IsForbidden(pawn) || !pawn.CanReserve(c, 1, -1, null, forced)) return null;
            Thing item = GenClosest.ClosestThingReachable(pawn.Position, pawn.Map, ThingRequest.ForGroup(ThingRequestGroup.HaulableEver),
                PathEndMode.ClosestTouch, TraverseParms.For(pawn), 9999f, x => c.Accepts(x) && !x.IsForbidden(pawn) && pawn.CanReserve(x));
            if (item == null) return null;
            Job j = JobMaker.MakeJob(RM_HospiceDefOf.RM_HospiceHaul, c, item);
            j.count = 1;
            return j;
        }
    }

    public class JobDriver_HospiceHaul : JobDriver
    {
        private Building_HospiceCradle Cradle { get { return (Building_HospiceCradle)job.GetTarget(TargetIndex.A).Thing; } }
        private Thing Item { get { return job.GetTarget(TargetIndex.B).Thing; } }

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(job.GetTarget(TargetIndex.A), job, 1, -1, null, errorOnFailed)
                && pawn.Reserve(job.GetTarget(TargetIndex.B), job, 1, -1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedNullOrForbidden(TargetIndex.A);
            this.FailOn(() => !Cradle.Accepts(Item));
            yield return Toils_Goto.GotoThing(TargetIndex.B, PathEndMode.ClosestTouch).FailOnDespawnedNullOrForbidden(TargetIndex.B).FailOnSomeonePhysicallyInteracting(TargetIndex.B);
            yield return Toils_Haul.StartCarryThing(TargetIndex.B);
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);
            yield return Toils_General.Wait(150).FailOnDestroyedNullOrForbidden(TargetIndex.A).WithProgressBarToilDelay(TargetIndex.A);
            Toil fin = new Toil();
            fin.initAction = delegate
            {
                Thing carried = pawn.carryTracker.CarriedThing;
                if (carried == null || !Cradle.Accepts(carried)) return;
                Cradle.Accept(carried);
                pawn.carryTracker.innerContainer.ClearAndDestroyContents();
            };
            fin.defaultCompleteMode = ToilCompleteMode.Instant;
            yield return fin;
        }
    }

    // Rings of kneeling chassis around the ruin layout's centre (centroid of ancient fortified walls, else the map centre).
    public class GenStep_KneelingRings : GenStep
    {
        public override int SeedPart { get { return 84921911; } }

        public override void Generate(Map map, GenStepParams parms)
        {
            if (!RM_WarscarSettings.hospiceEnabled) return;
            Vector3 centre = map.Center.ToVector3Shifted();
            ThingDef wallDef = DefDatabase<ThingDef>.GetNamedSilentFail("AncientFortifiedWall");
            if (wallDef != null)
            {
                List<Thing> walls = map.listerThings.ThingsOfDef(wallDef);
                if (walls.Count >= 6)
                {
                    float sx = 0f, sz = 0f;
                    for (int i = 0; i < walls.Count; i++) { sx += walls[i].Position.x; sz += walls[i].Position.z; }
                    centre = new Vector3(sx / walls.Count + 0.5f, 0f, sz / walls.Count + 0.5f);
                }
            }
            List<IntVec3> slots = new List<IntVec3>();
            int[] radii = { 6, 10, 14 };
            for (int r = 0; r < radii.Length; r++)
            {
                int count = Mathf.RoundToInt(radii[r] * 1.5f);
                for (int i = 0; i < count; i++)
                {
                    float a = (360f * i / count + Rand.Range(-8f, 8f)) * Mathf.Deg2Rad;
                    IntVec3 c = new IntVec3(Mathf.RoundToInt(centre.x + radii[r] * Mathf.Cos(a)), 0, Mathf.RoundToInt(centre.z + radii[r] * Mathf.Sin(a)));
                    if (!c.InBounds(map) || !c.Standable(map) || c.GetEdifice(map) != null || c.GetFirstItem(map) != null) continue;
                    if (Rand.Chance(0.2f)) continue;   // gaps
                    slots.Add(c);
                }
            }
            slots.Shuffle();
            int intact = Mathf.Min(slots.Count, Rand.RangeInclusive(0, Mathf.Clamp(RM_WarscarSettings.hospiceIntactPerMap, 0, 3)));
            for (int i = 0; i < slots.Count; i++)
            {
                IntVec3 c = slots[i];
                Rot4 rot = Rot4.FromAngleFlat((centre - c.ToVector3Shifted()).AngleFlat());
                if (i < intact)
                {
                    Thing t = ThingMaker.MakeThing(RM_HospiceDefOf.RM_KneelingChassis_Intact);
                    CompDeserterHistory h = t.TryGetComp<CompDeserterHistory>();
                    if (h != null) h.Roll();
                    GenSpawn.Spawn(MinifyUtility.MakeMinified(t), c, map);
                }
                else
                {
                    ThingDef d = Rand.Chance(0.3f) ? RM_HospiceDefOf.RM_KneelingChassis_Posed : RM_HospiceDefOf.RM_KneelingChassis_Slagged;
                    GenSpawn.Spawn(ThingMaker.MakeThing(d), c, map, rot);
                }
            }
        }
    }

    // "A deserter walks in": rare, only while a cradle stands on the map.
    public class IncidentWorker_DeserterWalksIn : IncidentWorker
    {
        protected override bool CanFireNowSub(IncidentParms parms)
        {
            Map map = parms.target as Map;
            if (map == null || !RM_WarscarSettings.hospiceEnabled || !RM_WarscarSettings.hospiceWalkInEnabled) return false;
            return map.listerThings.ThingsOfDef(RM_HospiceDefOf.RM_HospiceCradle).Count > 0;
        }

        protected override bool TryExecuteWorker(IncidentParms parms)
        {
            Map map = (Map)parms.target;
            if (!Rand.Chance(Mathf.Clamp01(RM_WarscarSettings.hospiceWalkInFrequency))) return false;
            IntVec3 cell;
            if (!CellFinder.TryFindRandomEdgeCellWith(c => c.Walkable(map) && map.reachability.CanReachColony(c), map, CellFinder.EdgeRoadChance_Ignore, out cell)) return false;
            Pawn p = PawnGenerator.GeneratePawn(RM_HospiceDefOf.RM_AncientServitor, null);
            p.SetFaction(null);
            CompDeserterHistory h = p.TryGetComp<CompDeserterHistory>();
            if (h != null) h.Roll();
            CompDeserterWalker w = p.TryGetComp<CompDeserterWalker>();
            if (w != null) w.walking = true;
            if (h != null && !h.unitName.NullOrEmpty()) p.Name = new NameSingle(h.unitName);
            GenSpawn.Spawn(p, cell, map);
            SendStandardLetter("A damaged machine", "A damaged machine is walking in from the edge of the map, straight toward your hospice cradle. It is not hostile.", LetterDefOf.NeutralEvent, parms, p);
            return true;
        }
    }
}
