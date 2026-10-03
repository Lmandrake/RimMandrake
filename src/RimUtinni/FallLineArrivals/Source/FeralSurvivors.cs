using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;
using Verse.AI.Group;

namespace RimMandrake.Utinni.FallLineArrivals
{
    // ════════════════════════════════════════════════════════════════════
    // FALL_LINE_FERAL_SURVIVORS_BUILD_1 — Band B (spec §5, §8, §10;
    // design/RimUtinni/fall_line_arrival_mechanism_spec.md).
    //
    // fall_line.md §8b: survivors of the falls gone feral, "wily, flee-prone"; the wreckage
    // is the cover they break for. One droid per event, factionless for life, a flat weighted
    // pick (every Droidworks utility kind carries the combatPower 99999 sentinel).
    //
    //   RUT_Hediff_Feral       the flag. Survives save/load; removes itself the moment the
    //                          pawn joins the player (the wild data-spike recruits it), so
    //                          "restoration is clean" holds by construction (§5.3).
    //   RUT_FeralDroidInsert   Humanlike_PreMain splice gated on the hediff (XML), then:
    //   JobGiver_FeralFlee     a player pawn within 18 cells -> break for a wreck away from it,
    //                          else FleeUtility.FleeJob; no flee cell = cornered -> fight.
    //   JobGiver_FeralLurk     otherwise loiter near the nearest wreck; at night, hold still.
    //   RUT_CompFeralLurker    on the wrecks: a share of landed wrecks hide one; it bolts the
    //                          first time a colonist comes within 25 cells (never at impact).
    //   IncidentWorker_FallSurvivor  the drift-in route from the map edge.
    // Every pawn here is species-agnostic: the feral-races item reuses the flee/lurk pieces.
    // ════════════════════════════════════════════════════════════════════

    public class FeralOption
    {
        public PawnKindDef kind;
        public float weight = 1f;
        /// <summary>The one dangerous pull; gated by its own Mod Setting.</summary>
        public bool dangerous;
    }

    /// <summary>The Band B pool, as data on RUT_FallSurvivor (plain &lt;li&gt; class, never PawnGenOption).</summary>
    public class FeralPoolExtension : DefModExtension
    {
        public List<FeralOption> options = new List<FeralOption>();
    }

    public static class FeralSurvivors
    {
        public const float ThreatRadius = 18f;
        public const int FleeDistance = 24;
        public const float WreckSearchRadius = 40f;

        private static HediffDef feral;
        private static IncidentDef survivorIncident;

        public static HediffDef FeralHediff =>
            feral ?? (feral = DefDatabase<HediffDef>.GetNamedSilentFail("RUT_Hediff_Feral"));

        private static IncidentDef SurvivorIncident =>
            survivorIncident ?? (survivorIncident = DefDatabase<IncidentDef>.GetNamedSilentFail("RUT_FallSurvivor"));

        public static bool IsFeral(Pawn p) =>
            p != null && FeralHediff != null && p.health?.hediffSet?.HasHediff(FeralHediff) == true;

        public static int FeralCount(Map map)
        {
            if (map == null)
            {
                return 0;
            }
            int n = 0;
            foreach (Pawn p in map.mapPawns.AllPawnsSpawned)
            {
                if (!p.Dead && p.Faction == null && IsFeral(p))
                {
                    n++;
                }
            }
            return n;
        }

        public static bool RoomForOne(Map map) => FeralCount(map) < Mathf.Max(1, FallLineArrivalsSettings.maxFeralPerMap);

        public static PawnKindDef PickKind()
        {
            FeralPoolExtension ext = SurvivorIncident?.GetModExtension<FeralPoolExtension>();
            if (ext == null)
            {
                return null;
            }
            List<FeralOption> legal = ext.options
                .Where(o => o?.kind != null && o.weight > 0f && (!o.dangerous || FallLineArrivalsSettings.allowDestroyer))
                .ToList();
            return legal.Count == 0 ? null : legal.RandomElementByWeight(o => o.weight).kind;
        }

        /// <summary>A wreck a feral survivor uses as cover: ours, or any mech ship chunk.</summary>
        public static bool IsWreck(Thing t) =>
            t?.def != null && (t.def.defName.StartsWith("RUT_FallWreck_") || t.def.defName == "ShipChunk_Mech");

