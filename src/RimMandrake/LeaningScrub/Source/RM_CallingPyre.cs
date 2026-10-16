using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;
using Verse.AI.Group;

namespace RimMandrake.LeaningScrub
{
    // ════════════════════════════════════════════════════════════════════
    // LEANINGSCRUB_MECHANICS_BUILD_1 part 5, second half — the calling-pyre.
    //
    // "The calling-pyre Ideology ritual torches your own fields to bring the herds down on all who remain (precept
    // variants forbidden/last-rite/venerated). Fire implies folly."
    // Rulings: Q7 (card 2026-10-15, "Ritual plus all three beliefs"); N3 (card, asked twice, FINAL: "Only fire- and
    // ritual-themed ones" offer it — PreceptDef.requiredMemes, any-of, read from IdeoFoundation.HasRequiredMemes).
    //
    // Pieces (Defs/Ideology/RM_CallingPyre.xml):
    //   IssueDef RM_CallingPyre + three belief precepts. Forbidden: the rite cannot be started and believers are
    //     shaken when anyone calls the herds. Last rite: only with enemies on the map. Venerated: any time, and
    //     believers are uplifted when it is done.
    //   PreceptDef RM_Ritual_CallingPyre (Precept_Ritual) -> RitualPatternDef -> this file's behaviour worker (the gate)
    //     and outcome worker (the fire and the herd).
    // The outcome sets FireCount fires on plants near the ritual spot, the colony's growing zones first; every tier
    // clears the fire-stamp threshold, so RM_MapComponent_FireStamp sends the giants already on the map. Then
    // HerdCount giants walk in from the edge; RagingCount of them come in manhunting (they fall on everyone, the
    // clan included), the rest go for the fire. A world with no stamper creature loaded calls no herd (said in the
    // letter). Numbers PROVISIONAL (RM_PyreKernel).
    // Gate: modEnabled && callingPyreEnabled (off: the rite cannot be started; precepts stay, inert).
    // Not built: the Jawa-faith "charred stake ring found only in the Gale" discovery (biome_rites_pass §7.1) — N3
    // made the precept a fire/ritual-meme belief, not a found rite; recorded on the item.
    // ════════════════════════════════════════════════════════════════════
    [DefOf]
    public static class RM_CallingPyreDefOf
    {
        public static PreceptDef RM_CallingPyre_Forbidden;
        public static PreceptDef RM_CallingPyre_LastRite;
        public static PreceptDef RM_CallingPyre_Venerated;
        public static HistoryEventDef RM_CalledTheHerds;

