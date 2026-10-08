using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace RimMandrake.AcousticScanner
{
    // GRAVSHIP_ACOUSTIC_SCANNER_1 — the TEMPORARY overlay a pulse leaves behind.
    // Holds only bands (never hit cells), draws them while they last, and forgets
    // them on expiry. Deliberately not saved: a reading is an ephemeral sound
    // picture, and a reload simply ends it. Auto-instantiated per map.
    public class RM_MapComponent_AcousticReading : MapComponent
    {
        private List<RM_AcousticBand> bands = new List<RM_AcousticBand>();
        private List<Color> colors = new List<Color>();
        private List<string> labels = new List<string>();
        private int expiresTick = -1;

        private static readonly float[] FillAlpha = { 0.08f, 0.16f, 0.26f };
        private static readonly float[] EdgeAlpha = { 0.35f, 0.6f, 0.9f };

        public RM_MapComponent_AcousticReading(Map map) : base(map) { }

        public bool Active => RM_AcousticKernel.OverlayActive(expiresTick, Find.TickManager.TicksGame, bands.Count);

        public void SetReading(List<RM_AcousticBand> newBands, List<Color> targetColors,
            List<string> targetLabels, int durationTicks)
        {
            bands = newBands ?? new List<RM_AcousticBand>();
            colors = targetColors ?? new List<Color>();
            labels = targetLabels ?? new List<string>();
            expiresTick = RM_AcousticKernel.OverlayExpiry(Find.TickManager.TicksGame, durationTicks);
        }

        public void Clear()
        {
            bands.Clear();
            expiresTick = -1;
        }

        public override void MapComponentUpdate()
        {
            if (expiresTick < 0) return;
            if (!Active) { Clear(); return; }
            if (Find.CurrentMap != map || WorldRendererUtility.WorldRendered) return;

            // Fill: one scaled quad per band. Edges: one instanced outline per (target, tier).
            var edgeGroups = new Dictionary<int, List<IntVec3>>();
            for (int i = 0; i < bands.Count; i++)
            {
                RM_AcousticBand band = bands[i];
                Color baseCol = ColorFor(band.targetIndex);
                int ti = (int)band.tier;
                Color fill = new Color(baseCol.r, baseCol.g, baseCol.b, FillAlpha[ti]);
                Material mat = MaterialPool.MatFrom(BaseContent.WhiteTex, ShaderDatabase.Transparent, fill);
                Vector3 center = band.rect.CenterVector3;
                center.y = AltitudeLayer.MetaOverlays.AltitudeFor();
                Matrix4x4 m = Matrix4x4.TRS(center, Quaternion.identity,
                    new Vector3(band.rect.Width, 1f, band.rect.Height));
                Graphics.DrawMesh(MeshPool.plane10, m, mat, 0);

                int key = band.targetIndex * 4 + ti;
                if (!edgeGroups.TryGetValue(key, out List<IntVec3> cells))
                {
                    cells = new List<IntVec3>();
                    edgeGroups[key] = cells;
                }
                foreach (IntVec3 c in band.rect) cells.Add(c);
            }
            foreach (KeyValuePair<int, List<IntVec3>> kv in edgeGroups)
            {
                Color baseCol = ColorFor(kv.Key / 4);
                GenDraw.DrawFieldEdges(kv.Value, new Color(baseCol.r, baseCol.g, baseCol.b, EdgeAlpha[kv.Key % 4]));
            }
        }

        public override void MapComponentOnGUI()
        {
            if (!Active || Find.CurrentMap != map || WorldRendererUtility.WorldRendered) return;
            // One label per strong band; moderate/faint bands stay unlabeled to keep the map legible.
            for (int i = 0; i < bands.Count; i++)
            {
                RM_AcousticBand band = bands[i];
                if (band.tier != RM_AcousticTier.Strong) continue;
                if (band.targetIndex < 0 || band.targetIndex >= labels.Count) continue;
                Vector3 c = band.rect.CenterVector3;
                GenMapUI.DrawText(new Vector2(c.x, c.z), labels[band.targetIndex], ColorFor(band.targetIndex));
            }
        }

        private Color ColorFor(int targetIndex)
        {
            return targetIndex >= 0 && targetIndex < colors.Count ? colors[targetIndex] : Color.white;
        }
    }
}
