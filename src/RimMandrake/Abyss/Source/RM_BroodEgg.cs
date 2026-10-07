using System.Collections.Generic;
using System.Text;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;
using Verse.Sound;

namespace RimMandrake.Abyss
{
    // ABYSS_LIGHTFALL_BROOD_WRECK_1 — the egg and the bonded beast.
    //
    // The egg (RM_SummEgg): taking it feeds the lair's wake meter once; putting it back near the
    // sleeper refunds most of that. While it sits on a player HOME map away from the lair, Witchfire
    // storms keep coming to that map and with each one a summ comes looking (owner's option C: "carrying
    // the egg brings Witchfire storms home ... one dragon comes looking" - a summ, never a dragon).
    // It hatches a summing. It imprints ONLY if a great bone of its kind stands aboard the player's
    // gravship on that map (owner, typed 2026-10-01); otherwise it hatches wild and the inspect text said why.

    public class CompProperties_RM_SummEgg : CompProperties
    {
        public float hatchDays = 20f;
        public PawnKindDef hatchKind;
        public ThingDef greatBoneDef;
        public HediffDef bondedHungerHediff;
        public IntRange stormIntervalDays = new IntRange(5, 9);
        public int summComesAfterTicks = 6000;
        public float returnRadius = 9f;

        public CompProperties_RM_SummEgg() { compClass = typeof(RM_CompSummEgg); }
    }

    public class RM_CompSummEgg : ThingComp
    {
        private float progress;          // 0..1
        private bool stolen;
        private int lairMapId = -1;
        private int nextStormTick = -1;
        private int summDueTick = -1;

        private CompProperties_RM_SummEgg Props => (CompProperties_RM_SummEgg)props;
        private const int Interval = 250;

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            if (lairMapId < 0 && parent.Map != null && RM_MapComponent_BroodWake.For(parent.Map)?.lairBuilt == true)
                lairMapId = parent.Map.uniqueID;
        }

        private Map LairMap()
        {
            if (lairMapId < 0) return null;
            List<Map> maps = Find.Maps;
            for (int i = 0; i < maps.Count; i++) if (maps[i].uniqueID == lairMapId) return maps[i];
            return null;
        }

        private bool HeldByPlayer()
        {
            IThingHolder h = parent.ParentHolder;
            if (h is Pawn_CarryTracker ct) return ct.pawn.Faction == Faction.OfPlayer;
            if (h is Pawn_InventoryTracker inv) return inv.pawn.Faction == Faction.OfPlayer;
            return false;
        }

        public override void CompTick()
        {
            base.CompTick();
            if (!parent.IsHashIntervalTick(Interval)) return;

            Map here = parent.MapHeld;
            Map lair = LairMap();
            RM_MapComponent_BroodWake wake = lair != null ? RM_MapComponent_BroodWake.For(lair) : null;

            // theft and return
            bool away = lair == null || here != lair;
            if (!stolen && lairMapId >= 0 && (HeldByPlayer() || away))
            {
                stolen = true;
                wake?.Notify(BroodWakeLogic.EggWeight, "an egg was taken");
            }
            else if (stolen && wake != null && here == lair && parent.Spawned && wake.motherCell.IsValid
                     && parent.Position.InHorDistOf(wake.motherCell, Props.returnRadius))
            {
                stolen = false;
                wake.Notify(-BroodWakeLogic.EggWeight * BroodWakeLogic.EggReturnRefund, "the egg came back");
                Messages.Message("The egg is back against her coils. The brood-mother settles.", parent, MessageTypeDefOf.PositiveEvent);
            }

            // storms at home while it is kept there
            if (stolen && RM_AbyssSettings.eggStormsEnabled && here != null && here != lair && here.IsPlayerHome)
                StormTick(here);

            // hatching
            progress += Interval / (Props.hatchDays * GenDate.TicksPerDay);
            if (progress >= 1f) Hatch();
        }

