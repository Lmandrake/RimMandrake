using System.Collections.Generic;
using Verse;

namespace RimMandrake.Inhabited
{
    /// <summary>
    /// One district slot in a settlement manifest -- SCHEMA ONLY.
    ///
    /// This names a district by LABEL (a free-text kind, e.g. "scrapyard",
    /// "cantina block"), a rough footprint and what it wants to sit beside.
    /// Nothing here is a Lua template reference: DISTRICT_TEMPLATE_LIBRARY_1
    /// owns the template vocabulary and will resolve labels to real content.
    /// A manifest that names districts a template library does not yet have is
    /// not an error -- v1's compose step reads only the first slot and stubs
    /// the rest.
    /// </summary>
    public class DistrictSlot
    {
        /// <summary>The district KIND, matched by label once a template library
        /// exists. Not a defName reference on purpose -- the vocabulary is not
        /// authored yet and a dangling defName reference would be a config
        /// error for content that has not shipped.</summary>
        public string label;

        /// <summary>Rough footprint in cells. Advisory only until a template
        /// claims the slot.</summary>
        public IntVec2 approxSize = new IntVec2(20, 20);

        /// <summary>Labels of other district slots this one wants to sit next
        /// to. Adjacency is a wish, not a placement -- the composer (v2) is
        /// free to fail it.</summary>
        public List<string> adjacentTo = new List<string>();

        /// <summary>False marks a slot as flavour/optional -- a smaller or
        /// lower-security settlement's manifest may list a district it does
        /// not insist on.</summary>
        public bool required = true;
    }

    /// <summary>
    /// One cast-assignment slot in a settlement manifest -- SCHEMA ONLY.
    ///
    /// Deliberately a free-text ROLE plus an optional InhabitedCastDef link,
    /// not a hard requirement that the cast content already exist. The engine
    /// (WorldObject_Inhabited.InstantiateCast, reused unchanged) already knows
    /// how to roll a cast from an InhabitedCastDef; this slot only records
    /// which role a district wants one for, so DISTRICT_TEMPLATE_LIBRARY_1 can
    /// wire real InhabitedCastDefs to real district content later.
    /// </summary>
    public class CastAssignmentSlot
    {
        /// <summary>Free-text role name, e.g. "trader", "boss", "guard".</summary>
        public string role;

        /// <summary>Which district slot (by label) this assignment belongs to.
        /// Empty means "settlement-wide", not tied to one district.</summary>
        public string district;

        /// <summary>Optional: an existing InhabitedCastDef to draw this role's
        /// people from. Null is a legitimate v1 value -- no cast content is
        /// authored by this item; SETTLEMENT_VERBS_WAVE_1 and the district
        /// library fill this in per real settlement.</summary>
        public InhabitedCastDef castDef;

        /// <summary>How many for this role. Rolled the same way InstantiateCast
        /// rolls an InhabitedRole's count.</summary>
        public IntRange count = new IntRange(1, 1);
    }

    /// <summary>
    /// A settlement manifest -- SETTLEMENT_VISIT_LOOP_1's core deliverable.
    ///
    /// Districts present, their sizes and adjacency, cast assignment slots,
    /// and the faction's security profile for the gate-search hook. DATA SHAPE
    /// ONLY: this item does not author district content (DISTRICT_TEMPLATE_LIBRARY_1),
    /// verbs (SETTLEMENT_VERBS_WAVE_1) or claim math (owned by RM_Property,
    /// untouched here).
    ///
    /// One manifest instance ships with this item: the Junkers pilot, in the
    /// RimUtinni companion mod (src/RimUtinni/AshkarrInhabited), naming an
    /// actual settlement from ASHKARR_WORLD_DEFINITION.md.
    /// </summary>
    public class SettlementManifestDef : Def
    {
        /// <summary>Which world settlement this manifest describes, as free
        /// text (a settlement name from ASHKARR_WORLDMAP_settlements.csv, e.g.
        /// "The Claim Jump"). Not a WorldObject reference: manifests are
        /// authored data that a settlement's WorldObject picks up, not the
        /// other way around.</summary>
        public string settlementName;

        /// <summary>The faction defName this settlement belongs to, as free
        /// text for the same reason (e.g. "Jawa_Junkers"). Informational only
        /// in v1 -- nothing here binds it to a live FactionDef.</summary>
        public string factionDefName;

        /// <summary>Districts present, their sizes and adjacency. v1's compose
        /// step reads only districts[0]; the rest is schema proven early.</summary>
        public List<DistrictSlot> districts = new List<DistrictSlot>();

        /// <summary>Cast assignment slots, settlement-wide or per district.</summary>
        public List<CastAssignmentSlot> castSlots = new List<CastAssignmentSlot>();

        /// <summary>The faction's gate-search posture. Null is a legitimate
        /// value and reads as "never searches" -- see GateSearchHook.</summary>
        public SecurityProfileDef securityProfile;

        /// <summary>
        /// What the settlement IS as a place: routine radii, sleep hours, the
        /// larder and trade tables, and the FATE that could end its cast.
        ///
        /// 🔑 THE ONLY ROUTE BY WHICH A SETTLEMENT EVER GETS AN InhabitedPlaceDef.
        /// Nothing else in this mod assigns WorldObject_Inhabited.placeDef, so
        /// before INHABITED_STOCK_ONTO_MAP_AND_FATE_1 added this field every
        /// settlement ran on the field's own defaults with an empty larder and no
        /// fate -- the archetype layer was authored, reachable by XML, and bound
        /// to nothing. GenStep_ComposeSettlementDistrict copies it onto the world
        /// object at map generation.
        ///
        /// Null stays legitimate: an unmanifested settlement, or one whose place
        /// archetype has not been authored, generates exactly as it did before.
        /// </summary>
        public InhabitedPlaceDef place;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors())
            {
                yield return e;
            }
            if (districts.NullOrEmpty())
            {
                // Fixed 2026-09-02 (opus code review, re-review pass): the loop
                // below dereferenced districts.Count unconditionally - a NullRef
                // inside def validation itself if districts is genuinely null
                // (IsNull="True" in XML), not just empty.
                yield return "no districts: a settlement manifest with no districts describes nothing";
                yield break;
            }
            for (int i = 0; i < districts.Count; i++)
            {
                if (districts[i].label.NullOrEmpty())
                {
                    yield return "district " + i + " has no label";
                }
            }
        }
    }
}
