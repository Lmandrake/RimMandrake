using System.Collections.Generic;
using RimWorld;
using Verse;

namespace Inhabited
{
    /// <summary>
    /// One authored trait on a character, with its degree resolved to the integer
    /// the engine actually uses.
    ///
    /// The cast files write degrees by NAME -- `NaturalMood(Sanguine)`,
    /// `DrugDesire(ChemicalFascination)` -- because that is what a person writing
    /// prose can hold in their head. `cast_to_xml.py` resolves the name against
    /// the def dump's `degreeDatas` and emits the integer, so nothing has to be
    /// looked up at runtime and a name that does not resolve fails at BUILD time
    /// rather than in somebody's game.
    /// </summary>
    public class CharacterTrait
    {
        public TraitDef def;

        /// <summary>The engine's degree. 0 for a single-degree trait.</summary>
        public int degree;

        /// <summary>What the author wrote, kept for readability and for diffing.</summary>
        public string degreeName;

        public override string ToString()
        {
            return (def?.defName ?? "NULL") + (degreeName.NullOrEmpty() ? "" : "(" + degreeName + ")");
        }
    }

    /// <summary>
    /// A hand-authored person, as data.
    ///
    /// Two hundred and ninety-four of these exist as prose across twelve cast
    /// files, and this def is what `src/RimMandrake/Utils/cast_to_xml.py` turns
    /// them into. The prose files stay the source of truth: they are what a human
    /// edits, and they are regenerated from, never back into.
    ///
    /// ⛔ TWO FIELDS ARE DELIBERATELY EMPTY AND MUST NOT BE GUESSED: xenotype and
    /// pawnKind. The prose does not carry them, DECIDE owes them, and a guessed
    /// xenotype ships a wrong-looking person into a world that is built once and
    /// frozen. Empty is a question; a guess is a defect nobody can see.
    ///
    /// ⚠️ `apparel` and `skills` WERE in that list and are not any more -- owner
    /// ruling 2026-08-21, INHABITED_DESIGN.md §5.7a. The prose now carries
    /// `weapon:`, `apparel:`, `item:` and `skills:` lines, optionally, on the
    /// people whose blockquote earns them. ⛔ Sparse is the specification: 171 of
    /// the 294 carry none of the four, and an empty list here means the author
    /// said nothing, not that anybody still owes it.
    ///
    /// ⚠️ `race` is a PROSE STRING -- "Ugnaught", "Chagrian" -- not a def. It is
    /// what the author wrote and it is not resolvable to anything yet. The droid
    /// cast uses `chassis` in its place and `serviceYears` in place of `age`, by
    /// owner ruling; that is handled, not normalised away.
    /// </summary>
    public class CharacterDef : Def
    {
        // ---- who ----

        /// <summary>The faction this person belongs to, by our own cast-file name.</summary>
        public string faction;

        /// <summary>The place they were authored into, from the cast file heading.</summary>
        public string place;

        /// <summary>Species, as prose. Not a def and not resolvable yet.</summary>
        public string race;

        /// <summary>Droids only: the chassis, in place of a race.</summary>
        public string chassis;

        /// <summary>As authored: `m`, `f`, `none`, `f-presenting`.</summary>
        public string genderText;

        /// <summary>Resolved where it can be. `null` for `none` and for a droid.</summary>
        public Gender? gender;

        /// <summary>Biological years. -1 when the entry carries service years instead.</summary>
        public int age = -1;

        /// <summary>Droids only: years in service, in place of an age.</summary>
        public int serviceYears = -1;

        /// <summary>
        /// The age EXACTLY as authored, and it is not decoration.
        ///
        /// The prose does not carry a plain integer on every entry -- the queue
        /// item's measurement was wrong about that. It carries "six hems (33)"
        /// for a Jawa, whose age is counted in robe-hems; "claims 40,000; is 90"
        /// for a droid who lies about it; "~90", "60ish", "300+", and a flat
        /// "unknown" for several people whose age nobody knows on purpose.
        /// The integer above is the number pulled out of that; THIS is the
        /// characterisation, and reducing it to the number would throw the
        /// interesting half away.
        /// </summary>
        public string ageText;

        // ---- what makes them themselves ----

