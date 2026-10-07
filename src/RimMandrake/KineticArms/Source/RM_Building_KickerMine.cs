using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.KineticArms
{
    /// <summary>
    /// The kicker mine (design §3.1 row 5): a persistent trap that launches whoever springs it in its FACING. It never
    /// destroys itself (trapDestroyOnSpring false) unless "Kicker mines re-arm" is off; each kick spends
    /// <see cref="RimMandrakeKineticArmsSettings.kickerFuelPerKick"/> chemfuel from its CompRefuelable, which colonists
    /// refill like any fuelled building. With too little charge it is a dud and is not sprung at all. The blast is
    /// centred on the cell BEHIND the plate so Explosive Knockback's radial throw points along the facing; the mine
    /// itself is ignored.
    /// </summary>
    public class RM_Building_KickerMine : Building_Trap
    {
        private CompRefuelable fuel;

        /// <summary>The piston needs a second to reset: a pawn still standing on the plate when the trap ticks again
        /// (Explosive Knockback launches it at the map's post-tick) must not be kicked twice.</summary>
        private int lastKickTick = -99999;

        private const int ResetTicks = 60;

        private CompRefuelable Fuel => fuel ?? (fuel = GetComp<CompRefuelable>());

        public bool Charged => !RimMandrakeKineticArmsSettings.kickerRearms || Fuel == null
            || Fuel.Fuel >= RimMandrakeKineticArmsSettings.kickerFuelPerKick - 0.001f;

        protected override float SpringChance(Pawn p)
        {
            return Charged ? base.SpringChance(p) : 0f;
        }

        protected override void SpringSub(Pawn p)
        {
            Kick(p);
        }

        /// <summary>Public so the proof scenes can fire it deterministically (no spring-chance roll).</summary>
        public void Kick(Pawn p)
        {
            if (!Spawned || !Charged || Find.TickManager.TicksGame - lastKickTick < ResetTicks)
            {
                return;
            }
            lastKickTick = Find.TickManager.TicksGame;
            Map map = Map;
            IntVec3 plate = Position;
            RM_KineticMath.Facing(Rotation.AsInt, out float dx, out float dz);
            float cone = def.GetModExtension<RM_KineticBoltExtension>()?.coneDegrees ?? 90f;
            const float radius = 1.5f;
            RM_KineticArmsUtil.ConeBlast(map, plate, dx, dz, radius, cone, out IntVec3 centre, out List<IntVec3> cells);
            if (RimMandrakeKineticArmsSettings.kickerRearms && Fuel != null)
            {
                Fuel.ConsumeFuel(RimMandrakeKineticArmsSettings.kickerFuelPerKick);
            }
            RM_KineticArmsFx.Ring(map, plate, radius);
            DamageDef dd = DefDatabase<DamageDef>.GetNamed("RM_Repulse_Kicker");
            GenExplosion.DoExplosion(centre, map, radius, dd, this, 1, 0f, null, null, null, p,
                ignoredThings: new List<Thing> { this }, overrideCells: cells);
            RM_KineticArmsJournal.Add("kick", def.defName, plate, centre, cells?.Count ?? -1);
            if (!RimMandrakeKineticArmsSettings.kickerRearms && !Destroyed)
            {
                Destroy();
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref lastKickTick, "rmLastKickTick", -99999);
        }

        public override string GetInspectString()
        {
            string s = base.GetInspectString();
            string arm = Charged ? "Armed, kicks " + Rotation.ToStringHuman() : "Not enough charge to kick";
            return s.NullOrEmpty() ? arm : s + "\n" + arm;
        }
    }
}
