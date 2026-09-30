using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    /// <summary>
    /// SOLAR_HEAT_EXPOSURE_1 §6 — the sun-load bar (design §6.1 "Show the
    /// budget"). Because sun heat feeds vanilla heat, the load IS the pawn's
    /// Heatstroke severity: the bar fills with it, and the line under it says
    /// what the sun is adding where the pawn stands right now (or that it is
    /// in shade). Shown for a single selected pawn on a sun-heat map.
    /// </summary>
    [StaticConstructorOnStartup]
    public class RM_Gizmo_SunLoad : Gizmo
    {
        private static readonly Texture2D FillTex = SolidColorMaterials.NewSolidColorTexture(new Color(0.85f, 0.45f, 0.15f));
        private static readonly Texture2D EmptyTex = SolidColorMaterials.NewSolidColorTexture(new Color(0.15f, 0.12f, 0.10f));

        private readonly Pawn pawn;
        private readonly RM_MapComponent_ShadeGrid grid;

        public RM_Gizmo_SunLoad(Pawn pawn, RM_MapComponent_ShadeGrid grid)
        {
            this.pawn = pawn;
            this.grid = grid;
            Order = -90f;
        }

        public override float GetWidth(float maxWidth)
        {
            return Mathf.Min(140f, maxWidth);
        }

        public override GizmoResult GizmoOnGUI(Vector2 topLeft, float maxWidth, GizmoRenderParms parms)
        {
            Rect rect = new Rect(topLeft.x, topLeft.y, GetWidth(maxWidth), 75f);
            Widgets.DrawWindowBackground(rect);
            Rect inner = rect.ContractedBy(6f);

            Hediff heat = pawn.health?.hediffSet?.GetFirstHediffOfDef(HediffDefOf.Heatstroke);
            float load = heat?.Severity ?? 0f;
            float offset = grid != null ? RM_SunHeatPatches.SunOffsetFor(pawn, grid) : 0f;

            Text.Font = GameFont.Tiny;
            Text.Anchor = TextAnchor.UpperLeft;
            Widgets.Label(new Rect(inner.x, inner.y, inner.width, 18f), "Sun load");

            Rect bar = new Rect(inner.x, inner.y + 20f, inner.width, 18f);
            Widgets.FillableBar(bar, Mathf.Clamp01(load), FillTex, EmptyTex, true);
            Text.Anchor = TextAnchor.MiddleCenter;
            Widgets.Label(bar, load.ToStringPercent());

            Text.Anchor = TextAnchor.UpperLeft;
            string now = offset > 0.5f ? "In sun: +" + offset.ToString("0") + "°C" : "In shade";
            Widgets.Label(new Rect(inner.x, inner.y + 42f, inner.width, 18f), now);
            Text.Font = GameFont.Small;

            if (Mouse.IsOver(rect))
            {
                Widgets.DrawHighlight(rect);
                RM_SunHeatExtension ext = grid?.HeatExtension;
                string kind = ext == null ? "" : ext.heatKind == RM_HeatKind.ambient
                    ? "Here the heat is in the air: shade does nothing, only insulation or an enclosed room helps."
                    : ext.heatKind == RM_HeatKind.lowSun
                        ? "Here the sun is low: only the lee shadow of a wall, rock or shield protects; a roof overhead does not."
                        : "Here roofs and shadows both protect.";
                TooltipHandler.TipRegion(rect, "Sun load is this creature's heatstroke. Standing in the sun adds "
                    + "to the temperature it feels, and the smaller it is, the faster it heats. " + kind);
            }
            return new GizmoResult(GizmoState.Clear);
        }
    }
}