        public List<CharacterTrait> traits = new List<CharacterTrait>();

        /// <summary>One line. Not a BackstoryDef; the authored text.</summary>
        public string childhood;

        /// <summary>One line. Not a BackstoryDef; the authored text.</summary>
        public string adult;

        /// <summary>
        /// One or two sentences: physical, manner, and the flaw that will cause
        /// trouble. The hook and the traits must agree -- a hook the mechanics do
        /// not back is a lie the player will catch.
        /// </summary>
        public string hook;

        // ---- kit, where the prose earns it (INHABITED_DESIGN.md §5.7a) ----
        //
        // All four are OPTIONAL and empty is the common case. `cast_to_xml.py`
        // writes only what a character's own blockquote says, and 171 of the 294
        // say nothing. ⛔ Do not backfill any of these to look complete.

        /// <summary>Their one signature weapon, or null. 18 characters have one.</summary>
        public ThingDef weapon;

        /// <summary>Worn. 15 characters have any.</summary>
        public List<ThingDef> apparel = new List<ThingDef>();

        /// <summary>
        /// Carried OR installed, and the prose does not distinguish -- bionics are
        /// written here too. Which it is, is CharacterApplier's call, not the
        /// parser's. 27 characters have any.
        /// </summary>
        public List<ThingDef> items = new List<ThingDef>();

        /// <summary>
        /// ⭐ OUTLIERS ONLY, high or low. 8 is average and is never written, so a
        /// skill absent here means "ordinary", not "unknown". `Shooting 0` on a man
        /// who spent twenty-nine years carrying the boarding ramp is authored, and
        /// says more than a 17 would. 101 characters carry a skills line.
        /// </summary>
        public List<SkillGain> skills = new List<SkillGain>();

        // ---- owed by DECIDE, deliberately empty ----

        public XenotypeDef xenotype;
        public PawnKindDef pawnKind;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors())
            {
                yield return e;
            }
            if (label.NullOrEmpty())
            {
                yield return "no label: a character without a name is not a character";
            }
            if (race.NullOrEmpty() && chassis.NullOrEmpty())
            {
                yield return "neither race nor chassis";
            }
            if (age < 0 && serviceYears < 0 && ageText.NullOrEmpty())
            {
                yield return "neither age, serviceYears nor ageText";
            }
            for (int i = 0; i < traits.Count; i++)
            {
                CharacterTrait t = traits[i];
                if (t?.def == null)
                {
                    // A trait that does not resolve is the one thing here that
                    // must fail loudly. It means the roster and the load set have
                    // drifted apart, and the person will come out wrong.
                    yield return "trait " + i + " did not resolve to a TraitDef";
                    continue;
                }
                bool degreeExists = false;
                for (int d = 0; d < t.def.degreeDatas.Count; d++)
                {
                    if (t.def.degreeDatas[d].degree == t.degree)
                    {
                        degreeExists = true;
                        break;
                    }
                }
                if (!degreeExists)
                {
                    yield return "trait " + t.def.defName + " has no degree " + t.degree
                                 + " (authored as '" + (t.degreeName ?? "-") + "')";
                }

                // RimWorld enforces NOTHING here: TraitSet.GainTrait checks no
                // conflicts and has no trait cap, so a character authored with
                // Kind AND Psychopath would simply be built, and no vanilla pawn
                // generation could ever have produced them. TraitDef.ConflictsWith
                // is bidirectional and also consults exclusionTags, so ask IT
                // rather than reading conflictingTraits off one side.
                for (int j = i + 1; j < traits.Count; j++)
                {
                    CharacterTrait other = traits[j];
                    if (other?.def == null)
                    {
                        continue;
                    }
                    if (t.def == other.def)
                    {
                        yield return "trait " + t.def.defName + " is listed twice";
                    }
                    else if (t.def.ConflictsWith(other.def))
                    {
                        yield return "IMPOSSIBLE PAIR: " + t.def.defName + " + " + other.def.defName
                                     + " conflict, so this person cannot exist. Pick one in "
                                     + "design/Jawa/bridge/INHABITED_CAST_*.md and re-run cast_to_xml.py";
                    }
                }
            }
        }
    }
}
