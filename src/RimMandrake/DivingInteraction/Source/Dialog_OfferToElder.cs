using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.DivingInteraction
{
    // ════════════════════════════════════════════════════════════════════
    // GREYSEA_BRINE_ELDERS_1 — the trade UI.
    //
    // "Negotiating with a geological intelligence that has spent tens of
    // thousands of years quietly collecting one specimen of anything
    // genuinely new" (sheet §4e) — NOT a price list, so this dialog shows
    // "seen" vs "novel" rather than a haggle. Whether an item is novel is
    // read live from RM_GameComponent_BrineElders for THIS map's world
    // tile, so the list updates the instant something is traded.
    //
    // SCOPE CUT, flagged rather than silently skipped: the sheet's own
    // sentence "a colonist of a new xenotype is an offering" implies a
    // LIVE pawn can be handed over. That is a one-way, permanent removal of
    // a colonist from the game and deserves its own explicit owner
    // confirmation before it ships as a clickable option — it is NOT
    // wired up here. Only spawned, non-Pawn Things and Corpses are listed.
    // Withholding this is deliberate, same posture as the resonant crystal
    // and the "beautiful useless artifact" — not forgotten, not faked.
    // ════════════════════════════════════════════════════════════════════
    public class Dialog_OfferToElder : Window
    {
        private static readonly HashSet<ThingDef> ExcludedTrivialGoods = new HashSet<ThingDef>
        {
            ThingDefOf.Silver,
        };

        private readonly RM_Building_BrineElder elder;
        private Vector2 scrollPos;

        public override Vector2 InitialSize => new Vector2(520f, 560f);

        public Dialog_OfferToElder(RM_Building_BrineElder elder)
        {
            this.elder = elder;
            forcePause = true;
            doCloseX = true;
            absorbInputAroundWindow = true;
        }

        private List<Thing> EligibleThings()
        {
            Map map = elder.Map;
            if (map == null)
            {
                return new List<Thing>();
            }
            return map.listerThings.AllThings
                .Where(t => t.Spawned
                    && !(t is Pawn)
                    && !(t is RM_Building_BrineElder)
                    && (t is Corpse || (t.def.category == ThingCategory.Item && t.def.EverHaulable))
                    && !ExcludedTrivialGoods.Contains(t.def))
                .OrderBy(t => t.LabelCap.ToString())
                .ToList();
        }

        public override void DoWindowContents(Rect inRect)
        {
            int tile = RM_ElderTradeUtility.TileForMap(elder.Map);
            RM_GameComponent_BrineElders comp = Current.Game.GetComponent<RM_GameComponent_BrineElders>();

            Text.Font = GameFont.Medium;
            Widgets.Label(new Rect(0f, 0f, inRect.width, 34f), "RM_OfferToElderTitle".Translate());
            Text.Font = GameFont.Small;

            Rect descRect = new Rect(0f, 36f, inRect.width, 48f);
            Widgets.Label(descRect, "RM_OfferToElderInstructions".Translate());

            List<Thing> things = EligibleThings();
            float y = 90f;
            Rect outRect = new Rect(0f, y, inRect.width, inRect.height - y - 40f);
            Rect viewRect = new Rect(0f, 0f, outRect.width - 16f, things.Count * 32f + 4f);

            Widgets.BeginScrollView(outRect, ref scrollPos, viewRect);
            float rowY = 0f;
            if (things.Count == 0)
            {
                Widgets.Label(new Rect(0f, 0f, viewRect.width, 32f), "RM_OfferToElderNoneEligible".Translate());
            }
            foreach (Thing t in things)
            {
                Rect rowRect = new Rect(0f, rowY, viewRect.width, 30f);
                Widgets.DrawHighlightIfMouseover(rowRect);

                bool novel = comp != null && tile >= 0 && !comp.HasSeen(tile, RM_ElderTradeUtility.NoveltyKey(t));
                string tag = novel ? "RM_ElderNovel".Translate() : "RM_ElderStale".Translate();
                string label = t.LabelCap + (t.stackCount > 1 ? " x" + t.stackCount : "") + "  —  " + tag;

                GUI.color = novel ? new Color(0.85f, 0.95f, 0.7f) : new Color(0.6f, 0.6f, 0.6f);
                Widgets.Label(rowRect, label);
                GUI.color = Color.white;

                if (Widgets.ButtonInvisible(rowRect))
                {
                    ConfirmAndOffer(t, novel);
                }
                rowY += 32f;
            }
            Widgets.EndScrollView();

            if (Widgets.ButtonText(new Rect(inRect.width / 2f - 60f, inRect.height - 32f, 120f, 32f), "CloseButton".Translate()))
            {
                Close();
            }
        }

        private void ConfirmAndOffer(Thing t, bool novel)
        {
            string text = novel
                ? "RM_ElderOfferConfirmNovel".Translate(t.LabelCap)
                : "RM_ElderOfferConfirmStale".Translate(t.LabelCap);
            Find.WindowStack.Add(Dialog_MessageBox.CreateConfirmation(text, delegate
            {
                RM_ElderTradeUtility.OfferResult result = RM_ElderTradeUtility.Offer(elder, t);
                ReportResult(result);
                Close();
            }, destructive: !novel));
        }

        private void ReportResult(RM_ElderTradeUtility.OfferResult result)
        {
            if (result.UniqueTreasureGranted != null)
            {
                Messages.Message(
                    "RM_ElderOfferResultTreasure".Translate(result.UniqueTreasureGranted.LabelCap),
                    new TargetInfo(elder.Position, elder.Map),
                    MessageTypeDefOf.PositiveEvent);
                return;
            }
            Messages.Message(
                result.WasNovel
                    ? "RM_ElderOfferResultNovel".Translate(result.SilverGranted)
                    : "RM_ElderOfferResultStale".Translate(result.SilverGranted),
                new TargetInfo(elder.Position, elder.Map),
                result.WasNovel ? MessageTypeDefOf.PositiveEvent : MessageTypeDefOf.NeutralEvent);
        }
    }
}
