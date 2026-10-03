using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.MessyConduit.Aerial
{
    /// <summary>On every anchor def: hidden from the architect menu while aerial lines are switched off; while placing,
    /// the range ring and a preview line to the anchor auto-link would choose (design 2.4).</summary>
    public class PlaceWorker_AerialRange : PlaceWorker
    {
        public override bool IsBuildDesignatorVisible(BuildableDef def) => AerialSettings.enabled;

        public override void DrawGhost(ThingDef def, IntVec3 center, Rot4 rot, Color ghostCol, Thing thing = null)
        {
            Map map = Find.CurrentMap;
            if (map == null) return;
            float r = Mathf.Min(AerialSettings.Range, GenRadial.MaxRadialPatternRadius - 0.01f);
            GenDraw.DrawRadiusRing(center, r);
            if (!AerialSettings.autoLink) return;
            RM_MapComponent_Aerial comp = map.GetComponent<RM_MapComponent_Aerial>();
            if (comp == null) return;
            var self = new AnchorInfo
            {
                Id = -1, X = center.x, Z = center.z, Faction = Faction.OfPlayer.loadID,
                MaxLinks = def.GetModExtension<AerialAnchorExtension>()?.maxLinks ?? 4, Roofed = map.roofGrid.Roofed(center),
            };
            var others = comp.Anchors.Where(a => a.Position != center).ToList();
            int pick = AerialMath.AutoLinkPick(self, others.Select(o => o.Info()).ToList(), AerialSettings.Range);
            if (pick < 0) return;
            CompAerialAnchor o2 = others.First(o => o.thingIDNumber == pick);
            float y = AltitudeLayer.MetaOverlays.AltitudeFor();
            GenDraw.DrawLineBetween(new Vector3(center.x + 0.5f, y, center.z + 0.5f), new Vector3(o2.Position.x + 0.5f, y, o2.Position.z + 0.5f), SimpleColor.White, 0.08f);
        }
    }

    /// <summary>The wall bracket stands against a wall: the cell BEHIND it (its rotation's opposite) must hold a built,
    /// impassable, non-rock edifice. (No vanilla 1.6 wall-attachment API is used: the bracket is an ordinary 1x1
    /// building drawn against the wall face.)</summary>
    public class PlaceWorker_AerialWallBracket : PlaceWorker
    {
        public override AcceptanceReport AllowsPlacing(BuildableDef checkingDef, IntVec3 loc, Rot4 rot, Map map, Thing thingToIgnore = null, Thing thing = null)
        {
            IntVec3 behind = loc + rot.Opposite.FacingCell;
            if (!behind.InBounds(map)) return "Must stand against a wall.";
            Building ed = behind.GetEdifice(map);
            if (ed == null || ed.def.passability != Traversability.Impassable || (ed.def.building != null && ed.def.building.isNaturalRock))
                return "Must stand against a wall (the arrow points away from it).";
            return AcceptanceReport.WasAccepted;
        }
    }

    /// <summary>The power-tap clamp must bite another faction's transmitter (conduit, battery, generator ...) on a
    /// cardinal side. Hidden from the architect menu when taps or aerial lines are switched off.</summary>
    public class PlaceWorker_PowerTap : PlaceWorker
    {
        public override bool IsBuildDesignatorVisible(BuildableDef def) => AerialSettings.enabled && AerialSettings.tapsEnabled;

        public override AcceptanceReport AllowsPlacing(BuildableDef checkingDef, IntVec3 loc, Rot4 rot, Map map, Thing thingToIgnore = null, Thing thing = null)
        {
            if (!AerialSettings.tapsEnabled) return "Power taps are switched off in Mod Settings.";
            foreach (IntVec3 c in GenAdj.CellsAdjacentCardinal(loc, rot, IntVec2.One))
            {
                if (!c.InBounds(map)) continue;
                Building tr = c.GetTransmitter(map);
                if (tr != null && tr.Faction != Faction.OfPlayer && tr.PowerComp?.PowerNet != null) return AcceptanceReport.WasAccepted;
            }
            return "Must bite someone else's power line: place it next to another faction's conduit or power building.";
        }
    }
}
