using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Reflection;
using System.Text;
using HarmonyLib;
using LudeonTK;
using RimWorld;
using Verse;

namespace RimMandrake.LuminousPigment
{
    // DEEPFIRE_GOD_BRIDGE_DELTAS_1: dev-menu tools for
    // src/RimMandrake/bridgetools/prove_deepfire_god_deltas.py. Same shape
    // as the other Deepfire proof actions: ToolMap actions (x/z), one
    // "[DeepfireGods] {json}" log line each; in 1.6 they show flat under
    // Actions as "T: GodDeltas: ..." / "T: LightsOut: ...".
    //
    // Every god action snapshots GameComponent_Ninefold.GetSatiation for all
    // nine gods immediately before and after the ONE real call it exercises
    // (CompDeepfire.AddCoat, MapComponent_DeepfireLights.AddFloorCoat, or the
    // trade patch's own DealSellsDeepfire + OnDeepfireSold), and reports the
    // diff. The script compares it against the spec's numbers times
    // Ninefold's eventMagnitudeMultiplier, which is reported alongside.
    public static class DeepfireGodDeltaDebugActions
    {
        private const string Tag = "[DeepfireGods] ";
        private const int LampOffsetX = 2;

        private static readonly CultureInfo Inv = CultureInfo.InvariantCulture;

