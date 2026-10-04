using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.Sound;

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
    public class RM_CapstanTurret : Building
    {
        private Pawn target;
        private int nextReelTick = -1;
        private int cooldownUntil = -1;
        private float topAngle;
        private int pulls;
        private int snaps;
        private static Graphic topGraphic;

        public Pawn Target => target;
        public int Pulls => pulls;
        public int Snaps => snaps;
        public bool CoolingDown => Find.TickManager.TicksGame < cooldownUntil;

        public CompPowerTrader Power => GetComp<CompPowerTrader>();
        public bool Working => RM_TheSumpSettings.capstanEnabled && (Power == null || Power.PowerOn) && Spawned;

        public static int ReelIntervalTicks => Mathf.Max(5, Mathf.RoundToInt(30f / Mathf.Max(0.1f, RM_TheSumpSettings.capstanReelSpeed)));

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_References.Look(ref target, "target");
            Scribe_Values.Look(ref nextReelTick, "nextReelTick", -1);
            Scribe_Values.Look(ref cooldownUntil, "cooldownUntil", -1);
            Scribe_Values.Look(ref topAngle, "topAngle");
            Scribe_Values.Look(ref pulls, "pulls");
            Scribe_Values.Look(ref snaps, "snaps");
        }

        protected override void Tick()
        {
            base.Tick();
            if (!Working)
            {
                if (target != null)
                {
                    Release(null);
                }
                return;
            }
            if (target != null)
            {
                if (Find.TickManager.TicksGame >= nextReelTick)
                {
                    ReelStep();
                }
                return;
            }
            if (!CoolingDown && this.IsHashIntervalTick(60))
            {
                Pawn t = FindTarget();
                if (t != null)
                {
                    TryRope(t);
                }
            }
        }

        /// <summary>What the turret ropes: a visible hostile in range, else (setting) a downed colonist out in the open.</summary>
        public Pawn FindTarget()
        {
            float range = RM_TheSumpSettings.capstanRange;
            Pawn best = null;
            float bestDist = float.MaxValue;
            foreach (Pawn p in Map.mapPawns.AllPawnsSpawned)
            {
                if (p.Dead || p == null)
                {
                    continue;
                }
                float d = p.Position.DistanceTo(Position);
                if (d > range || d < 2f || !GenSight.LineOfSight(Position, p.Position, Map, skipFirstCell: true))
                {
                    continue;
                }
                bool hostile = p.HostileTo(Faction.OfPlayer) && !p.Downed && Faction == Faction.OfPlayer;
                bool rescue = RM_TheSumpSettings.capstanFriendlyPull && p.Downed && p.Faction == Faction && p.RaceProps.Humanlike;
                if ((hostile || rescue) && d < bestDist)
                {
                    best = p;
                    bestDist = d;
                }
            }
            return best;
        }

        /// <summary>Throw the line. Over the mass or size cap the line snaps at once.</summary>
        public bool TryRope(Pawn p)
        {
            target = p;
            pulls++;
            nextReelTick = Find.TickManager.TicksGame + ReelIntervalTicks;
            DefDatabase<SoundDef>.GetNamedSilentFail("Interact_BeatFire")?.PlayOneShot(new TargetInfo(Position, Map));
            if (p.GetStatValue(StatDefOf.Mass) > RM_TheSumpSettings.capstanMaxMass || p.BodySize > RM_TheSumpSettings.capstanMaxBodySize)
            {
                Snap(p.LabelShortCap + " is too heavy for the line");
                return false;
            }
            return true;
        }

        private void ReelStep()
        {
            Pawn p = target;
            if (p == null || p.Dead || !p.Spawned || p.Map != Map || !GenSight.LineOfSight(Position, p.Position, Map, skipFirstCell: true))
            {
                Release(null);
                return;
            }
            if (p.Position.AdjacentTo8WayOrInside(this))
            {
                Release(null);
                return;
            }
            bool struggling = !p.Downed && p.HostileTo(Faction.OfPlayer);
            if (struggling && Rand.Chance(RM_TheSumpSettings.capstanSnapChance))
            {
                Snap(p.LabelShortCap + " fought the line until it parted");
                return;
            }
            IntVec3 next = NextCellToward(p.Position, Position);
            if (!next.IsValid || !next.InBounds(Map) || !next.Walkable(Map) || next.GetEdifice(Map) is Building b && b.def.Fillage == FillCategory.Full)
            {
                Release("The line drags " + p.LabelShort + " against an obstacle and goes slack.");
                return;
            }
            p.Position = next;
            p.Notify_Teleported(endCurrentJob: true, resetTweenedPos: false);
            if (p.stances != null)
            {
                p.stances.stunner.StunFor(ReelIntervalTicks + 5, this, addBattleLog: false, showMote: false);
            }
            topAngle = (p.DrawPos - DrawPos).AngleFlat();
            DefDatabase<SoundDef>.GetNamedSilentFail("Interact_Tend")?.PlayOneShot(new TargetInfo(Position, Map));
            nextReelTick = Find.TickManager.TicksGame + ReelIntervalTicks;
        }

        /// <summary>Proof hook (RM_CapstanTurretProof): one reel step now, ignoring the reel timer.</summary>
        public void DebugReelNow()
        {
            if (target != null)
            {
                ReelStep();
            }
        }

        public static IntVec3 NextCellToward(IntVec3 from, IntVec3 to)
        {
            int dx = System.Math.Sign(to.x - from.x);
            int dz = System.Math.Sign(to.z - from.z);
            return new IntVec3(from.x + dx, 0, from.z + dz);
        }

        public void Snap(string why)
        {
            snaps++;
            Pawn p = target;
            target = null;
            cooldownUntil = Find.TickManager.TicksGame + Mathf.RoundToInt(RM_TheSumpSettings.capstanCooldownSeconds * 60f);
            MoteMaker.ThrowText(DrawPos, Map, "Line snapped!", Color.red, 3.5f);
            FleckMaker.ThrowMicroSparks(DrawPos, Map);
            if (RM_TheSumpSettings.capstanSnapDamage > 0f)
            {
                TakeDamage(new DamageInfo(DamageDefOf.Blunt, RM_TheSumpSettings.capstanSnapDamage, 0f, -1f, p));
            }
            if (Faction == Faction.OfPlayer)
            {
                Messages.Message("The capstan's line snapped: " + why + ".", this, MessageTypeDefOf.NegativeEvent, historical: false);
            }
        }

        public void Release(string why)
        {
            target = null;
            cooldownUntil = Find.TickManager.TicksGame + Mathf.RoundToInt(RM_TheSumpSettings.capstanCooldownSeconds * 60f);
            if (why != null && Faction == Faction.OfPlayer)
            {
                Messages.Message(why, this, MessageTypeDefOf.NeutralEvent, historical: false);
            }
        }

        protected override void DrawAt(Vector3 drawLoc, bool flip = false)
        {
            base.DrawAt(drawLoc, flip);
            if (topGraphic == null)
            {
                topGraphic = GraphicDatabase.Get<Graphic_Single>("Things/Building/CapstanTurret/RM_CapstanTurret_Top", ShaderDatabase.Cutout, new Vector2(2f, 2f), Color.white);
            }
            Vector3 top = drawLoc;
            top.y = AltitudeLayer.BuildingOnTop.AltitudeFor();
            Matrix4x4 m = Matrix4x4.TRS(top, Quaternion.AngleAxis(topAngle, Vector3.up), new Vector3(2f, 1f, 2f));
            Graphics.DrawMesh(MeshPool.plane10, m, topGraphic.MatSingle, 0);
            if (target != null && target.Spawned)
            {
                GenDraw.DrawLineBetween(DrawPos, target.DrawPos, SimpleColor.Yellow, 0.3f);
            }
        }

        public override string GetInspectString()
        {
            string s = base.GetInspectString();
            string mine = !RM_TheSumpSettings.capstanEnabled ? "Switched off in Mod Settings."
                : target != null ? "Reeling in " + target.LabelShort + "."
                : CoolingDown ? "Re-coiling the line: " + (cooldownUntil - Find.TickManager.TicksGame).ToStringTicksToPeriod() + "."
                : "Ready. Range " + RM_TheSumpSettings.capstanRange.ToString("0") + " cells.";
            mine += "\nLines thrown " + pulls + ", snapped " + snaps + ".";
            return s.NullOrEmpty() ? mine : s + "\n" + mine;
        }

        public override void DrawExtraSelectionOverlays()
        {
            base.DrawExtraSelectionOverlays();
            GenDraw.DrawRadiusRing(Position, RM_TheSumpSettings.capstanRange);
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
