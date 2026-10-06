using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.Sound;
using RimMandrake.CreatureBehaviors;

namespace RimMandrake.TheSump
{
    // SUMP_CAPSTAN_TURRET_BUILD_1 (design/Jawa/worldbuilding/biomes/sump_bedazzle_review_2026-10-01.md §5, RULED).
    // Owner, typed: "I love the Blackline Capstan. Model it after the Lasso already built in the game (pulls people
    // towards you, weirdly nonphysical since it doesn't move you at all. But if that mechanic is attached to a
    // turret, it makes complete sense and is awesome. Remove lasso's from the game, but keep this)".
    //
    // The pull is RE-IMPLEMENTED, not borrowed (spec step 3's second branch): Melee Animation is slated to lose its
    // lassos (LASSO_CHERRYPICKER_REMOVAL_1) and its JobDriver_GrapplePawn needs a pawn anchor, so a dependency on it
    // would buy nothing. The lasso's numbers carry over as Mod Settings: range 10 (AM_GrappleRadius base), cooldown
    // 20 s (AM_GrappleCooldown base), and the mod's mass / body-size caps. Powered (the cleanest vanilla shape: a
    // CompPowerTrader, no crew). The reel is a forced move one cell at a time along the line to the turret, the way
    // vanilla moves a pawn it teleports (Position + Notify_Teleported), so it pulls "through anything it can pass".
    //
    // WEBWORK_TRACTION_LANCE_BUILD_1 step 1 (2026-10-06): the pull itself was LIFTED into the shared
    // RimMandrake.CreatureBehaviors.RM_CompTetherPull (one pull, two buildings: this capstan and the traction
    // lance). Behaviour unchanged: this class now only supplies the capstan's gating and its Mod Settings
    // numbers through IRM_TetherPullHost, and draws its turning top. Save keys moved with the fields unchanged.
    public class RM_CapstanTurret : Building, IRM_TetherPullHost
    {
        private static Graphic topGraphic;

        public RM_CompTetherPull Pull => GetComp<RM_CompTetherPull>();
        public Pawn Target => Pull?.Target;
        public int Pulls => Pull?.Pulls ?? 0;
        public int Snaps => Pull?.Snaps ?? 0;
        public bool CoolingDown => Pull != null && Pull.CoolingDown;

        public CompPowerTrader Power => GetComp<CompPowerTrader>();
        public bool Working => RM_TheSumpSettings.capstanEnabled && (Power == null || Power.PowerOn) && Spawned;

        public static int ReelIntervalTicks => RM_CompTetherPull.ReelIntervalTicksFor(RM_TheSumpSettings.capstanReelSpeed);

        public bool TetherCanWork => Working;

        public RM_TetherTuning TetherTuning => new RM_TetherTuning
        {
            range = RM_TheSumpSettings.capstanRange,
            reelSpeed = RM_TheSumpSettings.capstanReelSpeed,
            cooldownSeconds = RM_TheSumpSettings.capstanCooldownSeconds,
            friendlyPull = RM_TheSumpSettings.capstanFriendlyPull,
            snapChance = RM_TheSumpSettings.capstanSnapChance,
            maxMass = RM_TheSumpSettings.capstanMaxMass,
            maxBodySize = RM_TheSumpSettings.capstanMaxBodySize,
            snapDamage = RM_TheSumpSettings.capstanSnapDamage,
        };

        public Material TetherLineMaterial => null; // the capstan's yellow line

        public void Notify_TetherReelStep(Pawn target)
        {
        }

        public void Notify_TetherSnapped(Pawn target, string reasonCode)
        {
        }

        public void Notify_TetherReleased(Pawn target)
        {
        }

        public bool TryRope(Pawn p) => Pull != null && Pull.TryRope(p);

        /// <summary>Proof hook (RM_CapstanTurretProof): one reel step now, ignoring the reel timer.</summary>
        public void DebugReelNow() => Pull?.DebugReelNow();

