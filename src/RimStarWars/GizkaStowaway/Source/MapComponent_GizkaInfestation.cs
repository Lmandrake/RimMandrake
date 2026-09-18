using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.StarWars.GizkaStowaway
{
    public enum GizkaStage
    {
        None = 0,
        Cute = 1,
        Underfoot = 2,
        Infestation = 3,
        Plague = 4
    }

    /// <summary>
    /// GIZKA_TRIBBLE_ADAPTATION_1, draft §2 — the escalation, and the contract
    /// that makes it fair.
    ///
    /// "Stage letters are the contract: every stage boundary announces itself
    /// BEFORE its cost lands." That is the whole reason this component exists
    /// as a separate thing from the breeding comp. The breeding comp makes the
    /// population; this watches it cross a line and tells the player, in
    /// plain words, what is about to start costing them — and then starts it.
    /// No stage skips a letter, and venting or culling back below a band steps
    /// the stage down again so the warning can be re-earned.
    ///
    /// Stage bands are FRACTIONS of the Mod Settings population cap, not fixed
    /// counts. A player who slides the cap to 8 would otherwise never see the
    /// Infestation stage at all, and a player who slides it to 80 would spend
    /// the first sixty gizka in "Cute".
    ///
    /// The chewing mechanic rides the vanilla breakdown system rather than
    /// replacing it: CompBreakdownable.DoBreakdown() is public, the building
    /// genuinely breaks down, the vanilla repair job fixes it, and the only
    /// thing this mod adds is a second cause and a letter that NAMES that
    /// cause. CompBreakdownable's own MTB is a private const (13,680,000 ticks)
    /// and is not reachable, which is why the cadence below is our own number
    /// applied on top rather than a modifier to theirs.
    /// </summary>
    public class MapComponent_GizkaInfestation : MapComponent
    {
        private GizkaStage lastStage = GizkaStage.None;
        private int lastChewLetterTick = -999999;

        private const int CheckIntervalTicks = 2000;
        private const int ChewLetterCooldownTicks = 60000;   // one day

        // Mean ticks between one gizka chewing through one powered building it
        // shares a room with. Many gizka in one room compound this linearly,
        // which is how a Plague stage in a workshop feels different from an
        // Infestation stage in a barn.
        private const float ChewMtbTicksPerGizka = 900000f;

        public MapComponent_GizkaInfestation(Map map) : base(map) { }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref lastStage, "lastStage", GizkaStage.None);
            Scribe_Values.Look(ref lastChewLetterTick, "lastChewLetterTick", -999999);
        }

        public override void MapComponentTick()
        {
            base.MapComponentTick();
            if (Find.TickManager.TicksGame % CheckIntervalTicks != 0) return;

            RSW_GizkaSettings s = RSW_GizkaStowawayMod.Settings;
            if (s == null || !s.stowawayEventsEnabled) return;
            if (RSW_GizkaPopulation.Kind == null) return;

            List<Pawn> gizka = RSW_GizkaPopulation.ListOnMap(map);
            GizkaStage stage = StageFor(gizka.Count, s.populationCap);

            if (stage != lastStage)
            {
                if (stage > lastStage) AnnounceStage(stage, gizka.Count);
                lastStage = stage;
            }

            if (s.chewingEnabled && stage >= GizkaStage.Infestation)
            {
                DoChewing(gizka);
            }
        }

        public static GizkaStage StageFor(int count, int cap)
        {
            if (count <= 0) return GizkaStage.None;
            if (cap < 4) cap = 4;
            if (count >= Mathf.Max(6, Mathf.RoundToInt(cap * 0.72f))) return GizkaStage.Plague;
            if (count >= Mathf.Max(4, Mathf.RoundToInt(cap * 0.32f))) return GizkaStage.Infestation;
            if (count >= Mathf.Max(3, Mathf.RoundToInt(cap * 0.14f))) return GizkaStage.Underfoot;
            return GizkaStage.Cute;
        }

        private void AnnounceStage(GizkaStage stage, int count)
        {
            string label;
            string text;
            LetterDef def;

            switch (stage)
            {
                case GizkaStage.Underfoot:
                    label = "Gizka underfoot";
                    text = "There are " + count + " of them now.\n\nNobody has counted before because nobody thought counting would be necessary. They are in the stores, in the corridors, and under at least one bed. Food is going missing at a rate that is not yet alarming and is no longer nothing.\n\nThis is the last stage at which they are only a nuisance. If they are still here at roughly triple this number, they will start chewing wiring.";
                    def = LetterDefOf.NeutralEvent;
                    break;

                case GizkaStage.Infestation:
                    label = "Gizka infestation";
                    text = "There are " + count + " of them.\n\nThey have started on the wiring. Anything powered that shares a room with them will break down early, and the breakdown report will say so by name. Food stores are being raided in earnest.\n\nEvery way out of this is still open and every one of them costs something: cull them, sell them onward, bait them, or drop the temperature in the rooms they live in below what they will breed at. Doing nothing is also a choice, and it has a ceiling — they will stop multiplying when the place is full.";
                    def = LetterDefOf.NegativeEvent;
                    break;

                case GizkaStage.Plague:
                    label = "Gizka plague";
                    text = "There are " + count + " of them, and the number has stopped climbing — not because anything was done, but because there is no more room.\n\nYou can hear them through the walls. The floors are filthy, the wiring is a running repair job, and the food stores are a shared resource now.\n\nThis is the ceiling. It gets no worse on its own, and it gets no better on its own either. The exits have not changed: the knife, the market, the bait, or the cold.";
                    def = LetterDefOf.NegativeEvent;
                    break;

                default:
                    return;
            }

            Find.LetterStack.ReceiveLetter(label, text, def, GizkaLookTarget());
        }

        private LookTargets GizkaLookTarget()
        {
            List<Pawn> list = RSW_GizkaPopulation.ListOnMap(map);
            if (list.Count > 0) return new LookTargets(list[0]);
            return LookTargets.Invalid;
        }

        private void DoChewing(List<Pawn> gizka)
        {
            if (gizka.Count == 0) return;

            // Count gizka per room once, then walk the colonist buildings once.
            Dictionary<Room, int> perRoom = new Dictionary<Room, int>();
            for (int i = 0; i < gizka.Count; i++)
            {
                Room r = gizka[i].GetRoom();
                if (r == null || r.UsesOutdoorTemperature) continue;   // outdoors: nothing to chew
                perRoom.TryGetValue(r, out int n);
                perRoom[r] = n + 1;
            }
            if (perRoom.Count == 0) return;

            List<Building> buildings = map.listerBuildings.allBuildingsColonist;
            for (int i = 0; i < buildings.Count; i++)
            {
                Building b = buildings[i];
                CompBreakdownable brk = b.GetComp<CompBreakdownable>();
                if (brk == null || brk.BrokenDown) continue;

                CompPowerTrader power = b.GetComp<CompPowerTrader>();
                if (power == null || !power.PowerOn) continue;

                Room room = b.GetRoom();
                if (room == null || !perRoom.TryGetValue(room, out int here) || here <= 0) continue;

                if (!Rand.MTBEventOccurs(ChewMtbTicksPerGizka / here, 1f, CheckIntervalTicks)) continue;

                brk.DoBreakdown();

                if (Find.TickManager.TicksGame - lastChewLetterTick >= ChewLetterCooldownTicks)
                {
                    lastChewLetterTick = Find.TickManager.TicksGame;
                    Find.LetterStack.ReceiveLetter(
                        "Gizka-chewed: " + b.LabelCap,
                        b.LabelCap + " has broken down. The insulation is stripped off the leads in a way nothing on this map does except gizka.\n\nIt can be repaired like any other breakdown. It will happen again while they are living in that room.",
                        LetterDefOf.NegativeEvent,
                        new LookTargets(b));
                }
                return;   // at most one chewed building per check, on purpose
            }
        }
    }
}
