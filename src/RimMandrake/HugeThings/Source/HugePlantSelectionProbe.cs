using System.Collections.Generic;
using System.Text;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.HugeThings
{
    /// <summary>RIMMANDRAKE_SPLIT_HUGETHINGS_PLANT_AND_TITAN_PROMISES (PLANT_selection): a read-only bridge probe that answers
    /// "does a click anywhere on the picture select the plant?" through the game's own click path, not the mod's numbers.
    ///
    ///   jawa/static_call RimMandrake.HugeThings.HugePlantSelectionProbe ClickPicture current|x,z
    ///
    /// The picture is replayed from vanilla Plant.Print (1.6, read via RimSage): seed Position.GetHashCode(), the 0.05
    /// jitter draw, quad side graphicData.drawSize.x * plant.visualSizeRange.LerpThroughRange(growth) centred on
    /// TrueCenter and bottom-anchored on the root's south edge, then flipUv = Rand.Bool and the Graphic_Random variant
    /// Rand.Range(0, count). The visible part of that quad is the variant's art-measured opaque box (alpha >= 0.5, from
    /// measure_huge_plant_masks.py), mirrored when flipped. Each cell whose centre lies on it is clicked with the
    /// Selector's own parameters (GenUI.ThingsUnderMouse at the cell centre, mustBeSelectable, radius 1): a hit is the
    /// plant in the list, "first" is the plant at the head of it (what one click selects when nothing else is there).
    /// A one-cell ring of cells lying wholly outside the drawn quad is clicked too: any hit there is overreach. Changes nothing.</summary>
    public static class HugePlantSelectionProbe
    {
        public static string ClickPicture(Map map, IntVec3 root)
        {
            if (map == null || map != Find.CurrentMap) return "FAIL map is not the current map (the click path reads Find.CurrentMap)";
            if (!root.InBounds(map)) return "FAIL cell out of bounds";
            Plant plant = null;
            foreach (Thing t in root.GetThingList(map))
                if (t is Plant p && p.Position == root && p.TryGetComp<CompHugeFootprint>() != null) { plant = p; break; }
            if (plant == null) return "FAIL no huge plant rooted at " + root;

            float visual = plant.def.plant.visualSizeRange.LerpThroughRange(plant.Growth);
            float side = plant.def.graphicData.drawSize.x * visual;
            bool flip;
            int variant = -1;
            Vector3 c = plant.TrueCenter();
            Rand.PushState();
            try
            {
                Rand.Seed = root.GetHashCode();
                c += Gen.RandomHorizontalVector(0.05f);
                if (c.z - visual / 2f < root.z) c.z = root.z + visual / 2f;
                flip = Rand.Bool;
                if (plant.Graphic is Graphic_Random gr && gr.SubGraphicsCount > 0) variant = Rand.Range(0, gr.SubGraphicsCount);
            }
            finally { Rand.PopState(); }
            float qx0 = c.x - side / 2f, qz0 = c.z - side / 2f;

            string tex = null;
            if (variant >= 0 && plant.Graphic is Graphic_Random g2)
            {
                string path = g2.SubGraphicAtIndex(variant).path ?? "";
                int slash = path.LastIndexOf('/');
                tex = slash >= 0 ? path.Substring(slash + 1) : path;
            }
            RM_HugePlantExtension ext = plant.def.GetModExtension<RM_HugePlantExtension>();
            HugePlantVariant v = null;
            if (ext != null)
                foreach (HugePlantVariant cand in ext.variants)
                    if (cand.texture == tex) { v = cand; break; }
            if (v == null) return "FAIL no measured opaque box for drawn variant '" + tex + "' (index " + variant + ")";
            float u0 = flip ? 1f - v.opaqueMax.x : v.opaqueMin.x, u1 = flip ? 1f - v.opaqueMin.x : v.opaqueMax.x;
            float px0 = qx0 + u0 * side, px1 = qx0 + u1 * side, pz0 = qz0 + v.opaqueMin.y * side, pz1 = qz0 + v.opaqueMax.y * side;

            TargetingParameters click = new TargetingParameters
            {
                mustBeSelectable = true, canTargetPawns = true, canTargetBuildings = true, canTargetItems = true,
                mapObjectTargetsMustBeAutoAttackable = false
            };
            int cells = 0, hits = 0, first = 0, ring = 0, ringHits = 0;
            var missed = new List<string>();
            var notFirst = new Dictionary<string, int>();
            int ax0 = Mathf.FloorToInt(qx0) - 1, ax1 = Mathf.CeilToInt(qx0 + side), az0 = Mathf.FloorToInt(qz0) - 1, az1 = Mathf.CeilToInt(qz0 + side);
            for (int z = az0; z <= az1; z++)
            {
                for (int x = ax0; x <= ax1; x++)
                {
                    IntVec3 cell = new IntVec3(x, 0, z);
                    if (!cell.InBounds(map)) continue;
                    float cx = x + 0.5f, cz = z + 0.5f;
                    bool onPicture = cx >= px0 && cx <= px1 && cz >= pz0 && cz <= pz1;
                    bool outsideQuad = x + 1 <= qx0 || x >= qx0 + side || z + 1 <= qz0 || z >= qz0 + side;   // wholly outside
                    if (!onPicture && !outsideQuad) continue;
                    List<Thing> under = GenUI.ThingsUnderMouse(cell.ToVector3Shifted(), 1f, click);
                    int at = under.IndexOf(plant);
                    if (onPicture)
                    {
                        cells++;
                        if (at >= 0) hits++; else if (missed.Count < 12) missed.Add(x + "," + z);
                        if (at == 0) first++;
                        else if (at > 0)
                        {
                            string head = under[0].def.defName;
                            notFirst[head] = notFirst.TryGetValue(head, out int n) ? n + 1 : 1;
                        }
                    }
                    else { ring++; if (at >= 0) ringHits++; }
                }
            }
            var sb = new StringBuilder();
            sb.Append("plant=").Append(plant.ThingID).Append(" growth=").Append(plant.Growth.ToString("0.###"))
              .Append(" selectionOn=").Append(RM_HugeThingsSettings.PlantSelectionActive)
              .Append(" variant=").Append(tex).Append(" flip=").Append(flip)
              .Append(" quad=").Append(qx0.ToString("0.##")).Append(',').Append(qz0.ToString("0.##")).Append(" side=").Append(side.ToString("0.##"))
              .Append(" picture=").Append(px0.ToString("0.##")).Append(',').Append(pz0.ToString("0.##")).Append("..")
              .Append(px1.ToString("0.##")).Append(',').Append(pz1.ToString("0.##"))
              .Append(" selectRect=").Append(plant.CustomRectForSelector?.ToString() ?? "null")
              .Append(" pictureCells=").Append(cells).Append(" hits=").Append(hits).Append(" first=").Append(first)
              .Append(" missed=").Append(missed.Count == 0 ? "none" : string.Join(";", missed))
              .Append(" ringCells=").Append(ring).Append(" ringHits=").Append(ringHits)
              .Append(" aheadOfPlant=");
            if (notFirst.Count == 0) sb.Append("none");
            else foreach (var kv in notFirst) sb.Append(kv.Key).Append('x').Append(kv.Value).Append(';');
            return sb.ToString();
        }
    }
}
