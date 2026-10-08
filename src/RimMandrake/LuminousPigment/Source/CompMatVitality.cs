using RimWorld;
using Verse;

namespace RimMandrake.LuminousPigment
{
    // Spec §2.2: fresh crowncarpet is NOT CompRottable — vanilla rot slows in
    // the cold, and the ruling is the inverse ("dies if refrigerated"). This
    // comp reads its two numbers live from Mod Settings (matLifeDays,
    // matChillKillTemp) rather than baking them into CompProperties, so a
    // settings change takes effect on the next rare tick with no restart.
    //
    // Requires the ThingDef to declare <tickerType>Rare</tickerType> — a
    // comp's CompTickRare is only called if the parent Thing ticks at that
    // rate at all.
    public class CompProperties_MatVitality : CompProperties
    {
        public CompProperties_MatVitality()
        {
            compClass = typeof(CompMatVitality);
        }
    }

    public class CompMatVitality : ThingComp
    {
        private int ticksAlive;
        private bool dead;

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref ticksAlive, "ticksAlive", 0);
            Scribe_Values.Look(ref dead, "rmMatDead", false);
        }

        public override string CompInspectStringExtra()
        {
            if (dead) return null;
            float lifeDays = LuminousPigmentSettings.matLifeDays;
            int hoursLeft = RM_DeepfireRules.HoursLeft(ticksAlive, lifeDays, GenDate.TicksPerDay);
            return "alive: " + hoursLeft.ToString() + "h left";
        }

        public override void CompTickRare()
        {
            base.CompTickRare();
            if (dead) return;

            MatFate fate = RM_DeepfireRules.MatTick(ref ticksAlive, parent.AmbientTemperature, LuminousPigmentSettings.matChillKillTemp,
                LuminousPigmentSettings.matLifeDays, GenTicks.TickRareInterval, GenDate.TicksPerDay);
            if (fate == MatFate.DiedChill) MaybeWarnChill();
            if (fate != MatFate.Alive) BecomeDead();
        }

        private void MaybeWarnChill()
        {
            GameComponent_Deepfire gc = GameComponent_Deepfire.Instance;
            if (gc == null || gc.chillMessageShown) return;
            gc.chillMessageShown = true;
            Messages.Message(
                "Fresh crowncarpet dies in the cold -- refine it, don't refrigerate it.",
                MessageTypeDefOf.NegativeEvent, false);
        }

        private void BecomeDead()
        {
            if (dead) return;
            dead = true;

            ThingDef deadDef = ThingDef.Named("RM_CrowncarpetDead");
            if (deadDef == null) return; // absent defs must never throw.

            Thing deadThing = ThingMaker.MakeThing(deadDef);
            deadThing.stackCount = parent.stackCount;

            if (parent.Spawned)
            {
                Map map = parent.Map;
                IntVec3 pos = parent.Position;
                parent.Destroy(DestroyMode.Vanish);
                GenPlace.TryPlaceThing(deadThing, pos, map, ThingPlaceMode.Near);
                return;
            }

            ThingOwner owner = parent.holdingOwner;
            if (owner != null)
            {
                owner.Remove(parent);
                owner.TryAdd(deadThing);
                return;
            }

            parent.Destroy(DestroyMode.Vanish);
        }
    }
}
