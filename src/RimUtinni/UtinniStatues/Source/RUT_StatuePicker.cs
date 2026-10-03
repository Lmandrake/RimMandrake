using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.UtinniStatues
{
    /// <summary>One carving the player can dedicate a statue to (statue_mods_spec.md §1.2).</summary>
    public class RUT_StatueCarving
    {
        public string id;          // e.g. RUT_Idol_Shkaar; the texture is Things/Building/Art/RUT_UtinniIdols/<id>
        public string label;       // "idol of Sh'kaar"
        public string honours;     // "Sh'kaar the All-Searing", or the votive's meaning
        public string depicts;     // one line of what is carved

        public string TexPath => "Things/Building/Art/RUT_UtinniIdols/" + id;
    }

    /// <summary>
    /// UTINNI_STATUES_SKELETON_BUILD_1 — owner rulings R2 (typed 2026-09-25: "it's important the player be
    /// able to choose who they are honoring") and R8 (card: a picker button, not a 16-entry dropdown).
    /// Each statue tier carries the carvings of its own size; the button on a built statue picks one.
    /// </summary>
    public class CompProperties_StatuePicker : CompProperties
    {
        public List<RUT_StatueCarving> carvings = new List<RUT_StatueCarving>();

        public CompProperties_StatuePicker()
        {
            compClass = typeof(RUT_CompStatuePicker);
        }

        public RUT_StatueCarving Find(string id)
        {
            if (id == null)
            {
                return null;
            }
            for (int i = 0; i < carvings.Count; i++)
            {
                if (carvings[i].id == id)
                {
                    return carvings[i];
                }
            }
            return null;
        }

        public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string e in base.ConfigErrors(parentDef))
            {
                yield return e;
            }
            if (carvings.NullOrEmpty())
            {
                yield return "CompProperties_StatuePicker on " + parentDef.defName + " lists no carvings";
            }
            if (!typeof(RUT_Building_Statue).IsAssignableFrom(parentDef.thingClass))
            {
                yield return parentDef.defName + " must use thingClass RUT_Building_Statue or the chosen carving never draws";
            }
        }
    }

    public class RUT_CompStatuePicker : ThingComp
    {
        public string carvingId;

        private Graphic cachedGraphic;
        private string cachedFor;

        public CompProperties_StatuePicker Props => (CompProperties_StatuePicker)props;

        public RUT_StatueCarving Carving => Props.Find(carvingId);

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref carvingId, "rutCarving");
        }

        public void SetCarving(string id)
        {
            if (Props.Find(id) == null)
            {
                return;
            }
            carvingId = id;
            cachedGraphic = null;
            cachedFor = null;
            if (parent.Spawned)
            {
                parent.DirtyMapMesh(parent.Map);
            }
        }

        /// <summary>The chosen carving's graphic, or null (draw the def's placeholder) when nothing is chosen
        /// or that carving's PNG has not landed yet.</summary>
        public Graphic CarvingGraphic()
        {
            RUT_StatueCarving c = Carving;
            if (c == null)
            {
                return null;
            }
            if (cachedFor == c.id)
            {
                return cachedGraphic;
            }
            cachedFor = c.id;
            cachedGraphic = null;
            if (ContentFinder<Texture2D>.Get(c.TexPath, reportFailure: false) != null)
            {
                GraphicData gd = new GraphicData();
                gd.CopyFrom(parent.def.graphicData);
                gd.texPath = c.TexPath;
                gd.graphicClass = typeof(Graphic_Single);
                cachedGraphic = gd.GraphicColoredFor(parent);
            }
            return cachedGraphic;
        }

        public override string TransformLabel(string label)
        {
            RUT_StatueCarving c = Carving;
            return c == null ? label : c.label;
        }

        public override string CompInspectStringExtra()
        {
            RUT_StatueCarving c = Carving;
            if (c == null)
            {
                return "Not yet dedicated: choose who it honours.";
            }
            return "Honours: " + c.honours;
        }

        public override string GetDescriptionPart()
        {
            RUT_StatueCarving c = Carving;
            return c == null || c.depicts.NullOrEmpty() ? null : c.depicts;
        }

        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            foreach (Gizmo g in base.CompGetGizmosExtra())
            {
                yield return g;
            }
            if (parent.Faction != Faction.OfPlayer)
            {
                yield break;
            }
            RUT_StatueCarving cur = Carving;
            Command_Action cmd = new Command_Action
            {
                defaultLabel = cur == null ? "Dedicate…" : "Rededicate…",
                defaultDesc = "Choose who this statue honours. The carving changes to match.",
                icon = parent.def.uiIcon,
                action = OpenMenu,
            };
            yield return cmd;
        }

        private void OpenMenu()
        {
            List<FloatMenuOption> opts = new List<FloatMenuOption>();
            foreach (RUT_StatueCarving c in Props.carvings)
            {
                string id = c.id;
                string text = c.label + (c.id == carvingId ? " (current)" : "");
                Texture2D tex = ContentFinder<Texture2D>.Get(c.TexPath, reportFailure: false);
                FloatMenuOption o = tex != null
                    ? new FloatMenuOption(text, () => SetCarving(id), tex, Color.white)
                    : new FloatMenuOption(text, () => SetCarving(id));
                opts.Add(o);
            }
            Find.WindowStack.Add(new FloatMenu(opts));
        }
    }

    /// <summary>A sculpture whose drawn graphic follows the carving picked on its RUT_CompStatuePicker.</summary>
    public class RUT_Building_Statue : Building_Art
    {
        private RUT_CompStatuePicker picker;

        public RUT_CompStatuePicker Picker => picker ?? (picker = GetComp<RUT_CompStatuePicker>());

        public override Graphic Graphic => Picker?.CarvingGraphic() ?? base.Graphic;

        /// <summary>Bridge proof (jawa/static_call): dedicate the statue standing on <paramref name="cell"/>
        /// to <paramref name="carvingId"/> and read back its label. Returns "LABEL <label> | HONOURS <x>"
        /// or "REFUSED: why".</summary>
        public static string ProofDedicate(Map map, IntVec3 cell, string carvingId)
        {
            if (map == null)
            {
                return "REFUSED: no map";
            }
            foreach (Thing t in cell.GetThingList(map))
            {
                if (t is RUT_Building_Statue s && s.Picker != null)
                {
                    if (s.Picker.Props.Find(carvingId) == null)
                    {
                        return "REFUSED: " + carvingId + " is not a carving of " + s.def.defName;
                    }
                    s.Picker.SetCarving(carvingId);
                    return "LABEL " + s.LabelNoCount + " | HONOURS " + s.Picker.Carving?.honours;
                }
            }
            return "REFUSED: no statue at " + cell;
        }
    }
}