        private void StormTick(Map home)
        {
            int now = Find.TickManager.TicksGame;
            if (nextStormTick < 0) nextStormTick = now + Props.stormIntervalDays.RandomInRange * GenDate.TicksPerDay / 3;   // the first comes soon
            if (now >= nextStormTick)
            {
                WeatherDef storm = DefDatabase<WeatherDef>.GetNamedSilentFail(RM_MapComponent_Dark.StormWeather);
                if (storm != null) home.weatherManager.TransitionTo(storm);
                SoundDef rumble = DefDatabase<SoundDef>.GetNamedSilentFail("Thunder_OffMap");
                rumble?.PlayOneShotOnCamera(home);
                summDueTick = now + Props.summComesAfterTicks;
                nextStormTick = now + Props.stormIntervalDays.RandomInRange * GenDate.TicksPerDay;
                Messages.Message("A Witchfire storm is gathering over the colony. The stolen egg is calling, and something is listening.",
                    new LookTargets(parent), MessageTypeDefOf.ThreatSmall);
            }
            if (summDueTick >= 0 && now >= summDueTick)
            {
                summDueTick = -1;
                PawnKindDef kind = DefDatabase<PawnKindDef>.GetNamedSilentFail("RM_Summ");
                if (kind == null) return;
                if (!CellFinder.TryFindRandomEdgeCellWith(c => c.Standable(home) && !c.Fogged(home), home, CellFinder.EdgeRoadChance_Neutral, out IntVec3 cell)) return;
                Pawn summ = PawnGenerator.GeneratePawn(new PawnGenerationRequest(kind, null, PawnGenerationContext.NonPlayer, home.Tile));
                GenSpawn.Spawn(summ, cell, home);
                summ.mindState.mentalStateHandler.TryStartMentalState(MentalStateDefOf.Manhunter, "the egg's call", forced: true);
                Find.LetterStack.ReceiveLetter("A summ has come for the egg",
                    "The thunder was a summ calling. One has come down out of the storm and is crossing toward the stolen egg. "
                    + "Defend it, or take the egg back to the lair it came from.",
                    LetterDefOf.ThreatBig, summ);
            }
        }

        private bool GreatBoneAboard(Map map)
        {
            if (map == null || Props.greatBoneDef == null) return false;
            List<Thing> bones = map.listerThings.ThingsOfDef(Props.greatBoneDef);
            for (int i = 0; i < bones.Count; i++)
            {
                Thing b = bones[i];
                if (b.Faction == Faction.OfPlayer && (map.terrainGrid.FoundationAt(b.Position)?.IsSubstructure ?? false)) return true;
            }
            return false;
        }

        private ImprintResult Decide()
        {
            Map m = parent.MapHeld;
            bool players = stolen || HeldByPlayer() || (m != null && m.IsPlayerHome);
            return BroodImprintLogic.Decide(players, GreatBoneAboard(m), true);
        }

        private void Hatch()
        {
            Map map = parent.MapHeld;
            IntVec3 at = parent.PositionHeld;
            if (map == null || Props.hatchKind == null) { progress = 1f; return; }   // waits in a caravan until set down
            ImprintResult r = Decide();
            bool bonded = r == ImprintResult.Bonded;
            Pawn young = PawnGenerator.GeneratePawn(new PawnGenerationRequest(Props.hatchKind, bonded ? Faction.OfPlayer : null,
                PawnGenerationContext.NonPlayer, map.Tile, fixedBiologicalAge: 0f, fixedChronologicalAge: 0f, developmentalStages: DevelopmentalStage.Newborn));
            GenSpawn.Spawn(young, at, map);
            if (bonded && Props.bondedHungerHediff != null)
            {
                Hediff h = young.health.AddHediff(Props.bondedHungerHediff);
                if (h != null) h.Severity = SummBaneLogic.HungerSeverity(RM_AbyssSettings.beastHunger);
            }
            Find.LetterStack.ReceiveLetter(bonded ? "The summing has imprinted" : "The summing hatched wild",
                bonded ? "The egg has split and the summing inside has taken to you, drawn by the great bone aboard the ship. "
                         + "It will be ruinously hungry all its life, it will kill what it finds, and it will never stop growing."
                       : "The egg has split, but the summing will not imprint. " + BroodImprintLogic.WhyNot(r),
                bonded ? LetterDefOf.PositiveEvent : LetterDefOf.NegativeEvent, young);
            parent.Destroy(DestroyMode.Vanish);
        }

