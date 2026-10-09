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

        // Stack ops keep the clock (GPT review #3): a split piece inherits
        // its age; a merge takes the count-weighted age (CompRottable's own
        // PreAbsorbStack policy).
        public override void PostSplitOff(Thing piece)
        {
            base.PostSplitOff(piece);
            CompMatVitality o = piece.TryGetComp<CompMatVitality>();
            if (o == null || o == this) return;
            o.ticksAlive = ticksAlive;
            o.dead = dead;
        }

        public override void PreAbsorbStack(Thing otherStack, int count)
        {
            base.PreAbsorbStack(otherStack, count);
            CompMatVitality o = otherStack.TryGetComp<CompMatVitality>();
            if (o == null) return;
            int total = parent.stackCount + count;
            if (total <= 0) return;
            ticksAlive = (int)(((long)ticksAlive * parent.stackCount + (long)o.ticksAlive * count) / total);
        }

        public override string CompInspectStringExtra()
        {
            if (dead) return null;
            float lifeDays = LuminousPigmentSettings.matLifeDays;
            int hoursLeft = RM_DeepfireRules.HoursLeft(ticksAlive, lifeDays, GenDate.TicksPerDay);
            return "alive: " + hoursLeft.ToString() + "h left";
        }

        // MAT_DISCOVERY_SIGHT_RULE_1 PROVISIONAL (auto-decided 2026-10-09): fresh mat that a colonist has just
        // harvested (it spawns beside them) or that lies on the player's home map counts as the sighting, so a mat
        // cut before the plant's long-tick check ever ran still unlocks the research.
        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            if (respawningAfterLoad || dead || !LuminousPigmentSettings.matDiscoveryByEyeOrHand) return;
            GameComponent_Deepfire gc = GameComponent_Deepfire.Instance;
            if (gc == null || gc.matSeen) return;
            Map map = parent.Map;
            if (map == null) return;
            bool byHand = map.IsPlayerHome;
            if (!byHand)
            {
                foreach (Pawn p in map.mapPawns.FreeColonistsSpawned)
                {
                    if (p.Position.InHorDistOf(parent.Position, 3f)) { byHand = true; break; }
                }
            }
            if (byHand) CompMatDiscovery.MarkSeen(parent);
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
                // GPT review #24: the detached original is destroyed, and a
                // failed re-add drops the dead stack at the holder's root
                // position instead of losing it.
                owner.Remove(parent);
                if (!owner.TryAdd(deadThing))
                {
                    Map rootMap = ThingOwnerUtility.GetRootMap(owner.Owner);
                    if (rootMap != null)
                    {
                        GenPlace.TryPlaceThing(deadThing, ThingOwnerUtility.GetRootPosition(owner.Owner), rootMap, ThingPlaceMode.Near);
                    }
                }
                if (!parent.Destroyed) parent.Destroy(DestroyMode.Vanish);
                return;
            }

            parent.Destroy(DestroyMode.Vanish);
        }
    }
}