        static RM_CallingPyreDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_CallingPyreDefOf));
        }
    }

    public static class RM_CallingPyre
    {
        public static int Belief(Ideo ideo)
        {
            if (ideo == null) return RM_PyreKernel.BeliefNone;
            if (ideo.HasPrecept(RM_CallingPyreDefOf.RM_CallingPyre_Forbidden)) return RM_PyreKernel.BeliefForbidden;
            if (ideo.HasPrecept(RM_CallingPyreDefOf.RM_CallingPyre_LastRite)) return RM_PyreKernel.BeliefLastRite;
            if (ideo.HasPrecept(RM_CallingPyreDefOf.RM_CallingPyre_Venerated)) return RM_PyreKernel.BeliefVenerated;
            return RM_PyreKernel.BeliefNone;
        }

        public static string Explain(string reason)
        {
            switch (reason)
            {
                case RM_PyreKernel.ReasonOff: return "The calling-pyre is turned off in Mod Settings (Leaning Scrub).";
                case RM_PyreKernel.ReasonForbidden: return "Calling the herds with fire is forbidden by this belief.";
                case RM_PyreKernel.ReasonNoEnemies: return "A last rite: it can only be called with enemies on the map.";
                default: return null;
            }
        }

        public static string GateFor(Ideo ideo, Map map)
        {
            int hostiles = map != null && GenHostility.AnyHostileActiveThreatToPlayer(map) ? 1 : 0;
            return RM_PyreKernel.Gate(RM_WindCalendar.On(RM_LeaningScrubSettings.callingPyreEnabled), Belief(ideo), hostiles);
        }

        public static PawnKindDef StamperKind()
        {
            var found = new List<PawnKindDef>();
            List<PawnKindDef> all = DefDatabase<PawnKindDef>.AllDefsListForReading;
            for (int i = 0; i < all.Count; i++)
            {
                PawnKindDef k = all[i];
                if (k.race != null && k.RaceProps != null && k.RaceProps.Animal && RM_MapComponent_FireStamp.IsStamperDef(k.race))
                {
                    found.Add(k);
                }
            }
            return found.Count == 0 ? null : found.RandomElement();
        }

        /// <summary>Light up to <paramref name="want"/> fires on plants around <paramref name="center"/>, the
        /// player's growing zones first. Returns how many caught.</summary>
        public static int Ignite(Map map, IntVec3 center, float radius, int want, Thing instigator)
        {
            var zoned = new List<IntVec3>();
            var wild = new List<IntVec3>();
            foreach (IntVec3 c in GenRadial.RadialCellsAround(center, radius, true))
            {
                if (!c.InBounds(map) || c.Roofed(map) || c.GetPlant(map) == null) continue;
                if (map.thingGrid.ThingAt(c, ThingDefOf.Fire) != null) continue;
                if (c.GetZone(map) is Zone_Growing) zoned.Add(c); else wild.Add(c);
            }
            // Nearest first (zones before wild plants at each distance band) so the fires stay clustered: the fire-stamp
            // only counts open fires within ClusterRadius of one another. A light shuffle inside each list breaks ties.
            zoned.Shuffle();
            wild.Shuffle();
            zoned.SortBy(c => c.DistanceToSquared(center));
            wild.SortBy(c => c.DistanceToSquared(center));
            if (zoned.Count < want)
            {
                zoned.AddRange(wild);
            }
            int lit = 0;
            for (int i = 0; i < zoned.Count && lit < want; i++)
            {
                if (FireUtility.TryStartFireIn(zoned[i], map, 0.6f, instigator)) lit++;
            }
            return lit;
        }

        /// <summary>Walk <paramref name="count"/> giants in from the edge; <paramref name="raging"/> of them manhunting.
        /// Returns the pawns spawned.</summary>
        public static List<Pawn> CallHerd(Map map, PawnKindDef kind, int count, int raging, List<Pawn> made = null)
        {
            made = made ?? new List<Pawn>();
            if (kind == null || count <= 0) return made;
            if (!RCellFinder.TryFindRandomPawnEntryCell(out IntVec3 entry, map, 0f)) return made;
            for (int i = 0; i < count; i++)
            {
                IntVec3 at = CellFinder.RandomClosewalkCellNear(entry, map, 6);
                Pawn p = PawnGenerator.GeneratePawn(kind);
                GenSpawn.Spawn(p, at, map);
                made.Add(p);
                if (i < raging)
                {
                    p.mindState.mentalStateHandler.TryStartMentalState(MentalStateDefOf.Manhunter, "the calling-pyre", forced: true);
                }
            }
            return made;
        }
    }

    public class RM_RitualBehaviorWorker_CallingPyre : RitualBehaviorWorker
    {
        public RM_RitualBehaviorWorker_CallingPyre()
        {
        }

        public RM_RitualBehaviorWorker_CallingPyre(RitualBehaviorDef def) : base(def)
        {
        }

        public override string CanStartRitualNow(TargetInfo target, Precept_Ritual ritual, Pawn selectedPawn = null, Dictionary<string, Pawn> forcedForRole = null)
        {
            string reason = RM_CallingPyre.GateFor(ritual?.ideo, target.Map);
            if (reason != RM_PyreKernel.Ok)
            {
                return RM_CallingPyre.Explain(reason);
            }
            return base.CanStartRitualNow(target, ritual, selectedPawn, forcedForRole);
        }
    }

    public class RM_RitualOutcomeEffectWorker_CallingPyre : RitualOutcomeEffectWorker_FromQuality
    {
        public RM_RitualOutcomeEffectWorker_CallingPyre()
        {
        }

        public RM_RitualOutcomeEffectWorker_CallingPyre(RitualOutcomeEffectDef def) : base(def)
        {
        }

        protected override void ApplyExtraOutcome(Dictionary<Pawn, int> totalPresence, LordJob_Ritual jobRitual, RitualOutcomePossibility outcome, out string extraOutcomeDesc, ref LookTargets letterLookTargets)
        {
            extraOutcomeDesc = null;
            Map map = jobRitual.Map;
            if (map == null || !RM_WindCalendar.On(RM_LeaningScrubSettings.callingPyreEnabled))
            {
                return;
            }
            int tier = def.outcomeChances.IndexOf(outcome);
            // The rite has no speaker role, so the organizer can be null: the first participant lights it then (the
            // history event needs a doer of the colony's faction for the belief thoughts to land).
            Pawn organizer = jobRitual.Organizer;
            if (organizer == null)
            {
                foreach (Pawn p in totalPresence.Keys) { organizer = p; break; }
            }
            IntVec3 center = jobRitual.selectedTarget.Cell;
            int lit = RM_CallingPyre.Ignite(map, center, RM_LeaningScrubSettings.callingPyreRadius, RM_PyreKernel.FireCount(tier), organizer);
            PawnKindDef kind = RM_CallingPyre.StamperKind();
            int herd = RM_PyreKernel.HerdCount(tier, RM_LeaningScrubSettings.callingPyreHerdFactor);
            int raging = RM_PyreKernel.RagingCount(tier, herd);
            List<Pawn> came = RM_CallingPyre.CallHerd(map, kind, herd, raging);
            map.GetComponent<RM_MapComponent_FireStamp>()?.ConvergePass(sendMessage: false);
            if (organizer != null)
            {
                Find.HistoryEventsManager.RecordEvent(new HistoryEvent(RM_CallingPyreDefOf.RM_CalledTheHerds, organizer.Named(HistoryEventArgsNames.Doer)));
            }
            string thin = lit < RM_MapComponent_FireStamp.MinOpenFires ? " Too little caught to draw the giants already on the map." : "";
            if (came.Count > 0)
            {
                letterLookTargets = new LookTargets(came[0]);
                extraOutcomeDesc = string.Format("{0} fires were set. {1} {2} came in from the edge of the map, {3} of them raging at everyone in their path.{4}",
                    lit, came.Count, came.Count == 1 ? kind.label : kind.GetLabelPlural(), raging, thin);
            }
            else
            {
                extraOutcomeDesc = string.Format("{0} fires were set, but no herd on this world answered the call.{1}", lit, thin);
            }
        }
    }

    // Proof hook for jawa/static_call (validation.py chain "pyre"). Modes:
    //   defs  the three beliefs and the ritual are loaded and each is gated on the Ritualist meme (N3);
    //   fire  the SHIPPED Ignite lights at least the fire-stamp threshold on a fuzz patch, and CallHerd walks the
    //         stamper kind in (UNMEASURED when no stamper creature is loaded); everything made is removed;
    //   off   with callingPyreEnabled off the gate refuses the player's ideoligion.
    public static class RM_CallingPyreProof
    {
        public static string ProofPyre(string mode)
        {
            if (mode == "defs")
            {
                var bad = new List<string>();
                foreach (PreceptDef d in new[] { RM_CallingPyreDefOf.RM_CallingPyre_Forbidden, RM_CallingPyreDefOf.RM_CallingPyre_LastRite,
                    RM_CallingPyreDefOf.RM_CallingPyre_Venerated, DefDatabase<PreceptDef>.GetNamedSilentFail("RM_Ritual_CallingPyre") })
                {
                    if (d == null) { bad.Add("missing precept"); continue; }
                    if (d.requiredMemes.NullOrEmpty() || !d.requiredMemes.Exists(m => m.defName == "Ritualist")) bad.Add(d.defName + " not gated on Ritualist");
                }
                return bad.Count == 0 ? "PASS defs: 3 beliefs + ritual, all gated on the ritual/fire memes" : "FAIL: " + string.Join("; ", bad);
            }
            Map map = Find.CurrentMap;
            if (map == null) return "UNMEASURED: no current map";
            bool savedMod = RM_LeaningScrubSettings.modEnabled, savedPyre = RM_LeaningScrubSettings.callingPyreEnabled;
            var herd = new List<Pawn>();
            try
            {
                RM_LeaningScrubSettings.modEnabled = true;
                if (mode == "off")
                {
                    RM_LeaningScrubSettings.callingPyreEnabled = false;
                    string r = RM_CallingPyre.GateFor(Faction.OfPlayer?.ideos?.PrimaryIdeo, map);
                    return r == RM_PyreKernel.ReasonOff ? "PASS off: gate refuses" : "FAIL: callingPyreEnabled off but the gate said " + (r ?? "ok");
                }
                RM_LeaningScrubSettings.callingPyreEnabled = true;
                IntVec3 spot = IntVec3.Invalid;
                foreach (Thing t in map.listerThings.ThingsInGroup(ThingRequestGroup.Plant))
                {
                    if (t.def.GetModExtension<RM_RippleCoverExtension>() != null && !t.Position.Roofed(map) && t.Position.DistanceToEdge(map) > 20) { spot = t.Position; break; }
                }
                if (!spot.IsValid) return "UNMEASURED: no unroofed fuzz on this map";
                int lit = RM_CallingPyre.Ignite(map, spot, 6f, RM_PyreKernel.FireCount(0), null);
                foreach (Thing f in new List<Thing>(map.listerThings.ThingsOfDef(ThingDefOf.Fire)))
                {
                    if (!f.Destroyed && f.Position.InHorDistOf(spot, 30f)) f.Destroy();
                }
                PawnKindDef kind = RM_CallingPyre.StamperKind();
                int came = -1, raging = 0;
                if (kind != null)
                {
                    RM_CallingPyre.CallHerd(map, kind, 3, 1, herd);
                    came = herd.Count;
                    foreach (Pawn p in herd) { if (p.InMentalState) raging++; }
                }
                string st = string.Format("lit={0} came={1} raging={2}", lit, came, raging);
                if (lit < RM_MapComponent_FireStamp.MinOpenFires) return "FAIL: the pyre lit fewer fires than the stamp threshold " + st;
                if (kind == null) return "UNMEASURED: fires PASS but no stamper creature is loaded " + st;
                if (came != 3 || raging != 1) return "FAIL: the herd did not come as called " + st;
                return "PASS " + st;
            }
            finally
            {
                foreach (Pawn p in herd) { if (!p.Destroyed) p.Destroy(); }
                RM_LeaningScrubSettings.modEnabled = savedMod;
                RM_LeaningScrubSettings.callingPyreEnabled = savedPyre;
            }
        }
    }
}
