using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks.LiquidTypes
{
    /// <summary>
    /// LIQUID_BOTTLE_LOOP_1, the tank half (design §4/§9: "fill/empty bills
    /// at a tank"). A patched-together scavenger tank, big fixed liquid
    /// store -- ONE stored LiquidDef and a unit count, filled and drained by
    /// the same bottle/bucket/barrel chain everything else in this loop
    /// uses. Deliberately the v1 slice named in the item's own notes, not
    /// the universal cargo tank the design's §4/§6/§9 describe for the full
    /// liquid-logistics epic (minifiable, any-liquid-any-amount, pump/hose/
    /// tanker interop, VE PipeSystem adapters) -- none of that ships here.
    ///
    /// A tank holds exactly one liquid identity at a time: the first
    /// container to fill it decides <see cref="storedLiquid"/>, and it stays
    /// that liquid until drained to zero. No mixing, no per-liquid
    /// sub-tanks, no C# per liquid -- the same "one property block, read
    /// generically" discipline <see cref="LiquidDef"/> itself follows.
    /// </summary>
    public class Building_LiquidTank : Building
    {
        /// <summary>Design "big fixed liquid store" -- a base stock a
        /// dedicated tank building should dwarf a barrel (25 units) with,
        /// scaled by the Mod Settings multiplier so a colony under real
        /// stock pressure can tune it rather than being stuck with a
        /// hand-picked constant.</summary>
        private const int BaseCapacityUnits = 300;

        public LiquidDef storedLiquid;

        public int storedUnits;

        public int Capacity => Mathf.Max(25,
            Mathf.RoundToInt(BaseCapacityUnits * RimMandrakeFlowWorksSettings.tankCapacityMultiplier));

        public bool Empty => storedLiquid == null || storedUnits <= 0;

        /// <summary>Whether this tank can take <paramref name="units"/> more
        /// of <paramref name="liquid"/> right now -- either already holding
        /// that same liquid with room, or empty and free to adopt it.</summary>
        public bool CanAccept(LiquidDef liquid, int units)
        {
            if (liquid == null || units <= 0)
            {
                return false;
            }
            if (!Empty && storedLiquid != liquid)
            {
                return false;
            }
            return storedUnits + units <= Capacity;
        }

        /// <summary>Whether this tank can give up <paramref name="units"/>
        /// of the liquid it is currently holding.</summary>
        public bool CanProvide(int units)
        {
            return !Empty && units > 0 && storedUnits >= units;
        }

        /// <summary>Pours a filled container's contents in. Returns false
        /// (and changes nothing) on a liquid mismatch or a full tank -- the
        /// caller (JobDriver_EmptyBottleIntoTank) leaves the carried
        /// container alone rather than destroy it for a transfer that did
        /// not happen.</summary>
        public bool TryAddLiquid(LiquidDef liquid, int units)
        {
            if (!CanAccept(liquid, units))
            {
                return false;
            }
            storedLiquid = liquid;
            storedUnits += units;
            return true;
        }

        /// <summary>Draws units out for an empty container to fill from.
        /// Clears <see cref="storedLiquid"/> once the tank runs dry, so the
        /// NEXT liquid to arrive is free to be a different one.</summary>
        public bool TryRemoveLiquid(int units)
        {
            if (!CanProvide(units))
            {
                return false;
            }
            storedUnits -= units;
            if (storedUnits <= 0)
            {
                storedUnits = 0;
                storedLiquid = null;
            }
            return true;
        }

        public override string GetInspectString()
        {
            string baseString = base.GetInspectString();
            string content = Empty
                ? "RM_LiquidTankEmpty".Translate()
                : "RM_LiquidTankHolding".Translate(storedLiquid.LabelCap, storedUnits, Capacity);
            return string.IsNullOrEmpty(baseString) ? content : baseString + "\n" + content;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Defs.Look(ref storedLiquid, "storedLiquid");
            Scribe_Values.Look(ref storedUnits, "storedUnits", 0);
        }
    }
}
