/* Ported unchanged from Ruthless Faction Pursuit (workshop 3621784437) by Matathias, GPLv3.
 * See ../../LICENSE.txt and About.xml for the fork's credit and scope. */
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using UnityEngine;
using Verse;

namespace RuthlessPursuingMechanoids
{
    public class RFPSettings : ModSettings
    {
        public static bool printDebug = false;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref printDebug, "printDebug", false, true);
        }

        public void DoWindowContents(Rect inRect)
        {
            var list = new Listing_Standard()
            {
                ColumnWidth = inRect.width
            };
            list.Begin(inRect);

            list.CheckboxLabeled("printDebug".Translate(), ref printDebug);

            list.End();
        }

    }
    public class RFPMod : Mod
    {
        public static RFPSettings settings = new RFPSettings();

        public RFPMod(ModContentPack content) : base(content)
        {
            Pack = content;
            settings = GetSettings<RFPSettings>();
        }

        public ModContentPack Pack { get; }

        public override string SettingsCategory() => Pack.Name;

        public override void DoSettingsWindowContents(Rect inRect) => settings.DoWindowContents(inRect);
    }
}
