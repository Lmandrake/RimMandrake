using Verse;

namespace RimMandrake.Inhabited
{
    /// <summary>
    /// A named, visitable settlement -- SETTLEMENT_VISIT_LOOP_1, sitting on top
    /// of the wilderness-place engine (WorldObject_Inhabited) built for
    /// INHABITED_DESIGN.md's tile-mutator PLACEs.
    ///
    /// Deliberately a thin subclass. The roster, stock, cast-instantiation and
    /// teardown-to-roster machinery are ALL inherited unchanged -- roster
    /// (ThingOwner&lt;Pawn&gt;), InstantiateCast(), and the base class's Destroy()
    /// already implement "survivors return to the roster, the dead are
    /// forgotten" for any WorldObject_Inhabited subtype, and both
    /// GenStep_InhabitedCast and Patch_Game_DeinitAndRemoveMap look up their
    /// target via WorldObjectAt&lt;WorldObject_Inhabited&gt;, which matches this
    /// subclass polymorphically. Reusing them here is the whole point --
    /// SETTLEMENT_VISIT_LOOP_1's own scope is only the manifest and the casing
    /// record, not a second cast/route/teardown implementation.
    ///
    /// What this subclass actually adds: a manifest (what the settlement IS --
    /// districts, cast slots, security profile) and a casing record (what the
    /// colony now KNOWS about it, across visits).
    /// </summary>
    public class WorldObject_InhabitedSettlement : WorldObject_Inhabited
    {
        /// <summary>Districts, cast slots and security profile. May be null --
        /// an unmanifested settlement still generates a bare Encounter-style
        /// map with no compose step and no gate-search hook, rather than
        /// erroring.</summary>
        public SettlementManifestDef manifest;

        /// <summary>What the colony now knows about this settlement. Never
        /// null after construction or load.</summary>
        public SettlementCasing casing = new SettlementCasing();

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Defs.Look(ref manifest, "manifest");
            Scribe_Deep.Look(ref casing, "casing");
            if (Scribe.mode == LoadSaveMode.PostLoadInit && casing == null)
            {
                casing = new SettlementCasing();
            }
        }
    }
}
