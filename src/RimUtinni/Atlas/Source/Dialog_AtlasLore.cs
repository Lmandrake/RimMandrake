using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.Atlas
{
    // The lore leaf for a lit entry: opened only when the player clicks through
    // (owner ruling Q4, 2026-10-02: "you can click through to it once you unlock
    // it. Nothing gets in your way, ignorable if undesired"). Text is spoken by a
    // voice inside the world and never states a hidden truth (ruling R25).
    public class Dialog_AtlasLore : Window
    {
        private readonly AtlasEntryDef entry;
        private Vector2 scroll;

        public override Vector2 InitialSize => new Vector2(560f, 460f);

        public Dialog_AtlasLore(AtlasEntryDef entry)
        {
            this.entry = entry;
            doCloseX = true;
            doCloseButton = true;
            closeOnClickedOutside = true;
            absorbInputAroundWindow = true;
            forcePause = false;
        }

        public override void PreOpen()
        {
            base.PreOpen();
            AtlasRecord rec = GameComponent_Atlas.Instance?.RecordFor(entry);
            if (rec != null) rec.loreRead = true;
        }

        public override void DoWindowContents(Rect inRect)
        {
            Text.Font = GameFont.Medium;
            Rect title = new Rect(inRect.x, inRect.y, inRect.width, 36f);
            Widgets.Label(title, entry.LabelCap);
            Text.Font = GameFont.Small;

            float y = title.yMax;
            if (!entry.loreVoice.NullOrEmpty())
            {
                GUI.color = new Color(0.75f, 0.65f, 0.5f);
                Rect voice = new Rect(inRect.x, y, inRect.width, 24f);
                Widgets.Label(voice, "<i>" + entry.loreVoice + "</i>");
                GUI.color = Color.white;
                y = voice.yMax + 6f;
            }

            Rect outRect = new Rect(inRect.x, y, inRect.width, inRect.height - y - CloseButSize.y - 10f);
            float h = Text.CalcHeight(entry.lore, outRect.width - 16f);
            Rect view = new Rect(0f, 0f, outRect.width - 16f, h);
            Widgets.BeginScrollView(outRect, ref scroll, view);
            Widgets.Label(view, entry.lore);
            Widgets.EndScrollView();
        }
    }
}