        public override string CompInspectStringExtra()
        {
            var sb = new StringBuilder();
            sb.Append("Hatching: ").Append(progress.ToStringPercent());
            if (lairMapId >= 0) sb.Append(stolen ? " (taken from the lair)" : " (in the lair)");
            sb.AppendLine();
            sb.Append(BroodImprintLogic.WhyNot(Decide()));
            return sb.ToString();
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref progress, "progress", 0f);
            Scribe_Values.Look(ref stolen, "stolen", false);
            Scribe_Values.Look(ref lairMapId, "lairMapId", -1);
            Scribe_Values.Look(ref nextStormTick, "nextStormTick", -1);
            Scribe_Values.Look(ref summDueTick, "summDueTick", -1);
        }
    }

    // ── the bonded beast's bane: it kills what it finds ─────────────────────────
    public class CompProperties_RM_SummBane : CompProperties
    {
        public int checkInterval = 2000;
        public float searchRadius = 45f;
        public HediffDef hungerHediff;
        public CompProperties_RM_SummBane() { compClass = typeof(RM_CompSummBane); }
    }

    public class RM_CompSummBane : ThingComp
    {
        private CompProperties_RM_SummBane Props => (CompProperties_RM_SummBane)props;

        public override void CompTick()
        {
            base.CompTick();
            if (!parent.IsHashIntervalTick(Props.checkInterval)) return;
            if (!(parent is Pawn p) || !p.Spawned || p.Dead || p.Downed || p.Faction != Faction.OfPlayer) return;

            // keep the hunger in step with the slider
            if (Props.hungerHediff != null)
            {
                Hediff h = p.health.hediffSet.GetFirstHediffOfDef(Props.hungerHediff) ?? p.health.AddHediff(Props.hungerHediff);
                if (h != null) h.Severity = SummBaneLogic.HungerSeverity(RM_AbyssSettings.beastHunger);
            }

            if (!RM_AbyssSettings.baneEnabled || p.Drafted || p.InMentalState) return;
            if (p.CurJobDef == JobDefOf.AttackMelee || p.CurJobDef == JobDefOf.Ingest || p.CurJobDef == JobDefOf.PredatorHunt) return;
            float food = p.needs?.food?.CurLevelPercentage ?? 1f;
            if (!SummBaneLogic.ShouldHunt(food, Rand.Value)) return;

            var wild = new List<Pawn>();
            var tame = new List<Pawn>();
            IReadOnlyList<Pawn> all = p.Map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < all.Count; i++)
            {
                Pawn o = all[i];
                if (o == p || o.Dead || !o.RaceProps.Animal || o.def == p.def) continue;
                if (!o.Position.InHorDistOf(p.Position, Props.searchRadius) || !p.CanReach(o, PathEndMode.Touch, Danger.Deadly)) continue;
                if (o.Faction == null) wild.Add(o);
                else if (o.Faction == Faction.OfPlayer) tame.Add(o);
            }
            int kind = SummBaneLogic.PickVictimKind(wild.Count, tame.Count, Rand.Value);
            if (kind < 0) return;
            Pawn victim = (kind == 0 ? wild : tame).RandomElement();
            Job job = JobMaker.MakeJob(JobDefOf.AttackMelee, victim);
            job.killIncappedTarget = true;
            job.expiryInterval = 5000;
            p.jobs.StartJob(job, JobCondition.InterruptForced);
            if (kind == 1)
                Messages.Message(p.LabelShort + " has turned on " + victim.LabelShort + ". The summ kills what it finds.", new LookTargets(p), MessageTypeDefOf.NegativeEvent);
        }
    }
}
