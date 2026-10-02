using System.Text;
using RimWorld;
using Verse;

namespace RimMandrake.TerminalBiomes
{
    // CHILL_CRYOPONICS_GROWER_1 — a sealed, powered vat that carries its own
    // cryogenic propane bath, so the Chill's six deep-bed plants (sowTag
    // "RM_ChillBed") grow in it anywhere, not only on the liquid-propane floor.
    //
    // It is a plain Building_PlantGrower for sowing/harvesting. The ONLY thing
    // it adds is a predicate, ActiveCryoAt, that RM_Patch_ChillGrowers reads to
    // lift the three temperature/terrain checks that would otherwise reject
    // those plants on a warm map (the plants' maxGrowthTemperature is -20 C).
    // The bath runs on power: an unpowered vat (or the Mod Settings gate off)
    // is just an ordinary bed and the plants fall back to the surroundings.
    public class RM_Building_CryoGrower : Building_PlantGrower
    {
        public bool CryoActive
        {
            get
            {
                if (!RM_TerminalBiomesSettings.ChillCryoponicsActive)
                {
                    return false;
                }
                CompPowerTrader power = GetComp<CompPowerTrader>();
                return power == null || power.PowerOn;
            }
        }

        public override string GetInspectString()
        {
            StringBuilder sb = new StringBuilder(base.GetInspectString());
            if (sb.Length > 0)
            {
                sb.AppendLine();
            }
            sb.Append(CryoActive
                ? "Cryogenic bath: running"
                : "Cryogenic bath: offline (needs power)");
            return sb.ToString();
        }

        /// <summary>True when an active cryoponics vat covers this cell.</summary>
        public static bool ActiveCryoAt(IntVec3 c, Map map)
        {
            if (map == null || !c.InBounds(map))
            {
                return false;
            }
            var list = map.thingGrid.ThingsListAtFast(c);
            for (int i = 0; i < list.Count; i++)
            {
                if (list[i] is RM_Building_CryoGrower g && g.CryoActive)
                {
                    return true;
                }
            }
            return false;
        }

        /// <summary>True when either Chill grower (vat or floor bed) covers this cell.</summary>
        public static bool ChillGrowerAt(IntVec3 c, Map map)
        {
            if (map == null || !c.InBounds(map))
            {
                return false;
            }
            var list = map.thingGrid.ThingsListAtFast(c);
            for (int i = 0; i < list.Count; i++)
            {
                if (list[i] is RM_Building_CryoGrower)
                {
                    return true;
                }
                if (list[i] is Building_PlantGrower g && g.def.building != null
                    && g.def.building.sowTag == "RM_ChillBed")
                {
                    return true;
                }
            }
            return false;
        }
    }
}
