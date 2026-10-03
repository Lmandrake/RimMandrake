using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace RimMandrake.Utinni.Atlas
{
    // The Atlas tab: the Utinni drawn as a ship, every entry a running light on her
    // hull (owner ruling Q1, 2026-10-02). Click a lamp to bring up its card; click
    // the card to flip a riddle over to its hint. A lit lamp's card offers the lore
    // as a click-through, never pushed (ruling Q4).
    public class MainTabWindow_Atlas : MainTabWindow
    {
        private const float CardPanelWidth = 340f;
        private const float LampSize = 20f;
        private const float FlipSeconds = 0.32f;

        // Palette: warm 70s browns on deep space (owner likes the brown palette).
        private static readonly Color Space = new Color(0.07f, 0.055f, 0.045f);
        private static readonly Color Star = new Color(0.85f, 0.78f, 0.62f, 0.55f);
        private static readonly Color HullFill = new Color(0.36f, 0.24f, 0.15f);
        private static readonly Color HullEdge = new Color(0.76f, 0.54f, 0.29f);
        private static readonly Color ForeignPlate = new Color(0.30f, 0.30f, 0.27f); // the arm from another wreck
        private static readonly Color DeadPlate = new Color(0.25f, 0.18f, 0.13f);
        private static readonly Color BayFill = new Color(0.43f, 0.29f, 0.18f);
        private static readonly Color HeartCold = new Color(0.32f, 0.42f, 0.48f);
        private static readonly Color LampOff = new Color(0.16f, 0.12f, 0.09f);
        private static readonly Color LampOffEdge = new Color(0.55f, 0.42f, 0.28f);
        private static readonly Color LampLit = new Color(1f, 0.80f, 0.40f);
        private static readonly Color LampAbsent = new Color(0.22f, 0.22f, 0.22f);
        private static readonly Color CardFace = new Color(0.20f, 0.15f, 0.11f);
        private static readonly Color CardBack = new Color(0.14f, 0.18f, 0.20f);
        private static readonly Color CardEdge = new Color(0.76f, 0.54f, 0.29f);

        private AtlasEntryDef selected;
        private readonly HashSet<AtlasEntryDef> flipped = new HashSet<AtlasEntryDef>();
        private float flipStart = -10f;
        private AtlasEntryDef flipping;

        private List<Vector2> stars;

        public override Vector2 RequestedTabSize => new Vector2(1180f, 720f);

        private static GameComponent_Atlas Comp => GameComponent_Atlas.Instance;

        private static IEnumerable<AtlasEntryDef> Visible
        {
            get
            {
                foreach (AtlasEntryDef d in DefDatabase<AtlasEntryDef>.AllDefsListForReading)
                {
                    if (!AtlasSettings.CategoryEnabled(d.category)) continue;
                    if (!AtlasSettings.showUnavailable && !d.Available) continue;
                    yield return d;
                }
            }
        }

        public override void DoWindowContents(Rect inRect)
        {
            Rect header = new Rect(inRect.x, inRect.y, inRect.width, 34f);
            DrawHeader(header);

            Rect body = new Rect(inRect.x, header.yMax + 4f, inRect.width, inRect.height - header.height - 4f);
            Rect canvas = new Rect(body.x, body.y, body.width - CardPanelWidth - 10f, body.height);
            Rect cardPanel = new Rect(canvas.xMax + 10f, body.y, CardPanelWidth, body.height);

            DrawShip(canvas);
            DrawCardPanel(cardPanel);
        }

        private void DrawHeader(Rect r)
        {
            Text.Font = GameFont.Medium;
            Text.Anchor = TextAnchor.MiddleLeft;
            Widgets.Label(r, "RUT_Atlas_Title".Translate());
            Text.Anchor = TextAnchor.MiddleRight;
            Text.Font = GameFont.Small;
            if (AtlasSettings.showCounters)
            {
                List<AtlasEntryDef> avail = Visible.Where(d => d.Available).ToList();
                int lit = avail.Count(d => Comp != null && Comp.IsDiscovered(d));
                Widgets.Label(r, "RUT_Atlas_Counter".Translate(lit, avail.Count));
            }
            Text.Anchor = TextAnchor.UpperLeft;
        }

        private void DrawShip(Rect canvas)
        {
            Widgets.DrawBoxSolid(canvas, Space);
            DrawStars(canvas);

            // Silhouette.
            AtlasShipLayout.FillPolygon(canvas, AtlasShipLayout.EngineBlock, DeadPlate);
            AtlasShipLayout.FillPolygon(canvas, AtlasShipLayout.DorsalSpine, HullFill);
            AtlasShipLayout.FillPolygon(canvas, AtlasShipLayout.VentralPods, HullFill);
            AtlasShipLayout.FillPolygon(canvas, AtlasShipLayout.UpperMandible, ForeignPlate);
            AtlasShipLayout.FillPolygon(canvas, AtlasShipLayout.LowerMandible, DeadPlate);
            AtlasShipLayout.FillPolygon(canvas, AtlasShipLayout.Hull, HullFill);
            foreach (AtlasCategory c in new[] { AtlasCategory.Places, AtlasCategory.Resources, AtlasCategory.Gods })
                Widgets.DrawBoxSolid(AtlasShipLayout.ToCanvas(canvas, AtlasShipLayout.RegionFor(c)).ExpandedBy(4f), BayFill);

            AtlasShipLayout.OutlinePolygon(canvas, AtlasShipLayout.EngineBlock, HullEdge);
            AtlasShipLayout.OutlinePolygon(canvas, AtlasShipLayout.DorsalSpine, HullEdge);
            AtlasShipLayout.OutlinePolygon(canvas, AtlasShipLayout.VentralPods, HullEdge);
            AtlasShipLayout.OutlinePolygon(canvas, AtlasShipLayout.UpperMandible, HullEdge);
            AtlasShipLayout.OutlinePolygon(canvas, AtlasShipLayout.LowerMandible, HullEdge);
            AtlasShipLayout.OutlinePolygon(canvas, AtlasShipLayout.Hull, HullEdge);

            // Sensor vanes on the spine.
            for (int i = 0; i < 6; i++)
            {
                float x = 0.31f + i * 0.05f;
                Widgets.DrawLine(AtlasShipLayout.ToCanvas(canvas, new Vector2(x, 0.22f)),
                    AtlasShipLayout.ToCanvas(canvas, new Vector2(x - 0.015f, 0.14f)), HullEdge, 1.5f);
            }
            // Pod seams.
            for (int i = 1; i < 4; i++)
            {
                float x = 0.25f + i * 0.08f;
                Widgets.DrawLine(AtlasShipLayout.ToCanvas(canvas, new Vector2(x, 0.70f)),
                    AtlasShipLayout.ToCanvas(canvas, new Vector2(x, 0.80f)), HullEdge, 1f);
            }

            List<AtlasEntryDef> visible = Visible.ToList();
            int availableCount = visible.Count(d => d.Available);
            int litCount = visible.Count(d => d.Available && Comp != null && Comp.IsDiscovered(d));
            float progress = availableCount == 0 ? 0f : litCount / (float)availableCount;

            // Reliquary heart: warms from carbonite-cold to engine-gold as the Atlas fills.
            Vector2 heart = AtlasShipLayout.ToCanvas(canvas, AtlasShipLayout.HeartCentre);
            float hr = AtlasShipLayout.HeartRadius * canvas.height;
            AtlasShipLayout.FillCircle(heart, hr + 4f, HullEdge);
            AtlasShipLayout.FillCircle(heart, hr, Color.Lerp(HeartCold, LampLit, progress));

            // Running lights: only the restored stretch glows.
            List<Vector2> running = AtlasShipLayout.RunningLights(canvas, 40);
            int glowing = Mathf.RoundToInt(running.Count * progress);
            for (int i = 0; i < running.Count; i++)
            {
                Color c = i < glowing ? LampLit : LampOff;
                Widgets.DrawBoxSolid(new Rect(running[i].x - 2f, running[i].y - 2f, 4f, 4f), c);
            }

            // Region labels and lamps.
            foreach (AtlasCategory cat in System.Enum.GetValues(typeof(AtlasCategory)))
            {
                if (!AtlasSettings.CategoryEnabled(cat)) continue;
                List<AtlasEntryDef> entries = visible.Where(d => d.category == cat)
                    .OrderBy(d => d.order).ThenBy(d => d.defName).ToList();
                DrawRegionLabel(canvas, cat, entries);
                List<Vector2> centres = AtlasShipLayout.LampCentres(canvas, cat, entries.Count);
                for (int i = 0; i < entries.Count; i++)
                    DrawLamp(entries[i], centres[i], i);
            }

            if (Comp == null)
            {
                Text.Anchor = TextAnchor.LowerCenter;
                Widgets.Label(canvas.ContractedBy(8f), "RUT_Atlas_NoGame".Translate());
                Text.Anchor = TextAnchor.UpperLeft;
            }
        }

        private void DrawStars(Rect canvas)
        {
            if (stars == null)
            {
                stars = new List<Vector2>();
                var rng = new System.Random(1137);
                for (int i = 0; i < 90; i++)
                    stars.Add(new Vector2((float)rng.NextDouble(), (float)rng.NextDouble()));
            }
            foreach (Vector2 s in stars)
            {
                Vector2 p = AtlasShipLayout.ToCanvas(canvas, s);
                Widgets.DrawBoxSolid(new Rect(p.x, p.y, 1.5f, 1.5f), Star);
            }
        }

        private void DrawRegionLabel(Rect canvas, AtlasCategory cat, List<AtlasEntryDef> entries)
        {
            Vector2 a = AtlasShipLayout.ToCanvas(canvas, AtlasShipLayout.LabelAnchor(cat));
            string label = ("RUT_Atlas_Region_" + cat).Translate();
            if (AtlasSettings.showCounters && entries.Count > 0)
            {
                int avail = entries.Count(d => d.Available);
                int lit = entries.Count(d => d.Available && Comp != null && Comp.IsDiscovered(d));
                label += " " + lit + "/" + avail;
            }
            Text.Font = GameFont.Tiny;
            Vector2 size = Text.CalcSize(label);
            Rect r = new Rect(a.x - size.x / 2f, a.y - size.y / 2f, size.x, size.y);
            GUI.color = new Color(0.93f, 0.82f, 0.62f);
            Widgets.Label(r, label);
            GUI.color = Color.white;
            TooltipHandler.TipRegion(r, ("RUT_Atlas_Category_" + cat).Translate());
            Text.Font = GameFont.Small;
        }

        private void DrawLamp(AtlasEntryDef def, Vector2 centre, int index)
        {
            Rect r = new Rect(centre.x - LampSize / 2f, centre.y - LampSize / 2f, LampSize, LampSize);
            bool available = def.Available;
            bool lit = available && Comp != null && Comp.IsDiscovered(def);

            if (lit)
            {
                float pulse = AtlasSettings.lightsPulse ? 0.55f + 0.25f * Mathf.Sin(Time.realtimeSinceStartup * 2f + index) : 0.6f;
                Widgets.DrawBoxSolid(r.ExpandedBy(5f), new Color(LampLit.r, LampLit.g, LampLit.b, pulse * 0.35f));
                Widgets.DrawBoxSolidWithOutline(r, LampLit, HullEdge, 2);
            }
            else if (available)
            {
                Widgets.DrawBoxSolidWithOutline(r, LampOff, LampOffEdge, 2);
                Text.Font = GameFont.Tiny;
                Text.Anchor = TextAnchor.MiddleCenter;
                GUI.color = LampOffEdge;
                Widgets.Label(r, "?");
                GUI.color = Color.white;
                Text.Anchor = TextAnchor.UpperLeft;
                Text.Font = GameFont.Small;
            }
            else
            {
                Widgets.DrawBoxSolidWithOutline(r, LampAbsent, LampAbsent * 1.6f, 1);
                Widgets.DrawLine(new Vector2(r.x + 3f, r.y + 3f), new Vector2(r.xMax - 3f, r.yMax - 3f), LampAbsent * 2f, 1f);
            }

            if (selected == def)
                Widgets.DrawBox(r.ExpandedBy(3f), 1);

            Widgets.DrawHighlightIfMouseover(r);
            TooltipHandler.TipRegion(r, new TipSignal(() => LampTip(def), def.shortHash));
            if (Widgets.ButtonInvisible(r))
            {
                selected = def;
                SoundDefOf.Click.PlayOneShotOnCamera();
            }
        }

        private static string LampTip(AtlasEntryDef def)
        {
            if (!def.Available) return "RUT_Atlas_Absent".Translate();
            if (Comp != null && Comp.IsDiscovered(def)) return def.LabelCap;
            return def.riddle;
        }

        // ---------------- the card ----------------

        private void DrawCardPanel(Rect panel)
        {
            Widgets.DrawBoxSolid(panel, Space);
            if (selected == null)
            {
                Text.Anchor = TextAnchor.MiddleCenter;
                GUI.color = new Color(0.85f, 0.75f, 0.6f);
                Widgets.Label(panel.ContractedBy(20f), "RUT_Atlas_PickALight".Translate());
                GUI.color = Color.white;
                Text.Anchor = TextAnchor.UpperLeft;
                return;
            }

            Rect card = panel.ContractedBy(14f);
            card.height = Mathf.Min(card.height, 470f);

            // Flip animation: squash the card's width through zero, swapping faces at the midpoint.
            bool showBack = flipped.Contains(selected);
            float t = (Time.realtimeSinceStartup - flipStart) / FlipSeconds;
            if (AtlasSettings.flipAnimation && flipping == selected && t < 1f)
            {
                float scale = Mathf.Abs(Mathf.Cos(t * Mathf.PI));
                if (t < 0.5f) showBack = !showBack; // still showing the old face
                float w = card.width * Mathf.Max(0.02f, scale);
                card = new Rect(card.center.x - w / 2f, card.y, w, card.height);
            }

            bool available = selected.Available;
            bool lit = available && Comp != null && Comp.IsDiscovered(selected);

            Widgets.DrawBoxSolidWithOutline(card, showBack ? CardBack : CardFace, CardEdge, 2);
            if (card.width > 120f)
            {
                Rect inner = card.ContractedBy(14f);
                if (!available) DrawAbsentFace(inner);
                else if (lit) { if (showBack) DrawLitBack(inner); else DrawLitFace(inner); }
                else { if (showBack) DrawHintFace(inner); else DrawRiddleFace(inner); }
            }

            // Click the card to flip it. A riddle flips to its hint only when hints are allowed.
            bool canFlip = available && (lit || AtlasSettings.hintsAllowed);
            Rect clickZone = new Rect(card.x, card.y, card.width, card.height - (lit && !selected.lore.NullOrEmpty() ? 48f : 0f));
            if (canFlip)
            {
                Widgets.DrawHighlightIfMouseover(clickZone);
                if (Widgets.ButtonInvisible(clickZone))
                {
                    if (!flipped.Remove(selected)) flipped.Add(selected);
                    flipping = selected;
                    flipStart = Time.realtimeSinceStartup;
                    SoundDefOf.PageChange.PlayOneShotOnCamera();
                }
            }

            // Lore click-through: offered on a lit card, never pushed.
            if (lit && !selected.lore.NullOrEmpty() && card.width > 120f)
            {
                Rect btn = new Rect(card.x + 14f, card.yMax - 44f, card.width - 28f, 32f);
                AtlasRecord rec = Comp.RecordFor(selected);
                string label = rec != null && rec.loreRead ? "RUT_Atlas_LoreAgain".Translate() : "RUT_Atlas_LoreOpen".Translate();
                if (Widgets.ButtonText(btn, label))
                    Find.WindowStack.Add(new Dialog_AtlasLore(selected));
            }

            Rect footer = new Rect(panel.x + 14f, card.yMax + 10f, panel.width - 28f, panel.yMax - card.yMax - 20f);
            if (footer.height > 20f)
            {
                Text.Font = GameFont.Tiny;
                GUI.color = new Color(0.75f, 0.65f, 0.5f);
                string how = ("RUT_Atlas_Completion_" + selected.completion).Translate();
                string hintNote = !lit && available && canFlip ? "\n" + "RUT_Atlas_ClickToFlip".Translate() : "";
                Widgets.Label(footer, ("RUT_Atlas_Category_" + selected.category).Translate() + " · " + how + hintNote);
                GUI.color = Color.white;
                Text.Font = GameFont.Small;
            }
        }

        private static void Heading(ref Rect inner, string text, Color color)
        {
            Text.Font = GameFont.Medium;
            float h = Text.CalcHeight(text, inner.width);
            GUI.color = color;
            Widgets.Label(new Rect(inner.x, inner.y, inner.width, h), text);
            GUI.color = Color.white;
            Text.Font = GameFont.Small;
            inner.yMin += h + 8f;
        }

        private static void Body(ref Rect inner, string text, bool italic = false)
        {
            Text.Font = GameFont.Small;
            string shown = italic ? "<i>" + text + "</i>" : text;
            float h = Text.CalcHeight(shown, inner.width);
            Widgets.Label(new Rect(inner.x, inner.y, inner.width, h), shown);
            inner.yMin += h + 8f;
        }

        private void DrawRiddleFace(Rect inner)
        {
            Heading(ref inner, "RUT_Atlas_RiddleHeading".Translate(), new Color(0.95f, 0.8f, 0.55f));
            Body(ref inner, selected.riddle, italic: true);
        }

        private void DrawHintFace(Rect inner)
        {
            Heading(ref inner, "RUT_Atlas_HintHeading".Translate(), new Color(0.7f, 0.85f, 0.9f));
            Body(ref inner, selected.hint);
            if (AtlasSettings.showTrueNameOnHint)
                Body(ref inner, "RUT_Atlas_ItIsCalled".Translate(selected.LabelCap));
        }

        private void DrawLitFace(Rect inner)
        {
            Heading(ref inner, selected.LabelCap, LampLit);
            if (!selected.description.NullOrEmpty()) Body(ref inner, selected.description);
            AtlasRecord rec = Comp?.RecordFor(selected);
            if (rec != null && rec.Discovered)
            {
                GUI.color = new Color(0.75f, 0.65f, 0.5f);
                string when = rec.backfilled
                    ? "RUT_Atlas_FoundBefore".Translate().ToString()
                    : "RUT_Atlas_FoundAgo".Translate((Find.TickManager.TicksGame - rec.discoveredTick).ToStringTicksToPeriod(allowSeconds: false)).ToString();
                Body(ref inner, when);
                GUI.color = Color.white;
            }
        }

        private void DrawLitBack(Rect inner)
        {
            Heading(ref inner, "RUT_Atlas_WhatTheRiddleMeant".Translate(), new Color(0.7f, 0.85f, 0.9f));
            Body(ref inner, selected.riddle, italic: true);
            Body(ref inner, selected.hint);
        }

        private void DrawAbsentFace(Rect inner)
        {
            Heading(ref inner, "RUT_Atlas_AbsentHeading".Translate(), new Color(0.6f, 0.6f, 0.6f));
            Body(ref inner, "RUT_Atlas_Absent".Translate());
        }
    }
}
