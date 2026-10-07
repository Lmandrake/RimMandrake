using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.KineticArms
{
    /// <summary>
    /// The pulse cannon (design §3 row 7, owner Q6): a powered turret that stores pulse charges and refills them from
    /// power, so a big raid drains it and an ammo-free pit-capture farm is not free. Below one charge it picks no
    /// target; each completed burst spends one. A forced target ignores the gate (the player chose to fire), but the
    /// charge never goes below zero.
    /// </summary>
    public class RM_Building_PulseCannon : Building_TurretGun
    {
        private float charge = -1f;

        public float Charge => charge;

        public static int Capacity => Mathf.Max(1, RimMandrakeKineticArmsSettings.pulseCapacity);

        public static int RechargeTicks => Mathf.Max(1, Mathf.RoundToInt(RimMandrakeKineticArmsSettings.pulseRechargeSeconds * 60f));

        public override void SpawnSetup(Map map, bool respawningAfterLoad)
        {
            base.SpawnSetup(map, respawningAfterLoad);
            if (charge < 0f)
            {
                charge = Capacity;
            }
        }

        protected override void Tick()
        {
            base.Tick();
            if (Spawned)
            {
                charge = RM_KineticMath.Recharge(charge, Capacity, RechargeTicks, 1, powerComp == null || powerComp.PowerOn);
            }
        }

        public override LocalTargetInfo TryFindNewTarget()
        {
            if (!RM_KineticMath.CanFire(charge))
            {
                return LocalTargetInfo.Invalid;
            }
            return base.TryFindNewTarget();
        }

        protected override void BurstComplete()
        {
            base.BurstComplete();
            charge = RM_KineticMath.Spend(charge);
        }

        /// <summary>Proof hook: set the stored charge.</summary>
        public void SetCharge(float c) => charge = Mathf.Clamp(c, 0f, Capacity);

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref charge, "rmPulseCharge", -1f);
        }

        public override string GetInspectString()
        {
            string s = base.GetInspectString();
            string c = "Pulse charges: " + Mathf.FloorToInt(charge + 0.0001f) + " / " + Capacity;
            return s.NullOrEmpty() ? c : s + "\n" + c;
        }
    }
}
