using System.Globalization;
using System.Text;
using LudeonTK;
using RimWorld;
using Verse;

namespace RimMandrake.LuminousPigment
{
    // DEEPFIRE_FIRSTCOAT_BONUS_1: dev-menu tools for this item's own
    // quicktest (src/RimMandrake/bridgetools/prove_deepfire_firstcoat.py),
    // same shape as DeepfireFloorDebugActions.cs -- each action acts on the
    // clicked cell (rimworld/execute_debug_action with x/z) and writes
    // exactly one "[DeepfireFirstCoat] {json}" log line so the script parses
    // a result instead of guessing from the screen. Coat/remove go straight
    // through CompDeepfire.AddCoat()/RemoveAllCoats() -- the same entry
    // points the real WorkGiver/JobDriver path ends in -- so what is being
    // exercised is this item's own C# (DeepfireFirstCoatBonus,
    // RM_StatPart_Deepfire), not a shortcut around it.
    public static class DeepfireFirstCoatDebugActions
    {
        private const string Tag = "[DeepfireFirstCoat] ";

        [DebugAction("Deepfire", "FirstCoat: spawn art Normal at cell", actionType = DebugActionType.ToolMap, allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void SpawnArtNormal() => SpawnArt(QualityCategory.Normal);

        [DebugAction("Deepfire", "FirstCoat: spawn art Legendary at cell", actionType = DebugActionType.ToolMap, allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void SpawnArtLegendary() => SpawnArt(QualityCategory.Legendary);

        // SculptureSmall: CompArt + CompQuality, unambiguously an "art item"
        // (spec §3.5 bullet 1) -- the quality-bump path.
        private static void SpawnArt(QualityCategory quality)
        {
            Map map = Find.CurrentMap;
            IntVec3 c = UI.MouseCell();
            ThingDef def = ThingDef.Named("SculptureSmall");
            ThingDef stuff = ThingDef.Named("Steel");
            Thing thing = ThingMaker.MakeThing(def, stuff);
            CompQuality q = thing.TryGetComp<CompQuality>();
            q?.SetQuality(quality, ArtGenerationContext.Colony);
            GenSpawn.Spawn(thing, c, map, WipeMode.Vanish);
            Log.Message(Tag + Report(thing, "spawnArt"));
        }

        // Wall: paintable, CompColorable, no CompArt -- the spec's own
        // worked example for the Beauty-StatPart ("everything else") path
        // ("a wall (beauty 0) gets +3").
        [DebugAction("Deepfire", "FirstCoat: spawn wall at cell", actionType = DebugActionType.ToolMap, allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void SpawnWall()
        {
            Map map = Find.CurrentMap;
            IntVec3 c = UI.MouseCell();
            ThingDef def = ThingDef.Named("Wall");
            ThingDef stuff = ThingDef.Named("Steel");
            Thing thing = ThingMaker.MakeThing(def, stuff);
            GenSpawn.Spawn(thing, c, map, WipeMode.Vanish);
            Log.Message(Tag + Report(thing, "spawnWall"));
        }

        [DebugAction("Deepfire", "FirstCoat: coat thing at cell", actionType = DebugActionType.ToolMap, allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void CoatAtCell()
        {
            Thing thing = FindDeepfireThing(UI.MouseCell());
            if (thing == null) { Log.Message(Tag + "{\"action\":\"coat\",\"found\":false}"); return; }
            thing.TryGetComp<CompDeepfire>()?.AddCoat();
            Log.Message(Tag + Report(thing, "coat"));
        }

        [DebugAction("Deepfire", "FirstCoat: remove coats at cell", actionType = DebugActionType.ToolMap, allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void RemoveAtCell()
        {
            Thing thing = FindDeepfireThing(UI.MouseCell());
            if (thing == null) { Log.Message(Tag + "{\"action\":\"remove\",\"found\":false}"); return; }
            thing.TryGetComp<CompDeepfire>()?.RemoveAllCoats();
            Log.Message(Tag + Report(thing, "remove"));
        }

        [DebugAction("Deepfire", "FirstCoat: report thing at cell", actionType = DebugActionType.ToolMap, allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void ReportAtCell()
        {
            Thing thing = FindDeepfireThing(UI.MouseCell());
            if (thing == null) { Log.Message(Tag + "{\"action\":\"report\",\"found\":false}"); return; }
            Log.Message(Tag + Report(thing, "report"));
        }

        [DebugAction("Deepfire", "FirstCoat: destroy thing at cell", actionType = DebugActionType.ToolMap, allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void DestroyAtCell()
        {
            Thing thing = FindDeepfireThing(UI.MouseCell());
            bool found = thing != null;
            thing?.Destroy();
            Log.Message(Tag + "{\"action\":\"destroy\",\"found\":" + (found ? "true" : "false") + "}");
        }

        private static Thing FindDeepfireThing(IntVec3 c)
        {
            Map map = Find.CurrentMap;
            if (map == null || !c.InBounds(map)) return null;
            Building edifice = c.GetEdifice(map);
            if (edifice != null && edifice.TryGetComp<CompDeepfire>() != null) return edifice;
            foreach (Thing t in c.GetThingList(map))
            {
                if (t.TryGetComp<CompDeepfire>() != null) return t;
            }
            return null;
        }

        private static string Report(Thing thing, string action)
        {
            CultureInfo inv = CultureInfo.InvariantCulture;
            CompDeepfire comp = thing.TryGetComp<CompDeepfire>();
            CompQuality q = thing.TryGetComp<CompQuality>();
            bool isArt = DeepfireFirstCoatBonus.IsArtItem(thing);
            float beauty = thing.GetStatValue(StatDefOf.Beauty);

            var sb = new StringBuilder();
            sb.Append('{');
            sb.AppendFormat(inv, "\"action\":\"{0}\",\"found\":true,\"thingId\":{1},\"def\":\"{2}\",", action, thing.thingIDNumber, thing.def.defName);
            sb.AppendFormat(inv, "\"isArt\":{0},\"coats\":{1},\"bonusApplied\":{2},",
                isArt ? "true" : "false", comp != null ? comp.coats : -1, (comp != null && comp.bonusApplied) ? "true" : "false");
            sb.AppendFormat(inv, "\"quality\":\"{0}\",", q != null ? q.Quality.ToString() : "");
            sb.AppendFormat(inv, "\"beauty\":{0:0.####}", beauty);
            sb.Append('}');
            return sb.ToString();
        }
    }
}
