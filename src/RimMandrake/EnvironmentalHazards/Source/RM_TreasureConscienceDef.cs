using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // ════════════════════════════════════════════════════════════════════
    // ROT_LIVE_PREPARATIONS_1, owner card 6 (RULED 2026-09-17): "a pawn
    // carrying the Rot symbiont takes a mood debuff when the colony sells
    // the Rot's treasures — selling a part of yourself."
    //
    // CONTENT-BLIND BY CONSTRUCTION. This assembly names no treasure and no
    // symbiont. Two data shapes carry all of it:
    //
    //   * RM_TreasureMarkerExtension — a DefModExtension on any ThingDef
    //     that is "a treasure" of some conscience, carrying one string tag.
    //     Chosen over a thingCategory because a category is also a storage
    //     and a bill filter: giving the teas a shared category to mark them
    //     would silently reshape every stockpile UI and every ingredient
    //     filter that matches on parent categories. An extension is read by
    //     exactly one consumer and shows up nowhere else.
    //
    //   * RM_TreasureConscienceDef — one def per conscience, joining a tag
    //     to the hediffs that make a pawn care and the thought they take.
    //     Any mod can add a treasure (extension) or a symbiont (another
    //     hediff in carrierHediffs) with no C# at all.
    //
    // The trade seam is RM_Patch_TreasureSaleConscience.
    // ════════════════════════════════════════════════════════════════════
    public class RM_TreasureConscienceDef : Def
    {
        // Matches RM_TreasureMarkerExtension.treasureTag on the sold item.
        public string treasureTag;

        // A colonist holding ANY of these takes the thought. This is the
        // "symbiont set as data" half — never a hardcoded defName.
        public List<HediffDef> carrierHediffs = new List<HediffDef>();

        // The memory given. Must be a memory ThoughtDef (thoughtClass
        // Thought_Memory or a subclass) — ConfigErrors says so rather than
        // letting a situational ThoughtDef fail silently at give time.
        public ThoughtDef thought;

        // Ignore sales smaller than this many units in one deal, so
        // offloading a single spoiled cup is not a colony-wide crisis.
        public int minCountSold = 1;

        // false = only colonists on the negotiating caravan/map feel it;
        // true = every colonist of the faction, wherever they are. Card 6's
        // framing is a conscience, not gossip, so true is the default.
        public bool affectsAllColonists = true;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors())
            {
                yield return e;
            }

            if (treasureTag.NullOrEmpty())
            {
                yield return "RM_TreasureConscienceDef has no treasureTag — it can never match any "
                           + "item and is dead weight.";
            }

            if (thought == null)
            {
                yield return "RM_TreasureConscienceDef has no thought — nothing would ever be given.";
            }
            else if (thought.thoughtClass != null && !typeof(Thought_Memory).IsAssignableFrom(thought.thoughtClass))
            {
                yield return "RM_TreasureConscienceDef.thought (" + thought.defName + ") is not a memory "
                           + "thought (thoughtClass " + thought.thoughtClass.Name + ") — TryGainMemory "
                           + "cannot give it.";
            }

            if (carrierHediffs == null || carrierHediffs.Count == 0)
            {
                yield return "RM_TreasureConscienceDef has no carrierHediffs — no pawn could ever "
                           + "qualify, so the conscience is inert.";
            }
        }
    }

    // On a ThingDef: "selling me is selling a part of yourself, to whoever
    // holds the matching conscience."
    public class RM_TreasureMarkerExtension : DefModExtension
    {
        public string treasureTag;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors())
            {
                yield return e;
            }

            if (treasureTag.NullOrEmpty())
            {
                yield return "RM_TreasureMarkerExtension has no treasureTag — it marks nothing.";
            }
        }
    }
}
