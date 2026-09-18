using System.Collections.Generic;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // ROT_DECAY_HARVEST_1 ("the gut digests"). Generic on
    // purpose, same idiom as RM_MapComponent_DryRooms in this assembly: any
    // ThingDef anywhere can opt in by carrying RM_LivingProduceExtension
    // (currently patched onto RotSporeKit's two fungal food crops,
    // RUT_Glimmerslime / RUT_RawDulcis — see
    // UtinniPatches/Patches/RotDecayHarvest_LivingProduce.xml), and this
    // component is a harmless no-op if nothing on the map carries it.
    //
    // Fully re-derived from currently spawned things every sweep, same
    // reasoning RM_MapComponent_DryRooms already gives: no Scribe state
    // owed, a load just re-establishes it within one TickInterval.
    public class RM_MapComponent_LivingProduce : MapComponent
    {
        // Rare on purpose (the spec's own word) — this only needs to keep a
        // freezer roughly in equilibrium, not react tick-by-tick. 2000 ticks
        // (~33 game-seconds) is INVENTED; RM_LivingProduceExtension.heatPerUnit's
        // own header derives its default FROM this exact interval, so if this
        // number ever changes, that default must be re-derived too.
        private const int TickInterval = 2000;

        public RM_MapComponent_LivingProduce(Map map)
            : base(map)
        {
        }

        public override void MapComponentTick()
        {
            base.MapComponentTick();

            if (!RM_EnvironmentalHazardsSettings.livingProduceHeatEnabled)
            {
                return;
            }

            int tick = Find.TickManager.TicksGame;
            if (tick % TickInterval != 0)
            {
                return;
            }

            PushRoomHeat();
        }

        private void PushRoomHeat()
        {
            Dictionary<Room, float> energyByRoom = null;
            List<Thing> things = map.listerThings.AllThings;
            for (int i = 0; i < things.Count; i++)
            {
                Thing t = things[i];
                if (t.stackCount <= 0)
                {
                    continue;
                }

                RM_LivingProduceExtension ext = t.def.GetModExtension<RM_LivingProduceExtension>();
                if (ext == null)
                {
                    continue;
                }

                Room room = t.GetRoom();
                if (room == null)
                {
                    continue; // Room.PushHeat itself no-ops on an outdoor room; skip the lookup work for it here too
                }

                float energy = t.stackCount * ext.heatPerUnit;
                energyByRoom ??= new Dictionary<Room, float>();
                energyByRoom.TryGetValue(room, out float existing);
                energyByRoom[room] = existing + energy;
            }

            if (energyByRoom == null)
            {
                return;
            }

            foreach (KeyValuePair<Room, float> kv in energyByRoom)
            {
                kv.Key.PushHeat(kv.Value);
            }
        }
    }
}