        public static Thing NearestWreck(Pawn pawn, float radius, System.Predicate<Thing> extra = null)
        {
            Thing best = null;
            float bestD = radius * radius;
            foreach (Building b in pawn.Map.listerBuildings.allBuildingsNonColonist)
            {
                if (!IsWreck(b))
                {
                    continue;
                }
                float d = (b.Position - pawn.Position).LengthHorizontalSquared;
                if (d < bestD && (extra == null || extra(b)) && pawn.CanReach(b, PathEndMode.Touch, Danger.Deadly))
                {
                    bestD = d;
                    best = b;
                }
            }
            return best;
        }

        /// <summary>Generate one factionless survivor at `cell`, flag it, send the letter. Null when it could not.</summary>
        public static Pawn SpawnSurvivor(Map map, IntVec3 cell, PawnKindDef kind, bool fromWreck, LetterDef letter = null)
        {
            if (map == null || kind == null)
            {
                return null;
            }
            Pawn droid = PawnGenerator.GeneratePawn(new PawnGenerationRequest(
                kind, null, PawnGenerationContext.NonPlayer, map.Tile,
                forceGenerateNewPawn: true, allowDead: false, allowDowned: false,
                canGeneratePawnRelations: false, mustBeCapableOfViolence: false,
                colonistRelationChanceFactor: 0f, forceAddFreeWarmLayerIfNeeded: false,
                allowGay: true, allowPregnant: false, allowFood: false, allowAddictions: false));
            IntVec3 loc = CellFinder.RandomClosewalkCellNear(cell, map, fromWreck ? 2 : 6);
            GenSpawn.Spawn(droid, loc, map);
            // The hediff always goes on (it is the per-map count and the clean-wipe flag); the
            // "attack like a wild droid" setting adds the wild droid's permanent manhunt on top,
            // whose think subtree outranks the flee/lurk splice.
            if (FeralHediff != null)
            {
                droid.health.AddHediff(FeralHediff);
            }
            bool attack = FallLineArrivalsSettings.feralAttackInstead;
            if (attack)
            {
                droid.mindState.mentalStateHandler.TryStartMentalState(MentalStateDefOf.ManhunterPermanent,
                    "out on the Fall Line too long", forced: true, forceWake: true, transitionSilently: true);
            }
            string what = droid.KindLabel;
            string text = fromWreck
                ? "Something mechanical has broken from under the wreck and is running: a " + what + ", scoured to bare "
                  + "metal, that has been living in the wreckage since it came down.\n\n"
                : "A " + what + " has drifted in off the flats. It has been out on the Fall Line a long time, alone, "
                  + "and it belongs to no one.\n\n";
            text += attack
                ? "It will attack anything it sees."
                : "It will not come to you. It runs from people and hides in wreckage, and it fights only when cornered. "
                  + "Bring it down without wrecking it, take it prisoner, and a wild-keyed data spike will wipe it clean.";
            Find.LetterStack.ReceiveLetter(fromWreck ? "Feral droid breaks cover" : "Feral droid", text,
                letter ?? (attack ? LetterDefOf.ThreatSmall : LetterDefOf.NeutralEvent), droid);
            return droid;
        }

        /// <summary>Nearest spawned, undowned player pawn within `radius` that can see or reach the feral.</summary>
        public static Pawn NearestThreat(Pawn pawn, float radius)
        {
            Pawn best = null;
            float bestD = radius * radius;
            foreach (Pawn p in pawn.Map.mapPawns.SpawnedPawnsInFaction(Faction.OfPlayer))
            {
                if (p == pawn || p.Downed || p.Dead)
                {
                    continue;
                }
                float d = (p.Position - pawn.Position).LengthHorizontalSquared;
                if (d < bestD)
                {
                    bestD = d;
                    best = p;
                }
            }
            return best;
        }

