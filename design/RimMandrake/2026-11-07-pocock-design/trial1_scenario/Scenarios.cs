// Literal scenarios at ThoughtWorker_ViewedGraffitiMark: each builds a small world (two rooms split at x = 10, a colonist at (5,5)),
// puts one mark somewhere, and asks the REAL worker whether a given reaction thought is active. The expectations are written in
// play terms, never by re-deriving the kernel's boolean expressions, so a wrong literal, a swapped argument, a missing call or an
// inverted result at the call site changes an answer here.
using System;
using System.Collections.Generic;
using RimMandrake.Graffiti;
using RimWorld;
using Verse;

namespace GraffitiScenario
{
    public static class Program
    {
        static readonly ThoughtDef Hostile = new ThoughtDef { defName = "HostileMaker" };
        static readonly ThoughtDef SameIdeo = new ThoughtDef { defName = "SameIdeo" };
        static readonly ThoughtDef OtherIdeo = new ThoughtDef { defName = "OtherIdeo" };
        static readonly ThoughtDef Flat = new ThoughtDef { defName = "Flat" };

        static readonly Faction Pirates = new Faction("pirates");
        static readonly Faction Traders = new Faction("traders");
        static readonly Ideo ColonyIdeo = new Ideo("colony");
        static readonly Ideo OutsideIdeo = new Ideo("outside");

        static int pass, fail;

        static Map World()
        {
            var map = new Map();
            var a = new Room("A");
            var b = new Room("B");
            for (int x = 0; x < map.size; x++)
                for (int z = 0; z < map.size; z++)
                    map.rooms[new IntVec3(x, z)] = x < 10 ? a : b;
            return map;
        }

        static Pawn Viewer(Map map, Faction faction, Ideo ideo)
        {
            return new Pawn { Map = map, Spawned = true, Position = new IntVec3(5, 5), Faction = faction, Ideo = ideo };
        }

        static Filth_Mark Mark(Map map, IntVec3 at, ModExtension_Graffiti ext, Faction maker, Ideo makerIdeo)
        {
            var def = new ThingDef { defName = "RM_Graffiti_Test" };
            def.modExtensions.Add(ext);
            var mark = new Filth_Mark { def = def, makerFaction = maker, makerIdeo = makerIdeo };
            map.things[at] = new List<Thing> { mark };
            return mark;
        }

        static bool Feels(Pawn p, ThoughtDef thought)
        {
            var worker = new ThoughtWorker_ViewedGraffitiMark { def = thought };
            return worker.CurrentState(p).Active;
        }

        static void Expect(string scenario, bool got, bool want)
        {
            if (got == want) { pass++; Console.WriteLine("ok    " + scenario); }
            else { fail++; Console.WriteLine("FAIL  " + scenario + " (got " + got + ", want " + want + ")"); }
        }

        static void Reset()
        {
            RM_GraffitiSettings.viewerReactionEnabled = true;
            RM_GraffitiSettings.paintingEnabled = true;
            Faction.OfPlayer.hostile.Clear();
            Pirates.hostile.Clear();
            Pirates.hostile.Add(Faction.OfPlayer);
        }

        static ModExtension_Graffiti HostileTag() { return new ModExtension_Graffiti { onViewHostileMaker = Hostile }; }