        [DebugAction("Deepfire", "GodDeltas: coat new wall at cell", actionType = DebugActionType.ToolMap, allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void CoatNewWall()
        {
            Thing wall = SpawnAt(ThingDef.Named("Wall"), ThingDef.Named("Steel"));
            CoatAndReport(wall, "wall");
        }

        [DebugAction("Deepfire", "GodDeltas: coat new parka at cell", actionType = DebugActionType.ToolMap, allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void CoatNewParka()
        {
            Thing parka = SpawnAt(ThingDef.Named("Apparel_Parka"), ThingDefOf.Cloth);
            CoatAndReport(parka, "parka");
        }

        [DebugAction("Deepfire", "GodDeltas: second coat on thing at cell", actionType = DebugActionType.ToolMap, allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void SecondCoat()
        {
            Thing thing = FindDeepfireThing(UI.MouseCell());
            if (thing == null) { Log.Message(Tag + "{\"action\":\"secondCoat\",\"found\":false}"); return; }
            Dictionary<string, float> before = Snapshot();
            thing.TryGetComp<CompDeepfire>().AddCoat();
            Log.Message(Tag + Report("secondCoat", thing, before, Snapshot()));
        }

        [DebugAction("Deepfire", "GodDeltas: coat idol of Rekko at cell", actionType = DebugActionType.ToolMap, allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void CoatIdolRekko() => CoatIdol("Rekko");

        [DebugAction("Deepfire", "GodDeltas: coat idol of Ishko at cell", actionType = DebugActionType.ToolMap, allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void CoatIdolIshko() => CoatIdol(DeepfireGodDeltas.Ishko);

        // The Utinni statue mod (spec §5.3) is not built, so the idol is a
        // SculptureSmall whose def is tagged with RM_DeepfireGodExtension
        // for the duration of this one coat and untagged again afterwards --
        // the same GetModExtension read a real idol def would answer.
        private static void CoatIdol(string god)
        {
            ThingDef def = ThingDef.Named("SculptureSmall");
            Thing idol = SpawnAt(def, ThingDef.Named("Steel"));
            List<DefModExtension> original = def.modExtensions;
            var tagged = original != null ? new List<DefModExtension>(original) : new List<DefModExtension>();
            tagged.Add(new DeepfireGodExtension { god = god });
            def.modExtensions = tagged;
            try
            {
                CoatAndReport(idol, "idol:" + god);
            }
            finally
            {
                def.modExtensions = original;
            }
        }

        [DebugAction("Deepfire", "GodDeltas: coat floor cell at cell", actionType = DebugActionType.ToolMap, allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void CoatFloorCell()
        {
            Map map = Find.CurrentMap;
            IntVec3 c = UI.MouseCell();
            TerrainDef floor = map.terrainGrid.TopTerrainAt(c);
            GameComponent_Deepfire.ResetGodCoatEvents(DeepfireGodDeltas.KeyFor(floor));
            MapComponent_DeepfireLights mc = MapComponent_DeepfireLights.Get(map);
            Dictionary<string, float> before = Snapshot();
            bool added = mc != null && mc.AddFloorCoat(c);
            Dictionary<string, float> after = Snapshot();
            Log.Message(Tag + "{\"action\":\"floor\",\"terrain\":\"" + floor.defName + "\",\"added\":" + B(added)
                + "," + Common() + ",\"deltas\":" + Diff(before, after) + "}");
        }

        // godDeltaDiminishAfter + 1 fresh walls, one after another on the
        // clicked cell, each given its first coat. Reports the diff of the
        // last full-strength event and of the first diminished one.
        [DebugAction("Deepfire", "GodDeltas: diminish test at cell", actionType = DebugActionType.ToolMap, allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void DiminishTest()
        {
            ThingDef wallDef = ThingDef.Named("Wall");
            GameComponent_Deepfire.ResetGodCoatEvents(DeepfireGodDeltas.KeyFor(wallDef));
            int n = LuminousPigmentSettings.godDeltaDiminishAfter;
            string lastFull = "{}", firstDiminished = "{}";
            for (int i = 0; i <= n; i++)
            {
                Thing wall = SpawnAt(wallDef, ThingDef.Named("Steel"), resetCount: false);
                Dictionary<string, float> before = Snapshot();
                wall.TryGetComp<CompDeepfire>()?.AddCoat();
                string diff = Diff(before, Snapshot());
                if (i == n - 1) lastFull = diff;
                if (i == n) firstDiminished = diff;
                wall.Destroy();
            }
            Log.Message(Tag + "{\"action\":\"diminish\",\"diminishAfter\":" + n
                + ",\"events\":" + GameComponent_Deepfire.GodCoatEventsFor(DeepfireGodDeltas.KeyFor(wallDef))
                + "," + Common() + ",\"lastFull\":" + lastFull + ",\"firstDiminished\":" + firstDiminished + "}");
        }

        // The trade hook cannot be driven without a trader, so this proves
        // its two halves separately: (1) Patch_TradeDeal_DeepfireSold is
        // registered on TradeDeal.TryExecute under this mod's Harmony id;
        // (2) its own DealSellsDeepfire reads real Tradeables correctly
        // (a sold jar yes, a sold coated sculpture yes, sold plain steel no,
        // a BOUGHT jar no), and OnDeepfireSold moves Mob'Unloo.
        [DebugAction("Deepfire", "GodDeltas: sold deepfire (simulated deal)", actionType = DebugActionType.ToolMap, allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void SoldDeepfire()
        {
            MethodInfo tryExecute = AccessTools.Method(typeof(TradeDeal), nameof(TradeDeal.TryExecute));
            Patches info = Harmony.GetPatchInfo(tryExecute);
            bool prefix = info != null && info.Prefixes.Any(p => p.PatchMethod.DeclaringType == typeof(Patch_TradeDeal_DeepfireSold));
            bool postfix = info != null && info.Postfixes.Any(p => p.PatchMethod.DeclaringType == typeof(Patch_TradeDeal_DeepfireSold));

            Thing jar = ThingMaker.MakeThing(ThingDef.Named(DeepfireGodDeltas.DeepfireDefName));
            Thing steel = ThingMaker.MakeThing(ThingDef.Named("Steel"));
            Thing sculpture = ThingMaker.MakeThing(ThingDef.Named("SculptureSmall"), ThingDef.Named("Steel"));
            CompDeepfire sc = sculpture.TryGetComp<CompDeepfire>();
            if (sc != null) sc.coats = 1; // unspawned: set the field, not AddCoat (no god event, no light)

            bool sellsJar = DeepfireGodDeltas.DealSellsDeepfire(new List<Tradeable> { Selling(jar) });
            bool sellsSculpture = DeepfireGodDeltas.DealSellsDeepfire(new List<Tradeable> { Selling(sculpture) });
            bool sellsSteel = DeepfireGodDeltas.DealSellsDeepfire(new List<Tradeable> { Selling(steel) });
            bool buysJar = DeepfireGodDeltas.DealSellsDeepfire(new List<Tradeable> { Buying(jar) });

            Dictionary<string, float> before = Snapshot();
            if (sellsJar) DeepfireGodDeltas.OnDeepfireSold();
            Dictionary<string, float> after = Snapshot();

            Log.Message(Tag + "{\"action\":\"sold\",\"prefixRegistered\":" + B(prefix) + ",\"postfixRegistered\":" + B(postfix)
                + ",\"sellsJar\":" + B(sellsJar) + ",\"sellsCoatedSculpture\":" + B(sellsSculpture)
                + ",\"sellsSteel\":" + B(sellsSteel) + ",\"buysJar\":" + B(buysJar)
                + "," + Common() + ",\"deltas\":" + Diff(before, after) + "}");
        }

        private static Tradeable Selling(Thing thing)
        {
            var t = new Tradeable();
            t.thingsColony.Add(thing);
            t.ForceToDestination(1);
            return t;
        }

        private static Tradeable Buying(Thing thing)
        {
            var t = new Tradeable();
            t.thingsTrader.Add(thing);
            t.ForceToSource(1);
            return t;
        }

        // Spec §10 step 10: "With LightsOut: proxies survive an empty room
        // being 'switched off'". Coats a sculpture on the clicked cell (inside
        // a room the script built) and puts a StandingLamp beside it as the
        // control, roofs the room so LightsOut does not treat it as outdoors,
        // then calls LightsOut's own Lights.DisableAllLights(room) -- exactly
        // what it runs when a room empties -- and reads the result.
        [DebugAction("Deepfire", "LightsOut: switch off room at cell", actionType = DebugActionType.ToolMap, allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void LightsOutCheck()
        {
            Map map = Find.CurrentMap;
            IntVec3 c = UI.MouseCell();
            var sb = new StringBuilder("{\"action\":\"lightsOut\",\"lightsOutLoaded\":" + B(DeepfireLightsOutCompat.LightsOutLoaded)
                + ",\"canBeLightPatched\":" + B(DeepfireLightsOutCompat.CanBeLightPatched)
                + ",\"canConsumePatched\":" + B(DeepfireLightsOutCompat.CanConsumePatched));
            Type lights = AccessTools.TypeByName(DeepfireLightsOutCompat.LightsTypeName);
            Type resources = AccessTools.TypeByName(DeepfireLightsOutCompat.ResourcesTypeName);
            Type settings = AccessTools.TypeByName("LightsOut.Boilerplate.ModSettings");
            if (lights == null || resources == null)
            {
                Log.Message(Tag + sb + "}");
                return;
            }
            MethodInfo canBeLight = AccessTools.Method(lights, "CanBeLight", new[] { typeof(ThingWithComps) });
            MethodInfo disableAll = AccessTools.Method(lights, "DisableAllLights", new[] { typeof(Room), typeof(bool) });
            MethodInfo enableAll = AccessTools.Method(lights, "EnableAllLights", new[] { typeof(Room) });
            MethodInfo canConsume = AccessTools.Method(resources, "CanConsumeResources", new[] { typeof(ThingWithComps) });
            FieldInfo flick = settings != null ? AccessTools.Field(settings, "FlickLights") : null;

            Thing sculpture = SpawnAt(ThingDef.Named("SculptureSmall"), ThingDef.Named("Steel"));
            sculpture.TryGetComp<CompDeepfire>()?.AddCoat();
            ThingDef lampDef = ThingDef.Named("StandingLamp");
            Thing lamp = ThingMaker.MakeThing(lampDef, GenStuff.DefaultStuffFor(lampDef));
            lamp.SetFaction(Faction.OfPlayer);
            GenSpawn.Spawn(lamp, c + new IntVec3(LampOffsetX, 0, 0), map, WipeMode.Vanish);

            Thing proxy = c.GetThingList(map).FirstOrDefault(t => t.def == DeepfireDefOf.RM_DeepfireLightProxy);
            CompGlower glower = proxy?.TryGetComp<CompGlower>();
            Room room = c.GetRoom(map);
            if (room != null)
            {
                foreach (IntVec3 cell in room.Cells) map.roofGrid.SetRoof(cell, RoofDefOf.RoofConstructed);
            }

            bool glowsBefore = glower != null && glower.Glows;
            object proxyCanBeLight = proxy != null ? canBeLight.Invoke(null, new object[] { proxy }) : null;
            object lampCanBeLight = canBeLight.Invoke(null, new object[] { lamp });
            if (room != null) disableAll.Invoke(null, new object[] { room, false });
            glower?.UpdateLit(map);
            bool glowsAfter = glower != null && glower.Glows;
            object proxyConsume = proxy != null ? canConsume.Invoke(null, new object[] { proxy }) : null;
            object lampConsume = canConsume.Invoke(null, new object[] { lamp });
            if (room != null) enableAll.Invoke(null, new object[] { room });

            sb.Append(",\"flickLights\":" + (flick != null ? B((bool)flick.GetValue(null)) : "null"));
            sb.Append(",\"proxyFound\":" + B(proxy != null) + ",\"roomOutdoors\":" + B(room == null || room.OutdoorsForWork));
            sb.Append(",\"proxyCanBeLight\":" + Json(proxyCanBeLight) + ",\"lampCanBeLight\":" + Json(lampCanBeLight));
            sb.Append(",\"proxyGlowsBefore\":" + B(glowsBefore) + ",\"proxyGlowsAfter\":" + B(glowsAfter));
            sb.Append(",\"proxyCanConsume\":" + Json(proxyConsume) + ",\"lampCanConsume\":" + Json(lampConsume) + "}");
            lamp.Destroy();
            sculpture.Destroy();
            Log.Message(Tag + sb);
        }

        // ---- helpers ----

        private static Thing SpawnAt(ThingDef def, ThingDef stuff, bool resetCount = true)
        {
            Map map = Find.CurrentMap;
            IntVec3 c = UI.MouseCell();
            if (resetCount) GameComponent_Deepfire.ResetGodCoatEvents(DeepfireGodDeltas.KeyFor(def));
            Thing thing = ThingMaker.MakeThing(def, def.MadeFromStuff ? stuff : null);
            thing.SetFaction(Faction.OfPlayer);
            GenSpawn.Spawn(thing, c, map, WipeMode.Vanish);
            return thing;
        }

        private static void CoatAndReport(Thing thing, string action)
        {
            Dictionary<string, float> before = Snapshot();
            thing.TryGetComp<CompDeepfire>()?.AddCoat();
            Log.Message(Tag + Report(action, thing, before, Snapshot()));
        }

        private static Thing FindDeepfireThing(IntVec3 c)
        {
            Map map = Find.CurrentMap;
            if (map == null || !c.InBounds(map)) return null;
            foreach (Thing t in c.GetThingList(map))
            {
                if (t.TryGetComp<CompDeepfire>() != null) return t;
            }
            return null;
        }

        private static Dictionary<string, float> Snapshot()
        {
            var snap = new Dictionary<string, float>();
            foreach (string god in NinefoldDeltaBridge.GodNames)
            {
                if (NinefoldDeltaBridge.TryGetSatiation(god, out float v)) snap[god] = v;
            }
            return snap;
        }

        private static string Diff(Dictionary<string, float> before, Dictionary<string, float> after)
        {
            var sb = new StringBuilder("{");
            bool first = true;
            foreach (KeyValuePair<string, float> kv in after)
            {
                before.TryGetValue(kv.Key, out float b);
                if (!first) sb.Append(',');
                first = false;
                // "b" = satiation before, "d" = change: Ninefold clamps
                // satiation to [-100, 100], so the script needs the start
                // point to know the expected change after many events.
                sb.AppendFormat(Inv, "\"{0}\":{{\"b\":{1:0.####},\"d\":{2:0.####}}}", kv.Key, b, kv.Value - b);
            }
            return sb.Append('}').ToString();
        }

        private static string Common()
        {
            return string.Format(Inv, "\"ninefold\":{0},\"engineEnabled\":{1},\"godsReact\":{2},\"multiplier\":{3:0.####}",
                B(NinefoldDeltaBridge.Available), B(NinefoldDeltaBridge.EngineEnabled),
                B(LuminousPigmentSettings.godsReact), NinefoldDeltaBridge.MagnitudeMultiplier);
        }

        private static string Report(string action, Thing thing, Dictionary<string, float> before, Dictionary<string, float> after)
        {
            CompDeepfire comp = thing.TryGetComp<CompDeepfire>();
            return "{\"action\":\"" + action + "\",\"found\":true,\"def\":\"" + thing.def.defName + "\""
                + ",\"coats\":" + (comp != null ? comp.coats : -1)
                + ",\"statueGod\":\"" + (DeepfireGodDeltas.StatueGodOf(thing) ?? "") + "\""
                + ",\"wornClass\":" + B(DeepfireGodDeltas.IsWornClass(thing))
                + "," + Common() + ",\"deltas\":" + Diff(before, after) + "}";
        }

        private static string Json(object v)
        {
            if (v == null) return "null";
            return v is bool b ? B(b) : "\"" + v + "\"";
        }

        private static string B(bool b) => b ? "true" : "false";
    }
}
