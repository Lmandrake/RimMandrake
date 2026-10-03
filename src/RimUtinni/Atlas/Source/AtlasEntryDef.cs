using System.Collections.Generic;
using Verse;

namespace RimMandrake.Utinni.Atlas
{
    // Where on the Utinni an entry's running light sits. Each region of the ship
    // is one category (owner ruling Q1, 2026-10-02: "arranged in a beautiful
    // graphical display that looks like the utinni vessel"). The regions are the
    // ship's own identity features (design/Jawa/reconciled_lore/06_the_ship.md):
    // the asymmetric mandibles reach out into the wilds, the factory pods hold the
    // clan's crafts, the reliquary heart is the ship herself.
    public enum AtlasCategory
    {
        Creatures,   // port mandible: the wilds
        Giants,      // starboard mandible, the dead prong
        Places,      // the bridge: where the ship can go, what the land does
        Weather,     // the sensor vanes along the dorsal spine
        Resources,   // the hold
        Crafts,      // the factory pods
        Gods,        // the shrine decks: the nine, the rites
        Ship,        // the reliquary heart: the Utinni herself
    }

    // What has to happen for an entry to count (owner ruling Q6, 2026-10-02:
    // "depends on the thing"). Display-only: the triggers decide; this word tells
    // the player which kind of act lights the lamp.
    public enum AtlasCompletion
    {
        Seen,
        Used,
        Performed,
    }

    // One Atlas entry. Text is in the def, so a sitting edits XML, never C#.
    //   label        the thing's true name, shown once found
    //   description  what it is, shown once found
    //   riddle       the card's face before discovery (cryptic)
    //   hint         the card's back before discovery (plain)
    //   lore         optional click-through once found; written from
    //                design/Jawa/reconciled_lore in an in-world voice, never
    //                stating a hidden truth (ruling R25)
    //   loreVoice    who is speaking the lore ("a clan saying", "a trader's tale")
    public class AtlasEntryDef : Def
    {
        public string riddle;
        public string hint;
        public string lore;
        public string loreVoice;
        public AtlasCategory category = AtlasCategory.Places;
        public AtlasCompletion completion = AtlasCompletion.Seen;
        public int order;

        // Any one trigger satisfied lights the entry.
        public List<AtlasTrigger> triggers = new List<AtlasTrigger>();

        // Optional: the packageId of the mod that owns the subject. When set and
        // that mod is not active, the entry is "absent from this world".
        public string subjectPackageId;

        // Optional small material reward (off unless the player enables rewards).
        public string rewardThing;
        public int rewardCount;

        public bool Available
        {
            get
            {
                if (!subjectPackageId.NullOrEmpty() && !ModsConfig.IsActive(subjectPackageId))
                    return false;
                if (triggers.NullOrEmpty())
                    return false;
                for (int i = 0; i < triggers.Count; i++)
                    if (triggers[i].Available) return true;
                return false;
            }
        }

        public override void ResolveReferences()
        {
            base.ResolveReferences();
            if (triggers == null) return;
            foreach (AtlasTrigger t in triggers)
                t.ResolveReferences();
        }

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors())
                yield return e;
            if (riddle.NullOrEmpty()) yield return "AtlasEntryDef has no riddle";
            if (hint.NullOrEmpty()) yield return "AtlasEntryDef has no hint";
            if (triggers.NullOrEmpty()) yield return "AtlasEntryDef has no triggers";
            else
                foreach (AtlasTrigger t in triggers)
                    foreach (string e in t.ConfigErrors())
                        yield return e;
        }
    }
}