        public static int Main()
        {
            Map m; Pawn colonist;

            Reset(); m = World(); colonist = Viewer(m, Faction.OfPlayer, ColonyIdeo);
            Mark(m, new IntVec3(7, 5), HostileTag(), Pirates, OutsideIdeo);
            Expect("an enemy's tag 2 cells away in the same room: the colonist gets the hostile-maker thought", Feels(colonist, Hostile), true);

            Reset(); m = World(); colonist = Viewer(m, Faction.OfPlayer, ColonyIdeo);
            Mark(m, new IntVec3(7, 5), HostileTag(), Pirates, OutsideIdeo);
            RM_GraffitiSettings.viewerReactionEnabled = false;
            Expect("the same tag with 'Viewer reactions' off (painting still on): no thought", Feels(colonist, Hostile), false);

            Reset(); m = World(); colonist = Viewer(m, Faction.OfPlayer, ColonyIdeo);
            Mark(m, new IntVec3(12, 5), HostileTag(), Pirates, OutsideIdeo);
            Expect("the same tag through the wall, in the next room 7 cells away: no thought", Feels(colonist, Hostile), false);

            Reset(); m = World(); colonist = Viewer(m, Faction.OfPlayer, ColonyIdeo);
            Mark(m, new IntVec3(7, 5), HostileTag(), Pirates, OutsideIdeo);
            m.rooms.Remove(new IntVec3(7, 5));
            Expect("a tag on a wall cell that reports no room: the colonist still gets the thought", Feels(colonist, Hostile), true);

            Reset(); m = World(); colonist = Viewer(m, Faction.OfPlayer, ColonyIdeo);
            Mark(m, new IntVec3(5, 15), HostileTag(), Pirates, OutsideIdeo);
            m.rooms[new IntVec3(5, 15)] = m.rooms[new IntVec3(5, 5)];
            Expect("a tag 10 cells away in the same room: out of sight, no thought", Feels(colonist, Hostile), false);

            Reset(); m = World(); colonist = Viewer(m, Faction.OfPlayer, ColonyIdeo);
            Mark(m, new IntVec3(7, 5), HostileTag(), Pirates, OutsideIdeo);
            m.fogged.Add(new IntVec3(7, 5));
            Expect("a tag under fog: no thought", Feels(colonist, Hostile), false);

            Reset(); m = World(); colonist = Viewer(m, Faction.OfPlayer, ColonyIdeo);
            Mark(m, new IntVec3(7, 5), HostileTag(), Pirates, OutsideIdeo);
            colonist.Spawned = false; colonist.Map = null;
            Expect("a colonist who is not on the map: no thought", Feels(colonist, Hostile), false);

            Reset(); m = World(); colonist = Viewer(m, Faction.OfPlayer, ColonyIdeo);
            Mark(m, new IntVec3(7, 5), new ModExtension_Graffiti { visibility = GraffitiVisibility.ClanOnly, viewerReactionThought = Flat }, null, null);
            Expect("a clan-only mark: a colonist reads it", Feels(colonist, Flat), true);

            Reset(); m = World();
            Mark(m, new IntVec3(7, 5), new ModExtension_Graffiti { visibility = GraffitiVisibility.ClanOnly, viewerReactionThought = Flat }, null, null);
            Expect("the same clan-only mark: a visiting trader sees it but gets no thought", Feels(Viewer(m, Traders, OutsideIdeo), Flat), false);

            Reset(); m = World(); colonist = Viewer(m, Faction.OfPlayer, ColonyIdeo);
            Mark(m, new IntVec3(7, 5), new ModExtension_Graffiti { viewerReactionThought = Flat }, null, null);
            Expect("a public mark: a colonist gets its thought", Feels(colonist, Flat), true);
            Expect("the same public mark: a visiting trader gets it too", Feels(Viewer(m, Traders, OutsideIdeo), Flat), true);

            Reset(); m = World(); colonist = Viewer(m, Faction.OfPlayer, ColonyIdeo);
            Mark(m, new IntVec3(7, 5), new ModExtension_Graffiti { onViewSameIdeo = SameIdeo, onViewOtherIdeo = OtherIdeo }, Traders, ColonyIdeo);
            Expect("a trader's mark in the colony's own ideo: the colonist gets the same-ideo thought", Feels(colonist, SameIdeo), true);
            Expect("... and not the other-ideo thought", Feels(colonist, OtherIdeo), false);

            Reset(); m = World(); colonist = Viewer(m, Faction.OfPlayer, OutsideIdeo);
            Mark(m, new IntVec3(7, 5), new ModExtension_Graffiti { onViewSameIdeo = SameIdeo, onViewOtherIdeo = OtherIdeo }, Traders, ColonyIdeo);
            Expect("the same mark seen by a colonist of another ideo: the other-ideo thought", Feels(colonist, OtherIdeo), true);
            Expect("... and not the same-ideo thought", Feels(colonist, SameIdeo), false);

            Console.WriteLine("graffiti scenarios: " + pass + " ok, " + fail + " failed -> " + (fail == 0 ? "OK" : "FAILED"));
            return fail == 0 ? 0 : 1;
        }
    }
}
