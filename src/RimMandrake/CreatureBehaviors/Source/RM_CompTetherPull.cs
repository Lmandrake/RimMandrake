using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace RimMandrake.CreatureBehaviors
{
    // WEBWORK_TRACTION_LANCE_BUILD_1 step 1: THE ONE PULL. Lifted verbatim from RM_CapstanTurret
    // (SUMP_CAPSTAN_TURRET_BUILD_1, e263d1d13), which shipped it inline; the capstan now carries this comp and
    // its behaviour is unchanged. Owner, typed (capstan item): "Model it after the Lasso already built in the
    // game (pulls people towards you, weirdly nonphysical since it doesn't move you at all ...)".
    //
    // 🔴 One pull, two buildings, never a second implementation: the capstan (TheSump) and the traction lance
    // (Webwork, RM_Building_TractionLance) both name this class. Do not add a second forced-move/grapple site.
    //
    // The reel is a forced move one cell at a time along the line to the anchor (Position + Notify_Teleported,
    // the way vanilla moves a pawn it teleports), so it pulls "through anything it can pass". A Full-fillage
    // edifice on the next cell, or a broken line of sight, stops it ("wall").
    //
    // Live numbers come from the parent when it implements IRM_TetherPullHost (each building's own Mod
    // Settings); otherwise from these props.
    public class RM_CompProperties_TetherPull : CompProperties
    {
        public float range = 10f;
        public float reelSpeed = 1f;
        public float cooldownSeconds = 20f;
        public bool friendlyPull = true;
        public float snapChance = 0.08f;
        public float maxMass = 150f;
        public float maxBodySize = 2.5f;
        public float snapDamage = 20f;

        // Readable signs. {0} in snapMessage is the reason sentence.
        public string snapMessage = "The line snapped: {0}.";
        public string snapMoteText = "Line snapped!";
        public string ropeSound = "Interact_BeatFire";
        public string reelSound = "Interact_Tend";

        public RM_CompProperties_TetherPull()
        {
            compClass = typeof(RM_CompTetherPull);
        }
    }

    public struct RM_TetherTuning
    {
        public float range;
        public float reelSpeed;
        public float cooldownSeconds;
        public bool friendlyPull;
        public float snapChance;
        public float maxMass;
        public float maxBodySize;
        public float snapDamage;
    }

    /// <summary>A building that owns a RM_CompTetherPull and supplies its live numbers and gating.</summary>
    public interface IRM_TetherPullHost
    {
        /// <summary>Settings on, powered/crewed/rigged: whatever this building needs to throw and reel.</summary>
        bool TetherCanWork { get; }

        RM_TetherTuning TetherTuning { get; }

        /// <summary>The line colour; null = the capstan's yellow.</summary>
        Material TetherLineMaterial { get; }

        /// <summary>After each successful reel step (wear, power draw).</summary>
        void Notify_TetherReelStep(Pawn target);

        /// <summary>The line parted. reasonCode: mass | struggle | wear.</summary>
        void Notify_TetherSnapped(Pawn target, string reasonCode);

        /// <summary>The line went slack without snapping (arrived, lost, wall, obstacle, off).</summary>
        void Notify_TetherReleased(Pawn target);
    }

    public class RM_CompTetherPull : ThingComp
    {
        private Pawn target;
        private int nextReelTick = -1;
        private int cooldownUntil = -1;
        private float topAngle;
        private int pulls;
        private int snaps;
        // Deterministic-state proof field: pulled | arrived | lost | wall | obstacle | mass | struggle | wear | off.
        private string lastOutcome = "";

        public RM_CompProperties_TetherPull Props => (RM_CompProperties_TetherPull)props;
        public IRM_TetherPullHost Host => parent as IRM_TetherPullHost;

        public Pawn Target => target;
        public int Pulls => pulls;
        public int Snaps => snaps;
        public float TopAngle => topAngle;
        public string LastOutcome => lastOutcome;
        public bool CoolingDown => Find.TickManager.TicksGame < cooldownUntil;
        public int CooldownTicksLeft => cooldownUntil - Find.TickManager.TicksGame;

        public bool CanWork => parent.Spawned && (Host == null || Host.TetherCanWork);

        public RM_TetherTuning Tuning
        {
            get
            {
                if (Host != null)
                {
                    return Host.TetherTuning;
                }
                return new RM_TetherTuning
                {
                    range = Props.range,
                    reelSpeed = Props.reelSpeed,
                    cooldownSeconds = Props.cooldownSeconds,
                    friendlyPull = Props.friendlyPull,
                    snapChance = Props.snapChance,
                    maxMass = Props.maxMass,
                    maxBodySize = Props.maxBodySize,
                    snapDamage = Props.snapDamage,
                };
            }
        }

        public static int ReelIntervalTicksFor(float reelSpeed)
        {
            return Mathf.Max(5, Mathf.RoundToInt(30f / Mathf.Max(0.1f, reelSpeed)));
        }

        public int ReelIntervalTicks => ReelIntervalTicksFor(Tuning.reelSpeed);

        // Save keys identical to the capstan's pre-lift fields: comps scribe inside the thing's own node, so an
        // old capstan save loads straight into this comp.
        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_References.Look(ref target, "target");
            Scribe_Values.Look(ref nextReelTick, "nextReelTick", -1);
            Scribe_Values.Look(ref cooldownUntil, "cooldownUntil", -1);
            Scribe_Values.Look(ref topAngle, "topAngle");
            Scribe_Values.Look(ref pulls, "pulls");
            Scribe_Values.Look(ref snaps, "snaps");
            Scribe_Values.Look(ref lastOutcome, "tetherLastOutcome", "");
        }

        public override void CompTick()
        {
            base.CompTick();
            if (!CanWork)
            {
                if (target != null)
                {
                    Release(null, "off");
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
            if (!CoolingDown && parent.IsHashIntervalTick(60))
            {
                Pawn t = FindTarget();
                if (t != null)
                {
                    TryRope(t);
                }
            }
        }

        /// <summary>What the line ropes: a visible hostile in range, else (setting) a downed colonist out in the open.</summary>
        public Pawn FindTarget()
        {
            RM_TetherTuning tune = Tuning;
            Map map = parent.Map;
            Pawn best = null;
            float bestDist = float.MaxValue;
            foreach (Pawn p in map.mapPawns.AllPawnsSpawned)
            {
                if (p == null || p.Dead)
                {
                    continue;
                }
                float d = p.Position.DistanceTo(parent.Position);
                if (d > tune.range || d < 2f || !GenSight.LineOfSight(parent.Position, p.Position, map, skipFirstCell: true))
                {
                    continue;
                }
                bool hostile = p.HostileTo(Faction.OfPlayer) && !p.Downed && parent.Faction == Faction.OfPlayer;
                bool rescue = tune.friendlyPull && p.Downed && p.Faction == parent.Faction && p.RaceProps.Humanlike && !p.InBed();
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
            RM_TetherTuning tune = Tuning;
            target = p;
            pulls++;
            lastOutcome = "pulled";
            nextReelTick = Find.TickManager.TicksGame + ReelIntervalTicksFor(tune.reelSpeed);
            PlaySound(Props.ropeSound);
            if (p.GetStatValue(StatDefOf.Mass) > tune.maxMass || p.BodySize > tune.maxBodySize)
            {
                Snap(p.LabelShortCap + " is too heavy for the line", "mass");
                return false;
            }
            return true;
        }

        private void ReelStep()
        {
            Pawn p = target;
            Map map = parent.Map;
            if (p == null || p.Dead || !p.Spawned || p.Map != map)
            {
                Release(null, "lost");
                return;
            }
            if (!GenSight.LineOfSight(parent.Position, p.Position, map, skipFirstCell: true))
            {
                Release(null, "wall");
                return;
            }
            if (p.Position.AdjacentTo8WayOrInside(parent))
            {
                Release(null, "arrived");
                return;
            }
            bool struggling = !p.Downed && p.HostileTo(Faction.OfPlayer);
            if (struggling && Rand.Chance(Tuning.snapChance))
            {
                Snap(p.LabelShortCap + " fought the line until it parted", "struggle");
                return;
            }
            IntVec3 next = NextCellToward(p.Position, parent.Position);
            if (!next.IsValid || !next.InBounds(map) || !next.Walkable(map))
            {
                Release("The line drags " + p.LabelShort + " against an obstacle and goes slack.", "obstacle");
                return;
            }
            if (next.GetEdifice(map) is Building b && b.def.Fillage == FillCategory.Full)
            {
                Release("The line drags " + p.LabelShort + " against an obstacle and goes slack.", "wall");
                return;
            }
            p.Position = next;
            p.Notify_Teleported(endCurrentJob: true, resetTweenedPos: false);
            if (p.stances != null)
            {
                p.stances.stunner.StunFor(ReelIntervalTicks + 5, parent, addBattleLog: false, showMote: false);
            }
            topAngle = (p.DrawPos - parent.DrawPos).AngleFlat();
            PlaySound(Props.reelSound);
            nextReelTick = Find.TickManager.TicksGame + ReelIntervalTicks;
            Host?.Notify_TetherReelStep(p);
        }

        /// <summary>Proof hook: one reel step now, ignoring the reel timer.</summary>
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

        /// <param name="why">Player-facing reason sentence.</param>
        /// <param name="reasonCode">mass | struggle | wear (read by proofs and the host).</param>
        public void Snap(string why, string reasonCode)
        {
            snaps++;
            Pawn p = target;
            target = null;
            lastOutcome = reasonCode;
            Map map = parent.Map;
            cooldownUntil = Find.TickManager.TicksGame + Mathf.RoundToInt(Tuning.cooldownSeconds * 60f);
            MoteMaker.ThrowText(parent.DrawPos, map, Props.snapMoteText, Color.red, 3.5f);
            FleckMaker.ThrowMicroSparks(parent.DrawPos, map);
            float dmg = Tuning.snapDamage;
            if (dmg > 0f)
            {
                parent.TakeDamage(new DamageInfo(DamageDefOf.Blunt, dmg, 0f, -1f, p));
            }
            if (parent.Faction == Faction.OfPlayer)
            {
                Messages.Message(string.Format(Props.snapMessage, why), parent, MessageTypeDefOf.NegativeEvent, historical: false);
            }
            Host?.Notify_TetherSnapped(p, reasonCode);
        }

        public void Release(string why, string reasonCode)
        {
            Pawn p = target;
            target = null;
            lastOutcome = reasonCode;
            cooldownUntil = Find.TickManager.TicksGame + Mathf.RoundToInt(Tuning.cooldownSeconds * 60f);
            if (why != null && parent.Faction == Faction.OfPlayer)
            {
                Messages.Message(why, parent, MessageTypeDefOf.NeutralEvent, historical: false);
            }
            Host?.Notify_TetherReleased(p);
        }

        private void PlaySound(string defName)
        {
            if (defName.NullOrEmpty())
            {
                return;
            }
            DefDatabase<SoundDef>.GetNamedSilentFail(defName)?.PlayOneShot(new TargetInfo(parent.Position, parent.Map));
        }

        public override void PostDraw()
        {
            base.PostDraw();
            if (target != null && target.Spawned)
            {
                Material mat = Host?.TetherLineMaterial;
                if (mat != null)
                {
                    GenDraw.DrawLineBetween(parent.DrawPos, target.DrawPos, mat, 0.3f);
                }
                else
                {
                    GenDraw.DrawLineBetween(parent.DrawPos, target.DrawPos, SimpleColor.Yellow, 0.3f);
                }
            }
        }

        public override string CompInspectStringExtra()
        {
            string s = !CanWork ? "Idle."
                : target != null ? "Reeling in " + target.LabelShort + "."
                : CoolingDown ? "Re-coiling the line: " + CooldownTicksLeft.ToStringTicksToPeriod() + "."
                : "Ready. Range " + Tuning.range.ToString("0") + " cells.";
            return s + "\nLines thrown " + pulls + ", snapped " + snaps + ".";
        }

        public override void PostDrawExtraSelectionOverlays()
        {
            base.PostDrawExtraSelectionOverlays();
            // Lance range can reach 30 x 1.3 x 3 = 117 cells; DrawRadiusRing logs a red error above the radial table.
            GenDraw.DrawRadiusRing(parent.Position, Mathf.Min(Tuning.range, GenRadial.MaxRadialPatternRadius));
        }
    }
}
