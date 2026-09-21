using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // VENOMVINE_CONTACT_VENOM_BUILD_1. XML shape:
    //
    //   <ThingDef ParentName="PlantBase">
    //     <defName>RM_Venomvine</defName>
    //     ...
    //     <comps>
    //       <li Class="RimMandrake.EnvironmentalHazards.CompProperties_ContactVenom">
    //         <damageDef>RM_VenomvineScratch</damageDef>
    //         <damageAmount>3</damageAmount>
    //         <armorPenetration>0.05</armorPenetration>
    //         <contactIntervalTicks>2500</contactIntervalTicks>
    //         <bodyHeight>Bottom</bodyHeight>
    //       </li>
    //     </comps>
    //   </ThingDef>
    //
    // Generic on purpose (design §1b "class shape"): the shrubland thicket
    // form and any later thorn plant reuse this with different numbers, and
    // nothing here names a plant, a biome or a campaign.
    public class CompProperties_ContactVenom : CompProperties
    {
        // The scratch dealt on contact. A DamageDef whose own XML carries the
        // additionalHediffs → this is where the venom lives; no C# here ever
        // touches a HediffDef by name. Null falls back to vanilla Scratch,
        // which is a plain injury with no venom — a legible degradation, not
        // a crash.
        public DamageDef damageDef;

        public float damageAmount = 3f;
        public float armorPenetration = 0.05f;

        // One in-game hour. Also the pruning window: a pawn out of contact
        // for longer than this is forgotten entirely.
        public int contactIntervalTicks = 2500;

        // Thorns take the legs (design §1b "damage shape").
        public BodyPartHeight bodyHeight = BodyPartHeight.Bottom;

        public CompProperties_ContactVenom()
        {
            compClass = typeof(CompContactVenom);
        }
    }

    // The plant-side half. It does NOTHING on tick and must never depend on
    // ticking: PlantBase sets tickerType Long (every 2000 ticks, ~33 s) and a
    // pawn crossing a cell is there for ~10-20 ticks, so a comp that watched
    // its own cell from CompTick would miss essentially every crossing
    // (MEASURED, design §1a). All it does is tell the map's
    // MapComponent_ContactVenom which cell it holds; the MapComponent does
    // the sampling at a cadence of its own, O(pawns) and independent of how
    // many vines are standing.
    public class CompContactVenom : ThingComp
    {
        public CompProperties_ContactVenom Props => (CompProperties_ContactVenom)props;

        // The cell actually registered, cached rather than re-read from
        // parent.Position at deregistration time: Thing.DeSpawn clears the
        // thing's map/position state around the comp callback, so the only
        // cell we can be sure of removing is the one we put in.
        private IntVec3 registeredCell = IntVec3.Invalid;

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            Register(parent.Map);
        }

        public override void PostDeSpawn(Map map, DestroyMode mode = DestroyMode.Vanish)
        {
            base.PostDeSpawn(map, mode);
            Deregister(map);
        }

        private void Register(Map map)
        {
            if (map == null)
            {
                return;
            }

            MapComponent_ContactVenom tracker = map.GetComponent<MapComponent_ContactVenom>();
            if (tracker == null)
            {
                return;
            }

            registeredCell = parent.Position;
            tracker.RegisterCell(registeredCell, this);
        }

        private void Deregister(Map map)
        {
            if (map == null || !registeredCell.IsValid)
            {
                return;
            }

            map.GetComponent<MapComponent_ContactVenom>()?.DeregisterCell(registeredCell, this);
            registeredCell = IntVec3.Invalid;
        }
    }
}
