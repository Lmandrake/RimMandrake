using System;
using System.Collections.Generic;
using System.IO;
using RimMandrake.StructureInjections;
using Verse;

namespace RimMandrake.Inhabited
{
    /// <summary>
    /// Compose step -- SETTLEMENT_VISIT_LOOP_1's arrival/compose beat, now
    /// carrying DISTRICT_TEMPLATE_LIBRARY_1's real district geometry for the
    /// one label this pass wires end to end.
    ///
    /// v1 SCOPE, stated explicitly rather than shipped as a silent partial:
    /// only <c>districts[0]</c> is composed, exactly as the SETTLEMENT_VISIT_LOOP_1
    /// stub already did -- the difference is that when that slot's label has a
    /// real compiled template (see <see cref="TemplateFiles"/>), this step now
    /// replays actual walls/floor/roof/furniture onto the map instead of just
    /// recording a casing string. A settlement whose districts[0] label has no
    /// entry in <see cref="TemplateFiles"/> yet (or any manifest's
    /// districts[1..]) still falls back to the original placeholder-log
    /// behaviour. Composing all four Junkers districts in one map generation
    /// is DISTRICT_TEMPLATE_LIBRARY_1's stated stretch goal, not done here --
    /// the manifest's approxSize/adjacentTo fields remain advisory only, there
    /// is no multi-district spatial layout in this pass.
    ///
    /// Runs before Inhabited_Cast (order 900): the cast should have a composed
    /// place to be dropped into.
    ///
    /// Records the arrival on the casing record too: arrival and compose are
    /// one beat in the lifecycle, and this is the one place both naturally run
    /// (map generation happens exactly once per visit, at arrival).
    /// </summary>
    public class GenStep_ComposeSettlementDistrict : GenStep
    {
        public override int SeedPart => 1104459302;

        /// <summary>District label -> compiled flat rimplace plan file, resolved
        /// relative to this mod's own Templates/ folder. Compiled offline from
        /// the authored Lua source (design/Jawa/templates/junkers_*.lua) via
        /// `rimplace export &lt;template&gt; --out Templates/&lt;name&gt;.txt`
        /// (src/RimMandrake/Utils/rimplace). Only "scrapyard" is wired in this
        /// pass -- "dwelling cluster", "cantina block" and "depot" have
        /// authored+lint-clean Lua templates but are not yet exported/mapped
        /// here; adding them is copying this one dictionary entry plus an
        /// export run, not new engine work.</summary>
        private static readonly Dictionary<string, string> TemplateFiles =
            new Dictionary<string, string>
            {
                { "scrapyard", "junkers_scrapyard.txt" },
            };

        public override void Generate(Map map, GenStepParams parms)
        {
            WorldObject_InhabitedSettlement settlement =
                Find.WorldObjects.WorldObjectAt<WorldObject_InhabitedSettlement>(map.Tile);
            if (settlement == null)
            {
                return;
            }

            settlement.casing.RecordArrival(Find.TickManager.TicksGame);

            string districtLabel = "placeholder district";
            if (settlement.manifest?.districts != null && settlement.manifest.districts.Count > 0
                && !settlement.manifest.districts[0].label.NullOrEmpty())
            {
                districtLabel = settlement.manifest.districts[0].label;
            }

            settlement.casing.RecordDistrictComposed(districtLabel);

            if (TryComposeRealDistrict(map, districtLabel))
            {
                Log.Message("[RimMandrake.Inhabited] composed REAL district '" + districtLabel
                    + "' at " + settlement.LabelCap + " (visit #" + settlement.casing.visitCount
                    + ") via DISTRICT_TEMPLATE_LIBRARY_1.");
            }
            else
            {
                Log.Message("[RimMandrake.Inhabited] composed STUB district '" + districtLabel
                    + "' at " + settlement.LabelCap + " (visit #" + settlement.casing.visitCount
                    + ") -- no DISTRICT_TEMPLATE_LIBRARY_1 template wired for this label yet.");
            }
        }

        /// <summary>Resolves <paramref name="districtLabel"/> through
        /// <see cref="TemplateFiles"/>, parses the compiled flat plan (the
        /// runtime format StructureInjections' RimplacePlan.Parse reads,
        /// src/RimMandrake/StructureInjections/Source/RimplacePlan.cs) and
        /// replays it onto <paramref name="map"/> via
        /// GenStep_RimplacePlan.ApplyPlan -- the same mapgen-time executor
        /// StructureInjections' own GenStepDef-driven path uses, called
        /// directly rather than through a GenStepDef+planFile binding because
        /// the plan file to use depends on manifest data resolved at runtime,
        /// not on static XML. Returns false (no map change made) for any
        /// label with no template, or if the template file is missing/unparsable
        /// -- the caller falls back to the placeholder-log behaviour either
        /// way, so a missing template degrades to the pre-existing stub rather
        /// than an error.</summary>
        private bool TryComposeRealDistrict(Map map, string districtLabel)
        {
            if (districtLabel.NullOrEmpty()
                || !TemplateFiles.TryGetValue(districtLabel, out string fileName))
            {
                return false;
            }

            string modRoot = def.modContentPack?.RootDir;
            if (string.IsNullOrEmpty(modRoot))
            {
                Log.Error("[RimMandrake.Inhabited] GenStepDef " + def.defName +
                          " has no owning modContentPack; cannot resolve district template.");
                return false;
            }

            string path = Path.Combine(Path.Combine(modRoot, "Templates"), fileName);
            if (!File.Exists(path))
            {
                Log.Error("[RimMandrake.Inhabited] district template not found: " + path);
                return false;
            }

            RimplacePlan plan;
            try
            {
                plan = RimplacePlan.Parse(path);
            }
            catch (Exception ex)
            {
                Log.Error("[RimMandrake.Inhabited] failed to parse district template " + path +
                          ": " + ex);
                return false;
            }

            // Same centering rule GenStep_RimplacePlan.Generate uses for its own
            // planFile-driven path: the plan is authored at small, arbitrary
            // offline coordinates, so it is centered on the generated map.
            int dx = 0, dz = 0;
            if (plan.HasFootprint)
            {
                var mapCenter = map.Center;
                int planCenterX = plan.FootprintX + plan.FootprintW / 2;
                int planCenterZ = plan.FootprintZ + plan.FootprintH / 2;
                dx = mapCenter.x - planCenterX;
                dz = mapCenter.z - planCenterZ;
            }

            GenStep_RimplacePlan.ApplyPlan(map, plan, dx, dz, fileName);
            return true;
        }
    }
}
