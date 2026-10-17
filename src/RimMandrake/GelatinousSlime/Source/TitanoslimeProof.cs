using System.Linq;
using System.Text;
using RimWorld;
using Verse;

namespace RimMandrake.GelatinousSlime
{
    // TITANOSLIME_SLIME_BIOME_1 spec §8 live gates: jawa/static_call proofs (the RM_SlimeSeekerProof pattern), so a
    // script can set mass, force the verb's own engulf outcome and read the comp without clicking a DEV gizmo.
    // Every method takes the pawn by ThingID and returns key=value text. Nothing here runs unless a script calls it.
    public static class RM_TitanoslimeProof
    {
        private static RM_CompEngulfer Comp(Pawn p)
        {
            return p == null ? null : p.TryGetComp<RM_CompEngulfer>();
        }

        /// <summary>Pawn state, plus the slime's growth/hold state when it has the comp.</summary>
        public static string ProofRead(Pawn p)
        {
            if (p == null)
            {
                return "ERROR no pawn";
            }
            StringBuilder sb = new StringBuilder();
            sb.AppendFormat("id={0} def={1} spawned={2} dead={3} downed={4} destroyed={5} bodySize={6:0.###}",
                p.ThingID, p.def.defName, p.Spawned, p.Dead, p.Downed, p.Destroyed, p.BodySize);
            if (p.ageTracker != null)
            {
                PawnKindLifeStage kls = p.ageTracker.CurKindLifeStage;
                GraphicData g = kls != null ? kls.bodyGraphicData : null;
                sb.AppendFormat(" stage={0} lifeStage={1} drawSize={2}", p.ageTracker.CurLifeStageIndex,
                    p.ageTracker.CurLifeStage != null ? p.ageTracker.CurLifeStage.defName : "null",
                    g != null ? g.drawSize.x.ToString("0.##") : "null");
            }
            if (p.needs != null && p.needs.food != null)
            {
                sb.AppendFormat(" food={0:0.###}", p.needs.food.CurLevelPercentage);
            }
            if (p.health != null && p.health.hediffSet != null)
            {
                Hediff sl = SlimeDefs.Slimification != null ? p.health.hediffSet.GetFirstHediffOfDef(SlimeDefs.Slimification) : null;
                int acid = p.health.hediffSet.hediffs.Count(h => h.def.defName.Contains("Acid"));
                sb.AppendFormat(" health={0:0.###} slimification={1} acidHediffs={2}", p.health.summaryHealth.SummaryHealthPercent,
                    sl != null ? sl.Severity.ToString("0.###") : "none", acid);
            }
            if (p.stances != null && p.stances.stunner != null)
            {
                sb.AppendFormat(" stunned={0}", p.stances.stunner.Stunned);
            }
            sb.AppendFormat(" holder={0}", p.ParentHolder != null ? p.ParentHolder.GetType().Name : "null");
            Corpse c = p.Corpse;
            sb.AppendFormat(" corpse={0}", c == null ? "none" : (c.Destroyed ? "destroyed" : (c.Spawned ? "spawned" : "unspawned")));
            RM_CompEngulfer comp = Comp(p);
            if (comp != null)
            {
                sb.AppendFormat(" mass={0:0.###} held={1} capacity={2} heldClock=[{3}]", comp.AbsorbedMass, comp.HeldCount,
                    comp.Capacity, comp.DevHeldReport());
            }
            return sb.ToString();
        }

        /// <summary>The DEV gizmo path: absorbedMass set outright, stage re-locked.</summary>
        public static string ProofSetMass(Pawn p, float mass)
        {
            RM_CompEngulfer comp = Comp(p);
            if (comp == null)
            {
                return "ERROR no RM_CompEngulfer";
            }
            comp.DevSetMass(mass, false);
            return ProofRead(p);
        }

        /// <summary>A mass change through AddMass, the path every real growth source takes.</summary>
        public static string ProofFeed(Pawn p, float delta)
        {
            RM_CompEngulfer comp = Comp(p);
            if (comp == null)
            {
                return "ERROR no RM_CompEngulfer";
            }
            comp.DevFeed(delta);
            return ProofRead(p);
        }

        /// <summary>RM_Verb_MeleeEngulf's own outcome on a landed hit: engulf if the gate allows, else report the gate.</summary>
        public static string ProofEngulf(Pawn slime, Pawn prey)
        {
            RM_CompEngulfer comp = Comp(slime);
            if (comp == null || prey == null)
            {
                return "ERROR no RM_CompEngulfer or prey";
            }
            bool can = comp.CanEngulf(prey);
            if (can)
            {
                comp.Engulf(prey);
            }
            return "canEngulf=" + can + " preyHolder=" + (prey.ParentHolder != null ? prey.ParentHolder.GetType().Name : "null")
                   + " | " + ProofRead(slime);
        }

        /// <summary>Kills the pawn outright (no damage roll), for the corpse-site gate.</summary>
        public static string ProofKill(Pawn p)
        {
            if (p == null || p.Dead)
            {
                return "ERROR no living pawn";
            }
            Map map = p.MapHeld;
            IntVec3 pos = p.PositionHeld;
            p.Kill(null);
            return "killedAt=" + pos.x + "," + pos.z + " map=" + (map != null ? map.Index.ToString() : "null") + " | " + ProofRead(p);
        }

        /// <summary>Finds a pawn by thingIDNumber wherever it is (map, world, held, discarded): for "no corpse" reads.</summary>
        public static string ProofFind(int idNumber)
        {
            Pawn p = PawnsFinder.AllMapsWorldAndTemporary_AliveOrDead.FirstOrDefault(x => x.thingIDNumber == idNumber);
            if (p == null)
            {
                foreach (Map m in Find.Maps)
                {
                    Corpse c = m.listerThings.ThingsInGroup(ThingRequestGroup.Corpse).OfType<Corpse>()
                        .FirstOrDefault(x => x.InnerPawn != null && x.InnerPawn.thingIDNumber == idNumber);
                    if (c != null)
                    {
                        p = c.InnerPawn;
                        break;
                    }
                }
            }
            return p == null ? "found=False id=" + idNumber : "found=True " + ProofRead(p);
        }
    }
}