        /// <summary>
        /// Bridge proof (jawa/static_call): spawn one survivor from the pool beside `cell` on `map`
        /// as the lurker route would (fromWreck), returning "SPAWNED id kind" or "REFUSED: why".
        /// </summary>
        public static string ProofSpawnSurvivor(Map map, IntVec3 cell)
        {
            if (!FallLineArrivalsSettings.survivorsEnabled)
            {
                return "REFUSED: survivors are off";
            }
            if (!RoomForOne(map))
            {
                return "REFUSED: map already holds " + FeralCount(map) + " feral droids";
            }
            PawnKindDef kind = PickKind();
            if (kind == null)
            {
                return "REFUSED: empty pool (Droidworks absent?)";
            }
            Pawn p = SpawnSurvivor(map, cell, kind, true);
            return p == null ? "REFUSED: spawn failed" : "SPAWNED " + p.ThingID + " " + kind.defName;
        }
    }

    // ── the hediff's self-removal: joining the player ends feral ─────────
    public class HediffCompProperties_FeralClears : HediffCompProperties
    {
        public HediffCompProperties_FeralClears()
        {
            compClass = typeof(HediffComp_FeralClears);
        }
    }

    public class HediffComp_FeralClears : HediffComp
    {
        public override void CompPostTickInterval(ref float severityAdjustment, int delta)
        {
            base.CompPostTickInterval(ref severityAdjustment, delta);
            if (Pawn.Faction == Faction.OfPlayer && Pawn.IsHashIntervalTick(250, delta))
            {
                Pawn.health.RemoveHediff(parent);
            }
        }
    }

    // ── think tree ──────────────────────────────────────────────────────
    /// <summary>Feral and free: flagged, factionless, not a prisoner, not downed, no lord.</summary>
    public class ThinkNode_ConditionalFeralFree : ThinkNode_Conditional
    {
        protected override bool Satisfied(Pawn pawn)
        {
            return pawn.Spawned && pawn.Faction == null && !pawn.IsPrisoner && !pawn.Downed
                && pawn.GetLord() == null && FeralSurvivors.IsFeral(pawn);
        }
    }

    public class JobGiver_FeralFlee : ThinkNode_JobGiver
    {
        protected override Job TryGiveJob(Pawn pawn)
        {
            Pawn threat = FeralSurvivors.NearestThreat(pawn, FeralSurvivors.ThreatRadius);
            if (threat == null)
            {
                return null;
            }
            if (pawn.CurJobDef == JobDefOf.Flee && pawn.CurJob?.targetB.Thing == threat)
            {
                return null;
            }
            // Cover first: a wreck farther from the threat than we are, reachable.
            float myD = (pawn.Position - threat.Position).LengthHorizontalSquared;
            Thing cover = FeralSurvivors.NearestWreck(pawn, FeralSurvivors.WreckSearchRadius,
                w => (w.Position - threat.Position).LengthHorizontalSquared > myD + 16f);
            if (cover != null && CellFinder.TryFindRandomReachableNearbyCell(cover.Position, pawn.Map, 3f,
                    TraverseParms.For(pawn), c => c.Standable(pawn.Map) && c != pawn.Position, null, out IntVec3 hide))
            {
                Job toCover = JobMaker.MakeJob(JobDefOf.Flee, hide, threat);
                toCover.locomotionUrgency = LocomotionUrgency.Sprint;
                return toCover;
            }
            Job flee = FleeUtility.FleeJob(pawn, threat, FeralSurvivors.FleeDistance);
            if (flee != null)
            {
                return flee;
            }
            // Cornered: the only time it fights.
            if (pawn.Position.InHorDistOf(threat.Position, 4f))
            {
                Job fight = JobMaker.MakeJob(JobDefOf.AttackMelee, threat);
                fight.killIncappedTarget = false;
                fight.expiryInterval = 600;
                return fight;
            }
            return null;
        }
    }

    public class JobGiver_FeralLurk : ThinkNode_JobGiver
    {
        protected override Job TryGiveJob(Pawn pawn)
        {
            Thing wreck = FeralSurvivors.NearestWreck(pawn, FeralSurvivors.WreckSearchRadius);
            if (wreck == null)
            {
                return null;                                  // the tree's own wander takes it
            }
            float hour = GenLocalDate.DayPercent(pawn) * 24f;
            bool night = hour < 5f || hour > 21f;
            if (night && pawn.Position.InHorDistOf(wreck.Position, 3f))
            {
                Job still = JobMaker.MakeJob(JobDefOf.Wait, 600);
                still.checkOverrideOnExpire = true;
                return still;
            }
            if (!CellFinder.TryFindRandomReachableNearbyCell(wreck.Position, pawn.Map, night ? 2f : 6f,
                    TraverseParms.For(pawn), c => c.Standable(pawn.Map), null, out IntVec3 spot))
            {
                return null;
            }
            Job go = JobMaker.MakeJob(JobDefOf.GotoWander, spot);
            go.locomotionUrgency = LocomotionUrgency.Amble;
            go.expiryInterval = 1200;
            go.checkOverrideOnExpire = true;
            return go;
        }
    }