        protected override void DrawAt(Vector3 drawLoc, bool flip = false)
        {
            base.DrawAt(drawLoc, flip);
            if (topGraphic == null)
            {
                topGraphic = GraphicDatabase.Get<Graphic_Single>("Things/Building/CapstanTurret/RM_CapstanTurret_Top", ShaderDatabase.Cutout, new Vector2(2f, 2f), Color.white);
            }
            Vector3 top = drawLoc;
            top.y = AltitudeLayer.BuildingOnTop.AltitudeFor();
            Matrix4x4 m = Matrix4x4.TRS(top, Quaternion.AngleAxis(Pull?.TopAngle ?? 0f, Vector3.up), new Vector3(2f, 1f, 2f));
            Graphics.DrawMesh(MeshPool.plane10, m, topGraphic.MatSingle, 0);
        }

        public override string GetInspectString()
        {
            string s = base.GetInspectString();
            if (RM_TheSumpSettings.capstanEnabled)
            {
                return s;
            }
            return s.NullOrEmpty() ? "Switched off in Mod Settings." : s + "\nSwitched off in Mod Settings.";
        }
    }

    /// <summary>Dev proofs, called through jawa/static_call.</summary>
    public static class RM_CapstanTurretProof
    {
        /// <summary>
        /// Spawns a powered-off-grid capstan (power comp forced on) and a hostile of `kind` 8 cells away in the open,
        /// ropes it and reels until it arrives or the line goes; reports start/end distance and the outcome.
        /// kind "heavy" spawns a thrumbo-sized beast to prove the mass cap snaps the line.
        /// </summary>
        public static string ProofPull(string kind)
        {
            Map map = Find.CurrentMap;
            ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail("RM_CapstanTurret");
            if (map == null || def == null)
            {
                return "UNMEASURED no map or no RM_CapstanTurret def";
            }
            IntVec3 origin = IntVec3.Invalid;
            foreach (IntVec3 c in GenRadial.RadialCellsAround(map.Center, 40f, true))
            {
                CellRect r = new CellRect(c.x - 1, c.z - 1, 13, 4);
                if (r.InBounds(map) && r.Cells.All(x => x.Standable(map) && x.GetFirstBuilding(map) == null && x.GetFirstPawn(map) == null && !x.Fogged(map)))
                {
                    origin = c;
                    break;
                }
            }
            if (!origin.IsValid)
            {
                return "UNMEASURED no clear 13x4 strip";
            }
            var turret = (RM_CapstanTurret)GenSpawn.Spawn(ThingMaker.MakeThing(def), origin, map);
            turret.SetFaction(Faction.OfPlayer);
            if (turret.Power != null)
            {
                turret.Power.PowerOn = true;
            }
            Pawn p;
            if (kind == "heavy")
            {
                p = PawnGenerator.GeneratePawn(PawnKindDefOf.Thrumbo, null);
            }
            else
            {
                Faction enemy = Find.FactionManager.RandomEnemyFaction(allowNonHumanlike: false);
                PawnKindDef k = DefDatabase<PawnKindDef>.GetNamedSilentFail(kind) ?? PawnKindDefOf.Villager;
                p = PawnGenerator.GeneratePawn(k, enemy);
            }
            GenSpawn.Spawn(p, origin + new IntVec3(9, 0, 0), map);
            float start = p.Position.DistanceTo(turret.Position);
            bool roped = turret.TryRope(p);
            int steps = 0;
            while (turret.Target != null && steps < 40)
            {
                turret.DebugReelNow();
                steps++;
            }
            float end = p.Spawned ? p.Position.DistanceTo(turret.Position) : -1f;
            string outcome = string.Format("PULL kind={0} roped={1} start={2:0.0} end={3:0.0} steps={4} snaps={5} turretHp={6}/{7}",
                kind, roped, start, end, steps, turret.Snaps, turret.HitPoints, turret.MaxHitPoints);
            if (p.Spawned)
            {
                p.Destroy();
            }
            turret.Destroy();
            return outcome;
        }
    }
}
