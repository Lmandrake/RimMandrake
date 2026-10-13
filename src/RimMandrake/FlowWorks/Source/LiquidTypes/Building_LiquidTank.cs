using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks.LiquidTypes
{
    /// <summary>POND_VOLUME_UNIFY_DEEP_NOTCH_YARDSTICK (§8.2, §8.5): a tank's size is its FOOTPRINT (the def's size),
    /// one deep notch (RM_Volume.UnitsPerSquare) per square, doubled when <see cref="tall"/>. Absent = not tall.</summary>
    public class RM_LiquidTankExtension : DefModExtension
    {
        public bool tall;

        /// <summary>Height factor on the footprint's capacity (2 = tall, 4 = extra-tall). 0 (unset) falls back to <see cref="tall"/>,
        /// so every def written with the old flag loads unchanged.</summary>
        public float capacityFactor;

        public float HeightFactor => capacityFactor > 0f ? capacityFactor : (tall ? 2f : 1f);
    }

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
        public LiquidDef storedLiquid;

        /// <summary>Liquid networks L4 (rev 2 §3.2): the tank's job, saved as rmTankMode, default Store.</summary>
        public Machinery.RM_TankMode mode = Machinery.RM_TankMode.Store;

        /// <summary>Liquid networks L9 (rev 2 §3.4): on another faction's tank, the faction that caught the player at it (saved
        /// rmTheftCaughtBy) and the theft ticks not yet charged (rmTheftTicks); the stock last seen (runtime).</summary>
        public RimWorld.Faction theftCaughtBy;
        public int theftTicks;
        public int theftSeenUnits = -1;
        public LiquidDef theftSeenLiquid;

        /// <summary>The job in force: Store whenever tank jobs are off in Mod Settings, or the tank is not the player's.</summary>
        public Machinery.RM_TankMode EffectiveMode => Hose.RM_HoseSettings.tankModesEnabled && Faction == RimWorld.Faction.OfPlayer ? mode : Machinery.RM_TankMode.Store;

        /// <summary>Pumps and machines may put liquid in (every job but Empty).</summary>
        public bool TakesFromMachines => EffectiveMode != Machinery.RM_TankMode.Empty;

        /// <summary>Machines may draw from it (every job but Dump).</summary>
        public bool GivesToMachines => EffectiveMode != Machinery.RM_TankMode.Dump;

        /// <summary>A bottle may be poured in: a Fill tank always, a Store tank only on a player's order (bottle-loop fix).</summary>
        public bool TakesBottles(bool playerOrdered) => Machinery.RM_TankBottleRules.PoursInto(EffectiveMode, playerOrdered);

        /// <summary>An empty bottle may be filled from it: Store, Empty or Dump, never Fill (bottle-loop fix).</summary>
        public bool GivesToBottles => Machinery.RM_TankBottleRules.FillsFrom(EffectiveMode);

        public int storedUnits;

        /// <summary>One tank square = one deep canal square = one deep pond square (owner 2026-10-12): footprint area ×
        /// RM_Volume.UnitsPerSquare × (2 if tall) × the tank slider. A 2×2 tank holds 80 units, a tall one 160.</summary>
        public int Capacity => RM_Volume.TankCapacity(def.size.x * def.size.z,
            def.GetModExtension<RM_LiquidTankExtension>()?.HeightFactor ?? 1f, RimMandrakeFlowWorksSettings.tankCapacityMultiplier);

        /// <summary>§8.3: a tank from an older save keeps every stored unit above its new capacity; it refuses input
        /// (CanAccept) and drains normally.</summary>
        public bool Overfull => RM_Volume.Overfull(storedUnits, Capacity);

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

        public override System.Collections.Generic.IEnumerable<Gizmo> GetGizmos()
        {
            foreach (Gizmo g in base.GetGizmos())
            {
                yield return g;
            }
            if (!Hose.RM_HoseSettings.tankModesEnabled || Faction != RimWorld.Faction.OfPlayer)
            {
                yield break;
            }
            yield return new Command_Action
            {
                defaultLabel = ("RMFlow_TankMode_" + mode).Translate(),
                defaultDesc = "RMFlow_TankModeDesc".Translate(),
                icon = ContentFinder<Texture2D>.Get("UI/Commands/SetTargetFuelLevel", false) ?? BaseContent.BadTex,
                action = () =>
                {
                    mode = (Machinery.RM_TankMode)(((int)mode + 1) % 4);
                    Machinery.RM_LiquidNet.Bump(Map);
                }
            };
        }

        public override string GetInspectString()
        {
            string baseString = base.GetInspectString();
            string content = Empty
                ? "RM_LiquidTankEmpty".Translate()
                : "RM_LiquidTankHolding".Translate(storedLiquid.LabelCap, storedUnits, Capacity);
            if (!Empty && Overfull)
            {
                content += " " + "RM_LiquidTankOverfull".Translate();
            }
            if (Hose.RM_HoseSettings.tankModesEnabled && Faction == RimWorld.Faction.OfPlayer)
            {
                content += "\n" + "RMFlow_TankModeInspect".Translate(("RMFlow_TankMode_" + mode).Translate());
            }
            return string.IsNullOrEmpty(baseString) ? content : baseString + "\n" + content;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Defs.Look(ref storedLiquid, "storedLiquid");
            Scribe_Values.Look(ref storedUnits, "storedUnits", 0);
            Scribe_Values.Look(ref mode, "rmTankMode", Machinery.RM_TankMode.Store);
            Scribe_References.Look(ref theftCaughtBy, "rmTheftCaughtBy");
            Scribe_Values.Look(ref theftTicks, "rmTheftTicks", 0);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && storedLiquid == null && storedUnits > 0)
            {
                // The saved liquid's def no longer exists (mod removed): the units cannot keep an identity, and
                // left in place the next liquid poured in would adopt them (GPT FlowWorks review #27). Disclose
                // and clear rather than convert silently.
                Log.Warning("[RimMandrake.FlowWorks] " + this + " held " + storedUnits
                    + " units of a liquid whose def is gone; cleared.");
                storedUnits = 0;
            }
        }
    }
}