    // ── the wreck that hides one ────────────────────────────────────────
    public class RUT_CompProperties_FeralLurker : CompProperties
    {
        public float triggerRadius = 25f;

        public RUT_CompProperties_FeralLurker()
        {
            compClass = typeof(RUT_CompFeralLurker);
        }
    }

    public class RUT_CompFeralLurker : ThingComp
    {
        private bool armed;
        private bool rolled;

        public RUT_CompProperties_FeralLurker Props => (RUT_CompProperties_FeralLurker)props;

        public bool Armed => armed;

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            if (!rolled)
            {
                rolled = true;
                armed = FallLineArrivalsSettings.survivorsEnabled
                    && Rand.Chance(Mathf.Clamp01(FallLineArrivalsSettings.wreckLurkerChance));
            }
        }

        /// <summary>Dev/bridge: arm this wreck regardless of the roll.</summary>
        public void Arm()
        {
            rolled = true;
            armed = true;
        }

        public override void CompTick()
        {
            base.CompTick();
            if (!armed || !parent.Spawned || !parent.IsHashIntervalTick(250))
            {
                return;
            }
            if (!FallLineArrivalsSettings.survivorsEnabled)
            {
                return;
            }
            Pawn seen = null;
            foreach (Pawn p in parent.Map.mapPawns.FreeColonistsSpawned)
            {
                if (!p.Downed && p.Position.InHorDistOf(parent.Position, Props.triggerRadius))
                {
                    seen = p;
                    break;
                }
            }
            if (seen == null || !FeralSurvivors.RoomForOne(parent.Map))
            {
                return;
            }
            PawnKindDef kind = FeralSurvivors.PickKind();
            armed = false;
            FeralSurvivors.SpawnSurvivor(parent.Map, parent.Position, kind, true);
        }

        public override string CompInspectStringExtra()
        {
            return DebugSettings.godMode && armed ? "Something is hiding under it (dev)." : null;
        }

        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            if (DebugSettings.godMode && !armed)
            {
                yield return new Command_Action
                {
                    defaultLabel = "DEV: hide a feral droid",
                    action = Arm,
                };
            }
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref armed, "rutFeralArmed", false);
            Scribe_Values.Look(ref rolled, "rutFeralRolled", false);
        }
    }

    // ── the drift-in route ──────────────────────────────────────────────
    public class IncidentWorker_FallSurvivor : IncidentWorker
    {
        public override float BaseChanceThisGame => base.BaseChanceThisGame * FallLineArrivalsSettings.survivorFrequency;

        protected override bool CanFireNowSub(IncidentParms parms)
        {
            Map map = parms.target as Map;
            if (!FallLineArrivalsSettings.survivorsEnabled || !FallLineGate.Allowed(map) || !FeralSurvivors.RoomForOne(map))
            {
                return false;
            }
            return FeralSurvivors.PickKind() != null
                && RCellFinder.TryFindRandomPawnEntryCell(out _, map, CellFinder.EdgeRoadChance_Animal);
        }

        protected override bool TryExecuteWorker(IncidentParms parms)
        {
            if (!FallLineArrivalsSettings.survivorsEnabled || !(parms.target is Map map))
            {
                return false;
            }
            PawnKindDef kind = FeralSurvivors.PickKind();
            IntVec3 entry = parms.spawnCenter;
            if (kind == null || (!entry.IsValid
                && !RCellFinder.TryFindRandomPawnEntryCell(out entry, map, CellFinder.EdgeRoadChance_Animal)))
            {
                return false;
            }
            return FeralSurvivors.SpawnSurvivor(map, entry, kind, false, def.letterDef) != null;
        }
    }
}
