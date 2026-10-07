using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.Scarlands
{
    // WARSCAR_AEROSOL_SCREEN_1 part 9: glower shielding. Never run in game.
    //  * RM_CompGlowerShield (on RM_GlowerShieldPanel) registers itself; every pawn in the panel's room reads
    //    +RoomResistance ToxicEnvironmentResistance through RM_StatPart_GlowerShield (patched onto the stat's
    //    <parts> in Patches/RM_GlowerShielding.xml), and room toxic damage (ToxicUtility.DoPawnToxicDamage, which
    //    is also what tox gas calls via GasUtility.PawnGasEffectsTickInterval) is halved.
    //  * RM_GlowerPlate is plain apparel (equippedStatOffsets in XML); no C#.
    // Numbers INVENTED: room offset 0.35 stacks additively with the plate's 0.5 (stat caps at 1).
    public class RM_CompProperties_GlowerShield : CompProperties
    {
        public float resistanceOffset = 0.35f;
        public float gasDamageFactor = 0.5f;
        public RM_CompProperties_GlowerShield() { compClass = typeof(RM_CompGlowerShield); }
    }

    public class RM_CompGlowerShield : ThingComp
    {
        static readonly List<RM_CompGlowerShield> live = new List<RM_CompGlowerShield>();
        public RM_CompProperties_GlowerShield Props => (RM_CompProperties_GlowerShield)props;

        // Thing.Map is Find.Maps[index]: a panel left registered by a previous game would alias onto the new game's
        // map at the same index. Compare the registered Map reference instead, and prune stale entries on spawn.
        private Map registeredMap;

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            live.RemoveAll(s => s == null || s.registeredMap == null || !Find.Maps.Contains(s.registeredMap)
                || !s.parent.Spawned || s.parent.Map != s.registeredMap);
            registeredMap = parent.Map;
            if (!live.Contains(this)) live.Add(this);
        }

        public override void PostDeSpawn(Map map, DestroyMode mode = DestroyMode.Vanish)
        {
            live.Remove(this);
            registeredMap = null;
            base.PostDeSpawn(map, mode);
        }

        // Strongest panel serving the pawn's room, or null. Empty registry exits at once (the stat is read constantly).
        public static RM_CompGlowerShield For(Pawn p)
        {
            if (live.Count == 0 || !RM_WarscarSettings.glowerShieldingEnabled) return null;
            if (p == null || !p.Spawned) return null;
            Room room = p.GetRoom();
            if (room == null || room.PsychologicallyOutdoors) return null;
            RM_CompGlowerShield best = null;
            for (int i = 0; i < live.Count; i++)
            {
                RM_CompGlowerShield c = live[i];
                if (c.parent?.Spawned != true || c.registeredMap != p.Map) continue;
                if (c.parent.GetRoom() != room) continue;
                if (best == null || c.Props.resistanceOffset > best.Props.resistanceOffset) best = c;
            }
            return best;
        }

        public override string CompInspectStringExtra()
        {
            if (!RM_WarscarSettings.glowerShieldingEnabled) return "Glower shielding: switched off in mod settings.";
            return "Glower shielding: pawns in this room +" + Props.resistanceOffset.ToStringPercent()
                + " toxic environment resistance; toxic damage x" + Props.gasDamageFactor.ToString("0.0#") + ".";
        }
    }

    public class RM_StatPart_GlowerShield : StatPart
    {
        public override void TransformValue(StatRequest req, ref float val)
        {
            if (!(req.Thing is Pawn p)) return;
            RM_CompGlowerShield c = RM_CompGlowerShield.For(p);
            if (c != null) val += c.Props.resistanceOffset;
        }

        public override string ExplanationPart(StatRequest req)
        {
            if (!(req.Thing is Pawn p)) return null;
            RM_CompGlowerShield c = RM_CompGlowerShield.For(p);
            return c == null ? null : "Glower shield panel in this room: +" + c.Props.resistanceOffset.ToStringPercent();
        }
    }

    // Room toxic damage halved (tox gas included).
    [HarmonyPatch(typeof(ToxicUtility), nameof(ToxicUtility.DoPawnToxicDamage))]
    public static class RM_GlowerShieldPatches_ToxicDamage
    {
        [HarmonyPrefix]
        public static void Prefix(Pawn p, ref float extraFactor)
        {
            RM_CompGlowerShield c = RM_CompGlowerShield.For(p);
            if (c != null) extraFactor *= c.Props.gasDamageFactor;
        }
    }

    // Wall-adjacent: at least one cardinal neighbour is an impassable edifice (a wall).
    public class RM_PlaceWorker_WallAdjacent : PlaceWorker
    {
        public override AcceptanceReport AllowsPlacing(BuildableDef checkingDef, IntVec3 loc, Rot4 rot, Map map, Thing thingToIgnore = null, Thing thing = null)
        {
            for (int i = 0; i < 4; i++)
            {
                IntVec3 c = loc + GenAdj.CardinalDirections[i];
                if (!c.InBounds(map)) continue;
                Building e = c.GetEdifice(map);
                if (e != null && e.def.passability == Traversability.Impassable && e.def.Fillage == FillCategory.Full) return true;
            }
            return "Must be placed against a wall.";
        }
    }
}
